#!/usr/bin/env python3
"""
Batch upload 39 MW Canon documents to Zenodo with individual DOIs.
Requires: ZENODO_TOKEN environment variable set.
Run from the reliance-infrastructure-canon repo root.

Usage:
    export ZENODO_TOKEN="your_token_here"
    python zenodo_batch_upload.py
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN")
if not ZENODO_TOKEN:
    print("ERROR: Set ZENODO_TOKEN environment variable")
    print("Get a token from: https://zenodo.org/account/settings/applications/")
    sys.exit(1)

BASE = "https://zenodo.org/api/deposit/depositions"
HEADERS = {"Authorization": "Bearer {}".format(ZENODO_TOKEN)}
MASTER_DOI = "10.5281/zenodo.18707171"
COMMUNITY_ID = "reliance-infrastructure"

# Load master index for document titles
with open("verification/master-index.json") as f:
    master = json.load(f)
doc_metadata = master.get("documents", {})

# Find all canonical document files across layer directories
doc_dir = Path("documents")
doc_files = sorted(doc_dir.rglob("*.txt"))

print("Found {} documents to upload".format(len(doc_files)))
if len(doc_files) != 39:
    print("WARNING: Expected 39 documents, found {}".format(len(doc_files)))

results = []
for i, filepath in enumerate(doc_files, 1):
    # Extract document ID from filename (e.g., DOC-001 from DOC-001_MW-CANON_v2.1.0.txt)
    fname = filepath.name
    doc_id = fname.split("_")[0]  # DOC-001, DOC-002, etc.
    doc_num = doc_id.replace("DOC-", "")

    # Get title from master index if available
    meta = doc_metadata.get(doc_id, {})
    doc_title = meta.get("title", fname.replace("_", " ").replace(".txt", ""))
    layer = meta.get("layer", "unknown")

    print("\n--- Uploading {}/{}: {} ({}) ---".format(i, len(doc_files), doc_id, doc_title))

    # 1. Create empty deposit
    r = requests.post(BASE, json={}, headers=HEADERS)
    if r.status_code != 201:
        print("  ERROR creating deposit: {} {}".format(r.status_code, r.text[:200]))
        continue
    dep = r.json()
    dep_id = dep["id"]
    bucket_url = dep["links"]["bucket"]

    # 2. Upload file
    with open(filepath, "rb") as f:
        r = requests.put(
            "{}/{}".format(bucket_url, filepath.name),
            data=f,
            headers={"Authorization": "Bearer {}".format(ZENODO_TOKEN)}
        )
    if r.status_code not in (200, 201):
        print("  ERROR uploading file: {} {}".format(r.status_code, r.text[:200]))
        continue

    # 3. Set metadata
    title = "MW Canon Document {}: {}".format(doc_num, doc_title)

    metadata = {
        "metadata": {
            "title": title,
            "upload_type": "publication",
            "publication_type": "technicalnote",
            "description": (
                "Canonical constitutional document {} of the MW Infrastructure Stack "
                "(MW-Omega v2.0.0). Layer: {}. Part of the 39-document Reliance "
                "Infrastructure Canon. SHA3-512 hashed and Ed25519 signed."
            ).format(doc_num, layer),
            "creators": [{"name": "Kolo, Abraham J"}],
            "license": "cc-by-nd-4.0",
            "keywords": [
                "institutional governance",
                "constitutional authority",
                "deterministic systems",
                "MW Canon",
                "reliance infrastructure"
            ],
            "related_identifiers": [
                {
                    "identifier": MASTER_DOI,
                    "relation": "isPartOf",
                    "scheme": "doi"
                }
            ],
            "communities": [{"identifier": COMMUNITY_ID}],
            "notes": (
                "This document is part of the MW Infrastructure Stack, a 39-document "
                "institutional governance framework. Full stack available at: "
                "https://doi.org/{}".format(MASTER_DOI)
            )
        }
    }

    r = requests.put("{}/{}".format(BASE, dep_id), json=metadata, headers=HEADERS)
    if r.status_code != 200:
        print("  ERROR setting metadata: {} {}".format(r.status_code, r.text[:200]))
        continue

    # 4. Publish
    r = requests.post("{}/{}/actions/publish".format(BASE, dep_id), headers=HEADERS)
    if r.status_code != 202:
        print("  ERROR publishing: {} {}".format(r.status_code, r.text[:200]))
        continue

    doi = r.json().get("doi", "unknown")
    print("  Published: DOI {}".format(doi))
    results.append({
        "document_id": doc_id,
        "document": filepath.name,
        "title": doc_title,
        "layer": layer,
        "zenodo_id": dep_id,
        "doi": doi,
        "url": "https://doi.org/{}".format(doi)
    })

    # Rate limit: wait 2 seconds between uploads
    time.sleep(2)

# Save results
output_file = "verification/per-document-dois.json"
with open(output_file, "w") as f:
    json.dump({
        "master_doi": MASTER_DOI,
        "total_uploaded": len(results),
        "total_expected": len(doc_files),
        "documents": results
    }, f, indent=2)

print("\n=== COMPLETE ===")
print("Uploaded: {}/{}".format(len(results), len(doc_files)))
print("Results saved to: {}".format(output_file))
print("\nIMPORTANT: Revoke your Zenodo API token and generate a new one.")
print("Tokens: https://zenodo.org/account/settings/applications/")
