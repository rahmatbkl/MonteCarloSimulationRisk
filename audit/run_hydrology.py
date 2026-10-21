"""
Static vs transient hydrology: effect on the model, and a plausibility check
against published rainfall thresholds.

    python audit/run_hydrology.py   ->  results/hydrology/*

1. Full factorial (5^6 scores x N=400) with static and transient hydrology:
   mean Pf, main effects, exact Sobol' indices, case-study Pf.
2. Pressure-head and FS response in time for a reference slope.
3. Model-implied intensity-duration (I-D) thresholds per soil class, compared
   with verified empirical thresholds (see research_notes/Verifikasi referensi/
   transient_hydrology.md). This is a PLAUSIBILITY check, not a validation:
   the empirical thresholds come from other slopes and rainfall products.
"""

import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from landslide_risk import parameters_v2 as P2
from landslide_risk.config import VARIABLES
from landslide_risk.hydrology import pressure_head
from landslide_risk.physics import effective_root_cohesion, factor_of_safety
from landslide_risk.variance import exact_sobol

OUT = ROOT / "results" / "hydrology"
OUT.mkdir(parents=True, exist_ok=True)
CASE = np.array([[3, 4, 4, 4, 1, 2]])
SUMMARY = {}

# Verified empirical thresholds (I in mm/h, D in h)
THRESHOLDS = {
    "Caine (1980) global":           lambda D: 14.82 * D ** -0.39,
    "Guzzetti et al. (2008) global": lambda D: 2.20 * D ** -0.44,
    "Banjarmangu (Irawan et al. 2019)": lambda D: 43.2 * D ** -0.87,
}
POINTS = {   # daily / 3-day totals converted to mean intensity
    "Hidayat et al. 2019: 1-day 61 mm": (24, 61 / 24), "Hidayat et al. 2019: 3-day 91 mm": (72, 91 / 72),
    "Yuniawan et al. 2022: 1-day 30 mm": (24, 30 / 24), "Yuniawan et al. 2022: 3-day 64 mm": (72, 64 / 72),
}


def full_factorial(hydrology, seed=0, n_mc=400):
    rng = np.random.default_rng(seed)
    grid = np.array(list(itertools.product(range(1, 6), repeat=6)))
    pf = np.concatenate([(P2.sample_factor_of_safety_v2(grid[i:i + 1000], n_mc, rng, hydrology=hydrology) < 1).mean(1)
                         for i in range(0, len(grid), 1000)])
    df = pd.DataFrame(grid, columns=VARIABLES)
    df["pf"] = pf
    return df


def part1_compare():  # noqa: C901
    rows, mains = [], {}
    for h in ("static", "transient"):
        g = full_factorial(h)
        g.to_csv(OUT / f"full_factorial_{h}.csv", index=False)
        s, _ = exact_sobol(g, VARIABLES)
        w = s["ST"] / s["ST"].sum()
        fs = P2.sample_factor_of_safety_v2(CASE, 20000, np.random.default_rng(1), hydrology=h)[0]
        rows.append({"hydrology": h, "mean_pf": g.pf.mean(), "case_pf": float((fs < 1).mean()),
                     **{f"S1_{v}": s.loc[v, "S1"] for v in VARIABLES}, **{f"ST_{v}": s.loc[v, "ST"] for v in VARIABLES},
                     **{f"w_{v}": w[v] for v in VARIABLES}})
        mains[h] = {v: g.groupby(v).pf.mean().round(4).tolist() for v in VARIABLES}
        # rainfall effect conditional on permeable soils (where infiltration is not Ks-limited)
        mains[h]["rainfall_given_soil1"] = g[g.soil == 1].groupby("rainfall").pf.mean().round(4).tolist()
        mains[h]["rainfall_given_soil5"] = g[g.soil == 5].groupby("rainfall").pf.mean().round(4).tolist()
        print(h, "mean Pf", round(g.pf.mean(), 3), "case", rows[-1]["case_pf"], "w_rain", round(w["rainfall"], 4))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "static_vs_transient.csv", index=False)
    SUMMARY["compare"] = t.round(4).to_dict(orient="records")
    SUMMARY["main_effects"] = mains


