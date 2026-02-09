import logging
try:
    from .config import ARSENAL_MENU, PROMPT_TEMPLATES, GEMINI_API_KEY
    from .ai_client import JulesAI
except ImportError:
    from config import ARSENAL_MENU, PROMPT_TEMPLATES, GEMINI_API_KEY
    from ai_client import JulesAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_simulation_proposal(description):
    """Gera uma proposta técnica 'Architect Killer' sem usar IA."""
    code_snippet = f"""
// Playwright Proof of Concept for: {description[:30]}
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch({{ headless: true }});
  const page = await browser.newPage();
  await page.goto('TARGET_URL');
  // Logic to bypass anti-bot and extract data
  await browser.close();
}})();
"""
    proposal = f"""
[THE TECHNICAL HOOK]
A maioria das soluções falha porque ignora o fingerprinting do navegador.
Para {description[:50]}, implementarei um bypass via Playwright Stealth para garantir 100% de sucesso.

[THE EXECUTION MAP]
| PHASE | ACTION | S-TIER OUTCOME |
| :--- | :--- | :--- |
| Audit | Reverse engineering do alvo | Mapeamento de proteções Cloudflare/Datadome |
| Execution | Deploy do cluster Playwright | Raspagem assíncrona com rotação de Proxy Residencial |
| Scale | Integração via API/Webhook | Entrega de dados limpos em tempo real (JSON/CSV) |

[CODE PROOF]
```javascript{code_snippet}```

[ROI & ROADMAP]
- Estabilidade: 99.9% de uptime contra mudanças de layout.
- Velocidade: Processamento paralelo reduz tempo de execução em 70%.
- Entrega: Fase 1 (MVP) em 24h.

[THE AUTHORITY CLOSE]
Especialista em Web Scraping e Automações Complexas.
Ready to deploy this? Let's chat.
"""
    return proposal

def generate_proposal(platform, description, questions=None, use_ai=False):
    if not use_ai or not GEMINI_API_KEY:
        return generate_simulation_proposal(description)
    
    template = PROMPT_TEMPLATES.get("freelancer", PROMPT_TEMPLATES["default"])
    # Note: questions is accepted but not currently integrated into the fixed template prompt
    prompt = template.format(description=description, arsenal_items=ARSENAL_MENU)
    
    try:
        client = JulesAI()
        response = client.generate_content(prompt)
        if "FALHA CRÍTICA" in response or not response:
            return generate_simulation_proposal(description)
        return response
    except Exception as e:
        logger.error(f"Erro na geração IA: {e}")
        return generate_simulation_proposal(description)
