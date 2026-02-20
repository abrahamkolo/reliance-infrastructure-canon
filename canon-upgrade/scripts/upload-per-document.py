#!/usr/bin/env python3
"""
Upload each of the 39 canonical documents as individual Zenodo records.
Each document gets its own DOI for independent citation.

Requirements: pip install requests
Usage: 
  Set ZENODO_TOKEN environment variable first.
  python upload-per-document.py
"""

import json
import os
import sys
import time

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests")
    import requests

ZENODO_API = "https://zenodo.org/api"
PARENT_DOI = "10.5281/zenodo.18707171"

# Document metadata for all 39 docs
DOCUMENTS = [
    {"id": "DOC-001", "file_prefix": "DOC-001", "title": "MW Canon (MW-Omega)", "layer": "Layer 0 — Supreme Constitutional Authority", "version": "2.1.0"},
    {"id": "DOC-002", "file_prefix": "DOC-002", "title": "Layer Architecture & Non-Escalation Charter", "layer": "Layer 1 — Structural Charter", "version": "2.0.0"},
    {"id": "DOC-003", "file_prefix": "DOC-003", "title": "Determinism & Run-Only Enforcement Law", "layer": "Layer 1 — Structural Charter", "version": "2.0.0"},
    {"id": "DOC-004", "file_prefix": "DOC-004", "title": "Issuance & Decision Admissibility Charter", "layer": "Layer 2 — Operational Charter", "version": "2.0.0"},
    {"id": "DOC-005", "file_prefix": "DOC-005", "title": "Pricing & Fee Primitives Charter", "layer": "Layer 2 — Operational Charter", "version": "2.0.0"},
    {"id": "DOC-006", "file_prefix": "DOC-006", "title": "External Non-Advice & Safe-Interface Clause", "layer": "Layer 2 — Operational Charter", "version": "2.0.0"},
    {"id": "DOC-007", "file_prefix": "DOC-007", "title": "IRUA Constitution — Institutional Reliance & Usage Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-008", "file_prefix": "DOC-008", "title": "GEAA Constitution — Global Evidence Admissibility Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-009", "file_prefix": "DOC-009", "title": "CivicHab Constitution — Civic Habitat Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-010", "file_prefix": "DOC-010", "title": "GCPA Constitution — Global Capital & Portfolio Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-011", "file_prefix": "DOC-011", "title": "PMOA Constitution — Personal Mastery & Optimization Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-012", "file_prefix": "DOC-012", "title": "EWA Constitution — Eternal Works Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-013", "file_prefix": "DOC-013", "title": "EPA Constitution — Eternal Publishing Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-014", "file_prefix": "DOC-014", "title": "EFAA Constitution — Eternal Fine Art Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-015", "file_prefix": "DOC-015", "title": "UPDIUD Constitution — Universal Private DIUD Cell Ecosystem", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-016", "file_prefix": "DOC-016", "title": "SICA Constitution — Standards Issuance & Custody Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-017", "file_prefix": "DOC-017", "title": "IATA Constitution — Independent Arbitration & Tribunals Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-018", "file_prefix": "DOC-018", "title": "DRFA Constitution — Dispute Resolution Finality Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-019", "file_prefix": "DOC-019", "title": "CRTA Constitution — Crisis Response & Transition Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-020", "file_prefix": "DOC-020", "title": "IPPA Constitution — Intellectual Property Permanence Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-021", "file_prefix": "DOC-021", "title": "CSCA Constitution — Contractual Succession Continuity Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-022", "file_prefix": "DOC-022", "title": "DCPA Constitution — Data Custody Perpetuity Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-023", "file_prefix": "DOC-023", "title": "FAPA Constitution — Foundational Assets Permanence Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-024", "file_prefix": "DOC-024", "title": "Issuance Primitives Specification (IPS)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-025", "file_prefix": "DOC-025", "title": "Binary Decision Trees Master (BDTM)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-026", "file_prefix": "DOC-026", "title": "Artifact Formatting, ID & Hashing Standard (AFIHS)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-027", "file_prefix": "DOC-027", "title": "Custody & Chain-of-Custody Protocol (CCOCP)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-028", "file_prefix": "DOC-028", "title": "Registry Architecture Specification (RAS)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-029", "file_prefix": "DOC-029", "title": "Multi-Jurisdiction Mirroring Protocol (MJMP)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-030", "file_prefix": "DOC-030", "title": "Succession & Continuity Transfer Protocol (SCTP)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-031", "file_prefix": "DOC-031", "title": "Citation Authenticity Protocol (CAP)", "layer": "Layer 4 — Specification", "version": "2.0.0"},
    {"id": "DOC-032", "file_prefix": "DOC-032", "title": "GCRA Constitution — Global Capital Reliance Authority", "layer": "Layer 3 — Authority Constitution", "version": "2.0.0"},
    {"id": "DOC-033", "file_prefix": "DOC-033", "title": "Reliance Infrastructure Exchange (RIX)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
    {"id": "DOC-034", "file_prefix": "DOC-034", "title": "Reliance Ordering Doctrine (ROD)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
    {"id": "DOC-035", "file_prefix": "DOC-035", "title": "Cross-Authority Conflict Avoidance Protocol (CACAP)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
    {"id": "DOC-036", "file_prefix": "DOC-036", "title": "Collision Resolution Matrix (CRM)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
    {"id": "DOC-037", "file_prefix": "DOC-037", "title": "Pre-Reliance Preparation Matrix (PRPM)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
    {"id": "DOC-038", "file_prefix": "DOC-038", "title": "Binary Gates & Dormancy Protocol (BGDP)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
    {"id": "DOC-039", "file_prefix": "DOC-039", "title": "Execution Bridge Protocol (EBP)", "layer": "Layer 4 — Exchange System", "version": "2.0.0"},
]

def get_token():
    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        print("ERROR: Set ZENODO_TOKEN environment variable first.")
        print("  PowerShell: $env:ZENODO_TOKEN=\"your_token\"")
        sys.exit(1)
    return token

def find_document_file(doc_id):
    """Find the .txt file for a document in the documents/ subdirectories."""
    docs_dir = "documents"
    if not os.path.exists(docs_dir):
        print(f"ERROR: {docs_dir}/ directory not found. Run from repository root.")
        sys.exit(1)
    
    for root, dirs, files in os.walk(docs_dir):
        for f in files:
            if f.startswith(doc_id):
                return os.path.join(root, f)
    return None

def create_deposit(token, doc):
    """Create a new Zenodo deposit for a document."""
    headers = {"Content-Type": "application/json"}
    params = {"access_token": token}
    
    metadata = {
        "metadata": {
            "title": f"{doc['id']} — {doc['title']}",
            "upload_type": "publication",
            "publication_type": "workingpaper",
            "description": (
                f"<p>{doc['title']}</p>"
                f"<p>{doc['layer']}</p>"
                f"<p>Part of the Reliance Infrastructure Canon — a 39-document constitutional "
                f"framework for institutional-grade governance. SHA3-512 verified. "
                f"Deterministic, document-bound, founder-irrelevant.</p>"
                f"<p>Version: {doc['version']}</p>"
            ),
            "creators": [{"name": "Reliance Infrastructure Holdings LLC"}],
            "license": "cc-by-nd-4.0",
            "version": doc["version"],
            "keywords": [
                "institutional governance",
                "constitutional infrastructure", 
                "compliance framework",
                "SHA3-512",
                "document-bound authority",
                doc["layer"].split(" — ")[0] if " — " in doc["layer"] else doc["layer"]
            ],
            "related_identifiers": [
                {
                    "identifier": PARENT_DOI,
                    "relation": "isPartOf",
                    "scheme": "doi"
                },
                {
                    "identifier": "https://github.com/abrahamkolo/reliance-infrastructure-canon",
                    "relation": "isSupplementedBy",
                    "scheme": "url"
                }
            ],
            "language": "eng",
            "notes": f"Canonical document {doc['id']} from the Reliance Infrastructure Stack."
        }
    }
    
    r = requests.post(f"{ZENODO_API}/deposit/depositions", 
                      params=params, json=metadata, headers=headers)
    
    if r.status_code != 201:
        print(f"  ERROR creating deposit for {doc['id']}: {r.status_code} {r.text}")
        return None
    
    return r.json()

def upload_file(token, deposit_id, bucket_url, filepath):
    """Upload a file to a Zenodo deposit."""
    params = {"access_token": token}
    filename = os.path.basename(filepath)
    
    with open(filepath, "rb") as f:
        r = requests.put(f"{bucket_url}/{filename}", 
                        params=params, data=f)
    
    if r.status_code not in (200, 201):
        print(f"  ERROR uploading file: {r.status_code} {r.text}")
        return False
    return True

def publish_deposit(token, deposit_id):
    """Publish a Zenodo deposit."""
    params = {"access_token": token}
    r = requests.post(f"{ZENODO_API}/deposit/depositions/{deposit_id}/actions/publish",
                      params=params)
    
    if r.status_code != 202:
        print(f"  ERROR publishing: {r.status_code} {r.text}")
        return None
    return r.json()

def main():
    token = get_token()
    
    print("=" * 60)
    print("ZENODO PER-DOCUMENT UPLOAD")
    print(f"Parent DOI: {PARENT_DOI}")
    print(f"Documents: {len(DOCUMENTS)}")
    print("=" * 60)
    
    doi_mapping = {}
    errors = []
    
    for i, doc in enumerate(DOCUMENTS):
        print(f"\n[{i+1}/{len(DOCUMENTS)}] {doc['id']} — {doc['title']}")
        
        # Find the file
        filepath = find_document_file(doc["id"])
        if not filepath:
            print(f"  WARNING: File not found for {doc['id']}, skipping.")
            errors.append(doc["id"])
            continue
        
        print(f"  File: {filepath}")
        
        # Create deposit
        deposit = create_deposit(token, doc)
        if not deposit:
            errors.append(doc["id"])
            continue
        
        deposit_id = deposit["id"]
        bucket_url = deposit["links"]["bucket"]
        print(f"  Deposit created: {deposit_id}")
        
        # Upload file
        if not upload_file(token, deposit_id, bucket_url, filepath):
            errors.append(doc["id"])
            continue
        print(f"  File uploaded.")
        
        # Publish
        published = publish_deposit(token, deposit_id)
        if not published:
            errors.append(doc["id"])
            continue
        
        doi = published["doi"]
        doi_mapping[doc["id"]] = {
            "doi": doi,
            "url": f"https://doi.org/{doi}",
            "zenodo_id": published["id"],
            "title": doc["title"]
        }
        print(f"  PUBLISHED: DOI {doi}")
        
        # Rate limit: Zenodo recommends max 60 requests/minute
        time.sleep(2)
    
    # Save DOI mapping
    output_path = "metadata/zenodo-dois.json"
    os.makedirs("metadata", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "parent_doi": PARENT_DOI,
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "documents": doi_mapping
        }, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {len(doi_mapping)}/{len(DOCUMENTS)} documents published")
    if errors:
        print(f"ERRORS: {len(errors)} documents failed: {', '.join(errors)}")
    print(f"DOI mapping saved to {output_path}")
    print(f"\nNext: git add {output_path} && git commit -S -m 'SYSTEM-DEPLOY: Per-document Zenodo DOIs'")

if __name__ == "__main__":
    main()
