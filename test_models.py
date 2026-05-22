import os
from dotenv import load_dotenv
from google import genai

load_dotenv("c:/Users/admin/Documents/ss2-Gchecker-main/backend/.env")

api_key = os.getenv("GEMINI_API_KEY_1")
client = genai.Client(api_key=api_key)

try:
    models = client.models.list()
    for m in models:
        if "flash" in m.name.lower():
            print(m.name)
except Exception as e:
    print("Error listing models:", e)
