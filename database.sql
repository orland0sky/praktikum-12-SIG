-- ============================================================
-- PRAKTIKUM SIG 2026 - Pertemuan 12
-- Topik: Klasterisasi Hotspot Berbasis Kepadatan (DBSCAN)
-- Studi Kasus: Optimasi Penempatan Agen Drop-Point Logistik
-- Dosen: Mochamad T. Zein, M.Kom
-- ============================================================

-- LANGKAH 1A: Pastikan ekstensi PostGIS aktif
CREATE EXTENSION IF NOT EXISTS postgis;

-- LANGKAH 1B: Hapus tabel jika sudah ada
DROP TABLE IF EXISTS riwayat_penjemputan_paket;

-- LANGKAH 1C: Buat struktur tabel spasial
CREATE TABLE riwayat_penjemputan_paket (
    id_pesanan    VARCHAR(50) PRIMARY KEY,
    waktu_pesanan TIMESTAMP,
    koordinat     GEOMETRY(Point, 4326)
);

-- ============================================================
-- GENERATE DATA KLASTER
-- ============================================================

-- KLASTER 1: Area I - Purwokerto Timur (800 Titik)
-- Koordinat pusat: lng=109.2486, lat=-7.4265
INSERT INTO riwayat_penjemputan_paket (id_pesanan, waktu_pesanan, koordinat)
SELECT
    'PKG-ARI-' || LPAD(i::text, 4, '0'),
    NOW() - (random() * interval '30 days'),
    ST_SetSRID(
        ST_MakePoint(
            109.2486 + ((random() - 0.5) * 0.006),
            -7.4265  + ((random() - 0.5) * 0.006)
        ),
        4326
    )
FROM generate_series(1, 800) AS i;

-- KLASTER 2: Area II - Purwokerto Utara (600 Titik)
-- Koordinat pusat: lng=109.2495, lat=-7.4055
INSERT INTO riwayat_penjemputan_paket (id_pesanan, waktu_pesanan, koordinat)
SELECT
    'PKG-AII-' || LPAD(i::text, 4, '0'),
    NOW() - (random() * interval '30 days'),
    ST_SetSRID(
        ST_MakePoint(
            109.2495 + ((random() - 0.5) * 0.005),
            -7.4055  + ((random() - 0.5) * 0.005)
        ),
        4326
    )
FROM generate_series(1, 600) AS i;

-- KLASTER 3: Area III - Purwokerto Selatan (400 Titik)
-- Koordinat pusat: lng=109.2450, lat=-7.4450
INSERT INTO riwayat_penjemputan_paket (id_pesanan, waktu_pesanan, koordinat)
SELECT
    'PKG-III-' || LPAD(i::text, 4, '0'),
    NOW() - (random() * interval '30 days'),
    ST_SetSRID(
        ST_MakePoint(
            109.2450 + ((random() - 0.5) * 0.004),
            -7.4450  + ((random() - 0.5) * 0.004)
        ),
        4326
    )
FROM generate_series(1, 400) AS i;

-- NOISE / OUTLIER: Tersebar Acak di sekitar Purwokerto (200 Titik)
INSERT INTO riwayat_penjemputan_paket (id_pesanan, waktu_pesanan, koordinat)
SELECT
    'PKG-RND-' || LPAD(i::text, 4, '0'),
    NOW() - (random() * interval '30 days'),
    ST_SetSRID(
        ST_MakePoint(
            109.2450 + ((random() - 0.5) * 0.090),
            -7.4250  + ((random() - 0.5) * 0.090)
        ),
        4326
    )
FROM generate_series(1, 200) AS i;

-- ============================================================
-- VERIFIKASI DATA
-- ============================================================

-- Cek total data yang berhasil dimasukkan (harus = 2000)
SELECT COUNT(*) AS total_titik FROM riwayat_penjemputan_paket;

-- Preview data
SELECT * FROM riwayat_penjemputan_paket LIMIT 10;
