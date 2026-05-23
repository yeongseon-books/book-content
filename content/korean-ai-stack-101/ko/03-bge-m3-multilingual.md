---
title: "Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전"
series: korean-ai-stack-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- BGE-M3
- Multilingual
- FAISS
- Embeddings
- Python
last_reviewed: '2026-05-12'
seo_description: 다국어 dense 검색은 화려한 신호 결합보다 먼저, 기준선이 되는 dense 검색을 깨끗하게 측정해야 합니다.
---

# Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전

한국 팀이 다루는 검색 코퍼스는 질의는 한국어인데 문서 절반이 영어인 경우가 많습니다. 바로 이 지점에서 한국어 전용 검색 기준선은 테스트에서는 깔끔해 보여도 운영에서는 금방 부서지기 시작합니다.

이 글은 Korean AI Stack 101 시리즈의 3번째 글입니다. 여기서는 BGE-M3로 한국어·영어 혼합 코퍼스에서 dense 다국어 기준선을 측정한 뒤, 더 복잡한 검색 신호를 올리기 전에 무엇을 확인해야 하는지 살펴봅니다.

![Korean AI Stack 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-01-core-flow.ko.png)
*Korean AI Stack 101 3장 흐름 개요*

## 먼저 던지는 질문

- BGE-M3는 한국어와 영어가 섞인 코퍼스에서 KoSimCSE보다 어디서 강합니까?
- 하나의 모델이 dense, sparse, multi-vector 표현을 동시에 낸다는 말은 무엇을 뜻합니까?
- 다국어 검색 첫 버전에서는 dense만으로도 왜 충분한 경우가 많습니까?

## 왜 이 단계가 중요한가

이 글은 한국 회사에서 매일 마주치는 검색 상황으로 들어갑니다. 질의는 한국어인데, 문서 코퍼스 상당수가 영어로 쓰여 있는 경우입니다. 앞 글은 KoSimCSE로 한국어 짧은 문장을 다뤘습니다. 이번에는 한국어·영어 혼합 코퍼스에 BGE-M3를 적용합니다.

BGE-M3를 별도 단계로 다룰 이유는 두 가지입니다. 첫째, 다국어 인코더 없이는 한국 회사의 내부 문서 검색이 거의 성립하지 않습니다. 매뉴얼과 인시던트 회고는 영어로 쓰여 있고, 사용자는 한국어로 묻습니다. 둘째, BGE-M3는 dense, sparse, multi-vector 표현을 동시에 낼 수 있는 널리 쓰이는 공개 모델입니다. 그래서 이후 하이브리드 검색에서 같은 백본 위에서 점수를 합칠 수 있습니다. 다만 이 글은 dense 기준선에 집중합니다. sparse와 multi-vector는 다음 단계에서 다룹니다.

## 멘탈 모델

다국어 dense 검색은 네 단계로 분해됩니다.

```text
[multilingual corpus (ko+en)]      [Korean query]
        |                                |
        v                                v
[BGE-M3 encode -> 1024d]      [BGE-M3 encode -> 1024d]
        |                                |
        v                                v
[FAISS IndexFlatIP] <-------- search ----+
        |
        v
[top-k (language-agnostic)]
```

가장 중요한 것은 세 가지입니다.

- **언어 비대칭을 모델이 흡수합니다**: 코퍼스는 영어, 질의는 한국어여도 둘 다 같은 벡터 공간에 놓입니다. KoSimCSE는 언어 정렬이 강하지 않습니다.
- **정규화는 여전히 필요합니다**: BGE-M3 dense 출력은 기본적으로 단위 길이가 아닙니다. `normalize_embeddings=True`를 항상 켜야 합니다.
- **dense만으로도 의미가 있습니다**: 다국어 인코더는 이미 일부 키워드 신호를 dense 벡터에 녹여 두었기 때문에, dense 기준선만으로도 KoSimCSE보다 뚜렷한 개선이 보이는 경우가 많습니다.

추가로 두 가지를 더 기억하면 좋습니다.

- BGE-M3 dense 벡터는 1024차원입니다. KoSimCSE는 768차원이므로 FAISS 메모리가 대략 1.3배 늘어납니다.
- 모델 로드 시간도 더 깁니다. cold start에 5~10초가 추가될 수 있으므로 캐싱의 가치가 커집니다.

