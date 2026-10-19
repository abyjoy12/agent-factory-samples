# EBS renewal implementation and verification

The EBS implementation creates an immutable renewal draft, validates it, records an exact-hash review, and submits **Import Price Catalogs** for exactly one batch. The import creates a new local Purchasing blanket purchase agreement with status **Incomplete**. Existing agreements and releases remain separate.

The first live import completed on 19 October 2026. Database verification confirmed the new header, three goods lines, dates, unchanged USD prices, and Incomplete status. Repeating both staging and submission returned the original draft, request and BPA. Direct table reads/writes, administrative review, another source BPA, excessive uplift, an excessive term, an unknown draft and a conflicting idempotency payload were rejected under the runtime identity. Operational document numbers, credentials and receipts stay in the private EBS application directory.

Document retrieval and a private PAF draft agent were also built and tested on 19 October 2026. Nine authorized historical EBS PDFs produced 24 vector chunks. The agent combined live EBS prices with cited document evidence, created and validated a separate custom draft, and received `ORA-20008: Trusted review is required` when asked to submit it without operator approval. Database checks confirmed no new interface batch or import request from that denied action. The earlier imported BPA remains a separate fixture.

The agent uses `AIW26-PAF-HOL6004-BOO6096` under the designated sample-owner account. Memory and sharing between chat threads are enabled for that account; those settings must be applied separately after importing into each dedicated account. Application login and the Purchasing responsibility were verified, including the Oracle Forms launch. The buyer reports finding the resulting BPA in Forms with three lines; supplier/site, dates, prices and status still need explicit buyer confirmation. [Email/chat review](EMAIL-REVIEW.md) is deployed using the existing Email output tool and fixed demo code 6004. Its database tests passed 33 assertions. The initial SMTP suppression was resolved; a subsequent business run sent the email, captured later approval and separate submission, and imported a new Incomplete BPA. The user confirmed inbox receipt. No PAF source change, restart or new login was needed. The trusted operator procedure below remains separately controlled.

## Database installation

Canonical application setup belongs under `~/work/apps/ebs/contract-renewal/`. This directory contains sanitized copies for review and reuse. Live validation used EBS 12.2.14 and Oracle Database 19.24. Review schema names, tablespace, edition and installed concurrent-program arguments for each target. Apply customizations through the target's approved EBS patching process; the initial demo deployment was applied in its run edition.

1. As the EBS PDB DBA, run [01-schema.sql](sql/01-schema.sql) once. It creates a locked schema-only data owner, `XXAF_RENEWAL`, with a bounded tablespace quota. It intentionally refuses an existing schema. Never rerun by dropping live staging or audit records.
2. As APPS, run [02-register.sql](sql/02-register.sql). It registers the custom schema and uses `AD_ZD_TABLE.UPGRADE` for editioning views and APPS synonyms. Custom tables are not owned by APPS.
3. As APPS, run [03-api.sql](sql/03-api.sql). It compiles the runtime and operator-review packages and fails on compiler errors. The source selects from EBS through APPS synonyms and writes Purchasing interface tables only.
4. As the DBA, create a dedicated runtime login with a generated password stored in protected application credential storage. Grant only `CREATE SESSION` and `EXECUTE ON APPS.XXAF_RENEWAL_API`. Give it no roles, table access, administration package, or APPS password. Locking that login immediately suspends new connections; disabling its scope row denies existing sessions too.
5. As APPS, insert a reviewed `XXAF_RNW_SCOPE` row mapping the authenticated database username to an active EBS user, Purchasing responsibility/application, operating unit and one approved source header. Use binds for this configuration. The package validates active responsibility membership and MO access each time. The first mapping uses the source agreement's existing buyer. Caller-supplied user/org values cannot expand this scope.
6. Run [04-verify.sql](sql/04-verify.sql) as APPS and review grants as the DBA. Check that both package bodies are VALID, the custom schema is registered, the data owner is locked, and the runtime has exactly the two grants above. Keep generated output private.
7. As the DBA, install [05-paf-wrappers.sql](sql/05-paf-wrappers.sql) into the runtime schema. PAF discovers routines owned by the connected account. These five functions bridge the noneditioned runtime account to the editioned APPS package through fixed PL/SQL blocks with bound arguments. They accept no SQL text or routine name. Do not enable editions or grant `CREATE PROCEDURE` to the runtime just to make discovery work. Verify the five base functions and no administrative review-package access. The next step extends the bounded runtime.

