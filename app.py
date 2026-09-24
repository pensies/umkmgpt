import os
import json
import requests
import pandas as pd
import streamlit as st

# ===========================================================================
# 1. KONFIGURASI HALAMAN & TEMA (TEAL & MINT ACADEMIC PALETTE)
# ===========================================================================
st.set_page_config(
    page_title="UMKMGPT — Asisten Kepatuhan Regulasi UMKM F&B",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk UI/UX yang mencerminkan aplikasi edukasi premium
st.markdown("""
<style>
    :root {
        --primary-color: #0F6E6A;
        --secondary-color: #158F8A;
        --accent-color: #B4690E;
        --bg-light: #F8F9FA;
        --bg-highlight: #E8F2F0;
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
    .badge-research {
        background-color: #FCEDDB;
        color: var(--accent-color);
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 8px;
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
</style>
""", unsafe_allow_html=True)

# ===========================================================================
# 2. LAPIS SIMBOLIK: MESIN ATURAN DETERMINISTIK (100% BEBAS HALUSINASI)
# Menggunakan pola Object-Oriented untuk modularitas kode riset
# ===========================================================================
class SymbolicRuleEngine:
    @staticmethod
    def evaluate(profil: dict) -> dict:
        """
        Mengeksekusi pohon keputusan deterministik (Symbolic Decision Tree)
        berbasis hukum Indonesia (PP 28/2025, PP 20/2026, Perka BPOM 22/2018, SOP BPJPH).
        """
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
# 3. LAPIS NEURAL: PEDAGOGICAL REPHRASER & EDUCATIONAL SCAFFOLDING
# ===========================================================================
class EducationalScaffolder:
    @staticmethod
    def call_gemini_api(eval_res: dict, api_key: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
        Anda adalah asisten konsultan dan mentor bisnis (berfokus pada Education Informatics) untuk pemilik UMKM F&B Indonesia.
        Gunakan prinsip "Educational Scaffolding":
        1. Kurangi beban kognitif (gunakan poin-poin singkat).
        2. Berikan dorongan motivasi (empatik).
        3. Buat rencana aksi langkah-demi-langkah yang jelas.

        HASIL DETERMINISTIK (WAJIB DIPERTAHANKAN ANGKA & FAKTANYA):
        - Usaha: {eval_res['profil']['nama_usaha']} ({eval_res['profil']['bentuk_usaha']})
        - KBLI: {eval_res['kbli']['kode']} - Risiko {eval_res['kbli']['risiko']} -> Izin: {eval_res['kbli']['izin']}
        - Omzet: Rp {eval_res['tax']['omzet']:,} -> PPh Final: Rp {eval_res['tax']['pph_terutang']:,} ({eval_res['tax']['status']})
        - Keamanan Pangan: {eval_res['food_safety']['jenis']} dari {eval_res['food_safety']['instansi']}
        - Halal: {eval_res['halal']['jalur']} - Biaya: {eval_res['halal']['biaya']}

        Tuliskan panduan edukatif berformat Markdown. Jangan mengubah angka pajak sedikitpun. Beri sapaan, jelaskan mengapa pajaknya segitu (berdasarkan PP 20/2026), lalu beri "Rencana Aksi 3 Hari ke Depan".
        """
        
        try:
            response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"}, timeout=15)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"> ⚠️ **Info:** Tidak dapat menghubungi API Gemini ({e}). Menggunakan *Local Pedagogical Engine*.\n\n" + EducationalScaffolder.get_local_scaffolding(eval_res)

    @staticmethod
    def get_local_scaffolding(res: dict) -> str:
        """Fallback Scaffolding dengan prinsip Education Informatics"""
        p, k, t, f, h = res['profil'], res['kbli'], res['tax'], res['food_safety'], res['halal']
        
        if t["pph_terutang"] == 0:
            tax_text = f"Berdasarkan PP No. 20/2026, karena omzet Anda (Rp {t['omzet']:,}) di bawah batas Rp 500 juta, Anda mendapat subsidi **Bebas Pajak (Rp 0)**! Modal bisa diputar penuh untuk pengembangan."
        else:
            tax_text = f"Hebat! Omzet Anda (Rp {t['omzet']:,}) sudah menembus batas Rp 500 juta. Anda hanya perlu membayar 0,5% dari selisihnya, yakni sebesar **Rp {t['pph_terutang']:,} / tahun**. Ini kontribusi hebat untuk negara!"

        return f"""
### 🎓 Panduan Kepatuhan & Akselerasi Bisnis Anda

Halo Pengelola **{p['nama_usaha']}**! 🎉  
Langkah Anda mencari tahu tentang legalitas menunjukkan kedewasaan berbisnis. Legalitas bukan sekadar "aturan yang memberatkan", melainkan **kunci pembuka akses permodalan, kemitraan, dan kepercayaan pelanggan.**

Dalam pendekatan *Education Informatics*, kami membagi langkah besar menjadi tahap-tahap kecil agar tidak membebani Anda:

#### 📊 1. Ringkasan Posisi Usaha Anda
*   **Identitas KBLI:** {k['kode']} ({k['risiko']}). Cukup gunakan **{k['izin']}**.
*   **Insentif Pajak:** {tax_text}
*   **Standar Pangan:** Anda wajib mengurus **{f['jenis']}** ({f['instansi']}).
*   **Jaminan Halal:** Anda direkomendasikan masuk jalur **{h['jalur']}** ({h['biaya']}).

#### 🚀 2. Rencana Aksi (Action Plan) Terpandu
Mari selesaikan ini selangkah demi selangkah:

*   <span class="step-number">1</span> **Langkah Pertama (Hari Ini): Amankan NIB**  
    Buka situs [oss.go.id](https://oss.go.id) menggunakan NIK Anda. NIB akan terbit dalam waktu kurang dari 30 menit. Ini adalah "KTP" bagi bisnis Anda.
*   <span class="step-number">2</span> **Langkah Kedua: Standar Pangan**  
    Pelajari syarat pengajuan {f['jenis']} di website Dinkes setempat. {f['info']}
*   <span class="step-number">3</span> **Langkah Ketiga: Sertifikasi Halal**  
    Kunjungi [ptsp.halal.go.id](https://ptsp.halal.go.id). Ajukan pendaftaran dengan jalur {h['jalur']}.
"""

# ===========================================================================
# 4. ANTARMUKA STREAMLIT (UI/UX MULTI-TAB)
# ===========================================================================

# Sidebar: Metadata Riset & Pengaturan API
with st.sidebar:
    st.image("https://img.icons8.com/color/120/000000/graduation-cap.png", width=70)
    st.markdown("### 🎓 UMKMGPT Research Lab")
    st.caption("Neuro-Symbolic Legal AI untuk UMKM F&B")
    
    st.divider()
    st.markdown("**Identitas Peneliti (Author):**")
    st.write("👤 **Paulus Pensies Anggoro**")
    st.caption("NIM: 2520101007 | Peminatan: Education Informatics (EI)")
    st.write("👩‍🏫 **Dosen Pembimbing:**")
    st.caption("Dr. Theresia Herlina, S.Kom., M.T")
    st.caption("Magister Teknologi Informasi - Universitas Pradita")
    
    st.divider()
    st.markdown("**⚙️ Engine Configuration:**")
    api_key_input = st.text_input(
        "Gemini API Key (Opsional):",
        type="password",
        help="Masukkan API Key untuk mengaktifkan Neural Rephraser (Gemini 1.5 Pro/Flash). Jika kosong, menggunakan Local Pedagogical Engine bawaan sistem."
    )
    
    st.info("💡 **Mode Aktif:**\n" + ("🟢 Online (Gemini API)" if api_key_input else "🔵 Offline (Local Engine)"))

# Header Utama
st.markdown("""
<div class="main-header">
    <h1>UMKMGPT: Asisten AI Kepatuhan Regulasi UMKM F&B</h1>
    <p>Menggabungkan <b>Kepastian Hukum Deterministik</b> (Zero-Hallucination) dengan <b>Pendekatan Pedagogis</b> (Education Informatics) untuk memandu UMKM Indonesia mematuhi aturan perizinan, pajak, dan keamanan pangan.</p>
    <span class="badge-research">Fokus Lokus: KBLI 56, KBLI 10799, PP 20/2026, Halal BPJPH</span>
</div>
""", unsafe_allow_html=True)

# Tabs Navigasi
tab1, tab2, tab3 = st.tabs([
    "🧭 1. Diagnosis Kepatuhan (Core System)",
    "🧮 2. Simulasi Visual Pajak PP 20/2026",
    "📚 3. Arsitektur Metodologi (Neuro-Symbolic)"
])

# ── TAB 1: DIAGNOSIS KEPATUHAN USAHA ──────────────────────────────────────
with tab1:
    col_input, col_result = st.columns([1, 1.4], gap="large")
    
    with col_input:
        st.subheader("📝 Input Profil Usaha")
        st.caption("Isi form berikut untuk dievaluasi oleh Symbolic Rule Engine:")
        
        with st.form("form_compliance"):
            nama_usaha = st.text_input("Nama Usaha Kuliner:", value="Dapur Oma Serpong")
            bentuk_usaha = st.selectbox("Bentuk Legalitas:", ["Orang Pribadi (WPOP)", "Badan Usaha (CV/PT/Koperasi)"])
            model_usaha = st.selectbox("Kategori Usaha Utama:", ["Kedai Minuman / Kopi", "Warung Makan / Resto", "Jasa Boga / Katering", "Produksi Makanan Kemasan"])
            
            omzet = st.number_input(
                "Estimasi Omzet Kotor (Bruto) Tahunan (Rp):",
                min_value=0, max_value=4_800_000_000, value=400_000_000, step=50_000_000, format="%d"
            )
            
            kemasan = st.radio("Karakteristik Kemasan:", [
                "Siap saji langsung konsumsi (tanpa kemasan awet)",
                "Kemasan kering tahan >7 hari (kue, keripik, abon)",
                "Olahan beku (frozen food) / pangan berisiko (susu cair)"
            ])
            
            bahan = st.radio("Sumber Bahan Baku:", [
                "100% Nabati / Bahan bersertifikat halal resmi",
                "Menggunakan sembelihan hewan mandiri (tanpa sertifikat) / bahan kritis"
            ])
            
            btn_diagnosa = st.form_submit_button("🔍 Analisis Kepatuhan Hukum", use_container_width=True)

    with col_result:
        # Prepare Data & Run Symbolic Engine
        profil_data = {
            "nama_usaha": nama_usaha, "bentuk_usaha": bentuk_usaha, 
            "model_usaha": model_usaha, "omzet_tahunan": omzet, 
            "karakteristik_kemasan": kemasan, "bahan_baku": bahan
        }
        eval_result = SymbolicRuleEngine.evaluate(profil_data)
        
        st.subheader("🎯 Hasil Ekstraksi Hukum (Deterministik)")
        
        # Metric Cards
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.markdown(f'<div class="card-result"><div class="metric-label">Izin Berusaha</div><div class="metric-value" style="font-size:22px;">{eval_result["kbli"]["izin"].split(" ")[0]}</div><small>{eval_result["kbli"]["risiko"]}</small></div>', unsafe_allow_html=True)
        with mcol2:
            st.markdown(f'<div class="card-result"><div class="metric-label">Beban PPh Final</div><div class="metric-value" style="font-size:22px;">Rp {eval_result["tax"]["pph_terutang"]:,}</div><small>{"Bebas Pajak" if eval_result["tax"]["pph_terutang"]==0 else "Kena Pajak 0.5%"}</small></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="card-result"><div class="metric-label">Sertifikasi Halal</div><div class="metric-value" style="font-size:22px;">{eval_result["halal"]["jalur"].split(" ")[0]}</div><small>{eval_result["halal"]["biaya"]}</small></div>', unsafe_allow_html=True)

        st.markdown("### 🎓 Interpretasi Pedagogis (Neural Rephraser)")
        with st.container():
            st.markdown('<div class="pedagogical-box">', unsafe_allow_html=True)
            if api_key_input:
                with st.spinner("Memproses bahasa dengan Gemini AI..."):
                    ai_text = EducationalScaffolder.call_gemini_api(eval_result, api_key_input)
            else:
                ai_text = EducationalScaffolder.get_local_scaffolding(eval_result)
            
            st.markdown(ai_text, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.download_button("📥 Unduh Rencana Aksi (.md)", data=ai_text, file_name=f"Rencana_Aksi_{nama_usaha}.md", mime="text/markdown", use_container_width=True)

# ── TAB 2: SIMULATOR PAJAK INTERAKTIF ─────────────────────────────────────
with tab2:
    st.subheader("🧮 Simulator Visual Pajak UMKM (PP No. 20/2026)")
    st.caption("Visualisasi pembebasan pajak hingga omzet Rp 500 juta khusus untuk Wajib Pajak Orang Pribadi.")
    
    scol1, scol2 = st.columns([1, 2.5])
    
    with scol1:
        st.markdown("#### Parameter Simulasi")
        sim_bentuk = st.radio("Bentuk Entitas:", ["Orang Pribadi (WPOP)", "Badan Usaha (CV/PT)"], key="sim_bentuk")
        sim_omzet = st.slider("Omzet Saat Ini:", 0, 1500, 600, 50, format="%d Juta") * 1_000_000
        
        sim_dpp = max(0, sim_omzet - 500_000_000) if "Orang Pribadi" in sim_bentuk else sim_omzet
        sim_pph = int(sim_dpp * 0.005)
        
        st.markdown(f"**DPP:** Rp {sim_dpp:,.0f}")
        st.markdown(f"<h3 style='color:var(--primary-color)'>Beban Pajak:<br/>Rp {sim_pph:,.0f}</h3>", unsafe_allow_html=True)

    with scol2:
        # Membuat Dataframe untuk Visualisasi
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
        
        st.markdown("#### Kurva Beban Pajak Terhadap Omzet")
        st.line_chart(df, y="PajakTerutang", color="#B4690E")
        if "Orang Pribadi" in sim_bentuk:
            st.info("💡 **Perhatikan Garis Datar di Awal:** Pada grafik di atas, beban pajak tetap Rp 0 hingga omzet mencapai Rp 500.000.000. Inilah bukti insentif fasilitas PTKP untuk UMKM Orang Pribadi.")
        else:
            st.warning("⚠️ **Garis Linear Sejak Awal:** Karena Anda memilih Badan Usaha, tidak ada fasilitas bebas pajak Rp 500 juta. Garis pajak langsung naik (0,5%) sejak omzet pertama.")

# ── TAB 3: BASIS PENGETAHUAN SIMBOLIK ──────────────────────────────────────
with tab3:
    st.subheader("🏛️ Arsitektur Riset: Neuro-Symbolic AI")
    st.caption("Penjelasan metodologi perancangan sistem bagi telaah akademis.")
    
    st.markdown("""
    Aplikasi ini dibangun menggunakan arsitektur hybrid untuk mengatasi kelemahan LLM murni (halusinasi angka pajak/aturan hukum) dalam domain kritikal.
    
    ### 1. Symbolic Component (Pohon Keputusan Eksak)
    Aturan hukum di-hardcode (dikodifikasi) menjadi logika *if-else* matematis.
    *   **Perizinan:** KBLI 56 & 10799 (PP 28/2025)
    *   **Perpajakan:** Threshold Rp 500 Juta PTKP WPOP (PP 20/2026)
    *   **Halal:** Kriteria Bahan & Omzet Program SEHATI (Kepkaban BPJPH No.150/2022)
    *   **Keamanan Pangan:** Perka BPOM No.22/2018 (SLHS vs P-IRT vs BPOM MD)
    
    ### 2. Neural Component (Pedagogical Rephraser)
    Data deterministik (JSON) dikirim ke **Gemini 1.5 API** *bukan* untuk dihitung ulang, melainkan hanya untuk **diparafrase (rephrase)** menggunakan teori *Education Informatics* (Cognitive Load Theory & Scaffolding). Sistem menghasilkan panduan yang empatik, ramah, dan actionable.
    """)
    
    with st.expander("Lihat Struktur Payload JSON Internal"):
        st.json({
            "project_metadata": {
                "title": "Neuro-Symbolic AI Assistant for Regulatory Compliance",
                "author": "Paulus Pensies Anggoro (2520101007)",
                "specialization": "Education Informatics (EI)"
            },
            "status": "Ready for Sinta 2 / Scopus Q1 Submission"
        })

st.divider()
st.caption("© 2026 | Magister Teknologi Informasi - Universitas Pradita | Proyek Riset Individu")
