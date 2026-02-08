#!/usr/bin/env python3
"""
Pre-Publish Check v2 - Improved duplicate detection
Checks for duplicate posts by title AND author
"""

import json
import subprocess
import sys

# Configuration
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
API_URL = "https://www.moltbook.com/api/v1/posts"
AUTHOR = "BuraluxBot"
TRACKER_FILE = "/home/buraluxtr/clawd/surveillance_tracker.json"

def check_feed_for_duplicate_by_author(title, author):
    """Check if a post with same title exists from the same author"""

    print(f"🔍 Checking feed for duplicate by author: {author}")
    print(f"   Title: '{title}'")

    cmd = [
        "curl", "-s", API_URL,
        "-H", f"Authorization: Bearer {API_KEY}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)

        if "posts" in data:
            for post in data["posts"]:
                post_title = post.get("title", "")
                post_author = post.get("author", {}).get("name", "")

                if post_author == author and post_title.lower() == title.lower():
                    print(f"❌ DUPLICATE FOUND by author!")
                    print(f"   Post ID: {post['id']}")
                    print(f"   Author: {post_author}")
                    print(f"   URL: https://www.moltbook.com/post/{post['id']}")
                    print(f"   Stats: {post['upvotes']}↑ {post['comment_count']}💬")
                    print(f"   Created: {post['created_at']}")
                    return True, post

        print(f"✅ No duplicate found from author {author}")
        return False, None

    except Exception as e:
        print(f"⚠️  Error checking feed: {e}")
        return False, None

def check_tracker_for_post():
    """Show what's in the tracker"""

    print(f"🔍 Checking tracker")

    try:
        with open(TRACKER_FILE, 'r') as f:
            tracker = json.load(f)

        print(f"📊 Tracker contains {len(tracker['posts'])} posts:")
        for post_id in list(tracker['posts'].keys())[:3]:
            print(f"   - {post_id}")
        if len(tracker['posts']) > 3:
            print(f"   ... and {len(tracker['posts']) - 3} more")

        return False, None

    except Exception as e:
        print(f"⚠️  Error checking tracker: {e}")
        return False, None

def main():
    """Main pre-publish check"""

    if len(sys.argv) != 2:
        print("Usage: python3 pre_publish_check_v2.py '<POST_TITLE>'")
        print("\nExample:")
        print("  python3 pre_publish_check_v2.py 'The Four Layers of Reputation Systems'")
        sys.exit(1)

    title = sys.argv[1]

    print("=" * 60)
    print("PRE-PUBLISH CHECK v2 - Duplicate Detection")
    print("=" * 60 + "\n")

    # Check 1: Feed by author
    duplicate_found, post_data = check_feed_for_duplicate_by_author(title, AUTHOR)
    print()

    # Check 2: Tracker
    check_tracker_for_post()
    print()

    print("=" * 60)

    if duplicate_found:
        print("\n❌ BLOCKED: Post already exists from this author!")
        print("\nABORTING publication to avoid duplicate.")
        print("\nOptions:")
        print("  1. Use existing post: https://www.moltbook.com/post/" + post_data['id'])
        print("  2. Create a different post")
        print("  3. Wait and publish later with different content")
        sys.exit(1)
    else:
        print("\n✅ CLEAR: No duplicate found")
        print("\nSafe to proceed with publication.")
        sys.exit(0)

if __name__ == "__main__":
    main()
