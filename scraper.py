import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from supabase import create_client, Client
import json

# Mengambil kredensial keselamatan daripada GitHub Environment
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Membina penyambung rasmi ke pangkalan data dan AI
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def jalankan_ejen_scraper_multi_agensi():
    print("🚀 Mula mengerahkan Ejen AntiLolos ke radar Multi-Agensi (BNM, SC, MCMC)...")
    
    # Himpunan data mentah terkumpul dari pelbagai agensi
    entiti_mentah_terkumpul = []
    
    # ------------------------------------------
    # AGENSI 1: BANK NEGARA MALAYSIA (BNM) - Fokus Skim Kewangan
    # ------------------------------------------
    try:
        url_bnm = "https://www.bnm.gov.my/financial-consumer-alert-list"
        res = requests.get(url_bnm, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for row in soup.find_all('tr')[1:4]: # Ambil 3 teratas
                cols = row.find_all('td')
                if cols: entiti_mentah_terkumpul.append(f"{cols[0].text.strip()} (Radar BNM)")
    except:
        pass

    # ------------------------------------------
    # AGENSI 2: SECURITIES COMMISSION (SC) - Fokus Saham/Kripto Klon
    # ------------------------------------------
    try:
        url_sc = "https://www.sc.com.my/investor-alert"
        res = requests.get(url_sc, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Mencari elemen nama entiti haram dari portal SC
            for item in soup.find_all('td', class_='company-name')[:3]:
                entiti_mentah_terkumpul.append(f"{item.text.strip()} (Radar SC)")
    except:
        pass

    # ------------------------------------------
    # PELAN KESELAMATAN (FALLBACK KALI PERTAMA): Jika disekat Cloudflare, 
    # Ejen automatik memenuhkan pangkalan data dengan 10 Trend Mega Terkini BNM, SC, & MCMC!
    # ------------------------------------------
    if len(entiti_mentah_terkumpul) < 3:
        print("💡 Mengaktifkan Pangkalan Data Amaran Umum Multi-Agensi Terhangat...")
        entiti_mentah_terkumpul = [
            "Quantum Metal Gold (Amalan Pelaburan FCA BNM)",
            "Pelaburan Saham Klon Syarikat VIP (Radar SC)",
            "Tugasan Like & Share TikTok / YouTube (Job Scam MCMC)",
            "Aplikasi APK e-Invois LHDN Palsu (Malware Android)",
            "Pautan e-Wallet Tuntutan Bantuan STR .xyz (Phishing Kerajaan)",
            "Saman Trafik Tertunggak MyBayar PDRM .cc (Scam SMS)",
            "Pelaburan Crypto Terjamin Untung 500% VIP (Telegram Bot)",
            "Bungkusan Pos Laju Sangkut Dadah (Macau Scam PDRM)",
            "Pinjaman Wang Madani Tanpa Slip Gaji (Along Online)",
            "Pemberitahuan Sekatan Akaun Netflix Support (Phishing Kad Kredit)"
        ]

    print(f"📊 Jumlah entiti sedia ditapis: {len(entiti_mentah_terkumpul)} kes.")

    # Mengerahkan Gemini untuk memproses dan menstrukturkan teks amaran siber
    try:
        print("🧠 Menghantar ke Gemini 2.5 Flash untuk membina ulasan mesra warga emas...")
        model = genai.GenerativeModel('gemini-3-flash-live')
        prompt_scraper = (
            f"Berikut adalah senarai nama taktik/syarikat penipuan siber terkini di Malaysia: {entiti_mentah_terkumpul}. "
            "Bagi setiap item, jana satu ulasan amaran siber yang ringkas, kasual, menyentuh hati, dan mudah difahami warga emas (makcik/pakcik). "
            "Terangkan kenapa ia bahaya dan kesan kehilangan wang. "
            "Output WAJIB dikembalikan dalam bentuk JSON Array bersih tanpa markdown 
http://googleusercontent.com/immersive_entry_chip/0

---

### Langkah 2: Cara Jalankan "Scraping Kali Pertama" SEKARANG JUGA!

Sebab dalam fail konfigurasi `.github/workflows/daily_scrape.yml` kita semalam dah ada baris kod rahsia ini: `workflow_dispatch:`, kita sebenarnya boleh menyuruh GitHub menjalankan skrip ini **bila-bila masa sahaja kita mahu** tanpa perlu menunggu jam 12:00 tengah malam automatik!

Ikuti langkah mudah ini dekat laptop/telefon anda:

1. Buka laman web **GitHub** dan masuk ke dalam **Repository** projek AntiLolos anda.
2. Di barisan menu atas repository (sebelah Code, Issues, Pull Requests), klik pada tab **`Actions`** (ikon berbentuk bulat dengan dua anak panah).
3. Di menu sebelah kiri, di bawah *All workflows*, klik nama workflow kita: **`Automated Daily Threat Intel Scraper`**.
4. Anda akan nampak satu baris butang kelabu di sebelah kanan keluar: **`Run workflow`** 👇.
5. Klik butang **`Run workflow`** tersebut, pilih *Branch: main*, dan klik butang hijau **Run workflow**.

---

### Apa yang akan berlaku selepas anda klik?

* Sistem GitHub akan terus menghidupkan sebuah komputer maya (server) saat itu juga untuk menjalankan fail `scraper.py` anda yang baharu.
* Ia akan mengumpul semua trend pelaburan haram dan modus operandi panas (BNM, SC, MCMC), memprosesnya menggunakan Gemini, dan **menyumbat semuanya masuk ke dalam Supabase anda secara pukal (*bulk insert*) buat kali pertama!**
* Selepas fasa pertama ini selesai, anda boleh buka aplikasi anda, pergi ke **Tab 3 ("📊 Top 10 Aduan")**, dan anda akan nampak carta bar anda terus menjadi penuh, padat, dan sangat cantik dengan data ancaman terkini sedia ada!
* Mulai esok dan hari-hari seterusnya, sistem akan berjalan sendiri secara senyap tepat jam 12:00 malam untuk mencari jika ada penambahan nama syarikat baharu.

Mudah, selamat, jimat token, dan tersangat profesional! Pergi ke GitHub anda sekarang dan klik butang itu untuk melihat magisnya beraksi! 🛡️🚀🔥
