/**
 * middleware/auth.guard.js
 * Mirrors backend/middleware/ (auth middleware)
 *
 * Client-side auth guard: checks session state and redirects
 * unauthenticated users — just like @require_token decorators on the backend.
 *
 * Usage (add at top of any protected page's <script>):
 *   AuthGuard.requireAuth();     // redirect to login if not logged in
 *   AuthGuard.requireGuest();    // redirect to index if already logged in
 */

const AuthGuard = {
    /**
     * Protect a page: if no token found, redirect to login.
     * Use on index.html (protected pages).
     */
    requireAuth(redirectTo = "login.html") {
        if (!Session.isLoggedIn()) {
            window.location.replace(redirectTo);
        }
    },

    /**
     * Guest-only pages: if already logged in, redirect away.
     * Use on login.html and register.html.
     */
    requireGuest(redirectTo = "index.html") {
        if (Session.isLoggedIn()) {
            window.location.replace(redirectTo);
        }
    },
};
