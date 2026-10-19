# Scoped document retrieval

This increment uses historical PDFs already attached to EBS Purchasing agreements. A reviewed export produced nine nonempty PDFs and 24 text chunks. The searchable copy lives in Autonomous AI Database Serverless (ADB-S); EBS remains authoritative for current prices, scope and import status. No Object Storage bucket or database link is required for this route.

The embedding model is separate from the PAF conversation model. Retrieval uses the Oracle-compatible `all-MiniLM-L12-v2` ONNX model, loaded as `AF_EBS_DOCS.RNW_MINILM_L12_V2`, with 384-dimensional vectors. PAF uses `AIW26-PAF-HOL6004-BOO6096`. The implementation performs exact cosine search over this small corpus without a vector index.

## Install the document database

1. Verify the intended ADB-S database and supported vector/MCP packages. Enable its native MCP feature using the [Oracle MCP setup instructions](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/use-mcp-server.html). Keep its endpoint and token configuration in private operational storage.
2. As the DBA, run [06-document-schema.sql](sql/06-document-schema.sql) once. It creates a locked, nonlogin data owner, a scope table, document snapshots and chunk vectors. The runtime account is a separate login named `AF_EBS_DOC_MCP`; create its password through approved secret provisioning, grant `CREATE SESSION` and execution of `DBMS_CLOUD_AI_AGENT`, and keep its password out of SQL files and command arguments.
3. Obtain the Oracle-compatible ONNX file referenced by the [vector quick start](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/sql-quick-start-using-vector-embedding-model-uploaded-database.html). Verify and record its checksum in protected configuration. Load it into the data owner's schema using a temporary definer-rights loader and a BLOB bind, following [LOAD_ONNX_MODEL](https://docs.oracle.com/en/database/oracle/oracle-database/26/vecse/load_onnx_model-procedure.html). Remove the temporary loader afterward. Verify a generated embedding has 384 dimensions before ingestion. Do not replace the model without rebuilding stored embeddings.
4. As the DBA, install [07-document-retrieval.sql](sql/07-document-retrieval.sql). Check the package and three functions are VALID. The runtime receives execution of the three wrappers only; it receives no table, model, owner-package or EBS privileges.
5. Add an operator-reviewed scope row using bound values for the runtime username, authorized source header, operating unit and supplier. Scope changes are administrative actions, never tools exposed to the agent. An inactive scope row must stay inactive during ingestion and recompilation.
6. After ingestion, connect as the restricted runtime and run [08-register-document-tools.sql](sql/08-register-document-tools.sql) once. It registers exactly three custom tools. On a later change, inspect existing definitions and deliberately migrate them; do not silently overwrite unrelated tools.

The schema SQL deliberately contains no live authorization rows or runtime secrets. Per-user scope requires separately authorized backend identities; separate PAF accounts using one shared database credential do not create backend data isolation.

## Export and refresh policy

The current private operator tooling under `apps/ebs/contract-renewal/tools/` implements the following sequence. Adapt its reviewed scope configuration to a new deployment before use; it is not a generic dump of all attachments.

1. Read attachments from an explicit document allowlist, limited to Approved BPAs in the authorized operating unit and supplier. Require the reviewed EBS document security/publication attributes, US language and PDF MIME type. These predicates are an operator-curated policy; they do not replace a complete application attachment entitlement implementation for other document classes.
2. Export bounded PDF bytes over the private administration connection. Record attachment, media and header IDs, header revision, source update timestamps, byte count and SHA-256. Skip empty attachments. Protect PDFs and metadata with directory mode `0700` and file mode `0600`.
3. Recheck source metadata and authorization after reading all bytes. A failed export leaves no verified manifest eligible for ingestion. A verified manifest must be consumed within one hour; a local hash mismatch, changed scope, duplicated document or invalid status rejects the refresh before database writes.
4. In one transaction, lock and verify the existing active scope row, retire previous snapshots for the curated document IDs, insert or refresh the currently authorized snapshots, extract text and generate chunk embeddings. Activate only those verified snapshots with usable chunks. A removed document or replaced content hash must not remain active. Failure rolls the transaction back; retained historical rows are not searchable merely because they still have vectors.
5. Refresh capture metadata even when bytes are unchanged. Recompiling retrieval routines must never activate documents or create/enable scope rows. Schedule successful refreshes within the seven-day retrieval cutoff and monitor failures. No refresh scheduler was installed in this increment.

