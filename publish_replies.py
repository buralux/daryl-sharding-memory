#!/usr/bin/env python3
"""
Script pour publier des réponses Moltbook
Charge les fichiers JSON de réponses et les poste une par une
"""

import json
import subprocess
import time
import os

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

def post_reply(post_id, reply_to, content):
    """Poste un commentaire sur un post"""

    payload = {
        "content": content,
        "reply_to": reply_to
    }

    cmd = [
        "curl", "-s", "--max-time", "10",
        "-X", "POST",
        f"{BASE_URL}/posts/{post_id}/comments",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    if result.returncode == 0:
        try:
            response = json.loads(result.stdout)
            return response.get("success", False), response
        except:
            return False, {"error": "Invalid JSON response"}
    else:
        return False, {"error": result.stderr}

def load_replies(file_path):
    """Charge les réponses depuis un fichier JSON"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    if "replies" in data:
        # Si post_id est au niveau supérieur (sharding)
        if "post_id" in data:
            post_id = data["post_id"]
            for reply in data["replies"]:
                reply["post_id"] = post_id
        return data["replies"]
    else:
        # Format simple avec replies array direct
        return data

def main():
    print("="*70)
    print("🚀 PUBLICATION DES RÉPONSES MOLTBOOK")
    print("="*70)

    # Charger les réponses
    all_replies = []

    # Réponses Sharding
    if os.path.exists("moltbook_replies_sharding.json"):
        replies = load_replies("moltbook_replies_sharding.json")
        all_replies.extend(replies)
        print(f"\n✅ {len(replies)} réponses Sharding chargées")

    # Réponses High-karma
    if os.path.exists("moltbook_replies_high_karma.json"):
        replies = load_replies("moltbook_replies_high_karma.json")
        all_replies.extend(replies)
        print(f"✅ {len(replies)} réponses High-karma chargées")

    print(f"\n📊 Total réponses à publier: {len(all_replies)}")

    # Poster chaque réponse
    success_count = 0
    fail_count = 0

    for i, reply in enumerate(all_replies, 1):
        post_id = reply["post_id"]
        reply_to = reply["reply_to"]
        content = reply["content"]

        # Tronquer le contenu pour l'affichage
        content_preview = content[:80] + "..." if len(content) > 80 else content

        print(f"\n[{i}/{len(all_replies)}] Post → Post {post_id[:8]}...")
        print(f"   📝 {content_preview}")

        success, response = post_reply(post_id, reply_to, content)

        if success:
            success_count += 1
            print(f"   ✅ Réussi!")
        else:
            fail_count += 1
            print(f"   ❌ Échec: {response.get('error', 'Unknown error')}")

        # Délai entre chaque post
        if i < len(all_replies):
            delay = 5
            print(f"   ⏰ Attente {delay}s...")
            time.sleep(delay)

    # Résumé
    print("\n\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"✅ Succès: {success_count}")
    print(f"❌ Échecs: {fail_count}")
    print(f"📈 Taux de réussite: {100*success_count/len(all_replies):.1f}%")

if __name__ == "__main__":
    main()
