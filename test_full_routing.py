#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from memory_sharding_system import ShardRouter

# Initialiser le router
router = ShardRouter()
router.load_all_shards()

# Vérifier l'importance actuelle de chaque shard
print("Importance actuelle des shards:")
for shard_id, shard in router.shards.items():
    imp = shard.metadata.get("importance_score", 0)
    print(f"  {shard_id}: {imp}")

# Tester le routing
test_cases = [
    "Projet actif: Finaliser GitHub release",
    "Pattern identifié: La structure modulaire améliore la maintenabilité",
    "Stratégie de contenu: Focaliser sur la qualité",
]

for content in test_cases:
    print(f"\nTest: {content}")
    best_shard_id, cross_refs = router._find_best_shard_for_content(content)
    print(f"  → Best: {best_shard_id}")
    print(f"  → Cross-refs: {cross_refs}")
