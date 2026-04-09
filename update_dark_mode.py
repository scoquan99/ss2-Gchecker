import re

def process_file():
    with open(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\index.html", "r", encoding="utf-8") as f:
        content = f.read()

    new_dark_mode = """body.dark-mode {
            --bg-color: #09090b;
            --text-color: #f4f4f5;
            --card-bg: #18181b;
            --border-color: #27272a;
            --avatar-bg: #27272a;
            --avatar-hover: #3f3f46;
            --text-muted: #a1a1aa;
            --hover-bg: #27272a;
            --active-bg: transparent;
            --active-border: #3b82f6;
            --btn-bg: linear-gradient(135deg, #2563eb, #1d4ed8);
            --btn-text: #ffffff;
            --input-bg: #27272a;
            --icon-bg: #18181b; /* same as card */
            --panel-bg: #18181b;
        }

        body.dark-mode .container {
            box-shadow: none;
        }
        
        body.dark-mode .bottom-nav {
            background-color: #09090b;
            border-top: 1px solid #27272a;
            box-shadow: none;
        }
        
        body.dark-mode .app-header {
            border-bottom-color: #27272a;
        }
        
        body.dark-mode .tool-card {
            background-color: #18181b;
        }
        
        body.dark-mode .tool-icon {
            background-color: #27272a;
        }
        
        body.dark-mode textarea {
            border-color: #3f3f46;
        }
        """

    # We need to replace the old `body.dark-mode` to `}` with the new one.
    # The old one is from my previous inject script.
    old_dark_mode_pattern = r'body\.dark-mode\s*\{[^\}]+\}'
    # But wait, there might be multiple or I can just use a precise regex to capture from body.dark-mode to }
    content = re.sub(r'body\.dark-mode\s*\{[^}]+\}', new_dark_mode, content)

    # I'll also just add the extra dark mode overrides inside the style tag.
    # Actually wait, re.sub above will replace it but new_dark_mode contains extra classes which is fine.

    with open(r"e:\ss2-Gchecker-main\ss2-Gchecker-main\frontend\index.html", "w", encoding="utf-8") as f:
        f.write(content)

process_file()
