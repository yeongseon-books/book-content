---
title: "Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기"
series: korean-ai-stack-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- RAG
- Pipeline
- Retrieval
- LLM
- Python
last_reviewed: '2026-05-15'
seo_description: RAG 품질은 한 번의 마법 같은 호출이 아니라, 청크 경계와 검색 후보와 문맥 전달 방식이 함께 만드는 결과입니다.
---

# Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기

RAG는 어느 단계에서 실패했는지 눈에 보이기 시작하면 갑자기 덜 신비롭게 느껴집니다. 한국어 워크플로에서는 청킹, 검색, 생성이 각자 다른 종류의 오류를 만들기 때문에, 가장 현실적인 방법은 각 단계를 따로 들여다볼 수 있게 연결하는 것입니다.

이 글은 Korean AI Stack 101 시리즈의 마지막 글입니다. 여기서는 앞서 다룬 임베딩, OCR, 생성 조각을 하나의 최소 한국어 RAG 파이프라인으로 묶습니다.

![Korean AI Stack 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-01-core-flow.ko.png)
*Korean AI Stack 101 6장 흐름 개요*

## 먼저 던지는 질문

- 최소한의 한국어 RAG 파이프라인에서 빠질 수 없는 단계는 무엇일까요?
- 품질 병목은 보통 청킹, 임베딩, 검색, 생성 중 어디에서 가장 자주 생길까요?
- 검색된 문맥은 LLM에 들어가기 전에 어떤 형태로 정리해야 할까요?

## 이 글에서 배울 것

이 마지막 글은 시리즈에서 앞서 소개한 모든 조각을 연결합니다. 한국어 문서를 청크로 나누고, KoSimCSE 또는 BGE-M3로 임베딩하고, FAISS로 상위 청크를 찾고, 그 청크만 근거로 Groq 모델(또는 Solar / HyperCLOVA X)을 호출하는 최소 한국어 RAG 파이프라인을 만듭니다.

구체적으로는 네 가지 습관을 가져가면 됩니다.

1. **4단계 분해** — Ingest, Index, Retrieve, Generate를 별도 함수로 나눠 어느 단계가 병목인지 분리해서 봅니다.
2. **청크 경계 설계** — 문단, 고정 토큰, 문장 단위 청킹이 한국어에서 어떤 실패 패턴을 만드는지 이해합니다.
3. **검색과 생성 평가 분리** — Recall@k와 Faithfulness를 따로 측정해야 하는 이유를 익힙니다.
4. **추측 방지 프롬프트** — 문맥에 없으면 “모른다”고 답하게 하고, 출처 라인을 강제하는 패턴을 씁니다.

여기까지 익히면 30~50개 문서 규모의 작은 사내 위키 RAG를 만들고, 검색 실패와 hallucination을 별도로 디버깅할 수 있는 기초가 생깁니다.

---

## 왜 이 단계가 중요한가

LLM 단독 호출과 RAG의 차이는 **출처(provenance)**입니다. 예를 들어 사용자가 “결제는 됐는데 주문이 없다. 무엇부터 봐야 하나요?”라고 물었을 때, 독립형 LLM은 그럴듯하지만 실제 사내 정책과 맞지 않는 답을 지어낼 수 있습니다. 운영팀은 출처가 없는 답을 신뢰할 수 없습니다.

RAG가 어려운 이유는 단계 수가 많아서가 아니라, **단계별 책임 분리**가 어렵기 때문입니다. 답이 틀려 보이면 먼저 청킹이 어긋났는지, 임베딩이 의미를 놓쳤는지, top-k가 부족한지, 아니면 LLM이 문맥을 무시했는지 가려내야 합니다. end-to-end 호출 하나만 보면 이 진단이 거의 불가능합니다.

이 글의 코드는 중간 상태를 의도적으로 출력하고, 검색 점수와 선택된 청크 ID를 함께 남깁니다. 한국어 RAG에서는 청킹이 특히 자주 병목이 됩니다. 토크나이저가 공백과 형태소를 다르게 다루기 때문입니다. 어떤 청크가 선택됐는지 눈으로 확인하는 습관만으로도 디버깅 시간이 크게 줄어듭니다.

---

## 멘탈 모델 — 4단계 파이프라인

RAG는 네 개의 독립 단계로 분해됩니다.

