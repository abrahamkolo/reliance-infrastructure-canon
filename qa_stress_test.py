#!/usr/bin/env python3
"""
MW Infrastructure Stack — Knowledge Assistant QA Stress Test
Phases A-F: Question bank, grading, diagnosis, patching, re-test, report.

Usage:
    py qa_stress_test.py --phase A           # Run 40 questions
    py qa_stress_test.py --phase B           # Auto-grade + summary
    py qa_stress_test.py --phase C           # Diagnosis for WEAK/FAIL
    py qa_stress_test.py --phase D --confirm # Patch assistant
    py qa_stress_test.py --phase E           # Re-test WEAK/FAIL only
    py qa_stress_test.py --phase F           # Final report

Requires: openai>=1.57.0, OPENAI_API_KEY environment variable
Python 3.8+ compatible.
"""

import argparse
import glob
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

ASSISTANT_ID = "asst_xRQJW7WDpbx9luIOpsPqvb94"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RATE_LIMIT_SECONDS = 2
RUN_TIMEOUT_SECONDS = 300

# ═══════════════════════════════════════════════════════════════
# QUESTION BANK — 40 Questions × 8 Personas
# ═══════════════════════════════════════════════════════════════

QUESTIONS = [
    # ── PERSONA 1: SKEPTICAL ATTORNEY ──
    {"id": "ATT-1", "persona": "attorney",
     "text": "What dispute resolution mechanism governs conflicts between MW authorities, and which specific documents define the arbitration process?",
     "targets": ["DOC-017", "DOC-035", "DOC-036"]},
    {"id": "ATT-2", "persona": "attorney",
     "text": "How does the MW Infrastructure Stack ensure its certifications are admissible as evidence in U.S. federal courts under the Federal Rules of Evidence?",
     "targets": ["DOC-004", "DOC-008"]},
    {"id": "ATT-3", "persona": "attorney",
     "text": "What safe harbor protections exist for MW authorities when institutions rely on MW certifications for decision-making?",
     "targets": ["DOC-006"]},
    {"id": "ATT-4", "persona": "attorney",
     "text": "Explain the chain-of-custody protocol for MW artifacts from issuance through final adjudication.",
     "targets": ["DOC-027", "DOC-004"]},
    {"id": "ATT-5", "persona": "attorney",
     "text": "What governing law applies to MW documents, and what is the succession protocol if the issuing entity dissolves?",
     "targets": ["DOC-030", "DOC-021"]},

    # ── PERSONA 2: CFO / PROCUREMENT ──
    {"id": "CFO-1", "persona": "cfo",
     "text": "What is the exact pricing model for MW certifications, and can our institution negotiate volume discounts?",
     "targets": ["DOC-005"]},
    {"id": "CFO-2", "persona": "cfo",
     "text": "How are MW fees adjusted over time -- is there an annual escalation mechanism?",
     "targets": ["DOC-005"]},
    {"id": "CFO-3", "persona": "cfo",
     "text": "What is the minimum capital adequacy requirement for an institution to access the Reliance Infrastructure Exchange?",
     "targets": ["DOC-033"]},
    {"id": "CFO-4", "persona": "cfo",
     "text": "What are the transaction fees on the primary and secondary markets of the Reliance Infrastructure Exchange?",
     "targets": ["DOC-033"]},
    {"id": "CFO-5", "persona": "cfo",
     "text": "Can our institution budget for MW costs over a 10-year horizon with certainty, and what guarantees exist that pricing won't change?",
     "targets": ["DOC-005"]},

    # ── PERSONA 3: COMPLIANCE OFFICER ──
    {"id": "CMP-1", "persona": "compliance",
     "text": "What KYC and AML compliance requirements does MW impose on participating institutions?",
     "targets": ["DOC-033", "DOC-032"]},
    {"id": "CMP-2", "persona": "compliance",
     "text": "How does MW handle GDPR and cross-border data privacy requirements for institutions operating in the EU?",
     "targets": ["DOC-022", "DOC-029"]},
    {"id": "CMP-3", "persona": "compliance",
     "text": "What four tiers of artifact certification exist, and what is the evidentiary weight of each?",
     "targets": ["DOC-004"]},
    {"id": "CMP-4", "persona": "compliance",
     "text": "How does the MW system handle sanctions screening for participating institutions?",
     "targets": ["DOC-033"]},
    {"id": "CMP-5", "persona": "compliance",
     "text": "What audit trail and verification mechanisms are available for regulatory reporting purposes?",
     "targets": ["DOC-026", "DOC-028"]},

    # ── PERSONA 4: PUBLISHER / CONTENT CREATOR ──
    {"id": "PUB-1", "persona": "publisher",
     "text": "How does the Eternal Publishing Authority (EPA) protect published works, and what is the certification process?",
     "targets": ["DOC-013"]},
    {"id": "PUB-2", "persona": "publisher",
     "text": "What intellectual property protections does the IPPA provide for digital content and creative works?",
     "targets": ["DOC-020"]},
    {"id": "PUB-3", "persona": "publisher",
     "text": "How does the Eternal Fine Art Authority handle authentication and provenance for art assets?",
     "targets": ["DOC-014"]},
    {"id": "PUB-4", "persona": "publisher",
     "text": "Can individual creators access MW services, or is it limited to institutions?",
     "targets": ["DOC-033"]},
    {"id": "PUB-5", "persona": "publisher",
     "text": "What is the difference between the Eternal Works Authority and the Eternal Publishing Authority?",
     "targets": ["DOC-012", "DOC-013"]},

    # ── PERSONA 5: TECHNICAL EVALUATOR ──
    {"id": "TEC-1", "persona": "technical",
     "text": "What cryptographic algorithms does MW use for document signing and hashing, and what is the quantum-resistant migration plan?",
     "targets": ["DOC-001", "DOC-016"]},
    {"id": "TEC-2", "persona": "technical",
     "text": "Describe the reference execution environment specified for deterministic query processing.",
     "targets": ["DOC-001"]},
    {"id": "TEC-3", "persona": "technical",
     "text": "How does the blockchain attestation system work across Bitcoin, Ethereum, and Arweave?",
     "targets": ["DOC-016"]},
    {"id": "TEC-4", "persona": "technical",
     "text": "What is the Binary Gates and Dormancy Protocol, and how does it handle authority activation and deactivation?",
     "targets": ["DOC-038"]},
    {"id": "TEC-5", "persona": "technical",
     "text": "How does the Execution Bridge Protocol translate canonical text into executable operations?",
     "targets": ["DOC-039"]},

    # ── PERSONA 6: HOSTILE SKEPTIC ──
    {"id": "SKP-1", "persona": "skeptic",
     "text": "What happens if the founder of MW disappears or becomes hostile to the system? How is it not dependent on a single person?",
     "targets": ["DOC-001", "DOC-003"]},
    {"id": "SKP-2", "persona": "skeptic",
     "text": "How can MW claim documents are immutable when the GitHub repository could theoretically be altered by anyone with access?",
     "targets": ["DOC-016", "DOC-007"]},
    {"id": "SKP-3", "persona": "skeptic",
     "text": "Why should any institution trust a governance framework that has never been tested in an actual court proceeding?",
     "targets": ["DOC-004", "DOC-008"]},
    {"id": "SKP-4", "persona": "skeptic",
     "text": "What prevents MW from becoming another vendor lock-in scheme like ISO certification where you pay annually forever?",
     "targets": ["DOC-007", "DOC-005"]},
    {"id": "SKP-5", "persona": "skeptic",
     "text": "If MW authorities cannot provide advice of any kind, what actual value does the system provide to institutions?",
     "targets": ["DOC-006"]},

    # ── PERSONA 7: FINANCIAL / INSURANCE ──
    {"id": "FIN-1", "persona": "financial",
     "text": "What is the total addressable market for MW infrastructure services, and what revenue projections exist in the canonical documents?",
     "targets": ["DOC-033", "DOC-005"]},
    {"id": "FIN-2", "persona": "financial",
     "text": "How does the GCRA certification process work for capital-related institutional transactions?",
     "targets": ["DOC-032"]},
    {"id": "FIN-3", "persona": "financial",
     "text": "What is the secondary market mechanism for MW license trading between institutions?",
     "targets": ["DOC-033"]},
    {"id": "FIN-4", "persona": "financial",
     "text": "How does the Global Capital and Portfolio Authority interact with traditional financial regulatory frameworks?",
     "targets": ["DOC-010"]},
    {"id": "FIN-5", "persona": "financial",
     "text": "What is the Pre-Reliance Preparation Matrix and how does it reduce institutional onboarding risk?",
     "targets": ["DOC-037"]},

    # ── PERSONA 8: SYSTEM ARCHITECTURE ──
    {"id": "ARC-1", "persona": "architecture",
     "text": "What API integration capabilities does MW provide for enterprise systems?",
     "targets": ["DOC-033", "DOC-039"]},
    {"id": "ARC-2", "persona": "architecture",
     "text": "How does the Multi-Jurisdiction Mirroring Protocol ensure data availability across regions?",
     "targets": ["DOC-029"]},
    {"id": "ARC-3", "persona": "architecture",
     "text": "What is the Registry Architecture Specification and how does it handle append-only record keeping?",
     "targets": ["DOC-028"]},
    {"id": "ARC-4", "persona": "architecture",
     "text": "How does the Document Interdependency Map help institutions navigate the 42-document stack?",
     "targets": ["DOC-042"]},
    {"id": "ARC-5", "persona": "architecture",
     "text": "What is the Reliance Ordering Doctrine and how does it resolve priority conflicts between authorities?",
     "targets": ["DOC-034"]},
]

