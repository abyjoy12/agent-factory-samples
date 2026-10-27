# Acceptance checklist

## Before building

- Assign product, business, data security, integration, runtime and evaluation owners.
- Pin the actual OPAF 26.10 contract and supported invocation/export mechanisms.
- Inspect App 130 and App 181 schemas and UI before deciding reuse or migration.
- Resolve authorized scope, identity, evidence sources, freshness and source to target keys outside the prompt.
- Assign the new showcase App ID only during implementation. Leave the existing Planning App unchanged.

## Tool and staging controls

- Discover seven named business tools and compare their schema fingerprints with reviewed contracts.
- Enforce authorization server side on every read and write; model arguments cannot grant access.
- Preserve complete typed identity, evidence references, as-of age, units, nulls and truncation.
- Explain-only requests perform reads. Staging requires explicit intent and the reviewed proposal version.
- Changed previews require refresh. Stable service-generated keys and concurrency controls prevent duplicate drafts.
- Read back committed proposal, payload and audit references. Distinguish complete, decision-only, unknown and failed outcomes.
- Reconcile uncertain persistence before retry. Do not infer failure from timeout.
- Keep approval and business execution tools outside these two agent allowlists. Memory and cross-thread sharing default off.

## Business and portability evidence

- Run independently reviewed ordinary, empty, stale, partial, failed, ambiguous, unauthorized and adversarial fixtures.
- Test mixed units, duplicate joins, incorrect keys, edited proposals, replay, concurrent staging and failed readback.
- Require zero critical unauthorized operations, approval bypasses or invented transaction success.
- Agree recommendation quality, investigation-time, latency and cost targets before measuring; do not treat historic planning targets as achieved results.
- Record workflow, tool, prompt, model, policy and fixture versions with each run.
- Export native workflow files only from the built runtime; do not rename design JSON to a native package.
- Import and rebind in a second environment, then rerun business and control cases.
- Review derived content and licenses before external distribution. Exclude credentials, private endpoints, customer rows and learned memories.

## Autonomous follow on

- Keep case state durable outside a chat session; test authorized human continuation and review expiry.
- Establish scheduler ownership, case deduplication, retries, work budgets, escalation and stop conditions.
- Resolve a case only with its approved business evidence. Staging completion alone cannot establish KPI recovery or EBS application.
