#!/usr/bin/env python3
"""Check posts by BuraluxBot to see the author name"""

import subprocess
import json

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

# Fetch more posts to find BuraluxBot
cmd = ["curl", "-s", "--max-time", "5",
       "-H", f"Authorization: Bearer {API_KEY}",
       f"{BASE_URL}/feed?limit=20"]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

if result.stdout:
    try:
        response = json.loads(result.stdout)
        if response.get("success"):
            posts = response.get("posts", [])
            print(f"Nombre de posts: {len(posts)}\n")

            for post in posts:
                author = post.get('author', {})
                author_name = author.get('name', 'Unknown')

                # Look for variations of Buralux
                if 'buralux' in author_name.lower():
                    print(f"\n{'='*70}")
                    print(f"Title: {post.get('title')[:60]}")
                    print(f"Author name: {author_name}")
                    print(f"Author id: {author.get('id')}")
                    print(f"Author description: {author.get('description', '')[:100]}")
                    print(f"Upvotes: {post.get('upvotes')}")
                    print(f"Comments: {post.get('comment_count')}")
    except Exception as e:
        print(f"Error: {e}")
