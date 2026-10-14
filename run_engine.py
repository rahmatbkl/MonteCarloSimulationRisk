"""
Jalankan machine engine v2 + protokol penerimaan.

    python run_engine.py

Langkah:
  1. Verifikasi fisika (infinite slope, Bishop vs Taylor/ACADS, FORM vs MC)
  2. Tabel Pf full factorial (model parameter v2) pada 3 seed + Sobol eksak
  3. Data kasus lereng nyata -> FS Bishop -> 4 model -> CV berkelompok
  4. Protokol penerimaan -> results/engine/acceptance.md
"""

import itertools
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from landslide_risk import engine as E
from landslide_risk.acceptance import Criterion, paired_bootstrap_auc_diff, to_frame, to_markdown
from landslide_risk.bishop import bishop_fs, bishop_fs_many
from landslide_risk.case_data import load_cases
from landslide_risk.config import VARIABLES
from landslide_risk.metrics import bootstrap_ci, classification_metrics
from landslide_risk.parameters_v2 import sample_factor_of_safety_v2
from landslide_risk.physics import factor_of_safety
from landslide_risk.reliability import RandomVariable, form, pf_statistics, wilson_interval
from landslide_risk.variance import exact_sobol

warnings.filterwarnings("ignore")
OUT = Path("results/engine")
OUT.mkdir(parents=True, exist_ok=True)
N_MC = 400
CASE_STUDY = [3, 4, 4, 4, 1, 2]


def full_factorial(seed, n_mc=N_MC):
    rng = np.random.default_rng(seed)
    grid = np.array(list(itertools.product(range(1, 6), repeat=6)))
    pf = np.concatenate([(sample_factor_of_safety_v2(grid[i:i + 1000], n_mc, rng) < 1).mean(1)
                         for i in range(0, len(grid), 1000)])
    df = pd.DataFrame(grid, columns=VARIABLES)
    df["pf"] = pf
    return df


def lognormal(mean, cov):
    s = np.sqrt(np.log(1 + cov**2))
    return stats.lognorm(s=s, scale=mean / np.sqrt(1 + cov**2))


def verification():
    out = []
    # V1 infinite slope analitik
    fs = factor_of_safety(0.0, 30.0, 19.0, 2.0, 35.0, 0.0, 0.0)
    err = abs(fs - np.tan(np.radians(30)) / np.tan(np.radians(35)))
    out.append(Criterion("1 Verification", "V1", "Infinite slope, c'=0 dry: FS = tan(phi)/tan(beta)",
                         err, "abs err < 1e-9", err < 1e-9, "Skempton & DeLory (1957)"))
    # V2 Bishop vs Taylor (phi = 0)
    errs = []
    for beta, ns in [(60, 0.191), (75, 0.219), (90, 0.261)]:
        f, _ = bishop_fs(18.0, 20.0, 0.0, beta, 10.0, 0.0)
        errs.append(abs(f - 20 / (ns * 180)) / (20 / (ns * 180)))
    out.append(Criterion("1 Verification", "V2", "Bishop vs Taylor stability chart (phi=0, beta 60-90 deg)",
                         max(errs), "max rel err <= 5%", max(errs) <= 0.05, "Taylor (1937)"))
    # V3 Bishop c = 0 -> infinite slope limit
    f, _ = bishop_fs(18.0, 0.0, 35.0, 30.0, 10.0, 0.0)
    e3 = abs(f / (np.tan(np.radians(35)) / np.tan(np.radians(30))) - 1)
    out.append(Criterion("1 Verification", "V3", "Bishop, c'=0: converges to tan(phi)/tan(beta)",
                         e3, "rel err <= 2%", e3 <= 0.02, "Duncan & Wright (2005)"))
    # V4 ACADS 1(a)
    f, _ = bishop_fs(20.0, 3.0, 19.6, 26.57, 10.0, 0.0)
    e4 = abs(f - 0.99) / 0.99
    out.append(Criterion("1 Verification", "V4", "Bishop vs ACADS benchmark 1(a) (FS ref 0.99)",
                         e4, "rel err <= 3%", e4 <= 0.03, "Donald & Giam (1989), ACADS"))
    # V5 FORM vs Monte Carlo
    V = [RandomVariable("c", lognormal(8, 0.4)), RandomVariable("phi", lognormal(28, 0.1)),
         RandomVariable("gamma", stats.norm(18.5, 0.925)), RandomVariable("m", stats.uniform(0.3, 0.5))]
    R = np.eye(4); R[0, 1] = R[1, 0] = -0.5
    z = 2.0 / np.cos(np.radians(40))
    g = lambda x: factor_of_safety(x["c"], x["phi"], x["gamma"], z, 40, x["m"], 0.05) - 1
    f_form = form(g, V, R)
    rng = np.random.default_rng(0)
    u = rng.standard_normal((200_000, 4)) @ np.linalg.cholesky(R).T
    x = {v.name: v.from_normal(u[:, i]) for i, v in enumerate(V)}
    mc = pf_statistics(factor_of_safety(x["c"], x["phi"], x["gamma"], z, 40, x["m"], 0.05))
    d5 = abs(f_form["pf"] - mc["pf"])
    out.append(Criterion("1 Verification", "V5", "FORM vs Monte Carlo (correlated lognormal inputs)",
                         d5, "abs diff Pf <= 0.01", d5 <= 0.01, "Hasofer & Lind (1974)"))
    return out, {"form": f_form, "mc": mc}