def reference_slope(soil_class, fs_target=1.2):
    """
    Marginally stable reference slope for one soil class: class-mean strength,
    H = 1.5 m, initial m0 = 0.2, c_r = 2 kPa, and the slope angle beta chosen so
    that FS before rain equals fs_target. This makes I-D thresholds comparable
    between soil classes (each starts equally close to failure).
    """
    sc = P2.SOIL_CLASSES[soil_class]
    r = dict(c=sc.c_mean, phi=sc.phi_mean, gamma=sc.gamma_mean, ks=sc.ks_median,
             beta=35.0, H=1.5, m0=0.2, c_root=2.0, root_depth=1.0, kh=0.0)
    lo, hi = 5.0, 80.0
    for _ in range(60):
        r["beta"] = (lo + hi) / 2
        lo, hi = (r["beta"], hi) if min_fs(r, 0.0, 24, 50) > fs_target else (lo, r["beta"])
    return r


def min_fs(r, rain_mm_h, dur_h, d0_ratio, factors=(1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0)):
    z = r["H"] / np.cos(np.radians(r["beta"]))
    cos2 = np.cos(np.radians(r["beta"])) ** 2
    T = dur_h * 3600.0
    iz = rain_mm_h / 1000.0 / 3600.0
    d0 = r["ks"] * d0_ratio
    psi = max(pressure_head(z, z * (1 - r["m0"]), r["beta"], iz, r["ks"], d0, f * T, T) for f in factors)
    m = float(np.clip(psi / (z * cos2), 0, 1))
    cr = effective_root_cohesion(r["c_root"], r["root_depth"], r["H"])
    return float(factor_of_safety(r["c"], r["phi"], r["gamma"], z, r["beta"], m, r["kh"], cr))


def part2_time_response():
    r = reference_slope(1)                     # permeable class: rain is not Ks-limited
    z = r["H"] / np.cos(np.radians(r["beta"]))
    T = 24 * 3600.0
    iz = min(2.0 / 3600 / 1000, r["ks"])       # 2 mm/h for 24 h, capped at Ks
    rows = []
    for ratio in (5, 50, 200):
        d0 = r["ks"] * ratio
        for th in np.linspace(0, 96, 97):
            t = th * 3600.0
            rows.append({"d0_ratio": ratio, "t_h": th,
                         "psi_slip": float(pressure_head(z, z * (1 - r["m0"]), r["beta"], iz, r["ks"], d0, t, T)),
                         "psi_mid": float(pressure_head(z / 2, z * (1 - r["m0"]), r["beta"], iz, r["ks"], d0, t, T))})
    pd.DataFrame(rows).to_csv(OUT / "time_response.csv", index=False)


def critical_intensity(r, dur_h, d0_ratio):
    """Smallest intensity (mm/h) giving min FS < 1; nan if even I = Ks is not enough."""
    if min_fs(r, 0.0, dur_h, d0_ratio) < 1:
        return 0.0
    i_max = r["ks"] * 1000 * 3600                # Ks in mm/h: more rain is runoff
    if min_fs(r, i_max, dur_h, d0_ratio) >= 1:
        return np.nan
    lo, hi = 0.0, i_max
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if min_fs(r, mid, dur_h, d0_ratio) < 1 else (mid, hi)
    return hi


def part3_thresholds():
    rows = []
    durations = [1, 3, 6, 12, 24, 48, 72, 120, 240]
    for soil in (1, 2, 3, 4):
        r = reference_slope(soil)
        for ratio in (5, 50, 200):
            for D in durations:
                rows.append({"soil": soil, "beta_ref": r["beta"], "ks_mm_h": r["ks"] * 3.6e6, "d0_ratio": ratio, "D_h": D,
                             "fs_dry": min_fs(r, 0.0, D, ratio), "I_crit_mm_h": critical_intensity(r, D, ratio)})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "model_ID_thresholds.csv", index=False)
    emp = pd.DataFrame([{"threshold": k, "D_h": D, "I_mm_h": f(D)} for k, f in THRESHOLDS.items() for D in durations])
    emp.to_csv(OUT / "empirical_ID_thresholds.csv", index=False)
    SUMMARY["thresholds"] = t.round(4).to_dict(orient="records")


def main():
    part1_compare()
    part2_time_response()
    part3_thresholds()
    (OUT / "hydrology_summary.json").write_text(json.dumps(SUMMARY, indent=2, default=float))
    print("written", OUT)


if __name__ == "__main__":
    main()
