"""Uji kewajaran fisika dan reproduksi angka studi kasus di slide."""

import numpy as np
import pytest

from landslide_risk.physics import factor_of_safety, rainfall_to_water_ratio
from landslide_risk.risk_index import classify, hazard_index_weighted, risk_index, vulnerability_index
from landslide_risk.simulation import lhs_score_configurations, run_simulation

BASE = dict(c=5.0, phi_deg=30.0, gamma=19.0, z=2.0, beta_deg=35.0, m=0.0, kh=0.0)


def test_dry_cohesionless_slope_matches_textbook():
    # c = 0, kering, statik  ->  FS = tan(phi) / tan(beta)
    fs = factor_of_safety(**{**BASE, "c": 0.0})
    assert fs == pytest.approx(np.tan(np.radians(30)) / np.tan(np.radians(35)))


@pytest.mark.parametrize("key, worse", [("m", 1.0), ("kh", 0.2), ("beta_deg", 45.0), ("c", 1.0)])
def test_each_trigger_lowers_fs(key, worse):
    assert factor_of_safety(**{**BASE, key: worse}) < factor_of_safety(**BASE)


def test_root_cohesion_raises_fs():
    assert factor_of_safety(**BASE, c_root=5.0) > factor_of_safety(**BASE)


def test_rain_above_ks_becomes_runoff():
    # Ks = 1e-6 m/s = 3.6 mm/jam: hujan 50 dan 200 mm/jam meresap sama banyak
    args = dict(m0=0.2, duration_hr=2.0, ks_m_s=1e-6, porosity=0.1, z=2.0)
    assert rainfall_to_water_ratio(rain_mm_hr=50, **args) == rainfall_to_water_ratio(rain_mm_hr=200, **args)


def test_lhs_is_balanced():
    scores = lhs_score_configurations(1200, np.random.default_rng(0))
    for col in scores.T:
        assert np.all(np.bincount(col, minlength=6)[1:] == 240)


def test_pf_increases_from_safe_to_critical():
    df = run_simulation(n_configs=200, n_mc=200, seed=1)
    safe = df[(df.soil <= 2) & (df.geometry <= 2)].pf.mean()
    critical = df[(df.soil >= 4) & (df.geometry >= 4)].pf.mean()
    assert critical > safe + 0.3


def test_slide_case_study_numbers():
    weights = np.array([0.538, 0.373, 0.016, 0.001, 0.018, 0.054])
    scores = np.array([3, 4, 4, 4, 1, 2])
    hi = hazard_index_weighted(scores, weights)
    vi = vulnerability_index(distance_score=4, vegetation_score=2)
    assert hi["hi_raw"] == pytest.approx(3.300, abs=1e-3)
    assert hi["hi"] == pytest.approx(0.575, abs=1e-3)
    assert vi["vi"] == pytest.approx(0.584, abs=1e-3)
    ri = risk_index(hi["hi"], vi["vi"])
    assert ri == pytest.approx(0.579, abs=1e-3)
    assert classify(ri)["class"] == "III"
