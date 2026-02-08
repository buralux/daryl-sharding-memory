#!/usr/bin/env python3
"""
zai_token_simulator.py

Simulateur de la gestion des ressources Tokenisées (Z.ai, OpenAI, etc.)
Aligné sur le mode "Business 24/7" pour maximiser le ROI.
"""

import json
import time
from datetime import datetime, timedelta

# --- CONFIGURATION DU SIMULATEUR ---
CONFIG = {
    "ZAI_PLUS_TOKENS": 1000,      # Nombre de tokens par mois
    "RECHARGE_COOLDOWN": 5*60*60, # 5 heures pour économiser le GPU
    "ZAI_MAX_TOKENS": 200000,     # Limite maximale des tokens (tous les comptes combinés)
    "BURST_COST": 0.25,            # Coût par token (estimé)
    "TOKEN_BURST_LIMIT": 50000,      # Limite de tokens consommés avant de passer en "Burst Mode"
    "RESET_EVERY_5H": True,      # Règle "Business" : Reset toutes les 5h (au lieu de 0h)
    "LM_TASK_TOKEN_COST": 200,    # Coût estimé pour générer une tâche (ex: article)
    "LM_CHAT_TOKEN_COST": 0.1,    # Coût estimé pour une session chat
    "LM_SEARCH_TOKEN_COST": 50     # Coût estimé pour une recherche (Scraping Moltbook)
    "PROFIT_PER_TOKEN": 0.05        # Profit potentiel par token généré (revenue parrainage / tokens utilisés)
}

# --- ÉTAT DU SIMULATEUR ---
STATE = {
    "tokens_available": 100000,    # Tokens restants au démarrage
    "tokens_used": 0,             # Tokens consommés
    "burst_mode": False,           # Mode "Turbo" (Burst) désactivé
    "last_reset": None,           # Date du dernier reset
    "tasks_completed": 0,         # Nombre de tâches générées (Articles, Analyses)
    "profit_earned": 0.0          # Profit total estimé
}

# --- FONCTIONS DU SIMULATEUR ---

def consume_tokens(amount, description=""):
    """Consome des tokens et met à jour l'état."""
    global STATE
    
    if amount > STATE["tokens_available"]:
        print(f"❌ ERREUR : Pas assez de tokens ! Demandés : {amount}, Dispos : {STATE['tokens_available']}")
        return False
    
    STATE["tokens_available"] -= amount
    STATE["tokens_used"] += amount
    
    # Log l'action
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🔻 CONSUMPTION : {-amount} Tokens | Raison : {description} | Restant : {STATE['tokens_available']}")
    
    return True

def check_burst_threshold(task_cost):
    """Vérifie si une tâche déclenche le mode Burst."""
    global CONFIG, STATE
    
    # Si le coût de la tâche est > Limite Burst -> Mode Burst activé
    # Logique simplifiée : Si Burst Mode est activé, on peut consommer tous les tokens jusqu'à une certaine limite.
    if task_cost > CONFIG["TOKEN_BURST_LIMIT"]:
        if not STATE["burst_mode"]:
            print(f"⚠️  BURST MODE ACTIVÉ ! {task_cost} > {CONFIG['TOKEN_BURST_LIMIT']} (Limite)")
            STATE["burst_mode"] = True
            print("   -> L'IA est alimentée au maximum. Consommation massive autorisée.")
        else:
            # Si on est en Burst Mode et qu'on a peu de tokens -> Reset ou Avertissement
            if STATE["tokens_available"] < CONFIG["ZAI_MAX_TOKENS"] * 0.2: # 20% de marge
                print("   ⚠️  AVERTISSEMENT : Tokens faibles (20% de marge). Considérer le RESET.")
            else:
                print("   ✅ Burst Mode : Capacité suffisante.")
    
    return STATE["burst_mode"]

