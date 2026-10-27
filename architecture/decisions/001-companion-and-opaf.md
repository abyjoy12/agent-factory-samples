# Companion and OPAF Architecture Decision

Status: accepted strategy; implementation pending. Decision date: October 26, 2026.

## Accepted decisions

1. Use OPAF 26.10.0.0.0 as the agent/workflow runtime for this iteration.
2. Create a new EBS Agent Blueprint Showcase with a fresh App ID assigned at implementation. Preserve the existing Planning App as the sample business case. Do not reuse its ID or rename it in place.
3. Design a combined App 130/181 Business Agent Workbench for discovery, specification, testing and business acceptance. Reuse suitable patterns after inspecting their actual implementation.
4. Register tools independently and attach tool references to agents. Logical tools and MCP deployment bindings are separate records.
5. Place tasks within workflow steps, with Markdown instructions and structured inputs, outputs, assignments and completion criteria.
6. Treat Markdown skills as reusable guidance; verify OPAF loading or assemble their selected content during build. Skills do not create tools or grant permissions.
7. Expose typed business tools through MCP, with origin EBS/MSC reads where appropriate and SelectAIAJ local staging initially. Preserve private endpoint configuration.
8. End the WO and PO agents at local draft staging. Leave integration back to EBS open to customer/use-case implementation.
9. Use Planning Ontology as the first business-evaluation pattern, with independent expected results and deterministic checks.
10. Support autonomous KPI processes through durable cases, bounded specialist work, human worklists and explicit resolution criteria.
11. Keep the shared worklist/case service in the companion/backend; business apps may link to or embed it.
12. Hand versioned application blueprints and authoritative metadata to coding agents using APEXlang. Business evaluation closes the delivery loop.
13. Maintain the approximately 50-agent EBS supply-chain portfolio as a discovery roadmap; prioritize the two WO/PO staging workflows for the first implementation.
14. Store the design and reviewable definitions in GitHub, alongside native exports when built. Do not represent design JSON as runnable OPAF exports.

## Recommended defaults to validate

Use a small integration adapter around SDK/REST/A2A; author graphs in OPAF initially; version reviewed definitions and exports in Git; retain explicit registry/runtime reconciliation. Apply least privilege, explicit staging intent, version-bound review, request-key replay protection and independent persistence checks.

## Open implementation questions

- Exact 26.10 SDK package, REST response envelope, room handling and supported asynchronous/A2A operations.
- Whether durable checkpoint-based human continuation exists for the intended workflows, or case-driven reinvocation is required.
- APIs for runtime inventory, exports, evaluation/trace retrieval and provisioning.
- Actual App 130/181 schema/UI reuse, authorization and migration approach.
- Business-tool wrapper implementation, grants, trusted user propagation and session isolation.
- Tool-registry artifact format and migration path that preserves the existing catalog/release build.
- Skill loading mechanism, task templates, case storage, scheduler and event delivery.
- Customer-approved KPI formulas, thresholds, recovery windows, evaluation baselines and autonomy limits.

These questions do not reopen the accepted separation of business definitions, runtime orchestration, tools, human work and business outcomes. They constrain implementation claims until tested.
