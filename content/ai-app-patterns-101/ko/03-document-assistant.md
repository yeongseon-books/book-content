---
title: '문서 어시스턴트 — 요약, 추출, 분류'
series: ai-app-patterns-101
episode: 3
language: ko
status: draft
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

# 문서 어시스턴트 — 요약, 추출, 분류

> AI 앱 패턴 101 시리즈 (3/6)

예제 코드: [github.com/yeongseon-books/ai-app-patterns-101](https://github.com/yeongseon-books/ai-app-patterns-101/tree/main/ko/03-document-assistant)

문서 어시스턴트는 입력 문서를 받아 특정 작업을 수행하는 패턴입니다. 긴 문서를 요약하거나, 구조화된 정보를 추출하거나, 문서를 분류하는 작업에서 LLM은 큰 힘을 발휘합니다. 이 패턴은 챗봇이나 RAG와 달리 대화가 없고, 문서 자체가 입력입니다.

이번 글에서는 세 가지 문서 처리 패턴을 다룹니다.

- 요약 (Summarization)
- 정보 추출 (Information Extraction)
- 분류 (Classification)

---

## 문서 요약

짧은 문서는 단순하게 처리합니다. 전체를 프롬프트에 넣고 요약을 요청합니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

summarize_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "다음 문서를 {style} 스타일로 요약하세요.\n"
        "요약 길이: {length}\n"
        "독자: {audience}",
    ),
    ("human", "문서:\n{document}"),
])

chain = summarize_prompt | llm | StrOutputParser()

document = """
2024년 파이썬 개발자 설문조사 결과에 따르면, 파이썬은 5년 연속으로 가장 인기 있는 프로그래밍 언어로
선정되었습니다. 응답자의 67%가 파이썬을 주 언어로 사용한다고 답했으며, 그 중 45%는 데이터 과학과
머신러닝 업무에 파이썬을 사용합니다. 웹 개발 용도는 28%, 자동화 스크립트는 18%를 차지했습니다.

파이썬 3.12 버전은 전년 대비 성능이 25% 향상되었으며, 타입 힌트 지원이 강화되었습니다.
응답자의 89%가 파이썬 3.x를 사용 중이며, 파이썬 2.x 사용자는 2%에 불과합니다.

가장 많이 쓰는 프레임워크는 FastAPI(52%), Django(38%), Flask(34%) 순이었으며,
데이터 과학 분야에서는 pandas(78%), numpy(72%), scikit-learn(65%)이 상위를 차지했습니다.
"""

# 경영진용 요약
exec_summary = chain.invoke({
    "document": document,
    "style": "비즈니스 중심",
    "length": "3문장 이내",
    "audience": "기술 배경이 없는 경영진",
})
print("=== 경영진 요약 ===")
print(exec_summary)

# 개발자용 요약
dev_summary = chain.invoke({
    "document": document,
    "style": "기술적",
    "length": "불릿 포인트 5개",
    "audience": "시니어 개발자",
})
print("\n=== 개발자 요약 ===")
print(dev_summary)
```

---

## 긴 문서 요약 — Map-Reduce 패턴

문서가 컨텍스트 창 한계를 넘으면 전체를 한 번에 처리할 수 없습니다. Map-Reduce는 청크별로 요약하고(Map), 그 요약들을 다시 요약하는(Reduce) 방식입니다.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

map_prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 텍스트 구간을 핵심만 2~3문장으로 요약하세요."),
    ("human", "{chunk}"),
])

reduce_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "여러 구간의 요약을 받았습니다. 이를 하나의 일관된 요약으로 통합하세요.\n"
        "중복을 제거하고 논리적 흐름을 유지하세요.",
    ),
    ("human", "구간별 요약:\n{summaries}"),
])

map_chain = map_prompt | llm | StrOutputParser()
reduce_chain = reduce_prompt | llm | StrOutputParser()

def map_reduce_summarize(long_document: str) -> str:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(long_document)
    print(f"  청크 수: {len(chunks)}")

    # Map: 각 청크 요약
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        summary = map_chain.invoke({"chunk": chunk})
        chunk_summaries.append(summary)
        print(f"  청크 {i+1}/{len(chunks)} 요약 완료")

    # Reduce: 요약 통합
    combined = "\n\n".join(
        f"[구간 {i+1}] {s}" for i, s in enumerate(chunk_summaries)
    )
    final_summary = reduce_chain.invoke({"summaries": combined})
    return final_summary

long_doc = """
인공지능(AI)은 인간의 지적 능력을 컴퓨터로 구현하는 기술입니다. 1950년대 앨런 튜링이 "기계가 생각할 수 있는가?"라는 질문을 던지며 시작된 분야로, 이후 수십 년간 부침을 거듭해 왔습니다.

머신러닝은 AI의 한 분야로, 컴퓨터가 데이터에서 스스로 규칙을 학습하도록 합니다. 전통적인 프로그래밍이 명시적 규칙을 작성하는 것과 달리, 머신러닝은 데이터로부터 패턴을 찾습니다. 의사결정 트리, 랜덤 포레스트, 서포트 벡터 머신 등이 대표적 알고리즘입니다.

딥러닝은 머신러닝의 한 분야로, 인간 뇌의 신경망을 모방한 인공신경망을 사용합니다. 2012년 이미지넷 경진대회에서 딥러닝 모델이 기존 방법을 크게 앞서면서 주목받기 시작했습니다. 이후 이미지 인식, 음성 인식, 자연어 처리 분야에서 혁신을 이끌었습니다.

대규모 언어 모델(LLM)은 딥러닝 기반으로 방대한 텍스트 데이터를 학습한 모델입니다. GPT, BERT, LLaMA 등이 대표적이며, 텍스트 생성, 요약, 번역, 코드 작성 등 다양한 태스크에 활용됩니다. 2023년 ChatGPT의 등장으로 일반 대중에게도 크게 알려졌습니다.

AI의 미래는 밝지만 도전과제도 많습니다. 설명 가능성(XAI), 편향성, 프라이버시, 에너지 소비, 일자리 대체 등의 문제를 사회적으로 해결해야 합니다. 동시에 의료, 기후 변화, 교육 등 중요한 문제를 해결하는 데 AI가 핵심 역할을 할 것으로 기대됩니다.
"""

print("Map-Reduce 요약 시작...")
final = map_reduce_summarize(long_doc)
print(f"\n=== 최종 요약 ===\n{final}")
```

