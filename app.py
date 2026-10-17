import streamlit as st
import pandas as pd
import numpy as np
import os

# Konfigurasi Tampilan Dasbor Modern
st.set_page_config(page_title="ILP - Dasbor Jumantik", layout="wide")

st.title("📊 Dasbor Inovasi Surveilans Jentik Berkala (ILP)")
st.subheader("UPT Puskesmas Karangpawitan - Dinas Kesehatan Kabupaten Garut")
st.markdown("---")

# DATA AKURAT: 10 Desa Wilayah Kerja UPT Puskesmas Karangpawitan yang Benar
desa_list = [
    'Karangpawitan', 'Situjaya', 'Sindangpalay', 'Situgede', 'Cimurah', 
    'Sindanggalih', 'Situsari', 'Karangsari', 'Situsaeur', 'Sindanglaya'
]

# Path Lokasi Database CSV Lokal
DB_FILE = 'database_jumantik_karangpawitan.csv'

# LOGIKA DATABASE: Inisialisasi data awal jika file belum pernah ada
if not os.path.exists(DB_FILE):
    jumlah_desa = len(desa_list)
    angka_periksa = np.full(jumlah_desa, 150)
    np.random.seed(42)
    angka_positif = np.random.randint(2, 13, size=jumlah_desa)
    
    df_awal = pd.DataFrame({
        'Desa': desa_list,
        'Rumah_Diperiksa': list(angka_periksa),
        'Positif_Jentik': list(angka_positif)
    })
    df_awal.to_csv(DB_FILE, index=False)

# Memuat data aktif langsung dari file CSV database lokal
df = pd.read_csv(DB_FILE)

# SIDEBAR: Modul Input Data Dinamis untuk Programmer / Kader
st.sidebar.header("📝 Formulir Update Data Lapangan")
st.sidebar.write("Pilih desa dan masukkan hasil pemeriksaan terbaru:")

desa_pilihan = st.sidebar.selectbox("Pilih Lokasi Desa:", df['Desa'].tolist())

# Mengambil nilai data saat ini di database untuk ditampilkan di form input
indeks_desa = df[df['Desa'] == desa_pilihan].index[0]
current_periksa = int(df.loc[indeks_desa, 'Rumah_Diperiksa'])
current_positif = int(df.loc[indeks_desa, 'Positif_Jentik'])

input_periksa = st.sidebar.number_input("Jumlah Rumah Diperiksa:", min_value=1, value=current_periksa)
input_positif = st.sidebar.number_input("Jumlah Rumah Positif Jentik:", min_value=0, max_value=int(input_periksa), value=current_positif)

# TOMBOL SIMPAN KE DATABASE PERMANEN
if st.sidebar.button("💾 Simpan Data ke Database"):
    df.loc[indeks_desa, 'Rumah_Diperiksa'] = input_periksa
    df.loc[indeks_desa, 'Positif_Jentik'] = input_positif
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success(f"Berhasil! Data Desa {desa_pilihan} telah disimpan secara permanen.")
    st.rerun()

# Rumus Perhitungan Epidemiologi Otomatis Berdasarkan Data Database
df['Negatif_Jentik'] = df['Rumah_Diperiksa'] - df['Positif_Jentik']
total_dicek = int(df['Rumah_Diperiksa'].sum())
total_positif = int(df['Positif_Jentik'].sum())
total_bebas_jentik = total_dicek - total_positif

# Rumus Resmi ABJ Kemenkes
abj_global = (total_bebas_jentik / total_dicek) * 100

# VISUALISASI UTAMA: Kartu Metrik Modern
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏠 Total Rumah Diperiksa", value=f"{total_dicek} Rumah")
with col2:
    st.metric(label="🪱 Rumah Positif Jentik (Waspada)", value=f"{total_positif} Rumah", delta="Butuh PSN", delta_color="inverse")
with col3:
    status_target = "🟢 Memenuhi Target Kemenkes" if abj_global >= 95 else "🔴 Di Bawah Target Nasional"
    st.metric(label="🎯 Angka Bebas Jentik (ABJ) Global", value=f"{abj_global:.2f}%", delta=status_target)

st.markdown("---")

# TABEL DATA INTERAKTIF: Untuk Programmer Surveilans
st.write("### 📋 Analisis Prioritas Intervensi Berdasarkan Wilayah Kerja Desa")
st.dataframe(df[['Desa', 'Rumah_Diperiksa', 'Positif_Jentik', 'Negatif_Jentik']], use_container_width=True)

# GRAPH INTERAKTIF: Distribusi Kasus Positif Jentik Per Desa
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
