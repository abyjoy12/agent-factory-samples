from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote

from scripts.generate_docs import build_site
from scripts.publication_guard import address_lines, assert_publishable, check_pages, check_repository
from tests.test_generate_docs import write_sample


class PublicationGuardTests(unittest.TestCase):
    def test_rejects_deployment_addresses_in_common_publication_forms(self) -> None:
        address = "https://chat.company.internal/app"
        samples = [
            f"[Open chat]({address})",
            "diagram[\"CHAT.COMPANY.INTERNAL\"]",
            "The host is chat.company.internal.",
            "owner@company.internal",
            "//chat.company.internal/app",
            "http://10.21.34.56:8080/chat",
            "Origin: 10.21.34.56",
            "http://[fd00::1]:8080/chat",
            "Origin: fd00::1",
            "https://tenant.new-tld/chat",
            "https://github.com.company.internal",
            "https://github.com@chat.company.internal",
            "https://chat&#46;company&#46;internal",
            quote(quote(address, safe=""), safe=""),
            address.replace("/", "\\/"),
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertTrue(address_lines(sample))

    def test_allows_public_references_and_reserved_examples(self) -> None:
        samples = [
            "https://github.com/owner/repository",
            "https://docs.oracle.com/reference",
            "https://kgvarun.github.io/agent-factory-samples/",
            "https://app.example.invalid/path",
            "https://api.example.com/path",
            "http://localhost:8000",
            "http://127.0.0.1:8080",
            "http://192.0.2.1:8080",
            "https://[2001:db8::1]/path",
            "Socket.IO, SYS.UTL_HTTP, APEX 26.1.5 and API 11.13.18.05",
            "Bind 0.0.0.0 or use the configured host.",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual([], address_lines(sample))

    def test_diagnostic_does_not_publish_the_rejected_address(self) -> None:
        with self.assertRaises(ValueError) as caught:
            assert_publishable("Heading\nhttps://chat.company.internal", "README.md")
        self.assertIn("line(s) 2", str(caught.exception))
        self.assertNotIn("company.internal", str(caught.exception))

    def test_scans_all_pages_assets_including_html_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text('<a href="https://chat.company.internal">Chat</a>')
            (root / "agents.json").write_text(json.dumps({"origin": "chat.company.internal"}))
            (root / "asset.js").write_text('const origin="https://chat.company.internal";')
            self.assertEqual(3, len(check_pages(root)))

    def test_generator_rejects_manifest_address_before_changing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = write_sample(root)
            path = folder / "sample.json"
            manifest = json.loads(path.read_text())
            manifest["validation"]["environment"] = "chat.company.internal"
            path.write_text(json.dumps(manifest))
            output = root / "docs"
            output.mkdir()
            (output / "index.html").write_text("Previously approved page")
            with self.assertRaisesRegex(ValueError, "unapproved network address"):
                build_site(root, output)
            self.assertEqual("Previously approved page", (output / "index.html").read_text())

    def test_generator_rejects_private_repository_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_sample(root)
            with self.assertRaisesRegex(ValueError, "unapproved network address"):
                build_site(root, root / "docs", "https://git.company.internal/samples")
            self.assertFalse((root / "docs").exists())

    def test_index_and_revision_are_checked_instead_of_clean_working_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = lambda *args: subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)
            run("init", "-q")
            run("config", "user.email", "test@example.invalid")
            run("config", "user.name", "Publication test")
            readme = root / "README.md"
            readme.write_text("https://chat.company.internal")
            run("add", "README.md")
            readme.write_text("Sanitized working copy")
            self.assertEqual([], check_repository(root))
            self.assertEqual(1, len(check_repository(root, staged=True)))
            run("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Fixture")
            self.assertEqual(1, len(check_repository(root, revision="HEAD")))
            readme.write_text("Safe staged version")
            run("add", "README.md")
            readme.write_text("Unstaged https://chat.company.internal")
            self.assertEqual([], check_repository(root, staged=True))

    def test_pre_push_rejects_bad_intermediate_commit_even_when_tip_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = Path(__file__).resolve().parents[1]
            (root / "scripts").mkdir()
            shutil.copyfile(source / "scripts/publication_guard.py", root / "scripts/publication_guard.py")
            def run(*args):
                return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL).decode().strip()
            run("init", "-q")
            run("config", "user.email", "test@example.invalid")
            run("config", "user.name", "Publication test")
            readme = root / "README.md"
            readme.write_text("Safe baseline")
            run("add", ".")
            run("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Baseline")
            remote = run("rev-parse", "HEAD")
            readme.write_text("https://chat.company.internal")
            run("add", ".")
            run("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Unsafe intermediate")
            readme.write_text("Safe tip")
            run("add", ".")
            run("-c", "core.hooksPath=/dev/null", "commit", "-qm", "Clean tip")
            local = run("rev-parse", "HEAD")
            result = subprocess.run(["sh", str(source / ".githooks/pre-push")], cwd=root,
                input=f"refs/heads/main {local} refs/heads/main {remote}\n", text=True, capture_output=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Publication blocked", result.stderr)


if __name__ == "__main__":
    unittest.main()