| Stage | Input | Output | Quality metric |
|---|---|---|---|
| **Ingest** | Raw documents (PDF, HTML, OCR output) | Chunk list | Chunk length distribution, boundary placement |
| **Index** | Chunks + embedding model | FAISS index | Vector dimension, index size |
| **Retrieve** | Question embedding + index | Top-k chunks + scores | Recall@k |
| **Generate** | Question + retrieved chunks | Answer + citations | Faithfulness, speculation rate |

각 단계는 독립적으로 교체하고, 측정하고, 디버깅할 수 있습니다. Ingest 단계에서 청크 경계만 바꿔도 Recall@k가 크게 흔들릴 수 있고, Generate 단계에서 프롬프트만 바꿔도 hallucination 비율이 달라질 수 있습니다. 이 분리가 이 글 전체의 중심 멘탈 모델입니다.

> 한 문장으로 요약하면 이렇습니다. RAG는 “좋은 모델 하나”의 문제가 아니라, 입력 분해·검색·생성을 각자 측정 가능한 단계로 만드는 설계 문제입니다.

---

## 핵심 개념

### Chunking

청킹은 긴 문서를 검색 가능한 단위로 나누는 일입니다. 한국어에서는 보통 세 가지 전략을 자주 씁니다.

- **Paragraph** — `\n\n` 기준 분할. 가장 단순하고 의미 경계를 잘 보존합니다.
- **Fixed token** — 256~512토큰 단위에 50~100토큰 overlap을 둡니다. 길이가 예측 가능하고 인덱싱이 안정적입니다.
- **Sentence** — KSS나 kiwi로 문장 분리. 짧은 FAQ에는 잘 맞지만 각 청크가 너무 짧아질 수 있습니다.

### Embedding

청크를 벡터로 바꾸는 단계입니다. 한국어 단일 언어 코퍼스에는 KoSimCSE(2편)가, 다국어 코퍼스에는 BGE-M3(3편)가 일반적인 선택입니다. `normalize_embeddings=True`를 켜고 `IndexFlatIP`를 쓰면 코사인 유사도와 같은 결과를 얻습니다.

### Retrieval

질문 벡터와 가장 가까운 상위 k개 청크를 가져옵니다. 보통 k = 3~5에서 시작하고, LLM의 context window에 맞춰 조정합니다. 검색 점수는 항상 같이 로깅해야 나중에 품질을 감사할 수 있습니다.

### Generation

검색된 청크만 system 메시지에 넣어 LLM이 답하게 합니다. 꼭 지켜야 할 두 가지가 있습니다. (1) 문맥에 답이 없으면 “모른다”고 말하게 할 것, (2) 사용한 청크 번호를 인용하게 할 것.

---

## 적용 전후 비교
### 적용 전 — LLM 직접 호출

```python
client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': 'Payment succeeded but no order — what to check?'}],
)
```

LLM은 그럴듯한 일반론을 답합니다. 하지만 실제 사내 정책과 충돌할 수 있고, 출처도 없습니다.

### 적용 후 — RAG 파이프라인

```python
chunks = retrieve(question, top_k=3)        # internal-doc chunks
answer = generate(question, chunks)         # answer grounded only in chunks
print('sources:', [c['id'] for c in chunks])
```

답은 문서에 근거하고, 어떤 청크를 썼는지 정확히 추적할 수 있습니다.

---

## 단계별 실습

### 단계 1 — 청킹과 인덱싱

```python
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')

chunks = [
    '결제는 성공했지만 주문이 생성되지 않은 경우에는 주문 동기화 지연 여부를 먼저 확인합니다.',
    '결제 실패 문의는 카드 승인 실패와 주문 저장 실패를 분리해서 대응해야 합니다.',
    '환불 요청은 결제 채널별로 처리 시간이 다르며, 카드사 환불은 영업일 기준 3~5일이 소요됩니다.',
    '쿠폰이 적용되지 않을 때는 적용 조건(최소 주문 금액, 카테고리 제한, 만료일)을 먼저 확인합니다.',
]

vectors = model.encode(chunks, normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(vectors.shape[1])
index.add(vectors)
```

### 단계 2 — retrieval

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-01-minimal-runnable-example.ko.png)

*최소 실행 예제*

```python
def retrieve(question: str, top_k: int = 2) -> list[dict]:
    query_vec = model.encode([question], normalize_embeddings=True).astype('float32')
    distances, indices = index.search(query_vec, top_k)
    return [
        {'id': int(idx), 'score': float(score), 'text': chunks[idx]}
        for score, idx in zip(distances[0], indices[0])
    ]

question = '결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?'
hits = retrieve(question, top_k=2)
for h in hits:
    print(f"[{h['id']}] score={h['score']:.3f}  {h['text'][:40]}...")
```

