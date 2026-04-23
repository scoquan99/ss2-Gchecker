from flask import Blueprint, request, jsonify
from models.spell_model import SpellChecker
from database.history_dao import save_history, get_history
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
    """Lấy username từ JWT token trong header"""
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

    if text.strip() == "":
        return jsonify({"error": "Text cannot be empty"}), 400
    if len(text) > MAX_LENGTH:
        return jsonify({"error": "Text exceeds 5000 characters"}), 400

    result = checker.analyze_text(text, lang)

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
    import string
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    # AP style: capitalize tất cả trừ articles/prepositions ngắn
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
    if not text:
        return jsonify({"error": "Text is required"}), 400

    from google import genai as g
    import os
    c = g.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"""Analyze if this text was written by AI or a human.
Return ONLY this JSON, no explanation:
{{"ai_probability": 75, "reasoning": "brief explanation"}}
Text: {text}"""
    try:
        res = c.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        import json, re
        raw = res.text.strip().strip("```json").strip("```").strip()
        data_out = json.loads(raw)
        return jsonify(data_out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500