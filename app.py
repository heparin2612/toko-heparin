import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt  # Untuk grafik


st.set_page_config(layout="centered", page_title="Toko Heparin")

col1, col2 = st.columns([1, 6])  # Kolom kiri kecil, kanan besar

with col1:
    st.image("logo2.png", width=60)

with col2:
    st.markdown("""
        <div style='display: flex; align-items: center; height: 100%;'>
            <h2 style='margin: 0; font-size: 28px;'>Toko Heparin by Greenlight</h2>
        </div>
    """, unsafe_allow_html=True)




# =============================
# VIDEO & AUDIO PROMOSI
# =============================
st.markdown("### ")
try:
    with open("promo.mp4", "rb") as video_file:
        st.video(video_file.read())
except FileNotFoundError:
    st.warning("Video promo (promo.mp4) tidak ditemukan.")

# =============================
# INISIALISASI SESSION
# =============================
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

st.title("🛍️ Katalog Pakaian  Greenlight")

# =============================
# DATA PRODUK
# =============================
produk_list = [
   {"nama": "Kaos Greenlight Hitam", "harga": 94050, "gambar": "kaos1.jpg"},
    {"nama": "kaos Greenlight Hijau", "harga": 189050, "gambar": "kaos2.jpg"},
    {"nama": "Kaos Greenlight Hitam Pola", "harga": 175200, "gambar": "kaos3.jpg"},
    {"nama": "Greenlight Men's Hoodie Sweater Zipered Austin Jacket H080923", "harga": 360050, "gambar": "jaket1.jpg"},
    {"nama": "Greenlight Men's Bomber Corduroy Jacket Easton H020324", "harga": 341100, "gambar": "jaket2.jpg"},
    {"nama": "Greenlight x Alleia Celana Pria Cargo Pants Line Star CG031123 - Blue, 36", "harga": 449500, "gambar": "jaket3.jpg"},
    {"nama": "Greenlight Men's Bomber Corduroy Jacket Easton H010324", "harga": 341100, "gambar": "celana3.jpg"},
    {"nama": "Greenlight Men's Bomber Corduroy Jacket Easton H010324", "harga": 341100, "gambar": "jaket3.jpg"},
    {"nama": "Greenlight Men's Bomber Corduroy Jacket Easton H010324", "harga": 341100, "gambar": "jaket3.jpg"},
]



# =============================
# TAMPILKAN PRODUK
# =============================
for i in range(0, len(produk_list), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(produk_list):
            produk = produk_list[i + j]
            with cols[j]:
                try:
                    img = Image.open(produk["gambar"])
                    img = img.resize((250, 250))
                    st.image(img, use_container_width=False)
                except FileNotFoundError:
                    st.warning(f"Gambar '{produk['gambar']}' tidak ditemukan.")

                st.markdown(f"**{produk['nama']}**")
                st.markdown(f"💸 Rp {produk['harga']:,}")
                
                ukuran = st.selectbox("Pilih Ukuran", ["S", "M", "L", "XL"], key=f"ukuran_{i+j}")
                if st.button(f"🛒 Beli", key=f"beli_{i+j}"):
                    produk_dengan_ukuran = produk.copy()
                    produk_dengan_ukuran["ukuran"] = ukuran
                    st.session_state.keranjang.append(produk_dengan_ukuran)

# =============================
# TAMPILKAN KERANJANG
# =============================
if st.session_state.keranjang:
    total = 0
    for idx, item in enumerate(st.session_state.keranjang):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {item['nama']} - Rp {item['harga']:,}")
        with col2:
            if st.button("🗑 Hapus", key=f"hapus_{idx}"):
                st.session_state.keranjang.pop(idx)
                st.rerun() # Refresh tampilan
                break  # keluar biar tidak error

    total = sum([item["harga"] for item in st.session_state.keranjang])
    st.markdown(f"### 🧾 Total: Rp {total:,}")


    # Form Pembeli
    st.markdown("---")
    st.markdown("### 📝 Formulir Pembelian")
    with st.form("form_pembeli"):
        nama = st.text_input("Nama Lengkap")
        alamat = st.text_area("Alamat Pengiriman")
        kirim = st.form_submit_button("Konfirmasi Pesanan")
        if kirim:
            st.success(f"Terima kasih, {nama}. Pesanan Anda akan segera dikirim ke: {alamat}")

    # Upload Bukti Transfer
    st.markdown("### 📤 Upload Bukti Pembayaran")
    bukti = st.file_uploader("Upload gambar bukti transfer", type=["jpg", "png"])
    if bukti is not None:
        st.image(bukti, caption="Bukti Transfer", width=300)

    # Tampilkan QRIS
    st.markdown("### 💳 Pembayaran via QRIS")
    try:
        qris_img = Image.open("qris.png")
        st.image(qris_img, caption="Scan QRIS untuk Pembayaran", width=250)
    except FileNotFoundError:
        st.warning("QRIS image (qris.png) tidak ditemukan.")
else:
    st.write("Keranjang masih kosong.")

# =============================
# GRAFIK PRODUK TERLARIS
# =============================
st.markdown("### 📊 Grafik Produk Terlaris")
produk_names = [p["nama"] for p in produk_list]
penjualan_dummy = [1] * len(produk_list)


fig, ax = plt.subplots()
ax.barh(produk_names, penjualan_dummy, color="green")
ax.set_xlabel("Jumlah Terjual")
st.pyplot(fig)
