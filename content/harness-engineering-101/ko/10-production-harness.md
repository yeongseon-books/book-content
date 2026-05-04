---
title: Production Harness — 운영 가능한 Agent 작업 환경 만들기
series: harness-engineering-101
episode: 10
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Production
- Deployment
last_reviewed: '2026-05-03'
seo_description: 지금까지 다룬 모든 Harness를 통합해서 운영 가능한 Agent 환경을 만듭니다.
---

# Production Harness — 운영 가능한 Agent 작업 환경 만들기

> Harness Engineering 101 시리즈 (10/10)

지금까지 다룬 모든 Harness를 통합해서 운영 가능한 Agent 환경을 만듭니다. Production Harness는 task, context, constraint, tool, test, feedback, approval, observability를 한 시스템으로 묶는 마지막 조립 단계입니다.

---
## Production Harness란 무엇인가요?

Production Harness는 지금까지 다룬 9가지 harness를 하나의 운영 가능한 시스템으로 묶는 마지막 layer입니다. 개별 harness가 아무리 잘 만들어져 있어도, 배포·롤백·on-call 흐름이 없으면 실제 사용자에게 안전하게 가닿을 수 없습니다.

```python
from dataclasses import dataclass

@dataclass
class HarnessStack:
    task: object          # Ep2 — TaskSpec
    context: object       # Ep3 — ContextBudget
    constraint: object    # Ep4 — ConstraintPolicy
    tools: object         # Ep5 — ToolRegistry
    tests: object         # Ep6 — eval suite
    feedback: object      # Ep7 — FeedbackLoop
    approval: object      # Ep8 — ApprovalWorkflow
    observability: object # Ep9 — Tracer
```

Production Harness는 이 stack을 받아 "배포할 수 있는 단위"로 포장합니다.

## 9가지 Harness가 어떻게 맞물리는가

요청 하나가 들어오면 다음 순서로 흐릅니다.

```python
def handle_request(stack: HarnessStack, user_input: str) -> dict:
    with stack.observability.trace("agent.run") as trace:
        spec = stack.task.parse(user_input)
        ctx = stack.context.assemble(spec)
        plan = stack.feedback.run_until_done(
            spec=spec,
            context=ctx,
            execute_step=lambda step: _execute_step(stack, step, trace),
        )
        return plan.result

def _execute_step(stack: HarnessStack, step, trace):
    stack.constraint.check(step)
    if stack.approval.needs_approval(step):
        decision = stack.approval.request_and_wait(step)
        if decision.decision == "reject":
            return {"status": "rejected"}
    with trace.child(f"tool.{step.tool}"):
        return stack.tools.invoke(step.tool, step.input)
```

각 harness는 한 가지 책임만 갖고, 다음 harness에 넘기는 인터페이스가 명확해야 합니다. 책임이 섞이면 어디를 고쳐야 할지 모르게 됩니다.

## Deployment Pattern — 점진적 롤아웃

새로운 prompt나 도구는 절대 한 번에 100% 사용자에게 배포하지 않습니다.

```python
class CanaryDeployer:
    def __init__(self, baseline, candidate):
        self.baseline = baseline
        self.candidate = candidate

    def route(self, request, traffic_percent: int) -> str:
        bucket = hash(request.user_id) % 100
        return "candidate" if bucket < traffic_percent else "baseline"

    def should_promote(self, baseline_metrics, candidate_metrics) -> bool:
        if candidate_metrics.error_rate > baseline_metrics.error_rate * 1.1:
            return False
        if candidate_metrics.p95_latency_ms > baseline_metrics.p95_latency_ms * 1.2:
            return False
        if candidate_metrics.avg_cost_usd > baseline_metrics.avg_cost_usd * 1.5:
            return False
        return True
```

표준 ramp는 1% → 10% → 50% → 100%이고, 각 단계에서 최소 1시간 동안 baseline과 비교합니다. 한 단계라도 `should_promote`가 False면 즉시 0%로 롤백합니다.

## Rollback — "되돌릴 수 있어야" 배포다

배포 후 30초 안에 이전 버전으로 되돌릴 수 없다면 그것은 배포가 아니라 사고입니다.

```python
class HarnessVersion:
    def __init__(self, version_id: str, stack: HarnessStack):
        self.version_id = version_id
        self.stack = stack

class HarnessRouter:
    def __init__(self):
        self.versions: dict[str, HarnessVersion] = {}
        self.active_id: str | None = None
        self.previous_id: str | None = None

    def deploy(self, version: HarnessVersion):
        self.versions[version.version_id] = version
        self.previous_id = self.active_id
        self.active_id = version.version_id

    def rollback(self) -> str:
        if self.previous_id is None:
            raise RuntimeError("no previous version to roll back to")
        self.active_id, self.previous_id = self.previous_id, self.active_id
        return self.active_id
```

Prompt, tool definition, eval dataset 모두 version_id로 묶여 함께 롤백되어야 합니다. Prompt만 롤백하고 도구는 그대로 두면 알 수 없는 조합이 됩니다.

## On-call Runbook — 새벽 3시에 깨었을 때

