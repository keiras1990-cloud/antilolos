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
# 2. SUNTIKAN GAYA REKAAN KHAS (CUSTOM CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { border-radius: 25px !important; font-weight: bold; transition: all 0.3s ease; padding: 10px 24px; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 4px 15px rgba(0,0,0,0.05); }
    .scam-card { padding: 25px; border-radius: 15px; background-color: #fff5f5; border-left: 6px solid #ef4444; box-shadow: 0px 4px 12px rgba(239, 68, 68, 0.08); margin-bottom: 25px; }
    .safe-card { padding: 25px; border-radius: 15px; background-color: #f0fdf4; border-left: 6px solid #22c55e; box-shadow: 0px 4px 12px rgba(34, 197, 94, 0.08); margin-bottom: 25px; }
    .report-box { padding: 25px; border-radius: 15px; background-color: #ffffff; border: 2px solid #e2e8f0; text-align: center; box-shadow: 0px 6px 20px rgba(0,0,0,0.04); margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ENJIN GENERATOR KAD VISUAL (PILLOW)
# ==========================================
def generate_warning_card(status, ulasan):
    # Membina kanvas imej beresolusi tinggi
    img = Image.new('RGB', (800, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Menguruskan saiz tulisan secara dinamik (Sokongan Pillow Moden)
    try:
        font_small = ImageFont.load_default(size=16)
        font_ulasan = ImageFont.load_default(size=24)   # Saiz tulisan ulasan yang besar dan jelas
        font_header = ImageFont.load_default(size=28)   # Saiz pengepala status utama
    except:
        font_small = ImageFont.load_default()
        font_ulasan = ImageFont.load_default()
        font_header = ImageFont.load_default()
    
    # Menentukan tema warna berdasarkan klasifikasi siber
    theme_color = (239, 68, 68) if status == "SCAM BAHAYA" else (34, 197, 94)
    
    # Melukis jalur sisi keselamatan
    draw.rectangle([0, 0, 25, 450], fill=theme_color)
    
    # Menulis teks pengepala atas
    draw.text((60, 40), "PERISAI KESELAMATAN ANTILOLOS", fill=(100, 116, 139), font=font_small)
    
    # Format teks status utama mengikut permintaan baharu anda
    if status == "SCAM BAHAYA":
        header_text = "STATUS KELAS SCAM : BAHAYA!!"
    else:
        header_text = "STATUS KELAS : SELAMAT"
        
    # Memberi kesan tebal (bold) terkawal pada bahagian pengepala utama sahaja
    for dx in [0, 1]:
        for dy in [0, 1]:
            draw.text((60 + dx, 75 + dy), header_text, fill=theme_color, font=font_header)
            
    draw.text((60, 140), "Hasil Keputusan Imbasan AI:", fill=(71, 85, 105), font=font_small)
    
    # MEMBERSIHKAN TEKS: Buang simbol asterisks (**) daripada ulasan AI
    ulasan_bersih = ulasan.replace("**", "")
    
    # PEMOTONGAN PINTAR: Menyusun perenggan mengikut sempadan perkataan (Word-wrap)
    # Lebar 45 karakter adalah saiz optimum bagi tulisan saiz 24 pada kanvas lebar 800px
    lines = textwrap.wrap(ulasan_bersih, width=45)
    
    # Memastikan tulisan tidak terkeluar dari sempadan bawah kad (Maksimum 5 baris)
    lines = lines[:5]
    
    # Melukis ulasan secara bersih, tajam dan teratur tanpa gangguan pertindihan huruf
    current_y = 175
    for line in lines:
        draw.text((60, current_y), line, fill=(15, 23, 42), font=font_ulasan)
        current_y += 38
        
    # Kaki kad visual
    draw.rectangle([60, 390, 740, 392], fill=(226, 232, 240))
    draw.text((60, 405), "Semak mesej mencurigakan anda di: antilolos.streamlit.app", fill=(148, 163, 184), font=font_small)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# Mengawal penukaran menu utama
menu = ["🔍 Pengesan Scam", "🎯 Ujian Kekebalan"]
choice = st.radio("Menu", menu, horizontal=True, label_visibility="collapsed")

# ==========================================
# SEGMEN 1: 🔍 PENGESAN SCAM (LOGIK CACHING + GEMINI)
# ==========================================
if choice == "🔍 Pengesan Scam":
    st.title("🛡️ AntiLolos")
    st.subheader("Jangan Biarkan Data & Wang Anda Lolos!")
    st.write("Tampal mesej WhatsApp, SMS, atau pautan mencurigakan untuk dianalisis oleh pakar siber AI.")

    user_input = st.text_area("Kotak Semakan Mesej:", placeholder="Contoh: Tahniah! Anda terpilih menerima bantuan khas RM500. Sila sahkan di pautan...", height=130)
    
    if st.button("Semak Mesej Ini", type="primary"):
        if not user_input.strip():
            st.warning("Sila masukkan teks mesej terlebih dahulu.")
        else:
            with st.spinner("AntiLolos AI sedang mengimbas corak penipuan siber..."):
                
                # Memeriksa pangkalan data komuniti (Supabase Caching - Huruf Kecil)
                db_query = supabase.table("scam_logs").select("*").eq("teks_laporan", user_input.strip()).execute()
                
                if db_query.data:
                    status = db_query.data[0]["klasifikasi_gemini"]
                    ulasan = db_query.data[0]["ulasan_ai"]
                    st.caption("💡 Hasil semakan pantas ditemui dalam memori pangkalan data komuniti (RM0 Kos API).")
                else:
                    try:
                        # Menggunakan model versi 2.5 flash yang aktif dan hijau kuotanya
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
                        
                        # Menyimpan data ancaman baharu ke dalam storan awan Supabase
                        supabase.table("scam_logs").insert({
                            "teks_laporan": user_input.strip(),
                            "klasifikasi_gemini": status,
                            "ulasan_ai": ulasan
                        }).execute()
                    except Exception as e:
                        st.error(f"Sistem mengalami kelengahan teknikal rangkaian. Ralat: {e}")
                        status = "RALAT"
                
                # Paparan keputusan mengikut klasifikasi siber
                if status == "SCAM BAHAYA":
                    st.markdown(f"<div class='scam-card'><h3>⚠️ AMARAN KRITIKAL: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                    
                    # Penjanaan imej fizikal automatik untuk perkongsian mudah orang tua
                    image_bytes = generate_warning_card(status, ulasan)
                    st.image(image_bytes, caption="Kad Amaran AntiLolos Visual")
                    st.download_button("⬇️ Download Kad Amaran Ini (Simpan Imej)", image_bytes, "Amaran_AntiLolos.png", "image/png")
                    
                    share_text = f"*🚨 PERISAI AMARAN ANTILOLOS 🚨*\nMesej disemak: _\"{user_input[:40]}...\"_\n*Keputusan AI:* ⚠️ {ulasan}\nSemak segera di: https://antilolos.streamlit.app"
                
                elif status == "SELAMAT":
                    st.markdown(f"<div class='safe-card'><h3>✅ STATUS KESELAMATAN: {status}</h3><p>{ulasan}</p></div>", unsafe_allow_html=True)
                    
                    image_bytes = generate_warning_card(status, ulasan)
                    st.image(image_bytes, caption="Kad Pengesahan AntiLolos Visual")
                    st.download_button("⬇️ Download Kad Pengesahan Ini", image_bytes, "Selamat_AntiLolos.png", "image/png")
                    
                    share_text = f"*ℹ️ INFO KESELAMATAN ANTILOLOS*\nMesej ini telah disemak dan disahkan *SELAMAT*.\nSemak di: https://antilolos.streamlit.app"
                
                if status != "RALAT":
                    encoded_text = urllib.parse.quote(share_text)
                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 20px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold;">➔ Kongsi Amaran Ini ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)

# ==========================================
# SEGMEN 2: 🎯 UJIAN KEKEBALAN (KUIZ PENUH)
# ==========================================
elif choice == "🎯 Ujian Kekebalan":
    st.title("🎯 Ujian Kekebalan Digital")
    st.write("Hadapi 10 senario rawak simulasi ancaman harian. Adakah benteng pertahanan digital anda kukuh?")
    
    # Himpunan lengkap 10 Soalan dengan pilihan jawapan komprehensif bagi melatih ketahanan siber
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

    # Menguruskan pergerakan kuiz rawak menggunakan session_state
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
                <h2 style='margin: 0; color: #1e293b;'>🛡️ KAD LAPORAN ANTILOLOS</h2>
                <h1 style='color: #ef4444; font-size: 54px; margin: 15px 0;'>Risiko: {total}%</h1>
                <h4 style='margin-bottom: 15px; font-weight: bold;'>{status}</h4>
                <p style='font-size: 16px; text-align: justify; color: #475569;'>{ulasan}</p>
            </div>
        """, unsafe_allow_html=True)
        
        kuiz_share_text = f"*🚨 UJIAN KEKEBALAN DIGITAL #ANTILOLOS 🚨*\nKeputusan Skor Risiko Saya: *{total}%*\n*Klasifikasi Kesedaran:* {status}\n\nJangan tunggu sehingga simpanan bocor. Jom uji ketahanan mental siber anda sekarang di: https://antilolos.streamlit.app"
        encoded_kuiz_text = urllib.parse.quote(kuiz_share_text)
        whatsapp_kuiz_url = f"https://api.whatsapp.com/send?text={encoded_kuiz_text}"
        
        st.write("---")
        st.markdown(f'<a href="{whatsapp_kuiz_url}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 20px; width: 100%; cursor: pointer; font-size: 16px; font-weight: bold;">➔ Kongsi Keputusan Kuiz ke WhatsApp Keluarga</button></a>', unsafe_allow_html=True)
        
        if st.button("Ulang Semula Ujian", use_container_width=True):
            del st.session_state.soalan_shuffled
            st.session_state.soalan_semasa = 0
            st.session_state.skor_risiko = 0
            st.session_state.kuiz_tamat = False
            st.rerun()
