import argparse
import sys

# Arsenal Técnico S-Tier
ARSENAL = {
    "video": "Pipeline Veo 3 + Nano Banana (Fidelidade 4K) + ElevenLabs (Sound Design)",
    "traffic": "CAPI (Conversions API) + GTM Server-Side + Estratégia de Atribuição Avançada",
    "seo": "GEO (Generative Engine Optimization) + AEO (Answer Engine Optimization) + Knowledge Graph @graph",
    "content": "Técnica Nugget (Answer-First) + Information Gain (E-E-A-T)"
}

# Templates de Proposta (Estrutura para o AI ou Geração Manual)
PROMPT_TEMPLATES = {
    "freelancer": """### Proposal for Freelancer.com (Focus: Speed & Technical)
Language: English

Hello,
I have reverse-engineered your project: '{description}'.
Here is the technical roadmap to solve your pain points immediately:

| Phase | Milestone | Deliverable |
|-------|-----------|-------------|
| 1 | Technical Audit & Reverse Engineering | Gap Analysis |
| 2 | Arsenal Integration (Video/Traffic/SEO) | Technical Solution |
| 3 | Performance Scaling & ROI Tracking | Performance Report |

Technical Stack:
- Video: {video}
- Traffic: {traffic}
- SEO: {seo}
- Content: {content}

Test Keywords: [REVERSE-ENGINEERING], [4K-PIPELINE], [CAPI-OPTIMIZATION].""",

    "99freelas": """### Proposta para 99Freelas (Foco: ROI & Consultoria)
Idioma: Português

Olá,
Analisei seu projeto '{description}' e identifiquei os gargalos que estão travando seus resultados.
Minha abordagem foca em ROI real e consultoria estratégica, não apenas execução técnica.

Sugiro começarmos com um **Projeto Piloto** focado em validação rápida.

Nosso Arsenal Técnico Diferenciado:
- Vídeo: {video}
- Tráfego: {traffic}
- SEO: {seo}
- Conteúdo: {content}

Podemos agendar uma conversa para eu te mostrar como aplicaremos isso no seu caso?""",

    "upwork": """### Proposal for Upwork (Focus: Seniority & Case Studies)
Language: English

Dear Hiring Manager,
After reviewing your project description ('{description}'), I've applied a reverse-engineering lens to identify the core business objectives.
My senior approach ensures that every technical decision is backed by ROI and high-fidelity standards.

Strategy Highlights:
- High-Fidelity Production: {video}
- Data Attribution: {traffic}
- Generative Search Dominance: {seo}
- Authority Building: {content}

{questions_section}

I have successfully implemented similar strategies in past cases. Looking forward to discussing how we can replicate those results for you."""
}

def generate_proposal(platform, description, questions=None):
    """
    Generates a proposal based on the platform and project description using the defined templates.
    """
    platform = platform.lower().strip()

    # Simple mapping for robustness
    if "freelancer" in platform:
        key = "freelancer"
    elif "99freelas" in platform:
        key = "99freelas"
    elif "upwork" in platform:
        key = "upwork"
    else:
        return "Error: Unsupported platform. Use 'freelancer', '99freelas', or 'upwork'."

    template = PROMPT_TEMPLATES[key]

    # Prepare questions section for Upwork if needed
    questions_section = ""
    if key == "upwork" and questions:
        q_lines = ["#### Screening Questions:"]
        for i, q in enumerate(questions):
            q_lines.append(f"Q{i+1}: {q}")
            q_lines.append(f"A: [Detailed technical response addressing '{q}' using {ARSENAL['traffic']} and {ARSENAL['seo']} principles.]\n")
        questions_section = "\n".join(q_lines)
    elif key == "upwork":
        questions_section = "" # No questions provided

    # Fill the template
    try:
        return template.format(
            description=description,
            video=ARSENAL['video'],
            traffic=ARSENAL['traffic'],
            seo=ARSENAL['seo'],
            content=ARSENAL['content'],
            questions_section=questions_section
        )
    except KeyError as e:
        return f"Error filling template: Missing key {e}"

def main():
    parser = argparse.ArgumentParser(description='Generate S-Tier Proposals')
    parser.add_argument('--platform', required=True, help='Platform: freelancer, 99freelas, upwork')
    parser.add_argument('--description', required=True, help='Project description')
    parser.add_argument('--questions', nargs='*', help='Screening questions (for Upwork)')

    args = parser.parse_args()
    print(generate_proposal(args.platform, args.description, args.questions))

if __name__ == "__main__":
    main()
