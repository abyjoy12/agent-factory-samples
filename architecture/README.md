# Business Agent Workbench Architecture

The Business Agent Workbench is the proposed companion to OPAF: it helps business analysts discover capabilities, specify business processes, test workflows and review business outcomes. OPAF 26.10 provides the selected agent/workflow runtime. Business applications consume those capabilities through controlled integrations. EBS Agent Blueprint Showcase is the new customer demonstration application, with a fresh App ID to be assigned. The existing Planning App supplies the initial sample business case and remains unchanged.

This documentation records the strategy agreed on October 26, 2026. It authorizes no infrastructure deployment, application merge, data migration or EBS transaction. The combined App 130/181 workbench, shared registry extensions and autonomous case services are design decisions to implement. Existing agent samples keep their own runtime versions and validation records.

## Read the design

| Document | Decisions and scope |
| --- | --- |
| [System overview](overview.md) | Component responsibilities and business-to-runtime flow |
| [Registry model](registry-model.md) | Tool, MCP, agent, skill, workflow, task and evaluation definitions |
| [Execution and integration](execution-model.md) | OPAF 26.10, SDK/REST/A2A, identity and data placement |
| [Business evaluation](evaluation-model.md) | Ontology-grounded scenarios, independent checks and acceptance |
| [Autonomous processes and human work](autonomous-processes.md) | KPI monitoring, cases, specialist tasks, worklists and resolution |
| [Application blueprint handoff](application-blueprint.md) | Inputs for Codex/Claude and APEXlang application generation |
| [Repository and release strategy](repository-strategy.md) | Documentation, reusable artifacts, deployment bindings and synchronization |
| [Decision record](decisions/001-companion-and-opaf.md) | Accepted choices, recommended defaults and open implementation questions |

## Current evidence and artifacts

- The supplied About screen identifies OPAF 26.10.0.0.0. This establishes the selected release, not validation of every SDK or API operation.
- Trusted hostname checks established normal TLS, MCP initialization and five advertised native tools for each of two database gateways. Database access and named business-tool implementation were not tested by that discovery. See [MCP inventory](../integrations/oracle-database-mcp/server-inventory.json).
- The [WO and PO blueprints](../integrations/ebs-staging-blueprints/README.md) define local draft staging. Native OPAF workflows and restricted business-tool wrappers remain to be built and validated.
- App 181 supplies the registry starting point; App 130 supplies discovery/chat patterns. Combining them is proposed work, not a completed application merge or a claim that their existing schemas already implement this entire model.
- The repository currently keeps tool contracts within the two design packages. Moving canonical contracts to an independent tool repository is the agreed target architecture; this documentation update does not restructure implementation artifacts.

## Design boundary

Business definitions remain application-neutral. Demo-specific packages, tables, app numbers and UI routes belong in adapters. Agents can inspect evidence and create authorized local drafts. Human review is separate, and integration back to EBS remains customer-defined.

## Application identity clarification

Use [EBS Agent Blueprint Showcase](../integrations/ebs-staging-blueprints/demos/blueprint-showcase/README.md) as a new application with a fresh ID. Preserve the existing Planning App as the first sample business case. The Business Agent Workbench remains the separate companion. Earlier references that treated the planning application as the new showcase are superseded by this distinction.
