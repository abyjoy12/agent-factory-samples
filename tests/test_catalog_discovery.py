"""Offline regression checks for destination-safe native agent provisioning."""

import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("catalog_discovery", ROOT / "integrations/catalog-discovery/provision.py")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class CatalogDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "integrations/catalog-discovery/config.json").read_text())
        self.sample = {"generatedAt": "first-build", "agents": [{"slug": "sample-one", "name": "Sample One",
            "description": "A reference workflow", "page_url": "agents/example/sample-one/",
            "prerequisites": ["Configured source"], "questions": ["How does this work?"]}]}

    def snapshot(self, value):
        with patch.object(catalog.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(value).encode())):
            return catalog.catalog_snapshot(self.config["catalog_url"])

    def test_rebuild_timestamp_does_not_duplicate_or_break_upload_resume(self):
        _, first_hash, first_docs = self.snapshot(self.sample)
        rebuilt = {**self.sample, "generatedAt": "later-build"}
        _, second_hash, second_docs = self.snapshot(rebuilt)
        self.assertEqual(first_hash, second_hash)
        self.assertEqual(first_docs, second_docs)
        changed = copy.deepcopy(self.sample)
        changed["agents"][0]["prerequisites"] = ["Different source"]
        self.assertNotEqual(first_hash, self.snapshot(changed)[1])

    def test_snapshot_keeps_evidence_and_public_catalog_link(self):
        _, _, docs = self.snapshot(self.sample)
        self.assertIn("Configured source", docs["sample-one.txt"])
        self.assertIn(self.config["catalog_url"] + "agents/example/sample-one/", docs["sample-one.txt"])

    def test_snapshot_rejects_duplicate_slugs_and_foreign_pages(self):
        duplicate = {"agents": self.sample["agents"] * 2}
        with self.assertRaises(ValueError):
            self.snapshot(duplicate)
        foreign = copy.deepcopy(self.sample)
        foreign["agents"][0]["page_url"] = "https://other.example.com/agents/example/"
        with self.assertRaises(ValueError):
            self.snapshot(foreign)

    def test_owned_resource_is_never_adopted_from_another_user(self):
        resource = {"id": "one", "name": "Guide", "userId": "other@example.com"}
        with self.assertRaises(RuntimeError):
            catalog.owned_named([resource], "Guide", "participant@example.com")
        owned = {**resource, "isOwner": True}
        self.assertEqual(catalog.owned_named([owned], "Guide", "participant@example.com"), owned)
        with self.assertRaises(RuntimeError):
            catalog.owned_named([owned, {**owned, "id": "two"}], "Guide", "participant@example.com")

    def test_credentials_are_selected_by_exact_account(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "credentials.csv"
            path.write_text("user,password\nother@example.com,first\nparticipant@example.com,second\n")
            self.assertEqual(catalog.load_credentials(path, "PARTICIPANT@example.com"), "second")
            with self.assertRaises(ValueError):
                catalog.load_credentials(path, "missing@example.com")

    def test_private_receipt_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "account" / "receipt.json"
            catalog.save_private(path, {"id": "native-id"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_research_payload_does_not_change_template_or_use_another_model(self):
        template = {"strategy_id": "vector", "strategy_details": {"steps": [{"step_type": "embedding",
            "technique_options": ["not-an-input"], "step_configuration": {"selected_technique": {
                "technique_configuration": {"embedding_connection_name": "old"}}}}]}}
        original = copy.deepcopy(template)
        payload = catalog.research_payload(self.config, "source-id", template, "native-type", "query-technique")
        self.assertEqual(template, original)
        self.assertEqual(payload["selected_sources"], ["source-id"])
        self.assertIn("source-id", payload["help"])
        self.assertEqual(payload["preparation_strategy_details"][0]["global_configuration"][0]["llm_connection_name"], self.config["model"])
        self.assertNotIn("technique_options", json.dumps(payload))
        self.assertEqual(payload["assistant_details"]["assistant_type_uuid"], "native-type")

    def test_failed_preparation_is_not_marked_ready(self):
        with self.assertRaises(RuntimeError), patch.object(catalog.time, "sleep") as sleep:
            catalog.wait_for("Research", lambda: (False, "FAILED", {}), 30)
        sleep.assert_not_called()

    def test_resume_skips_completed_files_and_uses_utf8_byte_sizes(self):
        client = catalog.Client.__new__(catalog.Client)
        client.base = "https://factory.example.com/agentFactory"
        client.account = "participant@example.com"
        session = {"upload_session_id": "upload-one", "files": [
            {"filename": "a.txt", "file_id": "a", "status": "completed"},
            {"filename": "b.txt", "file_id": "b", "status": "pending"}]}
        calls = []

        def call(path, method="GET", payload=None, **kwargs):
            calls.append((path, payload, kwargs))
            return {"data": session}

        client.call = call
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            client.upload({"sourceName": "Snapshot"}, {"a.txt": "done", "b.txt": "caf\u00e9"}, state)
            file_specs = calls[0][1]["files"]
            self.assertEqual(file_specs[1]["size"], len("caf\u00e9".encode()))
            self.assertEqual(len(calls), 2)
            self.assertIn("caf\u00e9".encode(), calls[1][2]["body"])
            calls.clear()
            client.upload({"sourceName": "Snapshot"}, {"a.txt": "done", "b.txt": "caf\u00e9"}, state)
            self.assertEqual(calls[0][0], "/v1/file/uploadSessions/upload-one")

    def test_streamed_creation_must_end_in_success(self):
        client = catalog.Client.__new__(catalog.Client)
        client.base = "https://factory.example.com/agentFactory"
        client.origin = "https://factory.example.com"
        client.diagnostic_dir = None
        class Opener:
            def open(self, *args, **kwargs):
                return io.BytesIO(b'{"progress": "working"}\n{"success": false}\n')
        client.opener = Opener()
        with self.assertRaises(RuntimeError):
            client.call("/v1/createKnowledgeBase", "POST", {})


if __name__ == "__main__":
    unittest.main()
