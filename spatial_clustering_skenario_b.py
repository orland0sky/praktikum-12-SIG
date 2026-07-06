"""
=================================================================
PRAKTIKUM SIG 2026 - Pertemuan 12
TUGAS MANDIRI 1 - Uji Coba Hyperparameter

SKENARIO B: epsilon_km = 0.2 (200 meter), min_points = 50
Ekspektasi: Klaster kecil & sedikit, hanya area super padat yang terdeteksi
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

# ---- DBSCAN SKENARIO B ----
coords = df[['lat', 'lng']].values
coords_radians = np.radians(coords)

EARTH_RADIUS_KM = 6371.0
epsilon_km  = 0.2   # 200 meter (LEBIH KECIL)
min_points  = 50    # 50 titik (LEBIH BANYAK)
epsilon_rad = epsilon_km / EARTH_RADIUS_KM

print(f"\n[SKENARIO B] Hyperparameter:")
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

print(f"\n[HASIL SKENARIO B]")
print(f"  Jumlah klaster ditemukan : {jumlah_klaster}")
print(f"  Jumlah titik noise       : {jumlah_noise} ({jumlah_noise/len(df)*100:.1f}%)")

print("\n[RINGKASAN] Distribusi titik per klaster (Skenario B):")
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

output_file = 'hasil_klaster_skenario_b.geojson'
gdf.to_file(output_file, driver='GeoJSON')
print(f"\n[SELESAI] Data Skenario B disimpan ke: {output_file}")

"""
ANALISIS TEKNIS SKENARIO B (epsilon=0.2km, min_points=50):
===========================================================
- Radius 200m yang KECIL hanya mempertimbangkan titik-titik yang sangat
  berdekatan sebagai tetangga. Dua titik yang berjarak >200m tidak akan
  saling menghitung sebagai tetangga.
- min_points=50 yang TINGGI berarti sebuah area harus memiliki minimal 50
  titik dalam radius 200m untuk dianggap sebagai core point klaster.
- EFEK KOMBINASI: Hanya area yang BENAR-BENAR padat secara absolut yang
  akan menjadi klaster. Klaster yang terbentuk lebih kecil, lebih presisi,
  dan terpisah satu sama lain dengan jelas. Noise akan jauh lebih banyak.
- KEUNGGULAN: Rekomendasi lokasi kios sangat akurat karena hanya menunjuk
  area dengan kepadatan pesanan yang sangat tinggi.

=================================================================
JAWABAN TUGAS: Parameter manakah yang paling aman untuk satu kios di Area I?
=================================================================
JAWABAN: SKENARIO B (epsilon=0.2km, min_points=50) adalah yang PALING TEPAT
untuk menentukan lokasi hotspot yang paling absolut padat.

ALASAN TEKNIS:
1. Precision > Recall: Dengan anggaran TERBATAS (hanya 1 kios), kesalahan
   penempatan memiliki biaya yang sangat besar. Skenario B memastikan bahwa
   setiap titik dalam klaster memang BENAR-BENAR berada di area super padat,
   bukan sekadar memenuhi threshold rendah seperti Skenario A.

2. Eliminasi False Positive: Skenario A dengan min_points=5 bisa
   menggabungkan area-area yang sebenarnya terpisah menjadi satu klaster besar
   yang misleading. Pusat klaster tersebut mungkin bukan area paling padat.

3. Kepastian Absolut: Skenario B dengan radius 200m dan min_points=50 hanya
   menandai area yang dalam lingkaran 200m terdapat setidaknya 50 pesanan.
   Ini adalah "inti keras" (dense core) dari Area I yang sesungguhnya.
   Penempatan kios di titik pusat klaster ini menjamin jangkauan maksimal
   untuk area pesanan terpadat.
"""