8. Apply [09-email-review.sql](sql/09-email-review.sql) in its DBA, APPS, then DBA phases. `AD_ZD_TABLE.UPGRADE` must run as APPS. This adds the scoped request table, `APPS.XXAF_RENEWAL_EMAIL` and two fixed discovery wrappers. The final runtime has seven VALID wrappers, `CREATE SESSION` and execution of its two bounded packages, with no roles or table privileges. Preserve existing staging/audits. Configure the native SMTP sender and verify confirmation plus its real send result. See [email review](EMAIL-REVIEW.md).

The document database has a separate installation, model and access scope. See [document retrieval](RETRIEVAL.md). Its MCP login cannot access the EBS database or approve imports.

Create separate backend identities/scope rows for separately authorized users. Dedicated PAF accounts that share a database login share this backend scope. This implementation uses `SESSION_USER` for a direct database connection; a future MCP or proxy service needs its own verified identity propagation.

## Tool calls and review

Only the seven functions below are intended as EBS tools, alongside native Email output and scoped retrieval. Do not expose a general SQL executor, APPS connection, or the operator package.

| Function | Inputs and behavior |
| --- | --- |
| `get_bpa_snapshot` | Source header ID. Returns the scoped header and at most 100 lines as JSON. |
| `stage_renewal` | Source header ID, ISO start/end dates, uplift percentage, evidence reference and idempotency key. Creates immutable header/line snapshots and returns a draft/hash plus old/new prices. |
| `validate_renewal` | Draft ID. Checks active goods/items/UOM, supplier/site/buyer, required fields, source freshness, date range and deterministic prices. |
| `request_review` / `RNW_REQUEST_EMAIL_REVIEW` | Draft ID, hash and recipient supplied by the user in the current conversation. Returns complete readable review text/code, with legacy HTML for compatibility, and creates a 30-minute request; does not send. |
| `confirm_review` / `RNW_CONFIRM_EMAIL_REVIEW` | Draft ID, hash, recipient, code and reason. Records demo review after code 6004; does not import. |
| `submit_reviewed_renewal` | Draft ID. Requires an exact-hash, unexpired, unused review. Returns the submitted concurrent request; it does not claim the BPA exists yet. |
| `get_renewal_status` | Draft ID. Returns request status, bounded interface errors and verified result identifiers. Later reads refresh the actual EBS authorization status after buyer actions. |

Phase one supports open, Approved, local BPAs in USD with active goods lines (`LINE_TYPE_ID=1`), 1–100 lines, a term of at most 366 inclusive calendar days starting today or later, and a uniform 0–10% uplift rounded to two decimals. A 12-month example may be 365 or 366 days. Other currencies, price precision, global BPAs, service lines, line selection, changed suppliers, clauses, attachments and in-place amendments require additional implementation and tests.

These functions return CLOB JSON. PAF's Oracle PL/SQL executor is bound to the restricted runtime datasource and an allowlist containing the seven `AF_EBS_RENEWAL.RNW_*` wrapper functions. For a database operator testing the underlying API, use an explicit function call such as:

```sql
select APPS.XXAF_RENEWAL_API.get_bpa_snapshot(:source_header_id) from dual;

select APPS.XXAF_RENEWAL_API.stage_renewal(
  :source_header_id, :start_date, :end_date, :uplift_pct,
  :evidence_ref, :idempotency_key) from dual;

select APPS.XXAF_RENEWAL_API.validate_renewal(:draft_id) from dual;
```

The demo flow requests email, waits for successful native sending, then accepts a later user code/draft/reason message through the bounded email-review functions. These prompt checks do not authenticate human identity.

As a separately controlled alternative, after inspecting complete changes, an operator runs the following as APPS using the exact returned hash. **Never grant this package to the agent, accept a model-supplied approval flag, or use this administrative connection as its datasource.** The operator gate records the database operator and reason. The email-demo path records a `DEMO_EMAIL` label, hash, expiry and reason; it does not establish authenticated reviewer entitlement.

```sql
begin
  APPS.XXAF_RENEWAL_ADMIN.approve_draft(
    :draft_id, :expected_draft_hash, :review_reason);
end;
/
commit;
```

