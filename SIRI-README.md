# 📱 Clawd API - Siri Integration Guide

## 🚀 Serveur API actif

- **IP publique**: `34.76.121.179`
- **Port**: `3000`
- **URL de base**: `http://34.76.121.179:3000`
- **Statut**: ✅ En cours d'exécution

## 📋 Endpoints disponibles

### Health Check
```
GET /health
```
Vérifier que le serveur est actif.

### Gmail - Lire les emails
```
GET /api/gmail/read?limit=10
```
Retourne les 10 derniers emails.

### Gmail - Vérifier les emails non-lus
```
GET /api/gmail/check
```
Retourne le nombre d'emails non-lus.

### Navigateur - Ouvrir une URL
```
POST /api/browser/open
Content-Type: application/json

{
  "url": "https://example.com"
}
```

### Navigateur - Capturer une page
```
POST /api/browser/screenshot
Content-Type: application/json

{
  "url": "https://example.com"
}
```

### Logs
```
GET /api/logs
```
Retourne les logs des actions.

## 🍎 Siri Shortcuts Examples

### Exemple 1: Vérifier les emails non-lus

1. Ouvre l'app **Raccourcis** sur iOS
2. Crée un nouveau raccourci "Vérifier mails"
3. Ajoute l'action: **Obtenir le contenu de l'URL**
   - URL: `http://34.76.121.179:3000/api/gmail/check`
4. Ajoute l'action: **Obtenir la valeur du dictionnaire**
   - Clé: `unreadCount`
5. Ajoute l'action: **Parler le texte**
   - Texte: `Vous avez  non-lus.`

Dis: "Hey Siri, vérifier mes mails"

### Exemple 2: Lire les 5 derniers emails

1. Crée un nouveau raccourci "Lire emails"
2. Ajoute l'action: **Obtenir le contenu de l'URL**
   - URL: `http://34.76.121.179:3000/api/gmail/read?limit=5`
3. Ajoute l'action: **Obtenir la valeur du dictionnaire**
   - Clé: `emails`
4. Ajoute l'action: **Répéter avec chaque élément**
   - Dans: `emails`
   - Action: **Parler le texte**
     - Texte: `Email de  - `

Dis: "Hey Siri, lire mes emails"

### Exemple 3: Capturer une page web

1. Crée un nouveau raccourci "Capturer page"
2. Ajoute l'action: **Demander une entrée**
   - Invite: "Quelle URL capturer ?"
   - Stocker dans: `url`
3. Ajoute l'action: **Obtenir le contenu de l'URL**
   - URL: `http://34.76.121.179:3000/api/browser/screenshot`
   - Méthode: POST
   - En-têtes: `Content-Type: application/json`
   - Corps: `{"url": "url"}`
4. Ajoute l'action: **Afficher l'alerte**
   - Titre: "Capture effectuée"

Dis: "Hey Siri, capturer page"

## 🔧 Gestion du serveur

Démarrer le serveur:
```bash
/home/buraluxtr/clawd/start-api.sh
```

Vérifier les logs:
```bash
tail -f /home/buraluxtr/clawd/api-server.log
```

Arrêter le serveur:
```bash
pkill -f "node api-server.js"
```

## ⚠️ Notes importantes

1. **Sécurité**: Ce serveur est accessible publiquement sur l'IP de la VM.
   - Pour une utilisation en production, ajoutez de l'authentification
   - Utilisez HTTPS si possible

2. **Performance**: Les requêtes sont limitées pour éviter la surcharge.

3. **Gmail**: Gmail doit être configuré d'abord avec OAuth2 (voir `gmail-api.js`).

## 📞 Support

Pour plus d'actions ou des problèmes, contactez Clawd via Telegram.
