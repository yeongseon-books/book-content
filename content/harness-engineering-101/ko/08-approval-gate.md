---
title: Approval Gate — 사람 승인이 필요한 지점 설계하기
series: harness-engineering-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Approval
- Human-in-the-loop
last_reviewed: '2026-05-12'
seo_description: 어떤 행동은 자동으로 실행되어서는 안 됩니다. 결제, 배포, 삭제, 발송은 사람의 승인이 필요합니다.
---
# Approval Gate — 사람 승인이 필요한 지점 설계하기
에이전트 자동화가 실제 가치를 내기 시작하는 순간, 팀은 곧바로 반대 질문을 만나게 됩니다. 어디까지는 자동으로 흘려도 되고, 어디부터는 반드시 사람이 멈춰야 하는가입니다. 이 질문에 답하지 못하면 자동화는 곧 사고 가능성으로 읽힙니다.
결제, 배포, 삭제, 외부 발송처럼 되돌리기 어렵거나 책임이 큰 행동은 결과 품질만 좋다고 자동 실행해선 안 됩니다. 문제는 많은 팀이 이 기준을 운영 중에 감으로 적용한다는 점입니다. 감으로 세운 승인 체계는 바쁜 날 가장 먼저 무너집니다.
Approval Gate는 사람이 개입해야 하는 지점을 설계하는 층입니다. 위험 행동 앞에 명시적인 정지선을 두고, dry-run preview와 결정 로그를 남기며, 승인·거절·timeout을 모두 시스템 흐름에 포함시켜야 합니다.
이 글은 Harness Engineering 101 시리즈의 8번째 글입니다.
자동화의 가치는 모든 것을 자동화하는 데 있지 않고, 자동화하면 안 되는 지점을 정확히 고르는 데 있습니다.
## 이 글에서 다룰 문제
- Approval Gate는 단순한 수동 검토와 무엇이 다를까요?
- 어떤 행동 앞에 사람 승인을 두어야 할까요?
- 승인 요청에는 어떤 정보가 있어야 빠르고 정확한 결정을 할 수 있을까요?
- dry-run과 commit을 분리하면 무엇이 달라질까요?
- 승인 기록은 왜 실행 그 자체만큼 중요할까요?
## 왜 이 글이 중요한가
Approval Gate가 중요한 첫 번째 이유는 책임 경계입니다. 에이전트가 실제 세계에 영향을 주는 순간, 누가 언제 어떤 근거로 멈췄는지가 남아 있어야 합니다.
두 번째 이유는 자동화 품질이 아니라 사업 위험입니다. 금액이 크거나, 되돌리기 어렵거나, 법적 책임이 따르는 행동은 모델 신뢰도와 무관하게 사람 승인 단계를 가져야 합니다.
세 번째 이유는 운영 속도입니다. 잘 설계된 gate는 자동화를 늦추는 장치가 아니라, 위험한 행동에만 짧고 정확한 인간 판단을 끼워 넣어 전체 시스템 신뢰를 높이는 장치입니다.
## Approval Gate를 이해하는 가장 좋은 방법: 자동화 흐름 안에 사람의 결정 권한을 구조적으로 삽입하는 장치로 보는 것입니다
Approval Gate는 사람이 항상 마지막에 리뷰하는 구조와 다릅니다. 특정 행동 직전에 시스템이 멈추고, 결정 권한을 사람에게 넘긴 뒤, 승인 결과를 받아 다시 이어 가는 운영 프로토콜입니다.
좋은 gate는 사람에게 최소한의 핵심 정보만 보여줍니다. 무엇을 하려는지, 왜 위험한지, 어떤 결과가 예상되는지, 실행하면 어떤 레코드와 잔액이 바뀌는지를 한눈에 볼 수 있어야 합니다.
또한 gate는 request, wait, execute, log 전부를 포함해야 합니다. 승인만 받고 기록이 없거나, timeout 정책이 없거나, 거절 사유가 남지 않으면 같은 문제가 다시 반복됩니다.
> Approval Gate의 목적은 자동화를 막는 것이 아니라, 사람만이 져야 할 책임을 시스템 안에서 명시적으로 복원하는 데 있습니다.
## 핵심 개념
어떤 행동은 자동으로 실행되어서는 안 됩니다. 결제, 배포, 삭제, 발송은 사람의 승인이 필요합니다. Approval Gate는 어디서 사람이 멈춰야 하는지를 명시적으로 설계합니다.

