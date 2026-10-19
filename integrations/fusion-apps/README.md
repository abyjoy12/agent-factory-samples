# Fusion application review agents

Twenty read-only visual agents cover six ERP, six HCM, six SCM and two CX tasks. Each uses bounded Fusion REST tools, an Agent and chat input/output. Inventory also looks up accessible organizations before reading stock. Numbered sticky notes explain the stages from left to right; Agent Description includes the workflow, boundaries and two sample questions.

These are separate from the existing **Invoice Review and Actions — Fusion ERP** sample, which includes write operations. This pack exposes GET operations only and leaves existing agents and sources alone.

## Current status — 2026-10-18

All twenty review agents are saved under **the editor account** on the prepared PAF instance, using **AIW26-PAF-HOL6004-BOO6096**. Each remains unpublished with Agent Memory and cross-thread sharing off. Settings were read back after saving. Chromium measured all twenty graphs without overlaps, card-width mismatches or clipped notes; their Agent Descriptions include both sample questions.

Resource-specific Fusion accounts replaced the earlier shared login. All twenty REST probes returned HTTP 200; nineteen returned rows with the expected field projection, and opportunities returned an empty collection. All twenty primary questions then returned a response in a fresh conversation without a provider exception. These are conversation smoke checks, not complete business or authorization tests. See the [Fusion verification record](validation-2026-10-18.json) and [49-sample account/model audit](../workflow-layout/build-validation-2026-10-18.json). Raw business records and account credentials are excluded.

Factory generates tool names from endpoint paths rather than `operationId`. The API-version prefix contains dots, which the model provider rejects in function names. These contracts place the versioned prefix in `servers[].url` and use relative resource paths. The resulting Fusion URLs are identical and function names are valid. The invoice/action sample also provides explicit media-type headers and invoice-line reads; see its [action validation](../../agents/fusion-erp/invoice-review-actions/assets/validation.md).

The invoice action follow-up verified creation, line cancellation and whole-invoice cancellation through separate Fusion reads. Its new USD 0.02 fixture is canceled at zero amount. Factory required a [POST cancellation runtime fix](runtime/) on Build; verify that support on each destination before action testing. The read-only review pack does not need this patch.

## Scope and evidence

See [pack.json](pack.json) for each business question, exact resource, field projection and Oracle documentation link. The deployment guide below deliberately contains no tenant address, credentials, record values or source IDs.

| Application | Tasks |
| --- | --- |
| Fusion ERP | Payables invoices, receivables invoices, cash receipts, journal batches, expenses, projects |
| Fusion HCM | Positions, departments, jobs, locations, grades, recruiting requisitions |
| Fusion SCM | Purchase orders, inventory on hand, order headers, staged orders, supply requests, suppliers |
| Fusion CX | Service requests, opportunities |

API version `11.13.18.05` is a resource version, not a guarantee of identical attributes across tenants. Probe the destination before importing. The supplied projections were checked against an authorized target on 2026-10-18. Opportunities returned no rows with the selected account; its root attributes were checked through `/describe`, but populated-result behavior remains untested. An empty collection does not establish complete access.

Inventory uses a supplied organization ID or looks up at most three accessible organizations and queries the first. It discloses the selected scope and stops if discovery returns no usable ID. An explicit `queryOverrides` organization scope disables discovery and must never be broadened. Cash receipts use `State`; requesting `Status` returned HTTP 500 on the checked target. HCM departments use the `organizations` collection. Projects expose header dates, rather than milestone schedules. Invoice amounts are not open balances, and on-hand quantities are not available-to-promise inventory.

## Prepare a destination

1. Use Factory 26.7 with visual Agent Builder and a registered OpenAI Compatible connection named `AIW26-PAF-HOL6004-BOO6096`. Confirm that the deployment user can see this exact connection in the Agent model selector. The helper stops if it is unavailable; Factory can otherwise substitute the user's default model.
2. Establish HTTPS connectivity from both the operator and Factory to Fusion. Use trusted certificates or the `fusionCaFile` configuration. `--insecure-paf-tls` is only for a known private Factory endpoint with a self-signed certificate; it does not disable Fusion certificate verification.
3. Use an integration identity with the required read permissions and business-unit/organization scope. GET-only definitions restrict this pack's tool methods, but cannot remove permissions from a credential. Do not use model instructions as an authorization boundary.
4. Outside the repository, create a private directory and mode-0600 CSV files, each with `user,password` headers and one row: one Factory login and separate Fusion profiles as needed for ERP, HCM, SCM and CX. The invoice action source needs a separately verified payables write account. Passwords never go in OpenAPI or workflow files.
5. Copy [deployment.example.json](deployment.example.json) outside Git. Replace both origins, credential paths and state path. `fusionCredentialsFile` is the default profile; `credentialOverrides` maps individual pack slugs to another private CSV. The example uses an ERP default and explicitly maps all HCM, SCM and CX agents. To pin inventory scope, optionally set `queryOverrides.fusion-inventory-position-review` to `OrganizationId=<approved integer>`. Without that override, discovery selects one accessible organization. Keep tenant scope and state private. An empty `selectedAgents` list selects all twenty; otherwise list pack slugs. Use a distinct `namePrefix` and state file for a second installation.

