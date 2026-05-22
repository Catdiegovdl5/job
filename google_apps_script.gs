/**
 * =======================================================================
 * DIEGO.SYSTEMS | FUNNEL TELEMETRY GATEWAY
 * Google Apps Script — Versão: 2.0.0
 * =======================================================================
 *
 * INSTRUÇÕES DE CONFIGURAÇÃO:
 * 1. Abra sua planilha Google Sheets (ou crie uma nova).
 * 2. Vá em: Extensões > Apps Script
 * 3. Cole TODO este código substituindo o código padrão.
 * 4. Preencha as configurações abaixo (TELEGRAM_BOT_TOKEN).
 * 5. Salve (Ctrl+S) e clique em "Implantar" > "Nova Implantação".
 * 6. Tipo: "App da Web". Executar como: "Eu". Acesso: "Qualquer pessoa".
 * 7. Copie a URL gerada e cole no index.html em CONFIG.webhookUrl.
 *
 * SEGURANÇA: O token do Telegram fica APENAS no servidor do Google.
 * O código público do portfólio nunca expõe credenciais.
 * =======================================================================
 */

// =====================================================================
// CONFIGURAÇÕES — PREENCHA AQUI
// =====================================================================
const TELEGRAM_BOT_TOKEN = '7724330024:AAFtoSLgXVDlvNmeyPCVMnkWIqbk4wvLSVg'; // @mira262005_bot
const TELEGRAM_CHAT_ID   = '1501131002';      // Seu chat_id já configurado
const SHEET_NAME         = 'Leads';           // Nome da aba na planilha

// =====================================================================
// FUNÇÃO PRINCIPAL — Recebe o POST do portfólio
// =====================================================================
function doPost(e) {
  try {
    const rawBody = e.postData ? e.postData.contents : null;

    if (!rawBody) {
      return buildResponse(false, 'Payload vazio recebido.');
    }

    const payload = JSON.parse(rawBody);

    // Salva na planilha
    saveToSheet(payload);

    // Envia notificação no Telegram
    sendTelegramNotification(payload);

    return buildResponse(true, 'Lead processado com sucesso!');

  } catch (error) {
    console.error('Erro no doPost:', error.toString());
    return buildResponse(false, 'Erro interno: ' + error.toString());
  }
}

// =====================================================================
// Teste via GET (acesse a URL no navegador para verificar se está ativo)
// =====================================================================
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: 'ONLINE',
      sistema: 'DIEGO.SYSTEMS FUNNEL GATEWAY',
      versao: '2.0.0',
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

// =====================================================================
// SALVAR NA PLANILHA GOOGLE SHEETS
// =====================================================================
function saveToSheet(payload) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);

  // Cria a aba se não existir
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);

    // Cabeçalhos com formatação
    const headers = [
      'Data/Hora',
      'Status',
      'Nome',
      'Email',
      'WhatsApp',
      'Site',
      'Faturamento',
      'Investimento em Ads',
      'Gargalo Principal',
      'Tópico de Origem'
    ];

    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

    // Formata cabeçalho
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setBackground('#E25B22');
    headerRange.setFontColor('#FFFFFF');
    headerRange.setFontWeight('bold');
    headerRange.setFontSize(11);
    sheet.setFrozenRows(1);
    sheet.setColumnWidths(1, headers.length, 180);
  }

  // Monta a linha de dados
  const timestamp   = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  const status      = payload.status_qualificacao || 'N/A';
  const nome        = payload.contato?.nome || '';
  const email       = payload.contato?.email || '';
  const whatsapp    = payload.contato?.whatsapp || '';
  const site        = payload.contato?.site || '';
  const faturamento = payload.dados_empresa?.faturamento || '';
  const investimento= payload.dados_empresa?.investimento_anuncios || '';
  const gargalo     = payload.dados_empresa?.gargalo_principal || '';
  const topico      = payload.topico_origem || 'portfolio';

  sheet.appendRow([
    timestamp,
    status,
    nome,
    email,
    whatsapp,
    site,
    faturamento,
    investimento,
    gargalo,
    topico
  ]);

  // Colorir linha por status de qualificação
  const lastRow   = sheet.getLastRow();
  const rowRange  = sheet.getRange(lastRow, 1, 1, 10);

  if (status === 'QUALIFICADO') {
    rowRange.setBackground('#d4edda'); // Verde claro
    sheet.getRange(lastRow, 2).setFontColor('#155724').setFontWeight('bold');
  } else {
    rowRange.setBackground('#fff3cd'); // Amarelo claro
    sheet.getRange(lastRow, 2).setFontColor('#856404').setFontWeight('bold');
  }

  console.log('Lead salvo na planilha com sucesso:', nome);
}

// =====================================================================
// ENVIAR NOTIFICAÇÃO VIA TELEGRAM
// =====================================================================
function sendTelegramNotification(payload) {
  if (!TELEGRAM_BOT_TOKEN || TELEGRAM_BOT_TOKEN === 'SEU_TOKEN_AQUI') {
    console.warn('Token do Telegram não configurado. Configure TELEGRAM_BOT_TOKEN.');
    return;
  }

  const status      = payload.status_qualificacao || 'N/A';
  const nome        = payload.contato?.nome || '(sem nome)';
  const email       = payload.contato?.email || '(sem email)';
  const whatsapp    = payload.contato?.whatsapp || '(sem WhatsApp)';
  const site        = payload.contato?.site || '(sem site)';
  const faturamento = payload.dados_empresa?.faturamento || 'N/A';
  const investimento= payload.dados_empresa?.investimento_anuncios || 'N/A';
  const gargalo     = payload.dados_empresa?.gargalo_principal || 'N/A';
  const agora       = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

  // Ícone e título baseado no status
  const iconeStatus    = status === 'QUALIFICADO' ? '🟢✅' : '🟡⚠️';
  const tituloStatus   = status === 'QUALIFICADO'
    ? '🔥 LEAD QUALIFICADO — ACIONAR AGORA!'
    : '📋 Lead Registrado (Low-Tier)';

  const mensagem = `${iconeStatus} *${tituloStatus}*\n\n` +
    `⏰ *Horário:* ${agora}\n` +
    `📊 *STATUS:* \`${status}\`\n\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `👤 *Nome:* ${nome}\n` +
    `📧 *Email:* ${email}\n` +
    `📱 *WhatsApp:* ${whatsapp}\n` +
    `🌐 *Site:* ${site}\n\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `💰 *Faturamento:* ${faturamento}\n` +
    `📈 *Investimento Ads:* ${investimento}\n` +
    `🛠️ *Gargalo:* ${gargalo}\n\n` +
    `📝 _Lead salvo automaticamente no Google Sheets._`;

  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: mensagem,
      parse_mode: 'Markdown'
    }),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const result   = JSON.parse(response.getContentText());

    if (result.ok) {
      console.log('Notificação Telegram enviada com sucesso!');
    } else {
      console.error('Erro Telegram API:', JSON.stringify(result));
    }
  } catch (err) {
    console.error('Erro ao enviar para Telegram:', err.toString());
  }
}

// =====================================================================
// HELPER — Resposta padronizada JSON
// =====================================================================
function buildResponse(success, message) {
  return ContentService
    .createTextOutput(JSON.stringify({
      success: success,
      message: message,
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}
