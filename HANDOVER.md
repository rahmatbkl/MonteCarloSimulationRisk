# Serah-terima proyek: Landslide Risk Index berbasis Monte Carlo + fisika

**Tanggal paket:** 21 Oktober 2026 (diperbarui setelah verifikasi referensi dan hidrologi transien)
**Repo:** `rahmatbkl/MonteCarloSimulationRisk`, branch `claude/keen-planck-y8eq2h`

Dokumen ini merangkum seluruh pemahaman, keputusan, hasil, koreksi dan pekerjaan yang belum selesai, supaya proyek bisa dilanjutkan di komputer lokal tanpa membaca ulang percakapan.

---

## 1. Tujuan proyek

Mengganti pembobotan **AHP** (subjektif, tidak bisa direproduksi, bukan probabilitas) pada penilaian risiko longsor di Indonesia dengan model yang bobot dan hazard-nya **dihitung dari mekanika tanah**:

```
Skor lapangan X1..X6 (1-5) → distribusi parameter fisik → Factor of Safety (infinite slope / Bishop)
→ Monte Carlo → Pf → HI ; VI (jarak permukiman, vegetasi) → RI = √(HI·VI) → Kelas I–V
```

Enam variabel (klasifikasi Varnes):

| Variabel | Kelompok | Parameter fisik |
|---|---|---|
| X1 tanah | preparatory | c′, φ′, γ, Ks |
| X2 geometri | preparatory | β, H |
| X6 vegetasi | preparatory | c_r, kedalaman akar |
| X3 muka air tanah | jembatan | m₀ = h_w/z |
| X4 hujan | triggering | P (mm), D (jam) |
| X5 seismik | triggering | k_h = 0,5·PGA |

Sumber awal: dua dek slide (NotebookLM), yaitu "The Landslide Risk Index" dan "Algorithmic Landslide Risk Framework" (480.000 run = 1.200 LHS × 400 MC; bobot konsensus SRC + Sobol + RF; tanah + geometri 91%).

---

## 2. Cara menjalankan

```bash
pip install -r requirements.txt          # numpy scipy scikit-learn pandas matplotlib pytest (+ reportlab lxml untuk PDF)
python run_pipeline.py                   # model v1 (reproduksi kerangka slide), ~15 detik
python run_engine.py                     # engine v2 + protokol penerimaan, ~3 menit
python audit/run_audit.py                # audit bias & efek Monte Carlo, ~9 menit
python audit/run_hydrology.py            # statik vs transien + uji plausibilitas I–D, ~15 detik
python report/make_figures.py            # 15 gambar (300 dpi)
python report/build_report.py            # report/Landslide_Risk_Engine_Report.pdf
python report/build_audit_pdf.py         # report/Audit_Report.pdf
python -m pytest -q                      # 26 tes
```

`run_engine.py` membutuhkan data kasus lereng. Data ini sudah ada di `data/slope_cases_ma2022.csv`. Bila dihapus, data diunduh ulang otomatis dari PMC (Ma et al. 2022).

---

## 3. Peta file