---

## 정보 추출

비정형 텍스트에서 구조화된 데이터를 뽑아냅니다.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

extract_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "다음 텍스트에서 정보를 추출해 JSON으로 반환하세요. "
        "JSON만 반환하고 다른 텍스트는 포함하지 마세요.\n\n"
        "추출할 필드:\n{schema}",
    ),
    ("human", "텍스트:\n{text}"),
])

chain = extract_prompt | llm | JsonOutputParser()

job_schema = """
{
  "company": "회사명",
  "position": "직책",
  "location": "위치",
  "salary_range": "급여 범위 (없으면 null)",
  "required_skills": ["필수 기술 목록"],
  "experience_years": "경력 연수 (숫자, 없으면 null)",
  "employment_type": "고용 형태 (정규직/계약직/프리랜서)"
}"""

job_postings = [
    """
    ABC테크에서 시니어 백엔드 개발자를 채용합니다. 서울 강남구 위치.
    연봉 8천~1억 2천. Python/Django 5년 이상 경력 필수.
    AWS, Docker 경험 우대. 정규직 채용.
    """,
    """
    스타트업 XYZ에서 풀스택 개발자를 모집합니다. 재택 근무 가능.
    React, Node.js, PostgreSQL 능숙자. 3년 이상. 계약직 (전환 가능).
    """,
]

for i, posting in enumerate(job_postings, start=1):
    print(f"\n=== 채용공고 {i} ===")
    result = chain.invoke({"text": posting, "schema": job_schema})
    for key, value in result.items():
        print(f"  {key}: {value}")
```

---

## 문서 분류

문서를 카테고리로 분류합니다.

```python
import os

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

classify_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "다음 텍스트를 분류하세요. JSON만 반환하세요.\n\n"
        "가능한 카테고리: {categories}\n\n"
        "형식: {{\"category\": \"카테고리명\", \"confidence\": 0~1, \"reason\": \"이유\"}}",
    ),
    ("human", "텍스트:\n{text}"),
])

chain = classify_prompt | llm | JsonOutputParser()

categories = "기술/IT, 비즈니스/경영, 의료/건강, 스포츠, 엔터테인먼트, 기타"

texts = [
    "파이썬 3.12에서 타입 힌트 성능이 크게 개선되었다. 특히 제네릭 타입 처리 속도가 25% 빨라졌다.",
    "3분기 영업이익이 전년 동기 대비 15% 증가했다. 해외 시장 확대가 주요 요인이다.",
    "규칙적인 유산소 운동이 심혈관 질환 위험을 30% 낮춘다는 연구 결과가 발표됐다.",
    "챔피언스리그 결승에서 레알 마드리드가 맨체스터 시티를 2-1로 꺾고 우승했다.",
]

for text in texts:
    result = chain.invoke({"text": text, "categories": categories})
    print(f"텍스트: {text[:50]}...")
    print(f"  카테고리: {result.get('category')}, 신뢰도: {result.get('confidence'):.2f}")
    print(f"  이유: {result.get('reason')}\n")
```

---

## 마무리

요약, 추출, 분류는 문서 처리에서 가장 자주 쓰이는 패턴입니다. 긴 문서에는 Map-Reduce를 쓰고, 구조화 출력이 필요할 때는 `JsonOutputParser`를 활용합니다.

다음 글에서는 Agent + Tool 패턴을 다룹니다. LLM이 자율적으로 도구를 선택하고 실행하는 방법입니다.

<!-- blog-only:start -->
다음 글: [Agent + Tool 패턴 — 자율 도구 선택](./04-agent-tool-pattern.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [챗봇 패턴 — 대화 이력 관리와 상태](./01-chatbot-pattern.md)
- [RAG Q&A 패턴 — 문서 기반 질의응답](./02-rag-qa-pattern.md)
- **문서 어시스턴트 — 요약, 추출, 분류 (현재 글)**
- Agent + Tool 패턴 — 자율 도구 선택 (예정)
- 워크플로 자동화 — 다단계 체인 설계 (예정)
- Human-in-the-loop — 사람 개입 설계 패턴 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain 요약 체인](https://python.langchain.com/docs/use_cases/summarization/)
- [JsonOutputParser](https://python.langchain.com/docs/modules/model_io/output_parsers/json/)
- [Map-Reduce 패턴](https://python.langchain.com/docs/use_cases/summarization/#option-2-map-reduce)

Tags: LLM, RAG, Agent, Python
