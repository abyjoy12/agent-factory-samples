# Journal Close Review — Fusion ERP

**Which sampled journal batches need a period-close check?**

Review journal batch periods and statuses before a period-close check. Produce a bounded evidence brief, limitations and a human follow-up checklist.

## Workflow

Read left to right: **1. Ask a question → 2. Provide API tools → 3. Review and explain → 4. Read the answer.** Sticky notes sit above the node sections. Expand Agent Description for its walkthrough and sample questions. The REST connection supplies a tool; the Agent chooses when to execute it.

## Status

Build draft, model, layout and conversation smoke checks passed. See [validation](assets/validation.md) for the exact scope and outstanding checks.

## Setup

Follow the [end-to-end Fusion setup](../../../integrations/fusion-apps/). Import this sample as a draft, upload [its GET-only OpenAPI](assets/openapi.json), replace the example origin and configure authentication. Bind the source listed in [source bindings](assets/source-bindings.json), select `AIW26-PAF-HOL6004-BOO6096`, disable memory and cross-thread sharing, and save.

## Evidence and limits

Resource: `/fscmRestApi/resources/11.13.18.05/journalBatches`

Projection: `JeBatchId,BatchName,Status,DefaultPeriodName`

Report batch status as returned. A sampled batch is not evidence that a ledger or period is closed. Do not post, reverse, delete or change completion status.

Request `limit=10` and `onlyData=true`, do not expand child resources, and display at most five records. Query limits and projections are instructions; use credential scope or a gateway for hard enforcement. A sample is not the full population. No application changes are made.

## Sample questions

- Which sampled journal batches need a period-close check?
- What can this sample establish, what evidence is missing, and what should the business owner verify next? Do not change anything.

## Artifacts

- [Native workflow source](workflow.json)
- [Archive metadata](archive-metadata.json)
- [Readable instructions](assets/agent-instructions.md)
- [Oracle resource documentation](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/api-journal-batches.html)
