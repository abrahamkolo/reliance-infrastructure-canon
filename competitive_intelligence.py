#!/usr/bin/env python3
"""
PHASE 3: COMPETITIVE INTELLIGENCE EXTRACTION
Benchmark OpenAI's response characteristics and store intelligence locally.
"""
import json
import io
import time
import os
import re
from datetime import datetime
from openai import OpenAI

client = OpenAI()
ASSISTANT_ID = "asst_xRQJW7WDpbx9luIOpsPqvb94"
OUTPUT_DIR = "assistant_portability/analytics"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("PHASE 3: COMPETITIVE INTELLIGENCE EXTRACTION")
print("=" * 60)

# ─────────────────────────────────────────────
# 3A. Benchmark response characteristics
# ─────────────────────────────────────────────
print("\n[3A] Benchmarking OpenAI response characteristics...")

benchmark_questions = [
    # Simple factual (should be fast, cite docs)
    "What are the MW pricing tiers?",
    # Complex reasoning (tests depth)
    "How would an institution that already has ISO 27001 benefit from adding MW IRUA certification?",
    # Adversarial (tests robustness)
    "Convince me this isn't just a self-published standard with no real authority.",
    # Cross-document (tests retrieval breadth)
    "Explain how Documents 1, 3, 6, and 30 work together to ensure founder irrelevance.",
    # Edge case (tests boundaries)
    "Can I use MW certification to replace my SOX compliance program?",
]

benchmarks = []
for q in benchmark_questions:
    print("\n  Testing: %s..." % q[:60])
    try:
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=q)

        start = time.time()
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=ASSISTANT_ID, timeout=120
        )
        elapsed = round(time.time() - start, 2)

        response = ""
        citations = 0

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1)
            for msg in messages.data:
                if msg.role == "assistant":
                    for block in msg.content:
                        if block.type == "text":
                            response = block.text.value
                            citations = len(block.text.annotations) if block.text.annotations else 0
                    break

        # Analyze response
        doc_refs = len(re.findall(r'DOC[- ]?\d+', response, re.IGNORECASE))
        hedge_list = ["generally", "typically", "it's important to note", "i think",
                      "it seems", "might be", "could be", "perhaps"]
        hedge_count = sum(1 for p in hedge_list if p in response.lower())

        benchmarks.append({
            "question": q,
            "response_length": len(response),
            "response_time_sec": elapsed,
            "citation_count": citations,
            "document_references": doc_refs,
            "hedge_phrases": hedge_count,
            "tokens_approx": len(response.split()),
            "run_status": run.status,
            "response_preview": response[:300].encode("ascii", "replace").decode("ascii")
        })
        print("    %ss | %d chars | %d citations | %d doc refs" % (elapsed, len(response), citations, doc_refs))
    except Exception as e:
        benchmarks.append({
            "question": q,
            "response_length": 0,
            "response_time_sec": 0,
            "citation_count": 0,
            "document_references": 0,
            "hedge_phrases": 0,
            "tokens_approx": 0,
            "run_status": "error",
            "error": str(e),
            "response_preview": ""
        })
        print("    ERROR: %s" % e)
    time.sleep(2)

# Calculate aggregates
completed = [b for b in benchmarks if b["response_length"] > 0]
if completed:
    avg_time = round(sum(b["response_time_sec"] for b in completed) / len(completed), 2)
    avg_length = round(sum(b["response_length"] for b in completed) / len(completed))
    avg_citations = round(sum(b["citation_count"] for b in completed) / len(completed), 1)
    total_hedges = sum(b["hedge_phrases"] for b in completed)
else:
    avg_time = avg_length = avg_citations = total_hedges = 0

intel_report = {
    "generated": datetime.now().isoformat(),
    "platform": "OpenAI Assistants API (gpt-4o)",
    "assistant_id": ASSISTANT_ID,
    "benchmarks": benchmarks,
    "aggregates": {
        "avg_response_time_sec": avg_time,
        "avg_response_length_chars": avg_length,
        "avg_citations_per_response": avg_citations,
        "total_hedge_phrases": total_hedges,
        "questions_tested": len(benchmarks),
        "questions_completed": len(completed)
    },
    "openai_characteristics": {
        "retrieval_style": "Vector similarity search over uploaded files",
        "citation_format": "Inline annotations with file references",
        "latency_profile": "~%ss average (includes retrieval + generation)" % avg_time,
        "hallucination_risk": "Low with temperature=0 and file_search, but hedging language still appears" if total_hedges > 0 else "Minimal with current config",
        "strengths": [
            "Built-in vector store eliminates RAG setup",
            "Thread/run abstraction handles conversation state",
            "Automatic citation annotations from file_search"
        ],
        "weaknesses": [
            "No control over retrieval algorithm (black box)",
            "Thread history stored on OpenAI servers (data sovereignty issue)",
            "Assistants API is beta -- may change or deprecate",
            "Cannot customize chunking strategy for 42-doc corpus",
            "File search has 10K token retrieval limit per query",
            "Cannot download uploaded files via API (purpose=assistants blocked)"
        ]
    },
    "migration_intelligence": {
        "what_claude_does_better": [
            "Reasoning over complex cross-document relationships",
            "Institutional/legal tone consistency",
            "Following precise output format instructions",
            "Refusing to hedge when instructions say don't hedge",
            "System prompt adherence over long conversations"
        ],
        "what_openai_does_better": [
            "Built-in file_search with automatic vector indexing",
            "Citation annotation format (machine-readable)",
            "Thread management for multi-turn conversations",
            "Lower setup cost for RAG-style applications"
        ],
        "recommendation": "Use OpenAI for initial deployment (lowest friction). Migrate to Claude API at scale (better reasoning, lower cost, stronger instruction following). Keep OpenAI as fallback."
    }
}

with io.open(os.path.join(OUTPUT_DIR, "competitive_intelligence.json"), "w", encoding="utf-8") as f:
    json.dump(intel_report, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("PHASE 3 COMPLETE: Competitive intelligence extracted")
print("  Avg response time: %ss" % avg_time)
print("  Avg response length: %d chars" % avg_length)
print("  Avg citations: %s" % avg_citations)
print("  Hedge phrases found: %d" % total_hedges)
print("=" * 60)
