#!/usr/bin/env python3
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
faq_files = glob.glob("assistant_portability/vector_store_files/*.txt") + \
            glob.glob("assistant_portability/vector_store_files/*.md") + \
            glob.glob("outreach/MW-PROSPECT-FAQ-SUPPLEMENT.txt")
for faq_path in faq_files:
    if os.path.exists(faq_path) and "FAQ" in faq_path.upper():
        with open(faq_path) as f:
            faq_content += f"\n\n--- {os.path.basename(faq_path)} ---\n" + f.read()

# Build system prompt
system_prompt = config["instructions"] + "\n\n## SUPPLEMENTARY FAQ\n" + faq_content

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
