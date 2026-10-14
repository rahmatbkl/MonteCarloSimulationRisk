"""
Database kasus lereng nyata (stabil / gagal) untuk validasi engine.

Sumber: Ma, J. et al. (2022). "Slope Stability Analysis Using Machine
Learning..." Sensors 22:9166, Appendix A, 627 kasus (311 stabil / 316 gagal),
gabungan beberapa kompilasi (Sah et al. 1994; Lu & Rosenbaum 2003;
Zhou et al. 2019; Kardani et al. 2021; Lin et al.).
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/  (akses terbuka)

Pembersihan:
  - buang gamma < 10 kN/m3 (tidak fisik), beta <= 0, H <= 0
  - kelompokkan kasus yang HAMPIR DUPLIKAT (kompilasi saling tumpang tindih,
    nilai dibulatkan sedikit berbeda). Kelompok ini dipakai untuk
    cross-validation berkelompok, supaya kasus yang sama tidak muncul di data
    latih dan data uji sekaligus (kebocoran yang menggelembungkan AUC).
"""

from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/"
RAW = Path("data/raw/ma2022_sensors.html")
CLEAN = Path("data/slope_cases_ma2022.csv")


def download(path=RAW):
    path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    path.write_bytes(urlopen(req, timeout=60).read())


def _near_duplicate_groups(df):
    """Kasus dengan nilai hampir sama (dibulatkan) dianggap satu kelompok."""
    key = pd.DataFrame({
        "gamma": (df.gamma * 2).round(),          # 0.5 kN/m3
        "c": df.c.round(),                        # 1 kPa
        "phi": df.phi.round(),                    # 1 derajat
        "beta": df.beta.round(),                  # 1 derajat
        "H": np.round(np.log(df.H) / 0.02),       # 2% relatif
        "ru": (df.ru * 50).round(),               # 0.02
    })
    return key.groupby(list(key.columns), sort=False).ngroup().to_numpy()


def load_cases():
    """Return DataFrame bersih: gamma, c, phi, beta, H, ru, failed (1/0), group."""
    if CLEAN.exists():
        return pd.read_csv(CLEAN)
    if not RAW.exists():
        download()
    table = next(t for t in pd.read_html(RAW) if len(t) > 500 and "Status" in t.columns)
    df = table.iloc[:, 1:8].copy()
    df.columns = ["gamma", "c", "phi", "beta", "H", "ru", "status"]
    df["failed"] = (df.pop("status").str.strip().str.lower() == "failure").astype(int)
    df = df[(df.gamma >= 10) & (df.beta > 0) & (df.H > 0)].reset_index(drop=True)
    df["group"] = _near_duplicate_groups(df)
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN, index=False)
    return df
