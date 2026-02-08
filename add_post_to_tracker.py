#!/usr/bin/env python3
"""
Add published post to surveillance tracker
"""

import json
import sys

TRACKER_FILE = "/home/buraluxtr/clawd/surveillance_tracker.json"

def add_post_to_tracker(post_id):
    """Add a new post to the surveillance tracker"""

    try:
        # Load current tracker
        with open(TRACKER_FILE, 'r') as f:
            tracker = json.load(f)

        # Add new post
        tracker["posts"][post_id] = {
            "upvotes": 0,
            "comments": 0,
            "last_updated": ""
        }

        # Write back
        with open(TRACKER_FILE, 'w') as f:
            json.dump(tracker, f, indent=2)

        print(f"✅ Post {post_id} added to surveillance tracker")
        return True

    except Exception as e:
        print(f"❌ Error adding post to tracker: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 add_post_to_tracker.py <POST_ID>")
        sys.exit(1)

    post_id = sys.argv[1]
    add_post_to_tracker(post_id)