| Path | Isi |
|---|---|
| `landslide_risk/config.py` | Model v1: tabel skor → rentang seragam (sesuai slide) |
| `landslide_risk/physics.py` | Persamaan FS infinite slope (air pori, seismik pseudo-statik, akar) |
| `landslide_risk/simulation.py` | v1: LHS × Monte Carlo, Pf per lokasi |
| `landslide_risk/sensitivity.py` | v1: SRC, Sobol (surrogate GBM), RF permutation, konsensus |
| `landslide_risk/risk_index.py` | HI, VI, RI, klasifikasi |
| `landslide_risk/parameters_v2.py` | **v2**: distribusi literatur (c′ lognormal, φ′ normal terpotong, copula ρ = −0,5), hujan kumulatif, β ≤ 60° |
| `landslide_risk/bishop.py` | Bishop Simplified + pencarian lingkaran kritis; versi Monte Carlo (`bishop_fs_samples`) |
| `landslide_risk/reliability.py` | Pf, Wilson CI, β, FORM |
| `landslide_risk/variance.py` | Sobol **eksak** di ruang skor 5⁶ |
| `landslide_risk/case_data.py` | 575 kasus lereng nyata (Ma et al. 2022) + pengelompokan duplikat |
| `landslide_risk/engine.py` | Engine hibrida (gradient boosting **monoton penuh**) + 4 pembanding + CV berkelompok |
| `landslide_risk/case_mc.py` | Pf Monte Carlo per kasus nyata |
| `landslide_risk/metrics.py`, `acceptance.py` | AUC, Brier, ECE, TSS; 19 kriteria penerimaan; group bootstrap |
| `landslide_risk/hydrology.py` | Hidrologi transien Iverson (2000)/TRIGRS (D̂ = 4D₀/cos²α, bentuk terkoreksi) + solver Crank–Nicolson; opsi `hydrology="transient"` di `parameters_v2` |
| `audit/run_hydrology.py` | Statik vs transien; ambang I–D model vs ambang empiris |
| `docs/HIDROLOGI_TRANSIEN.md` | Status, persamaan, verifikasi, hasil hidrologi |
| `docs/CARA_MODEL_DICEK.md` | Matriks semua pengecekan (verifikasi, numerik, validasi, plausibilitas) |
| `docs/VERIFIKASI_REFERENSI.md` | Ringkasan verifikasi 151 butir sitasi; rinciannya di `research_notes/Verifikasi referensi/` |
| `audit/run_audit.py` | Audit: integritas data, bias validasi, efek Monte Carlo, ketidakpastian skoring |
| `report/` | Skrip gambar dan PDF, plus 2 PDF jadi |
| `results/` | `results/` (v1), `results/engine/` (v2), `results/audit/` |
| `docs/FORMULASI_MODEL.md` | Formulasi v1 dan kritik terhadap slide |
| `docs/AUDIT.md` | Audit lengkap (juga tersedia sebagai PDF) |
| `reports/Monte Carlo pengganti AHP longsor.md` | Kajian literatur (Bahasa Indonesia) |
| `research_notes/` | Catatan riset mentah 5 topik (sitasi dan URL) |
| `tests/` | 26 tes (fisika, reproduksi slide, pengaman audit, hidrologi) |

---

## 4. Riwayat pengembangan dan keputusan penting

1. **v1** mereproduksi kerangka slide dan angka studi kasus slide **persis** (HI 0,575, VI 0,584, RI 0,579, Kelas III).
2. **Bug fisika ditemukan dan diperbaiki:**
   - Kedalaman vertikal konstan membuat FS naik lagi di atas 45°. Solusi: tebal tanah H diukur tegak lurus lereng, dengan z = H/cos β.
   - Bishop sempat memberi FS 45% di bawah solusi eksak Taylor. Solusi: lingkaran ditolak bila m_α < 0,2, dan kedua ujung busur harus berada di setengah lingkaran bawah.
3. **v2** memakai distribusi dari literatur (ISSMGE TC304 2021, Phoon & Kulhawy 1999), korelasi c′–φ′, hujan kumulatif, dan kohesi akar dari kompilasi literatur.
4. **Kritik terhadap slide:**
   - HI berupa jumlah linier membuang efek non-linear.
   - Bobot hujan sekitar 0% adalah artefak model statik.
   - Infinite slope tidak berlaku untuk tebing 55–75°.
   - Rata-rata geometrik menekan variabel yang dinilai berbeda oleh tiap metode.
   - Rentang kelas di slide salah tulis.
5. **Engine hibrida** diuji pada 575 kasus lereng nyata dengan validasi silang berkelompok (kasus hampir-duplikat tidak boleh terpisah antara data latih dan uji).
6. **Audit (14 Okt)** mengoreksi klaim yang berlebihan. Lihat bagian 6.
7. **Hidrologi transien (21 Okt)** diimplementasikan, diverifikasi, dan dipasang ke Monte Carlo skor sebagai opsi. Lihat bagian 7.
8. **Verifikasi referensi (21 Okt):** 151 butir dicek; 23 dikoreksi, 7 klaim tidak didukung. Koreksi sudah diterapkan ke laporan, kode dan kajian. Lihat bagian 8.

---

## 5. Hasil yang berlaku (setelah audit)

**Validasi engine** pada seluruh 575 kasus, CV berkelompok 5-fold × 5, estimator single-pass:

| Model | AUC | Catatan |
|---|---|---|
| A Skor berbobot sama (**bukan AHP**) | 0,581 | pembanding heuristik |
| B Fisika saja (FS Bishop) | 0,645 | 0,756 di domain lereng tanah |
| E Regresi logistik | 0,731 | pembanding adil |
| **D Hibrida monoton penuh (dipakai)** | **0,860** (CI 0,832–0,896) | ECE 0,077; sensitivitas 0,81; spesifisitas 0,80 |
| C Boosting tanpa batasan | 0,906 | sebagian keunggulannya dari pola non-fisik (H, γ) |

