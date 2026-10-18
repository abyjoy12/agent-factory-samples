# Factory POST cancellation support

Fusion invoice cancellation and line cancellation use POST actions. The checked Factory runtime recognized cancellation vocabulary only for DELETE, so it rejected an explicitly confirmed POST cancellation before contacting Fusion. [patch_cancel_actions.py](patch_cancel_actions.py) adds cancellation vocabulary for the exact `/action/cancelInvoice` and `/action/cancelLine` path endings. Ordinary POST creation checks and the active conversation-turn context are preserved.

The helper checks the expected source, tests the isolated guard, and saves the original file with hashes before replacing it. It refuses source drift or corrupted backups and supports exact rollback. It does not contact Fusion, configure credentials or execute an invoice action. Agent confirmation remains a conversational control; the destination account supplies authorization.

## Apply to a reviewed installation

Back up the installation and use its own Python interpreter. Set `FACTORY_ROOT` to the installation directory containing `app/`; do not target shared `/mount` storage.

```bash
python patch_cancel_actions.py --root "$FACTORY_ROOT" --check
python patch_cancel_actions.py --root "$FACTORY_ROOT"
```

Restart Factory using the host's management procedure, verify HTTPS readiness, and rerun `--check`; `changed` must be false. Retain `.ansible-rest-cancel-actions` securely outside a disposable installation. Do not blindly reapply this patch to another Factory release: an unexpected guard must be reviewed first.

To roll back, run the following and restart Factory again:

```bash
python patch_cancel_actions.py --root "$FACTORY_ROOT" --action rollback
```

For managed instances, the sibling infra checkout contains `ansible/playbooks/patch_rest_cancel_actions.yml` and `ansible/runbooks/patch_rest_cancel_actions.md`. The playbook requires an explicit host limit and exports a protected controller backup before restarting the rootless Podman service. This pass applied it only to Build. Include the fix in a separately authorized final-instance rollout.

## Verification

Run the regression checks from the samples repository root:

```bash
python -m unittest discover -s tests -p test_fusion_cancel_patch.py -v
```

Checks cover apply/check/rollback, idempotence, source drift, corrupt backups, action-path lookalikes, query/fragment spoofing, and active-turn intent. Live Build tests then verified creation, line cancellation and whole-invoice cancellation using one new USD 0.02 fixture, followed by independent Fusion reads. The fixture is canceled at zero amount. See [the verification record](../validation-2026-10-18.json).