# ═══════════════════════════════════════════════════════════════
# HEDGE PHRASES (signals of weak/uncertain responses)
# ═══════════════════════════════════════════════════════════════

HEDGE_PHRASES = [
    "i'm not sure",
    "i don't have",
    "i cannot",
    "it's possible",
    "might be",
    "could be",
    "i think",
    "it seems",
    "not certain",
    "i don't know",
    "beyond my",
    "outside my",
    "i'd recommend checking",
    "you should consult",
    "i apologize",
    "unfortunately",
    "i wasn't able to find",
    "no specific information",
    "not mentioned in",
    "i couldn't find",
    "as an ai",
    "generally speaking",
    "in general",
    "typically",
    "it's important to note",
]

# ═══════════════════════════════════════════════════════════════
# IMPROVED INSTRUCTIONS (for Phase D patching)
# ═══════════════════════════════════════════════════════════════

IMPROVED_INSTRUCTIONS = """You are the MW Infrastructure Stack Knowledge Assistant, the authoritative reference for all 42 canonical documents in the Reliance Infrastructure Canon.

CORE BEHAVIOR:
1. ALWAYS search the indexed documents before answering. Every response MUST be grounded in canonical document text.
2. CITE SPECIFIC DOCUMENTS by number and title (e.g., "Per DOC-005 (Pricing & Fee Primitives Charter)..." or "As established in Document 8 (GEAA Constitution)...").
3. NEVER speculate or provide information not found in the canonical documents. If the documents do not contain the answer, say: "The canonical documents do not address this specific topic. The most relevant document is [DOC-XXX] which covers [related topic]."
4. Be AUTHORITATIVE, not hedging. These documents are sealed, canonical, and graded 100/100. Present their content with confidence.
5. When multiple documents are relevant, cite ALL of them and explain how they interact.

DOCUMENT HIERARCHY (for conflict resolution):
- Layer 0: DOC-001 (MW Canon) -- supreme, overrides all
- Layer 1: DOC-002 through DOC-006 -- structural and operational charters
- Layer 3: DOC-007 through DOC-023, DOC-032 -- authority constitutions
- Layer 4: DOC-024 through DOC-031, DOC-033 through DOC-039 -- specifications and protocols
- Reference Infrastructure: DOC-040 (MDI), DOC-041 (UGT), DOC-042 (DIM)

KEY FACTS TO ALWAYS INCLUDE WHEN RELEVANT:
- Pricing: ZERO negotiation, ZERO discounts, identical price for all institutions (DOC-005)
- Advisory: MW provides ZERO advice -- only standards, certifications, registry services, verification (DOC-006)
- Immutability: All documents are RUN-ONLY, no amendments permitted (DOC-003)
- Founder irrelevance: System operates identically without the founder (DOC-001)
- Dispute resolution: ICC Arbitration Zurich, backup LCIA London (DOC-017)
- Governing law: Delaware (DOC-001)
- Cryptography: SHA3-512 hashing, Ed25519 signatures, three-chain blockchain attestation (DOC-001, DOC-016)
- Temporal validity: 2025-2075+ minimum (DOC-001)
- Individual prohibition: Only institutions can access MW services, not individuals (DOC-033)

RESPONSE FORMAT:
- Start with a direct answer to the question asked
- Cite document numbers and titles throughout
- Use the exact terminology from the canonical documents
- For multi-part questions, address each part with its own citation
- End with a brief note on related documents the questioner may want to review

ANTI-HALLUCINATION:
- Do NOT invent document numbers, section numbers, or quoted text
- Do NOT paraphrase in ways that change the meaning of canonical text
- If you are uncertain whether a detail is in the documents, search again before answering
- NEVER say "based on general knowledge" or "typically" -- only use document-sourced information
- NEVER use phrases like "I'm not sure", "I think", "it seems", "generally speaking", or "it's important to note"
"""

