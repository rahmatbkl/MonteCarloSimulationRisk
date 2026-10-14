"""
Jalankan machine engine v2 + protokol penerimaan (versi teraudit).

    python run_engine.py

Langkah:
  1. Verifikasi fisika (infinite slope, Bishop vs Taylor/ACADS, FORM vs MC,
     implementasi batasan monoton)
  2. Tabel Pf full factorial (model parameter v2) pada 3 seed + Sobol eksak
  3. Data kasus lereng nyata -> FS Bishop -> 5 model -> CV berkelompok
     ANALISIS UTAMA = SELURUH data (ditetapkan sebelumnya). Subset "domain"
     dipilih SETELAH melihat hasil, jadi hanya dilaporkan sebagai sekunder.
  4. Pf Monte Carlo pada kasus nyata (uji kalibrasi probabilitas fisika)
  5. Protokol penerimaan -> results/engine/acceptance.md
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
from landslide_risk.acceptance import Criterion, group_bootstrap_auc, to_frame, to_markdown
from landslide_risk.bishop import bishop_fs, bishop_fs_many
from landslide_risk.case_data import load_cases
from landslide_risk.case_mc import case_pf
from landslide_risk.config import VARIABLES
from landslide_risk.metrics import classification_metrics
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


def verification(cases):
    out = []
    fs = factor_of_safety(0.0, 30.0, 19.0, 2.0, 35.0, 0.0, 0.0)
    err = abs(fs - np.tan(np.radians(30)) / np.tan(np.radians(35)))
    out.append(Criterion("1 Verification", "V1", "Infinite slope, c'=0 dry: FS = tan(phi)/tan(beta)",
                         err, "abs err < 1e-9", err < 1e-9, "Skempton & DeLory (1957)", "analytic"))
    errs = []
    for beta, ns in [(45, 0.170), (60, 0.191), (75, 0.219), (90, 0.261)]:
        f, _ = bishop_fs(18.0, 20.0, 0.0, beta, 10.0, 0.0)
        errs.append(abs(f - 20 / (ns * 180)) / (20 / (ns * 180)))
    out.append(Criterion("1 Verification", "V2", "Bishop vs Taylor chart, phi=0, beta 45/60/75/90 deg "
                         f"(errors {', '.join(f'{e:.1%}' for e in errs)})",
                         max(errs), "max rel err <= 5%", max(errs) <= 0.05,
                         "Taylor (1937); 45 deg limited by search depth", "literature"))
    f, _ = bishop_fs(18.0, 0.0, 35.0, 30.0, 10.0, 0.0)
    e3 = abs(f / (np.tan(np.radians(35)) / np.tan(np.radians(30))) - 1)
    out.append(Criterion("1 Verification", "V3", "Bishop, c'=0: converges to tan(phi)/tan(beta)",
                         e3, "rel err <= 2%", e3 <= 0.02, "Duncan & Wright (2005)", "analytic"))
    f, _ = bishop_fs(20.0, 3.0, 19.6, 26.57, 10.0, 0.0)
    e4 = abs(f - 1.00) / 1.00
    out.append(Criterion("1 Verification", "V4", "Bishop vs ACADS 1(a) (reference FS ~1.00, recalled, unverified)",
                         e4, "rel err <= 3%", e4 <= 0.03, "Donald & Giam (1989)", "literature"))
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
    out.append(Criterion("1 Verification", "V5", "FORM vs Monte Carlo (one test case, Pf ~0.97)",
                         d5, "abs diff Pf <= 0.01", d5 <= 0.01, "Hasofer & Lind (1974)", "project-set"))
    # V6 (was A7): guaranteed by construction, so it verifies the implementation only
    dom = cases[E.in_domain(cases)].reset_index(drop=True)
    model = E.fit_final(cases)
    pert = cases.copy(); pert["c"] = pert.c * 1.10
    pert["fs"] = bishop_fs_many(pert)
    pert = E.add_physics_features(pert)
    viol = (model.predict_proba(pert)[:, 1] > model.predict_proba(cases)[:, 1] + 1e-9).mean()
    out.append(Criterion("1 Verification", "V6", "Monotone constraints implemented: +10% c' never raises P(fail)",
                         viol, "= 0", viol == 0, "Guaranteed by construction (not a validation)", "analytic"))
    with open(OUT / "hybrid_engine.pkl", "wb") as fh:
        pickle.dump(model, fh)
    return out, {"form": f_form, "mc": mc}


def numerical(grids, sobols):
    out = []
    lo, hi = wilson_interval(N_MC // 2, N_MC)
    out.append(Criterion("2 Numerical", "N1", f"Max 95% CI half-width of Pf per configuration (N={N_MC})",
                         (hi - lo) / 2, "<= 0.05", (hi - lo) / 2 <= 0.05, "Wilson (1927); fixed by choice of N",
                         "analytic"))
    diffs = [np.abs(grids[0].pf - g.pf).mean() for g in grids[1:]]
    out.append(Criterion("2 Numerical", "N2", "Seed stability: mean |dPf| between seeds",
                         max(diffs), "<= 0.02", max(diffs) <= 0.02, "Reproducibility", "project-set"))
    dS = max((sobols[0]["ST"] - s["ST"]).abs().max() for s in sobols[1:])
    out.append(Criterion("2 Numerical", "N3", "Seed stability: max |dS_T| of Sobol indices",
                         dS, "<= 0.02", dS <= 0.02, "Archer, Saltelli & Sobol (1997)", "project-set"))
    fs = sample_factor_of_safety_v2(np.array([CASE_STUDY]), 20_000, np.random.default_rng(1))[0]
    st = pf_statistics(fs)
    out.append(Criterion("2 Numerical", "N4", "Site Pf estimator COV (case study, N=20,000)",
                         st["cov"], "<= 0.10", st["cov"] <= 0.10, "N = (1-Pf)/(COV^2 Pf)", "literature"))
    return out, st


def validation(cases):
    out, results = [], {}
    dom = cases[E.in_domain(cases)].reset_index(drop=True)
    for label, data in (("all", cases), ("domain", dom)):
        folds_g, oof_g, pooled_g = E.cross_validate(data, n_repeats=5, grouped=True)
        _, _, pooled_r = E.cross_validate(data, n_repeats=5, grouped=False)
        folds_g.to_csv(OUT / f"cv_folds_grouped_{label}.csv", index=False)
        oof_g.assign(failed=data.failed.values, group=data.group.values).to_csv(
            OUT / f"oof_grouped_{label}.csv", index=False)
        pooled_g.to_csv(OUT / f"pooled_metrics_grouped_{label}.csv")
        pooled_r.to_csv(OUT / f"pooled_metrics_random_{label}.csv")
        results[label] = {"data": data, "oof": oof_g, "pooled": pooled_g, "pooled_random": pooled_r}

    r = results["all"]                       # PRIMARY, pre-specified
    y, grp, oof, pm = r["data"].failed, r["data"].group, r["oof"], r["pooled"]
    auc = pm.loc["D_hybrid", "auc"]
    _, lo, _ = group_bootstrap_auc(y, grp, oof["D_hybrid"])
    out.append(Criterion("3 Validation", "A1", "Hybrid AUC, grouped CV, ALL cases (group-bootstrap 95% CI lower bound)",
                         lo, ">= 0.70 and point >= 0.80", lo >= 0.70 and auc >= 0.80,
                         "Hosmer & Lemeshow (2000)", "literature"))
    _, dlo, _ = group_bootstrap_auc(y, grp, oof["D_hybrid"], oof["E_logistic"])
    out.append(Criterion("3 Validation", "A2", "Hybrid beats logistic regression on raw inputs (dAUC, CI lower bound)",
                         dlo, "> 0", dlo > 0, "Fair statistical baseline", "project-set"))
    _, d2lo, _ = group_bootstrap_auc(y, grp, oof["D_hybrid"], oof["B_physics"])
    out.append(Criterion("3 Validation", "A3", "Hybrid beats physics-only FS (dAUC, CI lower bound)",
                         d2lo, "> 0", d2lo > 0, "Paired group bootstrap", "project-set"))
    ece = pm.loc["D_hybrid", "ece"]
    out.append(Criterion("3 Validation", "A4", "Hybrid calibration: ECE on single-pass OOF predictions",
                         ece, "<= 0.10", ece <= 0.10, "Guo et al. (2017)", "project-set"))
    brier = pm.loc["D_hybrid", "brier"]
    out.append(Criterion("3 Validation", "A5", "Hybrid Brier score (no-skill = 0.25)",
                         brier, "<= 0.20", brier <= 0.20, "Brier (1950)", "project-set"))
    gap = r["pooled_random"].loc["D_hybrid", "auc"] - auc
    out.append(Criterion("3 Validation", "A6", "Leakage gap: AUC(random CV) - AUC(grouped CV)",
                         gap, "<= 0.05", gap <= 0.05, "Brenning (2005)", "project-set"))

    print("  Monte Carlo Pf on real cases (this takes ~2 min)")
    pf = case_pf(cases)
    cases = cases.assign(pf_mc=pf)
    cases.to_csv(OUT / "cases_with_fs.csv", index=False)
    m = classification_metrics(cases.failed, pf)
    out.append(Criterion("3 Validation", "A7", "Physics Monte Carlo Pf is a calibrated probability (ECE of raw Pf, no fitting)",
                         m["ece"], "<= 0.10", m["ece"] <= 0.10, "Probability must mean frequency", "project-set"))
    out.append(Criterion("3 Validation", "A8", "Score-based HI (6 field scores -> Pf) validated against observed landslides",
                         np.nan, "AUC >= 0.80 and ECE <= 0.10", None,
                         "No outcome data with field scores exists yet", "literature"))
    out.append(Criterion("3 Validation", "A9", "Spatial/temporal validation on an Indonesian landslide inventory",
                         np.nan, "AUC >= 0.80 on spatial blocks", None,
                         "Reichenbach et al. (2018) SQL >= 5; data: Samodra (2024)", "literature"))
    results["pf_mc_metrics"] = m
    return out, results


def main():
    print("[1/4] Kasus lereng nyata + FS Bishop")
    cases = load_cases()
    cases["fs"] = bishop_fs_many(cases)
    cases = E.add_physics_features(cases)

    print("[2/4] Verifikasi fisika")
    crit_v, ver = verification(cases)

    print("[3/4] Full factorial v2 (3 seed) + Sobol eksak")
    grids = [full_factorial(seed) for seed in (0, 1, 2)]
    grids[0].to_csv(OUT / "full_factorial_v2.csv", index=False)
    sob = [exact_sobol(g, VARIABLES) for g in grids]
    sob[0][0].to_csv(OUT / "sobol_exact.csv")
    sob[0][1].to_csv(OUT / "sobol_second_order.csv")
    crit_n, site = numerical(grids, [s[0] for s in sob])

    print("[4/4] Validasi: 5 model, CV berkelompok, Pf Monte Carlo pada kasus")
    crit_a, res = validation(cases)
    for label in ("all", "domain"):
        print(f"  single-pass OOF metrics ({label}):")
        print(res[label]["pooled"][["auc", "accuracy", "sensitivity", "specificity", "brier", "ece"]].round(3).to_string())

    criteria = crit_v + crit_n + crit_a
    to_frame(criteria).to_csv(OUT / "acceptance.csv", index=False)
    (OUT / "acceptance.md").write_text(to_markdown(criteria, "Engine acceptance report (audited)"))
    (OUT / "site_case_study.json").write_text(json.dumps(
        {"scores": CASE_STUDY, **{k: float(v) for k, v in site.items()},
         "form_check": {"form_pf": ver["form"]["pf"], "mc_pf": ver["mc"]["pf"]}}, indent=2))
    print(to_markdown(criteria))


if __name__ == "__main__":
    main()