알림이 울렸을 때 on-call 엔지니어가 무엇을 봐야 하고, 무엇을 결정해야 하는지가 명문화되어 있어야 합니다.

```text
ALERT: agent.error_rate > 10% for 5 min

1. Trace 확인
   - Observability dashboard에서 최근 50개 trace 열기
   - 실패 span의 공통점 찾기 (모델? 도구? 단계?)

2. 1차 판단 (5분 이내)
   - 외부 의존성 장애? → 해당 도구 disable + status page 확인
   - 새 배포 직후? → rollback() 즉시 실행
   - 특정 사용자/입력 패턴? → 해당 패턴 quarantine

3. 2차 조치 (30분 이내)
   - Postmortem ticket 생성 (trace_id 포함)
   - eval suite에 실패 케이스 추가
   - 같은 패턴이 다시 오면 자동 차단되는지 확인
```

이 runbook은 코드와 함께 버전 관리되어야 하고, 분기마다 fire drill로 검증해야 합니다.

## Capstone Example — 환불 처리 에이전트

9가지 harness가 모두 적용된 최소 예시입니다.

```python
def build_refund_agent() -> HarnessStack:
    return HarnessStack(
        task=TaskParser(allowed_intents={"refund", "status"}),
        context=ContextBudget(max_tokens=4000, retrieval=OrderHistoryRAG()),
        constraint=ConstraintPolicy(
            max_amount_usd=10000,
            max_calls_per_run=5,
            allowed_tools={"lookup_order", "calc_refund", "issue_refund"},
        ),
        tools=ToolRegistry([LookupOrderTool(), CalcRefundTool(), IssueRefundTool()]),
        tests=EvalSuite.load("evals/refund/v3.jsonl"),
        feedback=FeedbackLoop(max_retries=2, max_reflects=1),
        approval=ApprovalWorkflow(
            store=PostgresApprovalStore(),
            notifier=SlackNotifier(channel="#refunds-approval"),
            rule=lambda step: step.tool == "issue_refund" and step.input["amount"] >= 100,
        ),
        observability=Tracer(exporter=OtelExporter(endpoint="https://otel.internal")),
    )
```

이 stack을 `HarnessRouter`에 등록하고, `CanaryDeployer`로 1% → 100% 순차 배포하면 production-ready 에이전트입니다.

## 흔한 실수 5가지

1. **모든 harness를 한 번에 도입**: 운영 부담이 한꺼번에 몰려 어느 harness도 제대로 쓰이지 않습니다. Approval과 Observability부터 도입하세요.
2. **rollback을 테스트하지 않음**: 사고가 나서야 rollback이 깨져 있다는 걸 알게 됩니다. 분기마다 실제로 롤백을 실행하는 fire drill을 도세요.
3. **canary 단계 없이 100% 배포**: 1만 명의 사용자가 동시에 깨진 응답을 받습니다. 항상 1%부터 시작하세요.
4. **on-call runbook이 코드 밖에 있음**: 위키에만 있는 runbook은 곧 outdated가 됩니다. 코드 저장소에 두고 PR로 갱신하세요.
5. **eval suite를 prompt와 따로 버전 관리**: 새 prompt가 옛 eval을 통과해서 배포된 뒤 실제 사용자에게는 깨집니다. version_id로 묶으세요.

## 핵심 요약

- Production Harness는 9가지 harness를 배포 가능한 단위로 묶는 마지막 layer입니다.
- 각 harness는 한 가지 책임만 갖고, 다음 harness로 넘어가는 인터페이스가 명확해야 합니다.
- Canary 배포(1%→10%→50%→100%)와 30초 안의 rollback은 production의 최소 요건입니다.
- On-call runbook은 코드 저장소에서 버전 관리하고 분기마다 fire drill로 검증하세요.
- Prompt, tool, eval dataset은 같은 version_id로 묶여 함께 롤백되어야 합니다.

이 시리즈의 마지막 글입니다. Harness Engineering 101에서 다룬 9가지 harness와 production layer를 조합하면, "그럴듯하게 보이지만 production에서 무너지는 데모"가 아니라 "사용자에게 신뢰받는 에이전트"를 만들 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- [Constraint Harness — 규칙, 경계, 금지 행동 정의하기](./04-constraint-harness.md)
- [Tool Harness — Agent가 사용할 도구를 안전하게 설계하기](./05-tool-harness.md)
- [Test Harness — 완료 조건을 테스트로 고정하기](./06-test-harness.md)
- [Feedback Loop — 실패를 고치게 만드는 반복 구조](./07-feedback-loop.md)
- [Approval Gate — 사람 승인이 필요한 지점 설계하기](./08-approval-gate.md)
- [Observability — Agent 작업을 추적하고 재현하기](./09-observability.md)
- **Production Harness — 운영 가능한 Agent 작업 환경 만들기 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [Google SRE — Release engineering](https://sre.google/sre-book/release-engineering/)
- [Martin Fowler — CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html)
- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [PagerDuty — Incident response documentation](https://response.pagerduty.com/)

Tags: AI Agent, Harness, Production, Reliability
