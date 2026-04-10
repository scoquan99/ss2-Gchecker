from textblob import TextBlob
import language_tool_python
import language_tool_python.utils as lt_utils
from google import genai
import json
import os
import threading
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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

    def analyze_vietnamese(self, text):
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
                model="gemini-2.0-flash",
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
                "highlighted_text": data.get("corrected_text", text)
            }

        except Exception as e:
            return {
                "corrected_text":   text,
                "grammar_errors":   [{"message": f"Gemini error: {str(e)}", "rule": "ERROR", "suggestions": [], "offset": 0, "length": 0}],
                "style_errors":     [],
                "highlighted_text": text
            }

    def analyze_text(self, text, lang="en-US"):

        if lang == "vi":
            return self.analyze_vietnamese(text)

        tool = self._get_tool(lang)

        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        matches = tool.check(text)
        corrected_text = lt_utils.correct(text, matches)

        grammar_errors = []
        style_errors = []
        highlighted_text = text

        for m in matches:

            error_data = {
                "message":     m.message,
                "rule":        m.rule_id,
                "suggestions": m.replacements,
                "offset":      m.offset,
                "length":      m.error_length
            }

            if "style" in m.rule_id.lower():
                style_errors.append(error_data)
                color = "blue"
            else:
                grammar_errors.append(error_data)
                color = "orange"

            wrong_word = text[m.offset:m.offset + m.error_length]
            highlight = f"<span style='background:{color}'>{wrong_word}</span>"
            highlighted_text = highlighted_text.replace(wrong_word, highlight)

        return {
            "corrected_text":   corrected_text,
            "grammar_errors":   grammar_errors,
            "style_errors":     style_errors,
            "highlighted_text": highlighted_text
        }