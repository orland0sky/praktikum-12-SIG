"""
=================================================================
PRAKTIKUM SIG 2026 - Pertemuan 12
TUGAS MANDIRI 2 - Integrasi Arsitektur Database

Modifikasi Langkah 4: Alih-alih export ke file .geojson statis,
hasil prediksi AI langsung ditulis ke tabel baru di PostGIS
menggunakan df.to_sql() dari SQLAlchemy.

Tabel tujuan: hasil_prediksi_logistik
=================================================================
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ---- KONEKSI DATABASE ----
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "db_fmikom_gis"
DB_USER     = "postgres"
DB_PASSWORD = "admin"   # <-- Ganti dengan password PostgreSQL Anda

db_uri = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_uri)
print(f"[INFO] Menghubungkan ke database: {DB_NAME}...")

# ---- EKSTRAKSI DATA DARI POSTGIS ----
query = """
    SELECT
        id_pesanan,
        waktu_pesanan,
        ST_X(koordinat) AS lng,
        ST_Y(koordinat) AS lat
    FROM riwayat_penjemputan_paket
"""

df = pd.read_sql(query, engine)
print(f"[INFO] Total data berhasil ditarik: {len(df)} baris")

# ---- DBSCAN CLUSTERING ----
from sklearn.cluster import DBSCAN

coords          = df[['lat', 'lng']].values
coords_radians  = np.radians(coords)

EARTH_RADIUS_KM = 6371.0
epsilon_km      = 0.5
epsilon_rad     = epsilon_km / EARTH_RADIUS_KM
min_points      = 20

print(f"\n[DBSCAN] Melatih model dengan epsilon={epsilon_km}km, min_points={min_points}...")

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
print(f"[HASIL] Ditemukan {jumlah_klaster} klaster, {jumlah_noise} titik noise.")

# ---- TUGAS MANDIRI 2: SIMPAN HASIL KE DATABASE (df.to_sql) ----
# Buat DataFrame khusus untuk disimpan ke database
df_hasil = df[['id_pesanan', 'waktu_pesanan', 'lng', 'lat', 'id_klaster']].copy()
df_hasil['epsilon_km']  = epsilon_km
df_hasil['min_points']  = min_points
df_hasil['skenario']    = 'Default'
df_hasil['is_hotspot']  = df_hasil['id_klaster'] != -1

print("\n[INFO] Menyimpan hasil prediksi ke tabel 'hasil_prediksi_logistik' di PostGIS...")

# Hapus tabel lama jika ada (untuk fresh insert)
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS hasil_prediksi_logistik;"))
    conn.commit()

# Simpan ke database menggunakan df.to_sql()
# if_exists='replace' akan membuat tabel baru atau menimpa yang lama
df_hasil.to_sql(
    name        = 'hasil_prediksi_logistik',
    con         = engine,
    if_exists   = 'replace',   # 'replace' = hapus & buat ulang, 'append' = tambahkan
    index       = False,        # Jangan simpan index DataFrame sebagai kolom
    schema      = 'public'      # Schema PostgreSQL default
)
print("[SUKSES] Data berhasil ditulis ke tabel 'hasil_prediksi_logistik'!")

# ---- VERIFIKASI: Baca kembali dari database ----
print("\n[VERIFIKASI] Membaca data dari tabel baru di database...")
df_verifikasi = pd.read_sql(
    "SELECT * FROM hasil_prediksi_logistik LIMIT 5;",
    engine
)
print(df_verifikasi.to_string())

# Statistik ringkasan
df_stats = pd.read_sql(
    """
    SELECT
        id_klaster,
        COUNT(*) AS jumlah_titik,
        ROUND(AVG(lng)::numeric, 6) AS avg_longitude,
        ROUND(AVG(lat)::numeric, 6) AS avg_latitude,
        skenario
    FROM hasil_prediksi_logistik
    GROUP BY id_klaster, skenario
    ORDER BY id_klaster;
    """,
    engine
)
print("\n[STATISTIK] Ringkasan per klaster di database:")
print(df_stats.to_string())

total_rows = pd.read_sql("SELECT COUNT(*) as total FROM hasil_prediksi_logistik;", engine)
print(f"\n[INFO] Total baris tersimpan di database: {total_rows['total'].iloc[0]}")
print("\n[SELESAI] Buka DBeaver/pgAdmin, refresh tabel, dan lihat 'hasil_prediksi_logistik'!")
print("         Lakukan screenshot tabel tersebut untuk laporan tugas Anda.")
