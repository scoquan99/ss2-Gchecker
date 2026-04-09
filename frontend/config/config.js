/**
 * config/config.js
 * Mirrors backend/config.py
 *
 * Single source of truth for all environment-level settings.
 * To switch environments, only this file needs to change.
 */

const AppConfig = {
    // API base URL — mirrors BASE_URL / FLASK_RUN_HOST in backend config.py
    API_BASE_URL: "http://localhost:5000",

    // Request timeout in milliseconds
    API_TIMEOUT_MS: 15000,

    // App metadata
    APP_NAME: "Text Quality Checker Pro",
    APP_VERSION: "1.0.0",

    // Supported languages
    SUPPORTED_LANGS: ["en", "vi"],
    DEFAULT_LANG: "en",

    // Local storage keys (centralized to avoid typos)
    STORAGE_KEYS: {
        TOKEN:     "token",
        USERNAME:  "username",
        DARK_MODE: "darkMode",
        APP_LANG:  "appLang",
    },
};
