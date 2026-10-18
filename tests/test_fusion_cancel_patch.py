import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "cancel_patch", Path(__file__).resolve().parents[1] /
    "integrations/fusion-apps/runtime/patch_cancel_actions.py")
patch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patch)

FIXTURE = '''class RestAPIToolFactory:
    _MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    _MUTATION_INTENT_TERMS_BY_METHOD = {
        "POST": {"create", "post"}, "PUT": {"update"},
        "PATCH": {"update"}, "DELETE": {"cancel", "delete"}}
    def __init__(self, current_user_message=None):
        self.current_user_message = str(current_user_message or "")
    def _normalize_method(self, method):
        return str(method or "").strip().upper()
    def _is_mutating_method(self, method):
        return self._normalize_method(method) in self._MUTATING_METHODS
    def _token_matches_intent_term(self, token, term):
        return token == term or len(term) >= 4 and token == f"{term}a"
    def _prompt_has_terms(self, terms):
        prompt = _CURRENT_REST_MUTATION_PROMPT.get()
        if prompt is None:
            prompt = self.current_user_message
        tokens = set(re.findall(r"[a-z0-9_]+", prompt.lower()))
        return any(self._token_matches_intent_term(token, term)
                   for token in tokens for term in terms)
''' + patch.OLD + '''    def _enforce_mutation_intent(self, method, url, request_inputs):
        request_inputs.pop("confirm_mutation", None)
        if not self._is_mutating_method(method):
            return False
''' + patch.OLD_CALL + '''
            return True
        raise ValueError("Mutation blocked")
'''


class CancellationPatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / patch.TARGET
        self.target.parent.mkdir(parents=True)
        self.target.write_text(FIXTURE)

    def test_check_writes_nothing(self):
        result = patch.apply(self.root, check=True)
        self.assertTrue(result["changed"])
        self.assertEqual(self.target.read_text(), FIXTURE)
        self.assertFalse((self.root / ".ansible-rest-cancel-actions").exists())

    def test_apply_idempotent_and_exact_rollback(self):
        self.assertTrue(patch.apply(self.root)["changed"])
        patch.verify(self.target.read_bytes())
        self.assertFalse(patch.apply(self.root)["changed"])
        self.assertTrue(patch.apply(self.root, "rollback")["changed"])
        self.assertEqual(self.target.read_text(), FIXTURE)
        self.assertFalse(patch.apply(self.root, "rollback")["changed"])
        self.assertTrue(patch.apply(self.root)["changed"])

    def test_unexpected_original_is_rejected(self):
        self.target.write_text(FIXTURE.replace(patch.OLD_CALL, "        if True:"))
        with self.assertRaises(ValueError):
            patch.apply(self.root)

    def test_edits_after_patch_are_preserved(self):
        patch.apply(self.root)
        self.target.write_text(self.target.read_text() + "\n# subsequent edit\n")
        with self.assertRaisesRegex(ValueError, "changed since patching"):
            patch.apply(self.root, "rollback")
        self.assertTrue(self.target.read_text().endswith("# subsequent edit\n"))

    def test_corrupt_backup_is_rejected(self):
        patch.apply(self.root)
        (self.root / ".ansible-rest-cancel-actions/original.py").write_text(FIXTURE + "\n# corruption\n")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            patch.apply(self.root, "rollback")

    def test_action_path_and_active_turn_scope(self):
        patch.apply(self.root)
        patch.verify(self.target.read_bytes())
        factory, context = patch.load_guard(self.target.read_bytes())
        guard = factory("cancel invoice")
        for url in ("https://example.invalid/invoices/action/cancelInvoiceExtra",
                    "https://example.invalid/invoices#action/cancelInvoice",
                    "https://example.invalid/action/cancelLine/unrelated"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                guard._enforce_mutation_intent("POST", url, {})
        token = context.set("cancel only line 1 now")
        try:
            self.assertTrue(factory("show invoices")._enforce_mutation_intent(
                "POST", "https://example.invalid/invoices/action/cancelLine", {}))
        finally:
            context.reset(token)
        with self.assertRaises(ValueError):
            factory("show invoices")._enforce_mutation_intent(
                "POST", "https://example.invalid/invoices/action/cancelLine", {"confirm_mutation": True})


if __name__ == "__main__":
    unittest.main()
