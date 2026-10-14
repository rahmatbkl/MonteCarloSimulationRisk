"""
Monte Carlo pada kasus lereng nyata: Pf Bishop probabilistik per kasus.

Setiap kasus dilaporkan dengan satu nilai c', phi', gamma. Di sini nilai
itu dianggap sebagai MEDIAN/rerata, lalu ketidakpastian ditambahkan dengan
COV dari literatur (c' lognormal COV 0.45, phi' normal terpotong COV 0.10,
gamma normal COV 0.05, rho(c',phi') = -0.5). Pf = P[FS < 1].

Tujuan audit: apakah Pf hasil Monte Carlo berperilaku seperti probabilitas
sungguhan (kasus dengan Pf = 0.8 benar-benar gagal ~80%)?
"""

import numpy as np

from .bishop import bishop_fs_samples


def case_pf(cases, cov_c=0.45, cov_phi=0.10, cov_gamma=0.05, rho=-0.5, n=400, seed=0):
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
