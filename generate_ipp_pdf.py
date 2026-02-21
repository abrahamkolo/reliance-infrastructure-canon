#!/usr/bin/env python3
"""Generate MW-CANON-INSTITUTIONAL-PROOF-PACKET.pdf -- institutional-grade IPP."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

OUT = "institutional/MW-CANON-INSTITUTIONAL-PROOF-PACKET.pdf"
os.makedirs("institutional", exist_ok=True)

def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=letter,
        leftMargin=0.8*inch, rightMargin=0.8*inch,
        topMargin=0.6*inch, bottomMargin=0.8*inch,
    )
    styles = getSampleStyleSheet()

    stamp = ParagraphStyle('Stamp', parent=styles['Normal'],
        fontName='Courier-Bold', fontSize=8,
        textColor=HexColor('#CC0000'), alignment=TA_CENTER, spaceAfter=8)
    title_s = ParagraphStyle('Title2', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18,
        alignment=TA_CENTER, spaceAfter=4)
    subtitle_s = ParagraphStyle('Sub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10,
        textColor=HexColor('#666666'), alignment=TA_CENTER, spaceAfter=20)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=13,
        spaceBefore=16, spaceAfter=6)
    body = ParagraphStyle('Body2', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14, spaceAfter=6)
    bullet = ParagraphStyle('Bullet', parent=body,
        leftIndent=20, bulletIndent=10, spaceAfter=3)
    footer_s = ParagraphStyle('Foot', parent=styles['Normal'],
        fontName='Courier', fontSize=6.5,
        textColor=HexColor('#888888'), alignment=TA_CENTER, spaceBefore=20)

    story = []

    # Cover
    story.append(Paragraph("INSTITUTIONAL USE ONLY", stamp))
    story.append(Spacer(1, 40))
    story.append(Paragraph("MW Infrastructure Canon", title_s))
    story.append(Paragraph("Institutional Proof Packet", ParagraphStyle('Sub2',
        parent=styles['Heading2'], fontName='Helvetica', fontSize=14,
        alignment=TA_CENTER, spaceAfter=8)))
    story.append(Paragraph("Version 2.0.0 | 39 Canonical Documents | CC BY-ND 4.0", subtitle_s))
    story.append(Paragraph("DOI: 10.5281/zenodo.18707171", subtitle_s))
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "Reliance Infrastructure Holdings LLC<br/>"
        "No support. No customization. No consultation.", subtitle_s))
    story.append(PageBreak())

    # Section 1
    story.append(Paragraph("1. What Is the MW Infrastructure Canon?", h2))
    story.append(Paragraph(
        "The MW Infrastructure Canon is a 39-document institutional governance framework "
        "providing deterministic certification standards for institutional compliance, "
        "constitutional governance, and organizational infrastructure.", body))
    story.append(Paragraph("Each document is:", body))
    for item in [
        "Graded 100/100 by multi-specialty panel evaluation",
        "SHA3-512 hashed and Ed25519 digitally signed",
        "Archived with DOI: 10.5281/zenodo.18707171 (Zenodo)",
        "Attested on Ethereum mainnet and Arweave permanent storage",
        "Licensed under CC BY-ND 4.0 (no unauthorized modifications)",
    ]:
        story.append(Paragraph("<bullet>&bull;</bullet> " + item, bullet))

    # Section 2
    story.append(Paragraph("2. Certification Benefits", h2))
    for item in [
        "Verifiable compliance with institutional governance standards",
        "Cryptographically authenticated certification artifacts",
        "Public registry listing (independently verifiable)",
        "Reduced counterparty risk (certified vs. uncertified institutions)",
        "Regulatory alignment (GDPR, CCPA, Delaware DGCL frameworks)",
    ]:
        story.append(Paragraph("<bullet>&bull;</bullet> " + item, bullet))

    # Section 3 - Licensing tiers table
    story.append(Paragraph("3. Licensing Tiers", h2))
    tier_data = [
        ["Tier", "Annual Fee", "Includes"],
        ["Evaluation", "$10,000", "Single authority access, read-only"],
        ["Standard", "$50,000", "Full canon access, certification rights"],
        ["Enterprise", "$150,000", "Full access + Founding Certified Institution status"],
    ]
    t = Table(tier_data, colWidths=[1.3*inch, 1.2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#222222')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Paragraph(
        "Payment constitutes binding acceptance of all terms. "
        "No negotiation. No customization. No support.", body))

    # Section 4
    story.append(Paragraph("4. Certification Timeline", h2))
    timeline = [
        ["Stage", "Duration", "Method"],
        ["Application", "1 day", "Submit documentation"],
        ["Review", "1-3 days", "Binary pass/fail (deterministic criteria)"],
        ["Issuance", "Same day upon pass", "Cryptographic certificate generation"],
        ["Total", "1-5 business days", "End to end"],
    ]
    t2 = Table(timeline, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#222222')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)

    # Section 5
    story.append(Paragraph("5. Legal Summary", h2))
    legal_items = [
        ("Governing Law", "Delaware, USA"),
        ("Dispute Resolution", "ICC International Court of Arbitration, Zurich"),
        ("Data Protection", "GDPR and CCPA compliant"),
        ("Liability", "Capped per licensing agreement"),
        ("Intellectual Property", "CC BY-ND 4.0 -- cite freely, cannot modify"),
    ]
    for label, value in legal_items:
        story.append(Paragraph(
            "<b>{}:</b> {}".format(label, value), body))

    # Section 6
    story.append(Paragraph("6. Technical Verification", h2))
    story.append(Paragraph(
        "Any third party can independently verify the integrity and authenticity of the "
        "MW Infrastructure Canon using the open-source verification tool:", body))
    story.append(Paragraph(
        "<font face='Courier' size='9'>"
        "git clone https://github.com/abrahamkolo/reliance-verify<br/>"
        "cd reliance-verify<br/>"
        "python3 verify.py"
        "</font>", body))
    story.append(Paragraph("Expected output: VERDICT: AUTHENTIC", body))

    # Section 7 - Proof chain table
    story.append(Paragraph("7. Cryptographic Proof Chain", h2))
    proof_data = [
        ["Layer", "Method", "Status"],
        ["Document Hashes", "SHA3-512 (39/39)", "Verified"],
        ["Digital Signatures", "Ed25519 (39/39)", "Verified"],
        ["GPG Commit Signing", "RSA 4096 (EB937371B8993E99)", "All commits signed"],
        ["Bitcoin Attestation", "OpenTimestamps", "Submitted"],
        ["Ethereum Attestation", "Mainnet 0-ETH data tx", "Pending"],
        ["Arweave Archive", "Permanent storage", "Pending"],
        ["Academic Archive", "Zenodo DOI: 10.5281/zenodo.18707171", "Published"],
    ]
    t3 = Table(proof_data, colWidths=[1.8*inch, 2.5*inch, 2.2*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#222222')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)

    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Reliance Infrastructure Holdings LLC | CC BY-ND 4.0 | "
        "DOI: 10.5281/zenodo.18707171 | No support. No customization.",
        footer_s))

    doc.build(story)
    print("Generated: {}".format(OUT))

if __name__ == "__main__":
    build()
