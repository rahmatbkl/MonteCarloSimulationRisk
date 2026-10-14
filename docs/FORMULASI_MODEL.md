# Formulasi Model: Landslide Risk Index berbasis Simulasi Fisika + Monte Carlo

Dokumen ini merumuskan model dari dua dek slide ("The Landslide Risk Index" dan
"Algorithmic Landslide Risk Framework") menjadi persamaan yang bisa langsung
diimplementasikan. Dokumen ini juga membahas pertimbangan memakai Monte Carlo
dibandingkan simulasi fisika penuh, beserta catatan kritis yang perlu ditangani
sebelum publikasi atau dipakai BPBD.

Implementasi: folder `landslide_risk/`. Untuk menjalankan: `python run_pipeline.py`.

---

## 1. Alur Model

```
Skor lapangan X1..X6 (1-5)
      │
      ▼
[A] Konversi skor → rentang parameter fisik          config.py
      │
      ▼
[B] Physics engine: Infinite Slope → FS               physics.py
      │
      ▼
[C] Inner loop Monte Carlo (400×) → Pf per konfigurasi simulation.py
[D] Outer loop LHS (1.200 konfigurasi)                 simulation.py
      │
      ▼
[E] Sensitivitas: SRC, Sobol', RF → bobot konsensus    sensitivity.py
      │
      ▼
[F] HI (hazard) × VI (vulnerability) → RI → Kelas I–V  risk_index.py
```

---

## 2. Variabel dan Konversi Skor → Parameter Fisik [A]

| Variabel | Peran (Varnes) | Parameter fisik yang diacak | Masuk ke FS lewat |
|---|---|---|---|
| X1 Jenis tanah | Preparatory | c′, φ′, γ, Ks | penahan (kohesi, gesekan), berat |
| X2 Geometri | Preparatory | β (sudut), H (tebal tanah) | pendorong (gravitasi) |
| X3 Muka air tanah | Jembatan | m₀ = h_w/z | tekanan pori u |
| X4 Curah hujan | Triggering | I (mm/jam), D (jam) | menaikkan m lewat infiltrasi |
| X5 Seismik | Triggering | k_h | gaya inersia pseudo-statik |
| X6 Vegetasi | Preparatory | c_r, kedalaman akar | kohesi akar |

Setiap skor memetakan ke **rentang** nilai (lihat `config.py`). Di dalam rentang
itu nilai diacak seragam, kecuali Ks yang diacak log-seragam karena tersebar
beberapa orde besaran.

> Rentang di `config.py` adalah **nilai awal dari literatur, bukan hasil kalibrasi**.
> Bobot akhir sangat sensitif terhadap rentang ini (lihat §5.1).

---

## 3. Persamaan Fisika [B]

### 3.1 Factor of Safety: Infinite Slope

Untuk tebal tanah H (tegak lurus lereng), kedalaman vertikal z = H / cos β:

```
σ_n   = γ · z · cos²β · (1 − k_h · tan β)              tegangan normal
u     = γ_w · m · z · cos²β                            tekanan air pori
τ_res = c′ + c_r,eff + max(σ_n − u, 0) · tan φ′        gaya penahan
τ_drv = γ · z · cos β · (sin β + k_h · cos β)          gaya pendorong

FS = τ_res / τ_drv            FS < 1  ⇒  longsor
```

Pemeriksaan: untuk c′ = 0, kering, dan statik, persamaan ini menjadi
FS = tan φ′ / tan β (sudah diuji di `tests/test_model.py`).

### 3.2 Hujan → Muka Air Tanah

```
f   = min(I, Ks)              laju infiltrasi; hujan > Ks menjadi limpasan
Δh  = f · D / n_e             kenaikan muka air tanah
m   = min(1, m₀ + Δh / z)
```

### 3.3 Kohesi Akar (efek kondisional muncul secara fisik)

```
c_r,eff = c_r · min(1, kedalaman_akar / H)
```

Akar hanya menahan jika menembus bidang gelincir. Karena itu "efek kondisional
vegetasi" yang ditemukan Random Forest muncul langsung dari fisika, tanpa aturan
buatan seperti "jika lereng > 60° akar = 0".

---

## 4. Simulasi dan Agregasi

### 4.1 Inner Loop: Monte Carlo [C]

Untuk satu konfigurasi skor **s** = (s₁..s₆):

```
Pf(s) = (1/N) · Σ 1[ FS(θ_k) < 1 ],    θ_k ~ Uniform(rentang(s)),  N = 400
SE(Pf) = √( Pf(1 − Pf) / N )  ≤ 0,025 untuk N = 400
```

