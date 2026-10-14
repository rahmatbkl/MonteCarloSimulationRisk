"""
Jalankan seluruh pipeline Landslide Risk Index.

    python run_pipeline.py              # 1.200 x 400 = 480.000 evaluasi
    python run_pipeline.py --quick      # 300 x 200, untuk uji cepat

Output ditulis ke folder results/:
    simulation.csv        Pf per konfigurasi skor (dataset {X, Pf})
    weights.csv           bobot SRC, Sobol, RF, dan konsensus
    full_factorial.csv    Pf untuk SEMUA 5^6 = 15.625 kombinasi skor (lookup table)
    case_study.json       studi kasus lereng (lempung sedang, 45 derajat, 80 m)
    fig_*.png             grafik ringkasan
"""

import argparse
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from landslide_risk import config as cfg
from landslide_risk.risk_index import assess_site
from landslide_risk.sensitivity import run_sensitivity
from landslide_risk.simulation import run_simulation, sample_factor_of_safety

OUT = Path("results")

# Warna (palet kategorikal tervalidasi, urutan tetap) dan tinta teks
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
INK, INK_MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

# Bobot konsensus dari slide asli (untuk verifikasi angka studi kasus)
SLIDE_WEIGHTS = np.array([0.538, 0.373, 0.016, 0.001, 0.018, 0.054])

CASE_STUDY = {"soil": 3, "geometry": 4, "groundwater": 4,
              "rainfall": 4, "seismic": 1, "vegetation": 2}
CASE_DISTANCE_M = 80.0


def full_factorial_pf(n_mc, seed):
    """Pf untuk semua 15.625 kombinasi skor. Murah karena seluruhnya vektor."""
    rng = np.random.default_rng(seed)
    grid = np.array(list(itertools.product(range(1, 6), repeat=6)))
    pf = np.empty(len(grid))
    for start in range(0, len(grid), 2000):          # dipecah agar hemat memori
        block = grid[start:start + 2000]
        pf[start:start + 2000] = (sample_factor_of_safety(block, n_mc, rng) < 1).mean(1)
    df = pd.DataFrame(grid, columns=cfg.VARIABLES)
    df["pf"] = pf
    return df


def _style(ax, title, xlabel, ylabel):
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.set_xlabel(xlabel, color=INK_MUTED)
    ax.set_ylabel(ylabel, color=INK_MUTED)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=INK_MUTED)