> 멘탈 모델을 짧게 요약하면 이렇습니다. BGE-M3의 첫 가치는 “한국어 질의와 영어 문서를 한 인덱스 안에서 같은 의미 축으로 비교하게 만든다”는 데 있습니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| BGE-M3 | BAAI가 공개한 다국어 임베딩 모델. 약 100개 언어 지원 |
| `BAAI/bge-m3` | `SentenceTransformer`로 바로 불러올 수 있는 Hugging Face 모델 ID |
| Dense vector | 기본 1024차원 임베딩. 의미 검색의 기본 축 |
| Sparse vector | 토큰 가중치 기반 표현. BM25와 닮았지만 가중치는 학습됨 |
| Multi-vector (ColBERT-style) | 토큰마다 작은 벡터를 두는 late interaction 방식 |
| `normalize_embeddings=True` | L2 정규화. inner product를 코사인 유사도와 같게 만듦 |
| `IndexFlatIP` | FAISS 내적 인덱스. 정규화된 dense 벡터와 자연스럽게 짝이 맞음 |

## 적용 전후 비교

**Before** — KoSimCSE만 쓰는 검색에서는 한국어 질의 “쿠버네티스 롤백 절차”가 한국어 문서만 끌어오고, 영어 runbook은 사실상 보이지 않습니다.

**After** — BGE-M3 dense 검색을 적용하면 동작은 다음처럼 바뀝니다.

```python
query = '배포 실패 시 쿠버네티스 롤백 절차를 찾고 싶습니다.'
# top-1: '실패한 배포에 대한 Kubernetes 롤백 플레이북'(점수 0.78, en)
# top-2 : '배포 실패 시 인증백 체크리스트' (점수 0.74, ko)
# top-3: 'CI 파이프라인 실패 알림' (점수 0.41, ko)
```

중요한 점은 세 가지입니다. 첫째, 한국어 질의가 영어 runbook을 top-1로 끌어올립니다. 둘째, 같은 의미의 한국어 문서도 top-2에서 가깝게 따라옵니다. 셋째, top-3과의 점수 간격이 커서 cut-off 임계값을 실제로 적용할 수 있습니다.

## 핵심 흐름

## 왜 dense 기준선부터 시작할까

![최소 실행 예제](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-01-minimal-runnable-example.ko.png)

*최소 실행 예제*

BGE-M3가 dense, sparse, multi-vector 신호를 한꺼번에 낸다고 해서 첫날부터 셋을 모두 합칠 필요는 없습니다. dense 기준선만 놓고 KoSimCSE와 비교하지 않으면, 나중에 개선이 sparse에서 왔는지 dense에서 왔는지, 아니면 가중치 조합 덕분인지 알 수 없습니다. 가장 단순한 dense + `IndexFlatIP` 조합에 Recall@5를 한 번 찍어 두는 일 자체가 이후 모든 실험의 기준점이 됩니다.

## 단계별 실습

### 단계 1 — 모델과 다국어 코퍼스 준비

```python
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BAAI/bge-m3'
DOCS = [
    {'lang': 'en', 'text': 'Kubernetes rollback playbook for failed deploys: kubectl rollout undo'},
    {'lang': 'en', 'text': 'Customer support label taxonomy for refund and cancellation tickets'},
    {'lang': 'ko', 'text': '배포 실패 시 롤백 체크리스트: 헬스체크, 트래픽 회수, 알림 순서'},
    {'lang': 'ko', 'text': 'CI 파이프라인 실패 시 슬랙 알림 정책과 담당자 매트릭스'},
    {'lang': 'ko', 'text': '환불 요청 처리 SLA와 cancellation 사유 코드 관리'},
]

model = SentenceTransformer(MODEL_NAME)
```

### 단계 2 — 임베딩과 인덱싱

```python
embeddings = model.encode(
    [doc['text'] for doc in DOCS],
    normalize_embeddings=True,
).astype('float32')

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
print('dim =', embeddings.shape[1])  # 1024
```

차원을 한 번은 직접 확인해 두세요. 나중에 IVF 학습 데이터를 얼마나 모아야 할지 감을 잡는 데 도움이 됩니다.

### 단계 3 — 한국어 쿼리로 영한 문서 검색

![이 코드에서 주목할 점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-02-what-to-notice-in-this-code.ko.png)

*이 코드에서 주목할 점*

```python
query = '배포 실패 시 쿠버네티스 롤백 절차를 찾고 싶습니다.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 3)

for score, idx in zip(distances[0], indices[0]):
    print(f"{score:.3f}  [{DOCS[idx]['lang']}]  {DOCS[idx]['text']}")
```

언어 코드를 함께 출력하면 교차 언어 매핑이 실제로 일어나는지 한눈에 보입니다.

