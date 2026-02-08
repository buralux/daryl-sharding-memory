#!/usr/bin/env python3
"""Check the structure of feed posts to see how to get the author"""

import subprocess
import json

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

cmd = ["curl", "-s", "--max-time", "5",
       "-H", f"Authorization: Bearer {API_KEY}",
       f"{BASE_URL}/feed?limit=3"]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

if result.stdout:
    try:
        response = json.loads(result.stdout)
        if response.get("success"):
            posts = response.get("posts", [])
            print(f"Nombre de posts: {len(posts)}")
            for post in posts:
                print(f"\n{'='*70}")
                print(f"ID: {post.get('id')}")
                print(f"Title: {post.get('title')[:50]}")
                print(f"Post keys: {list(post.keys())}")

                # Check different possible author fields
                if 'author' in post:
                    author = post.get('author')
                    print(f"Author field type: {type(author)}")
                    if isinstance(author, dict):
                        print(f"Author dict keys: {list(author.keys())}")
                        print(f"Author username: {author.get('username', 'NOT FOUND')}")
                        print(f"Author id: {author.get('id', 'NOT FOUND')}")
                    else:
                        print(f"Author value: {author}")

                if 'username' in post:
                    print(f"Username field: {post.get('username')}")

                if 'user_id' in post:
                    print(f"User ID: {post.get('user_id')}")

                print(f"Full post (first 500 chars): {str(post)[:500]}")
    except Exception as e:
        print(f"Error: {e}")
