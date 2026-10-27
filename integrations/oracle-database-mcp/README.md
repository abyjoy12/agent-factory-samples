# Oracle Database MCP for EBS Agents

Use MCP as the common tool interface for EBS evidence and local draft staging. The evidence can come directly from authorized EBS or planning-system objects; copying those objects into a 26ai database is not an inherent requirement of an EBS agent. A separate staging store remains necessary when an agent creates a reviewable proposal.

The project chat Create OCI HTTPS load balancer identifies two existing gateway services and their trusted hostname routes. Fresh checks through those routes passed normal TLS validation, MCP initialization and paginated tool discovery. The primary SQLcl gateway is routed through public port 443 to backend 8093; the separate NEWEBS gateway uses public port 8443 to backend 8094 according to the project configuration. Deployment addresses remain private. See [server inventory](server-inventory.json).

Both services report gateway version 4.0.7 and advertise list-connections, connect, disconnect, run-sqlcl and run-sql. These are actual discovered native tools; the [schemas](discovered-native-tools.json) are included. No database connection, business query or staging write was executed during discovery. Gateway version does not establish the underlying SQLcl or database version.

## Source data and staging are different decisions

| Data or capability | Recommended placement | Meaning |
| --- | --- | --- |
| ASCP planning evidence | Authorized MSC objects in the planning instance, or an approved read copy | A planning snapshot with its own plan and collection age |
| Operational work orders and purchase orders | Authorized EBS views or fixed queries over the relevant application objects | Transactional evidence with EBS identity, status and revision semantics |
| Proposal, payload and audit records | Customer-selected staging store; existing 26ai staging can be retained | Review material created by the agent, separate from source business transactions |
| Select AI, ontology, vector retrieval or evaluations | 26ai where those capabilities are needed and available | Optional agent capabilities, not a prerequisite for querying EBS through MCP |

The existing 26ai copies supported bounded planning queries, local deterministic functions, semantic grounding and reproducible demonstrations. Local artifacts do not establish the original motivation for every copied table. Keep useful copies until replacement source contracts are validated; this design does not migrate or remove data.

Reading MSC objects at their origin avoids an additional replicated copy but does not make a historical plan current. MSC can be in a separate planning database from transactional EBS. APPS commonly provides access paths such as synonyms and views; access through APPS object names does not require using the broad APPS application account as the agent login. Verify object ownership, editioning, grants and supported access in the actual destination.

## Recommended architecture

```text
Any agent runtime or host application
  -> Authorized business-tool MCP interface
       -> EBS_READ connection: bounded EBS operational evidence
       -> PLANNING_READ connection: bounded MSC planning evidence
       -> AI_READ connection: optional 26ai semantics and retrieval
       -> STAGING_WRITE connection: restricted local draft procedures

Separate customer integration, if implemented later
  -> Revalidate, execute and reconcile EBS changes
```

One logical business-tool server can route all four capabilities, while each agent sees only its own permitted tools. Connection aliases are operator-controlled bindings. The model does not choose arbitrary database connections, SQL text, schemas or network destinations.

If the existing server supports custom tool registration and per-tool routing, register the business tools there. If it exposes only generic SQLcl tools, retain it as an internal database adapter and place a business-tool facade in front. A SQLcl MCP transport does not automatically turn stored procedures into individually discoverable named business tools. Exposing all business capabilities through one interface does not require exposing every generic database tool to every agent.

## What the reviewed implementation establishes

Workspace source outside this sample repository contains a SQLcl MCP client using SSE and a separate contract-only facade. The facade registers list_ebs_query_contracts, discover_ebs_metadata and run_ebs_contract. Its three fixed query contracts cover supplier open deliveries, supplier delay impact and top open work orders. These are source-reviewed capabilities, not newly verified capabilities of the reported port 8093 deployment.

The source facade uses the generic connect and run-sql tools internally and does not expose them to its agent clients. It is a separate component from the two gateways just discovered. Its source default port is 8081; the older workspace upstream setting uses port 8080 and is not the authoritative current gateway route.

An initial probe of an IP-address HTTPS route failed certificate verification. The project chat supplied the correct trusted hostname routes; fresh TLS and protocol checks through them succeeded without disabling certificate verification. The historical failure is retained in the inventory as superseded diagnostic evidence, not a current blocker.

The reviewed source facade is EBS-focused and read-only. It has not been shown to route to 26ai, expose the new staging tools, carry a trusted end-user context or provide per-user row authorization. Reusing its pattern requires extending and validating those functions. It is not delivered as executable code in this documentation package.

## Tool exposure

The proposed [tool catalog](tool-catalog.json) maps business operations to connection roles. The two staging agents retain their [application-neutral contracts](../ebs-staging-blueprints/README.md).

