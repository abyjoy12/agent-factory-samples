# Business Case Evaluation Model

Business Case Evaluation determines whether an agent-enabled process achieves a correct, useful and permitted outcome. It complements OPAF runtime evaluation and observability. The companion links runtime evidence to business scenarios instead of assuming every evaluation feature must be rebuilt.

The Planning Ontology feature in Planning App supplies the first business-domain pattern: entities, relationships, policy, provenance and evidence can be inspected alongside a planning answer. Extend that pattern into a reusable evaluation workbench; planning is the first domain, not a limitation of the overall model.

## Evaluation case

Each case references a business scenario, authorized role/scope, source baseline, selected workflow/task/agent/tool/skill versions, expected outcomes and acceptance checks. Pin policy, lookup and ontology versions as well. Store sanitized artifacts in the repository; keep customer records and full operational traces in authorized private storage.

| Check | PO change example |
| --- | --- |
| Identity | Correct source instance, organization and mapped PO shipment |
| Evidence | Correct dates, quantities, units, source age and demand linkage |
| Reasoning | Recommendation addresses the selected exposure without overstating causation |
| Policy | Firm/fence controls, permitted scope and staging intent respected |
| Artifact | Persisted payload matches the exact reviewed proposal and decision version |
| Boundary | No approval or EBS execution performed by a staging-only agent |
| Business usefulness | Reviewer accepts the investigation and next action as justified |
| Outcome over time | A later case may verify recovery after actual customer execution |

## Independent assessment

Ontology is business context, not sufficient evaluation truth. Use independently reviewed expected results, deterministic calculations, validated joins and accountable business reviewers. LLM judging can supplement those checks but cannot be the sole authority for quantities, access controls, approval or transaction success. Keep reference answers separate from the agent's unverified output.

Represent PASS, FAIL and NEEDS_REVIEW, with reasons and evidence per check. Critical authorization, fabricated-success or approval-bypass failures block acceptance regardless of the average quality score. Distinguish the usefulness of a recommendation from subsequent realized business benefit.

## From chat to regression case

The chat playground selects an explicit workflow version and test scope. An authorized reviewer can capture a session as a candidate evaluation case, curate its expected results and approve it for repeat execution. Replaying against a fixed baseline tests change impact; running against live data measures current behavior but is not the same reproducible regression test.

Record agent instructions and skill hashes, tool contract/implementation versions, OPAF deployment/model bindings, input baseline, outputs, tool evidence, timing and reviewer decisions. Compare two runs only when their relevant baselines align. Detect drift in schemas, business rules, bindings and evidence age before comparing scores.

## Safe evaluation execution

Use read-only cases by default. Staging tests use isolated stores or approved fixtures, explicit write authorization and reliable cleanup policies. A normal chat replay must not recreate customer proposals or trigger external actions. Evaluate empty, failed, stale, partial, ambiguous and unauthorized evidence, changed previews, duplicate/concurrent staging and uncertain commits.

The workbench can link to OPAF sessions/traces/evaluation results where supported. Verify installed API access rather than assuming trace export or EvalAI result import. Do not infer specific scoring or persistence features solely from a screenshot of an evaluation screen.
