/**
 * assets/js/translations.js
 * Internationalization (i18n) — full language strings + apply logic
 * Supports: English (en), French (fr), Spanish (es)
 * Vietnamese is intentionally excluded to keep the UI language-consistent.
 */

const translations = {

    /* ─────────────── ENGLISH (default) ─────────────── */
    en: {
        // Brand
        "app-role":  "PRECISION LAB",
        "app-title": "Lumina Text Studio",

        // Input
        "input-placeholder": "Write or paste your text here... (10+ words for deeper analysis)",

        // Mode selector
        "select-mode": "Select Analysis Mode",
        "basic-title": "Basic Check",
        "basic-desc":  "Grammar, spelling & style",
        "tone-title":  "Tone Shaping",
        "tone-desc":   "Sync emotion & rhythm",
        "structural-title": "Structural Clarity",
        "struct-desc":      "Sentence variation & logical flow",
        "clarity-title": "Clarity Optimizer",
        "clarity-desc":  "Remove filler words & passive voice",
        "impact-title": "Word Impact",
        "impact-desc":  "Synonyms & vocabulary upgrade",
        "tone-placeholder": "e.g. Persuasive / Warm / Technical / Storytelling...",

        // Main action
        "analyze-btn": "Analyze & Refine",

        // Results panel
        "optimized-title":   "Polished Text",
        "highlights-title":  "Sentence Highlights",
        "stats-title":       "Writing Stats",
        "errors-title":      "Improvement Suggestions",
        "ai-panel-title":    "Deep AI Analysis",
        "ai-optimized-title": "AI Deep Analysis Results",

        // Extras / tools
        "extras-title":        "Expert Toolkit",
        "thesaurus-title":     "Thesaurus",
        "thesaurus-desc":      "WordNet synonyms & antonyms",
        "thesaurus-placeholder": "Enter a word to look up...",
        "thesaurus-btn":       "Explore",
        "cap-title":           "Title Case Formatter",
        "cap-desc":            "AP/MLA standard formatting",
        "cap-placeholder":     "enter messy title here",
        "cap-btn":             "Format",
        "ai-detect-title":     "AI Origin Scanner",
        "ai-detect-desc":      "Detects probability of AI-generated content",
        "ai-detect-btn":       "Scan Main Text",
        "summarize-title":     "Text Summarizer",
        "summarize-desc":      "AI condenses key points in seconds",
        "sum-short":           "Short",
        "sum-medium":          "Medium",
        "sum-detailed":        "Detailed",
        "summarize-btn":       "Summarize Now",
        "para-title":          "Paraphrase",
        "para-desc":           "Rewrite differently to avoid plagiarism",
        "para-standard":       "Standard",
        "para-creative":       "Creative",
        "para-formal":         "Formal",
        "para-simple":         "Simple",
        "para-btn":            "Rewrite Now",
        "diff-title":          "Before / After Compare",
        "diff-desc":           "See exactly what changed after analysis",
        "diff-btn":            "View Changes",

        // Popup
        "analyzing-popup-title": "Analyzing Your Text",
        "analyzing-popup-desc":  "Our AI engine is running a deep analysis. This may take a few seconds...",
        "results-popup-title":   "Analysis Complete",
        "results-popup-desc":    "Here are your full results.",

        // Dropdown
        "dropdown-login":    "Log in / Sign up",
        "dropdown-logout":   "Log out",
        "dropdown-lang":     "Language",
        "dropdown-darkmode": "Dark mode",
        "dropdown-help":     "Help Center",

        // AI Detector
        "ai-detect-title": "AI Origin Scanner",
        "ai-detect-desc":  "Detects probability of AI-generated content",
        "ai-detect-btn":   "Scan Main Text",

        // Summarizer
        "summarize-title": "Text Summarizer",
        "summarize-desc":  "AI condenses key ideas in seconds",
        "sum-short":       "Short",
        "sum-medium":      "Medium",
        "sum-detailed":    "Detailed",
        "summarize-btn":   "Summarize Now",

        // Paraphrase
        "para-title":    "Paraphrase",
        "para-desc":     "Rewrite to avoid plagiarism",
        "para-standard": "Standard",
        "para-creative": "Creative",
        "para-formal":   "Formal",
        "para-simple":   "Simple",
        "para-btn":      "Rewrite Now",

        // Diff
        "diff-title": "Before / After Comparison",
        "diff-desc":  "See exactly what changed after analysis",
        "diff-btn":   "View Changes",

        // Language names
        "lang-en": "English",
        "lang-fr": "Français",
        "lang-es": "Español",
    },

    /* ─────────────── FRENCH ─────────────── */
    fr: {
        // Brand
        "app-role":  "LAB DE PRÉCISION",
        "app-title": "Lumina Text Studio",

        // Input
        "input-placeholder": "Écrivez ou collez votre texte ici... (10+ mots pour une analyse approfondie)",

        // Mode selector
        "select-mode": "Choisir le mode d'analyse",
        "basic-title": "Vérification de base",
        "basic-desc":  "Grammaire, orthographe & style",
        "tone-title":  "Façonnage du ton",
        "tone-desc":   "Synchroniser émotion & rythme",
        "structural-title": "Clarté structurelle",
        "struct-desc":      "Variation de phrases & fluidité logique",
        "clarity-title": "Optimiseur de clarté",
        "clarity-desc":  "Supprimer les mots de remplissage & voix passive",
        "impact-title": "Impact des mots",
        "impact-desc":  "Synonymes & amélioration du vocabulaire",
        "tone-placeholder": "ex. Persuasif / Chaleureux / Technique / Narratif...",

        // Main action
        "analyze-btn": "Analyser & Affiner",

        // Results panel
        "optimized-title":   "Texte peaufiné",
        "highlights-title":  "Points saillants",
        "stats-title":       "Statistiques d'écriture",
        "errors-title":      "Suggestions d'amélioration",
        "ai-panel-title":    "Analyse IA approfondie",
        "ai-optimized-title": "Résultats de l'analyse IA",

        // Extras / tools
        "extras-title":        "Boîte à outils expert",
        "thesaurus-title":     "Thésaurus",
        "thesaurus-desc":      "Synonymes & antonymes WordNet",
        "thesaurus-placeholder": "Entrez un mot à rechercher...",
        "thesaurus-btn":       "Explorer",
        "cap-title":           "Formateur de titre",
        "cap-desc":            "Formatage standard AP/MLA",
        "cap-placeholder":     "entrez un titre désordonné ici",
        "cap-btn":             "Formater",
        "ai-detect-title":     "Détecteur d'origine IA",
        "ai-detect-desc":      "Détecte la probabilité de contenu généré par IA",
        "ai-detect-btn":       "Scanner le texte principal",
        "summarize-title":     "Résumé de texte",
        "summarize-desc":      "L'IA condense les points clés en quelques secondes",
        "sum-short":           "Court",
        "sum-medium":          "Moyen",
        "sum-detailed":        "Détaillé",
        "summarize-btn":       "Résumer maintenant",
        "para-title":          "Paraphrase",
        "para-desc":           "Réécrire différemment pour éviter le plagiat",
        "para-standard":       "Standard",
        "para-creative":       "Créatif",
        "para-formal":         "Formel",
        "para-simple":         "Simple",
        "para-btn":            "Réécrire maintenant",
        "diff-title":          "Comparaison Avant / Après",
        "diff-desc":           "Voyez exactement ce qui a changé après l'analyse",
        "diff-btn":            "Voir les changements",

        // Popup
        "analyzing-popup-title": "Analyse en cours",
        "analyzing-popup-desc":  "Notre moteur IA effectue une analyse approfondie. Cela peut prendre quelques secondes...",
        "results-popup-title":   "Analyse terminée",
        "results-popup-desc":    "Voici vos résultats complets.",

        // Dropdown
        "dropdown-login":    "Se connecter / S'inscrire",
        "dropdown-logout":   "Se déconnecter",
        "dropdown-lang":     "Langue",
        "dropdown-darkmode": "Mode sombre",
        "dropdown-help":     "Centre d'aide",

        // AI Detector
        "ai-detect-title": "Scanner d'origine IA",
        "ai-detect-desc":  "Détecte la probabilité de contenu généré par IA",
        "ai-detect-btn":   "Scanner le texte principal",

        // Summarizer
        "summarize-title": "Résumé de texte",
        "summarize-desc":  "L'IA condense les idées clés en quelques secondes",
        "sum-short":       "Court",
        "sum-medium":      "Moyen",
        "sum-detailed":    "Détaillé",
        "summarize-btn":   "Résumer maintenant",

        // Paraphrase
        "para-title":    "Paraphrase",
        "para-desc":     "Réécrire pour éviter le plagiat",
        "para-standard": "Standard",
        "para-creative": "Créatif",
        "para-formal":   "Formel",
        "para-simple":   "Simple",
        "para-btn":      "Réécrire maintenant",

        // Diff
        "diff-title": "Comparaison Avant / Après",
        "diff-desc":  "Voyez exactement ce qui a changé après l'analyse",
        "diff-btn":   "Voir les modifications",

        // Language names
        "lang-en": "English",
        "lang-fr": "Français",
        "lang-es": "Español",
    },

    /* ─────────────── SPANISH ─────────────── */
    es: {
        // Brand
        "app-role":  "LAB DE PRECISIÓN",
        "app-title": "Lumina Text Studio",

        // Input
        "input-placeholder": "Escribe o pega tu texto aquí... (10+ palabras para análisis profundo)",

        // Mode selector
        "select-mode": "Seleccionar modo de análisis",
        "basic-title": "Revisión básica",
        "basic-desc":  "Gramática, ortografía & estilo",
        "tone-title":  "Ajuste de tono",
        "tone-desc":   "Sincronizar emoción & ritmo",
        "structural-title": "Claridad estructural",
        "struct-desc":      "Variación de oraciones & fluidez lógica",
        "clarity-title": "Optimizador de claridad",
        "clarity-desc":  "Eliminar muletillas & voz pasiva",
        "impact-title": "Impacto de palabras",
        "impact-desc":  "Sinónimos & mejora de vocabulario",
        "tone-placeholder": "ej. Persuasivo / Cálido / Técnico / Narrativo...",

        // Main action
        "analyze-btn": "Analizar & Refinar",

        // Results panel
        "optimized-title":   "Texto pulido",
        "highlights-title":  "Fragmentos destacados",
        "stats-title":       "Estadísticas de escritura",
        "errors-title":      "Sugerencias de mejora",
        "ai-panel-title":    "Análisis IA profundo",
        "ai-optimized-title": "Resultados del análisis IA",

        // Extras / tools
        "extras-title":        "Kit de herramientas experto",
        "thesaurus-title":     "Tesauro",
        "thesaurus-desc":      "Sinónimos & antónimos WordNet",
        "thesaurus-placeholder": "Ingresa una palabra para buscar...",
        "thesaurus-btn":       "Explorar",
        "cap-title":           "Formateador de títulos",
        "cap-desc":            "Formato estándar AP/MLA",
        "cap-placeholder":     "ingresa un título desordenado aquí",
        "cap-btn":             "Formatear",
        "ai-detect-title":     "Escanner de origen IA",
        "ai-detect-desc":      "Detecta la probabilidad de contenido generado por IA",
        "ai-detect-btn":       "Escanear texto principal",
        "summarize-title":     "Resumidor de texto",
        "summarize-desc":      "La IA condensa los puntos clave en segundos",
        "sum-short":           "Corto",
        "sum-medium":          "Medio",
        "sum-detailed":        "Detallado",
        "summarize-btn":       "Resumir ahora",
        "para-title":          "Paráfrasis",
        "para-desc":           "Reescribir de forma diferente para evitar el plagio",
        "para-standard":       "Estándar",
        "para-creative":       "Creativo",
        "para-formal":         "Formal",
        "para-simple":         "Simple",
        "para-btn":            "Reescribir ahora",
        "diff-title":          "Comparación Antes / Después",
        "diff-desc":           "Ve exactamente qué cambió después del análisis",
        "diff-btn":            "Ver cambios",

        // Popup
        "analyzing-popup-title": "Analizando tu texto",
        "analyzing-popup-desc":  "Nuestro motor IA está realizando un análisis profundo. Esto puede tardar unos segundos...",
        "results-popup-title":   "Análisis completo",
        "results-popup-desc":    "Aquí están tus resultados completos.",

        // Dropdown
        "dropdown-login":    "Iniciar sesión / Registrarse",
        "dropdown-logout":   "Cerrar sesión",
        "dropdown-lang":     "Idioma",
        "dropdown-darkmode": "Modo oscuro",
        "dropdown-help":     "Centro de ayuda",

        // AI Detector
        "ai-detect-title": "Detector de origen IA",
        "ai-detect-desc":  "Detecta la probabilidad de contenido generado por IA",
        "ai-detect-btn":   "Escanear texto principal",

        // Summarizer
        "summarize-title": "Resumidor de texto",
        "summarize-desc":  "La IA condensa las ideas clave en segundos",
        "sum-short":       "Corto",
        "sum-medium":      "Medio",
        "sum-detailed":    "Detallado",
        "summarize-btn":   "Resumir ahora",

        // Paraphrase
        "para-title":    "Paráfrasis",
        "para-desc":     "Reescribir para evitar el plagio",
        "para-standard": "Estándar",
        "para-creative": "Creativo",
        "para-formal":   "Formal",
        "para-simple":   "Simple",
        "para-btn":      "Reescribir ahora",

        // Diff
        "diff-title": "Comparación Antes / Después",
        "diff-desc":  "Ve exactamente qué cambió después del análisis",
        "diff-btn":   "Ver cambios",

        // Language names
        "lang-en": "English",: translate a single key in current language
   Usage: t('analyze-btn')  →  'Analyze & Refine'
───────────────────────────────────────────────────── */
window.t = function(key, fallback) {
    const lang = localStorage.getItem(AppConfig.STORAGE_KEYS.APP_LANG) || AppConfig.DEFAULT_LANG;
    const dict = translations[lang] || translations[AppConfig.DEFAULT_LANG];
    return dict[key] ?? fallback ?? key;
};

/* ─────────────────────────────────────────────────────
   Core: apply all [data-i18n] elements on the page
───────────────────────────────────────────────────── */
function applyLanguage(lang) {
    // Normalise & persist
    const supported = Object.keys(translations);
    if (!supported.includes(lang)) lang = AppConfig.DEFAULT_LANG;
    localStorage.setItem(AppConfig.STORAGE_KEYS.APP_LANG, lang);

    const dict = translations[lang];

    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (!dict[key]) return;

        // Inputs / textareas — update placeholder
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
            el.placeholder = dict[key];
            return;
        }

        // Elements that contain child <i> icons — preserve icons, replace only text
        const icons = el.querySelectorAll("i, svg");
        if (icons.length > 0) {
            // Save all icon nodes
            const savedIcons = Array.from(icons).map(ic => ic.cloneNode(true));
            // Replace full content then re-insert icons at start
            el.textContent = " " + dict[key];
            savedIcons.reverse().forEach(ic => el.prepend(ic));
            return;
        }

        // Plain text elements
        el.textContent = dict[key];
    });

    // Sync the language switcher dropdown
    const langSelect = document.getElementById("langSwitcher");
    if (langSelect) langSelect.value = lang;

    // Update <html lang=""> for accessibility
    document.documentElement.lang = lang;
}

/* ─────────────────────────────────────────────────────
   Called from the dropdown onChange handler
   (mirrors handleLangChange in index.html)
───────────────────────────────────────────────────── */
window.applyLanguage = applyLanguage;

/* ─────────────────────────────────────────────────────
   Auto-init on DOM ready
───────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
    const savedLang = localStorage.getItem(AppConfig.STORAGE_KEYS.APP_LANG) || AppConfig.DEFAULT_LANG;
    applyLanguage(savedLang);
});
