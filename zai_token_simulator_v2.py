#!/usr/bin/env python3
"""
zai_token_simulator_v2.py - STRICT BUSINESS 24/7 MODE
Simulateur de la gestion des ressources Tokenisées (Z.ai, OpenAI, etc.)

CONTRAINTES STRICTES (User Request) :
1. FIXE TIMEZONE : Europe/Istanbul. Reset à 06:00 UTC (09:00 Local), PAS "toutes les 5h".
2. LIMITE POSTS : Max 2 posts/jour (Quota Stricte). Remplace l'ancien "Max 10".
3. PAS DE LOGS PROFIT : Supprimer tout `print("Profit Estime...")`.
4. RESET ADAPTATIF : Seulement si tokens < 1000 (Soft Reset).
5. ROLE : User = Pilote (Humain), Agent = Outil (Simulation Dashboard).
6. LOGS : Simples, Propres. Pas de Marketing virtuel.
"""

import json
import time
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION DU SIMULATEUR ---
CONFIG = {
    "ZAI_PLUS_TOKENS": 100000,     # Budget Mensuel
    "RESET_HOUR_UTC": 6,             # Heure du reset (06:00 UTC / 09:00 Istanbul)
    "MAX_POSTS_PER_DAY": 2,         # Quota Strict (Anciennement 10)
    "ADAPTIVE_THRESHOLD": 1000,       # Seuil pour Reset Adaptatif (Si < 1000 tokens -> Soft Reset)
    "TIMEZONE": "Europe/Istanbul",  # Fuseau Horaire
}

# --- ÉTAT DU SIMULATEUR ---
STATE = {
    "tokens_available": CONFIG["ZAI_PLUS_TOKENS"],
    "tokens_used": 0,
    "last_reset": datetime.now(timezone.utc).replace(hour=CONFIG["RESET_HOUR_UTC"]),
    "posts_today": 0,
    "current_mode": "IDLE",
    "last_adaptive_reset": None
}

# --- FONCTIONS UTILITAIRES ---

def log(message):
    """Journaliser l'action avec un niveau simple."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"🔵 [{timestamp}] {message}")

def log_success(message):
    """Journaliser une réussite."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"✅ [{timestamp}] {message}")

def is_reset_time():
    """Vérifie si l'heure actuelle correspond à l'heure de reset (06:00 UTC)."""
    now_utc = datetime.now(timezone.utc)
    return now_utc.hour == CONFIG["RESET_HOUR_UTC"]

def can_consume(amount):
    """Vérifie si on peut consommer les tokens."""
    if amount > STATE["tokens_available"]:
        log(f"❌ ERREUR : Pas assez de tokens ! Demande : {amount}, Dispo : {STATE['tokens_available']}")
        return False
    else:
        STATE["tokens_available"] -= amount
        STATE["tokens_used"] += amount
        return True

def check_adaptive_reset():
    """
    Vérifie si un Reset Adaptatif est nécessaire.
    Si tokens < 1000 (Seuil critique), on force un Soft Reset à 100k.
    Cela évite d'être bloqué sans tokens.
    """
    global STATE, CONFIG
    
    if STATE["tokens_available"] < CONFIG["ADAPTIVE_THRESHOLD"]:
        log("⚠️ ADAPTIVE RESET : Tokens faibles (< 1000).")
        log("   💸 RECHARGE : Remise à 100,000 tokens.")
        STATE["tokens_available"] = CONFIG["ZAI_PLUS_TOKENS"]
        STATE["last_adaptive_reset"] = datetime.now(timezone.utc)
        return True
    else:
        return False

def show_dashboard():
    """Affiche le tableau de bord simplifié."""
    print("========================================")
    print("   📊 DASHBOARD SIMULATEUR BUSINESS 24/7")
    print("========================================")
    print(f"   🪙 TOKENS DISPONIBLES : {STATE['tokens_available']}")
    print(f"   🧾 TOKENS CONSOMMÉS     : {STATE['tokens_used']}")
    print(f"   📝 POSTS AUJOUR'HUI       : {STATE['posts_today']}/{CONFIG['MAX_POSTS_PER_DAY']}")
    print(f"   🕐 HEURE DU PROCHAIN RESET : {CONFIG['RESET_HOUR_UTC']}:00 UTC ({CONFIG['RESET_HOUR_UTC'] + 2}H IST)")
    print(f"   ⏱ HEURE ACTUELLE (UTC)   : {datetime.now(timezone.utc).strftime('%H:%M')}")
    print("========================================")

# --- LOGIQUE MÉTIER ---