### 단계 4 — 언어별 Recall
```python
test_cases = [
    ('배포 실패 시 쿠버네티스 롤백 절차', 0),     # gold: English runbook
    ('환불 요청 SLA 알려 주세요', 4),              # gold: Korean refund policy
    ('CI 실패 알림은 누구에게 가나요', 3),         # gold: Korean CI policy
]

hits = 0
for query, gold_idx in test_cases:
    vec = model.encode([query], normalize_embeddings=True).astype('float32')
    _, idx = index.search(vec, 1)
    if idx[0][0] == gold_idx:
        hits += 1
print(f"Recall@1 (ko query) = {hits / len(test_cases):.2f}")
```

질의 언어를 한국어로 고정하고 정답 문서 언어만 바꾸는 것이 핵심입니다. 영어 정답 케이스에서 Recall이 0.6 아래로 떨어진다면 dense만으로는 부족하다는 신호입니다.

### 단계 5 — 동일 쿼리를 영어로 비교 (선택)

```python
en_query = 'kubernetes rollback procedure for failed deployment'
en_vec = model.encode([en_query], normalize_embeddings=True).astype('float32')
en_dist, en_idx = index.search(en_vec, 3)

for score, idx in zip(en_dist[0], en_idx[0]):
    print(f"{score:.3f}  [{DOCS[idx]['lang']}]  {DOCS[idx]['text']}")
```

같은 의미의 한국어 질의와 영어 질의에서 top-1이 유지된다면, 적어도 정성적으로는 모델이 언어 비대칭을 잘 흡수하고 있다고 볼 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 한국어 문서와 영어 문서는 **하나의 모델**로 인코딩해 하나의 인덱스에 넣습니다. BGE-M3에서는 언어별 인덱스를 따로 둘 필요가 거의 없습니다.
- 테스트 케이스에 정답 문서 언어를 섞어 넣어야 진짜 다국어 성능이 드러납니다.
- 1024차원은 KoSimCSE보다 메모리와 시간이 더 듭니다. 캐싱과 배치 인코딩의 중요성이 커집니다.
- dense Recall이 충분하다면 sparse나 multi-vector를 아직 추가하지 마세요.

## 자주 하는 실수

![엔지니어가 헷갈리는 지점](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-03-where-engineers-get-confused.ko.png)

*엔지니어가 헷갈리는 지점*

- **정규화를 빼먹는 것** — `normalize_embeddings=True` 없이 `IndexFlatIP`를 쓰면 dense 벡터 길이가 점수를 지배합니다.
- **언어별 인덱스를 따로 두는 것** — 그렇게 하면 BGE-M3의 교차 언어 정렬 효과를 스스로 깨뜨리게 됩니다. 같은 인덱스에 넣어야 합니다.
- **모델 간 절대 점수를 비교하는 것** — KoSimCSE의 0.91과 BGE-M3의 0.78은 같은 척도가 아닙니다. 모델이 다르면 분포도 다릅니다.
- **dense, sparse, multi-vector를 한 번에 켜는 것** — 개선 원인을 추적할 수 없게 됩니다. dense → sparse → multi-vector 순으로 하나씩 올리세요.
- **질의 길이를 무시하는 것** — BGE-M3는 8K 토큰까지 지원하지만, 너무 긴 질의는 의미를 묽게 만들고 점수를 평평하게 만듭니다. 200토큰 안팎이 실용적입니다.
- **GPU에서 fp32 그대로 쓰는 것** — BGE-M3는 fp16에서도 안전하고 빠릅니다. `model.half()` 한 줄로 메모리를 절반 가까이 줄일 수 있습니다.

## 실무 적용

- **다국어 내부 검색**: 영어 매뉴얼과 한국어 운영 가이드를 한 인덱스에 넣고 한국어 질의를 받는 것만으로도 쓸 만한 내부 검색 첫 버전이 빠르게 나옵니다.
- **하이브리드 검색의 dense 축**: BM25와 BGE-M3 dense를 가중 합치면 약어와 일반 의역을 함께 잡을 수 있습니다. 가중치는 0.3~0.7 범위에서 시작하면 됩니다.
- **Cross-encoder 재정렬**: BGE-M3로 top-50을 가져오고 `bge-reranker-large`로 재정렬하면 다국어 질의 정확도가 눈에 띄게 올라갑니다.
- **임베딩 캐시**: 1024차원 × 수만 문서는 메모리 부담이 큽니다. 디스크 캐싱과 mmap이 실무에서 중요해집니다.
- **인덱스 선택**: 1만 개 이하 → `IndexFlatIP`, 10만 개 이상 → `IndexIVFFlat`(nlist≈√N), 100만 개 이상 → `IndexHNSWFlat`이 일반적입니다.
- **언어별 모니터링**: 매주 Recall@5를 한국어 질의/영어 정답, 한국어 질의/한국어 정답으로 나눠 측정하면 어느 쪽에서 품질 압력이 생기는지 빨리 보입니다.

