# Business Policy Desk — Cross-application

Answer operational policy questions from a small supplied handbook with section citations and explicit gaps.

## Business story

**Audience:** Knowledge Management process owners and demo presenters. **Problem:** Employees need a consistent answer and a traceable policy reference. **Demonstrated outcome:** A cited answer from a small handbook and a clear response when the rule is absent.

**PAF feature:** File upload, Text combiner, and document-grounded Agent. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** For a USD 750 freight expedite, whose approval do we need? Cite the handbook.
2. **User:** What is the tax retention period for invoices under this handbook?

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `fileUpload`
- `textCombiner`
- `agentStep`
- `chatOutputComponent`

Sources: `assets/paf-demo-policy-handbook.txt`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select an available tool-capable LLM on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Upload the supplied paf-demo-policy-handbook.txt using the corresponding Builder component and select the uploaded filename.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

Answer only from the supplied fictional handbook. Begin policy answers with "For this fictional demo policy" and cite exact section IDs such as [PROC-02]. Quote short applicable text and explain how it applies. For a USD 750 expedite, approval by the procurement manager is required under PROC-02. Do not substitute general knowledge for missing rules. If the answer is absent, state "The supplied handbook does not define this" and identify the owner to consult. Do not call this vector retrieval or a Knowledge Agent: it is direct file grounding. No actual messages or approvals can be sent or recorded.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- The approval question cited PROC-02; the missing tax-retention question correctly reported the GAP-01 scope limit.

## Slide-building notes

1. **Business problem:** Employees need a consistent answer and a traceable policy reference.
2. **Agent action:** Answer operational policy questions from a small supplied handbook with section citations and explicit gaps.
3. **PAF capability:** File upload, Text combiner, and document-grounded Agent.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** A cited answer from a small handbook and a clear response when the rule is absent. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.
