# Changelog — Reliance Infrastructure Canon

## v2.0.0 (2026-02-20)

### Initial Canonical Release
- All 39 documents at institutional-grade (100/100)
- MW Canon (DOC-001) at v2.1.0; all others at v2.0.0
- SHA3-512 cryptographic verification for all documents
- Ed25519 digital signatures for all documents
- OpenTimestamps Bitcoin attestation
- GitHub canonical hosting with branch protection
- Zenodo academic archival (DOI: 10.5281/zenodo.18707171)
- CC BY-ND 4.0 licensing
- Complete founder irrelevance achieved

### Infrastructure
- Ed25519 signing key: `verification/reliance-signing-key.pub`
- Hashes: `verification/hashes.json` (SHA3-512)
- Signatures: `verification/signatures.json`
- Master Index: `verification/master-index.json`
- Blockchain attestation: `verification/blockchain-records.json`
- Independent verification: `verification/verify-canon.py`
- Automated backup: `.github/workflows/backup.yml`
- Automated Zenodo sync: `.github/workflows/zenodo-sync.yml`
