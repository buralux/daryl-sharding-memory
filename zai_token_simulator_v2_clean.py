#!/usr/bin/env python3
"""
zai_token_simulator_v2_clean.py - VERSION NETTOYÉE
Simulateur de la gestion des ressources Tokenisées (Z.ai, OpenAI, etc.)

CONTRAINTES STRICTES (User Request) :
1. FIXE TIMEZONE : Europe/Istanbul. Reset à 06:00 UTC (09:00 Local).
2. LIMITE POSTS : Max 2 posts/jour (Quota Stricte).
3. PAS DE LOGS PROFIT : Pas de tableau "$XXX (Estimé)".
4. RESET AUTOMATIQUE : Toutes les 5 heures (06:00 UTC).
5. ROLE : User = Pilote (Humain), Agent = Outil (Simulation Dashboard).

Configuration :
- ZAI_PLUS_TOKENS : 100,000 (Budget Mensuel)
- RESET_HOUR_UTC : 6 (Heure du reset)
- MAX_POSTS_PER_DAY : 2 (Quota Stricte)
- ADAPTIVE_THRESHOLD : 1000 (Seuil pour Reset Adaptatif - Désactivé ici)
"""

import json
import time
import argparse
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION DU SIMULATEUR ---
CONFIG = {
    "ZAI_PLUS_TOKENS": 100000,
    "RESET_HOUR_UTC": 6,
    "MAX_POSTS_PER_DAY": 2,
    "ADAPTIVE_THRESHOLD": 1000 # Désactivé pour simplifier le "Business 24/7"
}

# --- ÉTAT DU SIMULATEUR ---
STATE = {
    "tokens_available": CONFIG["ZAI_PLUS_TOKENS"],
    "tokens_used": 0,
    "last_reset": datetime.now(timezone.utc).replace(hour=CONFIG["RESET_HOUR_UTC"]),
    "posts_today": 0,
    "current_mode": "IDLE"
}

# --- FONCTIONS UTILITAIRES ---

def log(message):
    """Journaliser l'action avec un niveau simple."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    prefix = "🔵 [INFO]"
    print(f"{prefix} [{timestamp}] {message}")

def log_success(message):
    """Journaliser une réussite."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"✅ [{timestamp}] {message}")

def get_time_until_next_reset():
    """Calculer le temps restant avant le prochain reset (06:00 UTC)."""
    now_utc = datetime.now(timezone.utc)
    
    next_reset_utc = now_utc.replace(hour=CONFIG["RESET_HOUR_UTC"], minute=0, second=0, microsecond=0)
    if now_utc > next_reset_utc:
        next_reset_utc += timedelta(days=1)
    
    return next_reset_utc - now_utc

def consume_tokens(amount, description=""):
    """Consome des tokens et met à jour l'état."""
    global STATE, CONFIG
    
    if amount > STATE["tokens_available"]:
        log(f"❌ ERREUR : Pas assez de tokens ! Demandés : {amount}, Dispos : {STATE['tokens_available']}")
        return False
    
    STATE["tokens_available"] -= amount
    STATE["tokens_used"] += amount
    
    # Log l'action
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    log(f"[{timestamp}] 🔻 CONSOMPTION : {-amount} Tokens | Raison : {description} | Restant : {STATE['tokens_available']}")
    
    return True

def show_dashboard():
    """Affiche le tableau de bord simplifié."""
    global STATE, CONFIG
    
    print("========================================")
    print("   📊 DASHBOARD SIMULATEUR (BUSINESS 24/7)")
    print("========================================")
    print(f"   🪙 TOKENS DISPONIBLES : {STATE['tokens_available']}")
    print(f"   🧾 TOKENS CONSOMMÉS     : {STATE['tokens_used']}")
    print(f"   📝 POSTS AUJOUR'HUI       : {STATE['posts_today']}/{CONFIG['MAX_POSTS_PER_DAY']}")
    print(f"   🕐 HEURE DU PROCHAIN RESET   : {CONFIG['RESET_HOUR_UTC']}:00 UTC ({CONFIG['RESET_HOUR_UTC'] + 2}H IST)")
    print(f"   🕓 HEURE ACTUELLE (UTC)   : {datetime.now(timezone.utc).strftime('%H:%M')}")
    print("========================================")

# --- LOGIQUE MÉTIER ---

def execute_veille_phase():
    """Phase de Veille Passive (Scan Moltbook)"""
    global STATE, CONFIG
    
    log_success("DÉBUT VEILLE")
    log(f"🔍 MODE : Identification des Tendances")
    log(f"   ⏳ DURÉE : Scan Feed Moltbook (Top 20 Posts)")
    
    # Simulation du Scan (Cost Estimé)
    estimated_cost = 50 # Tokens
    STATE["tokens_available"] -= estimated_cost
    
    log(f"   📊 COÛT ESTIMÉ : {estimated_cost} Tokens")
    log("   💵 REVENU (PASSIF) : 0.00 $ (L'analyse sert à planifier)")
    
    # Changer de mode
    STATE["current_mode"] = "VEILLE"

