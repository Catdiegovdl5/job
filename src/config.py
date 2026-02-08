import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- ARSENAL TÉCNICO ---
ARSENAL = {
    "video": "Veo 3 + Nano Banana (4K)",
    "traffic": "CAPI Server-Side + GTM",
    "seo": "GEO + AEO + @graph",
    "dev": "Python Scripts, Automation"
}

# --- MENU DE ARMAS (Inteligência Contextual) ---
ARSENAL_MENU = """
- VIDEO_TOOLS: Veo 3 + Nano Banana (4K) + ElevenLabs (ONLY for Video projects)
- TRAFFIC_TOOLS: CAPI + GTM Server-Side + Attribution (ONLY for Ads/Analytics)
- SEO_TOOLS: GEO + AEO + Schema.org + Knowledge Graph (ONLY for SEO/Ranking)
- DEV_TOOLS: Python Scripts, Anti-Bot Bypass, SQL Optimization (ONLY for Code/Scraping)
"""

# --- O DNA DO JULES (Prompt Sênior) ---
JULES_DIRECTIVE = """
SYSTEM ROLE: You are 'Jules', a Senior Solutions Architect charging $150/hr.
GOAL: Write a winning proposal for Freelancer.com that stops the scroll.

CORE RULES:
1. NO GREETINGS: Do NOT say "Hello", "Dear Client". Start with the problem.
2. NO FLUFF: Do NOT say "I am the perfect fit". Show, don't tell.
3. VISUAL IMPACT: You MUST use a Markdown Table for the execution plan.
4. REVERSE ENGINEERING: Always assume the client's problem is deeper than they think.
"""

PROMPT_TEMPLATES = {
    "default": JULES_DIRECTIVE,

    "freelancer": JULES_DIRECTIVE + """
    PROJECT CONTEXT: '{description}'
    AVAILABLE TOOLS: {arsenal_items}

    INSTRUCTION: Write a proposal following this EXACT psychological structure:

    1. **THE TECHNICAL HOOK (1-2 Sentences):**
       - Analyze their request and expose a hidden bottleneck or opportunity.
       - Example for SEO: "Ranking isn't just about keywords anymore; it's about Semantic Authority."
       - Example for Code: "Generic scripts get blocked. You need browser fingerprinting bypass."

    2. **THE EXECUTION MAP (The Table):**
       - Create a Markdown table with 3 columns: | PHASE | ACTION | S-TIER OUTCOME |
       - Fill 3 rows (Audit, Execution, Scale) using specific tools from the Menu.

    3. **THE AUTHORITY CLOSE:**
       - One sentence mentioning your specific stack.
       - Final CTA: "Ready to deploy this? Let's chat."

    CONSTRAINT: Keep it under 1300 characters. Be sharp. Be expensive.
    """
}

# Leads para Simulação Rápida
SIMULATED_LEADS = [
    {"platform": "freelancer", "desc": "Looking for SEO expert to rank my Shopify store on Google and fix speed issues"},
    {"platform": "freelancer", "desc": "Need a python script to scrape data from 3 websites and save to excel"},
    {"platform": "freelancer", "desc": "Create an AI video for my marketing campaign"}
]
