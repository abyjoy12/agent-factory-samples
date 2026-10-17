# ORDS MCP integration — current probe and setup

**Status: runtime inspected and endpoint probed; not configured and not validated end to end — 2026-10-17.**

## Actual results

The existing customer-managed ORDS runtime reports **26.3.0.r2721811**. Requests to its `/ords/mcp` and `/mcp` endpoints, plus `/ords/.well-known/oauth-protected-resource/mcp`, returned HTTP **404**. The inspected configuration has no `feature.mcp`, MCP JWT profile, or dedicated MCP database pools. Its existing default pool uses the ORDS runtime identity for another demo database, not any PSFT/EBS module reader.

No authenticated `initialize`, `tools/list`, `database_list`, or SQL/custom-tool invocation succeeded. No PAF MCP source was registered. The module workflows in this repository use direct database integrations instead. The existing ORDS service, authentication, users and pools were not modified.

## Configuration path

Oracle documents ORDS MCP for ORDS 26.2 and later, with MCP disabled by default. The [ORDS 26.3 MCP guide](https://docs.oracle.com/en/database/oracle/oracle-rest-data-services/26.3/orddg/using-ords-model-context-protocol-mcp.html) describes JWT bearer authentication, protected-resource discovery, Streamable HTTP, and dedicated direct-to-database-user pools. A normal REST-enabled schema or a SQLcl stdio server is not proof that ORDS MCP is configured.

1. Use a dedicated ORDS MCP runtime/configuration so existing APEX and REST services can be retained.
2. Configure an approved JWT issuer, audience, JWKS URL and authorization-server discovery. Issue a token with the documented ORDS MCP access scope and the correct per-pool scope or role. Store tokens and client credentials privately.
3. Enable `feature.mcp` using the version-specific ORDS CLI. Configure separate named pools for the relevant `PAF_AGENT_RO`, `AF_EBS_FIN_RO`, `AF_EBS_SCM_RO` or `AF_EBS_OPS_RO` database users; retain the current database privileges. MCP pools connect directly as readers, not through `ORDS_PUBLIC_USER` or a shared elevated runtime account. Set each pool's MCP scope or role and secure `db.password` through the supported secret command.
4. With authentication, run `initialize`, `tools/list`, `database_list`, then inspect the intended schema. Compare a bounded fixed report with the corresponding sample's `assets/evidence.sql`. Do not execute an unreviewed SQL statement generated from a business prompt.
5. For a PAF demo, prefer an administrator-defined custom report tool with an explicit allowlist. `sql_run` can modify database state when its database user permits it; the name MCP does not make it read-only. Any server account must retain only the necessary reader access.
6. Register the MCP endpoint privately in PAF and use its MCP component. A successful direct SQL report or unauthenticated challenge is not an end-to-end PAF-to-MCP result. Document actual tool execution before claiming a working MCP sample.

## Existing report inputs

Reuse the fixed query assets for [EBS receivables](../../agents/oracle-ebs/receivables-portfolio-review/assets/evidence.sql), [EBS procurement](../../agents/oracle-ebs/purchase-receipt-review/assets/evidence.sql), and the PeopleSoft module folders. Their organization, currency, date, lifecycle and grain restrictions still apply when the transport changes to MCP. Exact custom-tool definition schemas and authentication are deployment-specific and must be checked against the installed ORDS version.
