---
title: 워크플로 자동화 — 다단계 체인 설계
series: ai-app-patterns-101
episode: 5
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
last_reviewed: '2026-05-12'
seo_description: 워크플로 자동화는 모델 선택권 대신 사람이 정의한 단계와 데이터 계약을 따르는 파이프라인입니다.
---

# 워크플로 자동화 — 다단계 체인 설계

작업 단계가 예측 가능할 때는 모델에게 자유를 더 주는 편이 오히려 시스템 신뢰도를 떨어뜨립니다. 워크플로의 가치는 handoff 지점, 중간 데이터 형태, 실패를 드러내야 하는 위치를 고정해 두는 데 있습니다.

한 번의 LLM 호출로는 잘 풀리지 않는 업무가 많습니다. 고객 문의를 받아 요약하고, 분류하고, 카테고리별 로직을 적용하고, 답변을 생성하는 식의 흐름이 대표적입니다. 이런 작업은 모델의 즉흥성보다 단계 간 계약이 더 중요합니다.

이 글은 AI App Patterns 101 시리즈의 5번째 글입니다. 여기서는 명시적인 단계와 깔끔한 데이터 계약을 가진 다단계 LLM 워크플로를 어떻게 설계할지 다룹니다.

## 이 글에서 다룰 문제

- 여러 LLM 단계를 연결할 때 중간 출력은 어떤 구조로 만들어야 할까요?
- 요약 → 분류 → 태깅 워크플로에서는 어느 지점에서 실패를 감지하고 드러내야 할까요?
- 어떤 상황에서 에이전트보다 고정 워크플로가 더 나을까요?

> 워크플로 자동화는 모델의 선택권을 줄이고, 사람이 정의한 단계와 데이터 계약을 따르는 파이프라인으로 바꾸는 설계입니다.

![이 글에서 답할 질문](../../../assets/ai-app-patterns-101/05/05-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*
> AI App Patterns 101 (5/6)

예제 코드: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/en/05-workflow-automation)

어떤 작업은 단일 LLM 호출로는 버티기 어렵습니다. 고객 문의를 받고, 분류하고, 카테고리별 로직을 적용하고, 마지막 답변을 만드는 흐름이 그렇습니다. 워크플로 자동화는 이런 단계를 LangChain LCEL로 연결해 하나의 일관된 파이프라인으로 만듭니다.

다룰 주제는 다음과 같습니다.

- 순차 체인 만들기
- 라우팅 — 중간 출력에 따라 분기하기
- 실용적인 다단계 코드 리뷰 파이프라인
- 각 단계의 출력을 다음 단계로 깔끔하게 전달하기

---

## 순차 체인

### 단계 사이의 순차 handoff

![단계 사이의 순차 handoff](../../../assets/ai-app-patterns-101/05/05-01-sequential-handoff-across-stages.ko.png)

*단계 사이의 순차 handoff*
### 병렬 작업을 포함한 DAG 스타일 분기

![병렬 작업을 포함한 DAG 스타일 분기](../../../assets/ai-app-patterns-101/05/05-02-dag-style-branching-with-parallel-work.ko.png)

*병렬 작업을 포함한 DAG 스타일 분기*
LCEL의 `|` 연산자는 단계를 연결합니다. 왼쪽 단계의 출력이 오른쪽 단계의 입력이 됩니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate the following text to {target_language}. Return only the translation."),
    ("human", "{text}"),
])

summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following text in two sentences."),
    ("human", "{text}"),
])

title_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a one-line title for the following text."),
    ("human", "{text}"),
])

str_parser = StrOutputParser()

def make_pipeline(target_language: str):
    """Return translate → summarize → title functions for the given language."""

    def translate(inputs: dict) -> dict:
        translated = (translate_prompt | llm | str_parser).invoke({
            "text": inputs["text"],
            "target_language": target_language,
        })
        return {"text": translated}

    def summarize(inputs: dict) -> dict:
        summary = (summarize_prompt | llm | str_parser).invoke(inputs)
        return {"text": summary}

    def make_title(inputs: dict) -> str:
        return (title_prompt | llm | str_parser).invoke(inputs)

    return translate, summarize, make_title

