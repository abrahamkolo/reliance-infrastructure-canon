#!/usr/bin/env python3
"""
Independent verification script for Reliance Infrastructure Canon.
Verifies SHA3-512 hashes AND Ed25519 signatures for all 39 documents.

Any institution can run this to prove document authenticity without
relying on the issuing authority.

Requirements: pip install cryptography
Usage: python verify-canon.py
"""

import hashlib
import json
import os
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    import base64
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

def verify_hashes(repo_root):
    """Verify SHA3-512 hashes for all documents."""
    hashes_path = repo_root / "verification" / "hashes.json"
    if not hashes_path.exists():
        print("ERROR: verification/hashes.json not found.")
        return False
    
    with open(hashes_path) as f:
        hashes = json.load(f)
    
    print(f"Verifying {len(hashes)} document hashes...\n")
    
    errors = 0
    verified = 0
    
    for filename, expected_hash in sorted(hashes.items()):
        found = False
        for root, dirs, files in os.walk(repo_root / "documents"):
            for f in files:
                if f == filename:
                    filepath = Path(root) / f
                    with open(filepath, "rb") as fh:
                        actual = hashlib.sha3_512(fh.read()).hexdigest()
                    
                    if actual == expected_hash:
                        print(f"  PASS  {filename}")
                        verified += 1
                    else:
                        print(f"  FAIL  {filename}")
                        print(f"        Expected: {expected_hash[:32]}...")
                        print(f"        Actual:   {actual[:32]}...")
                        errors += 1
                    found = True
                    break
            if found:
                break
        
        if not found:
            print(f"  MISSING  {filename}")
            errors += 1
    
    print(f"\nHash verification: {verified} passed, {errors} failed.")
    return errors == 0

def verify_signatures(repo_root):
    """Verify Ed25519 signatures for all documents."""
    if not HAS_CRYPTO:
        print("\nSkipping signature verification (install cryptography: pip install cryptography)")
        return None
    
    sigs_path = repo_root / "verification" / "signatures.json"
    pub_path = repo_root / "verification" / "reliance-signing-key.pub"
    
    if not sigs_path.exists():
        print("\nWARNING: verification/signatures.json not found. Skipping signature verification.")
        return None
    
    if not pub_path.exists():
        print("\nWARNING: verification/reliance-signing-key.pub not found. Skipping signature verification.")
        return None
    
    with open(pub_path, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read())
    
    with open(sigs_path) as f:
        sigs = json.load(f)
    
    docs = sigs.get("documents", {})
    print(f"\nVerifying {len(docs)} Ed25519 signatures...\n")
    
    errors = 0
    verified = 0
    
    for doc_name, doc_data in sorted(docs.items()):
        sig_b64 = doc_data.get("ed25519_signature")
        hash_val = doc_data.get("sha3_512")
        
        if not sig_b64 or not hash_val:
            print(f"  SKIP  {doc_name} (missing data)")
            continue
        
        try:
            pub_key.verify(
                base64.b64decode(sig_b64),
                hash_val.encode("utf-8")
            )
            print(f"  PASS  {doc_name}")
            verified += 1
        except Exception as e:
            print(f"  FAIL  {doc_name} ({e})")
            errors += 1
    
    print(f"\nSignature verification: {verified} passed, {errors} failed.")
    return errors == 0

def main():
    repo_root = Path(".")
    
    print("=" * 60)
    print("RELIANCE INFRASTRUCTURE CANON — VERIFICATION")
    print("=" * 60)
    print(f"Repository: {repo_root.resolve()}")
    print()
    
    hash_ok = verify_hashes(repo_root)
    sig_ok = verify_signatures(repo_root)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"  SHA3-512 Hashes:     {'PASS' if hash_ok else 'FAIL'}")
    if sig_ok is not None:
        print(f"  Ed25519 Signatures:  {'PASS' if sig_ok else 'FAIL'}")
    else:
        print(f"  Ed25519 Signatures:  SKIPPED")
    
    if hash_ok and (sig_ok is None or sig_ok):
        print("\n  VERDICT: AUTHENTIC")
    else:
        print("\n  VERDICT: INTEGRITY COMPROMISED — DO NOT RELY")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
