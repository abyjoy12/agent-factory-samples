# Invoice Duplicate Review — PeopleSoft

Surface repeated supplier invoice references for AP review with deterministic SQL and explainable matching.

## Business story

**Audience:** Finance process owners and demo presenters. **Problem:** AP reviewers need a repeatable first pass over repeated invoice references. **Demonstrated outcome:** A small candidate queue with an explicit match key and review checklist.

**PAF feature:** Fixed SQL query, JSON Parser, and grounded Agent. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Review the duplicate-invoice candidates and explain which vouchers AP should investigate.
2. **User:** Explain the matching rule and what evidence a reviewer must check before taking action.

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `SelectSqlQueryNode`
- `parser`
- `textCombiner`
- `agentStep`
- `chatOutputComponent`

Sources: `PAF_DATA.FSCM_INVOICES`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse PeopleSoft Financials and Supply Chain Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

The preceding result comes from the fixed candidate query. The matching key is business unit + vendor SETID + vendor ID + trimmed upper-case invoice reference + transaction currency + gross amount. Explain the key and why a match is only a review candidate. Credits, installments, reversals, and corrected vouchers require AP review. No rows means no matches under this rule, not absence of fraud or duplicates under other rules. Show evidence and a reviewer checklist. You cannot hold payments, mark fraud, or determine legal compliance. The query covers all loaded history, not today's payable balance. Show all five supplied groups with BUSINESS_UNIT, vendor, invoice reference, TXN_CURRENCY_CD, GROSS_AMT, CANDIDATE_COUNT and EXAMPLE_VOUCHER. Every amount must include its currency. Do not prioritize by gross amount across currencies; retain the supplied count-based ordering.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Fixed-query check returned 5 rows on the validation date; live counts can change.

## Slide-building notes

1. **Business problem:** AP reviewers need a repeatable first pass over repeated invoice references.
2. **Agent action:** Surface repeated supplier invoice references for AP review with deterministic SQL and explainable matching.
3. **PAF capability:** Fixed SQL query, JSON Parser, and grounded Agent.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** A small candidate queue with an explicit match key and review checklist. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.

The AI World lab model is `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible), already configured on `build.oracleagentfactory.com`. Configure the same model name in each final lab instance; the archive excludes model definitions and credentials. Read the numbered workflow notes from left to right, and use the expand control beside Agent Description for the walkthrough and sample questions.
