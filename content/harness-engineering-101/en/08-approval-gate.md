---
title: "Harness Engineering 101 (8/10): Approval Gates — Designing Where Humans Must Approve"
series: harness-engineering-101
episode: 8
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Approval
- Human-in-the-loop
last_reviewed: '2026-05-14'
seo_description: Some actions must never run automatically. Payments, deploys, deletes,
  and outbound messages need human approval.
---

# Harness Engineering 101 (8/10): Approval Gates — Designing Where Humans Must Approve

The moment agent automation starts creating real business value, a harder question follows immediately: which actions may flow through automatically, and which actions must stop in front of a human? If you cannot answer that question clearly, the automation reads as latent incident potential.

Payments, deploys, deletes, and outbound communication are not just another class of output. They are irreversible or high-liability actions. The right question is not “is the model usually right?” but “where does a human decision belong even when the model looks confident?”

This is the 8th post in the Harness Engineering 101 series. It defines Approval Gates as an operating protocol inside the agent loop rather than a vague promise of manual review.

![Approval gates - designing where humans must approve](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/08/08-01-approval-gates-designing-where-humans-mu.en.png)
*Approval gates - designing where humans must approve*
> The purpose of an Approval Gate is not to abandon automation, but to put human decision authority at irreversible or high-risk actions.

## Questions to Keep in Mind

- What decision authority does an Approval Gate structure instead of merely blocking automation?
- Which actions can stay in dry-run, and which require human approval?
- What must approval logs preserve so the decision can be reconstructed later?

## What Is an Approval Gate?

![What is an approval Gate](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/08/08-02-what-is-an-approval-gate.en.png)

*What is an approval Gate*
An Approval Gate is a point where the agent must request human approval before executing a specific action. Automated flow pauses, decision authority hands off to a human, and the agent resumes only after receiving the response.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ApprovalRequest:
    action_id: str
    action_type: str
    summary: str
    risk_level: Literal["low", "medium", "high"]
    payload: dict

@dataclass
class ApprovalDecision:
    action_id: str
    decision: Literal["approve", "reject"]
    approver: str
    reason: str
```

`ApprovalRequest` carries the minimum information a human needs to decide. It must show what the agent intends to do, why it is risky, and what input the action runs against — at a glance.

## Where Should an Approval Gate Sit?

If you put a human in front of every action, automation loses its value; if you skip the gate everywhere, you get incidents. Consider an Approval Gate when any of the following apply:

1. **Irreversible actions**: payments, deploys, deletes, outbound messages
2. **Actions above an amount or scope threshold**: refunds over $1,000, bulk emails to more than 1,000 recipients
3. **Actions with legal or contractual liability**: signing contracts, sending personal data outside the org
4. **Actions where model confidence is low**: self-evaluation score below threshold, first-time use of a new tool

```python
def needs_approval(action_type: str, payload: dict, confidence: float) -> bool:
    if action_type in {"payment", "deploy", "delete", "send_email"}:
        return True
    if action_type == "refund" and payload.get("amount", 0) >= 1000:
        return True
    if confidence < 0.7:
        return True
    return False
```

This function is a checkpoint the agent must pass before invoking a tool. Plug it into the ToolRegistry from the Tool Harness (Ep5), right before the call site.

## Designing the Approval Workflow

![Designing the approval workflow](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/08/08-03-designing-the-approval-workflow.en.png)

*Designing the approval workflow*
The workflow has four stages.

```python
import uuid
from datetime import datetime, timezone

class ApprovalWorkflow:
    def __init__(self, store, notifier):
        self.store = store
        self.notifier = notifier

    def request(self, action_type: str, summary: str, payload: dict, risk: str) -> str:
        action_id = str(uuid.uuid4())
        req = ApprovalRequest(
            action_id=action_id,
            action_type=action_type,
            summary=summary,
            risk_level=risk,
            payload=payload,
        )
        self.store.save_request(req, created_at=datetime.now(timezone.utc))
        self.notifier.notify(req)
        return action_id

    def wait(self, action_id: str, timeout_sec: int = 600) -> ApprovalDecision | None:
        return self.store.wait_for_decision(action_id, timeout_sec)

    def execute_if_approved(self, action_id: str, executor):
        decision = self.store.get_decision(action_id)
        if decision is None:
            return {"status": "pending"}
        if decision.decision == "reject":
            return {"status": "rejected", "reason": decision.reason}
        result = executor()
        self.store.mark_executed(action_id, result)
        return {"status": "executed", "result": result}
