"""Verification of the transient (Iverson 2000) hydrology."""

import numpy as np
import pytest

from landslide_risk.hydrology import (iverson_R, numerical_pressure_response, pressure_head,
                                      water_ratio_transient)


def test_response_function_limits():
    assert iverson_R(np.array([0.0, -1.0]))[0] == 0.0
    t = np.array([1e4, 1e6])
    # long-time behaviour: R -> sqrt(t*/pi) - 1 (pressure grows with sqrt(time))
    assert np.allclose(iverson_R(t), np.sqrt(t / np.pi) - 1, rtol=1e-3)


def test_analytic_matches_crank_nicolson():
    alpha, Ks, D0, Iz, T = 35.0, 1e-6, 5e-5, 8e-7, 24 * 3600.0
    Z = np.array([0.5, 1.0, 2.0, 3.0])
    t = np.array([6, 24, 36, 72]) * 3600.0
    num = numerical_pressure_response(Z, alpha, Iz, Ks, D0, t, T)
    ana = np.array([pressure_head(Z, Z, alpha, Iz, Ks, D0, tt, T, cap=False) for tt in t])  # d = Z: no background
    assert np.abs(num - ana).max() < 2e-3          # < 2 mm of pressure head


def test_no_rain_returns_initial_water_table():
    m = water_ratio_transient(np.array([0.4]), np.array([0.0]), np.array([24.0]),
                              np.array([1e-6]), 5e-5, np.array([2.0]), np.array([35.0]))
    assert m[0] == pytest.approx(0.4)


def test_rain_above_ks_is_runoff():
    args = dict(Z=1.5, d=1.5, alpha_deg=35.0, Ks=1e-6, D0=5e-5, t=86400.0, T=86400.0)
    assert pressure_head(Iz=1e-5, **args) == pressure_head(Iz=1e-6, **args)


def test_pressure_capped_at_surface_water_table():
    psi = pressure_head(Z=1.0, d=0.0, alpha_deg=30.0, Iz=1e-6, Ks=1e-6, D0=1e-3, t=3e6, T=3e6)
    assert psi <= np.cos(np.radians(30.0)) ** 2 * 1.0 + 1e-12


def test_deep_response_peaks_after_rain_stops():
    Z, T = 3.0, 6 * 3600.0
    times = np.array([1, 2, 4, 8]) * T
    psi = [pressure_head(Z, Z, 35.0, 1e-6, 1e-6, 2e-5, t, T) for t in times]
    assert np.argmax(psi) > 0                      # maximum after t = T
