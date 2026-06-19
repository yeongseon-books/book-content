---
series: ai-app-patterns-101
episode: 3
title: "AI App Patterns 101 (3/6): Document Assistant 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DocumentAI
  - Summarization
  - Extraction
  - MapReduce
  - LLM
seo_description: Map-Reduce 요약, JSON 구조화 추출, 배치 분류까지 문서 어시스턴트 패턴의 핵심 구현을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (3/6): Document Assistant 패턴

긴 PDF 보고서를 요약하거나, 계약서에서 주요 조항을 추출하거나, 수백 개의 고객 피드백을 카테고리별로 분류해야 할 때 Document Assistant 패턴이 등장합니다. 이 패턴의 특징은 단일 LLM 호출이 아니라 문서를 여러 단계로 처리하는 파이프라인 구조에 있습니다. 문서가 컨텍스트 길이를 초과하면 Map-Reduce로 분할 처리하고, 구조화 데이터가 필요하면 JSON 스키마를 강제하며, 대량 문서를 처리할 때는 배치와 비동기를 활용합니다.

이 글은 AI App Patterns 101 시리즈의 3번째 글입니다.

![Document Assistant 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/03/03-01-concept-at-a-glance.ko.png)
*Map-Reduce 요약과 구조화 추출이 결합된 Document Assistant 파이프라인*

## 이 글에서 다룰 문제

- 컨텍스트 길이를 초과하는 문서는 어떻게 요약할 수 있을까요?
- Map-Reduce 요약에서 Reduce 단계가 품질에 미치는 영향은 무엇일까요?
- LLM으로 구조화된 JSON 데이터를 안정적으로 추출하려면 어떻게 해야 할까요?
- 수백 개 문서를 배치 처리할 때 레이트 리밋을 어떻게 관리할까요?
- 분류 작업에서 LLM 응답의 일관성을 높이는 방법은 무엇일까요?

## 핵심 개념 한 줄 정리

- **Map-Reduce**: 문서를 청크로 분할해 각각 처리(Map)한 뒤 결과를 합쳐 최종 출력을 생성(Reduce)하는 패턴입니다.
- **Structured Extraction**: JSON 스키마를 LLM 출력에 강제해 파싱 가능한 구조화 데이터를 얻는 기법입니다.
- **Batch Classification**: 여러 문서를 정해진 카테고리로 분류하는 작업입니다.
- **Refine Strategy**: 이전 요약 결과를 다음 청크 요약에 누적해 나가는 순차 요약 전략입니다.
- **Async Processing**: 여러 LLM 호출을 병렬로 실행해 처리 시간을 단축하는 방식입니다.

## 요약 전략 비교

| 전략 | 장점 | 단점 | 적합 상황 |
|---|---|---|---|
| Map-Reduce | 병렬 처리 가능, 빠름 | Reduce 단계에서 세부 사항 손실 | 보고서, 뉴스 기사 요약 |
| Refine | 맥락 누적, 세부 사항 보존 | 순차 처리라 느림 | 계약서, 법률 문서 |
| 계층적 요약 | 다단계 압축 가능 | 구현 복잡도 높음 | 매우 긴 문서 (100+ 페이지) |
| 직접 요약 | 가장 단순 | 컨텍스트 길이 제한 | 짧은 문서 (1-2페이지) |

## 구체적인 시나리오

**시나리오 A — 투자 리포트 요약 서비스**: 애널리스트가 매일 50개 이상의 기업 실적 리포트(평균 20페이지)를 읽어야 합니다. 각 문서를 Map-Reduce로 처리해 경영진 요약(3문장), 핵심 수치, 리스크 요인을 자동 추출합니다.

**시나리오 B — 채용 서류 자동 심사**: 이력서와 자기소개서에서 직무 관련 기술, 경력 연차, 학력 사항을 JSON으로 추출해 HR 시스템에 자동 입력합니다. Pydantic 검증으로 파싱 실패를 사전 차단합니다.

**시나리오 C — 고객 피드백 분류**: 매일 수백 건의 앱스토어 리뷰와 지원 티켓을 자동 분류해 "버그 신고", "기능 요청", "결제 문제" 등 카테고리로 담당팀에 자동 배분합니다.

## 실습 1: Map-Reduce 요약

