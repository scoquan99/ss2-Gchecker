import language_tool_python
import language_tool_python.utils as lt_utils
from google import genai
import json
import os
import threading
from dotenv import load_dotenv

load_dotenv()

api_keys = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
api_keys = [k for k in api_keys if k and len(k.strip()) > 15]

# ─────────────────────────────────────────────
#  PROMPT riêng biệt cho từng mode
#  Mỗi mode có nhiệm vụ DUY NHẤT, không trùng
# ─────────────────────────────────────────────
MODE_PROMPTS = {

    # MODE 1 ── Kiến tạo giọng văn
    # Nhiệm vụ: khớp cảm xúc / nhịp điệu với tone mục tiêu
    "style": """You are a tone and voice editor. Your ONLY job is to rewrite the text so it perfectly matches the target tone.
Rules:
- Keep the original meaning 100%
- Adjust word choice, sentence rhythm, and emotional register to match the tone
- If tone is "formal": remove contractions, slang, casual phrasing
- If tone is "friendly": add warmth, use "you/we", softer language
- If tone is "persuasive": add conviction, action verbs, rhetorical flow
- If tone is "technical": precise terminology, no fluff
- Flag every phrase that clashes with the target tone
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full rewritten text matching the tone",
    "issues": [{"type": "tone", "original": "original phrase", "suggestion": "tone-adjusted version", "explanation": "why it clashes with the tone"}],
    "tone_score": 0,
    "tone_feedback": "short feedback: how well original text matches target tone and what changed"
}""",

    # MODE 2 ── Cấu trúc mạch lạc
    # Nhiệm vụ: sắp xếp lại cấu trúc câu/đoạn cho rõ ràng, có logic
    "structural": """You are a structure and flow editor. Your ONLY job is to improve sentence variation, paragraph logic, and transitions.
Rules:
- Vary sentence length: break up run-ons, combine choppy sentences
- Ensure each paragraph has: topic sentence → supporting details → conclusion
- Add or improve transition words between sentences and paragraphs
- Reorder sentences within a paragraph if it improves logical flow
- Do NOT change vocabulary or tone — only restructure
- Flag every structural weakness (missing transition, run-on, abrupt jump)
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full restructured text with better flow",
    "issues": [{"type": "structure", "original": "problematic sentence or transition", "suggestion": "restructured version", "explanation": "structural problem found"}],
    "tone_score": 0,
    "tone_feedback": "summary of structural changes made"
}""",

    # MODE 3 ── Tối ưu độ trong trẻo
    # Nhiệm vụ: cắt bỏ thừa, chuyển bị động → chủ động, đơn giản hoá
    "clarity": """You are a clarity and conciseness editor. Your ONLY job is to make the text cleaner and more direct.
Rules:
- Remove ALL filler words: "very", "really", "basically", "in order to", "the fact that", "it is important to note that", etc.
- Convert every passive voice sentence to active voice
- Replace wordy phrases with concise alternatives ("due to the fact that" → "because")
- Remove redundant words ("future plans", "past history", "end result")
- Split sentences longer than 25 words
- Do NOT change the meaning or tone — only remove fat
- Flag every filler, passive, or redundancy found
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full cleaned-up text, shorter and more direct",
    "issues": [{"type": "clarity", "original": "wordy/passive phrase", "suggestion": "concise/active version", "explanation": "type of issue: filler | passive voice | redundancy | run-on"}],
    "tone_score": 0,
    "tone_feedback": "summary: how many words cut, passive sentences fixed"
}""",

    # MODE 4 ── Sức mạnh ngôn từ
    # Nhiệm vụ: nâng cấp từ vựng, thay thế từ yếu/cliché bằng từ mạnh/chính xác
    "impact": """You are a vocabulary and impact specialist. Your ONLY job is to upgrade weak or generic words with powerful, precise alternatives.
Rules:
- Replace weak verbs ("is", "was", "have", "do", "make", "get") with strong, specific action verbs
- Replace vague adjectives ("good", "bad", "nice", "big", "small") with vivid, precise words
- Replace clichés and overused phrases with fresh, impactful alternatives
- Elevate vocabulary: replace common words with more expressive synonyms (context-appropriate)
- Keep sentence structure the same — only swap words
- Do NOT simplify — this mode UPGRADES vocabulary
- Flag every weak word or cliché found
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full text with upgraded vocabulary — same structure, stronger words",
    "issues": [{"type": "impact", "original": "weak word or cliché", "suggestion": "powerful alternative", "explanation": "why this word is weak and what the upgrade achieves"}],
    "tone_score": 0,
    "tone_feedback": "summary: how many words upgraded and overall impact improvement"
}"""
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

    # ─────────────────────────────────────────────
    #  Tiếng Việt — dùng Gemini hoàn toàn
    # ─────────────────────────────────────────────
    def analyze_vietnamese(self, text, mode="basic", tone="Professional"):
        if mode == "basic":
            prompt = f"""Kiểm tra lỗi ngữ pháp và chính tả tiếng Việt.
Chỉ trả về JSON thuần túy:
{{
    "corrected_text": "...",
    "grammar_errors": [{{"message": "mô tả lỗi", "rule": "GRAMMAR", "suggestions": ["gợi ý"], "offset": 0, "length": 1}}],
    "style_errors": []
}}
Đoạn văn: {text}"""
        elif mode == "style":
            prompt = f"""Viết lại đoạn văn tiếng Việt theo giọng văn: {tone}.
Giữ nguyên ý nghĩa, chỉ thay đổi cách diễn đạt cho khớp giọng điệu mục tiêu.
Chỉ trả về JSON:
{{
    "corrected_text": "văn bản đã viết lại theo giọng {tone}",
    "grammar_errors": [],
    "style_errors": [{{"message": "giải thích thay đổi", "rule": "TONE", "suggestions": [], "offset": 0, "length": 0}}]
}}
Đoạn văn: {text}"""
        elif mode == "structural":
            prompt = f"""Cải thiện cấu trúc và mạch lạc của đoạn văn tiếng Việt.
Sắp xếp lại câu cho logic hơn, thêm từ nối, chia đoạn hợp lý. Không thay đổi từ ngữ.
Chỉ trả về JSON:
{{
    "corrected_text": "văn bản đã cải thiện cấu trúc",
    "grammar_errors": [],
    "style_errors": [{{"message": "vấn đề cấu trúc tìm thấy", "rule": "STRUCTURE", "suggestions": ["gợi ý"], "offset": 0, "length": 0}}]
}}
Đoạn văn: {text}"""
        elif mode == "clarity":
            prompt = f"""Làm ngắn gọn và rõ ràng hơn đoạn văn tiếng Việt.
Bỏ từ thừa, chuyển câu bị động thành chủ động, đơn giản hoá cách diễn đạt.
Chỉ trả về JSON:
{{
    "corrected_text": "văn bản đã cắt gọn và làm rõ",
    "grammar_errors": [],
    "style_errors": [{{"message": "từ/cụm thừa hoặc bị động", "rule": "CLARITY", "suggestions": ["phiên bản ngắn gọn hơn"], "offset": 0, "length": 0}}]
}}
Đoạn văn: {text}"""
        elif mode == "impact":
            prompt = f"""Nâng cấp từ vựng trong đoạn văn tiếng Việt.
Thay thế từ yếu/chung chung bằng từ mạnh/chính xác/sắc nét hơn. Giữ nguyên cấu trúc câu.
Chỉ trả về JSON:
{{
    "corrected_text": "văn bản với từ vựng đã được nâng cấp",
    "grammar_errors": [],
    "style_errors": [{{"message": "từ yếu → từ mạnh hơn", "rule": "IMPACT", "suggestions": ["từ mạnh hơn"], "offset": 0, "length": 0}}]
}}
Đoạn văn: {text}"""
        else:
            prompt = f"""Kiểm tra lỗi ngữ pháp và chính tả tiếng Việt.
Chỉ trả về JSON:
{{
    "corrected_text": "...",
    "grammar_errors": [],
    "style_errors": []
}}
Đoạn văn: {text}"""

        if not api_keys:
            return {"corrected_text": text, "grammar_errors": [], "style_errors": [], "highlighted_text": text}

        for i, api_key in enumerate(api_keys):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                raw = response.text.strip().strip("```json").strip("```").strip()
                data = json.loads(raw)
                return {
                    "corrected_text":   data.get("corrected_text", text),
                    "grammar_errors":   data.get("grammar_errors", []),
                    "style_errors":     data.get("style_errors", []),
                    "highlighted_text": text
                }
            except Exception as e:
                print(f"Key {i+1} loi (vi): {str(e)[:80]}")
                continue

        return {"corrected_text": text, "grammar_errors": [], "style_errors": [], "highlighted_text": text}


    # ─────────────────────────────────────────────
    #  Gọi Gemini theo mode — prompt đã chuyên biệt
    # ─────────────────────────────────────────────
    def _run_ai_analysis(self, text, mode, tone):
        system = MODE_PROMPTS.get(mode, "")
        if not system:
            return None

        # Mode style: inject tone target vào prompt
        if mode == "style":
            system = system.replace("the target tone", f'the target tone "{tone}"')

        prompt = f"{system}\n\nTarget tone: {tone}\n\nText:\n{text}"

        if not api_keys:
            return {"error": "No API keys configured"}

        last_error = "unknown"
        for i, api_key in enumerate(api_keys):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                raw = response.text.strip().strip("```json").strip("```").strip()
                return json.loads(raw)
            except Exception as e:
                print(f"Key {i+1} loi (ai_analysis/{mode}): {str(e)[:80]}")
                last_error = str(e)
                continue

        return {"error": f"All API keys failed: {last_error}"}

    # ─────────────────────────────────────────────
    #  Tính stats văn bản
    # ─────────────────────────────────────────────
    def _compute_stats(self, text):
        import re
        words  = text.split()
        wcount = len(words)
        ccount = len(text)
        sents  = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        read_ease = round(max(0, 206.835 - 1.015 * (wcount / max(len(sents), 1)) - 84.6 * (sum(len(w) for w in words) / max(wcount, 1) / 5)), 1)

        # Top keywords (loại bỏ stopwords đơn giản)
        stopwords = {"the","a","an","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","shall","to","of","in","for","on","with","at","by","from","as","into","through","and","or","but","if","then","than","so","yet","nor","not","this","that","these","those","it","its","i","you","he","she","we","they","me","him","her","us","them","my","your","his","our","their"}
        freq = {}
        for w in words:
            w2 = re.sub(r'[^a-zA-Z]', '', w.lower())
            if w2 and w2 not in stopwords and len(w2) > 2:
                freq[w2] = freq.get(w2, 0) + 1
        top_kw = sorted(freq.items(), key=lambda x: -x[1])[:8]

        # Sentence highlights
        highlights = []
        for s in sents[:20]:
            wlen = len(s.split())
            cat = "short" if wlen <= 10 else ("medium" if wlen <= 20 else "long")
            highlights.append({"text": s, "category": cat})

        return {
            "word_count":        wcount,
            "char_count":        ccount,
            "sentence_count":    len(sents),
            "reading_time_mins": round(wcount / 200, 1),
            "speaking_time_mins":round(wcount / 130, 1),
            "reading_ease":      read_ease,
            "top_keywords":      [{"word": w, "count": c} for w, c in top_kw],
            "sentence_highlights": highlights,
        }

    # ─────────────────────────────────────────────
    #  Điểm vào chính
    # ─────────────────────────────────────────────
    def analyze_text(self, text, lang="en-US", mode="basic", tone="Professional"):

        if lang == "vi":
            result = self.analyze_vietnamese(text, mode, tone)
            result["stats"] = self._compute_stats(text)
            result["ai_analysis"] = None
            return result

        # ── LanguageTool (luôn chạy để lấy grammar errors) ──
        tool = self._get_tool(lang)
        matches = tool.check(text)
        lt_corrected = lt_utils.correct(text, matches)

        grammar_errors = []
        style_errors   = []

        style_categories = {
            "STYLE","TYPOGRAPHY","REDUNDANCY",
            "PLAIN_ENGLISH","REGISTER","COLLOQUIALISMS",
            "PUNCTUATION","CASING"
        }

        for m in matches:
            err = {
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
                style_errors.append(err)
            else:
                grammar_errors.append(err)

        result = {
            "corrected_text":   lt_corrected,
            "grammar_errors":   grammar_errors,
            "style_errors":     style_errors,
            "highlighted_text": _build_highlight(text, grammar_errors, style_errors),
            "ai_analysis":      None,
            "stats":            self._compute_stats(text),
        }

        # ── Mode cơ bản: chỉ dùng LanguageTool ──
        if mode == "basic":
            return result

        # ── Mode PRO: gọi Gemini với prompt chuyên biệt ──
        ai = self._run_ai_analysis(text, mode, tone)
        result["ai_analysis"] = ai

        if ai and not ai.get("error"):
            # Dùng improved_text từ Gemini thay cho lt_corrected
            if ai.get("improved_text"):
                result["corrected_text"] = ai["improved_text"]

            # Thêm issues của Gemini vào style_errors để hiển thị trong UI
            if ai.get("issues"):
                for issue in ai["issues"]:
                    result["style_errors"].append({
                        "message":   f'[{issue.get("type","").upper()}] {issue.get("explanation","")}',
                        "rule":      issue.get("type", "AI").upper(),
                        "category":  "STYLE",
                        "suggestions": [issue.get("suggestion", "")],
                        "offset":    None,
                        "length":    None,
                        "original":  issue.get("original", "")
                    })

        return result


# ─────────────────────────────────────────────
#  Helper: build highlighted HTML
# ─────────────────────────────────────────────
def _build_highlight(text, grammar_errors, style_errors):
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
        word   = text[offset:offset + length]
        color  = "rgba(239,68,68,0.25)"  if err["_type"] == "grammar" else "rgba(59,130,246,0.25)"
        border = "#ef4444"               if err["_type"] == "grammar" else "#3b82f6"
        result.append(f"<span style='background:{color}; border-bottom:2px solid {border}; border-radius:3px; padding:1px 2px;'>{word}</span>")
        last = offset + length

    result.append(text[last:])
    return "".join(result)
