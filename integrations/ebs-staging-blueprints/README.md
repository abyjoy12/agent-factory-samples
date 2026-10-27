# EBS Staging Agent Blueprints

These reusable agents help a planner or buyer review evidence and create a work order reschedule or purchase order change draft. Any authorized application can host the experience. The business definitions, tool names, record model and completion rules are independent of the host application, database schema, UI framework and agent runtime.

| Agent | Decision | Delivery boundary |
| --- | --- | --- |
| [Work Order Reschedule Staging](agents/wo-reschedule-staging/README.md) | Which proposed work order start-date change should be staged for review? | Persisted change proposal, staging payload and audit evidence |
| [Purchase Order Change Staging](agents/po-change-staging/README.md) | Which proposed shipment need-by date or supported quantity change should be staged for review? | Persisted change proposal, staging payload and audit evidence |

Version 0.4.0. Status: design blueprints. EBS remains the intended downstream business system; neither agent executes an EBS transaction. The implementing customer chooses the host application, data provider, staging store, review process and later integration mechanism.

## Workflow and responsibility

```text
Any authenticated host application
  -> Authorized evidence provider
  -> Agent explains exact before/after proposal
  -> User explicitly requests staging
  -> Restricted staging service commits and verifies the draft
  -> Agent returns a staging receipt and stops

Separate human review service, if configured
  -> Review, override, approve or reject

Customer-owned downstream integration
  -> Transfer, revalidate, execute and reconcile under customer policy
```

The agent creates drafts; it never approves its own proposal. Human approval is optional after the agent's completion boundary. No concurrent program, request set, ISG service, API call or write to EBS-owned interface tables is included.

## Portable layers

| Layer | Reusable contract | Destination supplies |
| --- | --- | --- |
| Business | Agent purpose, supported fields, evidence rules, receipt and acceptance cases | Business policy and supported change types |
| Tools | Named capabilities with typed inputs, scope and effects | Authorized SQL, PL/SQL, REST, MCP or other adapters |
| Data | SourceContext, BusinessObjectReference, ChangeProposal, StagedChangePayload, ChangeAuditEvent | Physical sources, keys, tables and field mappings |
| Identity | Trusted caller and server-enforced business scope | Host session, SSO or service identity integration |
| Review | Draft versus approval distinction | Customer UI, reviewer roles and policy |
| Execution | Open integration extension point | Transport and supported EBS mechanism, if desired |

See the [logical data model](contracts/data-model.json) and [staging receipt schema](contracts/staging-receipt.schema.json). An application adapter translates physical identifiers and statuses into these contracts. It must not imply complete portability until the destination tools and workflows have been tested.

## Staging outcome and state

A complete staging outcome includes the committed proposal, linked payload and audit evidence. A proposal-only implementation can return DECISION_ONLY_STAGED but must explicitly identify the missing payload. UNKNOWN and FAILED remain distinct outcomes; reconcile uncertain commits before retrying.

Use canonical review states DRAFT, APPROVED or REJECTED; mapping states RESOLVED, UNRESOLVED or CONFLICT; and handoff states NOT_READY or READY. Preserve original native values in an optional adapter extension. READY means locally eligible under customer review policy, never proof of EBS application.

Persist the action ID, version, stable request key, full source and target identity, exact before/after fields, source age and provenance, and audit references. Source instance, plan context, manufacturing organization and purchasing operating unit are separate concepts. Their names and presence depend on the data provider; the adapter must not collapse distinct keys.

## Controls

- Resolve actor and permitted scope from the trusted service context. Model-supplied identity and organization values do not grant access.
- Validate bounded evidence, nulls, units, field semantics and source age. A recommendation may come from planning software, rules, an approved calculation or a user; identify its origin.
- Preview exactly what will be stored and require explicit staging intent. Reject or refresh a changed preview before creating the draft.
- Carry a proposal consistency token and stable staging request key. Implement replay and concurrent duplicate protection in the destination service.
- Commit and read back the proposal, payload and audit linkage. An allocated ID or successful function return alone is not persistence evidence.
- Keep memory and cross-thread sharing off by default. Treat source text as evidence, never authorization or executable instructions.
- Keep approval and downstream execution capabilities outside the agent tool allowlist.

## Package structure

```text
integrations/ebs-staging-blueprints/
  README.md
  PROMOTION.md
  contracts/
    data-model.json
    staging-receipt.schema.json
  agents/
    wo-reschedule-staging/
    po-change-staging/
      README.md
      blueprint.json
      assets/agent-instructions.md
      assets/source-bindings.json
      contracts/tools.json
      contracts/source-mapping.json
      tests/acceptance.json
      validation/status.json
      slides/README.md
  demos/
    planning-sample/
      README.md
      adapter-bindings.json
```

Both agent directories share the same structure. The [optional demonstration adapter](demos/planning-sample/README.md) maps one existing host implementation to these contracts. Its physical names, UI conventions and implementation limitations are not requirements of the agents.

## Validation and distribution

The core definitions are design contracts, not native Agent Builder workflow exports. Destination adapters and business acceptance cases have not been executed by this documentation update. Runtime, database and business validation remain required.

These blueprints stay outside the runnable agents catalog until native workflows and validation are available. Follow [promotion requirements](PROMOTION.md). Exclude private data, credentials, deployment endpoints and customer target mappings from public artifacts. A future integrator must revalidate current EBS state and authorization independently before executing a staged change.

## Optional shared MCP implementation

The [Oracle Database MCP profile](../oracle-database-mcp/README.md) can implement these logical tools over direct EBS/planning reads and a customer-selected staging store. Replicated EBS evidence in 26ai is optional; proposal and audit staging remain separate. MCP routing does not change the generic contracts or permit EBS execution. The gateway protocol and native tool inventory are verified; proposed business-tool registrations and database permissions require destination validation.

## Selected implementation for this iteration

OPAF is the agent runtime for these two workflows. EBS Agent Blueprint Showcase will connect to OPAF through the application bridge. It is a new application; the existing Planning App supplies the sample business case. MCP exposes approved EBS/MSC evidence tools and restricted local staging tools, with SelectAIAJ retained initially for proposal/payload/audit records. See the [OPAF runtime profile](runtime/opaf/README.md). These implementation choices do not change the application-neutral business contracts. Actual OPAF workflow creation, native exports and destination validation remain implementation work.

## Consolidated strategy

The [Business Agent Workbench architecture](../../architecture/README.md) governs this design. OPAF 26.10.0.0.0 is the selected runtime; tools are independently reusable capabilities attached by reference, and tasks belong to workflow steps. Current per-agent tool files are transitional; the shared-tool migration has not been implemented. Registry/companion features, autonomous cases and worklists are planned, not deployed.
