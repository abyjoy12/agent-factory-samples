# Verify the Oracle Database MCP Deployment

This runbook inventories an existing server. It does not authorize installing a new service, expanding privileges, exposing a listener or executing business changes.

## Identify the endpoint

Use the private trusted hostname routes documented in the project chat Create OCI HTTPS load balancer. Fresh normal-TLS and MCP discovery checks passed for the primary gateway on public 443 and the NEWEBS gateway on public 8443. The project configuration maps these to backend 8093 and 8094 respectively. Record endpoint values in private operational configuration, not in publication inputs.

Do not replace the trusted hostname with an IP address: the earlier IP-route probe encountered an untrusted self-signed certificate. That probe does not describe the now-verified hostname route. Record the service owner, gateway version, underlying SQLcl version and authentication model separately.

Verify TLS and authentication using the deployment's approved configuration. Do not copy credentials or deployment addresses into README files, catalog JSON, public traces or command examples. Failure to connect must be reported as unverified, without claiming the server is missing or changing configuration to make a probe work.

## Discover without changing data

1. Initialize an MCP session with bounded timeouts and record sanitized server name/version and protocol capabilities.
2. Enumerate tools with tools/list, following pagination. Store tool names, input/output schemas, descriptions and declared effects. Do not treat a readOnlyHint as proof of actual read-only enforcement.
3. Compare generic SQLcl tools with business-tool registrations. Mark the proposed staging tools unavailable until they are actually registered and tested.
4. Under operator-approved discovery, inspect named connection aliases and privileges. Record only logical role mappings in the repository; exclude connection strings and secrets.
5. With a dedicated authorized session, run a bounded read-only identity check per target to confirm database/service identity and connected schema. Verify object existence, SELECT/EXECUTE grants and permitted business scope. Do not assume connection names prove their targets.
6. Confirm whether MSC planning objects and EBS transactional objects reside on the same target or different databases. Independently confirm 26ai availability and any required feature/version.

## Validate business contracts

For each EBS read, verify complete keys, code mappings, row grain, source age, result limits, query cost and row-level authorization. Compare the result to a business-reviewed reference. Return EMPTY, FAILED, STALE, PARTIAL and UNAUTHORIZED distinctly where applicable.

For local staging, use an approved test fixture and explicit user staging intent. Check proposal version, replay behavior, concurrent duplicate protection, transaction commit/readback, payload linkage and audit evidence. Test uncertain commit reconciliation. Keep these tests separate from the read-only inventory exercise.

Use concurrent sessions against different target roles and different callers to prove that connection selection, authorization context and results cannot leak across requests. Validate timeout behavior and resource cleanup. Do not claim multi-database routing from one successful connection.

## Record the result

Update server-inventory.json with the actual verification status and sanitized evidence. Update tool-catalog.json registration and validation status independently for each business tool. Keep source-reviewed implementation facts separate from discovered runtime behavior and business acceptance.

A successful MCP initialization establishes protocol reachability only. It does not establish database access, correct grants, business accuracy or safe staging. Keep downstream EBS execution outside these staging-agent acceptance tests.
