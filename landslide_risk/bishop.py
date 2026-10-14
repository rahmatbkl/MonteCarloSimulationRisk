"""
Physics engine tingkat 3: Bishop Simplified untuk lereng homogen
(bidang gelincir lingkaran), dengan pencarian lingkaran kritis.

Dipakai untuk lereng TINGGI (H puluhan-ratusan meter) seperti pada database
kasus lereng (gamma, c, phi, beta, H, ru), di mana model infinite slope
tidak berlaku.

Geometri (kaki lereng di titik asal):
    y = 0                untuk x < 0        (dasar)
    y = x * tan(beta)    untuk 0 <= x <= L  (muka lereng), L = H / tan(beta)
    y = H                untuk x > L        (puncak)

Bishop Simplified (keseimbangan momen, gaya antar-irisan horizontal):
    FS = sum[ (c*b + (W - u*b) * tan(phi)) / m_alpha ] / sum[ W * sin(alpha) ]
    m_alpha = cos(alpha) + sin(alpha) * tan(phi) / FS
    u = ru * gamma * h      (rasio tekanan pori ru)
Diselesaikan iteratif. Semua lingkaran kandidat dihitung sekaligus (vektor).
"""

import numpy as np


def _ground(x, H, beta_rad):
    return np.clip(x * np.tan(beta_rad), 0.0, H)


def _candidate_circles(H, beta_rad, n_exit=6, n_entry=16, n_sag=14):
    """
    Lingkaran kandidat ditentukan oleh titik keluar P1 (di/di depan kaki),
    titik masuk P2 (di muka/puncak lereng), dan sagitta s (kedalaman busur
    dari tali busur). s kecil -> bidang hampir datar (mendekati infinite slope),
    s besar -> lingkaran dalam (base failure).
    """
    L = H / np.tan(beta_rad)
    x1 = np.linspace(-1.0 * H, 0.0, n_exit)
    x2 = np.linspace(0.15 * L, L + 1.5 * H, n_entry)
    X1, X2, S = np.meshgrid(x1, x2, np.linspace(0.02, 0.5, n_sag), indexing="ij")
    X1, X2, S = X1.ravel(), X2.ravel(), S.ravel()

    y1, y2 = _ground(X1, H, beta_rad), _ground(X2, H, beta_rad)
    dx, dy = X2 - X1, y2 - y1
    chord = np.hypot(dx, dy)
    sag = S * chord
    R = (chord**2 / 4 + sag**2) / (2 * sag)
    nx, ny = -dy / chord, dx / chord                     # normal ke atas
    xc = (X1 + X2) / 2 + nx * (R - sag)
    yc = (y1 + y2) / 2 + ny * (R - sag)
    return X1, X2, xc, yc, R


def bishop_fs(gamma, c, phi_deg, beta_deg, H, ru, n_slices=40, n_iter=30, return_all=False):
    """
    FS minimum (lingkaran kritis) untuk satu lereng homogen.
    Return (fs_min, info_lingkaran_kritis).
    """
    beta = np.radians(beta_deg)
    tan_phi = np.tan(np.radians(phi_deg))
    x1, x2, xc, yc, R = _candidate_circles(H, beta)

    # Irisan: titik tengah tiap irisan antara x1 dan x2
    frac = (np.arange(n_slices) + 0.5) / n_slices
    x = x1[:, None] + frac[None, :] * (x2 - x1)[:, None]
    b = ((x2 - x1) / n_slices)[:, None]
    inside = np.clip(R[:, None] ** 2 - (x - xc[:, None]) ** 2, 1e-12, None)
    y_base = yc[:, None] - np.sqrt(inside)
    h = np.clip(_ground(x, H, beta) - y_base, 0.0, None)
    sin_a = np.clip((x - xc[:, None]) / R[:, None], -0.999, 0.999)
    cos_a = np.sqrt(1 - sin_a**2)

    loaded = h > 0
    W = gamma * h * b
    u = ru * gamma * h
    # Pembilang Bishop per irisan: c*b + (W - u*b) * tan(phi), tidak boleh negatif
    resist_num = np.where(loaded, c * b + np.maximum(W - u * b, 0.0) * tan_phi, 0.0)
    driving = (W * sin_a).sum(1)

    fs = np.full(len(R), 1.0)
    for _ in range(n_iter):
        m_alpha = cos_a + sin_a * tan_phi / fs[:, None]
        fs = (resist_num / np.maximum(m_alpha, 1e-3)).sum(1) / np.where(driving > 0, driving, np.nan)

    # Kriteria Whitman & Bailey (1967): lingkaran dengan m_alpha < 0.2 pada
    # irisan yang terbebani dianggap tidak valid (bukan di-clip, karena
    # clipping memotong tahanan dan membuat FS terlalu rendah).
    m_alpha = cos_a + sin_a * tan_phi / fs[:, None]
    # Kedua ujung busur harus berada di setengah lingkaran BAWAH (yc >= y1, y2);
    # jika tidak, "bidang gelincir" berakhir dengan potongan vertikal tanpa
    # tahanan dan FS menjadi terlalu rendah.
    y1, y2 = _ground(x1, H, beta), _ground(x2, H, beta)
    valid = ((driving > 0) & np.isfinite(fs) & (fs > 0) & (yc >= y1) & (yc >= y2)
             & np.all(~loaded | (m_alpha >= 0.2), axis=1))
    fs = np.where(valid, fs, np.inf)
    k = int(np.argmin(fs))
    info = {"xc": xc[k], "yc": yc[k], "R": R[k], "x_exit": x1[k], "x_entry": x2[k],
            "slices_x": x[k], "slices_base": y_base[k], "slices_h": h[k]}
    if return_all:   # untuk visualisasi: semua lingkaran kandidat
        info["all"] = {"xc": xc, "yc": yc, "R": R, "x1": x1, "x2": x2, "fs": fs}
    return float(fs[k]), info


