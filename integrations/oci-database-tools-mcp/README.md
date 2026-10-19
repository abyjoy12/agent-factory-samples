# Optional OCI Database Tools managed MCP integration

**Status: prepared, blocked, not deployed — 2026-10-17.** This is an extension blueprint, not an eleventh downloadable or working agent. The ten published business demos use direct Builder database/file integrations.

## Fresh endpoint check — 2026-10-17

The existing managed server `PAF` is still ACTIVE and targets its original, different database connection. A fresh unauthenticated JSON-RPC `initialize` request to its invocation endpoint returned HTTP **401**, with a bearer challenge containing protected-resource metadata and the server-specific scope. This confirms a reachable authenticated endpoint; it does **not** establish authenticated initialization, tool discovery, SQL execution, or PAF integration.

No usable OAuth/PAT credential for this invocation was supplied to this check, and no authentication changes were made to the shared server or identity domain. The earlier dedicated EBS server creation attempts below were not repeated or reported as successful. The new [direct receivables flow](../../agents/oracle-ebs/receivables-portfolio-review/) exercises the same bounded SQL without MCP; it does not validate the MCP transport. See also the separate [ORDS MCP probe](../ords-mcp/).

## Business demonstration

An EBS collections lead asks: “Summarize positive remaining receivables by organization and currency.” A managed MCP tool executes [receivables-summary.sql](receivables-summary.sql) and the PAF Agent explains the returned groups. The SQL is fixed, SELECT-only, limited to 15 groups, and runs under the existing EBS Finance integration reader. It returns payment-schedule counts, amounts and due-date ranges. It does not send collection notices, return customer contact details, net different currencies, or forecast cash.

The SQL returned 15 groups when checked directly against the demo database. MCP server creation, authentication, tool invocation and PAF-to-MCP execution have **not** passed validation.

## Existing resources inspected

- Existing OCI Database Tools connections already cover the demo application databases, including a dedicated EBS Finance reader.
- An active managed MCP server named `PAF` already exists. It points at a different Autonomous Database connection. It was left unchanged.
- The installed OCI CLI 3.76.0 did not contain the managed MCP commands. An isolated OCI Python SDK 2.188.0 environment was used to inspect resources and attempt creation; the system CLI was not replaced.

## Blockers encountered

1. Creating a dedicated `PAF EBS Finance Demo` managed MCP server against the existing identity domain returned `400 InvalidParameter`: the identity-domain issuer must match its domain URL. The existing SSO domain uses a legacy shared issuer. Its shared SSO configuration was not changed.
2. Creating an isolated identity domain returned `404 NotAuthorizedOrNotFound`, including in the tenancy home region. No isolated domain was created. This is an OCI service authorization/visibility response, not a Codex approval rejection.

No new managed MCP server, custom toolset, replacement identity domain or Vault secret was created by these attempts. A domain administrator must supply a compatible isolated domain, or authorize and assess the impact of changing the existing shared domain. Then server creation can proceed.

## Configuration to complete

1. Confirm that the target database, region and connection satisfy the current [managed MCP requirements](https://docs.oracle.com/en-us/iaas/database-tools/doc/overview-mcp-server.html). Oracle documents managed access to Oracle Database 19c and 26ai; the tested EBS source is 19c.
2. Obtain a compatible identity domain with its issuer equal to the domain URL. Follow [server creation prerequisites](https://docs.oracle.com/en-us/iaas/database-tools/doc/creating-mcp-server.html). Do not repoint the existing `PAF` server.
3. Review network reachability, the existing read-only connection and its Vault-backed credentials. Give the server resource principal only the documented access needed for that connection, its secret, network endpoint and a dedicated result bucket. The current tenancy has not been verified against every such IAM requirement.
4. Fill the placeholders in [server.example.json](server.example.json). With an OCI CLI version exposing managed MCP commands, generate the current input schema before applying the example:

   ```bash
   oci dbtools mcp-server create-mcp-server-default --generate-full-command-json-input
   # After reviewing the version-specific schema and filling the placeholders:
   oci dbtools mcp-server create-mcp-server-default --from-json file://server.example.json
   ```

   The sample shows the intended service fields; reconcile it with the installed CLI schema. Wait for ACTIVE and record the new server OCID and endpoint privately. See the [OCI CLI command reference](https://docs.oracle.com/en-us/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/dbtools/mcp-server/create-mcp-server-default.html).
5. Create the custom SQL toolset using [toolset.example.json](toolset.example.json), the new server OCID and the supplied query. Confirm the supported toolset version and role names for that deployment. Follow [toolset documentation](https://docs.oracle.com/en-us/iaas/database-tools/doc/database-tools-mcp-toolsets.html). Do not enable general-purpose SQL or DML tools for this demo.
6. Register a client and grant the permitted user role according to [client registration](https://docs.oracle.com/en-us/iaas/database-tools/doc/registering-mcp-client.html). Keep any PAT/client secrets in the supported secret store and PAF connection settings, never in Git. If a new secret is created in the local Agent-Factory environment, use its required Vault/secret-register synchronization workflow.
7. Register the endpoint as a PAF MCP source with the supported Streamable HTTP transport and authentication. Build `Chat input → Agent → Chat output`; connect an **MCP server** component to Agent tools and allow only `ebs_receivables_summary`. A **Deterministic MCP tool** component is an alternative when the same report must execute on every run.
8. Disable Agent Memory for the evidence-only version. Run the two prompts below, verify the executed tool, compare organization/currency/counts/dates to the fixed query, and check that unavailable-tool errors are disclosed. Export a `.paf` only after this end-to-end run succeeds.

## Suggested prompts and instructions

- “Summarize the positive remaining receivables by organization and currency using the MCP tool.”
- “Can we treat those totals as expected cash this week? Explain the missing evidence.”

Require the Agent to invoke the tool before answering; preserve organization, currency, raw status and due-date range; call the records payment schedules; disclose failed/empty results; and explain why positive balances are not automatically overdue or a cash forecast. Suggested actions are drafts for a collections owner. No messages or application writes are authorized by this workflow.

## Slide outline

1. Business question: a bounded receivables review.
2. Architecture: PAF MCP component → managed Database Tools server → fixed SQL tool → existing read-only EBS connection.
3. Control: explicit tool allowlist, fixed SELECT, organization/currency grain, private authentication.
4. Current status: SQL ready; identity prerequisite blocks managed-server deployment. Present a live tool run only after completing the steps above.