### 단계 3 — generation

![이 코드에서 주목할 점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-02-what-to-notice-in-this-code.ko.png)

*이 코드에서 주목할 점*

```python
from groq import Groq

client = Groq()

def generate(question: str, hits: list[dict]) -> str:
    context = '\n\n'.join(f"[{h['id']}] {h['text']}" for h in hits)
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {
                'role': 'system',
                'content': (
                    'Answer ONLY using the provided context. '
                    'If the answer is not in the context, reply '
                    '"I could not find a relevant policy" and do not speculate. '
                    'End the answer with a citation in the form [sources: 0,1].'
                ),
            },
            {'role': 'user', 'content': f'Context:\n{context}\n\nQuestion: {question}'},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content

answer = generate(question, hits)
print(answer)
```

### 단계 4 — 최소 평가 세트

```python
eval_set = [
    {'q': 'Payment succeeded but no order — steps to check?', 'expected_chunk': 0},
    {'q': 'How long does a refund take?', 'expected_chunk': 2},
    {'q': 'What to verify when a coupon is not applied?', 'expected_chunk': 3},
]

recall_hits = sum(
    1 for case in eval_set
    if case['expected_chunk'] in [h['id'] for h in retrieve(case['q'], top_k=3)]
)
print(f'Recall@3 = {recall_hits}/{len(eval_set)}')
```

평가 세트가 열 개 정도만 있어도 청킹과 임베딩을 바꿨을 때 영향이 숫자로 보이기 시작합니다.

### 단계 5 — 하나의 실행 함수로 묶기

실무에서 RAG가 갑자기 추상적으로 느껴지는 순간은 각 단계가 따로는 이해되는데, 한 번에 묶으면 어디서 무엇을 출력해야 하는지 사라질 때입니다. 그래서 최소 실행 스크립트에도 **중간 상태를 남기는 `run_pipeline()`** 하나를 두는 편이 좋습니다.

```python
import json
import re

def mask_pii(text: str) -> str:
    text = re.sub(r'\b\d{6}-\d{7}\b', '[RRN]', text)
    text = re.sub(r'\b\d{2,3}-\d{3,4}-\d{4}\b', '[PHONE]', text)
    return text

def run_pipeline(question: str) -> dict:
    masked_question = mask_pii(question)
    hits = retrieve(masked_question, top_k=2)
    answer = generate(masked_question, hits)
    result = {
        'question': masked_question,
        'hit_ids': [h['id'] for h in hits],
        'hit_scores': [round(h['score'], 3) for h in hits],
        'answer': answer,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

run_pipeline('결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?')
```

**Expected output:**

```json
{
  "question": "결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?",
  "hit_ids": [0, 1],
  "hit_scores": [0.873, 0.522],
  "answer": "먼저 주문 동기화 지연 여부를 확인하고, 그다음 결제 성공과 주문 저장 실패가 분리된 상황인지 점검해야 합니다. [sources: 0,1]"
}
```

이 출력이 중요한 이유는 두 가지입니다. 첫째, 답변만이 아니라 **선택된 청크와 점수**가 같이 남습니다. 둘째, 나중에 사용자 피드백이 들어왔을 때 “검색이 틀렸는지, 생성이 틀렸는지”를 로그 한 줄로 다시 열어 볼 수 있습니다.

### 단계 6 — 문맥이 없을 때 실패를 확인하기

RAG 글에서 빠지기 쉬운 검증이 하나 있습니다. **답할 수 없는 질문**도 일부러 넣어 봐야 한다는 점입니다. 그래야 추측 금지 프롬프트가 실제로 작동하는지 확인할 수 있습니다.

```python
unknown_question = '우리 회사 포인트 만료 정책은 몇 개월인가요?'
unknown_result = run_pipeline(unknown_question)
print(unknown_result['answer'])
```

**Expected output:**

```text
I could not find a relevant policy [sources: 1,3]
```

이 검증을 생략하면, 검색은 빈약한데 답변은 그럴듯한 상태가 얼마든지 남습니다. 한국어 RAG에서 특히 위험한 패턴입니다.

---

## 어느 단계가 병목인지 빨리 가르는 방법

