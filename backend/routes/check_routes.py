from flask import Blueprint, request, jsonify, g
from models.spell_model import SpellChecker
from database.history_dao import save_history, get_history, delete_history_item, delete_all_history
from datetime import datetime
from middleware.jwt_middleware import jwt_required
import os
from dotenv import load_dotenv

load_dotenv()

check_routes = Blueprint("check_routes", __name__)
checker = SpellChecker()
MAX_LENGTH = 5000


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

    save_history(text, response, lang, g.username)

    return jsonify(response)


@check_routes.route("/history", methods=["GET"])
@jwt_required
def history():
    limit = request.args.get("limit", 20, type=int)
    items = get_history(limit=limit, username=g.username)
    return jsonify({"history": items})


@check_routes.route("/history/<item_id>", methods=["DELETE"])
@jwt_required
def delete_history_by_id(item_id):
    success = delete_history_item(item_id, username=g.username)
    if success:
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"error": "Item not found or unauthorized"}), 404


@check_routes.route("/history/all", methods=["DELETE"])
@jwt_required
def delete_all_history_route():
    count = delete_all_history(username=g.username)
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
    from config import get_gemini_keys
    keys = get_gemini_keys()

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
                model="gemini-2.5-flash",
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


# ─────────────────────────────────────────────
#  SUMMARIZE — Tóm tắt văn bản
# ─────────────────────────────────────────────
@check_routes.route("/summarize", methods=["POST"])
@jwt_required
def summarize():
    import json
    from google import genai as gemini
    from config import get_gemini_keys

    data = request.json or {}
    text = data.get("text", "").strip()
    length = data.get("length", "medium")   # short | medium | long
    lang   = data.get("lang", "en")

    if not text:
        return jsonify({"error": "Text is required"}), 400
    if len(text) < 50:
        return jsonify({"error": "Text too short to summarize (min 50 chars)"}), 400

    length_map = {
        "short":  "1–2 sentences (max 40 words)",
        "medium": "3–5 sentences (max 100 words)",
        "long":   "a structured paragraph (max 200 words) with key points as bullet list"
    }
    length_desc = length_map.get(length, length_map["medium"])
    reply_lang  = "Vietnamese" if lang == "vi" else "the same language as the input text"

    prompt = f"""You are a professional summarizer. Summarize the following text in {reply_lang}.
Summary length: {length_desc}.
Rules:
- Capture ALL key ideas — do not omit important points
- Write in clear, neutral prose
- If length is "long", add a bullet-point key takeaways section after the paragraph
- Do NOT copy sentences verbatim
Return ONLY this JSON (no markdown):
{{
    "summary": "the summary text",
    "key_points": ["point 1", "point 2"],
    "word_count_original": 0,
    "word_count_summary": 0,
    "reduction_percent": 0
}}

Text:
{text[:6000]}"""

    from config import get_gemini_keys
    keys = get_gemini_keys()
    last_error = "No API keys"

    for api_key in keys:
        try:
            client = gemini.Client(api_key=api_key)
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            raw = res.text.strip().strip("```json").strip("```").strip()
            result = json.loads(raw)
            # Tính word count thực tế nếu AI không trả
            orig_wc = len(text.split())
            summ_wc = len(result.get("summary","").split())
            result["word_count_original"] = orig_wc
            result["word_count_summary"]  = summ_wc
            result["reduction_percent"]   = round((1 - summ_wc / max(orig_wc,1)) * 100)
            return jsonify(result)
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({"error": f"AI unavailable: {last_error}"}), 503


