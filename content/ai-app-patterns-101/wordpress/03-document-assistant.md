---
title: "바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트"
series: ai-app-patterns-101
episode: 3
language: ko
tags:
- Document Assistant
- Map-Reduce
- Summarization
- Structured Extraction
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트

이 글은 **바이브코딩을 위한 AI 앱 패턴** 시리즈의 세 번째 글입니다.

---

바이브코딩으로 "계약서를 요약해줘", "이 보고서에서 중요한 숫자를 뽑아줘"라는 기능을 만들려고 하면, 문서가 LLM 컨텍스트 윈도우보다 길다는 문제에 바로 부딪힙니다. GPT-4o도 128K 토큰이 한계인데, 긴 계약서나 보고서는 이를 쉽게 초과합니다.

문서 어시스턴트 패턴의 핵심은 긴 문서를 처리하는 세 가지 전략입니다. **Map-Reduce**(분할 후 합치기), **Refine**(순차적 개선), **구조화 추출**(정해진 형식으로 정보 뽑기). 어떤 전략을 쓰냐가 품질과 비용을 결정합니다.

> "긴 문서를 AI에게 처리하게 할 때 핵심은 '어떻게 분할하고 결합하는가'입니다."

## 이 글에서 다룰 질문

1. Map-Reduce와 Refine 요약 전략은 어떻게 다른가요?
2. 구조화 추출로 계약서에서 정보를 뽑는 방법은?
3. 비동기로 여러 청크를 동시에 처리하는 방법은?
4. 대량의 피드백을 분류하는 배치 처리 패턴은?
5. 어떤 문서 작업에 어떤 전략을 선택해야 하나요?

---

## 요약 전략 비교

| 전략 | 방법 | 장점 | 단점 |
|------|------|------|------|
| Map-Reduce | 청크별 요약 후 통합 | 병렬 처리 가능, 빠름 | 청크 간 연결 맥락 손실 |
| Refine | 이전 요약을 다음 청크에 반영 | 맥락 유지 | 순차 처리, 느림 |
| Stuff | 전체 문서를 한 번에 처리 | 가장 정확 | 컨텍스트 한도 초과 위험 |

## Before / After: 긴 문서 처리

**Before (전체 문서를 한 번에 전송)**
```python
long_doc = load_document("annual_report.pdf")  # 50,000 토큰
response = llm.chat(f"다음 연간 보고서를 요약하세요:\n{long_doc}")
# 오류: 컨텍스트 윈도우 초과
```

**After (Map-Reduce 전략)**
```python
import asyncio

def split_into_chunks(text: str, chunk_size: int = 2000) -> list[str]:
    """텍스트를 적절한 크기의 청크로 분할합니다."""
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

async def summarize_chunk(chunk: str, chunk_index: int) -> str:
    """하나의 청크를 요약합니다."""
    return await llm.async_chat(f"다음 내용을 3-5문장으로 요약하세요:\n{chunk}")

async def map_reduce_summarize(text: str) -> str:
    """Map-Reduce 방식으로 긴 문서를 요약합니다."""
    chunks = split_into_chunks(text)

    # Map: 청크들을 병렬로 요약
    chunk_summaries = await asyncio.gather(
        *[summarize_chunk(chunk, i) for i, chunk in enumerate(chunks)]
    )

    # Reduce: 청크 요약들을 통합
    combined = "\n\n".join(chunk_summaries)
    final_summary = await llm.async_chat(
        f"다음 부분별 요약을 통합해 하나의 완성된 요약을 만드세요:\n{combined}"
    )

    return final_summary
```

## 구조화 추출: Pydantic으로 정보 뽑기

```python
from pydantic import BaseModel, Field
from typing import Optional

class ContractInfo(BaseModel):
    parties: list[str] = Field(..., description="계약 당사자 목록")
    effective_date: Optional[str] = Field(None, description="계약 발효일 (YYYY-MM-DD)")
    total_value: Optional[float] = Field(None, description="계약 금액 (원)")
    termination_conditions: list[str] = Field(default_factory=list, description="계약 해지 조건")
    payment_terms: Optional[str] = Field(None, description="결제 조건")

def extract_contract_info(contract_text: str) -> ContractInfo:
    """계약서에서 구조화된 정보를 추출합니다."""
    response = llm.chat(
        f"""다음 계약서에서 정보를 추출해 JSON으로 반환하세요.
        필드:
        - parties: 계약 당사자 목록
        - effective_date: 발효일 (YYYY-MM-DD 형식)
        - total_value: 계약 금액 (숫자만)
        - termination_conditions: 해지 조건 목록
        - payment_terms: 결제 조건

        계약서:
        {contract_text}""",
        response_format={"type": "json_object"}
    )

    return ContractInfo(**json.loads(response))
```

## 배치 분류: 대량 피드백 처리

