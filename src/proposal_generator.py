import argparse
import sys
from src.config import ARSENAL

def generate_proposal(platform, description, questions=None):
    """
    Generates a proposal based on the platform and project description.

    Arsenal:
    - Video: Pipeline Veo 3 + Nano Banana (Fidelidade 4K) + ElevenLabs (Sound Design).
    - Traffic: CAPI (Conversions API) + GTM Server-Side + Estratégia de Atribuição Avançada.
    - SEO: GEO (Generative Engine Optimization) + AEO (Answer Engine Optimization) + Knowledge Graph @graph.
    - Content: Técnica Nugget (Answer-First) + Information Gain (E-E-A-T).
    """

    platform = platform.lower().strip()
    proposal = []

    if "freelancer" in platform:
        proposal.append("### Proposal for Freelancer.com (Focus: Speed & Technical)")
        proposal.append("Language: English\n")
        proposal.append("Hello,")
        proposal.append(f"I have reverse-engineered your project: '{description}'.")
        proposal.append("Here is the technical roadmap to solve your pain points immediately:\n")
        proposal.append("| Phase | Milestone | Deliverable |")
        proposal.append("|-------|-----------|-------------|")
        proposal.append("| 1 | Technical Audit & Reverse Engineering | Gap Analysis |")
        proposal.append("| 2 | Arsenal Integration (Video/Traffic/SEO) | Technical Solution |")
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

    args = parser.parse_args()
    print(generate_proposal(args.platform, args.description, args.questions))

if __name__ == "__main__":
    main()
