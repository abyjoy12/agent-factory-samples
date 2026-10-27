# Execution and Integration Model

OPAF 26.10.0.0.0 is the selected baseline, established by the supplied About screen. Use version-matched contracts for the actual deployment. The local older SDK archive and the current REST sample represent different integration contracts; the older archive does not make the instance-generated REST example obsolete.

## Runtime ownership

OPAF owns agent/workflow execution, model calls, tool selection and supported agent delegation. The companion owns business definitions, test sessions, cases, human decisions and business acceptance. A trusted integration adapter handles authentication, logical-to-runtime ID mapping, conversation correlation, response normalization and errors.

Build EBS Agent Blueprint Showcase as a new application with a fresh App ID and bind its interactions to OPAF. Preserve the existing Planning App and use its planning scenario as the sample business case. Existing deterministic database functions can be reused through restricted MCP wrappers; this iteration does not require new Select AI teams to orchestrate the agents. No existing Select AI feature is removed by this decision.

## Supported integration evidence

| Capability | Evidence and design implication |
| --- | --- |
| REST invocation | Oracle documents POST /agentFactory/v1/integrations/agents/{agent_id}/run for published custom workflows using an agent-specific bearer API key |
| Conversation continuity | The documented request can include roomId to continue an existing conversation |
| Execution identity | The documented key is agent-bound and executes as its creator; preserve end-user business authorization separately |
| Structured workflow data | Builder components support JSON and parsing/conversion; verify the external response envelope for the installed workflow |
| Python SDK | Oracle's 26.10 announcement introduces supported SDK invocation; select and test the package matched to this release |
| A2A | The 26.7 guide describes sending work, task-status retrieval, conversation continuation and cancellation; the 26.10 announcement adds expanded JSON/Markdown content and asynchronous task handling |
| Durable human checkpoint resume | The reviewed sources do not establish resumption of any arbitrary suspended workflow after approval; model the case continuation explicitly until verified |

Sources: [REST and conversation integration](https://docs.oracle.com/en/database/oracle/agent-factory/26.7/paias/agent-builder.html), [builder components](https://docs.oracle.com/en/database/oracle/agent-factory/26.7/paias/agent-builder-components.html), [A2A guide](https://docs.oracle.com/en/database/oracle/agent-factory/26.7/paias/a2a-agents.html), [26.10 announcement](https://blogs.oracle.com/database/announcing-private-agent-factory-26-10-featuring-deep-nl2sql).

These sources span releases: the 26.7 guide says the SDK is not supported, while the 26.10 announcement introduces it. Use the latter as release direction and verify detailed operations against the deployed SDK/API. A2A task continuation and a new message in an existing room are not equivalent to restoring a durable workflow checkpoint.

## Application integration adapter

The adapter accepts an authorized business operation, case context and selected workflow version. It resolves the deployed agent ID, invokes SDK/REST/A2A as appropriate, normalizes structured output and records run correlation. Keep case ID, task ID, workflow version, runtime execution/task ID and conversation room ID distinct.

Store credentials and deployment endpoints in private operational configuration. An API key, room ID or model argument does not prove the requesting user's business scope. Enforce trusted identity in the adapter and tool service. Validate output schemas before updating case or application state.

## Database and MCP services

Use logical profiles for EBS_READ, PLANNING_READ, AI_READ and STAGING_WRITE. The last profile invokes restricted local staging procedures rather than general EBS writes. Keep native connect/run-sql/run-sqlcl tools in a separate engineering/admin access profile; business agents receive named operations with typed contracts.

The gateway protocol and native tool inventories have been verified. The named business-tool registrations, database grants and trusted caller/session controls remain unvalidated. See [MCP guidance](../integrations/oracle-database-mcp/README.md).

Separate sessions by target, privilege profile and caller scope. Do not let concurrent requests switch a shared mutable connection between EBS and 26ai. Reads across databases do not imply a common snapshot or atomic distributed transaction. Preserve source keys, evidence timestamps and target revision, and disclose consistency limits.

## Staging boundary

The two initial agents end at local proposal/payload/audit staging. Require explicit staging intent, a current preview, stable request-key handling and committed readback. Report decision-only, failed and unknown outcomes distinctly. After uncertain persistence, reconcile before retrying.

Human approval is separate. READY or READY_FOR_IMPORT is local eligibility, not EBS execution. Supported concurrent programs, request sets, ISG, PL/SQL APIs, files and middleware remain customer integration options outside the delivered scope. Only independent transaction readback could later establish APPLIED; only business evidence could establish RESOLVED.
