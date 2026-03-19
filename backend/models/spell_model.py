from textblob import TextBlob
import language_tool_python

class SpellChecker:

    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')

    def analyze_text(self, text):

        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        matches = self.tool.check(text)

        grammar_errors = []
        style_errors = []

        highlighted_text = text

        for m in matches:

            error_data = {
                "message": m.message,
                "rule": m.rule_id,
                "suggestions": m.replacements,
                "offset": m.offset,
                "length": m.error_length
            }

            # style detection
            if "style" in m.rule_id.lower():
                style_errors.append(error_data)
                color = "blue"
            else:
                grammar_errors.append(error_data)
                color = "orange"

            wrong_word = text[m.offset:m.offset+m.error_length]

            highlight = f"<span style='background:{color}'>{wrong_word}</span>"

            highlighted_text = highlighted_text.replace(wrong_word, highlight)

        return {
            "corrected_text": corrected_text,
            "grammar_errors": grammar_errors,
            "style_errors": style_errors,
            "highlighted_text": highlighted_text
        }