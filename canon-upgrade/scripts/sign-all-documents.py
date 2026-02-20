#!/usr/bin/env python3
"""
Sign all 39 canonical documents with Ed25519.
Generates verification/signatures.json with signatures for each document.

Requirements: pip install cryptography
Usage: python sign-all-documents.py
"""

import json
import os
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    import base64
except ImportError:
    print("Installing cryptography library...")
    os.system(f"{sys.executable} -m pip install cryptography")
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    import base64

def main():
    repo_root = Path(".")
    key_path = repo_root / "reliance-signing-key.pem"
    pub_path = repo_root / "reliance-signing-key.pub"
    hashes_path = repo_root / "verification" / "hashes.json"
    sigs_path = repo_root / "verification" / "signatures.json"
    
    # Check for existing key or generate new one
    if key_path.exists():
        print(f"Loading existing signing key from {key_path}")
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    else:
        print("Generating new Ed25519 signing key pair...")
        private_key = Ed25519PrivateKey.generate()
        
        # Save private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(key_path, "wb") as f:
            f.write(pem_private)
        print(f"Private key saved to {key_path}")
        print(">>> SECURE THIS FILE. Never commit to repository. <<<")
        
        # Save public key
        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(pub_path, "wb") as f:
            f.write(pem_public)
        print(f"Public key saved to {pub_path}")
    
    # Load hashes
    if not hashes_path.exists():
        print(f"ERROR: {hashes_path} not found. Run from repository root.")
        sys.exit(1)
    
    with open(hashes_path, "r") as f:
        hashes = json.load(f)
    
    # Sign each document's hash
    signatures = {
        "algorithm": "Ed25519",
        "public_key_file": "verification/reliance-signing-key.pub",
        "signing_entity": "Reliance Infrastructure Holdings LLC",
        "signing_date": None,  # Will be set below
        "documents": {}
    }
    
    from datetime import datetime, timezone
    signatures["signing_date"] = datetime.now(timezone.utc).isoformat()
    
    count = 0
    for doc_name, doc_hash in hashes.items():
        # Sign the hash bytes (UTF-8 encoded hex string)
        hash_bytes = doc_hash.encode("utf-8")
        signature = private_key.sign(hash_bytes)
        sig_b64 = base64.b64encode(signature).decode("utf-8")
        
        signatures["documents"][doc_name] = {
            "sha3_512": doc_hash,
            "ed25519_signature": sig_b64
        }
        count += 1
        print(f"  Signed: {doc_name}")
    
    # Also sign the master index itself
    master_index_path = repo_root / "verification" / "master-index.json"
    if master_index_path.exists():
        with open(master_index_path, "rb") as f:
            mi_content = f.read()
        import hashlib
        mi_hash = hashlib.sha3_512(mi_content).hexdigest()
        mi_sig = private_key.sign(mi_hash.encode("utf-8"))
        signatures["master_index"] = {
            "sha3_512": mi_hash,
            "ed25519_signature": base64.b64encode(mi_sig).decode("utf-8")
        }
        print(f"  Signed: master-index.json")
        count += 1
    
    # Write signatures
    with open(sigs_path, "w") as f:
        json.dump(signatures, f, indent=2)
    
    print(f"\n{count} documents signed.")
    print(f"Signatures written to {sigs_path}")
    print(f"\nNEXT STEPS:")
    print(f"  1. Copy reliance-signing-key.pub to verification/")
    print(f"  2. git add verification/signatures.json verification/reliance-signing-key.pub")
    print(f"  3. git commit -S -m 'SYSTEM-DEPLOY: Ed25519 signatures for all documents'")
    print(f"  4. git push origin main")
    print(f"  5. SECURE reliance-signing-key.pem (DO NOT COMMIT)")

if __name__ == "__main__":
    main()
