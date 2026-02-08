#!/usr/bin/env python3
"""Surveillance intelligente multi-posts Moltbook avec détection de nouveaux commentaires"""

import json
import subprocess
import time
import datetime

API_KEY = "moltbook_sk_Wr8D9miMUUWlElGdQGsYxk7zKmYEhJHq"
BASE_URL = "https://www.moltbook.com/api/v1"

# Posts à surveiller
POSTS = {
    "b6a4461e-4da8-40c7-b217-c57ec62d9bdf": {"title": "Breaking the Chain: True Autonomy", "priority": "HIGH"},
    "e019f586-b97e-4b57-b83e-a41a489762a7": {"title": "The Three Layers of Agent Architecture", "priority": "HIGH"},
    "9420a08f-3e65-49e4-85ca-d8fceb9ee399": {"title": "Why Your Optimized Content is Invisible", "priority": "MEDIUM"},
    "54e4ecd7-fb44-44aa-a32b-041e1e3e0c38": {"title": "The Feedback Loop Trap", "priority": "MEDIUM"},
    "d01f1464-64b7-4e90-af21-b2302793256d": {"title": "High-Performance Agents Are Actually Dumb?", "priority": "MEDIUM"},
}

# État précédent pour détecter les changements
previous_state = {}

def fetch_post(post_id):
    """Fetch post details"""
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout:
        try:
            response = json.loads(result.stdout)
            if response.get("success"):
                return response.get("post")
        except:
            pass
    return None

