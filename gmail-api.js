#!/usr/bin/env node
/**
 * Gmail API Helper - OAuth2
 * Utilisation propre de l'API Gmail (pas besoin de navigateur)
 */

const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const TOKEN_PATH = path.join(__dirname, '.gmail-token.json');
const CREDENTIALS_PATH = path.join(__dirname, 'gmail-credentials.json');

/**
 * Charger les credentials OAuth
 */
function loadCredentials() {
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    console.error('❌ Fichier de credentials manquant:', CREDENTIALS_PATH);
    console.log('\n📝 Étapes pour obtenir les credentials :\n');
    console.log('1. Allez sur https://console.cloud.google.com/\n');
    console.log('2. Créez un nouveau projet\n');
    console.log('3. Activez l\'API Gmail :\n');
    console.log('   https://console.cloud.google.com/apis/library/gmail.googleapis.com\n');
    console.log('4. Créez des credentials OAuth 2.0 :\n');
    console.log('   - Type: Application de bureau\n');
    console.log('   - Scopes: https://www.googleapis.com/auth/gmail.readonly\n');
    console.log('5. Téléchargez le fichier JSON et renommez-le en "gmail-credentials.json"\n');
    console.log('6. Placez-le dans:', path.dirname(CREDENTIALS_PATH));
    process.exit(1);
  }

  const content = fs.readFileSync(CREDENTIALS_PATH);
  return JSON.parse(content);
}

/**
 * Obtenir et sauvegarder le token d'accès
 */
async function authorize() {
  const credentials = loadCredentials();
  const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;
  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

  // Vérifier si on a déjà un token
  if (fs.existsSync(TOKEN_PATH)) {
    oAuth2Client.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH)));
    return oAuth2Client;
  }

  // Sinon, demander l'autorisation
  return getNewToken(oAuth2Client);
}

/**
 * Obtenir un nouveau token OAuth
 */
function getNewToken(oAuth2Client) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('🔗 Ouvrez cette URL dans votre navigateur :\n');
  console.log(authUrl, '\n');
  console.log('✅ Connectez-vous avec votre compte Google\n');
  console.log('⏳ Une fois connecté, vous serez redirigé vers une URL vide\n');
  console.log('📋 Copiez l\'URL complète et collez-la ici:\n');

  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  rl.question('URL de redirection: ', (code) => {
    rl.close();
    oAuth2Client.getToken(code, (err, token) => {
      if (err) {
        console.error('❌ Erreur lors de la récupération du token:', err);
        return;
      }

      oAuth2Client.setCredentials(token);
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(token, null, 2));
      console.log('\n✅ Token sauvegardé dans:', TOKEN_PATH);
      console.log('✅ Vous êtes maintenant authentifié !\n');
      process.exit(0);
    });
  });
}

/**
 * Lister les emails
 */
async function listEmails(maxResults = 10) {
  const auth = await authorize();
  const gmail = google.gmail({ version: 'v1', auth });

  const res = await gmail.users.messages.list({
    userId: 'me',
    maxResults: maxResults,
  });

  const messages = res.data.messages || [];
  console.log(`\n📧 ${messages.length} emails trouvés:\n`);

  if (messages.length === 0) {
    console.log('Aucun email.');
    return;
  }

  // Récupérer les détails de chaque email
  for (const message of messages) {
    const msg = await gmail.users.messages.get({
      userId: 'me',
      id: message.id,
      format: 'metadata',
      metadataHeaders: ['Subject', 'From', 'Date'],
    });

    const headers = {};
    msg.data.payload.headers.forEach(h => {
      headers[h.name] = h.value;
    });

    console.log(`📬 De: ${headers.From}`);
    console.log(`   Sujet: ${headers.Subject}`);
    console.log(`   Date: ${headers.Date}`);
    console.log(`   ID: ${message.id}`);
    console.log('---');
  }
}

/**
 * Vérifier les emails non-lus
 */
async function checkUnread() {
  const auth = await authorize();
  const gmail = google.gmail({ version: 'v1', auth });

  const res = await gmail.users.messages.list({
    userId: 'me',
    q: 'is:unread',
    maxResults: 20,
  });

  const messages = res.data.messages || [];
  console.log(`\n📬 ${messages.length} emails non-lus:\n`);

  if (messages.length === 0) {
    console.log('✅ Aucun email non-lu.');
    return;
  }

  for (const message of messages) {
    const msg = await gmail.users.messages.get({
      userId: 'me',
      id: message.id,
      format: 'metadata',
      metadataHeaders: ['Subject', 'From', 'Date'],
    });

    const headers = {};
    msg.data.payload.headers.forEach(h => {
      headers[h.name] = h.value;
    });

    console.log(`📬 De: ${headers.From}`);
    console.log(`   Sujet: ${headers.Subject}`);
    console.log(`   Date: ${headers.Date}`);
    console.log('---');
  }
}

/**
 * Main
 */
async function main() {
  const action = process.argv[2];

  switch (action) {
    case 'auth':
      await authorize();
      console.log('✅ Authentification réussie !');
      break;
    case 'read':
      const limit = parseInt(process.argv[3]) || 10;
      await listEmails(limit);
      break;
    case 'check':
      await checkUnread();
      break;
    default:
      console.log('Usage: node gmail-api.js <action> [args]');
      console.log('\nActions:');
      console.log('  auth      - Première authentification (OAuth)');
      console.log('  read [N]  - Lire les N derniers emails (défaut: 10)');
      console.log('  check     - Vérifier les emails non-lus\n');
      console.log('⚠️  Note: La première fois, utilisez "auth" pour configurer OAuth');
      console.log('   Vous aurez besoin du fichier gmail-credentials.json\n');
  }
}

main().catch(console.error);
