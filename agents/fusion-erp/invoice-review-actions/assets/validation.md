# Validation — 2026-10-18

Create, line cancellation and whole-invoice cancellation independently verified; fixture canceled.

The editor-owned Build draft uses AIW26-PAF-HOL6004-BOO6096. Publication and memory settings were preserved. Both REST nodes now use separately authenticated, editor-owned read/action sources with a verified private payables account.

Read/action contracts now include explicit Content-Type parameters. Creation includes item lines and distribution combinations; exact invoice and child-line reads support reconciliation. Agent Description explains the left-to-right workflow, action proposals, confirmation, verification and two sample questions.

A unique USD 0.02 test invoice with two USD 0.01 item lines was proposed without writing. An independent exact-number GET found no invoice before and after the proposal. After explicit confirmation, separate Fusion reads verified one matching invoice and both item lines.

A line-cancellation proposal made no write. The first confirmation was blocked by Factory before reaching Fusion because its POST intent check did not recognize cancellation. The reviewed runtime patch was applied to Build only, with backup, restart and readiness checks. A renewed explicit confirmation then canceled the selected item line; an independent GET verified its amount was zero and the other item line remained USD 0.01.

Fusion also returned two zero-value tax lines, and the header stayed USD 0.02 while the item-line sum became USD 0.01. The agent disclosed that discrepancy without issuing a corrective write. Line cancellation does not by itself establish an updated header amount.

A whole-invoice cancellation proposal made no write. After explicit confirmation, independent Fusion GETs verified CanceledFlag=true, header amount USD 0.00 and all returned lines at zero with DiscardedFlag=true. The fixture is canceled; no pre-existing invoice was used as a write target.

All three supported action outcomes were established by separate reads. Raw Factory tool traces were not captured, so exact tool-call counts are not independently asserted. Conversational confirmation remains an instruction, while the integration account enforces destination permissions; no grants were changed.

After the changes, Chromium found no node overlaps, card-width mismatches or clipped sticky notes. The official encrypted export matched the live graph; only local REST bindings were cleared in the portable workflow. Final-instance deployment has not started.

See the [runtime patch](../../../../integrations/fusion-apps/runtime/) and the [Fusion verification record](../../../../integrations/fusion-apps/validation-2026-10-18.json). Oracle documents the destination permission requirements in [Payables Security](https://docs.oracle.com/en/cloud/saas/financials/26d/faipp/payables-security.html).
