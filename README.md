[![Hash Verification](https://github.com/abrahamkolo/reliance-infrastructure-canon/actions/workflows/backup.yml/badge.svg)](https://github.com/abrahamkolo/reliance-infrastructure-canon/actions/workflows/backup.yml)
[![Canon Integrity](https://github.com/abrahamkolo/reliance-infrastructure-canon/actions/workflows/integrity-check.yml/badge.svg)](https://github.com/abrahamkolo/reliance-infrastructure-canon/actions/workflows/integrity-check.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18707171.svg)](https://doi.org/10.5281/zenodo.18707171)
[![License: CC BY-ND 4.0](https://img.shields.io/badge/License-CC_BY--ND_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nd/4.0/)

# Reliance Infrastructure Canon

**39 Constitutional Documents for Institutional-Grade Governance**

## Start Here in 60 Seconds

**What this is:** 39 institutional-grade governance documents forming a complete constitutional stack for deterministic decision-making. Every document is cryptographically signed and independently verifiable.

**Quick verify** (requires Python 3.8+):
```bash
git clone https://github.com/abrahamkolo/reliance-infrastructure-canon.git
cd reliance-infrastructure-canon
python3 verification/verify-canon.py
```

Expected output:
```
Verifying 39 documents...
SHA3-512 hashes: 39/39 PASS
Ed25519 signatures: 39/39 PASS
Master index signature: PASS
═══════════════════════════
VERDICT: AUTHENTIC
═══════════════════════════
```

**Read first:** DOC-001: MW Canon — the root constitutional document.

**Full documentation:** See sections below.

---

## Overview

The Reliance Infrastructure Canon is a complete constitutional framework providing deterministic, document-bound governance for institutional operations. Every decision, certification, and compliance determination follows binary (YES/NO) logic with identical inputs producing identical outputs — regardless of who operates the system.

**Issuing Entity**: Reliance Infrastructure Holdings LLC  
**License**: CC BY-ND 4.0 (Attribution, No Derivatives)  
**Hash Algorithm**: SHA3-512  
**Signing Algorithm**: Ed25519  
**Status**: RUN-ONLY (no modifications permitted outside amendment protocol)

---

## Document Hierarchy

### Layer 0 — Supreme Constitutional Authority
| ID | Document | Version |
|----|----------|---------|
| DOC-001 | MW Canon (MW-Ω⁺⁺⁺⁺⁺) | 2.1.0 |

### Layer 1 — Structural Charters
| ID | Document | Version |
|----|----------|---------|
| DOC-002 | Layer Architecture & Non-Escalation Charter | 2.0.0 |
| DOC-003 | Determinism & Run-Only Enforcement Law | 2.0.0 |

### Layer 2 — Operational Charters
| ID | Document | Version |
|----|----------|---------|
| DOC-004 | Issuance & Decision Admissibility Charter | 2.0.0 |
| DOC-005 | Pricing & Fee Primitives Charter | 2.0.0 |
| DOC-006 | External Non-Advice & Safe-Interface Clause | 2.0.0 |

### Layer 3 — Authority Constitutions
| ID | Document | Version |
|----|----------|---------|
| DOC-007 | IRUA — Institutional Reliance & Usage Authority | 2.0.0 |
| DOC-008 | GEAA — Global Evidence Admissibility Authority | 2.0.0 |
| DOC-009 | CivicHab — Civic Habitat Authority | 2.0.0 |
| DOC-010 | GCPA — Global Capital & Portfolio Authority | 2.0.0 |
| DOC-011 | PMOA — Personal Mastery & Optimization Authority | 2.0.0 |
| DOC-012 | EWA — Eternal Works Authority | 2.0.0 |
| DOC-013 | EPA — Eternal Publishing Authority | 2.0.0 |
| DOC-014 | EFAA — Eternal Fine Art Authority | 2.0.0 |
| DOC-015 | UPDIUD — Universal Private DIUD Cell Ecosystem | 2.0.0 |
| DOC-016 | SICA — Standards Issuance & Custody Authority | 2.0.0 |
| DOC-017 | IATA — Independent Arbitration & Tribunals Authority | 2.0.0 |
| DOC-018 | DRFA — Dispute Resolution Finality Authority | 2.0.0 |
| DOC-019 | CRTA — Crisis Response & Transition Authority | 2.0.0 |
| DOC-020 | IPPA — Intellectual Property Permanence Authority | 2.0.0 |
| DOC-021 | CSCA — Contractual Succession Continuity Authority | 2.0.0 |
| DOC-022 | DCPA — Data Custody Perpetuity Authority | 2.0.0 |
| DOC-023 | FAPA — Foundational Assets Permanence Authority | 2.0.0 |
| DOC-032 | GCRA — Global Capital Reliance Authority | 2.0.0 |

### Layer 4 — Specifications & Protocols
| ID | Document | Version |
|----|----------|---------|
| DOC-024 | Issuance Primitives Specification (IPS) | 2.0.0 |
| DOC-025 | Binary Decision Trees Master (BDTM) | 2.0.0 |
| DOC-026 | Artifact Formatting, ID & Hashing Standard (AFIHS) | 2.0.0 |
| DOC-027 | Custody & Chain-of-Custody Protocol (CCOCP) | 2.0.0 |
| DOC-028 | Registry Architecture Specification (RAS) | 2.0.0 |
| DOC-029 | Multi-Jurisdiction Mirroring Protocol (MJMP) | 2.0.0 |
| DOC-030 | Succession & Continuity Transfer Protocol (SCTP) | 2.0.0 |
| DOC-031 | Citation Authenticity Protocol (CAP) | 2.0.0 |
| DOC-033 | Reliance Infrastructure Exchange (RIX) | 2.0.0 |
| DOC-034 | Reliance Ordering Doctrine (ROD) | 2.0.0 |
| DOC-035 | Cross-Authority Conflict Avoidance Protocol (CACAP) | 2.0.0 |
| DOC-036 | Collision Resolution Matrix (CRM) | 2.0.0 |
| DOC-037 | Pre-Reliance Preparation Matrix (PRPM) | 2.0.0 |
| DOC-038 | Binary Gates & Dormancy Protocol (BGDP) | 2.0.0 |
| DOC-039 | Execution Bridge Protocol (EBP) | 2.0.0 |

---

## Verification

### SHA3-512 Hash Verification

Every document's integrity can be independently verified:

```bash
# Linux/Mac
sha3sum -a 512 documents/constitutions/DOC-007_IRUA_CONSTITUTION_v2.0.txt

# Compare against verification/hashes.json
python3 -c "
import hashlib, json
with open('verification/hashes.json') as f:
    hashes = json.load(f)
with open('documents/constitutions/DOC-007_IRUA_CONSTITUTION_v2.0.txt', 'rb') as f:
    actual = hashlib.sha3_512(f.read()).hexdigest()
expected = hashes.get('DOC-007_IRUA_CONSTITUTION_v2.0.txt', 'NOT FOUND')
print('MATCH' if actual == expected else 'MISMATCH')
"
```

### Ed25519 Signature Verification

Documents are signed with Ed25519 per AFIHS §XI:

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import json, base64

# Load public key
with open('verification/reliance-signing-key.pub', 'rb') as f:
    pub_key = serialization.load_pem_public_key(f.read())

# Load signatures
with open('verification/signatures.json') as f:
    sigs = json.load(f)

# Verify a document
doc = 'DOC-007_IRUA_CONSTITUTION_v2.0.txt'
sig_b64 = sigs['documents'][doc]['ed25519_signature']
hash_val = sigs['documents'][doc]['sha3_512']

try:
    pub_key.verify(base64.b64decode(sig_b64), hash_val.encode('utf-8'))
    print(f'{doc}: VERIFIED')
except Exception:
    print(f'{doc}: FAILED')
```

### Blockchain Attestation

Three-chain attestation per SICA §3.1:

| Chain | Method | Status |
|-------|--------|--------|
| Bitcoin | OpenTimestamps (`verification/master-index.json.ots`) | Confirmed |
| Ethereum | Attestation transaction (see `verification/blockchain-records.json`) | Confirmed |
| Arweave | Permanent storage (see `verification/blockchain-records.json`) | Confirmed |

Verification details in `verification/blockchain-records.json`.

---

## Conflict Resolution Hierarchy

When documents conflict, higher-layer documents prevail:

1. **MW Canon** (DOC-001) — Supreme, overrides all
2. **Structural Charters** (DOC-002, DOC-003) — Override operational and below
3. **Operational Charters** (DOC-004 through DOC-006) — Override authority-level
4. **Authority Constitutions** (DOC-007 through DOC-023, DOC-032) — Override specifications
5. **Specifications & Protocols** (DOC-024 through DOC-031, DOC-033 through DOC-039) — Operational

---

## Ecosystem

| Tool | Purpose |
|---|---|
| [reliance-verify](https://github.com/abrahamkolo/reliance-verify) | Independent verification tool |
| [governance-templates](https://github.com/abrahamkolo/governance-templates) | Reusable institutional templates |
| [mw-omega-orchestrator](https://github.com/abrahamkolo/mw-omega-orchestrator) | Deterministic orchestration engine |

---

## Academic Citation

```bibtex
@misc{reliance_infrastructure_canon_2025,
  author       = {{Reliance Infrastructure Holdings LLC}},
  title        = {Reliance Infrastructure Canon — 39-Document Canonical Stack},
  year         = 2025,
  version      = {2.0.0},
  doi          = {10.5281/zenodo.18707171},
  url          = {https://doi.org/10.5281/zenodo.18707171},
  note         = {CC BY-ND 4.0. SHA3-512 verified. Document-bound governance.}
}
```

---

## Immutability Statement

These documents are issued under **Run-Only governance** (DOC-003). No modifications, derivatives, translations, or adaptations are permitted without formal amendment per the constitutional amendment protocol specified in each authority's constitution. Hash verification proves document authenticity regardless of source.

This repository is the **primary canonical archive** (Tier 1 per IRUA §3.3). Zenodo (DOI: 10.5281/zenodo.18707171) serves as the independent academic archive (Tier 2). Blockchain attestation provides immutable timestamp proof (Tier 3).

---

**Document-Bound. Founder-Irrelevant. Deterministic.**
