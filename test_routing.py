#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from memory_sharding_system import SHARD_DOMAINS

def test_routing(content):
    """Teste le routing d'un contenu"""
    content_lower = content.lower()
    scores = {}

    print(f"\n📝 Test: {content}")
    print(f"   Lower: {content_lower}\n")

    for domain, config in SHARD_DOMAINS.items():
        score = 0.0

        # Score base sur les mots-cles du domaine
        for keyword in config["keywords"]:
            if keyword.lower() in content_lower:
                score += 1.0
                print(f"   ✅ {domain}: '{keyword}' found (score: {score})")

        if score > 0:
            scores[domain] = score

    if scores:
        best = max(scores, key=scores.get)
        print(f"\n   🎯 Best shard: {best} (score: {scores[best]})")
    else:
        print(f"   ⚠️ No matches, using default: insights")

# Tests
test_routing("Projet actif: Finaliser GitHub release")
test_routing("Pattern identifié: La structure modulaire améliore la maintenabilité")
test_routing("Stratégie de contenu: Focaliser sur la qualité")
test_routing("contact expert sur le framework de sharding")
