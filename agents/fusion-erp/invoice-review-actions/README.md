# Invoice Review and Actions — Fusion ERP

**Which supplier invoice needs attention, and what exact change should I approve?**

Review supplier invoices and prepare or execute explicitly confirmed creation, line cancellation or whole-invoice cancellation. Shows exact targets and proposed values, then verifies outcomes through invoice and line reads. Unpublished draft; validate destination permissions and runtime support.

## Status

Editor-owned Build draft using **AIW26-PAF-HOL6004-BOO6096**. Creation, line cancellation and whole-invoice cancellation passed with separate Fusion readback. The new USD 0.02 fixture is canceled at zero amount. Layout, description, publication and memory settings were checked again. See the [validation record](assets/validation.md) for evidence and limits.

Factory required a [POST cancellation guard fix](../../../integrations/fusion-apps/runtime/). Verify this support on each destination before testing actions. No final-instance rollout has started.

## Capabilities

- Invoice reads, creation, cancellation and line cancellation through separate read/action REST sources.
- Exact-target proposals, explicit confirmation, no automatic retry of ambiguous writes, and independent invoice/line readback before reporting success.

## Prerequisites

- PAF 26.7-compatible visual Agent Builder and a registered model.
- Confirmed Fusion demo endpoint and a suitably scoped integration account.

## Import and configure

1. Import the release .paf into an unpublished destination flow.
2. Import assets/invoice-read-openapi.json and assets/invoice-actions-openapi.json as separate REST sources. Replace the example server URL with your confirmed Fusion endpoint and configure authentication in PAF. These reconstructed contracts require target-release validation.
3. Create or select the sources listed in assets/source-bindings.json; replace every environment-local node binding.
4. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. Disable Agent Memory and cross-thread sharing.
5. Verify POST cancellation support, permissions and connectivity against the intended environment before publishing. Creation requires valid accounting dates, distribution combinations and item lines that sum to the header amount.

## Controls and limits

- Write-capable unpublished draft. A new USD 0.02 fixture was created, one line canceled, then the whole invoice canceled and independently verified; destination validation is still required.
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
