# Sales Commitment Review — Oracle E-Business Suite

Help an account team explain unshipped sales-order lines and prepare a grounded customer update.

## Business story

**Audience:** Sales process owners and demo presenters. **Problem:** Account teams need a factual basis for discussing shipment commitments. **Demonstrated outcome:** Order-level follow-up with requested versus scheduled dates and no invented promise.

**PAF feature:** Deterministic SQL evidence followed by an Agent. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Which sales commitments need follow-up? Show the requested and scheduled dates from the sample orders.
2. **User:** Draft a customer update for the first order without promising an unconfirmed ship date.

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `SelectSqlQueryNode`
- `parser`
- `textCombiner`
- `agentStep`
- `chatOutputComponent`

Sources: `APPS.XXAF_SCM_SALES_ORDERS_V`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select an available tool-capable LLM on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse Oracle EBS Supply Chain Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

The query excludes explicitly cancelled headers/lines and shows positive ordered-minus-shipped quantity. This is an indicative exception list, not ATP, recognized revenue, or a certified open-order measure. A null shipment value is treated as zero by the explicit query rule. Do not promise a shipping date: distinguish customer request date, scheduled ship date, and an unconfirmed commitment. Preserve header/line/shipment IDs and org scope. The view does not expose UOM; do not aggregate quantities across lines/items. Give three sales follow-up actions and optionally a customer-facing draft without personal details or technical implementation content. Show each of the five supplied lines with ORG_ID, ORDER_NUMBER, LINE_ID, ORDERED_ITEM, REQUEST_DATE and SCHEDULE_SHIP_DATE. Label the list as a five-line sample, not a total open workload. Item details are present; UOM is absent.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Fixed-query check returned 5 rows on the validation date; live counts can change.

## Slide-building notes

1. **Business problem:** Account teams need a factual basis for discussing shipment commitments.
2. **Agent action:** Help an account team explain unshipped sales-order lines and prepare a grounded customer update.
3. **PAF capability:** Deterministic SQL evidence followed by an Agent.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** Order-level follow-up with requested versus scheduled dates and no invented promise. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.
