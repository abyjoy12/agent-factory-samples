# Application Blueprint Handoff

The workbench and OPAF produce a versioned handoff that a coding agent such as Codex or Claude can use with APEXlang to implement a business application. The handoff contains reviewable artifacts and authoritative metadata, not only screenshots or narrative requirements.

## Blueprint contents

| Input | Content |
| --- | --- |
| Business specification | Intended outcome, user journeys, roles, process boundaries and acceptance |
| Application design | Navigation, pages, forms, reports, review experiences and workflow entry points |
| Data/API metadata | Actual schemas, views, procedures, API specifications, constraints and grants |
| Reusable capability references | Data contracts, agents, skills, tasks and tool versions |
| OPAF workflow contract | Published workflow references/exports, inputs, outputs, error behavior and conversation model |
| Deployment profile | Private binding references, trusted identity and application/runtime correlation |
| Business evaluation | Approved scenarios, expected outcomes, fixtures and acceptance gates |

The coding agent resolves actual structure from authoritative metadata and API contracts. Prose can explain intent but cannot prove table columns, legal joins, procedure signatures or runtime response schemas. Missing structural inputs must be resolved before generation, rather than filled with invented identifiers.

## Generation and verification

Freeze the application specification and user experience before generating nontrivial APEXlang. Resolve the exact target app and workspace at implementation time. Generate pages and integration components against the selected contracts, validate compiler truth and run required checks. Deployment/import authorization and environment setup are separate implementation steps.

The generated application calls its trusted OPAF adapter; it does not need to reproduce agent orchestration or expose unrestricted database tools. It can use the companion's shared case/worklist services rather than generating independent copies of that state machine in every business app.

Capture blueprint version, application source revision, workflow/runtime bindings and evaluation results. Successful generation or compilation establishes an implementation artifact; business acceptance establishes whether it delivers the intended outcome. Use a new application, EBS Agent Blueprint Showcase, for blueprint-based generation; keep the existing Planning App as the sample business case without overwriting its application identity.

## Ownership and changes

Business analysts own intended behavior and acceptance. Workflow builders own executable OPAF graphs. Data/integration owners own validated contracts and implementations. Coding agents produce reviewable application changes. When a referenced contract changes, assess dependent agents, workflow steps, UI mappings and evaluation cases before releasing the application.
