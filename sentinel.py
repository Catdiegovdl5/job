import os
import re
import logging
from groq import Groq, RateLimitError
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client_groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
logger = logging.getLogger("Diego_Brain")

def gerar_analise_diego(titulo, desc, budget_str, usd_val):
    if not client_groq:
        return "N/A", "Erro API", "N/A", "N/A", "N/A"

    prompt = f"""
    Role: Diego, Especialista em Freelance e Poliglota.
    Project: "{titulo}"
    Context: "{desc}"

    INSTRUCTIONS:
    1. SECAO 0: NIVEL (💎 S-TIER ou ⚖️ MID-TIER)
    2. SECAO 1: RESUMO (Escreva em Português-Brasil, foco na dor do cliente)
    3. SECAO 2: ARSENAL (Ferramentas recomendadas)
    4. IDIOMA: Identifique o idioma do projeto (PT, EN ou ES). Responda as SECOES 3 e 4 nesse idioma.
    5. SECAO 3: OPC_A (Proposta técnica e direta)
    6. SECAO 4: OPC_B (Proposta persuasiva e de parceria)

    RULES:
    - Never use bold (**) or italics (_).
    - Format exactly as: SECAO X: content
    - Language of 3 and 4 MUST match the project.
    """

    try:
        completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        content = re.sub(r'[\*\#_]', '', completion.choices[0].message.content.strip())

        # 🛡️ Blindagem: Garante que sempre teremos 5 partes
        res = {"0": "MID-TIER", "1": "...", "2": "...", "3": "...", "4": "..."}

        # Divide o texto procurando os marcadores SECAO X
        # O split retorna algo como ['', '0', 'conteudo0', '1', 'conteudo1', ...]
        parts = re.split(r'SECAO\s*(\d)\s*:', content, flags=re.IGNORECASE)

        # Reatribui as partes encontradas
        # Começa do indice 1 (que é o numero da secao), e avança de 2 em 2
        for i in range(1, len(parts), 2):
            key = parts[i]
            if key in res:
                # O texto da seção está no próximo índice
                if i+1 < len(parts):
                    res[key] = parts[i+1].strip()

        return res["0"], res["1"], res["2"], res["3"], res["4"]

    except Exception as e:
        print(f"⚠️ Erro no Diego: {e}")
        return "Erro", "Erro", "Erro", "Erro", "Erro"
