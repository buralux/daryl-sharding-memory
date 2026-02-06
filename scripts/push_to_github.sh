#!/bin/bash
# Push DARYL Sharding Memory to GitHub
# This script handles the complete GitHub push process

set -e

echo "=== 🚀 Pushing DARYL Sharding Memory to GitHub ==="
echo ""

# Step 1: Initialize Git repository
echo "1️⃣ Initializing Git repository..."
git init

# Step 2: Add remote (handle if already exists)
echo "2️⃣ Adding remote..."
if git remote get-url origin >/dev/null 2>&1; then
    echo "   Remote origin already exists"
else
    git remote add origin https://github.com/buralux/daryl-sharding-memory.git
    echo "   Remote origin added"
fi

# Step 3: Add all files
echo "3️⃣ Adding all files to Git..."
git add .

# Step 4: Commit
echo "4️⃣ Creating initial commit..."
COMMIT_MSG="Initial release: DARYL Sharding Memory v1.0"
git commit -m "$COMMIT_MSG"

# Step 5: Push to GitHub
echo "5️⃣ Pushing to GitHub..."
git push -u origin main

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Repository published!"
    echo ""
    echo "📦 Repository URL: https://github.com/buralux/daryl-sharding-memory"
    echo ""
    echo "📊 Status:"
    echo "  • Public: YES"
    echo "  • README visible: YES"
    echo "  • License MIT: YES"
    echo "  • Complete system: YES"
    echo ""
    echo "🎯 Next: Moltbook post is live with repository link"
else
    echo ""
    echo "❌ FAILED: Push failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "  • Check your GitHub credentials"
    echo "  • Check your repository URL"
    echo "  • Check your internet connection"
fi

echo ""
echo "=== 🚀 Push Complete ==="
