# Inventory Position Review — Fusion SCM

**What does the sampled stock position show by organization and unit?**

Review sampled stock quantities by item, organization, subinventory and unit. Produce a bounded evidence brief, limitations and a human follow-up checklist.

## Workflow

Read left to right: **1. Ask a question → 2. Provide API tools → 3. Review and explain → 4. Read the answer.** Sticky notes sit above the node sections. Expand Agent Description for its walkthrough and sample questions. The REST connection supplies a tool; the Agent chooses when to execute it.

## Status

Build draft, model, layout and conversation smoke checks passed. See [validation](assets/validation.md) for the exact scope and outstanding checks.

## Setup

Follow the [end-to-end Fusion setup](../../../integrations/fusion-apps/). Import this sample as a draft, upload [its GET-only OpenAPI](assets/openapi.json), replace the example origin and configure authentication. Bind the source listed in [source bindings](assets/source-bindings.json), select `AIW26-PAF-HOL6004-BOO6096`, disable memory and cross-thread sharing, and save.

## Evidence and limits

Resource: `/fscmRestApi/resources/11.13.18.05/inventoryOnhandBalances`

Projection: `InventoryItemId,ItemNumber,OrganizationId,OrganizationCode,SubinventoryCode,PrimaryUOMCode,PrimaryQuantity`

On-hand quantities are not available-to-promise. Preserve organization, subinventory, item and unit; never sum across units or count the same stock twice. Do not reserve, transfer or promise stock. A single OrganizationId filter is required. Use the configured scope or the user-supplied organization ID. If neither is provided, look up at most three accessible inventory organizations, select the first and disclose that scope. Never guess IDs, scan other organizations or broaden a configured scope.

The organization lookup reads at most three IDs/codes with `InventoryFlag=true`. Request `limit=10` and `onlyData=true` for the scoped stock query, do not expand child resources, and display at most five records. Query limits and projections are instructions; use credential scope or a gateway for hard enforcement. A sample is not the full population. No application changes are made.

## Sample questions

- What does the sampled stock position show by organization and unit?
- What can this sample establish, what evidence is missing, and what should the business owner verify next? Do not change anything.

## Artifacts

- [Native workflow source](workflow.json)
- [Archive metadata](archive-metadata.json)
- [Readable instructions](assets/agent-instructions.md)
- [Oracle resource documentation](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/fasrp/api-inventory-management-inventory-on-hand-balances.html)
