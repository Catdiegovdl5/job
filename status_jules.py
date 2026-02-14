import os
import re
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Caminhos das pastas do projeto
PASTA_FONTE = "FILTRADO_MAX_3"
PASTA_CERTO = "CERTO"
PASTA_LIXO = "LIXO"
ARQUIVO_WHATSAPP = "Conversa do WhatsApp com Mauro.txt"

def check_status():
    logging.info("-" * 50)
    logging.info("🚀 RELATÓRIO DE STATUS DO JULES - PROJETO MAURO")
    logging.info("-" * 50)

    # 1. Analisa a conversa do WhatsApp
    try:
        with open(ARQUIVO_WHATSAPP, "r", encoding="utf-8") as f:
            texto = f.read()
            # Procura links do TikTok enviados (vm.tiktok.com ou vt.tiktok.com)
            links = re.findall(r'https://v[mt]\.tiktok\.com/\S+', texto)
            total_links = len(set(links))
    except FileNotFoundError:
        total_links = 0
        logging.warning("⚠️ Arquivo de conversa não encontrado.")

    # 2. Conta o progresso nas pastas
    def contar_pastas(diretorio):
        if not os.path.exists(diretorio): return 0
        return len([d for d in os.listdir(diretorio) if os.path.isdir(os.path.join(diretorio, d))])

    pendentes = contar_pastas(PASTA_FONTE)
    aprovados = contar_pastas(PASTA_CERTO)
    descartados = contar_pastas(PASTA_LIXO)
    total_processado = aprovados + descartados

    # 3. Exibe o Painel
    logging.info(f"📥 Links detectados na conversa: {total_links}")
    logging.info(f"⏳ Itens aguardando auditoria: {pendentes}")
    logging.info(f"✅ Músicas aprovadas (CERTO): {aprovados}")
    logging.info(f"❌ Músicas descartadas (LIXO): {descartados}")

    if total_processado > 0:
        aproveitamento = (aprovados / total_processado) * 100
        logging.info(f"📈 Taxa de aprovação: {aproveitamento:.1f}%")

    logging.info("-" * 50)
    if pendentes > 0:
        logging.info(f"💡 Dica do Jules: Você ainda tem {pendentes} pastas para revisar no 'auditor.py'!")
    else:
        logging.info("🎉 Parabéns, Diego! Você processou tudo o que foi baixado.")

if __name__ == "__main__":
    check_status()
