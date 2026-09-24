import os
import json
import requests
import pandas as pd
import streamlit as st

# ===========================================================================
# 1. KONFIGURASI HALAMAN & TEMA (KULINER KEKINIAN & CERAH)
# ===========================================================================
st.set_page_config(
    page_title="UMKMGPT — Cek Izin Kuliner",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS: Font Handwriting (Caveat & Nunito), Warna Cerah, Layout Ringkas
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Nunito:wght@500;700;800&display=swap');

    /* Terapkan font ke seluruh aplikasi */
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }
    
    :root {
        --primary-color: #D84315; /* Terracotta / Merah Bata Muted */
        --secondary-color: #E67E22; /* Karamel / Coklat Muda */
        --accent-color: #4A90E2; /* Biru Kalem */
        --bg-light: #FDFBF7; /* Krem Kopi Sangat Lembut */
    }
    
    /* Bikin layout lebih ringkas / padding dikecilkan */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    .main-header {
        background: linear-gradient(135deg, #C0392B 0%, #D35400 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 6px 15px rgba(192, 57, 43, 0.2);
        text-align: center;
    }
    .main-header h1 {
        font-family: 'Caveat', cursive;
        color: #FFFFFF !important;
        font-size: 52px;
        font-weight: 700;
        margin-bottom: 0px;
        line-height: 1.1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
    }
    .main-header p {
        color: #FFE6D5 !important;
        font-size: 17px;
        font-weight: 700;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    .badge-consumer {
        background-color: #FFFFFF;
        color: #C0392B;
        font-size: 13px;
        font-weight: 800;
        padding: 6px 15px;
        border-radius: 30px;
        display: inline-block;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    .card-result {
        background-color: #FFFFFF;
        border: 2px dashed #D35400;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .card-result:hover {
        transform: scale(1.02);
        background-color: #FDFBF7;
    }
    .metric-value {
        font-family: 'Nunito', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: #C0392B;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 14px;
        color: #777777;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .pedagogical-box {
        background-color: #FDFBF7;
        border-left: 6px solid #C0392B;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(192, 57, 43, 0.08);
        margin: 15px 0;
        color: #4A4A4A;
    }
    .step-number {
        display: inline-block;
        width: 26px;
        height: 26px;
        background-color: #D35400;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 26px;
        font-weight: 800;
        margin-right: 8px;
    }
    
    /* Sembunyikan elemen bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===========================================================================
# 2. CORE ENGINE: LOGIKA DETERMINISTIK (Tidak terlihat oleh pengguna)
# ===========================================================================
class SymbolicRuleEngine:
    @staticmethod
    def evaluate(profil: dict) -> dict:
        model_usaha = profil["model_usaha"]
        bentuk_usaha = profil["bentuk_usaha"]
        omzet = profil["omzet_tahunan"]
        kemasan = profil["karakteristik_kemasan"]
        bahan = profil["bahan_baku"]
        
        # 1. KBLI & OSS RBA
        if "Warung" in model_usaha or "Resto" in model_usaha:
            kbli = {"kode": "56102 / 56101", "nama": "Restoran / Warung Makan", "risiko": "Rendah", "izin": "NIB Saja (Langsung Jadi)"}
        elif "Kopi" in model_usaha or "Jus" in model_usaha:
            kbli = {"kode": "56303", "nama": "Kedai Minuman", "risiko": "Rendah", "izin": "NIB Saja (Langsung Jadi)"}
        elif "Katering" in model_usaha or "Jasa Boga" in model_usaha:
            kbli = {"kode": "56210", "nama": "Jasa Boga / Katering", "risiko": "Menengah Rendah", "izin": "NIB + Sertifikat SLHS"}
        else:
            kbli = {"kode": "10799", "nama": "Produksi Makanan Lainnya", "risiko": "Rendah", "izin": "NIB + Izin P-IRT"}

        # 2. PAJAK UMKM (PP 20/2026)
        ptkp = 500_000_000
        tarif = 0.005
        
        if "Perorangan" in bentuk_usaha:
            dpp = max(0, omzet - ptkp)
            status = "Hore! Omzet di bawah 500 Juta." if dpp == 0 else "Kena Pajak PPh 0.5% (atas sisa omzet)"
        else:
            dpp = omzet
            status = "Kena Pajak PPh 0,5% Flat"
            
        pph = int(dpp * tarif)
        tax = {"omzet": omzet, "dpp": dpp, "pph_terutang": pph, "status": status}

        # 3. IZIN EDAR PANGAN
        if "Siap saji" in kemasan:
            food_safety = {"jenis": "Izin SLHS / Higiene Sanitasi", "instansi": "Puskesmas / Dinkes", "info": "Cek kebersihan dapur."}
        elif ">7 hari" in kemasan:
            food_safety = {"jenis": "Nomor P-IRT", "instansi": "Dinkes via OSS", "info": "Izin edar produk kemasan rumahan."}
        else:
            food_safety = {"jenis": "Izin BPOM MD", "instansi": "BPOM RI", "info": "Wajib BPOM karena berisiko tinggi."}

        # 4. SERTIFIKASI HALAL
        if "Bahan alami" in bahan and omzet <= ptkp:
            halal = {"jalur": "Jalur SEHATI (Gratis)", "biaya": "Rp 0", "info": "Pakai jalur Self-Declare."}
        else:
            halal = {"jalur": "Jalur Reguler", "biaya": "Berbayar", "info": "Perlu audit LPH."}

        return {"profil": profil, "kbli": kbli, "tax": tax, "food_safety": food_safety, "halal": halal}

# ===========================================================================
# 3. CONSUMER REPHRASER: KONSULTAN VIRTUAL UMKM
# ===========================================================================
class EducationalScaffolder:
    @staticmethod
    def get_local_scaffolding(res: dict) -> str:
        p, k, t, f, h = res['profil'], res['kbli'], res['tax'], res['food_safety'], res['halal']
        
        if t["pph_terutang"] == 0:
            tax_text = f"Pemerintah lagi ngasih kado nih! 🎉 Karena omzet setahunmu (Rp {t['omzet']:,}) masih di bawah Rp 500 Juta, kamu **BEBAS PAJAK (Rp 0)**. Uangnya mending diputar lagi buat nambah menu atau promosi!"
        else:
            tax_text = f"Laris manis nih usahanya! 🍜 Karena omzetmu (Rp {t['omzet']:,}) udah ngelewatin batas Rp 500 Juta, kamu cuma perlu nyisihin 0,5% dari sisa kelebihannya, yaitu sekitar **Rp {t['pph_terutang']:,} / tahun**. Semangat terus bayar pajaknya!"

        return f"""
### 💡 Hasil Pengecekan Usaha Kamu

Halo **{p['nama_usaha']}**! 🧑‍🍳👩‍🍳  
Wah, seneng banget lihat kamu peduli sama legalitas usaha. Ngurus izin jaman *now* itu gampang banget dan bikin pelanggan makin percaya sama kualitas makananmu. 

Berikut ringkasan rahasia dapur legalitasmu:

*   📑 **Izin Jualan:** Usahamu tergolong gampang diurus. Kamu cuma butuh **{k['izin']}**.
*   💰 **Pajak UMKM:** {tax_text}
*   🛡️ **Izin Edar:** Makanan/minumanmu butuh **{f['jenis']}** dari {f['instansi']}.
*   🕌 **Sertifikat Halal:** Kamu bisa pakai **{h['jalur']}** ({h['biaya']}).

#### 🚀 Apa yang Harus Dilakukan Besok? (Gak Pake Ribet)

*   <span class="step-number">1</span> **Bikin NIB 15 Menit:** Siapin KTP, buka HP, daftar di **[oss.go.id](https://oss.go.id)**. Gratis dan langsung jadi!
*   <span class="step-number">2</span> **Urus Keamanan Makanan:** Mampir ke Dinkes/Puskesmas buat tanya syarat dapet **{f['jenis']}**.
*   <span class="step-number">3</span> **Daftar Halal:** Buka **[ptsp.halal.go.id](https://ptsp.halal.go.id)** dan bikin akun.
"""

# ===========================================================================
# 4. ANTARMUKA UTAMA APLIKASI
# ===========================================================================

# Sidebar disembunyikan
with st.sidebar:
    st.caption("UMKMGPT Admin Panel")

# Header Utama yang Super Catchy
st.markdown("""
<div class="main-header">
    <h1>Cek Izin & Pajak Kuliner 🍔🍹</h1>
    <p>Bantu Warung, Cafe, & Katering tau izin apa aja yang dibutuhin biar jualan makin tenang & laris manis!</p>
    <span class="badge-consumer">✨ Gratis • ⚡ Cepat • 💯 Akurat</span>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs([
    "📝 1. Cek Kebutuhan Izin",
    "📈 2. Simulasi Bebas Pajak"
])

with tab1:
    col_input, col_result = st.columns([1, 1.4], gap="medium")
    
    with col_input:
        st.markdown("#### 🛒 Ceritain Soal Usahamu")
        
        with st.form("form_compliance"):
            nama_usaha = st.text_input("Nama Usaha Kulinermu:", value="Kedai Kopi Senja ☕")
            bentuk_usaha = st.selectbox("Bentuk Usaha:", ["Orang Pribadi (Perorangan) 🙋‍♂️", "Badan Usaha (CV/PT) 🏢"])
            model_usaha = st.selectbox("Jualan Apa Nih?:", ["Kedai Minuman / Kopi / Jus 🧋", "Warung Makan / Resto / Cafe 🥘", "Jasa Boga / Katering 🍱", "Makanan Kemasan (Keripik/Kue) 🍪"])
            
            omzet = st.number_input(
                "Tebakan Omzet (Kotor) dalam 1 Tahun (Rp):",
                min_value=0, max_value=4_800_000_000, value=150_000_000, step=10_000_000, format="%d"
            )
            
            kemasan = st.radio("Sifat Makanannya:", [
                "Siap saji, dimakan hari itu juga 🍝",
                "Kemasan kering awet >7 hari (kue/keripik) 🥨",
                "Frozen food / olahan daging / susu cair 🥟"
            ])
            
            bahan = st.radio("Bahan Bakunya:", [
                "Bahan alami (sayur/buah) atau bumbu kemasan berlogo Halal 🥬",
                "Sembelih ayam/daging sendiri tanpa sertifikat RPH 🥩"
            ])
            
            # Tombol dengan styling native tapi full width
            btn_diagnosa = st.form_submit_button("✨ Cek Sekarang ✨", use_container_width=True)

    with col_result:
        profil_data = {
            "nama_usaha": nama_usaha, "bentuk_usaha": bentuk_usaha, 
            "model_usaha": model_usaha, "omzet_tahunan": omzet, 
            "karakteristik_kemasan": kemasan, "bahan_baku": bahan
        }
        eval_result = SymbolicRuleEngine.evaluate(profil_data)
        
        # Metric Cards (Ringkasan instan dengan bentuk dashed border fun)
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.markdown(f'<div class="card-result"><div class="metric-label">Perizinan Dasar</div><div class="metric-value">{eval_result["kbli"]["izin"].split(" ")[0]}</div><small>{eval_result["kbli"]["izin"].replace("NIB Saja ", "")}</small></div>', unsafe_allow_html=True)
        with mcol2:
            st.markdown(f'<div class="card-result"><div class="metric-label">Pajak Per Tahun</div><div class="metric-value">Rp {eval_result["tax"]["pph_terutang"]:,}</div><small>{"Bebas Pajak! 🎉" if eval_result["tax"]["pph_terutang"]==0 else "Tarif 0.5%"}</small></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="card-result"><div class="metric-label">Jalur Halal</div><div class="metric-value">{eval_result["halal"]["jalur"].split(" ")[1] if " " in eval_result["halal"]["jalur"] else eval_result["halal"]["jalur"]}</div><small>{eval_result["halal"]["biaya"]}</small></div>', unsafe_allow_html=True)

        st.markdown('<div class="pedagogical-box">', unsafe_allow_html=True)
        ai_text = EducationalScaffolder.get_local_scaffolding(eval_result)
        st.markdown(ai_text, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.download_button("📥 Simpan Panduan Ini (.md)", data=ai_text, file_name=f"Panduan_Asik_{nama_usaha.split(' ')[0]}.md", mime="text/markdown", use_container_width=True)

with tab2:
    st.markdown("### 🧮 Benarkah Usaha Kecil Bebas Pajak?")
    st.caption("Cobain geser slider di bawah buat buktiin kalau omzet di bawah 500 Juta itu beneran nggak bayar pajak buat perorangan!")
    
    scol1, scol2 = st.columns([1.2, 2.5], gap="medium")
    
    with scol1:
        sim_bentuk = st.radio("Kamu daftar sebagai:", ["Orang Pribadi (Perorangan) 🙋‍♂️", "Badan Usaha (CV/PT) 🏢"], key="sim_bentuk")
        sim_omzet = st.slider("Coba Geser Omzetmu:", 0, 1500, 250, 50, format="%d Juta") * 1_000_000
        
        sim_dpp = max(0, sim_omzet - 500_000_000) if "Perorangan" in sim_bentuk else sim_omzet
        sim_pph = int(sim_dpp * 0.005)
        
        st.markdown(f"<div style='background-color: #FDFBF7; padding: 15px; border-radius: 10px; border: 2px dashed #D35400; text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin:0; color: #777; font-weight: 800;'>Uang Kena Pajak: Rp {sim_dpp:,.0f}</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#C0392B; margin: 5px 0 0 0;'>Pajaknya:<br/>Rp {sim_pph:,.0f}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with scol2:
        omzet_range = list(range(0, 1500_000_000 + 1, 100_000_000))
        tax_data = []
        for o in omzet_range:
            if "Perorangan" in sim_bentuk:
                t = max(0, o - 500_000_000) * 0.005
            else:
                t = o * 0.005
            tax_data.append({"OmzetTahunan": o, "PajakTerutang": t})
            
        df = pd.DataFrame(tax_data)
        df.set_index("OmzetTahunan", inplace=True)
        
        st.line_chart(df, y="PajakTerutang", color="#C0392B")
        if "Perorangan" in sim_bentuk:
            st.info("💡 **Liat Garis Datarnya!** Selama omzetmu belum nabrak Rp 500 Juta, garis pajaknya anteng di angka 0. Enak banget kan?")
        else:
            st.warning("⚠️ **Garis Langsung Naik!** Karena CV/PT udah level badan usaha, pemerintah nggak ngasih diskon 500 Juta. Pajak 0,5% langsung jalan dari omzet pertama.")
