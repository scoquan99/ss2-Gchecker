import os
import json
import re
from google.genai import Client
from google.genai import types as genai_types
from dotenv import load_dotenv
import itertools

load_dotenv()

# ====================== ROTATE API KEYS ======================
api_keys = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
api_keys = [k for k in api_keys if k and len(k.strip()) > 15]
api_key_cycle = itertools.cycle(api_keys) if api_keys else None
# ============================================================


def _parse_json_response(raw: str) -> dict:
    """Safely parse JSON from model response, handling markdown fences."""
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw.strip())


class AIModel:
    def __init__(self):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.configured = len(self.api_keys) > 0
        print(f"DEBUG: Loaded {len(self.api_keys)} Gemini API keys")

    def _get_client(self):
        if not self.configured:
            return None
        api_key = self.api_keys[self.current_key_index]
        return Client(api_key=api_key)

    def _next_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

    def analyze(self, text, mode="structural", tone="Academic and neutral"):
        if not self.configured:
            return {"error": "GEMINI_API_KEY not configured in .env file"}

        mode_instructions = {
            "structural": (
                "You are a structure and flow editor. Improve sentence variation, paragraph logic, and transitions. "
                "Vary sentence length, ensure each paragraph has a topic sentence → supporting details → conclusion, "
                "and add transition words. Do NOT change vocabulary or tone — only restructure. "
                "Flag every structural weakness."
            ),
            "style": (
                f"You are a tone and voice editor. Rewrite the text to perfectly match the target tone: \"{tone}\". "
                "Keep the original meaning 100%. Adjust word choice, sentence rhythm, and emotional register. "
                "Flag every phrase that clashes with the target tone."
            ),
            "clarity": (
                "You are a clarity and conciseness editor. Remove ALL filler words, convert passive voice to active, "
                "replace wordy phrases with concise alternatives, and split sentences longer than 25 words. "
                "Do NOT change meaning or tone — only remove fat. Flag every filler, passive, or redundancy."
            ),
            "impact": (
                "You are a vocabulary and impact specialist. Replace weak verbs and vague adjectives with powerful, "
                "precise alternatives. Replace clichés with fresh expressions. Elevate vocabulary context-appropriately. "
                "Keep sentence structure the same — only swap words. Flag every weak word or cliché."
            ),
        }

        instruction = mode_instructions.get(mode, mode_instructions["structural"])

        prompt = f"""{instruction}

Target tone: {tone}

Return ONLY this JSON (no markdown, no explanation):
{{
    "improved_text": "full rewritten text",
    "issues": [{{"type": "{mode}", "original": "original phrase", "suggestion": "improved version", "explanation": "reason for change"}}],
    "tone_score": 0,
    "tone_feedback": "brief summary of changes made"
}}

Text:
{text[:5000]}"""

        for attempt in range(len(self.api_keys)):
            try:
                client = self._get_client()
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=1024)
                    )
                )
                return _parse_json_response(response.text)

            except Exception as e:
                error_str = str(e).lower()
                print(f"AI Analyze - Key {self.current_key_index+1} error: {str(e)[:100]}")
                if "quota" in error_str or "429" in error_str:
                    self._next_key()
                    continue
                else:
                    break

        return {"error": "All API keys exhausted or error occurred."}

    def detect_ai(self, text):
        if not self.configured:
            return {"ai_probability": 40, "reasoning": "Chưa cấu hình API key"}

        for attempt in range(len(self.api_keys)):
            try:
                client = self._get_client()
                prompt = f"""Bạn là chuyên gia ngôn ngữ học pháp y chuyên phát hiện văn bản do AI tạo ra.
Phân tích văn bản sau theo các tiêu chí:
1. MẪU TỪ VỰNG: Dùng quá nhiều cụm từ đệm, lặp lại cách mở đầu câu, phân bổ từ vựng cân bằng bất thường
2. MẪU CẤU TRÚC: Độ dài đoạn văn quá đồng đều, cấu trúc công thức (mở đầu → thân → kết luận)
3. MẪU NGỮ NGHĨA: Ví dụ chung chung, không cụ thể; ngôn ngữ né tránh; thiếu trải nghiệm cá nhân
4. MẪU PHONG CÁCH: Ngữ pháp hoàn hảo, thiếu lỗi đánh máy, giọng điệu trung lập đáng ngờ
5. TÍNH NHẤT QUÁN: AI thường mạch lạc toàn cục nhưng nông về chi tiết

Đánh giá từ 0 (chắc chắn do người viết) đến 100 (chắc chắn do AI tạo).
Trả về CHỈ JSON:
{{"ai_probability": 65, "reasoning": "Bằng chứng cụ thể tìm thấy trong văn bản (trích dẫn câu/cụm từ thực tế)"}}

Văn bản: {text[:6000]}"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(thinking_budget=1024)
                    )
                )
                return _parse_json_response(response.text)

            except Exception as e:
                error_str = str(e).lower()
                print(f"AI Detect - Key error: {str(e)[:80]}")
                if "quota" in error_str or "429" in error_str:
                    self._next_key()
                    continue
                else:
                    break

        return {"ai_probability": 50, "reasoning": "Tất cả keys đang hết quota. Thử lại sau."}