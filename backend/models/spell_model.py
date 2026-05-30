import language_tool_python
import language_tool_python.utils as lt_utils
from google import genai
from google.genai import types as genai_types
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

from config import get_gemini_keys

api_keys = get_gemini_keys()

MODE_PROMPTS = {
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

    "structural": """You are a structure and flow editor. Your ONLY job is to improve sentence variation, paragraph logic, and transitions.
Rules:
- Vary sentence length: break up run-ons, combine choppy sentences
- Ensure each paragraph has: topic sentence -> supporting details -> conclusion
- Add or improve transition words between sentences and paragraphs
- Reorder sentences within a paragraph if it improves logical flow
- Do NOT change vocabulary or tone -- only restructure
- Flag every structural weakness (missing transition, run-on, abrupt jump)
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full restructured text with better flow",
    "issues": [{"type": "structure", "original": "problematic sentence or transition", "suggestion": "restructured version", "explanation": "structural problem found"}],
    "tone_score": 0,
    "tone_feedback": "summary of structural changes made"
}""",

    "clarity": """You are a clarity and conciseness editor. Your ONLY job is to make the text cleaner and more direct.
Rules:
- Remove ALL filler words: "very", "really", "basically", "in order to", "the fact that", "it is important to note that", etc.
- Convert every passive voice sentence to active voice
- Replace wordy phrases with concise alternatives ("due to the fact that" -> "because")
- Remove redundant words ("future plans", "past history", "end result")
- Split sentences longer than 25 words
- Do NOT change the meaning or tone -- only remove fat
- Flag every filler, passive, or redundancy found
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full cleaned-up text, shorter and more direct",
    "issues": [{"type": "clarity", "original": "wordy/passive phrase", "suggestion": "concise/active version", "explanation": "type of issue: filler | passive voice | redundancy | run-on"}],
    "tone_score": 0,
    "tone_feedback": "summary: how many words cut, passive sentences fixed"
}""",

    "impact": """You are a vocabulary and impact specialist. Your ONLY job is to upgrade weak or generic words with powerful, precise alternatives.
Rules:
- Replace weak verbs ("is", "was", "have", "do", "make", "get") with strong, specific action verbs
- Replace vague adjectives ("good", "bad", "nice", "big", "small") with vivid, precise words
- Replace cliches and overused phrases with fresh, impactful alternatives
- Elevate vocabulary: replace common words with more expressive synonyms (context-appropriate)
- Keep sentence structure the same -- only swap words
- Do NOT simplify -- this mode UPGRADES vocabulary
- Flag every weak word or cliche found
Return ONLY this JSON (no markdown, no explanation):
{
    "improved_text": "full text with upgraded vocabulary -- same structure, stronger words",
    "issues": [{"type": "impact", "original": "weak word or cliche", "suggestion": "powerful alternative", "explanation": "why this word is weak and what the upgrade achieves"}],
    "tone_score": 0,
    "tone_feedback": "summary: how many words upgraded and overall impact improvement"
}"""
}


