#!/usr/bin/env python3
"""Generate CITATION-REGISTRY.md -- human-readable citation registry for all 39 documents."""
import json
import sys

if sys.platform == 'win32':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def clean(text):
    """Remove non-ASCII for safe markdown output."""
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append('?')
    return ''.join(out)

def main():
    with open('verification/master-index.json', encoding='utf-8') as f:
        master = json.load(f)

    docs = master['documents']
    lines = []

    # Header
    lines.append("# MW Infrastructure Canon -- Citation Registry")
    lines.append("")
    lines.append("**Version:** 2.0.0")
    lines.append("**Document Count:** 39")
    lines.append("**Master DOI:** [10.5281/zenodo.18707171](https://doi.org/10.5281/zenodo.18707171)")
    lines.append("**License:** CC BY-ND 4.0")
    lines.append("**Issuing Entity:** Reliance Infrastructure Holdings LLC")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Full stack citation
    lines.append("## How to Cite")
    lines.append("")
    lines.append("### Full Stack Citation")
    lines.append("")
    lines.append("```")
    lines.append("Kolo, A.J. (2025). MW Infrastructure Canon: 39-Document Institutional")
    lines.append("Governance Framework (Version 2.0.0). Reliance Infrastructure Holdings LLC.")
    lines.append("https://doi.org/10.5281/zenodo.18707171")
    lines.append("```")
    lines.append("")
    lines.append("### Individual Document Citation Template")
    lines.append("")
    lines.append("```")
    lines.append("Kolo, A.J. (2025). [Document Title] (MW-DOC-NNN, Version 2.0.0).")
    lines.append("In MW Infrastructure Canon. Reliance Infrastructure Holdings LLC.")
    lines.append("https://doi.org/10.5281/zenodo.18707171")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Registry table
    lines.append("## Document Registry")
    lines.append("")
    lines.append("| # | ID | Title | Layer | SHA3-512 (first 16) | PDF |")
    lines.append("|---|---|---|---|---|---|")

    for i in range(1, 40):
        doc_id = "DOC-{:03d}".format(i)
        meta = docs.get(doc_id, {})
        title = clean(meta.get('title', 'Unknown'))
        layer = meta.get('layer', 'N/A')
        sha = meta.get('sha3_512', 'N/A')
        sha_short = sha[:16] + "..." if len(sha) > 16 else sha
        pdf_link = "[PDF](pdf-reference/MW-CANON-DOC-{:02d}.pdf)".format(i)
        lines.append("| {} | MW-DOC-{:03d} | {} | {} | `{}` | {} |".format(
            i, i, title, layer, sha_short, pdf_link
        ))

    lines.append("")
    lines.append("---")
    lines.append("")

    # Verification section
    lines.append("## Verification")
    lines.append("")
    lines.append("| Method | Location |")
    lines.append("|---|---|")
    lines.append("| SHA3-512 Hashes | [`verification/hashes.txt`](verification/hashes.txt) |")
    lines.append("| Ed25519 Signatures | [`verification/signatures.json`](verification/signatures.json) |")
    lines.append("| Public Key | [`verification/public_key.pem`](verification/public_key.pem) |")
    lines.append("| Independent Verifier | [reliance-verify](https://github.com/abrahamkolo/reliance-verify) |")
    lines.append("| Blockchain Records | [`verification/BLOCKCHAIN-RECORDS.json`](verification/BLOCKCHAIN-RECORDS.json) |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Archives section
    lines.append("## Canonical Archives")
    lines.append("")
    lines.append("| Archive | Location | Status |")
    lines.append("|---|---|---|")
    lines.append("| GitHub (primary) | [reliance-infrastructure-canon](https://github.com/abrahamkolo/reliance-infrastructure-canon) | Live |")
    lines.append("| Zenodo (DOI) | [10.5281/zenodo.18707171](https://doi.org/10.5281/zenodo.18707171) | Published |")
    lines.append("| Ethereum Mainnet | See BLOCKCHAIN-RECORDS.json | Pending |")
    lines.append("| Arweave (permanent) | See BLOCKCHAIN-RECORDS.json | Pending |")
    lines.append("| PDF References | [`pdf-reference/`](pdf-reference/) | 39 PDFs with embedded hashes |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated from `verification/master-index.json`. CC BY-ND 4.0.*")

    with open('CITATION-REGISTRY.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print("CITATION-REGISTRY.md generated with {} document entries.".format(len(docs)))


if __name__ == "__main__":
    main()