- **Protokol penerimaan:** 16/19 lolos (4 di antaranya cek desain), 1 gagal, 2 tertunda.
  - **Gagal (A7):** Pf fisika tidak terkalibrasi pada lereng nyata (ECE 0,33). Lereng dengan Pf ≤ 0,1 ternyata 22% gagal; lereng dengan Pf > 0,9 hanya 57% gagal.
  - **Tertunda (A8):** alat skoring lapangan (6 skor → Pf) belum divalidasi terhadap kejadian longsor.
  - **Tertunda (A9):** belum ada validasi spasial pada inventaris longsor Indonesia.
- **Bobot Sobol eksak (v2):** geometri 0,44, vegetasi 0,26, tanah 0,19, seismik 0,06, MAT 0,03, hujan 0,01.
  - Bobot ini **bergantung pada definisi kelas**. Contoh rentang antar varian: tanah 0,18–0,37, vegetasi 0,07–0,28.
- **Studi kasus:**
  - Dengan Pf v2 = 0,86 → RI 0,71 → **Kelas IV**. Hasil ini stabil terhadap asumsi Monte Carlo (Pf 0,85–0,93).
  - Bila setiap skor punya peluang 20% meleset satu kelas: P(Kelas IV) = 0,87, P(Kelas III) = 0,10.
  - Ini **keluaran model, bukan temuan tervalidasi**.

---

## 6. Koreksi dari audit (jangan diulang)

| Klaim lama | Koreksi |
|---|---|
| AUC hibrida 0,903 / 0,906 | 0,860. Angka lama berasal dari domain yang dipilih setelah melihat hasil, prediksi dirata-rata 5 ulangan, dan H/γ tanpa batasan |
| "Mengalahkan AHP" | AHP **tidak pernah diuji**. Pembanding adil = regresi logistik (+0,13 AUC) |
| 16/17 kriteria lolos | 16/19 (4 analitik), 1 gagal, 2 tertunda; asal setiap ambang dilabeli |
| Engine tervalidasi | Hanya klasifikator Bishop-hibrida pada data global; alat skor lapangan **belum** |
| Pf = probabilitas untuk QRA | Pf belum terkalibrasi; perlu kalibrasi terhadap kejadian nyata |
| Bobot Sobol "obyektif" | Penilaian ahli berpindah ke tabel kelas, tidak hilang |
| Bishop vs Taylor 0,2% | 0,1–0,2% untuk 60–90°, **3,7% pada 45°** |
| AUC kasus dibandingkan dengan AUC peta literatur | Tidak bisa dibandingkan (tugasnya berbeda) |

**Masalah data:**
- 150 dari 288 lereng "stabil" memiliki FS Bishop < 1.
- 10 kelompok lereng berlabel ganda (stabil sekaligus gagal).
- 52 baris dibuang karena γ < 10 kN/m³.

---

## 7. Hidrologi: status transien

Rincian ada di `docs/HIDROLOGI_TRANSIEN.md`.

**Status.**
- **Statik** tetap menjadi default, supaya hasil yang sudah dilaporkan tidak berubah diam-diam.
- **Transien** tersedia lewat `hydrology="transient"`.
- **Persamaan transien:**
  - ψ(Z,t) = (Z − d)·β + Z·(Iz/Ks)·[R(t*) − R(t* − T*)].
  - D̂ = **4·D₀ / cos²α**. Iverson (2000) mencetak 4·D₀·cos²α, yang **salah**; bentuk yang benar dikonfirmasi oleh manual TRIGRS 2008 hlm. 25 dan kode `iverson.f95`.
  - Batasan: Iz ≤ Ks dan ψ ≤ β·Z.
  - FS diambil minimum selama dan setelah hujan.
- **D₀** terikat pada Ks: log₁₀(D₀/Ks) ~ U(log 5, log 200), sesuai rentang aplikasi TRIGRS yang terbit.

**Verifikasi.**
- Dibandingkan dengan solver Crank–Nicolson: selisih ≤ 0,7 mm.
- Dibandingkan dengan bentuk deret TRIGRS: identik. Uji ini yang menjaga konvensi D̂.
- Lima uji sifat lainnya lolos.

