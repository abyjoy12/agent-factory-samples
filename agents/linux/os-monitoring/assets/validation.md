# Linux OS Monitoring validation

Validated on **2026-10-18** using **AIW26-PAF-HOL6004-BOO6096** in the configured Agent Factory instance. The target is presented as Linux machine **linux-ops-01**. The draft remains unpublished.

## Automated and live checks

| Check | Result |
| --- | --- |
| Monitoring unit and ASGI lifecycle tests | 14 passed, including cgroups v1/v2, CPU units, reused PIDs, bounded inputs/history, fresh application evidence and startup before any MCP session |
| Repository tests | 14 passed |
| Native packaging | All 29 `.paf` archives built, decrypted and compared with their source workflows |
| Deployment | Syntax check, scoped preview, apply and readiness passed; unchanged reapply reported zero changes |
| Runtime limits | One assigned CPU, 1536 MiB memory with no additional swap, 128 PIDs, UID/GID 10001, read-only root, dropped capabilities and no-new-privileges |
| Private connection | Factory discovered exactly six tools; independent calls from its private source succeeded |
| Connection restrictions | Existing source firewall allowlist retained; initial negative checks rejected an unapproved Origin (403), Host (421) and non-allowlisted private client (timeout) |
| Baseline | Debian 12 x86_64, osquery 5.23.1; acceptance measured 1.0% CPU and 11.5% charged memory, with both APIs and three background jobs active |
| Application activity | All five application counters advanced over 12 seconds while their PIDs remained stable; baseline CPU stayed below 15% and memory below 25% |
| CPU fault | 80.7% of the assigned CPU; `batch-indexer` was the main observed contributor; multiple actual history samples showed pressure |
| Memory fault | Charged memory rose from 26.1% to 87.7%, increasing by 946 MiB between acceptance readings; `cache-builder` RSS exceeded 1 GiB |
| Filesystem fault | 58 MiB of real blocks on the 64 MiB operations tmpfs: 90.6% used |
| Orders outage | Orders 8081 became unavailable; inventory 8082, all three jobs and monitoring remained available; the other application PIDs stayed stable |
| Recovery and bounds | Fault expiry restored all five applications; reset cleared memory/filesystem pressure; requests for more than 30 minutes of history were rejected |
| Builder layout | All eight nodes inspected in the browser; no overlaps, width mismatches or clipped notes; four numbered notes above four functional nodes, laid out left to right |
| Native export | Official export validated; portable MCP binding cleared; saved description contains six sample questions |

Fixed application caches total 24 MiB, plus interpreter overhead. Short randomized work bursts, local API requests, a small overwritten report and bounded rotating logs produce varied observations without accumulating memory, queued work or output files. The memory fault allocates at most 1152 MiB and ramps over about 15 seconds. CPU and memory include monitoring overhead; the acceptance client adds some memory, so its values can exceed an independent reading. Percentages vary between observations.

## Factory conversations

All six conversations passed in separate, fresh rooms using the configured model. Answers were compared with independent MCP observations.

| Question | Observed result |
| --- | --- |
| Machine health | Reported observation time, assigned limits and all five healthy applications; 0.8% CPU and 9.1% charged memory |
| Application activity | Identified both APIs and all three jobs, with roles, PIDs, health and counters; did not infer throughput from a single reading |
| CPU investigation | Reported 78.1–81.9% CPU and `batch-indexer`; limited pressure duration to the observed samples and disclosed shorter history coverage |
| Memory investigation | Reported 85.2% charged memory and `cache-builder` RSS above 1 GiB; distinguished RSS from charged memory and did not infer a leak |
| Filesystem investigation | Reported the 64 MiB operations filesystem at 90.7%, with about 5.98 MiB available; bounded log activity explains variation from acceptance readings |
| Orders availability | Found orders unavailable with no 8081 listener; inventory and the three jobs continued making progress; did not infer a crash from absence alone |

All answers used **linux-ops-01**, omitted deployment-location details and stated that monitoring made no changes. Final reset restored all five applications. Independent checks measured 1.6% CPU and 9.1% charged memory, confirmed readiness and resource limits, and found no OOM kill.

The run endpoint returns the final answer rather than a full tool trace. These checks compare observable answers with independently captured evidence; they do not assert an exact internal call sequence. Raw responses, independent readings, URL policy snapshots and browser evidence remain in the private operations archive.

## Configuration and portability

The draft selects **AIW26-PAF-HOL6004-BOO6096**, with Agent Memory and cross-thread sharing disabled. Its six sample questions cover baseline health, CPU, memory, filesystem, orders availability and application activity. The native export clears its environment-local MCP binding for portability.

The instance owner approved **ALLOW_INSECURE_HTTP_URLS=true** on 2026-10-18. The setting was enabled and read back successfully; **BLOCK_PRIVATE_OUTBOUND_URLS=false** already permitted private destinations. The direct private MCP source is connected, and the source firewall restrictions remain in place.

Additional target instances have not been deployed or verified by these checks. Repeat import, local MCP binding, model availability, memory settings, private connectivity and all six questions on each target. Use its approved HTTP policy or a trusted private HTTPS endpoint.

## Repeat the checks

See the [setup and operation guide](../../../../integrations/linux-os-monitoring/README.md#validate-and-operate) for unit, protocol and scenario commands. Run scenario acceptance while the machine is not being used for other demonstrations because it temporarily injects faults. The operator script resets the scenario on exit.

Infrastructure automation, private evidence paths and exact rollout/rollback values are maintained in `~/work/infra/ansible`.
