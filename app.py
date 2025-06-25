from flask import Flask, request, jsonify, session
from flask_cors import CORS
import openai
from config import OPENAI_API_KEY, APP_SECRET_KEY
from prompt import cipher_prompt
from helpers import tool_definitions, tool_functions


from chat_api_refactor import handle_chat

#configure
app = Flask(__name__)

CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Your Next.js app
     supports_credentials=True,  # This is crucial for sessions
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"]
)

app.secret_key = APP_SECRET_KEY
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=False  # karena kamu pakai HTTP lokal
)


openai.api_key = OPENAI_API_KEY
@app.route("/api/setname", methods=["POST"])
def set_name():
    data = request.json
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"error": "Nama tidak boleh kosong"}), 400
    
    session["username"] = username
    return jsonify({"message": f"Halo {username}! Aku siap bantu kamu di Pekan IT 😊"})


@app.route("/api/chat", methods=["POST"])
def chat():
    return handle_chat()



@app.route("/api/clear-chat", methods=["POST"])
def clear_chat():
    session.pop("chat_history", None)
    session.modified = True
    return jsonify({"message": "Chat history cleared"})


MAX_LENGTHS = {
    "penjelasan_produk": 5,
    "nama": 50,
    "instansi": 50,
    "tampilan_produk": 10,
    "tampilan_stand": 10,
    "hiburan": 10,
    "kritik_saran": 255
}

def truncate_fields(data):
    for field, max_len in MAX_LENGTHS.items():
        if field in data:
            data[field] = str(data[field])[:max_len]
    return data

@app.route("/api/kirim-survey", methods=["POST"])
def kirim_survey():
    data = request.json

    if not data:
        return jsonify({"error": "Data tidak boleh kosong"}), 400

    # Potong jika terlalu panjang
    data = truncate_fields(data)

    required_fields = list(MAX_LENGTHS.keys())
    missing = [f for f in required_fields if not str(data.get(f, '')).strip()]
    if missing:
        return jsonify({"error": f"Field kosong/kurang: {missing}"}), 400

    try:
        response = requests.post("https://kuesioner-be.synchronizeteams.my.id/api/tamu/send", json=data)
        response.raise_for_status()
        return jsonify({"message": "Berhasil dikirim ke endpoint", "remote_response": response.json()})
    except requests.exceptions.RequestException as e:
        print("❌ HTTP Error:", e)
        return jsonify({"error": str(e), "detail": e.response.text if e.response else "No response body"}), 500

if __name__ == "__main__":
    app.run(debug=True)