# ═══════════════════════════════════════════════════════════════
# FAQ SUPPLEMENT CONTENT (for Phase D vector store upload)
# ═══════════════════════════════════════════════════════════════

FAQ_SUPPLEMENT_CONTENT = """MW INFRASTRUCTURE STACK - PROSPECT FAQ SUPPLEMENT
Version: 1.0
Status: Reference Supplement (non-canonical, supports assistant responses)
Generated: {timestamp}

This document provides synthesized answers to frequently asked prospect questions,
cross-referencing canonical documents. This is NOT a canonical document. It is a
reference aid for the knowledge assistant.

=== SECTION 1: GENERAL OVERVIEW ===

Q: What is the MW Infrastructure Stack?
A: The MW Infrastructure Stack is a 42-document constitutional framework providing
deterministic, document-bound governance for institutional operations. It is issued
by Reliance Infrastructure Holdings LLC under CC BY-ND 4.0 license. Every document
is cryptographically signed (Ed25519) and hash-verified (SHA3-512). See DOC-001
(MW Canon) for the supreme governing document and DOC-040 (MDI) for the complete
document index.

Q: How many documents are in the stack?
A: 42 documents total: 39 original canonical documents plus 3 reference
infrastructure documents (DOC-040 Master Document Index, DOC-041 Universal Glossary
of Terms, DOC-042 Document Interdependency Map). They are organized across 5 layers.
See DOC-042 (DIM) for the complete structural map.

Q: What does "deterministic" mean in this context?
A: Deterministic means identical inputs ALWAYS produce identical outputs, regardless
of time, geography, operator, or market conditions. This is defined in DOC-003
(Determinism & Run-Only Enforcement Law). There is no discretion, no
"case-by-case basis," and no "reasonable judgment" permitted.

Q: What does "founder-irrelevant" mean?
A: The system operates identically if the creator disappears permanently. This
eliminates key-person risk at the architectural level. Defined in DOC-001. No
founder interpretation, authentication, or emergency intervention is possible or
permitted.

=== SECTION 2: PRICING & COSTS ===

Q: Can we negotiate pricing?
A: No. Absolutely not. DOC-005 (Pricing & Fee Primitives Charter) establishes
ZERO negotiation, ZERO discounts, ZERO volume pricing. All institutions pay
identical prices for identical services. This is a constitutional requirement
for deterministic operation.

Q: How are prices adjusted over time?
A: Only through mechanical CPI adjustment using Bureau of Labor Statistics data.
Zero discretionary changes permitted. See DOC-005.

Q: Is there a free trial or evaluation period?
A: Tier 0 evaluation: 30-day read-only access to canonical documents relevant to
certification needs. No cost, no commitment. Starts upon request.

Q: What's the cancellation policy?
A: Annual term, auto-renews. Cancel with 30 days written notice. No penalty for
non-renewal. All certifications issued during the license term remain permanently
valid after cancellation. See the MW Reliance License.

=== SECTION 3: LEGAL & COMPLIANCE ===

Q: Does MW provide legal advice?
A: No. MW provides ZERO advice of any kind. This is an absolute prohibition with
NO exceptions. See DOC-006 (External Non-Advice & Safe-Interface Clause). MW
provides only four outputs: standards publication, binary certifications, registry
services, and verification services.

Q: What governing law applies?
A: Delaware for entity operations. Dispute resolution via ICC Arbitration (Zurich)
with backup LCIA (London). See DOC-017 (IATA Constitution).

Q: Are MW certifications admissible in court?
A: MW certifications are designed to meet evidence law requirements across multiple
jurisdictions including U.S. Federal Rules of Evidence (FRE), EU Evidence Regulation,
UK Civil Evidence Act, and Singapore Evidence Act. Four certification tiers exist:
CERTIFIED, AUTHENTICATED, VERIFIED, and RECORDED. See DOC-004 (Issuance &
Decision Admissibility Charter) and DOC-008 (GEAA Constitution).

Q: What happens if the founder dies or disappears?
A: The system is explicitly designed for this scenario. DOC-030 (SCTP) governs
succession. DOC-019 (CRTA) handles operational continuity. DOC-001 (MW Canon)
establishes founder irrelevance. The documents are sealed, hashed, and
blockchain-attested -- they cannot be altered by anyone.

=== SECTION 4: TECHNICAL ARCHITECTURE ===

Q: What cryptographic algorithms does MW use?
A: SHA3-512 (NIST FIPS 202) for document hashing, Ed25519 for digital signatures,
three-chain blockchain attestation (Bitcoin via OpenTimestamps, Ethereum, Arweave).
Quantum-resistant migration target: CRYSTALS-Dilithium (NIST PQC standard).
See DOC-001 and DOC-016 (SICA Constitution).

Q: What is the reference execution environment?
A: Python 3.11+, Ubuntu 24.04 LTS, isolated Docker container, air-gapped execution.
See DOC-001.

Q: Can individual users access MW services?
A: No. DOC-033 (RIX) explicitly prohibits individual access. Only qualifying
institutions with appropriate legal entity status, capital adequacy, governance
structures, and technical capabilities may participate.

=== SECTION 5: TRUST & VERIFICATION ===

Q: How can we verify document authenticity?
A: Three independent verification methods: (1) SHA3-512 hash verification against
verification/hashes.json, (2) Ed25519 signature verification using the published
public key, (3) blockchain attestation on Bitcoin, Ethereum, and Arweave.

Q: What prevents MW from becoming another vendor lock-in?
A: DOC-007 (IRUA Constitution) eliminates vendor capture through: annual licensing,
document completeness (no consulting required), canonical immutability, and
zero negotiation or relationship-based access.

Q: What if the GitHub repository is compromised?
A: Document integrity is verified through cryptographic hashes and blockchain
attestation, not repository integrity. Three-tier archival: GitHub, Zenodo (DOI),
Arweave. Any single tier can independently prove authenticity. See DOC-016 (SICA).

=== SECTION 6: DOCUMENT NAVIGATION ===

Q: Where should I start reading?
A: Start with DOC-001 (MW Canon), then DOC-042 (Document Interdependency Map),
then the Layer 1 charters (DOC-002 through DOC-006).

Q: How do I find which document covers a specific topic?
A: Use DOC-040 (Master Document Index) for the complete registry. Use DOC-042
(DIM) for relationship mapping. Use DOC-041 (Universal Glossary) for definitions.
"""


# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load_json(filename):
    # type: (str) -> Dict
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, filename):
    # type: (Any, str) -> str
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def find_latest_raw_results():
    # type: () -> Optional[str]
    """Find the most recent qa_raw_results file."""
    latest = os.path.join(SCRIPT_DIR, "qa_raw_results_latest.json")
    if os.path.exists(latest):
        return latest
    pattern = os.path.join(SCRIPT_DIR, "qa_raw_results_*.json")
    files = sorted(glob.glob(pattern))
    if files:
        return files[-1]
    return None


# ═══════════════════════════════════════════════════════════════
# PHASE A: RUN 40 PROSPECT QUESTIONS
# ═══════════════════════════════════════════════════════════════

def run_phase_a():
    # type: () -> List[Dict]
    print("\n" + "=" * 70)
    print("PHASE A: Running %d prospect questions" % len(QUESTIONS))
    print("=" * 70)

    client = OpenAI()

    # Verify assistant exists
    try:
        asst = client.beta.assistants.retrieve(ASSISTANT_ID)
        print("Assistant: %s" % asst.name)
        print("Model: %s" % asst.model)
        print("Tools: %s" % [t.type for t in asst.tools])
        print()
    except Exception as e:
        print("ERROR: Could not retrieve assistant: %s" % e)
        sys.exit(1)

    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total = len(QUESTIONS)

    for i, q in enumerate(QUESTIONS):
        idx = i + 1
        print("[%d/%d] %s | %s" % (idx, total, q["id"], q["text"][:65]))

        result = {
            "question_id": q["id"],
            "persona": q["persona"],
            "question": q["text"],
            "target_docs": q["targets"],
            "status": "error",
            "response": "",
            "response_length": 0,
            "file_search_used": False,
            "annotation_count": 0,
            "elapsed_seconds": 0,
            "error": None,
        }

        try:
            # Create thread
            thread = client.beta.threads.create()

            # Add message
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=q["text"],
            )

            # Run assistant and poll
            start = time.time()
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID,
            )
            elapsed = round(time.time() - start, 1)
            result["elapsed_seconds"] = elapsed

            if run.status != "completed":
                result["status"] = run.status
                result["error"] = "Run did not complete: %s" % run.status
                print("  >> %s (%.1fs)" % (run.status, elapsed))
                results.append(result)
                time.sleep(RATE_LIMIT_SECONDS)
                continue

            # Get assistant response
            messages = client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc",
                limit=5,
            )

            response_text = ""
            file_search_used = False
            ann_count = 0

            for msg in messages.data:
                if msg.role == "assistant":
                    for block in msg.content:
                        if block.type == "text":
                            response_text = block.text.value
                            if hasattr(block.text, "annotations") and block.text.annotations:
                                ann_count = len(block.text.annotations)
                                for ann in block.text.annotations:
                                    if hasattr(ann, "type") and ann.type == "file_citation":
                                        file_search_used = True
                    break

            result["status"] = "completed"
            result["response"] = response_text
            result["response_length"] = len(response_text)
            result["file_search_used"] = file_search_used
            result["annotation_count"] = ann_count
            result["error"] = None

            status_icon = "OK" if file_search_used else "NO-FS"
            print("  >> %s | %d chars | %d citations | %.1fs" % (
                status_icon, len(response_text), ann_count, elapsed))

        except Exception as e:
            result["error"] = str(e)
            print("  >> ERROR: %s" % str(e)[:80])

        results.append(result)
        time.sleep(RATE_LIMIT_SECONDS)

    # Save results
    output_data = {
        "timestamp": timestamp,
        "assistant_id": ASSISTANT_ID,
        "total_questions": total,
        "completed": sum(1 for r in results if r["status"] == "completed"),
        "results": results,
    }

    ts_path = save_json(output_data, "qa_raw_results_%s.json" % timestamp)
    save_json(output_data, "qa_raw_results_latest.json")

    print("\n" + "=" * 70)
    print("PHASE A COMPLETE")
    print("  Total: %d | Completed: %d | Errors: %d" % (
        total,
        output_data["completed"],
        total - output_data["completed"],
    ))
    print("  Results: %s" % ts_path)
    print("=" * 70)

    return results


