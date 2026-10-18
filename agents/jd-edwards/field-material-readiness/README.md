# Field Material Readiness — JD Edwards EnterpriseOne

Compare a fictional dispatch plan with live work-order components before a planner commits a field visit.

## Business story

**Audience:** Field Ops process owners and demo presenters. **Problem:** A planner needs to check material evidence before committing a visit. **Demonstrated outcome:** A fictional dispatch plan paired with real work-order components and indicative stock.

**PAF feature:** Read CSV file, fixed SQL material/inventory join, and Agent. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Use the sample dispatch plan to check material readiness for one work order. Explain which parts need a planner check.
2. **User:** Turn that into a pre-dispatch checklist and keep the fictional visit separate from the JDE evidence.

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `readCsv`
- `SelectSqlQueryNode`
- `textCombiner`
- `agentStep`
- `chatOutputComponent`

Sources: `PAF_JDE_API.WORK_ORDERS`, `PAF_JDE_API.WORK_ORDER_PARTS`, `PAF_JDE_API.BRANCH_INVENTORY`, `PAF_JDE_API.ITEMS`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse JD Edwards Manufacturing Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Upload the supplied paf-demo-dispatch-plan.csv using the corresponding Builder component and select the uploaded filename.
5. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

The supplied CSV is a fictional, unconfirmed dispatch plan. AUTO selects the first live work order having component rows by type/number/suffix; identify the selected order. It is a materials-planning example, not proof of an actual field visit. The fixed SQL joins components to branch inventory and the item primary unit. Show REQUIRED_NOT_ISSUED_QTY_PER_ROW and REQUIREMENT_SOURCE_ROWS, INDICATIVE_AVAILABLE_QUANTITY, UOM and INVENTORY_UOM for each component. Compare quantities only when units match. For a missing inventory row or different units, readiness is unknown. Inventory is indicative, not ATP or a reservation. Never say evidence gaps are absent when inventory or units are missing. The report is limited to twenty component rows; do not infer complete readiness for larger orders. Recommend a planner confirmation of stock allocation, site access and technician availability; never confirm a visit. The query groups identical visible component requirements and exposes REQUIREMENT_SOURCE_ROWS. When this exceeds one, the JDE requirement evidence is ambiguous: do not deduplicate away rows or declare readiness; ask the planner to check the original requirement lines. REQUIRED_NOT_ISSUED_QTY_PER_ROW is per visible requirement row, not a validated total. Repeated JDE rows are not repeated CSV visits.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Fixed-query check returned 2 rows on the validation date; live counts can change.
- Repeated visible JDE requirement rows are surfaced through REQUIREMENT_SOURCE_ROWS; readiness stays unconfirmed until the planner resolves them.

## Slide-building notes

1. **Business problem:** A planner needs to check material evidence before committing a visit.
2. **Agent action:** Compare a fictional dispatch plan with live work-order components before a planner commits a field visit.
3. **PAF capability:** Read CSV file, fixed SQL material/inventory join, and Agent.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** A fictional dispatch plan paired with real work-order components and indicative stock. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.

The AI World lab model is `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible), already configured on `build.oracleagentfactory.com`. Configure the same model name in each final lab instance; the archive excludes model definitions and credentials. Read the numbered workflow notes from left to right, and use the expand control beside Agent Description for the walkthrough and sample questions.
