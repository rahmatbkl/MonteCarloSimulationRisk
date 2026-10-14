"""
Simulation engine: Outer loop (Latin Hypercube) x Inner loop (Monte Carlo).

    1.200 konfigurasi skor (LHS)  x  400 iterasi MC  =  480.000 evaluasi FS

Outer loop  : memilih kombinasi skor (X1..X6) secara seimbang (LHS).
Inner loop  : untuk SATU kombinasi skor, acak nilai fisik di dalam rentang
              skornya, hitung FS, lalu Pf = (jumlah FS < 1) / N.
"""

import numpy as np
import pandas as pd
from scipy.stats import qmc

from . import config as cfg
from .physics import effective_root_cohesion, factor_of_safety, rainfall_to_water_ratio


def _range_table(table, key=None):
    """Ubah dict {skor: (min, max)} menjadi array low[6], high[6] (indeks 1-5)."""
    low, high = np.zeros(6), np.zeros(6)
    for score, value in table.items():
        lo, hi = value[key] if key else value
        low[score], high[score] = lo, hi
    return low, high


def _uniform_by_score(scores, table, rng, n_mc, key=None, log=False):
    """
    Acak nilai seragam di dalam rentang milik skor masing-masing konfigurasi.
    scores: array (n_cfg,) bilangan 1-5  ->  hasil: array (n_cfg, n_mc).
    log=True untuk besaran yang tersebar beberapa orde (mis. permeabilitas).
    """
    low, high = _range_table(table, key)
    lo = low[scores][:, None]
    hi = high[scores][:, None]
    u = rng.random((len(scores), n_mc))
    if log:
        return np.exp(np.log(lo) + u * (np.log(hi) - np.log(lo)))
    return lo + u * (hi - lo)


def _uniform(bounds, rng, shape):
    lo, hi = bounds
    return lo + rng.random(shape) * (hi - lo)


def sample_factor_of_safety(scores, n_mc, rng):
    """
    Inner loop Monte Carlo untuk banyak konfigurasi sekaligus.

    scores : array int (n_cfg, 6) berisi skor X1..X6
    return : array FS berukuran (n_cfg, n_mc)
    """
    scores = np.asarray(scores, dtype=int)
    soil, geom, gwt, rain, seis, veg = scores.T
    shape = (len(scores), n_mc)

    # X1 - parameter kekuatan tanah
    c = _uniform_by_score(soil, cfg.SOIL, rng, n_mc, key="c")
    phi = _uniform_by_score(soil, cfg.SOIL, rng, n_mc, key="phi")
    gamma = _uniform_by_score(soil, cfg.SOIL, rng, n_mc, key="gamma")
    ks = _uniform_by_score(soil, cfg.SOIL, rng, n_mc, key="ks", log=True)

    # X2 - geometri
    beta = _uniform_by_score(geom, cfg.SLOPE_ANGLE, rng, n_mc)
    # Ketebalan tanah diukur tegak lurus lereng (H), lalu dikonversi ke
    # kedalaman vertikal z = H / cos(beta) yang dipakai persamaan FS.
    # Tanpa konversi ini, FS justru naik lagi pada lereng > 45 derajat (artefak).
    thickness = _uniform(cfg.SLIP_DEPTH, rng, shape)
    z = thickness / np.cos(np.radians(beta))

    # X3 + X4 - air tanah awal, lalu dinaikkan oleh hujan
    m0 = _uniform_by_score(gwt, cfg.GROUNDWATER_RATIO, rng, n_mc)
    rain = _uniform_by_score(rain, cfg.RAINFALL_INTENSITY, rng, n_mc)
    duration = _uniform(cfg.RAIN_DURATION_HR, rng, shape)
    porosity = _uniform(cfg.EFFECTIVE_POROSITY, rng, shape)
    m = rainfall_to_water_ratio(m0, rain, duration, ks, porosity, z)

    # X5 - seismik
    kh = _uniform_by_score(seis, cfg.SEISMIC_KH, rng, n_mc)

    # X6 - vegetasi (kohesi akar, hanya jika akar mencapai bidang gelincir)
    cr = _uniform_by_score(veg, cfg.ROOT_COHESION, rng, n_mc)
    root_depth = _uniform_by_score(veg, cfg.ROOT_DEPTH, rng, n_mc)
    c_root = effective_root_cohesion(cr, root_depth, thickness)

    return factor_of_safety(c, phi, gamma, z, beta, m, kh, c_root)


def lhs_score_configurations(n_configs, rng):
    """
    Outer loop: Latin Hypercube Sampling pada ruang skor 1-5 untuk 6 variabel.
    Jika n_configs kelipatan 5, setiap skor muncul tepat n_configs/5 kali
    pada setiap variabel (dataset seimbang).
    """
    sampler = qmc.LatinHypercube(d=len(cfg.VARIABLES), rng=rng)
    unit = sampler.random(n_configs)
    return np.floor(unit * 5).astype(int) + 1


def run_simulation(n_configs=cfg.N_OUTER_LHS, n_mc=cfg.N_INNER_MC, seed=cfg.RANDOM_SEED):
    """
    Jalankan pipeline simulasi lengkap.
    Return DataFrame: kolom skor X1..X6 + pf, fs_min, fs_mean, fs_max.
    """
    rng = np.random.default_rng(seed)
    scores = lhs_score_configurations(n_configs, rng)
    fs = sample_factor_of_safety(scores, n_mc, rng)

    df = pd.DataFrame(scores, columns=cfg.VARIABLES)
    df["pf"] = (fs < 1.0).mean(axis=1)
    df["fs_min"] = fs.min(axis=1)
    df["fs_mean"] = fs.mean(axis=1)
    df["fs_max"] = fs.max(axis=1)
    return df


def site_probability_of_failure(scores, n_mc=20000, seed=cfg.RANDOM_SEED):
    """
    Pf untuk SATU lereng (skor lapangan), dengan selang kepercayaan 95% Wilson.
    Dipakai sebagai Hazard Index berbasis fisika langsung (lihat risk_index.py).
    """
    rng = np.random.default_rng(seed)
    fs = sample_factor_of_safety(np.atleast_2d(scores), n_mc, rng)[0]
    failures = int((fs < 1.0).sum())
    pf = failures / n_mc

    z = 1.96
    denom = 1 + z**2 / n_mc
    center = (pf + z**2 / (2 * n_mc)) / denom
    half = z * np.sqrt(pf * (1 - pf) / n_mc + z**2 / (4 * n_mc**2)) / denom
    return {"pf": pf, "ci_low": center - half, "ci_high": center + half,
            "fs_median": float(np.median(fs)), "n_mc": n_mc}