def plot_results(sim, weights, grid):
    # 1. Distribusi Pf (bimodal?)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(sim["pf"], bins=20, color=SERIES[0], edgecolor="white", linewidth=2)
    _style(ax, f"Distribusi Pf (N = {len(sim)} konfigurasi)", "Pf", "Jumlah konfigurasi")
    fig.tight_layout(); fig.savefig(OUT / "fig_pf_distribution.png", dpi=150); plt.close(fig)

    # 2. Rata-rata Pf per skor (variabel lain dimarjinalkan)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for color, var in zip(SERIES, cfg.VARIABLES):
        curve = grid.groupby(var)["pf"].mean()
        ax.plot(curve.index, curve.values, color=color, linewidth=2, marker="o",
                markersize=6, label=cfg.VARIABLE_LABELS[var])
    _style(ax, "Rata-rata Pf per skor (full factorial)", "Skor (1 = aman, 5 = kritis)", "Rata-rata Pf")
    ax.set_xticks(range(1, 6)); ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK)
    fig.tight_layout(); fig.savefig(OUT / "fig_pf_by_score.png", dpi=150); plt.close(fig)

    # 3. Bobot per metode
    fig, ax = plt.subplots(figsize=(7, 4.5))
    cols = ["SRC", "Sobol_ST", "RF_perm", "consensus_geo"]
    names = ["SRC", "Sobol' ST", "RF permutation", "Konsensus (geo)"]
    y = np.arange(len(cfg.VARIABLES)); h = 0.2
    for k, (col, name) in enumerate(zip(cols, names)):
        ax.barh(y + (k - 1.5) * h, weights[col], height=h - 0.02, color=SERIES[k], label=name)
    ax.set_yticks(y, [cfg.VARIABLE_LABELS[v] for v in cfg.VARIABLES])
    ax.invert_yaxis()
    _style(ax, "Bobot sensitivitas per metode", "Bobot (dinormalisasi)", "")
    ax.legend(frameon=False, fontsize=8, labelcolor=INK)
    fig.tight_layout(); fig.savefig(OUT / "fig_weights.png", dpi=150); plt.close(fig)

    # 4. Matriks screening 2D: Tanah x Geometri (variabel lain dimarjinalkan)
    matrix = grid.pivot_table(index="geometry", columns="soil", values="pf", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(matrix.values, origin="lower", cmap="Blues", vmin=0, vmax=1,
                   extent=(0.5, 5.5, 0.5, 5.5))
    for (i, j), v in np.ndenumerate(matrix.values):
        ax.text(j + 1, i + 1, f"{v:.2f}", ha="center", va="center", fontsize=8,
                color="white" if v > 0.55 else INK)
    ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
    ax.set_title("Matriks screening: rata-rata Pf", color=INK, fontsize=11, loc="left")
    ax.set_xlabel("Skor Jenis Tanah", color=INK_MUTED); ax.set_ylabel("Skor Geometri", color=INK_MUTED)
    fig.colorbar(im, ax=ax, label="Pf")
    fig.tight_layout(); fig.savefig(OUT / "fig_screening_matrix.png", dpi=150); plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="ukuran kecil untuk uji cepat")
    args = parser.parse_args()
    n_cfg, n_mc = (300, 200) if args.quick else (cfg.N_OUTER_LHS, cfg.N_INNER_MC)
    OUT.mkdir(exist_ok=True)

    print(f"[1/4] Simulasi LHS x MC: {n_cfg} x {n_mc} = {n_cfg * n_mc:,} evaluasi FS")
    sim = run_simulation(n_cfg, n_mc)
    sim.to_csv(OUT / "simulation.csv", index=False)
    print(f"      Pf rata-rata = {sim.pf.mean():.3f}, median = {sim.pf.median():.3f}")

    print("[2/4] Analisis sensitivitas (SRC, Sobol', Random Forest)")
    weights, diag = run_sensitivity(sim)
    weights.to_csv(OUT / "weights.csv")
    print(weights.round(3).to_string())
    print("      Diagnostik R2:", {k: round(v, 3) for k, v in diag.items()})

    print("[3/4] Full factorial 5^6 = 15.625 kombinasi (lookup table Pf)")
    grid = full_factorial_pf(n_mc, cfg.RANDOM_SEED + 1)
    grid.to_csv(OUT / "full_factorial.csv", index=False)

    print("[4/4] Studi kasus lereng")
    ours = assess_site(CASE_STUDY, CASE_DISTANCE_M, weights["consensus_geo"].to_numpy())
    slide = assess_site(CASE_STUDY, CASE_DISTANCE_M, SLIDE_WEIGHTS)
    case = {"bobot_simulasi_ini": ours, "bobot_slide_asli": slide["weighted"]}
    (OUT / "case_study.json").write_text(json.dumps(case, indent=2, default=float))
    print(f"      Bobot slide     : HI = {slide['weighted']['hi']:.3f}, VI = {slide['vi']:.3f}, "
          f"RI = {slide['weighted']['ri']:.3f} (Kelas {slide['weighted']['class']})")
    print(f"      Bobot simulasi  : HI = {ours['weighted']['hi']:.3f}, "
          f"RI = {ours['weighted']['ri']:.3f} (Kelas {ours['weighted']['class']})")
    print(f"      Fisika langsung : HI = Pf = {ours['site_pf']['pf']:.3f} "
          f"[{ours['site_pf']['ci_low']:.3f}-{ours['site_pf']['ci_high']:.3f}], "
          f"RI = {ours['physics']['ri']:.3f} (Kelas {ours['physics']['class']})")

    plot_results(sim, weights, grid)
    print(f"Selesai. Hasil di folder {OUT}/")


if __name__ == "__main__":
    main()
