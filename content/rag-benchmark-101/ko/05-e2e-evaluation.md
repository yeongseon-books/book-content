---
title: "RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가"
series: rag-benchmark-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- RAGAS
- Faithfulness
- AnswerRelevancy
- LLM
- Evaluation
last_reviewed: '2026-05-12'
seo_description: 종단 간 평가는 질문, 컨텍스트, 답변을 하나의 흐름으로 관찰할 때 비로소 의미가 생깁니다.
---

# RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가

종단 간 평가는 질문, 컨텍스트, 답변을 하나의 흐름으로 관찰할 때 비로소 의미가 생깁니다. 이 글은 RAG Benchmark 101 시리즈의 다섯 번째 글입니다. 여기서는 검색과 생성이 같은 데이터 경로 위에서 어떻게 만나며, 어디서 품질이 무너지는지 RAGAS로 구조적으로 측정하는 방법을 정리하겠습니다.

![질문, 컨텍스트, 답변이 평가 입력으로 묶이는 구조](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-01-dataset-structure-for-end-to-end-evaluat.ko.png)
*질문, 컨텍스트, 답변이 평가 입력으로 묶이는 구조*
> 종단 간 평가는 "답이 맞아 보이는가"를 묻는 인상 비평이 아닙니다. **답변이 컨텍스트에 근거하고 실제 질문에 답하는지**를 구조화된 점수로 읽는 과정입니다.

## 먼저 던지는 질문

- 검색 지표가 좋아도 최종 답변이 나쁘면 어느 단계를 다시 봐야 할까요?
- 검색, 생성, 근거성 평가를 한 리포트에 묶으면 어떤 디버깅이 쉬워질까요?
- LLM-as-judge나 RAGAS 점수는 어떤 기준선 없이 쓰면 위험할까요?

## 왜 이 주제가 중요한가

2편부터 4편까지 측정한 것은 모두 검색 단계의 품질이었습니다. 하지만 사용자가 실제로 보는 것은 LLM이 만든 최종 답변입니다. 검색이 완벽해도 LLM이 컨텍스트를 무시하면 환각이 생길 수 있고, 반대로 LLM이 좋아도 검색이 잘못된 문서를 가져오면 답변 품질은 한계가 분명합니다.

따라서 운영 환경의 RAG는 두 층을 모두 봐야 합니다.

- **검색 지표**: hit rate, MRR, recall — "올바른 문서를 가져왔는가?"
- **생성 지표**: faithfulness, answer relevancy — "답변이 그 문서에 근거하고 질문에 답하는가?"