| Agent-facing tools | Route | Effect |
| --- | --- | --- |
| list_work_order_reschedule_candidates | PLANNING_READ, with optional EBS_READ enrichment | Read only |
| preview_work_order_reschedule | PLANNING_READ/EBS_READ plus proposal consistency service | Read only in the business systems |
| stage_work_order_reschedule | STAGING_WRITE | Local staging only |
| list_purchase_order_change_candidates | PLANNING_READ or EBS_READ according to the use case | Read only |
| preview_purchase_order_change | EBS_READ and optional PLANNING_READ plus proposal consistency service | Read only in the business systems |
| stage_purchase_order_change | STAGING_WRITE | Local staging only |
| get_staging_receipt | Restricted read on the staging store | Read only |

Preview consistency state may be held by the adapter; it must not change EBS transactions. Capturing a preview token is distinct from staging a user proposal. The staging calls require explicit staging intent and the reviewed proposal version.

Raw list-connections, connect, run-sql, run-sqlcl and schema discovery belong to a separately authorized engineering/admin profile when needed. Production business agents receive the business-tool allowlist. Database command restrictions do not substitute for database grants, end-user authorization or transaction controls. SQLcl's documented tools can execute SQL and PL/SQL, so a generic execution tool is broader than a named read-only query contract. [Oracle SQLcl tool documentation](https://docs.oracle.com/en/database/oracle/sql-developer-command-line/26.3/sqcug/sqlcl-mcp-server-tools.html).

## Connection and session controls

Keep EBS_READ, PLANNING_READ, AI_READ and STAGING_WRITE separate logical profiles even if some initially share a database. Map roles to dedicated least-privilege accounts or approved procedures. Use database-enforced row policies or equivalent validated service controls, with trusted caller identity. An EBS login context is not automatically reproduced by a shared SQLcl connection, and an extracted copy does not inherit EBS authorization.

Do not reuse a single mutable SQLcl session across concurrent requests that switch databases or caller contexts. Isolate sessions by target, privilege profile and authenticated scope, or serialize access within a proven routing boundary. Reset session state before reuse. The reviewed EBS runner caches a client and a connected flag; it should not be treated as an already validated multi-database router.

Each staging transaction belongs to one staging database session. Reading EBS and writing a draft to 26ai is not an atomic distributed transaction and does not guarantee a common snapshot across databases. Preserve source keys, source timestamps, target revisions and consistency limitations. Revalidate changed evidence and reconcile uncertain commit outcomes before retrying. Do not apply a generic read retry loop to staging writes without idempotency and reconciliation.

## Evidence and freshness

Map origin objects to SourceContext and BusinessObjectReference rather than changing table names inside the model prompt. Keep source instance, plan, organization, item and typed order identifiers together. Do not equate an MSC planning transaction ID with an EBS WIP job ID or PO shipment ID. Complete-key joins, exception-type semantics, lookup meanings and quantity/date interpretations must be validated in the origin adapter.

Return source as-of, collection/extraction time where available, query time, provider identity, record grain, units, bounded counts/truncation, rule version and limitations. A recent query time is not the source business as-of time. In particular, the existing contract runner labels execution time as source_as_of; a production adapter must separate those meanings before claiming data freshness.

MCP is a protocol boundary, not a cross-database join engine. A combined answer needs deterministic joins or a controlled multi-step query with validated keys and disclosed consistency. Choose direct EBS reads only after reviewing workload, query plans, timeouts and required freshness; a protected read copy may remain the appropriate option.

## Operator verification

Follow the [verification runbook](VERIFICATION.md) to confirm database identities, privileges and caller scope before binding agents. Keep runtime addresses and credentials in private operational configuration outside publication inputs. This repository intentionally has no deployment URL, hostname, database connect string or token.

The [binding template](connection-profiles.example.json) contains aliases and null private bindings. The [staging profile](profiles/staging-agents.json) maps the existing generic contracts to a proposed MCP route without making MCP mandatory for all hosts.

No server, listener, privilege, database object or runtime connection was changed by this documentation work. No business query or staging write was executed by the probes.

## Selected OPAF implementation

For this iteration, OPAF contains the two agents and their workflows. EBS Agent Blueprint Showcase will be the new demo interface, with the Planning App retained as the sample business case, while EBS/MSC supply evidence and SelectAIAJ initially stores staged proposals, payloads and audit records. MCP is the tool interface, not the agent orchestrator. See the [OPAF runtime profile](../ebs-staging-blueprints/runtime/opaf/README.md). Native OPAF graphs and business-tool wrappers still require implementation and validation.

## Shared registry and OPAF baseline

The [architecture](../../architecture/README.md) specifies OPAF 26.10.0.0.0 and a shared tool registry. MCP discovery provides technical inventory; business-tool cards add purpose, contract version, permissions, bindings and validation. The companion can discover tools before opening the builder canvas. Discovery does not approve or execute them. Database gateway tools and proposed named business tools remain distinct.
