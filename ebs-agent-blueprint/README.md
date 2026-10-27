# EBS Agent Blueprint

This branch contains the consolidated action package for the Business Agent Workbench, OPAF 26.10, two WO and PO staging workflows, and the proposed EBS supply-chain portfolio.

Start with [START_HERE](START_HERE.md), then the [implementation action plan](implementation/ACTION_PLAN.md) and [updated Word plan](plan/EBS_Agent_Blueprint_Plan.docx).

## Package structure

| Directory | Purpose |
| --- | --- |
| design | Reviewed architecture, staging blueprints and MCP references |
| implementation | Thirteen work items, dependencies, deliverables and acceptance gates |
| plan | Updated implementation plan in Markdown and Word |
| portfolio | Fifty candidate agents with the two staging workflows prioritized |
| registry | Seven shared tool references and two agent references |
| templates | Portable agent, workflow-task and Markdown skill templates |

The Current package is included here as editable source files. Historical archives, duplicate ZIPs and the local 48-candidate review queue are excluded; the canonical 50-entry catalog already records follow-on candidates. These artifacts are design and implementation inputs, not deployed agents, database tools or native OPAF exports. The showcase App ID remains unassigned. EBS execution remains a customer integration extension.

The new consolidation is isolated on EBS-Agent-Blueprint and is not merged into main. Derived portfolio content retains its internal-review and external-clearance status; this upload does not assert licensing or production approval.