## 체크리스트

- [ ] 한국어 문서와 영어 문서를 같은 인덱스에 넣었습니다.
- [ ] dense 기준선의 Recall@5를 최소 한 번 측정해 기록했습니다.
- [ ] 정규화와 `IndexFlatIP`를 짝으로 적용했습니다.
- [ ] 같은 의미의 한국어·영어 질의에서 top-1이 일관되는지 점검했습니다.
- [ ] sparse나 multi-vector를 추가하기 전에 dense만의 한계를 적어 두었습니다.

## 연습 문제

1. 영어 문서 6개, 한국어 문서 6개로 코퍼스를 늘린 뒤 한국어 질의 5개에 대한 Recall@1을 측정해 보세요. 정답 언어별로 Recall을 나눠 비교해 보세요.
2. `normalize_embeddings=False`로 바꾸고 긴 영어 문서가 점수를 어떻게 왜곡하는지 관찰해 보세요.
3. 같은 코퍼스를 KoSimCSE로도 인덱싱한 뒤, 한국어 정답과 영어 정답 케이스에서 BGE-M3와 Recall@5를 비교해 보세요. 어떤 패턴이 보이나요?

## 다국어 벤치마크 표를 직접 만드는 방법

다국어 검색에서 중요한 것은 숫자 하나가 아니라 케이스별 실패 위치입니다. 한국어 질의로 영어 문서를 찾는 케이스, 한국어 질의로 한국어 문서를 찾는 케이스를 분리해 기록해야 개선 방향이 보입니다.

```python
def evaluate_by_target_language(index, model, docs, eval_cases, top_k=5):
    buckets = {
        'ko_target': {'n': 0, 'hits': 0},
        'en_target': {'n': 0, 'hits': 0},
    }

    for case in eval_cases:
        q = case['query']
        gold = case['gold_idx']
        target_lang = docs[gold]['lang']

        vec = model.encode([q], normalize_embeddings=True).astype('float32')
        _, idx = index.search(vec, top_k)
        retrieved = idx[0].tolist()

        key = 'ko_target' if target_lang == 'ko' else 'en_target'
        buckets[key]['n'] += 1
        buckets[key]['hits'] += int(gold in retrieved)

    for key, row in buckets.items():
        recall = row['hits'] / row['n'] if row['n'] else 0.0
        print(key, f"Recall@{top_k}={recall:.3f}")
```

**Expected output:**

```text
ko_target Recall@5=0.920
en_target Recall@5=0.860
```

이 정도 분리는 운영에서 매우 실용적입니다. 예를 들어 영어 정답 Recall만 하락하면 코퍼스 갱신이 영어 문서 쪽에 치우쳤는지, 질의 전처리가 한국어 표현을 과도하게 줄였는지부터 점검할 수 있습니다.

## dense + sparse + rerank 확장 순서

BGE-M3를 쓰면 dense, sparse, multi-vector를 한 번에 쓰고 싶어집니다. 하지만 실무에서는 원인 추적이 가능한 순서가 더 중요합니다.

| 단계 | 구성 | 측정 지표 | 다음 단계로 넘어가는 기준 |
| --- | --- | --- | --- |
| 1 | Dense only (`IndexFlatIP`) | Recall@5, MRR@5 | 한국어 질의/영어 정답 Recall이 0.8 이상 |
| 2 | Dense + BM25(RRF) | Recall@5, NDCG@10 | 약어/고유명사 질의에서 오탐 감소 확인 |
| 3 | Dense top-50 + Reranker | Recall@5, Precision@1 | top-1 정확도 개선이 일관적 |
| 4 | Sparse/multi-vector 추가 | Latency, Cost, Quality | 지연 예산 내에서 의미 있는 이득 확인 |

이 순서를 지키면 "왜 좋아졌는지"를 설명할 수 있고, 회귀가 발생했을 때 되돌리는 비용도 작아집니다.

## production 설정 예시: 다국어 검색 API

