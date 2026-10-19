# EBS Contract Renewal with Document Evidence

Renew an authorized Oracle Purchasing blanket purchase agreement (BPA) using live line prices and cited historical PDFs. The agent shows a proposal, stages immutable changes, sends a review email to a recipient supplied in the current chat, records a later user review and submits only on a separate request. The result is a new **Incomplete** BPA for buyer inspection in EBS Forms.

This is the catalog entry for the [EBS renewal integration](../../../integrations/ebs-contract-renewal/). Follow its [installation runbook](../../../integrations/ebs-contract-renewal/IMPLEMENTATION.md), [document retrieval setup](../../../integrations/ebs-contract-renewal/RETRIEVAL.md), [email review setup](../../../integrations/ebs-contract-renewal/EMAIL-REVIEW.md) and [complete demo flow](../../../integrations/ebs-contract-renewal/DEMO.md).

## Workflow and dependencies

The [portable graph](workflow.json) has one renewal Agent, three document MCP tools, seven restricted EBS PL/SQL functions, the native Email output tool and four explanatory notes on a left-to-right canvas. It uses **AIW26-PAF-HOL6004-BOO6096**. Read the [agent instructions](assets/agent-instructions.md) and [source bindings](assets/source-bindings.json) before importing.

The release workflow generates `ebs-contract-renewal.paf` from these sources. This is a workflow-only archive: it does not install database packages, document embeddings, connections, SMTP settings, model credentials or memory settings. The source is adapted from the tested saved graph with portable placeholders and local draft version 1; its archive metadata is generated rather than an official export receipt.

1. Install the restricted transaction API and scoped document retrieval using the integration runbooks. Register the transaction source as `AF_EBS_RENEWAL`, never APPS, and the document MCP source as `AF_EBS_DOC_MCP`.
2. Import the generated archive and leave the agent unpublished during target validation. Bind `__EBS_DATABASE_SOURCE_ID__` and `__DOCUMENT_MCP_SOURCE_ID__` to those sources.
3. Replace `__SOURCE_HEADER_ID__` and `__SOURCE_BPA_NUMBER__` with the agreement authorized by that account. Database scope remains authoritative.
4. Select the required model and privately configure a working SMTP sender. Leave the recipient blank; the user supplies one for each draft in the current conversation.
5. Apply [per-user memory settings](../../../integrations/per-user-deployment/) separately. Memory may retain presentation preferences; recipients, prices, scope, hashes and approvals must come from current chat or fresh tools.
6. Begin with read-only prompts, then follow the reviewed action sequence in one saved conversation.

## Demo prompts

| Step | Prompt or action |
| --- | --- |
| Inspect | “Summarize my source BPA, supplier/site, dates and every current line price.” |
| Retrieve | “Find historical renewal evidence. Cite the documents and explain what terms are missing.” |
| Propose | “Propose a 12-month renewal starting tomorrow with unchanged prices. Show dates and old/new prices before staging.” |
| Stage | “Stage the proposal I reviewed, validate it and show the draft ID and exact hash.” |
| Email | “Email review for draft `<draft_id>` to `<your-email-address>`.” Choose Send in the native confirmation and verify the send result. |
| Review | After receiving the email, enter in a later message: “Approve draft `<draft_id>` with code 6004. Reason: I reviewed the dates, prices and evidence gaps.” |
| Submit | In a separate later message: “Submit reviewed draft `<draft_id>`.” |
| Verify | “Check draft `<draft_id>` again. Show final status, request number, BPA number and imported line prices.” Then query that BPA in **Purchasing → Purchase Orders → Purchase Order Summary** in Oracle Forms. |

The assistant gives concise email receipts. The native Send/Cancel dialog is the single preview; assistant responses should not print HTML, tool JSON or another copy of the email. Resume completed runs with a status check instead of submitting again.

## Scope and validation

The initial path supports Approved, open, local USD goods BPAs with 1–100 active lines, a uniform 0–10% uplift and at most 366 inclusive days beginning today or later. It uses custom staging and supported Purchasing interfaces. It does not amend the source agreement, copy legal clauses or attachments, alter releases or approve the new BPA.

The database enforces scope, immutable hashes, recipient binding, review expiry and idempotency. The fixed code **6004** demonstrates confirmation; it is not authentication or proof of mailbox ownership. Successful-send and later-human-turn checks are agent instructions. Dedicated accounts need separately scoped sources, and missing legal clauses remain evidence gaps.

The 19 October 2026 business run verified email sending, user-confirmed inbox receipt, later review, separate submission and an imported Incomplete BPA with three matching line prices. Email-review database checks passed 33 assertions; saved-chat recipient behavior passed five UI checks without another email or import. The retrieval corpus contained nine EBS PDFs and 24 embedded chunks. Per-account rollout, failure fixtures and full buyer inspection remain follow-up checks. See the [integration validation record](../../../integrations/ebs-contract-renewal/README.md#security-and-validation) for details.
