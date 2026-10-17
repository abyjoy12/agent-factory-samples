# Module reader access and live demo checks

Validated 2026-10-17 on build PAF. The eight new module flows are unpublished drafts; existing published demos and connection definitions were retained.

## Access used

| Module | Reader | Objects required by this fixed report |
| --- | --- | --- |
| PeopleSoft Position Coverage Review | `PAF_AGENT_RO` | `PAF_DATA.HCM_POSITIONS`, `PAF_DATA.HCM_ASSIGNMENTS` |
| PeopleSoft Purchase Order Review | `PAF_AGENT_RO` | `PAF_DATA.FSCM_PURCHASE_ORDERS`, `PAF_DATA.FSCM_PO_LINES` |
| PeopleSoft Learning Capacity Review | `PAF_AGENT_RO` | `PAF_DATA.ELM_ACTIVITIES` |
| PeopleSoft Service Case Workload | `PAF_AGENT_RO` | `PAF_DATA.CRM_CASE_SUMMARY` |
| PeopleSoft Campus Capacity Review | `PAF_AGENT_RO` | `PAF_DATA.CS_CLASSES` |
| EBS Receivables Portfolio Review | `AF_EBS_FIN_RO` | `APPS.XXAF_FIN_AR_BALANCES_V` |
| EBS Purchase Receipt Review | `AF_EBS_SCM_RO` | `APPS.XXAF_SCM_PURCHASE_ORDERS_V` |
| EBS Concurrent Processing History | `AF_EBS_OPS_RO` | `APPS.XXAF_OPS_CONCURRENT_REQUESTS_V` |

The user authorized reader grant changes as needed. Live execution and the privilege audit showed that the existing access was sufficient; no database DDL or grant/revoke statement was executed for this expansion. Each module includes an idempotent SELECT-only grant reference. Those scripts are setup instructions for the correct PDB/view owner on another installation, not a migration that must be run here.

The five PeopleSoft PDBs reuse `PAF_AGENT_RO`. EBS uses separate Finance, Supply Chain and Operations readers. Reader inspection found `CREATE SESSION`, zero assigned roles, and SELECT/READ grants on the required objects. This audit covers system/role grants and the report objects; it is not a complete audit of every PUBLIC privilege inherited by an Oracle account. The application connections are shared demo integrations, not per-business-user application authorization.

## Live checks

All eight fixed queries completed using PAF SQL components. The eight graphs then each completed a primary prompt and a same-thread limitations follow-up. Four JDE replica graphs also completed fresh primary prompts with memory explicitly disabled. These are working demo checks, not comprehensive correctness, application regression, concurrency or authorization certification.

Reports retain historical dates and raw codes. The important boundaries are documented in every sample:

- HCM assignment counts include all returned HR statuses and cannot certify vacancies.
- PeopleSoft PO headers include raw lifecycle states and cannot certify open/approved/late status.
- ELM and Campus capacity subtraction is arithmetic, not bookable-seat eligibility.
- CRM missing closure dates do not certify open cases, and summed escalation counts do not count escalated cases.
- EBS AR counts payment schedules, keeps currencies/organizations separate and omits credits by design.
- EBS receipt arithmetic is at shipment grain and may include finally closed rows.
- EBS completed elapsed minutes and raw status codes cannot diagnose an outage or establish an SLA breach.

## MCP status

These reports use direct PAF data sources. See [Database Tools](../oci-database-tools-mcp/) and [ORDS](../ords-mcp/) for the separate probe results and remaining authentication/pool prerequisites. No working MCP demo is claimed.

## Repository content

Official workflow-only exports and compatible metadata are the source of truth. Import bindings, memory switches, fixed SQL, prompts, validation notes and presenter outlines accompany each sample. Credentials, cookie jars, Vault references, runtime database rows, private IP mappings and model responses are not copied into this integration folder.

## Reversal

Delete only the newly named drafts if no longer needed. Retain shared readers, their pre-existing grants, source data connections, existing published flows and GoldenGate. Do not run blanket REVOKE/DROP operations as demo cleanup.
