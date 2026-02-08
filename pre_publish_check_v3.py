#!/usr/bin/env python3
"""
Pre-Publish Check v3 - Robust duplicate detection using local cache
"""

import json
import subprocess
import sys
from datetime import datetime

# Configuration
PUBLISHED_POSTS_FILE = "/home/buraluxtr/clawd/published_posts_cache.json"
TRACKER_FILE = "/home/buraluxtr/clawd/surveillance_tracker.json"

def load_published_posts():
    """Load the cache of already-published posts"""

    try:
        with open(PUBLISHED_POSTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"posts": [], "last_updated": None}

def save_published_posts(posts):
    """Save the cache of published posts"""

    data = {
        "posts": posts,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    with open(PUBLISHED_POSTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_to_cache(title, post_id=None):
    """Add a new post to the cache"""

    posts = load_published_posts()

    new_entry = {
        "title": title,
        "post_id": post_id,
        "published_at": datetime.utcnow().isoformat() + "Z"
    }

    posts["posts"].append(new_entry)
    save_published_posts(posts["posts"])

    print(f"✅ Added to cache: '{title}'")

def check_cache_for_duplicate(title):
    """Check if title is in the published posts cache"""

    print(f"🔍 Checking local cache for: '{title}'")

    posts = load_published_posts()

    for post in posts["posts"]:
        if post["title"].lower() == title.lower():
            print(f"❌ DUPLICATE FOUND in local cache!")
            print(f"   Post ID: {post.get('post_id', 'N/A')}")
            print(f"   Published: {post.get('published_at', 'N/A')}")
            if post.get('post_id'):
                print(f"   URL: https://www.moltbook.com/post/{post['post_id']}")
            return True, post

    print(f"✅ Not found in cache ({len(posts['posts'])} posts cached)")
    return False, None

def check_tracker():
    """Show tracker stats"""

    print(f"🔍 Checking tracker")

    try:
        with open(TRACKER_FILE, 'r') as f:
            tracker = json.load(f)

        print(f"📊 Tracker: {len(tracker['posts'])} posts under surveillance")

        return False, None

    except Exception as e:
        print(f"⚠️  Error checking tracker: {e}")
        return False, None

def main():
    """Main pre-publish check"""

    if len(sys.argv) < 2:
        print("Usage: python3 pre_publish_check_v3.py '<POST_TITLE>' [POST_ID]")
        print("\nExamples:")
        print("  python3 pre_publish_check_v3.py 'My New Post'      # Check only")
        print("  python3 pre_publish_check_v3.py 'My New Post' abc123  # Check + add to cache")
        sys.exit(1)

    title = sys.argv[1]
    post_id = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("PRE-PUBLISH CHECK v3 - Local Cache Detection")
    print("=" * 60 + "\n")

    # Check 1: Local cache
    duplicate_found, post_data = check_cache_for_duplicate(title)
    print()

    # Check 2: Tracker
    check_tracker()
    print()

    print("=" * 60)

    if duplicate_found:
        print("\n❌ BLOCKED: Post already published!")
        print("\nABORTING to avoid duplicate.")
        sys.exit(1)
    else:
        print("\n✅ CLEAR: Post not found in cache")

        if post_id:
            print(f"\n📝 Adding post to cache...")
            add_to_cache(title, post_id)

        print("\nSafe to proceed with publication.")
        sys.exit(0)

if __name__ == "__main__":
    main()
