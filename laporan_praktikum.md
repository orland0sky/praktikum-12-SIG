# LAPORAN PRAKTIKUM SIG — PERTEMUAN 12
## Klasterisasi Hotspot Berbasis Kepadatan (DBSCAN) untuk Optimasi Penempatan Agen Drop-Point Logistik

---

**Nama Mata Kuliah :** Sistem Informasi Geografis (SIG)  
**Dosen Pengampu   :** Mochamad T. Zein, M.Kom  
**Topik             :** Analisis Spasial Lanjut — Machine Learning Spasial  
**Tahun Akademik   :** 2025/2026  

---

## 1. Tujuan Praktikum

Praktikum ini bertujuan agar mahasiswa mampu:

1. Mengekstrak dan memformat data titik spasial (*Point*) dari basis data **PostGIS** menjadi struktur *DataFrame* yang siap diproses algoritma *Machine Learning*.
2. Mengimplementasikan algoritma **Unsupervised Learning DBSCAN** menggunakan pustaka Python `scikit-learn`.
3. Memahami pengaruh **hyperparameter** radius jarak (epsilon) dan jumlah titik minimum (MinPts) terhadap pembentukan klaster geografis.
4. Mengekspor hasil prediksi klaster ke format **GeoJSON** untuk divisualisasikan melalui antarmuka peta interaktif **Leaflet.js**.

---

## 2. Alat dan Bahan

| No | Alat/Bahan | Keterangan |
|----|-----------|-----------|
| 1  | PostgreSQL ≥ 13 + PostGIS | RDBMS spasial untuk menyimpan dan query data koordinat |
| 2  | DBeaver Community | GUI klien database untuk manajemen PostGIS |
| 3  | Python ≥ 3.8 | Lingkungan eksekusi algoritma Machine Learning |
| 4  | pandas + geopandas | Manipulasi data tabular dan spasial |
| 5  | scikit-learn | Library implementasi DBSCAN |
| 6  | sqlalchemy + psycopg2 | Koneksi Python ke PostgreSQL |
| 7  | Antigravity IDE / VS Code | Editor kode + Live Server |
| 8  | Leaflet.js | Library visualisasi peta interaktif berbasis web |

---

## 3. Skenario dan Deskripsi Dataset

Dataset yang digunakan adalah **2.000 titik koordinat pemesanan paket** yang dihasilkan secara sintetis menggunakan PostGIS:

| Kelompok | ID Prefix | Jumlah Titik | Koordinat Pusat | Keterangan |
|----------|-----------|-------------|----------------|-----------|
| Klaster 1 | PKG-ARI- | 800 titik | lng=109.2486, lat=-7.4265 | Area I — Purwokerto Timur |
| Klaster 2 | PKG-AII- | 600 titik | lng=109.2495, lat=-7.4055 | Area II — Purwokerto Utara |
| Klaster 3 | PKG-III- | 400 titik | lng=109.2450, lat=-7.4450 | Area III — Purwokerto Selatan |
| Noise     | PKG-RND- | 200 titik | Tersebar acak | Outlier di pinggiran kota |

**Total dataset:** 2.000 titik koordinat dalam proyeksi **EPSG:4326** (WGS84).

---

## 4. Pembahasan Langkah Praktikum

### Langkah 1 — Persiapan Database (PostGIS)

Dataset dibuat menggunakan SQL Generator yang memanfaatkan fungsi `generate_series()` dan `ST_MakePoint()` milik PostGIS. Struktur tabel spasial:

```sql
CREATE TABLE riwayat_penjemputan_paket (
    id_pesanan    VARCHAR(50) PRIMARY KEY,
    waktu_pesanan TIMESTAMP,
    koordinat     GEOMETRY(Point, 4326)
);
```

Data spasial disimpan dalam kolom bertipe `GEOMETRY(Point, 4326)`, memungkinkan query berbasis jarak dan visualisasi langsung di DBeaver melalui tab **Spatial**.

### Langkah 2 — Ekstraksi Data ke Python

Data diekstrak dari PostGIS menggunakan query spasial:

```sql
SELECT id_pesanan, ST_X(koordinat) AS lng, ST_Y(koordinat) AS lat
FROM riwayat_penjemputan_paket
```

`ST_X()` mengekstrak Longitude dan `ST_Y()` mengekstrak Latitude dari objek geometri, menghasilkan 2.000 baris DataFrame siap proses.

### Langkah 3 — Algoritma DBSCAN

**Mengapa DBSCAN?** Berbeda dengan K-Means, DBSCAN menemukan klaster secara otomatis berdasarkan **kepadatan lokal** tanpa mensyaratkan jumlah klaster diketahui sebelumnya. Titik tanpa cukup tetangga diklasifikasikan sebagai *Noise* (label -1).

