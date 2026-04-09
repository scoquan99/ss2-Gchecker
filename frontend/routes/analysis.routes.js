/**
 * routes/analysis.routes.js
 * Mirrors backend/routes/ (analysis, tools endpoints)
 *
 * All API calls for text analysis features.
 */

const AnalysisAPI = {
    /**
     * POST /check
     * Main text analysis endpoint.
     * @param {string} text  - Input text to analyze
     * @param {string} mode  - "basic" | "tone" | "structural" | "clarity"
     * @param {string} tone  - Tone string (used only in "tone" mode)
     * @returns {{ corrected_text, highlighted_text, stats, grammar_errors, style_errors, ai_analysis }}
     */
    check(text, mode, tone = "Professional") {
        return apiFetch("/check", {
            method: "POST",
            body: JSON.stringify({ text, mode, tone }),
        });
    },

    /**
     * POST /ai_detect
     * Analyze text for AI-generated content.
     * @param {string} text
     * @returns {{ ai_probability: number, reasoning: string }}
     */
    detectAI(text) {
        return apiFetch("/ai_detect", {
            method: "POST",
            body: JSON.stringify({ text }),
        });
    },

    /**
     * POST /thesaurus
     * Look up synonyms and antonyms.
     * @param {string} word
     * @returns {{ synonyms: string[], antonyms: string[] }}
     */
    thesaurus(word) {
        return apiFetch("/thesaurus", {
            method: "POST",
            body: JSON.stringify({ word }),
        });
    },

    /**
     * POST /capitalize
     * Convert text to Title Case.
     * @param {string} text
     * @returns {{ capitalized: string }}
     */
    capitalize(text) {
        return apiFetch("/capitalize", {
            method: "POST",
            body: JSON.stringify({ text }),
        });
    },
};