article = """
Artificial intelligence is transforming the way businesses operate.
Companies across industries are adopting AI tools to automate repetitive tasks,
improve decision-making, and personalize customer experiences.
The healthcare sector uses AI to assist in diagnosis and drug discovery.
In finance, AI powers fraud detection and algorithmic trading.
As AI becomes more capable, organizations must also address ethical considerations
such as bias, transparency, and data privacy.
"""

translate_fn, summarize_fn, title_fn = make_pipeline("Korean")

step1 = translate_fn({"text": article})
print(f"translation:\n{step1['text']}\n")

step2 = summarize_fn(step1)
print(f"summary:\n{step2['text']}\n")

step3 = title_fn(step2)
print(f"title: {step3}")
```

---

## 라우팅 — 분류 기반 분기

### 분류가 결정하는 라우팅

![분류가 결정하는 라우팅](../../../assets/ai-app-patterns-101/05/05-03-classification-driven-routing.ko.png)

*분류가 결정하는 라우팅*
### 승인 게이트와 재시도 복구

![승인 게이트와 재시도 복구](../../../assets/ai-app-patterns-101/05/05-04-approval-gate-and-retry-recovery.ko.png)

*승인 게이트와 재시도 복구*
먼저 입력을 분류하고, 그 결과에 따라 적절한 체인으로 보냅니다. 두 단계 사이의 유일한 의존성은 분류기의 출력입니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)
str_parser = StrOutputParser()

classify_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Classify the following customer inquiry.\n"
        "Categories: BILLING, TECHNICAL, GENERAL\n"
        "Return the category name only. No other text.",
    ),
    ("human", "{inquiry}"),
])
classify_chain = classify_prompt | llm | str_parser

billing_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a billing specialist.\n"
        "Handle refunds, invoices, and charge-related inquiries.\n"
        "Be accurate and reassuring.",
    ),
    ("human", "{inquiry}"),
])

technical_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a technical support engineer.\n"
        "Handle bugs, errors, and how-to questions.\n"
        "Guide users step by step.",
    ),
    ("human", "{inquiry}"),
])

general_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a customer service representative.\n"
        "Handle general inquiries politely and helpfully.",
    ),
    ("human", "{inquiry}"),
])

billing_chain = billing_prompt | llm | str_parser
technical_chain = technical_prompt | llm | str_parser
general_chain = general_prompt | llm | str_parser

def route_and_respond(inquiry: str) -> dict:
    """Classify → route → generate specialist response."""
    category = classify_chain.invoke({"inquiry": inquiry}).strip().upper()

    chains = {
        "BILLING": billing_chain,
        "TECHNICAL": technical_chain,
        "GENERAL": general_chain,
    }
    chain = chains.get(category, general_chain)
    response = chain.invoke({"inquiry": inquiry})

    return {"category": category, "response": response}

test_inquiries = [
    "My bill doubled this month without any explanation. Please check.",
    "The app keeps crashing when I open it. What should I do?",
    "What are your business hours?",
]

for inquiry in test_inquiries:
    print(f"\ninquiry: {inquiry}")
    result = route_and_respond(inquiry)
    print(f"category: {result['category']}")
    print(f"response: {result['response']}")
```

---

## 다단계 데이터 변환 파이프라인

### 코드 리뷰 산출물 계약

![코드 리뷰 산출물 계약](../../../assets/ai-app-patterns-101/05/05-05-code-review-artifact-contract.ko.png)

*코드 리뷰 산출물 계약*
각 단계는 이전 단계의 출력을 다른 형태로 변환합니다. 아래 코드 리뷰 파이프라인은 analysis → suggestions → report라는 세 단계 변환을 보여 줍니다.

> 멘탈 모델은 각 단계를 작은 서비스처럼 보는 것입니다. 이전 단계가 불분명한 문자열을 넘기면 다음 단계는 조용히 실패합니다. 계약이 분명한 `dict`를 넘기면 로깅, 검증, 재시도가 훨씬 쉬워집니다.

