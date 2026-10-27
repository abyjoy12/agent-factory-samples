# EBS Agent Blueprint Action Package

Version 1.0 dated October 27, 2026. This is the consolidated implementation starting point for the Business Agent Workbench, OPAF 26.10 workflows and the new EBS Agent Blueprint Showcase. Start by implementing the two WO and PO local-staging workflows. The 50-agent portfolio supplies follow-on ideas.

## Reading and implementation order

1. Read the [updated implementation plan](plan/EBS_Agent_Blueprint_Plan.md) or its formatted Word version in the same directory.
2. Assign owners and begin W01 and W02 in the [action plan](implementation/ACTION_PLAN.md). Use [work-items.json](implementation/work-items.json) to track dependencies, deliverables, gates and evidence.
3. Use the [reviewed design](design/README.md), [independent tool index](registry/tool-index.json) and [agent index](registry/agent-index.json) to build the seven business tools and two workflows.
4. Apply the [acceptance checklist](implementation/ACCEPTANCE_CHECKLIST.md), capture actual native exports and prove a clean second-environment import.
5. Select subsequent candidates from the [50-agent portfolio](portfolio/README.md). Shared cases, worklists and autonomous KPI processes are later implementation tracks.

## Decisions to carry into implementation

- OPAF 26.10.0.0.0 is the selected runtime. Verify the installed SDK, REST and export contracts before coding bindings.
- The Business Agent Workbench combines suitable patterns from Apps 130 and 181 after inspection. Its registry, test chat, business evaluation and shared human-work services remain to be implemented.
- EBS Agent Blueprint Showcase is a new application with an unassigned App ID. Preserve the existing Planning App as the first sample case.
- Agents attach independent tools and Markdown skills by reference; workflow steps own tasks. Backend services enforce authorization.
- Origin EBS and MSC reads are supported architectural choices; 26ai evidence copies are optional. SelectAIAJ is the initial staging candidate, subject to inspection.
- Both agents stop at verified local draft staging. Approval and EBS integration are separate customer services.

## What this package contains

This package contains reviewed design references, a reconciled plan and 50-entry catalog, seven tool references, two agent references, portable design templates, thirteen work items, acceptance criteria, checksums and validation results. It contains no deployed app, database installer, business-wrapper implementation or native OPAF workflow export. Existing SQLcl gateway discovery does not establish business-tool availability.

The reviewed reference designs match the documentation merged in [PR 1](https://github.com/abyjoy12/agent-factory-samples/pull/1). The added action plan and reconciled portfolio are versioned on the EBS-Agent-Blueprint branch under ebs-agent-blueprint. They have not been merged into main. Treat this branch as the reviewable consolidation; changes to the main architecture remain subject to reconciliation and review.

The portfolio derives in part from documents carrying Oracle confidentiality markings. Treat this complete package as internal review material pending external content and licensing clearance. No restricted PDF, credential, deployment address or customer record is included.