다국어 검색 서비스는 모델 성능뿐 아니라 인덱스 운영 정책이 중요합니다. 아래는 BGE-M3를 기준으로 한 운영 설정 예시입니다.

```yaml
service:
  name: multilingual-retriever
  env: prod
  region: ap-northeast-2

embedding:
  model_id: BAAI/bge-m3
  normalize: true
  device: cuda
  dtype: float16
  batch_size: 96

index:
  backend: faiss
  type: ivf-flat-ip
  nlist: 4096
  nprobe: 24
  index_path: /data/index/docs.ivf
  metadata_path: /data/index/docs.meta.parquet

retrieval:
  top_k: 5
  min_score: 0.35
  reranker_enabled: true
  reranker_model: BAAI/bge-reranker-v2-m3

runtime:
  request_timeout_ms: 250
  max_qps_per_pod: 35
  warmup_queries:
    - 쿠버네티스 롤백 절차
    - 환불 SLA 정책
```

운영에서는 특히 `nprobe`와 `top_k`를 같이 관리해야 합니다. `nprobe`를 올리면 Recall은 좋아지지만 지연이 증가하므로, 요청 특성별로 프로파일을 분리해 두는 편이 좋습니다.

## 장애 상황에서 유용한 비교 로그

다국어 검색 장애는 특정 언어에서만 나타나는 경우가 많습니다. 요청마다 질의 언어, 정답 언어(평가 환경), 상위 후보 언어 분포를 같이 남기면 원인 분리가 빨라집니다.

```python
import json

def log_multilingual_retrieval(query, hits, query_lang='ko'):
    event = {
        'query': query,
        'query_lang': query_lang,
        'top_k': len(hits),
        'scores': [round(float(h['score']), 4) for h in hits],
        'langs': [h['lang'] for h in hits],
        'doc_ids': [h['id'] for h in hits],
    }
    print(json.dumps(event, ensure_ascii=False))
```

예를 들어 한국어 질의인데 상위 5개가 전부 영어로만 채워지는 시점이 잦아지면, 코퍼스 수급 불균형이나 토픽 편향을 의심해야 합니다.

## 토크나이저 길이 통계로 보는 다국어 입력 건강도

BGE-M3에서는 질의 언어가 바뀔 때 토큰 길이 분포가 크게 움직일 수 있습니다. 이 변화를 모르면 지연 증가를 모델 문제로 오해하기 쉽습니다. 아래처럼 질의 토큰 길이를 일별로 집계하면 운영 판단이 쉬워집니다.

```python
from transformers import AutoTokenizer
import numpy as np

tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-m3')

def token_length_stats(queries):
    lengths = [len(tokenizer.encode(q, add_special_tokens=True)) for q in queries]
    return {
        'count': len(lengths),
        'p50': int(np.percentile(lengths, 50)),
        'p90': int(np.percentile(lengths, 90)),
        'p99': int(np.percentile(lengths, 99)),
        'max': max(lengths),
    }
```

토큰 길이 p99가 갑자기 커지면, 프롬프트 입력에 로그 원문이 그대로 섞였는지, OCR 줄바꿈이 무너졌는지 먼저 확인해야 합니다.

## bilingual benchmark 예시 결과 표

다국어 기준선의 해석을 돕기 위해, 아래처럼 소규모 실험 결과를 문서에 남겨 두면 좋습니다.

| 모델 | ko->ko Recall@5 | ko->en Recall@5 | MRR@5 | p95 latency (ms) |
| --- | --- | --- | --- | --- |
| KoSimCSE | 0.94 | 0.51 | 0.73 | 34 |
| BGE-M3 dense | 0.92 | 0.86 | 0.79 | 51 |
| BGE-M3 dense + rerank | 0.95 | 0.89 | 0.84 | 89 |

이 표는 "어떤 모델이 무조건 우수한가"보다 "어떤 비용으로 어떤 개선을 얻었는가"를 보여 줍니다. 운영팀과 제품팀이 같은 그림을 보게 만드는 데 효과적입니다.

## 인덱스 재빌드와 배포 전략

다국어 코퍼스는 문서 증가 속도가 빠르기 때문에 인덱스 재빌드 전략을 먼저 정해야 합니다. 일반적으로는 아래 두 가지 패턴을 함께 씁니다.

1. **주간 전체 재빌드**: 누적 누락이나 드리프트를 정리합니다.
2. **시간 단위 증분 반영**: 최신 문서를 빠르게 검색 가능 상태로 올립니다.

