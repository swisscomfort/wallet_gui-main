#!/bin/bash
#
# GitHub Upload Script
# 
# ANLEITUNG:
# 1. Erstellen Sie das Repository auf GitHub: wallet-forensic-scanner
# 2. Ersetzen Sie YOUR_USERNAME unten durch Ihren GitHub-Benutzernamen
# 3. Führen Sie dieses Skript aus: bash upload_to_github.sh
#

# KONFIGURATION - BITTE ANPASSEN:
GITHUB_USERNAME="YOUR_USERNAME"  # <-- Hier Ihren GitHub-Benutzernamen eintragen
REPO_NAME="wallet-forensic-scanner"

# Repository URL
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "🚀 Uploading wallet-forensic-scanner to GitHub..."
echo "Repository: ${REPO_URL}"
echo ""

# Prüfen ob Git-Repository existiert
if [ ! -d ".git" ]; then
    echo "❌ Error: Kein Git-Repository gefunden!"
    exit 1
fi

# Remote hinzufügen
echo "📡 Adding GitHub remote..."
git remote remove origin 2>/dev/null || true  # Remove existing remote if any
git remote add origin "${REPO_URL}"

# Branch auf 'main' setzen
echo "🌿 Setting branch to 'main'..."
git branch -M main

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Repository uploaded to GitHub!"
    echo "🔗 Repository URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Visit your repository on GitHub"
    echo "   2. Add topics: forensics, cryptocurrency, wallet-recovery, pyqt6, cli-tool"
    echo "   3. Enable Issues, Wiki, Discussions"
    echo "   4. Create release v2.0.0"
    echo ""
else
    echo ""
    echo "❌ ERROR: Push failed!"
    echo "Please check:"
    echo "   - GitHub repository exists: ${REPO_URL}"
    echo "   - You have push permissions"
    echo "   - GitHub username is correct: ${GITHUB_USERNAME}"
fi