### 4.2 Outer Loop: Latin Hypercube [D]

Sebanyak 1.200 titik LHS di [0,1]⁶ dipetakan ke skor dengan floor(5u) + 1.
Hasilnya, tiap skor muncul tepat 240 kali per variabel. Total evaluasi
1.200 × 400 = 480.000.

**Catatan:** seluruh ruang skor hanya 5⁶ = 15.625 kombinasi. Dengan numpy,
semuanya bisa dihitung langsung dalam beberapa detik (`results/full_factorial.csv`),
sehingga LHS maupun surrogate tidak diperlukan untuk menutup ruang skor.

### 4.3 Sensitivitas dan Bobot Konsensus [E]

| Metode | Rumus | Menangkap |
|---|---|---|
| SRC | OLS pada X, y terstandar → w_i ∝ \|β_i\| | efek linear |
| Sobol′ total-order | S_Ti = E[Var(Y \| X₋ᵢ)] / Var(Y) (Jansen), pada surrogate GBM | varians + interaksi |
| RF permutation | penurunan R² data uji saat X_i diacak | non-linear, kondisional |

Bobot setiap metode dinormalisasi (Σw = 1), lalu digabung:

```
w_i = GM_i / Σ_j GM_j,    GM_i = (w_i^SRC · w_i^Sobol · w_i^RF)^(1/3)
```

### 4.4 Indeks Risiko [F]

```
HI  = (Σ w_i · s_i − 1) / 4                      versi bobot (slide)
HI* = Pf(s)  dari Monte Carlo langsung           versi fisika (disarankan)
VI  = (0,667 · s_jarak + 0,333 · s_vegetasi − 1) / 4
RI  = √(HI · VI)
```

| Kelas | RI | Tindakan |
|---|---|---|
| I | < 0,20 | Pemantauan rutin |
| II | 0,20–0,40 | Mitigasi ringan |
| III | 0,40–0,60 | Investigasi lapangan wajib |
| IV | 0,60–0,80 | Tindakan segera, pertimbangkan relokasi |
| V | ≥ 0,80 | Darurat: evakuasi, rekayasa geoteknik |

---

## 5. Hasil Implementasi (seed 42, 480.000 evaluasi)

| Variabel | SRC | Sobol′ ST | RF | Konsensus | Porsi interaksi |
|---|---|---|---|---|---|
| Jenis tanah | 0,311 | 0,374 | 0,360 | **0,354** | 29% |
| Geometri | 0,357 | 0,449 | 0,479 | **0,433** | 20% |
| Muka air tanah | 0,079 | 0,025 | 0,020 | 0,034 | 35% |
| Curah hujan | 0,001 | 0,001 | 0,000 | 0,001 | – |
| Seismik | 0,098 | 0,044 | 0,036 | 0,055 | 19% |
| Vegetasi | 0,153 | 0,108 | 0,105 | 0,123 | 35% |

Tanah + geometri = **79%**. Kesimpulan kualitatif slide (faktor preparatory
mendominasi) terkonfirmasi, tetapi angka persisnya berbeda (slide: 91%).

**Studi kasus** (lempung sedang, 45°, MAT dangkal, hujan tinggi, kebun kopi, permukiman 80 m):

| Metode HI | HI | VI | RI | Kelas |
|---|---|---|---|---|
| Bobot slide (reproduksi) | 0,575 | 0,584 | 0,579 | III |
| Bobot simulasi ini | 0,559 | 0,584 | 0,571 | III |
| **Pf fisika langsung** | **0,848** (CI 95%: 0,843–0,853) | 0,584 | **0,703** | **IV** |

Pada lereng ini, penjumlahan bobot linear **menurunkan kelas risiko satu tingkat**
dibandingkan fisikanya sendiri (lihat §7.2).

---

## 6. Monte Carlo vs Simulasi Fisika "Real": Pertimbangan

### 6.1 Monte Carlo dan fisika bukan pilihan yang saling menggantikan

Monte Carlo bukan model fisika. Monte Carlo adalah **cara merambatkan
ketidakpastian** melalui sebuah model fisika. Pertanyaan yang tepat adalah:
*mesin fisika apa yang dibungkus Monte Carlo, dan apakah layak dijalankan
ratusan ribu kali?*

