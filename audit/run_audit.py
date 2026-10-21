"""
Independent audit of the engine: data integrity, validation bias,
effect of Monte Carlo assumptions, and how scoring propagates.

    python audit/run_audit.py      (after run_engine.py)

Writes results/audit/*.csv and results/audit/audit_summary.json.
Every number quoted in docs/AUDIT.md comes from these files.
"""

import itertools
import json
import sys
import warnings
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from landslide_risk import engine as E
from landslide_risk import parameters_v2 as P2
from landslide_risk.bishop import bishop_fs_samples
from landslide_risk.case_data import RAW as RAW_HTML
from landslide_risk.config import VARIABLES
from landslide_risk.metrics import classification_metrics
from landslide_risk.risk_index import classify
from landslide_risk.simulation import sample_factor_of_safety as sample_v1
from landslide_risk.variance import exact_sobol

warnings.filterwarnings("ignore")
OUT = ROOT / "results" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = {}
CASE = np.array([3, 4, 4, 4, 1, 2])
VI_CASE = 0.584


# ===========================================================================
# Part 1  Data integrity
# ===========================================================================
def part1_data(cases):
    raw = next(t for t in pd.read_html(RAW_HTML) if len(t) > 500 and "Status" in t.columns).iloc[:, 1:8]
    raw.columns = ["gamma", "c", "phi", "beta", "H", "ru", "status"]
    removed = raw[raw.gamma < 10]
    g = cases.groupby("group").failed.agg(["min", "max", "size"])
    info = {
        "raw_rows": len(raw),
        "removed_gamma_lt_10": len(removed),
        "removed_failed_share": float((removed.status.str.lower().str.strip() == "failure").mean()),
        "kept_rows": len(cases),
        "phi_equal_0": int((cases.phi == 0).sum()),
        "c_equal_0": int((cases.c == 0).sum()),
        "ru_ge_1": int((cases.ru >= 1).sum()),
        "groups": int(cases.group.nunique()),
        "multi_member_groups": int((g["size"] > 1).sum()),
        "groups_with_conflicting_labels": int((g["min"] != g["max"]).sum()),
        "stable_with_fs_lt_1": int(((cases.failed == 0) & (cases.fs < 1)).sum()),
        "stable_total": int((cases.failed == 0).sum()),
        "failed_with_fs_ge_1": int(((cases.failed == 1) & (cases.fs >= 1)).sum()),
        "failed_total": int((cases.failed == 1).sum()),
    }
    SUMMARY["data"] = info
    print("Part 1", info)


# ===========================================================================
# Part 2  Validation bias
# ===========================================================================
class LogisticRaw:
    """Fair linear statistical baseline: logistic regression on the 6 raw inputs."""

    def fit(self, X, y):
        self.m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X[E.RAW], y)
        return self

    def predict_proba(self, X):
        return self.m.predict_proba(X[E.RAW])


MODELS = dict(E.MODELS)          # includes E_logistic (fair linear baseline)


def cv(df, n_splits=5, n_repeats=5, models=MODELS, group_col="group"):
    y, groups = df.failed.to_numpy(), df[group_col].to_numpy()
    folds, single, avg = [], {m: [] for m in models}, {m: np.zeros(len(df)) for m in models}
    for rep in range(n_repeats):
        oof = {m: np.zeros(len(df)) for m in models}
        for fold, (tr, te) in enumerate(StratifiedGroupKFold(n_splits, shuffle=True, random_state=rep)
                                        .split(df, y, groups)):
            for name, f in models.items():
                p = f(rep).fit(df.iloc[tr], y[tr]).predict_proba(df.iloc[te])[:, 1]
                oof[name][te] = p
                folds.append({"model": name, "repeat": rep, **classification_metrics(y[te], p)})
        for m in models:
            single[m].append(classification_metrics(y, oof[m]))
            avg[m] += oof[m] / n_repeats
    folds = pd.DataFrame(folds)
    rows = []
    for m in models:
        f = folds[folds.model == m]
        s = pd.DataFrame(single[m])
        a = classification_metrics(y, avg[m])
        rows.append({"model": m,
                     "auc_fold_mean": f.auc.mean(), "auc_fold_sd": f.auc.std(),
                     "auc_pooled_single": s.auc.mean(), "auc_pooled_avg5": a["auc"],
                     "ece_fold_mean": f.ece.mean(), "ece_pooled_single": s.ece.mean(), "ece_pooled_avg5": a["ece"],
                     "brier_fold_mean": f.brier.mean(), "brier_pooled_avg5": a["brier"],
                     "sens_pooled_single": s.sensitivity.mean(), "spec_pooled_single": s.specificity.mean()})
    return pd.DataFrame(rows).set_index("model"), avg