**Konversi Koordinat ke Radian** diperlukan karena DBSCAN menggunakan metrik **Haversine** yang menghitung jarak aktual di permukaan bumi:

```
epsilon_radian = epsilon_km / radius_bumi_km = 0.5 / 6371.0 ≈ 0.0000785 radian
```

**Konfigurasi default:** epsilon=0.5km, min_samples=20, algorithm=ball_tree, metric=haversine

### Langkah 4 — Export ke GeoJSON

Hasil prediksi dikonversi ke GeoDataFrame dan diekspor sebagai GeoJSON untuk konsumsi Leaflet.js.

### Langkah 5 — Visualisasi Peta (index.html)

Peta interaktif menggunakan dark basemap CartoDB dan menampilkan titik berwarna berdasarkan ID klaster (merah/kuning/biru = hotspot, abu-abu = noise).

---

## 5. Tugas Mandiri 1 — Uji Coba Hyperparameter

### Skenario A: epsilon=0.8km, min_points=5

**Ekspektasi dan Analisis:**

| Indikator | Nilai Ekspektasi | Penjelasan |
|-----------|-----------------|-----------|
| Jumlah klaster | Lebih sedikit | Radius besar bisa merge klaster yang berdekatan |
| Ukuran klaster | Lebih besar | Cakupan area per klaster meluas |
| Titik noise | Sangat sedikit | Threshold sangat rendah, hampir semua masuk klaster |
| Presisi hotspot | Rendah | Batas klaster kabur dan ambigu |

**Analisis Teknis Skenario A:**

- **Radius 800m** menyebabkan "neighborhood" mencakup area yang jauh lebih luas. Dua klaster berbeda yang letaknya berdekatan bisa tergabung (merge) menjadi satu klaster besar.
- **min_points=5** sangat rendah sehingga hampir semua titik bisa menjadi core point, termasuk titik noise yang kebetulan berdekatan dengan 4 titik lain.
- **Risiko untuk keputusan bisnis:** Pusat klaster yang terbentuk bisa jatuh di "antara" dua area padat, bukan di salah satunya, sehingga penempatan kios menjadi tidak optimal.

---

### Skenario B: epsilon=0.2km, min_points=50

**Ekspektasi dan Analisis:**

| Indikator | Nilai Ekspektasi | Penjelasan |
|-----------|-----------------|-----------|
| Jumlah klaster | Sama atau lebih banyak | Klaster besar bisa terpecah menjadi sub-klaster |
| Ukuran klaster | Lebih kecil, presisi tinggi | Hanya area super padat yang terbentuk |
| Titik noise | Jauh lebih banyak | Pinggiran klaster tereliminasi sebagai noise |
| Presisi hotspot | Sangat tinggi | Menunjuk "inti keras" kepadatan absolut |

**Analisis Teknis Skenario B:**

- **Radius 200m** setara dengan jalan kaki 2-3 menit. Hanya titik yang benar-benar berdekatan yang dianggap tetangga.
- **min_points=50** mensyaratkan 50+ pesanan dalam lingkaran 200m. Ini adalah kondisi kepadatan yang **sangat ketat dan selektif**.
- **Noise meningkat drastis:** Titik-titik di pinggiran klaster yang sebelumnya masuk sebagai border point kini menjadi noise.
- **Keunggulan untuk keputusan bisnis:** Setiap titik dalam klaster dijamin berada di area dengan kepadatan pesanan yang **absolut tinggi**.

---

### Perbandingan Visual Ketiga Skenario

| Aspek | Skenario A (0.8km, 5) | Default (0.5km, 20) | Skenario B (0.2km, 50) |
|-------|----------------------|---------------------|----------------------|
| Presisi lokasi | Rendah | Sedang | Sangat Tinggi |
| Cakupan area | Sangat luas | Sedang | Sempit tapi akurat |
| Jumlah noise | Sangat sedikit | Sedang (~200) | Sangat banyak |
| Risiko bisnis | Tinggi (over-generalize) | Sedang | Rendah |
| Cocok untuk | Eksplorasi awal | Analisis umum | Keputusan investasi |

---

### Jawaban: Parameter Terbaik untuk Satu Kios di Area I

**JAWABAN: Skenario B (epsilon=0.2km, min_points=50)**

**Alasan Teknis:**

Dengan anggaran yang **sangat terbatas** (hanya satu kios), setiap kesalahan penempatan memiliki opportunity cost yang besar karena tidak ada kios cadangan untuk menutupi area yang terlewat.

