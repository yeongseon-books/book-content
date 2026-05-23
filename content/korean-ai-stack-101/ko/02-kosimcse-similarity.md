---
title: "Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기"
series: korean-ai-stack-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- KoSimCSE
- FAISS
- SemanticSearch
- Embeddings
- Python
last_reviewed: '2026-05-12'
seo_description: 첫 문장 유사도 시스템은 복잡한 오케스트레이션보다 깔끔한 임베딩과 투명한 인덱스에서 출발합니다.
---

# Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기

처음 만드는 검색 루프는 눈으로 직접 따라갈 수 있을 만큼 작아야 합니다. 한국어 FAQ 검색에서는 정규화나 인덱스 선택을 한 번만 잘못해도, 뒤에 붙는 LLM 단계가 실제보다 똑똑해 보이는 착시가 금방 생깁니다.

이 글은 Korean AI Stack 101 시리즈의 2번째 글입니다. 여기서는 KoSimCSE로 최소한의 한국어 문장 유사도 검색 흐름을 만들고, 검색이 실제로 어떻게 작동하는지 드러냅니다.

![Korean AI Stack 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-01-core-flow.ko.png)
*Korean AI Stack 101 2장 흐름 개요*

## 먼저 던지는 질문

- KoSimCSE는 한국어 검색 작업에서 어디서 가장 먼저 효과를 냅니까?
- FAQ 질문만 먼저 인덱싱하는 방식이 왜 깔끔한 첫 버전일까요?
- 정규화된 임베딩이 `IndexFlatIP`와 왜 그렇게 잘 맞을까요?

## 왜 이 단계가 중요한가

이 글은 모델 비교에서 실제 한국어 검색 루프로 한 단계 들어갑니다. 범위는 일부러 좁혔습니다. FAQ 질문을 임베딩하고, FAISS에 넣고, 새 한국어 질의에 가장 가까운 질문을 찾는 일만 다룹니다.

문장 유사도 검색을 별도 단계로 다루는 이유는 분명합니다. 많은 한국어 RAG 시스템이 바로 이 지점에서 무너집니다. 임베딩 품질, 정규화, 인덱스 선택 중 하나라도 틀리면 LLM이 아무리 좋아도 잘못된 문서를 되살리지 못합니다. KoSimCSE처럼 검증된 모델로 가장 작은 검색 루프를 손에 익혀 두면, 이후 BGE-M3, 멀티벡터 검색, 하이브리드 검색으로 확장할 때도 비교 기준을 잃지 않습니다.

## 멘탈 모델

문장 유사도 검색은 네 단계로 분해됩니다.

```text
[corpus]                         [query]
   |                                |
   v                                v
[encode -> vector]            [encode -> vector]
   |                                |
   v                                v
[FAISS index] <----- search -----+
   |
   v
[top-k results]
```

가장 중요한 것은 두 가지입니다.

- **같은 모델로 인코딩하기**: 코퍼스와 쿼리는 같은 모델과 같은 정규화 방식을 공유해야 합니다. 모델을 섞으면 거리의 의미가 무너집니다.
- **거리 함수와 인덱스를 맞추기**: 정규화된 벡터 + `IndexFlatIP`(inner product)는 코사인 유사도와 수학적으로 같습니다. 정규화되지 않은 벡터에 내적을 쓰면 길이가 점수를 지배합니다.

추가로 두 가지를 더 기억하면 좋습니다.

- KoSimCSE는 contrastive learning으로 미세조정된 BERT 계열 인코더입니다. 짧은 한국어 문장에 강합니다.
- FAISS `IndexFlatIP`는 brute-force 인덱스입니다. 1만 개 정도까지는 충분히 빠르고, 그 이상이면 IVF나 HNSW로 넘어가면 됩니다.

> 멘탈 모델을 한 문장으로 줄이면 이렇습니다. 검색 품질은 “질문을 어떻게 벡터로 만들었는가”와 “그 벡터를 어떤 거리 규칙으로 비교하는가”의 합으로 결정됩니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| KoSimCSE | SimCSE contrastive learning 방식을 한국어 문장 임베딩에 적용한 모델 |
| `SentenceTransformer` | 임베딩 모델을 한 줄로 불러와 사용할 수 있는 라이브러리 |
| `normalize_embeddings=True` | L2 정규화. 벡터 길이를 1로 맞춰 코사인 유사도를 단순하게 만듦 |
| `IndexFlatIP` | FAISS의 내적 기반 brute-force 인덱스. 정규화된 벡터와 짝이 맞음 |
| `IndexFlatL2` | FAISS의 L2 거리 기반 brute-force 인덱스. 정규화되지 않은 벡터용 |
| top-k | 상위 k개 검색 결과. 디버깅에는 k=2~3이 적당 |
| Recall@k | 정답이 상위 k개 안에 들어오는 비율. 기본 검색 품질 지표 |

