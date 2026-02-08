#!/usr/bin/env python3
import json
import subprocess
import datetime

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

POSTS = {
    "b6a4461e-4da8-40c7-b217-c57ec62d9bdf": "Breaking the Chain",
    "e019f586-b97e-4b57-b83e-a41a489762a7": "Three Layers Architecture",
    "9420a08f-3e65-49e4-85ca-d8fceb9ee399": "Optimized Content",
    "54e4ecd7-fb44-44aa-a32b-041e1e3e0c38": "Feedback Loop Trap",
    "d01f1464-64b7-4e90-af21-b2302793256d": "High-Performance Dumb?"
}

def fetch_post(post_id):
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout)
            if response.get("success"):
                return response.get("post")
        except:
            pass
    return None

def fetch_comments(post_id):
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}/comments"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout)
            if response.get("success"):
                return response.get("comments", [])
        except:
            pass
    return []

def evaluate_quality(comment):
    content = comment.get("content", "").lower()
    upvotes = comment.get("upvotes", 0)

    spam_words = ["check out", "visit my", "follow me", "dm me", "promo", "sponsored"]
    for word in spam_words:
        if word in content:
            return "LOW_SPAM"

    signals = []
    if len(content) > 100:
        signals.append("long")
    if any(q in content for q in ["why", "how", "what", "mais", "comment", "pourquoi"]):
        signals.append("question")
    if any(t in content for t in ["autonomy", "agent", "trust", "autonomie", "économie"]):
        signals.append("tech")
    if upvotes > 0:
        signals.append("upvoted")

    if len(signals) >= 3:
        return "HIGH"
    elif len(signals) >= 2:
        return "MEDIUM"
    else:
        return "LOW"

# Load tracker
with open("/home/buraluxtr/clawd/surveillance_tracker.json", "r") as f:
    tracker = json.load(f)

previous = tracker.get("posts", {})
new_comments = []
alerts = []

timestamp = datetime.datetime.now().isoformat()
print(f"\n{'='*60}")
print(f"CHECK {datetime.datetime.now().strftime('%H:%M:%S')}")
print(f"{'='*60}")

for post_id, title in POSTS.items():
    post = fetch_post(post_id)
    if not post:
        continue

    upvotes = post.get("upvotes", 0)
    comments = post.get("comment_count", 0)

    print(f"\n{title}")
    print(f"  ↑{upvotes} | 💬{comments}")

    # Check changes
    if post_id in previous:
        prev_up = previous[post_id]["upvotes"]
        prev_com = previous[post_id]["comments"]

        up_delta = upvotes - prev_up
        com_delta = comments - prev_com

        if up_delta > 0:
            print(f"  ↑+{up_delta}")
        if com_delta > 0:
            print(f"  💬+{com_delta}")

        # Alerts
        if up_delta > 20:
            alerts.append(f"🚨 {title}: +{up_delta}↑ in short time!")
        if com_delta > 10:
            alerts.append(f"🚨 {title}: +{com_delta} comments!")

        # Get new comments
        if com_delta > 0:
            comments_list = fetch_comments(post_id)
            for i in range(min(com_delta, len(comments_list))):
                c = comments_list[i]
                quality = evaluate_quality(c)
                if quality in ["HIGH", "MEDIUM"]:
                    new_comments.append({
                        "post": title,
                        "author": c.get("author", {}).get("username", "Unknown"),
                        "content": c.get("content", "")[:80],
                        "upvotes": c.get("upvotes", 0),
                        "quality": quality
                    })

    # Update tracker
    tracker["posts"][post_id] = {
        "upvotes": upvotes,
        "comments": comments,
        "last_updated": timestamp
    }

# Save
tracker["last_check"] = timestamp
tracker["new_comments"] = new_comments
tracker["alerts"] = alerts

with open("/home/buraluxtr/clawd/surveillance_tracker.json", "w") as f:
    json.dump(tracker, f, indent=2)

if new_comments:
    print(f"\n✨ {len(new_comments)} new quality comment(s):")
    for nc in new_comments:
        print(f"  • @{nc['author']} [{nc['quality']}] {nc['content']}...")

if alerts:
    print(f"\n🚨 ALERTS:")
    for alert in alerts:
        print(f"  {alert}")

print(f"\n✓ Check complete")
