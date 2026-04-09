/**
 * assets/js/translations.js
 * Internationalization (i18n) — language strings + apply logic
 * Mirrors backend i18n / locale pattern
 */

const translations = {
    en: {
        "app-role": "Writing Assistant",
        "app-title": "Text Quality Checker Pro",
        "input-placeholder": "Paste your comprehensive text here to analyze...",
        "select-mode": "Select Analysis Mode",
        "basic-title": "Basic Verification",
        "basic-desc": "Standard spelling & grammar checks.",
        "tone-title": "Style & Tone Aligner",
        "tone-desc": "Set your tone and ensure consistent delivery.",
        "structural-title": "Structural Analysis",
        "struct-desc": "Analyze sentence variation and paragraph flow.",
        "clarity-title": "Clarity Boost",
        "clarity-desc": "Remove filler words and convert passive voice.",
        "impact-title": "Impact Suggestions",
        "impact-desc": "Discover powerful synonyms & context-aware choices.",
        "tone-placeholder": "e.g. Formal, High-Energy, Academic...",
        "analyze-btn": "Analyze Text",
        "optimized-title": "✨ Optimized Text",
        "highlights-title": "🖍️ Sentence Highlights",
        "stats-title": "📊 Writing Statistics",
        "errors-title": "⚠️ Flags & Errors",
        "ai-panel-title": "🤖 Deep AI Analysis",
        "extras-title": "Extras / Tools Suite",
        "thesaurus-title": "📘 The Thesaurus",
        "thesaurus-desc": "Dive deep into NLTK WordNet semantics.",
        "thesaurus-placeholder": "Type a word...",
        "thesaurus-btn": "Lookup",
        "cap-title": "🔠 Title Capitalizer",
        "cap-desc": "Format any string into perfect Title Case.",
        "cap-placeholder": "Enter messy title...",
        "cap-btn": "Capitalize",
        "ai-detect-title": "🤖 AI Detector Core",
        "ai-detect-desc": "Analyze the main text area for AI footprints.",
        "ai-detect-btn": "Check Text for AI",
        "nav-dash": "Home Dashboard",
        "nav-analysis": "Deep Analysis",
        "nav-projects": "Saved Projects",
        "nav-history": "Check History",
        "dropdown-login": "Log in / Sign up",
        "dropdown-darkmode": "Dark mode",
        "dropdown-help": "Help Center",
        "dropdown-contact": "Contact us",
        "lang-en": "English",
        "lang-vi": "Tiếng Việt",
    },
    vi: {
        "app-role": "Trợ lý Viết",
        "app-title": "Studio Máy Tính",
        "input-placeholder": "Dán văn bản chi tiết của bạn vào đây để phân tích...",
        "select-mode": "Chọn Chế độ Phân tích",
        "basic-title": "Xác minh Cơ bản",
        "basic-desc": "Kiểm tra chính tả & ngữ pháp tiêu chuẩn.",
        "tone-title": "Điều chỉnh Phong cách & Giọng điệu",
        "tone-desc": "Thiết lập giọng điệu và đảm bảo sự nhất quán.",
        "structural-title": "Phân tích Cấu trúc",
        "struct-desc": "Phân tích sự đa dạng câu và luồng đoạn văn.",
        "clarity-title": "Tăng cường Độ rõ ràng",
        "clarity-desc": "Loại bỏ từ thừa và chuyển đổi câu bị động.",
        "impact-title": "Đề xuất Tác động",
        "impact-desc": "Khám phá từ đồng nghĩa mạnh mẽ & lựa chọn ngữ cảnh.",
        "tone-placeholder": "vd. Trang trọng, Năng lượng cao, Học thuật...",
        "analyze-btn": "Phân tích Văn bản",
        "optimized-title": "✨ Văn bản Tối ưu",
        "highlights-title": "🖍️ Câu Nổi bật",
        "stats-title": "📊 Thống kê Viết",
        "errors-title": "⚠️ Cảnh báo & Lỗi",
        "ai-panel-title": "🤖 Phân tích AI Sâu",
        "extras-title": "Tính năng Bổ sung / Bộ công cụ",
        "thesaurus-title": "📘 Từ điển Đồng nghĩa",
        "thesaurus-desc": "Khám phá sâu ngữ nghĩa NLTK WordNet.",
        "thesaurus-placeholder": "Nhập một từ...",
        "thesaurus-btn": "Tra cứu",
        "cap-title": "🔠 Viết hoa Tiêu đề",
        "cap-desc": "Định dạng chuỗi thành Title Case hoàn hảo.",
        "cap-placeholder": "Nhập tiêu đề...",
        "cap-btn": "Viết hoa",
        "ai-detect-title": "🤖 Lõi Phát hiện AI",
        "ai-detect-desc": "Phân tích vùng văn bản chính để tìm dấu vết AI.",
        "ai-detect-btn": "Kiểm tra Văn bản vùng AI",
        "nav-dash": "Bảng Điều khiển",
        "nav-analysis": "Phân tích Sâu",
        "nav-projects": "Dự án đã Lưu",
        "nav-history": "Lịch sử Kiểm tra",
        "dropdown-login": "Đăng nhập / Đăng ký",
        "dropdown-darkmode": "Chế độ tối",
        "dropdown-help": "Trung tâm Trợ giúp",
        "dropdown-contact": "Liên hệ chúng tôi",
        "lang-en": "Anh (English)",
        "lang-vi": "Tiếng Việt",
    }
};

function applyLanguage(lang) {
    localStorage.setItem(AppConfig.STORAGE_KEYS.APP_LANG, lang);
    const dict = translations[lang] || translations["en"];
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (!dict[key]) return;
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
            el.placeholder = dict[key];
        } else {
            el.textContent = dict[key];
        }
    });
    const langSelect = document.getElementById("langSwitcher");
    if (langSelect) langSelect.value = lang;
}

document.addEventListener("DOMContentLoaded", () => {
    const savedLang = localStorage.getItem(AppConfig.STORAGE_KEYS.APP_LANG) || AppConfig.DEFAULT_LANG;
    applyLanguage(savedLang);
});
