---
title: 'Human-in-the-loop — 사람 개입 설계 패턴'
series: ai-app-patterns-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- RAG
- Agent
- Python
last_reviewed: '2026-05-01'
---

# Human-in-the-loop — 사람 개입 설계 패턴

## 이 글에서 답할 질문

- AI 초안을 바로 보내지 않고 사람 승인 단계를 넣어야 하는 기준은 무엇일까요?
- 낮은 신뢰도 결과만 사람에게 보내는 분기 패턴은 어떻게 구현할 수 있을까요?
- HITL 흐름을 데모 코드에서 재현하면서도 자동 실행 검증을 가능하게 하려면 어떻게 설계해야 할까요?

> Human-in-the-loop는 자동화를 포기하는 패턴이 아니라, 위험한 지점에서만 사람 판단을 끼워 넣는 제어 장치입니다.

![이 글에서 답할 질문](../../../assets/ai-app-patterns-101/06/06-01-questions-this-post-answers.ko.png)
> AI 앱 패턴 101 시리즈 (6/6)

예제 코드: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/ko/06-human-in-the-loop)

완전 자동화 파이프라인이 항상 옳지는 않습니다. 민감한 고객 데이터를 다루거나, 법적 효력이 있는 문서를 작성하거나, 금전적 결정을 내리는 경우에는 AI 출력 결과를 사람이 검토하고 승인해야 합니다. Human-in-the-loop(HITL)는 이런 경우를 위해 파이프라인 중간에 사람의 판단 지점을 만드는 패턴입니다.

이번 글에서는 다음을 다룹니다.

- HITL이 필요한 상황
- 승인 게이트 구현 패턴
- 신뢰도 기반 자동/수동 분기
- 감사 로그와 추적

---

## HITL이 필요한 상황

### 위험도에 따른 사람 개입 범위

![위험도에 따른 사람 개입 범위](../../../assets/ai-app-patterns-101/06/06-01-human-review-by-risk-level.ko.png)
모든 작업에 HITL이 필요한 것은 아닙니다. 다음 경우에 적합합니다.

**고위험 결정**: 금전 이체, 계약 생성, 개인정보 처리처럼 실수의 비용이 큰 경우입니다.

**낮은 신뢰도**: 모델이 확신하지 못하는 경우 사람에게 넘깁니다.

**규정 준수**: 특정 산업에서 AI 단독 결정이 법적으로 허용되지 않는 경우입니다.

**신뢰 구축 단계**: 새로운 AI 시스템을 처음 도입할 때 전수 검토로 시작해서 신뢰가 쌓이면 자동화 비율을 높입니다.

---

## 기본 승인 게이트

### 초안 생성과 승인 게이트 흐름

![초안 생성과 승인 게이트 흐름](../../../assets/ai-app-patterns-101/06/06-02-draft-generation-with-approval-gate.ko.png)
가장 단순한 HITL 패턴은 파이프라인 중간에 사람의 입력을 기다리는 것입니다.

```python
import os
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

draft_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 고객 서비스 담당자입니다.\n"
        "고객 문의에 대한 답변 초안을 작성하세요.\n"
        "정중하고 전문적으로 작성하세요.",
    ),
    ("human", "고객 문의:\n{inquiry}"),
])

draft_chain = draft_prompt | llm | StrOutputParser()

refine_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "답변 초안을 담당자의 피드백을 반영해 수정하세요.\n"
        "피드백 내용을 충실히 반영하되, 전문적인 톤을 유지하세요.",
    ),
    ("human", "초안:\n{draft}\n\n피드백:\n{feedback}"),
])

refine_chain = refine_prompt | llm | StrOutputParser()

def draft_with_human_review(inquiry: str) -> str:
    """초안 생성 → 사람 검토 → 필요시 수정 → 최종 답변."""
    # 1단계: 초안 생성
    draft = draft_chain.invoke({"inquiry": inquiry})
    print(f"\n=== 생성된 초안 ===\n{draft}\n")

    # 2단계: 사람 검토 (승인 게이트)
    print("담당자 검토:")
    print("  [1] 승인 — 초안을 그대로 사용합니다")
    print("  [2] 수정 — 피드백을 입력해 초안을 개선합니다")
    print("  [3] 거부 — 이 답변을 사용하지 않습니다")

    choice = input("선택 (1/2/3): ").strip()

    if choice == "1":
        return draft
    elif choice == "2":
        feedback = input("피드백을 입력하세요: ").strip()
        refined = refine_chain.invoke({"draft": draft, "feedback": feedback})
        print(f"\n=== 수정된 답변 ===\n{refined}")
        return refined
    else:
        print("답변이 거부되었습니다.")
        return ""

inquiry = "3주 전에 주문한 상품이 아직 도착하지 않았습니다. 어떻게 된 건가요?"
final_response = draft_with_human_review(inquiry)
if final_response:
    print(f"\n=== 최종 발송 답변 ===\n{final_response}")
```