**1. Prioritas Precision > Recall**
Skenario B memprioritaskan ketepatan (precision) di atas cakupan (recall). Klaster yang terbentuk hanya mencakup titik-titik yang dalam radius 200m terdapat minimal 50 pesanan. Ini adalah **inti kepadatan absolut** yang dijamin bukan fluke statistik.

**2. Eliminasi Area Ambigu**
Skenario A dengan min_points=5 dapat memasukkan area "cukup dekat" ke dalam klaster, padahal area tersebut mungkin tidak cukup padat untuk mendukung profitabilitas satu kios. Dengan Skenario B, setiap titik dalam klaster merupakan **confirmed hotspot**.

**3. Geometri Haversine**
Radius 200m berarti area lingkaran seluas kira-kira 0.126 km² (pi x 0.2² km²). Jika dalam area sekecil itu terdapat 50+ pesanan, area tersebut secara **geometri** adalah hotspot paling absolut padat.

**4. Robustness dan Reliabilitas**
Klaster Skenario B dibangun di atas kepadatan yang sangat kuat, sehingga tidak akan berubah drastis meskipun ada variasi data di masa mendatang.

---

## 6. Tugas Mandiri 2 — Integrasi Arsitektur Database

### Modifikasi Langkah 4: Export ke Tabel PostGIS

File `spatial_clustering_to_db.py` memodifikasi Langkah 4 dengan menggunakan `df.to_sql()` SQLAlchemy untuk menulis hasil prediksi langsung ke tabel baru `hasil_prediksi_logistik`:

```python
df_hasil.to_sql(
    name      = 'hasil_prediksi_logistik',
    con       = engine,
    if_exists = 'replace',
    index     = False,
    schema    = 'public'
)
```

### Perbandingan Arsitektur

| Aspek | File GeoJSON (Statis) | Tabel PostGIS (Dinamis) |
|-------|----------------------|------------------------|
| Pembaruan data | Manual (jalankan ulang script) | Otomatis via SQL/trigger |
| Multi-user | Tidak (file lokal) | Ya (concurrent access) |
| Query lanjutan | Tidak bisa | Bisa langsung JOIN, WHERE, dll |
| Integrasi backend | Perlu parsing file | Langsung query SQL |
| Skalabilitas | Terbatas ukuran file | Virtually unlimited |

### Struktur Tabel `hasil_prediksi_logistik`

| Kolom | Tipe Data | Keterangan |
|-------|-----------|-----------|
| id_pesanan | varchar | ID unik paket |
| waktu_pesanan | timestamp | Waktu pemesanan |
| lng | float8 | Longitude |
| lat | float8 | Latitude |
| id_klaster | int8 | Hasil prediksi DBSCAN (-1=noise) |
| epsilon_km | float8 | Hyperparameter epsilon |
| min_points | int8 | Hyperparameter min_points |
| skenario | varchar | Label skenario |
| is_hotspot | bool | True jika bukan noise |

> **Screenshot DBeaver/pgAdmin:** Lampirkan tangkapan layar yang menunjukkan tabel `hasil_prediksi_logistik` dengan data yang telah terisi, terutama kolom `id_klaster` berisi nilai hasil prediksi AI.

---

## 7. Kesimpulan

1. **DBSCAN** efektif untuk analisis hotspot spasial karena mampu menemukan klaster dengan bentuk arbitrer dan secara otomatis memisahkan *noise* tanpa mendefinisikan jumlah klaster terlebih dahulu.

2. **Hyperparameter sangat kritis:** Perubahan epsilon dan min_points menghasilkan perbedaan signifikan dalam jumlah, ukuran, dan presisi klaster. Tidak ada parameter "terbaik" secara universal — selalu bergantung konteks bisnis.

3. **Untuk keputusan bisnis bernilai tinggi** (investasi kios dengan anggaran terbatas), **Skenario B** (epsilon kecil, min_points besar) lebih aman karena mengidentifikasi "inti keras" hotspot yang benar-benar padat secara absolut.

4. **Integrasi Pipeline** PostGIS → Python ML → PostGIS → Leaflet.js membentuk arsitektur *spatial intelligence* yang scalable dan dapat dikembangkan lebih lanjut.

5. **Integrasi arsitektur database** menggunakan `df.to_sql()` jauh lebih unggul dibanding file GeoJSON statis dalam hal skalabilitas, multi-user access, dan kemampuan query lanjutan.

---

## 8. Referensi

1. Ester, M. et al. (1996). *A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise.* KDD-96.
2. Scikit-learn Documentation: DBSCAN Clustering
3. PostGIS Documentation: Spatial Functions Reference
4. Leaflet.js Documentation
5. SQLAlchemy Documentation: Engine and Connection