RAG를 디버깅할 때는 문제를 길게 설명하기보다, 먼저 아래 표처럼 **증상과 첫 점검 포인트를 대응**시키는 편이 훨씬 빠릅니다.

| 증상 | 흔한 원인 | 가장 먼저 볼 로그 |
| --- | --- | --- |
| 답변은 자연스러운데 사실이 틀림 | Retrieve 실패 또는 Generate 추측 | `hit_ids`, `hit_scores`, 인용 라인 |
| 검색 점수가 모두 비슷함 | 청크가 너무 짧거나 너무 일반적 | chunk 길이 분포, 상위 5개 점수 |
| top-1은 맞는데 답변이 엉뚱함 | context formatting 부족 | `Context:` 문자열 길이, system prompt |
| 특정 질문만 계속 실패 | 평가 세트 편향 또는 코퍼스 누락 | gold chunk 존재 여부, 질문 표현 |
| 긴 문서에서만 품질 저하 | chunk 경계가 의미 단위를 끊음 | 문단 기반 vs 고정 토큰 비교 결과 |

이 표를 팀 위키에 그대로 붙여 두면, 운영 중 “LLM이 이상하다”는 막연한 표현이 훨씬 빨리 구체화됩니다.

---

## 한국어 문맥을 LLM에 넘길 때의 포맷 규칙

생성 단계에서 흔한 실수는 검색된 청크를 그냥 이어 붙이는 것입니다. 한국어 문맥에서는 아래 세 가지를 같이 지키는 편이 안정적입니다.

1. **청크 ID를 앞에 붙입니다.** 인용과 디버깅이 쉬워집니다.
2. **문맥 사이에 빈 줄을 둡니다.** 청크 경계가 흐려지지 않습니다.
3. **질문보다 문맥을 먼저 읽게 합니다.** system 메시지에서 우선순위를 고정합니다.

```python
def build_context(hits: list[dict]) -> str:
    return '\n\n'.join(
        f"[chunk:{hit['id']}]\n{hit['text']}"
        for hit in hits
    )
```

아주 작은 함수처럼 보이지만, 이 포맷이 없으면 인용 라인도 쉽게 어긋나고, 같은 청크를 다시 찾기도 어려워집니다.

---

## 운영 전 점검용 미니 평가 루프

첫 버전이라도 질문 열 개 정도는 반드시 쌓아 두는 편이 좋습니다. 여기서 중요한 것은 화려한 평가 프레임워크보다 **회귀를 빨리 감지하는 작은 루프**입니다.

```python
def evaluate_retrieval(eval_set):
    failures = []
    hits = 0

    for case in eval_set:
        result = retrieve(case['q'], top_k=3)
        hit_ids = [item['id'] for item in result]
        ok = case['expected_chunk'] in hit_ids
        hits += int(ok)
        if not ok:
            failures.append({'question': case['q'], 'hit_ids': hit_ids})

    recall = hits / len(eval_set)
    return recall, failures

recall, failures = evaluate_retrieval(eval_set)
print('Recall@3 =', round(recall, 2))
print('Failures =', failures)
```

**Expected output:**

```text
Recall@3 = 1.0
Failures = []
```

실패 케이스가 생기면 그 질문을 그대로 다음 회귀 세트에 남겨 두세요. 좋은 RAG 팀은 평가 세트가 멋지기보다 **작아도 계속 누적**됩니다.

---

## 자주 하는 실수

![엔지니어가 헷갈리는 지점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-03-where-engineers-get-confused.ko.png)

*엔지니어가 헷갈리는 지점*

1. **더 강한 LLM이 RAG를 구해 준다고 믿는 것** — 검색이 틀린 청크를 가져오면 GPT-4o든 Claude Opus든 틀린 답을 냅니다. 먼저 Recall@k를 측정해야 합니다.
2. **검색 점수를 로깅하지 않는 것** — 답변만 보면 어느 단계가 깨졌는지 알 수 없습니다. 검색 결과, 점수, 선택된 청크 ID를 항상 함께 남겨야 합니다.
3. **top-k를 너무 크게 잡는 것** — k = 20은 노이즈만 늘리고 관련 청크를 묻어 버리기 쉽습니다. k = 3~5에서 시작하세요.
4. **출처를 생략하는 것** — 인용이 없으면 사용자도 운영자도 답을 검증할 수 없습니다. system 프롬프트에서 강제해야 합니다.
5. **청크가 너무 길거나 짧은 것** — 1000토큰을 넘기면 LLM이 무관한 부분에 끌리고, 50토큰보다 짧으면 맥락을 잃습니다. 200~500토큰이 실용적인 출발점입니다.
6. **민감 데이터를 마스킹하지 않고 보내는 것** — 주민등록번호, 카드번호, 계정 ID는 외부 LLM 호출 전에 가려야 합니다.
7. **평가 세트 없이 튜닝하는 것** — “느낌상 좋아졌다”는 회귀를 부릅니다. 열 개라도 적고 매번 측정해야 합니다.

