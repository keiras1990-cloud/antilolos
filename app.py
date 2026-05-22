import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. KONFIGURASI PASAK UTAMA & AMANAH DATA
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="AntiLolos", page_icon="🛡️", layout="centered")

# Suntikan Gaya Rekaan Khas (Custom CSS)
st.markdown("""
    <style>
    .stButton>button { border-radius: 25px !important; font-weight: bold; transition: all 0.3s ease; }
    .stButton>button:hover { transform: scale(1.02); }
    .scam-card { padding: 20px; border-radius: 15px; background-color: #ffeded; border-left: 6px solid #ff4b4b; box-shadow: 0px 4px 10px rgba(255, 75, 75, 0.1); margin-bottom: 20px; }
    .safe-card { padding: 20px; border-radius: 15px; background-color: #e8f5e9; border-left: 6px solid #4caf50; box-shadow: 0px 4px 10px rgba(76, 175, 80, 0.1); margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

menu = ["🔍 Pengesan Scam", "🎯 Ujian Kekebalan"]
choice = st.radio("Menu", menu, horizontal=True, label_visibility="collapsed")

# ==========================================
# SEGMEN 1: 🔍 PENGESAN SCAM (LOGIK CACHING + GEMINI)
# ==========================================
if choice == "🔍 Pengesan Scam":
    st.title("🛡️ AntiLolos")
    st.subheader("Jangan Biarkan Data & Wang Anda Lolos!")
    st.write("Tampal mesej WhatsApp, SMS, atau pautan mencurigakan untuk dianalisis oleh AI.")

    user_input = st.text_area("Kotak Semakan Mesej:", placeholder="Contoh: Tahniah! Anda terpilih menerima bantuan RM500...", height=130)
    
    if st.button("Semak Mesej Ini", type="primary"):
        if not user_input.strip():
            st.warning("Sila masukkan teks mesej terlebih dahulu.")
        else:
            with st.spinner("AntiLolos AI sedang mengimbas corak penipuan..."):
                
                # Enjin Caching Supabase
                db_query = supabase.table("scam_logs").select("*").eq("Teks_Laporan", user_input.strip()).execute()
                
                if db_query.data:
                    status = db_query.data[0]["Klasifikasi_Gemini"]
                    ulasan = db_query.data[0]["Ulasan_AI"]
                    st.caption("💡 Hasil semakan pantas ditemui dalam memori pangkalan data komuniti.")
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
                        
                        status = "SCAM BAHAYA" if "KATEGORI: SCAM BAHAYA" in output_text else "SELAMAT"
                        ulasan = output_text.replace("KATEGORI: SCAM BAHAYA", "").replace("KATEGORI: SELAMAT", "").strip()
                        
                        supabase.table("scam_logs").insert({
                            "Teks_Laporan": user_input.strip(),
                            "Klasifikasi_Gemini": status,
                            "Ulasan_AI": ulasan
                        }).execute()
                    except Exception as e:
                        st.error("Sistem mengalami kelengahan teknikal.")
                        status = "RALAT"
                
                if status == "SCAM BAHAYA":
                    st.markdown(f"<div class='scam-card'><h3>⚠️ AMARAN: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                    share_text = f"*🚨 PERISAI AMARAN ANTILOLOS 🚨*\nMesej disemak: _\"{user_input[:40]}...\"_\n*Keputusan AI:* ⚠️ {ulasan}\nSemak di: https://antilolos.streamlit.app"
                elif status == "SELAMAT":
                    st.markdown(f"<div class='safe-card'><h3>✅ STATUS: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                    share_text = f"*ℹ️ INFO KESELAMATAN ANTILOLOS*\nMesej ini disemak dan diklasifikasikan sebagai *SELAMAT*.\nSemak di: https://antilolos.streamlit.app"
                
                if status != "RALAT":
                    encoded_text = urllib.parse.quote(share_text)
                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 20px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold;">➔ Kongsi Amaran Ini ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)

# ==========================================
# SEGMEN 2: 🎯 UJIAN KEKEBALAN (KUIZ INTERAKTIF MOCK WHATSAPP)
# ==========================================
elif choice == "🎯 Ujian Kekebalan":
    st.title("🎯 Ujian Kekebalan Digital")
    st.write("Hadapi 10 senario rawak simulasi harian. Adakah pertahanan digital anda kukuh?")
    
    # Bank 10 Soalan dengan 4 Pilihan Jawapan (Total Risiko Maksimum = 100%)
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

    # Inisialisasi State & Fungsi Shuffle Rawak
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
            status, ulasan = "🔴 TAHAP KELOLOSAN KRITIKAL", "Sangat bahaya! Anda mudah panik dan ditipu oleh taktik siber. Simpanan anda berisiko tinggi lolos."
        elif total >= 30:
            status, ulasan = "🟡 TAHAP KELOLOSAN SEDERHANA", "Anda tahu asas keselamatan, tetapi emosi anda masih mudah dimanipulasi jika diasak secara psikologi."
        else:
            status, ulasan = "🟢 KEKAL KEBAL (ANTILOLOS!)", "Syabas! Perisai siber anda sangat kukuh. Taktik licik scammer tidak akan lolos daripada dikesan oleh anda."

        st.markdown(f"""
            <div style='padding: 25px; border-radius: 15px; background-color: #f8f9fa; border: 2px solid #343a40; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.05);'>
                <h2 style='margin: 0;'>🛡️ KAD LAPORAN ANTILOLOS</h2>
                <h1 style='color: #ff4b4b; font-size: 48px; margin: 10px 0;'>Risiko: {total}%</h1>
                <h4 style='margin-bottom: 15px;'>{status}</h4>
                <p style='font-size: 15px; text-align: justify; color: #495057;'>{ulasan}</p>
            </div>
        """, unsafe_allow_html=True)
        
        kuiz_share_text = f"*🚨 UJIAN KEKEBALAN DIGITAL #ANTILOLOS 🚨*\nKeputusan Risiko Saya: *{total}%*\n*Klasifikasi:* {status}\n\nJangan tunggu sampai wang simpanan bocor. Jom uji ketahanan mental siber anda di: https://antilolos.streamlit.app"
        encoded_kuiz_text = urllib.parse.quote(kuiz_share_text)
        whatsapp_kuiz_url = f"https://api.whatsapp.com/send?text={encoded_kuiz_text}"
        
        st.write("---")
        st.markdown(f'<a href="{whatsapp_kuiz_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 20px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold;">➔ Kongsi Keputusan Kuiz ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)
        
        if st.button("Ulang Semula Ujian"):
            del st.session_state.soalan_shuffled
            st.session_state.soalan_semasa = 0
            st.session_state.skor_risiko = 0
            st.session_state.kuiz_tamat = False
            st.rerun()