def group_bootstrap(df, p, q=None, n_boot=2000, seed=0):
    """AUC (or AUC difference p - q) with resampling of whole near-duplicate groups."""
    rng = np.random.default_rng(seed)
    groups = df.group.to_numpy()
    uniq = np.unique(groups)
    idx_by = {g: np.flatnonzero(groups == g) for g in uniq}
    y = df.failed.to_numpy()
    vals = []
    for _ in range(n_boot):
        idx = np.concatenate([idx_by[g] for g in rng.choice(uniq, len(uniq))])
        if len(set(y[idx])) < 2:
            continue
        v = roc_auc_score(y[idx], p[idx])
        if q is not None:
            v -= roc_auc_score(y[idx], q[idx])
        vals.append(v)
    return float(np.mean(vals)), float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def case_bootstrap(y, p, q=None, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        v = roc_auc_score(y[i], p[i]) - (roc_auc_score(y[i], q[i]) if q is not None else 0)
        vals.append(v)
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


def part2_validation(cases):
    res = {}
    dom = cases[E.in_domain(cases)].reset_index(drop=True)
    for label, d in (("all", cases), ("domain", dom)):
        table, avg = cv(d)
        table.to_csv(OUT / f"cv_estimators_{label}.csv")
        res[label] = {"table": table.round(4).to_dict(orient="index")}
        y = d.failed.to_numpy()
        res[label]["auc_D_groupboot"] = group_bootstrap(d, avg["D_hybrid"])
        res[label]["auc_D_caseboot_ci"] = case_bootstrap(y, avg["D_hybrid"])
        for other in ("A_heuristic", "B_physics", "C_ml_raw", "E_logistic"):
            res[label][f"dAUC_D_minus_{other}_groupboot"] = group_bootstrap(d, avg["D_hybrid"], avg[other])
        # operating point: threshold giving >= 90% recall of failures
        p = avg["D_hybrid"]
        thr = np.quantile(p[y == 1], 0.10)
        res[label]["threshold_for_90pct_recall"] = float(thr)
        res[label]["specificity_at_90pct_recall"] = float(((p < thr) & (y == 0)).sum() / (y == 0).sum())
        print(f"Part 2 [{label}]\n", table[["auc_fold_mean", "auc_fold_sd", "auc_pooled_avg5",
                                             "ece_fold_mean", "ece_pooled_avg5"]].round(3))

    # Domain-threshold sensitivity (the domain was chosen after seeing results)
    rows = []
    for gmax, hmax, rumax in itertools.product([21, 22, 23, 24, 25, 99], [50, 100, 200, 9999], [0.9, 1.01]):
        d = cases[(cases.gamma <= gmax) & (cases.H <= hmax) & (cases.ru <= rumax)].reset_index(drop=True)
        if len(d) < 120 or d.failed.nunique() < 2:
            continue
        t, _ = cv(d, n_repeats=2, models={k: MODELS[k] for k in ("B_physics", "D_hybrid")})
        rows.append({"gamma_max": gmax, "H_max": hmax, "ru_max": rumax, "n": len(d),
                     "auc_physics": t.loc["B_physics", "auc_fold_mean"], "auc_hybrid": t.loc["D_hybrid", "auc_fold_mean"]})
    dom_grid = pd.DataFrame(rows)
    dom_grid.to_csv(OUT / "domain_sensitivity.csv", index=False)
    res["domain_grid"] = {k: [float(dom_grid[k].min()), float(dom_grid[k].max())] for k in ("auc_physics", "auc_hybrid")}

    # Grouping coarseness: is leakage fully removed?
    rows = []
    for k in (1, 2, 4, 8):
        key = pd.DataFrame({"g": (cases.gamma * 2 / k).round(), "c": (cases.c / k).round(), "p": (cases.phi / k).round(),
                            "b": (cases.beta / k).round(), "h": np.round(np.log(cases.H) / (0.02 * k)),
                            "r": (cases.ru * 50 / k).round()})
        d = cases.copy()
        d["g2"] = key.groupby(list(key.columns), sort=False).ngroup().to_numpy()
        t, _ = cv(d, n_repeats=2, models={k2: MODELS[k2] for k2 in ("C_ml_raw", "D_hybrid")}, group_col="g2")
        rows.append({"coarseness": k, "n_groups": int(d.g2.nunique()),
                     "auc_ml": t.loc["C_ml_raw", "auc_fold_mean"], "auc_hybrid": t.loc["D_hybrid", "auc_fold_mean"]})
    pd.DataFrame(rows).to_csv(OUT / "grouping_sensitivity.csv", index=False)
    res["grouping"] = rows
    SUMMARY["validation"] = res


# ===========================================================================
# Part 3  Monte Carlo on real cases: does Pf behave like a probability?
# ===========================================================================
def lognormal(mean, cov, n, rng):
    s = np.sqrt(np.log(1 + cov**2))
    return mean / np.sqrt(1 + cov**2) * np.exp(s * rng.standard_normal(n)) if mean > 0 else np.zeros(n)


def mc_case_pf(cases, cov_c=0.45, cov_phi=0.10, cov_gamma=0.05, rho=-0.5, n=400, seed=0):
    rng = np.random.default_rng(seed)
    pf = np.empty(len(cases))
    for i, r in enumerate(cases.itertuples()):
        z1 = rng.standard_normal(n)
        z2 = rho * z1 + np.sqrt(1 - rho**2) * rng.standard_normal(n)
        sc = np.sqrt(np.log(1 + cov_c**2))
        c = r.c / np.sqrt(1 + cov_c**2) * np.exp(sc * z1) if r.c > 0 else np.zeros(n)
        phi = np.clip(r.phi * (1 + cov_phi * np.clip(z2, -3, 3)), 0, 89) if r.phi > 0 else np.zeros(n)
        gamma = r.gamma * (1 + cov_gamma * rng.standard_normal(n))
        fs = bishop_fs_samples(r.beta, r.H, r.ru, gamma, c, phi, mean_params=(r.gamma, r.c, r.phi))
        pf[i] = (fs < 1).mean()
    return pf


def part3_mc_cases(cases):
    rows = []
    y = cases.failed.to_numpy()
    dom = E.in_domain(cases)
    det = (cases.fs < 1).astype(float).to_numpy()
    for name, mask in (("all", np.ones(len(cases), bool)), ("domain", dom)):
        rows.append({"predictor": "deterministic FS<1 (0/1)", "subset": name,
                     **{k: v for k, v in classification_metrics(y[mask], det[mask]).items()
                        if k in ("auc", "brier", "ece", "sensitivity", "specificity")}})
        rows.append({"predictor": "-FS (ranking only)", "subset": name,
                     "auc": roc_auc_score(y[mask], -cases.fs.to_numpy()[mask])})
    scen = {"base (c'0.45, phi'0.10, rho-0.5)": dict(),
            "low COV (c'0.25, phi'0.05)": dict(cov_c=0.25, cov_phi=0.05),
            "independent (rho 0)": dict(rho=0.0)}
    pf_store = {}
    for label, kw in scen.items():
        pf = mc_case_pf(cases, **kw)
        pf_store[label] = pf
        for name, mask in (("all", np.ones(len(cases), bool)), ("domain", dom)):
            m = classification_metrics(y[mask], pf[mask])
            rows.append({"predictor": f"Monte Carlo Pf, {label}", "subset": name,
                         **{k: m[k] for k in ("auc", "brier", "ece", "sensitivity", "specificity")}})
        print("Part 3", label, "done")
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "mc_on_cases.csv", index=False)
    base = pf_store["base (c'0.45, phi'0.10, rho-0.5)"]
    cases = cases.assign(pf_mc=base)
    cases.to_csv(OUT / "cases_with_pf_mc.csv", index=False)

    # Calibration table of raw Monte Carlo Pf (no fitting)
    bins = pd.cut(base, [-0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    calib = pd.DataFrame({"bin": bins, "failed": y, "pf": base}).groupby("bin").agg(
        n=("failed", "size"), mean_pf=("pf", "mean"), observed=("failed", "mean"))
    calib.to_csv(OUT / "mc_pf_calibration.csv")

    # Hybrid with Pf_MC as physics feature instead of ln FS
    d = E.add_physics_features(cases)
    d["pf_mc"] = base
    feats = E.RAW + ["pf_mc", "stability_number", "friction_ratio"]
    E.MONOTONE["pf_mc"] = 1
    models = {"D_hybrid": MODELS["D_hybrid"],
              "D_hybrid_pfMC": lambda seed: E.make_ml(feats, monotone=True, seed=seed)}
    tab, _ = cv(d, n_repeats=3, models=models)
    tab.to_csv(OUT / "hybrid_with_pf_mc.csv")
    SUMMARY["mc_on_cases"] = {"table": t.round(4).to_dict(orient="records"),
                              "calibration": calib.round(3).reset_index().astype(str).to_dict(orient="records"),
                              "hybrid_lnFS_vs_PfMC": tab[["auc_fold_mean", "ece_fold_mean"]].round(4).to_dict(orient="index")}


# ===========================================================================
# Part 4  Monte Carlo assumptions in the score model
# ===========================================================================
def full_factorial(sampler, n_mc=400, seed=0):
    rng = np.random.default_rng(seed)
    grid = np.array(list(itertools.product(range(1, 6), repeat=6)))
    pf = np.concatenate([(sampler(grid[i:i + 1000], n_mc, rng) < 1).mean(1) for i in range(0, len(grid), 1000)])
    df = pd.DataFrame(grid, columns=VARIABLES)
    df["pf"] = pf
    return df


def part4_assumptions():
    base_soil, base_root = dict(P2.SOIL_CLASSES), dict(P2.ROOT_COHESION)

    def v2(rho=-0.5, cov_scale=1.0, root_scale=1.0):
        def sampler(scores, n, rng):
            P2.SOIL_CLASSES.clear()
            P2.SOIL_CLASSES.update({k: replace(s, c_cov=s.c_cov * cov_scale, phi_cov=s.phi_cov * cov_scale)
                                    for k, s in base_soil.items()})
            P2.ROOT_COHESION.clear()
            P2.ROOT_COHESION.update({k: (lo * root_scale, hi * root_scale) for k, (lo, hi) in base_root.items()})
            return P2.sample_factor_of_safety_v2(scores, n, rng, rho)
        return sampler

    variants = {
        "v1 uniform ranges (slides)": sample_v1,
        "v2 base": v2(),
        "v2 rho(c',phi') = 0": v2(rho=0.0),
        "v2 rho(c',phi') = -0.7": v2(rho=-0.7),
        "v2 COV x 0.5": v2(cov_scale=0.5),
        "v2 COV x 1.5": v2(cov_scale=1.5),
        "v2 root cohesion x 0.4 (lower-bound sensitivity)": v2(root_scale=0.4),
    }
    rows = []
    for name, sampler in variants.items():
        grid = full_factorial(sampler)
        s1, _ = exact_sobol(grid, VARIABLES)
        w = s1["ST"] / s1["ST"].sum()
        fs = sampler(CASE[None, :], 20000, np.random.default_rng(1))[0]
        pf = float((fs < 1).mean())
        ri = float(np.sqrt(pf * VI_CASE))
        rows.append({"variant": name, "mean_pf_all_15625": grid.pf.mean(),
                     **{f"w_{v}": w[v] for v in VARIABLES},
                     "case_pf": pf, "case_ri": ri, "case_class": classify(ri)["class"]})
        print("Part 4", name, round(pf, 3), classify(ri)["class"])
    P2.SOIL_CLASSES.clear(); P2.SOIL_CLASSES.update(base_soil)
    P2.ROOT_COHESION.clear(); P2.ROOT_COHESION.update(base_root)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "mc_assumption_sensitivity.csv", index=False)

    # Sample size: Monte Carlo noise on a configuration near a class boundary
    rng = np.random.default_rng(5)
    rows = []
    for n in (50, 100, 400, 2000, 20000):
        pfs = [(P2.sample_factor_of_safety_v2(CASE[None, :], n, rng)[0] < 1).mean() for _ in range(200)]
        cls = [classify(np.sqrt(p * VI_CASE))["class"] for p in pfs]
        rows.append({"N": n, "pf_mean": np.mean(pfs), "pf_sd": np.std(pfs),
                     "share_class_IV": np.mean([c == "IV" for c in cls])})
    pd.DataFrame(rows).to_csv(OUT / "mc_sample_size.csv", index=False)
    SUMMARY["mc_assumptions"] = {"variants": t.round(4).to_dict(orient="records"), "sample_size": rows}


# ===========================================================================
# Part 5  How scoring propagates: observer uncertainty and HI definitions
# ===========================================================================
def part5_scoring():
    grid = pd.read_csv(ROOT / "results" / "engine" / "full_factorial_v2.csv")
    lookup = grid.set_index(VARIABLES).pf
    slide_w = np.array([0.538, 0.373, 0.016, 0.001, 0.018, 0.054])
    grid["hi_weighted"] = (grid[VARIABLES].to_numpy() @ slide_w - 1) / 4
    rho_s = stats.spearmanr(grid.hi_weighted, grid.pf).correlation
    cls_w = grid.hi_weighted.apply(lambda h: classify(np.sqrt(h * VI_CASE))["class"])
    cls_p = grid.pf.apply(lambda h: classify(np.sqrt(h * VI_CASE))["class"])
    agree = float((cls_w == cls_p).mean())
    order = ["I", "II", "III", "IV", "V"]
    higher = float((cls_p.map(order.index) > cls_w.map(order.index)).mean())

    # Observer misclassification: each score off by one class with probability p_err
    rng = np.random.default_rng(0)
    rows = []
    for p_err in (0.0, 0.1, 0.2, 0.3):
        n = 20000
        shift = rng.choice([-1, 0, 1], size=(n, 6), p=[p_err / 2, 1 - p_err, p_err / 2])
        s = np.clip(CASE + shift, 1, 5)
        pf = lookup.loc[[tuple(r) for r in s]].to_numpy()
        veg = s[:, 5]
        vi = (0.667 * 4 + 0.333 * veg - 1) / 4
        ri = np.sqrt(pf * vi)
        cls = pd.Series([classify(x)["class"] for x in ri]).value_counts(normalize=True)
        rows.append({"p_err": p_err, "pf_p05": np.percentile(pf, 5), "pf_median": np.median(pf),
                     "pf_p95": np.percentile(pf, 95), **{f"P(class {k})": float(cls.get(k, 0.0)) for k in order}})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "scoring_uncertainty_case.csv", index=False)
    SUMMARY["scoring"] = {"spearman_weightedHI_vs_Pf": float(rho_s), "class_agreement_weighted_vs_Pf": agree,
                          "share_Pf_class_higher": higher, "observer_error": t.round(4).to_dict(orient="records")}
    print("Part 5", SUMMARY["scoring"]["spearman_weightedHI_vs_Pf"], agree)


def main():
    cases = pd.read_csv(ROOT / "results" / "engine" / "cases_with_fs.csv").drop(columns=["pf_mc"], errors="ignore")
    part1_data(cases)
    part2_validation(cases)
    part3_mc_cases(cases)
    part4_assumptions()
    part5_scoring()
    (OUT / "audit_summary.json").write_text(json.dumps(SUMMARY, indent=2, default=float))
    print("written", OUT)


if __name__ == "__main__":
    main()
