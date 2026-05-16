import os
import json
from google.genai import Client
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

        system_instruction = "You are a professional grammar and writing analysis engine. Return only valid JSON."

        # ... (giữ nguyên phần prompt của bạn)

        for attempt in range(len(self.api_keys)):
            try:
                client = self._get_client()
                # (phần generate_content giữ nguyên như cũ của bạn)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",   # Model mới
                    contents=prompt
                )
                # ... xử lý response giống cũ
                result_text = response.text.strip()
                # Xử lý markdown...
                if result_text.startswith('```'):
                    result_text = result_text.split('```')[1].replace('json', '').strip()
                result = json.loads(result_text)
                return result

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
                prompt = f"""Phân tích xem văn bản sau có phải do AI tạo ra không. Trả về chỉ JSON:
{{"ai_probability": 65, "reasoning": "Giải thích ngắn gọn bằng tiếng Việt"}}

Văn bản: {text[:6000]}"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                raw = response.text.strip().strip("```json").strip("```").strip()
                result = json.loads(raw)
                return result

            except Exception as e:
                error_str = str(e).lower()
                print(f"AI Detect - Key error: {str(e)[:80]}")
                if "quota" in error_str or "429" in error_str:
                    self._next_key()
                    continue
                else:
                    break

        return {"ai_probability": 50, "reasoning": "Tất cả keys đang hết quota. Thử lại sau."}