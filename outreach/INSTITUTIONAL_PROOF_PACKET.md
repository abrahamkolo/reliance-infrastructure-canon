# MW INFRASTRUCTURE STACK
## Institutional Proof Packet

### What does this system do?
The MW Infrastructure Stack provides deterministic governance certification for institutions. It issues binary (CERTIFIED / NOT CERTIFIED) determinations across 17 domains including evidence admissibility, capital governance, institutional reliance, and creative works authenticity. All certifications are cryptographically verified, blockchain-attested, and permanently archived.

### What does it explicitly NOT do?
- Does not provide legal, financial, or compliance advice
- Does not customize certifications for individual institutions
- Does not offer consulting, interpretation, or advisory services
- Does not negotiate terms, fees, or scope
- Does not maintain customer support infrastructure
- All exclusions governed by Document 6 (External Non-Advice Clause)

### How do you verify authenticity?
1. Every document has a SHA3-512 hash published in verification/hashes.json
2. Verify any document: `python3 -c "import hashlib; print(hashlib.sha3_512(open('FILE','rb').read()).hexdigest())"`
3. Compare against published hash in verification/hashes.json
4. OpenTimestamps proof anchored to Bitcoin blockchain (master-index.json.ots)
5. All commits GPG-signed with key EB937371B8993E99
6. Repository: github.com/abrahamkolo/reliance-infrastructure-canon

### How do you walk away safely?
- Cancel with 30 days written notice
- All certifications issued during license term remain permanently valid
- No data lock-in — all standards are published and independently verifiable
- No penalty for non-renewal
- Full exit protocol in licensing agreement
