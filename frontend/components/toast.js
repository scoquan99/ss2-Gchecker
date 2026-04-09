/**
 * components/toast.js
 * Reusable Toast notification component
 *
 * Usage:
 *   Toast.show("Message")
 *   Toast.show("Success!", "success")
 *   Toast.show("Error!", "error")
 *
 * Requires: a <div class="toast" id="toast"></div> in the page HTML.
 */

const Toast = {
    show(msg, kind = "", duration = 3200) {
        const el = document.getElementById("toast");
        if (!el) return;
        el.textContent = msg;
        el.className = "toast show" + (kind ? ` ${kind}` : "");
        clearTimeout(this._timer);
        this._timer = setTimeout(() => el.classList.remove("show"), duration);
    },
};