```

1. **request**: the agent creates the approval request and notifies a human.
2. **wait**: the system waits for a decision. No response within the window counts as a timeout.
3. **execute_if_approved**: the action runs only if approved.
4. **log**: every step gets recorded (Observability — covered in Ep9).

## Separating Dry-run from Commit

![Separating Dry-run from commit](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/08/08-04-separating-dry-run-from-commit.en.png)

*Separating Dry-run from commit*
If you include a preview of "what would actually happen" in the approval request, the human can decide far more accurately. A dry-run computes the result without producing side effects.

```python
class RefundTool:
    def dry_run(self, payload: dict) -> dict:
        return {
            "would_refund": payload["amount"],
            "to_account": payload["account_id"],
            "remaining_balance": self._balance(payload["account_id"]) - payload["amount"],
            "affects_records": ["transactions", "ledger", "audit_log"],
        }

    def commit(self, payload: dict) -> dict:
        return self._execute_refund(payload)
```

The Approval Gate must include the `dry_run` result inside `ApprovalRequest.summary`. Only then can the human see "approving this refund will leave the balance at -$500" up front and reject it.

## Decision Logging — Who, When, and Why

The record of an approval matters more than the approval itself. When an incident hits, if you cannot trace "why this decision was made," the same incident will repeat.

```python
@dataclass
class ApprovalLog:
    action_id: str
    action_type: str
    payload: dict
    dry_run_preview: dict
    requested_at: datetime
    decided_at: datetime
    approver: str
    decision: str
    reason: str
    executed_at: datetime | None
    result: dict | None
```

The log must answer five questions:

1. **What was the agent trying to do?** action_type, payload
2. **What information was available at decision time?** dry_run_preview
3. **Who decided?** approver
4. **Why this decision?** reason (required field)
5. **What actually executed?** result

## Failure modes approval design must survive

Approval systems usually fail in operationally boring ways before they fail in dramatic ones. The common problems are stale requests no one owns, humans receiving too little context to decide, and approval rules that are so broad that reviewers stop reading carefully.

An approval path needs explicit timeout behavior, a fallback approver or authority matrix, and a way to turn rejection reasons into feedback the agent can use next time. Otherwise the same bad request simply comes back with slightly different wording.

```python
def resolve_timeout(action_id: str, requested_at, now, timeout_sec: int = 600) -> dict:
    elapsed = (now - requested_at).total_seconds()
    if elapsed < timeout_sec:
        return {"status": "waiting"}
    return {
        "status": "timed_out",
        "decision": "reject",
        "reason": "No approver responded within the policy window.",
        "next_action": "escalate_or_cancel",
    }
```

```text
Expected approval log fragment
- action_id: 7c4f...
- action_type: refund
- risk_level: high
- dry_run.remaining_balance: -500
- decision: reject
- reason: "Would overdraw the account after refund"
```

## Handling Timeout and Queue Congestion

Approval systems break more often from timeouts than from explicit rejections. When no one responds, requests pile up in the queue, and the agent either waits indefinitely or resubmits the same request. A timeout policy is an operational stability rule, not a UX convenience.

```python
from datetime import datetime

def resolve_timeout(
    action_id: str, requested_at: datetime, now: datetime, timeout_sec: int = 600
) -> dict:
    elapsed = (now - requested_at).total_seconds()
    if elapsed < timeout_sec:
        return {"status": "waiting"}

    return {
        "status": "timed_out",
        "decision": "reject",
        "reason": "Approver did not respond within the allowed window.",
        "next_action": "escalate_or_cancel",
    }
