import os
import json
import requests
import pandas as pd
import streamlit as st

# ===========================================================================
# 1. KONFIGURASI HALAMAN & TEMA (CONSUMER-FRIENDLY UI)
# ===========================================================================
st.set_page_config(
    page_title="UMKMGPT — Asisten Legalitas & Pajak UMKM F&B",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="collapsed" # Sengaja disembunyikan agar pengguna fokus ke layar utama
)

# Custom CSS untuk UI/UX startup/consumer app yang ramah
st.markdown("""
<style>
    :root {
        --primary-color: #0F6E6A;
        --secondary-color: #158F8A;
        --accent-color: #B4690E;
        --bg-light: #F8F9FA;
    }
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(15, 110, 106, 0.2);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #E8F2F0 !important;
        font-size: 16px;
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .badge-consumer {
        background-color: #FCEDDB;
        color: var(--accent-color);
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        border: 1px solid #E0A96D;
    }
    .card-result {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-top: 4px solid var(--primary-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }
    .card-result:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: var(--primary-color);
        margin: 5px 0;
    }
    .metric-label {
        font-size: 13px;
        color: #555555;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .pedagogical-box {
        background-color: #FFFFFF;
        border-left: 5px solid var(--accent-color);
        padding: 20px;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 20px 0;
    }
    .step-number {
        display: inline-block;
        width: 28px;
        height: 28px;
        background-color: var(--primary-color);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-weight: bold;
        margin-right: 10px;
    }
    /* Menyembunyikan elemen footer bawaan Streamlit agar terlihat seperti app profesional */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
        if "Warung Makan" in model_usaha or "Resto" in model_usaha:
            kbli = {"kode": "56102 / 56101", "nama": "Penyediaan Makanan / Restoran", "risiko": "Rendah", "izin": "NIB Berlaku Langsung"}
        elif "Kopi" in model_usaha or "Minuman" in model_usaha:
            kbli = {"kode": "56303", "nama": "Kedai Minuman / Kopi", "risiko": "Rendah", "izin": "NIB Berlaku Langsung"}
        elif "Katering" in model_usaha or "Jasa Boga" in model_usaha:
            kbli = {"kode": "56210", "nama": "Jasa Boga untuk Event Tertentu", "risiko": "Menengah Rendah", "izin": "NIB + Sertifikat Standar (SLHS)"}
        else:
            kbli = {"kode": "10799", "nama": "Industri Produk Makanan Lainnya", "risiko": "Rendah (Mikro)", "izin": "NIB + Izin Edar P-IRT"}

        # 2. PAJAK UMKM (PP 20/2026)
        ptkp = 500_000_000
        tarif = 0.005
        
        if "Orang Pribadi" in bentuk_usaha:
            dpp = max(0, omzet - ptkp)
            status = "Bebas Pajak (Fasilitas PTKP)" if dpp == 0 else "Kena Pajak PPh Final atas Selisih"
        else:
            dpp = omzet
            status = "Kena Pajak PPh Final 0,5% Flat (Tanpa PTKP)"
            
        pph = int(dpp * tarif)
        tax = {"omzet": omzet, "dpp": dpp, "pph_terutang": pph, "status": status}

        # 3. IZIN EDAR PANGAN
        if "Siap saji" in kemasan:
            food_safety = {"jenis": "SLHS (Laik Higiene Sanitasi)", "instansi": "Dinas Kesehatan", "info": "Fokus pada sanitasi dapur."}
        elif ">7 hari" in kemasan:
            food_safety = {"jenis": "SPP-PIRT", "instansi": "Dinas Kesehatan", "info": "Pangan olahan kering rumah tangga."}
        else:
            food_safety = {"jenis": "Izin Edar BPOM MD", "instansi": "BPOM RI", "info": "Pangan berisiko tinggi (frozen food/susu)."}

        # 4. SERTIFIKASI HALAL
        if "100% Nabati" in bahan and omzet <= ptkp:
            halal = {"jalur": "SEHATI (Self Declare)", "biaya": "Rp 0 (Gratis)", "info": "Sertifikasi bersubsidi untuk usaha mikro."}
        else:
            halal = {"jalur": "Reguler (Audit LPH)", "biaya": "Berbayar (PNBP)", "info": "Perlu audit karena bahan kritis atau skala usaha."}

        return {"profil": profil, "kbli": kbli, "tax": tax, "food_safety": food_safety, "halal": halal}

# ===========================================================================
# 3. CONSUMER REPHRASER: KONSULTAN VIRTUAL UMKM
# ===========================================================================
class EducationalScaffolder:
    @staticmethod
    def call_gemini_api(eval_res: dict, api_key: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = f"""
        Anda adalah asisten konsultan bisnis yang ramah untuk pemilik UMKM F&B di Indonesia.
        Jelaskan poin-poin berikut dengan bahasa yang sangat mudah dimengerti, memotivasi, dan tidak mengintimidasi.
        
        FAKTA YANG HARUS DIJELASKAN SECARA AKURAT (JANGAN UBAH ANGKA):
        - Nama Usaha: {eval_res['profil']['nama_usaha']} ({eval_res['profil']['bentuk_usaha']})
        - Izin Berusaha: Anda hanya perlu mengurus {eval_res['kbli']['izin']} (KBLI {eval_res['kbli']['kode']} - Risiko {eval_res['kbli']['risiko']}).
        - Pajak: Omzet Rp {eval_res['tax']['omzet']:,}. Beban Pajak Anda adalah Rp {eval_res['tax']['pph_terutang']:,} per tahun. ({eval_res['tax']['status']}).
        - Keamanan Pangan: Urus izin {eval_res['food_safety']['jenis']} di {eval_res['food_safety']['instansi']}.
        - Sertifikasi Halal: Anda masuk jalur {eval_res['halal']['jalur']} ({eval_res['halal']['biaya']}).

        Berikan "Rencana Aksi 3 Hari ke Depan" yang praktis agar mereka tahu apa yang harus dikerjakan besok pagi. Gunakan Markdown dan Emoji.
        """
        try:
            response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"}, timeout=10)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return EducationalScaffolder.get_local_scaffolding(eval_res)

    @staticmethod
    def get_local_scaffolding(res: dict) -> str:
        p, k, t, f, h = res['profil'], res['kbli'], res['tax'], res['food_safety'], res['halal']
        
        if t["pph_terutang"] == 0:
            tax_text = f"Kabar Gembira! Berdasarkan aturan terbaru, karena omzet Anda (Rp {t['omzet']:,}) di bawah batas Rp 500 juta, Anda berhak menikmati fasilitas **Bebas Pajak (Rp 0)**! Putar terus modal Anda untuk membesarkan bisnis."
        else:
            tax_text = f"Bisnis Anda berkembang luar biasa! Omzet Anda (Rp {t['omzet']:,}) telah menembus batas Rp 500 juta. Anda cukup membayar pajak 0,5% dari selisihnya, yakni **Rp {t['pph_terutang']:,} per tahun**. Kontribusi hebat untuk kemajuan bersama!"

        return f"""
### 💡 Hasil Analisis & Panduan Legalitas Anda

Halo Kak Pengelola **{p['nama_usaha']}**! 
Terima kasih sudah peduli dengan legalitas usaha. Mengurus perizinan itu tidak seseram yang dibayangkan kok! Justru ini adalah tiket emas untuk mendapat modal usaha (KUR), kemitraan, dan menumbuhkan rasa percaya dari pelanggan Anda.

Berikut adalah ringkasan khusus untuk bisnis Anda:

#### 📊 1. Ringkasan Status Usaha
*   **Izin Berusaha:** Bisnis Anda tergolong aman (Risiko {k['risiko']}). Anda cukup mengurus **{k['izin']}** secara online.
*   **Perhitungan Pajak:** {tax_text}
*   **Keamanan Pangan:** Jenis produk Anda mewajibkan Anda memiliki **{f['jenis']}** dari {f['instansi']}.
*   **Sertifikat Halal:** Kabar baik, Anda bisa mendaftar melalui jalur **{h['jalur']}** ({h['biaya']}).

#### 🚀 2. Rencana Aksi (Apa yang harus dilakukan besok?)
Mari kita selesaikan perlahan agar tidak pusing:

*   <span class="step-number">1</span> **Langkah 1 (Selesaikan Hari Ini): Buat Akun OSS**  
    Siapkan KTP, buka situs resmi **[oss.go.id](https://oss.go.id)**. Daftar akun baru, dan NIB Anda akan terbit gratis secara instan dalam 15 menit. NIB ini adalah "KTP" bagi usaha Anda.
*   <span class="step-number">2</span> **Langkah 2: Urus Keamanan Pangan**  
    Kunjungi kantor kecamatan / Puskesmas terdekat untuk mencari info pengurusan pendaftaran {f['jenis']}. {f['info']}
*   <span class="step-number">3</span> **Langkah 3: Daftar Halal**  
    Jika NIB sudah di tangan, buka **[ptsp.halal.go.id](https://ptsp.halal.go.id)**. Ajukan pendaftaran dengan jalur {h['jalur']} dan cari pendamping PPH terdekat di daerah Anda.
"""

# ===========================================================================
# 4. ANTARMUKA UTAMA APLIKASI (TANPA IDENTITAS PENELITI)
# ===========================================================================

# Sidebar disembunyikan secara default, hanya menyimpan opsi rahasia untuk admin/API
with st.sidebar:
    st.image("https://img.icons8.com/color/120/000000/shop.png", width=70)
    st.markdown("### UMKMGPT Admin Panel")
    api_key_input = st.text_input(
        "Koneksi AI (Opsional):",
        type="password",
        help="Kosongkan saja untuk pemakaian normal (Offline Mode). Khusus untuk admin jika ingin mengaktifkan Neural Engine via API."
    )

# Header Utama (Consumer-Facing)
st.markdown("""
<div class="main-header">
    <h1>UMKMGPT: Cek Izin & Pajak Kuliner 👩‍🍳</h1>
    <p>Aplikasi gratis untuk membantu pemilik Warung, Cafe, dan Katering mengetahui persis Izin Usaha, Pajak, dan Jalur Halal apa yang cocok untuk bisnisnya dalam 1 menit.</p>
    <span class="badge-consumer">Cepat • Akurat • Sesuai Aturan Pemerintah Terbaru</span>
</div>
""", unsafe_allow_html=True)

# Tabs Navigasi (Hanya fitur fungsional, hilangkan metodologi riset)
tab1, tab2 = st.tabs([
    "🧭 1. Cek Kebutuhan Izin Usaha Saya",
    "🧮 2. Simulasi Bebas Pajak 500 Juta"
])

# ── TAB 1: DIAGNOSIS KEPATUHAN USAHA ──────────────────────────────────────
with tab1:
    col_input, col_result = st.columns([1, 1.4], gap="large")
    
    with col_input:
        st.subheader("📝 Masukkan Data Usaha Anda")
        st.caption("Data ini tidak kami simpan, hanya untuk kalkulasi otomatis.")
        
        with st.form("form_compliance"):
            nama_usaha = st.text_input("Nama Usaha Kuliner Anda:", value="Dapur Bu Asih")
            bentuk_usaha = st.selectbox("Bentuk Usaha:", ["Orang Pribadi (WPOP/Perorangan)", "Badan Usaha (CV/PT/Koperasi)"])
            model_usaha = st.selectbox("Kategori Bisnis Utama:", ["Kedai Minuman / Kopi / Jus", "Warung Makan / Resto / Cafe", "Jasa Boga / Katering Porsi Besar", "Produksi Makanan Kemasan Awet"])
            
            omzet = st.number_input(
                "Perkiraan Omzet (Pendapatan Kotor) dalam 1 Tahun (Rp):",
                min_value=0, max_value=4_800_000_000, value=250_000_000, step=50_000_000, format="%d"
            )
            
            kemasan = st.radio("Jenis Makanan yang Dijual:", [
                "Siap saji, dimakan hari itu juga (nasi bungkus, es teh, dll)",
                "Kemasan kering tahan lebih dari 7 hari (kue kering, keripik, abon)",
                "Olahan beku (frozen food) / daging kemasan / susu cair"
            ])
            
            bahan = st.radio("Bahan Baku Utama:", [
                "Bahan alami (sayur/buah) atau bahan kemasan yang sudah ada logo Halal",
                "Saya menyembelih ayam/daging sendiri tanpa sertifikat potong hewan"
            ])
            
            btn_diagnosa = st.form_submit_button("🔍 Cek Sekarang", use_container_width=True)

    with col_result:
        profil_data = {
            "nama_usaha": nama_usaha, "bentuk_usaha": bentuk_usaha, 
            "model_usaha": model_usaha, "omzet_tahunan": omzet, 
            "karakteristik_kemasan": kemasan, "bahan_baku": bahan
        }
        eval_result = SymbolicRuleEngine.evaluate(profil_data)
        
        st.subheader("🎯 Ringkasan Status Bisnis Anda")
        
        # Metric Cards (Ringkasan instan)
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.markdown(f'<div class="card-result"><div class="metric-label">Perizinan Dasar</div><div class="metric-value" style="font-size:20px;">{eval_result["kbli"]["izin"].split(" ")[0]}</div><small>{eval_result["kbli"]["risiko"]}</small></div>', unsafe_allow_html=True)
        with mcol2:
            st.markdown(f'<div class="card-result"><div class="metric-label">Pajak Per Tahun</div><div class="metric-value" style="font-size:20px;">Rp {eval_result["tax"]["pph_terutang"]:,}</div><small>{"Bebas Pajak! 🎉" if eval_result["tax"]["pph_terutang"]==0 else "Tarif UMKM 0.5%"}</small></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="card-result"><div class="metric-label">Status Halal</div><div class="metric-value" style="font-size:20px;">{eval_result["halal"]["jalur"].split(" ")[0]}</div><small>{eval_result["halal"]["biaya"]}</small></div>', unsafe_allow_html=True)

        st.markdown("### 💬 Arahan Spesifik untuk Anda")
        with st.container():
            st.markdown('<div class="pedagogical-box">', unsafe_allow_html=True)
            if api_key_input:
                with st.spinner("Sedang merumuskan saran terbaik untuk Anda..."):
                    ai_text = EducationalScaffolder.call_gemini_api(eval_result, api_key_input)
            else:
                ai_text = EducationalScaffolder.get_local_scaffolding(eval_result)
            
            st.markdown(ai_text, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.download_button("📥 Unduh Rencana Aksi Saya (.md)", data=ai_text, file_name=f"Panduan_Legalitas_{nama_usaha}.md", mime="text/markdown", use_container_width=True)

# ── TAB 2: SIMULATOR PAJAK INTERAKTIF ─────────────────────────────────────
with tab2:
    st.subheader("🧮 Benarkah UMKM Bebas Pajak? Cek di sini!")
    st.caption("Geser slider omzet di bawah ini untuk melihat apakah Anda wajib bayar pajak atau masuk kategori bebas pajak.")
    
    scol1, scol2 = st.columns([1, 2.5])
    
    with scol1:
        st.markdown("#### Kondisi Usaha Anda")
        sim_bentuk = st.radio("Anda Mendaftar Sebagai:", ["Orang Pribadi (Perorangan)", "Badan Usaha (CV/PT)"], key="sim_bentuk")
        sim_omzet = st.slider("Omzet (Pendapatan) Tahunan Anda:", 0, 1500, 300, 50, format="%d Juta") * 1_000_000
        
        sim_dpp = max(0, sim_omzet - 500_000_000) if "Orang Pribadi" in sim_bentuk else sim_omzet
        sim_pph = int(sim_dpp * 0.005)
        
        st.markdown(f"**Uang Kena Pajak:** Rp {sim_dpp:,.0f}")
        st.markdown(f"<h3 style='color:var(--primary-color)'>Pajak yang Disetor:<br/>Rp {sim_pph:,.0f}</h3>", unsafe_allow_html=True)

    with scol2:
        omzet_range = list(range(0, 1500_000_000 + 1, 100_000_000))
        tax_data = []
        for o in omzet_range:
            if "Orang Pribadi" in sim_bentuk:
                t = max(0, o - 500_000_000) * 0.005
            else:
                t = o * 0.005
            tax_data.append({"OmzetTahunan": o, "PajakTerutang": t})
            
        df = pd.DataFrame(tax_data)
        df.set_index("OmzetTahunan", inplace=True)
        
        st.markdown("#### Grafik Beban Pajak")
        st.line_chart(df, y="PajakTerutang", color="#B4690E")
        if "Orang Pribadi" in sim_bentuk:
            st.info("💡 **Penjelasan:** Lihat garis datar di awal grafik. Jika omzet Anda masih di bawah Rp 500.000.000, pajak Anda adalah 0 Rupiah! Pemerintah memberikan insentif ini khusus untuk pengusaha perorangan.")
        else:
            st.warning("⚠️ **Penjelasan:** Untuk CV atau PT, garis pajak langsung naik sejak awal karena Badan Usaha wajib membayar 0,5% dari semua omzet tanpa potongan Rp 500 juta.")

st.divider()
st.caption("Powered by UMKMGPT — Solusi Pintar Legalitas Bisnis F&B Indonesia")
