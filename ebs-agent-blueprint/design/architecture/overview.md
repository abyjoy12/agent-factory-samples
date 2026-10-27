# System Overview

The system supports two outcomes: generating a business application around reusable agent capabilities, and operating a business process over time through monitoring, investigation and human action. Both use the same governed definitions and runtime bindings.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| Business Agent Workbench | Registry cards, business specifications, workflow test chat, evaluation, cases and worklists |
| OPAF 26.10 | Author and execute deployed agent workflows; provide supported runtime integration and evidence |
| MCP business services | Advertise and execute authorized, typed business tools |
| Deterministic data services | Implement queries, calculations, validation and local staging operations |
| GitHub repository | Reviewable architecture, reusable definitions, sanitized exports and release history |
| Business application | Domain user experience, trusted context, workflow entry points and case links |
| Scheduler and case coordinator | Durable monitoring, task scheduling, state transitions, escalation and recovery |
| Coding agent with APEXlang | Generate the application using an approved blueprint and authoritative metadata |

The combined App 130/181 is itself an application. It is a shared administration and business-analysis experience rather than a replacement for every business UI. The new EBS Agent Blueprint Showcase can link to or embed case/worklist views. The existing Planning App remains a separate reference and sample business case. Physical consolidation, navigation and schema reuse require a separate implementation design.

## Interactive execution

```text
Business application or companion test chat
  -> Trusted integration adapter
  -> Selected OPAF workflow and conversation
  -> Task assignment to an agent
  -> Permitted business tools through MCP
  -> EBS/MSC evidence or local staging service
  -> Structured result and evidence
  -> Application display, evaluation and case update
```

The business analyst specifies intended behavior and acceptance. The workflow builder assembles executable behavior in OPAF. The coding agent implements the application around these contracts. A workflow may invoke a deterministic operation directly when agent judgment is unnecessary.

## Reusable composition

A workflow contains steps and tasks; a task is assigned to an agent; an agent has standing instructions, selected skills and attached tool references. The workflow supplies case-specific inputs and task instructions. Shared tools are independently defined and can be attached to multiple agents. A task can narrow an agent's tool use; it cannot grant new authority.

OPAF already provides builder, MCP, A2A, evaluation and observability capabilities. The companion adds the specific cross-artifact discovery, business context, acceptance and case-management experience required here. Product capability gaps must be verified before implementing duplicate administration features. This design makes no claim that another Oracle platform cannot implement similar patterns.

## Data placement

Read planning evidence from authorized origin MSC objects or a protected read copy, and operational evidence from approved EBS access paths. Preserve plan/collection age: a fresh query against an old plan is still historical evidence. MSC and operational EBS may be in different databases.

SelectAIAJ can retain deterministic services, semantics and local proposal/payload/audit staging. EBS copies in 26ai can support reproducible demonstrations or analytical workloads, but are not a prerequisite for OPAF agents. Replicated source evidence and agent-created draft staging are separate decisions. No source copies are removed by this strategy.

## First delivery boundary

The first capabilities are Work Order Reschedule Staging and Purchase Order Change Staging. Complete local staging means a persisted decision, linked payload and audit evidence confirmed by readback. Decision-only and uncertain outcomes must be represented accurately. Approval, submission, application and business resolution are separate milestones.

## Portfolio development

Maintain a discovery portfolio of approximately 50 EBS supply-chain agents across planning, procurement, supplier management, inventory, manufacturing, quality/process manufacturing, order management, logistics, maintenance/service and close. These are candidate business capabilities, not claims of 50 implemented agents or complete source feeds. Start the next implementation with the two existing WO/PO staging patterns, then expand using shared tools and validated data packs. Prioritize measured business value, source readiness, tool reuse and evaluation clarity.
