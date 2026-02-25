# BLOCKCHAIN ATTESTATION GUIDE

## Ethereum (or L2 if gas > $200/tx)

### Option 1: Etherscan verified message
1. Go to etherscan.io → Verified Signatures → Sign Message
2. Message: SHA3-512 root hash from master-index.json
3. Sign with wallet
4. Record transaction hash

### Option 2: Smart contract attestation
Deploy minimal attestation contract storing the master-index.json root hash.
If mainnet gas > $200, use Arbitrum One or Base L2 with mainnet settlement within 90 days.

### Required attestation data:
```
MW-INFRASTRUCTURE-v2.0.0
Documents: 39
Algorithm: SHA3-512
Root hash: [from master-index.json self-hash]
Entity: Reliance Infrastructure Holdings LLC
Timestamp: [ISO 8601]
```

## Bitcoin
Already done via OpenTimestamps (master-index.json.ots). COMPLETE.

## Arweave (Permanent Storage)
1. Create Arweave wallet (arweave.org)
2. Fund with ~0.1 AR (~$1-5)
3. Upload master-index.json to Arweave
4. Record transaction ID
5. Cost: ~$0.01-0.10 for JSON file

## Attestation Record
After completing each attestation, record the transaction details in operations/FRE_LOG_TEMPLATE.md and update this file:

| Chain | Status | TX Hash | Date |
|-------|--------|---------|------|
| Bitcoin (OTS) | COMPLETE | See master-index.json.ots | 2026-02-20 |
| Ethereum | PENDING | — | — |
| Arweave | PENDING | — | — |
