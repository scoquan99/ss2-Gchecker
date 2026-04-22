import os
import json
from google.genai import Client
from dotenv import load_dotenv
load_dotenv()

class AIModel:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.configured = True if self.api_key else False
        if self.configured:
            self.client = Client(api_key=self.api_key)
        else:
            self.client = None
        print(f"DEBUG: Key đang dùng là: {self.api_key[:10]}...")

    def analyze(self, text, mode="structural", tone="Academic and neutral"):
        if not self.configured:
            return {"error": "GEMINI_API_KEY not configured in .env file"}

        system_instruction = (
            "You are a grammar-analysis engine. For any text provided, return a JSON object matching the requested analysis mode. "
            "Do not provide conversational filler; only the JSON output. Ensure the JSON is strictly valid, and the keys are always lowercase strings. "
            "In your output, also always include an 'improved_text' key with the revised text applied."
        )

        if mode == "structural":
            prompt = f"""
            {system_instruction}
            Act as a professional copy editor. Review the text below for structural flow and rhythm. Specifically:
            1. Identify areas where sentence lengths are too similar and suggest variations to improve cadence.
            2. Highlight logic gaps between paragraphs and suggest transition phrases.
            3. Identify smothered verbs (nominalizations) and convert them back into active, punchy verbs.

            JSON format should have keys:
            - sentence_length_variations (list of strings: suggestions)
            - logic_gap_transitions (list of strings: suggestions)
            - smothered_verbs (list of strings: fixes)
            - improved_text (string: fully rewritten text)

            [TEXT]: {text}
            """
        elif mode == "clarity":
            prompt = f"""
            {system_instruction}
            Act as a minimalist editor. Your goal is to reduce the word count without losing the core meaning.
            1. Strip all filler words (e.g., actually, basically, just, very).
            2. Convert all passive voice instances to active voice.
            3. Flag any redundant phrases (e.g., collaborate together or future plans).
            4. Provide a Clarity Score out of 10 and explain how to improve it.

            JSON format should have keys:
            - filler_words_stripped (list of strings: words removed)
            - passive_to_active (list of strings: explanations of changes)
            - redundant_phrases (list of strings: phrases fixed)
            - clarity_score (integer: 1-10)
            - improvement_explanation (string)
            - improved_text (string: fully rewritten text)

            [TEXT]: {text}
            """
        elif mode == "tone":
            prompt = f"""
            {system_instruction}
            I want this text to sound {tone}.
            1. Analyze the current tone and identify any words that break character.
            2. Rewrite the opening and closing to better align with this persona.
            3. Check for inclusive language and suggest modern, gender-neutral alternatives where applicable.

            JSON format should have keys:
            - detected_tone (string: explanation of current tone vs target)
            - broken_character_words (list of strings: words that don't fit the tone)
            - opening_closing_rewrite (string: suggested opening and closing sentences)
            - inclusive_language_suggestions (list of strings: suggestions)
            - improved_text (string: fully rewritten text)

            [TEXT]: {text}
            """
        else:
            return {"error": "Invalid mode"}

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]  # Remove ```json
            if result_text.startswith('```'):
                result_text = result_text[3:]  # Remove ```
            if result_text.endswith('```'):
                result_text = result_text[:-3]  # Remove trailing ```
            
            result_text = result_text.strip()
            result = json.loads(result_text)
            return result
        except Exception as e:
            error_str = str(e)
            
            # Handle quota exceeded errors
            if "429" in error_str or "quota" in error_str.lower():
                return {
                    "error": "Gemini API quota exceeded. Free tier limit is 20 requests/day. Please try again tomorrow or upgrade to a paid plan.",
                    "quota_exceeded": True
                }
            
            # Handle authentication errors
            if "API_KEY" in error_str or "invalid" in error_str.lower():
                return {"error": "GEMINI_API_KEY is invalid or expired. Please renew your key."}
            
            # Handle other errors
            return {"error": f"AI service error: {error_str[:200]}"}

    def detect_ai(self, text):
        if not self.configured:
            return {"error": "GEMINI_API_KEY not configured"}
        
        prompt = f"""
        Analyze the following text for signs of AI generation. Look for low perplexity, low burstiness, and overly robotic transitions.
        Return a JSON object with keys:
        - ai_probability (integer 0-100 indicating likelihood it is AI generated)
        - reasoning (string explaining why)
        
        [TEXT]: {text}
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]  # Remove ```json
            if result_text.startswith('```'):
                result_text = result_text[3:]  # Remove ```
            if result_text.endswith('```'):
                result_text = result_text[:-3]  # Remove trailing ```
            
            result_text = result_text.strip()
            return json.loads(result_text)
        except Exception as e:
            error_str = str(e)
            
            # Handle quota exceeded errors
            if "429" in error_str or "quota" in error_str.lower():
                return {
                    "error": "Gemini API quota exceeded. Free tier limit is 20 requests/day. Please try again tomorrow.",
                    "quota_exceeded": True,
                    "ai_probability": None
                }
            
            # Handle authentication errors
            if "API_KEY" in error_str or "invalid" in error_str.lower():
                return {"error": "GEMINI_API_KEY is invalid or expired.", "ai_probability": None}
            
            return {"error": f"AI detection error: {error_str[:200]}", "ai_probability": None}
