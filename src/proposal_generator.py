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
    if not use_ai or not GEMINI_API_KEY:
        return "Erro: API Key não configurada ou IA desativada."

    # Seleciona o template correto
    template = PROMPT_TEMPLATES.get("freelancer", PROMPT_TEMPLATES["default"])

    # Monta o prompt
    prompt = template.format(
        description=description,
        arsenal_items=ARSENAL_MENU
    )

    client = JulesAI()
    try:
        logger.info(f"🧠 Jules analisando: {description[:30]}...")
        return client.generate_content(prompt)
    except Exception as e:
        logger.error(f"❌ Erro no cérebro da IA: {e}")
        return "Erro na geração da proposta."