```

Without this default behavior, the system drifts in two bad directions. First, risky requests linger in the queue and eventually get processed without context. Second, requesters hit retry, creating duplicate actions for the same operation.

---

## Approval Policy DSL and Role-Based Permissions

As team size grows, maintaining approval rules in if-statements becomes unmanageable. Conditions multiply across amount thresholds, data sensitivity levels, environments (prod/staging), and actor roles. Extracting rules into a policy DSL makes change history and code review tractable.

```yaml
# approval_policy.yaml
version: 1
rules:
  - name: high_amount_refund
    when:
      action_type: refund
      amount_gte: 1000
    requires:
      approver_role: finance_manager
      min_approvals: 1
      max_wait_seconds: 900

  - name: production_deploy
    when:
      action_type: deploy
      environment: production
    requires:
      approver_role: sre_oncall
      min_approvals: 2
      max_wait_seconds: 600

  - name: customer_broadcast
    when:
      action_type: send_email
      recipients_gte: 500
    requires:
      approver_role: crm_owner
      min_approvals: 1
      max_wait_seconds: 1200
```

```python
from dataclasses import dataclass

@dataclass
class ApprovalRequirement:
    approver_role: str
    min_approvals: int
    max_wait_seconds: int

def evaluate_requirement(
    action: dict, rules: list[dict]
) -> ApprovalRequirement | None:
    for rule in rules:
        cond = rule["when"]
        if cond.get("action_type") and cond["action_type"] != action.get("action_type"):
            continue
        if "amount_gte" in cond and action.get("amount", 0) < cond["amount_gte"]:
            continue
        if "environment" in cond and action.get("environment") != cond["environment"]:
            continue
        if "recipients_gte" in cond and action.get("recipients", 0) < cond["recipients_gte"]:
            continue
        req = rule["requires"]
        return ApprovalRequirement(
            req["approver_role"], req["min_approvals"], req["max_wait_seconds"]
        )
    return None
```

The policy DSL advantage is clear: during operations, "why does this action require two approvers?" is answered by reading the policy file, not by tracing code.

---

## Approval Event Model and Audit Trail

Storing only the final approval decision is not enough. You need the full state-transition timeline from request creation to final execution for audit and incident reconstruction.

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class ApprovalEvent:
    action_id: str
    event_type: str
    actor: str
    at: str
    payload: dict

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def build_request_event(
    action_id: str, requester: str, preview: dict
) -> ApprovalEvent:
    return ApprovalEvent(
        action_id=action_id,
        event_type="approval_requested",
        actor=requester,
        at=now_iso(),
        payload={"preview": preview},
    )

def build_decision_event(
    action_id: str, approver: str, decision: str, reason: str
) -> ApprovalEvent:
    return ApprovalEvent(
        action_id=action_id,
        event_type="approval_decided",
        actor=approver,
        at=now_iso(),
        payload={"decision": decision, "reason": reason},
    )

def build_execution_event(
    action_id: str, executor: str, result: dict
) -> ApprovalEvent:
    return ApprovalEvent(
        action_id=action_id,
        event_type="action_executed",
        actor=executor,
        at=now_iso(),
        payload={"result": result},
    )
```

An example timeline in JSON:

```json
{
  "action_id": "act-20260514-001",
  "timeline": [
    {"event_type": "approval_requested", "actor": "agent-refund", "at": "2026-05-14T10:01:04Z"},
    {"event_type": "approval_decided", "actor": "finance_manager_a", "at": "2026-05-14T10:02:11Z", "decision": "approve"},
    {"event_type": "action_executed", "actor": "refund-service", "at": "2026-05-14T10:02:12Z"}
  ]
}
```

With this timeline, you can reconstruct "the approval existed, but who executed and when?" down to the minute during an incident. Approval Gate reliability is determined by this event system, not by the approval UI.

---

## Multi-Approval and Delegation

In real organizations, approvers are not always online. A single-approver assumption creates an immediate bottleneck during nights and vacations. Design multi-approval and delegation rules together.

```python
@dataclass
class ApprovalAssignment:
    primary: str
    delegates: list[str]
    required_count: int

def resolve_approvers(
    primary: str, roster: dict[str, list[str]], required_count: int
) -> ApprovalAssignment:
    delegates = roster.get(primary, [])
    return ApprovalAssignment(
        primary=primary, delegates=delegates, required_count=required_count
    )

def is_quorum_reached(decisions: list, required_count: int) -> bool:
    approved = [d for d in decisions if d.decision == "approve"]
    return len(approved) >= required_count
```