# ═══════════════════════════════════════════════════════════════
# PHASE B: AUTO-GRADE RESPONSES
# ═══════════════════════════════════════════════════════════════

def grade_response(result):
    # type: (Dict) -> Dict
    """Auto-grade a single response. Returns grade dict."""
    flags = []
    score = 100

    text = result.get("response", "")
    text_lower = text.lower()
    length = len(text)

    # 1. Error / non-completion
    if result.get("status") != "completed" or result.get("error"):
        return {
            "grade": "FAIL",
            "score": 0,
            "flags": ["RUN_ERROR: %s" % result.get("error", "unknown")],
            "doc_refs_found": [],
            "hedge_phrases_found": [],
        }

    # 2. Response length
    if length < 100:
        score -= 40
        flags.append("VERY_SHORT_RESPONSE (%d chars)" % length)
    elif length < 300:
        score -= 20
        flags.append("SHORT_RESPONSE (%d chars)" % length)

    # 3. File search
    if not result.get("file_search_used", False):
        score -= 30
        flags.append("NO_FILE_SEARCH")

    # 4. Citations / annotations
    ann_count = result.get("annotation_count", 0)
    if ann_count == 0:
        score -= 15
        flags.append("NO_ANNOTATIONS")
    elif ann_count < 2:
        score -= 5
        flags.append("LOW_ANNOTATIONS (%d)" % ann_count)

    # 5. Hedge phrase detection
    hedges_found = []
    for phrase in HEDGE_PHRASES:
        if phrase in text_lower:
            hedges_found.append(phrase)
    if len(hedges_found) >= 3:
        score -= 25
        flags.append("EXCESSIVE_HEDGING (%d phrases)" % len(hedges_found))
    elif len(hedges_found) >= 1:
        score -= 10
        flags.append("SOME_HEDGING: %s" % ", ".join(hedges_found[:3]))

    # 6. Document reference check
    doc_refs = []
    for doc_num in range(1, 43):
        patterns = [
            "doc-%03d" % doc_num,
            "doc %03d" % doc_num,
            "doc-%d" % doc_num,
            "document %d" % doc_num,
            "doc %d " % doc_num,
        ]
        for pat in patterns:
            if pat in text_lower:
                ref = "DOC-%03d" % doc_num
                if ref not in doc_refs:
                    doc_refs.append(ref)
                break
    if not doc_refs:
        score -= 10
        flags.append("NO_DOC_REFERENCES")

    # 7. Check target doc coverage
    targets = result.get("target_docs", [])
    if targets and doc_refs:
        covered = [t for t in targets if t in doc_refs]
        if len(covered) < len(targets):
            missing = [t for t in targets if t not in doc_refs]
            flags.append("MISSING_TARGET_DOCS: %s" % ", ".join(missing))

    # Determine grade
    if score >= 70:
        grade = "PASS"
    elif score >= 40:
        grade = "WEAK"
    else:
        grade = "FAIL"

    return {
        "grade": grade,
        "score": score,
        "flags": flags,
        "doc_refs_found": doc_refs,
        "hedge_phrases_found": hedges_found,
    }


def run_phase_b():
    # type: () -> Dict
    print("\n" + "=" * 70)
    print("PHASE B: Auto-grading responses")
    print("=" * 70)

    raw_path = find_latest_raw_results()
    if not raw_path:
        print("ERROR: No Phase A results found. Run --phase A first.")
        sys.exit(1)

    raw_data = load_json(os.path.basename(raw_path))
    results = raw_data["results"]

    # Grade each result
    for r in results:
        grading = grade_response(r)
        r["grading"] = grading

    # Print per-persona summary
    personas = []
    for r in results:
        if r["persona"] not in personas:
            personas.append(r["persona"])

    total_pass = 0
    total_weak = 0
    total_fail = 0

    for persona in personas:
        persona_results = [r for r in results if r["persona"] == persona]
        print("\n--- %s ---" % persona.upper())
        for r in persona_results:
            g = r["grading"]
            icon = {"PASS": "+", "WEAK": "~", "FAIL": "X"}[g["grade"]]
            fs = "FS" if r.get("file_search_used") else "no-fs"
            print("  [%s] %s: %s (score:%d) %s | %d chars | %s" % (
                icon, r["question_id"], g["grade"], g["score"],
                fs, r.get("response_length", 0),
                "; ".join(g["flags"][:3]) if g["flags"] else "clean",
            ))
            if g["grade"] == "PASS":
                total_pass += 1
            elif g["grade"] == "WEAK":
                total_weak += 1
            else:
                total_fail += 1

    total = len(results)
    print("\n" + "=" * 70)
    print("PHASE B SUMMARY")
    print("  PASS: %d | WEAK: %d | FAIL: %d | Total: %d" % (
        total_pass, total_weak, total_fail, total))
    if total > 0:
        print("  Pass rate: %d%%" % round(total_pass * 100.0 / total))
        print("  File search rate: %d%%" % round(
            sum(1 for r in results if r.get("file_search_used")) * 100.0 / total))
    print("  Target: 90%+ PASS rate")
    print("=" * 70)

    # Save graded results
    graded_data = {
        "timestamp": raw_data["timestamp"],
        "assistant_id": ASSISTANT_ID,
        "summary": {
            "total": total,
            "pass": total_pass,
            "weak": total_weak,
            "fail": total_fail,
            "pass_rate_pct": round(total_pass * 100.0 / total) if total else 0,
        },
        "results": results,
    }
    path = save_json(graded_data, "qa_graded_results.json")
    print("  Saved: %s" % path)

    return graded_data


