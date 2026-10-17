# PeopleSoft Database Service Pulse

Translate live PDB tablespace capacity, session counts and interval metrics into a business-service monitoring brief.

## Business story

**Audience:** Database Performance process owners and demo presenters. **Problem:** Service owners need database metrics translated into operational questions. **Demonstrated outcome:** A timestamped PDB pulse with clear units, scope, and a DBA follow-up.

**PAF feature:** Read-only monitoring views, SQL query, Parser, and Agent. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Give the service owner a database pulse: current resource pressure, session states and interval metrics. State the scope and time.
2. **User:** Does this snapshot prove PeopleSoft is healthy, and what would a DBA need to diagnose a reported slowdown?

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `SelectSqlQueryNode`
- `parser`
- `textCombiner`
- `agentStep`
- `chatOutputComponent`

Sources: `PAF_DATA.DEMO_DB_RESOURCE_PULSE`, `PAF_DATA.DEMO_DB_SESSION_PULSE`, `PAF_DATA.DEMO_DB_METRIC_PULSE`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select an available tool-capable LLM on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse PeopleSoft Human Capital Management Read Only and rebind the nodes listed in assets/source-bindings.json.
4. A DBA runs assets/monitoring-setup.sql in the chosen HCM demo PDB after reviewing the existing PAF_DATA owner and PAF_AGENT_RO reader. This is the only new database setup required by this collection.
5. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

This is a current HCM PDB snapshot, not a complete application health or historical performance diagnosis. TABLESPACE_BLOCKS rows are used blocks with maximum tablespace-size blocks in UNIT_OR_LIMIT, not process/session limits; account for autoextend when explaining these maxima, and do not claim they equal allocated disk space. Session rows count active/inactive user sessions in this PDB. INTERVAL rows use V$CON_SYSMETRIC and retain their units. Explain observed tablespace utilization, session states and interval activity. Compute used/max*100 only when the denominator is numeric and positive. Never infer a root cause, outage, regression, missing indexes or capacity trend from one snapshot. A quiet snapshot does not prove application availability. The demo exposes no SQL text, bind values, personal session details, AWR or ASH. Recommend a DBA check with timestamp and business symptom; never kill sessions or change parameters.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Fixed-query check returned 14 rows on the validation date; live counts can change.
- DELETE against each monitoring view was denied for the integration reader. Only aggregate PDB metadata is exposed.

## Slide-building notes

1. **Business problem:** Service owners need database metrics translated into operational questions.
2. **Agent action:** Translate live PDB tablespace capacity, session counts and interval metrics into a business-service monitoring brief.
3. **PAF capability:** Read-only monitoring views, SQL query, Parser, and Agent.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** A timestamped PDB pulse with clear units, scope, and a DBA follow-up. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.
