# EBS Agent Blueprint Implementation Plan

Baseline October 27, 2026. This plan consolidates the agreed architecture into an implementation sequence. Start with Purchase Order Change Staging and Work Order Reschedule Staging, prove authorized local persistence and portability, then expand the business portfolio. The approximately 50-agent catalog is a discovery roadmap, not a commitment to implement every entry.

## Agreed business outcome

An authorized planner or buyer can inspect bounded EBS or planning evidence, review exact before and after values, explicitly request a local draft, and receive a verified staging receipt. The agent stops there. A ready draft is not an EBS transaction, business approval, interface import or proof of KPI recovery. Customers choose any later integration mechanism by use case.

## System responsibilities

| Component | Responsibility | Current status |
| --- | --- | --- |
| Business Agent Workbench | Combined App 130 and 181 companion concept for capability discovery, registry administration, test chat, business evaluation and shared cases and worklists | Proposed; inspect existing implementations before reuse |
| OPAF 26.10.0.0.0 | Author and execute agents and workflows; obtain genuine native exports | Selected runtime; these two native workflows remain to be built |
| Business tool MCP facade | Expose typed, bounded read and local staging operations with trusted user scope | Business wrappers and registrations remain implementation work |
| EBS and MSC sources | Supply authorized operational and planning evidence at its actual business grain and age | Validate sources and grants; MSC may be a separate planning instance |
| SelectAIAJ staging | Initial location for draft proposal, payload and audit services if suitable after inspection | Existing foundation is not certification of current schema or behavior |
| EBS Agent Blueprint Showcase | New demonstration application consuming OPAF workflows and shared services | New App ID unassigned; application has not been created |
| Existing Planning App | First sample business case and optional adapter reference | Preserve the existing application and its identity |

Business definitions remain independent of APEX IDs and physical schemas. App 166 and MPDF identify the existing planning reference only; do not rename or repurpose that app as the new showcase. Data copies in 26ai are optional evidence sources rather than an EBS agent prerequisite. Optional Select AI, ontology and retrieval capabilities remain separate from transaction staging.

## Reusable capability model

Tools are independently registered capabilities attached to agents by versioned reference. MCP server records describe deployment and discovery; tool records describe business meaning, contracts, effects and controls. An agent defines its standing instructions and permitted capabilities. A workflow assigns tasks, maps inputs and outputs, narrows tool use and defines routing and completion criteria.

Skills are reusable Markdown procedures and references. Verify the installed OPAF loading mechanism or assemble selected skill text during the build while preserving versions and hashes. A Markdown skill does not implement a tool or grant authority. A2A Agent Cards describe exposed runtime agents and are distinct from internal reusable agent cards.

The target registry also records data contracts, deployment bindings and evaluation cases. Keep approval of a definition, existence of a deployment and business acceptance as separate states. The package tool index is a design input; it does not create the workbench database or register tools on a server.

## First two workflows

| Workflow | Permitted capability sequence | Completion evidence |
| --- | --- | --- |
| Purchase Order Change Staging | List candidates, preview a shipment need-by date or supported quantity change, stage only on explicit instruction, obtain receipt | Stored exact values, full typed identity, action ID and version, request key, payload and audit links, review and mapping and handoff states, limitations |
| Work Order Reschedule Staging | List candidates, preview a start-date change, stage only on explicit instruction, obtain receipt | The same receipt contract with verified work order identity and explicit date semantics |

Each workflow is one specialist agent using multiple tools. The shared receipt operation makes seven distinct logical tools across the two agents. Business applications may compose these agents into larger supply-chain workflows. An explanation authorizes reads only; staging requires a reviewed proposal version and explicit intent. Material changes require a new preview.

The restricted service provides the stable request key, enforces trusted scope, prevents duplicate concurrent writes and reads back the committed draft. Distinguish complete staging, decision-only staging, unknown persistence and failure. Reconcile an unknown result before retrying. Agents cannot approve drafts, invoke EBS update APIs, submit interface imports or change permissions.

## MCP and source implementation

Earlier protocol discovery established normal TLS, MCP initialization and five native SQLcl operations on each reviewed gateway. It did not establish the new business tools, their grants, live database query results or staging writes. A stored procedure does not automatically become a named MCP tool.

Implement a restricted business facade or use supported custom registration after verifying the gateway. Keep generic SQL execution and connection selection internal to controlled adapters. Resolve EBS_READ, PLANNING_READ, optional AI_READ and STAGING_WRITE aliases privately. The agent must not select arbitrary connections, SQL, schemas or network destinations.