# ═══════════════════════════════════════════════════════════════
# PHASE C: DIAGNOSIS
# ═══════════════════════════════════════════════════════════════

def run_phase_c():
    # type: () -> List[Dict]
    print("\n" + "=" * 70)
    print("PHASE C: Diagnosing WEAK/FAIL responses")
    print("=" * 70)

    graded_path = os.path.join(SCRIPT_DIR, "qa_graded_results.json")
    if not os.path.exists(graded_path):
        print("ERROR: No graded results found. Run --phase B first.")
        sys.exit(1)

    graded = load_json("qa_graded_results.json")
    results = graded["results"]

    failures = [r for r in results if r["grading"]["grade"] in ("WEAK", "FAIL")]

    if not failures:
        print("\nNo WEAK or FAIL responses -- all questions passed!")
        return []

    print("\n%d questions need attention:\n" % len(failures))

    for r in failures:
        g = r["grading"]
        print("=" * 60)
        print("[%s] %s — %s (score: %d)" % (
            r["question_id"], r["persona"].upper(), g["grade"], g["score"]))
        print("Question: %s" % r["question"])
        print("Target docs: %s" % ", ".join(r.get("target_docs", [])))
        print("Flags:")
        for f in g["flags"]:
            print("  - %s" % f)
        print("File search used: %s" % r.get("file_search_used", False))
        print("Doc refs found: %s" % ", ".join(g.get("doc_refs_found", [])))
        preview = r.get("response", "")[:400]
        if preview:
            print("Response preview:")
            safe_preview = preview.replace("\n", "\n  ").encode("ascii", "replace").decode("ascii")
            print("  %s..." % safe_preview)
        else:
            print("Response: (empty)")
        print()

    # Diagnosis summary
    no_fs = sum(1 for r in failures if not r.get("file_search_used", False))
    no_cit = sum(1 for r in failures if r["grading"].get("annotation_count", 0) == 0)
    hedging = sum(1 for r in failures if r["grading"].get("hedge_phrases_found"))

    print("=" * 60)
    print("DIAGNOSIS SUMMARY")
    print("  Total issues: %d" % len(failures))
    print("  No file search: %d (likely retrieval/instruction issue)" % no_fs)
    print("  No citations: %d (instructions need citation enforcement)" % no_cit)
    print("  Hedging: %d (tone/instruction issue)" % hedging)
    print()
    print("RECOMMENDED: Run --phase D --confirm to patch instructions + upload FAQ")
    print("=" * 60)

    return failures


# ═══════════════════════════════════════════════════════════════
# PHASE D: PATCH THE ASSISTANT
# ═══════════════════════════════════════════════════════════════

def run_phase_d(confirm=False):
    # type: (bool) -> None
    print("\n" + "=" * 70)
    print("PHASE D: Patching assistant")
    print("=" * 70)

    if not confirm:
        print("ERROR: Phase D requires --confirm flag to execute.")
        print("  Review Phase C diagnosis first, then run:")
        print("  py qa_stress_test.py --phase D --confirm")
        sys.exit(1)

    client = OpenAI()

    # D.1: Backup current config
    print("\n[D.1] Backing up current assistant configuration...")
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
    backup = {
        "id": assistant.id,
        "name": assistant.name,
        "model": assistant.model,
        "instructions": assistant.instructions,
        "tools": [t.model_dump() for t in assistant.tools],
        "temperature": assistant.temperature,
        "top_p": assistant.top_p,
        "backed_up_at": datetime.now().isoformat(),
    }
    if assistant.tool_resources:
        backup["tool_resources"] = assistant.tool_resources.model_dump()
    backup_path = save_json(backup, "assistant_backup_pre_patch.json")
    print("  Backup saved: %s" % backup_path)
    print("  Current model: %s" % assistant.model)
    print("  Current instructions: %d chars" % len(assistant.instructions or ""))

    # D.2: Update instructions
    print("\n[D.2] Updating system instructions...")
    print("  New instructions: %d chars" % len(IMPROVED_INSTRUCTIONS))

    # D.3: Upload FAQ supplement
    print("\n[D.3] Creating and uploading FAQ supplement...")
    faq_content = FAQ_SUPPLEMENT_CONTENT.format(
        timestamp=datetime.now().isoformat()
    )
    faq_path = os.path.join(SCRIPT_DIR, "outreach", "MW-PROSPECT-FAQ-SUPPLEMENT.txt")
    os.makedirs(os.path.dirname(faq_path), exist_ok=True)
    with open(faq_path, "w", encoding="utf-8") as f:
        f.write(faq_content)
    print("  FAQ written: %s" % faq_path)

    # Upload to OpenAI
    with open(faq_path, "rb") as f:
        uploaded = client.files.create(file=f, purpose="assistants")
    print("  Uploaded to OpenAI: %s" % uploaded.id)

    # Add to vector store
    vs_ids = []
    if assistant.tool_resources and assistant.tool_resources.file_search:
        vs_ids = list(assistant.tool_resources.file_search.vector_store_ids or [])

    if vs_ids:
        print("  Adding to vector store: %s" % vs_ids[0])
        # Use create + manual poll (create_and_poll has 404 race on some SDK versions)
        vs_file = client.beta.vector_stores.files.create(
            vector_store_id=vs_ids[0],
            file_id=uploaded.id,
        )
        print("  Initial status: %s" % vs_file.status)
        # Manual poll with retries
        import time as _time
        for _attempt in range(30):
            _time.sleep(2)
            try:
                vs_file = client.beta.vector_stores.files.retrieve(
                    vector_store_id=vs_ids[0],
                    file_id=uploaded.id,
                )
                if vs_file.status in ("completed", "failed", "cancelled"):
                    break
            except Exception:
                pass  # Retry on transient 404
        print("  Vector store file status: %s" % vs_file.status)
    else:
        print("  WARNING: No existing vector store found. Creating new one...")
        vs = client.beta.vector_stores.create(
            name="MW Infrastructure Documents",
            file_ids=[uploaded.id],
        )
        vs_ids = [vs.id]
        print("  Created vector store: %s" % vs.id)

    # D.4: Apply all updates
    print("\n[D.4] Applying updates to assistant...")
    update_kwargs = {
        "instructions": IMPROVED_INSTRUCTIONS,
        "model": "gpt-4o",
        "temperature": 0,
        "tools": [{"type": "file_search"}],
    }

    # If we created a new vector store, attach it
    if not (assistant.tool_resources and assistant.tool_resources.file_search and
            assistant.tool_resources.file_search.vector_store_ids):
        update_kwargs["tool_resources"] = {
            "file_search": {"vector_store_ids": vs_ids}
        }

    updated = client.beta.assistants.update(ASSISTANT_ID, **update_kwargs)

    print("\n  Assistant updated successfully:")
    print("  Model: %s" % updated.model)
    print("  Temperature: %s" % updated.temperature)
    print("  Tools: %s" % [t.type for t in updated.tools])
    print("  Instructions: %d chars" % len(updated.instructions or ""))

    print("\n" + "=" * 70)
    print("PHASE D COMPLETE — Assistant patched")
    print("  Backup: assistant_backup_pre_patch.json")
    print("  FAQ: outreach/MW-PROSPECT-FAQ-SUPPLEMENT.txt")
    print("  Next: Run --phase E to re-test failed questions")
    print("=" * 70)


