from flask import Blueprint, request, jsonify
from models.spell_model import SpellChecker
from database.history_dao import save_history
from datetime import datetime
from middleware.jwt_middleware import jwt_required

check_routes = Blueprint("check_routes", __name__)

checker = SpellChecker()

MAX_LENGTH = 5000

@check_routes.route("/check", methods=["POST"])
@jwt_required
def check():

    data = request.json
    text = data.get("text","")

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
        "created_at": str(datetime.now())
    }

    save_history(text, response)
    return jsonify(response)