class SpellChecker:

    def __init__(self):
        self._tools = {}
        self._tools_lock = threading.Lock()
        self._preload()

    def _preload(self):
        # Warm up en-US at startup so the first real request doesn't pay the init cost
        threading.Thread(target=lambda: self._get_tool("en-US"), daemon=True).start()

    def _get_tool(self, lang):
        # Double-checked locking — avoid re-initialising if another thread beat us to it
        if lang not in self._tools:
            with self._tools_lock:
                if lang not in self._tools:
                    self._tools[lang] = language_tool_python.LanguageTool(lang)
        return self._tools[lang]

    def analyze_vietnamese(self, text, mode="basic", tone="Professional"):
        prompts = {
            "basic": f"""Check Vietnamese grammar and spelling.
Return ONLY this JSON:
{{
    "corrected_text": "...",
    "grammar_errors": [{{"message": "error description", "rule": "GRAMMAR", "suggestions": ["suggestion"], "offset": 0, "length": 1}}],
    "style_errors": []
}}
Text: {text}""",
            "style": f"""Rewrite this Vietnamese text to match the tone: {tone}.
Keep the meaning, only change phrasing to fit the target tone.
Return ONLY this JSON:
{{
    "corrected_text": "rewritten text in {tone} tone",
    "grammar_errors": [],
    "style_errors": [{{"message": "explanation of changes", "rule": "TONE", "suggestions": [], "offset": 0, "length": 0}}]
}}
Text: {text}""",
            "structural": f"""Improve the structure and flow of this Vietnamese text.
Reorder sentences for better logic, add transitions, split paragraphs appropriately. Do not change vocabulary.
Return ONLY this JSON:
{{
    "corrected_text": "restructured text",
    "grammar_errors": [],
    "style_errors": [{{"message": "structural issue found", "rule": "STRUCTURE", "suggestions": ["suggestion"], "offset": 0, "length": 0}}]
}}
Text: {text}""",
            "clarity": f"""Make this Vietnamese text more concise and clear.
Remove filler words, convert passive to active voice, simplify phrasing.
Return ONLY this JSON:
{{
    "corrected_text": "concise version",
    "grammar_errors": [],
    "style_errors": [{{"message": "filler/passive found", "rule": "CLARITY", "suggestions": ["concise version"], "offset": 0, "length": 0}}]
}}
Text: {text}""",
            "impact": f"""Upgrade the vocabulary of this Vietnamese text.
Replace weak/generic words with stronger, more precise alternatives. Keep sentence structure intact.
Return ONLY this JSON:
{{
    "corrected_text": "text with upgraded vocabulary",
    "grammar_errors": [],
    "style_errors": [{{"message": "weak word -> stronger word", "rule": "IMPACT", "suggestions": ["stronger word"], "offset": 0, "length": 0}}]
}}
Text: {text}"""
        }

        prompt = prompts.get(mode, prompts["basic"])

        if not api_keys:
            return {"corrected_text": text, "grammar_errors": [], "style_errors": [], "highlighted_text": text}

        for i, api_key in enumerate(api_keys):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=0)
                    )
                )
                raw = response.text.strip().strip("```json").strip("```").strip()
                data = json.loads(raw)
                return {
                    "corrected_text":   data.get("corrected_text", text),
                    "grammar_errors":   data.get("grammar_errors", []),
                    "style_errors":     data.get("style_errors", []),
                    "highlighted_text": text
                }
            except Exception as e:
                print(f"Key {i+1} error (vi): {str(e)[:80]}")
                continue

        return {"corrected_text": text, "grammar_errors": [], "style_errors": [], "highlighted_text": text}

    def _run_ai_analysis(self, text, mode, tone):
        system = MODE_PROMPTS.get(mode, "")
        if not system:
            return None

        if mode == "style":
            system = system.replace("the target tone", f'the target tone "{tone}"')

        prompt = f"{system}\n\nTarget tone: {tone}\n\nText:\n{text}"

        if not api_keys:
            return {"error": "No API keys configured"}

        last_error = "unknown"
        for i, api_key in enumerate(api_keys):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=0)
                    )
                )
                raw = response.text.strip().strip("```json").strip("```").strip()
                return json.loads(raw)
            except Exception as e:
                print(f"Key {i+1} error (ai_analysis/{mode}): {str(e)[:80]}")
                last_error = str(e)
                continue

        return {"error": f"All API keys failed: {last_error}"}

    def _compute_stats(self, text):
        import re
        words  = text.split()
        wcount = len(words)
        ccount = len(text)
        sents  = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        read_ease = round(max(0, 206.835 - 1.015 * (wcount / max(len(sents), 1)) - 84.6 * (sum(len(w) for w in words) / max(wcount, 1) / 5)), 1)

        stopwords = {"the","a","an","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","could","should","may","might","shall","to","of","in","for","on","with","at","by","from","as","into","through","and","or","but","if","then","than","so","yet","nor","not","this","that","these","those","it","its","i","you","he","she","we","they","me","him","her","us","them","my","your","his","our","their"}
        freq = {}
        for w in words:
            w2 = re.sub(r'[^a-zA-Z]', '', w.lower())
            if w2 and w2 not in stopwords and len(w2) > 2:
                freq[w2] = freq.get(w2, 0) + 1
        top_kw = sorted(freq.items(), key=lambda x: -x[1])[:8]

        highlights = []
        for s in sents[:20]:
            wlen = len(s.split())
            cat = "short" if wlen <= 10 else ("medium" if wlen <= 20 else "long")
            highlights.append({"text": s, "category": cat})

        return {
            "word_count":         wcount,
            "char_count":         ccount,
            "sentence_count":     len(sents),
            "reading_time_mins":  round(wcount / 200, 1),
            "speaking_time_mins": round(wcount / 130, 1),
            "reading_ease":       read_ease,
            "top_keywords":       [{"word": w, "count": c} for w, c in top_kw],
            "sentence_highlights": highlights,
        }

    def analyze_text(self, text, lang="en-US", mode="basic", tone="Professional"):

        if lang == "vi":
            result = self.analyze_vietnamese(text, mode, tone)
            result["stats"] = self._compute_stats(text)
            result["ai_analysis"] = None
            return result

        style_categories = {
            "STYLE","TYPOGRAPHY","REDUNDANCY",
            "PLAIN_ENGLISH","REGISTER","COLLOQUIALISMS",
            "PUNCTUATION","CASING"
        }

        lt_result    = {}
        ai_result    = {}
        stats_result = {}

        def run_language_tool():
            tool = self._get_tool(lang)
            matches = tool.check(text)
            lt_corrected = lt_utils.correct(text, matches)
            grammar_errors, style_errors = [], []
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
            lt_result["corrected"]      = lt_corrected
            lt_result["grammar_errors"] = grammar_errors
            lt_result["style_errors"]   = style_errors

        def run_stats():
            stats_result["data"] = self._compute_stats(text)

        # Always start LanguageTool + stats in parallel
        t_lt    = threading.Thread(target=run_language_tool)
        t_stats = threading.Thread(target=run_stats)
        t_lt.start()
        t_stats.start()

        # PRO modes: fire Gemini immediately — runs at the same time as LanguageTool
        t_ai = None
        if mode != "basic":
            def run_ai():
                ai_result["data"] = self._run_ai_analysis(text, mode, tone)
            t_ai = threading.Thread(target=run_ai)
            t_ai.start()

        # Collect results — total wait = max(LT, Gemini) not LT + Gemini
        t_lt.join()
        t_stats.join()
        if t_ai:
            t_ai.join()

        grammar_errors = lt_result.get("grammar_errors", [])
        style_errors   = lt_result.get("style_errors", [])
        lt_corrected   = lt_result.get("corrected", text)

        result = {
            "corrected_text":   lt_corrected,
            "grammar_errors":   grammar_errors,
            "style_errors":     style_errors,
            "highlighted_text": _build_highlight(text, grammar_errors, style_errors),
            "ai_analysis":      None,
            "stats":            stats_result.get("data", {}),
        }

        if mode == "basic":
            return result

        ai = ai_result.get("data")
        result["ai_analysis"] = ai

        if ai and not ai.get("error"):
            if ai.get("improved_text"):
                result["corrected_text"] = ai["improved_text"]
            if ai.get("issues"):
                for issue in ai["issues"]:
                    result["style_errors"].append({
                        "message":     f'[{issue.get("type","").upper()}] {issue.get("explanation","")}',
                        "rule":        issue.get("type", "AI").upper(),
                        "category":    "STYLE",
                        "suggestions": [issue.get("suggestion", "")],
                        "offset":      None,
                        "length":      None,
                        "original":    issue.get("original", "")
                    })

        return result


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