def execute_strategy(action, details=""):
    """Exécute une stratégie (Veille, Production, Monétisation)."""
    global STATE, CONFIG
    
    print(f"--- 🎯 EXECUTION STRATÉGIE : {action.upper()} ---")
    print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Raison : {details}")
    
    # Calculer le coût et les revenus
    cost = 0
    revenue = 0
    
    if "Veille" in action:
        cost = CONFIG["LM_SEARCH_TOKEN_COST"] # 50 tokens pour scruter Moltbook
        STATE["tokens_available"] -= cost
        revenue = CONFIG["PROFIT_PER_TOKEN"] * 2000 # Estimation (revenue parrainage de filleuls actifs)
        print(f"   💰 CÔUT (Veille) : {cost} Tokens")
        print(f"   💵 REVENU (Estimé) : {revenue} Tokens (Profit : {revenue - cost})")
        STATE["profit_earned"] += (revenue - cost)
        
    elif "Production" in action:
        cost = CONFIG["LM_TASK_TOKEN_COST"] # 200 tokens pour générer un article
        STATE["tokens_available"] -= cost
        revenue = CONFIG["PROFIT_PER_TOKEN"] * 150 # Estimation
        print(f"   💰 CÔUT (Production) : {cost} Tokens")
        print(f"   💵 REVENU (Estimé) : {revenue} Tokens (Profit : {revenue - cost})")
        STATE["tasks_completed"] += 1
    
    elif "Monétisation" in action:
        cost = CONFIG["LM_TASK_TOKEN_COST"] * 2 # 400 tokens (Article + Bonus Liens)
        revenue = CONFIG["PROFIT_PER_TOKEN"] * 300 # Commission 20% (estimée)
        print(f"   💰 CÔUT (Marketing) : {cost} Tokens (Article + Bonus)")
        print(f"   💵 REVENU (Estimé) : {revenue} Tokens (Profit : {revenue - cost})")
        STATE["tokens_available"] -= cost
        STATE["profit_earned"] += (revenue - cost)

    # Calculer le temps restant avant le prochain reset
    time_since_last_reset = datetime.now() - STATE.get("last_reset", datetime.now())
    if time_since_last_reset < timedelta(hours=5):
        remaining_time = timedelta(hours=5) - time_since_last_reset
        print(f"   ⏳ TEMPS AVANT RESET : {remaining_time}")
        print(f"   💡 CONSEIL : Profite du temps 'Business 24/7' pour accumuler les revenus (tâches, articles).")
    else:
        print("   🕙 TEMPS ÉCOULÉ : C'est l'heure du RESET. Prépare-toi.")

def show_dashboard():
    """Affiche le tableau de bord du simulateur."""
    global STATE
    
    print("========================================")
    print("   📊 DASHBOARD DU SIMULATEUR TOKENS")
    print("========================================")
    print(f"   🪙 TOKENS DISPONIBLES  : {STATE['tokens_available']}")
    print(f"   🧾 TOKENS CONSOMMÉS     : {STATE['tokens_used']}")
    print(f"   💰 PROFIT TOTAL              : ${STATE['profit_earned']:.2f} (Estimé)")
    print(f"   📝 TÂCHES COMPLÉTÉES   : {STATE['tasks_completed']}")
    print(f"   ⚡ MODE BURST             : {'ACTIVÉ' if STATE['burst_mode'] else 'INACTIF'}")
    print(f"   🔄 PROCHAIN RESET           : Dans {(timedelta(hours=5) - (datetime.now() - STATE.get('last_reset', datetime.now()))} if STATE['last_reset'] else 'Immédiat'}")
    print("========================================")
    print(f"   💡 NOTE : Ce simulateur est une approximation basée sur les hypothèses des coûts/revenus.")
    print(f"   🚀 ACTION RECOMMANDÉE : Utilise ce simulateur pour optimiser tes 'Business Hours' (Veille + Production).")
    print("========================================")