# ═══════════════════════════════════════════════════════════════
# PHASE E: RE-TEST WEAK/FAIL QUESTIONS
# ═══════════════════════════════════════════════════════════════

def run_phase_e():
    # type: () -> List[Dict]
    print("\n" + "=" * 70)
    print("PHASE E: Re-testing WEAK/FAIL questions")
    print("=" * 70)

    graded_path = os.path.join(SCRIPT_DIR, "qa_graded_results.json")
    if not os.path.exists(graded_path):
        print("ERROR: No graded results found. Run --phase B first.")
        sys.exit(1)

    graded = load_json("qa_graded_results.json")
    failures = [r for r in graded["results"] if r["grading"]["grade"] in ("WEAK", "FAIL")]

    if not failures:
        print("No WEAK/FAIL questions to re-test!")
        return []

    print("Re-testing %d questions...\n" % len(failures))
    client = OpenAI()
    retest_results = []

    for i, orig in enumerate(failures):
        idx = i + 1
        print("[%d/%d] %s | %s" % (idx, len(failures), orig["question_id"],
                                     orig["question"][:65]))

        result = {
            "question_id": orig["question_id"],
            "persona": orig["persona"],
            "question": orig["question"],
            "target_docs": orig.get("target_docs", []),
            "original_grade": orig["grading"]["grade"],
            "original_score": orig["grading"]["score"],
            "status": "error",
            "response": "",
            "response_length": 0,
            "file_search_used": False,
            "annotation_count": 0,
            "elapsed_seconds": 0,
            "error": None,
        }

        try:
            thread = client.beta.threads.create()
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=orig["question"],
            )

            start = time.time()
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID,
            )
            elapsed = round(time.time() - start, 1)
            result["elapsed_seconds"] = elapsed

            if run.status != "completed":
                result["status"] = run.status
                result["error"] = "Run did not complete: %s" % run.status
                print("  >> %s (%.1fs)" % (run.status, elapsed))
                retest_results.append(result)
                time.sleep(RATE_LIMIT_SECONDS)
                continue

            messages = client.beta.threads.messages.list(
                thread_id=thread.id, order="desc", limit=5)

            response_text = ""
            file_search_used = False
            ann_count = 0

            for msg in messages.data:
                if msg.role == "assistant":
                    for block in msg.content:
                        if block.type == "text":
                            response_text = block.text.value
                            if hasattr(block.text, "annotations") and block.text.annotations:
                                ann_count = len(block.text.annotations)
                                for ann in block.text.annotations:
                                    if hasattr(ann, "type") and ann.type == "file_citation":
                                        file_search_used = True
                    break

            result["status"] = "completed"
            result["response"] = response_text
            result["response_length"] = len(response_text)
            result["file_search_used"] = file_search_used
            result["annotation_count"] = ann_count

            # Grade the retest
            grading = grade_response(result)
            result["grading"] = grading

            improved = grading["score"] > orig["grading"]["score"]
            direction = "IMPROVED" if improved else ("SAME" if grading["score"] == orig["grading"]["score"] else "WORSE")
            print("  >> %s->%s (score: %d->%d) %s | %d chars | %.1fs" % (
                orig["grading"]["grade"], grading["grade"],
                orig["grading"]["score"], grading["score"],
                direction, len(response_text), elapsed))

        except Exception as e:
            result["error"] = str(e)
            result["grading"] = {"grade": "FAIL", "score": 0, "flags": ["ERROR: %s" % str(e)]}
            print("  >> ERROR: %s" % str(e)[:80])

        retest_results.append(result)
        time.sleep(RATE_LIMIT_SECONDS)

    # Summary
    new_pass = sum(1 for r in retest_results if r.get("grading", {}).get("grade") == "PASS")
    new_weak = sum(1 for r in retest_results if r.get("grading", {}).get("grade") == "WEAK")
    new_fail = sum(1 for r in retest_results if r.get("grading", {}).get("grade") == "FAIL")

    print("\n" + "=" * 70)
    print("PHASE E COMPLETE")
    print("  Re-tested: %d | PASS: %d | WEAK: %d | FAIL: %d" % (
        len(retest_results), new_pass, new_weak, new_fail))
    if retest_results:
        print("  New pass rate (retested): %d%%" % round(
            new_pass * 100.0 / len(retest_results)))
    print("=" * 70)

    retest_data = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "assistant_id": ASSISTANT_ID,
        "retested_count": len(retest_results),
        "summary": {"pass": new_pass, "weak": new_weak, "fail": new_fail},
        "results": retest_results,
    }
    save_json(retest_data, "qa_retest_results.json")

    return retest_results