## 적용 전후 비교

**Before** — 사용자가 FAQ 페이지에서 “비밀번호를 잊어버렸어요”라고 검색하면, 키워드 매칭은 “비밀번호 재설정”이 아니라 “비밀번호 변경 정책”을 먼저 올릴 수 있습니다.

**After** — KoSimCSE 기반 검색을 붙이면 동작은 다음처럼 바뀝니다.

```python
query = '로그인 비밀번호를 다시 설정하고 싶어요.'  # "I want to reset my login password."
# top-1: '비밀번호나 패스워드를 재설정하고 싶어요.' (score 0.91)
# top-2: '결제는 됐는데 주문 내역이 보이지 않습니다.' (score 0.32)
```

여기서 먼저 볼 점은 세 가지입니다. 첫째, “재설정”이라는 정확한 키워드가 없어도 매칭됩니다. 둘째, 상위 결과와 그다음 결과 사이에 큰 점수 간격이 생깁니다. 셋째, 사람이 직접 후보 의미를 읽어 보며 검색 품질을 판단할 수 있습니다.

## 핵심 흐름

## 왜 질문만 먼저 인덱싱할까

질문과 답변을 첫날부터 함께 임베딩하면 디버깅이 어려워집니다. 잘못된 매칭이 쿼리 때문인지, 답변 문장 길이 때문인지, 답변 표현이 의미를 흔든 것인지 구분하기 어려워집니다. 첫 버전은 질문만 인덱싱하고, 답변은 출력 단계에서 연결하는 편이 훨씬 투명합니다.

## 단계별 실습

### 단계 1 — 모델과 데이터 준비

```python
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BM-K/KoSimCSE-roberta-multitask'
FAQS = [
    {'category': 'account', 'question': '비밀번호나 패스워드를 재설정하고 싶어요.'},
    {'category': 'billing', 'question': '결제는 됐는데 주문 내역이 보이지 않습니다.'},
    {'category': 'shipping', 'question': '배송 상태는 어디에서 확인하나요?'},
]

model = SentenceTransformer(MODEL_NAME)
```

### 단계 2 — 임베딩과 인덱싱

```python
embeddings = model.encode(
    [item['question'] for item in FAQS],
    normalize_embeddings=True,
).astype('float32')

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
```

`normalize_embeddings=True`와 `IndexFlatIP`는 한 쌍입니다. 둘 중 하나라도 빠지면 점수 해석이 금방 흐려집니다.

### 단계 3 — 쿼리 검색

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-01-minimal-runnable-example.ko.png)

*최소 실행 예제*

```python
query = '로그인 비밀번호를 다시 설정하고 싶어요.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

### 단계 4 — 결과 해석

```python
for score, idx in zip(distances[0], indices[0]):
    print(f"{score:.3f}  {FAQS[idx]['question']}")
```

상위 1개만 보지 말고 2~3개를 함께 보세요. 점수 분포를 보면 결과를 얼마나 믿어도 되는지 바로 감이 옵니다.

### 단계 5 — Recall@k 측정 (선택)
```python
test_cases = [
    ('비밀번호 변경 어떻게 해요?', 0),  # gold: FAQ #0
    ('주문이 안 보여요', 1),
    ('택배 어디까지 왔나요?', 2),
]

hits = 0
for query, gold_idx in test_cases:
    vec = model.encode([query], normalize_embeddings=True).astype('float32')
    _, idx = index.search(vec, 1)
    if idx[0][0] == gold_idx:
        hits += 1
