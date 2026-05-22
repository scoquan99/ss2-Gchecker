from flask import Blueprint, request, jsonify
from models.spell_model import SpellChecker
from database.history_dao import save_history, get_history, delete_history_item, delete_all_history
from datetime import datetime
from middleware.jwt_middleware import jwt_required
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")

check_routes = Blueprint("check_routes", __name__)
checker = SpellChecker()
MAX_LENGTH = 5000


def get_username_from_token(request):
    try:
        auth = request.headers.get("Authorization", "")
        token = auth.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("username")
    except Exception:
        return None


@check_routes.route("/check", methods=["POST"])
@jwt_required
def check():
    data = request.json
    text = data.get("text", "")
    lang = data.get("lang", "en-US")
    mode = data.get("mode", "basic")
    tone = data.get("tone", "Professional")
    
    print(f"DEBUG - Received mode: {mode}, tone: {tone}")

    if text.strip() == "":
        return jsonify({"error": "Text cannot be empty"}), 400
    if len(text) > MAX_LENGTH:
        return jsonify({"error": "Text exceeds 5000 characters"}), 400

    result = checker.analyze_text(text, lang, mode=mode, tone=tone)

    spelling_errors = len(text.split()) - len(result["corrected_text"].split())
    grammar_count   = len(result["grammar_errors"])
    style_count     = len(result["style_errors"])
    total_errors    = spelling_errors + grammar_count + style_count
    quality_score   = max(0, 100 - total_errors * 5)

    response = {
        "original_text":    text,
        "corrected_text":   result["corrected_text"],
        "highlighted_text": result["highlighted_text"],
        "grammar_errors":   result["grammar_errors"],
        "style_errors":     result["style_errors"],
        "lang":             lang,
        "mode":             mode,
        "ai_analysis":      result.get("ai_analysis"),
        "stats":            result.get("stats"),
        "summary": {
            "spelling": spelling_errors,
            "grammar":  grammar_count,
            "style":    style_count,
            "total":    total_errors,
            "score":    quality_score
        },
        "created_at": str(datetime.now())
    }

    username = get_username_from_token(request)
    save_history(text, response, lang, username)

    return jsonify(response)


@check_routes.route("/history", methods=["GET"])
@jwt_required
def history():
    username = get_username_from_token(request)
    limit = request.args.get("limit", 20, type=int)
    items = get_history(limit=limit, username=username)
    return jsonify({"history": items})


@check_routes.route("/history/<item_id>", methods=["DELETE"])
@jwt_required
def delete_history_by_id(item_id):
    username = get_username_from_token(request)
    success = delete_history_item(item_id, username=username)
    if success:
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"error": "Item not found or unauthorized"}), 404


@check_routes.route("/history/all", methods=["DELETE"])
@jwt_required
def delete_all_history_route():
    username = get_username_from_token(request)
    count = delete_all_history(username=username)
    return jsonify({"message": f"Deleted {count} items"})


@check_routes.route("/thesaurus", methods=["POST"])
@jwt_required
def thesaurus():
    from nltk.corpus import wordnet
    data = request.json
    word = data.get("word", "").strip()
    if not word:
        return jsonify({"error": "Word is required"}), 400

    synonyms, antonyms = set(), set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
            if lemma.antonyms():
                antonyms.add(lemma.antonyms()[0].name().replace("_", " "))

    synonyms.discard(word)
    return jsonify({
        "synonyms": list(synonyms)[:15],
        "antonyms": list(antonyms)[:10]
    })


@check_routes.route("/capitalize", methods=["POST"])
@jwt_required
def capitalize():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    stop_words = {"a","an","the","and","but","or","for","nor","on","at","to","by","in","of","up","as"}
    words = text.split()
    result = []
    for i, w in enumerate(words):
        if i == 0 or i == len(words)-1 or w.lower() not in stop_words:
            result.append(w.capitalize())
        else:
            result.append(w.lower())
    return jsonify({"capitalized": " ".join(result)})


@check_routes.route("/ai_detect", methods=["POST"])
@jwt_required
def ai_detect():
    data = request.json
    text = data.get("text", "").strip()
    
    if not text or len(text) < 30:
        return jsonify({"ai_probability": 25, "reasoning": "Văn bản quá ngắn."})

    # Danh sách các key
    keys = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3")
    ]
    keys = [k for k in keys if k and len(k.strip()) > 15]  # Lọc key hợp lệ

    if not keys:
        return jsonify({"ai_probability": 35, "reasoning": "Không tìm thấy GEMINI_API_KEY nào."})

    for i, api_key in enumerate(keys):
        try:
            from google import genai as g
            import json
            
            client = g.Client(api_key=api_key)
            
            prompt = f"""
Phân tích xem văn bản sau có phải do AI tạo ra hay không.
Trả về chỉ JSON, không thêm gì khác:

{{"ai_probability": 70, "reasoning": "Giải thích ngắn gọn bằng tiếng Việt"}}

Văn bản: {text[:6000]}
"""

            res = client.models.generate_content(
                model="gemini-2.0-flash",   # hoặc gemini-2.0-flash
                contents=prompt
            )
            
            raw = res.text.strip().strip("```json").strip("```").strip()
            result = json.loads(raw)
            print(f"AI Detect thanh cong voi key {i+1}")
            return jsonify(result)

        except Exception as e:
            error_str = str(e).lower()
            print(f"Key {i+1} loi: {error_str[:100]}")
            last_error = str(e)
            continue  # Thử key tiếp theo

    # Nếu tất cả key đều lỗi
    return jsonify({"error": f"All API keys failed. Last error: {last_error}"}), 500