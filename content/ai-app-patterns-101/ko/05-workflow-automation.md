---
series: ai-app-patterns-101
episode: 5
title: "AI App Patterns 101 (5/6): Workflow Automation 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Workflow
  - Chain
  - LLM
  - Classification
  - StateMachine
seo_description: 순차 체인, 분류 기반 라우팅, 상태 머신으로 LLM 워크플로를 자동화하는 핵심 패턴을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (5/6): Workflow Automation 패턴

LLM 하나로 모든 작업을 처리하려 하면 품질이 불안정해지고 실패 지점을 찾기 어려워집니다. Workflow Automation 패턴은 복잡한 작업을 작은 단계로 분해하고, 각 단계를 순서대로 또는 조건에 따라 실행하는 방식입니다. 순차 체인은 단계마다 결과를 검증하고, 분류 기반 라우팅은 입력에 따라 다른 파이프라인을 선택하며, 상태 머신은 복잡한 비즈니스 프로세스를 표현합니다.

이 글은 AI App Patterns 101 시리즈의 5번째 글입니다.

![Workflow Automation 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/05/05-01-concept-at-a-glance.ko.png)
*순차 체인, 라우팅, 상태 머신이 결합된 워크플로 자동화 구조*

## 이 글에서 다룰 문제

- LLM 작업을 여러 단계로 분해하면 어떤 이점이 있을까요?
- 분류 기반 라우팅은 어떤 상황에서 단일 프롬프트보다 효과적일까요?
- 상태 머신으로 LLM 워크플로를 설계하면 무엇이 달라질까요?
- 체인의 중간 단계 실패를 어떻게 처리해야 할까요?
- 워크플로를 재시도 가능하고 재현 가능하게 만드는 방법은 무엇일까요?

## 핵심 개념 한 줄 정리

- **Sequential Chain**: 이전 단계의 출력이 다음 단계의 입력이 되는 파이프라인 구조입니다.
- **Routing**: 입력의 분류 결과에 따라 다른 처리 경로를 선택하는 패턴입니다.
- **State Machine**: 현재 상태와 전환 조건을 명시적으로 정의하는 워크플로 모델입니다.
- **Intermediate Validation**: 체인의 각 단계 출력을 다음 단계 진행 전에 검증하는 과정입니다.
- **Idempotency**: 같은 입력에 대해 항상 같은 결과를 보장하는 설계 원칙입니다.

## 워크플로 패턴 비교

| 패턴 | 적합 상황 | 장점 | 단점 |
|---|---|---|---|
| 순차 체인 | 단계별 처리가 명확한 작업 | 단계 격리, 디버깅 용이 | 레이턴시 누적 |
| 분류 라우팅 | 다양한 입력 유형 처리 | 전문화된 프롬프트 사용 가능 | 분류 오류 시 잘못된 경로 |
| 상태 머신 | 복잡한 비즈니스 프로세스 | 상태 추적, 재시작 가능 | 구현 복잡도 |
| 병렬 처리 | 독립적인 서브태스크 | 속도 향상 | 상태 동기화 필요 |

## 실습 1: 순차 체인

이메일 초안을 생성하고 → 검토하고 → 톤을 조정하는 3단계 체인입니다.

```python
from openai import OpenAI
from dataclasses import dataclass

client = OpenAI()


@dataclass
class ChainResult:
    step: str
    output: str
    success: bool
    error: str | None = None


def run_step(
    step_name: str,
    prompt: str,
    max_tokens: int = 512,
) -> ChainResult:
    """단일 체인 단계를 실행합니다."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return ChainResult(
            step=step_name,
            output=response.choices[0].message.content,
            success=True,
        )
    except Exception as e:
        return ChainResult(
            step=step_name,
            output="",
            success=False,
            error=str(e),
        )


def email_drafting_chain(
    topic: str,
    recipient: str,
    tone: str = "professional",
) -> dict:
    """이메일 작성 3단계 체인: 초안 → 검토 → 톤 조정."""
    results = []

    # 1단계: 초안 생성
    draft_result = run_step(
        "draft",
        f"다음 주제로 {recipient}에게 보낼 이메일 초안을 작성하세요:\n주제: {topic}",
        max_tokens=512,
    )
    results.append(draft_result)

    if not draft_result.success:
        return {"success": False, "error": draft_result.error, "steps": results}

    # 2단계: 검토 및 개선점 파악
    review_result = run_step(
        "review",
        f"다음 이메일 초안을 검토하고 개선이 필요한 부분을 3가지 지적하세요:\n\n{draft_result.output}",
        max_tokens=256,
    )
    results.append(review_result)

    # 3단계: 톤 조정
    final_result = run_step(
        "tone_adjust",
        (
            f"다음 이메일을 '{tone}' 톤으로 다시 작성하세요. "
            f"개선 사항: {review_result.output if review_result.success else '없음'}\n\n"
            f"원본:\n{draft_result.output}"
        ),
        max_tokens=512,
    )
    results.append(final_result)

    return {
        "success": final_result.success,
        "final_email": final_result.output if final_result.success else None,
        "steps": results,
    }


# 사용 예시
result = email_drafting_chain(
    topic="분기 성과 보고 미팅 일정 조율",
    recipient="팀 리더",
    tone="professional",
)
if result["success"]:
    print(result["final_email"])
```

