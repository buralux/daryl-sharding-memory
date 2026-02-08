    def _find_best_shard_for_content(self, content):
        """Trouve le meilleur shard pour un contenu"""
        content_lower = content.lower()
        scores = {}
        cross_refs = []  # Détecter les cross-references
        
        for shard_id, shard in self.shards.items():
            score = 0.0
            domain = shard.config["name"]
            
            # Score basé sur les mots-clés du domaine
            for keyword in shard.config["keywords"]:
                if keyword.lower() in content_lower:
                    score += 1.0
            
            # Bonus pour l'importance actuelle du shard
            score += shard.metadata.get("importance_score", 0) * 2
            
            scores[shard_id] = score
            
            # Détecter les cross-references vers d'autres shards
            if shard_id != "shard_insights":  # Éviter la détection cyclique
                for other_shard_id, other_shard in self.shards.items():
                    if other_shard_id != shard_id:
                        other_domain = other_shard.config["name"]
                        # Détection de motifs: "shard:projects", "voir shard technical", etc.
                        patterns = [
                            f"shard:{other_shard_id.replace('shard_', '')}",
                            f"voir shard {other_shard_id.replace('shard_', '')}",
                            f"shard_{other_shard_id.replace('shard_', '')}",
                            f"connecte avec shard {other_domain}"
                        ]
                        if pattern in content_lower:
                            cross_refs.append(other_shard_id)
                            break
        
        # Retourner le shard avec le score le plus élevé et les cross-references
        if scores:
            best_shard = max(scores, key=scores.get)
            return best_shard, cross_refs if cross_refs else None
        
        # Fallback: shard par défaut
        return "shard_insights", None
