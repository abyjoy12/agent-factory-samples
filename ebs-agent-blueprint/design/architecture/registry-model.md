# Registry Model

The registry represents business capabilities independently of their deployment. Cards are searchable views of versioned records and relationships; a card is not the underlying executable definition.

## Registered entities

| Entity | Content | Principal relationships |
| --- | --- | --- |
| Data contract | Meaning, keys, grain, units, freshness, schema and evidence rules | Consumed/produced by tools and evaluation cases |
| Tool | Operation, typed inputs/outputs, effects, errors, permissions and validation | References contracts; has deployment bindings; attached to agents |
| MCP server | Logical service, transport/authentication binding and discovery state | Advertises deployed tools |
| Agent | Purpose, standing instructions, selected skills and permitted tool references | Assigned tasks; deployed in OPAF |
| Skill | Reusable procedural guidance and supporting references | Included in selected agents or task contexts |
| Task | Assignment, inputs, expected outcome and completion criteria | Owned or referenced by a workflow step; assigned to an agent |
| Workflow | Steps, task assignments, routing, shared state and human handoffs | Deployed as executable OPAF workflow or coordinated operations |
| Evaluation case | Scenario, fixed evidence baseline, reference outcomes and checks | Exercises defined workflow/agent/tool versions |
| Autonomous process | KPI, detection policy, work assignment and resolution policy | Triggers workflows and creates/updates cases |
| Deployment binding | Logical version to physical implementation/runtime mapping | Links definitions to MCP operations, OPAF IDs and app entry points |

Record stable IDs, versions, owner, description, approval state, dependencies and validation evidence for every releasable definition. Track definition approval, deployment existence and evaluation acceptance separately. An approved design is not automatically deployed or business-validated.

## Tool repository and attachments

Canonical tools belong in a shared repository, not as copied implementations inside every agent. A logical tool can have different demo/customer bindings while preserving its business contract. Tool identity and version belong to the registry; the MCP tool name belongs to a deployment and must be mapped explicitly. MCP does not require a built-in business versioning scheme, so the registry must record contract versions and discovered-schema fingerprints itself.

An attachment references tool ID/version, permitted use and applicable restrictions. It can narrow row limits or allowed operations. Server-side enforcement remains authoritative; neither a Markdown instruction nor a registry attachment grants database access. Caller authorization must be checked for every operation.

For example, a buyer assistant and a shortage-resolution specialist can both reference preview_purchase_order_change. A read-only investigative task can omit the staging capability even if the agent is eligible to use it in another task.

## MCP discovery and business discovery

MCP servers advertise tool definitions, including names, descriptions and input schemas; output schemas and behavior annotations may also be present. Clients discover with tools/list and invoke with tools/call. See the [MCP specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

The workbench can inventory tools before a designer opens the OPAF canvas. Tool cards add business purpose, ownership, examples, effects, approval and evaluation status to the discovered technical information. Discovery never invokes the operation and does not approve it for use. A changed server schema should produce a reviewable drift finding rather than silently rewriting an approved contract.

The existing gateways advertise general SQLcl operations. Named business tools require a restricted implementation or facade; a database procedure does not automatically become a discoverable MCP tool. OPAF's MCP node has an Allowed tools selection in the supplied UI. That is a deployment attachment mechanism, not the independent business registry.

## Agents and A2A cards

An Agent registry card describes the reusable specialist. An A2A Agent Card describes a deployed agent's protocol identity, advertised skills, endpoint and authentication. Link the two, but retain their different meanings. A2A exposure and discoverability do not establish business approval or version compatibility.

OPAF's supplied A2A screen manages which published agents can be called externally and registered external agents. It does not by itself establish the entire business registry proposed here. Verify available product functionality before adding custom screens.

## Instructions and skills

Use Markdown for human-readable instructions. Standing agent instructions establish role and enduring boundaries. Task instructions express the current workflow assignment. Skills contain reusable procedures, references and examples; they may declare required tool capabilities without granting them.

Do not assume OPAF natively imports SKILL.md packages. Verify the installed release's mechanism. A build process may instead assemble selected skill content into agent instructions or task context, preserving source versions and content hashes. A2A-advertised skills are protocol capabilities and are not automatically equivalent to Markdown skill packages.

## Task placement

Tasks are relevant within workflows. Keep the task's instruction text in Markdown, referenced by a structured step definition. The step defines input mappings, assigned agent/version, expected output, completion criteria, timeout, routing and narrower permissions. Reusable task templates can be cataloged, but a standalone Select AI task object is not required for OPAF execution.

The existing Select AI implementation associates tool lists and instructions with tasks and binds agent/task pairs in teams. Preserve those useful semantics through the new model rather than assuming that moving instruction text alone migrates the executable team.
