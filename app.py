import streamlit as st
import google.generativeai as genai
from supabase import create_client
from PIL import Image, ImageDraw
import io
import urllib.parse
import random

# ==========================================
# 1. KONFIGURASI PASAK UTAMA
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="AntiLolos", page_icon="🛡️", layout="centered")

# ==========================================
# 2. CSS & FUNGSI KAD AMARAN
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .stButton>button { border-radius: 25px !important; font-weight: bold; transition: all 0.3s ease; }
    .stButton>button:hover { transform: scale(1.02); }
    .warning-card { padding: 20px; border-radius: 15px; background-color: #ffeded; border-left: 6px solid #ff4b4b; box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.1); margin-bottom: 20px; }
    .safe-card { padding: 20px; border-radius: 15px; background-color: #e8f5e9; border-left: 6px solid #4caf50; box-shadow: 0px 4px 10px rgba(76, 175, 80, 0.1); margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

def generate_warning_card(status, ulasan):
    img = Image.new('RGB', (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    color = (255, 75, 75) if status == "SCAM BAHAYA" else (76, 175, 80)
    draw.rectangle([0, 0, 20, 400], fill=color)
    draw.text((50, 50), f"STATUS: {status}", fill=color)
    draw.text((50, 100), f"Hasil Analisis AI:", fill=(50, 50, 50))
    draw.text((50, 150), ulasan[:80] + "...", fill=(0, 0, 0))
    draw.text((50, 350), "Dijana oleh AntiLolos AI", fill=(150, 150, 150))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

menu = ["🔍 Pengesan Scam", "🎯 Ujian Kekebalan"]
choice = st.radio("Menu", menu, horizontal=True, label_visibility="collapsed")

# ==========================================
# SEGMEN 1: PENGESAN SCAM
# ==========================================
if choice == "🔍 Pengesan Scam":
    st.title("🛡️ AntiLolos")
    st.subheader("Jangan Biarkan Data & Wang Anda Lolos!")
    user_input = st.text_area("Kotak Semakan Mesej:", placeholder="Contoh: Tahniah! Anda terpilih...", height=130)
    
    if st.button("Semak Mesej Ini", type="primary"):
        if not user_input.strip():
            st.warning("Sila masukkan mesej dahulu.")
        else:
            with st.spinner("AntiLolos AI sedang mengimbas..."):
                db_query = supabase.table("scam_logs").select("*").eq("teks_laporan", user_input.strip()).execute()
                if db_query.data:
                    status = db_query.data[0]["klasifikasi_gemini"]
                    ulasan = db_query.data[0]["ulasan_ai"]
                else:
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt = f"Analisis mesej ini: {user_input}. Format: KATEGORI: [SCAM BAHAYA atau SELAMAT]. Ulasan: [Ringkas]."
                        response = model.generate_content(prompt)
                        output = response.text
                        status = "SCAM BAHAYA" if "SCAM BAHAYA" in output else "SELAMAT"
                        ulasan = output.replace("KATEGORI: SCAM BAHAYA", "").replace("KATEGORI: SELAMAT", "").strip()
                        supabase.table("scam_logs").insert({"teks_laporan": user_input.strip(), "klasifikasi_gemini": status, "ulasan_ai": ulasan}).execute()
                    except:
                        status, ulasan = "RALAT", ""
            
            if status == "SCAM BAHAYA":
                st.markdown(f"<div class='warning-card'><h3>⚠️ AMARAN: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                image_bytes = generate_warning_card(status, ulasan)
                st.image(image_bytes, caption="Kad Amaran AntiLolos")
                st.download_button("⬇️ Download Kad Amaran", image_bytes, "Amaran_AntiLolos.png", "image/png")
                share_text = f"⚠️ AWAS! AntiLolos AI kesan scam: {ulasan}"
            elif status == "SELAMAT":
                st.markdown(f"<div class='safe-card'><h3>✅ STATUS: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                share_text = f"✅ AntiLolos AI: Mesej ini disahkan SELAMAT. {ulasan}"
            
            if status != "RALAT":
                encoded = urllib.parse.quote(share_text)
                st.markdown(f'<a href="https://api.whatsapp.com/send?text={encoded}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 20px; width: 100%;">➔ Kongsi ke WhatsApp</button></a>', unsafe_allow_html=True)

# ==========================================
# SEGMEN 2: UJIAN KEKEBALAN
# ==========================================
elif choice == "🎯 Ujian Kekebalan":
    st.title("🎯 Ujian Kekebalan Digital")
    st.write("Hadapi 10 senario rawak. Adakah pertahanan digital anda kukuh?")
    
    semua_soalan = [
        {"pengirim": "011-3482XXXX", "mesej": "Salam bro, aku Shah ni. Tersalah hantar kod TAC kat fon kau. Boleh forward balik tak? Urgent!", "pilihan": [{"teks": "Forward TAC", "risiko": 10}, {"teks": "Abaikan", "risiko": 0}]},
        {"pengirim": "SMS Bank", "mesej": "AMARAN! Akaun anda diakses peranti asing. Sekat segera di: http://maybank-security-lock.com", "pilihan": [{"teks": "Klik link", "risiko": 10}, {"teks": "Abaikan", "risiko": 0}]},
        {"pengirim": "Pegawai LHDN", "mesej": "Tunggakan cukai RM4,820. Waran sita rumah dalam 3 jam.", "pilihan": [{"teks": "Bayar terus", "risiko": 10}, {"teks": "Semak MyTax", "risiko": 0}]},
        {"pengirim": "Grup Telegram", "mesej": "Pelaburan Syariah Ustaz Jamil. Modal RM300 jadi RM5,000!", "pilihan": [{"teks": "Invest", "risiko": 10}, {"teks": "Report", "risiko": 0}]},
        {"pengirim": "Iklan Facebook", "mesej": "Telefon ada 14 virus! Pasang SecureCleaner.apk.", "pilihan": [{"teks": "Install", "risiko": 10}, {"teks": "Abaikan", "risiko": 0}]},
        {"pengirim": "Pos Laju", "mesej": "Bungkusan ditangguhkan. Bayar RM1.20 di: http://poslaju-redirection.top", "pilihan": [{"teks": "Bayar", "risiko": 10}, {"teks": "Abaikan", "risiko": 0}]},
        {"pengirim": "Shopee", "mesej": "Tahniah! Anda menang RM3,000. Tuntut di: http://shopee-rewards-2026.net", "pilihan": [{"teks": "Klik", "risiko": 10}, {"teks": "Abaikan", "risiko": 0}]},
        {"pengirim": "Mahkamah Tinggi", "mesej": "Anda terlibat gubahan wang. Tekan 1.", "pilihan": [{"teks": "Tekan 1", "risiko": 10}, {"teks": "Letak fon", "risiko": 0}]},
        {"pengirim": "SMS Komuniti", "mesej": "Pinjaman syariah lulus 30 min. WhatsApp: wa.me/6011xxxx", "pilihan": [{"teks": "WhatsApp", "risiko": 10}, {"teks": "Block", "risiko": 0}]},
        {"pengirim": "Mesej Viral", "mesej": "Bantuan e-Dompet RM300! Tebus di: http://bantuan-tunai-gov.xyz", "pilihan": [{"teks": "Klik", "risiko": 10}, {"teks": "Abaikan", "risiko": 0}]}
    ]

    if "soalan_shuffled" not in st.session_state:
        st.session_state.soalan_shuffled = random.sample(semua_soalan, len(semua_soalan))
        st.session_state.soalan_semasa = 0
        st.session_state.skor_risiko = 0
        st.session_state.kuiz_tamat = False

    if not st.session_state.kuiz_tamat:
        idx = st.session_state.soalan_semasa
        senario = st.session_state.soalan_shuffled[idx]
        st.caption(f"Senario {idx + 1} daripada 10")
        st.write(f"💬 Mesej dari **{senario['pengirim']}**: {senario['mesej']}")
        for p in senario['pilihan']:
            if st.button(p['teks'], key=f"btn_{idx}_{p['teks']}"):
                st.session_state.skor_risiko += p['risiko']
                if st.session_state.soalan_semasa + 1 < 10:
                    st.session_state.soalan_semasa += 1
                    st.rerun()
                else:
                    st.session_state.kuiz_tamat = True
                    st.rerun()
    else:
        total = st.session_state.skor_risiko
        st.success(f"Ujian Tamat! Skor Risiko Anda: {total}%")
        if st.button("Ulang Semula"):
            del st.session_state.soalan_shuffled
            st.session_state.soalan_semasa = 0
            st.session_state.skor_risiko = 0
            st.session_state.kuiz_tamat = False
            st.rerun()
