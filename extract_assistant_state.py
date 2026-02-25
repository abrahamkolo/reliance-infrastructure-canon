#!/usr/bin/env python3
"""
PHASE 1: FULL STATE EXTRACTION
Exports everything from OpenAI assistant into local repo.
"""
import json
import os
import io
import time
import re
from datetime import datetime
from openai import OpenAI

client = OpenAI()
ASSISTANT_ID = "asst_xRQJW7WDpbx9luIOpsPqvb94"
OUTPUT_DIR = "assistant_portability"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "vector_store_files"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "migration_configs"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "analytics"), exist_ok=True)

print("=" * 60)
print("PHASE 1: FULL STATE EXTRACTION")
print("=" * 60)

# ─────────────────────────────────────────────
# 1A. Export assistant configuration
# ─────────────────────────────────────────────
print("\n[1A] Extracting assistant configuration...")
asst = client.beta.assistants.retrieve(ASSISTANT_ID)

assistant_config = {
    "id": asst.id,
    "name": asst.name,
    "model": asst.model,
    "instructions": asst.instructions,
    "tools": [{"type": t.type} for t in asst.tools],
    "temperature": getattr(asst, "temperature", 0),
    "top_p": getattr(asst, "top_p", 1),
    "metadata": asst.metadata or {},
    "created_at": asst.created_at,
    "extracted_at": datetime.now().isoformat(),
    "tool_resources": {}
}

# Extract vector store IDs
if asst.tool_resources and asst.tool_resources.file_search:
    vs_ids = list(asst.tool_resources.file_search.vector_store_ids or [])
    assistant_config["tool_resources"]["vector_store_ids"] = vs_ids
else:
    vs_ids = []

with io.open(os.path.join(OUTPUT_DIR, "assistant_config.json"), "w", encoding="utf-8") as f:
    json.dump(assistant_config, f, indent=2, ensure_ascii=False)
print("  -> Config saved (%d char instructions, model: %s)" % (len(asst.instructions), asst.model))

# ─────────────────────────────────────────────
# 1B. Export system instructions as standalone file
# ─────────────────────────────────────────────
print("\n[1B] Extracting system instructions...")
with io.open(os.path.join(OUTPUT_DIR, "SYSTEM_INSTRUCTIONS.md"), "w", encoding="utf-8") as f:
    f.write("# MW Knowledge Assistant - System Instructions\n")
    f.write("# Extracted: %s\n" % datetime.now().isoformat())
    f.write("# Source: OpenAI Assistant %s\n" % ASSISTANT_ID)
    f.write("# Model: %s\n" % asst.model)
    f.write("# Temperature: %s\n\n" % getattr(asst, "temperature", 0))
    f.write(asst.instructions)
print("  -> Instructions saved as markdown")

# ─────────────────────────────────────────────
# 1C. Export vector store contents
# ─────────────────────────────────────────────
print("\n[1C] Extracting vector store contents...")
vs_manifest = []

for vs_id in vs_ids:
    print("  Vector store: %s" % vs_id)
    vs = client.beta.vector_stores.retrieve(vs_id)
    vs_info = {
        "id": vs.id,
        "name": vs.name,
        "status": vs.status,
        "file_count": vs.file_counts.completed if vs.file_counts else 0,
        "created_at": vs.created_at,
        "files": []
    }

    # List all files in vector store
    vs_files = client.beta.vector_stores.files.list(vs_id)
    for vsf in vs_files.data:
        try:
            file_obj = client.files.retrieve(vsf.id)
            file_info = {
                "id": file_obj.id,
                "filename": file_obj.filename,
                "bytes": file_obj.bytes,
                "purpose": file_obj.purpose,
                "created_at": file_obj.created_at,
                "status": vsf.status
            }

            # Download file content
            try:
                content = client.files.content(file_obj.id)
                local_path = os.path.join(OUTPUT_DIR, "vector_store_files", file_obj.filename)
                with open(local_path, "wb") as dl:
                    dl.write(content.read())
                file_info["local_path"] = local_path
                file_info["downloaded"] = True
                print("    -> Downloaded: %s (%d bytes)" % (file_obj.filename, file_obj.bytes))
            except Exception as e:
                file_info["downloaded"] = False
                file_info["download_error"] = str(e)
                print("    -> Download failed for %s: %s" % (file_obj.filename, e))

            vs_info["files"].append(file_info)
        except Exception as e:
            print("    -> Error retrieving file %s: %s" % (vsf.id, e))

    # Handle pagination
    while vs_files.has_more:
        vs_files = client.beta.vector_stores.files.list(vs_id, after=vs_files.data[-1].id)
        for vsf in vs_files.data:
            try:
                file_obj = client.files.retrieve(vsf.id)
                file_info = {
                    "id": file_obj.id,
                    "filename": file_obj.filename,
                    "bytes": file_obj.bytes,
                    "purpose": file_obj.purpose,
                    "created_at": file_obj.created_at,
                    "status": vsf.status
                }
                try:
                    content = client.files.content(file_obj.id)
                    local_path = os.path.join(OUTPUT_DIR, "vector_store_files", file_obj.filename)
                    with open(local_path, "wb") as dl:
                        dl.write(content.read())
                    file_info["local_path"] = local_path
                    file_info["downloaded"] = True
                    print("    -> Downloaded: %s (%d bytes)" % (file_obj.filename, file_obj.bytes))
                except Exception as e:
                    file_info["downloaded"] = False
                    file_info["download_error"] = str(e)
                    print("    -> Download failed for %s: %s" % (file_obj.filename, e))
                vs_info["files"].append(file_info)
            except Exception as e:
                print("    -> Error retrieving file %s: %s" % (vsf.id, e))

    vs_manifest.append(vs_info)

with io.open(os.path.join(OUTPUT_DIR, "vector_store_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(vs_manifest, f, indent=2, ensure_ascii=False)
print("  -> Vector store manifest saved")

# ─────────────────────────────────────────────
# 1D. Export QA test results as training data
# ─────────────────────────────────────────────
print("\n[1D] Extracting QA results as training data...")
training_pairs = []

# Load graded QA results
for qa_file in ["qa_graded_results.json", "qa_retest_results.json"]:
    if os.path.exists(qa_file):
        with io.open(qa_file, "r", encoding="utf-8") as f:
            qa_data = json.load(f)

        # Handle both formats: list of items or dict with "results" key
        items = qa_data if isinstance(qa_data, list) else qa_data.get("results", [])

        for item in items:
            # Get the best available response
            resp = item.get("response", "")
            grading = item.get("grading", {})
            score = grading.get("score", 0) if grading else item.get("score", 0)
            grade = grading.get("grade", "") if grading else item.get("grade", "")

            if resp and score >= 80:
                training_pairs.append({
                    "persona": item.get("persona", "unknown"),
                    "question": item.get("question", ""),
                    "ideal_response": resp,
                    "score": score,
                    "grade": grade,
                    "source": qa_file
                })

with io.open(os.path.join(OUTPUT_DIR, "golden_qa_pairs.json"), "w", encoding="utf-8") as f:
    json.dump(training_pairs, f, indent=2, ensure_ascii=False)
print("  -> %d golden Q&A pairs extracted as training data" % len(training_pairs))

print("\n" + "=" * 60)
print("PHASE 1 COMPLETE: All state extracted to %s/" % OUTPUT_DIR)
print("=" * 60)
