class ProposalStrategy:
    ARSENAL = {
        "video": "Pipeline Veo 3 + Nano Banana (Fidelidade 4K) + ElevenLabs (Sound Design)",
        "traffic": "CAPI (Conversions API) + GTM Server-Side + Estratégia de Atribuição Avançada",
        "seo": "GEO (Generative Engine Optimization) + AEO (Answer Engine Optimization) + Knowledge Graph @graph",
        "content": "Técnica Nugget (Answer-First) + Information Gain (E-E-A-T)"
    }

    @staticmethod
    def get_prompt(platform, description):
        platform = platform.lower().strip()

        arsenal_text = "\n".join([f"- {k.capitalize()}: {v}" for k, v in ProposalStrategy.ARSENAL.items()])

        base_prompt = f"""
Aja como o Jules, Proposals Architect S-Tier.
Sua missão é criar uma proposta MATADORA para um projeto de freelance.
Use Engenharia Reversa para focar nas dores do cliente.

Projeto: '{description}'

Arsenal Técnico Disponível:
{arsenal_text}
"""

        if "freelancer" in platform:
            return f"""{base_prompt}
Plataforma: Freelancer.com
Idioma: Inglês
Foco: Velocidade e Resposta Técnica.
Estrutura Obrigatória:
1. Saudação direta.
2. Análise técnica do projeto (Reverse Engineering).
3. Tabela de Marcos (Milestones) com 3 fases: Audit, Execution, Scaling.
4. Lista do Arsenal Técnico utilizado.
5. "Test Keywords": [REVERSE-ENGINEERING], [4K-PIPELINE], [CAPI-OPTIMIZATION].
Retorne APENAS o texto da proposta.
"""
        elif "99freelas" in platform:
            return f"""{base_prompt}
Plataforma: 99Freelas
Idioma: Português
Foco: ROI e Consultoria.
Estrutura Obrigatória:
1. Saudação profissional (Tom de parceiro).
2. Identificação de gargalos (Pain Points).
3. Proposta de "Projeto Piloto" para validação.
4. Lista do Arsenal Técnico.
5. Convite para conversa (Call to Action).
Retorne APENAS o texto da proposta.
"""
        elif "upwork" in platform:
            return f"""{base_prompt}
Plataforma: Upwork
Idioma: Inglês
Foco: Senioridade e Estudos de Caso.
Estrutura Obrigatória:
1. Saudação formal.
2. Abordagem Sênior (Deep Technical Response).
3. Destaques da Estratégia (High-Fidelity, Data Attribution, GEO, Authority).
4. Se houver perguntas de triagem, responda com profundidade técnica.
5. Mencione casos de sucesso similares.
Retorne APENAS o texto da proposta.
"""
        else:
            return f"""{base_prompt}
Plataforma: Genérica
Idioma: Inglês
Foco: Melhor solução técnica possível.
Use o arsenal técnico para justificar a abordagem.
Retorne APENAS o texto da proposta.
"""
