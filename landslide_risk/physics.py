"""
Physics engine: Infinite Slope Model (Mohr-Coulomb, limit equilibrium).

Semua fungsi bersifat vektor (numpy): input boleh skalar atau array,
sehingga ratusan ribu evaluasi FS dapat dihitung sekaligus tanpa loop.

Persamaan (per satuan luas bidang gelincir pada kedalaman z):

    sigma_n  = gamma * z * cos^2(beta) * (1 - kh * tan(beta))      tegangan normal total
    u        = gamma_w * (m * z) * cos^2(beta)                     tekanan air pori
    tau_res  = c' + c_r,eff + (sigma_n - u) * tan(phi')            gaya penahan
    tau_drv  = gamma * z * cos(beta) * (sin(beta) + kh * cos(beta)) gaya pendorong

    FS = tau_res / tau_drv        (FS < 1  ->  longsor)
"""

import numpy as np

from .config import GAMMA_WATER


def rainfall_to_water_ratio(m0, rain_mm_hr, duration_hr, ks_m_s, porosity, z):
    """
    Hitung rasio muka air tanah m = hw / z setelah hujan.

    Model sederhana (infiltrasi dibatasi kapasitas tanah):
      - Laju infiltrasi  f = min(I, Ks)   -> hujan melebihi Ks menjadi limpasan
      - Kenaikan MAT     dh = f * D / n_e
      - m = min(1, m0 + dh / z)

    Inilah jalur fisik hujan -> tekanan pori. Hujan yang sangat deras di
    tanah lempung (Ks kecil) hampir tidak menaikkan MAT karena air tidak
    sempat meresap - itu sebabnya "intensitas" saja bukan pemicu yang kuat.
    """
    rain_m_s = rain_mm_hr / 1000.0 / 3600.0
    infiltration = np.minimum(rain_m_s, ks_m_s)            # m/s
    water_rise = infiltration * (duration_hr * 3600.0) / porosity  # m
    return np.minimum(1.0, m0 + water_rise / z)


def effective_root_cohesion(root_cohesion, root_depth, z):
    """
    Akar hanya menahan jika menembus bidang gelincir.
    Penyederhanaan: c_r,eff = c_r * min(1, kedalaman_akar / z).
    """
    reach = np.clip(np.divide(root_depth, z), 0.0, 1.0)
    return root_cohesion * reach


def factor_of_safety(c, phi_deg, gamma, z, beta_deg, m, kh, c_root=0.0):
    """
    Factor of Safety infinite slope dengan air pori, seismik pseudo-statik,
    dan kohesi akar.

    Parameter
    ---------
    c        : kohesi efektif tanah c' (kPa)
    phi_deg  : sudut geser efektif phi' (derajat)
    gamma    : berat isi tanah (kN/m3)
    z        : kedalaman bidang gelincir (m)
    beta_deg : sudut lereng (derajat)
    m        : rasio muka air tanah hw/z (0-1)
    kh       : koefisien seismik horizontal (fraksi g)
    c_root   : kohesi akar efektif (kPa)
    """
    beta = np.radians(beta_deg)
    phi = np.radians(phi_deg)
    cos_b, sin_b = np.cos(beta), np.sin(beta)

    normal_stress = gamma * z * cos_b**2 * (1.0 - kh * np.tan(beta))
    pore_pressure = GAMMA_WATER * m * z * cos_b**2
    # Tegangan efektif tidak boleh negatif (tanah tidak menahan tarik).
    effective_normal = np.maximum(normal_stress - pore_pressure, 0.0)

    resisting = c + c_root + effective_normal * np.tan(phi)
    driving = gamma * z * cos_b * (sin_b + kh * cos_b)
    return resisting / driving
