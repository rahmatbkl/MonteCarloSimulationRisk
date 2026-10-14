"""
Machine engine hibrida: fisika (Bishop FS) + machine learning, dengan
validasi yang jujur (cross-validation berkelompok).

Empat model dibandingkan pada data kasus nyata yang SAMA:

  A. Heuristik  : indeks skor berbobot sama (mewakili pendekatan skoring/AHP;
                  setiap variabel diberi skor kuintil 1-5 lalu dijumlah).
  B. Fisika     : FS Bishop -> probabilitas lewat kalibrasi logistik log(FS).
  C. ML murni   : Gradient Boosting pada 6 parameter mentah.
  D. Hibrida    : Gradient Boosting pada parameter mentah + fitur fisika
                  (log FS, c/(gamma*H), tan(phi)/tan(beta)), dengan
                  BATASAN MONOTON yang konsisten fisika:
                     FS naik -> peluang gagal turun,  c, phi naik -> turun,
                     beta, ru naik -> naik.
                  Batasan ini mencegah model "belajar" hubungan yang
                  melanggar mekanika tanah dari data yang berisik.

Validasi: StratifiedGroupKFold (kelompok = kasus hampir duplikat) diulang
beberapa kali, + pembanding KFold acak untuk mengukur efek kebocoran.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold

from .metrics import classification_metrics

RAW = ["gamma", "c", "phi", "beta", "H", "ru"]
PHYS = ["log_fs", "stability_number", "friction_ratio"]

# Arah fisik tiap fitur terhadap peluang gagal (+1 naik, -1 turun, 0 bebas)
MONOTONE = {"gamma": 0, "c": -1, "phi": -1, "beta": 1, "H": 0, "ru": 1,
            "log_fs": -1, "stability_number": -1, "friction_ratio": -1}

# Arah skor heuristik: +1 berarti nilai besar = lebih berbahaya
HEURISTIC_DIRECTION = {"gamma": 1, "c": -1, "phi": -1, "beta": 1, "H": 1, "ru": 1}

# Domain penerapan: lereng TANAH (bukan massa batuan / tambang terbuka)
DOMAIN = {"gamma_max": 23.0, "H_max": 100.0, "ru_max": 0.9}


def add_physics_features(df):
    out = df.copy()
    out["log_fs"] = np.log(np.clip(out["fs"], 1e-3, None))
    out["stability_number"] = out.c / (out.gamma * out.H)
    out["friction_ratio"] = np.tan(np.radians(out.phi)) / np.tan(np.radians(out.beta))
    return out


def in_domain(df):
    return ((df.gamma <= DOMAIN["gamma_max"]) & (df.H <= DOMAIN["H_max"])
            & (df.ru <= DOMAIN["ru_max"])).to_numpy()


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class HeuristicIndex:
    """Skor kuintil 1-5 per variabel (arah sesuai intuisi pakar), bobot sama."""

    def fit(self, X, y=None):
        self.edges_ = {v: np.quantile(X[v], [0.2, 0.4, 0.6, 0.8]) for v in RAW}
        return self

    def score(self, X):
        total = np.zeros(len(X))
        for v in RAW:
            s = np.searchsorted(self.edges_[v], X[v].to_numpy()) + 1
            total += s if HEURISTIC_DIRECTION[v] > 0 else 6 - s
        return (total / len(RAW) - 1) / 4        # 0..1 seperti HI

    def predict_proba(self, X):
        p = self.score(X)
        return np.column_stack([1 - p, p])


class PhysicsCalibrated:
    """P(gagal) = sigmoid(a + b * log FS), hanya 2 parameter (b < 0 diharapkan)."""

    def fit(self, X, y):
        self.lr_ = LogisticRegression().fit(X[["log_fs"]], y)
        return self

    def predict_proba(self, X):
        return self.lr_.predict_proba(X[["log_fs"]])


def make_ml(features, monotone=False, seed=0):
    cst = [MONOTONE[f] for f in features] if monotone else None
    model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_depth=4,
                                           min_samples_leaf=10, l2_regularization=1.0,
                                           monotonic_cst=cst, random_state=seed)
    return _FeatureModel(model, features)


class _FeatureModel:
    def __init__(self, model, features):
        self.model, self.features = model, features

    def fit(self, X, y):
        self.model.fit(X[self.features], y)
        return self

    def predict_proba(self, X):
        return self.model.predict_proba(X[self.features])


MODELS = {
    "A_heuristic": lambda seed: HeuristicIndex(),
    "B_physics": lambda seed: PhysicsCalibrated(),
    "C_ml_raw": lambda seed: make_ml(RAW, seed=seed),
    "D_hybrid": lambda seed: make_ml(RAW + PHYS, monotone=True, seed=seed),
}


# ---------------------------------------------------------------------------
# Validasi
# ---------------------------------------------------------------------------
def cross_validate(df, n_splits=5, n_repeats=5, grouped=True):
    """
    Return:
      folds : DataFrame metrik per fold per model
      oof   : prediksi out-of-fold (dirata-rata antar ulangan) per model
    """
    X, y, groups = df, df["failed"].to_numpy(), df["group"].to_numpy()
    rows, oof = [], {m: np.zeros(len(df)) for m in MODELS}
    for rep in range(n_repeats):
        if grouped:
            splitter = StratifiedGroupKFold(n_splits, shuffle=True, random_state=rep)
            splits = splitter.split(X, y, groups)
        else:
            splits = StratifiedKFold(n_splits, shuffle=True, random_state=rep).split(X, y)
        for fold, (tr, te) in enumerate(splits):
            for name, factory in MODELS.items():
                model = factory(rep).fit(X.iloc[tr], y[tr])
                p = model.predict_proba(X.iloc[te])[:, 1]
                oof[name][te] += p / n_repeats
                rows.append({"model": name, "repeat": rep, "fold": fold,
                             **classification_metrics(y[te], p)})
    return pd.DataFrame(rows), pd.DataFrame(oof)


def summarize(folds):
    keys = ["auc", "accuracy", "tss", "kappa", "brier", "ece"]
    g = folds.groupby("model")[keys]
    return g.mean().round(3).join(g.std().round(3), rsuffix="_sd")


def fit_final(df, seed=0):
    """Latih engine hibrida final pada seluruh data (dalam domain)."""
    return MODELS["D_hybrid"](seed).fit(df, df["failed"].to_numpy())
