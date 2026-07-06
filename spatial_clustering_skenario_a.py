"""
=================================================================
PRAKTIKUM SIG 2026 - Pertemuan 12
TUGAS MANDIRI 1 - Uji Coba Hyperparameter

SKENARIO A: epsilon_km = 0.8 (800 meter), min_points = 5
Ekspektasi: Klaster besar & banyak, threshold titik sangat rendah
=================================================================
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from sqlalchemy import create_engine
from sklearn.cluster import DBSCAN

# ---- KONEKSI DATABASE ----
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "db_fmikom_gis"
DB_USER     = "postgres"
DB_PASSWORD = "admin"   # <-- Ganti dengan password PostgreSQL Anda

db_uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_uri)

query = """
    SELECT
        id_pesanan,
        ST_X(koordinat) AS lng,
        ST_Y(koordinat) AS lat
    FROM riwayat_penjemputan_paket
"""

df = pd.read_sql(query, engine)
print(f"[INFO] Total data: {len(df)} baris")

# ---- DBSCAN SKENARIO A ----
coords = df[['lat', 'lng']].values
coords_radians = np.radians(coords)

EARTH_RADIUS_KM = 6371.0
epsilon_km  = 0.8   # 800 meter (LEBIH BESAR)
min_points  = 5     # 5 titik (LEBIH SEDIKIT)
epsilon_rad = epsilon_km / EARTH_RADIUS_KM

print(f"\n[SKENARIO A] Hyperparameter:")
print(f"  - epsilon : {epsilon_km} km = {epsilon_km*1000:.0f} meter")
print(f"  - min_pts : {min_points} titik")

model_dbscan = DBSCAN(
    eps=epsilon_rad,
    min_samples=min_points,
    algorithm='ball_tree',
    metric='haversine'
)
model_dbscan.fit(coords_radians)

df['id_klaster'] = model_dbscan.labels_

jumlah_klaster = len(set(model_dbscan.labels_)) - (1 if -1 in model_dbscan.labels_ else 0)
jumlah_noise   = (model_dbscan.labels_ == -1).sum()

print(f"\n[HASIL SKENARIO A]")
print(f"  Jumlah klaster ditemukan : {jumlah_klaster}")
print(f"  Jumlah titik noise       : {jumlah_noise} ({jumlah_noise/len(df)*100:.1f}%)")

print("\n[RINGKASAN] Distribusi titik per klaster (Skenario A):")
klaster_counts = df['id_klaster'].value_counts().sort_index()
for label, count in klaster_counts.items():
    tipe = "NOISE" if label == -1 else f"Klaster {label}"
    print(f"  {tipe:15s}: {count} titik")

# ---- EXPORT KE GEOJSON ----
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lng, df.lat),
    crs="EPSG:4326"
)

output_file = 'hasil_klaster_skenario_a.geojson'
gdf.to_file(output_file, driver='GeoJSON')
print(f"\n[SELESAI] Data Skenario A disimpan ke: {output_file}")

"""
ANALISIS TEKNIS SKENARIO A (epsilon=0.8km, min_points=5):
==========================================================
- Radius 800m yang BESAR membuat DBSCAN mencari titik dalam area yang lebih luas.
  Dua titik yang secara fisik cukup jauh masih dianggap "tetangga".
- min_points=5 yang SANGAT RENDAH berarti hanya butuh 5 titik dalam radius 800m
  untuk membentuk sebuah klaster "core point".
- EFEK KOMBINASI: Akan menghasilkan klaster-klaster yang sangat BESAR dan MERGED
  (klaster yang semestinya terpisah bisa tergabung menjadi satu).
  Noise/outlier yang terdeteksi akan sangat SEDIKIT karena threshold rendah.
- RISIKO: Area yang sebenarnya tidak terlalu padat bisa ikut masuk klaster,
  sehingga rekomendasi lokasi kios menjadi kurang presisi/akurat.
"""
