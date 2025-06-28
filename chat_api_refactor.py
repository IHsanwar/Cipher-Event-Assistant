from flask import request, jsonify, session
import markdown
import traceback
import openai
import json

from prompt import cipher_prompt
from helpers import tool_definitions, submit_survey

# ===== Helper functions =====

def prepare_user_data():
    data = request.json
    if not data:
        raise ValueError("No JSON data provided")

    user_input = data.get("message", "")
    if user_input is None:
        user_input = ""
    return user_input.strip()

def build_openai_messages(user_input: str):
    username = session.get("username", "Pengunjung") or "Pengunjung"
    session.permanent = True

    history = session.get("chat_history", []) or []
    prompt = cipher_prompt.format(username=username)

    history.append({"role": "user", "content": user_input})
    return [{"role": "system", "content": prompt}] + history, history

def call_openai(messages):
    return openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
        tools=tool_definitions
    )

def handle_tool_call(tool_call):
    if isinstance(tool_call, list) and tool_call:
        function_call = tool_call[0].get("function", {})
    else:
        function_call = tool_call or {}

    function_name = function_call.get("name")
    args_raw = function_call.get("arguments", "{}")
    args = json.loads(args_raw) if args_raw else {}

    if function_name == "submit_survey":
        required_fields = [
            "nama", "instansi", "tampilan_produk", "tampilan_stand",
            "penjelasan_produk", "hiburan", "kritik_saran"
        ]
        missing = [f for f in required_fields if not str(args.get(f, '')).strip()]
        if missing:
            return f"❌ Data tidak lengkap. Field kosong: {missing}"
        return submit_survey(**args)

    return f"❌ Fungsi tidak dikenali: {function_name}"

def convert_markdown_to_html(text: str) -> str:
    md = markdown.Markdown(extensions=[
        'codehilite', 'fenced_code', 'tables', 'nl2br',
        'sane_lists', 'smarty', 'toc', 'attr_list',
        'def_list', 'footnotes', 'admonition'
    ], extension_configs={
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,
            'noclasses': True
        }
    })
    return md.convert(text)

# ===== Main chat endpoint =====

def handle_chat():
    try:
        user_input = prepare_user_data()
        messages, history = build_openai_messages(user_input)
        response = call_openai(messages)

        choice = response['choices'][0]
        finish_reason = choice.get('finish_reason')
        message = choice.get("message", {})
        tool_call = message.get("tool_calls") or message.get("function_call")

        if tool_call:
            reply = handle_tool_call(tool_call)
        else:
            content = message.get("content")
            reply = content.strip() if content else "❌ Respon kosong dari OpenAI"

        history.append({"role": "assistant", "content": reply})
        session["chat_history"] = history
        session.modified = True

        reply_html = convert_markdown_to_html(reply)

        return jsonify({
            "reply": reply,
            "reply_html": reply_html,
            "history_length": len(history),
            "debug": {
                "finish_reason": finish_reason,
                "has_tool_call": bool(tool_call),
                "content_length": len(reply)
            }
        })

    except openai.error.OpenAIError as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return jsonify({"error": f"OpenAI API Error: {str(e)}"}), 500
    except Exception as e:
        print(f"❌ Error in chat: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
