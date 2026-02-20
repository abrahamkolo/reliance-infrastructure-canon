#!/bin/bash
# ============================================================
# MW INFRASTRUCTURE CANON — GITHUB DEPLOYMENT SCRIPT
# ============================================================
# 
# PREREQUISITES:
#   1. GitHub account with repository created:
#      github.com/reliance-infrastructure/reliance-infrastructure-canon
#   2. Git installed locally
#   3. GPG key generated for commit signing
#   4. GitHub Personal Access Token (PAT) with repo scope
#
# USAGE:
#   chmod +x deploy-github.sh
#   ./deploy-github.sh
#
# ESTIMATED TIME: 15 minutes
# ============================================================

set -e

echo "============================================"
echo "MW INFRASTRUCTURE CANON — GITHUB DEPLOYMENT"
echo "============================================"
echo ""

# ---- STEP 1: Initialize Git Repository ----
echo "[1/7] Initializing Git repository..."
cd "$(dirname "$0")"
git init
git checkout -b main

# ---- STEP 2: Configure Git Identity ----
echo "[2/7] Configuring Git identity..."
echo "  → Set your identity before proceeding:"
echo "    git config user.name 'MW Infrastructure Authority'"
echo "    git config user.email 'canonical@mw-infrastructure.org'"
echo ""
echo "  → For GPG signing (recommended):"
echo "    git config commit.gpgsign true"
echo "    git config user.signingkey YOUR_GPG_KEY_ID"
echo ""
read -p "Press Enter after configuring identity..."

# ---- STEP 3: Stage All Files ----
echo "[3/7] Staging all canonical documents..."
git add .
echo "  → $(git diff --cached --stat | tail -1)"

# ---- STEP 4: Initial Commit ----
echo "[4/7] Creating initial signed commit..."
git commit -m "feat: Initial canonical release — MW Infrastructure Stack v2.0.0

39 constitutional documents, all at 100/100 institutional grade.
SHA3-512 hashes generated for full stack (2.2 MB).
Infrastructure Master Index (DOC-000) included.
MW Canon at v2.1.0; all other documents at v2.0.0.

Document-bound. Founder-irrelevant. Run-Only."

# ---- STEP 5: Tag Release ----
echo "[5/7] Creating version tag..."
git tag -a v2.0.0 -m "MW Infrastructure Stack v2.0.0 — Initial Canonical Release

39 documents. SHA3-512 verified. CC BY-ND 4.0.
See verification/master-index.json for complete inventory."

# ---- STEP 6: Add Remote ----
echo "[6/7] Adding GitHub remote..."
echo "  → Enter your repository URL:"
echo "    Example: https://github.com/reliance-infrastructure/reliance-infrastructure-canon.git"
read -p "Repository URL: " REPO_URL
git remote add origin "$REPO_URL"

# ---- STEP 7: Push ----
echo "[7/7] Pushing to GitHub..."
git push -u origin main
git push origin v2.0.0

echo ""
echo "============================================"
echo "✓ GITHUB DEPLOYMENT COMPLETE"
echo "============================================"
echo ""
echo "POST-DEPLOYMENT CHECKLIST:"
echo "  [ ] Enable branch protection on 'main'"
echo "  [ ] Require signed commits"
echo "  [ ] Disable force push"
echo "  [ ] Enable 2FA on GitHub account"
echo "  [ ] Create GitHub Release from v2.0.0 tag"
echo "  [ ] Verify all 39 documents accessible"
echo "  [ ] Confirm hashes.json matches local copies"
echo ""
echo "NEXT: Run deploy-zenodo.sh for academic archival"
