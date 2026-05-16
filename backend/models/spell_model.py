import language_tool_python
import language_tool_python.utils as lt_utils
from google import genai
import json
import os
import threading
import itertools
from dotenv import load_dotenv

load_dotenv()

# Rotate through available API keys
api_keys = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
api_keys = [k for k in api_keys if k and len(k.strip()) > 15]
api_key_cycle = itertools.cycle(api_keys) if api_keys else None
client = genai.Client(api_key=next(api_key_cycle)) if api_key_cycle else None

# Mode descriptions cho Gemini prompt
MODE_PROMPTS = {
    "style": """You are a style and tone editor. Analyze the text and:
1. Identify tone inconsistencies and informal language
2. Suggest improvements for the specified tone
3. Flag style issues (passive voice, wordiness, weak verbs)""",

    "structural": """You are a writing structure expert. Analyze the text and:
1. Evaluate sentence length variation
2. Check paragraph flow and transitions
3. Identify structural weaknesses""",

    "clarity": """You are a clarity and conciseness editor. Analyze the text and:
1. Identify filler words and redundant phrases
2. Flag passive voice constructions
3. Suggest more direct alternatives""",

    "impact": """You are a vocabulary and impact specialist. Analyze the text and:
1. Identify weak or overused words
2. Suggest powerful synonyms
3. Highlight opportunities for more impactful language""",
}


class SpellChecker:

    def __init__(self):
        self._tools = {}
        self._preload()

    def _preload(self):
        def load():
            for lang in ["en-US", "fr", "de", "es"]:
                print(f"[SpellChecker] Preloading {lang}...")
                self._get_tool(lang)
            print("[SpellChecker] All languages ready!")
        t = threading.Thread(target=load, daemon=True)
        t.start()

    def _get_tool(self, lang):
        if lang not in self._tools:
            self._tools[lang] = language_tool_python.LanguageTool(lang)
        return self._tools[lang]

    def analyze_vietnamese(self, text, mode="basic", tone="Professional"):
        prompt = f"""Kiểm tra lỗi ngữ pháp và chính tả tiếng Việt trong đoạn văn sau.
Chỉ trả về JSON thuần túy, không giải thích thêm, theo đúng format sau:
{{
    "corrected_text": "...",
    "grammar_errors": [{{"message": "mô tả lỗi", "rule": "GRAMMAR", "suggestions": ["gợi ý sửa"], "offset": 0, "length": 1}}],
    "style_errors": []
}}

Đoạn văn: {text}"""

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            data = json.loads(raw)

            return {
                "corrected_text":   data.get("corrected_text", text),
                "grammar_errors":   data.get("grammar_errors", []),
                "style_errors":     data.get("style_errors", []),
                "highlighted_text": text
            }

        except Exception as e:
            return {
                "corrected_text":   text,
                "grammar_errors":   [{"message": f"Gemini error: {str(e)}", "rule": "ERROR", "suggestions": [], "offset": 0, "length": 0}],
                "style_errors":     [],
                "highlighted_text": text
            }

    def _run_ai_analysis(self, text, mode, tone):
        """Gọi Gemini để phân tích sâu theo mode"""
        system = MODE_PROMPTS.get(mode, "")
        prompt = f"""{system}

Target tone: {tone}
Text to analyze: {text}

Return ONLY this JSON, no explanation:
{{
    "improved_text": "rewritten version",
    "issues": [{{"type": "style|clarity|structure|impact", "original": "original phrase", "suggestion": "better alternative", "explanation": "why"}}],
    "tone_score": 75,
    "tone_feedback": "brief feedback on tone"
}}"""

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            return json.loads(raw)
        except Exception as e:
            return {"error": str(e)}

    def analyze_text(self, text, lang="en-US", mode="basic", tone="Professional"):

        if lang == "vi":
            return self.analyze_vietnamese(text, mode, tone)

        # Luôn chạy LanguageTool để lấy grammar/style errors
        tool = self._get_tool(lang)
        matches = tool.check(text)
        corrected_text = lt_utils.correct(text, matches)

        grammar_errors = []
        style_errors = []

        style_categories = {
            "STYLE", "TYPOGRAPHY", "REDUNDANCY",
            "PLAIN_ENGLISH", "REGISTER", "COLLOQUIALISMS",
            "PUNCTUATION", "CASING"
        }

        for m in matches:
            error_data = {
                "message":     m.message,
                "rule":        m.rule_id,
                "category":    m.category,
                "suggestions": m.replacements,
                "offset":      m.offset,
                "length":      m.error_length
            }

            cat  = (m.category or "").upper()
            rule = m.rule_id.lower()

            if cat in style_categories or "style" in rule or "redundan" in rule:
                style_errors.append(error_data)
            else:
                grammar_errors.append(error_data)

        highlighted_text = _build_highlight(text, grammar_errors, style_errors)

        result = {
            "corrected_text":   corrected_text,
            "grammar_errors":   grammar_errors,
            "style_errors":     style_errors,
            "highlighted_text": highlighted_text,
            "ai_analysis":      None,
            "stats":            None,
        }

        # Với các mode nâng cao → gọi thêm Gemini
        if mode in ("style", "structural", "clarity", "impact"):
            ai = self._run_ai_analysis(text, mode, tone)
            result["ai_analysis"] = ai

            # Nếu Gemini trả improved_text → dùng làm corrected_text
            if ai and ai.get("improved_text"):
                result["corrected_text"] = ai["improved_text"]

            # Chuyển issues của Gemini thành style_errors để hiện trong UI
            if ai and ai.get("issues"):
                for issue in ai["issues"]:
                    result["style_errors"].append({
                        "message":     issue.get("explanation", issue.get("suggestion", "")),
                        "rule":        issue.get("type", "AI_SUGGESTION").upper(),
                        "category":    "STYLE",
                        "suggestions": [issue.get("suggestion", "")],
                        "offset":      None,
                        "length":      None,
                        "original":    issue.get("original", "")
                    })

        return result


def _build_highlight(text, grammar_errors, style_errors):
    """Build highlighted HTML dùng offset chính xác"""
    all_errors = [
        *[{**e, "_type": "grammar"} for e in grammar_errors if e.get("offset") is not None],
        *[{**e, "_type": "style"}   for e in style_errors   if e.get("offset") is not None],
    ]
    all_errors.sort(key=lambda e: e.get("offset", 0))

    result = []
    last = 0
    for err in all_errors:
        offset = err.get("offset")
        length = err.get("length")
        if offset is None or length is None or offset < last:
            continue
        result.append(text[last:offset])
        word  = text[offset:offset + length]
        color = "rgba(239,68,68,0.25)" if err["_type"] == "grammar" else "rgba(59,130,246,0.25)"
        border = "#ef4444" if err["_type"] == "grammar" else "#3b82f6"
        result.append(
            f"<span style='background:{color}; border-bottom:2px solid {border}; "
            f"border-radius:3px; padding:1px 2px;'>{word}</span>"
        )
        last = offset + length

    result.append(text[last:])
    return "".join(result)
