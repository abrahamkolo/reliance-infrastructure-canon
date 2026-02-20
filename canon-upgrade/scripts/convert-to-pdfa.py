#!/usr/bin/env python3
"""
Convert all 39 canonical .txt documents to PDF/A format for Zenodo archival.

Requires LibreOffice installed and accessible from command line.
On Windows: typically at C:\\Program Files\\LibreOffice\\program\\soffice.exe
On Linux: soffice

Usage: python convert-to-pdfa.py
"""

import os
import subprocess
import sys
import json
import shutil
from pathlib import Path

def find_libreoffice():
    """Find LibreOffice executable."""
    candidates = [
        "soffice",  # Linux / macOS PATH
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for c in candidates:
        if shutil.which(c) or os.path.exists(c):
            return c
    return None

def convert_to_pdfa(soffice_path, input_file, output_dir):
    """Convert a single file to PDF using LibreOffice."""
    cmd = [
        soffice_path,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    return True

def main():
    soffice = find_libreoffice()
    if not soffice:
        print("ERROR: LibreOffice not found.")
        print("Install from https://www.libreoffice.org/download/")
        print("On Windows, default install location is checked automatically.")
        sys.exit(1)
    
    print(f"Using LibreOffice at: {soffice}")
    
    # Find all documents
    docs_dir = Path("documents")
    if not docs_dir.exists():
        print("ERROR: documents/ directory not found. Run from repository root.")
        sys.exit(1)
    
    output_dir = Path("pdfa-output")
    output_dir.mkdir(exist_ok=True)
    
    txt_files = sorted(docs_dir.rglob("*.txt"))
    print(f"Found {len(txt_files)} documents to convert.\n")
    
    converted = 0
    errors = []
    
    for i, txt_file in enumerate(txt_files):
        print(f"[{i+1}/{len(txt_files)}] {txt_file.name}")
        
        if convert_to_pdfa(soffice, str(txt_file), str(output_dir)):
            # Rename to standard format: DOC-XXX_TITLE_vX.X.X.pdf
            pdf_name = txt_file.stem + ".pdf"
            pdf_path = output_dir / pdf_name
            if pdf_path.exists():
                print(f"  -> {pdf_path}")
                converted += 1
            else:
                print(f"  WARNING: PDF not generated")
                errors.append(str(txt_file))
        else:
            errors.append(str(txt_file))
    
    print(f"\n{'='*50}")
    print(f"Converted: {converted}/{len(txt_files)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    
    print(f"\nPDF files are in: {output_dir}/")
    print(f"\nNote: LibreOffice produces standard PDF. For strict PDF/A-1b compliance,")
    print(f"you can post-process with ghostscript:")
    print(f"  gs -dPDFA=1 -dBATCH -dNOPAUSE -sProcessColorModel=DeviceRGB \\")
    print(f"     -sDEVICE=pdfwrite -sPDFACompatibilityPolicy=1 \\")
    print(f"     -sOutputFile=output-pdfa.pdf input.pdf")
    print(f"\nNext steps:")
    print(f"  1. Upload all PDFs to the Zenodo record alongside the .tar.gz")
    print(f"  2. Or use upload-per-document.py to create individual records with PDFs")

if __name__ == "__main__":
    main()
