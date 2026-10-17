# Shared-session consolidation — 2026-10-17

This is the reconciliation baseline for the shared sample repository and build PAF instance, before the requested MCP repairs and action-capable agents.

## Reconciled state

- Local `main` and remote `main` both pointed to `db70a4e9090a88373029567257118adce45bbca2`. There was one local branch and one worktree. No remote commits needed merging.
- All **26** sample folders were preserved: 14 committed originals, eight uncommitted PSFT/EBS module additions, and four uncommitted JDE replica additions, including their generated documentation and integration notes.
- All **22** accessible live workflow graphs, titles and publication flags matched their saved `workflow.json` definitions. There were no graph conflicts requiring an overwrite or merge.
- The 12 newer drafts remain unpublished, with Agent Memory and cross-thread sharing disabled. The ten preceding business demos retain their existing published state. The original memory examples were not changed.
- The four original JDE fulfillment/memory workflow definitions returned HTTP 403 for the existing editor account. Their repository sources were preserved; their current live definitions could not be compared. An owner can share these four flows with the editor or provide fresh official exports to finish that comparison. Do not replace them from an older export merely to force consistency.
- The API listed 152 visible flows. The 126 flows outside this catalog were left in place. Compared with the previous module-run inventory, the only new visible flows were the eight already-documented PSFT/EBS additions. Visibility in the list does not imply permission to read a definition.
- A private backup and file-hash inventory were taken before consolidation. No live flow, model, source, publication flag, memory setting, application code or database was modified by reconciliation. No commit or push was performed.

The machine-readable [baseline](baseline.json) records workflow IDs, graph hashes and verification status. It contains no credentials or application query results. Hashes use SHA-256 over the graph serialized by Python `json.dumps(graph, sort_keys=True)`; environment-local bindings remain part of that graph.

## Work still outstanding at this baseline

| Integration | Observed state / next work |
| --- | --- |
| OCI Database Tools MCP | Existing managed server is active; preceding probe required OAuth. Dedicated EBS server creation previously failed the identity-domain issuer prerequisite. Authenticated tool execution is still pending. |
| ORDS MCP | Preceding inspection found ORDS 26.3 with MCP disabled and without JWT settings or dedicated MCP pools. Configuration and authenticated invocation are still pending. |
| PAF MCP sources | The editor account currently lists zero registered sources. |
| Action-capable agents | Fusion REST, AIDP, Kubernetes MCP and compute management/monitoring are requested follow-on work. No completed action-agent deployment is implied by this consolidation. |

See [DB Tools](../oci-database-tools-mcp/) and [ORDS](../ords-mcp/) for the recorded prerequisites. The existing analytical readers retain their privileges; action integrations need separately scoped identities and explicit action contracts.

## Continuing from another session

1. Refresh Git status and read this baseline before editing. Uncommitted files are shared work and must be preserved.
2. Match flows by workflow ID. Read the live definition again immediately before any update; compare it with the last observed graph. If both sides changed, save both and reconcile the differences before writing.
3. Obtain a fresh official export after an intended live change, then update the corresponding source, bindings and documentation together. Do not copy credentials, cookies, runtime records or model responses into this repository.
4. Keep memory and publication settings explicit: official archives do not carry the memory switches.
5. Regenerate the catalog after changing manifests. Keep private credentials and audit backups outside the repository. Review changes before any commit or release.

This report records metadata and definition comparison only; no business workflow was re-executed during consolidation.
