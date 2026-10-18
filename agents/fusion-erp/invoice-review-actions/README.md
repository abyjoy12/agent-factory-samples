# Invoice Review and Actions — Fusion ERP

**Which supplier invoice needs attention, and what exact change should I approve?**

Review supplier invoices and prepare or execute explicitly requested invoice creation, cancellation, or line cancellation through the configured Fusion REST sources. Shows the exact target and proposed values before requesting confirmation. Draft: source authentication and action behavior require target-environment validation.

## Status

Editor-owned draft using AIW26-PAF-HOL6004-BOO6096. The agent requested confirmation of a unique USD 0.02 invoice proposal. After confirmation, creation reported **HTTP 403 Forbidden**; independent Fusion lookups found no matching invoice before or after the attempt. Invoice and line cancellation remain untested because the isolated fixture could not be created. Review invoice-write permissions and business-unit access before continuing. See the [validation record](assets/validation.md) for evidence and limits. The workflow, sources, publication and memory settings were unchanged.

## Capabilities

- Invoice reads, creation, cancellation and line cancellation through separate read/action REST sources.
- Exact-target confirmation, no automatic retry of ambiguous writes, and API-result-based outcome reporting.

## Prerequisites

- PAF 26.7-compatible visual Agent Builder and a registered model.
- Confirmed Fusion demo endpoint and a suitably scoped integration account.

## Import and configure

1. Import the release .paf into an unpublished destination flow.
2. Import assets/invoice-read-openapi.json and assets/invoice-actions-openapi.json as separate REST sources. Replace the example server URL with your confirmed Fusion endpoint and configure authentication in PAF. These reconstructed contracts require target-release validation.
3. Create or select the sources listed in assets/source-bindings.json; replace every environment-local node binding.
4. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. Disable Agent Memory and cross-thread sharing.
5. Check permissions and connectivity against the intended demo environment before publishing.

## Controls and limits

- The flow can change Fusion invoices. It is an unpublished draft; no transaction was executed during migration.
- Conversational confirmation is an instruction, not a server-enforced approval mechanism. Restrict integration-account permissions and add an external approval gateway before unattended use.
- Do not retry an ambiguous write automatically. Do not claim payment, posting or approval capabilities.

## Suggested prompts

- List up to five supplier invoices and explain which fields need review. Do not change anything.
- Prepare the exact proposal for an invoice change I specify. Show the target and required fields; do not execute it.

## Artifacts

- [Official workflow export](workflow.json)
- [Source bindings](assets/source-bindings.json)
- [Agent instructions](assets/agent-instructions.md)
- [Consolidation and replication notes](../../../integrations/account-consolidation/)
- [Invoice read contract](assets/invoice-read-openapi.json)
- [Invoice action contract](assets/invoice-actions-openapi.json)

The AI World lab model is `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible), already configured on `build.oracleagentfactory.com`. Configure the same model name in each final lab instance; the archive excludes model definitions and credentials. Read the numbered workflow notes from left to right, and use the expand control beside Agent Description for the walkthrough and sample questions.