Reviews expire after one hour and are consumed in the same transaction that submits the import. The tool can then call `submit_reviewed_renewal(:draft_id)` and poll `get_renewal_status(:draft_id)` at a bounded interval. SQL-callable tools use autonomous, explicit transactions; callers must not hold locks on the same custom records. EBS context is initialized and cleared on success and failure before the transaction finishes.

The import hardcodes `ORIGINAL`, `BLANKET`, `INCOMPLETE`, no item creation, no sourcing rules, no global agreement, no grouping, and no CLM. It obtains a new EBS document number. `REFERENCE_NUM` and comments identify the source, while custom staging/audit retain the full mapping. This reference does not claim EBS amendment/release lineage. It does not copy clauses or attachments.

EBS normalizes the header end date to 23:59:59; verification compares the selected calendar dates and each line's expiration date. The completion check validates the result's request/source marker, organization, type, line count, items, categories, UOM, prices and initial Incomplete status. Status recovery also supports a later purge of accepted interface rows through the unique request mapping; that fallback is not exercised by purging live interface data during a smoke test.

## Retry, errors and verification

Reuse the same idempotency key and payload after a client timeout. A different payload with that key is rejected. Once a request ID exists, repeated submission returns that request and never starts another import. Source header/line changes before submission invalidate the snapshot. Drafts are immutable; stage a new draft for changed proposals and obtain a new review.

`SUBMITTED` means accepted for processing; `IMPORTED` means result checks passed. A completed concurrent request alone is not sufficient. `IMPORT_FAILED` requires operator diagnosis using the request log and interface errors; automatic resubmission is deliberately unavailable. Keep audits and consumed reviews. Do not delete a BPA or reassign an old key to hide a failed attempt. Unexpected missing or ambiguous result data raises an explicit investigation error.

The [operator JDBC client](tools/RenewalSql.java) accepts a SQL filename as its only argument and reads the username, password and JDBC URL through stdin from protected storage. It requires AES256 Oracle native encryption and integrity. This EBS server currently negotiates SHA1 integrity; the client prefers SHA256 when available. This is native Oracle network encryption, not TLS. TLS and stronger server integrity configuration remain deployment prerequisites to review for a production rollout; no server authentication settings were changed for this increment. Keep this general SQL verification client out of the agent tool list.

In the EBS application, use the scoped buyer's **Purchasing** responsibility and open **Purchase Orders → Purchase Order Summary**. This launches Oracle Forms through a JNLP download and requires a configured Java Forms launcher. Query the returned new BPA number and type **Blanket Purchase Agreement**. Verify supplier/site, operating unit, header term, all three lines and prices, and **Incomplete** status. Do not submit approval merely to verify creation. Users with a different operating-unit responsibility may not see the agreement. The authenticated browser check confirmed login, responsibility access and the Forms launch. The buyer subsequently reported seeing three lines in the resulting BPA. Full buyer confirmation of the remaining terms is still required.

The imported BPA is local. **Buyer Work Center → Agreements** supports global agreements, as described in the [Oracle Purchasing User's Guide](https://docs.oracle.com/cd/E26401_01/doc.122/e48931/T446883T443956.htm); an empty search there does not establish that a local BPA is missing.

The stored PAF datasource connection passed with required Oracle native encryption. Its routine picker returns exactly seven renewal wrappers; the MCP source returns exactly three document tools. The agent's description includes sample questions, evidence limits, staging behavior, native email confirmation, code/reason review, separate submission and Forms inspection. Four notes explain the left-to-right canvas. The [portable graph](../../agents/oracle-ebs/contract-renewal/workflow.json) contains binding placeholders, not deployment endpoints or credentials; see [setup](README.md).

Live email-review checks passed 33 assertions covering hash/recipient binding, escaped content, wrong codes, blocking, expiry, retries and expired-review submission denial. They submitted no import; the technical approval was explicitly expired. Native confirmation, the initial SMTP rejection, successful retry and the later business approval/import were saved in chat. The text-preview update passed nine database checks and five saved-UI checks without sending or importing. Remaining validation includes source changes, import rejection and adversarial document instructions in isolated fixtures. The smoke tests establish one configured account's scope and expected failures, not comprehensive cross-user testing. Before wider deployment, validate each account's backend scope and a production identity-based review mechanism, and obtain full buyer confirmation of the imported terms in Forms.
