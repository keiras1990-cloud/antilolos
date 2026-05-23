import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from supabase import create_client
import json

def jalankan_ejen_scraper_multi_agensi():
    print("🚀 Mula mengerahkan Ejen AntiLolos...")
    
    # 1. Mengambil kunci keselamatan di dalam fungsi keselamatan
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # Semakan awal: Jika ada kunci yang tertinggal di GitHub Secrets
    if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_API_KEY:
        print("❌ RALAT KRITIKAL: Kunci rahsia (Secrets) tidak dijumpai di GitHub Settings!")
        print(f"👉 STATUS - SUPABASE_URL: {'Ada' if SUPABASE_URL else 'TIADA'}")
        print(f"👉 STATUS - SUPABASE_KEY: {'Ada' if SUPABASE_KEY else 'TIADA'}")
        print(f"👉 STATUS - GEMINI_API_KEY: {'Ada' if GEMINI_API_KEY else 'TIADA'}")
        return

    try:
        # 2. Membina sambungan selamat di dalam kawasan kawalan ralat
        print("🔌 Menghubungkan talian ke Supabase & Google AI Studio...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Trend data ancaman mega terbaharu
        entiti_mentah_terkumpul = [
            "Quantum Metal Gold", "Pelaburan Saham Klon VIP", "Job Scam TikTok",
            "APK e-Invois LHDN", "Pautan Bantuan STR .xyz", "Saman PDRM .cc",
            "Crypto VIP Telegram", "Bungkusan Pos Laju Dadah", "Along Online", "Netflix Phishing"
        ]

        print("🧠 Memanggil Gemini 2.5 Flash untuk memproses ulasan warga emas...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt_scraper = """
        Berikut adalah senarai entiti/taktik penipuan: {}. 
        Bagi setiap satu, jana ulasan amaran siber dalam Bahasa Melayu yang ringkas, kasual, dan mudah difahami warga emas. 
        Output WAJIB dalam bentuk JSON Array bersih tanpa markdown dengan struktur objek ini sahaja:
        [{"teks_laporan": "NAMA", "klasifikasi_gemini": "SCAM BAHAYA", "ulasan_ai": "ULASAN"}]
        """.format(entiti_mentah_terkumpul)
        
        response_ai = model.generate_content(prompt_scraper)
        
        # Pembersihan blok teks janaan AI
        json_text = response_ai.text.replace("```json", "").replace("```", "").strip()
        data_scam_baharu = json.loads(json_text)
        
        kes_baru_ditambah = 0
        for kes in data_scam_baharu:
            # Semakan penduaan data sebelum disimpan
            semak = supabase.table("scam_logs").select("id").eq("teks_laporan", kes["teks_laporan"]).execute()
            if not semak.data:
                supabase.table("scam_logs").insert({
                    "teks_laporan": kes["teks_laporan"],
                    "klasifikasi_gemini": "SCAM BAHAYA",
                    "ulasan_ai": kes["ulasan_ai"]
                }).execute()
                kes_baru_ditambah += 1
                print(f"✅ Berjaya mengunci masuk kes: {kes['teks_laporan']}")
                
        print(f"🏁 Operasi Sukses! {kes_baru_ditambah} data baharu telah selamat dimasukkan ke Supabase.")
        
    except Exception as e:
        print(f"❌ Ralat operasi berlaku di dalam kod: {e}")

if __name__ == "__main__":
    jalankan_ejen_scraper_multi_agensi()
