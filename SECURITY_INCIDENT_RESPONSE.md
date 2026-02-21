# SECURITY INCIDENT RESPONSE

**Document:** Security Incident Response Protocol
**Applies To:** Reliance Infrastructure Canon & Associated Infrastructure
**Issuing Entity:** Reliance Infrastructure Holdings LLC
**Version:** 1.0.0
**Effective Date:** 2025-06-01
**Classification:** OPERATIONAL -- may be committed to repository

---

## 1. Incident Categories

### Category A: Repository Compromise

**Definition:** Unauthorized access to or modification of the canonical repository (`reliance-infrastructure-canon`), including but not limited to:

- Unauthorized commits or force-pushes
- Branch protection bypass
- GitHub account compromise
- CI/CD pipeline tampering
- Unauthorized release publication

**Severity:** CRITICAL

**Detection Indicators:**
- Unsigned commits appearing in history
- Branch protection rules modified without authorization
- Unexpected workflow runs or modifications
- Hash verification failures in CI
- Unauthorized collaborators added
- Release assets modified or added without corresponding commit

**Response Procedure:**

| Step | Action | Timeframe |
|---|---|---|
| 1 | Lock repository (set to private or enable security lock) | Immediate |
| 2 | Revoke all active sessions (`github.com/settings/sessions`) | Immediate |
| 3 | Rotate GitHub personal access tokens | Within 1 hour |
| 4 | Audit git log for unauthorized commits | Within 1 hour |
| 5 | Run `python3 verification/verify-canon.py` against known-good backup | Within 2 hours |
| 6 | If documents tampered: restore from Zenodo archive (DOI: 10.5281/zenodo.18707171) | Within 4 hours |
| 7 | Force-push verified clean state (ONLY authorized use of force-push) | Within 4 hours |
| 8 | Re-enable branch protection with enhanced rules | Within 4 hours |
| 9 | Rotate GPG and Ed25519 keys per KEY_ROTATION_PROTOCOL.md | Within 24 hours |
| 10 | Publish incident report (Section 5 format) | Within 72 hours |

---

### Category B: Payment System Compromise

**Definition:** Unauthorized access to or exploitation of payment infrastructure, including:

- Stripe account compromise
- Unauthorized transactions or refunds
- Payment page tampering (mwcanon-site)
- Invoice fraud or impersonation

**Severity:** CRITICAL

**Detection Indicators:**
- Unexpected Stripe dashboard activity
- Customer reports of suspicious payment flows
- Website payment page modifications not matching source code
- Unauthorized Stripe API key usage

**Response Procedure:**

| Step | Action | Timeframe |
|---|---|---|
| 1 | Disable Stripe live API keys | Immediate |
| 2 | Pause all active payment links | Immediate |
| 3 | Audit Stripe transaction log for unauthorized activity | Within 1 hour |
| 4 | Notify affected customers (if any) | Within 24 hours |
| 5 | Rotate all Stripe API keys | Within 24 hours |
| 6 | Verify mwcanon-site source matches deployed version | Within 24 hours |
| 7 | Re-deploy payment pages from verified source | Within 48 hours |
| 8 | File fraud report with Stripe if applicable | Within 48 hours |
| 9 | Publish incident report (Section 5 format) | Within 72 hours |

---

### Category C: Document Integrity Breach

**Definition:** Discovery that one or more canonical documents have been altered, corrupted, or do not match their registered hashes, including:

- SHA3-512 hash mismatch on any document
- Ed25519 signature verification failure
- Discrepancy between repository, Zenodo, and blockchain records
- Unauthorized document amendments

**Severity:** HIGH

**Detection Indicators:**
- CI integrity check workflow failure
- `verify-canon.py` reports MISMATCH or FAILED
- Zenodo archive hash differs from repository
- Blockchain attestation hash differs from computed master hash
- Third-party verification report flags discrepancy

**Response Procedure:**

| Step | Action | Timeframe |
|---|---|---|
| 1 | Identify affected document(s) by running full verification suite | Immediate |
| 2 | Compare repository version against Zenodo archive | Within 1 hour |
| 3 | Compare against blockchain attestation (Ethereum tx data) | Within 1 hour |
| 4 | Determine authoritative version (Zenodo = Tier 2 backup, blockchain = Tier 3 immutable) | Within 2 hours |
| 5 | If repository corrupted: restore from Zenodo archive | Within 4 hours |
| 6 | Re-run `verify-canon.py` to confirm restoration | Within 4 hours |
| 7 | If signing key compromised: execute KEY_ROTATION_PROTOCOL.md | Within 24 hours |
| 8 | Update `verification/master-index.json` if needed | Within 24 hours |
| 9 | Publish incident report (Section 5 format) | Within 72 hours |

**Authoritative Source Hierarchy:**

1. Blockchain attestation (immutable, highest trust)
2. Zenodo archive (DOI: 10.5281/zenodo.18707171, independently hosted)
3. GitHub repository (primary working copy, most current)

If all three disagree, the blockchain-attested hash determines which version is authentic.

---

### Category D: Signing Key Compromise

**Definition:** Private key material (Ed25519 or GPG) is exposed, stolen, or suspected compromised.

