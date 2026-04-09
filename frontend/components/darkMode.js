/**
 * components/darkMode.js
 * Dark mode toggle — reusable across all pages
 *
 * Usage:
 *   DarkMode.init();                  // call on DOMContentLoaded
 *   DarkMode.toggle(event);           // call from onclick
 */

const DarkMode = {
    init() {
        const isDark = localStorage.getItem(AppConfig.STORAGE_KEYS.DARK_MODE) === "true";
        if (isDark) {
            document.body.classList.add("dark-mode");
            const sw = document.getElementById("darkModeSwitch");
            if (sw) sw.classList.add("active");
        }
    },

    toggle(e) {
        if (e) e.stopPropagation();
        const isDark = document.body.classList.toggle("dark-mode");
        const sw = document.getElementById("darkModeSwitch");
        if (sw) sw.classList.toggle("active");
        localStorage.setItem(AppConfig.STORAGE_KEYS.DARK_MODE, isDark);
    },
};
