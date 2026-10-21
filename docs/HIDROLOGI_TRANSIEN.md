# Hidrologi transien: status, persamaan, verifikasi dan hasil

**Tanggal:** 21 Oktober 2026
**Kode:** `landslide_risk/hydrology.py`
**Uji:** `tests/test_hydrology.py`
**Analisis:** `audit/run_hydrology.py` → `results/hydrology/`
**Sumber:** `research_notes/Verifikasi referensi/transient_hydrology.md`

---

## 1. Jawaban singkat: apakah pemodelan air sudah transien?

| | Sebelum 21 Okt | Sekarang |
|---|---|---|
| Model air | **Statik**: m = min(1, m₀ + min(P, Ks·D)/(n_e·z)), neraca air sekali langkah | **Transien tersedia**: difusi tekanan air pori Iverson (2000), dasar dari TRIGRS |
| Waktu | Tidak ada | Tekanan dihitung selama **dan setelah** hujan; FS diambil pada waktu kritis |
| Dipakai di | v1, v2 | v2 dengan `hydrology="transient"`. Default tetap `"static"`, supaya hasil yang sudah dilaporkan tidak berubah diam-diam |
| Zona tak jenuh / suction | Tidak | **Belum** (opsi Gardner di TRIGRS belum diimplementasikan) |
| Dasar kedap kedalaman terbatas | Tidak | **Belum** (memakai solusi kedalaman tak hingga) |

---

## 2. Persamaan yang dipakai

Persamaan berikut dicek terhadap manual TRIGRS 2.0 (Baum et al. 2008, OFR 2008-1159) dan kode resmi TRIGRS v2.1 (`iverson.f95`).

```
ψ(Z,t) = (Z − d)·β + Z·(Iz/Ks)·R(t*)                      t ≤ T
ψ(Z,t) = (Z − d)·β + Z·(Iz/Ks)·[R(t*) − R(t* − T*)]       t > T
R(t*)  = √(t*/π)·exp(−1/t*) − erfc(1/√t*)
t* = t·D̂/Z²,   T* = T·D̂/Z²,   D̂ = 4·D₀ / cos²α
β  = cos²α − Iz_LT/Ks
Batasan: Iz ≤ Ks (kelebihan hujan → limpasan);  ψ ≤ β·Z
```

**Koreksi penting.** Makalah Iverson (2000) mencetak D̂ = 4·D₀·**cos²α**. Bentuk itu **salah**: kesalahan transformasi koordinat, ditemukan oleh mahasiswa R. Rigon dan dicatat di manual TRIGRS 2008 hlm. 25. Kode TRIGRS memakai `dhat = 4*D0/cos²` ("added 8 Jan 2013, RLB").

Implementasi pertama saya mengikuti bentuk cetak yang salah. Untuk β = 35°, D₀ = 10⁻⁵ m²/s, Z = 1,5 m dan hujan 6 jam, bentuk yang salah meremehkan respons transien sekitar 22 kali. Kesalahan ini sudah diperbaiki, dan sekarang dijaga oleh uji khusus.

**Penghubung ke model FS.** Tekanan hidrostatik sejajar lereng adalah ψ = m·z·cos²β, sehingga m = ψ/(z·cos²β). Nilai m ini dibatasi pada rentang [0, 1] lalu dimasukkan ke persamaan FS infinite slope yang sudah ada.

**Masukan hujan.**
- Hujan kumulatif P (mm) selama D jam (24–72 jam) diubah menjadi intensitas rata-rata Iz = P/D.
- FS dievaluasi pada t = D × {1; 1,25; 1,5; 2; 3; 4; 6}, karena puncak tekanan di kedalaman bisa terjadi setelah hujan berhenti.

**Difusivitas D₀.**
- Manual TRIGRS tidak memberi nilai default; definisinya D₀ = Ks/Ss.
- Aplikasi yang terbit memakai rasio D₀/Ks antara sekitar 2 dan 200:

| Sumber | D₀/Ks |
|---|---|
| Contoh manual TRIGRS | 8–60 |
| Raia et al. (2014) | 3,8–50 |
| Alvioli et al. (2014) | 8,3 dan 47 |
| Bandung Barat | 100 |
| Ma et al. (2023) | 200 |

- Di model ini log₁₀(D₀/Ks) diambil seragam antara log 5 dan log 200, dan D₀ **terikat pada Ks**.

---

## 3. Bagaimana hidrologi ini dicek (verifikasi)

| Uji | Yang dibuktikan | Hasil |
|---|---|---|
| Solusi analitik vs solver numerik Crank–Nicolson independen | Persamaan difusi **dipecahkan** dengan benar | Selisih ≤ 0,7 mm (≈ 1%) |
| Bentuk analitik vs bentuk deret TRIGRS: 2·(Iz/Ks)·√(D₁t)·ierfc(Z/2√(D₁t)), D₁ = D₀/cos²α | **Konvensi difusivitas** sama dengan TRIGRS | Identik (rel. 10⁻⁹) |
| R(0) = 0; untuk t* besar R → √(t*/π) − 1 | Perilaku batas fungsi respons | Lolos |
| Tanpa hujan → m = m₀ | Kondisi awal dipertahankan | Lolos |
| Iz > Ks memberi hasil sama dengan Iz = Ks | Kelebihan hujan menjadi limpasan | Lolos |
| ψ ≤ β·Z | Muka air maksimum di permukaan | Lolos |
| Puncak tekanan di kedalaman 3 m terjadi setelah hujan berhenti | Perilaku transien | Lolos |

**Pelajaran dari koreksi D̂.** Uji Crank–Nicolson lolos meskipun persamaannya salah, karena solver numerik memakai persamaan atur yang sama. Uji semacam itu hanya membuktikan persamaan *dipecahkan* dengan benar, bukan bahwa *persamaannya benar*. Karena itu sekarang ada uji kedua yang membandingkan langsung dengan bentuk dari sumber independen (TRIGRS).

---

## 4. Hasil: apa yang berubah dengan hidrologi transien?

Seluruh 15.625 kombinasi skor × N = 400 (`results/hydrology/static_vs_transient.csv`):

| | Statik | Transien |
|---|---|---|
| Rata-rata Pf | 0,628 | 0,631 |
| Pf studi kasus (3-4-4-4-1-2) | 0,860 | 0,866 |
| Bobot hujan (S_T dinormalisasi) | 0,012 | 0,007 |
| Bobot geometri / vegetasi / tanah | 0,44 / 0,26 / 0,19 | 0,46 / 0,25 / 0,19 |

**Kesimpulan jujur:** model transien **tidak** membuat hujan per kejadian lebih berpengaruh di model skor ini. Ada dua penyebab:
1. Ks kelas tanah yang realistis hanya 0,4–11 mm/jam, sehingga sebagian besar hujan per kejadian menjadi limpasan pada kedua model.
2. Keadaan air anteseden sudah diwakili oleh X3 (muka air tanah awal).

Pengaruh hujan di model ini terutama tersalur lewat X3. Ini konsisten dengan ambang hujan Indonesia yang berbasis hujan 1–3 hari dan anteseden (Hidayat et al. 2019; Yuniawan et al. 2022).

---

## 5. Uji plausibilitas: ambang intensitas–durasi (I–D)

**Metode.** Untuk setiap kelas tanah dibuat lereng acuan yang **marginal**: kekuatan rata-rata kelas, H = 1,5 m, m₀ = 0,2, c_r = 2 kPa, dan β dipilih sehingga FS sebelum hujan = 1,2. Lalu dihitung intensitas hujan minimum yang membuat FS < 1, untuk setiap durasi.

**Hasilnya dibandingkan dengan ambang empiris yang sudah diverifikasi:**