```python
import os

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

analyze_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Analyze the following code and return JSON only.\n"
        'Format: {{"language": "lang", "purpose": "purpose", "issues": ["issue list"], "score": 1-10}}',
    ),
    ("human", "Code:\n{code}"),
])

suggest_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Based on the code analysis, provide specific improvements.\n"
        "Include corrected code examples for each issue.",
    ),
    ("human", "Analysis:\n{analysis}\n\nOriginal code:\n{code}"),
])

report_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Summarize the code review into a concise report.\n"
        "Structure: overall assessment, key improvements, recommended actions.",
    ),
    ("human", "Analysis:\n{analysis}\n\nSuggestions:\n{suggestions}"),
])

analyze_chain = analyze_prompt | llm | JsonOutputParser()
suggest_chain = suggest_prompt | llm | StrOutputParser()
report_chain = report_prompt | llm | StrOutputParser()

def code_review_pipeline(code: str) -> dict:
    """Code analysis → suggestions → report."""
    analysis = analyze_chain.invoke({"code": code})
    print(f"  analysis done: score {analysis.get('score')}/10, {len(analysis.get('issues', []))} issues")

    suggestions = suggest_chain.invoke({
        "analysis": str(analysis),
        "code": code,
    })
    print("  suggestions done")

    report = report_chain.invoke({
        "analysis": str(analysis),
        "suggestions": suggestions,
    })
    print("  report done")

    return {"analysis": analysis, "suggestions": suggestions, "report": report}

sample_code = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    result = cursor.fetchone()
    conn.close()
    return result
"""

print("running code review pipeline...")
result = code_review_pipeline(sample_code)
print(f"\n=== final report ===\n{result['report']}")
```

---

## 이 코드에서 먼저 볼 점

- `main.py`는 같은 지원 티켓을 요약, 카테고리 분류, 태그 제안이라는 세 순차 단계로 나눕니다.
- 모든 단계가 `dict`를 반환하므로 중간 출력을 로깅하거나 점검하거나 저장하기 쉽습니다.
- 이런 구조는 승인, 라우팅, 재시도 정책 같은 운영 제어와 잘 맞습니다.

---

## 어디서 자주 헷갈릴까요?

- 단계가 많다고 자동으로 좋아지지 않습니다. 호출 하나가 늘 때마다 비용, 지연, 실패 표면도 함께 늘어납니다.
- 단계 사이에 원시 문자열만 넘기면 이후 검증과 분기가 구조화된 딕셔너리를 넘길 때보다 훨씬 어려워집니다.
- 워크플로와 에이전트를 가르는 진짜 기준은 도구 사용 여부가 아니라, 실행 경로가 런타임에 바뀌는지 여부입니다.

---

## 체크리스트

- [ ] 요약 출력이 다음 단계의 입력으로 전달된다
- [ ] 분류기가 제한된 카테고리 집합 중 하나를 반환한다
- [ ] 태깅 단계가 원문만이 아니라 앞선 단계 결과도 활용한다
- [ ] 최종 출력이 중간 산출물을 여전히 포함하는 구조화 객체다

---

## 정리

각 단계는 하나의 책임만 맡게 두는 편이 좋습니다. 너무 많은 일을 하는 단계는 테스트하기 어렵고, 디버깅하기 어렵고, 교체하기도 어렵습니다. 단계 출력이 구조화 데이터여야 하는데 자유 텍스트로 흘러나오면, 다음 단계는 조용히 실패하는 경우가 많습니다. 모든 단계의 출력 형식을 먼저 정의하고 검증한 뒤에야 다음 단계로 넘기는 습관이 필요합니다.

마지막 글에서는 Human-in-the-loop 설계를 다룹니다. 자동화 파이프라인 안에 사람 검토와 승인 게이트를 삽입하는 방식입니다.

<!-- toc:begin -->
## 시리즈 목차

- [챗봇 패턴 — 대화 이력과 상태 관리](./01-chatbot-pattern.md)
- [RAG Q&A 패턴 — 문서 기반 질의응답](./02-rag-qa-pattern.md)
- [문서 어시스턴트 — 요약, 추출, 분류](./03-document-assistant.md)
- [에이전트와 도구 패턴 — 자율적 도구 선택](./04-agent-tool-pattern.md)
- **워크플로 자동화 — 다단계 체인 설계 (현재 글)**
- Human-in-the-loop — 사람 개입 설계 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain LCEL](https://python.langchain.com/docs/expression_language/)
- [LangChain routing](https://python.langchain.com/docs/expression_language/how_to/routing/)
- [RunnableParallel](https://python.langchain.com/docs/expression_language/primitives/parallel/)

Tags: LLM, RAG, Agent, Python
