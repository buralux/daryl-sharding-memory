#!/usr/bin/env python3
"""
Session Memory Recovery - Récupère automatiquement la mémoire de la dernière session

Scanne tous les fichiers memory/YYYY-MM-DD.md et extrait:
- Décisions prises
- Points clés identifiés
- Leçons apprises
- Patterns découverts
- Actions importantes

Sauvegarde le tout dans last_session_memory.md pour être chargé au démarrage.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
MEMORY_DIR = Path("/home/buraluxtr/clawd/memory")
OUTPUT_FILE = Path("/home/buraluxtr/clawd/last_session_memory.md")
DAYS_TO_SCAN = 3

def extract_key_insights(content):
    """Extrait les insights clés d'un fichier de mémoire"""
    
    insights = {
        "decisions": [],
        "lessons": [],
        "patterns": [],
        "important_actions": []
    }
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Décisions
        if re.search(r'(décision|choix|chose|déterminé|déterminé|décidé)\b', line, re.IGNORECASE):
            insights["decisions"].append({
                "context": lines[max(0, i-2):i],
                "decision": line.strip()
            })
        
        # Leçons apprises
        elif re.search(r'(leçon|appri|appris|découvert|identifié|réalisé)\b', line, re.IGNORECASE):
            insights["lessons"].append({
                "context": lines[max(0, i-2):i],
                "lesson": line.strip()
            })
        
        # Patterns
        elif re.search(r'(pattern|framework|approche|stratégie|architecture|modèle|structure|workflow)\b', line, re.IGNORECASE):
            insights["patterns"].append({
                "context": lines[max(0, i-2):i],
                "pattern": line.strip()
            })
        
        # Actions importantes
        elif re.search(r'(créé|publié|supprimé|modifié|installé|mis à jour|ajouté)\b', line, re.IGNORECASE):
            insights["important_actions"].append({
                "context": lines[max(0, i-2):i],
                "action": line.strip()
            })
    
    return insights

def scan_memory_files():
    """Scanne les fichiers de mémoire des derniers jours"""
    
    print(f"🔍 Scanning memory files from last {DAYS_TO_SCAN} days...")
    print("=" * 60)
    
    if not MEMORY_DIR.exists():
        print("❌ Memory directory not found!")
        return None
    
    # Trouver les fichiers memory/*.md des derniers jours
    memory_files = []
    
    if MEMORY_DIR.is_dir():
        for file in MEMORY_DIR.iterdir():
            if file.is_file() and file.suffix == '.md':
                try:
                    # Extraire la date du nom
                    date_match = re.search(r'memory/(\d{4}-\d{2}-\d{2})\.md', file.name)
                    if date_match:
                        memory_files.append((file, date_match.group(1)))
                except Exception as e:
                    print(f"⚠️  Error parsing {file.name}: {e}")
    
    if not memory_files:
        print("❌ No memory files found!")
        return None
    
    # Trier par date (plus récents d'abord)
    memory_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📊 Found {len(memory_files)} memory files:\n")
    
    # Limiter aux D derniers jours
    recent_files = memory_files[:DAYS_TO_SCAN]
    
    all_insights = {
        "scanned_files": [],
        "decisions": [],
        "lessons": [],
        "patterns": [],
        "important_actions": []
    }
    
    for file, date_str in recent_files:
        print(f"\n📄 {date_str}: {file.name}")
        
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            
            # Extraire les insights
            insights = extract_key_insights(content)
            
            # Ajouter à la collection globale
            all_insights["decisions"].extend(insights["decisions"])
            all_insights["lessons"].extend(insights["lessons"])
            all_insights["patterns"].extend(insights["patterns"])
            all_insights["important_actions"].extend(insights["important_actions"])
            
            all_insights["scanned_files"].append({
                "date": date_str,
                "file": file.name,
                "size": len(content.split('\n'))
            })
            
        except Exception as e:
            print(f"❌ Error reading {file.name}: {e}")
    
    return all_insights