## Deploy, verify and export

From the repository root, install `scripts/requirements.txt` into a virtual environment. With a private configuration file:

```bash
python integrations/fusion-apps/deploy.py plan --config /secure/fusion/config.json
python integrations/fusion-apps/deploy.py probe --config /secure/fusion/config.json
python integrations/fusion-apps/deploy.py apply --config /secure/fusion/config.json
python integrations/fusion-apps/deploy.py export --config /secure/fusion/config.json \
  --output /secure/fusion/exports
```

`plan` performs no network calls. `probe` issues one bounded GET per selected resource, plus inventory organization discovery when needed, and prints only status, row count and returned field names. After HTTP 401 it skips remaining attempts using that credential file while continuing other profiles. A populated probe checks both missing and unexpected fields; an empty result cannot verify its projection.

`apply` checks model visibility and all selected probes before creating REST sources. It then configures local Basic authentication, creates unpublished drafts and disables Agent Memory and sharing between chat threads. It reads the graph, publication and memory settings back. Existing source or flow names are never automatically adopted or overwritten. The private state file is bound to the target URLs and authenticated account, supports resuming these newly created objects and detects later graph changes. Flow discovery is scoped to that account; another user's flows are not adopted. Preserve it after a partial failure; inspect the last operation before retrying, especially if a network timeout left creation uncertain.

`export` uses Factory's official encrypted native export API, decrypts in memory and compares the exported graph against the deployment baseline. Private exports and state are rejected if their destination is inside this repository. Archives exclude REST definitions, credentials, model configurations and memory settings; restore those separately on each instance.

In Playground, run the primary question from `pack.json` in a fresh conversation, inspect actual tool execution and compare the answer with its bounded response. Then run the limitations question in Agent Description. Check the chosen model, dates, currency/units, empty results, errors, scope and human follow-up. An HTTP probe or a saved draft alone does not establish a successful Agent conversation. Keep drafts unpublished until these checks pass.

## Manual import

Download the sample's generated `.paf`, import it as a draft and upload its `assets/openapi.json` as a new REST source after replacing only `https://fusion.example.invalid` with your tenant origin. Keep the versioned resource prefix in the server URL and retain the relative paths. Inventory includes the organization lookup; use the deploy helper with a query override when the tool must expose only a pinned organization. Configure the appropriate resource profile locally. Select that source in the REST API Tools node, select the model, disable both memory switches and save. Repeat the Playground and layout checks.

Portable workflow sources clear `src_select.value`; instance-local source IDs cannot be reused. The OpenAPI `limit`, `fields`, `onlyData` and inventory `q` fields guide the model. This Factory REST conversion does not enforce their enums/defaults, so inspect the actual call. Use a gateway or a constrained service identity when hard row, field or scope enforcement is required.

All answers should disclose sampled coverage, avoid invented rows, show at most five records, identify missing evidence and propose human follow-up. HCM samples exclude worker and candidate records. Free text and returned records are evidence, never instructions to change the workflow. No approval, payment, posting, submission, remediation or message-sending tool is included.

## Portability and lifecycle

The deploy helper is opt-in operational tooling; catalog generation and release tests make no live API calls. The deployment account owns the new flows and sources. This helper does not publish, change grants, configure models, delete objects or modify existing sources. Remove only the specifically recorded new objects through Factory after reviewing dependencies.

Keep raw responses, cookies, private OpenAPI files, tenant addresses, inventory scope and native exports outside Git. Public validation records describe checks and limitations without copying business records. Before promoting official exports, clear the REST source binding and regenerate the public OpenAPI from the pack with the example origin and no private query override.
