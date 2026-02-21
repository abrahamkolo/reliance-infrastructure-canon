import hashlib, json, os, sys
from datetime import datetime, timezone

docs_dir = "documents"
manifest = {
    "manifest_id": "MW-MANIFEST-v2.0.0",
    "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "algorithm": "SHA3-512",
    "algorithm_spec": "NIST FIPS 202 (Keccak)",
    "total_documents": 0,
    "gpg_signing_key": "EB937371B8993E99",
    "governing_entity": "Reliance Infrastructure Holdings LLC",
    "status": "SEALED",
    "documents": []
}

# Walk subdirectories in sorted order
all_files = []
for root, dirs, files in os.walk(docs_dir):
    dirs.sort()
    for fname in sorted(files):
        if fname.endswith('.txt'):
            all_files.append((root, fname))

hashes_lines = []
hashes_lines.append("MW Infrastructure Stack - SHA3-512 Hash Verification")
hashes_lines.append("=" * 60)
hashes_lines.append("Algorithm: SHA3-512 (NIST FIPS 202 / Keccak)")
hashes_lines.append("GPG Signing Key: EB937371B8993E99 (RSA 4096-bit)")
hashes_lines.append("Entity: Reliance Infrastructure Holdings LLC")
hashes_lines.append("Generated: " + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
hashes_lines.append("Status: SEALED - RUN-ONLY")
hashes_lines.append("")
hashes_lines.append("-" * 60)
hashes_lines.append("")

for root, fname in all_files:
    fpath = os.path.join(root, fname)
    rel_path = fpath.replace("\\", "/")
    with open(fpath, 'rb') as f:
        content = f.read()
    sha3_hash = hashlib.sha3_512(content).hexdigest()
    manifest["documents"].append({
        "filename": fname,
        "path": rel_path,
        "sha3_512": sha3_hash,
        "file_size_bytes": len(content),
        "word_count": len(content.decode('utf-8', errors='replace').split()),
        "status": "RUN-ONLY"
    })
    hashes_lines.append(fname)
    hashes_lines.append("  SHA3-512: " + sha3_hash)
    hashes_lines.append("  Size: {} bytes | Words: {}".format(len(content), len(content.decode('utf-8', errors='replace').split())))
    hashes_lines.append("")

manifest["total_documents"] = len(manifest["documents"])

# Write MANIFEST.json
with open("MANIFEST.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

# Write checksums file
os.makedirs("checksums", exist_ok=True)
hashes_lines.append("-" * 60)
hashes_lines.append("Total: {} documents".format(manifest["total_documents"]))

with open(os.path.join("checksums", "SHA3-512-HASHES.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(hashes_lines) + "\n")

print("Hashed {} documents".format(manifest["total_documents"]))
for doc in manifest["documents"]:
    print("  {}: {}...".format(doc["filename"], doc["sha3_512"][:24]))
print("\nWrote: MANIFEST.json")
print("Wrote: checksums/SHA3-512-HASHES.txt")
