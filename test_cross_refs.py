#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from memory_sharding_system import ShardRouter

router = ShardRouter()
router.load_all_shards()

# Test cross-reference detection
test_cases = [
    "Projet actif: GitHub release - voir shard technical",
    "Stratégie: connecte avec shard Technique et Architecture",
    "Pattern shard:projects détecté dans ce contenu",
]

for content in test_cases:
    print(f"\n📝 Test: {content}")
    best_shard_id, cross_refs = router._find_best_shard_for_content(content)
    print(f"  → Best: {best_shard_id}")
    print(f"  → Cross-refs: {cross_refs}")
