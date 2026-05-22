import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from PIL import Image, ImageDraw, ImageFont
import io
import urllib.parse
import random
import textwrap

# ==========================================
# 1. KONFIGURASI PASAK UTAMA & AMANAH DATA
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Membina penyambung rasmi ke pangkalan data dan AI
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="AntiLolos", page_icon="🛡️", layout="centered")

# ==========================================
# 2. SUNTIKAN GAYA REKAAN KHAS (KAMPUNG-PROOF & ANTI-DARK MODE)
# ==========================================
st.markdown("""
    <style>
    /* Memaksa seluruh latar belakang aplikasi kekal cerah & bersih walaupun di telefon Mod Gelap */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    
    /* Menghalang semua jenis tulisan daripada bertukar menjadi putih secara automatik */
    h1, h2, h3, h4, h5, h6, p, span, label, li, small, time {
        color: #1e293b !important;
    }
    
    /* Mengemaskan rupa bentuk bar Navigasi Tab supaya tulisan kelihatan jelas di telefon */
    button[data-baseweb="tab"] div p {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p {
        color: #ef4444 !important;
        font-weight: 700 !important;
    }
    
    /* Memastikan kotak input teks textarea mempunyai tulisan gelap yang kontras */
    .stTextArea textarea {
        color: #1e293b !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Mengoptimumkan kotak sembang (Chat Bubbles) kuiz supaya tulisan di dalamnya terang */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-testid="stChatMessage"] p {
        color: #1e293b !important;
    }
    
    /* Konfigurasi asas semua butang agar mesra skrin telefon */
    .stButton>button, .stDownloadButton>button { 
        border-radius: 25px !important; 
        font-weight: bold !important; 
        transition: all 0.3s ease; 
        padding: 12px 24px !important; 
        width: 100% !important;
        display: block !important;
        height: auto !important;
    }
    
    /* [SANGAT PENTING] Gaya Rekaan Khusus Butang Muat Turun (Download Button) Premium */
    .stDownloadButton>button {
        background-color: #2563eb !important; 
        color: #ffffff !important; 
        border: none !important;
        text-align: center !important;
    }
    .stDownloadButton>button:hover {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
    }
    
    /* Menjadikan butang pilihan kuiz mesra tulisan panjang pada skrin telefon */
    .stButton>button[data-testid="baseButton-secondary"] { 
        background-color: #ffffff !important; 
        color: #334155 !important; 
        border: 1px solid #cbd5e1 !important; 
        white-space: normal !important;      
        text-align: left !important;         
        word-break: break-word !important;   
        font-weight: 500 !important;
    }
    .stButton>button[data-testid="baseButton-secondary"]:hover {
        border-color: #ef4444 !important;
        background-color: #fef2f2 !important;
    }
    
    /* Warna khusus untuk Butang Utama (Semak Mesej) */
    .stButton>button[data-testid="baseButton-primary"] { 
        background-color: #ef4444 !important; 
        color: #ffffff !important; 
        border: none !important;
        text-align: center !important;       
    }
    
    /* Sentuhan visual responsif untuk kad amaran dan selamat */
    .scam-card { padding: 20px; border-radius: 15px; background-color: #fff5f5 !important; border-left: 6px solid #ef4444; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.06); margin-bottom: 20px; }
    .scam-card h3, .scam-card p { color: #7f1d1d !important; }
    
    .safe-card { padding: 20px; border-radius: 15px; background-color: #f0fdf4 !important; border-left: 6px solid #22c55e; box-shadow: 0px 4px 12px rgba(34, 197, 94, 0.06); margin-bottom: 20px; }
    .safe-card h3, .safe-card p { color: #064e3b !important; }
    
    .report-box { padding: 20px; border-radius: 15px; background-color: #ffffff !important; border: 2px solid #e2e8f0; text-align: center; box-shadow: 0px 6px 20px rgba(0,0,0,0.03); margin-top: 15px; }
    .report-box h2, .report-box h1, .report-box h4, .report-box p { color: #1e293b !important; }
    
    /* Susun atur kad carta Top 10 Aduan */
    .leaderboard-item { padding: 15px; border-radius: 12px; background-color: #ffffff !important; border: 1px solid #e2e8f0; margin-bottom: 10px; display: flex; align-items: center; box-shadow: 0px 2px 6px rgba(0,0,0,0.01); }
    .rank-number { font-size: 20px; font-weight: bold; color: #ef4444 !important; width: 35px; text-align: center; }
    .brand-logo { font-size: 26px; margin-right: 12px; width: 30px; text-align: center; }
    .scam-details { flex-grow: 1; word-break: break-word; }
    .scam-details strong, .scam-details span, .scam-details small { color: #1e293b !important; }
    .badge-count { background-color: #fee2e2 !important; color: #ef4444 !important; padding: 4px 10px; border-radius: 15px; font-weight: bold; font-size: 12px; text-align: center; margin-left: 5px; white-space: nowrap; }
    
    /* Memusatkan pengepala utama di skrin telefon */
    .main-header { text-align: center; padding: 10px 0; }
    div[data-testid="stRadio"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HELPER: PENGECAKAN LOGO AUTOMATIK
# ==========================================
def dapatkan_logo_scam(teks):
    teks_lower = teks.lower()
    if any(x in teks_lower for x in ["maybank", "cimb", "bank", "tac", "bsn", "pbe"]):
        return "🏦"  
    elif any(x in teks_lower for x in ["whatsapp", "wasap", "wa.me"]):
        return "🟢"  
    elif any(x in teks_lower for x in ["lhdn", "cukai", "hasil", "mahkamah", "polis", "pdrm"]):
        return "⚖️"  
    elif any(x in teks_lower for x in ["pos", "laju", "j&t", "courier", "bungkusan", "parcel"]):
        return "📦"  
    elif any(x in teks_lower for x in ["shopee", "lazada", "hadiah", "cabutan", "menang"]):
        return "🛍️"  
    elif "telegram" in teks_lower:
        return "✈️"  
    else:
        return "⚠️"  

# ==========================================
# 4. ENJIN GENERATOR KAD VISUAL (PILLOW)
# ==========================================
def generate_warning_card(status, ulasan):
    img = Image.new('RGB', (800, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_small = ImageFont.load_default(size=16)
        font_ulasan = ImageFont.load_default(size=24)   
        font_header = ImageFont.load_default(size=28)   
    except:
        font_small = ImageFont.load_default()
        font_ulasan = ImageFont.load_default()
        font_header = ImageFont.load_default()
    
    theme_color = (239, 68, 68) if status == "SCAM BAHAYA" else (34, 197, 94)
    draw.rectangle([0, 0, 25, 450], fill=theme_color)
    draw.text((60, 40), "PERISAI KESELAMATAN ANTILOLOS", fill=(100, 116, 139), font=font_small)
    
    if status == "SCAM BAHAYA":
        header_text = "STATUS KELAS SCAM : BAHAYA!!"
    else:
        header_text = "STATUS KELAS : SELAMAT"
        
    for dx in [0, 1]:
        for dy in [0, 1]:
            draw.text((60 + dx, 75 + dy), header_text, fill=theme_color, font=font_header)
            
    draw.text((60, 140), "Hasil Keputusan Imbasan AI:", fill=(71, 85, 105), font=font_small)
    
    ulasan_bersih = ulasan.replace("**", "")
    lines = textwrap.wrap(ulasan_bersih, width=45)
    lines = lines[:5]
    
    current_y = 175
    for line in lines:
        draw.text((60, current_y), line, fill=(15, 23, 42), font=font_ulasan)
        current_y += 38
        
    draw.rectangle([60, 390, 740, 392], fill=(226, 232, 240))
    draw.text((60, 405), "Semak mesej mencurigakan anda di: antilolos.streamlit.app", fill=(148, 163, 184), font=font_small)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# ==========================================
# 5. PEMBINAAN NAVIGASI TAB RASMI (PREMIUM MOBILE VIEW)
# ==========================================
tab1, tab2, tab3 = st.tabs(["🔍 Pengesan Scam", "🎯 Ujian Kekebalan", "📊 Top 10 Aduan"])

# ------------------------------------------
# SEGMEN 1: 🔍 PENGESAN SCAM
# ------------------------------------------
with tab1:
    st.markdown("<div class='main-header'><h1>🛡️ AntiLolos</h1><h3>Jangan Biarkan Data & Wang Anda Lolos!</h3></div>", unsafe_allow_html=True)
    st.write("Tampal mesej WhatsApp, SMS, atau pautan mencurigakan untuk dianalisis oleh pakar siber AI.")

    user_input = st.text_area("Kotak Semakan Mesej:", placeholder="Contoh: Tahniah! Anda terpilih menerima bantuan khas RM500. Sila sahkan di pautan...", height=120, key="input_scam")
    
    if st.button("Semak Mesej Ini", type="primary", key="btn_semak_scam"):
        if not user_input.strip():
            st.warning("Sila masukkan teks mesej terlebih dahulu.")
        else:
            with st.spinner("AntiLolos AI sedang imbas..."):
                db_query = supabase.table("scam_logs").select("*").eq("teks_laporan", user_input.strip()).execute()
                
                if db_query.data:
                    status = db_query.data[0]["klasifikasi_gemini"]
                    ulasan = db_query.data[0]["ulasan_ai"]
                    st.caption("💡 Hasil semakan pantas ditemui dalam memori pangkalan data komuniti (RM0 Kos API).")
                    
                    try:
                        supabase.table("scam_logs").insert({
                            "teks_laporan": user_input.strip(),
                            "klasifikasi_gemini": status,
                            "ulasan_ai": ulasan
                        }).execute()
                    except:
                        pass
                else:
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        system_instruction = (
                            "Anda adalah pakar keselamatan siber terlatih di Malaysia. Analisis mesej di bawah. "
                            "Tentukan klasifikasi sama ada ia 'SCAM BAHAYA' atau 'SELAMAT/SAH'. "
                            "Berikan ulasan yang ringkas, kasual, dan mudah difahami oleh warga emas. "
                            "Format output wajib dimulakan dengan baris pertama: KATEGORI: [SCAM BAHAYA atau SELAMAT]"
                        )
                        response = model.generate_content(f"{system_instruction}\n\nMesej:\n{user_input}")
                        output_text = response.text
                        
                        status = "SCAM BAHAYA" if "KATEGORI: SCAM BAHAYA" in output_text or "SCAM BAHAYA" in output_text else "SELAMAT"
                        ulasan = output_text.replace("KATEGORI: SCAM BAHAYA", "").replace("KATEGORI: SELAMAT", "").strip()
                        
                        supabase.table("scam_logs").insert({
                            "teks_laporan": user_input.strip(),
                            "klasifikasi_gemini": status,
                            "ulasan_ai": ulasan
                        }).execute()
                    except Exception as e:
                        st.error(f"Kelengahan rangkaian. Ralat: {e}")
                        status = "RALAT"
                
                if status == "SCAM BAHAYA":
                    st.markdown(f"<div class='scam-card'><h3>⚠️ AMARAN KRITIKAL: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                    image_bytes = generate_warning_card(status, ulasan)
                    st.image(image_bytes, use_container_width=True)
                    st.download_button("⬇️ Download Kad Amaran Ini (Simpan Imej)", image_bytes, "Amaran_AntiLolos.png", "image/png", use_container_width=True)
                    share_text = f"*🚨 PERISAI AMARAN ANTILOLOS 🚨*\nMesej disemak: _\"{user_input[:40]}...\"_\n*Keputusan AI:* ⚠️ {ulasan}\nSemak segera di: https://antilolos.streamlit.app"
                
                elif status == "SELAMAT":
                    st.markdown(f"<div class='safe-card'><h3>✅ STATUS KESELAMATAN: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                    image_bytes = generate_warning_card(status, ulasan)
                    st.image(image_bytes, use_container_width=True)
                    st.download_button("⬇️ Download Kad Pengesahan Ini", image_bytes, "Selamat_AntiLolos.png", "image/png", use_container_width=True)
                    share_text = f"*ℹ️ INFO KESELAMATAN ANTILOLOS*\nMesej ini telah disemak dan disahkan *SELAMAT*.\nSemak di: https://antilolos.streamlit.app"
                
                if status != "RALAT":
                    encoded_text = urllib.parse.quote(share_text)
                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 14px 20px; border-radius: 25px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s ease;">➔ Kongsi Amaran Ini ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)

# ------------------------------------------
# SEGMEN 2: 🎯 UJIAN KEKEBALAN
# ------------------------------------------
with tab2:
    st.markdown("<div class='main-header'><h1>🎯 Ujian Kekebalan Digital</h1></div>", unsafe_allow_html=True)
    st.write("Hadapi 10 senario rawak simulasi harian. Adakah benteng pertahanan digital anda kukuh?")
    
    semua_soalan = [
        {"pengirim": "011-3482XXXX", "mesej": "Salam bro, aku Shah ni. Tersalah hantar kod TAC kat fon kau. Boleh forward balik tak? Urgent!", "pilihan": [{"teks": "Salin dan hantar kod TAC terus sebab nak tolong kawan.", "risiko": 10}, {"teks": "Tanya dia balik 'Kau Shah yang mana satu?'", "risiko": 5}, {"teks": "Maki pengirim sebab curiga ini scammer.", "risiko": 2}, {"teks": "Abaikan, sekat nombor, dan call nombor sebenar Shah.", "risiko": 0}]},
        {"pengirim": "SMS Bank", "mesej": "AMARAN! Akaun anda diakses peranti asing. Sekat segera di: http://maybank-security-lock.com", "pilihan": [{"teks": "Panik dan terus klik link untuk tukar password.", "risiko": 10}, {"teks": "Klik link tapi sekadar nak tengok rupa website.", "risiko": 5}, {"teks": "Balas SMS tersebut 'Ini tipu!'", "risiko": 2}, {"teks": "Abaikan SMS dan buka aplikasi rasmi bank secara berasingan.", "risiko": 0}]},
        {"pengirim": "Pegawai LHDN", "mesej": "Tunggakan cukai RM4,820. Waran sita rumah dalam 3 jam. Bayar ke akaun agensi: 1642XXX.", "pilihan": [{"teks": "Takut kena sita, terus buat pindahan wang.", "risiko": 10}, {"teks": "Minta diskaun atau tempoh lanjutan bayaran.", "risiko": 5}, {"teks": "Letak telefon, tapi masih rasa risau dan panik.", "risiko": 2}, {"teks": "Letak panggilan dan semak terus di portal rasmi MyTax.", "risiko": 0}]},
        {"pengirim": "Grup Telegram", "mesej": "Pelaburan Syariah Ustaz Jamil. Modal RM300, pulangan RM5,000 dalam 24 jam.", "pilihan": [{"teks": "Keluarkan RM300 untuk cuba nasib.", "risiko": 10}, {"teks": "Tanya ahli grup lain sama ada mereka dah dapat duit.", "risiko": 5}, {"teks": "Hanya perhati (silent reader) tanpa buat apa-apa.", "risiko": 2}, {"teks": "Report grup tersebut dan Leave Group terus.", "risiko": 0}]},
        {"pengirim": "Iklan Facebook", "mesej": "Telefon anda ada 14 virus! Pasang SecureCleaner.apk sekarang untuk selamatkan peranti.", "pilihan": [{"teks": "Download dan install APK tersebut cepat-cepat.", "risiko": 10}, {"teks": "Download saja tapi tak install lagi.", "risiko": 5}, {"teks": "Tulis komen marah pada iklan tersebut.", "risiko": 2}, {"teks": "Abaikan iklan dan guna antivirus rasmi di telefon.", "risiko": 0}]},
        {"pengirim": "Pos Laju", "mesej": "Bungkusan ditangguhkan. Sila kemas kini alamat dan bayar RM1.20 di: http://poslaju-redirection.top", "pilihan": [{"teks": "Bayar RM1.20 guna kad debit/kredit.", "risiko": 10}, {"teks": "Isi alamat sahaja tapi tak letak maklumat bank.", "risiko": 5}, {"teks": "Klik link sekadar untuk baca butiran bungkusan.", "risiko": 2}, {"teks": "Abaikan SMS dan semak tracking number di aplikasi kurier.", "risiko": 0}]},
        {"pengirim": "Shopee", "mesej": "Tahniah! Anda menang Cabutan Bertuah RM3,000. Tuntut di: http://shopee-rewards-2026.net", "pilihan": [{"teks": "Klik link dan isi IC beserta nombor akaun bank.", "risiko": 10}, {"teks": "Klik link dan letak nama palsu untuk test.", "risiko": 5}, {"teks": "Tanya customer service Shopee dalam in-app chat.", "risiko": 2}, {"teks": "Abaikan, platform rasmi tak guna domain pelik macam .net.", "risiko": 0}]},
        {"pengirim": "Mahkamah Tinggi", "mesej": "(Panggilan Suara) Anda didapati terlibat kes gubahan wang haram. Tekan 1 untuk bercakap dengan pegawai.", "pilihan": [{"teks": "Tekan 1 dan ikut arahan pemanggil sebab takut.", "risiko": 10}, {"teks": "Tekan 1 tapi niat nak main-mainkan pemanggil.", "risiko": 5}, {"teks": "Dengar sampai habis tanpa cakap apa-apa.", "risiko": 2}, {"teks": "Letak telefon serta-merta.", "risiko": 0}]},
        {"pengirim": "SMS Komuniti", "mesej": "Pinjaman syariah lulus 30 min. RM5,000 bulan RM120. WhatsApp: wa.me/6011xxxx", "pilihan": [{"teks": "WhatsApp nombor tu sebab tengah sengkek.", "risiko": 10}, {"teks": "Simpan nombor tu kot-kot terdesak nanti.", "risiko": 5}, {"teks": "Padam SMS tersebut sahaja.", "risiko": 2}, {"teks": "Padam dan terus Block nombor pengirim.", "risiko": 0}]},
        {"pengirim": "Mesej Viral", "mesej": "Bantuan e-Dompet RM300 dibuka! Tebus kredit percuma di: http://bantuan-tunai-gov.xyz", "pilihan": [{"teks": "Klik dan log masuk guna ID perbankan internet.", "risiko": 10}, {"teks": "Share link tu kat kawan lain suruh diorang cuba dulu.", "risiko": 5}, {"teks": "Klik link untuk tengok siapa yang buat website tu.", "risiko": 2}, {"teks": "Abaikan dan rujuk portal rasmi Kementerian Kewangan.", "risiko": 0}]}
    ]

    if "soalan_shuffled" not in st.session_state:
        st.session_state.soalan_shuffled = random.sample(semua_soalan, len(semua_soalan))
        st.session_state.soalan_semasa = 0
        st.session_state.skor_risiko = 0
        st.session_state.kuiz_tamat = False

    if not st.session_state.kuiz_tamat:
        idx = st.session_state.soalan_semasa
        senario = st.session_state.soalan_shuffled[idx]
        st.progress((idx) / 10, text=f"Senario {idx + 1} daripada 10")
        st.write("---")
        st.caption(f"💬 Mesej Masuk daripada: **{senario['pengirim']}**")
        with st.chat_message("user", avatar="👤"):
            st.write(senario['mesej'])
        st.write("👇 **Apakah tindakan refleks digital anda?**")
        for i, pil in enumerate(senario['pilihan']):
            if st.button(pil['teks'], key=f"btn_{idx}_{i}", use_container_width=True):
                st.session_state.skor_risiko += pil['risiko']
                if st.session_state.soalan_semasa + 1 < 10:
                    st.session_state.soalan_semasa += 1
                    st.rerun()
                else:
                    st.session_state.kuiz_tamat = True
                    st.rerun()
    else:
        st.write("---")
        st.success("🏁 Tahniah! Anda telah selesai mengharungi Ujian Kekebalan Digital AntiLolos.")
        total = st.session_state.skor_risiko
        if total >= 70:
            status, ulasan = "🔴 TAHAP KELOLOSAN KRITIKAL", "Sangat bahaya! Anda mudah panik dan mudah ditipu oleh taktik psikologi siber. Wang simpanan anda berisiko tinggi lolos ke tangan pihak ketiga."
        elif total >= 30:
            status, ulasan = "🟡 TAHAP KELOLOSAN SEDERHANA", "Anda tahu asas keselamatan digital, tetapi emosi anda masih berisiko dimanipulasi jika diasak secara psikologi bertubi-tubi."
        else:
            status, ulasan = "🟢 KEKAL KEBAL (ANTILOLOS!)", "Syabas! Perisai siber anda sangat kukuh. Taktik licik penjenayah siber tidak akan mampu lolos daripada dikesan oleh kecerdasan minda anda."

        st.markdown(f"""
            <div class='report-box'>
                <h2 style='margin: 0;'>🛡️ KAD LAPORAN ANTILOLOS</h2>
                <h1 style='color: #ef4444; font-size: 54px; margin: 15px 0;'>Risiko: {total}%</h1>
                <h4 style='margin-bottom: 15px; font-weight: bold;'>{status}</h4>
                <p style='font-size: 16px; text-align: justify;'>{ulasan}</p>
            </div>
        """, unsafe_allow_html=True)
        kuiz_share_text = f"*🚨 UJIAN KEKEBALAN DIGITAL #ANTILOLOS 🚨*\nKeputusan Skor Risiko Saya: *{total}%*\n*Klasifikasi Kesedaran:* {status}\n\nJangan tunggu sehingga simpanan bocor. Jom uji ketahanan mental siber anda sekarang di: https://antilolos.streamlit.app"
        encoded_kuiz_text = urllib.parse.quote(kuiz_share_text)
        whatsapp_kuiz_url = f"https://api.whatsapp.com/send?text={encoded_kuiz_text}"
        st.write("---")
        st.markdown(f'<a href="{whatsapp_kuiz_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 25px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold; transition: 0.3s ease;">➔ Kongsi Keputusan Kuiz ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)
        if st.button("Ulang Semula Ujian", use_container_width=True, key="btn_restart_quiz"):
            del st.session_state.soalan_shuffled
            st.session_state.soalan_semasa = 0
            st.session_state.skor_risiko = 0
            st.session_state.kuiz_tamat = False
            st.rerun()

# ------------------------------------------
# SEGMEN 3: 📊 TOP 10 ADUAN SCAMMER
# ------------------------------------------
with tab3:
    st.markdown("<div class='main-header'><h1>📊 Trend Taktik Scammer Terkini</h1><h3>Carta Kehangatan Ancaman Siber Komuniti</h3></div>", unsafe_allow_html=True)
    st.write("Senarai 10 mesej penipuan yang paling kerap disemak dan dilaporkan oleh pengguna di dalam pangkalan data komuniti AntiLolos.")
    
    with st.spinner("Mengekstrak data carta kehangatan aduan siber..."):
        res = supabase.table("scam_logs").select("teks_laporan, klasifikasi_gemini, ulasan_ai").execute()
        
        if res.data:
            scam_counts = {}
            for data_row in res.data:
                if data_row.get("klasifikasi_gemini") == "SCAM BAHAYA":
                    teks_lapor = data_row.get("teks_laporan", "").strip()
                    ulas_ai = data_row.get("ulasan_ai", "").strip().replace("**", "")
                    
                    kunci_data = (teks_lapor, ulas_ai)
                    scam_counts[kunci_data] = scam_counts.get(kunci_data, 0) + 1
            
            top_10_sorted = sorted(scam_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_10_sorted:
                st.write("---")
                for rank, ((teks_aduan, ulasan_aduan), jumlah_kes) in enumerate(top_10_sorted, 1):
                    logo_visual = dapatkan_logo_scam(teks_aduan)
                    
                    teks_paparan = teks_aduan[:75] + "..." if len(teks_aduan) > 75 else teks_aduan
                    ulasan_paparan = ulasan_aduan[:90] + "..." if len(ulasan_aduan) > 90 else ulasan_aduan
                    
                    st.markdown(f"""
                        <div class='leaderboard-item'>
                            <div class='rank-number'>#{rank}</div>
                            <div class='brand-logo'>{logo_visual}</div>
                            <div class='scam-details'>
                                <strong>Mesej Ditangkap:</strong> 
                                <span style='font-style: italic;'>"{teks_paparan}"</span><br>
                                <small style='font-weight: 600;'>🛡️ Ulasan AI: {ulasan_paparan}</small>
                            </div>
                            <div class='badge-count'>{jumlah_kes} Aduan</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Pangkalan data belum merekodkan sebarang sampel kes 'SCAM BAHAYA' buat masa ini.")
        else:
            st.info("Tiada log rekod carian ditemui dalam pangkalan data komuniti.")
