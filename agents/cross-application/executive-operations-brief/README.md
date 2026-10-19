# Executive Working Capital Brief — Cross-application

Combine receivables and payables specialists into a leadership brief with separate currency, organization and date scopes.

## Business story

**Audience:** Executive Insights process owners and demo presenters. **Problem:** Leaders need receivables and payables evidence before a working-capital discussion. **Demonstrated outcome:** Two specialists produce bounded finance evidence without mixing currencies or claiming a cash forecast.

**PAF feature:** Native Agent subagents with one shared read-only finance source. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Give me an executive brief on receivables and unpaid supplier invoices. Call both specialists and separate facts from decisions.
2. **User:** Why can we not use these samples as a cash forecast or net the balances across organizations and currencies?

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `oracleDatabaseTools`
- `agentStep`
- `chatOutputComponent`

Sources: `APPS.XXAF_FIN_AR_BALANCES_V`, `APPS.XXAF_FIN_AP_INVOICES_V`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse Oracle EBS Finance Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

Call both the Receivables evidence specialist and the Payables evidence specialist before composing a broad brief. Produce three observations, two owner decisions and one evidence gap. Every amount must include currency and organization. Preserve due-date versus invoice-date distinctions and each specialist's actual record grain. Never sum different currencies or net AP and AR into a cash forecast. These historical examples are bounded samples, not an enterprise working-capital total. If one specialist fails, disclose a partial brief. No collections, payments or accounting entries are executed. This demo is deliberately restricted to ORG_ID 204 and USD for both specialists. Do not imply multi-organization coverage. Distinguish the number of result groups from SUM(INVOICE_COUNT) or SUM(SCHEDULE_COUNT). Never invent percentages, date ranges or missing columns. AP already provides invoice dates; AR provides due dates. Owner decisions should concern reviewing collectibility and reconciling unpaid invoices, not editing schemas or adding date columns. Show actual first/last dates from both reports.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on the prepared PAF instance. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Receivables and payables specialists share the same EBS Finance binding. The earlier cross-database prototype was discarded after source-context failures; this is not a cross-database demonstration.

## Slide-building notes

1. **Business problem:** Leaders need receivables and payables evidence before a working-capital discussion.
2. **Agent action:** Combine receivables and payables specialists into a leadership brief with separate currency, organization and date scopes.
3. **PAF capability:** Native Agent subagents with one shared read-only finance source.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** Two specialists produce bounded finance evidence without mixing currencies or claiming a cash forecast. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.

The AI World lab model is `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible), already configured on the prepared PAF instance. Configure the same model name in each final lab instance; the archive excludes model definitions and credentials. Read the numbered workflow notes from left to right, and use the expand control beside Agent Description for the walkthrough and sample questions.
