import os

# Configurações do Jules (Use sua API Key do Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Arsenal S-Tier
ARSENAL = {
    "video": "Pipeline Veo 3 + Nano Banana (Fidelidade 4K) + ElevenLabs (Sound Design)",
    "traffic": "CAPI (Conversions API) + GTM Server-Side + Estratégia de Atribuição Avançada",
    "seo": "GEO (Generative Engine Optimization) + AEO (Answer Engine Optimization) + Knowledge Graph @graph",
    "content": "Técnica Nugget (Answer-First) + Information Gain (E-E-A-T)"
}

# Prompt Templates
PROMPT_TEMPLATES = {
    "default": """
    Aja como o Jules, Proposals Architect S-Tier.
    Analise este projeto da plataforma {platform}: '{description}'
    Use o arsenal: {arsenal_items}.
    Gere uma proposta matadora em {language}.
    Retorne apenas o texto da proposta.
    """,
    "freelancer": """
    Aja como o Jules, Proposals Architect S-Tier.
    Analise este projeto da plataforma Freelancer.com: '{description}'
    Foco: Velocidade e Resposta Técnica.
    Use o arsenal: {arsenal_items}.
    Gere uma proposta matadora em Inglês (Turbo Core).
    Inclua uma tabela com Milestones e Palavras-chave de Teste.
    Retorne apenas o texto da proposta.
    """,
    "99freelas": """
    Aja como o Jules, Proposals Architect S-Tier.
    Analise este projeto da plataforma 99Freelas: '{description}'
    Foco: ROI e Consultoria.
    Use o arsenal: {arsenal_items}.
    Gere uma proposta matadora em Português.
    Mencione "Projeto Piloto" e use tom de parceiro.
    Retorne apenas o texto da proposta.
    """,
    "upwork": """
    Aja como o Jules, Proposals Architect S-Tier.
    Analise este projeto da plataforma Upwork: '{description}'
    Foco: Senioridade e Estudos de Caso.
    Use o arsenal: {arsenal_items}.
    Gere uma proposta matadora em Inglês.
    Responda tecnicamente às perguntas de triagem, se houver: {questions}.
    Retorne apenas o texto da proposta.
    """
}

# Simulated Leads (Fallback)
SIMULATED_LEADS = [
    {"platform": "freelancer", "desc": "Need a pro for AI Video and SEO"},
    {"platform": "99freelas", "desc": "Gestor de tráfego com CAPI"},
    {"platform": "upwork", "desc": "Looking for an SEO expert to improve rankings", "questions": ["What is your SEO strategy?"]}
]
