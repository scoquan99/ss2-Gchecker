import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv("c:/Users/admin/Documents/ss2-Gchecker-main/backend/.env")

api_keys = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]
api_keys = [k for k in api_keys if k and len(k.strip()) > 15]

prompt = """You are a style and tone editor. Analyze the text and:
1. Identify tone inconsistencies and informal language
2. Suggest improvements for the specified tone
3. Flag style issues (passive voice, wordiness, weak verbs)

Target tone: Academic and Formal
Text to analyze: this paragraph attempts to discuss an important issue, but it uses informal tone and lacks academic style. you know, many people think education is super important, and they kinda believe it helps them get a good job. but honestly, there is a lot of problem with how school teach student nowadays, and it dont always work well. like, teachers sometimes just give too much homework and stuff, which make students feel stressed and tired. also, the ideas are not presented in a clear structure and it dont really follow any formal writing rules, so it look unprofessional and not suitable for academic purpose.

Return ONLY this JSON, no explanation:
{
    "improved_text": "rewritten version",
    "issues": [{"type": "style|clarity|structure|impact", "original": "original phrase", "suggestion": "better alternative", "explanation": "why"}],
    "tone_score": 75,
    "tone_feedback": "brief feedback on tone"
}"""

for i, api_key in enumerate(api_keys):
    try:
        current_client = genai.Client(api_key=api_key)
        response = current_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(f"Key {i+1} Success!")
        print("Raw response:", response.text)
        
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        print("Before JSON load:", raw)
        data = json.loads(raw)
        print("Parsed JSON correctly!")
        break
    except Exception as e:
        print(f"Key {i+1} Error:", e)
