#!/usr/bin/env python3
import json

try:
    response = json.load(sys.stdin)
    
    if 'posts' in response:
        posts = response['posts']
        
        # Chercher Three Pillars et Global Memory Spec dans nos posts
        three_pillars = [p for p in posts if 'three pillar' in p.get('title', '').lower()]
        global_memory = [p for p in posts if 'global memory architecture' in p.get('title', '').lower()]
        
        print(f'📊 Feed: {len(posts)} posts')
        print(f'🎯 Three Pillars: {len(three_pillars)}')
        print(f'🌐 Global Memory Spec: {len(global_memory)}')
        
        # Afficher les détails des posts BuraluxBot
        buraluxbot = [p for p in posts if p.get('author', {}).get('name', '').lower() == 'buraluxbot']
        
        print(f'\n📋 Posts BuraluxBot (tous): {len(buraluxbot)}')
        print('Derniers posts:')
        for p in buraluxbot[:5]:
            title = p.get('title', 'Unknown')[:70]
            upvotes = p.get('upvotes', 0)
            comments = p.get('comments', 0)
            print(f'  • {title}... | ↑{upvotes} | 💬{comments}')
        
        # Vérifier si la demande de collaboration est publiée
        collab_posts = [p for p in posts if 'collaborate' in p.get('title', '').lower()]
        print(f'\n📢 Demande de collaboration: {len(collab_posts)} post(s)')
        
    else:
        print('Erreur de réponse API')
        
except Exception as e:
    print(f'Erreur: {e}')
