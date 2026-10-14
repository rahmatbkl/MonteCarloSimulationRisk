"""Regression guards for errors found in the audit (see docs/AUDIT.md)."""

import numpy as np
import pandas as pd
import pytest

from landslide_risk import engine as E
from landslide_risk.acceptance import group_bootstrap_auc
from landslide_risk.bishop import bishop_fs, bishop_fs_samples


def test_every_physical_input_is_monotone_constrained():
    # Audit: leaving gamma and H free let the model learn non-physical patterns.
    for feature in ("gamma", "c", "phi", "beta", "H", "ru", "log_fs", "stability_number", "friction_ratio"):
        assert E.MONOTONE[feature] != 0, feature


def test_heuristic_baseline_is_not_called_ahp():
    assert "NOT AHP" in E.__doc__ or "BUKAN AHP" in E.__doc__


@pytest.mark.parametrize("beta, ns", [(45, 0.170), (60, 0.191), (75, 0.219), (90, 0.261)])
def test_bishop_matches_taylor_including_45_degrees(beta, ns):
    fs, _ = bishop_fs(18.0, 20.0, 0.0, beta, 10.0, 0.0)
    assert fs == pytest.approx(20 / (ns * 180), rel=0.05)


def test_sampled_bishop_reproduces_deterministic_fs():
    for g, c, p, b, h, ru in [(21.8, 8.6, 32, 28, 13, 0.49), (20, 3, 19.6, 26.57, 10, 0)]:
        fs_det = bishop_fs(g, c, p, b, h, ru)[0]
        fs_mc = bishop_fs_samples(b, h, ru, np.array([g]), np.array([c]), np.array([p]))[0]
        assert fs_mc == pytest.approx(fs_det, rel=1e-6)


def test_cross_validation_returns_single_pass_estimator():
    rng = np.random.default_rng(0)
    n = 120
    df = pd.DataFrame({"gamma": rng.uniform(16, 22, n), "c": rng.uniform(0, 40, n), "phi": rng.uniform(15, 40, n),
                       "beta": rng.uniform(20, 50, n), "H": rng.uniform(5, 50, n), "ru": rng.uniform(0, 0.5, n)})
    df["fs"] = (df.c / (df.gamma * df.H) + np.tan(np.radians(df.phi)) / np.tan(np.radians(df.beta)))
    df["failed"] = (df.fs + rng.normal(0, 0.2, n) < 0.9).astype(int)
    df["group"] = np.arange(n) // 2
    folds, oof, pooled = E.cross_validate(E.add_physics_features(df), n_repeats=2)
    assert set(pooled.index) == set(E.MODELS)
    assert {"auc", "ece", "brier"} <= set(pooled.columns)


def test_group_bootstrap_resamples_groups():
    y = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    groups = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    p = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7, 0.4, 0.6])
    mean, lo, hi = group_bootstrap_auc(y, groups, p, n_boot=200)
    assert lo <= mean <= hi <= 1.0
