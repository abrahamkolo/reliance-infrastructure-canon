#!/bin/bash
# ============================================================
# MW INFRASTRUCTURE CANON — ZENODO DEPLOYMENT SCRIPT
# ============================================================
#
# PREREQUISITES:
#   1. Zenodo account at zenodo.org
#   2. Personal Access Token from zenodo.org/account/settings/applications/
#      (Scope: deposit:write, deposit:actions)
#   3. GitHub deployment completed first
#
# USAGE:
#   chmod +x deploy-zenodo.sh
#   export ZENODO_TOKEN="your_token_here"
#   ./deploy-zenodo.sh
#
# ESTIMATED TIME: 20 minutes
# ============================================================

set -e

echo "============================================"
echo "MW INFRASTRUCTURE CANON — ZENODO DEPLOYMENT"
echo "============================================"
echo ""

# ---- CHECK TOKEN ----
if [ -z "$ZENODO_TOKEN" ]; then
    echo "ERROR: ZENODO_TOKEN environment variable not set."
    echo ""
    echo "To get your token:"
    echo "  1. Go to https://zenodo.org/account/settings/applications/"
    echo "  2. Click 'New token'"
    echo "  3. Name: 'Reliance Infrastructure Canon'"
    echo "  4. Scopes: deposit:write, deposit:actions"
    echo "  5. Run: export ZENODO_TOKEN=\"your_token_here\""
    exit 1
fi

ZENODO_API="https://zenodo.org/api"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ---- STEP 1: Create Zenodo Deposit ----
echo "[1/5] Creating Zenodo deposit..."
DEPOSIT=$(curl -s -X POST "$ZENODO_API/deposit/depositions" \
    -H "Authorization: Bearer $ZENODO_TOKEN" \
    -H "Content-Type: application/json" \
    -d @"$SCRIPT_DIR/metadata/zenodo-metadata.json")

DEPOSIT_ID=$(echo "$DEPOSIT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
BUCKET_URL=$(echo "$DEPOSIT" | python3 -c "import sys,json; print(json.load(sys.stdin)['links']['bucket'])")

echo "  → Deposit ID: $DEPOSIT_ID"
echo "  → Bucket URL: $BUCKET_URL"

# ---- STEP 2: Create Archive Package ----
echo "[2/5] Creating archive package..."
cd "$SCRIPT_DIR"
tar -czf "/tmp/reliance-infrastructure-canon-v2.0.0.tar.gz" \
    --exclude='.git' \
    --exclude='deploy-*.sh' \
    documents/ verification/ metadata/ README.md LICENSE

echo "  → Archive created: $(du -h /tmp/reliance-infrastructure-canon-v2.0.0.tar.gz | cut -f1)"

# ---- STEP 3: Upload Archive to Zenodo ----
echo "[3/5] Uploading archive to Zenodo..."
curl -s -X PUT "$BUCKET_URL/reliance-infrastructure-canon-v2.0.0.tar.gz" \
    -H "Authorization: Bearer $ZENODO_TOKEN" \
    -H "Content-Type: application/gzip" \
    --data-binary @"/tmp/reliance-infrastructure-canon-v2.0.0.tar.gz" > /dev/null

echo "  → Upload complete"

# ---- STEP 4: Upload Master Index separately (for quick reference) ----
echo "[4/5] Uploading Master Index..."
curl -s -X PUT "$BUCKET_URL/master-index.json" \
    -H "Authorization: Bearer $ZENODO_TOKEN" \
    -H "Content-Type: application/json" \
    --data-binary @"$SCRIPT_DIR/verification/master-index.json" > /dev/null

echo "  → Master Index uploaded"

# ---- STEP 5: Publish ----
echo "[5/5] Publishing deposit..."
PUBLISH=$(curl -s -X POST "$ZENODO_API/deposit/depositions/$DEPOSIT_ID/actions/publish" \
    -H "Authorization: Bearer $ZENODO_TOKEN")

DOI=$(echo "$PUBLISH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('doi', 'PENDING'))")
RECORD_URL=$(echo "$PUBLISH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('links',{}).get('record_html', 'PENDING'))")

echo ""
echo "============================================"
echo "✓ ZENODO DEPLOYMENT COMPLETE"
echo "============================================"
echo ""
echo "  DOI:        $DOI"
echo "  Record URL: $RECORD_URL"
echo "  Deposit ID: $DEPOSIT_ID"
echo ""
echo "POST-DEPLOYMENT CHECKLIST:"
echo "  [ ] Verify DOI resolves correctly"
echo "  [ ] Create Zenodo community 'reliance-infrastructure' (if not exists)"
echo "  [ ] Add DOI badge to GitHub README"
echo "  [ ] Record DOI in Master Index"
echo "  [ ] Verify archive downloadable"
echo ""
echo "BOTH DEPLOYMENTS COMPLETE."
echo "GitHub: Primary canonical repository (live)"
echo "Zenodo: Academic archival with DOI (permanent)"
echo ""
echo "The system now exists independent of any person."

# ---- Cleanup ----
rm -f /tmp/reliance-infrastructure-canon-v2.0.0.tar.gz
