#!/usr/bin/env python3
"""Generate hashes.json -- maps SHA3-512 hashes to documents for SEAI verify page."""
import json
import sys

if sys.platform == 'win32':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def clean(text):
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
    hashes = {}

    for i in range(1, 40):
        doc_id = "DOC-{:03d}".format(i)
        meta = docs.get(doc_id, {})
        sha = meta.get('sha3_512', '')
        title = clean(meta.get('title', 'Unknown'))
        filename = meta.get('filename', '')

        if sha:
            hashes[sha] = {
                "document": "Document {}".format(i),
                "id": doc_id,
                "title": title,
                "filename": filename,
                "status": "CANONICAL"
            }

    output = {
        "hashes": hashes,
        "count": len(hashes),
        "version": "2.0.0",
        "doi": "10.5281/zenodo.18707171",
        "verify_tool": "https://github.com/abrahamkolo/reliance-verify"
    }

    with open('hashes.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print("hashes.json generated with {} entries.".format(len(hashes)))

if __name__ == "__main__":
    main()
