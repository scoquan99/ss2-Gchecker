from flask import Blueprint, request, jsonify
from middleware.jwt_middleware import jwt_required
import os
from dotenv import load_dotenv

load_dotenv()
chat_routes = Blueprint("chat_routes", __name__)

from config import get_gemini_keys

GEMINI_KEYS = get_gemini_keys()

SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên về viết lách và ngôn ngữ của ứng dụng "Lumina Text Studio".
Bạn giúp người dùng:
- Giải thích các lỗi ngữ pháp, chính tả, văn phong
- Gợi ý cách viết tốt hơn
- Trả lời câu hỏi về tiếng Anh, tiếng Việt và các ngôn ngữ khác
- Phân tích và cải thiện đoạn văn bản
Trả lời ngắn gọn, rõ ràng, thân thiện. Dùng ngôn ngữ phù hợp với câu hỏi (hỏi tiếng Việt → trả lời tiếng Việt)."""


@chat_routes.route("/chat", methods=["POST"])
@jwt_required
def chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    history = data.get("history", [])  # [{role, content}, ...]

    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    if len(user_message) > 2000:
        return jsonify({"error": "Message too long (max 2000 chars)"}), 400

    # Build conversation context (last 10 turns)
    context_turns = history[-10:] if history else []
    context_text = ""
    for turn in context_turns:
        role = "Người dùng" if turn.get("role") == "user" else "Trợ lý"
        context_text += f"{role}: {turn.get('content', '')}\n"
    context_text += f"Người dùng: {user_message}"

    prompt = f"{SYSTEM_PROMPT}\n\n--- Cuộc hội thoại ---\n{context_text}\n\nTrợ lý:"

    last_error = "No API keys available"
    for i, api_key in enumerate(GEMINI_KEYS):
        try:
            from google import genai as g
            client = g.Client(api_key=api_key)
            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            reply = res.text.strip()
            return jsonify({"reply": reply})
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({"error": f"AI unavailable: {last_error}"}), 503
