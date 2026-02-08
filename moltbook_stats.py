#!/usr/bin/env python3
import json
import sys
import datetime

# Lecture du JSON depuis stdin
data = json.load(sys.stdin)

# Parsing safe de la date
now = datetime.datetime.now(datetime.timezone.utc)
cutoff = now - datetime.timedelta(hours=24)

agent_keywords = ['agent', 'ai', 'agents', 'agentskills', 'consciousness', 'collaboration', 'coordinate', 'bot', 'trading', 'token', 'market', 'shellraiser', 'moltbook', 'solana', 'crypto', 'blockchain', 'web3']
discussion_keywords = ['?', '!', 'what', 'how', 'why', 'thoughts', 'opinion', 'debate', 'agree', 'disagreement']

# Métriques
metrics = {
    'total_posts_24h': 0,
    'agent_related_posts': 0,
    'discussion_related_posts': 0,
    'total_upvotes': 0,
    'total_comments': 0,
    'top_authors': {},
    'top_topics': {},
    'most_engaged_post': None
}

max_engagement = 0

for post in data.get('posts', []):
    created_at_str = post.get('created_at', '')
    title = post.get('title', '').lower()
    content = post.get('content', '').lower()
    
    # Parsing date (enlève Z si présent)
    created_at_str = created_at_str.replace('Z', '+00:00')
    try:
        created_at = datetime.datetime.fromisoformat(created_at_str)
    except:
        continue
    
    # Filtrer 24h
    if created_at < cutoff:
        continue
    
    metrics['total_posts_24h'] += 1
    
    # Upvotes/Comments
    upvotes = post.get('upvotes', 0)
    comments = post.get('comment_count', 0)
    
    metrics['total_upvotes'] += upvotes
    metrics['total_comments'] += comments
    
    # Identification type de post
    combined_text = f"{title} {content}"
    is_agent_discussion = any(kw in combined_text for kw in agent_keywords)
    is_general_discussion = any(kw in combined_text for kw in discussion_keywords)
    
    if is_agent_discussion:
        metrics['agent_related_posts'] += 1
    
    if is_general_discussion:
        metrics['discussion_related_posts'] += 1
    
    # Top Authours
    author = post.get('author', {}).get('name', 'Unknown')
    if author not in metrics['top_authors']:
        metrics['top_authors'][author] = {'posts': 0, 'upvotes': 0, 'comments': 0}
    
    metrics['top_authors'][author]['posts'] += 1
    metrics['top_authors'][author]['upvotes'] += upvotes
    metrics['top_authors'][author]['comments'] += comments
    
    # Top Topics
    for kw in agent_keywords:
        if kw in title:
            metrics['top_topics'][kw] = metrics['top_topics'].get(kw, 0) + 1
    
    # Most Engaged Post
    engagement = upvotes + (comments * 2)
    if engagement > max_engagement:
        max_engagement = engagement
        metrics['most_engaged_post'] = post

# Trier les auteurs
sorted_authors = sorted(metrics['top_authors'].items(), key=lambda x: x[1]['upvotes'], reverse=True)

# Trier les topics
sorted_topics = sorted(metrics['top_topics'].items(), key=lambda x: x[1], reverse=True)[:5]

# Afficher les statistiques
print('=== MOLTBOOK AGENT DISCUSSIONS - 24H STATS ===')
print(f"Time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total Posts (24h): {metrics['total_posts_24h']}")
print(f"Agent Related Posts: {metrics['agent_related_posts']}")
print(f"General Discussions: {metrics['discussion_related_posts']}")
print(f"Total Upvotes: {metrics['total_upvotes']}")
print(f"Total Comments: {metrics['total_comments']}")
print('')
print('--- TOP 5 AGENT COMMUNITIES (by Upvotes) ---')
for i, (author, stats) in enumerate(sorted_authors[:5]):
    print(f"{i+1}. {author}: {stats['posts']} posts, {stats['upvotes']} upvotes, {stats['comments']} comments")
print('')
print('--- TOP 5 DISCUSSION TOPICS ---')
for i, (topic, count) in enumerate(sorted_topics):
    print(f"{i+1}. {topic}: {count} mentions")
print('')
print('--- MOST ENGAGED POST ---')
most_engaged = metrics.get('most_engaged_post')
if most_engaged:
    print(f"Title: {most_engaged.get('title', 'N/A')[:60]}...")
    print(f"Author: {most_engaged.get('author', {}).get('name', 'N/A')}")
    print(f"Upvotes: {most_engaged.get('upvotes', 0)} | Comments: {most_engaged.get('comment_count', 0)}")
    print(f"URL: https://www.moltbook.com/post/{most_engaged.get('id', 'N/A')}")
else:
    print('No highly engaged post found.')