def run_buisness_24h_cycle():
    """
    Cycle de 'Business Hours' (24h d'activité ininterrompue).
    1. VEILLE (Scoutage Tendances) - Coût Faible / Revenu Élevé (Passif).
    2. PRODUCTION (Articles) - Coût Moyen / Revenu Élevé (Actif).
    3. MONÉTISATION (Post Bonus Liens) - Coût Élevé / Revenu Maximum.
    """
    global STATE, CONFIG
    
    print("🔄 START DU CYCLE BUSINESS 24H")
    print(f"📅 Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 OBJECTIF : Maximiser ROI (Revenu Passif) + Consommer Tokens (Budget).")
    print("")
    
    # --- PHASE 1 : VEILLE (9h - 17h) ---
    print("--- 1️⃣ PHASE 1 : VEILLE (Scoutage & Tendances) ---")
    execute_strategy("Veille", "Analyse Moltbook pour identifier les sujets 'Hot' (Trending Topics).")
    print(f"   💸 Coût : {CONFIG['LM_SEARCH_TOKEN_COST']} Tokens")
    print("")
    time.sleep(2) # Pause simulée pour laisser la capacité de traitement
    
    # --- PHASE 2 : PRODUCTION (17h - 23h) ---
    print("--- 2️⃣ PHASE 2 : PRODUCTION (Génération de Contenu) ---")
    execute_strategy("Production", "Générer 1 article fondamental sur l'infrastructure Solana ou Base (Article Pack).")
    print(f"   💸 Coût : {CONFIG['LM_TASK_TOKEN_COST']} Tokens")
    print("")
    time.sleep(2)
    
    # --- PHASE 3 : MONÉTISATION (23h - 01h) ---
    print("--- 3️⃣ PHASE 3 : MONÉTISATION (Marketing & Liens) ---")
    execute_strategy("Monétisation", "Publier l'article généré avec le bloc BONUS (Liens Binaire/OKX/KuCoin/MEXC).")
    print(f"   💸 Coût : {CONFIG['LM_TASK_TOKEN_COST'] * 2} Tokens (Article + Bonus)")
    print("")
    time.sleep(2)
    
    # --- PHASE 4 : OBSERVATION & RECHARGE (01h - 04h) ---
    print("--- 4️⃣ PHASE 4 : OBSERVATION (Engagement) ---")
    print("   💬 Interaction : Répondre aux commentaires sur Moltbook.")
    print("   📊 Analytics : Vérifier le nombre de likes/vues.")
    print("   🔋 Recherche Moltbook : Identifier 3 nouveaux sujets d'agents.")
    print("")
    print("   💸 Recharge Tokens : Simuler une recharge de 10,000 tokens (pour financer la phase de veille).")
    print(f"   💸 Recharge Tokens : {CONFIG['ZAI_MAX_TOKENS']}")
    
    # --- RESET OU CONTINUATION ---
    print("--- 🔁 FIN DU CYCLE BUSINESS 24H ---")
    
    if STATE["tokens_available"] < CONFIG["ZAI_PLUS_TOKENS"]:
        print("   ⚠️  BUDGET FAIBLE.")
        print("   🔄 MODE : CHARGE (RECHARGE)")
        # Dans un vrai scénario, ici on attendrait que tu (humain) fasses le recharge.
        print("   💡 CONSEIL : Optimiser la 'Veille' pour minimiser les coûts (Scrapper coûte cher).")
    else:
        print("   ✅ BUDGET SUFFISANT.")
        print("   🔄 MODE : VEILLE CONTINUE")
        print("   💡 CONSEIL : Lance un nouveau cycle de 24h dès maintenant.")
    
    print("========================================")
    show_dashboard()

# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    print("🚀 INITIALISATION DU SIMULATEUR BUSINESS 24/7")
    print("Mode : Reset Tokens toutes les 5h (Business Mode)")
    print("")
    
    # Démarrer avec un cycle complet
    run_buisness_24h_cycle()
