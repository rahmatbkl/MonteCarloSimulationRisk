"""
Analytics engine: tiga "lensa" sensitivitas + bobot konsensus.

    1. SRC   - Standardized Regression Coefficient (efek linear marjinal)
    2. Sobol - indeks total-order via surrogate Gradient Boosting (varians + interaksi)
    3. RF    - Random Forest permutation importance (non-linear & kondisional)

Masing-masing dinormalisasi agar jumlahnya = 1, lalu digabung menjadi
satu bobot konsensus.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

from .config import RANDOM_SEED, VARIABLES


def _normalize(values):
    values = np.clip(np.asarray(values, dtype=float), 0.0, None)
    total = values.sum()
    return values / total if total > 0 else np.full_like(values, 1.0 / len(values))


def src_weights(df, target="pf"):
    """SRC: regresi OLS pada X dan y yang sudah distandarisasi; bobot = |beta_i|."""
    X = df[VARIABLES].to_numpy(float)
    y = df[target].to_numpy(float)
    Xs = (X - X.mean(0)) / X.std(0)
    ys = (y - y.mean()) / y.std()
    design = np.column_stack([np.ones(len(ys)), Xs])
    coef, *_ = np.linalg.lstsq(design, ys, rcond=None)
    beta = coef[1:]
    r2 = 1 - np.sum((ys - design @ coef) ** 2) / np.sum(ys**2)
    return {"weights": _normalize(np.abs(beta)), "beta": beta, "r2": r2}


def sobol_weights(df, target="pf", n_base=8192, seed=RANDOM_SEED):
    """
    Sobol' first-order (S1) dan total-order (ST).

    Langkah:
      1. Latih surrogate Gradient Boosting: skor X1..X6 -> Pf.
      2. Estimator Saltelli (S1) dan Jansen (ST) pada surrogate,
         dengan input skor diskret 1-5 berdistribusi seragam.
    Bobot = ST yang dinormalisasi. Porsi interaksi = (ST - S1) / ST.
    """
    rng = np.random.default_rng(seed)
    X = df[VARIABLES].to_numpy(float)
    y = df[target].to_numpy(float)
    surrogate = GradientBoostingRegressor(n_estimators=400, max_depth=4,
                                          learning_rate=0.05, random_state=seed)
    surrogate.fit(X, y)

    d = len(VARIABLES)
    A = rng.integers(1, 6, size=(n_base, d)).astype(float)
    B = rng.integers(1, 6, size=(n_base, d)).astype(float)
    fA, fB = surrogate.predict(A), surrogate.predict(B)
    variance = np.var(np.concatenate([fA, fB]))

    s1, st = np.zeros(d), np.zeros(d)
    for i in range(d):
        ABi = A.copy()
        ABi[:, i] = B[:, i]
        fABi = surrogate.predict(ABi)
        s1[i] = np.mean(fB * (fABi - fA)) / variance            # Saltelli 2010
        st[i] = 0.5 * np.mean((fA - fABi) ** 2) / variance      # Jansen 1999

    s1 = np.clip(s1, 0, None)
    interaction = np.where(st > 0, np.clip((st - s1) / st, 0, 1), 0.0)
    return {"weights": _normalize(st), "S1": s1, "ST": st,
            "interaction_share": interaction, "surrogate_r2": surrogate.score(X, y)}


def rf_weights(df, target="pf", seed=RANDOM_SEED):
    """Random Forest permutation importance dihitung pada data uji (bukan data latih)."""
    X = df[VARIABLES].to_numpy(float)
    y = df[target].to_numpy(float)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=seed)
    forest = RandomForestRegressor(n_estimators=500, min_samples_leaf=3,
                                   random_state=seed, n_jobs=-1)
    forest.fit(X_tr, y_tr)
    perm = permutation_importance(forest, X_te, y_te, n_repeats=20,
                                  random_state=seed, n_jobs=-1)
    return {"weights": _normalize(perm.importances_mean),
            "importance": perm.importances_mean, "test_r2": forest.score(X_te, y_te)}


def consensus_weights(method_weights, how="geometric"):
    """
    Gabungkan bobot beberapa metode.

    how="geometric"  : rata-rata geometrik (seperti kerangka asli). Hati-hati:
                       satu metode yang memberi ~0 akan "menghapus" variabel itu.
    how="arithmetic" : rata-rata aritmetik, lebih toleran terhadap ketidaksepakatan.
    """
    W = np.vstack(list(method_weights.values()))
    if how == "geometric":
        combined = np.exp(np.log(np.clip(W, 1e-9, None)).mean(axis=0))
    elif how == "arithmetic":
        combined = W.mean(axis=0)
    else:
        raise ValueError("how harus 'geometric' atau 'arithmetic'")
    return _normalize(combined)


def run_sensitivity(df, target="pf"):
    """Jalankan ketiga metode dan kembalikan (tabel bobot, detail tiap metode)."""
    src = src_weights(df, target)
    sobol = sobol_weights(df, target)
    rf = rf_weights(df, target)
    per_method = {"SRC": src["weights"], "Sobol_ST": sobol["weights"], "RF_perm": rf["weights"]}

    table = pd.DataFrame(per_method, index=VARIABLES)
    table["consensus_geo"] = consensus_weights(per_method, "geometric")
    table["consensus_arith"] = consensus_weights(per_method, "arithmetic")
    table["sobol_S1"] = sobol["S1"]
    table["sobol_ST"] = sobol["ST"]
    table["interaction_share"] = sobol["interaction_share"]

    diagnostics = {"src_r2": src["r2"], "sobol_surrogate_r2": sobol["surrogate_r2"],
                   "rf_test_r2": rf["test_r2"]}
    return table, diagnostics
