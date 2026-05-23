import os
import json
import re
from supabase import create_client
import google.generativeai as genai

def jalankan_ejen_scraper_multi_agensi():
    print("🚀 Mula mengerahkan Ejen AntiLolos (Versi Ultimate)...")
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_API_KEY:
        print("❌ RALAT KRITIKAL: Kunci rahsia (Secrets) tak lengkap!")
        return

    try:
        print("🔌 Talian ke Supabase disambungkan...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Trend data ancaman
        entiti_mentah_terkumpul = [
            "Quantum Metal Gold", "Pelaburan Saham Klon VIP", "Job Scam TikTok",
            "APK e-Invois LHDN", "Pautan Bantuan STR .xyz", "Saman PDRM .cc",
            "Crypto VIP Telegram", "Bungkusan Pos Laju Dadah", "Along Online", "Netflix Phishing"
        ]

        # 1. UPGRADE KE GEMINI 3 FLASH!
        print("🧠 Memanggil Gemini 3 Flash...")
        model = genai.GenerativeModel('gemini-3-flash')
        
        # 2. PROMPT YANG KETAT (Elak ralat tanda petik)
        prompt_scraper = f"""
        Anda adalah pakar keselamatan siber. Berikan ulasan pendek, kasual, dan mudah difahami warga emas untuk setiap entiti scam berikut: {entiti_mentah_terkumpul}.
        
        SYARAT MUTLAK:
        1. Jangan letak backticks (```json).
        2. Jangan tambah sebarang ayat pendahuluan atau penutup.
        3. Gunakan format nama 'key' yang bersih tanpa double quotes berlebihan.
        4. Wajib pulangkan HANYA format JSON Array yang tepat seperti ini:
        [
          {{"teks_laporan": "Nama Scam", "klasifikasi_gemini": "SCAM BAHAYA", "ulasan_ai": "Ulasan anda di sini."}}
        ]
        """
        
        response_ai = model.generate_content(prompt_scraper)
        teks_mentah = response_ai.text
        
        print("📥 [LOG INTIP] Teks dipulangkan oleh AI:")
        print(teks_mentah)
        
        # 3. PENGEKSTRAK JSON KEBAL (Cari [ dan ])
        match = re.search(r'\[.*\]', teks_mentah, re.DOTALL)
        if match:
            json_bersih = match.group(0)
        else:
            json_bersih = teks_mentah.replace("```json", "").replace("```", "").strip()
            
        data_scam_baharu = json.loads(json_bersih)
        
        kes_baru_ditambah = 0
        for kes in data_scam_baharu:
            # 4. PEMBERSIH KEY DICTIONARY TOTAL (Settle ralat KeyError)
            kes_clean = {str(k).replace('"', '').replace("'", "").strip(): v for k, v in kes.items()}
            
            teks_laporan = kes_clean.get("teks_laporan")
            ulasan_ai = kes_clean.get("ulasan_ai")
            klasifikasi = kes_clean.get("klasifikasi_gemini", "SCAM BAHAYA")

            if not teks_laporan or not ulasan_ai:
                continue 
            
            # 5. MASUKKAN KE SUPABASE JIKA TIADA DUPLIKASI
            teks_laporan_clean = str(teks_laporan).strip()
            semak = supabase.table("scam_logs").select("id").eq("teks_laporan", teks_laporan_clean).execute()
            
            if not semak.data:
                supabase.table("scam_logs").insert({
                    "teks_laporan": teks_laporan_clean,
                    "klasifikasi_gemini": klasifikasi,
                    "ulasan_ai": ulasan_ai
                }).execute()
                kes_baru_ditambah += 1
                print(f"✅ Berjaya simpan: {teks_laporan_clean}")
                
        print(f"🏁 OPERASI SUKSES! {kes_baru_ditambah} data baharu telah selamat dikunci masuk.")
        
    except Exception as e:
        print(f"❌ Ralat operasi: {e}")

if __name__ == "__main__":
    jalankan_ejen_scraper_multi_agensi()
