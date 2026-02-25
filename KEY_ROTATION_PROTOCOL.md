# KEY ROTATION PROTOCOL
## Reliance Infrastructure Holdings LLC

### GPG Signing Key Rotation

**Current Key:** EB937371B8993E99
**Algorithm:** RSA
**Created:** 2026-02-20

### Rotation Schedule
- **Routine rotation:** Every 2 years OR upon suspected compromise
- **Emergency rotation:** Immediately upon confirmed compromise

### Rotation Procedure
1. Generate new GPG keypair: `gpg --full-generate-key` (RSA 4096-bit, 2-year expiry)
2. Sign new key with old key: `gpg --default-key [OLD_KEY] --sign-key [NEW_KEY]`
3. Export new public key: `gpg --armor --export [NEW_KEY] > verification/reliance-signing-key-v[N].pub`
4. Update git config: `git config user.signingkey [NEW_KEY]`
5. Update verification/master-index.json with new key reference
6. Create signed commit announcing rotation
7. Tag new release with both old and new keys
8. Update GPG escrow (new sealed envelope)
9. Revoke old key after 90-day overlap period: `gpg --gen-revoke [OLD_KEY]`
10. Publish revocation certificate

### Emergency Rotation (Compromise)
1. Immediately generate revocation certificate for compromised key
2. Publish revocation to keyservers
3. Generate new keypair (steps 1-8 above)
4. Audit all commits signed with compromised key
5. Re-sign critical tags with new key
6. Notify any reliant institutions
7. Document incident in SECURITY_INCIDENT_RESPONSE.md log

### Verification After Rotation
- All historical commits remain valid (signed with key valid at time of signing)
- New commits use new key
- master-index.json updated to reference both keys during overlap
- Old key public component retained in verification/ for historical verification

### Key Escrow Update
After rotation, create new physical escrow per MANUAL 1 instructions.
Destroy old escrow only after 90-day overlap period.
