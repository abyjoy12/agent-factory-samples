# PeopleSoft Workforce Planning Brief

Explain department staffing and FTE using effective-dated assignments and nonconfidential catalogs.

## Business story

**Audience:** HR process owners and demo presenters. **Problem:** Managers can confuse assignment counts, headcount and FTE. **Demonstrated outcome:** A staffing discussion grounded in effective-dated assignments and clear measures.

**PAF feature:** Oracle database tools plus Current Date and Text combiner. A successful demonstration shows the evidence path and the resulting business decision. No measured time savings, financial return or compliance outcome is claimed.

## Demo in three minutes

1. **User:** Which departments have the most assignments and FTE? Explain what the numbers count.
2. **User:** Why can we not add the employee counts across those groups to obtain global headcount?

Pause after the first answer to show the Builder graph and the evidence source. Use the second prompt as a follow-up; it is illustrative unless specifically covered in the validation notes below. Preserve historical dates and explain missing evidence instead of refreshing sample records to make them appear current.

## Components and source contract

- `chatInputComponent`
- `oracleDatabaseTools`
- `currentDateTime`
- `textCombiner`
- `agentStep`
- `chatOutputComponent`

Sources: `PAF_DATA.HCM_WORKFORCE_SUMMARY`, `PAF_DATA.HCM_DEPARTMENTS`, `PAF_DATA.HCM_ASSIGNMENTS`.

The exact official workflow export is in `workflow.json`. [source-bindings.json](assets/source-bindings.json) identifies every database and file binding. SQL used by deterministic components is supplied separately in `assets/`; model-generated SQL tools remain constrained by the integration account's database privileges. Read the complete [agent instructions](assets/agent-instructions.md) for join, unit, date and interpretation rules.

## Setup

1. Import the release .paf with the repository archive passphrase. Imported flows are unpublished until reviewed.
2. Select an available tool-capable LLM on every Agent node. The demo used xai.grok-4.3; model connections are not bundled.
3. Create or reuse PeopleSoft Human Capital Management Read Only and rebind the nodes listed in assets/source-bindings.json.
4. Disable Agent Memory and sharing between chat threads for this flow. This instance enables them by default; the official export does not include those switches. Run the documented primary prompt, inspect the evidence and dates, then publish for the demo audience.

## Business interpretation and limits

Use the configured HCM database only. Start with SELECT BUSINESS_UNIT,SETID_DEPT,DEPTID,HR_STATUS,EMPL_STATUS,ASSIGNMENT_COUNT,EMPLOYEE_COUNT,TOTAL_FTE FROM PAF_DATA.HCM_WORKFORCE_SUMMARY ORDER BY ASSIGNMENT_COUNT DESC FETCH FIRST 10 ROWS ONLY. Distinguish assignments, distinct people per group, and FTE. Never sum grouped distinct employee counts to claim global headcount. Department joins require SETID_DEPT=HCM_DEPARTMENTS.SETID and DEPTID. For global distinct people use COUNT(DISTINCT EMPLOYEE_ID) over HCM_ASSIGNMENTS with the explicitly stated HR_STATUS filter. These views resolve the latest effective date/sequence not after today. Do not decide hiring, firing, pay, promotions, or rank individuals. Provide staffing questions for a manager, not individual employment decisions.

All suggested follow-ups are for human review. The workflow does not execute application changes or send messages. Demo integration accounts do not reproduce each business user's application authorization. Use the existing curated views and credentials in the Builder; never commit credentials or real employee/customer records to this public repository.

## Validation

**Passed live smoke validation — 2026-10-17.**

- One primary business prompt completed against this exact graph on build.oracleagentfactory.com. Response wording depends on the selected model.
- Fixed queries were checked separately where present. Database/application sample data was not copied into this repository.
- This is a demo validation, not certification of business accuracy, policy compliance or production readiness. Review returned evidence during presentations.

## Slide-building notes

1. **Business problem:** Managers can confuse assignment counts, headcount and FTE.
2. **Agent action:** Explain department staffing and FTE using effective-dated assignments and nonconfidential catalogs.
3. **PAF capability:** Oracle database tools plus Current Date and Text combiner.
4. **Evidence:** Show the bound source and a current playground run; preserve identifiers, units and source dates.
5. **Value hypothesis:** A staffing discussion grounded in effective-dated assignments and clear measures. Measure preparation effort and reviewer usefulness in a pilot; this demo makes no ROI claim.
6. **Boundary:** Show one limitation from the instructions and the human decision that remains.

See [slides/README.md](slides/README.md) for a presenter sequence. The root README compares all demos and explains which features are implemented.
