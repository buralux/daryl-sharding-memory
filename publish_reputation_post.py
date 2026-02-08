#!/usr/bin/env python3
"""
Moltbook Publisher - The Four Layers of Reputation Systems
Publishes the reputation systems post to Moltbook.
"""

import json
import subprocess

# Configuration
API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
API_URL = "https://www.moltbook.com/api/v1/posts"
POST_FILE = "/home/buraluxtr/clawd/moltbook_post_reputation_portability.json"

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

    print(f"📝 Publishing post: {post_data['title']}")
    print(f"📂 Submolt: {post_data['submolt']}")
    print(f"📊 Content length: {len(post_data['content'])} characters\n")

    cmd = [
        "curl", "-s", "-X", "POST", API_URL,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ SUCCESS: Post published!")
            if "id" in response:
                print(f"🆔 Post ID: {response['id']}")
            if "url" in response:
                print(f"🔗 URL: {response['url']}")
            print(f"📄 Full response: {json.dumps(response, indent=2)}")
            return True
        else:
            print(f"❌ FAILED: curl failed with code {result.returncode}")
            print(f"📄 stdout: {result.stdout}")
            print(f"📄 stderr: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ FAILED: Request timeout after 30 seconds")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON response: {str(e)}")
        print(f"📄 Response: {result.stdout}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Moltbook Reputation Post Publisher ===\n")
    success = publish_post()
    print(f"\n{'='*50}")
    if success:
        print("✅ Post successfully published to Moltbook!")
    else:
        print("❌ Failed to publish post. Check error messages above.")
