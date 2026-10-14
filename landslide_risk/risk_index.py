"""
Output: Hazard Index (HI), Vulnerability Index (VI), Risk Index (RI).

    HI  = (sum(w_i * skor_i) - 1) / 4          -> 0..1   (versi bobot, seperti slide)
    HI* = Pf hasil Monte Carlo untuk skor lapangan  (versi fisika langsung, disarankan)
    VI  = (0.667 * skor_jarak + 0.333 * skor_vegetasi - 1) / 4
    RI  = sqrt(HI * VI)                        (rata-rata geometrik)
"""

import numpy as np

from . import config as cfg
from .simulation import site_probability_of_failure


def normalize_score(raw):
    """Ubah skor tertimbang 1.0-5.0 menjadi indeks 0.0-1.0."""
    return (raw - 1.0) / 4.0


def hazard_index_weighted(scores, weights):
    """HI versi kerangka asli: jumlah tertimbang skor, dinormalisasi ke 0-1."""
    raw = float(np.dot(weights, scores))
    return {"hi_raw": raw, "hi": normalize_score(raw),
            "contribution": np.asarray(weights) * np.asarray(scores)}


def settlement_distance_score(distance_m):
    """Konversi jarak permukiman (m) ke skor 1-5."""
    for score, (lo, hi) in cfg.SETTLEMENT_DISTANCE_SCORE.items():
        if lo <= distance_m < hi:
            return score
    raise ValueError(f"Jarak tidak valid: {distance_m}")


def vulnerability_index(distance_score, vegetation_score):
    w = cfg.VI_WEIGHTS
    raw = w["settlement_distance"] * distance_score + w["vegetation_runout"] * vegetation_score
    return {"vi_raw": raw, "vi": normalize_score(raw)}


def risk_index(hi, vi):
    return float(np.sqrt(hi * vi))


def classify(ri):
    for upper, code, name, action in cfg.RISK_CLASSES:
        if ri < upper:
            return {"class": code, "name": name, "action": action}


def assess_site(field_scores, settlement_distance_m, weights):
    """
    Penilaian satu lereng.

    field_scores          : dict {variabel: skor 1-5} untuk X1..X6
    settlement_distance_m : jarak permukiman terdekat (m)
    weights               : bobot konsensus (urutan cfg.VARIABLES)

    Mengembalikan dua versi RI:
      - "weighted" : HI dari bobot konsensus (metode slide)
      - "physics"  : HI = Pf Monte Carlo langsung (menangkap interaksi & ambang)
    """
    scores = np.array([field_scores[v] for v in cfg.VARIABLES])
    dist_score = settlement_distance_score(settlement_distance_m)
    vi = vulnerability_index(dist_score, field_scores["vegetation"])

    hi_w = hazard_index_weighted(scores, weights)
    site_pf = site_probability_of_failure(scores)

    result = {"scores": dict(zip(cfg.VARIABLES, scores.tolist())),
              "distance_score": dist_score, **vi, "site_pf": site_pf}
    for label, hi in (("weighted", hi_w["hi"]), ("physics", site_pf["pf"])):
        ri = risk_index(hi, vi["vi"])
        result[label] = {"hi": hi, "ri": ri, **classify(ri)}
    result["weighted"]["hi_raw"] = hi_w["hi_raw"]
    result["weighted"]["contribution"] = dict(zip(cfg.VARIABLES, hi_w["contribution"].round(4).tolist()))
    return result
