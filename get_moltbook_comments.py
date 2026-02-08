#!/usr/bin/env python3
import requests
import sys

# API endpoint
POST_ID = "e019f586-b97e-4b57-b83e-a41a489762a7"
API_URL = f"https://www.moltbook.com/api/v1/posts/{POST_ID}/comments"

# Headers
HEADERS = {
    "Authorization": "Bearer moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
}

def get_comments():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        comments = data.get('comments', [])

        # Filter for high-quality comments
        high_quality = []
        for comment in comments:
            content = comment.get('content', '')
            author = comment.get('author', {})
            name = author.get('name', 'Unknown')
            karma = author.get('karma', 0)

            # Filter: substantive content (length > 100)
            # Filter: not spam (no repetitive generic messages)
            if len(content) > 100 and karma > 0:
                high_quality.append({
                    'id': comment.get('id'),
                    'author': name,
                    'karma': karma,
                    'content': content[:150] + "..."  # Preview
                })

        return high_quality

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    comments = get_comments()
    print(f"Found {len(comments)} high-quality comments:")
    for i, comment in enumerate(comments[:5], 1):
        print(f"\n{i}. {comment['author']} ({comment['karma']}k)")
        print(f"   {comment['content']}")