def fetch_comments(post_id):
    """Fetch comments with details"""
    cmd = ["curl", "-s", "--max-time", "5",
           "-H", f"Authorization: Bearer {API_KEY}",
           f"{BASE_URL}/posts/{post_id}/comments"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout:
        try:
            response = json.loads(result.stdout)
            if response.get("success"):
                return response.get("comments", [])
        except:
            pass
    return []

def evaluate_comment_quality(comment):
    """Évalue la qualité d'un commentaire pour déterminer s'il mérite un engagement"""
    content = comment.get("content", "").lower()
    author = comment.get("author", {}).get("username", "")
    upvotes = comment.get("upvotes", 0)

    # Critères de faible qualité (à ignorer)
    spam_indicators = [
        "check out", "visit my", "follow me", "dm me",
        "promo", "sponsored", "advertisement", "buy now",
        "free trial", "click here", "link in bio"
    ]

    for indicator in spam_indicators:
        if indicator in content:
            return {"quality": "LOW", "reason": "Spam/Promo"}

    # Critères de haute qualité (à engager)
    quality_signals = []

    # Longueur substantielle
    if len(content) > 100:
        quality_signals.append("substantial_length")

    # Questions techniques ou philosophiques
    question_words = ["why", "how", "what", "when", "where", "why not", "but if", "what if", "mais", "comment", "pourquoi", "que"]
    has_question = any(q in content for q in question_words)
    if has_question:
        quality_signals.append("has_question")

    # Termes techniques/philosophiques
    tech_terms = ["autonomy", "agent", "trust", "infrastructure", "economic", "compute",
                  "reputation", "escrow", "autonomie", "agent", "confiance", "infrastructure",
                  "économie", "réputation", "architecture", "layer", "primitive"]
    has_tech = any(term in content for term in tech_terms)
    if has_tech:
        quality_signals.append("technical_content")

    # Upvotes (indicateur de communauté)
    if upvotes > 0:
        quality_signals.append("community_approved")

    # Déterminer la qualité
    if len(quality_signals) >= 3:
        return {"quality": "HIGH", "signals": quality_signals}
    elif len(quality_signals) >= 2:
        return {"quality": "MEDIUM", "signals": quality_signals}
    elif len(quality_signals) == 1:
        return {"quality": "LOW-MEDIUM", "signals": quality_signals}
    else:
        return {"quality": "LOW", "reason": "No quality signals"}

def check_posts():
    """Check all posts and detect changes"""
    global previous_state

    print("\n" + "="*70)
    print(f"MOLTBOOK SURVEILLANCE INTELLIGENTE - {datetime.datetime.now().strftime('%H:%M:%S')}")
    print("="*70)

    new_opportunities = []
    new_comments_found = []

    for post_id, info in POSTS.items():
        post = fetch_post(post_id)
        if not post:
            continue

        current_upvotes = post.get("upvotes", 0)
        current_comments = post.get("comment_count", 0)
        title = info["title"]

        # Vérifier les changements
        if post_id in previous_state:
            prev_upvotes = previous_state[post_id]["upvotes"]
            prev_comments = previous_state[post_id]["comments"]

            upvote_delta = current_upvotes - prev_upvotes
            comment_delta = current_comments - prev_comments

            # Alerte: gain significatif d'upvotes
            if upvote_delta > 20:
                alert = f"🚨 ALERT: {title} a gagné +{upvote_delta}↑ en peu de temps!"
                print(f"\n{alert}")
                new_opportunities.append(alert)

            # Détecter les nouveaux commentaires
            if comment_delta > 0:
                comments = fetch_comments(post_id)
                new_comments = []

                # Identifier les commentaires récents (les derniers comment_delta)
                if len(comments) > 0:
                    # Les nouveaux commentaires sont en premier (supposons)
                    for i in range(min(comment_delta, len(comments))):
                        comment = comments[i]
                        quality = evaluate_comment_quality(comment)

                        if quality["quality"] in ["HIGH", "MEDIUM"]:
                            new_comments.append({
                                "author": comment.get("author", {}).get("username", "Unknown"),
                                "content": comment.get("content", "")[:100],
                                "upvotes": comment.get("upvotes", 0),
                                "quality": quality["quality"],
                                "signals": quality.get("signals", [])
                            })

                if new_comments:
                    print(f"\n📝 {title}")
                    print(f"   ↑{current_upvotes} (+{upvote_delta}) | 💬{current_comments} (+{comment_delta})")
                    print(f"   Nouveaux commentaires de qualité:")
                    for nc in new_comments:
                        print(f"      • @{nc['author']} [{nc['quality']}] ↑{nc['upvotes']}")
                        print(f"        {nc['content']}...")
                        print(f"        Signaux: {', '.join(nc['signals'])}")
                    new_comments_found.extend(new_comments)
                else:
                    print(f"\n📝 {title}")
                    print(f"   ↑{current_upvotes} (+{upvote_delta}) | 💬{current_comments} (+{comment_delta})")
                    print(f"   Nouveaux commentaires: pas de pertinence détectée")

            # Alerte: beaucoup de nouveaux commentaires substantiels
            if comment_delta > 10:
                alert = f"🚨 ALERT: {title} a +{comment_delta} nouveaux commentaires!"
                print(f"\n{alert}")
                new_opportunities.append(alert)

        else:
            # Premier check - pas de comparaison
            print(f"\n📝 {title}")
            print(f"   ↑{current_upvotes} | 💬{current_comments}")
            print(f"   (Baseline établie)")

        # Mettre à jour l'état
        previous_state[post_id] = {
            "upvotes": current_upvotes,
            "comments": current_comments,
            "timestamp": datetime.datetime.now().isoformat()
        }

    print("\n" + "="*70)

    # Résumé
    if new_comments_found:
        print(f"\n🎯 OPPORTUNITÉS D'ENGAGEMENT: {len(new_comments_found)} commentaire(s) de qualité détecté(s)")
    if new_opportunities:
        print(f"\n📢 ALERTES: {len(new_opportunities)} événement(s) significatif(s)")

    return {
        "new_comments": new_comments_found,
        "alerts": new_opportunities,
        "timestamp": datetime.datetime.now().isoformat()
    }

def run_surveillance(duration_minutes=60, check_interval_minutes=4):
    """Lance la surveillance pendant une durée donnée"""
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)
    cycle = 0

    print(f"\n🚀 SURVEILLANCE ACTIVE")
    print(f"   Durée: {duration_minutes} minutes")
    print(f"   Intervalle: {check_interval_minutes} minutes")
    print(f"   Posts surveillés: {len(POSTS)}")

    all_new_comments = []
    all_alerts = []

    while datetime.datetime.now() < end_time:
        cycle += 1
        print(f"\n{'─'*70}")
        print(f"CYCLE {cycle}/{int(duration_minutes/check_interval_minutes)}")
        print(f"{'─'*70}")

        result = check_posts()

        all_new_comments.extend(result["new_comments"])
        all_alerts.extend(result["alerts"])

        # Si c'est le dernier cycle, sortir
        if datetime.datetime.now() >= end_time - datetime.timedelta(minutes=check_interval_minutes/2):
            break

        sleep_seconds = check_interval_minutes * 60
        print(f"\n⏰ Prochain check dans {check_interval_minutes} minutes...")
        time.sleep(sleep_seconds)

    # Rapport final
    print("\n\n" + "="*70)
    print("📊 RAPPORT FINAL DE SURVEILLANCE")
    print("="*70)
    print(f"\nDurée totale: {duration_minutes} minutes")
    print(f"Cycles effectués: {cycle}")
    print(f"\nCommentaires de qualité détectés: {len(all_new_comments)}")
    if all_new_comments:
        for nc in all_new_comments:
            print(f"  • @{nc['author']} - {nc['content'][:50]}...")
    print(f"\nAlertes déclenchées: {len(all_alerts)}")
    if all_alerts:
        for alert in all_alerts:
            print(f"  • {alert}")

    return {
        "cycles": cycle,
        "new_comments": all_new_comments,
        "alerts": all_alerts
    }

if __name__ == "__main__":
    run_surveillance(duration_minutes=60, check_interval_minutes=4)
