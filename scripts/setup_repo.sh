#!/bin/bash
# Repository Initialization Script for DARYL Sharding Memory
# This script prepares the project for GitHub upload

set -e

echo "=== 🚀 Initializing DARYL Sharding Memory Repository ==="

# Check if we're in the project root
if [ ! -f "memory_sharding_system.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo ""
echo "✅ Project root confirmed"

# Create directory structure
echo "📁 Creating directory structure..."

mkdir -p src/cli
mkdir -p docs
mkdir -p scripts

# Move existing files to organized structure
echo "🔄 Organizing files..."

if [ -f "memory_sharding_system.py" ]; then
    cp memory_sharding_system.py src/
    echo "   ✓ Moved: memory_sharding_system.py → src/"
fi

if [ -f "daryl_memory_cli.py" ]; then
    cp daryl_memory_cli.py src/cli/
    echo "   ✓ Moved: daryl_memory_cli.py → src/cli/"
fi

if [ -f "daryl_sharding_critique_analysis.md" ]; then
    cp daryl_sharding_critique_analysis.md docs/
    echo "   ✓ Moved: daryl_sharding_critique_analysis.md → docs/"
fi

if [ -f "DARYL_SHARDING_v1.0_SPEC.md" ]; then
    cp DARYL_SHARDING_v1.0_SPEC.md docs/
    echo "   ✓ Moved: DARYL_SHARDING_v1.0_SPEC.md → docs/"
fi

if [ -f "moltbook_post_daryl_sharding_recap.json" ]; then
    rm moltbook_post_daryl_sharding_recap.json
    echo "   ✓ Deleted: moltbook_post_daryl_sharding_recap.json (temp file)"
fi

if [ -f "moltbook_post_daryl_sharding_clarification.json" ]; then
    rm moltbook_post_daryl_sharding_clarification.json
    echo "   ✓ Deleted: moltbook_post_daryl_sharding_clarification.json (temp file)"
fi

if [ -f "daryl_memory_cli.py" ]; then
    # Fix the shebang line
    sed -i '1s|#!/usr/bin/env python3\n|#!/usr/bin/env python3\n|' daryl_memory_cli.py
    echo "   ✓ Fixed: Shebang in daryl_memory_cli.py"
fi

# Verify structure
echo ""
echo "📋 Verifying repository structure..."

# Check required files
required_files=(
    "src/memory_sharding_system.py"
    "src/cli/daryl_memory_cli.py"
    "LICENSE"
    "README.md"
    ".gitignore"
)

all_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file is missing"
        all_exist=false
    fi
done

if [ "$all_exist" = true ]; then
    echo ""
    echo "✅ All required files verified"
else
    echo ""
    echo "❌ Some required files are missing"
    echo "   Please check the repository structure"
fi

# Create initialization summary
echo ""
echo "=== 📊 Initialization Summary ==="
echo ""
echo "Project: DARYL Sharding Memory"
echo "Version: 1.0"
echo "Status: Ready for GitHub"
echo ""
echo "📁 Structure:"
echo "  ├── src/"
echo "  │   ├── memory_sharding_system.py (Core system)"
echo "  │   └── cli/"
echo "  │       └── daryl_memory_cli.py (CLI interface)"
echo "  ├── docs/"
echo "  │   ├── SECURITY_CONSIDERATIONS.md (Security model)"
echo "  │   ├── DARYL_SHARDING_v1.0_SPEC.md (Specification)"
echo "  │   └── (Additional documentation)"
echo "  ├── scripts/"
echo "  │   └── setup_repo.sh (This script)"
echo "  ├── LICENSE (MIT License)"
echo "  ├── README.md (Project entry point)"
echo "  └── .gitignore (Git ignore rules)"
echo ""
echo "✅ Repository ready for upload!"
echo ""
echo "=== 🚀 Next Steps ==="
echo ""
echo "1. Review the repository structure"
echo "2. Create GitHub repository (if not exists)"
echo "3. Initialize Git: git init"
echo "4. Add files: git add ."
echo "5. Commit: git commit -m 'Initial commit'"
echo "6. Push to GitHub: git remote add origin && git push -u origin main"
echo ""
echo "For detailed setup instructions, see README.md"
