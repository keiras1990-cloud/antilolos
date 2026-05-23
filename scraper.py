import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from supabase import create_client
import json

def jalankan_ejen_scraper_multi_agensi():
    print("🚀 Mula mengerahkan Ejen AntiLolos...")
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_API_KEY:
        print("❌ RALAT KRITIKAL: Kunci rahsia (Secrets) tidak dijumpai di GitHub Settings!")
        return

    try:
        print("🔌 Menghubungkan talian ke Supabase & Google AI Studio...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Trend data ancaman mega terbaharu
        entiti_mentah_terkumpul = [
            "Quantum Metal Gold", "Pelaburan Saham Klon VIP", "Job Scam TikTok",
            "APK e-Invois LHDN", "Pautan Bantuan STR .xyz", "Saman PDRM .cc",
            "Crypto VIP Telegram", "Bungkusan Pos Laju Dadah", "Along Online", "Netflix Phishing"
        ]

        print("🧠 Memanggil Gemini 2.5 Flash dengan mod JSON Tulen...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt_scraper = """
        Berikut adalah senarai entiti/taktik penipuan: {}. 
        Bagi setiap satu, jana ulasan amaran siber dalam Bahasa Melayu yang ringkas, kasual, dan mudah difahami warga emas. 
        Output WAJIB dalam bentuk JSON Array dengan struktur objek ini:
        [{"teks_laporan": "NAMA", "klasifikasi_gemini": "SCAM BAHAYA", "ulasan_ai": "ULASAN"}]
        """.format(entiti_mentah_terkumpul)
        
        # Menggunakan konfigurasi khas untuk memaksa output JSON sistem yang sah
        response_ai = model.generate_content(
            prompt_scraper,
            generation_config={"response_mime_type": "application/json"}
        )
        
        data_scam_baharu = json.loads(response_ai.text)
        
        kes_baru_ditambah = 0
        for kes in data_scam_baharu:
            # Taktik Kebal: Bersihkan sebarang tanda petik tersesat pada nama 'key' jika ada
            kes_clean = {str(k).replace('"', '').replace("'", "").strip(): v for k, v in kes.items()}
            
            teks_laporan = kes_clean.get("teks_laporan")
            ulasan_ai = kes_clean.get("ulasan_ai")
            klasifikasi = kes_clean.get("klasifikasi_gemini", "SCAM BAHAYA")

            if not teks_laporan or not ulasan_ai:
                continue # Abaikan rekod jika rosak
            
            # Semak penduaan data sebelum disimpan
            semak = supabase.table("scam_logs").select("id").eq("teks_laporan", teks_laporan).execute()
            if not semak.data:
                supabase.table("scam_logs").insert({
                    "teks_laporan": teks_laporan,
                    "klasifikasi_gemini": klasifikasi,
                    "ulasan_ai": ulasan_ai
                }).execute()
                kes_baru_ditambah += 1
                print(f"✅ Berjaya mengunci masuk kes: {teks_laporan}")
                
        print(f"🏁 Operasi Sukses! {kes_baru_ditambah} data baharu telah selamat dimasukkan ke Supabase.")
        
    except Exception as e:
        print(f"❌ Ralat operasi berlaku di dalam kod: {e}")

if __name__ == "__main__":
    jalankan_ejen_scraper_multi_agensi()
