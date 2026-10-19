# Discover sample agents through conversation

Create two native Private Agent Factory agents that help participants choose and
understand samples from the [published catalog](https://kgvarun.github.io/agent-factory-samples/).

| Agent | Native type | Evidence | Use it for |
| --- | --- | --- | --- |
| **Agent Catalog Knowledge Guide** | Knowledge | Catalog web source, refreshed every 24 hours | Find a sample, explain its workflow, prerequisites and action boundaries |
| **Agent Catalog Deep Research** | Deep Research | Versioned file snapshot of the published catalog, with vector search | Compare samples and prepare a cited recommendation or demonstration plan |

The Knowledge Guide demonstrates web ingestion and retrieval. Deep Research
demonstrates file ingestion, vector preparation and research across documents.
The current Deep Research API accepts file sources; it cannot select a web source
directly. The script converts the public `agents.json` into one text document per
sample plus an overview. Each document retains its exact public catalog URL and
the catalog metadata, including workflow steps, tools and prerequisites. No
business application records are included.

Both agents explain documented capabilities. A catalog listing does not establish
that a sample's connections or tools are configured in the participant's account.
These discovery agents cannot execute the listed workflows or change applications.
Review their cited evidence before using a recommendation.

## Prerequisites

- A destination Factory account that can create web/file sources and native
  Knowledge and Deep Research agents.
- The generation connection **AIW26-PAF-HOL6004-BOO6096** accessible to that account.
- An active **cohere.embed-v4.0** embedding connection, or an explicitly configured
  compatible embedding name in a private copy of `config.json`.
- Outbound HTTPS access to the public catalog for both the provisioning client
  and the Factory web crawler. The script uses a depth-two crawl and excludes
  archives, images, styles and scripts.
- Python 3.10 or newer. Creation uses only the standard library. Optional UI
  history verification also requires `requests` and `python-socketio[client]`.

The prepared authoring copy belongs to the editor account. For participant
environments, run the same script authenticated as each participant. Agent and
source IDs are destination-specific and are discovered or created there.

## Repeatable creation

The operational project belongs under `~/work/apps/agent-factory/catalog-discovery/`.
This directory contains its sanitized, portable recipe. Copy `provision.py` and
`config.json` there before running, or run this checked-out recipe with all state
outside the repository. Provisioning does not change Factory source code or
require a service restart.

Keep the actual application URL, account and credential file in private operator
configuration. The credential CSV must contain `user,password` (or
`username,password`) columns and exactly one row matching the destination account.
Do not put real values in this repository, README files or Pages assets.

```bash
# Set these values through private operator configuration first:
# PAF_BASE_URL, PAF_ACCOUNT, PAF_CREDENTIALS_CSV, PAF_STATE_DIR
# Use a different private state directory for every destination/account pair.

python3 provision.py plan

python3 provision.py apply \
  --credentials-csv "$PAF_CREDENTIALS_CSV" \
  --state-dir "$PAF_STATE_DIR"

python3 provision.py verify \
  --credentials-csv "$PAF_CREDENTIALS_CSV" \
  --state-dir "$PAF_STATE_DIR"
```

`plan` reads the published catalog without contacting Factory. `apply` creates or
reuses the owned web source, a content-addressed file snapshot and both native
agents. It waits for ingestion and research preparation, verifies source bindings
and the Knowledge model, and sets **the destination account's default model** to
the required generation connection so new Deep Research UI chats select it too.
This account preference also applies to other native chats that use the account
default. The global model default is not changed.

Existing matching names owned by another account are rejected. Matching owned
resources are reused. If catalog content changes, a new snapshot and a versioned
research agent are created; earlier research agents are retained. A timestamp-only
site rebuild does not create another snapshot. Existing web sources are reused
with their current crawl settings; inspect those settings if an operator changes
them manually. The web-source URL must still match the configured catalog.

`receipt.json` records destination IDs, model checks, snapshot hash and preparation
status. Upload sessions, diagnostics and chat responses remain alongside it in
private files with mode `0600`, under directories with mode `0700`. After a timeout
or interrupted upload, rerun `apply` with the same account and state directory.
Do not delete an active upload session or reuse state for another account.

Native creation uses these API families:

| Resource | API |
| --- | --- |
| Web source | `/v1/datasource/web` |
| File snapshot | `/v1/file/uploadSessions` and its chunk endpoint |
| Knowledge agent | `/v1/createKnowledgeBase`, `/v1/knowledge/agents`, `/v1/knowledge/settings/{id}` |
| Deep Research | `/v1/deepResearch/agents` and native preparation/access-method discovery APIs |
| Account model preference | `/v1/setPrimaryLLMConfig` |

These are native agent types, so workflow-only `.paf` exports are not the creation
recipe. Retain the script, configuration and private destination receipt instead.
Agent Builder memory switches do not apply to these native types; the research
assistant is created with its optional cache and memory flags disabled.

### Knowledge help compatibility

On versions providing `PATCH /v1/knowledge/agents/{id}`, the script installs the
full Knowledge Guide description and sample questions from
`KNOWLEDGE_DESCRIPTION` in `provision.py`. The running authoring installation
does not expose that endpoint. Creation and retrieval work, but its long help
field remains unavailable; the receipt records `knowledge_help_updated: false`.
New copies still receive the short description with two sample questions at
creation. Existing copies keep their description when that edit endpoint is
unavailable. The complete purpose, boundaries and questions are included here and
in the portable source. No database workaround or Factory code patch is used.

## Participant questions

For **Agent Catalog Knowledge Guide**:

- Which sample renews an EBS blanket purchase agreement? Explain its review and
  submission steps, prerequisites and limitations, and give its catalog link.
- Which Linux monitoring sample uses osquery? What can it inspect and what can
  it change?
- Find a read-only Fusion procurement example and explain how to import it.
- Does finding a sample here mean it is already configured in my account?

For **Agent Catalog Deep Research**:

- Compare EBS Contract Renewal and Linux OS Monitoring: workflows, data sources,
  permitted actions, prerequisites and a demonstration question for each. Finish
  with their public catalog links.
- Recommend three procurement samples with setup checklists, evidence links,
  approval boundaries and a five-minute demonstration plan.
- Compare a knowledge workflow and a database analysis workflow. What data does
  each need, and what does an import leave to configure?
- Which samples use memory, and which settings need to be reapplied after import?

Research citations may display snapshot filenames. Ask for the public catalog
link stored in each document's `Source URL` or `page_url` when a response omits it.
Consult the receipt for the snapshot's hash and catalog generation time. Rerun
`apply` to prepare a new snapshot after a catalog content update; web recrawling
alone does not refresh a Deep Research snapshot.

## Verify and demonstrate

`verify` sends one question through each native run API. Each run creates a normal
private chat under the destination account and records its room ID. Review the
answer, source citations and boundaries in the corresponding agent's chat history.
An API response alone is a smoke check, not a complete answer-quality evaluation.

For independent readback through the UI's history transport:

```bash
python3 -m venv /tmp/catalog-history-venv
/tmp/catalog-history-venv/bin/pip install requests 'python-socketio[client]'
/tmp/catalog-history-venv/bin/python provision.py history \
  --credentials-csv "$PAF_CREDENTIALS_CSV" \
  --state-dir "$PAF_STATE_DIR"
```

The default Socket.IO path is `/socket.io`; use `--socket-path` if the destination
uses another path. This verifies that both the user and assistant messages can be
read back from the saved rooms. It does not create additional conversations.

Live validation on **2026-10-19**: the 50-workflow catalog was ingested as a web
source and 51 snapshot documents; both native agents became ready. The Knowledge
Guide answered the EBS renewal question with its steps, two prerequisites and
approval boundary. Deep Research compared it with Linux monitoring, distinguished
write versus read-only scope and cited both snapshot documents. Both conversations
were independently read back with user and assistant messages using the native
UI history interfaces. Knowledge help editing has the compatibility limit above.

Run the offline regression checks from the sample repository root:

```bash
python3 -B -m unittest tests.test_catalog_discovery -v
```
