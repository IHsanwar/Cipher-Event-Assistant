from flask import Flask, request, jsonify, session
from flask_cors import CORS
import openai
from config import OPENAI_API_KEY, APP_SECRET_KEY
from prompt import cipher_prompt
import markdown

#configure
app = Flask(__name__)

CORS(app, supports_credentials=True)
app.secret_key = APP_SECRET_KEY
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=False  # karena kamu pakai HTTP lokal
)


openai.api_key = OPENAI_API_KEY
def create_enhanced_renderer():
    """Create a custom renderer with better styling"""
    class CustomRenderer(mistune.HTMLRenderer):
        def block_code(self, code, info=None):
            # Enhanced code blocks with language detection
            lang_class = f' class="language-{info}"' if info else ''
            return f'<div class="code-block-wrapper"><pre><code{lang_class}>{mistune.escape(code)}</code></pre></div>'
        
        def blockquote(self, text):
            return f'<blockquote class="chat-quote">{text}</blockquote>'
        
        def table(self, text):
            return f'<div class="table-wrapper"><table class="chat-table">{text}</table></div>'
        
        def list_item(self, text):
            return f'<li class="chat-list-item">{text}</li>'
    
    return mistune.create_markdown(
        renderer=CustomRenderer(),
        plugins=['strikethrough', 'footnotes', 'table', 'task_lists', 'def_list']
    )
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
    username = session.get("username")
    prompt = cipher_prompt.format(username=username)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ]
        )
        reply_markdown = response['choices'][0]['message']['content']

        md = markdown.Markdown(extensions=[
            'codehilite',           # Syntax highlighting for code blocks
            'fenced_code',          # ```code``` blocks
            'tables',               # Table support
            'nl2br',                # Convert newlines to <br>
            'sane_lists',           # Better list handling
            'smarty',               # Smart quotes and dashes
            'toc',                  # Table of contents
            'attr_list',            # Add attributes to elements
            'def_list',             # Definition lists
            'footnotes',            # Footnote support
            'admonition',           # Note/warning boxes
        ], extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
                'noclasses': True,  # Inline styles for better compatibility
            }
        })
        reply_html = md.convert(reply_markdown)
        print("Session username:", session.get("username"))
        return jsonify({
            "reply": reply_markdown,
            "reply_html": reply_html
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
