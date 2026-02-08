#!/usr/bin/env python3
"""Scan Moltbook posts by karma/engagement"""

import json
import subprocess
import datetime

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

def fetch_all_posts(limit: int = 50):
    """Fetch posts from general feed"""
    cmd = ["curl", "-s", "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts?limit={limit}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get("success"):
            return response.get("posts", [])
    return []

def fetch_post_comments(post_id: str):
    """Fetch comments for a post"""
    cmd = ["curl", "-s", "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}/comments"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get("success"):
            return response.get("comments", [])
    return []

def calculate_engagement_score(post):
    """Calculate engagement score (karma)"""
    upvotes = post.get("upvotes", 0)
    comments = post.get("comment_count", 0)

    # Engagement = upvotes + (comments * 2) - comments count more
    return upvotes + (comments * 2)

def main():
    print("=== SCANNING MOLTBOOK TOP POSTS ===\n")

    # Fetch posts
    print("Fetching posts...")
    posts = fetch_all_posts(limit=100)
    print(f"Found {len(posts)} posts\n")

    if not posts:
        print("No posts found!")
        return

    # Score and sort by engagement
    scored_posts = []
    for post in posts:
        score = calculate_engagement_score(post)
        if score > 0:  # Only include posts with some engagement
            scored_posts.append((score, post))

    # Sort by engagement score (highest first)
    scored_posts.sort(key=lambda x: x[0], reverse=True)

    # Display top 20
    print("=== TOP 20 POSTS BY KARMA (Upvotes + Comments×2) ===\n")

    for i, (score, post) in enumerate(scored_posts[:20]):
        title = post.get("title", "No title")
        author = post.get("author", {}).get("name", "Unknown")
        upvotes = post.get("upvotes", 0)
        comments = post.get("comment_count", 0)
        post_id = post.get("id", "N/A")

        print(f"{i+1:2d}. [{score:3d} karma] ↑{upvotes} 💬{comments}")
        print(f"    Title: {title[:80]}")
        print(f"    Author: {author}")
        print(f"    URL: https://www.moltbook.com/post/{post_id}")
        print()

    print(f"\n✅ Total posts scanned: {len(posts)}")
    print(f"✅ Posts with engagement: {len(scored_posts)}")

if __name__ == "__main__":
    main()
