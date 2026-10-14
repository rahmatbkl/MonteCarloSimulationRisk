"""
Konfigurasi: tabel konversi Skor (1-5) -> rentang parameter fisik.

Setiap variabel X1..X6 dinilai 1 (aman) s.d. 5 (kritis) di lapangan
(lihat "Hazard Heatmap Matrix"). Di dalam simulasi, tiap skor diubah
menjadi RENTANG nilai fisik, lalu nilai di dalam rentang itu diacak
(Monte Carlo inner loop).

PENTING: angka-angka di bawah adalah nilai awal yang wajar dari literatur
mekanika tanah, BUKAN hasil kalibrasi. Bobot konsensus akhir sangat
bergantung pada rentang ini, jadi sesuaikan dengan data uji tanah,
SNI 8460:2017, dan inventaris longsor di wilayah studi Anda.
"""

# Urutan variabel dipakai di seluruh kode (kolom X1..X6).
VARIABLES = ["soil", "geometry", "groundwater", "rainfall", "seismic", "vegetation"]

VARIABLE_LABELS = {
    "soil": "Jenis Tanah (X1)",
    "geometry": "Geometri Lereng (X2)",
    "groundwater": "Muka Air Tanah (X3)",
    "rainfall": "Curah Hujan (X4)",
    "seismic": "Beban Seismik (X5)",
    "vegetation": "Tutupan Vegetasi (X6)",
}

# ---------------------------------------------------------------------------
# X1 - Jenis tanah: kohesi efektif c' (kPa), sudut geser phi' (derajat),
#      berat isi gamma (kN/m3), permeabilitas jenuh Ks (m/s).
#      Format: skor -> {parameter: (min, max)}
# ---------------------------------------------------------------------------
SOIL = {
    1: {"c": (15.0, 25.0), "phi": (33.0, 38.0), "gamma": (19.5, 21.0), "ks": (1e-6, 1e-5)},  # Lempung keras / pasir padat
    2: {"c": (10.0, 18.0), "phi": (28.0, 33.0), "gamma": (19.0, 20.5), "ks": (5e-7, 5e-6)},  # Lempung kaku
    3: {"c": (5.0, 12.0),  "phi": (23.0, 28.0), "gamma": (18.0, 19.5), "ks": (1e-7, 1e-6)},  # Lempung sedang
    4: {"c": (2.0, 6.0),   "phi": (18.0, 23.0), "gamma": (16.5, 18.0), "ks": (5e-8, 5e-7)},  # Lempung lunak
    5: {"c": (0.0, 3.0),   "phi": (12.0, 18.0), "gamma": (11.0, 14.0), "ks": (1e-6, 1e-5)},  # Gambut / organik
}

# X2 - Geometri: sudut lereng beta (derajat).
SLOPE_ANGLE = {
    1: (10.0, 25.0),   # Landai
    2: (25.0, 35.0),   # Sedang
    3: (35.0, 45.0),   # Curam
    4: (45.0, 55.0),   # Sangat curam
    5: (55.0, 75.0),   # Tebing (lihat catatan validitas infinite slope di docs)
}
# Ketebalan tanah di atas bidang gelincir H (m), diukur TEGAK LURUS lereng.
# Sama untuk semua skor (longsor translasi dangkal). z vertikal = H / cos(beta).
SLIP_DEPTH = (1.0, 3.0)

# X3 - Muka air tanah awal, rasio m0 = hw / z (0 = kering, 1 = jenuh penuh).
GROUNDWATER_RATIO = {
    1: (0.00, 0.10),   # Dalam
    2: (0.10, 0.35),   # Sedang
    3: (0.35, 0.60),   # Dangkal
    4: (0.60, 0.85),   # Sangat dangkal
    5: (0.85, 1.00),   # Jenuh
}

# X4 - Intensitas hujan I (mm/jam).
RAINFALL_INTENSITY = {
    1: (5.0, 50.0),     # Rendah
    2: (50.0, 75.0),    # Sedang
    3: (75.0, 100.0),   # Tinggi
    4: (100.0, 150.0),  # Sangat tinggi
    5: (150.0, 250.0),  # Ekstrem
}
# Durasi hujan D (jam) dan porositas efektif n_e (-) untuk konversi
# hujan -> kenaikan muka air tanah. Lihat physics.rainfall_to_water_ratio().
RAIN_DURATION_HR = (1.0, 6.0)
EFFECTIVE_POROSITY = (0.05, 0.20)

# X5 - Koefisien seismik horizontal kh (pseudo-statik, fraksi g).
SEISMIC_KH = {
    1: (0.000, 0.020),   # Statis
    2: (0.020, 0.070),   # Rendah
    3: (0.070, 0.120),   # Moderat
    4: (0.120, 0.175),   # Tinggi
    5: (0.175, 0.300),   # Parah
}

# X6 - Vegetasi: kohesi akar cr (kPa) dan kedalaman efektif akar (m).
# Kedalaman akar membuat efek vegetasi otomatis "kondisional":
# jika bidang gelincir lebih dalam dari akar, akar tidak menahan.
ROOT_COHESION = {
    1: (8.0, 15.0),   # Hutan lebat
    2: (4.0, 8.0),    # Perkebunan (mis. kopi)
    3: (2.0, 4.0),    # Semak
    4: (0.5, 2.0),    # Padang rumput
    5: (0.0, 0.0),    # Gundul
}
ROOT_DEPTH = {1: (1.5, 3.0), 2: (1.0, 2.0), 3: (0.5, 1.5), 4: (0.2, 0.5), 5: (0.0, 0.0)}

# Konstanta fisik
GAMMA_WATER = 9.81  # kN/m3

# ---------------------------------------------------------------------------
# Pengaturan simulasi (sesuai kerangka di slide)
# ---------------------------------------------------------------------------
N_OUTER_LHS = 1200      # jumlah konfigurasi skor (outer loop, LHS)
N_INNER_MC = 400        # iterasi Monte Carlo per konfigurasi (inner loop)
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Vulnerability Index (AHP) - tetap dari kerangka asli
# ---------------------------------------------------------------------------
VI_WEIGHTS = {"settlement_distance": 0.667, "vegetation_runout": 0.333}

# Skor jarak permukiman (m): skor -> (jarak_min, jarak_max)
SETTLEMENT_DISTANCE_SCORE = {
    1: (800.0, float("inf")),
    2: (400.0, 800.0),
    3: (150.0, 400.0),
    4: (40.0, 150.0),
    5: (0.0, 40.0),
}

# Kelas Risk Index (RI di rentang 0-1)
RISK_CLASSES = [
    (0.20, "I",   "Sangat Rendah", "Pemantauan rutin."),
    (0.40, "II",  "Rendah",        "Mitigasi ringan."),
    (0.60, "III", "Sedang",        "Wajib investigasi lapangan."),
    (0.80, "IV",  "Tinggi",        "Tindakan segera; pertimbangkan relokasi."),
    (1.01, "V",   "Sangat Tinggi", "DARURAT - evakuasi dan rekayasa geoteknik mendalam."),
]
