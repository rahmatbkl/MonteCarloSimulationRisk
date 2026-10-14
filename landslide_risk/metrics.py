"""
Metrik validasi untuk prediksi longsor (klasifikasi gagal/stabil dan
probabilitas).

    Diskriminasi : ROC-AUC  (seberapa baik model membedakan gagal vs stabil)
    Kalibrasi    : Brier score, Expected Calibration Error (ECE)
                   (apakah Pf = 0.7 benar-benar gagal ~70% kasus)
    Klasifikasi  : akurasi, sensitivitas (recall gagal), spesifisitas,
                   Cohen's kappa, True Skill Statistic (TSS)
"""

import numpy as np
from sklearn.metrics import brier_score_loss, cohen_kappa_score, confusion_matrix, roc_auc_score


def expected_calibration_error(y_true, prob, n_bins=10):
    """ECE: rata-rata |frekuensi gagal teramati - probabilitas prediksi| per bin."""
    y_true, prob = np.asarray(y_true), np.asarray(prob)
    bins = np.minimum((prob * n_bins).astype(int), n_bins - 1)
    ece = 0.0
    for b in range(n_bins):
        mask = bins == b
        if mask.any():
            ece += mask.mean() * abs(y_true[mask].mean() - prob[mask].mean())
    return float(ece)


def classification_metrics(y_true, prob, threshold=0.5):
    """Semua metrik sekaligus. y_true: 1 = gagal/longsor, 0 = stabil."""
    y_true = np.asarray(y_true).astype(int)
    prob = np.clip(np.asarray(prob, dtype=float), 0, 1)
    y_pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if tp + fn else np.nan
    spec = tn / (tn + fp) if tn + fp else np.nan
    return {
        "auc": float(roc_auc_score(y_true, prob)) if len(set(y_true)) > 1 else np.nan,
        "accuracy": float((tp + tn) / len(y_true)),
        "sensitivity": float(sens),
        "specificity": float(spec),
        "tss": float(sens + spec - 1),
        "kappa": float(cohen_kappa_score(y_true, y_pred)),
        "brier": float(brier_score_loss(y_true, prob)),
        "ece": expected_calibration_error(y_true, prob),
        "n": int(len(y_true)),
    }


def auc_label(auc):
    """Interpretasi AUC (Hosmer & Lemeshow, 2000)."""
    if auc >= 0.9:
        return "outstanding"
    if auc >= 0.8:
        return "excellent"
    if auc >= 0.7:
        return "acceptable"
    return "poor"


def bootstrap_ci(y_true, prob, metric="auc", n_boot=1000, seed=0, confidence=0.95):
    """Selang kepercayaan bootstrap untuk satu metrik."""
    rng = np.random.default_rng(seed)
    y_true, prob = np.asarray(y_true), np.asarray(prob)
    values = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y_true), len(y_true))
        if len(set(y_true[idx])) < 2:
            continue
        values.append(classification_metrics(y_true[idx], prob[idx])[metric])
    a = (1 - confidence) / 2
    return float(np.quantile(values, a)), float(np.quantile(values, 1 - a))