---

## 신뢰도 기반 자동/수동 분기

### 신뢰도 임계값 라우팅 구조

![신뢰도 임계값 라우팅 구조](../../../assets/ai-app-patterns-101/06/06-03-confidence-threshold-routing.ko.png)
LLM에 신뢰도 점수를 함께 반환하도록 하고, 점수가 낮으면 자동으로 사람 검토 경로로 보냅니다.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

classify_with_confidence_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "다음 텍스트를 분류하고 신뢰도를 평가하세요.\n"
        "JSON만 반환하세요.\n"
        '형식: {{"category": "카테고리", "confidence": 0.0~1.0, "reason": "근거"}}',
    ),
    ("human", "{text}"),
])

chain = classify_with_confidence_prompt | llm | JsonOutputParser()

CONFIDENCE_THRESHOLD = 0.85

def classify_with_hitl(text: str) -> dict:
    """신뢰도가 낮으면 사람 검토로 라우팅."""
    result = chain.invoke({"text": text})
    confidence = result.get("confidence", 0.0)

    if confidence >= CONFIDENCE_THRESHOLD:
        result["reviewed_by"] = "auto"
        print(f"자동 분류: {result['category']} (신뢰도 {confidence:.2f})")
    else:
        print(f"낮은 신뢰도 ({confidence:.2f}) — 수동 검토 필요")
        print(f"AI 제안 카테고리: {result['category']}")
        print(f"근거: {result['reason']}")
        human_category = input("올바른 카테고리를 입력하세요: ").strip()
        result["category"] = human_category
        result["reviewed_by"] = "human"

    return result

texts = [
    "2024년 3분기 매출이 전년 동기 대비 23% 증가했습니다.",   # 명확한 경우
    "제품이 생각보다 좀 달랐어요.",                             # 모호한 경우
]

for text in texts:
    print(f"\n텍스트: {text}")
    result = classify_with_hitl(text)
    print(f"결과: {result}")
```

---

## 감사 로그

### 검토 결정과 감사 로그 기록 구조

![검토 결정과 감사 로그 기록 구조](../../../assets/ai-app-patterns-101/06/06-04-review-decisions-with-audit-events.ko.png)
HITL 시스템에서는 누가, 언제, 무엇을 검토했는지 기록이 필수입니다.

```python
import json
import os
from datetime import datetime
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

LOG_FILE = Path("audit_log.jsonl")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

generate_prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 요청에 대한 계약 조항 초안을 작성하세요."),
    ("human", "{request}"),
])

generate_chain = generate_prompt | llm | StrOutputParser()