# ─────────────────────────────────────────────
#  PARAPHRASE — Viết lại tránh đạo văn
# ─────────────────────────────────────────────
@check_routes.route("/paraphrase", methods=["POST"])
@jwt_required
def paraphrase():
    import json
    from google import genai as gemini
    from config import get_gemini_keys

    data = request.json or {}
    text   = data.get("text", "").strip()
    mode   = data.get("mode", "standard")   # standard | creative | formal | simple
    lang   = data.get("lang", "en")

    if not text:
        return jsonify({"error": "Text is required"}), 400
    if len(text) < 10:
        return jsonify({"error": "Text too short"}), 400

    mode_instructions = {
        "standard": "Rewrite using different vocabulary and sentence structures while keeping the exact meaning. Aim for ~same length.",
        "creative":  "Rewrite with creative flair — vary rhythm, use vivid language, make it more engaging. Same meaning, more personality.",
        "formal":    "Rewrite in formal academic/professional register. Use precise terminology, no contractions or casual phrasing.",
        "simple":    "Rewrite using simple, everyday language. Short sentences, common words, easy to understand for any reader."
    }
    instruction = mode_instructions.get(mode, mode_instructions["standard"])
    reply_lang  = "Vietnamese" if lang == "vi" else "the same language as the input"

    prompt = f"""You are a paraphrasing expert. {instruction}
Reply in {reply_lang}.
Rules:
- Change at least 70% of the words
- Do NOT change the core meaning
- Provide 2 alternative versions so the user can choose
Return ONLY this JSON (no markdown):
{{
    "version_1": "first paraphrased version",
    "version_2": "second paraphrased version (noticeably different from version 1)",
    "similarity_reduced": true,
    "changes_made": "brief description of what changed (vocabulary, structure, tone)"
}}

Original text:
{text[:3000]}"""

    keys = get_gemini_keys()
    last_error = "No API keys"

    for api_key in keys:
        try:
            client = gemini.Client(api_key=api_key)
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            raw = res.text.strip().strip("```json").strip("```").strip()
            return jsonify(json.loads(raw))
        except Exception as e:
            last_error = str(e)
            continue

    return jsonify({"error": f"AI unavailable: {last_error}"}), 503


# ─────────────────────────────────────────────
#  DIFF — So sánh trước / sau
# ─────────────────────────────────────────────
@check_routes.route("/diff", methods=["POST"])
@jwt_required
def diff():
    import difflib, html

    data = request.json or {}
    original  = data.get("original", "")
    corrected = data.get("corrected", "")

    if not original or not corrected:
        return jsonify({"error": "Both original and corrected texts are required"}), 400

    # Word-level diff
    orig_words = original.split()
    corr_words = corrected.split()

    matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
    orig_html, corr_html = [], []
    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        orig_chunk = " ".join(orig_words[i1:i2])
        corr_chunk = " ".join(corr_words[j1:j2])

        if tag == "equal":
            safe = html.escape(orig_chunk)
            orig_html.append(safe)
            corr_html.append(safe)
        elif tag == "replace":
            orig_html.append(f'<mark class="diff-removed">{html.escape(orig_chunk)}</mark>')
            corr_html.append(f'<mark class="diff-added">{html.escape(corr_chunk)}</mark>')
            changes.append({"type": "replace", "from": orig_chunk, "to": corr_chunk})
        elif tag == "delete":
            orig_html.append(f'<mark class="diff-removed">{html.escape(orig_chunk)}</mark>')
            changes.append({"type": "delete", "from": orig_chunk, "to": ""})
        elif tag == "insert":
            corr_html.append(f'<mark class="diff-added">{html.escape(corr_chunk)}</mark>')
            changes.append({"type": "insert", "from": "", "to": corr_chunk})

    orig_wc = len(orig_words)
    corr_wc = len(corr_words)

    return jsonify({
        "original_html":  " ".join(orig_html),
        "corrected_html": " ".join(corr_html),
        "changes":        changes,
        "stats": {
            "total_changes":   len(changes),
            "replacements":    sum(1 for c in changes if c["type"] == "replace"),
            "deletions":       sum(1 for c in changes if c["type"] == "delete"),
            "insertions":      sum(1 for c in changes if c["type"] == "insert"),
            "words_before":    orig_wc,
            "words_after":     corr_wc,
            "word_delta":      corr_wc - orig_wc,
        }
    })