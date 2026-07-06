"""
=================================================================
PRAKTIKUM SIG 2026 - Pertemuan 12
Topik : Analisis Spasial Lanjut
Studi Kasus : Klasterisasi Hotspot Berbasis Kepadatan (DBSCAN)
              Optimasi Penempatan Agen Drop-Point Logistik
Dosen : Mochamad T. Zein, M.Kom

File  : spatial_clustering.py
Langkah : 2 (Ekstraksi Data) + 3 (DBSCAN) + 4 (Export GeoJSON)
=================================================================
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from sqlalchemy import create_engine
from sklearn.cluster import DBSCAN

# ==============================================================
# LANGKAH 2 - EKSTRAKSI DATA DARI POSTGIS
# ==============================================================

# 1. Konfigurasi Koneksi PostgreSQL
#    >>> SESUAIKAN PASSWORD DENGAN SETTING DATABASE LOKAL ANDA <<<
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "db_fmikom_gis"
DB_USER     = "postgres"
DB_PASSWORD = "admin"   # <-- Ganti dengan password PostgreSQL Anda

db_uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_uri)
print(f"[INFO] Menghubungkan ke database: {DB_NAME}...")

# 2. Query SQL Spasial: Mengekstrak X (Longitude) dan Y (Latitude)
query = """
    SELECT
        id_pesanan,
        ST_X(koordinat) AS lng,
        ST_Y(koordinat) AS lat
    FROM riwayat_penjemputan_paket
"""

# 3. Memuat data ke Pandas DataFrame
df = pd.read_sql(query, engine)
print(f"[INFO] Total Data Berhasil Ditarik: {len(df)} baris")
print(df.head())

# ==============================================================
# LANGKAH 3 - ALGORITMA DBSCAN
# ==============================================================

# 4. Konversi Koordinat ke Radian
#    (Metrik Haversine mensyaratkan input dalam radian)
coords = df[['lat', 'lng']].values
coords_radians = np.radians(coords)
print("\n[INFO] Koordinat berhasil dikonversi ke radian.")

# 5. Konfigurasi Hyperparameter DBSCAN
EARTH_RADIUS_KM = 6371.0
epsilon_km      = 0.5   # Radius pencarian = 500 meter
epsilon_rad     = epsilon_km / EARTH_RADIUS_KM
min_points      = 20    # Minimal 20 titik untuk membentuk klaster

print(f"\n[DBSCAN] Konfigurasi Hyperparameter:")
print(f"  - epsilon      : {epsilon_km} km ({epsilon_km*1000:.0f} meter)")
print(f"  - min_points   : {min_points} titik")
print(f"  - epsilon_rad  : {epsilon_rad:.8f} radian")

# 6. Training Model DBSCAN
print("\n[INFO] Melatih model DBSCAN...")
model_dbscan = DBSCAN(
    eps=epsilon_rad,
    min_samples=min_points,
    algorithm='ball_tree',
    metric='haversine'
)
model_dbscan.fit(coords_radians)
print("[INFO] Training selesai.")

# 7. Menyimpan Hasil Prediksi ke DataFrame
#    Label -1 = Outlier/Noise
#    Label 0, 1, 2, ... = ID Klaster
df['id_klaster'] = model_dbscan.labels_

jumlah_klaster = len(set(model_dbscan.labels_)) - (1 if -1 in model_dbscan.labels_ else 0)
jumlah_noise   = (model_dbscan.labels_ == -1).sum()

print(f"\n[HASIL] Algoritma menemukan {jumlah_klaster} hotspot/klaster logistik")
print(f"[HASIL] Jumlah titik noise (diabaikan): {jumlah_noise}")

# Ringkasan per klaster
print("\n[RINGKASAN] Distribusi titik per klaster:")
klaster_counts = df['id_klaster'].value_counts().sort_index()
for label, count in klaster_counts.items():
    tipe = "NOISE" if label == -1 else f"Klaster {label}"
    print(f"  {tipe:15s}: {count} titik")

# ==============================================================
# LANGKAH 4 - KONVERSI HASIL MODEL KE GEOJSON
# ==============================================================

# 8. Membuat GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lng, df.lat),
    crs="EPSG:4326"
)

# 9. Mengekspor ke berkas GeoJSON
output_file = 'hasil_klaster_logistik.geojson'
gdf.to_file(output_file, driver='GeoJSON')
print(f"\n[SELESAI] Data spasial disimpan ke: {output_file}")
print(f"[INFO]    Buka index.html dengan Live Server untuk melihat peta.")
