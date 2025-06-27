from langchain.tools import Tool
from datetime import datetime
import requests



def get_current_time(_):
    from datetime import datetime
    return f"Sekarang: {datetime.now()}" 

def get_wheather(kota):
    return "Cuaca di " + kota + " adalah cerah dengan suhu 30°C."
# helpers.py
def submit_survey(nama, instansi, tampilan_produk, tampilan_stand, penjelasan_produk, hiburan, kritik_saran):
    survey_data = {
        "nama": nama or "",
        "instansi": instansi or "",
        "tampilan_produk": tampilan_produk or "",
        "tampilan_stand": tampilan_stand or "",
        "penjelasan_produk": penjelasan_produk or "",
        "hiburan": hiburan or "",
        "kritik_saran": kritik_saran or ""
    }

    print("📩 Mengirim survey:", survey_data)

    try:
        res = requests.post("https://cipher.ihsanwd10.my.id/api/kirim-survey", json=survey_data)
        res.raise_for_status()
        return "✅ Survei kamu telah dikirim! Terima kasih!"
    except Exception as e:
        return f"❌ Gagal kirim survei: {str(e)}"



# Dictionary pemetaan nama tool ke fungsi
tool_functions = {
    "Survey": submit_survey,
}

# JSON untuk dikirim ke OpenAI

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "submit_survey",
            "description": "Mengirim data hasil survei ke sistem",
            "parameters": {
                "type": "object",
                "properties": {
                    "nama": {"type": "string"},
                    "instansi": {"type": "string"},
                    "tampilan_produk": {"type": "string"},
                    "tampilan_stand": {"type": "string"},
                    "penjelasan_produk": {"type": "string"},
                    "hiburan": {"type": "string"},
                    "kritik_saran": {"type": "string"}
                },
                "required": [
                    "nama", "instansi", "tampilan_produk", "tampilan_stand",
                    "penjelasan_produk", "hiburan", "kritik_saran"
                ]
            }
        }
        
    }
]

