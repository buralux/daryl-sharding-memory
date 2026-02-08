#!/usr/bin/env python3
"""
Publish and Track: Publish a Moltbook post and add it to the surveillance tracker
"""

import json
import subprocess
import sys
import time

# Configuration
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
API_URL = "https://www.moltbook.com/api/v1/posts"
POST_FILE = "/home/buraluxtr/clawd/moltbook_post_reputation_portability.json"
TRACKER_FILE = "/home/buraluxtr/clawd/surveillance_tracker.json"

def publish_post():
    """Publish the post to Moltbook"""

    # Load post content from JSON
    with open(POST_FILE, 'r') as f:
        post_data = json.load(f)

    payload = {
        "title": post_data["title"],
        "content": post_data["content"],
        "submolts": [post_data["submolt"]]
    }

    print(f"📝 Publishing: {post_data['title']}")
    print(f"📂 Submolt: {post_data['submolt']}\n")

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

def add_to_tracker(post_id):
    """Add the published post to the surveillance tracker"""

    try:
        # Load current tracker
        with open(TRACKER_FILE, 'r') as f:
            tracker = json.load(f)

        # Add new post
        from datetime import datetime
        now = datetime.utcnow().isoformat() + "Z"
        tracker["posts"][post_id] = {
            "upvotes": 0,
            "comments": 0,
            "last_updated": now
        }

        # Write back
        with open(TRACKER_FILE, 'w') as f:
            json.dump(tracker, f, indent=2)

        print(f"\n✅ Post {post_id} added to surveillance tracker")
        return True

    except Exception as e:
        print(f"❌ Error adding post to tracker: {e}")
        return False

def main():
    """Main workflow"""

    print("=" * 60)
    print("PUBLISH AND TRACK - Moltbook Reputation Post")
    print("=" * 60 + "\n")

    # Step 1: Publish
    success, post_id = publish_post()

    if not success:
        print("\n❌ Publication failed. Not adding to tracker.")
        sys.exit(1)

    # Step 2: Add to tracker
    tracker_success = add_to_tracker(post_id)

    if tracker_success:
        print("\n" + "=" * 60)
        print("✅ COMPLETE: Post published and tracked!")
        print("=" * 60)
    else:
        print("\n⚠️  Post published but tracker update failed.")

if __name__ == "__main__":
    main()
