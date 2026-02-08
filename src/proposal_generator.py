import logging
try:
    from .config import ARSENAL_MENU, PROMPT_TEMPLATES, GEMINI_API_KEY
    from .ai_client import JulesAI
except ImportError:
    from config import ARSENAL_MENU, PROMPT_TEMPLATES, GEMINI_API_KEY
    from ai_client import JulesAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_proposal(platform, description, use_ai=True):
    if not use_ai or not GEMINI_API_KEY: return "Erro: Sem chave de API."
    
    template = PROMPT_TEMPLATES.get("freelancer", PROMPT_TEMPLATES["default"])
    prompt = template.format(description=description, arsenal_items=ARSENAL_MENU)
    
    try:
        client = JulesAI()
        return client.generate_content(prompt)
    except Exception as e:
        return f"Erro na geração: {e}"
