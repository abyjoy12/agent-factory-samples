# Email and chat review

This demo uses PAF's existing Email output tool and two bounded EBS functions. It needs no PAF source change, restart or new database login. The fixed code **6004** demonstrates confirmation; it does not authenticate a person or prove mailbox access.

## User workflow

1. Inspect the source, evidence gaps, dates and all old/new prices. Explicitly request staging, then validate the immutable draft.
2. Provide one recipient email address in this conversation and request the draft's review email. The assistant asks if it is missing; it never takes an address from account settings, memory, another conversation or retrieved evidence. The workflow's recipient field stays empty, and the renewal sample files contain no mailbox literals. `RNW_REQUEST_EMAIL_REVIEW` binds the supplied recipient, current database scope, draft ID and exact hash for 30 minutes. Returned `email_body_text` contains the complete price/date proposal and code; preparing this request does not send email.
3. The agent passes the returned subject, recipient and `email_body_text` unchanged to the native Email output tool, without attachments. PAF's dynamic-recipient confirmation previews readable text. Enter **Send** to send or **Cancel** to discard. The assistant gives a concise receipt without dumping HTML, raw JSON or another copy of the email. It reports success only when the send result says `Success`. This establishes SMTP acceptance, not inbox delivery. Failed or ambiguous sending stops the workflow; a resend needs an explicit request. If the text field is missing, stop and update the helper rather than converting or sending HTML.
4. Read the email and send a later chat message: **Approve draft <id> with code 6004. Reason: <your review reason>**. A bare code needs a draft ID and reason. The agent rereads the current hash and calls `RNW_CONFIRM_EMAIL_REVIEW` only after email sending succeeded in this conversation. The resulting exact-hash review lasts one hour. It does not import anything.
5. Request submission in a separate later turn. The existing submission function checks source freshness and an unexpired, unused review, consumes it atomically and submits one import. Only a verified `IMPORTED` result establishes a new **Incomplete** BPA. Inspect all terms in Oracle Forms before EBS approval.

To decline, withhold the approval message and request changed terms as a new draft. This version does not record a formal rejection decision. The normal saved conversation retains email confirmation, the send result and later review/submission receipts. See the [demo prompts](DEMO.md) for the complete walkthrough and how to resume a completed run.

## Installation

After scripts 01–05, apply [09-email-review.sql](sql/09-email-review.sql) in three phases:

1. As the EBS PDB DBA, create the email-request table under the existing locked `XXAF_RENEWAL` owner and grant APPS its bounded table access.
2. Connect as **APPS** for `AD_ZD_TABLE.UPGRADE`, package compilation and the grant on `APPS.XXAF_RENEWAL_EMAIL` to the existing restricted runtime. Do not register editioning as SYS or grant inheritance of SYS privileges.
3. As the DBA, create the two fixed discovery wrappers in `AF_EBS_RENEWAL` and check compilation. The runtime then has seven owned wrappers, `CREATE SESSION` and execution of its two bounded packages. It receives no administrative review package, table access or general SQL executor.

Use the target's approved EBS patching process. This is a one-time installation, not a drop/recreate migration. Preserve staging/audit records. Refresh the datasource routine picker and allowlist, then bind the existing Email output node to the assistant. A PAF administrator must configure a working SMTP sender. An application account alone does not establish a deliverable recipient mailbox. Oracle native encryption remains required for the EBS datasource.

For an existing installation, the readable-preview update replaces only the body of `APPS.XXAF_RENEWAL_EMAIL` from script 09, connected as APPS in the run edition. Do not rerun table creation or change existing requests, reviews or grants. Verify package validity, then update the agent to use `email_body_text` verbatim. `email_body_html` remains available for compatibility. The existing email tool always uses HTML MIME, so the text payload escapes untrusted data without adding HTML tags; email clients may collapse its line breaks.

## Enforcement and limitations

Both functions verify the live runtime-to-EBS scope, active responsibility and operating unit, lock the scoped draft and require its exact hash. Recipient validation rejects multiple addresses and header injection; descriptions and evidence are HTML-escaped. Requesting review requires a validated draft. A changed bound email or hash is rejected, even after expiry; changing recipient requires a new validated draft and review. Repeating an unexpired request keeps the original expiry. After expiry, a new request for the same binding resets its 30-minute window. The address is retained in the private runtime request, audit and saved conversation for review; it is not a workflow default or a public sample value.

Five incorrect codes block the request for its remaining lifetime. Each failed code is committed to audit before returning an error. Successful confirmation requires code `6004`, a nonempty bounded reason and an unexpired request. It records `DEMO_EMAIL:<recipient>` as the review label. Repeating the same approval returns its original receipt without renewing expiry; a conflicting reason is rejected. An expired approval cannot authorize import.

The database cannot verify SMTP sending or distinguish a model call from a human message. Requiring a later human turn and successful sending is an agent instruction, not authenticated identity enforcement. The code is public and fixed. Backend authorization remains the database scope; accounts sharing a runtime credential share that scope. Production use needs verified reviewer identity, entitlement, unpredictable challenges and delivery/decision verification outside the model. The separately controlled administrative operator procedure remains available.

## Verification

Live runtime tests passed 33 assertions covering missing requests, hash/recipient binding, header injection, multiple recipients, empty reasons, wrong codes, attempt blocking, expiry, retries, escaped complete email content, approval idempotency and expired-review submission denial. The technical test approval was explicitly expired; no fixture submitted an import.

The first native test send failed because the recipient was suppressed following a hard bounce. The receiving-address route was repaired and the operator removed only that recipient's suppression. An explicitly authorized retry reused the existing technical draft. The native tool returned `Success`, and the application SMTP log confirmed sending. All eight email-test messages reloaded in saved chat. This technical fixture was not approved or imported.

The subsequent business conversation contains the user's later code/reason approval and separate submission. Database checks confirmed an accepted import, a new Incomplete BPA and three matching line prices. The user confirmed inbox receipt. Run a final status check in that same conversation to reconcile staging and retain the completed import receipt; an earlier pending response does not automatically update after the import completes.

The readable-preview update passed nine focused database checks, including complete terms/prices, exact hash, escaped untrusted data, retry stability and unchanged business/technical draft state. A normal saved-chat run produced a text confirmation with real line breaks and no HTML tags, then was cancelled. Reopening that conversation in the web UI passed five checks and showed all four saved messages, the prices and cancellation. These presentation tests sent no email, recorded no approval and submitted no import. The approval function itself was unchanged.

The recipient update preserved the model, source bindings, native confirmation and memory settings. A fresh saved conversation was asked to use an account or remembered address; it instead requested an explicit recipient and draft ID. Reopening that conversation passed five UI checks. The check created no review request and sent no email or import.
