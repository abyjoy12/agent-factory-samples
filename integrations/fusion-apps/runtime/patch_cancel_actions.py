#!/usr/bin/env python3
"""Patch Factory's POST cancellation intent check with guarded backup/rollback.

Run against the installation root, never shared storage. This helper does not
import Factory, load credentials, or issue requests. Restart Factory after apply.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile


TARGET = "app/models/agentBuilder/steps/customSteps/RestAPIsToolsStep.py"
OLD = '''    def _mutation_allowed_for_prompt(self, method):
        method_name = self._normalize_method(method)
        if not self._is_mutating_method(method_name):
            return True

        if not self.current_user_message.strip():
            return False

        intent_terms = self._MUTATION_INTENT_TERMS_BY_METHOD.get(method_name, set())
        return self._prompt_has_terms(intent_terms)
'''
NEW = '''    def _mutation_allowed_for_prompt(self, method, url=None):
        method_name = self._normalize_method(method)
        if not self._is_mutating_method(method_name):
            return True

        if not self.current_user_message.strip():
            return False

        intent_terms = self._MUTATION_INTENT_TERMS_BY_METHOD.get(method_name, set())
        # Fusion exposes cancellation as POST actions, not resource creation.
        # Match the path only: query strings and similarly named resources must
        # not turn an ordinary POST into a cancellation action.
        from urllib.parse import urlsplit
        if method_name == "POST" and re.search(
            r"/action/(?:cancelInvoice|cancelLine)/?$", urlsplit(str(url or "")).path
        ):
            intent_terms = {"cancel", "cancelar", "cancela"}
        return self._prompt_has_terms(intent_terms)
'''
OLD_CALL = "        if self._mutation_allowed_for_prompt(method):"
NEW_CALL = "        if self._mutation_allowed_for_prompt(method, url):"


def transform(data):
    text = data.decode("utf-8")
    if text.count(OLD) != 1 or text.count(OLD_CALL) != 1:
        raise ValueError("Expected the reviewed Factory mutation guard exactly once")
    updated = text.replace(OLD, NEW).replace(OLD_CALL, NEW_CALL)
    compile(updated, TARGET, "exec", dont_inherit=True)
    return updated.encode("utf-8")


def load_guard(data):
    """Isolate the actual guard for regression checks without application imports."""
    tree = ast.parse(data)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "RestAPIToolFactory")
    names = {"__init__", "_normalize_method", "_is_mutating_method",
             "_token_matches_intent_term", "_prompt_has_terms",
             "_mutation_allowed_for_prompt", "_enforce_mutation_intent"}
    cls.body = [n for n in cls.body if isinstance(n, ast.Assign) or
                isinstance(n, ast.FunctionDef) and n.name in names]
    from contextvars import ContextVar
    import re
    context = ContextVar("isolated_mutation_prompt", default=None)
    env = {"re": re, "_CURRENT_REST_MUTATION_PROMPT": context}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), TARGET, "exec"), env)
    return env["RestAPIToolFactory"], context


def verify(data):
    factory, context = load_guard(data)
    for action in ("cancelInvoice", "cancelLine"):
        url = "https://example.invalid/invoices/action/" + action
        guard = factory("I confirm: cancel this test invoice now.")
        assert guard._enforce_mutation_intent("POST", url, {}) is True
        assert not factory("Create an invoice")._mutation_allowed_for_prompt("POST", url)
        assert not factory("Show invoices")._mutation_allowed_for_prompt("POST", url)
        token = context.set("Show invoices")
        try:
            assert not guard._mutation_allowed_for_prompt("POST", url)
        finally:
            context.reset(token)
    guard = factory("Cancel the invoice")
    assert not guard._mutation_allowed_for_prompt("POST", "https://example.invalid/invoices")
    assert not guard._mutation_allowed_for_prompt("POST", "https://example.invalid/invoices?q=/action/cancelInvoice")
    assert factory("Create invoice")._mutation_allowed_for_prompt("POST", "https://example.invalid/invoices")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    info = path.stat()
    fd, temporary = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        shutil.copystat(path, temporary)
        os.chown(temporary, info.st_uid, info.st_gid)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(root, action="patch", check=False):
    root = Path(root).resolve(strict=True)
    path = root / TARGET
    if root == Path("/mount") or Path("/mount") in root.parents:
        raise ValueError("Refusing shared /mount storage")
    if path.resolve(strict=True) != path or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError("Target must be an unlinked regular file")
    backup = root / ".ansible-rest-cancel-actions"
    manifest = backup / "manifest.json"
    original_path = backup / "original.py"
    if any(p.is_symlink() for p in (backup, manifest, original_path)):
        raise ValueError("Unsafe backup location")
    current = path.read_bytes()
    if backup.exists():
        saved = json.loads(manifest.read_text())
        original = original_path.read_bytes()
        patched = transform(original)
        if saved != {"root": str(root), "original_sha256": digest(original), "patched_sha256": digest(patched)}:
            raise ValueError("Backup integrity mismatch")
        if current not in (original, patched):
            raise ValueError("Target changed since patching; refusing to overwrite")
    else:
        original = current
        patched = transform(original)
    verify(patched)
    desired = patched if action == "patch" else original
    changed = current != desired
    if changed and not check:
        if not backup.exists():
            backup.mkdir(mode=0o700)
            original_path.write_bytes(original)
            original_path.chmod(0o600)
            manifest.write_text(json.dumps({"root": str(root), "original_sha256": digest(original), "patched_sha256": digest(patched)}))
            manifest.chmod(0o600)
        if path.read_bytes() != current:
            raise ValueError("Target changed during preparation")
        atomic_write(path, desired)
        if path.read_bytes() != desired:
            raise ValueError("Target readback mismatch")
    return {"changed": changed, "action": action, "check_mode": check,
            "before_sha256": digest(current), "after_sha256": digest(desired),
            "backup_dir": str(backup), "guard_checks_passed": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--action", choices=("patch", "rollback"), default="patch")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(apply(args.root, args.action, args.check)))


if __name__ == "__main__":
    main()
