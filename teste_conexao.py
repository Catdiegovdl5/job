import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def teste_vida():
    print("📡 Testando conexão com Llama 3.3 (70B)...")
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ ERRO: Chave API não encontrada no .env")
        return

    try:
        client = Groq(api_key=api_key)
        
        # Usando o modelo NOVO que você listou
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Responda apenas: 'Sistemas 70B Online'.",
                }
            ],
            model="llama-3.3-70b-versatile", 
        )

        print("✅ CONEXÃO BEM SUCEDIDA!")
        print(f"🤖 Resposta do Robô: {chat_completion.choices[0].message.content}")

    except Exception as e:
        print(f"❌ FALHA CRÍTICA: {e}")

if __name__ == "__main__":
    teste_vida()
