#!/usr/bin/env node
/**
 * Helper pour Gmail via Playwright (headless)
 * Version 2 - Amélioré pour contourner la détection de bots
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  headless: true,
  viewport: { width: 1280, height: 800 },
  downloadPath: path.join(__dirname, 'downloads'),
  cookiesPath: path.join(__dirname, '.gmail-cookies-v2.json'),
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
    executablePath: '/snap/bin/chromium',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--disable-extensions',
      '--disable-infobars',
      '--disable-notifications',
    ],
  });

  const context = await browser.newContext({
    viewport: CONFIG.viewport,
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    storageState: fs.existsSync(CONFIG.cookiesPath) ? CONFIG.cookiesPath : undefined,
    locale: 'fr-FR',
    timezoneId: 'Europe/Paris',
    permissions: ['geolocation'],
  });

  // Masquer le fait que c'est un navigateur automatisé
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr', 'en-US', 'en'] });
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
    console.log('Navigation vers la page de connexion Google...');
    await page.goto('https://accounts.google.com/signin', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    // Vérifier si déjà connecté
    if (page.url().includes('mail.google.com/mail')) {
      console.log('✓ Déjà connecté');
      await browser.close();
      return true;
    }

    // Login - Étape 1 : Email
    console.log('Étape 1 : Saisie de l\'email...');
    try {
      await page.waitForSelector('input[type="email"], input[name="identifier"]', { timeout: 15000 });
    } catch (e) {
      // Maybe already on password page?
      const passwordInput = await page.$('input[type="password"]');
      if (passwordInput) {
        console.log('  Email déjà saisi');
      } else {
        throw e;
      }
    }

    const emailInput = await page.$('input[type="email"], input[name="identifier"]');
    if (emailInput && (await emailInput.inputValue()) === '') {
      await emailInput.fill(email);
      await page.waitForTimeout(1000);
    }

    // Cliquer sur Suivant - essayer plusieurs sélecteurs
    console.log('Clic sur "Suivant"...');
    const nextSelectors = ['#identifierNext', '[role="button"]:has-text("Suivant")', 'button:has-text("Next")', 'button:has-text("Suivant")', '[role="button"][type="submit"]'];
    let clicked = false;
    for (const selector of nextSelectors) {
      try {
        const btn = page.locator(selector).first();
        if (await btn.isVisible({ timeout: 1000 })) {
          await btn.click();
          clicked = true;
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (!clicked) {
      throw new Error('Impossible de trouver le bouton "Suivant"');
    }

    await page.waitForTimeout(3000);

    // Étape 2 : Mot de passe
    if (password) {
      console.log('Étape 2 : Saisie du mot de passe...');
      try {
        await page.waitForSelector('input[type="password"], input[name="Passwd"]', { timeout: 15000 });
        await page.fill('input[type="password"], input[name="Passwd"]', password);
        await page.waitForTimeout(1000);

        // Cliquer sur Suivant
        const passwordNextSelectors = ['#passwordNext', '[role="button"]:has-text("Suivant")', 'button:has-text("Next")', 'button:has-text("Suivant")', '[role="button"][type="submit"]'];
        for (const selector of passwordNextSelectors) {
          try {
            const btn = page.locator(selector).first();
            if (await btn.isVisible({ timeout: 1000 })) {
              await btn.click();
              break;
            }
          } catch (e) {
            // Continue
          }
        }
      } catch (e) {
        console.log('⚠️  Impossible de trouver le champ de mot de passe');
        console.log('   URL actuelle:', page.url());
        console.log('   Vérifications supplémentaires nécessaires ?');

        // Capture pour debug
        await page.screenshot({ path: path.join(CONFIG.downloadPath, 'debug-password-step.png'), fullPage: true });
        console.log('   Capture enregistrée:', path.join(CONFIG.downloadPath, 'debug-password-step.png'));

        await browser.close();
        throw e;
      }
    }

    // Attendre la redirection ou la vérification
    console.log('Attente de la redirection...');
    let waited = 0;
    const maxWait = 30000;
    while (waited < maxWait) {
      const url = page.url();
      if (url.includes('mail.google.com/mail')) {
        console.log('✓ Connexion réussie !');
        await saveCookies(context);
        await browser.close();
        return true;
      }

      if (url.includes('challenge') || url.includes('signin/v2/challenge')) {
        console.log('⚠️  Vérification 2FA requise');
        console.log('   L\'automatisation ne peut pas gérer la 2FA');
        await page.screenshot({ path: path.join(CONFIG.downloadPath, 'debug-2fa.png'), fullPage: true });
        await browser.close();
        throw new Error('2FA requise - veuillez vous connecter manuellement');
      }

      await page.waitForTimeout(1000);
      waited += 1000;
    }

    console.log('⚠️  Timeout - capture de la page actuelle...');
    await page.screenshot({ path: path.join(CONFIG.downloadPath, 'debug-timeout.png'), fullPage: true });
    console.log('   URL:', page.url());
    await browser.close();
    throw new Error('Timeout lors de la connexion');

  } catch (error) {
    console.error('✗ Erreur de connexion:', error.message);
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
    default:
      console.log('Usage: node gmail-helper-v2.js login <email> [password]');
      console.log('Note: Gmail peut demander une vérification 2FA');
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { login, launchBrowser };
