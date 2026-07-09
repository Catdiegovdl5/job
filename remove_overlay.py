import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove overlay HTML
overlay_html = r'\s*<!-- Audio Trigger / Hijack Overlay -->\s*<div id="enter-overlay">\s*<div class="system-warning">.*?</div>\s*<div.*?>.*?</div>\s*</div>'
html = re.sub(overlay_html, '', html, flags=re.DOTALL)

# Remove overlay CSS
overlay_css = r'\s*#enter-overlay \{.*?\}\s*\.system-warning \{.*?\}\s*@keyframes pulseRed \{.*?\}'
html = re.sub(overlay_css, '', html, flags=re.DOTALL)

# Replace overlay JS with body click JS
old_js = r"// OVERLAY INIT E TABS LOGIC.*?AudioEngine\.init\(\);\s*\}\);"
new_js = """// TABS LOGIC E AUDIO INIT
    let audioInitialized = false;
    document.body.addEventListener('click', () => {
        if (!audioInitialized) {
            AudioEngine.init();
            audioInitialized = true;
        }
    });"""
html = re.sub(old_js, new_js, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
