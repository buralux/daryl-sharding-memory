#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Surveillance du feed Moltbook pour détecter automatiquement les nouveaux posts de BuraluxBot
et commencer leur surveillance immédiate.

HOTFIX V1.1: Tracker Resilient Load + Atomic Save + Corrupt Backup

✅ Fixes appliqués :
- Load resilient (fallback sur {} si JSON corrompu)
- Atomic save (écriture temporaire + rename atomique)
- Corrupt backup (backup + tentative de repair)
- Reboot automatique du tracker si < 10 posts (bootstrap depuis le scan)
"""

import json
import subprocess
import time
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import signal
import shutil

# Configuration
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"
TARGET_USER = "BuraluxBot"

# Fichiers de persistance
STATE_FILE = "feed_monitor_state.json"
TRACKER_FILE = "surveillance_tracker.json"

# Configuration du bootstrap tracker
TRACKER_VERSION = "1.1.0"  # Version du tracker
TRACKER_BOOTSTRAP_THRESHOLD = 10  # Reboot si < X posts
TRACKER_LAST_SCAN_FILE = "tracker_last_scan.json"  # Stocker le dernier scan
TRACKER_BOOTSTRAP_MODE = False  # Mode de bootstrap (si le tracker est corrompu)

# État pour détecter les nouveaux posts
known_posts = {}
last_check_time = None

def signal_handler(signum, frame):
    """Handler pour arrêt gracieux"""
    print(f"\n🛑 Arrêt du Feed Monitor (Signal {signum})")
    save_state()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# =============================================================================
# HOTFIX V1.1: Tracker Resilient Load + Atomic Save + Corrupt Backup
# =============================================================================

def load_json_resilient(path: str, default=None):
    """
    Charge un fichier JSON de manière résiliente
    
    Args:
        path: Chemin du fichier
        default: Valeur par défaut si fichier inexistant
        
    Returns:
        Données JSON ou la valeur par défaut
    """
    p = Path(path)
    if not p.exists():
        print(f"📂 Fichier inexistant: {path}")
        return default
    
    try:
        with p.open('r', encoding='utf-8', errors='replace') as f:
            raw = f.read().strip()
            if not raw:
                return default
            
            return json.loads(raw)
    except Exception as e:
        print(f"❌ Erreur chargement {path}: {e}")
        
        # Backup du fichier corrompu
        try:
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup = p.with_suffix(f".corrupt.{ts}")
            shutil.copy2(p, backup)
            print(f"💾 Backup créé: {backup}")
        except Exception as be:
            print(f"⚠️ Erreur création backup: {be}")
        
        # Tentative de repair
        try:
            cut_positions = [raw.rfind('}'), raw.rfind(']')]
            cut = max(cut_positions)
            if cut > 0:
                candidate = raw[:cut+1]
                try:
                    repaired = json.loads(candidate)
                    with p.open('w', encoding='utf-8') as f:
                        f.write(json.dumps(repaired, indent=2, ensure_ascii=False))
                    print(f"🔧 Repair réussi: {path}")
                    return repaired
                except Exception as re:
                    print(f"⚠️ Repair échoué: {re}")
        except Exception as re:
            pass
        
        # Fallback sur la valeur par défaut
        print(f"⚠️ Fallback sur la valeur par défaut")
        return default

def save_json_atomic(path: str, data):
    """
    Sauvegarde un fichier JSON de manière atomique (évite la corruption)
    
    Args:
        path: Chemin du fichier
        data: Données JSON à sauvegarder
    """
    p = Path(path)
    
    # Créer le répertoire parent si nécessaire
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Écrire dans un fichier temporaire
    tmp = p.with_suffix(f".tmp.{os.getpid()}")
    try:
        with tmp.open('w', encoding='utf-8') as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Remplacer atomiquement
        tmp.replace(p)
        # print(f"💾 Atomic save: {path}")
    except Exception as e:
        print(f"❌ Erreur atomic save: {e}")

def load_tracker():
    """
    Charge le tracker de surveillance avec résilience
    """
    global TRACKER_BOOTSTRAP_MODE
    
    tracker = load_json_resilient(TRACKER_FILE, default={
        "posts": {},
        "alerts": [],
        "stats": {
            "total_posts": 0,
            "total_comments": 0,
            "high_karma_opportunities": 0
        },
        "metadata": {
            "version": TRACKER_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    })
    
    # Vérifier si le tracker est en mode bootstrap
    total_posts = tracker.get("stats", {}).get("total_posts", 0)
    if total_posts < TRACKER_BOOTSTRAP_THRESHOLD:
        TRACKER_BOOTSTRAP_MODE = True
        print(f"🔄 Tracker en mode BOOTSTRAP (posts: {total_posts})")
    else:
        TRACKER_BOOTSTRAP_MODE = False
    
    return tracker

def save_tracker(tracker):
    """
    Sauvegarde le tracker de manière atomique
    """
    # Mettre à jour le metadata
    tracker["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    tracker["metadata"]["bootstrap_mode"] = TRACKER_BOOTSTRAP_MODE
    
    save_json_atomic(TRACKER_FILE, tracker)

def bootstrap_tracker_from_feed():
    """
    Bootstrape le tracker depuis le dernier scan du feed
    """
    print("🔄 Bootstrap du tracker depuis le feed...")
    
    # Récupérer les 10 derniers posts du feed
    cmd = ["curl", "-s", "--max-time", "10",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/feed?limit=10"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout:
            response = json.loads(result.stdout)
            posts = response.get("posts", [])
            
            # Filtrer uniquement les posts de BuraluxBot
            buraluxbot_posts = [p for p in posts if p.get("author") == TARGET_USER]
            
            # Créer le tracker initialisé
            tracker = {
                "posts": {},
                "alerts": [],
                "stats": {
                    "total_posts": len(buraluxbot_posts),
                    "total_comments": 0,
                    "high_karma_opportunities": 0
                },
                "metadata": {
                    "version": TRACKER_VERSION,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "bootstrap_mode": True,
                    "bootstrapped_from": "feed"
                    "bootstrapped_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
            # Ajouter les posts au tracker
            for post in buraluxbot_posts:
                post_id = post.get("id")
                
                tracker["posts"][post_id] = {
                    "id": post_id,
                    "title": post.get("title", ""),
                    "author": post.get("author", ""),
                    "author_karma": post.get("author_karma", 0),
                    "timestamp": post.get("timestamp", ""),
                    "url": post.get("url", ""),
                    "upvotes": post.get("upvotes", 0),
                    "comments": post.get("comments", 0),
                    "submolt": post.get("submolt", ""),
                    "tags": post.get("tags", []),
                    "content_preview": post.get("content", "")[:200],
                    "surveillance": {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "monitored": True,
                        "comments_monitored": True,
                        "last_check": datetime.now(timezone.utc).isoformat(),
                        "comment_opportunities": []
                    }
                }
            
            # Sauvegarder le dernier scan
            last_scan = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "posts_count": len(buraluxbot_posts),
                "posts_ids": [p.get("id") for p in buraluxbot_posts]
            }
            
            with open(TRACKER_LAST_SCAN_FILE, 'w', encoding='utf-8') as f:
                f.write(json.dumps(last_scan, indent=2, ensure_ascii=False))
            
            save_tracker(tracker)
            print(f"✅ Tracker bootstrappé: {len(buraluxbot_posts)} posts")
            
            return tracker
        
    except Exception as e:
        print(f"❌ Erreur bootstrap: {e}")
        return {}

# =============================================================================
# FONCTIONS ORIGINALES (Modifiées pour utiliser le tracker hotfix)
# =============================================================================

def load_state():
    """Charge l'état de surveillance des posts connus"""
    global known_posts
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                known_posts = json.load(f)
        except:
            known_posts = {}
    else:
        known_posts = {}

