from textblob import TextBlob
import language_tool_python
import language_tool_python.utils as lt_utils

class SpellChecker:

    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')

    def analyze_text(self, text):

        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        matches = self.tool.check(text)
        corrected_text = lt_utils.correct(text, matches)

        grammar_errors = []
        style_errors = []

        # Build highlighted text by processing matches in reverse order
        # (reverse order prevents offset shifts from affecting later replacements)
        sorted_matches = sorted(matches, key=lambda x: x.offset, reverse=True)
        highlighted_text = text

        for m in sorted_matches:
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

            # Extract the exact error text using offsets
            wrong_word = text[m.offset:m.offset+m.error_length]
            highlight = f"<span style='background-color:{color}; padding:2px 4px; border-radius:3px;'>{wrong_word}</span>"

            # Replace at specific offset position to avoid double-replacement
            highlighted_text = highlighted_text[:m.offset] + highlight + highlighted_text[m.offset+m.error_length:]

        return {
            "corrected_text": corrected_text,
            "grammar_errors": grammar_errors,
            "style_errors": style_errors,
            "highlighted_text": highlighted_text
        }