# Implementation action plan

Start with W01 and W02, then complete the PO vertical slice before widening the implementation. The WO workflow reuses the same controls and shared receipt service. W06 and W08 can progress alongside tool implementation once their dependencies are met. Assign named owners and estimates during kickoff; none are assumed here.

| Work item | Accountable role | Depends on | Reviewable exit |
| --- | --- | --- | --- |
| W01 Confirm implementation baseline | Product owner and runtime engineer | None | One reproducible read-only invocation with its actual response; unresolved API assumptions recorded. |
| W02 Validate data and authorized scope | EBS functional lead and data security owner | W01 | Ordinary and unauthorized fixtures prove row scope; source age and exact target identity are independently checked. |
| W03 Implement seven restricted business tools | Integration engineer | W02 | Typed schemas, least privilege, explicit side effects, idempotency, concurrency control and committed readback pass tests; tools/list advertises business tools without agent access to generic SQL executors. |
| W04 Build PO staging vertical slice | OPAF workflow builder | W03 | Changed preview, replay, missing intent, unauthorized scope, partial and unknown persistence fixtures pass; native export captured only after actual build. |
| W05 Build WO staging vertical slice | OPAF workflow builder | W03, W04 | WO source and target identities, date semantics and proposal consistency validated; no EBS action or approval capability exposed. |
| W06 Implement minimum workbench registry | APEX engineer and business analyst | W01 | Capabilities discoverable before canvas use; tools attach by reference; approved definitions and discovered schemas produce visible drift findings. |
| W07 Create new showcase application | APEX engineer | W04, W05, W06 | User can inspect, preview, request staging and open the receipt through the OPAF bridge; actual app identity and bindings recorded privately. |
| W08 Establish business evaluation baseline | Business evaluator and EBS functional lead | W02 | At least 20 reviewed fixtures per pilot include empty, stale, partial, failed, ambiguous, unauthorized and adversarial conditions; expectations and owners are signed off. |
| W09 Run end to end acceptance | Business evaluator and security owner | W04, W05, W07, W08 | Zero critical scope or control failures; no invented EBS success; every staged success has receipt/readback evidence; agreed performance and business targets measured. |
| W10 Prove export and second environment import | Release engineer | W09 | Complete native exports, checksums, import instructions, exclusions and destination test evidence allow another implementer to reproduce both workflows. |
| W11 Expand planning portfolio | Product owner and business analyst | W09 | Each selected agent has a sponsor, source contract, independent acceptance cases and an achievable artifact; no requirement to implement all 50. |
| W12 Add durable cases and human worklists | Companion backend engineer | W06, W09 | Human response is authorized and version-bound; continuation uses a verified runtime checkpoint or explicit case-driven reinvocation. |
| W13 Pilot bounded autonomous KPI process | Process owner and runtime engineer | W12 | Replay, deduplication, stale evidence, repeated breach, escalation, human wait and post-action KPI observation are tested; unresolved EBS effects remain explicitly unresolved. |

The [structured backlog](work-items.json) contains the corresponding deliverables and empty evidence references. Status starts at NOT_STARTED. A documentation package does not satisfy an implementation gate.

## First implementation boundary

Complete W01 to W10 for the reusable WO and PO demonstration. W11 is portfolio expansion; W12 and W13 are later companion and autonomous-process capabilities. Do not make the full 50-agent portfolio or autonomous operation a prerequisite for the two staging demonstrations.

## Customer integration extension

A customer may later provide concurrent programs, request sets, supported interfaces, ISG or PL/SQL APIs. That work is a separate track requiring current-state revalidation, approval policy, request receipts and independent EBS reconciliation. A draft marked ready is not an EBS transaction.