def save_state():
    """Sauvegarde l'état de surveillance"""
    with open(STATE_FILE, 'w') as f:
        json.dump(known_posts, f, indent=2)

def fetch_feed(limit=10):
    """Récupère les derniers posts du feed"""
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/feed?limit={limit}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout:
        try:
            return json.loads(result.stdout)
        except:
            return {"posts": []}
    else:
        return {"posts": []}

def add_post_to_tracker(post, priority="HIGH"):
    """
    Ajoute un nouveau post au tracker de surveillance
    
    Args:
        post: Données du post
        priority: Priorité du post (HIGH/MEDIUM/LOW)
    """
    # Charger le tracker avec résilience
    tracker = load_tracker()
    
    post_id = post.get("id")
    title = post.get("title", "")
    
    # Ajouter le post
    tracker["posts"][post_id] = {
        "id": post_id,
        "title": title,
        "author": post.get("author", ""),
        "author_karma": post.get("author_karma", 0),
        "timestamp": post.get("timestamp", ""),
        "url": post.get("url", ""),
        "upvotes": post.get("upvotes", 0),
        "comments": post.get("comments", 0),
        "submolt": post.get("submolt", ""),
        "tags": post.get("tags", []),
        "content_preview": post.get("content", "")[:200],
        "surveillance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "monitored": True,
            "comments_monitored": True,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "comment_opportunities": []
        }
    }
    
    # Mettre à jour les stats
    tracker["stats"]["total_posts"] = len(tracker["posts"])
    
    # Sauvegarder de manière atomique
    save_tracker(tracker)
    
    print(f"✅ Post ajouté au tracker: {title} (ID: {post_id})")

