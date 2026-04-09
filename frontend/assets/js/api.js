/**
 * assets/js/api.js
 * Core API fetch engine
 * Mirrors backend/app.py request/response handling patterns
 *
 * Provides: APIError class + apiFetch() base function
 * Used by: routes/auth.routes.js, routes/analysis.routes.js
 */

/**
 * APIError — structured error object
 * Carries HTTP status code + message + original cause
 */
class APIError extends Error {
    constructor(message, status = 0, cause = null) {
        super(message);
        this.name   = "APIError";
        this.status = status;   // 0 = network/offline error
        this.cause  = cause;
    }
}

/**
 * apiFetch — base fetch wrapper
 *
 * Automatically:
 *  - Prepends AppConfig.API_BASE_URL
 *  - Injects Authorization: Bearer <token> if session exists
 *  - Enforces timeout via AbortController
 *  - Normalizes all errors into APIError
 *  - Returns parsed JSON body or throws APIError
 */
async function apiFetch(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId  = setTimeout(() => controller.abort(), AppConfig.API_TIMEOUT_MS);

    const token   = Session.getToken();
    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    try {
        const res = await fetch(`${AppConfig.API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Parse body regardless of status (server may return {error: "..."} on 4xx)
        let data;
        const ct = res.headers.get("content-type") || "";
        data = ct.includes("application/json")
            ? await res.json()
            : { message: await res.text() };

        if (!res.ok) {
            throw new APIError(data?.error || data?.message || `HTTP ${res.status}`, res.status);
        }

        return data;

    } catch (err) {
        clearTimeout(timeoutId);
        if (err.name === "AbortError")  throw new APIError("Request timed out. Please try again.", 408);
        if (err instanceof APIError)    throw err;
        throw new APIError(`Network error: ${err.message}`, 0, err);
    }
}