| Durasi | Model, tanah kelas 1, D₀/Ks = 50 | Model, kelas 2, D₀/Ks = 200 | Guzzetti 2008 (global) | Banjarmangu (Irawan 2019) | Indonesia (1-hr / 3-hr) |
|---|---|---|---|---|---|
| 1 jam | tidak longsor | tidak longsor | 2,20 | 43,2 | – |
| 3 jam | 8,99 | 2,72 | 1,36 | 16,6 | – |
| 12 jam | 2,79 mm/jam | 0,88 | 0,74 | 4,97 | – |
| 24 jam | 1,65 | 0,53 | 0,54 | 2,72 | Hidayat 2,54; Yuniawan 1,25 |
| 72 jam | 0,80 | 0,27 | 0,34 | 1,05 | Hidayat 1,26; Yuniawan 0,89 |

**Temuan:**
- Untuk tanah permeabel dan durasi ≥ 12 jam, ambang model berada **di dalam rentang** ambang empiris global dan lokal. Kemiringan kurvanya juga sebanding.
- Untuk hujan singkat (< 3–6 jam) dan tanah berpermeabilitas rendah (kelas 3–4), model **tidak bisa memicu longsor**, padahal data empiris menunjukkan bisa. Ini batasan nyata. Penyebab yang mungkin: aliran preferensial, kehilangan suction, konsentrasi limpasan dari lereng atas, dan lapisan tanah yang tidak homogen. Semuanya tidak dimodelkan.
- Ambang model sangat sensitif terhadap D₀ (bergeser 3–8× antara D₀/Ks = 5 dan 200). **D₀ adalah parameter yang paling perlu dikalibrasi.**
- Ini **uji plausibilitas, bukan validasi**: ambang empiris berasal dari lereng dan produk hujan yang berbeda.

---

## 6. Data untuk validasi temporal (langkah berikutnya)

- **NASA Global Landslide Catalog** memuat 355 kejadian di Indonesia (2006–2016). Dari jumlah itu, 151 dipicu hujan dengan akurasi lokasi ≤ 5 km. Tanggalnya harian, tanpa jam.
- **Hujan:** GPM IMERG V07 (0,1°, per 30 menit/harian; perlu akun Earthdata) atau CHIRPS (terbuka). GSMaP terkoreksi stasiun setara dengan data stasiun di DAS Progo.
- **Protokol yang diusulkan:**
  1. Untuk setiap kejadian, ambil hujan 1–30 hari sebelumnya.
  2. Jalankan model transien di lokasi itu.
  3. Hitung hit / miss / false alarm, dengan pembanding ambang Yuniawan et al. (2022) yang dipakai sistem peringatan nasional.
- **Celah penelitian:** belum ada aplikasi TRIGRS di Indonesia yang diuji terhadap tanggal kejadian. Studi Hidayat 2019, Muntohar 2021, Sugianti 2022 dan Hermawan 2023 semuanya divalidasi secara kualitatif atau spasial.

---

## 7. Keterbatasan yang tersisa

1. Tidak ada zona tak jenuh. Tanah dianggap jenuh atau hampir jenuh, sehingga suction tidak menambah kekuatan; ini konservatif untuk tanah residual tropis.
2. Kedalaman dianggap tak hingga, tanpa dasar kedap. Pada tanah tipis di atas batuan, tekanan bisa naik lebih cepat dari model.
3. Aliran vertikal 1-D, tanpa aliran lateral dari lereng atas (ε = H/√A ≪ 1).
4. β memakai versi kode TRIGRS (cos²α − Iz_LT/Ks). Laporan TRIGRS 2002 dan Raia et al. (2014) memakai cos α·[cos α − (Iz/Kz)_LT]. Keduanya identik untuk Iz_LT = 0, yaitu nilai yang dipakai di sini.
5. Ralat Baum & Godt (2013) untuk laporan TRIGRS 2008/2010 belum terbaca; kode dipakai sebagai acuan.
