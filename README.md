# Praktikum SIG 2026 — Pertemuan 12
## Klasterisasi Hotspot DBSCAN untuk Optimasi Logistik

> **Dosen:** Mochamad T. Zein, M.Kom  
> **Topik:** Analisis Spasial Lanjut — Machine Learning Spasial

---

## Struktur File

```
praktikum 12 SIG/
└── tugas/
    ├── README.md                          ← Panduan ini
    ├── database.sql                       ← Langkah 1: SQL generator dataset
    ├── spatial_clustering.py              ← Langkah 2-4: Script utama DBSCAN
    ├── spatial_clustering_skenario_a.py   ← Tugas Mandiri 1a: epsilon=0.8km, min_pts=5
    ├── spatial_clustering_skenario_b.py   ← Tugas Mandiri 1b: epsilon=0.2km, min_pts=50
    ├── spatial_clustering_to_db.py        ← Tugas Mandiri 2: Export ke PostGIS
    ├── index.html                         ← Langkah 5: Visualisasi peta Leaflet.js
    └── laporan_praktikum.md               ← Tugas Mandiri 3: Laporan analisis
```

---

## Urutan Pengerjaan

### LANGKAH 1 — Setup Database PostGIS

1. Buka **DBeaver** atau **pgAdmin**
2. Buat database baru bernama `db_fmikom_gis`
3. Buka SQL Editor, paste seluruh isi `database.sql`
4. Jalankan dengan **Ctrl+A** lalu **Alt+X** (Execute All)
5. Verifikasi: `SELECT COUNT(*) FROM riwayat_penjemputan_paket;` → harus **2000**

---

### LANGKAH 2 — Setup Python Environment

Buka terminal di folder `tugas/` dan jalankan:

```bash
# Buat Virtual Environment
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate

# Install dependensi
pip install pandas geopandas scikit-learn sqlalchemy psycopg2-binary
```

---

### LANGKAH 3-4 — Jalankan Script Utama

> **Penting:** Edit terlebih dahulu `DB_PASSWORD` di dalam file Python sesuai password PostgreSQL Anda!

```bash
# Edit password di baris: DB_PASSWORD = "postgres"
# lalu jalankan:
python spatial_clustering.py
```

Output yang diharapkan:
```
[INFO] Menghubungkan ke database: db_fmikom_gis...
[INFO] Total Data Berhasil Ditarik: 2000 baris
[DBSCAN] Konfigurasi Hyperparameter:
  - epsilon      : 0.5 km (500 meter)
  - min_points   : 20 titik
[INFO] Training selesai.
[HASIL] Algoritma menemukan 3 hotspot/klaster logistik
[HASIL] Jumlah titik noise (diabaikan): ~200
[SELESAI] Data spasial disimpan ke: hasil_klaster_logistik.geojson
```

---

### LANGKAH 5 — Visualisasi Peta

Buka `index.html` menggunakan **Live Server** di IDE Anda. Anda akan melihat:
- Peta gelap CartoDB dengan titik berwarna
- Panel statistik (total titik, jumlah klaster, noise)
- **Tombol switcher skenario** (Default / Skenario A / Skenario B)
- Legenda dinamis
- Popup detail setiap titik saat diklik

---

### TUGAS MANDIRI 1 — Uji Hyperparameter

```bash
# Skenario A (epsilon=0.8km, min_pts=5)
python spatial_clustering_skenario_a.py

# Skenario B (epsilon=0.2km, min_pts=50)
python spatial_clustering_skenario_b.py
```

Setelah masing-masing dijalankan, muat ulang browser dan klik tombol skenario di peta.

---

### TUGAS MANDIRI 2 — Export ke Database

```bash
python spatial_clustering_to_db.py
```

Kemudian buka DBeaver/pgAdmin, refresh tabel, dan buat **screenshot** tabel `hasil_prediksi_logistik`.

---

### TUGAS MANDIRI 3 — Laporan

Baca dan edit `laporan_praktikum.md` sesuai hasil aktual yang Anda dapatkan.  
Lengkapi dengan screenshot yang diminta dan kumpulkan via **Edlink** sebelum PAS.

---

## Troubleshooting

| Error | Solusi |
|-------|--------|
| `psycopg2.OperationalError` | Periksa apakah PostgreSQL berjalan dan password benar |
| `ModuleNotFoundError` | Pastikan virtual environment aktif dan pip install sudah dijalankan |
| `geopandas` tidak bisa install | Install GDAL terlebih dahulu atau gunakan `conda install geopandas` |
| File GeoJSON tidak terbentuk | Periksa apakah script Python berjalan tanpa error hingga selesai |
| Peta kosong di browser | Pastikan file GeoJSON ada di folder yang sama dengan `index.html` |
| `Cannot find PostGIS` | Jalankan `CREATE EXTENSION postgis;` di database Anda |
