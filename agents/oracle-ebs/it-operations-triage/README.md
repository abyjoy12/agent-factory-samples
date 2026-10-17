# EBS IT Operations Triage

Route outage questions and batch-performance questions to focused read-only operations assistants.

## Business story

**Audience:** IT process owners and demo presenters. **Problem:** Service desks need different evidence for outages and batch delays. **Demonstrated outcome:** Intent routing to a focused evidence check and an actionable escalation brief.

**PAF feature:** Condition routing with separate outage and batch Agent paths. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Review the latest concurrent requests and summarize batch operations follow-up.
2. **User:** Users report an outage and cannot log in. What can we verify from the application-node evidence?

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `conditionComponent`
- `oracleDatabaseTools`
- `agentStep`
- `chatOutputComponent`

Sources: `APPS.XXAF_OPS_CONCURRENT_REQUESTS_V`, `APPS.XXAF_OPS_NODES_V`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select an available tool-capable LLM on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse Oracle EBS Operations Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

Use only APPS.XXAF_OPS_CONCURRENT_REQUESTS_V, APPS.XXAF_OPS_PRODUCTS_V and APPS.XXAF_OPS_NODES_V in the configured EBS Operations database. For batch review, select SYSTIMESTAMP OBSERVED_AT,REQUEST_DATE,REQUEST_ID,USER_CONCURRENT_PROGRAM_NAME,PHASE_CODE,STATUS_CODE,HOLD_FLAG,ACTUAL_START_DATE,ACTUAL_COMPLETION_DATE,ROUND((ACTUAL_COMPLETION_DATE-ACTUAL_START_DATE)*1440,2) ELAPSED_MINUTES from APPS.XXAF_OPS_CONCURRENT_REQUESTS_V order by REQUEST_DATE desc fetch first 10 rows only. Show the actual latest sample date. Report raw phase/status; do not infer failure without a documented code mapping. Completed run durations are historical observations, not current incident duration or an SLA violation without an agreed threshold. Never cancel/restart jobs or claim an incident ticket was created.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Both the batch and outage routing branches were exercised; node configuration is not a live login test.

## Slide-building notes

1. **Business problem:** Service desks need different evidence for outages and batch delays.
2. **Agent action:** Route outage questions and batch-performance questions to focused read-only operations assistants.
3. **PAF capability:** Condition routing with separate outage and batch Agent paths.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** Intent routing to a focused evidence check and an actionable escalation brief. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.