```yaml
# approval_delegation.yaml
delegation:
  finance_manager_a: [finance_manager_b, finance_manager_c]
  sre_oncall_a: [sre_oncall_b]
quorum:
  deploy_production: 2
  refund_over_1000: 1
```

With delegation in place, you can separate most timeouts into availability problems rather than policy violations. Teams operating Approval Gates must manage approval-time SLAs alongside approval accuracy.

Approval UX is also an operational factor. When approvers can see a summary card with risk badges on mobile, response times drop noticeably. Conversely, a structure that requires multiple link hops to reach the approval screen creates approval delays that cascade into full pipeline delays.

---

## Five Common Mistakes

1. **Requiring approval for everything.** You lose the value of automation, and humans stop reading the requests carefully. Set explicit risk thresholds.
2. **Approval requests without enough context.** "Approve this refund?" forces the human to reject by default. Always include a dry-run preview.
3. **No timeout policy.** If no one responds, the agent stalls forever. Auto-rejecting on timeout is the safer default.
4. **Not requiring a rejection reason.** A bare reject without a reason invites the same request again. Treat rejection reasons as a learning signal.
5. **No delegation of approval authority.** If only one person can approve, the system halts when they go on vacation. Design an authority matrix.

## Key Takeaways

- An Approval Gate is the point where a human decides before an irreversible or liability-bearing action runs.
- Use explicit rules like `needs_approval` to decide where gates belong.
- The workflow is four stages: request, wait, execute, log.
- Include a dry-run preview in the request so humans see consequences before deciding.
- An ApprovalLog must answer the 5W1H so post-incident review can succeed.

## Operational checklist

- [ ] Define irreversible or high-liability actions and encode them in approval rules.
- [ ] Include action summary, risk level, payload, and dry-run preview in every approval request.
- [ ] Implement approve, reject, and timeout as first-class code paths.
- [ ] Require rejection reasons and reuse them as feedback on the next attempt.
- [ ] Record who decided, when, why, and what actually executed in the approval log.

The next post covers Observability — how to record, trace, and replay agent runs.

## Answering the Opening Questions

- **What decision authority does an Approval Gate structure instead of merely blocking automation?**
  - It structures authority for actions that are hard to undo or high-accountability: data changes, external sends, spending, or permission escalation.
- **Which actions can stay in dry-run, and which require human approval?**
  - Reads, suggestions, and previews can often stay in dry-run. Real changes, payments, deletion, and customer-visible actions need human approval.
- **What must approval logs preserve so the decision can be reconstructed later?**
  - Logs should preserve who approved, when, which input, diff, and risk summary they reviewed, and what execution followed approval.

<!-- toc:begin -->
## In this series

- [Harness Engineering 101 (1/10): What Is Harness Engineering?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — Turning Vague Work into Executable Tasks](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Designing What the Agent Should Know and Not Know](./03-context-harness.md)
- [Harness Engineering 101 (4/10): Constraint Harness — Defining Rules, Boundaries, and Forbidden Actions](./04-constraint-harness.md)
- [Harness Engineering 101 (5/10): Tool Harness — Designing Safe Tools for Agents](./05-tool-harness.md)
- [Harness Engineering 101 (6/10): Test Harness — Turning Completion Criteria into Tests](./06-test-harness.md)
- [Harness Engineering 101 (7/10): Feedback Loops — Building Structures That Let Agents Recover from Failure](./07-feedback-loop.md)
- **Harness Engineering 101 (8/10): Approval Gates — Designing Where Humans Must Approve (current)**
- Harness Engineering 101 (9/10): Observability — Tracing and Replaying Agent Work (upcoming)
- Harness Engineering 101 (10/10): Production Harness — Building Operational Environments for Agents (upcoming)

<!-- toc:end -->

---

## References

### Official docs and references

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI — Best Practices for Safety in Agent Systems](https://platform.openai.com/docs/guides/safety-best-practices)
- [LangChain — Human-in-the-loop](https://python.langchain.com/docs/concepts/human_in_the_loop/)

### Verification-friendly operations references

- [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [PagerDuty Incident Response Guide](https://response.pagerduty.com/)

Tags: AI Agent, Harness, Production, Reliability