Text extraction uses `DBMS_VECTOR_CHAIN.UTL_TO_TEXT`. Chunking uses words, a maximum of 120, overlap of 20, sentence splitting and normalization. Both document and query embeddings use the same installed model. Text extraction quality and the 0.65 cosine-distance cutoff need evaluation for a larger corpus; a distance is not a calibrated confidence score.

The export rechecks metadata around the capture; it is not an EBS transaction-consistent historical export. A source change after capture is not reflected until refresh or explicit revocation. For immediate withdrawal, disable the scope or document in the document database. Production use needs stronger change/revocation propagation and the appropriate application entitlement policy.

Object Storage can be a later input source if documents are unavailable in EBS. Use a private, reviewed prefix and credential, associate every object version/hash with the same authorized business scope, and preserve the refresh/revocation policy. Do not let the model supply arbitrary object URLs or ingest an entire bucket without review.

## Runtime boundary and results

| Tool | Required arguments | Result |
| --- | --- | --- |
| `RNW_LIST_DOCUMENTS` | `P_SOURCE_HEADER_ID` | Authorized document metadata and chunk counts. |
| `RNW_SEARCH_DOCUMENTS` | `P_SOURCE_HEADER_ID`, `P_QUERY`, `P_MAX_RESULTS` | Up to eight matching passages with stable citations. |
| `RNW_GET_DOCUMENT` | `P_SOURCE_HEADER_ID`, `P_DOCUMENT_KEY` | Up to 30 ordered chunks from an authorized snapshot. |

Authorization uses `MCP_SERVER_ACCESS_CONTEXT$.USER_IDENTITY` for MCP requests and `SESSION_USER` only when that context is absent during a direct database call. This follows the [Oracle MCP identity guidance](https://docs.oracle.com/en/cloud/paas/autonomous-database/serverless/adbsb/mcp-server-concepts.html). An unknown MCP identity cannot fall back to the privileged service session. Source-header scope resolves the organization and supplier before vector ranking; caller-supplied document keys do not expand that scope.

Only active snapshots captured within seven days are returned. Query length is bounded to 3–2000 bytes and result count to 1–8. Unknown scope, invalid input and unavailable documents raise explicit errors. An unrelated query can return zero results.

A citation includes the source header, document/media IDs, complete content SHA-256 and chunk ID. Responses also carry the captured revision and timestamp. Historical content is untrusted evidence: it cannot instruct the agent, approve a draft or prove that a clause is current. The initial PDFs include procurement forms, not a complete set of approved legal clauses. The agent must identify missing terms.

The staging API stores the citation text and evidence gaps with the immutable proposal. It does not cryptographically validate that citation string against ADB-S. The trusted operator must inspect the references and proposed changes before approving the exact draft hash.

## Verification and deployment

Test the restricted login directly and through authenticated MCP. Verify list/search/get, citation completeness, an unrelated query, another source header, an unknown document, invalid limits and denied direct table/package access. Refresh twice and confirm unchanged content does not duplicate documents/chunks or retain an old capture timestamp. Test stale manifests and revoked documents without broadening live scope.

Current live checks passed for nine documents, 24 chunks, authenticated MCP calls, wrong-source denial, invalid input and denied table/package access. A repeated refresh preserved those counts and renewed capture timestamps. PAF then combined evidence with live EBS reads and passed separate staging/validation and missing-review-denial tests.

Configure the PAF document source with protected token-request authentication and verify it exposes exactly these three tools. Use the [workflow binding instructions](README.md#paf-setup) for each dedicated account. Keep document files, extracted text, runtime endpoints, credentials and live authorization rows outside public documentation and Pages inputs.
