# Selective account consolidation — 2026-10-17

Six relevant flows were copied from the authorized source account into the editor account on build PAF. The originals remain intact. Four copies replace existing JDE catalog entries; two add new use cases. The catalog contains **28 distinct samples**, all with purpose-first names and application names at the end.

## What changed

- Reviewed 103 named entries from the 152-flow visible list. Thirty-one readable named flows belonged to the source account. List visibility was not treated as permission to copy another owner's flow.
- Created six editor-owned, unpublished drafts with specific descriptions. Corrected their model binding to the editor's registered `xai.grok-4.3` model.
- Granted the editor **use** access to five required data sources: the two JDE REST sources, two Fusion invoice REST sources and EBS Sensor Control. Existing recipients and group grants were preserved. Source ownership and credentials remain at the source account.
- Kept all four JDE examples because they demonstrate distinct stateless, explicit-memory, implicit-memory and auditable-feedback patterns. Configured their documented memory switches on the new flows. Learned memories, conversations and user history were not copied.
- Reworked the Fusion invoice draft with bounded reads, exact-target confirmation instructions, explicit supported actions and ambiguous-write handling. It can create/cancel invoices and cancel lines using its configured sources. **No Fusion write was executed.** Prompt confirmation is not an independently enforced approval gateway.
- Reduced the EBS diagnostic copy to six allowlisted control-package routines. Removed its generic SQL tool and REST run controller, and rewrote the description and instructions to accurately describe existing-run review. It does not initiate or cancel runs.
- Renamed the 22 existing editor catalog flows and refreshed their descriptions from their manifests. Their graphs were compared before the metadata-only changes; publication and memory settings were retained.
- Captured fresh official exports. The old JDE catalog IDs are recorded in [migration.json](migration.json), alongside the new IDs and selection decisions.

## Selection decisions

| Source flow | Disposition |
| --- | --- |
| litellmtest | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Email Validator Node Test | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| EBS-PLSQL | Excluded: generic PL/SQL draft with empty instructions and empty routine allowlist; the diagnostic flow is the curated replacement. |
| LLM-test | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| DBA Tools EBS | Deferred: bound MCP source 22 is absent from the account selection and its sharing endpoint returns 403; duplicate/general DBA variants need a working scoped connection. |
| EBS DBA User | Deferred: bound MCP source 22 is absent from the account selection and its sharing endpoint returns 403; duplicate/general DBA variants need a working scoped connection. |
| Better Money Habits (KA) | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Financial Wellness Agent | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Oracle DB and Knowldge - Orig Table | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Support KB - D01 | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Simplest A | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Export-1 | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Copied KB | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Demo -22 | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| AJ - EBS Query | Deferred: bound MCP source 22 is absent from the account selection and its sharing endpoint returns 403; duplicate/general DBA variants need a working scoped connection. |
| AJEBS | Deferred: bound MCP source 22 is absent from the account selection and its sharing endpoint returns 403; duplicate/general DBA variants need a working scoped connection. |
| Agent Memory | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| EBS Functional Checks | [Functional Check Evidence Review — Oracle EBS](../../agents/oracle-ebs/functional-check-evidence-review/) |
| Gaelic | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| JDE JPS920 Fulfillment Coach | [Fulfillment Coach (JPS920) — JD Edwards EnterpriseOne](../../agents/jd-edwards/jps920-fulfillment-coach/) |
| Agent to Agent | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| EBS/ASCP Inventory Working-Capital Analyst. | Deferred: detailed SQL-analysis instructions are wired only to four inventory/ATP PL/SQL routines; advertised scope exceeds actual tools. Retain as design input for a scoped SQL reader. |
| OIC MCP Server - Demo | Deferred: patient-care utilization project is outside the requested ERP/HCM/SCM and infrastructure scope. |
| Fusion Apps - Invoice REST API | [Invoice Review and Actions — Fusion ERP](../../agents/fusion-erp/invoice-review-actions/) |
| AIDP-PP-Shared | Excluded: input/agent/output only, empty instructions and no connected tools. Does not implement an AIDP integration. |
| JD Edwards Fulfillment Exception Agent | [Fulfillment Exception Agent — JD Edwards EnterpriseOne](../../agents/jd-edwards/fulfillment-exception/) |
| JD Edwards Fulfillment Memory Agent | [Fulfillment Memory Agent — JD Edwards EnterpriseOne](../../agents/jd-edwards/fulfillment-memory/) |
| JD Edwards Adaptive Fulfillment Advisor | [Adaptive Fulfillment Advisor — JD Edwards EnterpriseOne](../../agents/jd-edwards/adaptive-fulfillment-advisor/) |
| Demo-1 | Excluded: generic multi-node JDE experiment overlaps the four more clearly scoped fulfillment examples. |
| openai-test | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |
| Router Test | Scratch, generic, language/model test, or unrelated demo; no distinct supported use case for this catalog. |

