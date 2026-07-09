# Fix emoji encoding - replace ?? placeholders with proper unicode emoji references
# Use HTML entities for emojis instead of raw emoji chars

cat_icons = {
    "INTELIGÊNCIA ARTIFICIAL": "&#x1F916;",   # 🤖
    "ANÁLISE DE DADOS": "&#x1F4CA;",           # 📊
    "MARKETING E PERFORMANCE": "&#x1F4C8;",    # 📈
    "DESENVOLVIMENTO WEB": "&#x1F4BB;",        # 💻
    "VENDAS E EDUCAÇÃO FINANCEIRA": "&#x1F4B0;" # 💰
}

certs_data = [
    ("INTELIGÊNCIA ARTIFICIAL", "&#x1F916;", "MICROSOFT_AI_01", "VISÃO COMPUTACIONAL",
     "./certificados/01_Microsoft_Visao_Computacional.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Computer Vision • Azure Cognitive • Image Recognition"),

    ("INTELIGÊNCIA ARTIFICIAL", "&#x1F916;", "MICROSOFT_AI_02", "PROCESSAMENTO DE LINGUAGEM NATURAL",
     "./certificados/02_Microsoft_Processamento_de_Linguagem_Natural.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "NLP • Azure Text Analytics • Sentiment Analysis"),

    ("INTELIGÊNCIA ARTIFICIAL", "&#x1F916;", "MICROSOFT_AI_03", "MINERAÇÃO DE CONHECIMENTO",
     "./certificados/03_Microsoft_Mineracao_de_Conhecimento.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Azure Cognitive Search • Semantic Search • AI Indexing"),

    ("INTELIGÊNCIA ARTIFICIAL", "&#x1F916;", "MICROSOFT_AI_04", "VISÃO GERAL DA IA GENERATIVA",
     "./certificados/04_Microsoft_Visao_Geral_da_IA_Generativa.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "LLMs • Prompt Engineering • Generative AI • Azure OpenAI"),

    ("INTELIGÊNCIA ARTIFICIAL", "&#x1F916;", "MICROSOFT_AI_05", "IA GENERATIVA NO AZURE",
     "./certificados/09_Microsoft_Visao_Geral_da_IA_no_Azure.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Azure AI Studio • Model Deployment • RAG • API Integration"),

    ("INTELIGÊNCIA ARTIFICIAL", "&#x1F916;", "MICROSOFT_AI_06", "IA PARA PEQUENOS NEGÓCIOS",
     "./certificados/08_Microsoft_IA_para_PMEs.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "IA Aplicada • Automação de Processos • Copilot • PMEs"),

    ("ANÁLISE DE DADOS", "&#x1F4CA;", "MICROSOFT_DATA_01", "ANÁLISE DE DADOS AVANÇADA",
     "./certificados/05_Microsoft_Analisando_Dados_com_o_Excel.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Power Query • DAX • Excel Avançado • Modelagem de Dados"),

    ("ANÁLISE DE DADOS", "&#x1F4CA;", "ESCOLA_DATA_01", "INTRODUÇÃO À ANÁLISE DE DADOS",
     "./certificados/Certificate analise de dados.pdf",
     "ESCOLA DO TRABALHADOR", "https://logo.clearbit.com/educacao.sp.gov.br", "2026",
     "Análise Exploratória • Limpeza de Dados • Visualização"),

    ("MARKETING E PERFORMANCE", "&#x1F4C8;", "GOOGLE_CERT_01", "GOOGLE ANALYTICS IQ",
     "./certificados/Certificação do Google Analytics.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "GA4 • Funis de Conversão • Audiências • Relatórios"),

    ("MARKETING E PERFORMANCE", "&#x1F4C8;", "GOOGLE_CERT_02", "GOOGLE ADS: REDE DE PESQUISA",
     "./certificados/Certificação em rede de Pesquisa do Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Search Ads • Smart Bidding • Qualidade de Anúncio • ROI"),

    ("MARKETING E PERFORMANCE", "&#x1F4C8;", "GOOGLE_CERT_03", "GOOGLE ADS: REDE DE DISPLAY",
     "./certificados/Certificação em Display do Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Display Ads • Remarketing • Segmentação de Audiência"),

    ("MARKETING E PERFORMANCE", "&#x1F4C8;", "GOOGLE_CERT_04", "GOOGLE ADS: CAMPANHAS DE VÍDEO",
     "./certificados/Certificação em campanhas de vídeo no Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "YouTube Ads • CPV • Formatos de Vídeo • Brand Safety"),

    ("MARKETING E PERFORMANCE", "&#x1F4C8;", "GOOGLE_CERT_05", "GOOGLE ADS: MÉTRICAS",
     "./certificados/Certificação em métricas do Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Atribuição • ROAS • Mensuração • Conversão Offline"),

    ("DESENVOLVIMENTO WEB", "&#x1F4BB;", "MICROSOFT_DEV_01", "DESENVOLVIMENTO WEB (HTML/CSS/JS)",
     "./certificados/06_Microsoft_Crie_um_Site_HTML_CSS_JS.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "HTML5 • CSS3 • JavaScript • Layouts Responsivos"),

    ("VENDAS E EDUCAÇÃO FINANCEIRA", "&#x1F4B0;", "MICROSOFT_FIN_01", "EDUCAÇÃO FINANCEIRA COM EXCEL",
     "./certificados/01. Educação Financeira Usando o Excel - Módulo 1 - Nosso Relacionamento com Dinheiro.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Orçamento Pessoal • Planejamento • Excel Financeiro"),

    ("VENDAS E EDUCAÇÃO FINANCEIRA", "&#x1F4B0;", "MEETIME_SDR_01", "CERTIFICADO SDR",
     "./certificados/Diego Antonio de jesus santos - 2026-07-08.pdf",
     "MEETIME", "https://logo.clearbit.com/meetime.com.br", "2026",
     "Prospecção Ativa • Cold Calling • BANT • CRM • SDR"),
]

def skill_tags(skills_str):
    tags = [s.strip() for s in skills_str.split('•')]
    parts = ['<div class="flip-skills">']
    for tag in tags:
        parts.append(f'<span class="flip-skill-tag">{tag}</span>')
    parts.append('</div>')
    return ''.join(parts)

# Group by category preserving order
categories = {}
for item in certs_data:
    cat = item[0]
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(item)

html_parts = []
html_parts.append('''    <!-- CERTIFICADOS -->
    <section id="certificados" class="wrap sec-py">
        <h2 class="display fade-in glitch-hover interact-snd" style="font-size: clamp(2.5rem, 6vw, 6rem); margin-bottom: 20px;">ARQUIVOS_CERTIFICADOS<span class="blood-dot">.</span></h2>
        <p style="color: var(--text-muted); margin-bottom: 50px;">[ REGISTROS DE QUALIFICAÇÃO TÉCNICA E ENGENHARIA ]</p>
''')

for cat_name, items in categories.items():
    cat_icon = items[0][1]
    html_parts.append(f'''
        <h3 class="cert-cat-title"><span class="cat-icon">{cat_icon}</span> [ {cat_name} ]</h3>
        <div class="flip-grid">''')

    for item in items:
        _, icon_html, cert_id, title, pdf_path, issuer, logo_url, year, skills_str = item
        skills_html = skill_tags(skills_str)
        html_parts.append(f'''
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-front">
                        <div class="flip-front-top">
                            <span class="flip-cat-icon">{icon_html}</span>
                            <span class="flip-id">[ {cert_id} ]</span>
                        </div>
                        <div class="flip-logo-wrap">
                            <img src="{logo_url}" class="flip-logo" alt="{issuer}" onerror="this.style.display='none'">
                        </div>
                        <div class="flip-title">{title}</div>
                        <div class="flip-issuer">{issuer} // {year}</div>
                        <div class="flip-hint">&#x21BB; HOVER PARA DETALHES</div>
                    </div>
                    <div class="flip-back">
                        <div class="flip-front-top">
                            <span class="flip-cat-icon">{icon_html}</span>
                            <span class="flip-id">[ {cert_id} ]</span>
                        </div>
                        <div class="flip-back-title">{title}</div>
                        {skills_html}
                        <div class="flip-back-issuer">{issuer} // {year}</div>
                        <a href="{pdf_path}" target="_blank" class="flip-btn">[ ABRIR CERTIFICADO &#x2192; ]</a>
                    </div>
                </div>
            </div>''')

    html_parts.append('\n        </div>')

html_parts.append('\n    </section>')

new_certs_html = ''.join(html_parts)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
old_section_pattern = r'    <!-- CERTIFICADOS -->.*?</section>'
html = re.sub(old_section_pattern, new_certs_html, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"FIXED: Rebuilt {len(certs_data)} cards using HTML entities for icons (no encoding issues)")
