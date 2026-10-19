import streamlit as st
import pandas as pd
import numpy as np
import os
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

# Konfigurasi Tampilan Dasbor Modern
st.set_page_config(page_title="ILP - Dasbor Jumantik", layout="wide")

st.title("📊 Dasbor Surveilans Jentik Berkala ")
st.subheader("UPT Puskesmas Karangpawitan - Dinas Kesehatan Kabupaten Garut")
st.markdown("---")

# DATA AKURAT: 10 Desa Wilayah Kerja UPT Puskesmas Karangpawitan yang Benar
desa_list = [
    'Karangpawitan', 'Situjaya', 'Sindangpalay', 'Situgede', 'Cimurah', 
    'Sindanggalih', 'Situsari', 'Karangsari', 'Situsaeur', 'Sindanglaya'
]

# Koordinat Perkiraan Awal Tengah Desa (Sebagai Fallback jika Koordinat Kosong)
koordinat_default = {
    'Karangpawitan': (-7.2064, 107.9405), 'Situjaya': (-7.2100, 107.9500),
    'Sindangpalay': (-7.2000, 107.9350), 'Situgede': (-7.2250, 107.9420),
    'Cimurah': (-7.1850, 107.9250), 'Sindanggalih': (-7.1950, 107.9380),
    'Situsari': (-7.2120, 107.9600), 'Karangsari': (-7.2020, 107.9480),
    'Situsaeur': (-7.2180, 107.9550), 'Sindanglaya': (-7.1900, 107.9450)
}

# Path Lokasi Database CSV Lokal
DB_FILE = 'database_jumantik_karangpawitan.csv'

# LOGIKA DATABASE: Inisialisasi data awal (ditambahkan kolom Latitude dan Longitude)
if not os.path.exists(DB_FILE):
    jumlah_desa = len(desa_list)
    angka_periksa = np.full(jumlah_desa, 150)
    np.random.seed(42)
    angka_positif = np.random.randint(2, 13, size=jumlah_desa)
    
    # Ambil nilai default koordinat
    lats = [koordinat_default[d][0] for d in desa_list]
    lons = [koordinat_default[d][1] for d in desa_list]
    
    df_awal = pd.DataFrame({
        'Desa': desa_list,
        'Rumah_Diperiksa': list(angka_periksa),
        'Positif_Jentik': list(angka_positif),
        'Latitude': lats,
        'Longitude': lons
    })
    df_awal.to_csv(DB_FILE, index=False)

# Memuat data aktif langsung dari file CSV database lokal
df = pd.read_csv(DB_FILE)

# Migrasi otomatis jika file CSV lama belum punya kolom Latitude/Longitude
if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
    df['Latitude'] = df['Desa'].map(lambda d: koordinat_default.get(d, (-7.2064, 107.9405))[0])
    df['Longitude'] = df['Desa'].map(lambda d: koordinat_default.get(d, (-7.2064, 107.9405))[1])
    df.to_csv(DB_FILE, index=False)

# ==========================================
# SIDEBAR: Modul Input Data Dinamis
# ==========================================
st.sidebar.header("📝 Formulir Update Data Lapangan")
st.sidebar.write("Pilih desa dan masukkan hasil pemeriksaan terbaru:")

desa_pilihan = st.sidebar.selectbox("Pilih Lokasi Desa:", df['Desa'].tolist())

# Mengambil nilai data saat ini di database untuk ditampilkan di form input
indeks_desa = df[df['Desa'] == desa_pilihan].index[0]
current_periksa = int(df.loc[indeks_desa, 'Rumah_Diperiksa'])
current_positif = int(df.loc[indeks_desa, 'Positif_Jentik'] if not pd.isna(df.loc[indeks_desa, 'Positif_Jentik']) else 0)
current_lat = df.loc[indeks_desa, 'Latitude']
current_lon = df.loc[indeks_desa, 'Longitude']

input_periksa = st.sidebar.number_input("Jumlah Rumah Diperiksa:", min_value=1, value=current_periksa)
input_positif = st.sidebar.number_input("Jumlah Rumah Positif Jentik:", min_value=0, max_value=int(input_periksa), value=current_positif)

# KOMPONEN SHARE LOKASI GPS (Otomatis mengambil koordinat HP kader)
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Koordinat Lokasi Kunjungan")
st.sidebar.info("Aktifkan GPS HP/Perangkat lalu klik tombol di bawah ini saat berada di lokasi:")

location = streamlit_geolocation()

# Logika penentuan koordinat baru atau tetap menggunakan koordinat lama
if location and location.get('latitude') and location.get('longitude'):
    lat_baru = location['latitude']
    lon_baru = location['longitude']
    st.sidebar.success(f"📍 GPS Terkunci: {lat_baru:.5f}, {lon_baru:.5f}")