Unowned templates, inaccessible definitions, unnamed scratch entries and irrelevant generic demonstrations were not copied. The missing MCP source used by the old DBA examples was not substituted with an unrelated database connection.

## What was checked

[Current baseline](current-baseline.json) records all 28 editor-owned catalog definitions, publication and memory settings. API read-back confirmed new ownership, names, descriptions, unpublished state and memory switches. Source sharing was read back, and official exports were obtained. These are configuration and migration checks. **The migrated flows were not executed end to end**, and no database or business transaction was changed as part of this consolidation. Earlier validation of a source example is not automatically validation of its new workflow ID.

The shared EBS Sensor Control source passes the permission-checked database-detail API, but the current registered-database selector omits it. The saved node retains its authorized source ID. Avoid clearing this binding in the UI; on another instance create an editor-owned control source and select it normally. This migration did not change application code.

The Fusion draft still uses the source account's existing configured endpoint. The endpoint for the separately supplied Fusion credential file must be confirmed before expanding ERP/HCM/SCM access. No credentials from that file were sent to a guessed environment. The broader Fusion pack remains preparation work and is not counted as deployed agents.

## Replicate on another PAF instance

1. Download the selected `.paf` assets from the repository release and import them as unpublished flows, using the repository archive passphrase.
2. Follow each sample's setup and `assets/source-bindings.json` or OpenAPI file. IDs in workflow JSON identify this installation and must be rebound on the destination.
3. For the four JDE flows, import the supplied AIS OpenAPI contract and configure the destination AIS URL, credentials, environment and role. Select the new REST source in the graph.
4. For Fusion, import the two supplied OpenAPI reconstructions separately, replace the placeholder server URL and configure credentials in PAF. Confirm the contract against the target Fusion release. Use an account whose write permissions match the intended demonstration. Add a server-enforced approval integration before unattended write execution.
5. For EBS evidence review, provide the existing custom `PAF_DEMO.EBS_CHECK_API` backend and populated control catalog. The sample includes its binding contract and six-routine allowlist, **not the custom backend installer**. Keep `auto_commit=false`; do not add the omitted generic SQL or run-controller tools to this read-only sample.
6. Select a destination model. Set the memory switches from each manifest; official exports do not carry those settings. The three memory examples start without learned history.
7. Validate authentication, permissions, evidence and behavior in the destination demo environment before publishing. Keep runtime responses, credentials, cookies and token files outside Git.

An archive moves a workflow definition. It does not copy source credentials, database packages, application data, MCP servers, model registrations or learned memories.

## Reversibility

The originals were not renamed, deleted or unpublished. To undo consolidation, delete only the six destination flow IDs listed in `migration.json` through the editor's Agent Builder. Remove the newly added editor source shares only after confirming that no remaining flow uses them. Do not remove existing recipients or source resources. Restore the prior catalog files from Git if you also want the catalog to point back to the original IDs. The 22 metadata-only name changes can be reversed using the prior Git revision's workflow names/descriptions.

Private pre-change definitions and share snapshots are retained outside this public repository. No source-account passwords, auth configurations, database rows or conversation records are included here.
