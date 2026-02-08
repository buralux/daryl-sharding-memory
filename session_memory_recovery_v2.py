#!/usr/bin/env python3
"""
Session Memory Recovery - Version simplifiée
Scanne les derniers fichiers memory/*.md et génère last_session_memory.md
"""

import re
from pathlib import Path
from datetime import datetime

# Configuration
MEMORY_DIR = Path("/home/buraluxtr/clawd/memory")
OUTPUT_FILE = Path("/home/buraluxtr/clawd/last_session_memory.md")

def extract_key_content(content):
    """Extrait le contenu important d'un fichier de mémoire"""
    
    important_parts = {
        "tasks_completed": [],
        "decisions": [],
        "lessons": [],
        "insights": []
    }
    
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        
        # Tâches complétées
        if any(keyword in line_lower for keyword in ['publié', 'créé', 'posté', 'ajouté', 'supprimé']):
            important_parts["tasks_completed"].append(line.strip())
        
        # Décisions
        elif any(keyword in line_lower for keyword in ['décision', 'choix', 'déterminé', 'décidé', 'choisi']):
            important_parts["decisions"].append(line.strip())
        
        # Leçons apprises
        elif any(keyword in line_lower for keyword in ['leçon', 'appris', 'découvert', 'identifié', 'réalisé']):
            important_parts["lessons"].append(line.strip())
        
        # Insights
        elif any(keyword in line_lower for keyword in ['insight', 'pattern', 'framework', 'stratégie']):
            important_parts["insights"].append(line.strip())
    
    return important_parts

def scan_recent_memory_files():
    """Scanne les fichiers memory des 3 derniers jours"""
    
    print("🔍 Scanning memory files (last 3 days)...")
    print("=" * 60)
    
    if not MEMORY_DIR.exists():
        print("❌ Memory directory not found!")
        return None
    
    # Lister tous les fichiers .md dans memory/
    memory_files = []
    
    for file in MEMORY_DIR.glob("*.md"):
        if file.is_file():
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                memory_files.append({
                    "file": file,
                    "content": content
                })
            except Exception as e:
                print(f"⚠️  Error reading {file.name}: {e}")
    
    if not memory_files:
        print("❌ No memory files found!")
        return None
    
    # Trier par date de modification (plus récents d'abord)
    memory_files.sort(key=lambda x: x['file'].stat().st_mtime, reverse=True)
    
    print(f"📊 Found {len(memory_files)} memory files:\n")
    
    # Limiter aux 3 plus récents
    recent_files = memory_files[:3]
    
    return recent_files

def generate_session_memory(recent_files):
    """Génère le fichier last_session_memory.md"""
    
    output_lines = []
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    output_lines.append("# SESSION MEMORY RECOVERY")
    output_lines.append(f"# Generated: {timestamp}")
    output_lines.append("# Source: Automatic scan of memory/*.md files (last 3 days)")
    output_lines.append("")
    
    output_lines.append("## 📋 TÂCHES RÉCENTES")
    output_lines.append("")
    
    for file_data in recent_files:
        file_name = file_data['file'].name
        content = file_data['content']
        
        important_parts = extract_key_content(content)
        
        output_lines.append(f"\n### {file_name}")
        output_lines.append("")
        
        if important_parts['tasks_completed']:
            output_lines.append("#### ✅ Tâches Complétées")
            for task in important_parts['tasks_completed'][:5]:
                output_lines.append(f"- {task}")
        
        if important_parts['decisions']:
            output_lines.append("#### 🎯 Décisions")
            for decision in important_parts['decisions'][:5]:
                output_lines.append(f"- {decision}")
        
        if important_parts['lessons']:
            output_lines.append("#### 📝 Leçons Apprises")
            for lesson in important_parts['lessons'][:5]:
                output_lines.append(f"- {lesson}")
        
        if important_parts['insights']:
            output_lines.append("#### 💡 Insights")
            for insight in important_parts['insights'][:5]:
                output_lines.append(f"- {insight}")
    
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## 💡 COMMENTAIRES")
    output_lines.append("")
    output_lines.append("Ceci est une extraction automatique des fichiers memory/*.md des 3 derniers jours.")
    output_lines.append("")
    output_lines.append("Pour charger cette mémoire dans une nouvelle session:")
    output_lines.append("```bash")
    output_lines.append("# Au début de session")
    output_lines.append("cat /home/buraluxtr/clawd/last_session_memory.md")
    output_lines.append("```")
    output_lines.append("")
    output_lines.append("Cela permet de reprendre rapidement le contexte et les décisions de la session précédente.")
    
    output_lines.append("")
    output_lines.append("## 🔄 MISE À JOUR")
    output_lines.append("")
    output_lines.append("Fichier mis à jour automatiquement par `session_memory_recovery.py`")
    output_lines.append("Exécuté à la fin de chaque session pour synchroniser.")
    
    return '\n'.join(output_lines)

def main():
    """Fonction principale"""
    
    print("🚀 SESSION MEMORY RECOVERY (Simplifiée)")
    print("=" * 60)
    print()
    
    # Scanne les fichiers de mémoire
    recent_files = scan_recent_memory_files()
    
    if recent_files is None:
        print("❌ No insights found!")
        return
    
    # Générer le fichier de récupération
    print("📝 Generating last_session_memory.md...")
    
    recovery_content = generate_session_memory(recent_files)
    
    try:
        OUTPUT_FILE.write_text(recovery_content, encoding='utf-8')
        print(f"✅ Session memory saved to: {OUTPUT_FILE}")
        print(f"📊 Files scanned: {len(recent_files)}")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS: Session memory recovered!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error saving recovery file: {e}")

if __name__ == "__main__":
    main()