def bishop_fs_samples(beta_deg, H, ru, gamma, c, phi_deg, n_circles=30, n_slices=40, n_iter=30,
                      mean_params=None):
    """
    Monte Carlo Bishop: FS untuk banyak sampel parameter (gamma, c, phi berupa array).

    Pendekatan standar untuk efisiensi: cari dulu lingkaran kritis dengan
    parameter rata-rata (mean_params), simpan n_circles lingkaran dengan FS
    terendah, lalu setiap sampel dievaluasi pada lingkaran-lingkaran tersebut
    dan diambil minimumnya. Asumsi: lingkaran kritis tidak berpindah jauh
    ketika parameter berubah di sekitar rata-ratanya.
    """
    g0, c0, p0 = mean_params if mean_params else (np.median(gamma), np.median(c), np.median(phi_deg))
    _, info = bishop_fs(g0, c0, p0, beta_deg, H, ru, n_slices, n_iter, return_all=True)
    allc = info["all"]
    order = np.argsort(allc["fs"])[:n_circles]
    order = order[np.isfinite(allc["fs"][order])]
    x1, x2, xc, yc, R = (allc[k][order] for k in ("x1", "x2", "xc", "yc", "R"))

    beta = np.radians(beta_deg)
    frac = (np.arange(n_slices) + 0.5) / n_slices
    x = x1[:, None] + frac[None, :] * (x2 - x1)[:, None]                 # (k, s)
    b = ((x2 - x1) / n_slices)[:, None]
    y_base = yc[:, None] - np.sqrt(np.clip(R[:, None] ** 2 - (x - xc[:, None]) ** 2, 1e-12, None))
    h = np.clip(_ground(x, H, beta) - y_base, 0.0, None)
    sin_a = np.clip((x - xc[:, None]) / R[:, None], -0.999, 0.999)
    cos_a = np.sqrt(1 - sin_a**2)
    loaded = h > 0

    gamma = np.asarray(gamma, float)[:, None, None]
    c = np.asarray(c, float)[:, None, None]
    tan_phi = np.tan(np.radians(np.asarray(phi_deg, float)))[:, None, None]
    W = gamma * h * b                                                      # (n, k, s)
    resist = np.where(loaded, c * b + np.maximum(W * (1 - ru), 0.0) * tan_phi, 0.0)
    driving = (W * sin_a).sum(2)
    fs = np.ones(driving.shape)
    for _ in range(n_iter):
        m_alpha = np.maximum(cos_a + sin_a * tan_phi / fs[:, :, None], 1e-3)
        fs = (resist / m_alpha).sum(2) / np.where(driving > 0, driving, np.nan)
    fs = np.where(np.isfinite(fs) & (fs > 0), fs, np.inf)
    return fs.min(axis=1)


def bishop_fs_many(df):
    """FS Bishop untuk setiap baris DataFrame (kolom gamma, c, phi, beta, H, ru)."""
    return np.array([bishop_fs(r.gamma, r.c, r.phi, r.beta, r.H, r.ru)[0]
                     for r in df.itertuples()])
