# EBS contract renewal with document vector search

**Status, 19 October 2026:** the EBS import path, scoped vector retrieval and private PAF draft agent are implemented. The email/code business run created a new **Incomplete** blanket purchase agreement (BPA) with three matching line prices; the user confirmed inbox receipt and is inspecting the result in EBS. The saved conversation includes later user approval and a separate submission. A final status check captures the completed import receipt after asynchronous processing. Email review uses the existing Email output tool and demo code **6004**; its database checks passed 33 assertions.

This extends [Simplifying contract renewals: an AI agent for EBS with Private Agent Factory](https://blogs.oracle.com/database/simplifying-contract-renewals-an-ai-agent-for-ebs-with-private-agent-factory). It reads current Purchasing prices, searches historical EBS PDFs, stages immutable changes and submits the supported import interface after an exact-hash review. The fixed-code path demonstrates confirmation, not authenticated reviewer identity. Service Contracts and other modules need their own interfaces.

Follow the [demo flow and copyable chat prompts](DEMO.md). For a completed run, resume with its status check and existing BPA verification.

## Architecture and alternatives

```text
Question → Renewal agent → Evidence, proposal and next action
                ↑
         ┌──────┴──────────────────┐
         │                         │
  ADB-S document MCP       Restricted EBS PL/SQL
  3 retrieval tools        7 renewal functions
                                   │
                         Staging → Validation
                                   │
                   Email → Later chat code + reason
                                   │
                       Separate import request
                                   │
                    Import → New Incomplete BPA
                                   │
                     Buyer inspection in EBS Forms
```

| Route | Advantages | Costs and current limits |
| --- | --- | --- |
| **ADB-S MCP + direct EBS PL/SQL, implemented** | Scoped vector evidence; EBS-local validation and transactions; no database-link dependency. | Two sources and backend scope/review setup; fixed-code review is demo-only. |
| ADB-S MCP + EBS database link | One endpoint for evidence and transactions. | Existing link tests returned `ORA-28040`; identity propagation, remote LOBs, commits and retries need a prototype. Authentication was not weakened. |
| ADB-S MCP + OCI Database Tools MCP | Managed MCP transport and predefined toolsets. | The shared server uses an ADMIN connection to another database. A dedicated identity, roles and restricted EBS connection remain prerequisites. It was not repointed. |
| EBS application service | Application-facing authentication and service boundary. | Depends on deployed services and BPA coverage; staging and review remain necessary. |

Oracle documents [PL/SQL-backed MCP tools](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/use-mcp-server.html) and [Database Tools MCP toolsets](https://docs.oracle.com/en-us/iaas/database-tools/doc/database-tools-mcp-toolsets.html). A third runtime database has no required role here.

## Implemented workflow

1. Read the authorized source BPA and current header/line prices.
2. Search authorized historical documents and return cited passages, source IDs, hashes, captured revisions and dates. Report missing legal terms explicitly.
3. Show proposed dates, uniform uplift and all old/new prices. An explicit request containing all target terms authorizes custom staging; otherwise obtain missing values and confirmation.
4. Stage an immutable draft with evidence references and a stable idempotency key. Validate scope, source freshness, supplier/site/items, dates, UOM and deterministic prices.
5. Request one recipient email address from the user in the current conversation, prepare its exact-draft review and send with native confirmation. There is no default recipient, and account settings or memory cannot supply one. The database supplies readable text for this preview; the assistant gives concise receipts without repeating the email or printing HTML. After successful sending, the user enters code **6004**, draft ID and a review reason in a later message. This records a one-hour demo review; it does not import. See [email/chat review](EMAIL-REVIEW.md).
6. On a separate later request, submit the reviewed draft through Import Price Catalogs. A request ID means processing; report creation only when result checks confirm `IMPORTED`.
7. Inspect the new Incomplete BPA in **Purchasing → Purchase Orders → Purchase Order Summary**, querying its returned number. This launches Oracle Forms. Buyer Work Center's global-agreement search may omit a local BPA.

The initial write scope supports Approved, open, local USD BPAs with 1–100 active goods lines, a uniform 0–10% uplift and at most 366 inclusive days starting today or later. It does not copy clauses/attachments, change supplier, amend the source, alter releases or approve the resulting BPA. See [installation and transaction details](IMPLEMENTATION.md).

The retrieval corpus contains **nine real EBS PDF attachments and 24 embedded chunks**; one empty attachment was skipped. EBS supplied the PDFs, so Object Storage was unnecessary. A private curated Object Storage source remains an alternative. There is no approved legal-template tool. Purchase documents do not establish missing renewal, liability or termination clauses. See [retrieval setup and limits](RETRIEVAL.md).

## PAF setup

The [portable workflow](../../agents/oracle-ebs/contract-renewal/workflow.json) includes model `AIW26-PAF-HOL6004-BOO6096`, a detailed Agent description, eight sample questions and four explanatory sticky notes on a left-to-right canvas. Source-binding placeholders need target configuration.

1. Install staging/API/wrappers, the three-phase email-review SQL and scoped retrieval from the linked runbooks. Configure a working SMTP sender in PAF administrator settings.
2. In each intended account, register an encrypted EBS datasource using restricted `AF_EBS_RENEWAL`. Verify exactly seven `RNW_*` wrappers, including both email-review functions. Never use APPS as its datasource.
3. Register the document MCP source using restricted `AF_EBS_DOC_MCP` and protected token-request credentials. Check list/search/get and wrong-source denial. Runtime endpoints stay in private operational configuration.
4. Bind `__EBS_DATABASE_SOURCE_ID__`, `__DOCUMENT_MCP_SOURCE_ID__`, `__SOURCE_HEADER_ID__` and `__SOURCE_BPA_NUMBER__` to reviewed account resources. Prompt bindings cannot expand database authorization.
5. Save/import using the target workflow interface and verify sources/model. JSON is reviewable workflow source, not an encrypted `.paf` archive. Live IDs remain private.
6. Apply [per-user memory settings](../per-user-deployment/) separately after import. Memory/thread sharing are enabled for the current draft; fresh tools must supply prices, scope, hashes, review and import state.
7. Start with read-only chat, then explicitly stage once. Verify unreviewed submission creates no interface batch/request. Test email confirmation and its actual result before entering a review code. SMTP errors must stop approval.

For tests that must appear in web UI history, use authenticated `POST /v1/agentBuilder/run/{agent_id}` with `{"message":"<question>"}`. Retain `roomId` for follow-ups and reopen the conversation under the same account/flow. `POST /v1/runAgentBuilderFlow` executes a temporary graph without saving a conversation. Memory settings are separate from persistence.

Sample questions:

- “Summarize my source BPA and show current line prices.”
- “Find historical evidence for renewal terms, cite passages and identify gaps.”
- “Propose 12 months from tomorrow with unchanged prices. Show changes before staging.”
- “Stage these confirmed dates and prices, validate and show its ID and hash.”
- “Email my validated draft's review to <your-email-address>.”
- “Approve draft <id> with code 6004. Reason: I checked the dates, prices and gaps.”
- “Submit my reviewed draft as a new Incomplete BPA.”
- “Check whether it imported and tell me how to inspect it in EBS.”

## Security and validation

The runtime has `CREATE SESSION`, execution of its two bounded packages and seven owned wrappers. The authenticated database username maps to an active EBS user, responsibility, operating unit and source header. Calls initialize/clear EBS context. They write custom staging and Purchasing interfaces, without direct Purchasing base-table updates.

Reviews bind the immutable hash, expire after one hour and are consumed atomically on submission. Idempotency prevents duplicate drafts/imports; source changes invalidate stale proposals. `SUBMITTED`, `IMPORTED` and `IMPORT_FAILED` differ. The demo code is not proof of identity. Later-human-turn and successful-send checks are agent instructions, not database-enforced reviewer identity. A plain yes does not authorize import. A separately controlled operator procedure remains available.

The document login runs only three retrieval wrappers. It uses [MCP identity context](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/mcp-server-concepts.html), with org/supplier predicates before ranking, bounded results and a seven-day capture limit. Document text is untrusted evidence. Accounts sharing a backend credential share its data scope; separately authorized identities are needed for isolation.

Live checks covered direct/MCP retrieval, citations, unrelated queries, wrong-source/input denial, denied table/admin access, seven-function discovery, combined model execution, staging/validation and missing-review denial. The first import and repeated-call idempotency were verified. Saved read-only chat was reopened in the UI. Email-review tests passed 33 assertions including expiry and retry behavior, without submitting an import. Native email confirmation, the initial SMTP rejection and the successful retry were captured in saved chat; all eight email-test messages reloaded in the UI. The email test recorded no approval and submitted no import.

The later business run verified email sending, user-confirmed inbox receipt, later exact-hash review, separate submission and a completed import with matching prices. Remaining checks include source-change/import-failure fixtures, per-account deployment and full buyer inspection. This is a tested integration draft, not a production rollout. Keep application setup under `~/work/apps/ebs`, PAF operations under `~/work/apps/agent-factory`, infrastructure under `~/work/infra`, and sanitized examples here. Credentials, PDFs, extracted text, live IDs, endpoints and receipts stay outside publication inputs.
