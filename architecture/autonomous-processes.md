# Autonomous Processes and Human Work

An autonomous process is a durable operating definition linking a KPI, detection policy, case lifecycle, specialist workflows and resolution criteria. Continuous monitoring normally uses scheduled checks and business events rather than an indefinitely running LLM loop.

## Process definition

| Definition | Required content |
| --- | --- |
| KPI contract | Formula, grain, units, source/freshness requirements, calculation version and owner |
| Detection policy | Tolerance, persistence window, severity, suppression, anomaly method and baseline |
| Assignment policy | Coordinator, specialist capabilities, task inputs and expected results |
| Autonomy policy | Permitted reads, staging or future execution; budgets, timeouts and approval gates |
| Resolution contract | Recovery threshold, observation window, verification evidence and residual-risk owner |
| Escalation policy | Missing evidence, blocked action, overdue human work, repeated failure and unresolved recovery |

Use deterministic tools for KPI calculation and tolerance checks. Statistical anomalies are a separate signal requiring an appropriate method and baseline. Neither a breach nor an anomaly establishes root cause. Agents investigate the evidence and coordinate work within the defined policies.

## Durable coordination

```text
Scheduled check or business event
  -> Calculate KPI and evaluate detection policy
  -> Open or update an existing business case
  -> Coordinator assigns specialist tasks
  -> Specialists investigate through permitted tools
  -> Synthesis reconciles findings and proposes a plan
  -> Human decision or customer action when needed
  -> Observe and verify recovery
  -> Resolve, continue observation or escalate
```

Persist case state independently of conversation memory. Store evidence references, task assignments, proposal versions, decisions, execution receipts, next review time and correlation IDs. Deduplicate related events so every KPI check does not create another case or repeat the same intervention. Use controlled concurrency for case updates and task claims.

Recommended case states are DETECTED, INVESTIGATING, AWAITING_HUMAN, AWAITING_EXECUTION, OBSERVING_RECOVERY, RESOLVED and ESCALATED. Parallel tasks can proceed while a case awaits one decision. Apply bounded retries, run budgets, backoff and escalation; do not repeatedly generate the same recommendation when no external state has changed.

OPAF executes the specialist workflows. A scheduler/event source, coordinator and persistent case store provide continuity. Verify which capabilities the installed runtime supplies and implement the remainder in the companion/backend. The present strategy does not assert that SDK invocation provides a durable process engine.

## Human worklist and case folder

The shared companion contains the canonical worklist and case folders. Business applications can link to, embed or tailor those views. A worklist item identifies the action required, assigned person/role, priority, due date and case/task reference. The case folder contains KPI history, business context, specialist findings, exact proposal, alternatives, evidence, approvals and audit history.

Human actions include approve, reject, revise, request analysis, reassign and escalate according to role. Record the response as a versioned event. Bind approval to the exact proposal reviewed, revalidate changed evidence and invalidate approval after material changes. Include delegation, timeout and overdue escalation policies.

The coordinator consumes that event and determines the next authorized task or workflow invocation. Do not promise to resume an arbitrary OPAF checkpoint until its supported contract is verified. A new invocation with durable case context may be the appropriate continuation.

## Resolution and current boundary

Closing a worklist item does not close the case. APPROVED, STAGED, SUBMITTED, APPLIED and RESOLVED describe different milestones. A resolved case requires the defined business recovery evidence for its observation window or an explicitly accepted alternative disposition.

Under the initial staging-only scope, a case that requires an EBS change remains AWAITING_EXECUTION after local approval/staging until a customer integration or accountable human supplies execution evidence. The process can continue monitoring, follow up and escalate, while avoiding a false claim that staging resolved the business problem.
