#!/usr/bin/env node
/**
 * Script de débug pour Gmail
 * Permet de voir ce qui se passe pendant la connexion
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const debugDir = path.join(__dirname, 'debug');
if (!fs.existsSync(debugDir)) {
  fs.mkdirSync(debugDir, { recursive: true });
}

async function debugLogin(email, password) {
  // Lancer en mode non-headless pour voir ce qui se passe
  const browser = await chromium.launch({
    headless: false,
    executablePath: '/snap/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigation vers la page de connexion Google...');
    await page.goto('https://accounts.google.com/signin', { waitUntil: 'networkidle' });

    // Capture d'écran de la page initiale
    await page.screenshot({ path: path.join(debugDir, '1-initial.png'), fullPage: true });
    console.log('✓ Capture 1: Page initiale');

    // Remplir l'email
    console.log(`Saisie de l'email: ${email}`);
    await page.waitForSelector('input[type="email"], input[name="identifier"]', { timeout: 10000 });
    await page.fill('input[type="email"], input[name="identifier"]', email);
    await page.screenshot({ path: path.join(debugDir, '2-email-filled.png'), fullPage: true });
    console.log('✓ Capture 2: Email saisi');

    // Cliquer sur Suivant
    console.log('Clic sur "Suivant"...');
    const nextButton = page.locator('#identifierNext, [role="button"]:has-text("Suivant"), button:has-text("Next")').first();
    await nextButton.click();
    await page.waitForTimeout(3000);

    // Capture après clic sur Suivant
    await page.screenshot({ path: path.join(debugDir, '3-after-next.png'), fullPage: true });
    console.log('✓ Capture 3: Après clic Suivant');

    // Attendre et capturer la page actuelle
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(debugDir, '4-current-page.png'), fullPage: true });
    console.log('✓ Capture 4: Page actuelle');

    // Afficher l'URL actuelle
    console.log(`URL actuelle: ${page.url()}`);

    console.log('\n📸 Captures enregistrées dans:', debugDir);
    console.log('🔍 Veuillez examiner les captures pour comprendre le problème');
    console.log('⏳ Le navigateur reste ouvert pour inspection...');

    // Garder le navigateur ouvert
    console.log('\nAppuyez sur Ctrl+C dans ce terminal pour fermer le navigateur');
    await new Promise(() => {}); // Attendre indéfiniment

  } catch (error) {
    console.error('✗ Erreur:', error.message);
    await page.screenshot({ path: path.join(debugDir, 'error.png'), fullPage: true });
    await browser.close();
    throw error;
  }
}

const email = process.argv[2];
const password = process.argv[3];

if (!email) {
  console.log('Usage: node gmail-debug.js <email> [password]');
  process.exit(1);
}

debugLogin(email, password).catch(console.error);
