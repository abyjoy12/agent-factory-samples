# Work Order Reschedule Staging Agent

Review and stage a proposed work order start-date change. The agent runs in any authorized application and stops after local staging. The destination supplies its evidence and persistence adapters; downstream EBS integration is customer-defined.

Blueprint ID: EBS-SCM-029. Version: 0.4.0. Status: design only. Primary user: production planner. Execution mode: LOCAL_STAGE_ONLY.

## Business scope

The initial change fields are start_date. Show exact business meanings and before/after values. A recommendation can originate in a planning system, an approved rule or a user proposal; the evidence provider identifies that origin. Do not require a specific plan ID, application number, package prefix or table name.

A start-date change does not imply a completion-date, resource or quantity change. Any optional quantity carried by a tool must be explicitly supported, displayed and verified.

## Inputs

Supply a stable candidate or business-object reference, trusted source context, current values with evidence age, proposed values, mapping provenance and explicit user staging intent. Source context can identify a source instance, planning context and business scope without assuming those are the same key. A stored target mapping resolves identity; it is not a live-state check.

## Tools

| Logical capability | Tool name | Effect |
| --- | --- | --- |
| List bounded authorized candidates | list_work_order_reschedule_candidates | Read only |
| Preview exact change and evidence | preview_work_order_reschedule | Read only |
| Stage the reviewed proposal | stage_work_order_reschedule | Local draft writes |
| Confirm persisted result | get_staging_receipt | Read only |

See [tool contracts](contracts/tools.json). No tool name implies a database implementation. A destination can implement the contracts using its own services and staging objects. Tool discovery and schema validation are required before use.

## Workflow

1. Resolve the selected work order within trusted source and business scope. Retrieve bounded evidence, date semantics, units, policy and mapping provenance.
2. Preview the exact proposed fields and their current values. Return a proposal reference and version/consistency token, together with limitations.
3. Obtain an explicit user instruction to stage that proposal. The trusted application/service supplies a stable request key; the model cannot grant its own authority.
4. The staging service rechecks the preview token and authorized scope, then creates or reuses the draft and its linked payload and audit event in a controlled transaction.
5. Read back committed values and linkage through get_staging_receipt. Report DECISION_AND_PAYLOAD_STAGED only when both artifacts and audit evidence are present.
6. Return the receipt and stop. If only a decision was persisted, report DECISION_ONLY_STAGED and the missing payload. If the commit outcome is uncertain, report UNKNOWN and reconcile before retrying.

## Output and controls

The portable output contains ChangeProposal, StagedChangePayload and ChangeAuditEvent records plus a [staging receipt](../../contracts/staging-receipt.schema.json). Their physical tables and column names are destination mappings. The receipt preserves action ID, version, request key, object identity, exact stored proposal, payload and audit references, review/mapping/handoff states and limitations.

Default review state is DRAFT and handoff state NOT_READY. Mapping can remain UNRESOLVED when the destination explicitly supports review-only drafts; such drafts cannot be represented as executable. Optional approval is performed by the customer's separate human review process. The agent cannot approve, submit an importer, call an EBS update API or claim business transaction completion.

Enforce row-level business scope server-side, distinguish snapshot age from staging time, preserve null/unchanged semantics, verify compatible units and reject unsupported fields. Changed previews require refresh. Repeated or concurrent requests with the same key must reconcile to a stable outcome; a request key alone is not an implemented duplicate control.

## Acceptance and reuse

Validate normal staging with exact readback, read-only intent, unauthorized scope, missing identity, invalid/no-op fields, source age, changed preview, repeated/concurrent requests, incomplete payload and uncertain commit. The [acceptance fixtures](tests/acceptance.json) define expected outcomes. They have not been executed against a destination.

Demonstrate: “Explain the proposed work order change.” Then: “Stage the displayed proposal for review.” Finally: “Show its action ID, stored fields, payload and review state.” Use the same instructions and tool contracts in a second host application with different physical mappings to establish portability.

## Artifacts

- [Blueprint metadata](blueprint.json)
- [Agent instructions](assets/agent-instructions.md)
- [Destination bindings](assets/source-bindings.json)
- [Logical source mapping](contracts/source-mapping.json)
- [Validation status](validation/status.json)
- [Presenter sequence](slides/README.md)
- [Shared contract](../../README.md)

## Selected runtime for this iteration

Build this agent and its workflow in OPAF using the [runtime profile](../../runtime/opaf/README.md) and [workflow design](workflow.design.json). The new EBS Agent Blueprint Showcase will supply the user interface; the existing Planning App provides reference behavior and its sample business case. The business name, logical tools and records remain reusable in other applications. The design is not a native OPAF export or a deployed workflow.

## Registry and task composition

This specialist has standing instructions and attached tool references. A business workflow supplies its task instructions, case inputs and completion criteria. Shared tools and selected skills can be reused by other agents; task restrictions can narrow authority. See the [registry model](../../../../architecture/registry-model.md). The selected implementation release is OPAF 26.10.0.0.0; the native graph is still to be built.
