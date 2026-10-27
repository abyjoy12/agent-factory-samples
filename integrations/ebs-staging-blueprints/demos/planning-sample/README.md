# Planning App Reference Adapter

The existing Planning App is the reference implementation and sample business case for the generic Work Order Reschedule Staging and Purchase Order Change Staging agents. Its packages, table names, UI and historical plan scope belong to this adapter. They do not define the reusable agents.

See [adapter mappings](adapter-bindings.json) and the [generic contract](../../README.md). This is implementation guidance based on local source review, not an executable adapter or fresh runtime validation.

## Existing bindings

| Generic function | Existing demo source |
| --- | --- |
| Recommendation evidence | MPDF_GOVERNED_API.GET_RESCHEDULE_CANDIDATES and MPDF_RESCHEDULE_CANDIDATES_V |
| Work order staging | MPDF_RESCHEDULE_STAGE_API.STAGE_RECOMMENDATION('WO', organization_id, transaction_id) |
| Purchase order recommendation staging | MPDF_PO_STAGE_API.REQUEST('STAGE_RECOMMENDATION', payload), delegating to the shared staging API |
| Manual purchase order decision draft | MPDF_PO_STAGE_API.REQUEST('STAGE', payload) |
| Human review | Examine Before Submit using MPDF_PLANNER_GOVERNANCE_API |
| Optional approved handoff selection | MPDF_WO_PO_READY_V |

The staging functions require an authenticated Planning App session. Wrap them in a trusted application adapter rather than accepting a model-supplied actor. Row-level organization/instance authorization must be established independently.

## Data and state translation

ChangeProposal maps to MPDF_WO_PO_CHANGES; ChangeAuditEvent maps to MPDF_WO_PO_CHANGE_EVENTS. The WO payload maps to MPDF_EBS_DISCRETE_JOBS_IFACE and the PO payload to MPDF_EBS_PO_CHANGES. All are local SelectAIAJ staging objects, not EBS-owned interface tables.

VERIFIED maps to canonical RESOLVED and UNVERIFIED to UNRESOLVED. DRAFT/NOT_READY with payload NEW is local draft staging. APPROVED/READY with payload READY is optional human-reviewed eligibility. Preserve original values in adapter_extensions where useful. READY_FOR_IMPORT is a local label, not evidence of EBS execution.

## Demo limitations to carry forward

- The recommendation staging implementation is fixed to Plan 779 and stored historical mappings. Replace those assumptions in another environment; do not generalize demonstration rows into a universal mapping service.
- WO mapping uses MPDF_HJ_EBS_JOB. PO mapping uses MPDF_EBS_PO_TARGET_MAP. Neither establishes current EBS business values without a fresh check.
- Recommendation staging creates a decision, payload and event. Manual PO STAGE creates only the decision and event; report DECISION_ONLY_STAGED until an adapter completes and verifies the payload.
- The initial PO recommendation copies quantity into the decision but does not populate payload NEW_QUANTITY. Keep the first demo date-only unless quantity mirroring is implemented and verified.
- SOURCE_SNAPSHOT_AT is assigned at staging in the reviewed code. Preserve actual planning as-of and mapping age separately.
- Recommendation draft reuse is limited. Stable replay protection, concurrent duplicate prevention and preview consistency tokens require adapter work. Do not claim the existing legacy function supplies those guarantees.
- Initial source LIST behavior needs a destination row cap, and manual selection needs complete-key authorization. App authentication alone is insufficient.
- The current function result contains id/status/reused. Add authorized readback to construct the generic receipt and verify commit, payload and audit persistence.

Legacy signatures do not accept the generic proposal_ref, expected_version and request_key directly. The adapter must resolve the proposal reference to authorized source keys, revalidate the reviewed version, manage the request-key ledger and return the canonical receipt. No schema or package migration is included here.

## Demonstration sequence

Use the generic agent names and instructions. Bind the logical tools through this adapter, select an authorized historical recommendation, explain its age and exact fields, request staging, then inspect local records. End at the draft receipt. Optional Examine Before Submit review belongs to the application; EBS integration remains customer-defined.

## OPAF iteration

Keep the Planning App structure and connect its selected interactions to the OPAF staging workflows. OPAF owns agent orchestration; existing database functions supply deterministic services through the trusted MCP adapter. The local data/staging design does not require a new Select AI agent team. Application identity and conversation correlation must be carried through the bridge and validated by the tool service. See the [runtime profile](../../runtime/opaf/README.md).

## Naming and implementation identity

Planning App identifies the existing planning reference, not the new blueprint showcase. The [implementation reference](implementation-reference.json) records the existing deployment identity and database namespace for adapter maintenance. Renaming this documentation does not rename database objects, change application identifiers or modify a live APEX application.

## New showcase application

The [EBS Agent Blueprint Showcase](../blueprint-showcase/README.md) is a separate planned application with a fresh ID. The existing Planning App and its physical bindings are preserved; this guide documents reference behavior rather than a requirement to reuse or overwrite that application.