def log_event(event_type: str, data: dict) -> None:
    """감사 이벤트를 JSONL 파일에 기록."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        **data,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def contract_clause_with_audit(request: str, reviewer_id: str) -> dict:
    """계약 조항 생성 → 감사 로그 → 사람 승인."""
    # 초안 생성
    draft = generate_chain.invoke({"request": request})
    log_event("draft_generated", {"request": request, "draft": draft})

    # 검토 요청
    print(f"\n초안:\n{draft}\n")
    approved = input("승인 (y/n): ").strip().lower() == "y"

    if approved:
        log_event("approved", {
            "reviewer_id": reviewer_id,
            "request": request,
            "draft": draft,
        })
        return {"status": "approved", "content": draft}
    else:
        reason = input("거부 이유: ").strip()
        log_event("rejected", {
            "reviewer_id": reviewer_id,
            "request": request,
            "draft": draft,
            "reason": reason,
        })
        return {"status": "rejected", "reason": reason}

result = contract_clause_with_audit(
    request="30일 이내 취소 시 전액 환불 조항",
    reviewer_id="reviewer_001",
)
print(f"\n결과: {result['status']}")
print(f"감사 로그: {LOG_FILE}")
```

---

## 이 코드에서 봐야 할 것

- `main.py`는 초안 생성 뒤 신뢰도 점수를 계산하고, 기준 미만이면 `input()` 기반 검토 단계로 넘어갑니다.
- 자동 검증을 위해 `HITL_DECISIONS` 환경변수에서 승인/수정 흐름을 읽어 실제 입력을 시뮬레이션합니다.
- 같은 구조를 웹 앱에서는 승인 큐와 운영자 콘솔로 바꾸면 됩니다.

---

## 실무에서 헷갈리는 지점

### 사람 피드백이 정책으로 돌아가는 루프

![사람 피드백이 정책으로 돌아가는 루프](../../../assets/ai-app-patterns-101/06/06-05-human-feedback-back-into-policy-loop.ko.png)
- HITL은 사람을 항상 마지막에 두는 패턴이 아닙니다. 분류 전, 전송 전, 결제 전 등 여러 위치에 들어갈 수 있습니다.
- 신뢰도 점수는 사실상 라우팅 힌트이지 객관적 진실값이 아닙니다. 사람 검토 기준은 별도 정책으로 정해야 합니다.
- 사람 검토를 넣으면 품질만 좋아지는 것이 아니라 처리량이 줄어듭니다. SLA와 운영 인력까지 같이 계산해야 합니다.

---

## 체크리스트

- [ ] 저위험 요청은 자동 승인 경로로 끝난다
- [ ] 고위험 또는 저신뢰 요청은 사람 검토 경로로 간다
- [ ] 검토 결정이 최종 결과에 반영된다
- [ ] 자동 실행 시에도 사람 선택이 환경변수로 재현 가능하다

---

## 마무리

HITL은 자동화를 포기하는 것이 아닙니다. 신뢰도가 높은 경우는 자동으로 처리하고, 불확실한 경우만 사람에게 넘기는 방식으로 자동화와 신뢰성을 동시에 얻을 수 있습니다. 감사 로그는 시스템의 신뢰도를 높이고, 나중에 모델을 개선하기 위한 데이터가 됩니다.

이 시리즈에서는 챗봇, RAG Q&A, 문서 어시스턴트, Agent, 워크플로 자동화, Human-in-the-loop까지 LLM 앱의 핵심 패턴 6가지를 다뤘습니다. 각 패턴은 독립적으로 쓸 수도 있고, 조합해서 복잡한 시스템을 만들 수도 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [챗봇 패턴 — 대화 이력 관리와 상태](./01-chatbot-pattern.md)
- [RAG Q&A 패턴 — 문서 기반 질의응답](./02-rag-qa-pattern.md)
- [문서 어시스턴트 — 요약, 추출, 분류](./03-document-assistant.md)
- [Agent + Tool 패턴 — 자율 도구 선택](./04-agent-tool-pattern.md)
- [워크플로 자동화 — 다단계 체인 설계](./05-workflow-automation.md)
- **Human-in-the-loop — 사람 개입 설계 패턴 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [LangGraph HITL 가이드](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/)
- [Human-in-the-loop AI 설계](https://arxiv.org/abs/2108.00018)
- [신뢰도 보정 (Calibration)](https://en.wikipedia.org/wiki/Calibration_(statistics))

Tags: LLM, RAG, Agent, Python
