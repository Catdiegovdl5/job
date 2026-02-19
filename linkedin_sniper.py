import os
import sys
import asyncio
import csv
from datetime import datetime
from groq import Groq
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ ERRO: Configure a GROQ_API_KEY no .env")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

# --- FUNÇÃO DE CRM (NOVIDADE V9) ---
def salvar_lead(nome, cargo, empresa, mensagem):
    # Use absolute path to ensure it writes to the correct directory
    arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads_linkedin.csv")
    header = ["Data", "Nome", "Cargo/Empresa", "Mensagem Gerada", "Status"]
    
    # Cria o arquivo com cabeçalho se não existir
    novo_arquivo = not os.path.exists(arquivo)
    
    with open(arquivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';') # Ponto e vírgula para abrir fácil no Excel BR
        if novo_arquivo:
            writer.writerow(header)
        
        # Salva o Lead (Write the lead)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            nome,
            cargo,
            mensagem,
            "Enviado (Pendente)"
        ])
    print(f"   💾 [CRM] Lead {nome} salvo no Excel.")

async def gerar_mensagem(nome, contexto):
    prompt = f"""
    Aja como especialista em Networking B2B.
    ALVO: {nome} | CONTEXTO: "{contexto}"
    MISSÃO: Escreva mensagem de conexão LinkedIn (Note) curta (Max 200 chars).
    REGRAS: 
    1. "Olá {nome.split()[0]},".
    2. Mencione cargo/empresa se houver.
    3. Final: "Vamos conectar?" ou "Abraço!".
    SAÍDA: Apenas o texto.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=150
        )
        msg = completion.choices[0].message.content.replace('"', '').strip()
        return msg
    except:
        return f"Olá {nome.split()[0]}, vi seu perfil profissional e gostaria de conectar."

async def linkedin_radar():
    print("🕵️♂️ LINKEDIN SNIPER V9.1 (MIRA INTELIGENTE)...")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0]
            
            # --- NOVO: BUSCA A ABA DO LINKEDIN ENTRE TODAS AS ABERTAS ---
            page = None
            for p_temp in context.pages:
                titulo = await p_temp.title()
                if "LinkedIn" in titulo:
                    page = p_temp
                    break
            
            if not page:
                print("❌ ERRO: Não encontrei nenhuma aba do LinkedIn aberta!")
                print(f"Abas detectadas: {[await p_tab.title() for p_tab in context.pages]}")
                return
            # ------------------------------------------------------------

        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return

        print(f"🎯 Mira travada na aba: {await page.title()}")

        print("📜 Carregando lista...")
        await page.mouse.wheel(0, 4000)
        await asyncio.sleep(2)
        await page.mouse.wheel(0, -2000)
        
        # Pega todos os links de perfil
        links = await page.locator('a[href*="/in/"]').all()
        
        processed_names = [] # Lista para evitar duplicatas
        count = 0

        print(f"🎯 Buscando Alvos e Salvando no CRM...")
        print("-" * 50)

        for link in links:
            if count >= 5: break # Limite de 5 por vez
            
            try:
                raw_text = await link.inner_text()
                
                # --- LIMPEZA DE NOME ---
                # Remove quebras de linha e pega só a primeira parte
                nome_limpo = raw_text.split("\n")[0].strip()
                # Remove o "• 2º" ou "• 3º+"
                nome_limpo = nome_limpo.split("•")[0].strip()
                
                # Filtros de Qualidade
                if len(nome_limpo) < 3: continue
                if "LinkedIn" in nome_limpo or "Member" in nome_limpo: continue
                
                # Filtro de Duplicata (Se já processou, pula)
                if nome_limpo in processed_names:
                    continue

                # Captura Contexto (Sobe na árvore HTML para ler o cargo)
                pai = link.locator('xpath=../../../../..')
                if await pai.count() == 0: 
                    pai = link.locator('xpath=../../..')
                
                contexto = await pai.inner_text()
                if len(contexto) < 15: continue # Contexto vazio = lixo

                print(f"👤 ALVO: {nome_limpo}")
                
                # Gera Copy
                # Passa apenas o nome limpo para a IA, mas usa o contexto para info
                msg = await gerar_mensagem(nome_limpo, contexto)
                
                print(f"📝 COPY: {msg}")
                
                # --- SALVA NO EXCEL ---
                # Limpa quebras de linha do contexto para o CSV ficar bonito
                contexto_csv = contexto.replace("\n", " | ")
                salvar_lead(nome_limpo, contexto_csv, "N/A", msg)
                
                print("-" * 50)
                
                processed_names.append(nome_limpo)
                count += 1
                
            except Exception:
                pass

        if count > 0:
            print(f"\n✅ {count} Leads salvos em 'leads_linkedin.csv'.")
        else:
            print("⚠️ Nenhum alvo novo encontrado. Tente descer mais a página.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(linkedin_radar())
