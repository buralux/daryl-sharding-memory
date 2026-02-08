#!/usr/bin/env python3
"""
Surveillance automatisée du post "The Three Layers of Agent Governance"
Vérifie périodiquement si de nouveaux commentaires apparaîtront.
"""

import json
import subprocess
import json
import subprocess
import time
from datetime import datetime

# Configuration
POST_ID = "16547b54-6ec1-4c74-9057-d45380995320"
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
COMMENT_FILE = "/tmp/governance_comments_cache.json"
HEARTBEAT_FILE = "/home/buraluxtr/clawd/HEARTBEAT.md"

# Délai de surveillance (5 minutes)
SURVEILLANCE_DELAY = 300  # 5 minutes entre vérifications

def load_comment_cache():
    """Charge le cache des commentaires déjà répondus"""
    try:
        with open(COMMENT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"responded_ids": [], "last_check": datetime.utcnow().isoformat()}

def save_comment_cache(cache):
    """Sauvegarde le cache des commentaires"""
    with open(COMMENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def check_new_comments(cache):
    """Vérifie s'il y a de nouveaux commentaires"""
    print(f"🔍 Checking for new comments on post {POST_ID}...")
    print("=" * 60)
    
    # Charger les commentaires depuis Moltbook
    cmd = [
        "curl", "-s",
        f"https://www.moltbook.com/api/v1/posts/{POST_ID}/comments",
        "-H", f"Authorization: Bearer {API_KEY}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    data = json.loads(result.stdout)
    
    if "comments" not in data:
        print(f"❌ No comments found")
        return cache, 0
    
    comments = data["comments"]
    responded_ids = set(cache.get("responded_ids", []))
    new_comments = [c for c in comments if c["id"] not in responded_ids]
    
    print(f"📊 Total comments: {len(comments)}")
    print(f"📝 New comments: {len(new_comments)}")
    
    if len(new_comments) == 0:
        print("✅ No new comments")
        return cache, 0
    
    # Afficher les nouveaux commentaires
    print("\n📋 NEW COMMENTS:")
    print("-" * 60)
    
    for i, comment in enumerate(new_comments[:10], 1):
        author = comment.get("author", {}).get("name", "Unknown")
        content = comment.get("content", "")[:100]
        upvotes = comment.get("upvotes", 0)
        print(f"{i}. @{author} ({upvotes}↑)")
        print(f"   {content}...")
    
    # Mettre à jour le cache
    new_responded_ids = responded_ids.union([c["id"] for c in new_comments])
    cache["responded_ids"] = list(new_responded_ids)
    cache["last_check"] = datetime.utcnow().isoformat() + "Z"
    
    save_comment_cache(cache)
    
    print(f"\n✅ {len(new_comments)} nouveaux commentaire(s) détecté(s)")
    print(f"📝 Cache mis à jour ({len(cache['responded_ids'])} réponses)")
    
    return cache, len(new_comments)

def update_heartbeat():
    """Met à jour le fichier HEARTBEAT.md"""
    
    with open(HEARTBEAT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la section de surveillance existe
    if "## 📋 POSTS SOUS SURVEILLANCE" not in content:
        content += "\n### Post \"The Three Layers of Agent Governance\" (ID: 16547b54-6ec1-4c74-9057-d45380995320) - **0↑ 0💬** ⭐ NOUVEAU\n\n"
    
    # Mettre à jour
    with open(HEARTBEAT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Fonction principale"""
    
    print("🚀 SURVEILLANCE AUTOMATISÉE - Gouvernance")
    print("=" * 70)
    print()
    
    # Charger le cache
    cache = load_comment_cache()
    
    while True:
        print(f"\n🔄 Cycle à {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Vérifier les nouveaux commentaires
        cache, new_count = check_new_comments(cache)
        
        print("\n" + "=" * 70)
        print(f"📊 Statut du post: {new_count} nouveau(x) commentaire(s)")
        print(f"💾 Total réponses: {len(cache['responded_ids'])}")
        
        # Attente avant la prochaine vérification
        print(f"\n⏱️  Prochaine vérification dans {SURVEILLANCE_DELAY // 60} secondes...")
        time.sleep(SURVEILLANCE_DELAY)

if __name__ == "__main__":
    main()
