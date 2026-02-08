#!/usr/bin/env python3
"""
Script pour déclencher le workflow GitHub Actions pour pousser le code.
Le workflow utilisera le GITHUB_TOKEN pour l'authentification.
"""

import subprocess
import json
import sys

def run_github_cli_command(cmd):
    """Exécute une commande GitHub CLI et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Erreur: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"Exception: {e}")
        return None

def trigger_workflow():
    """Déclenche le workflow bot-push.yml"""
    
    # Vérifier si GitHub CLI est installé
    result = run_github_cli_command("gh --version")
    if not result:
        print("❌ GitHub CLI n'est pas installé")
        print("\n📋 Instructions manuelles:")
        print("1. Allez sur https://github.com/buralux/daryl-sharding-memory/actions")
        print("2. Cliquez sur le workflow 'Bot push on'")
        print("3. Cliquez sur 'Run workflow'")
        print("4. Sélectionnez la branche 'main'")
        print("5. Cliquez sur 'Run workflow'")
        return
    
    print("✅ GitHub CLI détectée")
    
    # Déclencher le workflow
    print("\n🚀 Déclenchement du workflow GitHub Actions...")
    result = run_github_cli_command(
        "gh workflow run bot-push.yml -R buralux/daryl-sharding-memory"
    )
    
    if result:
        print("✅ Workflow déclenché avec succès !")
        print("\n📊 Suivez le workflow ici:")
        print("https://github.com/buralux/daryl-sharding-memory/actions")
    else:
        print("❌ Échec du déclenchement du workflow")
        print("\n📋 Instructions manuelles:")
        print("1. Allez sur https://github.com/buralux/daryl-sharding-memory/actions")
        print("2. Cliquez sur le workflow 'Bot push on'")
        print("3. Cliquez sur 'Run workflow'")
        print("4. Sélectionnez la branche 'main'")
        print("5. Cliquez sur 'Run workflow'")

if __name__ == "__main__":
    trigger_workflow()
