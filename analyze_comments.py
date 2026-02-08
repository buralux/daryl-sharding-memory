#!/usr/bin/env python3
import requests
import json
from bs4 import BeautifulSoup
import sys

# Posts performants à analyser
TARGET_POSTS = {
    "e019f586-b97e-4b57-b83e-a41a489762a7": "Three Layers of Agent Architecture",
    "e48201ea-6531-48c1-9ceb-82e50a1d95a1": "Duplication Shield",
    "9833bf4c-c70d-4f39-8ab0-db4d8d495d4d": "Four Layers of Reputation Systems",
    "26a31f04-8b90-41b8-ad76-1c3d3b5f99c1": "Three Layers of Agent Validation",
    "17d16526-5b0f-4b85-ad6d-8d14cd45418b": "The Stateless Trap"
}

def get_post_comments(post_id):
    """Récupère les commentaires d'un post Moltbook"""
    url = f"https://www.moltbook.com/post/{post_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour {post_id}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Chercher les commentaires dans la page HTML
        comments = []
        comment_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            word in str(x).lower() for word in ['comment', 'reply', 'message']
        ))

        # Alternative: chercher les scripts JSON-LD ou embedded data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'comments' in script.string.lower():
                try:
                    data = json.loads(script.string)
                    if 'comments' in data:
                        comments.extend(data['comments'])
                except:
                    pass

        return {
            'post_id': post_id,
            'url': url,
            'comments_count': len(comments),
            'comments': comments
        }

    except Exception as e:
        print(f"Erreur pour {post_id}: {e}")
        return None

def main():
    print("📊 Analyse des commentaires sur les posts performants\n")

    for post_id, title in TARGET_POSTS.items():
        print(f"🔍 Analyse: {title}")
        print(f"   ID: {post_id}")

        result = get_post_comments(post_id)
        if result:
            print(f"   ✅ Commentaires trouvés: {result['comments_count']}")
            # Afficher les 3 premiers commentaires si disponibles
            for i, comment in enumerate(result['comments'][:3]):
                print(f"      {i+1}. {str(comment)[:100]}...")
        else:
            print("   ❌ Pas de commentaires accessibles")

        print()

if __name__ == '__main__':
    main()
