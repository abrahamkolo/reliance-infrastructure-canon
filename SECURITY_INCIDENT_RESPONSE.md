# SECURITY INCIDENT RESPONSE
## Reliance Infrastructure Holdings LLC

### Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| CRITICAL | Key compromise, repo tampering, unauthorized commits | Immediate (< 1 hour) |
| HIGH | Unauthorized access attempt, hash mismatch detected | < 4 hours |
| MEDIUM | Suspicious activity, failed auth attempts | < 24 hours |
| LOW | Policy violation, minor configuration drift | < 72 hours |

### Incident Response Procedure

#### 1. Detection & Triage
- Identify the incident type and severity
- Preserve all evidence (logs, screenshots, commit history)
- Do NOT modify the repository until triage is complete

#### 2. Containment
- **Key compromise:** Immediately revoke key per KEY_ROTATION_PROTOCOL.md
- **Repo tampering:** Enable branch protection if not active; review all recent commits
- **Unauthorized access:** Revoke GitHub tokens; rotate all credentials
- **Hash mismatch:** Quarantine affected document; verify against OpenTimestamps proof

#### 3. Verification
- Re-verify all 39 document hashes against verification/hashes.json
- Verify OpenTimestamps proof: `ots verify verification/master-index.json.ots`
- Check GPG signature on all recent commits: `git log --show-signature -10`
- Compare against Zenodo archived copies (DOI: 10.5281/zenodo.18707171)

#### 4. Recovery
- Restore any tampered documents from verified backup
- Re-sign restored commits with current valid key
- Update master-index.json if any documents were restored
- Create new OpenTimestamps proof if master-index changed

#### 5. Documentation
Record all incidents below with: date, severity, description, actions taken, resolution.

### Incident Log

| Date | Severity | Description | Resolution |
|------|----------|-------------|------------|
| — | — | No incidents recorded | — |

### Contact Chain
1. Repository owner (primary)
2. Registered agent (if owner unavailable 14+ days)
3. Designated successor (per Operating Agreement Article VI)

### Preventive Measures
- GPG-signed commits enforced on all branches
- Branch protection on main (require signed commits)
- Regular hash verification (monthly recommended)
- OpenTimestamps re-attestation on any document update
- GitHub security alerts enabled
- Dependabot enabled for script dependencies