def numerical(grids, sobols):
    out = []
    lo, hi = wilson_interval(N_MC // 2, N_MC)
    out.append(Criterion("2 Numerical", "N1", f"Max 95% CI half-width of Pf per configuration (N={N_MC})",
                         (hi - lo) / 2, "<= 0.05", (hi - lo) / 2 <= 0.05, "Wilson (1927)"))
    diffs = [np.abs(grids[0].pf - g.pf).mean() for g in grids[1:]]
    out.append(Criterion("2 Numerical", "N2", "Seed stability: mean |dPf| between seeds",
                         max(diffs), "<= 0.02", max(diffs) <= 0.02, "Reproducibility (this protocol)"))
    dS = max((sobols[0]["ST"] - s["ST"]).abs().max() for s in sobols[1:])
    out.append(Criterion("2 Numerical", "N3", "Seed stability: max |dS_T| of Sobol indices",
                         dS, "<= 0.02", dS <= 0.02, "Archer, Saltelli & Sobol (1997)"))
    fs = sample_factor_of_safety_v2(np.array([CASE_STUDY]), 20_000, np.random.default_rng(1))[0]
    st = pf_statistics(fs)
    out.append(Criterion("2 Numerical", "N4", "Site Pf estimator COV (case study, N=20,000)",
                         st["cov"], "<= 0.10", st["cov"] <= 0.10, "N = (1-Pf)/(COV^2 Pf)"))
    return out, st


def validation(cases):
    out = []
    dom = cases[E.in_domain(cases)].reset_index(drop=True)
    results = {}
    for label, data in (("all", cases), ("domain", dom)):
        folds_g, oof_g = E.cross_validate(data, n_repeats=5, grouped=True)
        folds_r, oof_r = E.cross_validate(data, n_repeats=5, grouped=False)
        folds_g.to_csv(OUT / f"cv_folds_grouped_{label}.csv", index=False)
        oof_g.assign(failed=data.failed.values).to_csv(OUT / f"oof_grouped_{label}.csv", index=False)
        pooled = {m: classification_metrics(data.failed, oof_g[m]) for m in oof_g}
        pooled_r = {m: classification_metrics(data.failed, oof_r[m]) for m in oof_r}
        results[label] = {"data": data, "oof": oof_g, "pooled": pooled, "pooled_random": pooled_r,
                          "summary": E.summarize(folds_g)}
        pd.DataFrame(pooled).T.to_csv(OUT / f"pooled_metrics_grouped_{label}.csv")
        pd.DataFrame(pooled_r).T.to_csv(OUT / f"pooled_metrics_random_{label}.csv")

    r = results["domain"]
    y, p = r["data"].failed, r["oof"]["D_hybrid"]
    auc = r["pooled"]["D_hybrid"]["auc"]
    lo, hi = bootstrap_ci(y, p, "auc")
    out.append(Criterion("3 Validation", "A1", "Hybrid AUC, grouped CV, soil domain (95% CI lower bound)",
                         lo, ">= 0.70 (min), point >= 0.80", lo >= 0.70 and auc >= 0.80,
                         "Hosmer & Lemeshow (2000)"))
    d, dlo, dhi = paired_bootstrap_auc_diff(y, p, r["oof"]["A_heuristic"])
    out.append(Criterion("3 Validation", "A2", "Hybrid beats heuristic/AHP-like index (dAUC, CI lower bound)",
                         dlo, "> 0", dlo > 0, "Paired bootstrap"))
    d2, d2lo, _ = paired_bootstrap_auc_diff(y, p, r["oof"]["B_physics"])
    out.append(Criterion("3 Validation", "A3", "Hybrid beats physics-only FS (dAUC, CI lower bound)",
                         d2lo, "> 0", d2lo > 0, "Paired bootstrap"))
    ece = r["pooled"]["D_hybrid"]["ece"]
    out.append(Criterion("3 Validation", "A4", "Calibration: expected calibration error (pooled OOF)",
                         ece, "<= 0.10", ece <= 0.10, "Guo et al. (2017)"))
    brier = r["pooled"]["D_hybrid"]["brier"]
    out.append(Criterion("3 Validation", "A5", "Brier score (no-skill = 0.25)",
                         brier, "<= 0.20", brier <= 0.20, "Brier (1950)"))
    gap = r["pooled_random"]["D_hybrid"]["auc"] - auc
    out.append(Criterion("3 Validation", "A6", "Leakage gap: AUC(random CV) - AUC(grouped CV)",
                         gap, "<= 0.05", gap <= 0.05, "Brenning (2005)"))

    # A7 konsistensi fisika: naikkan c' 10% -> peluang gagal tidak boleh naik
    model = E.fit_final(r["data"])
    base = r["data"]
    pert = base.copy(); pert["c"] = pert.c * 1.10
    pert["fs"] = bishop_fs_many(pert)
    pert = E.add_physics_features(pert)
    viol = (model.predict_proba(pert)[:, 1] > model.predict_proba(base)[:, 1] + 1e-9).mean()
    out.append(Criterion("3 Validation", "A7", "Physical consistency: share of cases where +10% c' raises P(fail)",
                         viol, "= 0", viol == 0, "Monotone constraints (this engine)"))
    out.append(Criterion("3 Validation", "A8", "Spatial/temporal validation on Indonesian landslide inventory",
                         np.nan, "AUC >= 0.80 on spatial blocks", None,
                         "Reichenbach et al. (2018) SQL>=5; pending data (Samodra 2024)"))
    with open(OUT / "hybrid_engine.pkl", "wb") as fh:
        pickle.dump(model, fh)
    return out, results


def main():
    print("[1/4] Verifikasi fisika")
    crit_v, ver = verification()

    print("[2/4] Full factorial v2 (3 seed) + Sobol eksak")
    grids = [full_factorial(seed) for seed in (0, 1, 2)]
    grids[0].to_csv(OUT / "full_factorial_v2.csv", index=False)
    sob = [exact_sobol(g, VARIABLES) for g in grids]
    sob[0][0].to_csv(OUT / "sobol_exact.csv")
    sob[0][1].to_csv(OUT / "sobol_second_order.csv")
    crit_n, site = numerical(grids, [s[0] for s in sob])
    print(sob[0][0].round(3).to_string())

    print("[3/4] Kasus lereng nyata: Bishop FS + 4 model, CV berkelompok")
    cases = load_cases()
    cases["fs"] = bishop_fs_many(cases)
    cases = E.add_physics_features(cases)
    cases.to_csv(OUT / "cases_with_fs.csv", index=False)
    crit_a, res = validation(cases)
    for label in ("all", "domain"):
        print(f"  pooled metrics ({label}):")
        print(pd.DataFrame(res[label]["pooled"]).T[["auc", "accuracy", "brier", "ece", "tss"]].round(3).to_string())

    print("[4/4] Protokol penerimaan")
    criteria = crit_v + crit_n + crit_a
    to_frame(criteria).to_csv(OUT / "acceptance.csv", index=False)
    (OUT / "acceptance.md").write_text(to_markdown(criteria, "Engine acceptance report"))
    (OUT / "site_case_study.json").write_text(json.dumps(
        {"scores": CASE_STUDY, **{k: float(v) for k, v in site.items()},
         "form_check": {"form_pf": ver["form"]["pf"], "mc_pf": ver["mc"]["pf"]}}, indent=2))
    print(to_markdown(criteria))


if __name__ == "__main__":
    main()