**Severity:** CRITICAL

**Detection Indicators:**
- Private key file found in public location
- Unauthorized signatures appearing on non-canonical content
- Key custodian reports device theft or unauthorized access
- Third party demonstrates ability to produce valid signatures

**Response Procedure:**

Immediately execute **KEY_ROTATION_PROTOCOL.md Section 4 (Emergency Key Rotation)**, then:

| Step | Action | Timeframe |
|---|---|---|
| 1 | Revoke GPG key on keyservers | Immediate |
| 2 | Generate new key pairs | Within 1 hour |
| 3 | Re-sign all 39 documents | Within 4 hours |
| 4 | Submit new blockchain attestation | Within 24 hours |
| 5 | Update all external references | Within 48 hours |
| 6 | Audit for any fraudulent use of compromised key | Within 7 days |
| 7 | Publish incident report (Section 5 format) | Within 72 hours |

---

## 2. Response Timeline Summary

| Severity | Initial Response | Containment | Resolution | Report |
|---|---|---|---|---|
| CRITICAL | Immediate (< 15 min) | Within 4 hours | Within 48 hours | Within 72 hours |
| HIGH | Within 1 hour | Within 8 hours | Within 7 days | Within 7 days |
| MEDIUM | Within 24 hours | Within 48 hours | Within 14 days | Within 14 days |

---

## 3. Communication Protocol

### 3.1 Internal Communication

All incident-related actions are logged via GPG-signed git commits with the prefix:

```
[SECURITY-INCIDENT] <Category>: <Brief Description>
```

### 3.2 External Communication

| Audience | Channel | Timing |
|---|---|---|
| Certified Institutions | Direct email (if applicable) | Within 24 hours of confirmation |
| Public | Repository incident report | Within 72 hours |
| Law Enforcement | Direct contact (if criminal activity) | As required by law |
| GitHub Security | security@github.com (if platform involved) | Immediate |

### 3.3 Information Disclosure Rules

- NEVER disclose private key material in incident reports
- NEVER disclose specific vulnerability details until patched
- DO disclose: timeline, affected scope, remediation steps, verification instructions
- All public communications reviewed before release

---

## 4. Recovery Verification

An incident is NOT resolved until ALL of the following pass:

```bash
# 1. Full canon verification
python3 verification/verify-canon.py
# Expected: VERDICT: AUTHENTIC (39/39 PASS)

# 2. CI pipeline green
gh run list --workflow=integrity-check.yml --limit=1
# Expected: completed, success

# 3. Branch protection intact
gh api repos/abrahamkolo/reliance-infrastructure-canon/branches/main/protection
# Expected: required_signatures, enforce_admins, required_linear_history all true

# 4. External archives consistent
# Manually verify Zenodo hashes match repository hashes
```

---

## 5. Incident Report Template

All incidents MUST be documented using this format. Store incident reports in `security/incidents/` (create directory if needed). Reports are GPG-signed and committed.

```markdown
# Incident Report: [YYYY-MM-DD] [Category] [Brief Title]

## Summary
- **Category:** A / B / C / D
- **Severity:** CRITICAL / HIGH / MEDIUM
- **Detected:** [timestamp]
- **Contained:** [timestamp]
- **Resolved:** [timestamp]
- **Reported By:** [name/system]

## Timeline
| Time | Event |
|---|---|
| [timestamp] | [event description] |

## Impact
- Documents affected: [list or "none"]
- Keys rotated: [yes/no]
- External parties notified: [list or "none"]
- Financial impact: [amount or "none"]

## Root Cause
[Description of how the incident occurred]

## Remediation
[Steps taken to resolve]

## Prevention
[Changes made to prevent recurrence]

## Verification
- verify-canon.py: PASS / FAIL
- CI status: GREEN / RED
- Branch protection: INTACT / RESTORED
- External archives: CONSISTENT / UPDATED
```

---

## 6. Preventive Measures

### 6.1 Ongoing Monitoring

| Check | Frequency | Method |
|---|---|---|
| CI integrity workflow | Every push | GitHub Actions (automatic) |
| Branch protection audit | Weekly | `gh api` verification |
| Zenodo consistency check | Monthly | Manual hash comparison |
| GPG key expiry check | Monthly | `gpg --list-keys` |
| GitHub session audit | Monthly | `github.com/settings/sessions` |
| Stripe activity review | Weekly | Stripe dashboard |

### 6.2 Access Controls

- GitHub account: 2FA enabled (hardware key preferred)
- GPG key: Stored on encrypted media, never on cloud
- Stripe: Restricted API keys with minimum necessary permissions
- Repository: Branch protection with required signatures + admin enforcement

### 6.3 Backup Verification

| Archive | Verification Method | Frequency |
|---|---|---|
| GitHub (Tier 1) | CI integrity-check workflow | Every push |
| Zenodo (Tier 2) | Download and hash-compare | Quarterly |
| Blockchain (Tier 3) | Decode tx data and compare master hash | Annually |
| Local backup | `verify-canon.py` against local copy | Monthly |

---

*Reliance Infrastructure Holdings LLC | CC BY-ND 4.0 | This protocol is part of the MW Infrastructure Canon operational framework.*
