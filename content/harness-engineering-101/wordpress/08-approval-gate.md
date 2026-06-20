---
title: "바이브코딩을 위한 하네스 엔지니어링 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기"
series: harness-engineering-101
episode: 8
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Approval
- Human-in-the-loop
---

# 바이브코딩을 위한 하네스 엔지니어링 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 여덟 번째 글입니다. 에이전트 자동화에서 사람의 승인이 반드시 필요한 지점을 설계하는 Approval Gate를 다룹니다.

---

에이전트 자동화의 목표는 사람 개입을 줄이는 것입니다. 그런데 줄이면 안 되는 지점이 있습니다. 고객에게 이메일을 보내기 전, 데이터베이스를 수정하기 전, 외부 결제를 처리하기 전 — 이 지점들은 에이전트가 아무리 자신감 있어도 사람이 한 번 확인해야 합니다.

Approval Gate는 에이전트 실행 중간에 사람의 승인을 받고 나서야 다음 단계로 진행하는 구조입니다. 자동화와 안전성의 균형을 설계하는 것입니다.

> "자동화할 수 있는 것과 자동화해야 하는 것은 다릅니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트 작업 중 사람 승인이 필요한 지점이 어디인지 식별했나요?
2. 승인 요청을 어떻게 전달하나요?(슬랙, 이메일, 웹 UI)
3. 승인 대기 중 에이전트는 어떻게 처리되나요?
4. 승인이 거부되면 에이전트는 어떻게 하나요?
5. 승인 없이 자동으로 실행해도 되는 조건이 있나요?

---

## Approval Gate 설계

```python
from dataclasses import dataclass
from enum import Enum

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"

@dataclass
class ApprovalRequest:
    request_id: str
    action: str
    details: dict
    risk_level: str  # low | medium | high
    requester: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    rejection_reason: str | None = None
```

## 위험도 기반 자동 승인

```python
def should_auto_approve(request: ApprovalRequest) -> bool:
    """위험도가 낮은 작업은 자동 승인"""
    if request.risk_level == "low":
        return True
    return False

def process_approval(request: ApprovalRequest, approval_backend) -> ApprovalStatus:
    if should_auto_approve(request):
        return ApprovalStatus.APPROVED

    # 실제 승인 요청 전송
    approval_backend.send_request(request)

    # 타임아웃 대기
    status = approval_backend.wait_for_response(
        request.request_id,
        timeout_seconds=300,
    )
    return status
```

## 에이전트 파이프라인에 통합

```python
def agent_pipeline_with_gate(task: dict, approval_backend) -> dict:
    # 1단계: 분석 (승인 불필요)
    analysis = run_analysis(task)

    # 2단계: 승인 게이트
    request = ApprovalRequest(
        request_id=f"req_{task['id']}",
        action="외부 API 호출 및 데이터 변경",
        details={"analysis": analysis, "estimated_impact": "고객 데이터 수정"},
        risk_level="high",
        requester="agent",
    )

    status = process_approval(request, approval_backend)

    if status == ApprovalStatus.REJECTED:
        return {"success": False, "reason": "승인 거부됨"}
    if status == ApprovalStatus.TIMEOUT:
        return {"success": False, "reason": "승인 타임아웃"}

    # 3단계: 승인 후 실행
    result = run_action(analysis)
    return {"success": True, "result": result}
```

---

## Before / After

| 항목 | Before (승인 없음) | After (Approval Gate) |
|------|------------------|-----------------------|
| 중요 작업 | 자동 실행 | 승인 후 실행 |
| 거부 처리 | 없음 | rejection_reason 반환 |
| 위험도 구분 | 없음 | low/medium/high 분류 |
| 타임아웃 | 무한 대기 | timeout_seconds 설정 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 모든 작업 승인 요청 | 승인 피로 | 위험도 낮은 작업 자동 승인 |
| 타임아웃 없음 | 무한 대기 | timeout_seconds 필수 |
| 거부 이유 미기록 | 패턴 파악 불가 | rejection_reason 필드 |
| 승인 기록 없음 | 감사 추적 불가 | 모든 승인 요청 로그 |

---

## AI 활용 팁

```
에이전트 파이프라인에 Approval Gate를 추가해줘.
ApprovalRequest는 action, details, risk_level을 포함하고, 위험도가 낮은 작업은 자동 승인해야 해.
승인 요청은 슬랙 메시지로 전송하고, 5분 타임아웃 후 응답 없으면 TIMEOUT 처리해줘.
승인 거부 시 rejection_reason을 에이전트에게 반환해줘.
```

---

## 체크리스트

- [ ] ApprovalRequest dataclass 정의
- [ ] 위험도 기반 자동 승인 로직
- [ ] 승인 요청 전송 채널 구현(슬랙/이메일)
- [ ] 타임아웃 처리
- [ ] 거부 이유(rejection_reason) 반환
- [ ] 모든 승인 요청 로그 기록

---

## 처음 질문으로 돌아가기

"에이전트가 다 알아서 하면 좋지 않나요?" — 대부분은 그래도 됩니다. 하지만 되돌릴 수 없는 작업, 고객에게 영향을 주는 작업, 비용이 큰 작업은 사람이 한 번 확인해야 합니다. Approval Gate는 그 지점을 명시적으로 설계하는 것입니다.

---

## 정리

- 위험도(low/medium/high)로 자동 승인과 수동 승인을 구분한다
- 승인 요청에는 action, details, risk_level을 명시한다
- 타임아웃으로 무한 대기를 방지한다
- 모든 승인 요청을 로그로 남겨 감사 추적을 가능하게 한다

---

## 참고 자료

- [LangGraph Human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [Anthropic 에이전트 안전성](https://docs.anthropic.com/en/docs/build-with-claude/agentic-and-tool-use/best-practices-for-agentic-and-tool-use)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- Approval Gate 설계
- 위험도 기반 자동 승인
- 에이전트 파이프라인에 통합
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Approval, Human-in-the-loop
