"""
Hidrologi TRANSIEN: respons tekanan air pori terhadap hujan (Iverson, 2000).

Ini adalah dasar model TRIGRS (Baum et al., 2002; 2008). Persamaan Richards
dilinearisasi untuk tanah jenuh/hampir jenuh pada lereng panjang (Z^2/A << 1),
sehingga tekanan air pori menyebar ke bawah sebagai proses DIFUSI:

    d(psi)/dt = (D0 / cos^2(alpha)) d2(psi)/dZ2          (Z vertikal, ke bawah)

Solusi (Iverson 2000, persamaan 27-28), untuk hujan intensitas Iz selama T:

    psi(Z,t) = (Z - d) * beta + Z * (Iz/Kz) * R(t*)                   t <= T
    psi(Z,t) = (Z - d) * beta + Z * (Iz/Kz) * [R(t*) - R(t* - T*)]    t >  T

    beta  = cos^2(alpha) - (Iz/Kz)_LT     (komponen tunak/background)
    t*    = t / (Z^2 / D_hat),   T* = T / (Z^2 / D_hat),   D_hat = 4 D0 / cos^2(alpha)

KOREKSI PENTING: Iverson (2000) mencetak D_hat = 4 D0 cos^2(alpha). Itu
salah (kesalahan transformasi koordinat, ditemukan mahasiswa R. Rigon;
lihat manual TRIGRS 2.0, Baum et al. 2008, OFR 2008-1159, hlm. 25). Kode
resmi TRIGRS v2.1 (iverson.f95, baris 41) memakai dhat = 4*D0/cos^2
("added 8 Jan 2013, RLB"). Modul ini mengikuti bentuk yang dikoreksi.
    R(t*) = sqrt(t*/pi) * exp(-1/t*) - erfc(1/sqrt(t*))

Batasan yang diterapkan (seperti TRIGRS):
  - Iz <= Kz: hujan di atas kapasitas infiltrasi menjadi limpasan
  - psi <= beta * Z: tekanan tidak boleh melebihi muka air di permukaan tanah
  - psi < 0 (di atas muka air) tidak memberi sumbangan suction (konservatif)

Yang TIDAK dimodelkan: zona tak jenuh/suction (TRIGRS opsi Gardner),
dasar kedap pada kedalaman terbatas, aliran lateral, evapotranspirasi.
"""

import numpy as np
from scipy.special import erfc

from .physics import effective_root_cohesion, factor_of_safety


def iverson_R(t_star):
    """Fungsi respons R(t*) (Iverson 2000). R = 0 untuk t* <= 0."""
    t = np.asarray(t_star, dtype=float)
    out = np.zeros_like(t)
    pos = t > 0
    tp = t[pos]
    out[pos] = np.sqrt(tp / np.pi) * np.exp(-1.0 / tp) - erfc(1.0 / np.sqrt(tp))
    return out


def pressure_head(Z, d, alpha_deg, Iz, Ks, D0, t, T, Iz_lt=0.0, cap=True):
    """
    Tekanan air pori psi (m) pada kedalaman vertikal Z (m) dan waktu t (s)
    setelah awal hujan berintensitas Iz (m/s) selama T (s).

    d     : kedalaman muka air tanah awal (m, vertikal dari permukaan)
    D0    : difusivitas hidraulik jenuh (m^2/s)
    Iz_lt : infiltrasi jangka panjang (m/s), menentukan beta
    cap   : batasi psi <= beta*Z (False hanya untuk verifikasi persamaan difusi)
    """
    alpha = np.radians(alpha_deg)
    cos2 = np.cos(alpha) ** 2
    iz = np.minimum(Iz, Ks)                         # kelebihan -> limpasan
    beta = cos2 - np.minimum(Iz_lt, Ks) / Ks
    d_hat = 4.0 * D0 / cos2                         # bentuk terkoreksi (TRIGRS)
    t_star = t * d_hat / Z**2
    T_star = T * d_hat / Z**2
    response = iverson_R(t_star) - np.where(t > T, iverson_R(t_star - T_star), 0.0)
    psi = (Z - d) * beta + Z * (iz / Ks) * response
    return np.minimum(psi, beta * Z) if cap else psi   # muka air maksimum di permukaan


