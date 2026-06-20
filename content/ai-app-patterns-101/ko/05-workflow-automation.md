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

워크플로의 가치는 핸드오프 지점, 중간 데이터 형태, 실패를 드러내야 하는 위치를 고정해 두는 데 있습니다. 모델에게 자유를 더 줄수록 시스템 신뢰도가 떨어지는 경우가 많습니다.

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

## 구체적인 시나리오

**시나리오 A — 콘텐츠 검수 파이프라인**: 사용자가 블로그 글을 제출하면 (1) 글을 분류하고, (2) 카테고리별 검수 규칙을 적용하고, (3) 수정 사항을 제안하고, (4) 최종 승인 여부를 결정하는 워크플로를 자동화합니다.

**시나리오 B — 고객 문의 자동화**: 고객 문의가 들어오면 의도를 분류해 "불만", "문의", "요청" 중 하나로 판단하고, 각 유형에 맞는 전문 응답 파이프라인으로 라우팅합니다. 불만 처리는 공감 표현 + 해결책 + 에스컬레이션 옵션 세 단계가 필요하지만, 일반 문의는 단순 응답으로 충분합니다.

## 실습 1: 순차 체인

이메일 초안을 생성하고 → 검토하고 → 톤을 조정하는 3단계 체인입니다. 각 단계의 성공 여부를 체크해 실패 시 전체 파이프라인을 중단합니다.

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
    elapsed_ms: float = 0.0


def run_step(
    step_name: str,
    prompt: str,
    max_tokens: int = 512,
) -> ChainResult:
    """단일 체인 단계를 실행합니다."""
    import time
    start = time.time()
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
            elapsed_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return ChainResult(
            step=step_name,
            output="",
            success=False,
            error=str(e),
            elapsed_ms=(time.time() - start) * 1000,
        )


def email_drafting_chain(
    topic: str,
    recipient: str,
    tone: str = "professional",
) -> dict:
    """이메일 작성 3단계 체인: 초안 → 검토 → 톤 조정."""
    steps = []

    # 1단계: 초안 생성
    draft_result = run_step(
        "draft",
        f"다음 주제로 {recipient}에게 보낼 이메일 초안을 작성하세요:\n주제: {topic}",
        max_tokens=512,
    )
    steps.append(draft_result)

    if not draft_result.success:
        return {
            "success": False,
            "failed_at": "draft",
            "error": draft_result.error,
            "steps": [s.__dict__ for s in steps],
        }

    # 2단계: 검토 및 개선점 파악
    review_result = run_step(
        "review",
        f"다음 이메일 초안을 검토하고 개선이 필요한 부분을 3가지 지적하세요:\n\n{draft_result.output}",
        max_tokens=256,
    )
    steps.append(review_result)

    # 3단계: 톤 조정 (검토 실패해도 초안 기반으로 진행)
    feedback_text = review_result.output if review_result.success else "검토 없이 진행"
    final_result = run_step(
        "tone_adjust",
        (
            f"다음 이메일을 '{tone}' 톤으로 다시 작성하세요. "
            f"참고 피드백: {feedback_text}\n\n"
            f"원본:\n{draft_result.output}"
        ),
        max_tokens=512,
    )
    steps.append(final_result)

    return {
        "success": final_result.success,
        "final_email": final_result.output if final_result.success else None,
        "steps": [s.__dict__ for s in steps],
        "total_elapsed_ms": sum(s.elapsed_ms for s in steps),
    }


# 사용 예시
result = email_drafting_chain(
    topic="분기 성과 보고 미팅 일정 조율",
    recipient="팀 리더",
    tone="professional",
)
if result["success"]:
    print(result["final_email"])
    print(f"총 소요 시간: {result['total_elapsed_ms']:.0f}ms")
