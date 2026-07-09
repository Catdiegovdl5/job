import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def inject_logo(match):
    block = match.group(0)
    
    # Determine the logo based on issuer or text
    domain = ""
    if "GOOGLE" in block:
        domain = "google.com"
    elif "MEETIME" in block:
        domain = "meetime.com.br"
    else:
        domain = "microsoft.com"
    
    # Change Certificate 16 to the correct title
    if "BOOTCAMP_DATA_02" in block:
        block = block.replace("BOOTCAMP AVANÇADO DE ANÁLISE DE DADOS", "INTRODUÇÃO À ANÁLISE DE DADOS")
        block = block.replace("BOOTCAMP_DATA_02", "MICROSOFT_DATA_02")
        block = block.replace("BOOTCAMP // 2024", "ESCOLA DO TRABALHADOR // 2026")
    
    # Inject cert-header and logo
    pattern = r'(<div>\s*<div class="term-id">.*?</div>\s*<div class="term-title">.*?</div>\s*</div>)'
    replacement = f'<div class="cert-header">\n                    \\1\n                    <img src="https://logo.clearbit.com/{domain}" class="cert-logo" alt="Logo">\n                </div>'
    
    new_block = re.sub(pattern, replacement, block, count=1, flags=re.DOTALL)
    
    # Update preview text to be cleaner
    new_block = new_block.replace("Requer screenshot para preview de imagem", "Visualização Indisponível")
    return new_block

start_str = '<div class="terminal-list">'
end_str = '</section>'
start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx)

list_content = content[start_idx:end_idx]
new_list_content = re.sub(r'<a href="\./certificados.*?</a>', inject_logo, list_content, flags=re.DOTALL)

content = content[:start_idx] + new_list_content + content[end_idx:]

# Inject CSS for the logos
css = """
        .cert-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
        .cert-logo { height: 35px; width: auto; max-width: 100px; object-fit: contain; filter: grayscale(1) contrast(1.5) brightness(1.2); opacity: 0.3; transition: all 0.3s cubic-bezier(.25,.46,.45,.94); }
        .term-item:hover .cert-logo { opacity: 0.9; filter: grayscale(1) contrast(2) invert(1) drop-shadow(0 0 5px rgba(255,0,0,0.5)); }
"""
css_target = "/* ─────────────────────────────────────────────\n           CERTIFICATES (Terminal List)\n        ───────────────────────────────────────────── */"
content = content.replace(css_target, css_target + css)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
