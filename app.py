import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import urllib.parse
import random
from PIL import Image, ImageDraw
import io

# ==========================================
# 1. KONFIGURASI PASAK UTAMA & AMANAH DATA
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="AntiLolos", page_icon="🛡️", layout="centered")

# ==========================================
# 2. DESIGN & FUNGSI GAMBAR
# ==========================================
st.markdown("""
    <style>
    .stButton>button { border-radius: 25px !important; font-weight: bold; transition: all 0.3s ease; }
    .stButton>button:hover { transform: scale(1.02); }
    .scam-card { padding: 20px; border-radius: 15px; background-color: #ffeded; border-left: 6px solid #ff4b4b; box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.1); margin-bottom: 20px; }
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
            st.warning("Sila masukkan teks mesej terlebih dahulu.")
        else:
            with st.spinner("AntiLolos AI sedang mengimbas..."):
                db_query = supabase.table("scam_logs").select("*").eq("teks_laporan", user_input.strip()).execute()
                if db_query.data:
                    status = db_query.data[0]["Klasifikasi_Gemini"]
                    ulasan = db_query.data[0]["Ulasan_AI"]
                else:
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        output_text = model.generate_content(f"Analisis mesej ini: {user_input}. Format: KATEGORI: [SCAM BAHAYA atau SELAMAT]. Ulasan: [Ringkas].").text
                        status = "SCAM BAHAYA" if "KATEGORI: SCAM BAHAYA" in output_text else "SELAMAT"
                        ulasan = output_text.replace("KATEGORI: SCAM BAHAYA", "").replace("KATEGORI: SELAMAT", "").strip()
                        supabase.table("scam_logs").insert({
                            "teks_laporan": user_input.strip(),
                            "klasifikasi_gemini": status,
                            "ulasan_ai": ulasan
                        }).execute()     
                    except:
                        status, ulasan = "RALAT", ""
            
            if status == "SCAM BAHAYA":
                st.markdown(f"<div class='scam-card'><h3>⚠️ AMARAN: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                image_bytes = generate_warning_card(status, ulasan)
                st.image(image_bytes, caption="Kad Amaran AntiLolos")
                st.download_button("⬇️ Download Kad Amaran", image_bytes, "Amaran_AntiLolos.png", "image/png")
                share_text = f"⚠️ AWAS! AntiLolos AI kesan scam: {ulasan}"
            elif status == "SELAMAT":
                st.markdown(f"<div class='safe-card'><h3>✅ STATUS: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                share_text = f"✅ AntiLolos AI: Mesej ini disahkan SELAMAT. {ulasan}"
            
            if status != "RALAT":
                encoded_text = urllib.parse.quote(share_text)
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 20px; width: 100%; cursor: pointer;">➔ Kongsi Amaran Ini ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)

# ==========================================
# SEGMEN 2: UJIAN KEKEBALAN (KUIZ PENUH)
# ==========================================
elif choice == "🎯 Ujian Kekebalan":
    st.title("🎯 Ujian Kekebalan Digital")
    st.write("Hadapi 10 senario rawak. Adakah pertahanan digital anda kukuh?")
    
    semua_soalan = [
        {"pengirim": "011-3482XXXX", "mesej": "Salam bro, aku Shah ni. Tersalah hantar kod TAC kat fon kau. Boleh forward balik tak? Urgent!", "pilihan": [{"teks": "Salin dan hantar kod TAC terus sebab nak tolong kawan.", "risiko": 10}, {"teks": "Tanya dia balik 'Kau Shah yang mana satu?'", "risiko": 5}, {"teks": "Maki pengirim sebab curiga ini scammer.", "risiko": 2}, {"teks": "Abaikan, sekat nombor, dan call nombor sebenar Shah.", "risiko": 0}]},
        {"pengirim": "SMS Bank", "mesej": "AMARAN! Akaun anda diakses peranti asing. Sekat segera di: http://maybank-security-lock.com", "pilihan": [{"teks": "Panik dan terus klik link untuk tukar password.", "risiko": 10}, {"teks": "Klik link tapi sekadar nak tengok rupa website.", "risiko": 5}, {"teks": "Balas SMS tersebut 'Ini tipu!'", "risiko": 2}, {"teks": "Abaikan SMS dan buka aplikasi rasmi bank secara berasingan.", "risiko": 0}]},
        {"pengirim": "Pegawai LHDN", "mesej": "Tunggakan cukai RM4,820. Waran sita rumah dalam 3 jam. Bayar ke akaun agensi: 1642XXX.", "pilihan": [{"teks": "Takut kena sita, terus buat pindahan wang.", "risiko": 10}, {"teks": "Minta diskaun atau tempoh lanjutan bayaran.", "risiko": 5}, {"teks": "Letak telefon, tapi masih rasa risau dan panik.", "risiko": 2}, {"teks": "Letak panggilan dan semak terus di portal rasmi MyTax.", "risiko": 0}]},
        {"pengirim": "Grup Telegram", "mesej": "🔥 PELUANG EMAS! Pelaburan Syariah Ustaz Jamil. Modal RM300, pulangan RM5,000 dalam 24 jam.", "pilihan": [{"teks": "Keluarkan RM300 untuk cuba nasib.", "risiko": 10}, {"teks": "Tanya ahli grup lain sama ada mereka dah dapat duit.", "risiko": 5}, {"teks": "Hanya perhati (silent reader) tanpa buat apa-apa.", "risiko": 2}, {"teks": "Report grup tersebut dan Leave Group terus.", "risiko": 0}]},
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
        st.info(senario['mesej'])
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
        st.success("🏁 Tahniah! Anda telah selesai.")
        total = st.session_state.skor_risiko
        if total >= 70: status, ulasan = "🔴 TAHAP KELOLOSAN KRITIKAL", "Sangat bahaya!"
        elif total >= 30: status, ulasan = "🟡 TAHAP KELOLOSAN SEDERHANA", "Masih boleh diperbaiki."
        else: status, ulasan = "🟢 KEKAL KEBAL (ANTILOLOS!)", "Syabas!"
        st.write(f"### {status}")
        st.write(ulasan)
        if st.button("Ulang Semula Ujian"):
            del st.session_state.soalan_shuffled
            st.session_state.soalan_semasa = 0
            st.session_state.skor_risiko = 0
            st.session_state.kuiz_tamat = False
            st.rerun()
