#!/usr/bin/env python3
"""Generate 39 read-only PDF reference documents with embedded SHA3-512 hashes."""
import os
import sys
import json
import hashlib
import re
from pathlib import Path

# Force UTF-8 output
if sys.platform == 'win32':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# --- Config ---
REPO_ROOT = Path(".")
DOC_DIR = REPO_ROOT / "documents"
OUT_DIR = REPO_ROOT / "pdf-reference"
MASTER_INDEX = REPO_ROOT / "verification" / "master-index.json"

OUT_DIR.mkdir(exist_ok=True)

# Common mojibake replacements
MOJIBAKE_MAP = [
    ("\u00ce\u00a9", "Omega"),
    ("\u00c3\u008e\u00c2\u00a9", "Omega"),
    ("ÃŽÂ©", "Omega"),
    ("Î©", "Omega"),
    ("Ω", "Omega"),
    ("â\u0081º", "+"),
    ("Ã¢ÂÂº", "+"),
    ("â\u0080\u0094", "--"),
    ("Ã¢ÂÂ", "--"),
    ("â\u0080\u0093", "-"),
    ("â\u0080\u009c", '"'),
    ("â\u0080\u009d", '"'),
    ("â\u0080\u0099", "'"),
    ("â\u0080\u0098", "'"),
    ("Ã‚Â·", " - "),
    ("Â·", " - "),
    ("Ã‚Â§", "S"),
    ("Â§", "S"),
    ("Ã¢ÂÂ¢", "(TM)"),
    ("Ã¢ÂÂ", ""),
    ("Â±", "+/-"),
    ("Ã‚Â±", "+/-"),
    ("Â©", "(c)"),
    ("Â®", "(R)"),
    ("\u00e2\u0080\u0099", "'"),
    ("\u00e2\u0080\u009c", '"'),
    ("\u00e2\u0080\u009d", '"'),
    ("\u00c2\u00a7", "S"),
    ("\u00c2\u00b7", " - "),
]

def clean_text(text):
    """Fix common UTF-8 mojibake artifacts."""
    for bad, good in MOJIBAKE_MAP:
        text = text.replace(bad, good)
    # Remove remaining non-ASCII that would break reportlab
    cleaned = []
    for ch in text:
        if ord(ch) < 128 or ch in ('\n', '\t'):
            cleaned.append(ch)
        elif ord(ch) < 256:
            cleaned.append(ch)
        else:
            cleaned.append('?')
    return ''.join(cleaned)

