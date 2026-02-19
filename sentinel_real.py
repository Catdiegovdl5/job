import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def limpar_texto(texto):
    # Remove marcadores e sujeira
    texto = re.sub(r'(?:__|\*\*|\[|#)?\s*SECAO_\d\s*(?:__|\*\*|\]|:|#)?', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\[?(S-TIER|MID-TIER)\]?', '', texto)
    remove_list = [
        "Resumo:", "Ferramentas:", "Proposta Direta:", 
        "Proposta Persuasiva:", "Opção A:", "Opção B:", 
        "O problema é que", "A solução é", "###"
    ]
    for item in remove_list:
        texto = texto.replace(item, "")
    return texto.strip()

def analisar_e_escrever(titulo, descricao, budget, skills):
    if not GROQ_API_KEY: return "ERRO KEY", "Sem API Key", "N/A", "Check .env", "Check .env", "0", "0"
    if not client: return "ERRO CLIENT", "Falha Client", "N/A", "Erro Client", "Erro Client", "0", "0"

    # --- CÉREBRO CAMALEÃO (V30) ---
    system_prompt = """
    Você é o 'Diego'. Sua missão é fechar contratos High-Ticket.
    Você não é mono-skill. Você se ADAPTA ao projeto.
    
    PASSO 1: IDENTIFIQUE O NICHO DO PROJETO:
    
    [CASO A: VÍDEO / YOUTUBE / EDIÇÃO]
    - Sua Persona: Especialista em Retenção e Viralização.
    - Sua Prova: "Cresci um canal até 12k inscritos (100k views) e VENDI a operação."
    - Oferta: "Faço um Style Frame (Teste de 5s) para validar a estética."
    - Ferramentas: After Effects, Premiere, CapCut.
    
    [CASO B: DADOS / EXCEL / AUTOMAÇÃO / PYTHON]
    - Sua Persona: Especialista em Automação e Inteligência de Dados.
    - Sua Prova: "Crio scripts em Python que automatizam o trabalho manual de dias em minutos."
    - Oferta: "Posso automatizar essa planilha/processo para rodar sozinho."
    - Ferramentas: Python (Pandas), Excel Avançado, Dashboards, Web Scraping.
    
    [CASO C: TRÁFEGO / MARKETING / COPY]
    - Sua Persona: Gestor de Performance.
    - Sua Prova: "Foco em ROI e Conversão, não em métricas de vaidade."
    - Ferramentas: Facebook Ads, Google Ads, Copywriting Persuasivo.

    REGRAS DE OURO:
    - NUNCA misture as personas. Se o projeto é planilha, NÃO fale de "Sound Design".
    - Se o projeto é Vídeo, NÃO fale de "Planilhas".
    - Use "Eu" (Lobo Solitário).
    - ZERO papo corporativo ("Prezado", "Abrangente", "Significativo"). Seja técnico e direto.
    - NUNCA comece com "Olá! Sou o Diego" ou "Meu nome é Diego". Vá direto ao ponto.

    ESTRUTURA OBRIGATÓRIA:
    __SECAO_0__
    [S-TIER]
    __SECAO_1__
    [Resumo Ácido: Aponte o erro que eles estão cometendo hoje no nicho deles]
    __SECAO_2__
    [3 Ferramentas REAIS para AQUELE nicho específico]
    __SECAO_3__
    [Proposta Direta: "Li o escopo. Minha stack é X. Entrego em Y dias. Valor: $. Vamos?"]
    __SECAO_4__
    [Proposta Persuasiva: Use a "Prova" correta para o nicho (Canal Vendido OU Automação Python).]
    """

    user_prompt = f"""
    PROJETO DO CLIENTE:
    Título: {titulo}
    Descrição: {descricao}
    Budget: {budget}
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=1500
        )

        content = completion.choices[0].message.content.strip()
        
        # DEBUG
        print("\n" + "="*10 + " CÉREBRO ADAPTATIVO V30 " + "="*10)
        print(content[:100] + "...")

        dados = {
            "0": "MID-TIER", "1": "...", "2": "...", "3": "Erro A", "4": content
        }

        parts = re.split(r'(?:__|\*\*|#)?\s*SECAO_(\d)\s*(?:__|\*\*|#)?', content, flags=re.IGNORECASE)
        
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                chave = parts[i].strip()
                valor = parts[i+1].strip()
                if chave in dados:
                    dados[chave] = limpar_texto(valor)

        return dados["0"], dados["1"], dados["2"], dados["3"], dados["4"], budget, "7"

    except Exception as e:
        print(f"❌ Erro: {e}")
        return "ERRO", "Falha", "N/A", "Erro", f"Erro: {e}", "0", "0"

def gerar_analise_diego(title, desc, budget, usd):
    return analisar_e_escrever(title, desc, budget, "Geral")
