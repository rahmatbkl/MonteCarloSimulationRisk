"""
Model parameter v2: distribusi probabilistik berbasis literatur.

Perbedaan dengan v1 (config.py, rentang seragam):
  1. Parameter tanah memakai DISTRIBUSI dengan COV dari literatur:
       c'  ~ lognormal          (tidak bisa negatif, ekor kanan panjang)
       phi'~ normal terpotong ±3 sigma
       gamma ~ normal (COV 5%)
       Ks  ~ lognormal (median, simpangan baku log10)
     Sumber COV: ISSMGE TC304 (2021) state-of-the-art review of inherent
     variability (doi:10.53243/R0001); Phoon & Kulhawy (1999).
  2. Korelasi c'-phi' negatif (rho = -0.5) lewat Gaussian copula
     (Lumb 1970: -0.37 s.d. -0.70; Cherubini: -0.61). Mengabaikan korelasi
     ini membuat Pf terlalu besar (Hammah et al.: Pf 1.05% pada rho=0
     vs 0.05% pada rho=-0.5).
  3. Hujan memakai CURAH HUJAN KUMULATIF kejadian (mm, 1-3 hari), bukan
     intensitas per jam. Longsor di Jawa umumnya dipicu hujan kumulatif
     300-600 mm; intensitas di atas Ks hanya menjadi limpasan.
  4. Kohesi akar dari kompilasi Stevens et al. (2006) dan sumber lain.

Skor (1-5) untuk geometri, MAT, hujan, seismik, vegetasi tetap memakai
rentang seragam: skor adalah KELAS, jadi nilai sebenarnya bisa di mana saja
di dalam kelas itu (ketidakpastian epistemik klasifikasi).
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats

from .physics import effective_root_cohesion, factor_of_safety


@dataclass(frozen=True)
class SoilClass:
    name: str
    c_mean: float        # kPa
    c_cov: float
    phi_mean: float      # derajat
    phi_cov: float
    gamma_mean: float    # kN/m3
    ks_median: float     # m/s
    ks_log10_sd: float = 0.5
    gamma_cov: float = 0.05
    drainable_porosity: tuple = (0.05, 0.15)


# Tabel kelas tanah (mean & COV). Kelas 2-5: nilai tengah ditetapkan dari
# rentang yang dikutip di research_notes/.../soil_parameter_statistics.md.
# Kalibrasi dengan data uji lab lokal bila tersedia.
SOIL_CLASSES = {
    1: SoilClass("Lempung keras / pasir padat", 15.0, 0.45, 34.0, 0.08, 19.0, 3e-6),
    2: SoilClass("Lempung kaku",                 12.0, 0.45, 29.0, 0.12, 18.0, 1e-6),
    3: SoilClass("Lempung sedang",                9.0, 0.50, 25.0, 0.15, 17.0, 3e-7),
    4: SoilClass("Lempung lunak",                 5.0, 0.55, 21.0, 0.18, 16.0, 1e-7),
    5: SoilClass("Gambut / organik",              3.0, 0.60, 20.0, 0.20, 11.0, 5e-5,
                 drainable_porosity=(0.20, 0.40)),
}
RHO_C_PHI = -0.5

# Kelas variabel lain: skor -> (min, max), diacak seragam
SLOPE_ANGLE = {1: (10, 25), 2: (25, 35), 3: (35, 45), 4: (45, 55), 5: (55, 60)}
# Skor 5 dibatasi 60 derajat: di atasnya mekanisme runtuhan batuan/toppling,
# di luar domain infinite slope.
THICKNESS = (1.0, 3.0)  # m, tegak lurus lereng (longsor dangkal)
GROUNDWATER_RATIO = {1: (0.0, 0.1), 2: (0.1, 0.35), 3: (0.35, 0.6), 4: (0.6, 0.85), 5: (0.85, 1.0)}
CUMULATIVE_RAIN_MM = {1: (0, 50), 2: (50, 100), 3: (100, 200), 4: (200, 350), 5: (350, 600)}
RAIN_DURATION_HR = (24.0, 72.0)
SEISMIC_KH = {1: (0.0, 0.02), 2: (0.02, 0.07), 3: (0.07, 0.12), 4: (0.12, 0.175), 5: (0.175, 0.30)}
# kh = 0.5 * PGA (Hynes-Griffin & Franklin, 1984); lihat peta PGA SNI 1726:2019.
ROOT_COHESION = {1: (7.0, 25.0), 2: (2.0, 7.0), 3: (1.5, 4.0), 4: (1.0, 3.0), 5: (0.0, 0.0)}
ROOT_DEPTH = {1: (1.5, 3.0), 2: (1.0, 2.0), 3: (0.5, 1.5), 4: (0.2, 0.5), 5: (0.0, 0.0)}


# ---------------------------------------------------------------------------
# Sampler
# ---------------------------------------------------------------------------
def lognormal_from_mean_cov(mean, cov):
    sigma = np.sqrt(np.log(1 + cov**2))
    return stats.lognorm(s=sigma, scale=mean / np.sqrt(1 + cov**2))


def truncated_normal(mean, cov, n_sigma=3.0):
    sd = mean * cov
    return stats.truncnorm(-n_sigma, n_sigma, loc=mean, scale=sd)


def sample_soil(soil_class: SoilClass, n, rng, rho=RHO_C_PHI):
    """Sampel c', phi', gamma, Ks untuk satu kelas tanah (Gaussian copula c'-phi')."""
    z1 = rng.standard_normal(n)
    z2 = rho * z1 + np.sqrt(1 - rho**2) * rng.standard_normal(n)
    u1, u2 = stats.norm.cdf(z1), stats.norm.cdf(z2)
    c = lognormal_from_mean_cov(soil_class.c_mean, soil_class.c_cov).ppf(u1)
    phi = truncated_normal(soil_class.phi_mean, soil_class.phi_cov).ppf(u2)
    gamma = rng.normal(soil_class.gamma_mean, soil_class.gamma_mean * soil_class.gamma_cov, n)
    ks = soil_class.ks_median * 10 ** (soil_class.ks_log10_sd * rng.standard_normal(n))
    porosity = rng.uniform(*soil_class.drainable_porosity, n)
    return c, phi, gamma, ks, porosity


def _uniform_class(table, scores, rng, n):
    lo = np.array([table[s][0] for s in scores], float)[:, None]
    hi = np.array([table[s][1] for s in scores], float)[:, None]
    return lo + rng.random((len(scores), n)) * (hi - lo)


def sample_physical(scores, n_mc, rng, rho=RHO_C_PHI):
    """
    Sampel semua parameter fisik untuk banyak konfigurasi skor.
    scores: (n_cfg, 6) urutan [soil, geometry, groundwater, rainfall, seismic, vegetation]
    Return dict array (n_cfg, n_mc).
    """
    scores = np.asarray(scores, int)
    n_cfg = len(scores)
    soil_s, geom, gwt, rain, seis, veg = scores.T

    p = {k: np.empty((n_cfg, n_mc)) for k in ("c", "phi", "gamma", "ks", "porosity")}
    for s in np.unique(soil_s):                      # tanah: per kelas
        rows = soil_s == s
        draws = sample_soil(SOIL_CLASSES[s], rows.sum() * n_mc, rng, rho)
        for key, values in zip(("c", "phi", "gamma", "ks", "porosity"), draws):
            p[key][rows] = values.reshape(rows.sum(), n_mc)

    p["beta"] = _uniform_class(SLOPE_ANGLE, geom, rng, n_mc)
    p["thickness"] = THICKNESS[0] + rng.random((n_cfg, n_mc)) * (THICKNESS[1] - THICKNESS[0])
    p["m0"] = _uniform_class(GROUNDWATER_RATIO, gwt, rng, n_mc)
    p["rain_mm"] = _uniform_class(CUMULATIVE_RAIN_MM, rain, rng, n_mc)
    p["duration_hr"] = RAIN_DURATION_HR[0] + rng.random((n_cfg, n_mc)) * (RAIN_DURATION_HR[1] - RAIN_DURATION_HR[0])
    p["kh"] = _uniform_class(SEISMIC_KH, seis, rng, n_mc)
    p["c_root"] = _uniform_class(ROOT_COHESION, veg, rng, n_mc)
    p["root_depth"] = _uniform_class(ROOT_DEPTH, veg, rng, n_mc)
    return p


def water_ratio_cumulative(m0, rain_mm, duration_hr, ks, porosity, z):
    """
    Hujan kumulatif -> kenaikan MAT.
      kapasitas infiltrasi selama kejadian = Ks * D
      air meresap = min(P, Ks * D)       (sisanya limpasan)
      dh = air meresap / porositas drainable
    Sekarang hujan berpengaruh: tanah permeabel menyerap seluruh P,
    tanah lempung dibatasi Ks*D.
    """
    infiltrated_m = np.minimum(rain_mm / 1000.0, ks * duration_hr * 3600.0)
    return np.minimum(1.0, m0 + infiltrated_m / porosity / z)


def fs_from_parameters(p):
    """Hitung FS dari dict parameter fisik (hasil sample_physical atau data lapangan)."""
    z = p["thickness"] / np.cos(np.radians(p["beta"]))
    m = water_ratio_cumulative(p["m0"], p["rain_mm"], p["duration_hr"], p["ks"], p["porosity"], z)
    c_root = effective_root_cohesion(p["c_root"], p["root_depth"], p["thickness"])
    return factor_of_safety(p["c"], p["phi"], p["gamma"], z, p["beta"], m, p["kh"], c_root)


def sample_factor_of_safety_v2(scores, n_mc, rng, rho=RHO_C_PHI):
    return fs_from_parameters(sample_physical(scores, n_mc, rng, rho))