```python
def should_trigger_full_rebuild(last_full_rebuild_hours, drift_ratio):
    if last_full_rebuild_hours >= 24 * 7:
        return True
    if drift_ratio >= 0.12:
        return True
    return False
```

여기서 `drift_ratio`는 전체 문서 중 증분 인덱스에만 있고 본 인덱스에 없는 문서 비율입니다. 이 값이 커지면 검색 결과가 오래된 문서에 치우치기 시작합니다.

## 팀 운영 체크포인트: 다국어 검색 회귀를 줄이는 절차

다국어 검색은 모델 품질보다 운영 절차에서 더 자주 흔들립니다. 주간 점검 루틴을 간단히 고정해 두면 불필요한 회귀를 크게 줄일 수 있습니다.

1. **코퍼스 증분 확인**: 지난주 대비 언어별 문서 증가율을 기록합니다.
2. **평가 세트 재실행**: ko->ko, ko->en Recall@5를 같은 시드로 다시 측정합니다.
3. **지연 예산 점검**: p95 지연과 GPU 메모리 사용량을 함께 확인합니다.
4. **상위 실패 케이스 기록**: 실패 질문 10개를 다음 회귀 세트에 고정합니다.

이 절차를 문서화해 두면, 새로운 모델이나 인덱스 옵션을 실험할 때도 팀 전체가 같은 기준으로 결과를 해석할 수 있습니다.

## 정리

BGE-M3 dense 예제의 가치는 다국어 검색의 기준선을 선명하게 그어 준다는 데 있습니다. 한국어 질의로 영어 runbook을 top-1까지 끌어올리는 것만으로도 이미 큰 진전입니다. sparse와 multi-vector의 추가 이득은 그 기준선 위에서만 제대로 측정할 수 있습니다. 한국어와 영어를 한 모델로 같은 공간에 넣는다는 한 가지 약속이, 내부 검색 v1을 가능하게 만듭니다.

다음 글에서는 4편 CLOVA OCR API를 다룹니다. 한국어 문서 이미지에서 텍스트를 안정적으로 뽑아 내고, 그 결과를 BGE-M3 코퍼스가 기대하는 형태로 정리하는 과정을 코드로 살펴봅니다.

## 처음 질문으로 돌아가기

- **BGE-M3는 한국어와 영어가 섞인 코퍼스에서 KoSimCSE보다 어디서 강합니까?**
  - 한국어 질의로 영어 runbook이나 영어 제품 문서를 찾아야 할 때 강점이 가장 분명하게 드러납니다. 이 글의 예제에서도 한국어 질문이 영어 롤백 문서를 top-1로 끌어올렸고, ko->en Recall을 따로 측정해 그 차이를 확인했습니다. 즉 BGE-M3의 첫 가치는 한국어 의미를 영어 문서 공간까지 안정적으로 이어 주는 데 있습니다.
- **하나의 모델이 dense, sparse, multi-vector 표현을 동시에 낸다는 말은 무엇을 뜻합니까?**
  - 같은 백본 모델에서 의미 벡터(dense), 토큰 가중치 기반 신호(sparse), 토큰별 상호작용용 표현(multi-vector)을 함께 꺼낼 수 있다는 뜻입니다. 다만 이 글은 그중 dense만 먼저 고정해 다국어 기준선을 측정했습니다. 이유는 나중에 sparse나 rerank를 추가했을 때 개선 원인이 어디서 왔는지 분리해서 읽기 위해서입니다.
- **다국어 검색 첫 버전에서는 dense만으로도 왜 충분한 경우가 많습니까?**
  - dense만으로도 한국어 질의와 영어 문서를 같은 벡터 공간에서 비교할 수 있어서 초기 개선 폭이 큽니다. 여기에 Recall@5를 먼저 찍어 두면 sparse나 multi-vector를 붙이기 전에도 기준선이 명확해집니다. 첫 버전에서 복잡한 신호를 한꺼번에 켜지 않는 이유는 품질 상승과 지연 증가의 원인을 설명 가능하게 남기기 위해서입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Korean AI Stack 101 (1/6): 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- **Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전 (현재 글)**
- Korean AI Stack 101 (4/6): CLOVA OCR API로 문서 텍스트 추출 (예정)
- Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기 (예정)
- Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

## 참고 자료

- [BAAI/bge-m3 model card](https://huggingface.co/BAAI/bge-m3)
- [BGE-M3 paper (M3-Embedding)](https://arxiv.org/abs/2402.03216)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/korean-ai-stack-101/ko/03-bge-m3-multilingual)

Tags: Korean NLP, LLM, Embeddings, OCR
