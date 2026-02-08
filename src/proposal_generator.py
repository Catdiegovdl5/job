import argparse
import sys
import logging

try:
    from .config import ARSENAL, PROMPT_TEMPLATES, GEMINI_API_KEY, SKILL_SETS
    from .ai_client import JulesAI
except ImportError:
    # Fallback for when running as script directly (though better to run as module)
    from config import ARSENAL, PROMPT_TEMPLATES, GEMINI_API_KEY, SKILL_SETS
    from ai_client import JulesAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_skill(description):
    """
    Detects the primary skill from the project description based on SKILL_SETS keys.
    """
    desc_lower = description.lower()
    for skill, data in SKILL_SETS.items():
        if skill.lower() in desc_lower:
            return skill, data["strategy"]
    return "General", "High-Value Execution"

def generate_proposal_with_ai(platform, description, questions=None):
    """
    Generates a proposal using the Gemini API via JulesAI.
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not found. Falling back to template.")
        return generate_proposal(platform, description, questions, use_ai=False)

    platform_key = platform.lower().strip()
    # Normalize platform key for template lookup
    if "freelancer" in platform_key:
        platform_key = "freelancer"
    elif "99freelas" in platform_key:
        platform_key = "99freelas"
    elif "upwork" in platform_key:
        platform_key = "upwork"
    else:
        platform_key = "default"

    template = PROMPT_TEMPLATES.get(platform_key, PROMPT_TEMPLATES["default"])

    arsenal_items = ", ".join([f"{k}: {v}" for k, v in ARSENAL.items()])
    questions_str = "\n".join([f"- {q}" for q in questions]) if questions else "None"
    language = "Português" if platform_key == "99freelas" else "Inglês"

    detected_skill, skill_strategy = detect_skill(description)

    prompt = template.format(
        platform=platform,
        description=description,
        arsenal_items=arsenal_items,
        questions=questions_str,
        language=language,
        detected_skill=detected_skill,
        skill_strategy=skill_strategy
    )

    client = JulesAI()
    try:
        logger.info(f"Generating AI proposal for {platform}...")
        return client.generate_content(prompt)
    except Exception as e:
        logger.error(f"AI Generation failed: {e}. Falling back to template.")
        return generate_proposal(platform, description, questions, use_ai=False)

def generate_proposal(platform, description, questions=None, use_ai=False):
    """
    Generates a proposal based on the platform and project description.
    If use_ai is True, attempts to use JulesAI. Otherwise, uses templates.
    """
    if use_ai:
        return generate_proposal_with_ai(platform, description, questions)

    # Template-based generation (Fallback)
    platform = platform.lower().strip()
    proposal = []

    detected_skill, skill_strategy = detect_skill(description)

    if "freelancer" in platform:
        proposal.append("### Proposal for Freelancer.com (Focus: Speed & Technical)")
        proposal.append("Language: English\n")
        proposal.append("Hello,")
        proposal.append(f"I have reverse-engineered your project: '{description}'.")
        proposal.append(f"Core Strategy: {skill_strategy} (Skill: {detected_skill})")
        proposal.append("Here is the technical roadmap to solve your pain points immediately:\n")
        proposal.append("| Phase | Milestone | Deliverable |")
        proposal.append("|-------|-----------|-------------|")
        proposal.append("| 1 | Technical Audit & Reverse Engineering | Gap Analysis |")
        proposal.append(f"| 2 | {skill_strategy} Implementation | Technical Solution |")
        proposal.append("| 3 | Performance Scaling & ROI Tracking | Performance Report |\n")
        proposal.append("Technical Stack:")
        proposal.append(f"- Video: {ARSENAL['video']}")
        proposal.append(f"- Traffic: {ARSENAL['traffic']}")
        proposal.append(f"- SEO: {ARSENAL['seo']}")
        proposal.append(f"- Content: {ARSENAL['content']}\n")
        proposal.append("Test Keywords: [REVERSE-ENGINEERING], [4K-PIPELINE], [CAPI-OPTIMIZATION].")

    elif "99freelas" in platform:
        proposal.append("### Proposta para 99Freelas (Foco: ROI & Consultoria)")
        proposal.append("Idioma: Português\n")
        proposal.append("Olá,")
        proposal.append(f"Analisei seu projeto '{description}' e identifiquei os gargalos que estão travando seus resultados.")
        proposal.append(f"Estratégia Central: {skill_strategy} (Skill: {detected_skill})")
        proposal.append("Minha abordagem foca em ROI real e consultoria estratégica, não apenas execução técnica.\n")
        proposal.append("Sugiro começarmos com um **Projeto Piloto** focado em validação rápida.")
        proposal.append("\nNosso Arsenal Técnico Diferenciado:")
        proposal.append(f"- Vídeo: {ARSENAL['video']}")
        proposal.append(f"- Tráfego: {ARSENAL['traffic']}")
        proposal.append(f"- SEO: {ARSENAL['seo']}")
        proposal.append(f"- Conteúdo: {ARSENAL['content']}\n")
        proposal.append("Podemos agendar uma conversa para eu te mostrar como aplicaremos isso no seu caso?")

    elif "upwork" in platform:
        proposal.append("### Proposal for Upwork (Focus: Seniority & Case Studies)")
        proposal.append("Language: English\n")
        proposal.append("Dear Hiring Manager,")
        proposal.append(f"After reviewing your project description ('{description}'), I've applied a reverse-engineering lens to identify the core business objectives.")
        proposal.append(f"Focus: {skill_strategy} (Skill: {detected_skill})")
        proposal.append("My senior approach ensures that every technical decision is backed by ROI and high-fidelity standards.\n")
        proposal.append("Strategy Highlights:")
        proposal.append(f"- High-Fidelity Production: {ARSENAL['video']}")
        proposal.append(f"- Data Attribution: {ARSENAL['traffic']}")
        proposal.append(f"- Generative Search Dominance: {ARSENAL['seo']}")
        proposal.append(f"- Authority Building: {ARSENAL['content']}\n")

        if questions:
            proposal.append("#### Screening Questions:")
            for i, q in enumerate(questions):
                proposal.append(f"Q{i+1}: {q}")
                proposal.append(f"A: [Detailed technical response addressing '{q}' using {ARSENAL['traffic']} and {ARSENAL['seo']} principles.]\n")

        proposal.append("I have successfully implemented similar strategies in past cases. Looking forward to discussing how we can replicate those results for you.")

    else:
        return "Error: Unsupported platform. Use 'freelancer', '99freelas', or 'upwork'."

    return "\n".join(proposal)

def main():
    parser = argparse.ArgumentParser(description='Generate S-Tier Proposals')
    parser.add_argument('--platform', required=True, help='Platform: freelancer, 99freelas, upwork')
    parser.add_argument('--description', required=True, help='Project description')
    parser.add_argument('--questions', nargs='*', help='Screening questions (for Upwork)')
    parser.add_argument('--ai', action='store_true', help='Use AI to generate proposal')

    args = parser.parse_args()
    print(generate_proposal(args.platform, args.description, args.questions, use_ai=args.ai))

if __name__ == "__main__":
    main()