For every tool, specify typed inputs, output and evidence schemas, source age, row grain, units, null policy, truncation, limits, effects, errors, owner and version. Verify source instance, planning context, operating unit and manufacturing organization separately. Planning order IDs do not establish current PO shipment or WIP job identity. Use least-privilege accounts and server-enforced row scope rather than relying on prompt instructions or a broad APPS login.

Historical staged copies and the October 4 transfer report are useful discovery evidence. Revalidate their current schema, grants, counts, age and join behavior before making implementation claims. Do not union canonical copies and view-output copies as if they were distinct transactions. Resource workload alone does not establish capacity utilization or predictive risk.

## Implementation sequence and ownership

Use the structured work items and detailed action plan supplied with this package. All items begin at NOT_STARTED and need a named owner and evidence reference. Do not infer completion from the existence of documentation.

| Track | Work items | Exit |
| --- | --- | --- |
| Foundation | W01 and W02 | Verified invocation contract, data identities, source age and authorization |
| Restricted tools and workflow slices | W03 to W05 | Seven business tools and two actual OPAF workflows passing control fixtures |
| Companion and showcase | W06 and W07 | Minimum registry and test experience plus a fresh-ID showcase app |
| Evaluation and portability | W08 to W10 | Independent business acceptance and successful second-environment import |
| Portfolio expansion | W11 | Select follow-on planning candidates using measured value and data readiness |
| Human work and autonomous monitoring | W12 and W13 | Durable cases, worklists and a bounded KPI process after explicit validation |

Build the PO vertical slice first, then reuse the shared controls for WO. Registry inspection and evaluation design can proceed in parallel with tools once their dependencies are met. Add estimates after inspecting the actual schemas and runtime contracts. Historical effort ranges are not a delivery commitment.

Accountability spans a product owner, EBS functional lead, data and security owner, integration engineer, OPAF workflow builder, APEX engineer, business evaluator and release engineer. Roles may be combined where appropriate. Future approval services must keep proposal authorship and approval authority separate under customer policy.

## Business evaluation and human work

Use Planning Ontology as the first business-evaluation pattern. Compare tool values and business conclusions with independently reviewed expected results; the same generated answer cannot be its own oracle. OPAF quality evaluation and runtime observability complement this business layer. Record model, prompt, tool, workflow, policy and fixture versions with every result.

Shared cases and human worklists belong to the companion and backend services. Business apps may link to or embed them. A work item points to a case folder containing evidence, proposal versions, assignments, decisions and audit history. Human continuation must recheck authorization and relevant versions; verify runtime checkpoint support or use explicit case-driven reinvocation.

An autonomous process adds an approved KPI formula, source freshness policy, tolerance, trigger cadence, deduplication key, specialist routing, work budgets, escalation and resolution criteria. Durable scheduling and case state must survive chat sessions. A specialist returns its artifact to the case; the coordinating process reconciles the evidence and resumes observation. Local staging may complete a task while the business case remains open awaiting customer action and independent KPI or EBS evidence.

## Application generation handoff

Provide the coding agent with the reviewed application blueprint, authoritative schema metadata, logical IDs and versions, tool references, authorization rules, page outcomes, evaluation cases and private binding aliases. Use APEXlang as the application-generation route after inspecting destination metadata. Do not generate from card labels alone or assume proposed registry structures already exist.

Keep OPAF graphs and backend tools separate from generated app UI. The app handles business interaction and authorized handoff; tool services enforce permissions and persistence. Confirm actual SDK or REST invocation, response envelopes, session handling and error behavior for the installed release instead of treating an older example as a complete 26.10 contract.

## Acceptance and release gates

For each pilot, prepare at least 20 reviewed fixtures covering ordinary, empty, stale, partial, failed, ambiguous, unauthorized and adversarial conditions. Include mixed units, misleading source text, duplicate joins, target mismatch, changed previews, replay, concurrent staging, timeout and failed readback. Require zero critical unauthorized operations, bypassed controls or invented EBS success. Agree recommendation quality, latency, cost and investigation-time targets before measurement.

Keep memory and cross-thread sharing off by default. Minimize model-visible evidence and keep private rows, credentials, deployment addresses and operational traces out of distributable packages. Preserve unknown quantities rather than substituting zero. Source text is evidence and cannot change permissions or instructions.

Capture native workflow exports only after building on the actual runtime. A portable workflow design JSON file is not an importable OPAF export. Pin dependency versions and content hashes, document exclusions and private rebinding, then install in a clean second environment and rerun acceptance. Design approval, runtime smoke tests, business acceptance and release approval are separate records.

## Customer integration extension