| Tingkat | Mesin fisika | Contoh perangkat | Biaya/evaluasi | Data dibutuhkan | Cocok untuk |
|---|---|---|---|---|---|
| 0 | Tidak ada (heuristik) | AHP, skoring | ~0 | opini pakar | — (yang ingin diganti) |
| 1 | **Infinite slope statik** | model ini, SINMAP, SHALSTAB | µs | c′, φ′, γ, β, H, m | **screening regional**, ribuan lereng |
| 2 | Infinite slope + hidrologi transien | TRIGRS, Iverson (2000) | ms | + Ks, D₀, hujan per jam/hari | peringatan dini berbasis hujan |
| 3 | Limit equilibrium 2D/3D | SLOPE/W, Scoops3D | detik | profil lereng, stratigrafi | per lereng, longsor rotasi/dalam |
| 4 | Numerik FEM/FDM hidro-mekanik | PLAXIS, FLAC, GeoStudio | menit–jam | uji lab lengkap, monitoring | desain mitigasi per lokasi |
| 5 | Dinamika runout | r.avaflow, DAN3D, MPM/SPH | jam | DEM detail, reologi | jangkauan & dampak (VI fisik) |

### 6.2 Kelebihan infinite slope + Monte Carlo

1. **Murah**: 480.000 evaluasi kurang dari 15 detik, sehingga sensitivitas global bisa dihitung.
2. **Transparan**: setiap bobot bisa ditelusuri ke persamaan gaya, bukan opini.
3. **Jujur terhadap ketidakpastian**: hasilnya Pf beserta selang kepercayaan, bukan satu angka FS.
4. **Bisa direproduksi**: seed yang sama menghasilkan angka yang sama (kelemahan utama AHP).

### 6.3 Batasan yang tidak bisa diatasi Monte Carlo

1. **Mekanisme**: hanya longsor translasi dangkal (H ≪ panjang lereng). Tidak berlaku
   untuk longsor rotasi, runtuhan batuan/toppling (tebing 55–75°), atau aliran debris.
2. **Statik, tanpa waktu**: hujan tidak punya durasi dan riwayat (antecedent). Inilah
   alasan pengaruh hujan ≈ 0 (§7.3).
3. **Tanpa ruang**: setiap lereng berdiri sendiri. Tidak ada aliran air dari hulu
   (contributing area) dan tidak ada korelasi spasial.
4. **Monte Carlo hanya sebaik distribusi inputnya**: rentang seragam per skor dianggap
   independen, padahal c′ dan φ′ biasanya berkorelasi negatif (ρ ≈ −0,3 s.d. −0,7).
5. **Pf bukan probabilitas tahunan**: Pf di sini adalah "peluang lereng berskor *s*
   tidak stabil, jika kondisinya terjadi". Itu ukuran *susceptibility*, belum *hazard*
   (yang butuh frekuensi/periode ulang pemicu; Fell et al., 2008).

### 6.4 Rekomendasi: pendekatan bertingkat

```
Regional (kabupaten)   : Tingkat 1–2 + Monte Carlo → peta Pf / RI per sel DEM
        │  lereng Kelas IV–V
        ▼
Per lokasi             : Tingkat 3–4 (SLOPE/W / PLAXIS) dengan data bor & lab
        │  desain mitigasi
        ▼
Dampak                 : Tingkat 5 (runout) untuk menggantikan VI berbasis jarak
```

Alternatif yang lebih cepat dari Monte Carlo untuk Pf kecil (< 10⁻³): FOSM, FORM
(indeks reliabilitas β), atau Subset Simulation / Importance Sampling. Monte Carlo
biasa butuh N ≈ 100/Pf sampel agar galatnya ~10%.

---

## 7. Catatan Kritis terhadap Kerangka di Slide

Urutan dari yang paling berpengaruh pada kesimpulan.

### 7.1 Klaim "obyektif" bersyarat pada rentang skor

Bobot adalah sifat dari *tabel konversi skor → parameter* yang dipilih peneliti,
bukan sifat alam. Contoh dari implementasi ini: hanya dengan mengubah definisi
kedalaman (vertikal → tegak lurus lereng), bobot geometri berubah dari 16% menjadi
43%, dan tanah dari 54% menjadi 35%.
**Saran:** laporkan tabel rentang secara eksplisit, rujuk sumbernya (SNI 8460:2017,
data lab lokal), dan sertakan analisis robustnes bobot terhadap rentang tersebut.

### 7.2 HI linear membuang temuan non-linear sendiri

Slide menunjukkan Pf bimodal, kurva bertangga (partial dependence), dan interaksi
20–47%, tetapi HI dihitung sebagai jumlah linear Σ w·s. Studi kasus membuktikan
akibatnya: HI = 0,575 (Kelas III), padahal Pf fisik = 0,85 (Kelas IV).
**Saran:** gunakan **HI = Pf(s)** langsung dari tabel lookup 15.625 kombinasi
(`results/full_factorial.csv`). Tabel ini tetap praktis di lapangan karena cukup
dicari barisnya, dan bobot konsensus tetap dipakai sebagai *penjelasan*
(faktor mana yang dominan), bukan sebagai rumus HI.

