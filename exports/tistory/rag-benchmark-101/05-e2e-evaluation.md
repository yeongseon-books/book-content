
# 종단 간 RAG 파이프라인 평가

<!-- a-grade-intro:begin -->
## 핵심 질문

검색·생성·정책을 합친 종단 간 RAG 평가는 어떻게 설계하나요?

이 글은 그 질문에 답하기 위해 종단 간 RAG 평가의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- retrieval 지표와 generation 지표를 분리해서 보는 것이 왜 중요한지 이해합니다.
- LLM 기반 평가(faithfulness, relevance)와 문자열 지표(BLEU, ROUGE)의 차이를 구분합니다.
- 종단 간 평가 파이프라인을 Python으로 구성하는 실습을 합니다.
- 평가 결과를 해석해서 retrieval과 generation 중 어디를 개선해야 하는지 판단할 수 있습니다.

## 이 글에서 답할 질문

![이 글에서 답할 질문](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*

- ragas 0.1.22에서 `Faithfulness`와 `AnswerRelevancy`를 실제로 어떻게 계산하나요?
- LangChain LLM과 임베딩 모델을 RAGAS wrapper에 어떻게 연결하나요?
- 검색이 아니라 **최종 답변의 품질**을 볼 때는 어떤 데이터셋 모양이 필요한가요?
- 검색 실패와 생성 실패를 어떻게 분리해서 진단할 수 있나요?

> 종단 간(end-to-end) 평가는 "답이 맞아 보이는가"가 아니라, **답이 컨텍스트에 근거했고 질문에 직접 답했는가**를 구조화된 점수로 보는 일입니다.

## 왜 중요한가

지금까지(2~4편) 측정한 것은 모두 "검색 단계"의 품질이었습니다. 하지만 사용자가 보는 것은 LLM이 만든 최종 답변입니다. 검색이 완벽해도 LLM이 컨텍스트를 무시하면 답변은 hallucination이 됩니다. 반대로 LLM이 훌륭해도 검색이 엉뚱한 문서를 가져오면 답변 품질은 그 문서 품질을 넘지 못합니다.

따라서 RAG 시스템을 운영할 때는 두 단계를 모두 측정해야 합니다.

- **Retrieval metrics**: hit rate, MRR, recall — "올바른 문서를 가져왔는가"
- **Generation metrics**: faithfulness, answer relevancy — "답변이 그 문서에 근거하고 질문에 답했는가"

이 글에서는 두 번째 축을 만듭니다. 핵심 도구는 [RAGAS](https://docs.ragas.io/)입니다. RAGAS는 LLM을 심판으로 써서 답변의 충실도와 관련성을 점수화합니다.

## Mental Model

종단 간 평가의 데이터 흐름은 다음과 같습니다.

```
question  ──►  retriever  ──►  contexts (List[str])
                                    │
question + contexts  ──►  LLM  ──►  answer
                                    │
question + contexts + answer  ──►  RAGAS metrics
                                    │
                                    ▼
                          {faithfulness, answer_relevancy}
```

평가 데이터셋의 한 행은 `(question, contexts, answer)` 튜플입니다. ground truth가 있으면 `context_precision`, `context_recall` 같은 지표도 추가할 수 있습니다.

RAGAS는 내부적으로 LLM을 한 번 더 호출해 점수를 매깁니다. 즉 평가 자체에 LLM 호출 비용과 latency가 발생합니다.

## 핵심 개념

| 지표 | 측정 대상 | ground truth 필요? |
| --- | --- | --- |
| Faithfulness | 답변의 모든 주장이 컨텍스트에서 도출되는가 | 아니오 |
| Answer Relevancy | 답변이 질문에 직접 답하는가 | 아니오 |
| Context Precision | 검색된 문서 중 실제로 답변에 쓰인 비율 | 예 |
| Context Recall | 정답에 필요한 정보가 컨텍스트에 들어 있는가 | 예 |

`Faithfulness`와 `AnswerRelevancy`는 ground truth 없이도 계산되므로, 골드셋이 작거나 아직 만들지 못한 초기 단계에 적합합니다.

## Before vs. After

**Before**: PR 리뷰에서 "답변이 그럴듯하다"는 한 줄 코멘트로 머지합니다. 운영에서 사용자가 "근거 없는 답을 받았다"고 신고할 때까지 hallucination을 발견하지 못합니다.

**After**: 매 PR에서 RAGAS가 자동으로 50개 질문에 대한 faithfulness/answer_relevancy를 계산합니다.

```
metric              before  after
faithfulness        0.78    0.91
answer_relevancy    0.82    0.85
```

faithfulness가 0.78에서 0.91로 올랐다는 것은 hallucination이 줄었다는 직접적인 증거입니다.

## 단계별 실습

### 1단계 — 평가 데이터셋 준비

![질문과 컨텍스트와 답변이 평가 입력으로 묶이는 구조](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-01-dataset-structure-for-end-to-end-evaluat.ko.png)

*질문과 컨텍스트와 답변이 평가 입력으로 묶이는 구조*

```python
from datasets import Dataset

samples = []
for question in QUESTIONS:
    docs = retriever.invoke(question)
    contexts = [doc.page_content for doc in docs]
    answer = llm.invoke(build_prompt(question, contexts)).content
    samples.append({
        "question": question,
        "contexts": contexts,   # List[str], 단일 문자열 X
        "answer": answer,
    })

dataset = Dataset.from_list(samples)
```

`contexts`는 반드시 문자열 리스트입니다. 단일 문자열로 넘기면 RAGAS 내부에서 KeyError가 발생합니다.

### 2단계 — LLM과 임베딩 wrapper 연결

![LLM wrapper와 임베딩 wrapper가 평가기에 연결되는 경로](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-02-wrapper-path-into-the-ragas-evaluator.ko.png)

*LLM wrapper와 임베딩 wrapper가 평가기에 연결되는 경로*

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

### 3단계 — 평가 실행

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

실행 코드는 `rag-benchmark-101/ko/05-e2e-evaluation/main.py`에 있습니다. `GROQ_API_KEY`가 필요합니다.

```bash
cd /root/Github/rag-benchmark-101/ko/05-e2e-evaluation
export GROQ_API_KEY=...
python3 main.py
```

### 4단계 — 결과 해석

![검색 실패와 생성 실패를 분리해 읽는 해석 축](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-03-reading-retrieval-and-generation-failure.ko.png)

*검색 실패와 생성 실패를 분리해 읽는 해석 축*

| Faithfulness | Answer Relevancy | 진단 |
| --- | --- | --- |
| 낮음 | 낮음 | 검색이 무관한 문서를 줬거나, LLM이 컨텍스트를 무시 |
| 낮음 | 높음 | 답변이 그럴듯하지만 hallucination — 가장 위험 |
| 높음 | 낮음 | 컨텍스트에 충실하지만 질문을 빗나감 — prompt를 의심 |
| 높음 | 높음 | 정상 |

특히 "낮음 / 높음"은 사용자에게 자신감 있게 잘못된 답을 주는 패턴입니다. 우선순위로 잡아야 합니다.

## 자주 하는 실수

- **`contexts`를 단일 문자열로 전달** — 반드시 `List[str]`. 자주 발생하는 KeyError의 원인입니다.
- **`max_workers`를 크게 설정** — Groq, OpenAI 같은 외부 LLM은 rate limit이 있습니다. 처음에는 1로 두고 늘립니다.
- **`temperature > 0`** — 평가 LLM은 deterministic이어야 합니다. `temperature=0`을 강제합니다.
- **검색 단계 점수와 분리하지 않기** — RAGAS 점수가 낮을 때 retrieval 실패 때문인지 generation 실패 때문인지 알 수 없습니다. 2~4편의 hit rate, MRR을 함께 봐야 합니다.
- **버전 차이 무시** — RAGAS는 0.1.x와 0.2.x에서 import 경로와 metric 생성 방식이 다릅니다. 이 글은 0.1.22 기준입니다.

## 실무 적용

![데이터셋 형태와 실행 조건을 먼저 확인하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/05/05-04-verification-flow-before-metric-executio.ko.png)

*데이터셋 형태와 실행 조건을 먼저 확인하는 흐름*

- **평가 데이터셋 크기**: 시작은 30~50개. 안정화 후 200~500개로 확장. 1,000개를 넘기면 비용과 시간이 부담스러워집니다.
- **샘플링 전략**: 매 PR마다 stratified 50개를 빠르게 돌리고, 야간에 전체를 돌립니다.
- **평가 LLM 선택**: 평가용 LLM을 **생성 LLM과 다른** 모델로 두면 self-bias를 줄일 수 있습니다(예: 생성은 Llama-3.1, 평가는 GPT-4o-mini).
- **결과 저장**: 점수만 저장하지 말고 (question, answer, contexts, score, reasoning)를 함께 남깁니다. 회귀 디버깅의 출발점입니다.
- **CI 게이트**: faithfulness가 기준치 아래로 떨어지면 PR 차단. answer_relevancy는 처음에는 경고만으로 시작합니다.

## 실무에서는 이렇게 생각한다

E2E 평가에서 가장 자주 나오는 실수는 generation 품질이 낮을 때 무조건 프롬프트를 손보는 것입니다. 하지만 대부분의 나쁜 응답은 retrieval이 잘못된 문서를 가져와서 생기는 것입니다. retrieval 지표를 먼저 분리해서 보지 않으면 프롬프트만 돌리다 시간을 낭비하게 됩니다.

LLM 기반 평가(LLM-as-a-judge)는 편리하지만 비용과 일관성 문제가 있습니다. 같은 응답을 두 번 평가하면 점수가 달라질 수 있습니다. 그래서 실무에서는 LLM 평가를 스크리닝 도구로 쓰고, 최종 판단은 도메인 전문가의 샘플 리뷰로 보완하는 방식이 현실적입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **골든 셋** — 질문·기대 답·근거 문서를 묶은 골든 셋이 출발점입니다.
- **Faithfulness 자동화** — 근거-답변 정렬 검사를 LLM-as-judge와 룰로 이중화합니다.
- **회귀 게이트** — 임계값을 넘지 못하면 배포를 막는 CI 게이트를 둡니다.
- **Cost·Latency 동시** — 품질 지표와 비용·latency를 한 보드에서 추적합니다.
- **실패 사례 누적** — 운영에서 발견한 실패 케이스를 골든 셋에 환류합니다.

## 체크리스트

- [ ] ragas 0.1.22의 클래스 기반 API(`Faithfulness()`, `AnswerRelevancy()`)로 metric 객체를 생성했다.
- [ ] LLM과 임베딩을 `LangchainLLMWrapper` / `LangchainEmbeddingsWrapper`로 감쌌다.
- [ ] `Dataset`이 `question`, `contexts`(List[str]), `answer` 컬럼을 가진다.
- [ ] `temperature=0`이고 `max_workers`가 보수적이다.
- [ ] retrieval metric(hit rate, MRR)과 generation metric(faithfulness, answer_relevancy)을 같이 본다.

## 연습 문제

1. ground truth를 추가해 `ContextPrecision`, `ContextRecall`을 함께 계산하도록 확장해 보세요. 어떤 신호가 새로 보이나요?
2. 같은 질문에 대해 retriever를 일부러 잘못된 문서로 바꿔 답변을 만들어 보세요. faithfulness와 answer_relevancy 중 어느 쪽이 먼저 떨어지나요?
3. 평가 LLM을 생성 LLM과 같게 / 다르게 두 번 돌려 보고 점수 차이를 비교해 보세요.

## 정리 · 다음 글

이번 글에서는 RAGAS로 종단 간 평가 루프를 만들고, faithfulness와 answer_relevancy로 hallucination과 관련성을 측정했습니다. 핵심은 **데이터셋 구조 맞추기**, **wrapper로 LLM/임베딩 연결**, **검색 점수와 생성 점수 함께 보기**입니다.

다음 글(6편)에서는 1~5편의 모든 측정 도구를 합쳐 **하나의 통합 벤치마크 리포트**를 만듭니다. 이 시리즈의 마무리입니다.

## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- [임베딩 모델 비교](./03-embedding-comparison.md)
- [VectorDB 선택 기준](./04-vectordb-selection.md)
- **종단 간 RAG 파이프라인 평가 (현재 글)**
- RAG 벤치마크 완성 (예정)

---

## 참고 자료

- [RAGAS documentation](https://docs.ragas.io/)
- [RAGAS GitHub repository](https://github.com/explodinggradients/ragas)
- [Groq Python integration in LangChain](https://python.langchain.com/docs/integrations/chat/groq/)
- [HuggingFace Datasets](https://huggingface.co/docs/datasets)

Tags: RAG, VectorDB, Benchmarking, LLM

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
