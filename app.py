from flask import Flask, request, jsonify, session
from flask_cors import CORS
import openai
from config import OPENAI_API_KEY
from prompt import cipher_prompt

app = Flask(__name__)
CORS(app)
app.secret_key = "cipher-secret"  # dibutuhkan untuk menyimpan sesi nama

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
    data = request.json
    user_input = data.get("message", "").strip()
    username = session.get("username", "Barts")  # fallback ke 'Barts' jika belum diatur

    prompt = cipher_prompt.format(username=username)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
