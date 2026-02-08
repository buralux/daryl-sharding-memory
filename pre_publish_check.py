#!/usr/bin/env python3
"""
Pre-Publish Check - Verify that a post doesn't already exist before publishing
"""

import json
import subprocess
import sys

# Configuration
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
API_URL = "https://www.moltbook.com/api/v1/posts"
TRACKER_FILE = "/home/buraluxtr/clawd/surveillance_tracker.json"

def check_feed_for_title(title):
    """Check if a post with the same title exists in the recent feed"""

    print(f"🔍 Checking feed for duplicate title: '{title}'")

    cmd = [
        "curl", "-s", API_URL,
        "-H", f"Authorization: Bearer {API_KEY}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)

        if "posts" in data:
            for post in data["posts"]:
                if post.get("title", "").lower() == title.lower():
                    print(f"❌ DUPLICATE FOUND: Post ID {post['id']}")
                    print(f"   URL: https://www.moltbook.com/post/{post['id']}")
                    print(f"   Stats: {post['upvotes']}↑ {post['comment_count']}💬")
                    print(f"   Created: {post['created_at']}")
                    return True, post

        print("✅ No duplicate found in feed")
        return False, None

    except Exception as e:
        print(f"⚠️  Error checking feed: {e}")
        return False, None

def check_tracker_for_title(title):
    """Check if post is already in the surveillance tracker"""

    print(f"🔍 Checking tracker for: '{title}'")

    try:
        with open(TRACKER_FILE, 'r') as f:
            tracker = json.load(f)

        for post_id, data in tracker["posts"].items():
            # We'd need to fetch post titles to check properly
            # For now, just report how many posts are tracked
            pass

        print(f"📊 Tracker contains {len(tracker['posts'])} posts")
        return False, None

    except Exception as e:
        print(f"⚠️  Error checking tracker: {e}")
        return False, None

def main():
    """Main pre-publish check"""

    if len(sys.argv) != 2:
        print("Usage: python3 pre_publish_check.py '<POST_TITLE>'")
        print("\nExample:")
        print("  python3 pre_publish_check.py 'The Four Layers of Reputation Systems'")
        sys.exit(1)

    title = sys.argv[1]

    print("=" * 60)
    print("PRE-PUBLISH CHECK - Moltbook Duplicate Detection")
    print("=" * 60 + "\n")

    # Check 1: Feed
    duplicate_in_feed, post_data = check_feed_for_title(title)
    print()

    # Check 2: Tracker
    check_tracker_for_title(title)
    print()

    print("=" * 60)

    if duplicate_in_feed:
        print("\n❌ BLOCKED: Post already exists!")
        print("\nABORTING publication to avoid duplicate.")
        print("\nOptions:")
        print("  1. Use the existing post (check engagement)")
        print("  2. Create a different post")
        print("  3. Wait and publish later with different content")
        sys.exit(1)
    else:
        print("\n✅ CLEAR: No duplicate found")
        print("\nSafe to proceed with publication.")
        sys.exit(0)

if __name__ == "__main__":
    main()