긴 문서를 청크로 분할해 각각 요약하고(Map), 청크 요약들을 합쳐 최종 요약을 생성합니다(Reduce). asyncio로 Map 단계를 병렬 실행하면 처리 시간을 크게 줄일 수 있습니다.

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()


def split_into_chunks(text: str, max_words: int = 800) -> list[str]:
    """문서를 단어 기준으로 청크로 분할합니다."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i : i + max_words])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


async def summarize_chunk(chunk: str, chunk_num: int, total: int) -> str:
    """단일 청크를 요약합니다 (Map 단계)."""
    prompt = (
        f"다음은 긴 문서의 {chunk_num}/{total} 부분입니다. "
        "핵심 내용만 3-5문장으로 요약하세요.\n\n"
        f"{chunk}"
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content


async def reduce_summaries(summaries: list[str], original_length: int) -> str:
    """청크 요약들을 하나의 최종 요약으로 합칩니다 (Reduce 단계)."""
    combined = "\n\n".join(
        f"[파트 {i+1}]\n{s}" for i, s in enumerate(summaries)
    )
    prompt = (
        f"다음은 {original_length}단어 문서의 각 파트 요약입니다. "
        "중복을 제거하고 전체 내용을 5-7문장으로 통합 요약하세요. "
        "핵심 결론과 주요 발견 사항을 강조하세요.\n\n"
        f"{combined}"
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return response.choices[0].message.content


async def map_reduce_summarize(text: str) -> dict:
    """Map-Reduce 방식으로 긴 문서를 요약합니다."""
    chunks = split_into_chunks(text, max_words=800)
    word_count = len(text.split())

    if len(chunks) == 1:
        # 짧은 문서는 직접 요약
        summary = await summarize_chunk(chunks[0], 1, 1)
        return {"summary": summary, "chunks_processed": 1, "original_word_count": word_count}

    # Map: 모든 청크를 병렬로 요약 (시간 단축 핵심)
    map_tasks = [summarize_chunk(c, i + 1, len(chunks)) for i, c in enumerate(chunks)]
    chunk_summaries = await asyncio.gather(*map_tasks)

    # Reduce: 청크 요약들을 통합
    final_summary = await reduce_summaries(list(chunk_summaries), word_count)

    return {
        "summary": final_summary,
        "chunks_processed": len(chunks),
        "original_word_count": word_count,
        "chunk_summaries": list(chunk_summaries),  # 디버깅용
    }


# 사용 예시: 투자 리포트 요약
sample_report = """
ABC 주식회사 2026년 1분기 실적 보고서

요약: 1분기 매출액은 전년 동기 대비 23% 증가한 1,200억원을 기록했습니다.
영업이익률은 15.3%로 업계 평균 12%를 상회했습니다.

[본문 - 약 5,000 단어의 상세 분석 내용...]
"""

result = asyncio.run(map_reduce_summarize(sample_report))
print(f"요약 완료: {result['chunks_processed']}개 청크 처리")
print(f"최종 요약:\n{result['summary']}")
```

Map 단계에서 병렬 처리를 사용하면 10개 청크를 순차 처리하는 대비 약 8-9배 빠릅니다. 단, OpenAI API의 레이트 리밋에 걸리지 않도록 동시 요청 수를 세마포어로 제한하는 것이 좋습니다.

## 실습 2: Refine 전략 (순차 요약)

계약서나 법률 문서처럼 앞뒤 맥락이 중요할 때는 Refine 전략이 Map-Reduce보다 더 좋은 결과를 냅니다.

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def refine_summarize(text: str, max_words_per_chunk: int = 600) -> dict:
    """순차적으로 요약을 정제하는 Refine 전략입니다."""
    chunks = split_into_chunks(text, max_words_per_chunk)
    running_summary = ""
    chunk_results = []

    for i, chunk in enumerate(chunks):
        if not running_summary:
            # 첫 청크: 직접 요약
            prompt = f"다음 텍스트를 3-4문장으로 요약하세요:\n\n{chunk}"
        else:
            # 이후 청크: 기존 요약을 바탕으로 보완
            prompt = (
                f"현재까지의 요약:\n{running_summary}\n\n"
                f"추가 내용:\n{chunk}\n\n"
                "위 추가 내용을 반영해 기존 요약을 보완하세요. "
                "새로운 정보만 추가하고 중복은 제거하세요. 5-7문장으로 유지하세요."
            )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        running_summary = response.choices[0].message.content
        chunk_results.append({"chunk": i + 1, "summary": running_summary})

    return {
        "final_summary": running_summary,
        "chunks_processed": len(chunks),
        "progression": chunk_results,
    }
```

## 실습 3: JSON 구조화 추출

계약서나 이력서에서 특정 필드를 추출할 때 JSON 응답 형식을 강제하면 파싱 오류를 크게 줄일 수 있습니다.

```python
from openai import OpenAI
from pydantic import BaseModel, Field
import json

client = OpenAI()


class ContractInfo(BaseModel):
    parties: list[str] = Field(description="계약 당사자 목록")
    start_date: str | None = Field(None, description="계약 시작일 (YYYY-MM-DD)")
    end_date: str | None = Field(None, description="계약 종료일 (YYYY-MM-DD)")
    total_value: str | None = Field(None, description="계약 금액 (통화 단위 포함)")
    key_obligations: list[str] = Field(default_factory=list, description="주요 의무 사항")
    termination_conditions: list[str] = Field(default_factory=list, description="계약 해지 조건")
    governing_law: str | None = Field(None, description="준거법")


def extract_contract_info(contract_text: str) -> ContractInfo:
    """계약서에서 핵심 정보를 구조화 추출합니다."""
    schema = ContractInfo.model_json_schema()
    prompt = f"""다음 계약서에서 정보를 추출하세요.

