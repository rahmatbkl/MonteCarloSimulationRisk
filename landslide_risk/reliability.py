"""
Reliability engine: statistik Pf, indeks reliabilitas beta, konvergensi
Monte Carlo, dan FORM (First Order Reliability Method) sebagai pembanding.

Kenapa perlu dua metode (MC dan FORM)?
    MC   : akurat untuk fungsi apa pun, tetapi butuh banyak sampel bila Pf kecil.
    FORM : sangat cepat, tetapi aproksimasi linear di titik desain.
    Jika keduanya sepakat, kita yakin Pf tidak dipengaruhi galat numerik
    (verifikasi silang - salah satu syarat "reliability" model).
"""

import numpy as np
from scipy import optimize, stats


# ---------------------------------------------------------------------------
# 1. Statistik Monte Carlo
# ---------------------------------------------------------------------------
def pf_statistics(fs, threshold=1.0, confidence=0.95):
    """
    Ringkasan Pf dari sampel FS.

    Return:
      pf        : estimasi probabilitas kegagalan
      ci_low/high : selang kepercayaan Wilson
      cov       : koefisien variasi estimator Pf = sqrt((1-Pf)/(N*Pf))
      beta      : indeks reliabilitas ekuivalen = -Phi^-1(Pf)
    """
    fs = np.asarray(fs).ravel()
    n = fs.size
    k = int((fs < threshold).sum())
    pf = k / n
    lo, hi = wilson_interval(k, n, confidence)
    cov = np.sqrt((1 - pf) / (n * pf)) if k > 0 else np.inf
    return {"pf": pf, "ci_low": lo, "ci_high": hi, "cov": cov, "n": n,
            "failures": k, "beta": beta_from_pf(pf),
            "fs_mean": float(fs.mean()), "fs_std": float(fs.std()),
            "fs_p05": float(np.percentile(fs, 5))}


def wilson_interval(k, n, confidence=0.95):
    """Selang kepercayaan Wilson untuk proporsi k/n (stabil walau k = 0)."""
    z = stats.norm.ppf(0.5 + confidence / 2)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def required_samples(pf, target_cov=0.10):
    """Jumlah sampel MC agar COV estimator Pf <= target: N = (1-Pf)/(COV^2 * Pf)."""
    pf = np.clip(pf, 1e-12, 1 - 1e-12)
    return int(np.ceil((1 - pf) / (target_cov**2 * pf)))


def beta_from_pf(pf):
    """Indeks reliabilitas beta = -Phi^-1(Pf). Pf=0.5 -> 0, Pf=1e-3 -> 3.09."""
    pf = np.clip(pf, 1e-15, 1 - 1e-15)
    return float(-stats.norm.ppf(pf))


def pf_from_beta(beta):
    return float(stats.norm.cdf(-beta))


def convergence_curve(fs, threshold=1.0, n_points=30):
    """Pf kumulatif terhadap jumlah sampel - untuk plot dan cek stabilitas."""
    failed = (np.asarray(fs).ravel() < threshold).astype(float)
    n = np.unique(np.geomspace(50, failed.size, n_points).astype(int))
    pf = np.cumsum(failed)[n - 1] / n
    return n, pf


# ---------------------------------------------------------------------------
# 2. FORM (Hasofer-Lind / iHLRF) dengan transformasi Nataf (Gaussian copula)
# ---------------------------------------------------------------------------
class RandomVariable:
    """Variabel acak dengan distribusi scipy 'frozen', mis. stats.lognorm(...)."""

    def __init__(self, name, dist):
        self.name = name
        self.dist = dist

    def from_normal(self, u):
        """Transformasi standar normal u -> ruang fisik x (inverse CDF)."""
        return self.dist.ppf(stats.norm.cdf(u))


def form(limit_state, variables, correlation=None, max_iter=100, tol=1e-6):
    """
    FORM: cari titik desain u* (titik gagal terdekat ke origin di ruang normal
    standar). beta = |u*|, Pf ~ Phi(-beta).

    limit_state : fungsi g(x_dict) -> FS - 1   (g < 0 berarti gagal)
    variables   : list RandomVariable
    correlation : matriks korelasi di ruang normal (Gaussian copula), opsional

    Diselesaikan sebagai optimasi: min |u|^2  s.t. g(x(u)) = 0  (SLSQP).
    Return: beta, pf, design point (fisik), dan faktor sensitivitas alpha^2.
    """
    d = len(variables)
    L = np.linalg.cholesky(correlation) if correlation is not None else np.eye(d)

    def to_physical(u):
        z = L @ u                               # standar normal berkorelasi
        return {v.name: float(v.from_normal(z[i])) for i, v in enumerate(variables)}

    def g(u):
        return limit_state(to_physical(u))

    if g(np.zeros(d)) <= 0:                     # titik median sudah gagal
        start = np.zeros(d)
    else:
        start = np.full(d, 0.1)

    result = optimize.minimize(lambda u: u @ u, start, method="SLSQP",
                               constraints=[{"type": "eq", "fun": g}],
                               options={"maxiter": max_iter, "ftol": tol})
    u_star = result.x
    beta = float(np.linalg.norm(u_star))
    if g(np.zeros(d)) < 0:                      # median gagal -> beta negatif
        beta = -beta
    alpha = u_star / (np.linalg.norm(u_star) + 1e-15)
    return {"beta": beta, "pf": pf_from_beta(beta), "converged": bool(result.success),
            "design_point": to_physical(u_star),
            "importance": dict(zip([v.name for v in variables], (alpha**2).round(4)))}
