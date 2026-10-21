# Bagaimana model ini dicek

**Tanggal:** 21 Oktober 2026

Dokumen ini menjawab satu pertanyaan: **apa saja yang sudah dibuktikan tentang model, dengan cara apa, dan apa yang belum.**

Pengecekan mengikuti kerangka Verification & Validation (V&V), Oberkampf, Trucano & Hirsch (2003), SAND2003-3769:

| Istilah | Pertanyaan yang dijawab |
|---|---|
| **Verifikasi** | Apakah persamaan dipecahkan dengan benar? |
| **Cek numerik** | Apakah noise simulasi bisa mengubah kesimpulan? |
| **Validasi** | Apakah prediksi cocok dengan kejadian nyata? |
| **Plausibilitas** | Apakah perilaku model masuk akal dibanding pengetahuan empiris? Ini lebih lemah dari validasi. |

Semua cek bisa dijalankan ulang:

```bash
python -m pytest -q          # 26 uji otomatis
python run_engine.py         # tabel penerimaan → results/engine/acceptance.md
python audit/run_audit.py    # audit bias → results/audit/
python audit/run_hydrology.py
```

---

## 1. Verifikasi fisika

| Kode | Cek | Pembanding | Hasil | Lokasi |
|---|---|---|---|---|
| V1 | Infinite slope, c′ = 0, kering: FS = tan φ′/tan β | Analitik (Skempton & DeLory 1957) | Galat 1e-16 | `tests/test_model.py`, `run_engine.py` |
| V2 | Bishop, φ = 0, β = 45/60/75/90° | Taylor (1937), lingkaran kaki. Angka Ns dihitung ulang secara independen saat verifikasi referensi | 3,7% / 0,1% / 0,2% / 0,1% | `tests/test_audit_guards.py` |
| V3 | Bishop, c′ = 0 → infinite slope | Analitik | 0,1% | `run_engine.py` |
| V4 | Bishop, ACADS 1(a) | FS wasit 1,00 (Giam & Donald 1989; terverifikasi dari manual RS2) | 0,991 (0,9%) | `run_engine.py` |
| V5 | FORM vs Monte Carlo | Dua metode independen | Selisih Pf 0,0008 | `run_engine.py` |
| V6 | Batasan monoton engine | Dijamin konstruksi (cek implementasi, bukan validasi) | 0 pelanggaran | `run_engine.py` |
| H1 | Iverson analitik vs Crank–Nicolson | Solver numerik independen | ≤ 0,7 mm | `tests/test_hydrology.py` |
| H2 | Konvensi difusivitas D̂ | Bentuk deret TRIGRS (kode resmi `iverson.f95`) | Identik | `tests/test_hydrology.py` |
| H3 | Batas R, tanpa hujan, limpasan, batas ψ, puncak pasca-hujan | Sifat matematis | Lolos | `tests/test_hydrology.py` |

**Bug yang tertangkap oleh verifikasi:**
1. Kedalaman vertikal konstan membuat FS naik di atas 45°.
2. Bishop memberi FS 45% di bawah Taylor, karena clipping m_α dan busur yang melewati setengah lingkaran atas.
3. Hidrologi memakai D̂ versi cetak Iverson yang salah, sehingga respons transien terlalu kecil hingga 22×.

Bug ketiga **tidak** tertangkap oleh verifikasi Crank–Nicolson, karena solver itu memakai persamaan yang sama. Bug ini baru tertangkap saat referensi dicek ke kode TRIGRS. Pelajarannya: verifikasi juga harus membandingkan dengan **sumber independen**, bukan hanya dengan solusi numerik dari persamaan yang sama.

---

## 2. Cek numerik

| Kode | Cek | Hasil |
|---|---|---|
| N1 | Lebar CI 95% Pf per konfigurasi (N = 400) | ≤ 0,049 (analitik dari N) |
| N2 | Stabilitas antar seed: rata-rata \|ΔPf\| | 0,016 |
| N3 | Stabilitas antar seed: indeks Sobol | ≤ 0,0004 |
| N4 | COV Pf studi kasus (N = 20.000) | 0,003 |
| – | Noise Monte Carlo vs galat skoring | s.d. 0,017 vs ≈ 0,16 (galat skoring ~9× lebih besar) |

---

## 3. Validasi terhadap kejadian nyata

Data: 575 kasus lereng (Ma et al. 2022). Validasi silang dikelompokkan (5-fold × 5), sehingga kasus hampir-duplikat tidak terpisah antara data latih dan uji.

| Kode | Cek | Hasil | Status |
|---|---|---|---|
| A1 | AUC engine hibrida, seluruh kasus | 0,860 (CI 0,832–0,896) | Lolos |
| A2 | Lebih baik dari regresi logistik | +0,13 | Lolos |
| A3 | Lebih baik dari fisika saja | +0,22 | Lolos |
| A4 | Kalibrasi (ECE) | 0,077 | Lolos |
| A5 | Brier | 0,151 | Lolos |
| A6 | Selisih AUC karena kebocoran | 0,014 | Lolos |
| A7 | Pf fisika terkalibrasi sebagai probabilitas | ECE 0,33 | **Gagal** |
| A8 | Alat skor lapangan (6 skor → Pf) vs kejadian longsor | Belum ada data | **Tertunda** |
| A9 | Validasi spasial pada inventaris Indonesia | Data tersedia (Samodra 2024), belum dikerjakan | **Tertunda** |
| T1 | Validasi temporal hidrologi transien (tanggal kejadian + hujan) | Data tersedia (NASA GLC + IMERG/CHIRPS), belum dikerjakan | **Tertunda** |

---

## 4. Cek plausibilitas (bukan validasi)

| Cek | Hasil |
|---|---|
| Urutan pengaruh parameter vs literatur | Sejalan: kekuatan tanah, geometri dan kedalaman dominan; hujan lewat air anteseden |
| Ambang I–D model vs ambang empiris (Guzzetti 2008; Banjarmangu; Hidayat 2019; Yuniawan 2022) | Untuk durasi ≥ 12 jam di tanah permeabel: masuk rentang. Untuk hujan singkat: model tidak bisa memicu longsor (batasan) |
| Kurva Pf naik monoton terhadap skor | Ya, untuk semua variabel |

---

## 5. Audit integritas analisis

Lihat `docs/AUDIT.md`. Ringkasnya:
- Klaim AUC lama (0,903) dikoreksi menjadi 0,860.
- "Mengalahkan AHP" ditarik, karena AHP tidak pernah diuji.
- Setiap ambang penerimaan diberi label asal: literatur, ditetapkan proyek, atau analitik.

---

## 6. Verifikasi referensi

Lihat `docs/VERIFIKASI_REFERENSI.md`. Sebanyak 151 butir sitasi dan angka diperiksa ke sumber, dan koreksinya sudah diterapkan ke laporan, kode dan kajian literatur.
