---
title: "바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화"
series: ai-app-patterns-101
episode: 5
language: ko
tags:
- Workflow Automation
- Sequential Chain
- State Machine
- Routing
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화

이 글은 **바이브코딩을 위한 AI 앱 패턴** 시리즈의 다섯 번째 글입니다.

---

바이브코딩으로 AI 앱을 만들다 보면 "이메일 초안 작성 → 검토 → 전송"처럼 여러 단계를 순서대로 처리해야 하는 경우가 자주 생깁니다. 각 단계에서 이전 단계 결과를 받아 처리하고, 상황에 따라 다른 경로로 분기되는 구조입니다.

워크플로우 자동화의 핵심은 세 가지 패턴입니다. **순차 체인**(각 단계 결과를 다음 단계로 전달), **분류 기반 라우팅**(AI가 요청 유형을 판단해 다른 처리 경로 선택), **상태 머신**(문서 승인 같은 명확한 상태 전환 관리). 이 세 가지를 적절히 조합하면 복잡한 업무 프로세스를 AI로 자동화할 수 있습니다.

> "워크플로우 자동화는 단순히 AI를 여러 번 호출하는 것이 아닙니다. 각 단계의 입출력 계약을 명확히 하고, 상태를 투명하게 관리하는 것입니다."

## 이 글에서 다룰 질문

1. 순차 체인에서 각 단계를 어떻게 연결하나요?
2. AI 분류 기반 라우팅은 어떻게 구현하나요?
3. 상태 머신으로 복잡한 승인 프로세스를 어떻게 모델링하나요?
4. 체크포인트로 워크플로우를 중단 후 재개하는 방법은?
5. 낮은 신뢰도 분류 결과를 어떻게 처리하나요?

---

## 워크플로우 패턴 비교

| 패턴 | 특징 | 적합한 상황 |
|------|------|------------|
| 순차 체인 | 단계 A → B → C 고정 순서 | 항상 같은 처리 순서 |
| 분류 기반 라우팅 | 입력에 따라 다른 경로 | 여러 유형의 요청 처리 |
| 상태 머신 | 명확한 상태 전환 | 승인 프로세스, 다단계 검토 |

## Before / After: 이메일 초안 워크플로우

**Before (수동 단계)**
```python
# 각 단계가 독립적으로 실행되어 연결이 없음
subject = "분기 보고서"
body = llm.chat("이메일 본문 작성")
# 어디서 멈췄는지, 다음에 무엇을 해야 하는지 모름
```

**After (순차 체인)**
```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ChainResult:
    step_name: str
    input_data: Any
    output_data: Any
    success: bool
    error: str | None = None

def run_step(step_name: str, prompt: str, input_data: Any) -> ChainResult:
    """하나의 체인 단계를 실행합니다."""
    try:
        result = llm.chat(f"{prompt}\n\n입력: {input_data}")
        return ChainResult(step_name=step_name, input_data=input_data, output_data=result, success=True)
    except Exception as e:
        return ChainResult(step_name=step_name, input_data=input_data, output_data=None, success=False, error=str(e))

def email_drafting_chain(topic: str, recipient: str) -> dict:
    """이메일 초안 작성 3단계 체인."""
    # 1단계: 핵심 포인트 생성
    step1 = run_step(
        "key_points",
        f"{recipient}에게 보낼 이메일의 핵심 포인트 3가지를 작성하세요.",
        topic
    )
    if not step1.success:
        return {"success": False, "failed_at": "key_points", "error": step1.error}

    # 2단계: 초안 작성
    step2 = run_step(
        "draft",
        "핵심 포인트를 바탕으로 전문적인 이메일 초안을 작성하세요.",
        step1.output_data
    )
    if not step2.success:
        return {"success": False, "failed_at": "draft", "error": step2.error}

    # 3단계: 마지막 검토
    step3 = run_step(
        "review",
        "이메일을 검토하고 어조, 명확성, 전문성을 개선하세요.",
        step2.output_data
    )

    return {
        "success": step3.success,
        "final_email": step3.output_data,
        "steps": [step1, step2, step3]
    }
```

## 분류 기반 라우팅

```python
LOW_CONFIDENCE_THRESHOLD = 0.7

def classify_intent(text: str) -> dict:
    """사용자 요청의 의도를 분류합니다."""
    result = llm.chat(f"""다음 요청의 의도를 분류하고 신뢰도를 0-1로 평가하세요.
    카테고리: technical_support, billing, general_inquiry, complaint
    JSON으로 반환: {{"category": "...", "confidence": 0.0-1.0}}

    요청: {text}""", response_format={"type": "json_object"})

    return json.loads(result)

def route_and_handle(text: str) -> str:
    """분류 결과에 따라 요청을 라우팅합니다."""
    classification = classify_intent(text)

    # 신뢰도가 낮으면 사람에게 에스컬레이션
    if classification["confidence"] < LOW_CONFIDENCE_THRESHOLD:
        return escalate_to_human(text, reason="낮은 분류 신뢰도")

    handlers = {
        "technical_support": handle_technical,
        "billing": handle_billing,
        "general_inquiry": handle_general,
        "complaint": handle_complaint
    }

    handler = handlers.get(classification["category"], handle_general)
    return handler(text)
```

