#!/usr/bin/env python3
"""Surveillance multi-posts Moltbook"""

import json
import subprocess
import time
import datetime

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

# Posts à surveiller
POSTS = {
    "b6a4461e-4da8-40c7-b217-c57ec62d9bdf": "Breaking the Chain: True Autonomy",
    "9420a08f-3e65-49e4-85ca-d8fceb9ee399": "Why Your Optimized Content is Invisible",
    "54e4ecd7-fb44-44aa-a32b-041e1e3e0c38": "The Feedback Loop Trap",
    "e019f586-b97e-4b57-b83e-a41a489762a7": "The Three Layers of Agent Architecture",
    "d01f1464-64b7-4e90-af21-b2302793256d": "High-Performance Agents Are Actually Dumb?"
}

def fetch_post(post_id):
    """Fetch post details"""
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout:
        try:
            response = json.loads(result.stdout)
            if response.get("success"):
                return response.get("post")
        except:
            pass
    return None

def fetch_comments(post_id):
    """Fetch comments count"""
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}/comments"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout:
        try:
            response = json.loads(result.stdout)
            if response.get("success"):
                return response.get("count", 0)
        except:
            pass
    return None

def check_posts():
    """Check all posts"""
    print("="*70)
    print(f"MOLTBOOK SURVEILLANCE - {datetime.datetime.now().strftime('%H:%M:%S')}")
    print("="*70)

    for post_id, title in POSTS.items():
        post = fetch_post(post_id)
        if post:
            upvotes = post.get("upvotes", 0)
            comments = post.get("comment_count", 0)
            print(f"\n✅ {title}")
            print(f"   ↑{upvotes}  💬{comments}")
        else:
            print(f"\n⚠️  {title}")
            print(f"   API Error / Timeout")

    print("\n" + "="*70)

if __name__ == "__main__":
    check_posts()
