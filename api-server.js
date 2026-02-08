#!/usr/bin/env node
/**
 * Serveur REST API pour Clawd
 * Permet à Siri (via Shortcuts) et d'autres services de piloter Clawd
 */

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Logs
const logFile = path.join(__dirname, 'api-logs.json');
function logAction(action, data = {}) {
  const log = {
    timestamp: new Date().toISOString(),
    action,
    data,
  };

  const logs = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile)) : [];
  logs.push(log);

  // Garder seulement les 100 derniers logs
  if (logs.length > 100) {
    logs.shift();
  }

  fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
  console.log(`[${new Date().toISOString()}] ${action}`, data);
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Endpoint: Gmail - Lire les emails
app.get('/api/gmail/read', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;

    // Vérifier si les credentials Gmail sont disponibles
    const credentialsPath = path.join(__dirname, '.gmail-token.json');
    if (!fs.existsSync(credentialsPath)) {
      return res.status(400).json({
        error: 'Gmail non configuré',
        message: 'Veuillez configurer les credentials Gmail d\'abord',
      });
    }

    const { google } = require('googleapis');
    const TOKEN_PATH = credentialsPath;
    const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];

    const auth = new google.auth.OAuth2();
    auth.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH)));

    const gmail = google.gmail({ version: 'v1', auth });
    const gmailRes = await gmail.users.messages.list({
      userId: 'me',
      maxResults: limit,
    });

    const messages = gmailRes.data.messages || [];

    // Récupérer les détails de chaque email
    const emails = [];
    for (const msg of messages.slice(0, 5)) { // Limité à 5 pour la performance
      const details = await gmail.users.messages.get({
        userId: 'me',
        id: msg.id,
        format: 'metadata',
        metadataHeaders: ['Subject', 'From', 'Date'],
      });

      const headers = {};
      details.data.payload.headers.forEach(h => {
        headers[h.name] = h.value;
      });

      emails.push({
        id: msg.id,
        subject: headers.Subject,
        from: headers.From,
        date: headers.Date,
        snippet: details.data.snippet,
      });
    }

    logAction('gmail_read', { count: emails.length, limit });

    res.json({
      success: true,
      count: emails.length,
      emails,
    });
  } catch (error) {
    logAction('gmail_error', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Gmail - Vérifier les emails non-lus
app.get('/api/gmail/check', async (req, res) => {
  try {
    const credentialsPath = path.join(__dirname, '.gmail-token.json');
    if (!fs.existsSync(credentialsPath)) {
      return res.status(400).json({
        error: 'Gmail non configuré',
        message: 'Veuillez configurer les credentials Gmail d\'abord',
      });
    }

    const { google } = require('googleapis');
    const TOKEN_PATH = credentialsPath;

    const auth = new google.auth.OAuth2();
    auth.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH)));

    const gmail = google.gmail({ version: 'v1', auth });
    const resGmail = await gmail.users.messages.list({
      userId: 'me',
      q: 'is:unread',
      maxResults: 20,
    });

    const messages = resGmail.data.messages || [];

    logAction('gmail_check', { unreadCount: messages.length });

    res.json({
      success: true,
      unreadCount: messages.length,
      messagesCount: messages.length,
    });
  } catch (error) {
    logAction('gmail_error', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Navigateur - Ouvrir une URL
app.post('/api/browser/open', async (req, res) => {
  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({ success: false, error: 'URL requise' });
    }

    const browser = await chromium.launch({
      headless: true,
      executablePath: '/snap/bin/chromium',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });

    const title = await page.title();

    logAction('browser_open', { url, title });

    res.json({
      success: true,
      url,
      title,
    });

    await browser.close();
  } catch (error) {
    logAction('browser_error', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Navigateur - Capturer une page
app.post('/api/browser/screenshot', async (req, res) => {
  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({ success: false, error: 'URL requise' });
    }

    const browser = await chromium.launch({
      headless: true,
      executablePath: '/snap/bin/chromium',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });

    const screenshotPath = path.join(__dirname, 'downloads', `screenshot-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    logAction('browser_screenshot', { url, screenshotPath });

    res.json({
      success: true,
      url,
      screenshot: screenshotPath,
    });

    await browser.close();
  } catch (error) {
    logAction('browser_error', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Récupérer les logs
app.get('/api/logs', (req, res) => {
  try {
    const logs = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile)) : [];
    res.json({ success: true, logs });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Commande personnalisée (pour Clawdbot)
app.post('/api/command', async (req, res) => {
  try {
    const { command, message } = req.body;

    if (!command && !message) {
      return res.status(400).json({ success: false, error: 'Commande ou message requis' });
    }

    logAction('custom_command', { command, message });

    // Écrire le message dans un fichier pour que Clawdbot puisse le lire
    const triggerFile = path.join(__dirname, '.trigger-message.txt');
    fs.writeFileSync(triggerFile, message || command);

    res.json({
      success: true,
      message: `Message enregistré pour envoi: ${message || command}`,
    });
  } catch (error) {
    logAction('command_error', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Envoi direct sur Telegram
app.post('/api/telegram-send', async (req, res) => {
  try {
    const { message, chatId } = req.body;

    if (!message) {
      return res.status(400).json({ success: false, error: 'Message requis' });
    }

    const targetChatId = chatId || '875268068'; // Buralux par défaut

    logAction('telegram_send', { chatId: targetChatId, messageLength: message.length });

    // Pour envoyer directement sur Telegram, on aurait besoin d'aller via l'API Clawdbot
    // Pour l'instant, on utilise le fichier trigger comme avant
    const triggerFile = path.join(__dirname, '.trigger-message.txt');
    fs.writeFileSync(triggerFile, message);

    res.json({
      success: true,
      message: 'Message enregistré pour envoi via heartbeat',
      chatId: targetChatId,
    });
  } catch (error) {
    logAction('telegram_send_error', { error: error.message });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Démarrer le serveur
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Serveur API Clawd démarré`);
  console.log(`📡 Port: ${PORT}`);
  console.log(`🔗 URL: http://0.0.0.0:${PORT}`);
  console.log(`\n📋 Endpoints disponibles:`);
  console.log(`   GET  /health                    - Vérifier l'état`);
  console.log(`   GET  /api/gmail/read             - Lire les emails`);
  console.log(`   GET  /api/gmail/check            - Vérifier les emails non-lus`);
  console.log(`   POST /api/browser/open          - Ouvrir une URL`);
  console.log(`   POST /api/browser/screenshot     - Capturer une page`);
  console.log(`   GET  /api/logs                  - Voir les logs`);
  console.log(`   POST /api/command               - Commande personnalisée`);
  console.log(`\n⏳ Serveur en cours d'exécution...`);
});
