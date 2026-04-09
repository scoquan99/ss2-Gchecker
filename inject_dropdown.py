import re

def process_file():
    with open(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. ADD CSS Variables and Dark Mode Support
    root_css = """
        :root {
            --bg-color: #f3f4f6;
            --text-color: #111827;
            --card-bg: #ffffff;
            --border-color: #e5e7eb;
            --avatar-bg: #e5e7eb;
            --avatar-hover: #d1d5db;
            --text-muted: #6b7280;
            --hover-bg: #f9fafb;
            --active-bg: #eff6ff;
            --active-border: #3b82f6;
            --btn-bg: linear-gradient(135deg, #111827, #374151);
            --btn-text: #ffffff;
            --input-bg: #ffffff;
            --icon-bg: #f3f4f6;
            --panel-bg: #fdfdfd;
        }

        body.dark-mode {
            --bg-color: #121212;
            --text-color: #e5e7eb;
            --card-bg: #1e1e1e;
            --border-color: #333333;
            --avatar-bg: #333333;
            --avatar-hover: #444444;
            --text-muted: #9ca3af;
            --hover-bg: #2a2a2a;
            --active-bg: #1a2c4e;
            --active-border: #3b82f6;
            --btn-bg: linear-gradient(135deg, #3b82f6, #2563eb);
            --btn-text: #ffffff;
            --input-bg: #1e1e1e;
            --icon-bg: #2d2d2d;
            --panel-bg: #1a1a1a;
        }
    """

    # Replace hardcoded colors in CSS with variables
    replacements = [
        ("background-color: #f3f4f6;", "background-color: var(--bg-color);"),
        ("color: #111827;", "color: var(--text-color);"),
        ("background: #ffffff;", "background: var(--card-bg);"),
        ("border-bottom: 1px solid #e5e7eb;", "border-bottom: 1px solid var(--border-color);"),
        ("background: #e5e7eb;", "background: var(--avatar-bg);"),
        ("background: #d1d5db;", "background: var(--avatar-hover);"),
        ("border: 2px solid #e5e7eb;", "border: 2px solid var(--border-color);"),
        ("border: 1px solid #e5e7eb;", "border: 1px solid var(--border-color);"),
        ("border: 1px solid #d1d5db;", "border: 1px solid var(--border-color);"),
        ("background: #fff;", "background: var(--card-bg);"),
        ("border-color: #3b82f6; background: #eff6ff;", "border-color: var(--active-border); background: var(--active-bg);"),
        ("background: #f3f4f6;", "background: var(--icon-bg);"),
        ("color: #6b7280;", "color: var(--text-muted);"),
        ("background: linear-gradient(135deg, #111827, #374151);", "background: var(--btn-bg);"),
        ("border-top: 2px solid #e5e7eb;", "border-top: 2px solid var(--border-color);"),
        ("background: #f9fafb;", "background: var(--hover-bg);"),
        ("background: #fdfdfd;", "background: var(--panel-bg);"),
        ("color: #374151;", "color: var(--text-color);"),
        ("color: #4b5563;", "color: var(--text-muted);"),
        ("color: #1f2937;", "color: var(--text-color);"),
    ]
    
    # Needs a bit of custom regex for text area colors
    content = content.replace("</style>", """
        textarea, input, select {
            color: var(--text-color);
            background-color: var(--input-bg);
        }
        pre#aiAnalysisOutput { color: var(--text-color) !important; }
        #correctedText, #sentenceHighlightsDiv, .result-card h4 { color: var(--text-color) !important; }
        
        /* Dropdown Styles */
        .profile-dropdown {
            position: absolute;
            top: 55px;
            right: 0;
            width: 260px;
            background: #18191c;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            z-index: 1000;
            overflow: hidden;
            display: none;
            border: 1px solid #2a2c31;
        }
        .profile-dropdown.open {
            display: block;
        }
        .dropdown-group {
            border-bottom: 1px solid #2a2c31;
            padding: 8px 0;
        }
        .dropdown-group:last-child {
            border-bottom: none;
        }
        .dropdown-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            color: #d1d5db;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            position: relative;
        }
        .dropdown-item:hover {
            background: #232529;
            color: #ffffff;
        }
        .dropdown-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 14px;
            color: #8ca3c6;
        }
        .dropdown-item:hover .dropdown-icon {
            color: #a5c0e8;
        }
        .dropdown-chevron {
            margin-left: auto;
            color: #8ca3c6;
            display: flex;
        }
        .toggle-switch {
            width: 36px;
            height: 20px;
            background: #333;
            border-radius: 10px;
            position: relative;
            margin-left: auto;
            border: 1px solid #444;
            transition: background 0.2s;
        }
        .toggle-switch.active { background: #4caf50; border-color: #4caf50; }
        .toggle-circle {
            width: 14px;
            height: 14px;
            background: #8ca3c6;
            border-radius: 50%;
            position: absolute;
            top: 2px;
            left: 2px;
            transition: transform 0.2s, background 0.2s;
        }
        .toggle-switch.active .toggle-circle {
            transform: translateX(16px);
            background: #fff;
        }

        .header-controls { position: relative; } /* Important for dropdown */
    </style>""")

    content = content.replace("<style>", "<style>\n" + root_css)
    
    for old, new in replacements:
        content = content.replace(old, new)

    # 2. Add Dropdown to HTML - replacing old header-controls contents
    old_controls_pattern = r'<div class="header-controls">.*?</div>\s*</div>'
    
    new_controls = """<div class="header-controls">
                <div class="avatar" onclick="toggleProfileDropdown()" title="Menu">👤</div>
                
                <!-- Dropdown Menu -->
                <div class="profile-dropdown" id="profileDropdown">
                    <div class="dropdown-group">
                        <div class="dropdown-item" onclick="handleAuthAction()">
                            <span class="dropdown-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
                            </span>
                            <span id="authActionText" data-i18n="dropdown-login">Log in / Sign up</span>
                        </div>
                    </div>
                    
                    <div class="dropdown-group">
                        <div class="dropdown-item" style="position: relative;">
                            <select id="langSwitcher" onchange="handleLangChange(this.value)" style="position: absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:pointer;">
                                <option value="en">English</option>
                                <option value="vi">Tiếng Việt</option>
                            </select>
                            <span class="dropdown-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
                            </span>
                            <span id="currentLangDisplay">English</span>
                            <span class="dropdown-chevron">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                            </span>
                        </div>
                        
                        <div class="dropdown-item" onclick="toggleDarkMode(event)">
                            <span class="dropdown-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                            </span>
                            <span data-i18n="dropdown-darkmode">Dark mode</span>
                            <div class="toggle-switch" id="darkModeSwitch">
                                <div class="toggle-circle"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="dropdown-group">
                        <div class="dropdown-item">
                            <span class="dropdown-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                            </span>
                            <span data-i18n="dropdown-help">Help Center</span>
                        </div>
                        <div class="dropdown-item">
                            <span class="dropdown-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                            </span>
                            <span data-i18n="dropdown-contact">Contact us</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""
    
    content = re.sub(old_controls_pattern, new_controls, content, flags=re.DOTALL)

    # 3. Add Script functions
    script_code = """
        function toggleProfileDropdown() {
            document.getElementById('profileDropdown').classList.toggle('open');
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const dropdown = document.getElementById('profileDropdown');
            const avatar = document.querySelector('.avatar');
            if (dropdown.classList.contains('open') && !dropdown.contains(e.target) && !avatar.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });

        // Initialize auth UI based on token
        document.addEventListener('DOMContentLoaded', () => {
            const tkn = localStorage.getItem('token');
            if(tkn) {
                document.getElementById('authActionText').textContent = "Log out";
            } else {
                document.getElementById('authActionText').textContent = "Log in / Sign up";
            }
            
            // Init Dark mode
            const isDark = localStorage.getItem('darkMode') === 'true';
            if(isDark) {
                document.body.classList.add('dark-mode');
                document.getElementById('darkModeSwitch').classList.add('active');
            }
            
            // Sync Lang display
            const savedLang = localStorage.getItem('appLang') || 'en';
            syncLangDisplay(savedLang);
        });

        function handleAuthAction() {
            if(localStorage.getItem('token')) {
                logout(); // Extracted from existing
            } else {
                window.location.href = 'login.html';
            }
        }

        function handleLangChange(lang) {
            applyLanguage(lang);
            syncLangDisplay(lang);
            document.getElementById('profileDropdown').classList.remove('open');
        }

        function syncLangDisplay(lang) {
            const display = document.getElementById('currentLangDisplay');
            if(lang === 'vi') {
                display.textContent = "Tiếng Việt";
            } else {
                display.textContent = "English";
            }
            document.getElementById('langSwitcher').value = lang;
        }

        function toggleDarkMode(e) {
            e.stopPropagation(); // Prevent closing dropdown if we just toggle
            const isDark = document.body.classList.toggle('dark-mode');
            document.getElementById('darkModeSwitch').classList.toggle('active');
            localStorage.setItem('darkMode', isDark);
        }
    """
    content = content.replace("</script>", script_code + "\n</script>\n", 1)

    with open(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\index.html", "w", encoding="utf-8") as f:
        f.write(content)

process_file()
