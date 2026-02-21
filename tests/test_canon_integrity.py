"""Canonical stack integrity tests -- run as CI verification."""
import json
import hashlib
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestHashIntegrity:
    """Verify SHA3-512 hashes for all 39 documents."""

    @pytest.fixture
    def hashes(self):
        with open(os.path.join(REPO_ROOT, "verification", "hashes.json")) as f:
            return json.load(f)

    def test_hashes_file_exists(self):
        path = os.path.join(REPO_ROOT, "verification", "hashes.json")
        assert os.path.exists(path), "hashes.json not found"

    def test_39_hashes_present(self, hashes):
        assert len(hashes) == 39, f"Expected 39 hashes, got {len(hashes)}"

    def test_all_hashes_verify(self, hashes):
        errors = []
        for filename, expected_hash in hashes.items():
            found = False
            for root, dirs, files in os.walk(os.path.join(REPO_ROOT, "documents")):
                if filename in files:
                    filepath = os.path.join(root, filename)
                    with open(filepath, "rb") as f:
                        actual = hashlib.sha3_512(f.read()).hexdigest()
                    if actual != expected_hash:
                        errors.append(f"MISMATCH: {filename}")
                    found = True
                    break
            if not found:
                errors.append(f"MISSING: {filename}")
        assert not errors, f"Hash verification errors: {errors}"


class TestMasterIndex:
    """Verify master index structure and completeness."""

    @pytest.fixture
    def index(self):
        with open(os.path.join(REPO_ROOT, "verification", "master-index.json")) as f:
            return json.load(f)

    def test_master_index_exists(self):
        path = os.path.join(REPO_ROOT, "verification", "master-index.json")
        assert os.path.exists(path)

    def test_index_has_documents(self, index):
        assert "documents" in index or len(index) > 0


class TestSignatures:
    """Verify Ed25519 signature file structure."""

    def test_signatures_file_exists(self):
        path = os.path.join(REPO_ROOT, "verification", "signatures.json")
        assert os.path.exists(path), "signatures.json not found"

    def test_signatures_has_39_entries(self):
        with open(os.path.join(REPO_ROOT, "verification", "signatures.json")) as f:
            sigs = json.load(f)
        # Signatures are nested under "documents" key
        if "documents" in sigs:
            assert len(sigs["documents"]) >= 39
        else:
            assert len(sigs) >= 39


class TestPublicKey:
    """Verify Ed25519 public key is present."""

    def test_public_key_exists(self):
        path = os.path.join(REPO_ROOT, "verification", "reliance-signing-key.pub")
        assert os.path.exists(path), "Public signing key not found"

    def test_public_key_not_empty(self):
        path = os.path.join(REPO_ROOT, "verification", "reliance-signing-key.pub")
        assert os.path.getsize(path) > 0, "Public key file is empty"


class TestDocumentStructure:
    """Verify canonical document organization."""

    def test_four_layer_directories(self):
        docs_dir = os.path.join(REPO_ROOT, "documents")
        expected = [
            "01-constitutional-authorities",
            "02-operational-protocols",
            "03-legal-instruments",
            "04-interface-packs",
        ]
        for d in expected:
            assert os.path.isdir(os.path.join(docs_dir, d)), f"Missing directory: {d}"

    def test_39_documents_present(self):
        docs_dir = os.path.join(REPO_ROOT, "documents")
        count = 0
        for root, dirs, files in os.walk(docs_dir):
            for f in files:
                if f.startswith("DOC-") and f.endswith(".txt"):
                    count += 1
        assert count == 39, f"Expected 39 documents, found {count}"

    def test_license_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "LICENSE"))

    def test_readme_exists(self):
        assert os.path.exists(os.path.join(REPO_ROOT, "README.md"))