def water_ratio_transient(m0, rain_mm, duration_hr, ks, d0, z, beta_deg,
                          time_factors=(1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0)):
    """
    Rasio m (setara hidrostatik sejajar lereng) yang PALING KRITIS selama dan
    setelah hujan, untuk dipakai di persamaan FS infinite slope.

    Hubungan dengan model statik: tekanan hidrostatik sejajar lereng
    psi = m * z * cos^2(beta), sehingga m = psi / (z cos^2 beta).

    Hujan kumulatif P (mm) selama D jam -> intensitas rata-rata Iz = P / D.
    FS dievaluasi pada t = D x time_factors (puncak tekanan di kedalaman bisa
    tercapai SETELAH hujan berhenti), lalu diambil m maksimum.
    """
    cos2 = np.cos(np.radians(beta_deg)) ** 2
    T = duration_hr * 3600.0
    Iz = (rain_mm / 1000.0) / T
    d = z * (1.0 - m0)
    m = np.full(np.broadcast(m0, z).shape, -np.inf)
    for f in time_factors:
        psi = pressure_head(z, d, beta_deg, Iz, ks, d0, f * T, T)
        m = np.maximum(m, psi / (z * cos2))
    return np.clip(m, 0.0, 1.0)


def fs_transient_from_parameters(p, d0):
    """FS dengan hidrologi transien; p = dict parameter (lihat parameters_v2)."""
    z = p["thickness"] / np.cos(np.radians(p["beta"]))
    m = water_ratio_transient(p["m0"], p["rain_mm"], p["duration_hr"], p["ks"], d0, z, p["beta"])
    c_root = effective_root_cohesion(p["c_root"], p["root_depth"], p["thickness"])
    return factor_of_safety(p["c"], p["phi"], p["gamma"], z, p["beta"], m, p["kh"], c_root)


# ---------------------------------------------------------------------------
# Verifikasi: solusi numerik independen (Crank-Nicolson) dari persamaan difusi
# ---------------------------------------------------------------------------
def numerical_pressure_response(Z_eval, alpha_deg, Iz, Ks, D0, t_eval, T, z_max=None, nz=801, nt=4000):
    """
    Selesaikan d(psi')/dt = (D0 / cos^2 alpha) d2(psi')/dZ2 dengan beda hingga
    Crank-Nicolson, psi'(Z,0) = 0, d(psi')/dZ = -Iz/Ks di Z=0 selama hujan
    (0 sesudahnya), psi' = 0 di Z = z_max (jauh). Mengembalikan psi'(Z_eval, t_eval).
    Dipakai HANYA untuk memverifikasi solusi analitik Iverson.
    """
    D = D0 / np.cos(np.radians(alpha_deg)) ** 2
    iz = min(Iz, Ks)
    if z_max is None:
        z_max = 10.0 * max(Z_eval.max(), np.sqrt(D * t_eval.max()))
    z = np.linspace(0.0, z_max, nz)
    dz = z[1] - z[0]
    dt = t_eval.max() / nt
    r = D * dt / dz**2
    n = nz - 1                                       # unknowns z[0..nz-2]; z[-1] fixed at 0
    # Matrices for interior + Neumann ghost node at Z=0
    main_a = np.full(n, 1 + r); off_a = np.full(n - 1, -r / 2)
    main_b = np.full(n, 1 - r); off_b = np.full(n - 1, r / 2)
    off_a_up = off_a.copy(); off_b_up = off_b.copy()
    off_a_up[0] = -r; off_b_up[0] = r                 # ghost node: psi_-1 = psi_1 + 2 dz g
    from scipy.linalg import solve_banded
    ab = np.zeros((3, n)); ab[0, 1:] = off_a_up; ab[1] = main_a; ab[2, :-1] = off_a
    psi = np.zeros(n)
    out = {}
    times = np.sort(np.asarray(t_eval))
    k = 0
    for step in range(1, nt + 1):
        t0, t1 = (step - 1) * dt, step * dt
        g0 = -iz / Ks if t0 < T else 0.0
        g1 = -iz / Ks if t1 <= T else 0.0
        rhs = main_b * psi
        rhs[:-1] += off_b_up * psi[1:]
        rhs[1:] += off_b * psi[:-1]
        # ghost-node flux terms (psi_-1 = psi_1 - 2 dz g)
        rhs[0] += -r * dz * (g0 + g1)
        psi = solve_banded((1, 1), ab, rhs)
        while k < len(times) and t1 >= times[k] - 1e-9:
            out[times[k]] = np.interp(Z_eval, z[:-1], psi)
            k += 1
    return np.array([out[t] for t in t_eval])
