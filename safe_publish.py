#!/usr/bin/env python3
"""
Safe Publish: Check for duplicates THEN publish
Complete workflow: check → publish → cache → track
"""

import json
import subprocess
import sys
from datetime import datetime

# Configuration
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
API_URL = "https://www.moltbook.com/api/v1/posts"
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

def check_duplicate(title):
    """Check if title is in the published posts cache"""

    print(f"🔍 Checking for duplicate: '{title}'")

    posts = load_published_posts()

    for post in posts["posts"]:
        if post["title"].lower() == title.lower():
            print(f"❌ DUPLICATE FOUND!")
            print(f"   Post ID: {post.get('post_id', 'N/A')}")
            print(f"   Published: {post.get('published_at', 'N/A')}")
            if post.get('post_id'):
                print(f"   URL: https://www.moltbook.com/post/{post['post_id']}")
            return True

    print(f"✅ No duplicate found ({len(posts['posts'])} posts cached)")
    return False

def publish_post(title, content, submolt):
    """Publish the post to Moltbook"""

    print(f"\n📝 Publishing: '{title}'")
    print(f"📂 Submolt: {submolt}")

    payload = {
        "title": title,
        "content": content,
        "submolts": [submolt]
    }

    cmd = [
        "curl", "-s", "-X", "POST", API_URL,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        response = json.loads(result.stdout)

        if response.get("success") and "post" in response:
            post_id = response["post"]["id"]
            print("✅ Post published successfully!")
            print(f"🆔 Post ID: {post_id}")
            print(f"🔗 URL: https://www.moltbook.com{response['post']['url']}")
            print(f"📊 Stats: {response['post']['upvotes']}↑ {response['post']['comment_count']}💬")
            return True, post_id
        else:
            print("❌ Failed to publish!")
            print(json.dumps(response, indent=2))
            return False, None

    except subprocess.TimeoutExpired:
        print("❌ Request timeout after 30 seconds")
        return False, None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def add_to_cache(title, post_id):
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

def add_to_tracker(post_id):
    """Add the published post to the surveillance tracker"""

    try:
        with open(TRACKER_FILE, 'r') as f:
            tracker = json.load(f)

        now = datetime.utcnow().isoformat() + "Z"
        tracker["posts"][post_id] = {
            "upvotes": 0,
            "comments": 0,
            "last_updated": now
        }

        with open(TRACKER_FILE, 'w') as f:
            json.dump(tracker, f, indent=2)

        print(f"✅ Added to tracker: {post_id}")

    except Exception as e:
        print(f"❌ Error adding to tracker: {e}")

def main():
    """Main safe publish workflow"""

    if len(sys.argv) < 4:
        print("Usage: python3 safe_publish.py '<TITLE>' '<CONTENT_FILE>' '<SUBMOLT>'")
        print("\nExample:")
        print("  python3 safe_publish.py 'My Post' /path/to/post.json general")
        sys.exit(1)

    title = sys.argv[1]
    content_file = sys.argv[2]
    submolt = sys.argv[3]

    print("=" * 60)
    print("SAFE PUBLISH - Complete Workflow")
    print("=" * 60 + "\n")

    # Step 1: Check for duplicates
    if check_duplicate(title):
        print("\n❌ BLOCKED: Post already published!")
        print("\nABORTING to avoid duplicate.")
        sys.exit(1)

    # Step 2: Load content
    try:
        with open(content_file, 'r') as f:
            post_data = json.load(f)
        content = post_data["content"]
        print(f"📄 Content loaded from: {content_file}")
    except Exception as e:
        print(f"❌ Error loading content: {e}")
        sys.exit(1)

    # Step 3: Publish
    success, post_id = publish_post(title, content, submolt)

    if not success:
        print("\n❌ Publication failed. Aborting.")
        sys.exit(1)

    # Step 4: Add to cache
    print()
    add_to_cache(title, post_id)

    # Step 5: Add to tracker
    add_to_tracker(post_id)

    print("\n" + "=" * 60)
    print("✅ COMPLETE: Post published, cached, and tracked!")
    print("=" * 60)

if __name__ == "__main__":
    main()
