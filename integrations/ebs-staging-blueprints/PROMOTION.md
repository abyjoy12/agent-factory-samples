# Promote a Staging Blueprint to a Runnable Agent Sample

1. For this iteration, use OPAF 26.10.0.0.0 for agents/workflows, create EBS Agent Blueprint Showcase as a new demonstration application with a fresh App ID and SelectAIAJ as the initial staging store. Bind trusted identity and EBS/MSC evidence through MCP. Keep those deployment choices outside the reusable business names and definitions.
2. Map the logical records and tool contracts to destination implementations. Resolve complete source/target keys, scope, status translation, provenance, units and field semantics.
3. Implement preview consistency, idempotent staging, transaction ownership and authorized readback. A decision-only implementation must return DECISION_ONLY_STAGED until a payload exists.
4. Build the real native workflow with the readable agent instructions, memory off and the documented tool allowlist. Keep human approval and downstream execution separate.
5. Exercise all applicable acceptance cases, including source freshness, changed preview, duplicate/concurrent requests, authorization denial, incomplete payload and uncertain commit. Retain sanitized results.
6. Capture the native workflow and compatible archive metadata. Create agents/oracle-ebs/wo-reschedule-staging or agents/oracle-ebs/po-change-staging with workflow.json, archive-metadata.json, a complete sample.json, source bindings, instructions, documentation and demo material under the repository source/release contract.
7. Keep business-facing names application-neutral. Put host-specific mappings and setup in a named adapter guide; do not embed physical schema names or UI routes in the core instructions.
8. Run contribution checks, publication checks and archive round-trip validation. Import and rebind in a second environment before claiming portability.

Design metadata is not a native workflow payload. Do not rename blueprint.json to workflow.json or invent an archive/export receipt. EBS integration remains customer-owned and is not required for staging-agent acceptance.

Follow the [repository strategy](../../architecture/repository-strategy.md) when introducing shared tools, task definitions and skill packages. Preserve existing runnable sample contracts during migration.
