/**
 * middleware/session.js
 * Mirrors backend session/token handling
 *
 * Centralizes all localStorage access for auth tokens.
 * No other file should directly read/write token from localStorage.
 */

const Session = {
    getToken:    () => localStorage.getItem(AppConfig.STORAGE_KEYS.TOKEN),
    getUsername: () => localStorage.getItem(AppConfig.STORAGE_KEYS.USERNAME),
    isLoggedIn:  () => !!localStorage.getItem(AppConfig.STORAGE_KEYS.TOKEN),

    save(token, username) {
        localStorage.setItem(AppConfig.STORAGE_KEYS.TOKEN,    token);
        localStorage.setItem(AppConfig.STORAGE_KEYS.USERNAME, username);
    },

    clear() {
        localStorage.removeItem(AppConfig.STORAGE_KEYS.TOKEN);
        localStorage.removeItem(AppConfig.STORAGE_KEYS.USERNAME);
    },
};
