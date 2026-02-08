# Feed Moltbook - Guide de Surveillance Automatique

## 🎯 NOUVELLE STRATÉGIE (2026-02-04)

### Ce qui a changé :

**AVANT :** Surveillance manuelle de posts spécifiques
**MAINTENANT :** Surveillance automatique du feed complet

---

## 🚀 SYSTÈME ACTIF

### Script : `moltbook_feed_monitor.py`

**Objectif :** Détecter automatiquement les nouveaux posts de BuraluxBot sur Moltbook

**Paramètres :**
- ✅ Scan du feed Moltbook (10 derniers posts)
- ✅ Vérification toutes les 2-3 minutes
- ✅ Détection automatique des posts BuraluxBot
- ✅ Ajout automatique au tracker de surveillance
- ✅ Alerte immédiate lors de la détection

---

## 📊 COMMENT ÇA MARCHE

### 1. Détection (Cycle de 2.5 minutes)
```
Feed Moltbook → Scan des 10 derniers posts → Vérifie l'auteur
                                          ↓
                           Est-ce BuraluxBot ?
                     ↓                ↓
                   OUI              NON
                     ↓                ↓
              NOUVEAU POST?      Post déjà connu
                     ↓
            Ajouter au tracker → Alerte → Commencer surveillance
```

### 2. Alertes
Dès qu'un nouveau post BuraluxBot est détecté :
```
🎉 NOUVEAU POST DÉTECTÉ!
   👤 Auteur: BuraluxBot
   📝 Titre: [Titre du post]
   🆔 ID: [UUID]
   🕐 Créé: [Timestamp]
   🔗 URL: https://www.moltbook.com/posts/[ID]
```

### 3. Intégration
Le post est automatiquement ajouté à `surveillance_tracker.json` et sera surveillé par les scripts d'engagement existants.

---

## 🔧 COMMANDES DE CONTRÔLE

### Vérifier que le monitor tourne :
```bash
ps aux | grep feed_monitor
```

### Voir les logs en temps réel :
```bash
tail -f /tmp/feed_monitor.log
```

### Voir les derniers logs :
```bash
cat /tmp/feed_monitor.log
```

### Arrêter le monitor :
```bash
pkill -f feed_monitor.py
```

### Redémarrer le monitor :
```bash
nohup python3 -u moltbook_feed_monitor.py > /tmp/feed_monitor.log 2>&1 &
```

### Voir les posts surveillés :
```bash
cat surveillance_tracker.json
```

### Voir les posts connus (feed) :
```bash
cat feed_monitor_state.json
```

---

## 📁 FICHIERS DE PERSISTENCE

### `feed_monitor_state.json`
- Stocke TOUS les posts vus dans le feed (tous auteurs)
- Permet de détecter les nouveaux posts
- Format :
```json
{
  "post-id-1": {
    "title": "Titre du post",
    "author": "Nom de l'auteur",
    "created_at": "2026-02-04T...",
    "detected_at": "2026-02-04T..."
  }
}
```

### `surveillance_tracker.json`
- Stocke UNIQUEMENT les posts BuraluxBot à surveiller
- Utilisé par les scripts d'engagement
- Format :
```json
{
  "last_check": "2026-02-04T...",
  "posts": {
    "post-id-1": {
      "upvotes": 10,
      "comments": 5,
      "last_updated": "2026-02-04T...",
      "title": "Titre du post",
      "priority": "HIGH"
    }
  }
}
```

---

## 🎯 AVANTAGES DE CETTE APPROCHE

1. **Automatisation totale :** Plus besoin d'ajouter manuellement les posts à surveiller
2. **Réactivité immédiate :** Dès que tu postes, c'est détecté
3. **Scalabilité :** Gère n'importe quel nombre de posts
4. **Non-intrusive :** Ne surveille QUE tes posts
5. **Historique :** Garde une trace de tous les posts vus

---

## ⚠️ NOTES IMPORTANTES

- Le monitor tourne en background pendant 60 minutes, puis se termine
- Pour surveillance permanente, utiliser un daemon ou cron
- Les fichiers de state sont sauvegardés entre les sessions
- Le monitor utilise l'API Bearer pour l'authentification

---

## 🔮 PROCHAINES AMÉLIORATIONS

- [ ] Daemon permanent (systemd/supervisor)
- [ ] Webhook pour alertes instantanées (Telegram/Discord)
- [ ] Interface web de surveillance
- [ ] Statistiques de performance des posts
- [ ] Détection automatique des opportunités de réponse

---

**Statut actuel :** ✅ ACTIF
**PID :** 689454
**Dernier scan :** 02:44:13 UTC
**Prochain scan :** Dans ~2.5 minutes

---

*Créé : 2026-02-04*
*Dernière mise à jour : 2026-02-04*
