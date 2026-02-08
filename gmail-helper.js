#!/usr/bin/env node
/**
 * Helper pour Gmail via Playwright (headless)
 * Fonctions: login, read-emails, check-new-emails, send-email
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  headless: true,
  viewport: { width: 1280, height: 800 },
  downloadPath: path.join(__dirname, 'downloads'),
  cookiesPath: path.join(__dirname, '.gmail-cookies.json'),
};

if (!fs.existsSync(CONFIG.downloadPath)) {
  fs.mkdirSync(CONFIG.downloadPath, { recursive: true });
}

/**
 * Lancer le navigateur avec cookies sauvegardés
 */
async function launchBrowser() {
  const browser = await chromium.launch({
    headless: CONFIG.headless,
    executablePath: '/snap/bin/chromium', // Utiliser Chromium Snap installé
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const context = await browser.newContext({
    viewport: CONFIG.viewport,
    storageState: fs.existsSync(CONFIG.cookiesPath) ? CONFIG.cookiesPath : undefined,
  });

  return { browser, context };
}

/**
 * Sauvegarder les cookies après login
 */
async function saveCookies(context) {
  const cookies = await context.cookies();
  fs.writeFileSync(CONFIG.cookiesPath, JSON.stringify(cookies, null, 2));
  console.log('✓ Cookies sauvegardés');
}

/**
 * Login à Gmail
 */
async function login(email, password = null) {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();

  try {
    console.log('Navigation vers Gmail...');
    await page.goto('https://accounts.google.com/signin', { waitUntil: 'networkidle' });

    // Vérifier si déjà connecté
    if (page.url().includes('mail.google.com/mail')) {
      console.log('✓ Déjà connecté');
      await browser.close();
      return true;
    }

    // Login - Étape 1 : Email
    console.log('Étape 1 : Saisie de l\'email...');
    await page.waitForSelector('input[type="email"], input[name="identifier"]', { timeout: 10000 });
    await page.fill('input[type="email"], input[name="identifier"]', email);

    // Cliquer sur le bouton Suivant avec différents sélecteurs possibles
    const nextButton = page.locator('#identifierNext, [role="button"]:has-text("Suivant"), button:has-text("Next"), button:has-text("Suivant")').first();
    await nextButton.click();
    await page.waitForTimeout(2000);

    // Étape 2 : Mot de passe
    if (password) {
      console.log('Étape 2 : Saisie du mot de passe...');
      await page.waitForSelector('input[type="password"], input[name="Passwd"]', { timeout: 10000 });
      await page.fill('input[type="password"], input[name="Passwd"]', password);

      const passwordNextButton = page.locator('#passwordNext, [role="button"]:has-text("Suivant"), button:has-text("Next"), button:has-text("Suivant")').first();
      await passwordNextButton.click();
    } else {
      console.log('Mot de passe requis - veuillez compléter manuellement');
      console.log('⚠️  Mode headless désactivé pour 2FA si nécessaire');
      await browser.close();
      // Recommencer en mode non-headless
      return await loginInteractive(email, password);
    }

    // Attendre la redirection vers Gmail
    console.log('Attente de la redirection vers Gmail...');
    try {
      await page.waitForURL('**/mail.google.com/**', { timeout: 30000 });
      console.log('✓ Connexion réussie');

      // Sauvegarder les cookies
      await saveCookies(context);

      await browser.close();
      return true;
    } catch (redirectError) {
      // Peut-être une 2FA ou une autre vérification
      console.log('⚠️  Vérification supplémentaire requise (2FA ?)');
      console.log('✗ Erreur de connexion:', redirectError.message);
      await browser.close();
      throw redirectError;
    }
  } catch (error) {
    console.error('✗ Erreur de connexion:', error.message);
    await browser.close();
    throw error;
  }
}

/**
 * Login interactif (pour 2FA)
 */
async function loginInteractive(email, password = null) {
  const browser = await chromium.launch({
    headless: false,
    executablePath: '/snap/bin/chromium',
    args: ['--no-sandbox']
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await page.goto('https://accounts.google.com/signin');
    await page.fill('input[type="email"]', email);
    await page.click('identifierNext');

    if (password) {
      await page.waitForSelector('input[type="password"]', { timeout: 10000 });
      await page.fill('input[type="password"]', password);
      await page.click('passwordNext');
    }

    // Attendre que l'utilisateur complète la 2FA
    console.log('⏳ Attente de la connexion (complétez la 2FA dans le navigateur)...');
    await page.waitForURL('https://mail.google.com/mail*', { timeout: 120000 });
    console.log('✓ Connexion réussie');

    await saveCookies(context);

    await browser.close();
    return true;
  } catch (error) {
    console.error('✗ Erreur:', error.message);
    await browser.close();
    throw error;
  }
}

/**
 * Lire la boîte de réception
 */
async function readInbox(limit = 10) {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();

  try {
    console.log('Ouverture de Gmail...');
    await page.goto('https://mail.google.com/mail/u/0/#inbox', { waitUntil: 'networkidle' });

    // Attendre que les mails chargent
    await page.waitForSelector('table[role="grid"]', { timeout: 10000 });

    // Extraire les emails
    const emails = await page.evaluate((limit) => {
      const rows = document.querySelectorAll('table[role="grid"] tr');
      const results = [];

      for (let i = 0; i < Math.min(rows.length, limit); i++) {
        const row = rows[i];
        const subjectEl = row.querySelector('.bog');
        const senderEl = row.querySelector('.go');
        const dateEl = row.querySelector('.yW');

        if (subjectEl) {
          results.push({
            subject: subjectEl.textContent?.trim(),
            sender: senderEl?.textContent?.trim(),
            date: dateEl?.textContent?.trim(),
            id: i,
          });
        }
      }

      return results;
    }, limit);

    console.log(`✓ ${emails.length} emails lus`);
    await browser.close();
    return emails;
  } catch (error) {
    console.error('✗ Erreur:', error.message);
    await browser.close();
    throw error;
  }
}

/**
 * Vérifier les nouveaux emails (non-lus)
 */
async function checkNewEmails() {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();

  try {
    await page.goto('https://mail.google.com/mail/u/0/#inbox', { waitUntil: 'networkidle' });
    await page.waitForSelector('table[role="grid"]', { timeout: 10000 });

    const unreadCount = await page.evaluate(() => {
      const unreadBadge = document.querySelector('.bs .nZ');
      return unreadBadge ? parseInt(unreadBadge.textContent) : 0;
    });

    console.log(`✓ ${unreadCount} emails non-lus`);

    const unreadEmails = await page.evaluate(() => {
      const rows = document.querySelectorAll('table[role="grid"] tr');
      const results = [];

      rows.forEach((row, i) => {
        if (row.querySelector('.zA.zE')) {
          const subjectEl = row.querySelector('.bog');
          const senderEl = row.querySelector('.go');

          if (subjectEl) {
            results.push({
              subject: subjectEl.textContent?.trim(),
              sender: senderEl?.textContent?.trim(),
              id: i,
            });
          }
        }
      });

      return results;
    });

    await browser.close();
    return { unreadCount, unreadEmails };
  } catch (error) {
    console.error('✗ Erreur:', error.message);
    await browser.close();
    throw error;
  }
}

/**
 * Main
 */
async function main() {
  const args = process.argv.slice(2);
  const action = args[0];

  switch (action) {
    case 'login':
      await login(args[1], args[2]);
      break;
    case 'inbox':
      const emails = await readInbox(parseInt(args[1]) || 10);
      console.log(JSON.stringify(emails, null, 2));
      break;
    case 'check':
      const { unreadCount, unreadEmails } = await checkNewEmails();
      console.log(`Non-lus: ${unreadCount}`);
      console.log(JSON.stringify(unreadEmails, null, 2));
      break;
    default:
      console.log('Usage: node gmail-helper.js <action> [args]');
      console.log('Actions: login <email> [password], inbox [limit], check');
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { login, readInbox, checkNewEmails };