def scan_feed_for_new_posts():
    """Scan le feed pour les nouveaux posts de BuraluxBot"""
    print(f"📡 Scan Feed: {datetime.now().strftime('%H:%M:%S')}")
    
    # Charger le tracker avec résilience
    tracker = load_tracker()
    
    # Récupérer le feed
    feed = fetch_feed(limit=10)
    posts = feed.get("posts", [])
    
    # Filtrer uniquement les posts de BuraluxBot
    buraluxbot_posts = [p for p in posts if p.get("author") == TARGET_USER]
    
    new_posts_count = 0
    for post in buraluxbot_posts:
        post_id = post.get("id")
        
        if post_id not in tracker["posts"]:
            # Nouveau post détecté
            add_post_to_tracker(post)
            new_posts_count += 1
            
            # Alert
            title = post.get("title", "")
            url = post.get("url", "")
            print(f"🚨 NOUVEAU POST: {title}")
            print(f"   URL: {url}")
            
            # Ajouter aux alertes
            tracker["alerts"].append({
                "type": "NEW_POST",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "title": title,
                "url": url
            })
    
    if new_posts_count > 0:
        # Sauvegarder le tracker (déjà fait dans add_post_to_tracker)
        tracker["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_tracker(tracker)

def monitor_comments_for_post(post_id):
    """Surveille les commentaires d'un post"""
    # Charger le tracker
    tracker = load_tracker()
    
    if post_id not in tracker["posts"]:
        print(f"⚠️ Post {post_id} introuvable dans le tracker")
        return
    
    # Récupérer les commentaires
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}/comments"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            response = json.loads(result.stdout)
            comments = response.get("comments", [])
            
            # Analyser les commentaires
            high_karma_targets = []
            for comment in comments:
                author_karma = comment.get("author_karma", 0)
                author_name = comment.get("author_name", "")
                content = comment.get("content", "")
                
                # Filtrer les high-karma targets (karma > 300k)
                if author_karma > 300000:
                    high_karma_targets.append({
                        "author": author_name,
                        "karma": author_karma,
                        "content": content[:100]
                    })
            
            # Mettre à jour les opportunities
            if high_karma_targets:
                tracker["posts"][post_id]["surveillance"]["comment_opportunities"] = high_karma_targets
                tracker["stats"]["high_karma_opportunities"] = len([t for p in tracker["posts"].values() for t in p.get("surveillance", {}).get("comment_opportunities", [])])
            
            # Sauvegarder le tracker
            save_tracker(tracker)
    except Exception as e:
        print(f"❌ Erreur récupération commentaires: {e}")

def main():
    """Point d'entrée principal"""
    print("🚀 FEED MONITOR ACTIF")
    print("="*70)
    print(f"🎯 Cible: {TARGET_USER}")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"📁 Tracker: {TRACKER_FILE}")
    print(f"⚡ Version: {TRACKER_VERSION} (Hotfix V1.1)")
    print("="*70)
    
    # Charger le tracker avec résilience
    tracker = load_tracker()
    
    print(f"\n📊 État du tracker:")
    print(f"   Posts: {len(tracker['posts'])}")
    print(f"   Alertes: {len(tracker['alerts'])}")
    print(f"   Mode: {'BOOTSTRAP' if TRACKER_BOOTSTRAP_MODE else 'NORMAL'}")
    print()
    
    # Boucle principale de surveillance
    scan_count = 0
    while True:
        try:
            scan_count += 1
            print(f"\n──────────────────────────────────────────────────────────────────────")
            print(f"CYCLE {scan_count} - {datetime.now().strftime('%H:%M:%S')}")
            print("──────────────────────────────────────────────────────────────────────")
            
            # Scan pour les nouveaux posts
            scan_feed_for_new_posts()
            
            print(f"📡 Feed scan: {len(tracker['posts'])} posts récupérés")
            print(f"⏰ Prochain scan dans 2 minutes...")
            
            # Attendre 2 minutes
            time.sleep(120)
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt utilisateur")
            save_state()
            break
        except Exception as e:
            print(f"❌ Erreur dans la boucle principale: {e}")
            time.sleep(60)  # Attendre 1 minute avant de réessayer

if __name__ == "__main__":
    main()
