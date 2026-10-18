# Project Milestone Review — Fusion ERP

**Which project dates and statuses should a project manager verify?**

Review project header dates and statuses before a project-manager follow-up. Produce a bounded evidence brief, limitations and a human follow-up checklist.

## Workflow

Read left to right: **1. Ask a question → 2. Provide API tools → 3. Review and explain → 4. Read the answer.** Sticky notes sit above the node sections. Expand Agent Description for its walkthrough and sample questions. The REST connection supplies a tool; the Agent chooses when to execute it.

## Status

REST probe passed; portable draft prepared; Build model binding pending. See [validation](assets/validation.md) for the exact scope and outstanding checks.

## Setup

Follow the [end-to-end Fusion setup](../../../integrations/fusion-apps/). Import this sample as a draft, upload [its GET-only OpenAPI](assets/openapi.json), replace the example origin and configure authentication. Bind the source listed in [source bindings](assets/source-bindings.json), select `AIW26-PAF-HOL6004-BOO6096`, disable memory and cross-thread sharing, and save.

## Evidence and limits

Resource: `/fscmRestApi/resources/11.13.18.05/projects`

Projection: `ProjectId,ProjectNumber,ProjectName,ProjectStatus,ProjectStartDate,ProjectEndDate`

Project header dates are not detailed milestones or earned-value evidence. Distinguish stored finish dates from forecasts. Do not infer budget variance, completion or delivery promises.

Request `limit=10` and `onlyData=true`, do not expand child resources, and display at most five records. Query limits and projections are instructions; use credential scope or a gateway for hard enforcement. A sample is not the full population. No application changes are made.

## Sample questions

- Which project dates and statuses should a project manager verify?
- What can this sample establish, what evidence is missing, and what should the business owner verify next? Do not change anything.

## Artifacts

- [Native workflow source](workflow.json)
- [Archive metadata](archive-metadata.json)
- [Readable instructions](assets/agent-instructions.md)
- [Oracle resource documentation](https://docs.oracle.com/en/cloud/saas/project-management/26a/fapap/api-projects.html)