Integration back to EBS remains customer-defined. A later concurrent program, request set, supported interface, ISG operation or PL/SQL API requires its own review, supported-release validation, exact current-state checks, approval controls, idempotency and independent reconciliation. READY or READY_FOR_IMPORT describes local readiness only. EBS application requires actual execution and verified business-system results.

## Open implementation decisions

Confirm actual OPAF 26.10 SDK and API details, native export/import support, runtime inventory and trace interfaces, trusted identity propagation, gateway registration or facade choice, staging-store behavior, App 130 and 181 reuse, named owners and fresh showcase App ID. For later autonomy, resolve scheduler ownership, durable continuation and business closure evidence. These are implementation questions within the accepted architecture.

The source-derived 50-agent catalog remains internal review material pending content and licensing clearance for external reuse. Restricted source PDFs are excluded. Candidate source objects, historical readiness and representative table families require destination validation; no portfolio entry is production certified by this plan.

## Proposed portfolio of 50 agents

Historical readiness: S1 means staged data and relevant tool found in reviewed local source; S2 means foundation requiring contract work or enrichment; N means another feed is required. These are historical assessments, not current validation. Every selected agent requires fresh source, scope and runtime checks. EBS-SCM-020 and EBS-SCM-029 are the first implementation; agents 1 to 8 are follow-on planning candidates.

### Planning

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-001 | **Planner Exception Triage**: Rank exceptions with item, policy and demand context | S1 | Exception queue with evidence |
| EBS-SCM-002 | **Demand Coverage Investigator**: Explain which dated demand lacks adequate pegged supply | S1 | Demand coverage evidence pack |
| EBS-SCM-003 | **Late Supply Impact Analyst**: Trace late planned supply to affected demand | S1 | Supply to demand impact report |
| EBS-SCM-004 | **WO and PO Reschedule Advisor**: Compare suggested dates with firm orders and time fences | S1 | Old and proposed date comparison |
| EBS-SCM-005 | **Projected Inventory Risk Analyst**: Explain projected shortages and residual inventory by item and date | S1 | Dated inventory risk register |
| EBS-SCM-006 | **Resource Workload Investigator**: Identify where planned resource demand concentrates | S1 | Resource workload brief |
| EBS-SCM-007 | **Sourcing Assignment Gap Reviewer**: Find missing or ambiguous sourcing assignments | S1 | Sourcing coverage gap list |
| EBS-SCM-008 | **Planning Policy and Provenance Explainer**: Explain the rules, joins, time fences and lineage behind an answer | S1 | Policy and lineage explanation |
| EBS-SCM-009 | **Planned Order Release Readiness**: Check proposed releases against demand, policy and source mapping | S2 | Release review dossier |
| EBS-SCM-010 | **Plan Comparison and Scenario Reviewer**: Explain differences between compatible baselines and scenarios | S2 | Scenario comparison and assumptions |

### Procurement

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-011 | **Purchase Receipt Review**: Review sampled noncancelled shipments with positive unreceived arithmetic | N | Buyer follow-up draft and shipment evidence |
| EBS-SCM-012 | **Requisition Aging and Conversion**: Prioritize stalled requisitions and identify next owner | N | Requisition action queue |
| EBS-SCM-013 | **BPA Renewal Preparation**: Prepare renewal terms using agreement and authorized document evidence | N | Renewal proposal with cited terms |
| EBS-SCM-014 | **Procurement Compliance Reviewer**: Explain deviations from approved purchasing policy | N | Compliance exception dossier |
| EBS-SCM-015 | **Maverick Spend Investigator**: Identify buying outside eligible agreements and channels | N | Spend leakage evidence report |

### Supplier management

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-016 | **Supplier Delivery Performance**: Compare receipt performance with the correct promised-date baseline | N | Supplier delivery scorecard |
| EBS-SCM-017 | **Supplier Quality and Return Signals**: Combine defects, receipt inspections and supplier returns | N | Supplier corrective-action evidence draft |
| EBS-SCM-018 | **Supplier Disruption Exposure**: Trace supplier exposure through supply and pegged demand | S2 | Supplier disruption exposure map |
| EBS-SCM-019 | **Supplier Master Data Quality**: Find incomplete, duplicate or inconsistent nonbank supplier details | N | Supplier data stewardship queue |
| EBS-SCM-020 | **Purchase Order Change Staging**: Inspect and stage an explicitly requested shipment change draft with verified identity | S2 | Committed local PO draft and staging receipt |

