/**
 * components/errorHandler.js
 * Reusable form error display + HTTP status → user message mapping
 *
 * Usage:
 *   ErrorHandler.showBanner("errorBannerText", "errorBanner", "Something went wrong");
 *   ErrorHandler.clearBanner("errorBanner", ["fieldA", "fieldB"]);
 *   const msg = ErrorHandler.getMessage(err, "auth");   // "auth" | "register" | "general"
 */

const ErrorHandler = {
    /**
     * Show an error banner and optionally highlight a field
     */
    showBanner(textId, bannerId, msg, fieldId = null) {
        const textEl   = document.getElementById(textId);
        const bannerEl = document.getElementById(bannerId);
        if (textEl)   textEl.textContent = msg;
        if (bannerEl) bannerEl.classList.add("visible");
        if (fieldId) {
            const field = document.getElementById(fieldId);
            if (field) field.classList.add("has-error");
            const input = field?.querySelector("input");
            if (input) input.focus();
        }
    },

    /**
     * Clear error banner and all field error highlights
     */
    clearBanner(bannerId, fieldIds = []) {
        const bannerEl = document.getElementById(bannerId);
        if (bannerEl) bannerEl.classList.remove("visible");
        fieldIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.remove("has-error");
        });
    },

    /**
     * Map HTTP status codes to user-friendly messages.
     * context: "auth" | "register" | "analysis" | "general"
     */
    getMessage(err, context = "general") {
        const status = err?.status ?? 0;

        const contextMap = {
            auth: {
                400: "Invalid username or password format.",
                401: "Incorrect username or password. Please try again.",
                404: "Account not found. Check your username.",
            },
            register: {
                400: err.message || "Please check your input and try again.",
                409: "This username or email is already registered.",
                422: "Invalid data. Please review your entries.",
            },
            analysis: {
                400: "Invalid text input.",
                401: "Session expired. Please sign in again.",
            },
        };

        const sharedMap = {
            429: "Too many requests. Please wait a moment.",
            500: "Server error. Please try again shortly.",
            503: "Server unavailable. Please try again shortly.",
            408: "Request timed out. Check your connection.",
            0:   "Cannot reach server. Check your internet connection.",
        };

        const specific = contextMap[context]?.[status];
        const shared   = sharedMap[status];
        return specific || shared || err?.message || "Something went wrong. Please try again.";
    },
};