---

## 실무에서는 이렇게 확장합니다

작은 예제가 실무로 넘어갈 때 가장 먼저 붙는 요소는 보통 세 가지입니다.

1. **입력 경로 분리** — HTML, PDF, OCR 결과가 같은 `chunks` 구조로 들어오게 맞춥니다.
2. **검색 후 재정렬** — top-20을 가져온 뒤 cross-encoder로 top-3을 다시 고릅니다.
3. **답변 감사 로그** — 질문, 청크 ID, 점수, 인용, 사용자 피드백을 한 줄 JSON으로 남깁니다.

예를 들면 아래 정도의 로그만 있어도 다음 개선 방향이 뚜렷해집니다.

```python
audit_log = {
    'question': question,
    'retrieved': hits,
    'answer': answer,
    'citations_present': '[sources:' in answer,
}
print(json.dumps(audit_log, ensure_ascii=False))
```

이 로그는 장애 대응에도 그대로 도움이 됩니다. “왜 틀렸지?”라는 질문에 답변만 보여 주는 팀보다, 검색 후보와 인용까지 함께 보여 주는 팀이 훨씬 빨리 원인을 좁힙니다.

---

## 실무 적용 — internal wiki RAG

실제 운영에서는 보통 다음 요소가 더 붙습니다.

- **메타데이터 필터** — `{'team': 'payments', 'updated_at': '2026-04-01'}` 같은 필드를 청크에 붙여 팀이나 날짜 범위로 검색을 좁힙니다. FAISS만으로는 부족하고, Qdrant, Weaviate, Milvus 같은 벡터 DB를 함께 쓰는 경우가 많습니다.
- **하이브리드 검색** — BM25(키워드)와 dense(임베딩) 점수를 Reciprocal Rank Fusion으로 합치면, 한국어 고유명사와 약어 검색이 크게 좋아집니다.
- **Reranking** — top-20을 먼저 뽑고 cross-encoder(예: `BAAI/bge-reranker-v2-m3`)로 다시 점수를 매긴 뒤 top-3만 LLM에 넘기면 정확도가 올라갑니다.
- **OCR 입력** — PDF나 이미지 문서는 4편의 CLOVA OCR을 거쳐 청킹 단계로 넣습니다.
- **모델 교체** — 외부 API 제약이 크면 5편의 Solar나 HyperCLOVA X로 생성 모델만 바꿀 수 있습니다. `retrieve`와 `generate` 인터페이스가 분리돼 있으면 교체 비용이 거의 없습니다.
- **로깅과 운영** — 질문, 검색된 청크 ID, 점수, 답변, 사용자 피드백을 요청당 한 줄 JSON으로 남기면 며칠치 데이터만으로도 다음 평가 세트가 만들어집니다.

---

## 체크리스트

- [ ] Ingest, Index, Retrieve, Generate를 별도 함수로 분리했습니다.
- [ ] 청크 경계를 먼저 정하고, 검색된 청크를 직접 읽어 봤습니다. (200~500토큰 권장)
- [ ] 검색 점수와 선택된 청크 ID를 답변과 함께 항상 로깅합니다.
- [ ] system 프롬프트에 추측 금지와 출처 인용 강제를 넣었습니다.
- [ ] 최소 열 개의 질문/정답 청크 평가 세트를 만들고 Recall@k를 측정했습니다.
- [ ] 민감 정보 마스킹을 `generate` 직전에 적용합니다.
- [ ] top-k는 3~5에서 시작하고 LLM context 예산에 맞춰 조정합니다.
- [ ] 답할 수 없는 질문 세 개 이상으로 anti-speculation 동작을 검증했습니다.

---

## 연습 문제