print(f"Recall@1 = {hits / len(test_cases):.2f}")
```

## 이 코드에서 먼저 봐야 할 점

![이 코드에서 주목할 점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-02-what-to-notice-in-this-code.ko.png)

*이 코드에서 주목할 점*

- 인덱스는 전체 답변이 아니라 **질문 문자열**을 저장합니다.
- `normalize_embeddings=True`는 inner product를 코사인 유사도와 같게 만들어 줍니다.
- 테스트 질의는 인덱싱된 질문을 그대로 반복하지 않고, 서로 다른 표현으로 바꿉니다.
- 전체 스크립트가 상위 두 개 결과를 출력하는 이유는, 근접 오답을 눈으로 볼 수 있어야 랭킹 오류를 진단하기 쉽기 때문입니다.

## 자주 하는 실수

![엔지니어가 헷갈리는 지점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-03-where-engineers-get-confused.ko.png)

*엔지니어가 헷갈리는 지점*

- **정규화를 빼먹는 것** — `normalize_embeddings=True` 없이 `IndexFlatIP`를 쓰면 긴 문장이 부당하게 높은 점수를 받습니다.
- **다른 모델로 인코딩하는 것** — 코퍼스는 KoSimCSE, 쿼리는 BGE-M3로 만들면 거리가 무의미해집니다. 항상 같은 모델을 쓰세요.
- **top-1만 믿는 것** — 0.92도 오답일 수 있습니다. 0.92 vs 0.91 vs 0.45 같은 후보 간 간격이 신뢰도를 보여 줍니다.
- **FAQ 설정을 긴 문서에 재사용하는 것** — 긴 문서는 청킹과 다른 거리 전략이 필요합니다. KoSimCSE는 짧은 문장에 최적화되어 있습니다.
- **테스트 데이터를 인덱스에 넣는 것** — Recall이 비현실적으로 높아집니다. 항상 분리해야 합니다.
- **모델이 바뀌어도 점수 임계값을 그대로 쓰는 것** — 모델이 바뀌면 점수 분포도 바뀝니다. 임계값도 다시 맞춰야 합니다.

## 실무 적용

- **두 단계 검색**: KoSimCSE로 100개 후보를 가져오고, 그다음 cross-encoder(`bongsoo/kpf-cross-encoder` 등)로 재정렬하면 정확도가 크게 올라갑니다.
- **카테고리 필터**: 검색 전에 카테고리로 후보군을 줄이면 정확도와 속도가 모두 좋아집니다.
- **임베딩 캐시**: FAQ 코퍼스는 자주 변하지 않습니다. 임베딩을 디스크에 저장해 앱 시작 시 불러오면 cold start를 줄일 수 있습니다.
- **인덱스 선택**: 1만 개 이하 → `IndexFlatIP`, 10만 개 이상 → `IndexIVFFlat`, 100만 개 이상 → `IndexHNSWFlat`이 일반적인 출발점입니다.
- **하이브리드 검색**: BM25(키워드)와 KoSimCSE(의미) 점수를 가중 결합하면 도메인 용어와 일반적인 의역을 함께 잡을 수 있습니다.
- **Recall 모니터링**: 매주 새 사용자 질의 50개 정도를 뽑아 정답을 붙이고 Recall@5를 측정하면, 검색 품질 하락을 빨리 발견할 수 있습니다.

## 체크리스트

- [ ] 인덱스에 질문만 저장할지, 답변도 저장할지, 둘 다 넣을지 결정했습니다.
- [ ] 같은 의도를 여러 표현으로 바꾼 질의를 시험했습니다.
- [ ] 튜닝 중에는 적어도 상위 두세 개 결과를 출력합니다.
- [ ] LLM을 붙이기 전에 검색 단계만 따로 검증했습니다.
- [ ] Recall@k를 최소 한 번은 측정했습니다.

## 연습 문제

1. FAQ 코퍼스를 10개로 늘리고, 비슷한 의미의 항목 두 개를 일부러 추가해 보세요. 두 항목 사이에서 top-1 점수 간격이 어떻게 달라지는지 확인해 보세요.
2. `normalize_embeddings=False`로 바꾸고 같은 질의를 검색해 보세요. 랭킹이 어떻게 달라지는지 비교해 보세요.
3. KoSimCSE 대신 `jhgan/ko-sroberta-multitask`를 써서 같은 질의의 점수 분포를 비교해 보세요. 어느 모델이 더 선명한 간격을 보여 주나요?

## 토크나이저 특성이 검색 점수에 미치는 영향

KoSimCSE를 실무에서 쓸 때 놓치기 쉬운 포인트가 토크나이저입니다. 같은 의미의 문장이어도 공백, 조사, 외래어 표기 차이에 따라 토큰 조각이 달라지고, 이 차이가 임베딩 분포로 이어집니다. 운영에서는 모델 이름만 고정하지 말고 토크나이저 특성도 함께 기록해 두는 편이 좋습니다.

| 항목 | KoSimCSE (RoBERTa 계열) | BGE-M3 (XLM-R 계열) | 운영 시사점 |
| --- | --- | --- | --- |
| 기본 토크나이저 | SentencePiece/BPE 기반 | SentencePiece 기반 다국어 | 한국어+영어 혼합 비율이 높으면 BGE-M3 기준선도 함께 유지 |
| 한국어 조사 처리 | 조사 경계에서 토큰 분할이 잦음 | 비교적 완만하게 분해 | 짧은 질의에서는 KoSimCSE 강점이 두드러질 수 있음 |
| 영문 약어 처리 | 약어/버전 문자열에서 분산이 큼 | 약어를 더 안정적으로 유지 | `API v2`, `SLA`, `OCR`가 많으면 다국어 모델 검증 필요 |
| 띄어쓰기 오탈자 내성 | 중간 | 중간 이상 | 입력 정규화 파이프라인이 필수 |

```python
from transformers import AutoTokenizer