```

## 실습 2: 분류 기반 라우팅

입력을 먼저 분류한 뒤 전문화된 파이프라인으로 라우팅합니다. 분류 신뢰도가 낮으면 기본 핸들러로 폴백합니다.

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

LOW_CONFIDENCE_THRESHOLD = 0.60


def classify_intent(text: str) -> dict:
    """고객 메시지의 의도를 분류합니다."""
    categories_desc = "\n".join(
        f"- {k}: {v}" for k, v in INTENT_CATEGORIES.items()
    )
    prompt = f"""다음 고객 메시지의 의도를 분류하세요.

카테고리:
{categories_desc}

메시지: {text}

JSON으로만 응답:
{{"intent": "카테고리키", "confidence": 0.0-1.0, "urgency": "high/medium/low", "key_points": ["핵심1", "핵심2"]}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def handle_complaint(text: str, key_points: list[str]) -> str:
    """불만 메시지 전용 응답: 공감 → 해결책 → 에스컬레이션 옵션."""
    points_text = "\n".join(f"- {p}" for p in key_points)
    prompt = (
        "고객이 불만을 제기했습니다. 다음 구조로 응답하세요:\n"
        "1. 공감 표현\n2. 즉시 해결 방법\n3. 에스컬레이션 옵션 안내\n\n"
        f"불만 핵심 사항:\n{points_text}\n\n"
        f"전체 내용: {text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content


def handle_inquiry(text: str) -> str:
    """정보 문의 전용 응답: 명확한 답변 + 관련 추가 정보."""
    prompt = (
        "고객이 정보를 문의했습니다. "
        "명확하고 간결한 답변을 제공하고, 관련 추가 정보를 제안하세요.\n\n"
        f"문의 내용: {text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content


def handle_default(text: str) -> str:
    """기본 핸들러: 저신뢰도 또는 기타 분류."""
    return (
        "안녕하세요! 메시지를 받았습니다. "
        "더 정확한 도움을 드리기 위해 내용을 확인하고 24시간 이내에 답변 드리겠습니다."
    )


def route_and_handle(customer_message: str) -> dict:
    """의도를 분류하고 적절한 핸들러로 라우팅합니다."""
    intent_result = classify_intent(customer_message)
    intent = intent_result.get("intent", "other")
    confidence = intent_result.get("confidence", 0.0)
    key_points = intent_result.get("key_points", [])

    # 저신뢰도는 기본 핸들러로
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        response = handle_default(customer_message)
        route = "low_confidence_fallback"
    elif intent == "complaint":
        response = handle_complaint(customer_message, key_points)
        route = "complaint_pipeline"
    elif intent == "inquiry":
        response = handle_inquiry(customer_message)
        route = "inquiry_pipeline"
    else:
        response = handle_default(customer_message)
        route = "default_pipeline"

    return {
        "intent": intent,
        "confidence": confidence,
        "urgency": intent_result.get("urgency", "medium"),
        "route": route,
        "response": response,
    }


# 테스트
messages = [
    "주문한 상품이 일주일째 배송이 안 됩니다. 이게 말이 되나요?",
    "할인 쿠폰 사용 방법을 알려주세요.",
    "앱이 가끔 느려지는 것 같은데 조금 더 빠르게 만들어주실 수 있나요?",
]

for msg in messages:
    result = route_and_handle(msg)
    print(f"\n메시지: {msg[:50]}...")
    print(f"분류: {result['intent']} (신뢰도: {result['confidence']:.2f}, 경로: {result['route']})")
```

## 실습 3: 상태 머신 워크플로

