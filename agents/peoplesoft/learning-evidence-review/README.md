# Learning Evidence Review — PeopleSoft

Prepare a training-evidence review queue using completion dates, raw enrollment status, and target dates.

## Business story

**Audience:** Compliance process owners and demo presenters. **Problem:** Training owners need an evidence queue without overclaiming compliance. **Demonstrated outcome:** Grouped completion and target-date signals with explicit policy and evidence gaps.

**PAF feature:** Fixed aggregate SQL, Current Date, and a policy-aware Agent. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Prepare a training-evidence review queue. Which groups have past target dates without a recorded completion?
2. **User:** What additional evidence would be needed before calling these employees noncompliant?

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `SelectSqlQueryNode`
- `textCombiner`
- `currentDateTime`
- `agentStep`
- `chatOutputComponent`

Sources: `PAF_DATA.ELM_ENROLLMENTS`, `PAF_DATA.ELM_COURSES`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select `AIW26-PAF-HOL6004-BOO6096` on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse PeopleSoft Enterprise Learning Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

Describe the query's completion-date and target-date rules exactly. The mandatory flag and enrollment status are raw codes: do not invent a code dictionary. A recorded completion is not a compliance certification; a missing completion is not proof of misconduct or a legal violation. The course name is from the current effective-dated catalog, which can differ from a historical activity version. Never disclose learner identifiers. Use the dates to show historical-demo limitations and propose an evidence review, not employee discipline. Ask the training owner to confirm policy applicability, code meanings, equivalencies, and approved exceptions.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on the prepared PAF instance. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.
- Fixed-query check returned 12 rows on the validation date; live counts can change.

## Slide-building notes

1. **Business problem:** Training owners need an evidence queue without overclaiming compliance.
2. **Agent action:** Prepare a training-evidence review queue using completion dates, raw enrollment status, and target dates.
3. **PAF capability:** Fixed aggregate SQL, Current Date, and a policy-aware Agent.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** Grouped completion and target-date signals with explicit policy and evidence gaps. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.

The AI World lab model is `AIW26-PAF-HOL6004-BOO6096` (OpenAI Compatible), already configured on the prepared PAF instance. Configure the same model name in each final lab instance; the archive excludes model definitions and credentials. Read the numbered workflow notes from left to right, and use the expand control beside Agent Description for the walkthrough and sample questions.