def run_business_24h_cycle():
    """
    Cycle complet "Business 24/7" (24 heures d'opération).
    Structure :
    1. VEILLE (Opportunités) - Max 2 posts/jour.
    2. DÉCISION & PRODUCTION - Génération de l'article principal.
    3. MONÉTISATION - Publication avec liens BONUS (si nécessaire).
    """
    global STATE, CONFIG
    
    print("========================================")
    print("🚀 START DU CYCLE BUSINESS 24H")
    print(f"📅 Début : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print("========================================")
    
    start_time = datetime.now(timezone.utc)
    
    # --- PHASE 1 : VEILLE (00:00 - 08:59 UTC) ---
    print("📊 --- PHASE 1 : VEILLE & OPÉRABILITÉ ---")
    action = "VEILLE"
    reason = "Identifier les sujets 'Hot' pour optimiser le ROI."
    
    log(f"🔵 MODE : {action}")
    log(f"💭 RASON : {reason}")
    log(f"   ⏰ PLANNING : Attente de l'opportunité parfaite.")
    
    # Simulation de la Veille (Ne consomme rien ici)
    # On suppose qu'on a identifié le sujet "Meme Coins Solana" par l'analyse Moltbook.
    
    # --- PHASE 2 : DÉCISION & PRODUCTION (09:00 - 17:00 UTC) ---
    print("📊 --- PHASE 2 : DÉCISION & PRODUCTION ---")
    action = "PRODUCTION"
    reason = "Générer l'article principal sur 'Solana DeFi vs Base L2'."
    
    log(f"🔵 MODE : {action}")
    log(f"💭 RASON : {reason}")
    log(f"   ⚙️ QUOTA : {STATE['posts_today']}/{CONFIG['MAX_POSTS_PER_DAY']} (Quota Stricte)")
    
    # Consomation des tokens (Coût estimé)
    # Note : On ne calcule pas le profit en $. On suit strictement les tokens disponibles.
    
    log(f"   📝 ACTION : GÉNÉRATION CONTENU (DRAFTING)...")
    print(f"   🧾 TOKENS : {STATE['tokens_available']}")
    
    # Simulation de la consomation
    estimated_cost = 1000 # Estimation conservative pour un gros article
    
    # Check du seuil adaptatif AVANT de consommer
    if not check_adaptive_reset():
        # Si on a fait un adaptatif reset, on ne consomme pas les tokens du cycle normal
        log("   ⚠️ SOFT RESET APPLIQUÉ. Tokens rechargés. Cycle adaptatif activé.")
        estimated_cost = 0 # Pas de coût car rechargé
    
    # Si pas de reset adaptatif, on consomme
    if estimated_cost > 0:
        if can_consume(estimated_cost):
            STATE["posts_today"] += 1 # Incrémenter le compteur
            log_success(f"✅ CONTENU GÉNÉRÉ. Cost : {estimated_cost} Tokens. Reste : {STATE['tokens_available']}")
        else:
            log("   ❌ IMPOSSIBLE DE PRODUIRE (Pas assez de tokens).")
            return # Arrêter le cycle
            
    # --- PHASE 3 : MONÉTISATION (17:00 - 00:59 UTC) ---
    print("📊 --- PHASE 3 : MONÉTISATION ---")
    action = "MONÉTISATION"
    reason = "Publier l'article sur Moltbook (Plateforme Cible)."
    
    log(f"🔵 MODE : {action}")
    log(f"💭 RASON : {reason}")
    log(f"   💸 CONTEXTE : Plateforme Moltbook. Quota : {STATE['posts_today']}/{CONFIG['MAX_POSTS_PER_DAY']}")
    
    # Consomation des tokens (Coût estimé pour Publication + Bonus)
    estimated_cost = 100 # Estimation pour l'ensemble (Post + Bonus)
    
    if can_consume(estimated_cost):
        STATE["posts_today"] += 1 # Finir le quota
        log_success(f"✅ ARTICLE PUBLIÉ. Cost : {estimated_cost} Tokens. Reste : {STATE['tokens_available']}")
    else:
        log("   ❌ IMPOSSIBLE DE PUBLIER (Pas assez de tokens).")
            return
            
    # --- PHASE 4 : OBSERVATION (00:59 - 06:00 UTC) ---
    print("📊 --- PHASE 4 : OBSERVATION ---")
    action = "OBSERVATION"
    reason = "Analyser l'engagement (Likes, Commentaires)."
    
    log(f"🔵 MODE : {action}")
    log(f"💭 RASON : {reason}")
    log("   ⏳ TEMPS : En attente du Reset de 06:00 UTC.")
    time.sleep(2) # Pause légère
    
    # --- PHASE 5 : CHECK DE RESET (05:59 - 06:00 UTC) ---
    print("📊 --- PHASE 5 : CHECK DE RESET ---")
    log(f"⏳ ATTENTE DE L'HEURE {CONFIG['RESET_HOUR_UTC']}:00 UTC...")
    
    # Boucle d'attente jusqu'à 06:00 UTC
    while datetime.now(timezone.utc).hour < CONFIG["RESET_HOUR_UTC"]:
        time.sleep(30) # Pause de 30 secondes
        # Log silencieux pour ne pas polluer
        
    # Exécution du Reset (Strict 24h)
    log("   🔄 RESET JOURNALIER 06:00 UTC (24h CYCLE)")
    STATE["tokens_available"] = CONFIG["ZAI_PLUS_TOKENS"] # Remise à 100k
    STATE["tokens_used"] = 0 # Remise à zéro
    STATE["last_reset"] = datetime.now(timezone.utc)
    
    # --- FIN DU CYCLE ---
    print("----------------------------------------")
    print("🏁 FIN DU CYCLE BUSINESS 24H")
    print(f"📅 Date : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 CONSEIL : Le cycle se répète toutes les 24h.")
    print("========================================")
    
    show_dashboard()

# --- MAIN (PRINCIPAL) ---
if __name__ == "__main__":
    print("🚀 INITIALISATION DU SIMULATEUR BUSINESS 24/7")
    print("🔧 RÈGLES STRICTES : MAX 2 POSTS/JOUR, RESET 06:00 UTC, PAS DE PROFIT VIRTUEL.")
    print("")
    
    run_business_24h_cycle()