**Hasil.**
- Statik vs transien hampir sama: rata-rata Pf 0,628 vs 0,631; Pf studi kasus 0,860 vs 0,866; bobot hujan 0,012 vs 0,007.
- Penyebabnya, Ks realistis (0,4–11 mm/jam) membuat hujan per kejadian sebagian besar menjadi limpasan, dan air anteseden sudah terwakili oleh X3.

**Uji plausibilitas I–D.**
- Untuk tanah permeabel dan durasi ≥ 12 jam, ambang model berada di antara ambang Guzzetti (2008) dan ambang Banjarmangu, dekat ambang 1–3 hari Hidayat (2019) dan Yuniawan (2022).
- Untuk hujan singkat atau tanah lempung, model tidak bisa memicu longsor (batasan nyata).
- D₀ menggeser ambang 3–8×, sehingga D₀ adalah parameter yang paling perlu dikalibrasi.

**Belum.**
- Zona tak jenuh (suction, opsi Gardner).
- Dasar kedap pada kedalaman terbatas.
- Aliran lateral.
- **Validasi temporal**: NASA GLC punya 151 kejadian hujan di Indonesia dengan akurasi ≤ 5 km, yang bisa dipasangkan dengan GPM IMERG/CHIRPS.

---

## 8. Verifikasi referensi: status

Rincian ada di `docs/VERIFIKASI_REFERENSI.md` dan `research_notes/Verifikasi referensi/`.

**Hasil.** Dari 151 butir: 112 terverifikasi, 23 dikoreksi, 7 klaim tidak didukung, 9 tidak bisa diakses.

**Koreksi terpenting:**
1. Konvensi D̂ Iverson.
2. SNI 8460: angka 1,5/1,3 untuk **batuan**. Lereng tanah memakai FS 1,25–≥2,0 menurut ketidakpastian dan konsekuensi. Pseudo-statik > 1,1, dengan kh = 0,5·PGA.
3. Hammah et al. (2004): pemotongan distribusi mengubah Pf.
4. Judul dan penulis Milledge (2012), Stevens (2006) dan Samodra (2024).
5. Lumb (1970) justru menyatakan c dan φ **independen**; nilai ρ = −0,5 kini berstatus asumsi.
6. Hujan 300–600 mm adalah hujan anteseden 30 hari (Hadmoko et al., 2017), bukan per kejadian.
7. Beberapa angka AUC dan studi di kajian literatur.

**Masih belum terverifikasi:**
- Isi spesifik Fell (2008), Corominas (2014) dan Liu & Wu (2008).
- Nilai ρ dari Lumb dan Cherubini; klaim Wang et al. (2024) "+36,7%"; nilai kh dari Seed (1979).
- Atribusi m_α < 0,2 ke Whitman & Bailey.
- Detail InaRISK.

---

## 9. Langkah berikutnya (urut prioritas)

1. **Data lapangan:** catat skor 6 variabel di lokasi longsor yang terpetakan dan di lereng stabil pembanding. Hanya cara ini yang bisa menguji kriteria A8.
2. **Validasi spasial (A9)** dengan inventaris Samodra (2024) Cyclone Cempaka (Mendeley doi:10.17632/vrtx3w6mjd.1, CC BY), memakai CV berblok spasial. Pembanding resmi: InaRISK BNPB.
3. **Kalibrasi Pf** (isotonic/Platt) pada data hasil ketika data tersedia. Ini memperbaiki kriteria A7.
4. **Validasi temporal hidrologi transien** dan kalibrasi D₀ (bagian 7).
5. **Kalibrasi tabel kelas** dengan data uji lab lokal dan SoilKsatDB, lalu laporkan rentang bobot pada batas kelas ±20%.
6. **Studi antar-pengamat:** beberapa engineer menilai lereng yang sama untuk mengukur galat skoring yang sebenarnya.
7. **Cek butir referensi yang masih belum terverifikasi** (bagian 8) bila teks lengkapnya bisa diakses.

---

## 10. Syarat penggunaan etis

- Selama A8 dan A9 belum lolos, hasil hanya untuk **riset dan screening**, bukan dasar tunggal untuk evakuasi atau relokasi. Setiap hasil Kelas IV–V perlu ditinjau ahli geoteknik.
- Selalu laporkan recall (proporsi longsor yang terdeteksi), bukan hanya AUC. Pada ambang 0,5 model melewatkan **19% lereng yang gagal**.
- Publikasikan tabel kelas, distribusi, kode dan data. Bedakan dengan jelas mana yang **tervalidasi**, mana yang **hanya terverifikasi**, dan mana yang **asumsi**.