![Approval Gate - 사람 승인이 필요한 지점 설계하기](../../../assets/harness-engineering-101/08/08-01-approval-gates-designing-where-humans-mu.ko.png)

### Approval Gate란 무엇인가요?

![Approval Gate란 무엇인가요](../../../assets/harness-engineering-101/08/08-02-what-is-an-approval-gate.ko.png)

Approval Gate는 에이전트가 특정 행동을 실행하기 직전에 사람의 승인을 요구하는 지점입니다. 자동화된 흐름을 일시적으로 멈추고, 결정 권한을 사람에게 넘긴 뒤, 사람의 응답을 받아 다시 진행하거나 중단합니다.

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

`ApprovalRequest`는 "사람이 결정을 내리기 위해 필요한 최소 정보"를 담습니다. 에이전트가 무엇을 하려 하는지, 왜 위험한지, 어떤 입력으로 실행되는지를 한눈에 보여줘야 합니다.

### 어디에 Approval Gate를 둬야 할까요?

모든 행동에 사람을 끼우면 자동화의 의미가 사라지고, 어디에도 두지 않으면 사고가 납니다. 다음 4가지 기준 중 하나라도 해당하면 Approval Gate를 두는 것을 검토합니다.

1. **되돌릴 수 없는 행동**: 결제, 배포, 삭제, 외부 발송
2. **금액·범위가 임계치를 넘는 행동**: 100만 원 이상 환불, 1000명 이상 일괄 메일
3. **법적·계약상 책임이 따르는 행동**: 계약 체결, 개인정보 외부 전송
4. **모델 신뢰도가 낮은 행동**: 자체 평가 점수가 임계치 미만, 새로운 도구 첫 호출

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

이 함수는 에이전트가 도구를 호출하기 직전에 항상 거쳐야 하는 관문입니다. Tool Harness(Ep5)의 ToolRegistry에서 도구를 실행하기 전 단계에 끼워 넣습니다.

### Approval Workflow 설계하기

![Approval Workflow 설계하기](../../../assets/harness-engineering-101/08/08-03-designing-the-approval-workflow.ko.png)

승인 흐름은 4단계로 구성됩니다.

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

1. **request**: 에이전트가 승인 요청을 생성하고 사람에게 알립니다.
2. **wait**: 사람의 결정을 기다립니다. 일정 시간 내 응답이 없으면 timeout으로 간주합니다.
3. **execute_if_approved**: 승인된 경우에만 실제 행동을 실행합니다.
4. **log**: 모든 단계를 기록합니다 (Observability — Ep9에서 다룹니다).

### Dry-run vs Commit 분리

![Dry-run vs Commit 분리](../../../assets/harness-engineering-101/08/08-04-separating-dry-run-from-commit.ko.png)

승인 요청 자체에 "실행될 결과의 미리보기"를 함께 보여주면 사람이 훨씬 정확하게 결정할 수 있습니다. Dry-run은 실제 부수효과 없이 결과만 계산하는 모드입니다.

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

Approval Gate는 `dry_run` 결과를 `ApprovalRequest.summary`에 포함시켜야 합니다. 그래야 사람이 "이 환불을 승인하면 잔액이 -50만 원이 된다"는 사실을 미리 보고 거절할 수 있습니다.

### Decision Logging — 누가, 언제, 왜 승인했는가