문서 검토 프로세스를 상태 머신으로 모델링합니다. 상태를 명시적으로 추적하면 장애 복구와 감사가 쉬워집니다.

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from openai import OpenAI
import json

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
        """상태 전환을 기록합니다. 현재 상태로 전환은 무시합니다."""
        if new_state == self.state:
            return
        old_state = self.state
        self.state = new_state
        self.history.append({
            "from": old_state.value,
            "to": new_state.value,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def can_transition_to(self, target: ReviewState) -> bool:
        """유효한 상태 전환인지 확인합니다."""
        valid_transitions = {
            ReviewState.SUBMITTED: {ReviewState.ANALYZING},
            ReviewState.ANALYZING: {ReviewState.REVIEW_NEEDED, ReviewState.APPROVED},
            ReviewState.REVIEW_NEEDED: {ReviewState.APPROVED, ReviewState.REJECTED},
        }
        return target in valid_transitions.get(self.state, set())


def analyze_document(workflow: DocumentWorkflow) -> DocumentWorkflow:
    """문서를 분석해 위험 수준을 평가합니다."""
    if not workflow.can_transition_to(ReviewState.ANALYZING):
        raise ValueError(f"현재 상태 {workflow.state.value}에서 ANALYZING으로 전환 불가")

    workflow.transition(ReviewState.ANALYZING, "자동 분석 시작")

    prompt = (
        "다음 문서를 분석하고 위험 수준을 평가하세요.\n\n"
        f"{workflow.content[:2000]}\n\n"
        "JSON으로만 응답:\n"
        '{"risk_level": "low/medium/high", "issues": ["이슈1", "이슈2"], '
        '"requires_human_review": true/false, "auto_approve_reason": "이유 또는 null"}'
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        response_format={"type": "json_object"},
    )

    workflow.analysis = json.loads(response.choices[0].message.content)

    if workflow.analysis.get("requires_human_review", True):
        workflow.transition(
            ReviewState.REVIEW_NEEDED,
            f"위험 수준: {workflow.analysis.get('risk_level', 'unknown')}",
        )
    else:
        workflow.transition(
            ReviewState.APPROVED,
            workflow.analysis.get("auto_approve_reason", "자동 승인 기준 충족"),
        )

    return workflow


def process_document(doc_id: str, content: str) -> DocumentWorkflow:
    """문서 워크플로를 처음부터 실행합니다."""
    workflow = DocumentWorkflow(doc_id=doc_id, content=content)
    workflow = analyze_document(workflow)

    print(f"\n[{doc_id}]")
    print(f"  최종 상태: {workflow.state.value}")
    print(f"  위험 수준: {workflow.analysis.get('risk_level', 'N/A')}")
    print(f"  이슈: {workflow.analysis.get('issues', [])}")
    print(f"  상태 이력:")
    for h in workflow.history:
        print(f"    {h['from']} → {h['to']}: {h['reason']}")

    return workflow


# 테스트
workflows = [
    process_document("doc_001", "일반적인 마케팅 이메일 초안입니다."),
    process_document("doc_002", "계약서 초안: 고객의 개인정보를 제3자에게 제공하는 조항 포함."),
]
```

## 실습 4: 체크포인트와 재시작

장기 워크플로에서 중간 결과를 저장해 실패 시 처음부터 재실행하지 않아도 됩니다.

```python
import json
from pathlib import Path


def save_checkpoint(run_id: str, step: str, data: dict) -> None:
    """워크플로 중간 결과를 파일로 저장합니다."""
    checkpoint_dir = Path(f".checkpoints/{run_id}")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_file = checkpoint_dir / f"{step}.json"
    with checkpoint_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_checkpoint(run_id: str, step: str) -> dict | None:
    """저장된 체크포인트를 불러옵니다."""
    checkpoint_file = Path(f".checkpoints/{run_id}/{step}.json")
    if not checkpoint_file.exists():
        return None
    with checkpoint_file.open(encoding="utf-8") as f:
        return json.load(f)


def run_workflow_with_checkpoints(
    run_id: str,
    text: str,
    resume_from: str | None = None,
) -> dict:
    """체크포인트를 활용한 재시작 가능한 워크플로입니다."""
    results = {}

    # 1단계: 분류 (이미 완료됐으면 스킵)
    if resume_from not in ("classify", None) or resume_from is None:
        if cached := load_checkpoint(run_id, "classify"):
            results["classify"] = cached
            print(f"[{run_id}] classify: 캐시 사용")
        else:
            # 실제 분류 로직 실행
            results["classify"] = {"category": "inquiry", "confidence": 0.9}
            save_checkpoint(run_id, "classify", results["classify"])
            print(f"[{run_id}] classify: 완료")

    # 2단계: 응답 생성
    if "classify" in results:
        if cached := load_checkpoint(run_id, "response"):
            results["response"] = cached
            print(f"[{run_id}] response: 캐시 사용")
        else:
            results["response"] = {"text": "생성된 응답..."}
            save_checkpoint(run_id, "response", results["response"])
            print(f"[{run_id}] response: 완료")

    return results
```

## 운영 체크리스트

- [ ] 체인의 각 단계에서 출력 유효성을 검증합니다.
- [ ] 중간 단계 실패 시 재시도 또는 대체 경로가 있습니다.
- [ ] 분류 결과에 신뢰도 임계값 필터가 적용됩니다.
- [ ] 상태 머신의 모든 상태 전환이 로깅됩니다.
- [ ] 체크포인트로 실패 시 중간 단계부터 재시작할 수 있습니다.
- [ ] 상태 전환 유효성 검사가 코드로 강제됩니다.
- [ ] 전체 워크플로 실행 시간이 단계별로 측정됩니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 체인 단계 실패를 무시 | 잘못된 입력으로 다음 단계 진행, 품질 저하 | 각 단계 후 success 체크 및 중단 로직 |
| 분류 신뢰도 낮아도 라우팅 | 잘못된 파이프라인으로 처리 | 신뢰도 0.6 미만은 기본 핸들러로 폴백 |
| 상태 전환 기록 없음 | 어느 단계에서 실패했는지 추적 불가 | history 배열에 모든 전환 기록 |
| 긴 체인에 레이턴시 확인 없음 | 전체 파이프라인이 너무 느림 | 각 단계 시간을 측정하고 병렬화 검토 |
| 중간 결과물 저장 없음 | 실패 시 처음부터 재실행 필요 | 단계별 체크포인트 저장 구현 |
| 상태 전환 유효성 미검사 | 잘못된 상태 전환으로 데이터 무결성 손상 | can_transition_to() 메서드로 전환 전 검증 |
| 분류와 응답 생성을 한 단계에서 처리 | 분류 오류 시 원인 분리 불가 | 단계를 명확히 분리하고 각각 검증 |
| 워크플로 실행 메타데이터 미저장 | 성능 병목 파악 불가 | run_id, elapsed_ms, stopped_reason 저장 |

## 처음 질문으로 돌아가기

- **LLM 작업을 여러 단계로 분해하면 어떤 이점이 있을까요?**
  각 단계를 독립적으로 검증하고 재시도할 수 있어 전체 파이프라인의 신뢰성이 높아집니다. 어느 단계에서 오류가 났는지 정확히 파악할 수 있고, 단계별로 다른 모델이나 프롬프트를 사용해 최적화할 수 있습니다.

- **분류 기반 라우팅은 어떤 상황에서 효과적일까요?**
  입력 유형이 다양하고 각 유형에 맞는 전문화된 응답이 필요할 때 효과적입니다. 단일 범용 프롬프트보다 전문화된 프롬프트가 일반적으로 품질이 높습니다. 분류 신뢰도가 낮을 때 폴백 핸들러를 두는 것이 안전합니다.

- **상태 머신으로 LLM 워크플로를 설계하면 무엇이 달라질까요?**
  현재 상태를 명시적으로 추적할 수 있어 장애 복구와 재시작이 가능해집니다. 상태 전환 유효성을 코드로 강제할 수 있고, 이력으로 처리 과정을 감사할 수 있습니다.

- **체인의 중간 단계 실패를 어떻게 처리해야 할까요?**
  각 단계 결과에 success 플래그를 두고, 실패 시 즉시 파이프라인을 중단합니다. 체크포인트를 저장해 실패한 단계부터 재시작할 수 있게 하면 긴 파이프라인에서 비용과 시간을 절약할 수 있습니다.

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
