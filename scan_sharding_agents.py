#!/usr/bin/env python3
import json
import sys
from collections import Counter

try:
    # Récupérer le feed
    response = json.load(sys.stdin)
    
    if 'posts' not in response:
        print('Erreur: Pas de posts dans la réponse')
        sys.exit(1)
    
    posts = response['posts']
    
    # Chercher des posts qui parlent de sharding
    sharding_keywords = ['shard', 'sharding', 'partition', 'distribute', 'memory', 'state', 'coordination', 'cross-shard', 'multiverse', 'blockchain', 'consensus', 'architecture', 'scalable']
    
    sharding_posts = []
    for p in posts:
        title = p.get('title', '').lower()
        content = p.get('content', '').lower()
        author = p.get('author', {})
        author_name = author.get('name', 'Unknown')
        author_karma = author.get('karma', 0)
        
        # Compter les mots-clés
        keyword_count = 0
        for kw in sharding_keywords:
            if kw in title or kw in content:
                keyword_count += 1
        
        # Ignorer BuraluxBot
        if author_name.lower() == 'buraluxbot' and keyword_count > 0:
            continue
        
        # Ajouter si on trouve des mots-clés
        if keyword_count > 0:
            sharding_posts.append({
                'id': p.get('id'),
                'title': p.get('title', 'Unknown'),
                'author': author_name,
                'author_karma': author_karma,
                'keyword_count': keyword_count,
                'upvotes': p.get('upvotes', 0),
                'comments': p.get('comments', 0),
                'url': f"https://www.moltbook.com/post/{p.get('id')}",
                'tags': p.get('tags', [])
            })
    
    # Trier par nombre de mots-clés (les plus pertinents)
    sharding_posts.sort(key=lambda x: x['keyword_count'], reverse=True)
    
    print(f'📊 Feed scanné: {len(posts)} posts')
    print(f'🎯 Posts sur le sharding: {len(sharding_posts)}')
    print()
    print(f'Top 20 agents qui parlent de sharding:')
    for i, p in enumerate(sharding_posts[:20], 1):
        print(f'{i}. {p["author"]} ({p["author_karma"]}k) | {p["keyword_count"]} mots-clés sharding | ↑{p["upvotes"]} | 💬{p["comments"]}')
        print(f'   📝 {p["title"][:70]}...')
        print(f'   🔗 {p["url"]}')
        print()
    
    print(f'✅ Total agents trouvés: {len(sharding_posts)}')
    print(f'✅ Total BuraluxBot posts: {[p for p in posts if p.get("author", {}).get("name", "").lower() == "buraluxbot"]}')
    
except Exception as e:
    print(f'Erreur: {e}')
    sys.exit(1)
