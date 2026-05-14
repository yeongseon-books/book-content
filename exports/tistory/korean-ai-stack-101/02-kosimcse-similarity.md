
# KoSimCSE로 문장 유사도 구현하기

처음 만드는 검색 루프는 눈으로 직접 따라갈 수 있을 만큼 작아야 합니다. 한국어 FAQ 검색에서는 정규화나 인덱스 선택을 한 번만 잘못해도, 뒤에 붙는 LLM 단계가 실제보다 똑똑해 보이는 착시가 금방 생깁니다.

이 글은 Korean AI Stack 101 시리즈의 2번째 글입니다. 여기서는 KoSimCSE로 최소한의 한국어 문장 유사도 검색 흐름을 만들고, 검색이 실제로 어떻게 작동하는지 드러냅니다.

## 이 글에서 다룰 문제

- KoSimCSE는 한국어 검색 작업에서 어디서 가장 먼저 효과를 냅니까?
- FAQ 질문만 먼저 인덱싱하는 방식이 왜 깔끔한 첫 버전일까요?
- 정규화된 임베딩이 `IndexFlatIP`와 왜 그렇게 잘 맞을까요?
- 유사도 점수가 높아도 왜 엉뚱한 결과가 나올 수 있을까요?

> 처음으로 쓸 만한 문장 유사도 시스템은 복잡한 오케스트레이션이 아니라, 깔끔한 임베딩과 투명한 인덱스에서 나옵니다.

> Korean AI Stack 101 (2/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/02-kosimcse-similarity)

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

## Before vs. After

**Before** — 사용자가 FAQ 페이지에서 “비밀번호를 잊어버렸어요”라고 검색하면, 키워드 매칭은 “비밀번호 재설정”이 아니라 “비밀번호 변경 정책”을 먼저 올릴 수 있습니다.

**After** — KoSimCSE 기반 검색을 붙이면 동작은 다음처럼 바뀝니다.

```python
query = '로그인 비밀번호를 다시 설정하고 싶어요.'  # "I want to reset my login password."
# top-1: '비밀번호나 패스워드를 재설정하고 싶어요.' (score 0.91)
# top-2: '결제는 됐는데 주문 내역이 보이지 않습니다.' (score 0.32)
```

핵심은 세 가지입니다. 첫째, “재설정”이라는 정확한 키워드가 없어도 매칭됩니다. 둘째, top-1과 top-2 사이에 큰 점수 간격이 생깁니다. 셋째, 사람이 직접 후보 의미를 읽어 보며 검색 품질을 판단할 수 있습니다.

## 핵심 흐름

![Core flow](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-01-core-flow.ko.png)

*Core flow*

## 왜 질문만 먼저 인덱싱할까

질문과 답변을 첫날부터 함께 임베딩하면 디버깅이 어려워집니다. 잘못된 매칭이 쿼리 때문인지, 답변 문장 길이 때문인지, 답변 표현이 의미를 흔든 것인지 구분하기 어려워집니다. 첫 버전은 질문만 인덱싱하고, 답변은 출력 단계에서 연결하는 편이 훨씬 투명합니다.

## 단계별 실습

### Step 1 — Prepare model and data

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

### Step 2 — Embed and index

```python
embeddings = model.encode(
    [item['question'] for item in FAQS],
    normalize_embeddings=True,
).astype('float32')

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
```

`normalize_embeddings=True`와 `IndexFlatIP`는 한 쌍입니다. 둘 중 하나라도 빠지면 점수 해석이 금방 흐려집니다.

### Step 3 — Search a query

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-01-minimal-runnable-example.ko.png)

*최소 실행 예제*

```python
query = '로그인 비밀번호를 다시 설정하고 싶어요.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

### Step 4 — Interpret the result

```python
for score, idx in zip(distances[0], indices[0]):
    print(f"{score:.3f}  {FAQS[idx]['question']}")
```

상위 1개만 보지 말고 2~3개를 함께 보세요. 점수 분포를 보면 결과를 얼마나 믿어도 되는지 바로 감이 옵니다.

### Step 5 — Measure Recall@k (optional)

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

## 정리

KoSimCSE 예제의 가치는 검색 루프를 끝까지 눈에 보이게 유지한다는 데 있습니다. 이 기준선이 있어야 나중에 다국어 임베딩이나 생성 단계를 올려도 무엇이 좋아졌는지 비교할 수 있습니다. 정규화, 인덱스 선택, top-k 출력이라는 세 가지 작은 습관만으로도 한국어 검색의 첫 버전은 꽤 단단해집니다.

다음 글에서는 3편 BGE-M3로 넘어갑니다. 한국어와 영어가 섞인 코퍼스에서 KoSimCSE보다 어디가 강한지, dense + sparse 멀티벡터 검색이 코드에서 무엇을 뜻하는지 살펴봅니다.

## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- **KoSimCSE로 문장 유사도 구현하기 (현재 글)**
- BGE-M3 다국어 임베딩 실전 (예정)
- CLOVA OCR API로 문서 텍스트 추출 (예정)
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

## 참고 자료

- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [SimCSE paper](https://arxiv.org/abs/2104.08821)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

Tags: Korean NLP, LLM, Embeddings, OCR

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