## 실습 2: 분류 기반 라우팅

입력을 먼저 분류한 뒤 전문화된 파이프라인으로 라우팅합니다.

```python
from openai import OpenAI
import json

client = OpenAI()

INTENT_CATEGORIES = {
    "complaint": "불만 및 문제 보고",
    "inquiry": "정보 문의",
    "request": "기능 또는 서비스 요청",
    "praise": "긍정적 피드백",
    "other": "기타",
}


def classify_intent(text: str) -> dict:
    """고객 메시지의 의도를 분류합니다."""
    categories_desc = "\n".join(
        f"- {k}: {v}" for k, v in INTENT_CATEGORIES.items()
    )
    prompt = f"""다음 고객 메시지의 의도를 분류하세요.

카테고리:
{categories_desc}

메시지: {text}

JSON으로만 응답: {{"intent": "카테고리키", "confidence": 0.0-1.0, "urgency": "high/medium/low"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def handle_complaint(text: str) -> str:
    """불만 메시지 전용 응답 생성입니다."""
    prompt = (
        "고객이 불만을 제기했습니다. 공감을 표현하고, 즉시 해결 방법을 제안하고, "
        "에스컬레이션 옵션을 안내하는 응답을 작성하세요.\n\n"
        f"불만 내용: {text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content


def handle_inquiry(text: str) -> str:
    """정보 문의 전용 응답 생성입니다."""
    prompt = (
        "고객이 정보를 문의했습니다. 명확하고 간결한 답변을 제공하고, "
        "관련 추가 정보를 제안하세요.\n\n"
        f"문의 내용: {text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content


def route_and_handle(customer_message: str) -> dict:
    """의도를 분류하고 적절한 핸들러로 라우팅합니다."""
    intent_result = classify_intent(customer_message)
    intent = intent_result.get("intent", "other")

    handlers = {
        "complaint": handle_complaint,
        "inquiry": handle_inquiry,
    }

    handler = handlers.get(intent)
    if handler:
        response = handler(customer_message)
    else:
        # 기본 핸들러
        response = f"안녕하세요! 말씀해 주셔서 감사합니다. {customer_message[:50]}..."

    return {
        "intent": intent,
        "confidence": intent_result.get("confidence", 0.0),
        "urgency": intent_result.get("urgency", "medium"),
        "response": response,
    }
```

## 실습 3: 상태 머신 워크플로

문서 검토 프로세스를 상태 머신으로 모델링합니다.

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from openai import OpenAI

client = OpenAI()


class ReviewState(Enum):
    SUBMITTED = "submitted"
    ANALYZING = "analyzing"
    REVIEW_NEEDED = "review_needed"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class DocumentWorkflow:
    doc_id: str
    content: str
    state: ReviewState = ReviewState.SUBMITTED
    analysis: dict = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)

    def transition(self, new_state: ReviewState, reason: str = "") -> None:
        """상태 전환을 기록합니다."""
        old_state = self.state
        self.state = new_state
        self.history.append({
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })


