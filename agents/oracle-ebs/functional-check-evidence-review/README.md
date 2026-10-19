# Functional Check Evidence Review — Oracle EBS

**Which EBS checks explain this run’s warnings, and what should the operator investigate?**

Find cataloged EBS functional checks, inspect their impact and guidance, and review progress, reports, and evidence from existing runs through six allowlisted control-package routines. Does not start or cancel runs or execute remediation.

## Status

Editor-owned draft; runtime not exercised. Source sharing, new-flow ownership, metadata and memory settings were read back; an official export was captured. No Fusion action or EBS diagnostic run was executed during migration. The destination must validate source authentication, backend compatibility and expected behavior before use. Shared control-source access succeeded through the permission-checked database-detail API. The current owner-filtered database selector omits this shared source; retain the saved binding, or create an editor-owned source on another instance.

## Capabilities

- Six explicitly allowlisted PL/SQL routines for catalog and existing-run evidence.
- Preserves pagination, run status, execution-window limitations and source guidance.

## Prerequisites

- PAF 26.7-compatible visual Agent Builder and a registered model.
- An existing EBS Sensor Control deployment with its catalog, run ledger and diagnostic package.

## Import and configure

1. Import the release .paf into an unpublished destination flow.
2. Provide the pre-existing PAF_DEMO.EBS_CHECK_API package and its control catalog. This sample does not install that custom backend. Use a control reader able to call the six documented routines; preserve the node routine allowlist and auto_commit=false.
3. Create or select the sources listed in assets/source-bindings.json; replace every environment-local node binding.
4. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. Disable Agent Memory and cross-thread sharing.
5. Check permissions and connectivity against the intended demo environment before publishing.

## Controls and limits

- Removed generic database tools and the REST run controller from this copy.
- Only six diagnostic routines are allowlisted; no run creation, cancellation or remediation tool is attached.
- The database account privileges remain the security boundary; a package-wide EXECUTE grant can expose more routines to other clients.

## Suggested prompts

- Show the available check families and explain what evidence I need to review an existing run.
- For run <run_id>, summarize recorded failures, warnings, execution time and incomplete evidence. Do not start a run.

## Artifacts

- [Official workflow export](workflow.json)
- [Source bindings](assets/source-bindings.json)
- [Agent instructions](assets/agent-instructions.md)
- [Consolidation and replication notes](../../../integrations/account-consolidation/)

The AI World lab model is `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible), already configured on the prepared PAF instance. Configure the same model name in each final lab instance; the archive excludes model definitions and credentials. Read the numbered workflow notes from left to right, and use the expand control beside Agent Description for the walkthrough and sample questions.
