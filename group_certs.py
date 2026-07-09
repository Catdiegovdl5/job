import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_str = '<div class="terminal-list">'
end_str = '</section>'
start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx)

if start_idx != -1 and end_idx != -1:
    list_content = content[start_idx:end_idx]

    # Extract all certs
    certs = re.findall(r'<a href="\./certificados.*?</a>', list_content, flags=re.DOTALL)

    categories = {
        "INTELIGÊNCIA ARTIFICIAL": [],
        "ANÁLISE DE DADOS": [],
        "MARKETING E PERFORMANCE": [],
        "DESENVOLVIMENTO WEB": [],
        "VENDAS E EDUCAÇÃO FINANCEIRA": []
    }

    for cert in certs:
        if "MICROSOFT_AI" in cert:
            categories["INTELIGÊNCIA ARTIFICIAL"].append(cert)
        elif "MICROSOFT_DATA" in cert:
            categories["ANÁLISE DE DADOS"].append(cert)
        elif "GOOGLE_CERT" in cert:
            categories["MARKETING E PERFORMANCE"].append(cert)
        elif "MICROSOFT_DEV" in cert:
            categories["DESENVOLVIMENTO WEB"].append(cert)
        else:
            categories["VENDAS E EDUCAÇÃO FINANCEIRA"].append(cert)

    new_html = ""
    for cat, items in categories.items():
        if len(items) == 0: continue
        new_html += f'\n<h3 class="display" style="font-size: 2rem; color: var(--text-bright); margin-top: 60px; margin-bottom: 20px; border-bottom: 1px solid var(--blood); padding-bottom: 10px; display: inline-block;">[ {cat} ]</h3>\n'
        new_html += '<div class="terminal-list" style="margin-top: 20px;">\n'
        for item in items:
            new_html += "    " + item + "\n"
        new_html += '</div>\n'

    content = content[:start_idx] + new_html + content[end_idx:]

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("Could not find terminal-list block.")