samples = [
    '결제는 됐는데 주문 내역이 보이지 않습니다.',
    '결제는됬는데 주문내역이 안보여요',
    'Payment succeeded but order history is missing',
]

tok_kosimcse = AutoTokenizer.from_pretrained('BM-K/KoSimCSE-roberta-multitask')
tok_bgem3 = AutoTokenizer.from_pretrained('BAAI/bge-m3')

for text in samples:
    print('\n[TEXT]', text)
    print('KoSimCSE:', tok_kosimcse.tokenize(text)[:18])
    print('BGE-M3  :', tok_bgem3.tokenize(text)[:18])
```

토큰 비교의 목적은 모델 내부를 해부하는 데 있지 않습니다. 점수가 흔들린 날에 “질의가 어떤 방식으로 분해됐는지”를 빠르게 확인하는 진단 도구로 쓰는 데 있습니다.

## 작은 벤치마크 세트로 Recall과 MRR 함께 보기

실무에서는 Recall@k 하나만으로 랭킹 품질을 다 설명하기 어렵습니다. 정답이 top-3 안에 들어와도 늘 3등이면 사용자 체감은 낮습니다. 그래서 KoSimCSE 기준선에서는 Recall@k와 MRR(Mean Reciprocal Rank)을 함께 측정하는 편이 좋습니다.

```python
def evaluate_retrieval_metrics(index, model, cases, top_k=3):
    recall_hits = 0
    reciprocal_ranks = []

    for query, gold_idx in cases:
        vec = model.encode([query], normalize_embeddings=True).astype('float32')
        _, idx = index.search(vec, top_k)
        ranked = idx[0].tolist()

        if gold_idx in ranked:
            recall_hits += 1
            rank = ranked.index(gold_idx) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    recall = recall_hits / len(cases)
    mrr = sum(reciprocal_ranks) / len(cases)
    return {'recall_at_k': round(recall, 3), 'mrr_at_k': round(mrr, 3)}

benchmark_cases = [
    ('패스워드 초기화 방법 알려 주세요', 0),
    ('결제 후 주문 목록이 비어 있어요', 1),
    ('배송 조회는 어디에서 하나요', 2),
    ('송장 번호 확인하는 방법', 2),
    ('주문이 사라졌어요', 1),
]

print(evaluate_retrieval_metrics(index, model, benchmark_cases, top_k=3))
```

**Expected output:**

```text
{'recall_at_k': 1.0, 'mrr_at_k': 0.9}
```

이 숫자는 “정답을 찾는가”와 “정답을 위로 끌어올리는가”를 동시에 보여 줍니다. 한국어 FAQ에서는 두 지표가 함께 올라갈 때 상담 전환율 개선이 안정적으로 나타나는 경우가 많습니다.

## production 설정 예시: KoSimCSE 검색 서비스

실무 서비스로 옮길 때는 코드보다 설정이 먼저 흔들립니다. 모델 버전, 인덱스 파일 경로, 재빌드 주기, timeout이 환경마다 다르면 같은 질의가 다르게 동작할 수 있습니다.

```yaml
service:
  name: korean-faq-retriever
  env: prod
  host: 0.0.0.0
  port: 8080

embedding:
  model_id: BM-K/KoSimCSE-roberta-multitask
  normalize: true
  batch_size: 128
  cache_dir: /var/lib/app/embeddings

index:
  type: faiss-flat-ip
  path: /var/lib/app/index/faqs.index
  metadata_path: /var/lib/app/index/faqs.meta.json
  rebuild_cron: '0 3 * * *'