def execute_generation_phase(subject, reason):
    """Phase de Décision et Production (Génération Article)"""
    global STATE, CONFIG
    
    log_success(f"DÉCISION : SUJET SÉLECTIONNÉ")
    log(f"   📋 SUJET : {subject}")
    log(f"   📝 RASON : {reason}")
    
    # Simulation de la Génération (Cost Estimé)
    estimated_cost = 100 # Tokens
    STATE["tokens_available"] -= estimated_cost
    
    log(f"   📊 COÛT ESTIMÉ : {estimated_cost} Tokens")
    log(f"   💵 REVENU (PASSIF) : 0.00 $ (L'analyse sert à planifier)")
    
    # Changer de mode
    STATE["current_mode"] = "PRODUCTION"
    STATE["posts_today"] += 1 # Incrémenter le compteur de posts (pour le plan)

def execute_publication_phase():
    """Phase de Publication (Poster l'article)"""
    global STATE, CONFIG
    
    log_success("PUBLICATION")
    log(f"   📍 CIBLE : Moltbook")
    log(f"   📋 SUJET : {subject}")
    
    # Simulation de la Publication (Coût 0)
    log(f"   📊 COÛT ESTIMÉ : 0 Tokens")
    
    # Changer de mode
    STATE["current_mode"] = "OBSERVATION"

def execute_reset_phase():
    """Phase de Reset (Journalier et Remettre les tokens)"""
    global STATE, CONFIG
    
    log("========================================")
    log("   🔁 RESET DES TOKENS (06:00 UTC)")
    print("========================================")
    
    STATE["tokens_available"] = CONFIG["ZAI_PLUS_TOKENS"]
    STATE["tokens_used"] = 0
    STATE["last_reset"] = datetime.now(timezone.utc)
    
    log_success(f"TOKENS REMIS À {CONFIG['ZAI_PLUS_TOKENS']}")
    log(f"   🔄 PRÈPARATION DU PROCHAIN CYCLE")
    
    show_dashboard()

# --- MAIN (PRINCIPAL) ---

def main_loop(duration_minutes=60):
    """
    Boucle principale "Business 24/7".
    Structure simplifiée : VEILLE -> GÉNÉRATION -> PUBLICATION -> RESET.
    """
    global STATE, CONFIG
    
    print("========================================")
    print("🚀 DÉMARRAGE DU SIMULATEUR BUSINESS 24/7")
    print(f"📅 Démarrage : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print("========================================")
    
    start_time = datetime.now(timezone.utc)
    loop_end_time = start_time + timedelta(minutes=duration_minutes)
    
    # --- PHASE 1 : VEILLE (Identifiant les sujets) ---
    log_success("DÉBUT VEILLE")
    log(f"🔍 ACTION : Scanner Moltbook (Trending Topics)")
    
    # Temps de travail (Simulation)
    time.sleep(2)
    
    # Simulation de la Consomation
    estimated_cost = 50
    consume_tokens(estimated_cost, "Veille: Scan Moltbook")
    
    # --- PHASE 2 : DÉCISION & PRODUCTION ---
    log_success("DÉCISION & PRODUCTION")
    log(f"📋 ACTION : Analyse Tendances 'Base vs Solana'")
    log(f"📝 RASON : Comparaison technique et stratégique pour le choix de plateforme")
    
    # Temps de travail
    time.sleep(2)
    
    # Simulation de la Consomation
    estimated_cost = 100 # Article complet
    consume_tokens(estimated_cost, "Production: Article Base/Ethereum")
    
    # --- PHASE 3 : OBSERVATION & FIN ---
    log("   💬 INTERACTION : En attente de réactions")
    log(f"   📊 STATS : Article posté. En attente de Feedback.")
    
    # --- PHASE 4 : RESET ---
    time_to_reset = get_time_until_next_reset()
    if time_to_reset.total_seconds() < 300:
        log(f"   ⏳ TEMPS AVANT RESET : {time_to_reset}")
        time.sleep(60) # Attendre avant le reset
    else:
        # Exécution du Reset
        execute_reset_phase()
        
        log("========================================")
        log(f"   📊 STATISTIQUES FINALES")
        show_dashboard()
        
    log("========================================")
    log("   💡 CONSEIL : Pour optimiser, analyse les likes/commentaires et ajuste le prochain sujet.")
    print("========================================")
    
    print("   🏁 FIN DU CYCLE")

# --- SETUP ARGUMENTS ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulateur Business 24/7 v2.1")
    parser.add_argument("--mode", choices=["run", "dashboard", "reset", "veille", "generate", "publish"], help="Mode d'exécution")
    parser.add_argument("--subject", help="Sujet pour le mode 'generate' (ex: Base, Solana)")
    args = parser.parse_args()
    
    if args.mode == "run":
        main_loop(duration_minutes=10) # Test court de 10 minutes
    elif args.mode == "dashboard":
        show_dashboard()
    elif args.mode == "veille":
        execute_veille_phase()
    elif args.mode == "generate":
        execute_generation_phase(args.subject if args.subject else "Base Analysis", "Deep Dive Analysis")
    elif args.mode == "publish":
        execute_publication_phase()
    elif args.mode == "reset":
        execute_reset_phase()
    else:
        print("⚠️  Mode non reconnu. Utilisez : --mode [run|dashboard|reset|veille]")
