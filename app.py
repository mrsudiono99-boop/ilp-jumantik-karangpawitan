import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. KONFIGURASI HALAMAN PREMIUM & TEMA DARK-MODE ELEGAN
st.set_page_config(
    page_title="ILP - Dasbor Jumantik Karangpawitan", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. GAYA DESAIN CUSTOM CSS (Kekinian & Elegant UI)
st.markdown("""
    <style>
    html, body, [data-testid="stSidebar"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #059669 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 25px;
    }
    
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
    }
    
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border: 0;
        border-top: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER UTAMA (ELEGANT DESIGN)
st.markdown('<h1 class="main-title">✨ Integrasi Layanan Primer (ILP)</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">📊 Dasbor Inovasi Surveilans Jentik Berkala — UPT Puskesmas Karangpawitan, Garut</p>', unsafe_allow_html=True)

# 4. DATA WILAYAH KERJA
desa_list = [
    'Karangpawitan', 'Situjaya', 'Sindangpalay', 'Situgede', 'Cimurah', 
    'Sindanggalih', 'Situsari', 'Karangsari', 'Situsaeur', 'Sindanglaya'
]

DB_FILE = 'database_jumantik_karangpawitan.csv'

# LOGIKA DATABASE LOKAL
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

df = pd.read_csv(DB_FILE)

# 5. MODUL FORMULIR SIDEBAR (UI MINIMALIS)
st.sidebar.markdown("### 📝 Pembaruan Data Lapangan")
st.sidebar.markdown("Masukkan rekapitulasi data hasil pemeriksaan kader:")

desa_pilihan = st.sidebar.selectbox("Lokasi Wilayah Desa:", df['Desa'].tolist())

# Perbaikan Bug Pembacaan Indeks Data Server Cloud
indeks_desa = df[df['Desa'] == desa_pilihan].index
current_periksa = int(df.loc[indeks_desa, 'Rumah_Diperiksa'].values[0])
current_positif = int(df.loc[indeks_desa, 'Positif_Jentik'].values[0])

input_periksa = st.sidebar.number_input("Total Rumah Diperiksa:", min_value=1, value=current_periksa)
input_positif = st.sidebar.number_input("Rumah Positif Jentik:", min_value=0, max_value=int(input_periksa), value=current_positif)

if st.sidebar.button("💾 Simpan Permanen ke Database"):
    df.loc[indeks_desa, 'Rumah_Diperiksa'] = input_periksa
    df.loc[indeks_desa, 'Positif_Jentik'] = input_positif
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success(f"Sukses memperbarui data Desa {desa_pilihan}!")
    st.rerun()

# PERHITUNGAN OTOMATIS EPIDEMIOLOGI
df['Negatif_Jentik'] = df['Rumah_Diperiksa'] - df['Positif_Jentik']
total_dicek = int(df['Rumah_Diperiksa'].sum())
total_positif = int(df['Positif_Jentik'].sum())
total_bebas_jentik = total_dicek - total_positif
abj_global = (total_bebas_jentik / total_dicek) * 100

# 6. VISUALISASI METRIK UTAMA BERBASIS KARTU MODERN (GRID LAYOUT)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; margin: 0;">🏠 TOTAL RUMAH DIPERIKSA</p>
            <h2 style="color: #f8fafc; font-size: 2.2rem; font-weight: 700; margin: 5px 0;">{total_dicek:,} <span style="font-size: 1rem; font-weight: 500; color: #64748b;">Rumah</span></h2>
            <p style="color: #10b981; font-size: 0.85rem; font-weight: 600; margin: 0;">↑ Cakupan Penuh 10 Desa</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; margin: 0;">🪱 TEMUAN POSITIF JENTIK</p>
            <h2 style="color: #f43f5e; font-size: 2.2rem; font-weight: 700; margin: 5px 0;">{total_positif:,} <span style="font-size: 1rem; font-weight: 500; color: #64748b;">Rumah</span></h2>
            <p style="color: #f97316; font-size: 0.85rem; font-weight: 600; margin: 0;">⚠ Butuh Intervensi PSN</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    status_warna = "#10b981" if abj_global >= 95 else "#f59e0b"
    status_teks = "🟢 Memenuhi Target Nasional" if abj_global >= 95 else "🔴 Di Bawah Target Kemenkes"
    st.markdown(f"""
        <div class="metric-card">
            <p style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; margin: 0;">🎯 ANGKA BEBAS JENTIK (ABJ)</p>
            <h2 style="color: {status_warna}; font-size: 2.2rem; font-weight: 700; margin: 5px 0;">{abj_global:.2f}%</h2>
            <p style="color: {status_warna}; font-size: 0.85rem; font-weight: 600; margin: 0;">{status_teks}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 7. BAGIAN DATA DAN GRAFIK
tab1, tab2 = st.tabs(["📊 Visualisasi Grafik Distribusi Wilayah", "📋 Tabel Analisis Data Surveilans"])

with tab1:
    st.write("#### Tren Temuan Rumah Positif Jentik Nyamuk Per Desa")
    st.bar_chart(data=df, x='Desa', y='Positif_Jentik', use_container_width=True)

with tab2:
    st.write("#### Data Pemantauan Wilayah Setempat (PWS) Kecamatan Karangpawitan")
    st.dataframe(df[['Desa', 'Rumah_Diperiksa', 'Positif_Jentik', 'Negatif_Jentik']], use_container_width=True)

# 8. FOOTER UNDUH LAPORAN
st.markdown("<hr>", unsafe_allow_html=True)
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Ekspor Rekap Laporan Bulanan (.CSV) untuk Dinas Kesehatan",
    data=csv_data,
    file_name='laporan_abj_karangpawitan_fix.csv',
    mime='text/csv',
)
