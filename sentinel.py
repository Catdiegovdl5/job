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

    # Prompt recalibrado para 5 SEÇÕES (V7.1)
    prompt = f"""
    Role: Diego, Especialista em Freelance e Poliglota.
    Project: "{titulo}"
    Context: "{desc}"

    INSTRUCTIONS:
    1. SECAO 1 (RESUMO): Escreva em Português (Brasil), foco na dor do cliente.
    2. IDIOMA: Identifique se o projeto é PT, EN ou ES.
    3. PROPOSTAS: Escreva as seções 3 e 4 no MESMO idioma do projeto.
    4. MÚLTIPLA ESCOLHA:
       - SECAO 3 (OPC_A): Proposta técnica e direta.
       - SECAO 4 (OPC_B): Proposta persuasiva e de parceria.

    FORMATO OBRIGATÓRIO (NÃO USE BOLD ** OU MARCADORES #):
    SECAO 0: [NIVEL]
    SECAO 1: [RESUMO]
    SECAO 2: [ARSENAL]
    SECAO 3: [OPC_A]
    SECAO 4: [OPC_B]
    """

    try:
        completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        content = re.sub(r'[\*\#_]', '', completion.choices[0].message.content.strip())

        # Extração Robusta de 5 partes
        sections = {"0": "MID-TIER", "1": "...", "2": "...", "3": "...", "4": "..."}
        current = None
        for line in content.split('\n'):
            if "SECAO " in line.upper():
                match = re.search(r'SECAO (\d)', line.upper())
                if match: current = match.group(1)
                continue
            if current and line.strip():
                sections[current] = sections[current].replace("...", "") + " " + line.strip()

        # RETORNA EXATAMENTE 5 VALORES PARA O MONITOR
        return sections["0"].strip(), sections["1"].strip(), sections["2"].strip(), sections["3"].strip(), sections["4"].strip()

    except Exception as e:
        print(f"⚠️ Erro no Diego: {e}")
        return "Erro", "Erro", "Erro", "Erro", "Erro"