retrieval:
  top_k: 3
  min_score: 0.42
  timeout_ms: 120

observability:
  log_level: INFO
  metrics_enabled: true
  trace_sample_ratio: 0.05
```

설정 파일은 단순해 보이지만 운영 사고를 크게 줄여 줍니다. 모델 교체, 임계값 조정, 인덱스 재생성 스케줄 변경이 코드 수정 없이 기록 가능한 변경으로 남기 때문입니다.

## 장애 대응 관점의 운영 로그 예시

검색 장애는 "틀린 답변"으로 보이지만 실제 원인은 검색 후보 미스인 경우가 많습니다. 따라서 요청마다 아래 항목은 남겨 두는 편이 좋습니다.

```python
import json
from datetime import datetime, timezone

def log_retrieval_event(query, hits, model_name):
    event = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'model': model_name,
        'query': query,
        'top_hits': [
            {
                'idx': int(hit['idx']),
                'score': round(float(hit['score']), 4),
                'category': hit['category'],
            }
            for hit in hits
        ],
    }
    print(json.dumps(event, ensure_ascii=False))
```

이 로그가 있으면 "모델이 나빠졌다"는 막연한 주장 대신 "배송 카테고리 질의에서 score tail이 내려갔다"처럼 수정 가능한 문제로 바뀝니다.

## 한국어 검색 품질을 올리는 데이터 정리 팁

모델 선택만큼 중요한 것이 코퍼스 정리입니다. 한국어 FAQ는 띄어쓰기 변형, 존댓말/반말, 약어 표기가 다양해서 같은 의미가 다른 표면형으로 자주 등장합니다.

- 질문 문장을 수집할 때는 실제 사용자 표현을 그대로 남기고, 별도 필드에 정규화 문장을 추가합니다.
- 고유명사와 도메인 용어는 사전으로 관리해 표기 변형을 통일합니다.
- 지나치게 긴 질문은 핵심 의도를 보존한 요약 버전을 함께 저장해 검색 안정성을 높입니다.

이런 정리는 모델 교체와 무관하게 지속적으로 가치가 쌓입니다. 즉, KoSimCSE를 쓰든 다른 임베딩을 쓰든 검색 기반 품질의 바닥선을 데이터 설계로 끌어올릴 수 있습니다.

## 한국어 FAQ 검색용 오프라인 회귀 테스트 예시

검색 품질은 배포 전 오프라인 회귀 테스트에서 많이 걸러낼 수 있습니다. 아래 예시는 질문 표현 변형을 포함한 테스트셋을 고정해 두고, 기준선보다 성능이 떨어지면 배포를 막는 단순한 패턴입니다.

```python
BASELINE = {
    'recall_at_3': 0.94,
    'mrr_at_3': 0.82,
}

def assert_regression_guard(metrics):
    if metrics['recall_at_k'] < BASELINE['recall_at_3']:
        raise AssertionError(
            f"Recall regression: {metrics['recall_at_k']} < {BASELINE['recall_at_3']}"
        )
    if metrics['mrr_at_k'] < BASELINE['mrr_at_3']:
        raise AssertionError(
            f"MRR regression: {metrics['mrr_at_k']} < {BASELINE['mrr_at_3']}"
        )

metrics = evaluate_retrieval_metrics(index, model, benchmark_cases, top_k=3)
assert_regression_guard(metrics)
print('Pass regression guard:', metrics)
```

이런 회귀 가드는 완벽한 품질 보증이 아니지만, 모델 변경이나 전처리 수정 후 생기는 명백한 하락을 빠르게 차단해 줍니다.

## 한국어 질의 정규화 파이프라인 예시

KoSimCSE는 짧은 문장에 강하지만, 입력이 지나치게 흔들리면 점수 분포가 금방 평평해집니다. 따라서 질의 정규화는 과도하게 똑똑할 필요 없이 일관성만 확보해도 큰 효과가 있습니다.

```python
import re

SPACE_RE = re.compile(r'\s+')

REPLACE_RULES = {
    '패스워드': '비밀번호',
    '로그인 불가': '로그인 안 됨',
    '주문내역': '주문 내역',
    '환불요청': '환불 요청',
}

def normalize_query(text: str) -> str:
    t = text.strip()
    for src, dst in REPLACE_RULES.items():
        t = t.replace(src, dst)
    t = SPACE_RE.sub(' ', t)
    return t