def escape_xml(text):
    """Escape XML special characters for reportlab Paragraph objects."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def compute_sha3_512(filepath):
    """Compute SHA3-512 hash of a file."""
    h = hashlib.sha3_512()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_title(text):
    """Extract title from first meaningful line of document."""
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith('_') and len(line) > 5:
            return line
    return "Untitled"

def generate_pdf(doc_num, title, content, src_hash, filepath, out_path):
    """Generate a single PDF with header stamp, content, and hash footer."""
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.6*inch,
        bottomMargin=0.8*inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    stamp_style = ParagraphStyle(
        'Stamp', parent=styles['Normal'],
        fontName='Courier-Bold', fontSize=7,
        textColor=HexColor('#CC0000'),
        alignment=TA_CENTER, spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontName='Courier', fontSize=7,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER, spaceAfter=12,
    )
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=14,
        textColor=HexColor('#111111'),
        spaceAfter=12, alignment=TA_LEFT,
    )
    heading_style = ParagraphStyle(
        'SectionHead', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=11,
        textColor=HexColor('#222222'),
        spaceBefore=10, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9,
        leading=12, spaceAfter=4,
    )
    hash_style = ParagraphStyle(
        'Hash', parent=styles['Normal'],
        fontName='Courier', fontSize=5.5,
        textColor=HexColor('#444444'),
        alignment=TA_CENTER, spaceBefore=12,
    )
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontName='Courier', fontSize=6,
        textColor=HexColor('#888888'),
        alignment=TA_CENTER, spaceBefore=4,
    )

    story = []

    # Red stamp header
    story.append(Paragraph(
        "CANONICAL - RUN-ONLY - UPGRADE-CLOSED - REFERENCE-GRADE",
        stamp_style
    ))

    # Metadata line
    story.append(Paragraph(
        "MW Infrastructure Stack - Document {} of 39 - Version 2.0.0 - CC BY-ND 4.0".format(doc_num),
        meta_style
    ))

    # Title
    safe_title = escape_xml(title[:120])
    story.append(Paragraph(safe_title, title_style))
    story.append(Spacer(1, 6))

    # Content - split into paragraphs
    lines = content.split('\n')
    para_buf = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Flush paragraph buffer
            if para_buf:
                text = escape_xml(' '.join(para_buf))
                try:
                    story.append(Paragraph(text, body_style))
                except Exception:
                    story.append(Paragraph(text.encode('ascii', 'replace').decode(), body_style))
                para_buf = []
            continue

        # Detect section headers (Roman numerals, ALL CAPS, or starting with letter + period)
        is_heading = False
        if re.match(r'^[IVX]+\.', stripped):
            is_heading = True
        elif re.match(r'^[A-Z]\.\s', stripped):
            is_heading = True
        elif stripped.startswith('DOCUMENT ') or stripped.startswith('Section '):
            is_heading = True
        elif stripped == stripped.upper() and len(stripped) > 3 and not stripped.startswith('_'):
            is_heading = True

        if is_heading:
            # Flush buffer first
            if para_buf:
                text = escape_xml(' '.join(para_buf))
                try:
                    story.append(Paragraph(text, body_style))
                except Exception:
                    pass
                para_buf = []
            safe = escape_xml(stripped[:200])
            try:
                story.append(Paragraph(safe, heading_style))
            except Exception:
                pass
        elif stripped.startswith('_'):
            # Separator line - skip
            continue
        else:
            para_buf.append(stripped)

    # Flush remaining
    if para_buf:
        text = escape_xml(' '.join(para_buf))
        try:
            story.append(Paragraph(text, body_style))
        except Exception:
            pass

    # Hash footer
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "SHA3-512: {}".format(src_hash),
        hash_style
    ))
    story.append(Paragraph(
        "Reliance Infrastructure Holdings LLC - CC BY-ND 4.0 - DOI: 10.5281/zenodo.18707171",
        footer_style
    ))

    doc.build(story)


def main():
    # Load master index
    with open(str(MASTER_INDEX), encoding='utf-8') as f:
        master = json.load(f)

    documents = master['documents']
    manifest_lines = []
    manifest_lines.append("PDF-HASH-MANIFEST")
    manifest_lines.append("=" * 60)
    manifest_lines.append("Generated for MW Infrastructure Canon v2.0.0")
    manifest_lines.append("39 documents | CC BY-ND 4.0 | DOI: 10.5281/zenodo.18707171")
    manifest_lines.append("=" * 60)
    manifest_lines.append("")
    manifest_lines.append("{:<10} {:<50} {}".format("Doc #", "Source SHA3-512 (first 32)", "PDF SHA3-512 (first 32)"))
    manifest_lines.append("-" * 100)

    for i in range(1, 40):
        doc_id = "DOC-{:03d}".format(i)
        meta = documents.get(doc_id)
        if not meta:
            print("WARNING: {} not found in master index".format(doc_id))
            continue

        filepath = Path(meta['filepath'])
        if not filepath.exists():
            print("WARNING: {} not found at {}".format(doc_id, filepath))
            continue

        # Read and clean content
        with open(str(filepath), 'r', encoding='utf-8', errors='replace') as f:
            raw = f.read()
        content = clean_text(raw)
        title = meta.get('title', extract_title(content))
        title = clean_text(title)

        # Compute source hash
        src_hash = compute_sha3_512(str(filepath))

        # Output PDF path
        pdf_name = "MW-CANON-DOC-{:02d}.pdf".format(i)
        pdf_path = OUT_DIR / pdf_name

        print("Generating {} ({})...".format(pdf_name, doc_id))
        try:
            generate_pdf(i, title, content, src_hash, filepath, pdf_path)
        except Exception as e:
            print("  ERROR: {}".format(e))
            continue

        # Compute PDF hash
        pdf_hash = compute_sha3_512(str(pdf_path))

        manifest_lines.append("{:<10} {}  {}".format(
            "DOC-{:03d}".format(i),
            src_hash[:32],
            pdf_hash[:32]
        ))

        print("  OK - {} bytes".format(pdf_path.stat().st_size))

    # Write manifest
    manifest_path = OUT_DIR / "PDF-HASH-MANIFEST.txt"
    with open(str(manifest_path), 'w', encoding='utf-8') as f:
        f.write('\n'.join(manifest_lines) + '\n')

    print("\n=== COMPLETE ===")
    print("PDFs: {}".format(len(list(OUT_DIR.glob("*.pdf")))))
    print("Manifest: {}".format(manifest_path))


if __name__ == "__main__":
    main()
