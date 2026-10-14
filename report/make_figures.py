"""
Generate all publication-quality figures for the technical report.

    python report/make_figures.py        (run run_engine.py first)

Figures are written to report/figures/ as 300-dpi PNG.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from sklearn.calibration import calibration_curve
from sklearn.inspection import permutation_importance, partial_dependence
from sklearn.metrics import roc_curve

from landslide_risk import engine as E
from landslide_risk.bishop import bishop_fs
from landslide_risk.config import VARIABLES
from landslide_risk.parameters_v2 import SOIL_CLASSES, sample_physical, fs_from_parameters
from landslide_risk.physics import factor_of_safety
from landslide_risk.reliability import convergence_curve, wilson_interval
from landslide_risk.variance import exact_sobol

RES = ROOT / "results" / "engine"
FIG = ROOT / "report" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Style
# --------------------------------------------------------------------------
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
SERIES = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
INK, MUTED, GRID, PANEL = "#0b0b0b", "#52514e", "#e4e3df", "#f4f3ef"

plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 9,
    "axes.titlesize": 10, "axes.labelsize": 9, "legend.fontsize": 7.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "savefig.dpi": 300, "savefig.bbox": "tight", "figure.dpi": 110,
})
LABEL = {"soil": "Soil type $X_1$", "geometry": "Slope geometry $X_2$",
         "groundwater": "Groundwater $X_3$", "rainfall": "Rainfall $X_4$",
         "seismic": "Seismic load $X_5$", "vegetation": "Vegetation $X_6$"}
SHORT = {"soil": "$X_1$ soil", "geometry": "$X_2$ geom.", "groundwater": "$X_3$ GWT",
         "rainfall": "$X_4$ rain", "seismic": "$X_5$ seismic", "vegetation": "$X_6$ veg."}


def panel_label(ax, s):
    ax.text(-0.12, 1.06, s, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom")


def save(fig, name):
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)
    print("  saved", name)


def box(ax, x, y, w, h, text, fc="white", ec=MUTED, fs=8, bold=False, tc=INK):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.012,rounding_size=0.015",
                                fc=fc, ec=ec, lw=0.9))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, p, q, color=MUTED, style="-|>", lw=0.9, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=9, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=5))


# Reference state for gradient / Hessian analysis (medium clay, steep slope)
REF = {"c": 9.0, "phi": 25.0, "gamma": 17.0, "beta": 40.0, "H": 2.0, "m": 0.5, "kh": 0.05, "cr": 3.0}
SIGMA = {"c": 4.5, "phi": 3.75, "gamma": 0.85, "beta": 2.9, "H": 0.58, "m": 0.072, "kh": 0.015, "cr": 0.72}
SYM = {"c": "$c'$", "phi": r"$\phi'$", "gamma": r"$\gamma$", "beta": r"$\beta$", "H": "$H$",
       "m": "$m$", "kh": "$k_h$", "cr": "$c_r$"}


def fs_point(p):
    z = p["H"] / np.cos(np.radians(p["beta"]))
    return factor_of_safety(p["c"], p["phi"], p["gamma"], z, p["beta"], p["m"], p["kh"], p["cr"])


def gradient(p, keys, rel=1e-4):
    g = {}
    for k in keys:
        h = max(abs(p[k]) * rel, 1e-6)
        up, dn = dict(p), dict(p)
        up[k] += h; dn[k] -= h
        g[k] = (fs_point(up) - fs_point(dn)) / (2 * h)
    return g


def hessian(p, keys, rel=1e-3):
    n = len(keys)
    Hm = np.zeros((n, n))
    for i, a in enumerate(keys):
        for j, b in enumerate(keys):
            ha, hb = max(abs(p[a]) * rel, 1e-5), max(abs(p[b]) * rel, 1e-5)
            def f(da, db):
                q = dict(p); q[a] += da; q[b] += db
                return fs_point(q)
            Hm[i, j] = (f(ha, hb) - f(ha, -hb) - f(-ha, hb) + f(-ha, -hb)) / (4 * ha * hb)
    return Hm


# --------------------------------------------------------------------------
# F1  Conceptual framework
# --------------------------------------------------------------------------
def fig_concept():
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    cols = [0.10, 0.30, 0.50, 0.70, 0.90]
    titles = ["1  Field input", "2  Physics", "3  Simulation", "4  Learning & analytics", "5  Decision"]
    fills = ["#e8f0fb", "#fde9e1", "#e3f5ee", "#f1effb", "#fbeef3"]
    for x, t, f in zip(cols, titles, fills):
        ax.add_patch(Rectangle((x - 0.095, 0.05), 0.19, 0.82, fc=f, ec="none"))
        ax.text(x, 0.92, t, ha="center", fontsize=9, fontweight="bold")
    box(ax, cols[0], 0.70, 0.17, 0.16, "Score sheet\n$X_1\\ldots X_6 \\in\\{1..5\\}$\n(Varnes classes)")
    box(ax, cols[0], 0.42, 0.17, 0.16, "Measured\nparameters\n$c', \\phi', \\gamma, \\beta, H$")
    box(ax, cols[0], 0.15, 0.17, 0.13, "Exposure\nsettlement distance")
    box(ax, cols[1], 0.70, 0.17, 0.16, "Parameter model\nlognormal / trunc.-\nnormal + copula")
    box(ax, cols[1], 0.42, 0.17, 0.16, "Limit equilibrium\ninfinite slope |\nBishop simplified")
    box(ax, cols[2], 0.70, 0.17, 0.16, "Monte Carlo\n$P_f=P[FS<1]$\nWilson CI, $\\beta$")
    box(ax, cols[2], 0.42, 0.17, 0.16, "Full-factorial\n$5^6$ score space\nexact Sobol'")
    box(ax, cols[3], 0.70, 0.17, 0.16, "Hybrid ML engine\nmonotone GBM on\nphysics features")
    box(ax, cols[3], 0.42, 0.17, 0.16, "Validation\n575 real slopes\ngrouped CV")
    box(ax, cols[4], 0.70, 0.17, 0.16, "Hazard index\nHI $= P_f$", fc="#fff")
    box(ax, cols[4], 0.42, 0.17, 0.16, "Risk index\nRI $=\\sqrt{HI\\cdot VI}$\nClass I–V", bold=True)
    box(ax, cols[4], 0.15, 0.17, 0.13, "Vulnerability\nindex VI")
    for y in (0.70, 0.42):
        for a, b in zip(cols[:-1], cols[1:]):
            arrow(ax, (a + 0.088, y), (b - 0.088, y))
    arrow(ax, (cols[1], 0.615), (cols[1], 0.505))
    arrow(ax, (cols[3], 0.505), (cols[3], 0.615))
    arrow(ax, (cols[0] + 0.088, 0.15), (cols[4] - 0.088, 0.15))
    arrow(ax, (cols[4], 0.62), (cols[4], 0.505))
    arrow(ax, (cols[4], 0.22), (cols[4], 0.335))
    ax.text(0.5, 0.005, "Judgement enters only through measurable class limits and literature distributions; "
            "weights and probabilities are computed, not elicited.", ha="center", fontsize=7.5,
            color=MUTED, style="italic")
    save(fig, "F01_concept")


# --------------------------------------------------------------------------
# F2  Parameter hierarchy (with exact total Sobol indices)
# --------------------------------------------------------------------------
def fig_hierarchy(sobol):
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.set_xlim(-0.07, 1.02); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.5, 0.94, 0.36, 0.08, "Landslide Risk Index  RI $=\\sqrt{HI\\cdot VI}$", fc="#f1effb", bold=True)
    box(ax, 0.40, 0.78, 0.22, 0.07, "Hazard HI $= P_f$ (physics)", fc="#fde9e1")
    box(ax, 0.895, 0.78, 0.19, 0.07, "Vulnerability VI (AHP)", fc="#e8f0fb")
    arrow(ax, (0.45, 0.90), (0.42, 0.815)); arrow(ax, (0.58, 0.90), (0.88, 0.815))
    groups = [(0.19, "Preparatory (resisting & driving)", 0.30), (0.45, "Bridge", 0.09),
              (0.65, "Triggering", 0.21)]
    for x, t, w in groups:
        box(ax, x, 0.62, w, 0.06, t, fc=PANEL, fs=7.5)
        arrow(ax, (0.40, 0.745), (x, 0.65))
    var_x = {"soil": 0.08, "geometry": 0.19, "vegetation": 0.30, "groundwater": 0.45,
             "rainfall": 0.595, "seismic": 0.705}
    parent = {"soil": 0.19, "geometry": 0.19, "vegetation": 0.19, "groundwater": 0.45,
              "rainfall": 0.65, "seismic": 0.65}
    st = sobol["ST"] / sobol["ST"].sum()
    for v, x in var_x.items():
        shade = plt.cm.Blues(0.15 + 0.8 * st[v] / st.max())
        box(ax, x, 0.44, 0.088, 0.10, f"{SHORT[v]}\n$S_T$={sobol['ST'][v]:.2f}", fc=shade, fs=7,
            tc="white" if st[v] > 0.5 * st.max() else INK)
        arrow(ax, (parent[v], 0.59), (x, 0.49))
    params = {"soil": "$c'$  $\\phi'$\n$\\gamma$  $K_s$\n$n_e$", "geometry": "$\\beta$\n$H$",
              "vegetation": "$c_r$\n$d_{root}$", "groundwater": "$m_0=h_w/z$",
              "rainfall": "$P$ (mm)\n$D$ (h)", "seismic": "$k_h=0.5\\,PGA$"}
    for v, x in var_x.items():
        box(ax, x, 0.24, 0.088, 0.13, params[v], fc="white", fs=7.5)
        arrow(ax, (x, 0.39), (x, 0.305))
    box(ax, 0.84, 0.44, 0.088, 0.10, "Settlement\ndistance\n$w=0.667$", fc="#e8f0fb", fs=7)
    box(ax, 0.95, 0.44, 0.088, 0.10, "Run-out\nvegetation\n$w=0.333$", fc="#e8f0fb", fs=7)
    arrow(ax, (0.87, 0.745), (0.84, 0.49)); arrow(ax, (0.92, 0.745), (0.95, 0.49))
    for y, t in [(0.94, "Level 0"), (0.78, "Level 1"), (0.62, "Level 2"), (0.44, "Level 3"), (0.24, "Level 4")]:
        ax.text(-0.065, y, t, fontsize=6.5, color=MUTED, ha="left", va="center")
    ax.text(0.37, 0.10, "Level 4: physical parameters sampled by Monte Carlo  →  "
            "$FS(c',\\phi',\\gamma,\\beta,H,m,k_h,c_r)$", ha="center", fontsize=8, color=MUTED)
    ax.text(0.37, 0.05, "Box shading = exact total-order Sobol' index $S_T$ of $P_f$ over the $5^6$ score space",
            ha="center", fontsize=7.5, color=MUTED, style="italic")
    save(fig, "F02_hierarchy")


# --------------------------------------------------------------------------
# F3  Mechanics schematics: infinite slope + Bishop slices
# --------------------------------------------------------------------------
def fig_mechanics(cases):
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]; ax.set_aspect("equal"); ax.axis("off")
    b = np.radians(30); tb = np.tan(b); z = 1.5
    xs = np.array([0.0, 7.0])
    ax.add_patch(Polygon([(0, 0), (7, 7 * tb), (7, 7 * tb - z), (0, -z)], fc="#e9dfcc", ec="none"))
    ax.add_patch(Polygon([(0, -z), (7, 7 * tb - z), (7, 7 * tb - z - 0.9), (0, -z - 0.9)], fc="#b9ad9b", ec="none"))
    ax.plot(xs, xs * tb, color=INK, lw=1.1)                                   # ground surface
    ax.plot(xs, xs * tb - z, color=RED, lw=1.8)                               # slip plane
    ax.plot(xs, xs * tb - 0.45 * z, color=BLUE, lw=1.0, ls="--")              # water table
    x0, x1 = 3.0, 4.0                                                         # vertical slice
    ax.add_patch(Polygon([(x0, x0 * tb), (x1, x1 * tb), (x1, x1 * tb - z), (x0, x0 * tb - z)],
                         fc="white", ec=INK, lw=1.0, alpha=0.9))
    cx, cy = 3.5, 3.5 * tb - z / 2
    arrow(ax, (cx, cy), (cx, cy - 1.25), color=INK, lw=1.2)
    ax.text(cx + 0.1, cy - 0.55, "$W$", fontsize=9, ha="left")
    arrow(ax, (cx, cy), (cx - 0.9, cy), color=ORANGE, lw=1.2)
    ax.text(cx - 0.95, cy + 0.08, "$k_hW$", fontsize=8.5, color=ORANGE, ha="right")
    bx, by = 3.5, 3.5 * tb - z
    t = np.array([np.cos(b), np.sin(b)]); n = np.array([-np.sin(b), np.cos(b)])
    base = np.array([bx, by])
    arrow(ax, base - 0.05 * t, base + 0.9 * t, color=GREEN, lw=1.2)
    ax.text(*(base + 0.95 * t + [0.05, -0.05]), r"$\tau_{res}$", fontsize=9, color=GREEN)
    arrow(ax, base - 0.9 * n, base, color=VIOLET, lw=1.2)
    ax.text(*(base - 0.95 * n + [0.05, -0.1]), r"$N'=\sigma_n-u$", fontsize=8, color=VIOLET)
    ax.annotate("", (x1 + 0.25, x1 * tb), (x1 + 0.25, x1 * tb - z),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
    ax.text(x1 + 0.32, x1 * tb - z / 2, "$z$", fontsize=9, color=MUTED, va="center")
    arc = np.linspace(0, b, 30)
    ax.plot(1.3 * np.cos(arc), 1.3 * np.sin(arc), color=INK, lw=0.8)
    ax.plot([0, 1.6], [0, 0], color=INK, lw=0.6, ls=":")
    ax.text(1.45, 0.25, r"$\beta$", fontsize=9)
    ax.text(5.2, 5.2 * tb - 0.45 * z - 0.05, "water table, $m=h_w/z$", fontsize=7, color=BLUE, ha="left",
            va="top", rotation=30, rotation_mode="anchor")
    ax.text(5.0, 5.0 * tb - z - 0.12, "slip plane", fontsize=7, color=RED, ha="left", va="top",
            rotation=30, rotation_mode="anchor")
    ax.set_xlim(-0.3, 7.2); ax.set_ylim(-2.6, 4.3)
    ax.set_title("(a) Infinite slope: forces on a vertical slice", fontsize=9, loc="left")
    ax = axes[1]
    row = cases[(cases.failed == 1) & (cases.H.between(10, 40)) & (cases.phi > 15) & (cases.c > 5)].iloc[0]
    fs, info = bishop_fs(row.gamma, row.c, row.phi, row.beta, row.H, row.ru)
    H, beta = row.H, np.radians(row.beta)
    L = H / np.tan(beta)
    xs = np.linspace(-1.2 * H, L + 1.8 * H, 400)
    ground = np.clip(xs * np.tan(beta), 0, H)
    ax.fill_between(xs, -0.6 * H, ground, color="#e9dfcc")
    ax.plot(xs, ground, color=INK, lw=1)
    th = np.linspace(0, 2 * np.pi, 400)
    cx, cy = info["xc"] + info["R"] * np.cos(th), info["yc"] + info["R"] * np.sin(th)
    keep = (cx >= info["x_exit"]) & (cx <= info["x_entry"]) & (cy <= info["yc"])
    ax.plot(cx[keep], cy[keep], color=RED, lw=1.6)
    for xi, yb, hh in zip(info["slices_x"][::2], info["slices_base"][::2], info["slices_h"][::2]):
        if hh > 0:
            ax.plot([xi, xi], [yb, yb + hh], color=MUTED, lw=0.5)
    ax.plot(info["xc"], info["yc"], "o", color=RED, ms=3)
    ax.plot([info["xc"], info["x_exit"]], [info["yc"], np.clip(info["x_exit"] * np.tan(beta), 0, H)],
            color=RED, lw=0.5, ls=":")
    ax.set_aspect("equal"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_title(f"(b) Bishop simplified: critical circle, FS = {fs:.2f}", fontsize=9, loc="left")
    ax.text(0.98, 0.03, f"$\\gamma$={row.gamma:.1f}, $c'$={row.c:.1f} kPa,\n$\\phi'$={row.phi:.1f}°, "
            f"$\\beta$={row.beta:.0f}°, H={H:.0f} m, $r_u$={row.ru:.2f}\nobserved: failed",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color=MUTED)
    save(fig, "F03_mechanics")


# --------------------------------------------------------------------------
# F4  FS response surfaces + gradient field
# --------------------------------------------------------------------------
def fig_response_surfaces():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0))
    beta = np.linspace(15, 60, 120); m = np.linspace(0, 1, 120)
    B, M = np.meshgrid(beta, m)
    p = dict(REF); p.update(beta=B, m=M)
    F = fs_point(p)
    ax = axes[0]
    cs = ax.contourf(B, M, F, levels=np.linspace(0, 3, 31), cmap="RdBu", extend="max")
    ax.contour(B, M, F, levels=[1.0], colors=INK, linewidths=1.4)
    ax.contour(B, M, F, levels=[1.5], colors=INK, linewidths=0.8, linestyles="--")
    gy, gx = np.gradient(F, m, beta)
    s = (slice(None, None, 12), slice(None, None, 12))
    # gradient in axis-normalised coordinates (beta range 45 deg, m range 1)
    U, V = gx[s] * 45, gy[s] * 1.0
    norm = np.hypot(U, V) + 1e-9
    ax.quiver(B[s], M[s], U / norm, V / norm, color=INK, alpha=0.75, scale=24, width=0.004)
    ax.set_xlabel(r"Slope angle $\beta$ (°)"); ax.set_ylabel(r"Groundwater ratio $m=h_w/z$")
    ax.set_title(r"(a) $FS(\beta, m)$ and $\nabla FS$ (arrows)", fontsize=9, loc="left")
    ax.text(41.5, 0.03, "FS=1", fontsize=7.5, color=INK, rotation=-62); ax.grid(False)
    fig.colorbar(cs, ax=ax, label="FS", ticks=[0, 0.5, 1, 1.5, 2, 2.5, 3])

    c = np.linspace(0, 25, 120); phi = np.linspace(12, 40, 120)
    C, P = np.meshgrid(c, phi)
    p = dict(REF); p.update(c=C, phi=P)
    F2 = fs_point(p)
    ax = axes[1]
    cs = ax.contourf(C, P, F2, levels=np.linspace(0, 3, 31), cmap="RdBu", extend="max")
    ax.contour(C, P, F2, levels=[1.0], colors=INK, linewidths=1.4)
    ax.contour(C, P, F2, levels=[1.5], colors=INK, linewidths=0.8, linestyles="--")
    for k, sc in SOIL_CLASSES.items():
        ax.plot(sc.c_mean, sc.phi_mean, "o", ms=5, mfc="white", mec=INK)
        ax.annotate(str(k), (sc.c_mean, sc.phi_mean), xytext=(4, 3), textcoords="offset points", fontsize=7.5)
    ax.set_xlabel("Effective cohesion $c'$ (kPa)"); ax.set_ylabel(r"Friction angle $\phi'$ (°)")
    ax.set_title(r"(b) $FS(c', \phi')$ and soil-class means", fontsize=9, loc="left"); ax.grid(False)
    fig.colorbar(cs, ax=ax, label="FS", ticks=[0, 0.5, 1, 1.5, 2, 2.5, 3])
    fig.text(0.5, -0.04, "Reference: $\\gamma$=17 kN/m³, H=2 m, $k_h$=0.05, $c_r$=3 kPa; "
             "(a) $c'$=9 kPa, $\\phi'$=25°;  (b) $\\beta$=40°, m=0.5. Solid: FS=1, dashed: FS=1.5 (SNI 8460).",
             ha="center", fontsize=7.5, color=MUTED)
    fig.tight_layout()
    save(fig, "F04_response_surfaces")


# --------------------------------------------------------------------------
# F5  Gradient analysis
# --------------------------------------------------------------------------
def fig_gradients():
    keys = list(REF)
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    betas = np.linspace(15, 60, 46)
    for k, col in zip(keys, SERIES):
        vals = []
        for bb in betas:
            p = dict(REF); p["beta"] = bb
            vals.append(gradient(p, [k])[k] * SIGMA[k])
        ax.plot(betas, vals, color=col, lw=1.6, label=SYM[k])
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xlabel(r"Slope angle $\beta$ (°)")
    ax.set_ylabel(r"$\sigma_i\,\partial FS/\partial x_i$")
    ax.set_title("(a) Standardised gradient vs slope angle", fontsize=9, loc="left")
    ax.legend(ncol=4, frameon=False, loc="lower right")

    ax = axes[1]
    mat = np.zeros((5, len(keys)))
    for i, (k_cls, sc) in enumerate(SOIL_CLASSES.items()):
        p = dict(REF); p.update(c=sc.c_mean, phi=sc.phi_mean, gamma=sc.gamma_mean)
        g = gradient(p, keys)
        sig = dict(SIGMA); sig.update(c=sc.c_mean * sc.c_cov, phi=sc.phi_mean * sc.phi_cov,
                                       gamma=sc.gamma_mean * sc.gamma_cov)
        mat[i] = [g[k] * sig[k] for k in keys]
    lim = np.abs(mat).max()
    im = ax.imshow(mat, cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
    for (i, j), v in np.ndenumerate(mat):
        ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=6.5,
                color="white" if abs(v) > 0.6 * lim else INK)
    ax.set_xticks(range(len(keys)), [SYM[k] for k in keys])
    ax.set_yticks(range(5), [f"Class {k}" for k in SOIL_CLASSES])
    ax.set_title(r"(b) Sensitivity (Jacobian) matrix $\sigma_j\,\partial FS/\partial x_j$", fontsize=9, loc="left")
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.85, label=r"$\Delta FS$ per 1$\sigma$")
    fig.tight_layout()
    save(fig, "F05_gradients")


# --------------------------------------------------------------------------
# F6  Matrices: input correlation, Hessian interaction, Sobol second order
# --------------------------------------------------------------------------
def fig_matrices(S2):
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.9))
    rng = np.random.default_rng(0)
    p = sample_physical(np.array([[3, 3, 3, 3, 3, 3]]), 20000, rng)
    fs = fs_from_parameters(p)[0]
    names = ["c", "phi", "gamma", "ks", "beta", "m0", "rain_mm", "kh", "c_root"]
    lab = ["$c'$", r"$\phi'$", r"$\gamma$", "$K_s$", r"$\beta$", "$m_0$", "$P$", "$k_h$", "$c_r$", "FS"]
    df = pd.DataFrame({n: p[n][0] for n in names}); df["FS"] = fs
    R = df.rank().corr().to_numpy()
    ax = axes[0]
    im = ax.imshow(R, cmap="RdBu", vmin=-1, vmax=1)
    for (i, j), v in np.ndenumerate(R):
        if i != j and abs(v) >= 0.1:
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=5.5,
                    color="white" if abs(v) > 0.6 else INK)
    ax.set_xticks(range(len(lab)), lab, fontsize=7); ax.set_yticks(range(len(lab)), lab, fontsize=7)
    ax.set_title("(a) Spearman $\\rho$: inputs & FS", fontsize=9, loc="left"); ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.7)

    keys = list(REF)
    Hm = hessian(REF, keys)
    sig = np.array([SIGMA[k] for k in keys])
    Hn = Hm * np.outer(sig, sig)
    ax = axes[1]
    lim = np.abs(Hn).max()
    im = ax.imshow(Hn, cmap="RdBu", vmin=-lim, vmax=lim)
    for (i, j), v in np.ndenumerate(Hn):
        if abs(v) > 0.05 * lim:
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.5,
                    color="white" if abs(v) > 0.6 * lim else INK)
    ax.set_xticks(range(len(keys)), [SYM[k] for k in keys], fontsize=7)
    ax.set_yticks(range(len(keys)), [SYM[k] for k in keys], fontsize=7)
    ax.set_title(r"(b) Hessian $\sigma_i\sigma_j\,\partial^2 FS/\partial x_i\partial x_j$", fontsize=9, loc="left")
    ax.grid(False); fig.colorbar(im, ax=ax, shrink=0.7)

    ax = axes[2]
    M = S2.loc[VARIABLES, VARIABLES].to_numpy()
    im = ax.imshow(M, cmap="Blues", vmin=0, vmax=M.max())
    for (i, j), v in np.ndenumerate(M):
        ax.text(j, i, f"{v:.3f}" if i != j else f"{v:.2f}", ha="center", va="center", fontsize=5.8,
                color="white" if v > 0.5 * M.max() else INK, fontweight="bold" if i == j else "normal")
    t = ["$X_1$", "$X_2$", "$X_3$", "$X_4$", "$X_5$", "$X_6$"]
    ax.set_xticks(range(6), t); ax.set_yticks(range(6), t)
    ax.set_title("(c) Sobol' $S_i$ (diag.) & $S_{ij}$", fontsize=9, loc="left"); ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.7)
    fig.tight_layout()
    save(fig, "F06_matrices")


# --------------------------------------------------------------------------
# F7  Monte Carlo behaviour for the case-study slope
# --------------------------------------------------------------------------
def fig_monte_carlo():
    rng = np.random.default_rng(1)
    p = sample_physical(np.array([[3, 4, 4, 4, 1, 2]]), 20000, rng)
    fs = fs_from_parameters(p)[0]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.6))
    ax = axes[0]
    bins = np.linspace(0, 2.2, 60)
    ax.hist(fs[fs < 1], bins=bins, color=RED, alpha=0.85, label=f"FS<1  ($P_f$={np.mean(fs < 1):.3f})")
    ax.hist(fs[fs >= 1], bins=bins, color=BLUE, alpha=0.85, label="FS≥1")
    ax.axvline(1, color=INK, lw=1); ax.axvline(1.5, color=INK, lw=0.8, ls="--")
    ax.set_xlabel("Factor of safety"); ax.set_ylabel("Count")
    ax.legend(frameon=True, framealpha=0.95, edgecolor="none", loc="upper right", fontsize=7)
    ax.set_title("(a) FS distribution, case study", fontsize=9, loc="left")
    ax = axes[1]
    n, pf = convergence_curve(fs)
    lo, hi = zip(*[wilson_interval(int(round(q * k)), k) for q, k in zip(pf, n)])
    ax.fill_between(n, lo, hi, color=BLUE, alpha=0.2, lw=0, label="95% Wilson CI")
    ax.plot(n, pf, color=BLUE, lw=1.5, label="running $P_f$")
    ax.axvline(400, color=ORANGE, lw=0.8, ls="--"); ax.text(430, ax.get_ylim()[0] + 0.01, "N=400", fontsize=7, color=ORANGE)
    ax.set_xscale("log"); ax.set_xlabel("Number of samples N"); ax.set_ylabel("$P_f$"); ax.legend(frameon=False)
    ax.set_title("(b) Convergence", fontsize=9, loc="left")
    ax = axes[2]
    pf_grid = np.logspace(-4, -0.3, 100)
    for cov, col in [(0.05, GREEN), (0.10, BLUE), (0.20, ORANGE)]:
        ax.plot(pf_grid, (1 - pf_grid) / (cov**2 * pf_grid), color=col, lw=1.5, label=f"COV = {cov:.2f}")
    ax.axhline(400, color=MUTED, lw=0.8, ls=":"); ax.text(1.2e-4, 480, "N = 400", fontsize=7, color=MUTED)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("$P_f$"); ax.set_ylabel("Required N")
    ax.legend(frameon=False); ax.set_title("(c) Sample size $N=(1-P_f)/(COV^2P_f)$", fontsize=9, loc="left")
    fig.tight_layout()
    save(fig, "F07_monte_carlo")


# --------------------------------------------------------------------------
# F8  Score-space results: marginal curves, screening matrix, Sobol bars
# --------------------------------------------------------------------------
def fig_score_space(grid, sob):
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.7), gridspec_kw={"width_ratios": [1.15, 1, 1]})
    ax = axes[0]
    for v, col in zip(VARIABLES, SERIES):
        cur = grid.groupby(v).pf.mean()
        ax.plot(cur.index, cur.values, "-o", color=col, ms=3.5, lw=1.5, label=SHORT[v])
    ax.set_xticks(range(1, 6)); ax.set_ylim(0, 1)
    ax.set_xlabel("Score (1 safe → 5 critical)"); ax.set_ylabel(r"$E[P_f\,|\,X_i]$")
    ax.legend(frameon=False, ncol=2, fontsize=6.5); ax.set_title("(a) Main effects", fontsize=9, loc="left")
    ax = axes[1]
    M = grid.pivot_table(index="geometry", columns="soil", values="pf", aggfunc="mean")
    im = ax.imshow(M.values, origin="lower", cmap="Blues", vmin=0, vmax=1, extent=(0.5, 5.5, 0.5, 5.5))
    for (i, j), v in np.ndenumerate(M.values):
        ax.text(j + 1, i + 1, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                color="white" if v > 0.55 else INK)
    ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
    ax.set_xlabel("Soil score $X_1$"); ax.set_ylabel("Geometry score $X_2$"); ax.grid(False)
    ax.set_title("(b) Screening matrix $E[P_f]$", fontsize=9, loc="left")
    fig.colorbar(im, ax=ax, shrink=0.85)
    ax = axes[2]
    y = np.arange(6)
    ax.barh(y + 0.18, sob.loc[VARIABLES, "S1"], height=0.34, color=BLUE, label="$S_i$ (first order)")
    ax.barh(y - 0.18, sob.loc[VARIABLES, "ST"], height=0.34, color=ORANGE, label="$S_{T,i}$ (total)")
    ax.set_yticks(y, [SHORT[v] for v in VARIABLES]); ax.invert_yaxis()
    ax.set_xlabel("Sobol' index (exact)"); ax.legend(frameon=False, loc="center right", fontsize=7)
    ax.set_title("(c) Variance decomposition", fontsize=9, loc="left")
    fig.tight_layout()
    save(fig, "F08_score_space")


# --------------------------------------------------------------------------
# F9  Machine engine architecture
# --------------------------------------------------------------------------
def fig_engine_architecture():
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    X = [0.10, 0.31, 0.52, 0.735, 0.92]
    box(ax, X[0], 0.78, 0.17, 0.17, "Case histories\n575 slopes\n$(\\gamma,c',\\phi',\\beta,H,r_u)$", fc="#e8f0fb", fs=7.5)
    box(ax, X[0], 0.42, 0.17, 0.17, "Near-duplicate\ngrouping\n(466 groups)", fc=PANEL, fs=7.5)
    box(ax, X[1], 0.78, 0.17, 0.17, "Physics solver\nBishop simplified,\ncritical circle", fc="#fde9e1", fs=7.5)
    box(ax, X[1], 0.42, 0.17, 0.17, "Domain check\n$\\gamma\\leq 23$, $H\\leq 100$ m,\n$r_u\\leq 0.9$", fc=PANEL, fs=7.5)
    box(ax, X[2], 0.78, 0.17, 0.17, "Physics features\n$\\ln FS$, $N_s=c'/\\gamma H$,\n$\\tan\\phi'/\\tan\\beta$", fc="#fde9e1", fs=7.5)
    box(ax, X[2], 0.42, 0.17, 0.17, "Raw features\n$\\gamma, c', \\phi', \\beta, H, r_u$", fc="#e8f0fb", fs=7.5)
    box(ax, X[3], 0.60, 0.18, 0.30, "Monotone gradient\nboosting\n\n$\\partial P/\\partial \\ln FS \\leq 0$\n"
        "$\\partial P/\\partial c' \\leq 0$,  $\\partial P/\\partial \\phi' \\leq 0$\n"
        "$\\partial P/\\partial \\beta \\geq 0$,  $\\partial P/\\partial r_u \\geq 0$", fc="#f1effb", fs=7.5)
    box(ax, X[4], 0.60, 0.13, 0.22, "Output\n$P(\\mathrm{fail})$\nFS\ndomain flag", fc="white", fs=7.5)
    box(ax, X[3], 0.20, 0.18, 0.15, "Grouped 5-fold CV x5\nAUC, Brier, ECE,\nleakage gap", fc=PANEL, fs=7.5)
    box(ax, 0.36, 0.08, 0.50, 0.08, "Acceptance gates: verification (5) | numerical (4) | validation (8)",
        fc="#e3f5ee", fs=7.5)
    for y in (0.78, 0.42):
        arrow(ax, (X[0] + 0.088, y), (X[1] - 0.088, y))
        arrow(ax, (X[1] + 0.088, y), (X[2] - 0.088, y))
    arrow(ax, (X[0], 0.69), (X[0], 0.51))
    arrow(ax, (X[2] + 0.088, 0.76), (X[3] - 0.093, 0.66))
    arrow(ax, (X[2] + 0.088, 0.44), (X[3] - 0.093, 0.54))
    arrow(ax, (X[3] + 0.093, 0.60), (X[4] - 0.068, 0.60))
    arrow(ax, (X[3], 0.445), (X[3], 0.28))
    arrow(ax, (X[3] - 0.093, 0.18), (0.61, 0.10))
    save(fig, "F09_engine_architecture")



# --------------------------------------------------------------------------
# F10 Validation: ROC, reliability diagram, AUC comparison
# --------------------------------------------------------------------------
NAMES = {"A_heuristic": "A Heuristic (AHP-like)", "B_physics": "B Physics only",
         "C_ml_raw": "C ML (raw)", "D_hybrid": "D Hybrid (monotone)"}
MCOL = {"A_heuristic": MUTED, "B_physics": ORANGE, "C_ml_raw": AQUA, "D_hybrid": BLUE}


def fig_validation():
    oof = pd.read_csv(RES / "oof_grouped_domain.csv")
    y = oof.failed
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.75))
    ax = axes[0]
    pm = pd.read_csv(RES / "pooled_metrics_grouped_domain.csv", index_col=0)
    for m in NAMES:
        fpr, tpr, _ = roc_curve(y, oof[m])
        ax.plot(fpr, tpr, color=MCOL[m], lw=1.6, label=f"{NAMES[m]}  {pm.loc[m, 'auc']:.3f}")
    ax.plot([0, 1], [0, 1], color=GRID, lw=1)
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.legend(frameon=False, fontsize=6.3, loc="lower right", title="AUC (grouped CV)", title_fontsize=6.5)
    ax.set_title("(a) ROC, soil domain (n=327)", fontsize=9, loc="left")
    ax = axes[1]
    for m in ("B_physics", "D_hybrid", "A_heuristic"):
        pt, pp = calibration_curve(y, oof[m], n_bins=8, strategy="quantile")
        ax.plot(pp, pt, "-o", color=MCOL[m], ms=3.5, lw=1.4, label=f"{NAMES[m]}  ECE {pm.loc[m, 'ece']:.3f}")
    ax.plot([0, 1], [0, 1], color=GRID, lw=1)
    ax.set_xlabel("Predicted P(fail)"); ax.set_ylabel("Observed failure frequency")
    ax.legend(frameon=True, framealpha=0.95, edgecolor="none", fontsize=6.3, loc="lower right")
    ax.set_title("(b) Reliability diagram", fontsize=9, loc="left")
    ax = axes[2]
    g = pd.read_csv(RES / "cv_folds_grouped_domain.csv").groupby("model").auc.agg(["mean", "std"])
    r = pd.read_csv(RES / "pooled_metrics_random_domain.csv", index_col=0).auc
    x = np.arange(4)
    ax.bar(x - 0.2, g.loc[list(NAMES), "mean"], 0.38, yerr=g.loc[list(NAMES), "std"], color=BLUE,
           capsize=2, error_kw={"lw": 0.8}, label="grouped CV (honest)")
    ax.bar(x + 0.2, r.loc[list(NAMES)], 0.38, color=ORANGE, label="random CV (leaky)")
    ax.axhline(0.8, color=INK, lw=0.8, ls="--"); ax.axhline(0.7, color=MUTED, lw=0.8, ls=":")
    ax.set_xticks(x, ["A", "B", "C", "D"]); ax.set_ylim(0.5, 1.0); ax.set_ylabel("AUC")
    ax.legend(frameon=False, fontsize=6.5, loc="upper left"); ax.set_title("(c) AUC: grouped vs random CV", fontsize=9, loc="left")
    fig.tight_layout()
    save(fig, "F10_validation")


# --------------------------------------------------------------------------
# F11 How the machine models: importance + partial dependence (monotone)
# --------------------------------------------------------------------------
def fig_machine_interpretation():
    cases = pd.read_csv(RES / "cases_with_fs.csv")
    dom = cases[E.in_domain(cases)].reset_index(drop=True)
    model = E.fit_final(dom)
    feats = E.RAW + E.PHYS
    X, y = dom[feats], dom.failed
    imp = permutation_importance(model.model, X, y, scoring="roc_auc", n_repeats=30, random_state=0)
    order = np.argsort(imp.importances_mean)
    lab = {"gamma": r"$\gamma$", "c": "$c'$", "phi": r"$\phi'$", "beta": r"$\beta$", "H": "$H$", "ru": "$r_u$",
           "log_fs": r"$\ln FS$ (physics)", "stability_number": r"$N_s=c'/\gamma H$",
           "friction_ratio": r"$\tan\phi'/\tan\beta$"}
    fig = plt.figure(figsize=(7.6, 3.1))
    gs = fig.add_gridspec(2, 4, width_ratios=[1.3, 1, 1, 1])
    ax = fig.add_subplot(gs[:, 0])
    cols = [ORANGE if feats[i] in E.PHYS else BLUE for i in order]
    ax.barh(range(len(order)), imp.importances_mean[order], xerr=imp.importances_std[order], color=cols,
            capsize=2, error_kw={"lw": 0.7})
    ax.set_yticks(range(len(order)), [lab[feats[i]] for i in order])
    ax.set_xlabel(r"$\Delta$AUC when permuted"); ax.set_title("(a) Permutation importance", fontsize=9, loc="left")
    ax.text(0.98, 0.04, "orange = physics feature", transform=ax.transAxes, ha="right", fontsize=7, color=ORANGE)
    grouped = {}
    rng = np.random.default_rng(0)
    from sklearn.metrics import roc_auc_score
    base_auc = roc_auc_score(y, model.model.predict_proba(X)[:, 1])
    for name, cols_ in (("physics block", E.PHYS), ("raw block", E.RAW)):
        drops = []
        for _ in range(30):
            Xp = X.copy(); idx = rng.permutation(len(X))
            Xp[cols_] = X[cols_].to_numpy()[idx]
            drops.append(base_auc - roc_auc_score(y, model.model.predict_proba(Xp)[:, 1]))
        grouped[name] = float(np.mean(drops))
    pd.Series(grouped).to_csv(RES / "grouped_importance.csv")
    ax.text(0.98, 0.14, f"block permutation: physics {grouped['physics block']:.3f}, "
            f"raw {grouped['raw block']:.3f}", transform=ax.transAxes, ha="right", fontsize=6.5, color=MUTED)
    for k, f in enumerate(["log_fs", "c", "phi", "beta", "ru", "stability_number"]):
        ax = fig.add_subplot(gs[k // 3, 1 + k % 3])
        pdp = partial_dependence(model.model, X, [feats.index(f)], grid_resolution=40, kind="both")
        grid = pdp["grid_values"][0]
        ice = pdp["individual"][0]
        for row in ice[:: max(1, len(ice) // 40)]:
            ax.plot(grid, row, color=BLUE, alpha=0.08, lw=0.6)
        ax.plot(grid, pdp["average"][0], color=INK, lw=1.6)
        sign = {-1: "↓", 1: "↑", 0: ""}[E.MONOTONE[f]]
        ax.set_title(f"{lab[f]}  {sign}", fontsize=8, loc="left")
        ax.set_ylim(0, 1); ax.tick_params(labelsize=6.5)
        if k % 3 == 0:
            ax.set_ylabel("P(fail)", fontsize=7.5)
    fig.text(0.62, 1.0, "(b) Partial dependence (black) + ICE curves (blue): monotone by construction",
             ha="center", fontsize=9)
    fig.tight_layout()
    save(fig, "F11_machine_interpretation")


# --------------------------------------------------------------------------
# F12 Risk index plane + case study
# --------------------------------------------------------------------------
def fig_risk_plane():
    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    hi = np.linspace(0, 1, 300)
    Hh, Vv = np.meshgrid(hi, hi)
    RI = np.sqrt(Hh * Vv)
    levels = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    cs = ax.contourf(Hh, Vv, RI, levels=levels, colors=["#dbe8f8", "#b3cdef", "#f3f2ee", "#f6c9b5", "#e98e6b"])
    ax.contour(Hh, Vv, RI, levels=levels[1:-1], colors="white", linewidths=1)
    for lvl, name in zip([0.1, 0.3, 0.5, 0.7, 0.9], ["I", "II", "III", "IV", "V"]):
        ax.text(lvl * 1.0 + 0.02, lvl * 1.0 - 0.04, name, fontsize=10, fontweight="bold", color=INK)
    site = __import__("json").loads((RES / "site_case_study.json").read_text())
    vi = 0.584
    ax.plot(0.575, vi, "s", color=MUTED, ms=7, label="HI weighted (slides) → III")
    ax.plot(site["pf"], vi, "o", color=RED, ms=7, label=f"HI = $P_f$ v2 ({site['pf']:.2f}) → "
            f"{'IV' if np.sqrt(site['pf'] * vi) >= 0.6 else 'III'}")
    ax.annotate("", (site["pf"], vi), (0.575, vi), arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.set_xlabel("Hazard index HI"); ax.set_ylabel("Vulnerability index VI")
    ax.set_title(r"Risk plane RI $=\sqrt{HI\cdot VI}$ with case study", fontsize=9, loc="left")
    ax.legend(frameon=False, fontsize=7, loc="upper left"); ax.grid(False)
    save(fig, "F12_risk_plane")


def main():
    grid = pd.read_csv(RES / "full_factorial_v2.csv")
    sob, S2 = exact_sobol(grid, VARIABLES)
    cases = pd.read_csv(RES / "cases_with_fs.csv")
    fig_concept()
    fig_hierarchy(sob)
    fig_mechanics(cases)
    fig_response_surfaces()
    fig_gradients()
    fig_matrices(S2)
    fig_monte_carlo()
    fig_score_space(grid, sob)
    fig_engine_architecture()
    fig_validation()
    fig_machine_interpretation()
    fig_risk_plane()


if __name__ == "__main__":
    main()
