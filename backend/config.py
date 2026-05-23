import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME",   "grammar_checker")

def get_gemini_keys():
    """Một nơi duy nhất load + validate Gemini API keys."""
    raw = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 9)]
    return [k.strip() for k in raw if k and len(k.strip()) > 15]
