certs_data = [
    # (category, cat_icon, cert_id, title, pdf_path, issuer, issuer_logo, year, extra_desc)
    # INTELIGENCIA ARTIFICIAL
    ("INTELIGÊNCIA ARTIFICIAL", "🤖", "MICROSOFT_AI_01", "VISÃO COMPUTACIONAL",
     "./certificados/01_Microsoft_Visao_Computacional.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Fundamentos de Computer Vision com Azure Cognitive Services."),
    ("INTELIGÊNCIA ARTIFICIAL", "🤖", "MICROSOFT_AI_02", "PROCESSAMENTO DE LINGUAGEM NATURAL",
     "./certificados/02_Microsoft_Processamento_de_Linguagem_Natural.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "NLP com Azure: análise de sentimentos, extração de entidades e tradução automática."),
    ("INTELIGÊNCIA ARTIFICIAL", "🤖", "MICROSOFT_AI_03", "MINERAÇÃO DE CONHECIMENTO",
     "./certificados/03_Microsoft_Mineracao_de_Conhecimento.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Azure Cognitive Search: indexação inteligente e busca semântica em dados não estruturados."),
    ("INTELIGÊNCIA ARTIFICIAL", "🤖", "MICROSOFT_AI_04", "VISÃO GERAL DA IA GENERATIVA",
     "./certificados/04_Microsoft_Visao_Geral_da_IA_Generativa.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Fundamentos de LLMs, prompt engineering e deployment de modelos generativos no Azure."),
    ("INTELIGÊNCIA ARTIFICIAL", "🤖", "MICROSOFT_AI_05", "IA GENERATIVA NO AZURE",
     "./certificados/09_Microsoft_Visao_Geral_da_IA_no_Azure.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Integração de serviços de IA generativa do Azure em aplicações de produção."),
    ("INTELIGÊNCIA ARTIFICIAL", "🤖", "MICROSOFT_AI_06", "IA PARA PEQUENOS E MÉDIOS NEGÓCIOS",
     "./certificados/08_Microsoft_IA_para_PMEs.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Estratégias práticas de adoção de IA para maximizar eficiência operacional em PMEs."),
    # ANALISE DE DADOS
    ("ANÁLISE DE DADOS", "📊", "MICROSOFT_DATA_01", "ANÁLISE DE DADOS AVANÇADA",
     "./certificados/05_Microsoft_Analisando_Dados_com_o_Excel.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Power Query, DAX avançado e modelagem de dados para análise empresarial com Excel."),
    ("ANÁLISE DE DADOS", "📊", "ESCOLA_DATA_01", "INTRODUÇÃO À ANÁLISE DE DADOS",
     "./certificados/Certificate analise de dados.pdf",
     "ESCOLA DO TRABALHADOR", "https://logo.clearbit.com/educacao.sp.gov.br", "2026",
     "Fundamentos de análise de dados: coleta, limpeza, visualização e interpretação de resultados."),
    # MARKETING
    ("MARKETING E PERFORMANCE", "📈", "GOOGLE_CERT_01", "GOOGLE ANALYTICS IQ",
     "./certificados/Certificação do Google Analytics.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Individual Qualification em GA4: rastreamento avançado, funis de conversão e relatórios."),
    ("MARKETING E PERFORMANCE", "📈", "GOOGLE_CERT_02", "GOOGLE ADS: REDE DE PESQUISA",
     "./certificados/Certificação em rede de Pesquisa do Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Campanhas de busca pagas: lances, qualidade de anúncio e otimização de ROI em pesquisa."),
    ("MARKETING E PERFORMANCE", "📈", "GOOGLE_CERT_03", "GOOGLE ADS: REDE DE DISPLAY",
     "./certificados/Certificação em Display do Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Criação e otimização de campanhas display: segmentação por audiência e remarketing."),
    ("MARKETING E PERFORMANCE", "📈", "GOOGLE_CERT_04", "GOOGLE ADS: CAMPANHAS DE VÍDEO",
     "./certificados/Certificação em campanhas de vídeo no Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "YouTube Ads: formatos de vídeo, segmentação demográfica e otimização de CPV."),
    ("MARKETING E PERFORMANCE", "📈", "GOOGLE_CERT_05", "GOOGLE ADS: MÉTRICAS",
     "./certificados/Certificação em métricas do Google Ads.pdf",
     "GOOGLE", "https://logo.clearbit.com/google.com", "2024",
     "Mensuração de campanhas: atribuição, métricas de conversão e otimização baseada em dados."),
    # DEV WEB
    ("DESENVOLVIMENTO WEB", "💻", "MICROSOFT_DEV_01", "DESENVOLVIMENTO WEB (HTML/CSS/JS)",
     "./certificados/06_Microsoft_Crie_um_Site_HTML_CSS_JS.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Construção de sites interativos do zero com HTML5, CSS3 e JavaScript moderno."),
    # VENDAS E FINANCA
    ("VENDAS E EDUCAÇÃO FINANCEIRA", "💰", "MICROSOFT_FIN_01", "EDUCAÇÃO FINANCEIRA COM EXCEL",
     "./certificados/01. Educação Financeira Usando o Excel - Módulo 1 - Nosso Relacionamento com Dinheiro.pdf",
     "MICROSOFT", "https://logo.clearbit.com/microsoft.com", "2024",
     "Gestão financeira pessoal com Excel: orçamento, planejamento e análise de investimentos."),
    ("VENDAS E EDUCAÇÃO FINANCEIRA", "💰", "MEETIME_SDR_01", "CERTIFICADO SDR",
     "./certificados/Diego Antonio de jesus santos - 2026-07-08.pdf",
     "MEETIME", "https://logo.clearbit.com/meetime.com.br", "2026",
     "Sales Development Representative: prospecção ativa, cold calling e qualificação de leads B2B."),
]

# Build the HTML for the entire certs section
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
    html_parts.append(f'''
        <h3 class="cert-cat-title">[ {cat_name} ]</h3>
        <div class="flip-grid">''')

    for item in items:
        _, _, cert_id, title, pdf_path, issuer, logo_url, year, desc = item
        html_parts.append(f'''
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-front">
                        <span class="flip-id">[ {cert_id} ]</span>
                        <div class="flip-logo-wrap">
                            <img src="{logo_url}" class="flip-logo" alt="{issuer}" onerror="this.style.display='none'">
                        </div>
                        <div class="flip-title">{title}</div>
                        <div class="flip-issuer">{issuer} // {year}</div>
                        <div class="flip-hint">↻ HOVER PARA DETALHES</div>
                    </div>
                    <div class="flip-back">
                        <span class="flip-id">[ {cert_id} ]</span>
                        <div class="flip-back-title">{title}</div>
                        <p class="flip-desc">{desc}</p>
                        <div class="flip-back-issuer">{issuer} // {year}</div>
                        <a href="{pdf_path}" target="_blank" class="flip-btn">[ ABRIR CERTIFICADO → ]</a>
                    </div>
                </div>
            </div>''')

    html_parts.append('\n        </div>')

html_parts.append('\n    </section>')

new_certs_html = ''.join(html_parts)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace everything between the <!-- CERTIFICADOS --> and </section> markers
import re
old_section_pattern = r'    <!-- CERTIFICADOS -->.*?</section>'
html = re.sub(old_section_pattern, new_certs_html, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Rebuilt certificates section with {len(certs_data)} flip cards across {len(categories)} categories!")
