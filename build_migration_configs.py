#!/usr/bin/env python3
"""
PHASE 2: BUILD MIGRATION-READY CONFIGS
Creates drop-in configs for 3 alternative platforms.
"""
import json
import io
import os
from datetime import datetime

OUTPUT_DIR = "assistant_portability"

# Load extracted state
with io.open(os.path.join(OUTPUT_DIR, "assistant_config.json"), encoding="utf-8") as f:
    config = json.load(f)

instructions = config["instructions"]

print("=" * 60)
print("PHASE 2: MIGRATION-READY CONFIGS")
print("=" * 60)

# ─────────────────────────────────────────────
# 2A. Anthropic Claude API config
# ─────────────────────────────────────────────
print("\n[2A] Building Anthropic Claude API config...")

anthropic_config = {
    "_meta": {
        "platform": "Anthropic Claude API",
        "generated": datetime.now().isoformat(),
        "migration_time_estimate": "30 minutes",
        "cost_estimate": "~$0.015/query (Claude Sonnet 4.5) or ~$0.075/query (Claude Opus 4.5)",
        "docs": "https://docs.anthropic.com/en/docs/build-with-claude"
    },
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 4096,
    "temperature": 0,
    "system": instructions,
    "knowledge_loading_strategy": {
        "method": "system_prompt_injection",
        "description": "Load FAQ supplement and key document excerpts directly into system prompt. For full 42-doc retrieval, use Claude's built-in PDF/document processing or a RAG pipeline.",
        "steps": [
            "1. Append FAQ supplement content to system prompt",
            "2. For RAG: Use a vector DB (Pinecone/Weaviate/Chroma) with the 42 docs",
            "3. On each query, retrieve top-5 relevant chunks and inject into user message",
            "4. Claude processes query + retrieved context + system instructions"
        ]
    },
    "api_example": {
        "endpoint": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "headers": {
            "x-api-key": "ANTHROPIC_API_KEY",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        "body": {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 4096,
            "temperature": 0,
            "system": "[SYSTEM_INSTRUCTIONS + FAQ_SUPPLEMENT + RETRIEVED_CONTEXT]",
            "messages": [
                {"role": "user", "content": "{prospect_question}"}
            ]
        }
    },
    "advantages_over_openai": [
        "No assistant/thread/run abstraction -- simpler API",
        "System prompt can hold full FAQ + doc excerpts directly",
        "Claude's reasoning is stronger for institutional/legal questions",
        "No vector store dependency -- use any RAG backend",
        "Anthropic alignment = less hallucination risk on governance content"
    ],
    "migration_script": "migration_configs/anthropic_migrate.py"
}

with io.open(os.path.join(OUTPUT_DIR, "migration_configs", "anthropic_config.json"), "w", encoding="utf-8") as f:
    json.dump(anthropic_config, f, indent=2, ensure_ascii=False)

# Write actual migration script
anthropic_script = '''#!/usr/bin/env python3
"""
MW Knowledge Assistant -- Anthropic Claude Migration Script
Run this to deploy the assistant on Anthropic's API.
Prerequisites: pip install anthropic chromadb
"""

import json
import os
import glob
from anthropic import Anthropic

# Load extracted state
with open("assistant_portability/assistant_config.json") as f:
    config = json.load(f)

# Load FAQ supplement
faq_content = ""
faq_files = glob.glob("assistant_portability/vector_store_files/*.txt") + \\
            glob.glob("assistant_portability/vector_store_files/*.md") + \\
            glob.glob("outreach/MW-PROSPECT-FAQ-SUPPLEMENT.txt")
for faq_path in faq_files:
    if os.path.exists(faq_path) and "FAQ" in faq_path.upper():
        with open(faq_path) as f:
            faq_content += f"\\n\\n--- {os.path.basename(faq_path)} ---\\n" + f.read()

# Build system prompt
system_prompt = config["instructions"] + "\\n\\n## SUPPLEMENTARY FAQ\\n" + faq_content

# Initialize client
client = Anthropic()  # Uses ANTHROPIC_API_KEY env var


def ask_assistant(question: str) -> str:
    """Send a prospect question to the MW Knowledge Assistant (Claude version)."""
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text


# Test
if __name__ == "__main__":
    test_q = "What does the MW Infrastructure Stack cost and what are the pricing tiers?"
    print(f"Q: {test_q}")
    print(f"A: {ask_assistant(test_q)}")
'''

with io.open(os.path.join(OUTPUT_DIR, "migration_configs", "anthropic_migrate.py"), "w", encoding="utf-8") as f:
    f.write(anthropic_script)

print("  -> Anthropic config + migration script saved")

# ─────────────────────────────────────────────
# 2B. Azure OpenAI config
# ─────────────────────────────────────────────
print("\n[2B] Building Azure OpenAI config...")

azure_config = {
    "_meta": {
        "platform": "Azure OpenAI Service",
        "generated": datetime.now().isoformat(),
        "migration_time_estimate": "45 minutes",
        "cost_estimate": "Same as OpenAI but with Azure enterprise billing",
        "docs": "https://learn.microsoft.com/en-us/azure/ai-services/openai/"
    },
    "deployment_name": "mw-knowledge-assistant",
    "model": "gpt-4o",
    "api_version": "2024-05-01-preview",
    "temperature": 0,
    "system_message": instructions,
    "setup_steps": [
        "1. Create Azure OpenAI resource in Azure Portal",
        "2. Deploy gpt-4o model as 'mw-knowledge-assistant'",
        "3. Upload 42 canonical docs + FAQ supplement to Azure AI Search",
        "4. Configure 'On Your Data' with the AI Search index",
        "5. Set system message from SYSTEM_INSTRUCTIONS.md",
        "6. Test with QA pairs from golden_qa_pairs.json"
    ],
    "api_example": {
        "endpoint": "https://{resource}.openai.azure.com/openai/deployments/mw-knowledge-assistant/chat/completions",
        "api_version": "2024-05-01-preview",
        "headers": {
            "api-key": "AZURE_OPENAI_KEY",
            "content-type": "application/json"
        }
    },
    "advantages": [
        "Enterprise SLA and compliance (SOC2, HIPAA, FedRAMP)",
        "Data residency control (choose Azure region)",
        "Private networking (VNET integration)",
        "Better for institutional prospects who require Azure compliance"
    ]
}

with io.open(os.path.join(OUTPUT_DIR, "migration_configs", "azure_config.json"), "w", encoding="utf-8") as f:
    json.dump(azure_config, f, indent=2, ensure_ascii=False)
print("  -> Azure OpenAI config saved")

# ─────────────────────────────────────────────
# 2C. Self-hosted config (Ollama + local RAG)
# ─────────────────────────────────────────────
print("\n[2C] Building self-hosted config...")

selfhosted_config = {
    "_meta": {
        "platform": "Self-Hosted (Ollama + ChromaDB)",
        "generated": datetime.now().isoformat(),
        "migration_time_estimate": "2-3 hours",
        "cost_estimate": "$0 ongoing (hardware cost only)",
        "docs": "https://ollama.ai + https://docs.trychroma.com"
    },
    "model": "llama3.1:70b or mixtral:8x7b",
    "vector_db": "ChromaDB (local, zero cost)",
    "setup_steps": [
        "1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh",
        "2. Pull model: ollama pull llama3.1:70b",
        "3. pip install chromadb langchain-community",
        "4. Index 42 docs + FAQ supplement into ChromaDB collection",
        "5. Build RAG pipeline: query -> ChromaDB retrieval -> Ollama generation",
        "6. Test with golden_qa_pairs.json",
        "7. Deploy behind nginx for HTTPS"
    ],
    "advantages": [
        "Zero ongoing API cost",
        "Complete data sovereignty (nothing leaves your server)",
        "No vendor dependency whatsoever",
        "Ultimate founder-irrelevance: runs on any Linux box forever",
        "Perfect for institutional prospects with data residency requirements"
    ],
    "minimum_hardware": {
        "RAM": "32GB (70B model) or 16GB (8x7B model)",
        "GPU": "Optional but recommended (NVIDIA with 24GB+ VRAM)",
        "Storage": "50GB for model + docs",
        "CPU": "8+ cores recommended"
    }
}

with io.open(os.path.join(OUTPUT_DIR, "migration_configs", "selfhosted_config.json"), "w", encoding="utf-8") as f:
    json.dump(selfhosted_config, f, indent=2, ensure_ascii=False)
print("  -> Self-hosted config saved")

# ─────────────────────────────────────────────
# 2D. Platform comparison matrix
# ─────────────────────────────────────────────
print("\n[2D] Building platform comparison matrix...")

comparison = {
    "generated": datetime.now().isoformat(),
    "current_platform": "OpenAI Assistants API",
    "migration_readiness": "100% -- all configs built, all state extracted",
    "platforms": {
        "openai": {
            "status": "ACTIVE (current)",
            "cost_per_query": "$0.03-0.08",
            "migration_time": "0 (already deployed)",
            "pros": "Easiest setup, built-in vector store, thread management",
            "cons": "Vendor lock-in risk, no data sovereignty, price changes",
            "recommendation": "Keep as primary until FRE-001 complete"
        },
        "anthropic": {
            "status": "READY TO DEPLOY",
            "cost_per_query": "$0.015-0.075",
            "migration_time": "30 minutes",
            "pros": "Better reasoning, lower hallucination, simpler API, cheaper",
            "cons": "No built-in vector store (need external RAG)",
            "recommendation": "Deploy as primary after FRE-001, keep OpenAI as backup"
        },
        "azure": {
            "status": "CONFIG READY",
            "cost_per_query": "$0.03-0.08",
            "migration_time": "45 minutes",
            "pros": "Enterprise SLA, compliance certs, data residency",
            "cons": "Azure account setup overhead, same model as OpenAI",
            "recommendation": "Deploy only if institutional prospect requires Azure compliance"
        },
        "self_hosted": {
            "status": "CONFIG READY",
            "cost_per_query": "$0.00",
            "migration_time": "2-3 hours",
            "pros": "Zero cost, full sovereignty, no vendor dependency",
            "cons": "Hardware required, lower quality than GPT-4o/Claude",
            "recommendation": "Deploy at $50K+ ARR when infrastructure investment justified"
        }
    },
    "switching_trigger_matrix": {
        "openai_price_increase_20pct": "Switch to Anthropic",
        "openai_api_degradation": "Switch to Anthropic",
        "prospect_requires_azure": "Deploy Azure config",
        "prospect_requires_data_sovereignty": "Deploy self-hosted",
        "arr_exceeds_50k": "Deploy self-hosted as primary, keep cloud as backup",
        "openai_discontinues_assistants_api": "Switch to Anthropic (30 min)"
    }
}

with io.open(os.path.join(OUTPUT_DIR, "platform_comparison.json"), "w", encoding="utf-8") as f:
    json.dump(comparison, f, indent=2, ensure_ascii=False)
print("  -> Platform comparison matrix saved")

print("\n" + "=" * 60)
print("PHASE 2 COMPLETE: 3 migration configs built")
print("=" * 60)
