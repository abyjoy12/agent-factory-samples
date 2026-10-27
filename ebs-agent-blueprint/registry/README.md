# Registry implementation starting point

The [tool index](tool-index.json) lists seven independent logical capabilities and points to the reviewed contracts. The shared receipt tool has two source references; keep its schema consistent until canonical contracts are migrated deliberately. The [agent index](agent-index.json) attaches capabilities by reference. These indexes are package navigation and design inputs, not database tables or deployed MCP registrations.

Implement the full [registry model](../design/architecture/registry-model.md) in the Business Agent Workbench. Add separately versioned MCP bindings, skills, workflow tasks, evaluation cases and deployment records. An MCP server card describes a deployed service and its discovered inventory; a tool card describes a business capability. An A2A card describes an exposed runtime agent, not every reusable agent definition.

Maintain authoring system, logical version, content hash, runtime IDs, schema fingerprints and reconciliation status. Detect drift rather than silently overwriting approved definitions. Agent instructions and Markdown skills cannot grant permissions.
