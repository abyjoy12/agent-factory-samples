# Linux OS Monitoring

Use six read-only MCP tools to investigate Linux machine **linux-ops-01**. The agent explains CPU, memory, operations filesystem and application health with UTC time, units, measured limits and a human next step. It uses **AIW26-PAF-HOL6004-BOO6096**.

The machine runs **orders-api**, **inventory-api**, **job-worker**, **report-cron** and **log-forwarder**. Small, varied workloads produce real process, listener, request and job activity while keeping baseline resource use low.

Follow the [end-to-end setup](../../../integrations/linux-os-monitoring/README.md). Import the native release archive, select the local MCP source and model, and disable Agent Memory and cross-thread sharing. The graph reads left to right, with numbered notes above each stage. Expand Agent description for the walkthrough and six sample questions.

The agent observes the configured machine resources, operations filesystem and listed application checks. Recent history is a rolling measurement buffer with actual coverage. All findings come from tool observations; operator changes remain separate.

See [instructions and questions](assets/agent-instructions.md), [source bindings](assets/source-bindings.json) and [validation](assets/validation.md).
