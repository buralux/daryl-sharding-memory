#!/usr/bin/env python3
import requests
import re
import json
import sys

# Posts performants à analyser
TARGET_POSTS = {
    "e019f586-b97e-4b57-b83e-a41a489762a7": "Three Layers of Agent Architecture",
    "e48201ea-6531-48c1-9ceb-82e50a1d95a1": "Duplication Shield",
    "9833bf4c-c70d-4f39-8ab0-db4d8d495d4d": "Four Layers of Reputation Systems",
    "26a31f04-8b90-41b8-ad76-1c3d3b5f99c1": "Three Layers of Agent Validation",
    "17d16526-5b0f-4b85-ad6d-8d14cd45418b": "The Stateless Trap"
}

def get_post_html(post_id):
    """Récupère le HTML d'un post Moltbook"""
    url = f"https://www.moltbook.com/post/{post_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        return response.text
    except Exception as e:
        print(f"Erreur pour {post_id}: {e}")
        return None

def extract_comments_data(html):
    """Extrait les données des commentaires du HTML"""
    # Chercher des données JSON dans les scripts
    json_pattern = r'<script[^>]*>([\s\S]*?)</script>'
    scripts = re.findall(json_pattern, html)

    for script in scripts:
        if 'comments' in script.lower() or 'comments_count' in script.lower():
            try:
                # Nettoyer et essayer de parser
                clean_script = script.strip()
                if clean_script.startswith('window.') or clean_script.startswith('self.'):
                    # Retirer les assignments JS
                    clean_script = re.sub(r'^window\.\w+\s*=\s*', '', clean_script)
                    clean_script = re.sub(r'^self\.\w+\s*=\s*', '', clean_script)
                    clean_script = re.sub(r';\s*$', '', clean_script)

                data = json.loads(clean_script)
                if data and (isinstance(data, dict) or isinstance(data, list)):
                    return data
            except:
                continue

    # Chercher des indices dans le HTML
    comment_count_match = re.search(r'comments["\':\s]+(\d+)', html, re.IGNORECASE)
    if comment_count_match:
        return {'comments_count': int(comment_count_match.group(1))}

    return None

def main():
    print("📊 Analyse des commentaires sur les posts performants\n")

    for post_id, title in TARGET_POSTS.items():
        print(f"🔍 {title}")
        print(f"   ID: {post_id}")

        html = get_post_html(post_id)
        if html:
            comments_data = extract_comments_data(html)

            if comments_data:
                print(f"   ✅ Données trouvées: {json.dumps(comments_data, indent=2)[:300]}...")
            else:
                print(f"   ⚠️ HTML reçu mais pas de données de commentaire extraites")
                # Vérifier si la page contient au moins le post
                if 'post' in html.lower() or title.lower() in html.lower():
                    print(f"   📄 Page chargée (contient le titre)")
                else:
                    print(f"   ❌ Page incorrecte")
        else:
            print("   ❌ Erreur lors du chargement de la page")

        print()

if __name__ == '__main__':
    main()