```python
import asyncio

async def classify_feedback(text: str) -> str:
    """피드백을 카테고리로 분류합니다."""
    result = await llm.async_chat(f"""다음 고객 피드백을 하나의 카테고리로 분류하세요.
    카테고리: UI, 성능, 기능 요청, 버그, 결제, 기타

    피드백: {text}
    카테고리만 답하세요.""")
    return result.strip()

async def batch_classify(feedbacks: list[str], max_concurrent: int = 10) -> list[str]:
    """동시 처리 수를 제한해 대량 피드백을 분류합니다."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def classify_with_limit(text):
        async with semaphore:
            return await classify_feedback(text)

    return await asyncio.gather(*[classify_with_limit(f) for f in feedbacks])
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 긴 문서를 한 번에 처리 | 컨텍스트 초과, 오류 | Map-Reduce 또는 Refine 전략 |
| 동기 방식으로 배치 처리 | 처리 시간 폭증 | asyncio로 병렬화 |
| 추출 결과 검증 없음 | 잘못된 데이터 타입, 누락 필드 | Pydantic 모델로 검증 |
| 배치 처리 시 속도 제한 무시 | API 429 오류 | Semaphore로 동시성 제어 |

## AI 팁

Refine 전략은 이전 요약을 다음 청크 처리에 반영하므로 맥락이 잘 유지됩니다. 특히 순서가 중요한 문서(이야기, 계약서 본문 흐름)에는 Refine이 Map-Reduce보다 품질이 좋습니다.

```python
async def refine_summarize(text: str) -> str:
    """Refine 전략으로 순차적으로 요약을 개선합니다."""
    chunks = split_into_chunks(text)
    current_summary = ""

    for i, chunk in enumerate(chunks):
        if i == 0:
            current_summary = await llm.async_chat(f"다음 내용을 요약하세요:\n{chunk}")
        else:
            current_summary = await llm.async_chat(f"""기존 요약을 새 내용을 반영해 개선하세요.

            기존 요약:
            {current_summary}

            추가 내용:
            {chunk}

            개선된 요약:""")

    return current_summary
```

## 체크리스트

- [ ] 문서 길이에 따라 적절한 전략(Map-Reduce/Refine/Stuff)을 선택했다
- [ ] 구조화 추출에 Pydantic 모델로 검증을 적용했다
- [ ] 배치 처리에 asyncio와 Semaphore를 사용한다
- [ ] 청크 분할 시 맥락 보존을 위해 오버랩을 설정했다
- [ ] 추출된 구조화 데이터의 품질을 검증했다

## 처음 질문으로 돌아가기

**Map-Reduce vs Refine 차이는?** Map-Reduce는 청크를 병렬로 요약한 뒤 통합하므로 빠르지만 청크 간 맥락 연결이 약합니다. Refine은 순차적으로 이전 요약을 개선하므로 느리지만 맥락 연결이 강합니다.

**계약서에서 정보 추출은?** Pydantic 모델로 원하는 필드를 정의하고, LLM에게 JSON 형식으로 반환하도록 요청합니다. Pydantic이 자동으로 타입 검증을 합니다.

**비동기 병렬 처리 방법은?** `asyncio.gather()`로 여러 청크를 동시에 처리하고, `asyncio.Semaphore()`로 동시 처리 수를 제한해 API 속도 제한을 피합니다.

**배치 분류 패턴은?** Semaphore로 동시성을 제어하면서 asyncio.gather()로 여러 피드백을 병렬 분류합니다.

**전략 선택 기준은?** 짧은 문서는 Stuff(전체), 긴 문서에서 속도가 중요하면 Map-Reduce, 긴 문서에서 맥락 연결이 중요하면 Refine.

## 정리

문서 어시스턴트 패턴은 긴 문서를 AI가 처리할 수 있도록 분할하고 결합하는 전략입니다. Map-Reduce는 빠르고, Refine은 맥락을 잘 유지합니다. 구조화 추출에 Pydantic을 쓰면 타입 안전성이 보장됩니다. 대량 처리 시 asyncio로 병렬화하되 Semaphore로 API 한도를 지켜야 합니다.

다음 글에서는 에이전트가 도구를 등록하고 선택적으로 사용하는 **에이전트 도구 패턴**을 다룹니다.

## 참고 자료

- [AI 앱 패턴 원문: 문서 어시스턴트](../ko/03-document-assistant.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴](./01-chatbot-pattern.md)
2. [바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
3. **바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트 (현재 글)**
4. [바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴](./04-agent-tool-pattern.md)
5. [바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화](./05-workflow-automation.md)
6. [바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop](./06-human-in-the-loop.md)
<!-- toc:end -->

Tags: Document Assistant, Map-Reduce, Summarization, Structured Extraction, 바이브코딩