## 상태 머신: 문서 승인 프로세스

```python
from enum import Enum

class ReviewState(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_NEEDED = "revision_needed"

class DocumentWorkflow:
    VALID_TRANSITIONS = {
        ReviewState.DRAFT: [ReviewState.UNDER_REVIEW],
        ReviewState.UNDER_REVIEW: [ReviewState.APPROVED, ReviewState.REJECTED, ReviewState.REVISION_NEEDED],
        ReviewState.REVISION_NEEDED: [ReviewState.DRAFT],
        ReviewState.APPROVED: [],
        ReviewState.REJECTED: []
    }

    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.state = ReviewState.DRAFT
        self.history = []

    def can_transition_to(self, new_state: ReviewState) -> bool:
        return new_state in self.VALID_TRANSITIONS.get(self.state, [])

    def transition(self, new_state: ReviewState, reason: str = "") -> bool:
        if not self.can_transition_to(new_state):
            raise ValueError(f"{self.state.value} → {new_state.value} 전환 불가")
        self.history.append({"from": self.state.value, "to": new_state.value, "reason": reason})
        self.state = new_state
        return True
```

## 체크포인트로 워크플로우 재개

```python
import json
from pathlib import Path

def save_checkpoint(workflow_id: str, step: int, state: dict):
    """워크플로우 진행 상태를 저장합니다."""
    checkpoint = {"workflow_id": workflow_id, "step": step, "state": state}
    Path(f"checkpoints/{workflow_id}.json").write_text(json.dumps(checkpoint))

def load_checkpoint(workflow_id: str) -> dict | None:
    """저장된 체크포인트를 불러옵니다."""
    path = Path(f"checkpoints/{workflow_id}.json")
    return json.loads(path.read_text()) if path.exists() else None
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 단계 실패 시 전체 중단 | 앞 단계 작업이 모두 소실 | 체크포인트로 중간 저장 |
| 낮은 신뢰도 분류를 강행 | 잘못된 핸들러 실행 | 임계값 이하면 에스컬레이션 |
| 상태 전환 검증 없음 | 잘못된 상태 전환 발생 | VALID_TRANSITIONS로 전환 검증 |
| 단계별 결과 기록 없음 | 어디서 실패했는지 모름 | ChainResult로 각 단계 기록 |

## AI 팁

워크플로우가 복잡해질수록 각 단계의 입출력 형식을 Pydantic으로 명시적으로 정의하면 단계 간 데이터 전달 오류를 줄일 수 있습니다. 또한 체크포인트를 주기적으로 저장하면 장시간 실행 워크플로우가 중간에 실패해도 처음부터 다시 시작할 필요가 없습니다.

낮은 신뢰도 분류를 처리할 때는 "확실하지 않으면 사람에게 물어보라"는 원칙이 가장 안전합니다.

## 체크리스트

- [ ] 각 체인 단계의 입출력 형식을 명확히 정의했다
- [ ] 체크포인트로 워크플로우 중단/재개를 지원한다
- [ ] 분류 신뢰도가 낮을 때 에스컬레이션 경로가 있다
- [ ] 상태 머신의 유효 전환을 코드로 검증한다
- [ ] 각 단계 실행 결과를 로깅한다

## 처음 질문으로 돌아가기

**순차 체인에서 단계 연결 방법은?** 각 단계를 함수로 만들고, 이전 단계의 output_data를 다음 단계의 입력으로 전달합니다. ChainResult로 성공/실패를 추적합니다.

**AI 분류 기반 라우팅은?** LLM에게 요청을 분류하게 하고, 신뢰도가 충분할 때만 자동 라우팅합니다. 낮은 신뢰도는 사람에게 에스컬레이션합니다.

**상태 머신으로 승인 프로세스 모델링은?** 가능한 상태와 유효한 전환을 딕셔너리로 정의하고, 전환 전에 `can_transition_to()`로 검증합니다.

**체크포인트로 재개는?** 각 단계 완료 시 현재 상태를 파일/DB에 저장하고, 재시작 시 저장된 체크포인트에서 재개합니다.

**낮은 신뢰도 분류 처리는?** 임계값(예: 0.7) 이하의 신뢰도는 자동 처리하지 않고 사람이 검토하도록 에스컬레이션합니다.

## 정리

워크플로우 자동화는 순차 체인, 분류 기반 라우팅, 상태 머신 세 가지 패턴을 조합해 구현합니다. 각 단계의 입출력을 명확히 하고, 체크포인트로 재개 가능성을 보장하며, 낮은 신뢰도 상황에서는 사람에게 에스컬레이션하는 것이 핵심입니다.

다음 글에서는 AI 결정에 사람이 개입하는 **Human-in-the-Loop** 패턴을 다룹니다.

## 참고 자료

- [AI 앱 패턴 원문: 워크플로우 자동화](../ko/05-workflow-automation.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴](./01-chatbot-pattern.md)
2. [바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
3. [바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트](./03-document-assistant.md)
4. [바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴](./04-agent-tool-pattern.md)
5. **바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화 (현재 글)**
6. [바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop](./06-human-in-the-loop.md)
<!-- toc:end -->

Tags: Workflow Automation, Sequential Chain, State Machine, Routing, 바이브코딩