def analyze_document(workflow: DocumentWorkflow) -> DocumentWorkflow:
    """문서를 분석해 위험 수준을 평가합니다."""
    workflow.transition(ReviewState.ANALYZING, "자동 분석 시작")

    prompt = (
        "다음 문서를 분석하고 위험 수준을 평가하세요.\n\n"
        f"{workflow.content[:2000]}\n\n"
        "JSON으로만 응답: {"
        '"risk_level": "low/medium/high", '
        '"issues": ["이슈1", "이슈2"], '
        '"requires_human_review": true/false'
        "}"
    )

    import json
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        response_format={"type": "json_object"},
    )

    workflow.analysis = json.loads(response.choices[0].message.content)

    if workflow.analysis.get("requires_human_review", True):
        workflow.transition(ReviewState.REVIEW_NEEDED, "고위험 또는 검토 필요")
    else:
        workflow.transition(ReviewState.APPROVED, "자동 승인 기준 충족")

    return workflow


def process_document(doc_id: str, content: str) -> DocumentWorkflow:
    """문서 워크플로를 처음부터 실행합니다."""
    workflow = DocumentWorkflow(doc_id=doc_id, content=content)
    workflow = analyze_document(workflow)

    print(f"[{doc_id}] 최종 상태: {workflow.state.value}")
    print(f"[{doc_id}] 분석 결과: {workflow.analysis}")
    print(f"[{doc_id}] 상태 이력: {len(workflow.history)}단계")

    return workflow
```

## 운영 체크리스트

- [ ] 체인의 각 단계에서 출력 유효성을 검증합니다.
- [ ] 중간 단계 실패 시 재시도 또는 대체 경로가 있습니다.
- [ ] 분류 결과에 신뢰도 임계값 필터가 적용됩니다.
- [ ] 상태 머신의 모든 상태 전환이 로깅됩니다.
- [ ] 워크플로 실행 결과가 재현 가능하도록 입력과 출력이 저장됩니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 체인 단계 실패를 무시 | 잘못된 입력으로 다음 단계 진행 | 각 단계 후 success 체크 및 중단 로직 |
| 분류 신뢰도 낮아도 라우팅 | 잘못된 파이프라인으로 처리 | 신뢰도 0.6 미만은 기본 핸들러로 |
| 상태 전환 기록 없음 | 어느 단계에서 실패했는지 추적 불가 | history 배열에 모든 전환 기록 |
| 긴 체인에 레이턴시 확인 없음 | 전체 파이프라인이 너무 느림 | 각 단계 시간을 측정하고 병렬화 검토 |
| 중간 결과물 저장 없음 | 실패 시 처음부터 재실행 필요 | 단계별 체크포인트 저장 구현 |

## 처음 질문으로 돌아가기

- **LLM 작업을 여러 단계로 분해하면 어떤 이점이 있을까요?**
  각 단계를 독립적으로 검증하고 재시도할 수 있어 전체 파이프라인의 신뢰성이 높아집니다. 어느 단계에서 오류가 났는지 정확히 파악할 수 있고, 단계별로 다른 모델이나 프롬프트를 사용해 최적화할 수 있습니다.

- **분류 기반 라우팅은 어떤 상황에서 효과적일까요?**
  입력 유형이 다양하고 각 유형에 맞는 전문화된 응답이 필요할 때 효과적입니다. 단일 범용 프롬프트보다 전문화된 프롬프트가 일반적으로 품질이 높습니다. 다만 분류 오류가 잘못된 파이프라인으로 이어질 수 있으므로 신뢰도 임계값 설정이 중요합니다.

- **상태 머신으로 LLM 워크플로를 설계하면 무엇이 달라질까요?**
  현재 상태를 명시적으로 추적할 수 있어 장애 복구와 재시작이 가능해집니다. 비즈니스 프로세스의 어느 단계에 있는지 언제든 조회할 수 있고, 상태 이력으로 처리 과정을 감사할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): Chatbot 패턴](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document Assistant 패턴](./03-document-assistant.md)
- [AI App Patterns 101 (4/6): Agent Tool 패턴](./04-agent-tool-pattern.md)
- **AI App Patterns 101 (5/6): Workflow Automation 패턴 (현재 글)**
- [AI App Patterns 101 (6/6): Human-in-the-Loop 패턴](./06-human-in-the-loop.md)

<!-- toc:end -->

## 참고 자료

- [LangChain — Sequential Chains](https://python.langchain.com/docs/modules/chains/)
- [LangGraph — State Machines for LLM](https://langchain-ai.github.io/langgraph/)
- [OpenAI — Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Martin Fowler — State Machine](https://martinfowler.com/bliki/StateMachine.html)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: Workflow, Chain, LLM, Classification, StateMachine