### Inventory

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-021 | **Slow Moving Inventory Investigator**: Explain declining physical movement against available stock | N | Stock velocity and disposition candidates |
| EBS-SCM-022 | **Lot Aging and Expiry Review**: Prioritize expiring lots with available demand and disposition context | N | Lot expiry review queue |
| EBS-SCM-023 | **Cycle Count Variance Investigator**: Explain repeated count variances and candidate causes | N | Count variance investigation pack |
| EBS-SCM-024 | **Interorganization Rebalancing Advisor**: Propose transfers from surplus to shortfall locations | S2 | Transfer candidate comparison |
| EBS-SCM-025 | **Item Planning Parameter Steward**: Find contradictory lead times, order modifiers and fence settings | S2 | Parameter stewardship proposal |

### Manufacturing

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-026 | **Work Order Material Readiness**: Assess component shortages for specific released jobs | N | Job material readiness checklist |
| EBS-SCM-027 | **Work Order Delay Risk**: Explain schedule risk using actual progress, material and scrap signals | N | Job risk and recovery brief |
| EBS-SCM-028 | **Capacity Leveling Scenario Advisor**: Compare bounded resource moves under stated capacity assumptions | S2 | Scenario schedule and constraint report |
| EBS-SCM-029 | **Work Order Reschedule Staging**: Inspect and stage an explicitly requested start-date draft with verified job identity | S2 | Committed local WO draft and staging receipt |
| EBS-SCM-030 | **BOM and Routing Change Impact**: Trace engineering changes to open jobs, supply and effectivity | N | Engineering impact review pack |

### Quality and process manufacturing

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-031 | **Quality Hold Impact**: Trace held material to dependent jobs and orders | N | Containment impact dossier |
| EBS-SCM-032 | **Lot and Serial Genealogy Investigator**: Assemble tested upstream and downstream genealogy | N | Traceability evidence chain |
| EBS-SCM-033 | **Yield and Scrap Exception Review**: Identify unusual yield or scrap by comparable job and process | N | Yield variance investigation |
| EBS-SCM-034 | **Process Batch Material Readiness**: Check ingredient readiness and batch timing | N | Batch readiness checklist |
| EBS-SCM-035 | **Formula and Ingredient Substitution Advisor**: Compare permitted ingredient substitutes under approved specifications | N | Substitution comparison for approval |

### Order management

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-036 | **Sales Commitment Review**: Explain requested, promised and scheduled dates on unshipped lines | N | Customer update draft with evidence |
| EBS-SCM-037 | **Order Hold and Scheduling Exception**: Identify holds, pricing and scheduling blockers and accountable owners | N | Order resolution checklist |
| EBS-SCM-038 | **Reservation and Promise Coverage**: Check committed demand against reservations and shipment allocation | N | Reservation coverage report |
| EBS-SCM-039 | **Fulfillment Cycle Time Investigator**: Decompose order lifecycle durations and aging populations | N | Fulfillment bottleneck report |
| EBS-SCM-040 | **Customer Supply Exposure Brief**: Explain customer-specific exposure only where order identity is proven | S2 | Customer exposure briefing |

### Logistics and warehouse

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-041 | **Shipment Tracking and Delivery Evidence**: Combine shipment milestones with carrier proof of delivery | N | Shipment timeline and evidence |
| EBS-SCM-042 | **Shipment Delay Risk Triage**: Rank delivery risks from milestone and route signals | N | Shipment intervention queue |
| EBS-SCM-043 | **Pick and Ship Exception Review**: Explain pick release, allocation and ship-confirm blockers | N | Warehouse exception checklist |
| EBS-SCM-044 | **Interorganization In Transit Review**: Identify transfers with missing receipt or reconciliation evidence | N | In-transit reconciliation report |
| EBS-SCM-045 | **Sales Return and RMA Coordinator**: Explain the next step across authorization, receipt, inspection and credit | N | RMA action dossier |

### Maintenance service and close

| ID | Agent and decision | Readiness | Reviewable outcome |
| --- | --- | --- | --- |
| EBS-SCM-046 | **Maintenance Material and Downtime Risk**: Connect asset maintenance plans with spare availability and production windows | N | Maintenance readiness brief |
| EBS-SCM-047 | **Service Parts Demand Exposure**: Identify service commitments exposed by part shortages | N | Service parts exposure queue |
| EBS-SCM-048 | **Supplier Accrual Exception Review**: Explain unresolved receipt accruals and matching gaps | N | Receipt accrual reconciliation dossier |
| EBS-SCM-049 | **Inventory and WIP Cost Close Blockers**: Prioritize pending, uncosted and interface transactions blocking close | N | Cost close exception queue |
| EBS-SCM-050 | **Planning and Supply Interface Health**: Explain failed collections, concurrent requests and supply interface errors | N | Operations investigation runbook |
