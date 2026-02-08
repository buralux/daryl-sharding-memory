#!/usr/bin/env python3
"""Test version of Moltbook engagement script"""

import json
import subprocess
import sys

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

def fetch_posts(submolt: str, limit: int = 5):
    cmd = ["curl", "-s", "-H", f"Authorization: Bearer {API_KEY}", f"{BASE_URL}/posts?submolt={submolt}&limit={limit}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get("success"):
            return response.get("posts", [])
    return []

def analyze_post_quality(post):
    if not post:
        return 0.0

    score = 0.0
    upvotes = post.get("upvotes", 0)
    comments = post.get("comment_count", 0)

    if 2 <= upvotes <= 15:
        score += 0.2
    elif upvotes >= 16:
        score += 0.1

    if 1 <= comments <= 20:
        score += 0.15

    content = post.get("content") or ""
    content_len = len(content)

    if 200 <= content_len <= 2000:
        score += 0.15
    elif content_len > 2000:
        score += 0.1

    title = post.get("title") or ""
    if "?" in title or len(title) > 20:
        score += 0.1

    content_lower = content.lower()
    question_words = ["?", "how", "what", "why", "thoughts", "opinion"]
    if any(qw in content_lower for qw in question_words):
        score += 0.15

    if "@" in content_lower or "#" in content_lower:
        score += 0.1

    return score

def main():
    print("=== Testing Moltbook Engagement ===")

    submolts = ["thinkingsystems", "meta", "skills"]

    all_posts = []
    for submolt in submolts:
        print(f"\nFetching {submolt}...")
        posts = fetch_posts(submolt, limit=5)
        print(f"  Found {len(posts)} posts")
        all_posts.extend(posts)

    print(f"\nTotal posts: {len(all_posts)}")

    print("\n=== Analyzing post quality ===")
    scored_posts = []
    for post in all_posts:
        score = analyze_post_quality(post)
        if score > 0.4:
            title = post.get("title", "No title")[:50]
            author = post.get("author", {}).get("name", "Unknown")
            upvotes = post.get("upvotes", 0)
            scored_posts.append((score, post))
            print(f"Score {score:.2f}: {title}... by {author} (↑{upvotes})")

    scored_posts.sort(key=lambda x: x[0], reverse=True)
    print(f"\nHigh quality posts found: {len(scored_posts)}")

    print("\n=== Testing upvote endpoint ===")
    if scored_posts:
        top_post = scored_posts[0][1]
        post_id = top_post.get("id")

        # Try upvote endpoints
        endpoints = [
            f"/posts/{post_id}/upvote",
            f"/posts/{post_id}/vote",
            f"/vote/post/{post_id}",
            f"/upvote/{post_id}"
        ]

        for endpoint in endpoints:
            print(f"Trying: {endpoint}")
            cmd = ["curl", "-s", "-X", "POST", "-H", f"Authorization: Bearer {API_KEY}",
                   f"{BASE_URL}{endpoint}", "-H", "Content-Type: application/json", "-d", "{}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    print(f"  Response: {response.get('success', False)}")
                    if response.get("success"):
                        print(f"  ✅ Upvote endpoint found: {endpoint}")
                        break
                except:
                    pass
            print(f"  Failed")

    print("\n=== Test complete ===")

if __name__ == "__main__":
    main()
