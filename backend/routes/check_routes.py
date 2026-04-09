from flask import Blueprint, request, jsonify
from models.spell_model import SpellChecker
from models.ai_model import AIModel
from models.analytics import analyze_text_stats, get_synonyms_antonyms
from database.history_dao import save_history
from datetime import datetime
from middleware.jwt_middleware import jwt_required

check_routes = Blueprint("check_routes", __name__)

checker = SpellChecker()
ai_checker = AIModel()

MAX_LENGTH = 5000

@check_routes.route("/check", methods=["POST"])
@jwt_required
def check():

    data = request.json
    text = data.get("text","")
    mode = data.get("mode", "basic")
    tone = data.get("tone", "Academic and neutral")

    if text.strip() == "":
        return jsonify({"error":"Text cannot be empty"}),400

    if len(text) > MAX_LENGTH:
        return jsonify({"error":"Text exceeds 5000 characters"}),400

    result = checker.analyze_text(text)

    spelling_errors = len(text.split()) - len(result["corrected_text"].split())
    grammar_count = len(result["grammar_errors"])
    style_count = len(result["style_errors"])
    total_errors = spelling_errors + grammar_count + style_count
    quality_score = max(0, 100 - total_errors*5)

    response = {
        "original_text": text,
        "corrected_text": result["corrected_text"],
        "highlighted_text": result["highlighted_text"],
        "grammar_errors": result["grammar_errors"],
        "style_errors": result["style_errors"],
        "summary": {
            "spelling": spelling_errors,
            "grammar": grammar_count,
            "style": style_count,
            "total": total_errors,
            "score": quality_score
        },
        "mode": mode,
        "created_at": str(datetime.now())
    }

    response["stats"] = analyze_text_stats(text)

    if mode != "basic":
        ai_result = ai_checker.analyze(text, mode=mode, tone=tone)
        if "error" in ai_result:
            # Return 429 for quota exceeded, 500 for other errors
            status_code = 429 if ai_result.get("quota_exceeded") else 500
            return jsonify({"error": ai_result["error"]}), status_code
        response["ai_analysis"] = ai_result

    save_history(text, response)
    return jsonify(response)

@check_routes.route("/ai_detect", methods=["POST"])
@jwt_required
def ai_detect():
    data = request.json
    text = data.get("text","")
    if not text.strip():
        return jsonify({"error":"Text cannot be empty"}),400
    return jsonify(ai_checker.detect_ai(text))

@check_routes.route("/thesaurus", methods=["POST"])
@jwt_required
def thesaurus():
    data = request.json
    word = data.get("word","").strip()
    if not word:
        return jsonify({"error":"Word cannot be empty"}),400
    return jsonify(get_synonyms_antonyms(word))

@check_routes.route("/capitalize", methods=["POST"])
@jwt_required
def capitalize():
    try:
        import titlecase
    except ImportError:
        return jsonify({"error": "titlecase package not installed"}), 500
    
    data = request.json
    text = data.get("text","")
    if not text.strip():
        return jsonify({"error":"Text cannot be empty"}),400
    
    try:
        capitalized = titlecase.titlecase(text)
        return jsonify({"capitalized": capitalized})
    except Exception as e:
        return jsonify({"error": f"Error capitalizing text: {str(e)}"}), 500