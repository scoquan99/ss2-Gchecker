/**
 * routes/auth.routes.js
 * Mirrors backend/routes/auth_routes.py
 *
 * All API calls related to authentication.
 * Endpoint paths must match the backend route definitions exactly.
 */

const AuthAPI = {
    /**
     * POST /auth/login
     * @param {string} username
     * @param {string} password
     * @returns {{ token: string }}
     */
    login(username, password) {
        return apiFetch("/auth/login", {
            method: "POST",
            body: JSON.stringify({ username, password }),
        });
    },

    /**
     * POST /auth/register
     * @param {string} username
     * @param {string} email
     * @param {string} full_name
     * @param {string} password
     * @returns {{ message: string }}
     */
    register(username, email, full_name, password) {
        return apiFetch("/auth/register", {
            method: "POST",
            body: JSON.stringify({ username, email, full_name, password }),
        });
    },
};