이 글의 목표는 두 번째 축을 세우는 것입니다. 핵심 도구는 [RAGAS](https://docs.ragas.io/)이며, 이 도구는 LLM을 평가자로 사용해 답변의 충실도와 관련성을 계산합니다.

## 기본 멘탈 모델

종단 간 평가의 데이터 흐름은 아래와 같습니다.

```text
question  ──►  retriever  ──►  contexts (List[str])
                                    │
question + contexts  ──►  LLM  ──►  answer
                                    │
question + contexts + answer  ──►  RAGAS metrics
                                    │
                                    ▼
                          {faithfulness, answer_relevancy}
```

이 흐름에서 평가 데이터셋의 한 행은 `(question, contexts, answer)` 튜플입니다. 여기에 정답 답변이나 정답 컨텍스트가 있다면 `context_precision`, `context_recall` 같은 지표를 더 붙일 수 있습니다. 하지만 시작점으로는 `Faithfulness`와 `AnswerRelevancy`만으로도 충분한 신호를 얻을 수 있습니다.

다만 여기에는 비용이 있습니다. RAGAS는 점수를 계산할 때 LLM을 다시 호출합니다. 즉, 평가 자체가 추가 토큰과 지연 시간을 발생시킵니다. 그래서 이 평가는 매 요청 실시간으로 돌리는 기능이 아니라, 배치 평가나 CI 평가에 더 적합합니다.

## 핵심 개념

| 지표 | 측정 대상 | Ground truth 필요 여부 |
| --- | --- | --- |
| Faithfulness | 답변의 모든 주장이 컨텍스트에서 도출되는가 | 아니오 |
| Answer Relevancy | 답변이 질문에 직접 답하는가 | 아니오 |
| Context Precision | 검색된 문서 중 실제로 답변에 기여한 비율 | 예 |
| Context Recall | 정답 답변에 필요한 정보가 컨텍스트에 모두 있었는가 | 예 |

초기 단계에서는 Ground truth가 충분하지 않은 경우가 많습니다. 그럴 때 `Faithfulness`와 `AnswerRelevancy`가 좋은 출발점이 됩니다. 정답 답변이 없어도 답변이 문맥에 기반하는지, 질문을 제대로 받았는지 확인할 수 있기 때문입니다.

## 수동 리뷰만 할 때와 구조화 평가를 할 때

이전에는 PR 리뷰에서 "답변이 그럴듯하다"는 문장 하나로 머지될 수 있습니다. 환각은 운영에서 사용자가 신고하기 전까지 잘 드러나지 않습니다.

이후에는 RAGAS가 50개 질문에 대해 자동으로 faithfulness와 answer relevancy를 계산합니다.

```text
metric              before  after
faithfulness        0.78    0.91
answer_relevancy    0.82    0.85
```

예를 들어 faithfulness가 0.78에서 0.91로 올랐다면, 답변이 컨텍스트 밖 주장으로 새는 비율이 줄었다는 뜻입니다. 이 값은 환각 감소를 직접적으로 시사합니다.

## 단계별로 종단 간 평가 만들기

### 1단계 — 평가 데이터셋 만들기

```python
from datasets import Dataset

samples = []
for question in QUESTIONS:
    docs = retriever.invoke(question)
    contexts = [doc.page_content for doc in docs]
    answer = llm.invoke(build_prompt(question, contexts)).content
    samples.append({
        "question": question,
        "contexts": contexts,   # List[str], not a single string
        "answer": answer,
    })

dataset = Dataset.from_list(samples)
```

여기서 가장 흔한 실수는 `contexts`를 단일 문자열로 넘기는 것입니다. RAGAS는 `List[str]`를 기대하므로, 문자열 하나로 합치면 내부에서 에러가 날 수 있습니다.

### 2단계 — LLM과 임베딩을 wrapper로 연결하기

![RAGAS 평가기로 들어가는 wrapper 경로](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-02-wrapper-path-into-the-ragas-evaluator.ko.png)

*RAGAS 평가기로 들어가는 wrapper 경로*

```python
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

ragas_llm = LangchainLLMWrapper(llm)
ragas_emb = LangchainEmbeddingsWrapper(embedding)
```

평가용 LLM은 가능한 한 결정적으로 동작해야 하므로 `temperature=0`으로 두는 편이 안전합니다. 그렇지 않으면 같은 데이터셋을 두 번 평가했을 때 점수 흔들림이 커질 수 있습니다.

### 3단계 — 평가 실행하기

```python
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.run_config import RunConfig

result = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), AnswerRelevancy(strictness=1)],
    llm=ragas_llm,
    embeddings=ragas_emb,
    run_config=RunConfig(timeout=300, max_workers=1),
)
print(result)
```

실행 코드는 `rag-benchmark-101/en/05-e2e-evaluation/main.py`에 있습니다. `GROQ_API_KEY`가 필요합니다.

```bash
cd en/05-e2e-evaluation
export GROQ_API_KEY=...
python3 main.py
```

여기서는 ragas 0.1.22의 클래스 기반 API를 그대로 사용합니다. 버전이 달라지면 import 경로와 사용 방식도 달라질 수 있으므로, 문서와 코드 버전을 함께 고정하는 습관이 중요합니다.

### 4단계 — 결과를 검색 실패와 생성 실패로 나눠 읽기

![검색 실패와 생성 실패를 분리해 읽는 해석 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-03-reading-retrieval-and-generation-failure.ko.png)

*검색 실패와 생성 실패를 분리해 읽는 해석 축*

| Faithfulness | Answer Relevancy | Diagnosis |
| --- | --- | --- |
| Low | Low | 검색이 무관한 문서를 가져왔거나, LLM이 컨텍스트를 무시했을 가능성 |
| Low | High | 그럴듯하지만 환각인 답변. 가장 위험한 경우 |
| High | Low | 컨텍스트에는 충실하지만 질문을 빗나감. 프롬프트를 의심할 만함 |
| High | High | 건강한 상태 |

특히 **Faithfulness는 낮고 Answer Relevancy는 높은** 경우를 눈여겨봐야 합니다. 사용자는 답변이 질문에 잘 맞는다고 느끼지만, 실제 근거는 빈약한 상태이기 때문입니다.

## 자주 하는 실수

- **`contexts`를 문자열 하나로 넘기기** — 반드시 `List[str]`여야 합니다.
- **`max_workers`를 크게 잡기** — 외부 LLM API는 rate limit이 있으므로 처음에는 보수적으로 시작해야 합니다.
- **`temperature > 0`로 평가하기** — 평가자 LLM은 가능한 한 결정적이어야 합니다.
- **검색 점수와 분리하지 않기** — RAGAS 점수가 떨어져도 검색이 문제인지 생성이 문제인지 모르면 고칠 방향을 잡기 어렵습니다.
- **버전 차이를 무시하기** — RAGAS 0.1.x와 0.2.x는 API가 다를 수 있습니다.

## 운영 환경으로 가져갈 때

운영에서는 평가 데이터셋 크기와 비용 균형이 중요합니다. 시작은 30~50개 질문이면 충분하고, 안정화되면 200~500개로 늘릴 수 있습니다. 매 PR마다 전체를 돌리기보다, 계층 표본 50개 정도를 빠르게 돌리고 야간 작업에서 전체를 평가하는 편이 현실적입니다.

가능하다면 생성에 쓰는 LLM과 평가에 쓰는 LLM을 분리하는 편이 좋습니다. 같은 모델이 자기 답을 평가하면 편향이 생길 수 있기 때문입니다. 또한 결과는 점수만 남기지 말고 `(question, answer, contexts, score, reasoning)`까지 보존해야 회귀를 디버깅할 수 있습니다.

결국 종단 간 평가는 검색 지표를 대체하는 것이 아니라 보완합니다. Faithfulness가 낮을 때 검색 품질이 이미 낮았다면 먼저 검색부터 고쳐야 합니다. 반대로 검색은 양호한데 faithfulness만 낮다면 프롬프트나 생성 모델을 의심해야 합니다.

## 체크리스트

![지표 실행 전 데이터셋 형태와 실행 조건을 확인하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-04-verification-flow-before-metric-executio.ko.png)

*지표 실행 전 데이터셋 형태와 실행 조건을 확인하는 흐름*

- [ ] ragas 0.1.22의 클래스 기반 API(`Faithfulness()`, `AnswerRelevancy()`)를 사용했는가?
- [ ] LLM과 임베딩을 `LangchainLLMWrapper`, `LangchainEmbeddingsWrapper`로 감쌌는가?
- [ ] `Dataset`에 `question`, `contexts`(List[str]), `answer` 컬럼이 있는가?
- [ ] `temperature=0`이고 `max_workers`를 보수적으로 잡았는가?
- [ ] 검색 지표와 생성 지표를 함께 보고 있는가?

## 연습 문제

1. Ground truth를 추가해 `ContextPrecision`과 `ContextRecall`까지 계산해 보세요. 어떤 추가 신호가 보이나요?
2. 같은 질문에 대해 검색기가 일부러 틀린 문서를 돌려주게 해 보세요. faithfulness와 answer relevancy 중 무엇이 먼저 떨어지나요?
3. 생성과 평가에 같은 모델을 쓸 때와 다른 모델을 쓸 때를 비교해 보세요. 점수 차이가 있나요?

## 정리와 다음 글

이 글에서는 RAGAS를 이용해 faithfulness와 answer relevancy를 측정하는 종단 간 평가 루프를 만들었습니다. 핵심은 세 가지입니다. **데이터셋 형태를 정확히 맞추고, wrapper로 평가기를 연결하고, 검색 점수와 생성 점수를 함께 읽는 것**입니다.

다음 글에서는 1편부터 5편까지의 도구를 하나로 묶습니다. 검색, 생성, 평가 결과를 한 번에 내는 통합 벤치마크 파이프라인이 시리즈의 마지막 주제입니다.

## 종단 간 평가 리포트를 운영 가능한 형태로 확장하기

종단 간 평가에서 가장 큰 실패는 점수 평균만 남기고 샘플 근거를 버리는 것입니다. 운영에서는 "왜 떨어졌는가"를 설명할 수 있어야 하므로, 아래 세 층을 함께 저장해야 합니다.

1. 집계 점수: faithfulness, answer relevancy, 검색 지표
2. 샘플별 점수: 질문 단위의 세부 점수
3. 근거 데이터: contexts, answer, 참조 문서 ID

### RAGAS 출력과 검색 출력 결합 예시

```python
def merge_eval_rows(retrieval_rows, ragas_df):
    merged = []
    for idx, r in enumerate(retrieval_rows):
        merged.append({
            "query_id": r["query_id"],
            "question": r["question"],
            "ranked_ids": r["ranked_ids"],
            "hit@5": r["hit@5"],
            "mrr": r["mrr"],
            "answer": r["answer"],
            "faithfulness": float(ragas_df.iloc[idx]["faithfulness"]),
            "answer_relevancy": float(ragas_df.iloc[idx]["answer_relevancy"]),
        })
    return merged
```

이 구조를 쓰면 "검색은 맞았는데 답변 근거성이 떨어진 질문"을 즉시 필터링할 수 있습니다.

### 판정 규칙을 명시적으로 두기

점수만 나열하면 의사결정이 지연됩니다. 아래처럼 판정 규칙을 함께 두면 결과 해석이 빨라집니다.

| 조건 | 판정 | 다음 액션 |
| --- | --- | --- |
| hit@5 낮음 + faithfulness 낮음 | 검색-생성 동시 실패 | 인덱스/임베딩/프롬프트 동시 점검 |
| hit@5 높음 + faithfulness 낮음 | 생성 근거성 실패 | 인용 강제 프롬프트, 답변 포맷 제한 |
| hit@5 낮음 + faithfulness 높음 | 검색 누락 | chunking, query expansion, reranker |
| answer relevancy 낮음 | 질문 해석 실패 | 시스템 프롬프트와 질문 정규화 수정 |

### 평가자 일관성을 위한 프롬프트 버전 고정

LLM-as-judge는 평가 프롬프트가 바뀌면 점수 분포도 같이 바뀝니다. 그래서 평가 프롬프트를 버전 문자열로 고정해 리포트에 남겨야 합니다.

```yaml
evaluator:
  provider: groq
  model: llama-3.1-8b-instant
  temperature: 0
  prompt_version: ragas-faithfulness-v3
  max_workers: 1
```

프롬프트 버전을 남기지 않으면, 다음 달 점수 변화가 모델 변화인지 평가 기준 변화인지 구분하기 어렵습니다.

### LangSmith 트레이스 연동 예시

질문별 실패를 빠르게 재현하려면 실행 ID와 트레이스를 연결하는 편이 좋습니다.

```python
trace_row = {
    "query_id": query_id,
    "run_id": run_id,
    "langsmith_trace_url": trace_url,
    "faithfulness": faithfulness,
    "answer_relevancy": answer_relevancy,
}
```

리포트에서 낮은 점수 행을 클릭해 바로 트레이스로 이동할 수 있으면 디버깅 시간이 크게 줄어듭니다.

### RAGAS 실행 결과 텍스트 예시

```text
RAGAS aggregate:
  faithfulness: 0.872
  answer_relevancy: 0.846

Worst cases by faithfulness:
  q-014: 0.41 (질문: "IVF nprobe를 1로 두면?")
  q-033: 0.45 (질문: "chunk overlap 권장값은?")
```

이 출력은 단순 평균보다 훨씬 실용적입니다. 팀은 즉시 최악 사례 두세 개를 열어 원인 분석을 시작할 수 있습니다.

### 프로덕션용 평가 실행 정책

평가 비용과 안정성을 위해 다음 정책을 자주 사용합니다.

| 실행 종류 | 샘플 수 | 주기 | 목적 |
| --- | ---: | --- | --- |
| PR 경량 평가 | 30~50 | PR마다 | 회귀 빠른 감지 |
| Nightly 표준 평가 | 200~400 | 매일 | 추세 모니터링 |
| 릴리스 전 전체 평가 | 500+ | 릴리스 직전 | 승인 근거 확보 |

이 정책을 문서화해 두면 "언제 어떤 점수를 신뢰할 것인가"에 대한 조직 합의를 만들 수 있습니다.

## 실전 부록: 종단 간 평가 임계치와 실패 샘플 기록

종단 간 평가는 점수만 맞추는 작업이 아니라 위험 질문을 관리하는 작업입니다. 그래서 임계치와 샘플 보관 정책을 같이 두는 편이 좋습니다.

### 임계치 정책 예시

| 지표 | 경고 | 차단 | 비고 |
| --- | ---: | ---: | --- |
| faithfulness | 0.86 미만 | 0.82 미만 | 환각 위험 증가 |
| answer relevancy | 0.84 미만 | 0.80 미만 | 질문 비적합 답변 증가 |
| retrieval hit@5 | 0.90 미만 | 0.86 미만 | 근거 문서 누락 증가 |

차단 기준은 한 번에 엄격하게 올리기보다, 2주 이상의 baseline 분포를 본 뒤 단계적으로 조정하는 방식이 안전합니다.

### 실패 샘플 저장 포맷

```json
{
  "query_id": "q-108",
  "question": "nprobe를 줄이면 어떤 트레이드오프가 생기나요?",
  "contexts": ["..."],
  "answer": "...",
  "scores": {
    "faithfulness": 0.41,
    "answer_relevancy": 0.79,
    "hit@5": 1.0
  },
  "diagnosis": "retrieval-ok-generation-hallucination"
}
```

`diagnosis` 같은 분류 키를 추가해 두면 회귀 사례를 유형별로 빠르게 집계할 수 있습니다.

### 평가 실행 안정성 설정

```python
from ragas.run_config import RunConfig

run_config = RunConfig(
    timeout=300,
    max_workers=1,
    max_retries=2,
    retry_wait=2,
)
```

평가 파이프라인은 외부 API 의존성이 크기 때문에 timeout/retry를 명시하지 않으면 flaky 실패가 많아집니다.

### 리트리벌 품질과 생성 품질을 함께 보여 주는 요약 표

| bucket | 질문 수 | avg hit@5 | avg faithfulness | avg answer relevancy |
| --- | ---: | ---: | ---: | ---: |
| 쉬운 질문 | 80 | 0.97 | 0.92 | 0.90 |
| 중간 질문 | 90 | 0.91 | 0.86 | 0.85 |
| 어려운 질문 | 40 | 0.82 | 0.76 | 0.79 |

이 표는 난이도별 품질 격차를 드러내기 때문에, 개선 우선순위를 정할 때 실용적입니다.

### 실패 케이스 라벨링 체계 예시

질문별 회귀를 빠르게 분류하려면 라벨링 체계를 먼저 정해 두는 편이 좋습니다.

| label | 의미 |
| --- | --- |
| retrieval-miss | 정답 문서 미회수 |
| grounded-but-offtopic | 근거는 있으나 질문 비적합 |
| hallucination-with-confidence | 자신감 있는 무근거 답변 |
| citation-format-error | 근거 문서 인용 형식 오류 |

라벨이 고정되면 월간 품질 회고에서 실패 비율 변화를 쉽게 추적할 수 있습니다.

라벨링 체계를 유지할 때는 최소 주 1회 표본 검수를 권장합니다. 자동 라벨링 규칙이 누적 편향을 만들 수 있기 때문입니다. 사람이 주기적으로 확인한 라벨 샘플을 기준선으로 유지하면, 평가 파이프라인의 해석 품질도 함께 안정화됩니다.

평가 리포트를 공유할 때는 낮은 점수 사례만이 아니라 개선된 사례도 같이 포함하는 편이 좋습니다. 실패 사례만 누적되면 팀이 원인만 찾고 성공 패턴을 재사용하지 못하는 경우가 많기 때문입니다. 성공 사례를 함께 기록하면 프롬프트와 검색 설정의 유효 패턴을 더 빠르게 확산할 수 있습니다.

### RAGAS 배치 평가 코드 확장

실무에서는 평균 점수만 출력하면 디버깅이 어렵습니다. 샘플별 점수와 입력 데이터를 함께 저장해 두어야 회귀 분석이 가능합니다. 아래처럼 DataFrame으로 내보내는 코드를 붙이면 재검토가 쉬워집니다.

```python
import pandas as pd

result = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), AnswerRelevancy(strictness=1)],
    llm=ragas_llm,
    embeddings=ragas_emb,
    run_config=RunConfig(timeout=300, max_workers=1),
)

score_df = result.to_pandas()
full_df = pd.concat([dataset.to_pandas(), score_df], axis=1)
full_df.to_csv("ragas_report.csv", index=False)

print(full_df[["question", "faithfulness", "answer_relevancy"]].head(10))
```

이 파일을 PR 아티팩트로 남기면, 점수 하락이 생겼을 때 어떤 질문에서 무너졌는지 즉시 추적할 수 있습니다.

### 종단 간 테스트 스크립트 예시

배포 파이프라인에서는 "검색 + 생성 + 평가"가 한 번에 실행되는 스크립트가 필요합니다. 아래 예시는 실패 임계치를 넘으면 종료 코드 1로 실패시키는 구조입니다.

```python
#!/usr/bin/env python3
import json
import sys

from my_rag_eval import run_rag_eval  # returns dict with aggregate scores

THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.82,
}

def main() -> int:
    report = run_rag_eval(sample_size=50)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    for metric, minimum in THRESHOLDS.items():
        score = report["aggregate"][metric]
        if score < minimum:
            print(f"FAIL: {metric}={score:.3f} < {minimum:.3f}")
            return 1

    print("PASS: e2e RAG evaluation thresholds satisfied")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

이 스크립트를 CI에서 nightly로 실행하면, 검색 인덱스 변경이나 프롬프트 변경이 실제 답변 품질에 미친 영향을 조기에 감지할 수 있습니다.

### 평가 비용과 안정성 관리

RAGAS는 유용하지만 비용이 들기 때문에 실행 정책을 분리하는 편이 좋습니다. PR마다 30~50개 샘플로 빠르게 회귀만 확인하고, 야간에는 300개 이상으로 안정 추세를 보는 식입니다. 또한 동일 데이터셋을 주기적으로 재평가해 평가 모델 드리프트를 모니터링하면, 점수 변화가 앱 문제인지 평가자 문제인지 분리하는 데 도움이 됩니다.

## 처음 질문으로 돌아가기

- **검색 지표가 좋아도 최종 답변이 나쁘면 어느 단계를 다시 봐야 할까요?**
  검색은 좋아졌는데 답변이 나쁘다면 프롬프트 구성, context 주입, 생성 설정, 근거성 평가를 다음으로 봐야 합니다.

- **검색, 생성, 근거성 평가를 한 리포트에 묶으면 어떤 디버깅이 쉬워질까요?**
  한 리포트에 묶으면 “검색 실패”, “근거는 맞지만 답변 실패”, “답변은 좋지만 출처 누락” 같은 유형을 빠르게 나눌 수 있습니다.

- **LLM-as-judge나 RAGAS 점수는 어떤 기준선 없이 쓰면 위험할까요?**
  기준선과 샘플 리뷰 없이 judge 점수만 보면 평가 모델의 편향이나 프롬프트 변화가 실제 개선처럼 보일 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG Evaluation and Benchmarking 101 (1/6): RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정](./02-retrieval-benchmarking.md)
- [RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교](./03-embedding-comparison.md)
- [RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준](./04-vectordb-selection.md)
- **RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가 (현재 글)**
- RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [RAGAS documentation](https://docs.ragas.io/)
- [RAGAS GitHub repository](https://github.com/explodinggradients/ragas)
- [Groq Python integration in LangChain](https://python.langchain.com/docs/integrations/chat/groq/)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/05-e2e-evaluation)

Tags: RAG, VectorDB, Benchmarking, LLM
