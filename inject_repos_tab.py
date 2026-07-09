import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Navigation Button
nav_target = r'(<button data-target="tab-certificados".*?\[ CERTIFICADOS \]</button>)'
nav_replacement = r'\1\n            <button data-target="tab-repositorios" class="tab-link btn-audio interact-snd">[ REPOSITÓRIOS ]</button>'
html = re.sub(nav_target, nav_replacement, html)

# 2. Add CSS
css = """
        /* ─────────────────────────────────────────────
           REPOSITÓRIOS - GRID NEON GLITCH
        ───────────────────────────────────────────── */
        .repo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }

        .repo-neon-btn {
            position: relative;
            background: rgba(10,0,0,0.8);
            border: 1px solid rgba(139,0,0,0.3);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            text-decoration: none;
            overflow: hidden;
            transition: all 0.3s ease;
            height: 100%;
            cursor: pointer;
        }

        .repo-neon-btn::before {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,0,0,0.1), transparent);
            transform: skewX(-20deg);
            transition: all 0.5s ease;
            pointer-events: none;
        }

        .repo-neon-btn:hover {
            border-color: rgba(255,0,0,0.8);
            box-shadow: 0 0 15px rgba(255,0,0,0.4), inset 0 0 20px rgba(139,0,0,0.2);
            transform: translateY(-3px);
            background: rgba(20,0,0,0.9);
        }

        .repo-neon-btn:hover::before {
            left: 200%;
        }

        .repo-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.4rem;
            color: var(--text-bright);
            letter-spacing: 0.08em;
            margin-bottom: 12px;
            position: relative;
            transition: all 0.2s ease;
        }

        /* Glitch text effect on hover */
        .repo-neon-btn:hover .repo-title {
            animation: textGlitch 0.3s cubic-bezier(.25, .46, .45, .94) both infinite;
            color: #ff3333;
            text-shadow: 2px 0 0 #00ffff, -2px 0 0 #ff00ff;
        }

        @keyframes textGlitch {
            0% { transform: translate(0) }
            20% { transform: translate(-2px, 1px) }
            40% { transform: translate(-1px, -1px) }
            60% { transform: translate(2px, 1px) }
            80% { transform: translate(1px, -1px) }
            100% { transform: translate(0) }
        }

        .repo-lang {
            font-family: 'Inter', sans-serif;
            font-size: 0.65rem;
            font-weight: 700;
            color: rgba(255,255,255,0.9);
            background: rgba(139,0,0,0.8);
            padding: 4px 8px;
            display: inline-block;
            margin-bottom: 12px;
            align-self: flex-start;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }
        
        .repo-neon-btn:hover .repo-lang {
            background: #ff1111;
            box-shadow: 0 0 10px rgba(255,0,0,0.6);
        }

        .repo-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            color: var(--text-dim);
            line-height: 1.5;
            margin-bottom: 20px;
            flex-grow: 1;
            transition: color 0.3s;
        }
        
        .repo-neon-btn:hover .repo-desc {
            color: rgba(255,255,255,0.8);
        }

        .repo-footer {
            font-family: 'Courier New', monospace;
            font-size: 0.65rem;
            color: rgba(139,0,0,0.5);
            letter-spacing: 0.1em;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(139,0,0,0.2);
            padding-top: 12px;
            transition: all 0.3s;
        }
        
        .repo-neon-btn:hover .repo-footer {
            color: #ff5555;
            border-top-color: rgba(255,0,0,0.5);
        }
"""
html = html.replace('</style>', css + '\n    </style>')

# 3. Add Tab Content
repos_data = [
    ("Automacao-Lead-Scoring-Triagem", "N8N / IA", "Pipeline autônomo de qualificação de leads integrando n8n e IA para triagem automática 24/7."),
    ("Assistente-Virtual-Imobiliario", "TypeScript", "Assistente de vendas IA focado no mercado imobiliário para gestão e conversão de leads."),
    ("Diego_InHire_Bot", "Python", "Agente automatizado para recrutamento e seleção, com análise semântica de currículos."),
    ("maquina_triagem_pj", "Python", "Sistema de triagem e filtragem de contratos B2B para qualificação de propostas."),
    ("zap-bot", "Python", "Robô de atendimento e conversão direta via WhatsApp, com disparos em massa e IA."),
    ("vagas_bot", "Python", "Bot rastreador de oportunidades e vagas em tempo real para automação de candidaturas."),
    ("telegram-bots", "Python", "Coleção de scripts de automação e alertas para canais e grupos do Telegram."),
    ("DiegoAutoFill_Extensao", "JavaScript", "Extensão de navegador para preenchimento automático inteligente de formulários complexos."),
    ("Web-Scraping", "Python", "Pipelines massivos de extração de dados, bypass de proteções e normalização de datasets."),
    ("FaceMonitor", "Python", "Sistema de visão computacional para monitoramento de face e tracking biométrico."),
    ("dr-manhattan-ts", "TypeScript", "Arquitetura avançada de manipulação temporal e agendamento assíncrono de tarefas."),
    ("polymarket-arbitrage", "Python", "Bot de arbitragem em mercados de predição buscando discrepâncias de odds em tempo real."),
    ("sistema", "Python / Web", "Dashboard centralizado de telemetria e operação para controle das automações."),
    ("TURBO.CORE", "Python", "Motor central de execução e ofuscação de payloads para operações de alta performance."),
    ("anti-blur-tinder", "JS / Bypass", "Engenharia reversa visual para remoção de borrões e paywalls em interfaces web.")
]

tab_html = '''
    <div id="tab-repositorios" class="tab-content">
        <section class="wrap sec-py">
            <h2 class="display fade-in glitch-hover interact-snd" style="font-size: clamp(2.5rem, 6vw, 6rem); margin-bottom: 20px;">REPOSITÓRIOS_RAW<span class="blood-dot">.</span></h2>
            <p style="color: var(--text-muted); margin-bottom: 40px;">[ ACESSO DIRETO AO CÓDIGO FONTE E ARQUITETURA NO GITHUB ]</p>
            
            <div class="repo-grid">
'''

for repo, lang, desc in repos_data:
    tab_html += f'''
                <a href="https://github.com/Catdiegovdl5/{repo}" target="_blank" class="repo-neon-btn interact-snd fade-in">
                    <span class="repo-lang">{lang}</span>
                    <h3 class="repo-title">{repo}</h3>
                    <p class="repo-desc">{desc}</p>
                    <div class="repo-footer">
                        <span>[ ACESSAR SOURCE ]</span>
                        <span>&#x2192;</span>
                    </div>
                </a>
'''

tab_html += '''
            </div>
            
            <div class="next-step-wrap" style="text-align: center; margin-top: 80px;">
                <button data-target="tab-home" class="tab-link btn-audio interact-snd" style="font-size: 1rem; padding: 15px 30px; letter-spacing: 0.2em; background: transparent; color: var(--text-bright); border: 1px solid var(--blood); cursor: pointer; text-transform: uppercase; font-family: var(--f-body); font-weight: 800;">[ RETORNAR AO INÍCIO ]</button>
            </div>
        </section>
    </div>
'''

# Find insertion point: Just before </main>
html = html.replace('</main>', tab_html + '\n</main>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Sucesso! Aba Repositorios injetada.")