else:
    lat_baru = current_lat
    lon_baru = current_lon
    st.sidebar.warning(f"Menggunakan koordinat tersimpan: {lat_baru:.5f}, {lon_baru:.5f}")

st.sidebar.markdown("---")

# TOMBOL SIMPAN KE DATABASE PERMANEN
if st.sidebar.button("💾 Simpan Data ke Database"):
    df.loc[indeks_desa, 'Rumah_Diperiksa'] = input_periksa
    df.loc[indeks_desa, 'Positif_Jentik'] = input_positif
    df.loc[indeks_desa, 'Latitude'] = lat_baru
    df.loc[indeks_desa, 'Longitude'] = lon_baru
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success(f"Berhasil! Data Desa {desa_pilihan} beserta koordinat lokasi telah disimpan.")
    st.rerun()

# ==========================================
# PERHITUNGAN DAN VISUALISASI UTAMA
# ==========================================
df['Negatif_Jentik'] = df['Rumah_Diperiksa'] - df['Positif_Jentik']
total_dicek = int(df['Rumah_Diperiksa'].sum())
total_positif = int(df['Positif_Jentik'].sum())
total_bebas_jentik = total_dicek - total_positif

# Rumus Resmi ABJ Kemenkes
abj_global = (total_bebas_jentik / total_dicek) * 100

# Tampilan Kartu Metrik Modern
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏠 Total Rumah Diperiksa", value=f"{total_dicek} Rumah")
with col2:
    st.metric(label="🪱 Rumah Positif Jentik (Waspada)", value=f"{total_positif} Rumah", delta="Butuh PSN", delta_color="inverse")
with col3:
    status_target = "🟢 Memenuhi Target Kemenkes" if abj_global >= 95 else "🔴 Di Bawah Target Nasional"
    st.metric(label="🎯 Angka Bebas Jentik (ABJ) Global", value=f"{abj_global:.2f}%", delta=status_target)

st.markdown("---")

# ==========================================
# TAMPILAN MAPS/PETA SEBARAN BERDASARKAN HASIL DATA
# ==========================================
st.write("### 🗺️ Peta Geografis Penyebaran Temuan Jentik Nyamuk")
st.write("Warna Pin merah mengindikasikan desa dengan kasus positif tinggi (>5 rumah).")

# Hapus baris data jika ada koordinat kosong
df_peta = df.dropna(subset=['Latitude', 'Longitude'])

if not df_peta.empty:
    # Set pusat peta di rata-rata titik koordinat yang ada
    pusat_lat = df_peta['Latitude'].mean()
    pusat_lon = df_peta['Longitude'].mean()
    
    # Buat objek peta folium
    peta = folium.Map(location=[pusat_lat, pusat_lon], zoom_start=13, control_scale=True)
    
    # Looping memasang penanda (Pin) di setiap lokasi desa
    for _, row in df_peta.iterrows():
        # Penentuan warna Pin berdasarkan keparahan (Jumlah Positif Jentik)
        if row['Positif_Jentik'] > 5:
            warna_pin = 'red'
            ikon = 'exclamation-sign'
        else:
            warna_pin = 'green'
            ikon = 'ok-sign'
            
        # Isi teks informasi pop-up saat Pin di peta diklik
        isi_popup = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 180px;">
            <b>Desa:</b> {row['Desa']}<br>
            <hr style="margin: 5px 0;">
            🏠 Rumah Diperiksa: {int(row['Rumah_Diperiksa'])}<br>
            🔴 Positif Jentik: <b style="color:red;">{int(row['Positif_Jentik'])}</b><br>
            🟢 Bebas Jentik: {int(row['Negatif_Jentik'])}
        </div>
        """
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(isi_popup, max_width=250),
            icon=folium.Icon(color=warna_pin, icon=ikon)
        ).add_to(peta)
        
    # Tampilkan peta ke dalam UI Streamlit secara dinamis
    st_folium(peta, width="100%", height=450, returned_objects=[])
else:
    st.info("Data titik koordinat belum tersedia.")

st.markdown("---")

# TABEL DATA INTERAKTIF
st.write("### 📋 Analisis Prioritas Intervensi Berdasarkan Wilayah Kerja Desa")
st.dataframe(df[['Desa', 'Rumah_Diperiksa', 'Positif_Jentik', 'Negatif_Jentik', 'Latitude', 'Longitude']], use_container_width=True)

# GRAPH INTERAKTIF
st.markdown("---")
st.write("### 📊 Grafik Distribusi Temuan Positif Jentik Nyamuk Per Desa")
st.bar_chart(data=df, x='Desa', y='Positif_Jentik', use_container_width=True)

# Fitur Ekspor Laporan Bulanan ke Excel/CSV
st.markdown("---")
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Unduh Rekap Laporan Bulanan (.CSV) untuk Dinas Kesehatan",
    data=csv_data,
    file_name='laporan_abj_karangpawitan_fix.csv',
    mime='text/csv',
)