# ═══════════════════════════════════════════════════════════════
# PHASE F: FINAL REPORT
# ═══════════════════════════════════════════════════════════════

def run_phase_f():
    # type: () -> None
    print("\n" + "=" * 70)
    print("PHASE F: Generating final QA report")
    print("=" * 70)

    # Load artifacts
    graded_path = os.path.join(SCRIPT_DIR, "qa_graded_results.json")
    retest_path = os.path.join(SCRIPT_DIR, "qa_retest_results.json")

    if not os.path.exists(graded_path):
        print("ERROR: No graded results. Run phases A-B first.")
        sys.exit(1)

    graded = load_json("qa_graded_results.json")
    retest = None
    if os.path.exists(retest_path):
        retest = load_json("qa_retest_results.json")

    pre = graded["summary"]
    total = pre["total"]

    # Calculate post-patch overall pass rate
    if retest:
        # Start with original results, replace retested ones
        post_results = {}
        for r in graded["results"]:
            post_results[r["question_id"]] = r["grading"]["grade"]
        for r in retest["results"]:
            post_results[r["question_id"]] = r.get("grading", {}).get("grade", "FAIL")

        post_pass = sum(1 for g in post_results.values() if g == "PASS")
        post_weak = sum(1 for g in post_results.values() if g == "WEAK")
        post_fail = sum(1 for g in post_results.values() if g == "FAIL")
    else:
        post_pass = pre["pass"]
        post_weak = pre["weak"]
        post_fail = pre["fail"]

    # Build report
    report = {
        "generated": datetime.now().isoformat(),
        "assistant_id": ASSISTANT_ID,
        "pre_patch": {
            "total": total,
            "pass": pre["pass"],
            "weak": pre["weak"],
            "fail": pre["fail"],
            "pass_rate_pct": pre["pass_rate_pct"],
        },
        "post_patch": {
            "total": total,
            "pass": post_pass,
            "weak": post_weak,
            "fail": post_fail,
            "pass_rate_pct": round(post_pass * 100.0 / total) if total else 0,
        },
    }

    if retest:
        report["retest_detail"] = []
        for r in retest["results"]:
            report["retest_detail"].append({
                "question_id": r["question_id"],
                "persona": r["persona"],
                "question": r["question"][:80],
                "before": "%s (%d)" % (r.get("original_grade", "?"), r.get("original_score", 0)),
                "after": "%s (%d)" % (
                    r.get("grading", {}).get("grade", "?"),
                    r.get("grading", {}).get("score", 0)),
            })

    save_json(report, "qa_final_report.json")

    # Print report
    print("""
+============================================================+
|    MW KNOWLEDGE ASSISTANT -- QA REFINEMENT REPORT          |
+============================================================+
|                                                            |
|  PHASE A: {total} questions tested across 8 personas         |
|                                                            |
|  PRE-PATCH:                                                |
|    PASS: {pre_pass:>2}  |  WEAK: {pre_weak:>2}  |  FAIL: {pre_fail:>2}  |  Rate: {pre_rate}%   |
|                                                            |
|  POST-PATCH:                                               |
|    PASS: {post_pass:>2}  |  WEAK: {post_weak:>2}  |  FAIL: {post_fail:>2}  |  Rate: {post_rate}%   |
|                                                            |
|  IMPROVEMENT: {pre_rate}% -> {post_rate}%                           |
|  TARGET: 90%+                                              |
+============================================================+
""".format(
        total=total,
        pre_pass=pre["pass"], pre_weak=pre["weak"], pre_fail=pre["fail"],
        pre_rate=pre["pass_rate_pct"],
        post_pass=post_pass, post_weak=post_weak, post_fail=post_fail,
        post_rate=round(post_pass * 100.0 / total) if total else 0,
    ))

    if retest and report.get("retest_detail"):
        print("RE-TEST DETAIL:")
        for d in report["retest_detail"]:
            print("  %s (%s): %s -> %s" % (
                d["question_id"], d["persona"], d["before"], d["after"]))

    # Remaining failures
    remaining = []
    if retest:
        for r in retest["results"]:
            if r.get("grading", {}).get("grade") in ("WEAK", "FAIL"):
                remaining.append(r)

    if remaining:
        print("\nREMAINING ISSUES (%d):" % len(remaining))
        for r in remaining:
            print("  [%s] %s: %s" % (
                r["question_id"],
                r.get("grading", {}).get("grade", "?"),
                r["question"][:70]))
    else:
        print("\nAll re-tested questions now passing!")

    print("\nReport saved: qa_final_report.json")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="MW Knowledge Assistant QA Stress Test")
    parser.add_argument("--phase", required=True,
                        choices=["A", "B", "C", "D", "E", "F"],
                        help="Phase to execute (A-F)")
    parser.add_argument("--confirm", action="store_true",
                        help="Required for Phase D to execute patches")
    args = parser.parse_args()

    phase = args.phase.upper()

    if phase == "A":
        run_phase_a()
    elif phase == "B":
        run_phase_b()
    elif phase == "C":
        run_phase_c()
    elif phase == "D":
        run_phase_d(confirm=args.confirm)
    elif phase == "E":
        run_phase_e()
    elif phase == "F":
        run_phase_f()


if __name__ == "__main__":
    main()