계약서:
{contract_text[:4000]}

반드시 다음 JSON 스키마를 따르세요:
{json.dumps(schema, ensure_ascii=False, indent=2)}

규칙:
- 날짜는 YYYY-MM-DD 형식
- 금액은 통화 단위 포함 (예: "5,000만원", "USD 50,000")
- 찾을 수 없는 필드는 null 반환 (추측 금지)"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    raw = json.loads(response.choices[0].message.content)
    return ContractInfo(**raw)


# 사용 예시
sample_contract = """
서비스 이용 계약서

본 계약은 2026년 1월 1일을 기준으로,
갑: ABC 주식회사 (대표 김철수)
을: XYZ 컨설팅 주식회사 (대표 이영희)
간에 체결합니다.

제1조 (계약 기간): 2026년 1월 1일부터 2026년 12월 31일까지
제2조 (계약 금액): 총 5,000만원 (VAT 별도)
제3조 (갑의 의무): 매월 25일까지 작업 지시서 제공
제4조 (을의 의무): 매월 마지막 영업일까지 산출물 납품
제5조 (계약 해지): 30일 전 서면 통보 시 계약 해지 가능
준거법: 대한민국 법률
"""

try:
    info = extract_contract_info(sample_contract)
    print(f"당사자: {info.parties}")
    print(f"계약 기간: {info.start_date} ~ {info.end_date}")
    print(f"계약 금액: {info.total_value}")
    print(f"주요 의무: {info.key_obligations}")
except Exception as e:
    print(f"추출 실패: {e}")
```

## 실습 4: 배치 분류

수백 개 고객 피드백을 카테고리별로 분류하는 배치 처리입니다. `asyncio.Semaphore`로 동시 요청 수를 제한해 레이트 리밋을 관리합니다.

```python
import asyncio
import json
from openai import AsyncOpenAI

client = AsyncOpenAI()

CATEGORIES = ["버그 신고", "기능 요청", "사용법 문의", "결제 문제", "기타"]


