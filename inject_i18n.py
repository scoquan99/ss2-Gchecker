import re

def process_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove Google Translate
    content = re.sub(r'<div id="google_translate_element"[^>]*></div>', '', content)
    content = re.sub(r'<script type="text/javascript">\s*function googleTranslateElementInit\(\) \{.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script type="text/javascript" src="//translate\.google\.com/translate_a/element\.js\?cb=googleTranslateElementInit"></script>', '', content)

    # Lang switcher HTML
    lang_html = """<div class="lang-switcher-container">
                    <select class="lang-switcher" id="langSwitcher" onchange="applyLanguage(this.value)">
                        <option value="en" data-i18n="lang-en">English</option>
                        <option value="vi" data-i18n="lang-vi">Tiếng Việt</option>
                    </select>
                </div>"""

    if "index.html" in file_path:
        content = content.replace('<div class="header-controls">', f'<div class="header-controls">\n                {lang_html}')
    elif "login.html" in file_path or "register.html" in file_path:
        content = re.sub(r'(<h2>.*?</h2>)', r'\1\n        <div style="text-align: center; margin-bottom: 20px;">' + lang_html + "</div>", content)

    # Inject translations.js
    content = content.replace('</body>', '    <script src="translations.js"></script>\n</body>')

    if "index.html" in file_path:
        # Add styles
        style = """
        .lang-switcher-container {
            position: relative;
            margin-right: 15px;
        }
        .lang-switcher {
            appearance: none;
            background-color: #f3f4f6;
            border: 1px solid #d1d5db;
            padding: 8px 32px 8px 16px;
            border-radius: 20px;
            font-family: inherit;
            font-size: 14px;
            font-weight: 500;
            color: #374151;
            cursor: pointer;
            outline: none;
            transition: all 0.2s;
        }
        .lang-switcher:hover {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        .lang-switcher-container::after {
            content: "▼";
            font-size: 10px;
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: #6b7280;
        }
        """
        content = content.replace("</style>", style + "\n    </style>")

        # Maps string to data-i18n
        tag_map = [
            ('>Writing Assistant<', ' data-i18n="app-role">Writing Assistant<'),
            ('>Studio Desktop<', ' data-i18n="app-title">Studio Desktop<'),
            ('id="inputText" placeholder="Paste your comprehensive text here to analyze..."', 'id="inputText" data-i18n="input-placeholder" placeholder="Paste your comprehensive text here to analyze..."'),
            ('>Select Analysis Mode<', ' data-i18n="select-mode">Select Analysis Mode<'),
            ('>Basic Verification<', ' data-i18n="basic-title">Basic Verification<'),
            ('>Standard spelling & grammar checks.<', ' data-i18n="basic-desc">Standard spelling & grammar checks.<'),
            ('>Style & Tone Aligner<', ' data-i18n="tone-title">Style & Tone Aligner<'),
            ('>Set your tone and ensure consistent delivery.<', ' data-i18n="tone-desc">Set your tone and ensure consistent delivery.<'),
            ('>Structural Analysis<', ' data-i18n="structural-title">Structural Analysis<'),
            ('>Analyze sentence variation and paragraph flow.<', ' data-i18n="struct-desc">Analyze sentence variation and paragraph flow.<'),
            ('>Clarity Boost<', ' data-i18n="clarity-title">Clarity Boost<'),
            ('>Remove filler words and convert passive voice.<', ' data-i18n="clarity-desc">Remove filler words and convert passive voice.<'),
            ('>Impact Suggestions<', ' data-i18n="impact-title">Impact Suggestions<'),
            ('>Discover powerful synonyms & context-aware choices.<', ' data-i18n="impact-desc">Discover powerful synonyms & context-aware choices.<'),
            ('id="toneInput" placeholder="e.g. Formal, High-Energy, Academic..."', 'id="toneInput" data-i18n="tone-placeholder" placeholder="e.g. Formal, High-Energy, Academic..."'),
            ('>Analyze Text<', ' data-i18n="analyze-btn">Analyze Text<'),
            ('>✨ Optimized Text<', ' data-i18n="optimized-title">✨ Optimized Text<'),
            ('>🖍️ Sentence Highlights<', ' data-i18n="highlights-title">🖍️ Sentence Highlights<'),
            ('>📊 Writing Statistics<', ' data-i18n="stats-title">📊 Writing Statistics<'),
            ('>⚠️ Flags & Errors<', ' data-i18n="errors-title">⚠️ Flags & Errors<'),
            ('>🤖 Deep AI Analysis<', ' data-i18n="ai-panel-title">🤖 Deep AI Analysis<'),
            ('class="section-title">Extras / Tools Suite<', 'class="section-title" data-i18n="extras-title">Extras / Tools Suite<'),
            ('>📘 The Thesaurus<', ' data-i18n="thesaurus-title">📘 The Thesaurus<'),
            ('>Dive deep into NLTK WordNet semantics.<', ' data-i18n="thesaurus-desc">Dive deep into NLTK WordNet semantics.<'),
            ('id="thesaurusInput" class="tool-input" placeholder="Type a word..."', 'id="thesaurusInput" class="tool-input" data-i18n="thesaurus-placeholder" placeholder="Type a word..."'),
            ('>Lookup<', ' data-i18n="thesaurus-btn">Lookup<'),
            ('>🔠 Title Capitalizer<', ' data-i18n="cap-title">🔠 Title Capitalizer<'),
            ('>Format any string into perfect Title Case.<', ' data-i18n="cap-desc">Format any string into perfect Title Case.<'),
            ('id="capitalizeInput" class="tool-input" placeholder="Enter messy title..."', 'id="capitalizeInput" class="tool-input" data-i18n="cap-placeholder" placeholder="Enter messy title..."'),
            ('>Capitalize<', ' data-i18n="cap-btn">Capitalize<'),
            ('>🤖 AI Detector Core<', ' data-i18n="ai-detect-title">🤖 AI Detector Core<'),
            ('>Analyze the main text area for AI footprints.<', ' data-i18n="ai-detect-desc">Analyze the main text area for AI footprints.<'),
            ('>Check Text for AI<', ' data-i18n="ai-detect-btn">Check Text for AI<'),
            ('<span>Home Dashboard</span>', '<span data-i18n="nav-dash">Home Dashboard</span>'),
            ('<span>Deep Analysis</span>', '<span data-i18n="nav-analysis">Deep Analysis</span>'),
            ('<span>Saved Projects</span>', '<span data-i18n="nav-projects">Saved Projects</span>'),
            ('<span>Check History</span>', '<span data-i18n="nav-history">Check History</span>')
        ]
        
        for search, replace in tag_map:
            content = content.replace(search, replace)
            
    elif "login.html" in file_path:
        tag_map = [
            ('<h2>Login</h2>', '<h2 data-i18n="login-title">Login</h2>'),
            ('<label for="username">Username</label>', '<label for="username" data-i18n="username-label">Username</label>'),
            ('<label for="password">Password</label>', '<label for="password" data-i18n="password-label">Password</label>'),
            ('<button type="submit" class="auth-btn">Login</button>', '<button type="submit" class="auth-btn" data-i18n="login-btn">Login</button>'),
            ('<p>Don\'t have an account? <a href="register.html">Register here</a></p>', '<p><span data-i18n="no-account">Don\'t have an account?</span> <a href="register.html" data-i18n="register-here">Register here</a></p>')
        ]
        for search, replace in tag_map:
            content = content.replace(search, replace)

        # Style for login
        style = """
        .lang-switcher-container {
            position: relative;
            display: inline-block;
        }
        .lang-switcher {
            appearance: none;
            background-color: var(--card-bg, #fff);
            border: 1px solid var(--border, #e5e7eb);
            padding: 6px 28px 6px 12px;
            border-radius: 6px;
            font-family: inherit;
            font-size: 13px;
            color: var(--text, #111827);
            cursor: pointer;
            outline: none;
        }
        .lang-switcher:hover { border-color: #3b82f6; }
        .lang-switcher-container::after {
            content: "▼";
            font-size: 9px;
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: #6b7280;
        }
        """
        content = content.replace("</style>", style + "\n    </style>")
            
    elif "register.html" in file_path:
        tag_map = [
            ('<h2>Register</h2>', '<h2 data-i18n="register-title">Register</h2>'),
            ('<label for="username">Username</label>', '<label for="username" data-i18n="username-label">Username</label>'),
            ('<label for="password">Password</label>', '<label for="password" data-i18n="password-label">Password</label>'),
            ('<label for="confirmPassword">Confirm Password</label>', '<label for="confirmPassword" data-i18n="confirm-label">Confirm Password</label>'),
            ('<button type="submit" class="auth-btn">Register</button>', '<button type="submit" class="auth-btn" data-i18n="register-btn">Register</button>'),
            ('<p>Already have an account? <a href="login.html">Login here</a></p>', '<p><span data-i18n="already-account">Already have an account?</span> <a href="login.html" data-i18n="login-here">Login here</a></p>')
        ]
        for search, replace in tag_map:
            content = content.replace(search, replace)

        # Style for register
        style = """
        .lang-switcher-container {
            position: relative;
            display: inline-block;
        }
        .lang-switcher {
            appearance: none;
            background-color: var(--card-bg, #fff);
            border: 1px solid var(--border, #e5e7eb);
            padding: 6px 28px 6px 12px;
            border-radius: 6px;
            font-family: inherit;
            font-size: 13px;
            color: var(--text, #111827);
            cursor: pointer;
            outline: none;
        }
        .lang-switcher:hover { border-color: #3b82f6; }
        .lang-switcher-container::after {
            content: "▼";
            font-size: 9px;
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: #6b7280;
        }
        """
        content = content.replace("</style>", style + "\n    </style>")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Processing index.html")
process_html_file(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\index.html")
print("Processing login.html")
process_html_file(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\login.html")
print("Processing register.html")
process_html_file(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\register.html")
print("Done!")
