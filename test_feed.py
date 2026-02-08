#!/usr/bin/env python3
"""Test rapide de l'API Moltbook pour le feed"""

import subprocess
import json

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

print("Test de récupération du feed Moltbook...")

cmd = ["curl", "-s", "--max-time", "5",
       "-H", f"Authorization: Bearer {API_KEY}",
       f"{BASE_URL}/feed?limit=5"]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

print(f"Status code: {result.returncode}")
print(f"Output length: {len(result.stdout)}")

if result.stdout:
    try:
        response = json.loads(result.stdout)
        print(f"Response: {json.dumps(response, indent=2)[:500]}")
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw output: {result.stdout[:200]}")
