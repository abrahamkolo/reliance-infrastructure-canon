# KEY ROTATION PROTOCOL

**Document:** Key Rotation Protocol
**Applies To:** Reliance Infrastructure Canon
**Issuing Entity:** Reliance Infrastructure Holdings LLC
**Version:** 1.0.0
**Effective Date:** 2025-06-01
**Review Cycle:** Every 12 months or upon trigger event

---

## 1. Schedule

### 1.1 Standard Rotation Cycle

| Key Type | Rotation Interval | Next Rotation |
|---|---|---|
| Ed25519 Signing Key | 24 months | 2027-06-01 |
| GPG Commit Signing Key (RSA 4096) | 24 months | 2027-06-01 |
| Repository Deploy Keys | 12 months | 2026-06-01 |

### 1.2 Rotation Triggers (Immediate)

Rotation MUST occur immediately if any of the following conditions are met:

- Private key material suspected or confirmed compromised
- Key custodian departure or role change
- Cryptographic weakness discovered in algorithm (e.g., NIST advisory)
- Security incident involving signing infrastructure
- Court order or regulatory requirement

---

## 2. Rotation Procedure

### Step 1: Generate New Key Pair

```bash
# Ed25519 (document signing)
python3 -c "
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

private_key = Ed25519PrivateKey.generate()

# Save private key (NEVER commit to repository)
with open('reliance-signing-key-v2.pem', 'wb') as f:
    f.write(private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ))

# Save public key
with open('reliance-signing-key-v2.pub', 'wb') as f:
    f.write(private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ))
print('New Ed25519 key pair generated.')
"

# GPG (commit signing)
gpg --full-generate-key  # Select RSA 4096, 2-year expiry
```

### Step 2: Re-Sign All Documents

```bash
python3 verification/sign-canon.py --key reliance-signing-key-v2.pem
```

All 39 documents MUST be re-signed. Partial re-signing is NOT permitted.

### Step 3: Update Verification Artifacts

Update the following files with new signatures and public key:

| File | Action |
|---|---|
| `verification/reliance-signing-key.pub` | Replace with new public key |
| `verification/signatures.json` | Regenerate all 39 signatures |
| `verification/master-index.json` | Update `signing_key` field |
| `hashes.json` | Regenerate (hashes unchanged, metadata updated) |

### Step 4: Blockchain Re-Attestation

- Submit new master hash to Ethereum mainnet (0-ETH data transaction)
- Generate new OpenTimestamps proof for `master-index.json`
- Upload updated archive to Arweave

### Step 5: Archive Old Key

```bash
# Archive old public key with date stamp
cp verification/reliance-signing-key.pub \
   verification/archive/reliance-signing-key-v1-retired-$(date +%Y%m%d).pub
```

Old keys are NEVER deleted. They are archived for historical verification.

### Step 6: Update External References

- Update Zenodo deposit with new verification artifacts
- Update mwcanon-site with new `hashes.json`
- Update reliance-verify tool if public key is embedded
- Notify certified institutions (if any) of key rotation

### Step 7: Verification Gate

The rotation is NOT complete until:

```bash
cd reliance-infrastructure-canon
python3 verification/verify-canon.py
# Expected: VERDICT: AUTHENTIC (39/39 PASS with NEW key)
```

Both old signatures (archived) and new signatures (active) must be documented in the commit message.

---

## 3. Post-Quantum Migration Plan

### 3.1 Timeline

| Phase | Target Date | Action |
|---|---|---|
| Monitoring | Now | Track NIST PQC standardization (ML-DSA, SLH-DSA) |
| Evaluation | When NIST finalizes | Test ML-DSA-65 (FIPS 204) for document signing |
| Dual-Signing | 6 months post-finalization | Sign with both Ed25519 AND ML-DSA-65 |
| Migration | 12 months post-finalization | Primary signing moves to PQC algorithm |
| Deprecation | 24 months post-finalization | Ed25519 signatures archived, PQC-only |

### 3.2 Algorithm Selection Criteria

1. NIST standardized (FIPS certified)
2. Signature size compatible with JSON storage
3. Library support in Python cryptography package
4. Deterministic signature generation (no nonce reuse risk)

### 3.3 Migration Procedure

The post-quantum migration follows the same 7-step rotation procedure above, with the additional requirement that:

- `signatures.json` includes BOTH Ed25519 and PQC signatures during dual-signing phase
- `verify-canon.py` is updated to verify both signature types
- Master index records the algorithm transition

---

## 4. Emergency Key Rotation

### 4.1 Trigger

Emergency rotation is invoked when:

- Key compromise is **confirmed** (not merely suspected)
- Active exploitation is detected
- Law enforcement or legal counsel directs immediate rotation

### 4.2 Emergency Procedure

| Step | Action | Timeframe |
|---|---|---|
| 1 | Revoke compromised GPG key (`gpg --gen-revoke`) | Immediate |
| 2 | Generate new Ed25519 + GPG key pairs | Within 1 hour |
| 3 | Re-sign all 39 documents | Within 4 hours |
| 4 | Push signed commit with `[EMERGENCY-ROTATION]` prefix | Within 4 hours |
| 5 | Submit new Ethereum attestation | Within 24 hours |
| 6 | Update Zenodo deposit | Within 48 hours |
| 7 | Publish rotation notice in repository | Within 48 hours |

### 4.3 Communication

Emergency rotation commits MUST include:

```
[EMERGENCY-ROTATION] Key rotation: <old-key-fingerprint> -> <new-key-fingerprint>

Reason: <brief description>
Old key archived: verification/archive/<filename>
New key active: verification/reliance-signing-key.pub
All 39 documents re-signed and verified.
```

### 4.4 Post-Emergency Audit

Within 7 days of emergency rotation:

1. Document the incident in SECURITY_INCIDENT_RESPONSE.md format
2. Verify all external references updated
3. Confirm blockchain attestations submitted
4. Review access controls and key storage procedures
5. Update this protocol if procedural gaps identified

---

## 5. Key Storage Requirements

| Key Type | Storage Location | Access |
|---|---|---|
| Ed25519 Private Key | Offline encrypted USB (primary) + attorney escrow (backup) | Founder only |
| GPG Private Key | Local keyring + encrypted backup | Founder only |
| Ed25519 Public Key | Repository (`verification/reliance-signing-key.pub`) | Public |
| GPG Public Key | GitHub + keyservers | Public |
| Archived Keys | `verification/archive/` directory | Public (read-only) |

Private keys MUST NEVER be:
- Committed to any repository
- Stored in cloud storage without encryption
- Shared via email, messaging, or any electronic communication
- Stored on internet-connected devices without full-disk encryption

---

*Reliance Infrastructure Holdings LLC | CC BY-ND 4.0 | This protocol is part of the MW Infrastructure Canon operational framework.*
