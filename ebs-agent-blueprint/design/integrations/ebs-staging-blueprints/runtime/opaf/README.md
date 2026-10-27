# OPAF Runtime for the EBS Staging Agents

For this iteration, OPAF 26.10.0.0.0 owns the deployed agent instructions, conversation, workflow routing, model calls and MCP tool invocation. EBS Agent Blueprint Showcase is a new application that will host the demonstration user experience. The existing Planning App is the sample business case and is preserved. The agent definitions and business-tool contracts remain independent of the application.

```text
New EBS Agent Blueprint Showcase application
  -> Application bridge to the selected OPAF workflow
  -> OPAF agent and workflow
  -> Approved business tools through MCP
       -> EBS/MSC evidence reads
       -> SelectAIAJ local proposal, payload and audit staging
  -> OPAF response and verified staging receipt
  -> New showcase review and display experience
```

The application's trusted bridge supplies user and business-scope context and maintains correlation to the OPAF conversation. OPAF conversation IDs do not themselves authorize database access. MCP tools validate scope and perform deterministic operations. The model does not receive arbitrary SQL or connection-selection privileges.

## Implementation scope

Create one OPAF agent/workflow for Work Order Reschedule Staging and one for Purchase Order Change Staging. Each receives its four permitted MCP tools, the existing readable instructions and a model binding. Keep memory and cross-thread sharing off initially. The proposed design files describe intended behavior; they are not native exports or evidence that the workflows already exist in OPAF.

The existing Planning App remains a separate sample/reference. Build the new showcase application from the approved blueprint and wire its actions/chat to OPAF. Assign a fresh application ID rather than overwriting the planning deployment. Customer-specific identity propagation, selected workflow IDs, conversation handling and result rendering are implementation bindings, not core agent names.

SelectAIAJ remains a useful data-services and staging backend. Existing deterministic SQL/PLSQL, lookups, evidence contracts and audit objects may be reused through MCP after validation. This iteration does not require creating new Select AI teams to orchestrate these agents. Existing Select AI features are not removed or reconfigured by this design decision.

## Conversation and workflow sequence

1. Accept the user's question and trusted application context. Read-only requests follow only the evidence and preview path.
2. Resolve an authorized candidate and call the preview tool. Return exact before/after values, policy context, evidence age and limitations.
3. Wait for an explicit staging request for the displayed version. If source values or scope change, refresh the preview and obtain staging intent for the changed proposal.
4. Invoke the restricted staging tool with proposal reference, expected version and a stable request key managed by the trusted bridge/service.
5. Read back the receipt and show complete, decision-only, unknown or failed persistence accurately. Reconcile uncertain outcomes before retrying.
6. Stop at local staging. Separate human review may continue in the existing application. EBS integration is left to the customer.

## Deliverables and validation

- Two configured OPAF workflows and agents with their restricted tool bindings.
- Native workflow exports and compatible archive metadata captured after the actual build.
- Sanitized model/source binding instructions and a validation record identifying the OPAF runtime version.
- Verified showcase-to-OPAF correlation, trusted caller propagation and receipt rendering using the existing page structure.
- Acceptance cases for tool correctness, unauthorized scope, explicit staging intent, source changes, duplicate requests and uncertain commits.

The database gateway's generic SQL tools are verified as discoverable; the named business tools still need registration/wrapping and testing. An OPAF graph alone cannot replace the required business-tool implementation. Do not publish a runnable sample or .paf until its native workflow exists and its validation status is accurate.


## Broader architecture and runtime gates

See the [architecture overview](../../../../architecture/README.md) and [execution model](../../../../architecture/execution-model.md). The supplied About screen confirms the selected 26.10.0.0.0 release. Validate the matching SDK and response/task contracts before implementing continuation. roomId conversation reuse does not establish durable workflow checkpoint resume.

The [registry model](../../../../architecture/registry-model.md) places canonical tools in a shared repository and tasks within workflow steps. The current per-agent tool contract files are transitional design artifacts. OPAF builds the executable graph; the companion manages business specifications, acceptance and durable case/worklist state. Native Skill Markdown loading and arbitrary human pause/resume remain verification items.
