from sentinel_real import gerar_analise_diego

# Simulação de um projeto real da Workana
titulo = "Editor de Vídeo para Canal Dark no Youtube"
desc = "Preciso de um editor para fazer 2 vídeos por semana de curiosidades. Eu mando o áudio e o roteiro. Precisa buscar imagens sem direitos autorais e colocar legendas dinâmicas. Pago R$ 50 por vídeo."
budget = "R$ 50 - 100 BRL"

print("🧠 JULES ESTÁ PENSANDO...")
nivel, resumo, arsenal, opc_a, opc_b = gerar_analise_diego(titulo, desc, budget, 0)

print("-" * 30)
print(f"🏆 NÍVEL: {nivel}")
print(f"📝 RESUMO: {resumo}")
print("-" * 30)
print(f"🎯 OPÇÃO A (Direta):\n{opc_a}")
print("-" * 30)
print(f"🤝 OPÇÃO B (Persuasiva):\n{opc_b}")
print("-" * 30)
