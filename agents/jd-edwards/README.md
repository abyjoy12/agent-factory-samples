# JD Edwards EnterpriseOne agents

The original four samples use read-only AIS table-query endpoints for fulfillment and Agent Memory. Two additional business demos use curated database views and an allowlisted PL/SQL report.

## Business demos

- [Supplier follow-up](supplier-follow-up/) — open purchase lines through a PL/SQL routine allowlist
- [Field material readiness](field-material-readiness/) — fictional dispatch CSV, live work-order components and inventory evidence

## Fulfillment and memory demos

- [Fulfillment exception management](fulfillment-exception/) — stateless shortage investigation and recommendations
- [Explicit memory for fulfillment](fulfillment-memory/) — named-profile setup and cross-session recall
- [Adaptive fulfillment advising](adaptive-fulfillment-advisor/) — implicit learning from normal corrections
- [JPS920 fulfillment coaching](jps920-fulfillment-coach/) — incremental learning with a user-visible memory audit

All samples keep JDE credentials, connection definitions, model mappings, and learned user memories outside the repository and generated PAF.
