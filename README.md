# Landslide Risk Index: Infinite Slope + Monte Carlo

Model penilaian risiko longsor berbasis fisika mekanika tanah. Bobot faktor tidak
ditebak pakar (AHP), melainkan diturunkan dari 480.000 simulasi Factor of Safety.

```
Skor lapangan (1-5) → Infinite Slope FS → Monte Carlo (400×) × LHS (1.200)
→ Sensitivitas (SRC, Sobol', Random Forest) → HI × VI → Risk Index (Kelas I-V)
```

Formulasi matematis lengkap, perbandingan Monte Carlo vs simulasi fisika penuh,
dan catatan kritis ada di **[docs/FORMULASI_MODEL.md](docs/FORMULASI_MODEL.md)**.

## Cara Menjalankan

```bash
pip install -r requirements.txt
python run_pipeline.py            # model v1 (kerangka slide), ~15 detik
python run_engine.py              # engine v2 + protokol penerimaan, ~2 menit
python audit/run_audit.py         # audit bias & efek Monte Carlo, ~9 menit
python report/make_figures.py     # 15 gambar kualitas publikasi (300 dpi)
python report/build_report.py     # laporan PDF teknis
python -m pytest -q               # uji fisika & reproduksi angka slide
```

## Engine v2 (hibrida fisika + machine learning)

| Komponen | File |
|---|---|
| Distribusi parameter dari literatur (lognormal c', normal terpotong phi', copula rho=-0.5, hujan kumulatif) | `landslide_risk/parameters_v2.py` |
| Bishop Simplified + pencarian lingkaran kritis (terverifikasi vs Taylor & ACADS) | `landslide_risk/bishop.py` |
| Pf, Wilson CI, beta, FORM | `landslide_risk/reliability.py` |
| Sobol eksak pada ruang skor 5^6 | `landslide_risk/variance.py` |
| 575 kasus lereng nyata (Ma et al. 2022) + pengelompokan duplikat | `landslide_risk/case_data.py` |
| Engine hibrida (gradient boosting monoton) + CV berkelompok | `landslide_risk/engine.py` |
| Metrik (AUC, Brier, ECE, TSS) dan 19 kriteria penerimaan | `landslide_risk/metrics.py`, `acceptance.py` |
| Pf Monte Carlo per kasus nyata (uji kalibrasi) | `landslide_risk/case_mc.py` |
| Audit bias validasi, efek Monte Carlo, ketidakpastian skoring | `audit/run_audit.py` |

Hasil (versi teraudit, analisis utama = seluruh 575 kasus, CV berkelompok):

| Model | AUC |
|---|---|
| A Skor berbobot sama (**bukan** AHP) | 0,581 |
| B Fisika saja (FS Bishop) | 0,645 |
| E Regresi logistik (pembanding adil) | 0,731 |
| **D Hibrida, monoton penuh (dipakai)** | **0,860** (CI 0,832–0,896) |

Penerimaan: 16 dari 19 kriteria lolos (4 di antaranya cek desain), **1 gagal**
(Pf Monte Carlo fisika tidak terkalibrasi sebagai probabilitas pada lereng nyata,
ECE 0,33), **2 tertunda** (alat skoring lapangan belum divalidasi terhadap kejadian
longsor; validasi spasial Indonesia). Lihat `docs/AUDIT.md`.

> **Penggunaan:** hasil ini untuk riset dan screening, belum untuk keputusan
> evakuasi/relokasi. Setiap hasil Kelas IV–V perlu ditinjau ahli geoteknik.

Dokumen:
- `docs/AUDIT.md`: audit kesalahan, bias validasi, peran Monte Carlo dan skoring
- `report/Landslide_Risk_Engine_Report.pdf`: laporan teknis (konsep, fisika, gradien & matriks, engine, penerimaan, audit)
- `reports/Monte Carlo pengganti AHP longsor.md`: kajian literatur
- `docs/FORMULASI_MODEL.md`: formulasi v1 dan kritik

## Struktur

| File | Isi |
|---|---|
| `landslide_risk/config.py` | Tabel skor → rentang parameter fisik (**kalibrasi di sini**) |
| `landslide_risk/physics.py` | Persamaan FS, infiltrasi hujan, kohesi akar |
| `landslide_risk/simulation.py` | Inner loop Monte Carlo, outer loop LHS, Pf per lokasi |
| `landslide_risk/sensitivity.py` | SRC, Sobol′ (surrogate GBM), RF permutation, konsensus |
| `landslide_risk/risk_index.py` | HI, VI, RI, klasifikasi, penilaian satu lereng |
| `run_pipeline.py` | Menjalankan semuanya dan menulis `results/` |
| `tests/test_model.py` | Uji kewajaran fisika dan reproduksi studi kasus slide |

## Menilai Satu Lereng

```python
from landslide_risk.risk_index import assess_site
import pandas as pd

weights = pd.read_csv("results/weights.csv", index_col=0)["consensus_geo"].to_numpy()
scores = {"soil": 3, "geometry": 4, "groundwater": 4,
          "rainfall": 4, "seismic": 1, "vegetation": 2}

result = assess_site(scores, settlement_distance_m=80, weights=weights)
print(result["weighted"])   # HI dari bobot konsensus (metode slide)
print(result["physics"])    # HI = Pf Monte Carlo langsung (disarankan)
```

## Hasil Utama (seed 42)

- Tanah + geometri = **79%** bobot konsensus. Faktor preparatory mendominasi.
- Studi kasus slide direproduksi persis (HI 0,575, VI 0,584, RI 0,579, Kelas III).
  Namun Pf fisika langsung = 0,85, sehingga **RI 0,70 (Kelas IV)**. HI linear
  meremehkan risiko lereng ini.
- Bobot hujan ≈ 0 adalah **artefak model statik**, bukan bukti bahwa hujan tidak
  penting (lihat dokumen formulasi §7.3).

> Rentang parameter di `config.py` adalah nilai awal dari literatur. Kalibrasi
> dengan data uji tanah lokal dan validasi terhadap inventaris longsor sebelum
> hasilnya dipakai untuk keputusan.
