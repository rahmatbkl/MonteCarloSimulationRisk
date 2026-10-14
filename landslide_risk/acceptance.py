"""
Protokol penerimaan (acceptance) engine.

Tiga gerbang, mengikuti kerangka Verification & Validation
(Oberkampf, Trucano & Hirsch 2003; ASME V&V):

  1. VERIFIKASI   - apakah persamaan dipecahkan dengan benar?
                    (solusi analitik & benchmark klasik)
  2. NUMERIK      - apakah Monte Carlo cukup presisi & stabil?
                    (selang kepercayaan, stabilitas seed, FORM vs MC)
  3. VALIDASI     - apakah prediksi cocok dengan kejadian nyata?
                    (AUC, kalibrasi, kebocoran data, konsistensi fisika)

Setiap kriteria menyimpan: nilai, ambang, status (PASS / FAIL / PENDING),
dan rujukan ambang.
"""

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass
class Criterion:
    gate: str
    code: str
    description: str
    value: float
    threshold: str
    passed: object          # True / False / None (= PENDING)
    reference: str

    @property
    def status(self):
        return "PENDING" if self.passed is None else ("PASS" if self.passed else "FAIL")


def to_frame(criteria):
    rows = []
    for c in criteria:
        d = asdict(c)
        d["status"] = c.status
        d.pop("passed")
        rows.append(d)
    return pd.DataFrame(rows)


def to_markdown(criteria, title="Acceptance report"):
    lines = [f"# {title}", "", "| Gate | Code | Criterion | Value | Threshold | Status | Reference |",
             "|---|---|---|---|---|---|---|"]
    for c in criteria:
        value = f"{c.value:.4g}" if isinstance(c.value, (int, float, np.floating)) and np.isfinite(c.value) else "-"
        lines.append(f"| {c.gate} | {c.code} | {c.description} | {value} | {c.threshold} | "
                     f"**{c.status}** | {c.reference} |")
    n_pass = sum(c.status == "PASS" for c in criteria)
    lines += ["", f"Passed {n_pass} / {len(criteria)} criteria "
              f"({sum(c.status == 'PENDING' for c in criteria)} pending)."]
    return "\n".join(lines)


def paired_bootstrap_auc_diff(y, p_a, p_b, n_boot=2000, seed=0):
    """CI 95% untuk AUC(a) - AUC(b) pada sampel yang sama (bootstrap berpasangan)."""
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(seed)
    y, p_a, p_b = map(np.asarray, (y, p_a, p_b))
    diffs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        if len(set(y[i])) < 2:
            continue
        diffs.append(roc_auc_score(y[i], p_a[i]) - roc_auc_score(y[i], p_b[i]))
    return float(np.mean(diffs)), float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))