1. **청킹 전략 비교** — 같은 문서를 (a) 문단 분리와 (b) 300토큰 + 50토큰 overlap 청크로 각각 인덱싱해 보세요. 같은 다섯 개 질문에 대한 Recall@3를 비교해 보세요.
2. **추측 금지 규칙 검증** — 코퍼스에 없는 질문 세 개를 평가 세트에 추가한 뒤, 추측 금지 system 프롬프트가 있을 때와 없을 때 speculation 빈도를 비교해 보세요.
3. **하이브리드 검색** — `rank_bm25`로 BM25 점수를 추가하고, dense 점수와 RRF로 결합한 뒤 dense-only 대비 Recall@3가 얼마나 오르는지 측정해 보세요.
4. **출처 강제** — 답변에 `[sources: 0,1]` 라인이 없으면 한 번 더 호출하는 retry를 추가해 보세요.

---

## 정리

이 시리즈가 남기는 더 깊은 교훈은 특정 도구 선택보다 **한국어 문서 처리 단계를 분명히 분리하는 습관**입니다. 임베딩 비교(1편), 문장 유사도(2편), 다국어 검색(3편), OCR(4편), 생성 API(5편)를 차례로 쌓아 오면, 한국어 RAG 파이프라인도 훨씬 차분하게 설계할 수 있습니다.

마지막으로 남길 포인트는 세 가지입니다. 첫째, 검색과 생성을 같은 블랙박스로 두지 않는 것. 둘째, 검색 후보와 점수를 항상 남기는 것. 셋째, 답할 수 없는 질문으로도 파이프라인을 검증하는 것입니다. 이 세 가지만 지켜도 작은 한국어 RAG는 훨씬 빨리 운영 가능한 형태로 가까워집니다.

이 글로 시리즈를 마칩니다. 다음에 이어서 보면 좋은 시리즈는 두 가지입니다.

- **vector-search-101** — FAISS, Qdrant, Milvus를 더 깊게 다루며 메타데이터 필터, 하이브리드 검색, 인덱스 튜닝을 배웁니다.
- **ai-evaluation-101** — Recall@k, MRR, Faithfulness, RAGAS로 RAG 평가 체계를 만드는 시리즈입니다.

작은 평가 세트와 네 단계 파이프라인만 손에 익혀도 더 큰 RAG 시스템으로 훨씬 안정적으로 확장할 수 있습니다.

## 처음 질문으로 돌아가기

- **최소한의 한국어 RAG 파이프라인에서 빠질 수 없는 단계는 무엇일까요?**
  - Ingest, Index, Retrieve, Generate 네 단계는 최소 구성에서도 빠질 수 없습니다. 문서를 청크로 만들고, 임베딩과 인덱스를 준비하고, 상위 청크를 찾고, 그 청크만 근거로 답하게 해야 비로소 RAG라고 부를 수 있습니다. 이 글이 각 단계를 별도 함수로 나눈 이유도 어느 지점이 깨졌는지 바로 보기 위해서입니다.
- **품질 병목은 보통 청킹, 임베딩, 검색, 생성 중 어디에서 가장 자주 생길까요?**
  - 이 글의 관점에서는 청킹과 검색에서 먼저 병목이 드러나는 경우가 많습니다. 의미 경계를 잘못 자른 청크나 낮은 Recall의 검색 결과를 가져오면, 뒤의 LLM이 아무리 자연스럽게 말해도 답은 틀어집니다. 그래서 `hit_ids`, `hit_scores`, 답할 수 없는 질문 검증을 함께 남기도록 했습니다.
- **검색된 문맥은 LLM에 들어가기 전에 어떤 형태로 정리해야 할까요?**
  - 청크 ID를 붙인 문맥 블록으로 정리하고, 청크 사이를 빈 줄로 분리한 뒤, 출처 인용과 추측 금지 규칙을 함께 넘겨야 합니다. 이렇게 해야 답변 마지막의 `[sources: ...]`가 실제 검색 후보와 연결되고, 문맥에 없는 질문에는 모른다고 답하게 만들 수 있습니다. 즉 문맥 전달은 텍스트 복붙이 아니라 검증 가능한 근거 포맷 설계입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Korean AI Stack 101 (1/6): 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- [Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전](./03-bge-m3-multilingual.md)
- [Korean AI Stack 101 (4/6): CLOVA OCR API로 문서 텍스트 추출](./04-clova-ocr.md)
- [Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기](./05-hyperclova-solar-api.md)
- **Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [RAGAS — RAG evaluation framework](https://github.com/explodinggradients/ragas)
- [Reciprocal Rank Fusion paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/korean-ai-stack-101/ko/06-korean-rag-pipeline)

Tags: Korean NLP, LLM, Embeddings, OCR