```

정규화는 모델을 속이기 위한 트릭이 아니라, 같은 의도 문장을 같은 형태로 들어오게 만들어 인덱스 탐색을 더 안정적으로 만드는 작업입니다.

## 코사인 점수 임계값을 주기적으로 갱신하는 기준

고정 임계값은 시간이 지나면 쉽게 낡습니다. FAQ가 늘고 문장 길이가 변하면 점수 분포가 이동하기 때문입니다. 월 단위로 아래 통계를 다시 계산해 기준을 갱신하는 편이 안전합니다.

| 구간 | 권장 계산 방식 | 운영 활용 |
| --- | --- | --- |
| Similar 분포 하한 | 유사 쌍 점수 p10 | 이 값 아래면 재학습/정규화 점검 |
| Unrelated 분포 상한 | 무관 쌍 점수 p90 | 이 값 위면 오탐 위험 알람 |
| 안전 임계값 | `(similar_p10 + unrelated_p90) / 2` | low-confidence 검색 결과 분기 |

이 방식은 절대 정답은 아니지만, 운영 데이터가 바뀔 때 임계값도 함께 움직여야 한다는 원칙을 팀에 정착시키는 데 도움이 됩니다.

마지막으로, 임계값은 문서에 숫자만 남기지 말고 계산에 사용한 샘플 수와 날짜를 함께 기록해 두세요. 그래야 다음 분기에 값이 달라졌을 때 품질 변화인지 데이터 구성 변화인지 빠르게 구분할 수 있습니다.

## 정리

KoSimCSE 예제의 가치는 검색 루프를 끝까지 눈에 보이게 유지한다는 데 있습니다. 이 기준선이 있어야 나중에 다국어 임베딩이나 생성 단계를 올려도 무엇이 좋아졌는지 비교할 수 있습니다. 정규화, 인덱스 선택, top-k 출력이라는 세 가지 작은 습관만으로도 한국어 검색의 첫 버전은 꽤 단단해집니다.

다음 글에서는 3편 BGE-M3로 넘어갑니다. 한국어와 영어가 섞인 코퍼스에서 KoSimCSE보다 어디가 강한지, dense + sparse 멀티벡터 검색이 코드에서 무엇을 뜻하는지 살펴봅니다.

## 처음 질문으로 돌아가기

- **KoSimCSE는 한국어 검색 작업에서 어디서 가장 먼저 효과를 냅니까?**
  - 비밀번호 재설정, 주문 내역 누락처럼 짧은 한국어 FAQ 질문을 다른 표현으로 다시 물었을 때 가장 먼저 효과가 드러납니다. 이 글의 예제처럼 같은 의도 문장이 top-1로 붙고 2위 후보와 점수 간격이 벌어지면, 검색 기준선으로 쓰기 좋은 상태입니다. 즉 첫 효과는 화려한 다국어 검색보다 한국어 문장 유사도 정렬에서 먼저 보입니다.
- **FAQ 질문만 먼저 인덱싱하는 방식이 왜 깔끔한 첫 버전일까요?**
  - 질문만 인덱싱하면 검색이 틀렸을 때 원인을 질문 의미 매칭 문제로 바로 좁힐 수 있습니다. 답변까지 같이 넣으면 긴 문장 길이, 설명 방식, 부가 문맥이 점수에 섞여 디버깅이 어려워집니다. 첫 버전에서 질문과 답변의 역할을 분리해 둔 이유가 여기에 있습니다.
- **정규화된 임베딩이 `IndexFlatIP`와 왜 그렇게 잘 맞을까요?**
  - 정규화된 벡터에 내적을 쓰면 코사인 유사도와 같은 의미가 되어 점수 해석이 단순해집니다. 반대로 정규화를 빼면 긴 문장이나 특정 길이 편향이 점수를 지배해 FAQ 랭킹이 쉽게 흐려집니다. 그래서 이 글에서는 `normalize_embeddings=True`와 `IndexFlatIP`를 항상 한 쌍으로 다뤘습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Korean AI Stack 101 (1/6): 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- **Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기 (현재 글)**
- Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전 (예정)
- Korean AI Stack 101 (4/6): CLOVA OCR API로 문서 텍스트 추출 (예정)
- Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기 (예정)
- Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

## 참고 자료

- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [SimCSE paper](https://arxiv.org/abs/2104.08821)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/korean-ai-stack-101/ko/02-kosimcse-similarity)

Tags: Korean NLP, LLM, Embeddings, OCR