승인 자체보다 더 중요한 것은 승인의 기록입니다. 사고가 났을 때 "왜 이 결정이 내려졌는가"를 추적하지 못하면 같은 사고가 반복됩니다.

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

기록은 다음 5가지 질문에 답할 수 있어야 합니다.

1. **무엇을 하려 했는가**: action_type, payload
2. **결정 시점에 무엇을 알 수 있었는가**: dry_run_preview
3. **누가 결정했는가**: approver
4. **왜 그런 결정을 내렸는가**: reason (필수 입력)
5. **실제로 무엇이 실행되었는가**: result
## 흔히 헷갈리는 지점
- 모든 행동에 승인을 붙이면 더 안전하다고 생각하기 쉽지만, 실제로는 사람도 더 이상 꼼꼼히 보지 않게 됩니다.
- 승인 요청에 맥락이 적을수록 빠를 것 같지만, 정보가 부족하면 기본값은 거의 항상 거절이 됩니다.
- timeout은 단순한 UX 문제라고 보기 쉽지만, 정책이 없으면 시스템은 영원히 멈춰 있을 수 있습니다.
- reject reason은 없어도 된다고 생각하기 쉽지만, 거절 사유가 없으면 같은 요청이 다시 올라옵니다.
- 승인 로그는 나중에 감사용으로만 필요하다고 보기 쉽지만, 실제로는 사고 분석과 정책 개선의 핵심 데이터입니다.
## 운영 체크리스트
- [ ] 되돌릴 수 없거나 책임이 큰 행동 목록을 정의하고 `needs_approval` 규칙에 반영합니다.
- [ ] 승인 요청에 action summary, risk level, payload, dry-run preview를 포함합니다.
- [ ] 승인·거절·timeout 세 경로를 모두 코드 흐름에 넣습니다.
- [ ] 거절 사유를 필수 입력으로 받아 feedback signal로 재사용합니다.
- [ ] 누가 언제 왜 승인했고 실제로 무엇이 실행됐는지 ApprovalLog에 남깁니다.
## 정리
Approval Gate는 사람이 검토하는 문화를 선언하는 장치가 아니라, 사람의 결정 권한을 실행 흐름 안에 구조적으로 삽입하는 장치입니다. 그 구조가 있어야 자동화는 책임 있는 시스템이 됩니다.
핵심은 gate 위치와 승인 페이로드입니다. 어디서 멈출지 명확해야 하고, 멈춘 뒤 사람에게 보여 줄 정보가 충분히 좋아야 빠르고 정확한 판단이 가능합니다.
다음 글에서는 Observability를 다룹니다. 승인과 거절, 도구 호출과 모델 판단을 모두 추적할 수 있어야 비로소 에이전트 시스템을 재현하고 운영할 수 있습니다.
<!-- toc:begin -->
## Harness Engineering 101 시리즈

- [Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- [Constraint Harness — 규칙, 경계, 금지 행동 정의하기](./04-constraint-harness.md)
- [Tool Harness — Agent가 사용할 도구를 안전하게 설계하기](./05-tool-harness.md)
- [Test Harness — 완료 조건을 테스트로 고정하기](./06-test-harness.md)
- [Feedback Loop — 실패를 고치게 만드는 반복 구조](./07-feedback-loop.md)
- **Approval Gate — 사람 승인이 필요한 지점 설계하기 (현재 글)**
- [Observability — Agent 작업을 추적하고 재현하기](./09-observability.md)
- [Production Harness — 운영 가능한 Agent 작업 환경 만들기](./10-production-harness.md)

<!-- toc:end -->
## 참고 자료
### 공식 문서

- [Anthropic — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI — Best practices for safety in agent systems](https://platform.openai.com/docs/guides/safety-best-practices)
- [Google SRE — Postmortem culture](https://sre.google/sre-book/postmortem-culture/)
- [LangChain — Human-in-the-loop](https://python.langchain.com/docs/concepts/human_in_the_loop/)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)
Tags: AI Agent, Harness, Approval, Human-in-the-loop