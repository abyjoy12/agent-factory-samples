# Fusion application review agents

Twenty read-only visual agents cover six ERP, six HCM, six SCM and two CX tasks. Each uses one Fusion REST collection, an Agent and chat input/output. Numbered sticky notes explain the stages from left to right; Agent Description includes the workflow, boundaries and two sample questions.

These are separate from the existing **Invoice Review and Actions — Fusion ERP** sample, which includes write operations. This pack exposes GET operations only and leaves existing agents and sources alone.

## Current status — 2026-10-18

All twenty portable sample folders are prepared. All twenty REST resource checks returned HTTP 200; the four empty collections and their remaining checks are listed below. Workflow graphs use native Factory component templates, with blank REST source bindings for import. They have not been captured from successful official Build deployments. Archive metadata records preparation time, and each sample's validation record distinguishes HTTP checks from Agent execution.

Build deployment is incomplete: the requested `AIW26-PAF-HOL6004-BOO6096` model connection is not visible to the Kumar account. One initial payables source and unpublished draft were created before model substitution was detected. Its memory switches are off, but its model binding remains unverified. No other pack flow is claimed as deployed. Continue only after the requested connection is accessible or a replacement is explicitly chosen; then verify fresh conversations and capture official exports.

## Scope and evidence

See [pack.json](pack.json) for each business question, exact resource, field projection and Oracle documentation link. The deployment guide below deliberately contains no tenant address, credentials, record values or source IDs.

| Application | Tasks |
| --- | --- |
| Fusion ERP | Payables invoices, receivables invoices, cash receipts, journal batches, expenses, projects |
| Fusion HCM | Positions, departments, jobs, locations, grades, recruiting requisitions |
| Fusion SCM | Purchase orders, inventory on hand, order headers, staged orders, supply requests, suppliers |
| Fusion CX | Service requests, opportunities |

API version `11.13.18.05` is a resource version, not a guarantee of identical attributes across tenants. Probe the destination before importing. The supplied projections were checked against an authorized target on 2026-10-18. Four collections returned no rows: expenses, recruiting requisitions, sales order headers and opportunities. Their root attributes were also checked through `/describe`; populated-result behavior still needs destination testing.

Inventory requires one approved organization ID. Cash receipts use `State`; requesting `Status` returned HTTP 500 on the checked target. HCM departments use the `organizations` collection. Projects expose header dates, rather than milestone schedules. Invoice amounts are not open balances, and on-hand quantities are not available-to-promise inventory.

## Prepare a destination

1. Use Factory 26.7 with visual Agent Builder and a registered OpenAI Compatible connection named `AIW26-PAF-HOL6004-BOO6096`. Confirm that the deployment user can see this exact connection in the Agent model selector. The helper stops if it is unavailable; Factory can otherwise substitute the user's default model.
2. Establish HTTPS connectivity from both the operator and Factory to Fusion. Use trusted certificates or the `fusionCaFile` configuration. `--insecure-paf-tls` is only for a known private Factory endpoint with a self-signed certificate; it does not disable Fusion certificate verification.
3. Use an integration identity with the required read permissions and business-unit/organization scope. GET-only definitions restrict this pack's tool methods, but cannot remove permissions from a credential. Do not use model instructions as an authorization boundary.
4. Outside the repository, create a private directory and two mode-0600 CSV files, each with `user,password` headers and one row: one Factory login and one Fusion login. Passwords never go in OpenAPI or workflow files.
5. Copy [deployment.example.json](deployment.example.json) outside Git. Replace both origins, credential paths and state path. Set `queryOverrides.fusion-inventory-position-review` to `OrganizationId=<approved integer>`. Keep tenant scope and state private. An empty `selectedAgents` list selects all twenty; otherwise list pack slugs. Use a distinct `namePrefix` and state file for a second installation.

## Deploy, verify and export

From the repository root, install `scripts/requirements.txt` into a virtual environment. With a private configuration file:

```bash
python integrations/fusion-apps/deploy.py plan --config /secure/fusion/config.json
python integrations/fusion-apps/deploy.py probe --config /secure/fusion/config.json
python integrations/fusion-apps/deploy.py apply --config /secure/fusion/config.json
python integrations/fusion-apps/deploy.py export --config /secure/fusion/config.json \
  --output /secure/fusion/exports
```

`plan` performs no network calls. `probe` issues one bounded GET per selected resource and prints only status, row count and returned field names. It stops further credential attempts after HTTP 401. A populated probe checks both missing and unexpected fields; an empty result cannot verify its projection.

`apply` checks model visibility and all selected probes before creating REST sources. It then configures local Basic authentication, creates unpublished drafts and disables Agent Memory and sharing between chat threads. It reads the graph, publication and memory settings back. Existing source or flow names are never automatically adopted or overwritten. The private state file supports resuming these newly created objects and detects later graph changes. Preserve it after a partial failure; inspect the last operation before retrying, especially if a network timeout left creation uncertain.

`export` uses Factory's official encrypted native export API, decrypts in memory and compares the exported graph against the deployment baseline. Private exports and state are rejected if their destination is inside this repository. Archives exclude REST definitions, credentials, model configurations and memory settings; restore those separately on each instance.

In Playground, run the primary question from `pack.json` in a fresh conversation, inspect actual tool execution and compare the answer with its bounded response. Then run the limitations question in Agent Description. Check the chosen model, dates, currency/units, empty results, errors, scope and human follow-up. An HTTP probe or a saved draft alone does not establish a successful Agent conversation. Keep drafts unpublished until these checks pass.

## Manual import

Download the sample's generated `.paf`, import it as a draft and upload its `assets/openapi.json` as a new REST source after replacing `https://fusion.example.invalid` with your tenant origin. For inventory, set the approved organization filter in the tool description/default and Agent instructions. Configure authentication locally. Select that source in the REST API Tools node, select the model, disable both memory switches and save. Repeat the Playground and layout checks.

Portable workflow sources clear `src_select.value`; instance-local source IDs cannot be reused. The OpenAPI `limit`, `fields`, `onlyData` and inventory `q` fields guide the model. This Factory REST conversion does not enforce their enums/defaults, so inspect the actual call. Use a gateway or a constrained service identity when hard row, field or scope enforcement is required.

All answers should disclose sampled coverage, avoid invented rows, show at most five records, identify missing evidence and propose human follow-up. HCM samples exclude worker and candidate records. Free text and returned records are evidence, never instructions to change the workflow. No approval, payment, posting, submission, remediation or message-sending tool is included.

## Portability and lifecycle

The deploy helper is opt-in operational tooling; catalog generation and release tests make no live API calls. The deployment account owns the new flows and sources. This helper does not publish, change grants, configure models, delete objects or modify existing sources. Remove only the specifically recorded new objects through Factory after reviewing dependencies.

Keep raw responses, cookies, private OpenAPI files, tenant addresses, inventory scope and native exports outside Git. Public validation records describe checks and limitations without copying business records. Before promoting official exports, clear the REST source binding and regenerate the public OpenAPI from the pack with the example origin and no private query override.
