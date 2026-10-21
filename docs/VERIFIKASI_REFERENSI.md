# Ringkasan verifikasi referensi

**Tanggal:** 21 Oktober 2026
**Rincian per butir** (tabel dengan URL dan kutipan bukti): `research_notes/Verifikasi referensi/`
**Penerapan:** 83 koreksi diterapkan ke kajian literatur (`reports/Monte Carlo pengganti AHP longsor.md`), ditambah koreksi ke laporan PDF, `run_engine.py` dan `parameters_v2.py`.

## 1. Cakupan dan hasil

Setiap sitasi, dan setiap angka yang diatribusikan ke sumber, dicek ke sumber primer. Sumber yang dipakai: Crossref, DOI, halaman penerbit, repositori, teks lengkap terbuka, dan kode resmi.

| Dokumen | Butir dicek | Terverifikasi | Dikoreksi | Klaim tidak didukung | Tidak ditemukan / tak bisa diakses |
|---|---|---|---|---|---|
| Laporan PDF + `run_engine.py` | 27 | 21 | 5 | 1 | 0 |
| Kajian literatur, bagian 1 | 66 | 46 | 10 | 5 | 5 |
| Kajian literatur, bagian 2 + dataset/URL | 58 | 45 | 8 | 1 | 4 |
| **Total** | **151** | **112 (74%)** | **23** | **7** | **9** |

Hitungan diambil dari kolom status tiap tabel. Status "VERIFIED (reword)" dihitung sebagai terverifikasi.

Hidrologi transien diperiksa secara terpisah (`transient_hydrology.md`): persamaan Iverson/TRIGRS, nilai D₀, ambang hujan Indonesia, dan data validasi temporal.

---

## 2. Kesalahan terpenting dan perbaikannya

| # | Temuan | Dampak | Diperbaiki di |
|---|---|---|---|
| 1 | **Iverson (2000) mencetak D̂ = 4·D₀·cos²α. Yang benar 4·D₀/cos²α** (manual dan kode TRIGRS) | Implementasi pertama meremehkan respons transien hingga ~22× | `hydrology.py` + uji pengaman |
| 2 | **SNI 8460:2017 salah kutip.** Angka 1,5/1,3 berlaku untuk lereng **batuan** (Tabel 26). Lereng tanah: FS 1,25–1,5 (ketidakpastian rendah) atau 1,5–≥2,0 (tinggi), tergantung konsekuensi (Tabel 25). Pseudo-statik FS > 1,1; kh = 0,5·PGA (§12.2.7) | Kriteria keandalan lokasi | Laporan PDF, kajian |
| 3 | **Hammah et al.** bukan "FEM, Rocscience", melainkan konferensi CGS 2004. Klaim "pemotongan ±3σ tidak membiaskan Pf" **salah** (0,12% → 0,05%) | Teks model probabilistik | Laporan PDF |
| 4 | **Milledge et al. (2012)**: judul dan penulis salah. Angka "16" untuk L/H berasal dari Griffiths et al. (2011) | Batas validitas infinite slope | Laporan PDF |
| 5 | **Stevens et al. (2006)**: inisial salah (V., bukan E.). Hutan alami (25,6–94,3 kPa) tidak tercakup | Kelas vegetasi | Laporan PDF, `parameters_v2.py` |
| 6 | **Samodra (2024)**: judul dataset salah | Rencana validasi spasial | Laporan PDF |
| 7 | **Lumb (1970)** justru menyatakan c dan φ **independen**. −0,61 berasal dari Cherubini **1997** | Sumber ρ = −0,5 kini ditandai *asumsi* | `parameters_v2.py`, kajian |
| 8 | **Hujan Jawa 300–600 mm** = hujan anteseden **30 hari** untuk longsor dangkal (Hadmoko et al. 2017), bukan per kejadian | Batas kelas hujan kini ditandai *asumsi proyek* | `parameters_v2.py`, laporan |
| 9 | **HIRESSS** memakai P(FS < 1), bukan P(FS < 1,2). **Haiyan** tidak memuat AUC 0,79. Angka Tenta dan Flow-R berbeda | Perbandingan AUC literatur | Kajian |
| 10 | "+20,1%" adalah gabungan dua makalah. Selisih "37%" adalah selisih Pf, bukan selisih β | Klaim hibrida dan metode reliabilitas | Kajian |
| 11 | Lisensi UGLC adalah **CC BY-NC**. Risiko 10⁻⁴/10⁻⁵ per tahun berasal dari AGS 2000/2007, bukan JTC-1 | Katalog data, kriteria risiko | Kajian |
| 12 | Klaim "belum ada COV Indonesia" **salah**: Sarah et al. (2024) memuatnya | Kajian parameter tanah | Kajian |
| 13 | 7 referensi dipakai di teks tetapi belum ada di daftar pustaka | Kelengkapan | Laporan PDF |

---

## 3. Yang kini terverifikasi (sebelumnya diragukan)

- **Angka Taylor (1937):** dihitung ulang secara independen dan benar. Catatan: pada 45° lingkaran kritis globalnya adalah lingkaran dasar, Ns ≈ 0,181.
- **ACADS 1(a):** FS wasit 1,00.
- **Tabel β target USACE ETL 1110-2-547:** ketujuh baris, dari sumber primer.
- **Ambang hujan:**
  - Guzzetti (2008): I = 2,20·D⁻⁰·⁴⁴, terkonfirmasi lewat **sumber sekunder** (basis data ambang CNR-IRPI; Brunetti et al. 2010), bukan dari teks aslinya.
  - Banjarmangu: I = 43,2·D⁻⁰·⁸⁷.
  - Hidayat (2019): 61 mm/1 hari, 91 mm/3 hari.
  - Yuniawan (2022): 30 mm/1 hari, 64 mm/3 hari.
- **Atribusi La Liboriana:** Vega & Hidalgo (2023).
- **Statistik Reichenbach (2018), angka 180 m Brenning, NASA GLC:** 11.033 kejadian; 355 di Indonesia.
- **Kh = 0,5·PGA:** langsung dari SNI 8460 §12.2.7.

---

## 4. Masih belum terverifikasi (jangan dikutip sebagai fakta)

- Isi spesifik Fell et al. (2008), Corominas et al. (2014) dan Liu & Wu (2008) yang dikutip. Karyanya ada, tetapi teksnya tidak terbaca.
- Nilai ρ c′–φ′ dari Lumb dan Cherubini.
- Wang et al. (2024) "+36,7%"; Seed (1979) kh 0,10–0,15.
- Kriteria m_α < 0,2 sebagai milik Whitman & Bailey (1967). Atribusinya sudah dilunakkan di laporan.
- Detail InaRISK (URL, lisensi, resolusi); server BNPB tidak dapat diakses saat pengecekan.
- Bentuk β pada laporan TRIGRS 2002 vs kode. Keduanya identik untuk Iz_LT = 0, yaitu nilai yang dipakai.
