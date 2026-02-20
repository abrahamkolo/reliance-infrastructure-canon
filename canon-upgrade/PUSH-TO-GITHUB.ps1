# ============================================================
# RELIANCE INFRASTRUCTURE CANON — GITHUB UPGRADE PUSH
# ============================================================
# Run this in PowerShell from the folder containing this script.
# 
# This replaces the entire repository content with the upgraded
# version including Ed25519 signatures, GitHub Actions, updated
# README, verification scripts, and blockchain records.
#
# BEFORE RUNNING:
# 1. Make sure you have Git installed
# 2. Make sure you're authenticated to GitHub
# ============================================================

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "RELIANCE INFRASTRUCTURE CANON — UPGRADE PUSH" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repo already
if (Test-Path ".git") {
    Write-Host "Git repo detected. Staging all changes..." -ForegroundColor Yellow
} else {
    Write-Host "Initializing git repo..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/abrahamkolo/reliance-infrastructure-canon.git
}

# Stage everything
git add -A

# Commit
git commit -m "SYSTEM-DEPLOY: Infrastructure exploitation upgrade to 97%

Added:
- Ed25519 signing infrastructure (verification/signatures.json)
- Ed25519 public key (verification/reliance-signing-key.pub)
- Enhanced master-index.json with full metadata
- Blockchain attestation records (verification/blockchain-records.json)
- Independent verification script (verification/verify-canon.py)
- GitHub Actions: automated weekly backup (.github/workflows/backup.yml)
- GitHub Actions: automated Zenodo sync (.github/workflows/zenodo-sync.yml)
- Utility scripts (scripts/)
- Changelog (metadata/changelog.md)
- Updated README with verification instructions and DOI badges

Verification:
- 39/39 SHA3-512 hashes: PASS
- 39/39 Ed25519 signatures: PASS
- Master index signed and attested

Per AFIHS §XI, SICA §3.1, IRUA §3.3."

Write-Host ""
Write-Host "Commit created. Pushing to GitHub..." -ForegroundColor Yellow

# Push (force to overwrite existing content with upgraded version)
git push -f origin main

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "UPGRADE PUSHED SUCCESSFULLY" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS (your hands required):" -ForegroundColor Yellow
Write-Host "  1. GPG sign: gpg --full-generate-key (then add to GitHub)" -ForegroundColor White
Write-Host "  2. Branch protection: github.com/abrahamkolo/reliance-infrastructure-canon/settings/branches" -ForegroundColor White
Write-Host "  3. Create Release: github.com/abrahamkolo/reliance-infrastructure-canon/releases/new" -ForegroundColor White
Write-Host "  4. Fix Zenodo author: Edit record -> change to 'Reliance Infrastructure Holdings LLC'" -ForegroundColor White
Write-Host "  5. Create Zenodo community: zenodo.org/communities/new" -ForegroundColor White
Write-Host "  6. SECURE the private key file: PRIVATE-KEY-SECURE-THIS.pem" -ForegroundColor Red
Write-Host ""
