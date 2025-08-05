import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import mysql.connector
import os

# ================================
# KONEKSI KE DATABASE MySQL
# ================================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # ganti kalau pakai password
    database="toko_heparin"
)
cursor = conn.cursor()

# Buat tabel kalau belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS checkout (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(255),
    alamat TEXT,
    produk TEXT,
    total INT,
    bukti_transfer VARCHAR(255)
)
""")
conn.commit()

# ================================
# KONFIGURASI STREAMLIT
# ================================
st.set_page_config(layout="centered", page_title="Toko Heparin")
BUKTI_FOLDER = "bukti_transfer"
os.makedirs(BUKTI_FOLDER, exist_ok=True)

col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo2.png", width=60)
with col2:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 100%;'>
            <h2 style='margin: 0; font-size: 28px;'>Toko Heparin by Greenlight</h2>
        </div>
    """, unsafe_allow_html=True)

# ================================
# VIDEO PROMO
# ================================
try:
    with open("promo.mp4", "rb") as video_file:
        st.video(video_file.read())
except FileNotFoundError:
    st.warning("Video promo (promo.mp4) tidak ditemukan.")

# ================================
# DATA PRODUK
# ================================
produk_list = [
    {"nama": "Kaos Greenlight Hitam", "harga": 94050, "gambar": "kaos1.jpg"},
    {"nama": "kaos Greenlight Hijau", "harga": 189050, "gambar": "kaos2.jpg"},
    {"nama": "Kaos Greenlight Hitam Pola", "harga": 175200, "gambar": "kaos3.jpg"},
    {"nama": "Greenlight Men's Hoodie Sweater Zipered Austin Jacket H080923", "harga": 360050, "gambar": "jaket1.jpg"},
    {"nama": "Greenlight Men's Bomber Corduroy Jacket Easton H020324", "harga": 341100, "gambar": "jaket2.jpg"},
    {"nama": "Greenlight x Alleia Celana Pria Cargo Pants Line Star CG031123 - Blue, 36", "harga": 449500, "gambar": "jaket3.jpg"},
    {"nama": "Greenlight Men's Bomber Corduroy Jacket Easton H010324", "harga": 341100, "gambar": "celana3.jpg"},
    {"nama": "Greenlight Men's Cargo Slim Fit Pants Garrison H050424", "harga": 445550, "gambar": "celana1.jpg"},
    {"nama": "Greenlight Men's Cargo Regular Fit Pants Jogol OL-050924", "harga": 229000, "gambar": "celana2.jpg"},
]

# ================================
# INISIALISASI KERANJANG
# ================================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

st.title(" Katalog Pakaian Greenlight")

# ================================
# TAMPILKAN PRODUK
# ================================
for i in range(0, len(produk_list), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(produk_list):
            produk = produk_list[i + j]
            with cols[j]:
                try:
                    img = Image.open(produk["gambar"])
                    img = img.resize((250, 250))
                    st.image(img)
                except FileNotFoundError:
                    st.warning(f"Gambar '{produk['gambar']}' tidak ditemukan.")

                st.markdown(f"**{produk['nama']}**")
                st.markdown(f"💸 Rp {produk['harga']:,}")
                ukuran = st.selectbox("Pilih Ukuran", ["S", "M", "L", "XL"], key=f"ukuran_{i+j}")
                if st.button(f"🛒 Beli", key=f"beli_{i+j}"):
                    produk_dengan_ukuran = produk.copy()
                    produk_dengan_ukuran["ukuran"] = ukuran
                    st.session_state.keranjang.append(produk_dengan_ukuran)

# ================================
# TAMPILKAN KERANJANG
# ================================
if st.session_state.keranjang:
    total = sum([item["harga"] for item in st.session_state.keranjang])
    for idx, item in enumerate(st.session_state.keranjang):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {item['nama']} - Ukuran {item['ukuran']} - Rp {item['harga']:,}")
        with col2:
            if st.button("🗑 Hapus", key=f"hapus_{idx}"):
                st.session_state.keranjang.pop(idx)
                st.rerun()
                break

    st.markdown(f"### 🧳 Total: Rp {total:,}")

    # FORMULIR PEMBELIAN
    st.markdown("---")
    st.markdown("### 📝 Formulir Pembelian")
    with st.form("form_pembeli"):
        nama = st.text_input("Nama Lengkap")
        alamat = st.text_area("Alamat Pengiriman")
        kirim = st.form_submit_button("Konfirmasi Pesanan")

        if kirim:
            daftar_produk = "; ".join([f"{item['nama']} (Ukuran {item['ukuran']})" for item in st.session_state.keranjang])
            cursor.execute("INSERT INTO checkout (nama, alamat, produk, total) VALUES (%s, %s, %s, %s)",
                           (nama, alamat, daftar_produk, total))
            conn.commit()
            st.success(f"Terima kasih, {nama}. Pesanan Anda akan segera dikirim ke: {alamat}")

    # =============================
    # UPLOAD BUKTI TRANSFER
    # =============================
    st.markdown("### 📄 Upload Bukti Pembayaran")
    bukti = st.file_uploader("Upload gambar bukti transfer", type=["jpg", "png"])
    if bukti is not None:
        st.image(bukti, caption="Bukti Transfer", width=300)
        bukti_path = os.path.join(BUKTI_FOLDER, bukti.name)
        with open(bukti_path, "wb") as f:
            f.write(bukti.getbuffer())

        cursor.execute("SELECT id FROM checkout ORDER BY id DESC LIMIT 1")
        last = cursor.fetchone()
        if last:
            cursor.execute("UPDATE checkout SET bukti_transfer = %s WHERE id = %s", (bukti.name, last[0]))
            conn.commit()
            st.success("Bukti transfer berhasil disimpan.")

    # =============================
    # QRIS
    # =============================
    st.markdown("### 💳 Pembayaran via QRIS")
    try:
        qris_img = Image.open("qris.png")
        st.image(qris_img, caption="Scan QRIS untuk Pembayaran", width=250)
    except FileNotFoundError:
        st.warning("QRIS image (qris.png) tidak ditemukan.")
else:
    st.info("Keranjang masih kosong. Silakan pilih produk.")

# =============================
# GRAFIK PRODUK TERLARIS
# =============================
st.markdown("### 📊 Grafik Produk Terlars")
produk_names = [p["nama"] for p in produk_list]
penjualan_dummy = [1] * len(produk_list)

fig, ax = plt.subplots()
ax.barh(produk_names, penjualan_dummy, color="green")
ax.set_xlabel("Jumlah Terjual")
st.pyplot(fig)