def generate_session_memory_md(insights):
    """Génère le fichier last_session_memory.md"""
    
    output_lines = []
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    output_lines.append(f"# SESSION MEMORY RECOVERY")
    output_lines.append(f"# Extracted: {timestamp}")
    output_lines.append("# Source: Automatic scan of memory/*.md files")
    output_lines.append("")
    output_lines.append("## 📊 SCANNED FILES")
    output_lines.append("")
    
    for file_info in insights["scanned_files"]:
        output_lines.append(f"- **{file_info['date']}** ({file_info['size']} lines)")
    
    if not insights["scanned_files"]:
        output_lines.append("_No memory files found_")
    
    output_lines.append("")
    output_lines.append("## 🎯 DECISIONS PRISAS")
    output_lines.append("")
    
    if insights["decisions"]:
        for i, decision in enumerate(insights["decisions"][:10], 1):
            if decision["context"]:
                output_lines.append(f"\n{decision['context']}")
            output_lines.append(f"{decision['decision']}")
        
        if len(insights["decisions"]) > 10:
            output_lines.append(f"\n_... and {len(insights['decisions']) - 10} more")
    else:
        output_lines.append("_No decisions recorded_")
    
    output_lines.append("")
    output_lines.append("## 📝 LEÇONS APPRIS")
    output_lines.append("")
    
    if insights["lessons"]:
        for i, lesson in enumerate(insights["lessons"][:10], 1):
            if lesson["context"]:
                output_lines.append(f"\n{lesson['context']}")
            output_lines.append(f"{lesson['lesson']}")
        
        if len(insights["lessons"]) > 10:
            output_lines.append(f"\n_... and {len(insights['lessons']) - 10} more")
    else:
        output_lines.append("_No lessons recorded_")
    
    output_lines.append("")
    output_lines.append("## 🔧 PATTERNS DÉCOUVERTS")
    output_lines.append("")
    
    if insights["patterns"]:
        for i, pattern in enumerate(insights["patterns"][:10], 1):
            if pattern["context"]:
                output_lines.append(f"\n{pattern['context']}")
            output_lines.append(f"{pattern['pattern']}")
        
        if len(insights["patterns"]) > 10:
            output_lines.append(f"\n_... and {len(insights['patterns']) - 10} more")
    else:
        output_lines.append("_No patterns discovered_")
    
    output_lines.append("")
    output_lines.append("## ⚡ ACTIONS IMPORTANTES")
    output_lines.append("")
    
    if insights["important_actions"]:
        for i, action in enumerate(insights["important_actions"][:10], 1):
            if action["context"]:
                output_lines.append(f"\n{action['context']}")
            output_lines.append(f"{action['action']}")
        
        if len(insights["important_actions"]) > 10:
            output_lines.append(f"\n_... and {len(insights['important_actions']) - 10} more")
    else:
        output_lines.append("_No important actions recorded_")
    
    output_lines.append("")
    output_lines.append("---")
    output_lines.append("")
    output_lines.append("## 💡 COMMENTAIRES")
    output_lines.append("")
    output_lines.append("_Ceci est une extraction automatique des fichiers memory/*.md des 3 derniers jours._")
    output_lines.append("_L'objectif est de récupérer rapidement le contexte et les décisions de la dernière session._")
    output_lines.append("_Pour charger cette mémoire dans une nouvelle session :_")
    output_lines.append("```bash")
    output_lines.append("# Au début de session")
    output_lines.append("cat /home/buraluxtr/clawd/last_session_memory.md")
    output_lines.append("```")
    
    return '\n'.join(output_lines)

def main():
    """Fonction principale"""
    
    print("🚀 SESSION MEMORY RECOVERY")
    print("=" * 60)
    print()
    
    # Scanne les fichiers de mémoire
    insights = scan_memory_files()
    
    if insights is None:
        print("❌ No insights found!")
        return
    
    # Générer le fichier de sortie
    print("📝 Generating last_session_memory.md...")
    
    recovery_content = generate_session_memory_md(insights)
    
    try:
        OUTPUT_FILE.write_text(recovery_content, encoding='utf-8')
        print(f"✅ Session memory saved to: {OUTPUT_FILE}")
        print(f"📊 Files scanned: {len(insights['scanned_files'])}")
        print(f"🎯 Decisions: {len(insights['decisions'])}")
        print(f"📝 Lessons: {len(insights['lessons'])}")
        print(f"🔧 Patterns: {len(insights['patterns'])}")
        print(f"⚡ Actions: {len(insights['important_actions'])}")
        
        # Générer aussi un JSON pour un chargement facile
        json_output = OUTPUT_FILE.parent / "last_session_memory.json"
        summary = {
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "files_scanned": insights["scanned_files"],
            "decisions": insights["decisions"][:10],
            "lessons": insights["lessons"][:10],
            "patterns": insights["patterns"][:10],
            "actions": insights["important_actions"][:10]
        }
        
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON summary saved to: {json_output}")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS: Session memory recovered!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error saving recovery file: {e}")

if __name__ == "__main__":
    main()
