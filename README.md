# Private Agent Factory Agent Samples

This repository is a source-first catalog of documented agents for Oracle AI Database Private Agent Factory. Human-reviewable workflow sources and supporting assets live in Git; password-protected `.paf` archives are generated, verified, and published by GitHub Actions.

## Find an agent

The [agent catalog](https://kgvarun.github.io/agent-factory-samples/) has search and a responsive filter sidebar for **application, business domain, functional use case, application module and technical feature**. Each card starts with a specific business question, followed by its description. Combine filters, copy a link to the current view, and explore the same business task across applications. Agent guides include section navigation and links back to matching samples.

For example, **Capacity planning** brings together workforce, learning and campus scenarios; **Supplier follow-up** spans JDE, EBS and PeopleSoft. Technical filters describe features implemented in the saved graphs. See the [catalog authoring guide](scripts/catalog_assets/README.md) for metadata, vocabulary and presentation changes.

## Selective account consolidation — 2026-10-17

The catalog now has **28 samples** with purpose-first names. Six relevant source-account flows were consolidated as editor-owned drafts: four existing JDE fulfillment/memory samples, [Invoice Review and Actions — Fusion ERP](agents/fusion-erp/invoice-review-actions/), and [Functional Check Evidence Review — Oracle EBS](agents/oracle-ebs/functional-check-evidence-review/). The originals are retained. The existing 22 editor flows were renamed consistently.

See the [selection decisions, migration status and replication guide](integrations/account-consolidation/). Source access, ownership and settings were checked; these new copies were not run end to end. The Fusion draft has write tools and requires target-environment validation before use. The EBS copy reviews existing evidence only.

## Shared-session baseline

[Repository and live PAF reconciliation](integrations/session-consolidation/) records the 26 retained samples, 22 matching accessible live flows, four access-limited comparisons, and outstanding integration work. Consult it before editing shared flows.

## Module expansion and JDE replica drafts — 2026-10-17

At this earlier expansion the catalog contained **26 workflow samples**. This expansion adds **eight PSFT/EBS module drafts** and records the **four JDE replica drafts** from the preceding setup. All twelve are saved on build PAF under `editor@oracleagentfactory.com`, with Agent Memory and cross-thread sharing disabled. They remain unpublished.

| Application / module | New draft |
| --- | --- |
| PeopleSoft / HR | [PeopleSoft Position Coverage Review](agents/peoplesoft/position-coverage-review/) |
| PeopleSoft / Procurement | [PeopleSoft Purchase Order Review](agents/peoplesoft/purchase-order-review/) |
| PeopleSoft / Learning | [PeopleSoft Learning Capacity Review](agents/peoplesoft/learning-capacity-review/) |
| PeopleSoft / Customer Service | [PeopleSoft Service Case Workload](agents/peoplesoft/service-case-workload/) |
| PeopleSoft / Campus Operations | [PeopleSoft Campus Capacity Review](agents/peoplesoft/campus-capacity-review/) |
| EBS / Finance | [EBS Receivables Portfolio Review](agents/oracle-ebs/receivables-portfolio-review/) |
| EBS / Procurement | [EBS Purchase Receipt Review](agents/oracle-ebs/purchase-receipt-review/) |
| EBS / IT Operations | [EBS Concurrent Processing History](agents/oracle-ebs/concurrent-history-review/) |

JDE replica drafts: [Backorder Triage](agents/jd-edwards/replica-backorder-triage/), [Supplier Follow-up](agents/jd-edwards/replica-supplier-follow-up/), [Finance Activity Review](agents/jd-edwards/replica-finance-activity-review/), [Work Order Material Risk](agents/jd-edwards/replica-work-order-material-risk/). These bind separately to **JDEDEMO**; they do not switch the existing JDE source or published application flows.

### What was exercised

- All eight module fixed queries ran through the existing integration readers. Each new flow completed its primary business prompt and its limitations follow-up: **16 successful conversation requests**.
- All four JDE replica drafts completed a fresh primary conversation with memory explicitly disabled.
- Reader grant inspection showed only `CREATE SESSION` as a system privilege, no assigned roles, and existing SELECT/READ access to each required view. **No new grants, DML permissions or schema changes were needed for this expansion.** Each module includes an exact `assets/reader-grants.sql` setup reference for another installation.
- The new source exports, manifests, binding maps, SQL, prompts and presenter outlines are included here. Runtime records and model responses are retained only in private audit files.
- [Module access and validation notes](integrations/module-readers/README.md) explain scope and limits. New local `.paf` files are generated in ignored `dist/`; adding these source files does not itself publish a GitHub release.

### MCP checks

These drafts currently use direct PAF SQL/PLSQL components. Neither remote MCP path completed an authenticated tool invocation:

- **OCI Database Tools MCP:** the existing server is ACTIVE, and a fresh initialization request returned **401 with an OAuth bearer challenge**. It targets a different database. The earlier attempt to create a dedicated EBS server remains blocked by the identity-domain issuer prerequisite; no shared domain or server was changed. See [Database Tools MCP](integrations/oci-database-tools-mcp/).
- **ORDS MCP:** the existing ORDS runtime is **26.3.0**. The MCP and discovery requests returned **404**; MCP feature/JWT settings and dedicated MCP pools are absent. See the [ORDS MCP setup and probe notes](integrations/ords-mcp/). This is not an authenticated database/tool test.

## Original business demo collection

**Ten original business demos, plus the four original JDE fulfillment and memory examples.** The new demos are deployed on [build.oracleagentfactory.com](https://build.oracleagentfactory.com). The linked guides contain their current purpose-first titles; the table describes the original collection. The public [catalog](https://kgvarun.github.io/agent-factory-samples/) provides setup guides and the [latest release](https://github.com/kgvarun/agent-factory-samples/releases/tag/latest) provides importable `.paf` files.

| Business audience | Demo | Builder capability to show |
| --- | --- | --- |
| Procurement | [JDE Supplier Follow-up Desk](agents/jd-edwards/supplier-follow-up/) | Oracle PL/SQL executor with an explicit routine allowlist |
| Finance | [PeopleSoft Invoice Duplicate Review](agents/peoplesoft/invoice-duplicate-review/) | Fixed SQL query, JSON Parser, and grounded Agent |
| HR | [PeopleSoft Workforce Planning Brief](agents/peoplesoft/workforce-planning/) | Oracle database tools plus Current Date and Text combiner |
| Sales | [EBS Sales Commitment Review](agents/oracle-ebs/sales-commitment-review/) | Deterministic SQL evidence followed by an Agent |
| IT | [EBS IT Operations Triage](agents/oracle-ebs/it-operations-triage/) | Condition routing with separate outage and batch Agent paths |
| Field Ops | [JDE Field Material Readiness](agents/jd-edwards/field-material-readiness/) | Read CSV file, fixed SQL material/inventory join, and Agent |
| Compliance | [PeopleSoft Learning Evidence Review](agents/peoplesoft/learning-evidence-review/) | Fixed aggregate SQL, Current Date, and a policy-aware Agent |
| Knowledge Management | [Business Policy Desk](agents/cross-application/policy-desk/) | File upload, Text combiner, and document-grounded Agent |
| Executive Insights | [Executive Working Capital Brief](agents/cross-application/executive-operations-brief/) | Native Agent subagents with one shared read-only finance source |
| Database Performance | [PeopleSoft Database Service Pulse](agents/peoplesoft/database-service-pulse/) | Read-only monitoring views, SQL query, Parser, and Agent |

Each sample includes a business story, two demo prompts, evidence and interpretation rules, import bindings, validation notes, and a four-slide presenter sequence. Start with its README; `slides/README.md` is the short presenter outline. These are workflow demonstrations, with no measured ROI or production-readiness claim.

### Suggested 15-minute demo tour

1. **Policy Desk — 2 minutes:** ask about a USD 750 expedite. Show the file upload, the PROC-02 citation, and a missing-policy question. Explain that the handbook is fictional.
2. **Supplier Follow-up — 3 minutes:** show ten open PO lines. Open the PL/SQL routine allowlist and draft a supplier inquiry. The draft is not sent.
3. **IT Operations Triage — 3 minutes:** run the batch prompt, then the outage prompt. Show the Condition node taking different paths and explain why node configuration cannot prove login availability.
4. **Executive Working Capital Brief — 3 minutes:** show the supervisor and two native Agent subagents using the same read-only Finance source. Keep AP invoices distinct from AR payment schedules and preserve currencies.
5. **Field Material Readiness — 2 minutes:** contrast the fictional dispatch CSV with live JDE requirements. Repeated visible requirement rows need planner review; indicative inventory cannot confirm a visit.
6. **Database Service Pulse — 2 minutes:** show current HCM PDB metrics, units and timestamps. One snapshot is insufficient to diagnose a slowdown.

For a Finance audience substitute Invoice Duplicate Review; for HR or Compliance use Workforce Planning or Learning Evidence Review. For Sales use the five-line commitment sample and customer-update draft. The original four examples below remain the tour for persistent Agent Memory.

### Implemented feature coverage

The new collection uses Chat input/output, Agent, native Agent subagents, Oracle database tools, Oracle PL/SQL executor, SQL query, Parser, Condition, Current Date, Text combiner, File upload and Read CSV file. The original examples add REST API tools and explicit/implicit Agent Memory. Those original business demos do not send email, post to Slack, change application records or execute approvals. The subsequently added Fusion invoice draft has explicitly documented write tools.

Policy Desk uses direct file grounding; it is not a vector Knowledge Agent. The executive specialists share one EBS Finance source; they are not a cross-database federation demo. Select AI/In-Database Agent, A2A, image processing and Deep Research are not claimed by this collection. The optional [OCI Database Tools MCP blueprint](integrations/oci-database-tools-mcp/) is prepared but not deployed.

### Source and environment setup

- Reuse the existing curated JDE, PeopleSoft and EBS sources. Each `assets/source-bindings.json` names the exact source and affected nodes; schema references and deterministic SQL are included where applicable. Credentials and actual database rows are excluded.
- **Disable Agent Memory and sharing between chat threads for all ten new demos.** This instance enables them by default. Old prototype responses were recalled during development until these per-flow switches were disabled. The official export does not bundle these switches. Do not alter the original memory demos.
- After import, rebind source IDs and the model, and upload supplied file assets again. The validated model was `xai.grok-4.3`; output wording and model quality can vary.
- Historical JDE/EBS/PeopleSoft dates remain historical. Only database-monitoring observations and actual query clocks describe the observation time. The fictional policy and visit are labeled in their assets.
- To adapt a demo to another application/version, copy it into a new use-case folder with a distinct slug/title, inspect that version's view columns and grain, revise SQL and instructions, and repeat the business prompt. Do not assume EBS, PeopleSoft and JDE status codes, effective dates or units are interchangeable. These samples do not claim validation on every application version.

### Database changes and reversibility

Only the HCM demo PDB needed new database objects: three `PAF_DATA.DEMO_DB_*_PULSE` views, limited owner grants on `DBA_TABLESPACE_USAGE_METRICS`, `V_$SESSION` and `V_$CON_SYSMETRIC`, and SELECT on those views for the existing `PAF_AGENT_RO` reader. The owner remains locked. The reader sees selected tablespace counts, aggregate user-session states and five interval metrics, without session identities, SQL text or bind values.

The [monitoring setup](agents/peoplesoft/database-service-pulse/assets/monitoring-setup.sql) and [reader-access disable script](agents/peoplesoft/database-service-pulse/assets/monitoring-disable.sql) document the change. The disable script revokes only the three reader grants; it deliberately leaves the views and existing owner intact. No application tables, application configuration, initialization parameters or runtime services were changed. No EBS or JDE database change was needed for these demos.

### Validation and known limits — 2026-10-17

All ten final graphs completed their primary business prompt on the live instance with Agent Memory disabled. The IT batch and outage branches and Policy Desk's missing-policy response were also exercised. Fixed SQL was checked against its documented source; attempted writes through the three monitoring views were denied. Repository release generation decrypts and compares each archive with its source payload.

These checks establish a working demo path, not comprehensive business accuracy or application regression coverage. Inspect dates, amounts and evidence during a presentation. Suggested follow-ups are illustrative unless the sample validation notes say they were exercised. No app-wide regression or load test was performed. Real responses are intentionally not copied into this public repository.

The earlier executive prototype using different database connections failed with source-context errors on this build; the shipped two-specialist version uses one Finance connection. OCI managed MCP creation is blocked by an identity-domain issuer mismatch and lack of permission to create an isolated domain. See the integration README for the exact state and completion steps; no demo MCP server or replacement identity domain was created.

## Original JDE fulfillment and memory samples

| Sample | Connection context | Agent Memory behavior |
| --- | --- | --- |
| [JD Edwards Fulfillment Exception Agent](agents/jd-edwards/fulfillment-exception/) | Builder-managed JPS920 headers | None; grounded read-only analysis |
| [JD Edwards Fulfillment Memory Agent](agents/jd-edwards/fulfillment-memory/) | Supplied through an explicit named profile | Explicit setup and cross-session recall |
| [JD Edwards Adaptive Fulfillment Advisor](agents/jd-edwards/adaptive-fulfillment-advisor/) | Learned when first needed | Implicit learning through ordinary work and corrections |
| [JDE JPS920 Fulfillment Coach](agents/jd-edwards/jps920-fulfillment-coach/) | Builder-managed JPS920 headers | Implicit incremental corrections with a user-facing audit section |

These four samples form a progression from a stateless shortage investigation to a realistic, end-user-oriented Agent Memory demonstration. Their six JDE tools are read-only Simple Table Query operations over F4211, F4201, F41021, F4311, F4101, and F0101.

## Source and release contract

Each use-case folder under `agents/<application>/<use-case>/` contains:

| File | Purpose |
| --- | --- |
| `workflow.json` | Exact plaintext Agent Builder custom-flow payload extracted from the official export |
| `archive-metadata.json` | Server export metadata retained for compatible rebuilds |
| `sample.json` | Validated documentation and release manifest source |
| `README.md` | Contributor-oriented explanation and setup notes |
| `assets/agent-instructions.md` | Readable copy of the custom instructions |
| `assets/*.json` | Sanitized OpenAPI or other distributable dependencies |
| `slides/` | Optional presentation material |

`workflow.json` is not presented as Open Agent Spec. It is the product's serialized visual custom-flow payload. The original REST-based JDE flows currently cannot be exported as portable Open Agent Spec because their REST API Tools nodes are implemented by the Agent Builder runtime.

Generated `.paf` files are ignored by Git and must never be committed. The release workflow packages every `workflow.json`, decrypts the new archive in memory, compares the recovered JSON and metadata with the source, and only then publishes it.

## What the PAF contains

The generated archives are complete workflow-only imports for Private Agent Factory 26.7. They include:

- the visual graph, agent instructions, node settings, and workflow identifiers;
- the original compatible archive metadata;
- exactly one custom flow per sample.

They intentionally exclude:

- JDE or other application credentials;
- database, REST and MCP connection definitions or credentials;
- LLM connection definitions;
- Agent Memory configuration switches;
- learned user memory records;
- application rows and uploaded file contents.

Exact product exports can retain environment-local database IDs, model names, and uploaded filenames as binding hints. Those identifiers are not portable connection definitions. After import, create or reuse each documented source, configure authentication privately, rebind its nodes, select a model, and upload the supplied assets. Set Agent Memory according to the sample: off for the ten new business demos, enabled only for the memory examples that require it. Imported workflows remain unpublished until reviewed.

## Repository layout

```text
agent-factory-samples/
├── agents/
│   └── <application>/
│       └── <use-case>/
│           ├── workflow.json
│           ├── archive-metadata.json
│           ├── sample.json
│           ├── README.md
│           ├── assets/
│           └── slides/
├── docs/                         # Generated catalog and per-agent Pages
├── scripts/
│   ├── build_release.py          # Build, decrypt, compare, checksum
│   ├── generate_docs.py          # Validate manifests and generate Pages
│   └── utilities/
│       └── agent_sample.py       # Extract, inspect, and package PAFs
├── tests/
└── .github/workflows/
    ├── pages.yml
    └── release.yml
```

## Set up locally

Python 3.10 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

Passwords are prompted for securely by the archive utility. Automation reads the passphrase from a named environment variable. Never commit it, print it, place it in `sample.json`, or put it directly on a command line.

## Extract a UI export into reviewable source

Export one custom flow from **My Custom Flows**, then run:

```bash
python scripts/utilities/agent_sample.py create-from-paf ~/Downloads/exported_flows_*.paf \
  --application "JD Edwards"
```

The command asks for the export passphrase, validates the envelope and ZIP, requires exactly one flow, and creates a starter folder under `agents/<application>/<use-case>/` with `workflow.json`, `archive-metadata.json`, and documentation directories. It does not copy the generated binary into the sample folder.

For non-interactive automation:

```bash
export PAF_PASSWORD_FROM_SECRET_STORE='...'
python scripts/utilities/agent_sample.py create-from-paf exported.paf \
  --application "JD Edwards" \
  --password-env PAF_PASSWORD_FROM_SECRET_STORE
```

Add and complete `sample.json` in the new folder before committing it. The documentation build intentionally fails when required documentation is absent.

## Build and inspect archives

Build all release assets with the common repository archive passphrase:

```bash
export PAF_ARCHIVE_PASSWORD='...'
python scripts/build_release.py
```

The command writes only to ignored `dist/`:

```text
dist/
├── <agent-slug>.paf
├── manifest.json
├── SHA256SUMS
└── RELEASE_NOTES.md
```

To build a single sample:

```bash
python scripts/utilities/agent_sample.py pack agents/<application>/<use-case> \
  --password-env PAF_ARCHIVE_PASSWORD
```

To validate and summarize a downloaded archive without exposing its graph or passphrase:

```bash
python scripts/utilities/agent_sample.py inspect path/to/agent.paf \
  --password-env PAF_ARCHIVE_PASSWORD
```

The PAF envelope uses PBKDF2-HMAC-SHA256 with 100,000 iterations, a random 16-byte salt, and a 32-byte key. AES-256-GCM uses a random 12-byte IV. The file stores Base64 of `salt || IV || ciphertext || tag`.

The common passphrase provides format-compatible archive protection and import gating, not source confidentiality: the workflow source is intentionally reviewable in this repository. Distribute the passphrase through an approved secret-sharing channel.

## GitHub Actions and releases

Set the repository Actions secret once:

```bash
gh secret set PAF_ARCHIVE_PASSWORD
```

The command prompts for the value. Use the repository-specific common archive passphrase, never an Oracle account password.

On every push to `main`, `.github/workflows/release.yml`:

1. runs all tests and validates the documentation manifests;
2. builds all encrypted archives;
3. decrypts and compares every generated archive with its source;
4. produces SHA-256 checksums and a machine-readable manifest;
5. uploads the complete `dist/` directory as a workflow artifact;
6. replaces the rolling prerelease tagged `latest`.

Pushing a `v*` tag publishes a permanent versioned release using the same validated assets. Release notes never contain the archive passphrase.

## GitHub Pages documentation

`sample.json` is the documentation contract. It records:

- application and use-case names and hierarchy slugs;
- title, summary, category, workflow version, and compatible PAF version;
- connection ownership and Agent Memory behavior;
- capabilities, prerequisites, tools, and safety controls;
- import and binding steps;
- realistic multi-session demo turns and expected outcomes;
- validation date, environment, status, and notes;
- source and release artifact names;
- either `artifacts.openapi` for REST definitions or `artifacts.dependencies` for database/file bindings (both may be supplied).

Generate the site locally:

```bash
python scripts/generate_docs.py \
  --repository-url https://github.com/kgvarun/agent-factory-samples/tree/main \
  --release-base-url https://github.com/kgvarun/agent-factory-samples/releases/download/latest
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. The site groups use cases by application and includes a detailed page for every agent, documented demo prompts and validation scope, direct release downloads, source links, and `agents.json` for machine-readable discovery.

The Pages workflow regenerates and validates the site on every push to `main` and always uploads `rendered-agent-pages-<commit>` as an Actions artifact. Public repositories deploy automatically.

For a private repository, the organization plan must support GitHub Pages. Enable Pages with **Build and deployment → Source → GitHub Actions**, then create the repository variable `ENABLE_GITHUB_PAGES=true`. Until then, deployment is skipped without hiding documentation-build failures.

## Validate a contribution

```bash
python -m unittest discover -s tests -v
python scripts/generate_docs.py
PAF_ARCHIVE_PASSWORD='a-local-test-secret' python scripts/build_release.py
```

Before contributing, confirm that:

- the workflow imports into a compatible non-production Private Agent Factory environment;
- the folder follows `agents/<application>/<use-case>/` and its manifest slugs match that hierarchy;
- `sample.json` accurately documents prerequisites, tool scope, setup, demo turns, and validation;
- `workflow.json` remains the exact payload intended for packaging;
- environment-local dependencies can be rebound after import;
- memory-enabled samples exclude learned user data;
- OpenAPI and other assets are sanitized and redistribution-safe;
- no passwords, credentials, cookies, tokens, or customer-confidential data are present;
- no `.paf` file is tracked in Git.

## Format reference

The archive layout and password envelope follow the internal Agent Builder import/export specification. The repository utility packages an existing valid Agent Builder graph; it does not translate an arbitrary agent definition into a custom flow.
