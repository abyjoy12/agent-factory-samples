# Per-user deployment decision — 2026-10-18

Participants will use dedicated Factory accounts and import their own copies of
the sample agents. The editor account is the preparation account. For the
per-user rollout, enable Agent Memory and cross-thread sharing so each user's
agent can recall useful context across their own conversations.

Use **AIW26-PAF-HOL6004-BOO6096** for the sample agents. Business and operating
system facts must still come from fresh tool queries; remembered context does
not replace current evidence or required confirmation for write actions.

## Programmatic import

Native `.paf` exports do not carry Agent Memory switches or learned memory.
Automate the workflow import and destination configuration together, using an
authenticated session for each destination user:

1. Import the archive with `POST /v1/agentBuilder/customFlows/importAll` using
   multipart fields `flowsArchive` and `password`.
2. Capture the destination agent IDs returned by the import.
3. Configure destination datasource bindings and the required model connection.
4. For each agent, call `PUT /v1/agentBuilder/memory/settings/{agentId}` with
   `{"enabled": true, "shareBetweenChatThreads": true}`.
5. Read back the same endpoint with `GET`; verify both switches and memory
   availability, then validate the imported workflow before publishing.

Each destination starts with fresh learned memory, scoped to that user and
agent. Keep credentials, sessions and deployment state private and separate
for each account.

## Implementation status

This records the rollout decision; the general batch importer is still to be
implemented. Existing sample manifests and Build settings retain their current
values. The [Fusion deployer](../fusion-apps/deploy.py) already uses the agent
creation and memory APIs, but currently sets both memory switches to `false`.
Update the deployment policy and manifests consistently when implementing the
per-user importer. No live memory setting changed as part of this note.
