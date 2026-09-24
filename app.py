import os
import json
import requests
import pandas as pd
import streamlit as st

# ===========================================================================
# 1. KONFIGURASI HALAMAN & TEMA (KULINER KEKINIAN & CERAH)
# ===========================================================================
st.set_page_config(
    page_title="KawanKuliner — Cek Izin & Pajak",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS: Font Handwriting, Warna Cerah, Layout Ringkas
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Nunito:wght@500;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    
    :root {
        --primary-color: #D84315; 
        --secondary-color: #E67E22; 
        --accent-color: #4A90E2; 
        --bg-light: #FDFBF7; 
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }

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
        font-size: 24px;
        font-weight: 800;
        color: #C0392B;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 13px;
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===========================================================================
# 2. CORE ENGINE: LOGIKA DETERMINISTIK (Food & Beverage Adaptif)
# ===========================================================================
class SymbolicRuleEngine:
    @staticmethod
    def evaluate(profil: dict) -> dict:
        model_usaha = profil["model_usaha"]
        bentuk_usaha = profil["bentuk_usaha"]
        omzet = profil["omzet_tahunan"]
        kemasan = profil["karakteristik_kemasan"]
        bahan = profil["bahan_baku"]
        tipe_bisnis = profil["tipe_bisnis"] # "MAKANAN" atau "MINUMAN"
        
        # 1. KBLI & OSS RBA
        if "Warung Makan" in model_usaha or "Resto" in model_usaha:
            kbli = {"kode": "56101 / 56102", "nama": "Restoran / Warung Makan", "risiko": "Rendah", "izin": "NIB Saja"}
        elif "Kedai Minuman" in model_usaha or "Kopi" in model_usaha:
            kbli = {"kode": "56303", "nama": "Rumah Minum / Kedai Minuman", "risiko": "Rendah", "izin": "NIB Saja"}
        elif "Jasa Boga" in model_usaha or "Katering" in model_usaha:
            kbli = {"kode": "56210", "nama": "Jasa Boga / Katering", "risiko": "Menengah Rendah", "izin": "NIB + SLHS"}
        elif "Produksi Makanan" in model_usaha:
            kbli = {"kode": "10799", "nama": "Industri Produk Makanan Lainnya", "risiko": "Rendah", "izin": "NIB + P-IRT"}
        else: # Produksi Minuman
            kbli = {"kode": "11040", "nama": "Industri Minuman Ringan", "risiko": "Rendah/Menengah", "izin": "NIB + Izin Edar"}

        # 2. PAJAK UMKM (PP 20/2026)
        ptkp = 500_000_000
        tarif = 0.005
        if "Perorangan" in bentuk_usaha:
            dpp = max(0, omzet - ptkp)
            status = "Bebas Pajak (Omzet < 500 Juta)" if dpp == 0 else "Kena PPh 0.5% (Atas sisa omzet)"
        else:
            dpp = omzet
            status = "Kena PPh 0,5% Flat"
        tax = {"omzet": omzet, "dpp": dpp, "pph_terutang": int(dpp * tarif), "status": status}

        # 3. IZIN EDAR PANGAN
        if "Siap konsumsi" in kemasan or "Gelas/Cup" in kemasan:
            food_safety = {"jenis": "SLHS (Higiene Sanitasi)", "instansi": "Dinkes", "info": "Cek kebersihan tempat saji, tidak butuh izin edar label."}
        elif "Kering" in kemasan or "Serbuk" in kemasan:
            food_safety = {"jenis": "Nomor P-IRT", "instansi": "Dinkes via OSS", "info": "Cocok untuk produk kering yang awet di suhu ruang."}
        else:
            # Frozen food, Daging, Susu botol cair, dll (Risiko tinggi)
            food_safety = {"jenis": "Izin BPOM MD", "instansi": "BPOM RI", "info": "Wajib BPOM karena produk basah/cair berisiko tinggi (mudah basi)."}

        # 4. SERTIFIKASI HALAL
        # Cek jika bahan berisiko (Daging non-RPH atau Susu cair)
        is_risiko_tinggi = ("tanpa sertifikat RPH" in bahan.lower()) or ("susu hewani cair" in bahan.lower())
        
        if not is_risiko_tinggi and omzet <= ptkp:
            halal = {"jalur": "SEHATI (Self Declare)", "biaya": "Gratis (Rp 0)", "info": "Dapat subsidi pemerintah untuk UMKM Mikro."}
        else:
            halal = {"jalur": "Jalur Reguler", "biaya": "Berbayar", "info": "Harus diaudit LPH karena bahan baku/omzet."}

        return {"profil": profil, "kbli": kbli, "tax": tax, "food_safety": food_safety, "halal": halal}

# ===========================================================================
# 3. CONSUMER REPHRASER: KONSULTAN VIRTUAL UMKM
# ===========================================================================
class EducationalScaffolder:
    @staticmethod
    def get_local_scaffolding(res: dict) -> str:
        p, k, t, f, h = res['profil'], res['kbli'], res['tax'], res['food_safety'], res['halal']
        
        if t["pph_terutang"] == 0:
            tax_text = f"Pemerintah lagi ngasih kado nih! 🎉 Karena omzet setahunmu (Rp {t['omzet']:,}) masih di bawah Rp 500 Juta, kamu **BEBAS PAJAK (Rp 0)**. Uang pajaknya mending diputar lagi buat nambah alat/promosi!"
        else:
            tax_text = f"Laris manis nih usahanya! 🚀 Karena omzetmu (Rp {t['omzet']:,}) udah ngelewatin batas Rp 500 Juta, kamu cuma perlu nyisihin 0,5% dari sisa kelebihannya, yaitu sekitar **Rp {t['pph_terutang']:,} / tahun**."

        return f"""
### 💡 Hasil Pengecekan Bisnis Kamu

Halo **{p['nama_usaha']}**! 👋  
Seneng banget lihat kamu peduli sama legalitas usaha. Ngurus izin jaman *now* itu gampang banget dan bikin pelanggan makin percaya sama produkmu. 

Berikut ringkasan rahasia dapur legalitasmu:

*   📑 **Izin Usaha Dasar:** Usahamu tergolong gampang diurus. Kamu cuma butuh izin **{k['izin']}**.
*   💰 **Pajak UMKM:** {tax_text}
*   🛡️ **Keamanan Produk:** Produkmu butuh izin **{f['jenis']}** yang dikeluarkan oleh {f['instansi']}. {f['info']}
*   🕌 **Sertifikat Halal:** Kamu bisa pakai pendaftaran **{h['jalur']}** ({h['biaya']}).

#### 🚀 Rencana Aksi (Tinggal Jalanin Besok Pagi)

*   <span class="step-number">1</span> **Bikin NIB 15 Menit:** Siapin KTP, buka HP, daftar di **[oss.go.id](https://oss.go.id)**. Gratis dan langsung jadi!
*   <span class="step-number">2</span> **Urus Izin {f['jenis']}:** Hubungi {f['instansi']} setempat atau cek website mereka untuk syarat pendaftarannya.
*   <span class="step-number">3</span> **Daftar Halal:** Buka **[ptsp.halal.go.id](https://ptsp.halal.go.id)**, bikin akun, dan ajukan sertifikasi Halal {h['jalur']}.
"""

# ===========================================================================
# 4. ANTARMUKA UTAMA APLIKASI
# ===========================================================================
with st.sidebar:
    st.caption("KawanKuliner Admin Panel")

st.markdown("""
<div class="main-header">
    <h1>KawanKuliner 🍔🍹</h1>
    <p>Cek Izin & Pajak untuk Warung, Kedai Kopi, Katering, hingga Produk Kemasan. 100% Akurat dengan Aturan Pemerintah!</p>
    <span class="badge-consumer">✨ Gratis • ⚡ Cepat • 💯 Terpercaya</span>
</div>
""", unsafe_allow_html=True)

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
            bentuk_usaha = st.selectbox("Kamu Mendaftar Sebagai:", ["Orang Pribadi (Perorangan) 🙋‍♂️", "Badan Usaha (CV/PT) 🏢"])
            
            # Kategorisasi yang lebih luas mencakup Makanan & Minuman
            model_usaha = st.selectbox("Jenis Bisnismu:", [
                "Warung Makan / Resto / Cafe 🥘", 
                "Kedai Minuman / Kopi / Jus / Boba 🧋", 
                "Jasa Boga / Katering 🍱", 
                "Produksi Makanan/Camilan Kemasan 🍪",
                "Produksi Minuman Botol/Kemasan 🧃"
            ])
            
            # Deteksi Tipe Bisnis (Makanan vs Minuman)
            is_minuman = "Minuman" in model_usaha or "Kopi" in model_usaha or "Jus" in model_usaha

            omzet = st.number_input(
                "Tebakan Omzet (Kotor) dalam 1 Tahun (Rp):",
                min_value=0, max_value=4_800_000_000, value=150_000_000, step=10_000_000, format="%d"
            )
            
            # Pertanyaan adaptif tergantung apakah ini bisnis makanan atau minuman
            st.markdown("---")
            if is_minuman:
                kemasan = st.radio("Bagaimana Minuman Disajikan/Dikemas?", [
                    "Siap minum di Gelas/Cup (Dine-in / Takeaway) 🥤",
                    "Serbuk/Bubuk kering (Kopi bubuk, Teh seduh) ☕",
                    "Cair di Botol Kemasan awet (Susu botol, Kopi literan botol) 🧃"
                ])
                bahan = st.radio("Bahan Baku Minuman:", [
                    "100% Nabati (Kopi, Teh, Buah) / Sirup berlogo Halal 🍋",
                    "Menggunakan Susu Hewani Cair / Bahan import tanpa logo halal 🥛"
                ])
            else:
                kemasan = st.radio("Bagaimana Makanan Disajikan/Dikemas?", [
                    "Siap konsumsi, dimakan hari itu juga (Piring/Bungkus) 🍝",
                    "Kemasan kering awet >7 hari (Kue kering, Keripik, Abon) 🥨",
                    "Frozen food / Olahan daging basah / Kalengan 🥟"
                ])
                bahan = st.radio("Bahan Baku Makanan:", [
                    "Bahan alami sayur/buah atau bumbu kemasan berlogo Halal 🥬",
                    "Menyembelih ayam/daging sendiri tanpa sertifikat RPH 🥩"
                ])
            
            btn_diagnosa = st.form_submit_button("✨ Cek Izin Sekarang ✨", use_container_width=True)

    with col_result:
        profil_data = {
            "nama_usaha": nama_usaha, 
            "bentuk_usaha": bentuk_usaha, 
            "model_usaha": model_usaha, 
            "omzet_tahunan": omzet, 
            "karakteristik_kemasan": kemasan, 
            "bahan_baku": bahan,
            "tipe_bisnis": "MINUMAN" if is_minuman else "MAKANAN"
        }
        eval_result = SymbolicRuleEngine.evaluate(profil_data)
        
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.markdown(f'<div class="card-result"><div class="metric-label">Izin Dasar</div><div class="metric-value">{eval_result["kbli"]["izin"].split(" ")[0]}</div><small>{eval_result["kbli"]["izin"]}</small></div>', unsafe_allow_html=True)
        with mcol2:
            st.markdown(f'<div class="card-result"><div class="metric-label">Pajak Tahunan</div><div class="metric-value">Rp {eval_result["tax"]["pph_terutang"]:,}</div><small>{"Bebas Pajak! 🎉" if eval_result["tax"]["pph_terutang"]==0 else "Tarif 0.5%"}</small></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="card-result"><div class="metric-label">Jalur Halal</div><div class="metric-value">{eval_result["halal"]["jalur"].split(" ")[0]}</div><small>{eval_result["halal"]["biaya"]}</small></div>', unsafe_allow_html=True)

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