async def classify_feedback(feedback: str, feedback_id: str) -> dict:
    """단일 피드백을 분류합니다."""
    categories_str = ", ".join(f'"{c}"' for c in CATEGORIES)
    prompt = f"""다음 고객 피드백을 분류하세요.

허용 카테고리: {categories_str}

피드백:
{feedback}

JSON으로만 응답:
{{"category": "카테고리명", "confidence": 0.0-1.0, "summary": "한 줄 요약", "priority": "high/medium/low"}}"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return {"id": feedback_id, **result}


async def batch_classify(
    feedbacks: list[dict],
    concurrency: int = 5,
) -> list[dict]:
    """레이트 리밋을 고려한 배치 분류 처리입니다."""
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def classify_with_semaphore(item: dict) -> dict:
        async with semaphore:
            try:
                result = await classify_feedback(item["text"], item["id"])
                await asyncio.sleep(0.1)  # 레이트 리밋 완충
                return result
            except Exception as e:
                return {
                    "id": item["id"],
                    "category": "기타",
                    "confidence": 0.0,
                    "priority": "low",
                    "error": str(e),
                }

    tasks = [classify_with_semaphore(f) for f in feedbacks]
    results = await asyncio.gather(*tasks)
    return list(results)


# 분류 결과 집계
def aggregate_results(results: list[dict]) -> dict:
    """분류 결과를 카테고리별로 집계합니다."""
    from collections import Counter
    category_counts = Counter(r.get("category", "기타") for r in results)
    high_priority = [r for r in results if r.get("priority") == "high"]
    failed = [r for r in results if "error" in r]

    return {
        "total": len(results),
        "by_category": dict(category_counts),
        "high_priority_count": len(high_priority),
        "failed_count": len(failed),
    }


# 사용 예시
feedbacks = [
    {"id": "fb001", "text": "로그인 버튼이 클릭되지 않아요. iOS 17에서 발생합니다."},
    {"id": "fb002", "text": "다크 모드 기능을 추가해 주세요!"},
    {"id": "fb003", "text": "결제가 두 번 청구되었습니다. 환불 요청합니다."},
    {"id": "fb004", "text": "비밀번호를 어떻게 변경하나요?"},
    {"id": "fb005", "text": "앱이 자꾸 튕겨요. 앱 버전 3.2.1입니다."},
]

results = asyncio.run(batch_classify(feedbacks))
summary = aggregate_results(results)

for r in results:
    print(f"{r['id']}: [{r['category']}] 신뢰도={r.get('confidence', 0):.2f} 우선순위={r.get('priority', 'N/A')}")

print(f"\n집계: {summary}")
```

## 실습 5: Pydantic 검증 계층

추출과 분류 결과를 후속 시스템에 넘기기 전에 Pydantic으로 검증하면 조용한 실패를 방지합니다.

```python
from pydantic import BaseModel, Field, ValidationError, field_validator


class FeedbackClassification(BaseModel):
    id: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    priority: str
    summary: str

    @field_validator("category")
    @classmethod
    def category_must_be_allowed(cls, v: str) -> str:
        allowed = {"버그 신고", "기능 요청", "사용법 문의", "결제 문제", "기타"}
        if v not in allowed:
            raise ValueError(f"허용되지 않은 카테고리: {v}. 허용 목록: {allowed}")
        return v

    @field_validator("priority")
    @classmethod
    def priority_must_be_valid(cls, v: str) -> str:
        if v not in {"high", "medium", "low"}:
            raise ValueError(f"유효하지 않은 우선순위: {v}")
        return v


def validate_and_separate(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """검증 통과한 결과와 실패한 결과를 분리합니다."""
    valid = []
    invalid = []

    for r in results:
        try:
            validated = FeedbackClassification(**r)
            valid.append(validated.model_dump())
        except ValidationError as e:
            invalid.append({"id": r.get("id"), "errors": e.errors()})

    return valid, invalid
```

## FastAPI 문서 처리 엔드포인트

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class SummarizeRequest(BaseModel):
    text: str
    strategy: str = "map_reduce"  # "map_reduce" | "refine"
    max_words_per_chunk: int = 800


class ExtractRequest(BaseModel):
    text: str
    doc_type: str = "contract"  # "contract" | "resume" | "invoice"


@app.post("/documents/summarize")
async def summarize_endpoint(req: SummarizeRequest):
    if req.strategy == "refine":
        result = await refine_summarize(req.text, req.max_words_per_chunk)
    else:
        result = await map_reduce_summarize(req.text)

    return {
        "summary": result["summary"] if "summary" in result else result["final_summary"],
        "chunks_processed": result["chunks_processed"],
        "strategy": req.strategy,
    }


@app.post("/documents/classify-batch")
async def classify_batch_endpoint(items: list[dict]):
    results = await batch_classify(items)
    valid, invalid = validate_and_separate(results)
    return {
        "valid": valid,
        "invalid": invalid,
        "success_rate": len(valid) / len(items) if items else 0,
    }
```

## 운영 체크리스트

- [ ] Map 단계 청크 크기가 모델 컨텍스트 한도의 60% 이내로 설정되어 있습니다.
- [ ] JSON 추출 실패 시 재시도 로직이 있습니다.
- [ ] 배치 처리 중 개별 아이템 실패가 전체 배치를 중단시키지 않습니다.
- [ ] 긴 문서 처리 시 예상 비용을 미리 계산합니다.
- [ ] 추출 결과에 대한 스키마 검증이 Pydantic으로 이루어집니다.
- [ ] 배치 분류 동시 요청 수가 Semaphore로 제한됩니다.
- [ ] 분류 카테고리 이탈 값이 validation 단계에서 차단됩니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| Map 청크를 너무 작게 설정 | 맥락 손실로 요약 품질 저하 | 청크를 600-1000 단어로 설정 |
| Reduce 없이 청크 요약만 반환 | 요약이 파편화되어 독자 혼란 | Reduce 단계에서 통합 요약 필수 |
| JSON 강제 없이 텍스트 파싱 | 구조화 데이터 추출 실패율 높음 | response_format json_object 사용 |
| 동시 요청 수 제한 없음 | OpenAI 레이트 리밋 오류 (429) | Semaphore로 동시성 5-10개로 제어 |
| 분류 카테고리를 프롬프트에만 나열 | 모델이 임의 카테고리 생성 | 허용 카테고리를 JSON 스키마로 명시 |
| 추출 후 Pydantic 검증 없음 | 잘못된 타입/범위 값이 DB에 저장 | model_validate()로 즉시 검증 |
| 배치 실패 건 격리 없음 | 2건 실패가 전체 500건 배치 중단 | 개별 try-except로 실패 건만 분리 |
| Refine과 Map-Reduce 구분 없이 사용 | 맥락 의존도 높은 문서에서 품질 저하 | 법률/계약 문서는 Refine, 뉴스/보고서는 Map-Reduce |

## 처음 질문으로 돌아가기

- **컨텍스트 길이를 초과하는 문서는 어떻게 요약할 수 있을까요?**
  Map-Reduce 패턴을 사용합니다. 문서를 800단어 청크로 분할해 병렬 요약하고(Map), 청크 요약들을 하나로 통합합니다(Reduce). 청크 간 맥락 연속성이 중요하면 Refine 전략을 선택하세요.

- **LLM으로 구조화된 JSON 데이터를 안정적으로 추출하려면 어떻게 해야 할까요?**
  `response_format={"type": "json_object"}`로 JSON 응답을 강제하고, Pydantic 모델로 스키마를 정의해 파싱 후 검증합니다. 프롬프트에 JSON 스키마를 직접 포함하고 "찾을 수 없으면 null" 규칙을 명시하면 환각을 줄입니다.

- **배치 처리 시 레이트 리밋을 어떻게 관리할까요?**
  `asyncio.Semaphore`로 동시 요청 수를 5-10개로 제한하고, 요청 간 0.1초 딜레이를 추가합니다. 개별 아이템 실패를 catch해 전체 배치가 중단되지 않도록 오류 처리를 분리합니다.

- **Map-Reduce Reduce 단계가 품질에 미치는 영향은 무엇일까요?**
  Reduce 프롬프트가 약하면 청크 요약을 단순 이어붙이는 것과 다르지 않습니다. "중복 제거", "논리 흐름 유지", "핵심 결론 강조" 지시를 명확히 넣어야 진짜 통합 요약이 만들어집니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): Chatbot 패턴](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
- **AI App Patterns 101 (3/6): Document Assistant 패턴 (현재 글)**
- [AI App Patterns 101 (4/6): Agent Tool 패턴](./04-agent-tool-pattern.md)
- [AI App Patterns 101 (5/6): Workflow Automation 패턴](./05-workflow-automation.md)
- [AI App Patterns 101 (6/6): Human-in-the-Loop 패턴](./06-human-in-the-loop.md)

<!-- toc:end -->

## 참고 자료

- [LangChain — Document Summarization](https://python.langchain.com/docs/use_cases/summarization)
- [OpenAI — Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic — BaseModel](https://docs.pydantic.dev/latest/)
- [Python asyncio — Semaphore](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: DocumentAI, Summarization, Extraction, MapReduce, LLM
