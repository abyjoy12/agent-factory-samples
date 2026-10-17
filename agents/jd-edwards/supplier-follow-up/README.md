# Supplier Follow-up Desk — JD Edwards EnterpriseOne

Prepare a focused supplier follow-up list from open purchase lines without changing purchase orders.

## Business story

**Audience:** Procurement process owners and demo presenters. **Problem:** Buyers spend time locating open lines before supplier calls. **Demonstrated outcome:** A short evidence-backed follow-up queue and a draft inquiry.

**PAF feature:** Oracle PL/SQL executor with an explicit routine allowlist. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Show ten open purchase lines and tell the buyer which supplier commitments to check first. Keep historical dates visible.
2. **User:** Draft a short follow-up for the first supplier, referencing the PO and item. Do not send it.

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `oraclePLSQLExecutor`
- `agentStep`
- `chatOutputComponent`

Sources: `PAF_JDE_PROCURE.GET_OPEN_PURCHASE_LINES`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select an available tool-capable LLM on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse JD Edwards Procurement Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

Use only GET_OPEN_PURCHASE_LINES. Start with P_LIMIT=10; use null P_BRANCH, P_ITEM_CODE, P_SUPPLIER_NUMBER unless the user supplies a filter. Call it before answering. Report order company, order/type/line, supplier, item, branch, open quantity with UOM, promised date, hold and raw status. Rank dated open lines before undated ones, retaining historical dates. Quantities of different items/UOM cannot be summed as a meaningful supply total. Draft a short supplier follow-up referencing the actual returned line; never send it. An open line is evidence to investigate, not proof that a supplier is at fault. The stored routine limits the available operation and returns a ref cursor.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.

## Slide-building notes

1. **Business problem:** Buyers spend time locating open lines before supplier calls.
2. **Agent action:** Prepare a focused supplier follow-up list from open purchase lines without changing purchase orders.
3. **PAF capability:** Oracle PL/SQL executor with an explicit routine allowlist.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** A short evidence-backed follow-up queue and a draft inquiry. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.