### 7.3 Pengaruh hujan 0,1% adalah artefak struktur model

Dalam model statik, intensitas hujan di atas Ks langsung menjadi limpasan. Semua
kelas hujan (≥ 5 mm/jam) sudah melebihi Ks lempung (≤ 3,6 mm/jam), sehingga skor
hujan tidak mengubah apa pun. Selain itu, MAT (X3) sudah diacak terpisah, sehingga
jalur utama hujan → tekanan pori "sudah terpakai" oleh X3.
Kesimpulan "AHP melebih-lebihkan hujan (25% vs 0,1%)" karena itu **tidak sah**,
sebab model memang tidak mampu merepresentasikan peran hujan. Sebagian besar longsor
di Indonesia justru dipicu hujan.
**Saran:** ganti X4 menjadi **hujan kumulatif** (mm dalam 1–3 hari) dan/atau
hujan antecedent, gunakan hidrologi transien (TRIGRS/Iverson), dan jadikan X3 kondisi
*awal* musiman.

### 7.4 Model infinite slope tidak valid untuk skor geometri 5 (55–75°)

Pada sudut ini mekanismenya runtuhan batuan/toppling, dan lapisan tanah tebal jarang
bertahan. Jika kedalaman diukur vertikal, rumus FS bahkan memberi Pf yang **turun**
setelah 45° (suku kohesi ∝ 1/sin 2β). Ini ditemukan saat membangun kode ini dan
sudah diperbaiki dengan ketebalan tegak lurus lereng.
**Saran:** batasi skor 5 pada 55–60° untuk tanah, atau tandai sebagai "di luar
domain model, wajib analisis batuan".

### 7.5 Rata-rata geometrik menghukum ketidaksepakatan

Jika satu metode memberi bobot ≈ 0, GM ikut ≈ 0 walaupun dua metode lain memberi
bobot besar. Pada slide dek kedua, kurva marginal seismik (ΔPf ≈ 0,66) dan MAT
(ΔPf ≈ 0,57) hampir setara geometri (≈ 0,64), tetapi bobot konsensusnya hanya
1,8% dan 1,6%.
**Saran:** periksa ulang konsistensi ini. Laporkan juga rata-rata aritmetik
(`consensus_arith`) dan Sobol′ ST sebagai acuan utama, karena Sobol′ satu-satunya
yang secara definisi menguraikan varians.

### 7.6 Hal-hal lain

- **Vegetasi dihitung dua kali** (di HI sebagai kohesi akar dan di VI sebagai
  peredam runout). Ini boleh asalkan disebutkan sebagai pilihan desain, karena
  mekanismenya berbeda.
- **Inkonsistensi antar slide**: pipeline dek 1 menulis RI 0–100 dengan 3 kelas
  (0–33/34–66/67–100), padahal klasifikasi akhir 5 kelas 0–1. Rentang kelas di
  slide "Merumuskan Indeks Risiko Absolut" (dek 2) juga tertulis keliru
  (0,1–0,0 …), yang benar adalah < 0,20 / 0,20–0,40 / 0,40–0,60 / 0,60–0,80 / ≥ 0,80.
- **Belum ada validasi**: model fisika tetap harus diuji terhadap inventaris longsor
  (data BNPB/DIBI atau pemetaan lapangan) dengan ROC-AUC / success-rate curve.
  Tanpa itu, "obyektif" belum berarti "akurat".
- **VI terlalu sederhana**: hanya jarak dan vegetasi. Pertimbangkan kepadatan
  penduduk, jenis bangunan, dan infrastruktur kritis.

---

## 8. Langkah Lanjut yang Disarankan

1. Kalibrasi `config.py` dengan data uji tanah lokal (c′, φ′, γ, Ks) per kelas tanah.
2. Ganti X4 dengan hujan kumulatif dan tambahkan hidrologi transien (§7.3).
3. Ambil sampel c′–φ′ berkorelasi (Gaussian copula) dengan distribusi lognormal/beta.
4. Jadikan HI = Pf lookup (§7.2). Bobot konsensus dipakai untuk interpretasi.
5. Validasi terhadap inventaris longsor (AUC ≥ 0,75 sebagai target awal).
6. Uji robustnes: variasikan rentang ±20% lalu laporkan sebaran bobot (error bar).
