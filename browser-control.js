#!/usr/bin/env node
/**
 * Script de contrôle de navigateur autonome (Playwright)
 * Utilisation: node browser-control.js <url> [action]
 * Actions: open, screenshot, fill-form, download
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  headless: true,
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  downloadPath: path.join(__dirname, 'downloads'),
};

// Créer le dossier de téléchargement
if (!fs.existsSync(CONFIG.downloadPath)) {
  fs.mkdirSync(CONFIG.downloadPath, { recursive: true });
}

/**
 * Lancer le navigateur
 */
async function launchBrowser() {
  const browser = await chromium.launch({
    headless: CONFIG.headless,
    executablePath: '/snap/bin/chromium', // Utiliser Chromium Snap installé
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
    ],
  });

  const context = await browser.newContext({
    viewport: CONFIG.viewport,
    userAgent: CONFIG.userAgent,
    downloadBehavior: 'allow',
    acceptDownloads: true,
  });

  return { browser, context };
}

/**
 * Ouvrir une URL
 */
async function openUrl(url) {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();

  try {
    console.log(`Ouverture de: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle' });
    console.log('✓ Page chargée');

    const title = await page.title();
    console.log(`Titre: ${title}`);

    // Renvoyer le titre et l'URL pour vérification
    const result = {
      title,
      url: page.url(),
      screenshot: null,
    };

    // Prendre une capture d'écran
    const screenshotPath = path.join(CONFIG.downloadPath, `screenshot-${Date.now()}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    result.screenshot = screenshotPath;
    console.log(`✓ Capture: ${screenshotPath}`);

    await browser.close();
    return result;
  } catch (error) {
    console.error('✗ Erreur:', error.message);
    await browser.close();
    throw error;
  }
}

/**
 * Remplir un formulaire
 */
async function fillForm(url, fields) {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();

  try {
    console.log(`Ouverture de: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle' });

    console.log('Remplissage du formulaire...');
    for (const [selector, value] of Object.entries(fields)) {
      await page.waitForSelector(selector, { timeout: 5000 });
      await page.fill(selector, value);
      console.log(`  ✓ ${selector} = ${value}`);
    }

    await browser.close();
    return { success: true };
  } catch (error) {
    console.error('✗ Erreur:', error.message);
    await browser.close();
    throw error;
  }
}

/**
 * Télécharger un fichier
 */
async function downloadFile(url) {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();

  try {
    console.log(`Téléchargement depuis: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle' });

    // Configurer le téléchargement
    const downloadPromise = page.waitForEvent('download');

    // Cliquer sur le lien de téléchargement (à adapter selon la page)
    // Ici on cherche un bouton de téléchargement générique
    const downloadButton = await page.locator('a[download], button:has-text("télécharger"), button:has-text("download")').first();
    await downloadButton.click();

    const download = await downloadPromise;
    const filePath = path.join(CONFIG.downloadPath, download.suggestedFilename());
    await download.saveAs(filePath);

    console.log(`✓ Téléchargé: ${filePath}`);

    await browser.close();
    return { success: true, filePath };
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
  const url = args[0];
  const action = args[1] || 'open';

  if (!url) {
    console.log('Usage: node browser-control.js <url> [action]');
    console.log('Actions: open, screenshot, fill-form, download');
    process.exit(1);
  }

  switch (action) {
    case 'open':
    case 'screenshot':
      await openUrl(url);
      break;
    case 'fill-form':
      // Exemple: node browser-control.js https://example.com fill-form '{"#email":"test@example.com","#password":"pass"}'
      const fields = JSON.parse(args[2] || '{}');
      await fillForm(url, fields);
      break;
    case 'download':
      await downloadFile(url);
      break;
    default:
      console.log(`Action inconnue: ${action}`);
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { launchBrowser, openUrl, fillForm, downloadFile };
