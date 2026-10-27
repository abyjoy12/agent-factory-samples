# Repository and Release Strategy

Keep architecture and reusable definitions together in the repository. README is the entry point; versioned architecture documents explain how the artifacts relate and how they reach deployment. Credentials, private endpoints, customer rows and full operational traces stay outside publication inputs.

## Target organization

```text
architecture/             Responsibilities, models and decision records
contracts/                Shared business and evidence contracts
tools/                    Independent versioned business tool definitions
skills/                   Markdown instruction packages and references
agents/                   Agent source, instructions and tool/skill references
tasks/                    Reusable task templates where needed
workflows/                Task assignments, routing and executable references
evaluations/              Synthetic cases, references and sanitized results
integrations/             Runtime, MCP and application adapters
```

This is a target organization, not a completed restructuring. The existing agents tree drives runnable catalog/release automation and requires real native workflow payloads. Keep design-only work in the current integrations packages until a deliberate migration updates that contract. Do not add incomplete manifests that imply a working .paf download.

## Artifact representation

Use Markdown for architecture, standing instructions, skills and task text. Use structured definitions for IDs, versions, schemas, relationships, step routing, policies and bindings. Refer to one canonical tool contract instead of duplicating its input schema under every agent. Give each artifact its own identity and version even when a release bundles several together.

An MCP tool implementation can have multiple deployment bindings. Register logical purpose separately from advertised server/tool names and discovered schemas. Tool registry cards and the server's tool inventory are related views; they do not require duplicate definitions. Task restrictions can narrow agent attachments but cannot expand tool authority.

## Authoring and authority

Recommended starting policy: author executable graphs in OPAF, capture native exports, and version reviewed business definitions and release artifacts in GitHub. The registry can hold drafts, editable working copies and references. Registry export/import and reconciliation must be explicit. Approval changes and synchronization events need audit history.

Avoid two competing authoritative editors for the same artifact. Record the authoring system, logical version, source revision, content hash, OPAF workflow ID/version and last reconciliation state. Detect divergence and require a review decision rather than applying silent bidirectional edits. The final provisioning/synchronization mechanism remains an implementation decision.

## Release contents

A release should identify contract, tool, skill, agent, task and workflow versions; native exports; deployment binding templates; evaluation references; validation results; and checksums. Pin versions or use reviewed compatible ranges and a resolved release lock. Verify dependency closure and destination import/rebind. Check the actual supported OPAF export/import schema rather than fabricating a native workflow from portable design JSON.

Separate design approval, implemented binding, runtime smoke test, business acceptance and production release states. A workflow export excludes environment setup unless the artifact explicitly includes an installer. Preserve exclusions for credentials, private connection IDs, uploaded customer documents and learned memories.

## Documentation references

Use Oracle documentation and release announcements with their release scope. The 26.7 REST and A2A guides provide specific contracts, while the 26.10 announcement establishes newer SDK and interoperability direction. Record remaining version-specific verification rather than treating every older guide as a complete 26.10 API reference. Do not copy deployment hostnames from screenshots or operational chats into the repository.
