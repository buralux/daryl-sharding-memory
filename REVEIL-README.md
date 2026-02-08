# 🌅 Système de Réveil Matinal - Configuration Complexe

## ✅ Ce qui est configuré

### Scripts créés
- **reveil-matin.sh** - Script simple qui appelle l'API
- **reveil-matin-daemon.sh** - Daemon en arrière-plan qui envoie le message automatiquement à 6h UTC

### Serveur API
- **api-server.js** - API REST sur http://localhost:3000
- Endpoint `/api/command` - Accepte `{"message": "..."}`
- Écrit dans `/home/buraluxtr/clawd/.trigger-message.txt`

### État actuel
- ✅ API server running (PID: 17223)
- ✅ Daemon running (PID: 17693)
- ✅ Créontab : Pas configurée (crontab pas installé)

## 🎯 Comment ça marche

### Option 1 : Daemon automatique (recommandé ✅)
Le daemon `/home/buraluxtr/clawd/reveille-matin-daemon.sh` tourne en arrière-plan et :
1. Vérifie l'heure toutes les 60 secondes
2. À 6h00 UTC, envoie le message via l'API
3. Crée un fichier `.trigger-message.txt` pour éviter doublons
4. Se réactive le lendemain

### Option 2 : Manuel
```bash
/home/buraluxtr/clawd/reveille-matin.sh
```

## 📋 Gestion

**Vérifier le daemon :**
```bash
ps aux | grep reveil-matin-daemon
```

**Voir les logs :**
```bash
tail -f /home/buraluxtr/clawd/reveille-matin-daemon.log
```

**Redémarrer le daemon :**
```bash
pkill -f reveil-matin-daemon
nohup /home/buraluxtr/clawd/reveille-matin-daemon.sh > /home/buraluxtr/clawd/reveille-matin-daemon.log 2>&1 &
```

**Arrêter le daemon :**
```bash
pkill -f reveil-matin-daemon
```

## ⚙️ Message personnalisé

Pour changer le message de réveil :
1. Ouvrir `/home/buraluxtr/clawd/reveille-matin-daemon.sh`
2. Modifier la variable `MESSAGE`
3. Redémarrer le daemon

## 📞 Support

Problèmes ? Contacter Clawdbot via Telegram.
