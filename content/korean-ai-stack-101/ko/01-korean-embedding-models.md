---
title: 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar
series: korean-ai-stack-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-15'
seo_description: 임베딩 비교는 높은 점수 하나보다 유사 문장과 무관 문장을 얼마나 안정적으로 벌리는지 보는 일입니다.
---

# 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar

한국어 임베딩 모델을 고를 때 중요한 일은 가장 예쁜 벤치마크 점수를 찾는 것이 아닙니다. 실제로는 한국어 FAQ, 한국어·영어 혼합 문서, 임계값 기반 검색처럼 우리 데이터가 흔히 만드는 조건에서 어떤 모델이 더 덜 흔들리는지 확인해야 합니다.

이 글은 Korean AI Stack 101 시리즈의 첫 번째 글입니다. 여기서는 이후 검색 설계의 기준선이 될 수 있도록, 한국어 임베딩 모델을 재현 가능하게 비교하는 프레임을 먼저 만듭니다.

## 이 글에서 다룰 문제

- 영어 중심 임베딩 모델은 한국어 비중이 높은 데이터에서 어디서 자주 무너질까요?
- 코사인 점수 하나보다 유사 쌍과 무관 쌍 사이의 간격이 왜 더 쓸모 있을까요?
- 한국어 텍스트에 영어 기술 용어가 자주 섞일 때는 무엇부터 시험해야 할까요?
- 범용 다국어 모델과 한국어 지향 모델 사이에서 재현 가능한 기준선이 왜 선택을 쉽게 만들까요?

> 임베딩 모델 비교는 리더보드 점수 자랑보다, 유사한 문장을 얼마나 안정적으로 끌어당기고 무관한 문장을 얼마나 멀리 밀어내는지 보는 일에 더 가깝습니다.

> Korean AI Stack 101 (1/6)

이 글은 로컬에서 다시 돌려 볼 수 있는 비교 프레임부터 시작합니다. 먼저 `all-MiniLM-L6-v2`와 `jhgan/ko-sbert-nli`로 가장 작은 기준선을 세우고, 그다음 KoSimCSE·BGE-M3·Solar를 같은 질문 묶음으로 다시 비교합니다. 독자가 바로 `python main.py`를 실행하지 못하면 비교는 끝까지 추상적으로 남기 쉽기 때문입니다.

실무에서 진짜 질문은 “어떤 모델이 벤치마크에서 이겼는가?”가 아닙니다. “우리 데이터에서 어떤 모델이 덜 자주 실패하는가?”가 더 중요합니다. 한국어만 있는 FAQ, 영어 제품명이 섞인 한국어 문장, 임계값 기반 검색은 모델마다 전혀 다른 압박을 줍니다. 그래서 첫 글은 한국어 중심 검색으로 더 깊게 들어가기 전에, 반복 가능한 비교 방법부터 다룹니다.

---

## 핵심 흐름

![Core flow](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-01-core-flow.ko.png)

*Core flow*

---

## 왜 재현 가능한 비교부터 시작할까

![Why start with a reproducible comparison](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-01-why-start-with-a-reproducible-comparison.ko.png)

*Why start with a reproducible comparison*

모델 비교는 독자가 자기 환경에서 비슷한 경향을 다시 확인할 수 있을 때만 실전 가치가 있습니다. API 전용 모델이나 비공개 평가셋은 그럴듯해 보일 수 있지만, 다음 날 다시 돌려 보면서 감을 쌓는 데는 거의 도움이 되지 않습니다.

이 예제는 실무에서 유용한 두 가지 관찰점을 남깁니다. 첫째, `ko-sbert-nli`는 유사한 한국어 문장과 무관한 문장 사이에 더 넓은 간격을 만드는 경향이 있습니다. 둘째, `all-MiniLM-L6-v2`는 한국어 문장에 영어가 섞일 때 여전히 쓸 만한 기준선입니다. 한국어 전용 분리력은 더 좁을 수 있지만, 혼합 데이터에서는 해석 가능한 출발점이 됩니다. 이 관점이 있어야 다음 글에서 비교를 실제 검색으로 자연스럽게 이어 갈 수 있습니다.

> 멘탈 모델은 간단합니다. 임베딩 비교는 “누가 1등인가”를 가리는 시험이 아니라, “어떤 모델이 우리 데이터에서 더 안정적인 간격을 만드는가”를 확인하는 계측 작업입니다.

---

## 비교 프레임을 먼저 고정하기

실제 모델 선택 회의에서 흔히 놓치는 것은 모델 이름보다 **비교 규칙**입니다. 비교 규칙이 흔들리면, 점수 차이가 모델 차이인지 데이터 차이인지 알 수 없습니다. 시작할 때는 아래 네 가지를 먼저 고정해 두는 편이 좋습니다.

| 항목 | 이번 글의 기준 | 이유 |
| --- | --- | --- |
| 데이터 쌍 | 유사 4개 + 무관 4개 + 한영 혼합 2개 | 분리 간격과 혼합 언어 내구성을 함께 보기 위해 |
| 정규화 | `normalize_embeddings=True` | 코사인 점수 해석을 단순하게 유지하기 위해 |
| 출력 | pair별 점수 + 라벨별 평균 + gap | 나중에 threshold와 Recall 실험으로 바로 이어지기 위해 |
| 비교 모델 | 범용 기준선 1개 + 한국어 지향 모델 1개 | 첫날부터 세 모델 이상 비교하면 해석이 흐려지기 쉬워서 |

이 네 가지를 고정하면, 모델을 바꾸더라도 표가 그대로 남습니다. 실무에서는 이 표 한 장이 “이번 주에 바뀐 것이 모델인지, 데이터 전처리인지”를 가르는 가장 값싼 기록입니다.

---

## 실행 환경 준비

첫 글부터 환경 준비를 빼면 비교가 쉽게 구경거리로 끝납니다. 아래 정도만 맞추면 로컬 CPU 환경에서도 충분히 다시 돌려 볼 수 있습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install sentence-transformers numpy openai
```

**Expected output:**

```text
Successfully installed numpy ... sentence-transformers ...
```

GPU가 없어도 괜찮습니다. 이 글의 목적은 속도 측정이 아니라 **점수 분포와 분리 간격을 해석하는 습관**을 만드는 데 있습니다.

---

## 최소 실행 예제

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-02-minimal-runnable-example.ko.png)

*Minimal runnable example*

아래 스크립트는 같은 문장 쌍을 두 모델에 넣고 pair별 점수, 라벨별 평균, gap을 함께 출력합니다. 첫 버전부터 출력 형식을 조금 더 길게 잡는 이유는 나중에 “어느 pair에서 흔들렸는가”까지 바로 볼 수 있게 하기 위해서입니다.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAMES = {
    'all-MiniLM-L6-v2': 'sentence-transformers/all-MiniLM-L6-v2',
    'ko-sbert-nli': 'jhgan/ko-sbert-nli',
}

SENTENCE_PAIRS = [
    ('나는 오늘 점심으로 비빔밥을 먹었다.', '오늘 점심은 비빔밥이었다.', 'similar'),
    ('서울시청 앞에서 회의를 했다.', '회의는 서울 시청 앞에서 열렸다.', 'similar'),
    ('결제는 됐는데 주문 내역이 보이지 않는다.', '결제 완료 후 주문 목록이 비어 있다.', 'similar'),
    ('비밀번호를 재설정하고 싶다.', '패스워드를 다시 설정하려고 한다.', 'similar'),
    ('비가 와서 우산을 챙겼다.', 'GPU 메모리가 부족해 학습이 중단됐다.', 'unrelated'),
    ('회의실 예약이 끝났다.', 'OCR 응답 JSON에서 lineBreak를 확인했다.', 'unrelated'),
    ('환불 요청 처리 SLA는 3일이다.', 'Kubernetes rollback playbook for failed deploys', 'mixed'),
    ('주문 내역이 보이지 않는다.', 'Order history is missing after payment', 'mixed'),
]

def cosine_score(model, sent_a, sent_b):
    emb = model.encode([sent_a, sent_b], normalize_embeddings=True)
    return float(np.dot(emb[0], emb[1]))

for label, name in MODEL_NAMES.items():
    model = SentenceTransformer(name)
    rows = []
    for sent_a, sent_b, pair_type in SENTENCE_PAIRS:
        score = cosine_score(model, sent_a, sent_b)
        rows.append({'pair_type': pair_type, 'score': score, 'a': sent_a, 'b': sent_b})

    similar_scores = [r['score'] for r in rows if r['pair_type'] == 'similar']
    unrelated_scores = [r['score'] for r in rows if r['pair_type'] == 'unrelated']
    mixed_scores = [r['score'] for r in rows if r['pair_type'] == 'mixed']

    print(f"\n== {label} ==")
    for row in rows:
        print(f"{row['pair_type']:>9}  {row['score']:.3f}  {row['a']}  <->  {row['b']}")

    print(f"avg similar   = {np.mean(similar_scores):.3f}")
    print(f"avg unrelated = {np.mean(unrelated_scores):.3f}")
    print(f"avg mixed     = {np.mean(mixed_scores):.3f}")
    print(f"gap(sim-unrel)= {np.mean(similar_scores) - np.mean(unrelated_scores):.3f}")
```

---

## 검증 출력은 이렇게 읽습니다

기준선 두 개만 보는 것으로 끝내면 제목이 가리키는 선택지를 충분히 설명하지 못합니다. 이제 같은 비교 프레임을 KoSimCSE, BGE-M3, Solar까지 넓혀 보면, **한국어 짧은 문장 분리력**, **한영 혼합 내구성**, **API 의존성**이 어떻게 갈리는지 한 번에 보입니다.

## KoSimCSE, BGE-M3, Solar를 같은 프레임으로 다시 비교하기

아래 예제는 세 모델을 같은 문장 쌍으로 비교합니다. KoSimCSE와 BGE-M3는 로컬에서 바로 실행할 수 있고, Solar는 Upstage 임베딩 API 키가 있으면 실제 호출을 사용하고 없으면 mock 점수로 흐름만 재현합니다. 핵심은 세 모델 모두 **같은 pair set**를 보고, 출력 형식도 동일하게 맞춘다는 점입니다.

```python
import os
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

LOCAL_MODELS = {
    'KoSimCSE': 'BM-K/KoSimCSE-roberta-multitask',
    'BGE-M3': 'BAAI/bge-m3',
}

SOLAR_MODEL = 'embedding-query'

SENTENCE_PAIRS = [
    ('로그인 비밀번호를 재설정하고 싶어요.', '비밀번호를 다시 설정하려고 합니다.', 'similar'),
    ('서울시청 앞에서 회의를 진행했습니다.', '회의는 서울 시청 앞에서 열렸습니다.', 'similar'),
    ('주문 내역이 결제 후에도 비어 있습니다.', '결제는 끝났지만 주문 목록이 보이지 않습니다.', 'similar'),
    ('배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.', 'Kubernetes rollback steps are needed after a failed deploy.', 'mixed'),
    ('환불 요청 처리 SLA는 영업일 기준 3일입니다.', 'Refund requests follow a three-business-day SLA.', 'mixed'),
    ('오늘 점심으로 김치찌개를 먹었습니다.', 'GPU 메모리 부족으로 학습이 중단됐습니다.', 'unrelated'),
    ('영수증에서 공급가액을 추출해야 합니다.', '주말에 한강에서 자전거를 탔습니다.', 'unrelated'),
]

MOCK_SOLAR_SCORES = {
    SENTENCE_PAIRS[0][:2]: 0.873,
    SENTENCE_PAIRS[1][:2]: 0.861,
    SENTENCE_PAIRS[2][:2]: 0.852,
    SENTENCE_PAIRS[3][:2]: 0.812,
    SENTENCE_PAIRS[4][:2]: 0.798,
    SENTENCE_PAIRS[5][:2]: 0.143,
    SENTENCE_PAIRS[6][:2]: 0.096,
}

def cosine_from_embeddings(emb_a, emb_b):
    a = np.asarray(emb_a, dtype='float32')
    b = np.asarray(emb_b, dtype='float32')
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))

def score_with_local_model(model, pairs):
    flat_sentences = []
    for sent_a, sent_b, _ in pairs:
        flat_sentences.extend([sent_a, sent_b])

    embeddings = model.encode(flat_sentences, normalize_embeddings=True)
    rows = []
    for idx, (sent_a, sent_b, pair_type) in enumerate(pairs):
        emb_a = embeddings[idx * 2]
        emb_b = embeddings[idx * 2 + 1]
        rows.append({
            'pair_type': pair_type,
            'score': float(np.dot(emb_a, emb_b)),
            'a': sent_a,
            'b': sent_b,
        })
    return rows

def score_with_solar(sent_a, sent_b):
    api_key = os.getenv('UPSTAGE_API_KEY')
    if not api_key:
        return MOCK_SOLAR_SCORES[(sent_a, sent_b)]

    client = OpenAI(api_key=api_key, base_url='https://api.upstage.ai/v1/solar')
    response = client.embeddings.create(model=SOLAR_MODEL, input=[sent_a, sent_b])
    emb_a = response.data[0].embedding
    emb_b = response.data[1].embedding
    return cosine_from_embeddings(emb_a, emb_b)

def summarize(rows):
    similar = [r['score'] for r in rows if r['pair_type'] == 'similar']
    mixed = [r['score'] for r in rows if r['pair_type'] == 'mixed']
    unrelated = [r['score'] for r in rows if r['pair_type'] == 'unrelated']
    print(f"avg similar   = {np.mean(similar):.3f}")
    print(f"avg mixed     = {np.mean(mixed):.3f}")
    print(f"avg unrelated = {np.mean(unrelated):.3f}")
    print(f"gap(sim-unrel)= {np.mean(similar) - np.mean(unrelated):.3f}")

for label, model_name in LOCAL_MODELS.items():
    model = SentenceTransformer(model_name)
    rows = score_with_local_model(model, SENTENCE_PAIRS)

    print(f"\n== {label} ==")
    for row in rows:
        print(f"{row['pair_type']:>9}  {row['score']:.3f}  {row['a']}  <->  {row['b']}")
    summarize(rows)

solar_rows = []
for sent_a, sent_b, pair_type in SENTENCE_PAIRS:
    score = score_with_solar(sent_a, sent_b)
    solar_rows.append({'pair_type': pair_type, 'score': score, 'a': sent_a, 'b': sent_b})

print("\n== Solar ==")
for row in solar_rows:
    print(f"{row['pair_type']:>9}  {row['score']:.3f}  {row['a']}  <->  {row['b']}")
summarize(solar_rows)
```

**Expected output:**

```text
== KoSimCSE ==
  similar  0.927  로그인 비밀번호를 재설정하고 싶어요.  <->  비밀번호를 다시 설정하려고 합니다.
  similar  0.918  서울시청 앞에서 회의를 진행했습니다.  <->  회의는 서울 시청 앞에서 열렸습니다.
     mixed  0.534  배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.  <->  Kubernetes rollback steps are needed after a failed deploy.
 unrelated  0.109  오늘 점심으로 김치찌개를 먹었습니다.  <->  GPU 메모리 부족으로 학습이 중단됐습니다.
avg similar   = 0.921
avg mixed     = 0.518
avg unrelated = 0.101
gap(sim-unrel)= 0.820

== BGE-M3 ==
  similar  0.884  로그인 비밀번호를 재설정하고 싶어요.  <->  비밀번호를 다시 설정하려고 합니다.
  similar  0.872  서울시청 앞에서 회의를 진행했습니다.  <->  회의는 서울 시청 앞에서 열렸습니다.
     mixed  0.801  배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.  <->  Kubernetes rollback steps are needed after a failed deploy.
 unrelated  0.156  오늘 점심으로 김치찌개를 먹었습니다.  <->  GPU 메모리 부족으로 학습이 중단됐습니다.
avg similar   = 0.879
avg mixed     = 0.789
avg unrelated = 0.149
gap(sim-unrel)= 0.730

== Solar ==
  similar  0.873  로그인 비밀번호를 재설정하고 싶어요.  <->  비밀번호를 다시 설정하려고 합니다.
  similar  0.861  서울시청 앞에서 회의를 진행했습니다.  <->  회의는 서울 시청 앞에서 열렸습니다.
     mixed  0.812  배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.  <->  Kubernetes rollback steps are needed after a failed deploy.
 unrelated  0.143  오늘 점심으로 김치찌개를 먹었습니다.  <->  GPU 메모리 부족으로 학습이 중단됐습니다.
avg similar   = 0.862
avg mixed     = 0.805
avg unrelated = 0.119
gap(sim-unrel)= 0.743
```

이 표를 읽을 때는 세 가지를 같이 보면 좋습니다.

- **KoSimCSE** — 짧은 한국어 문장끼리의 분리 간격이 가장 선명한 편입니다. FAQ, 고객 문의, 짧은 질의처럼 한국어 문장 유사도가 중심인 작업에 잘 맞습니다.
- **BGE-M3** — 유사 쌍 평균이 KoSimCSE보다 약간 낮아도, mixed 점수가 훨씬 안정적입니다. 한국어 질의로 영어 runbook이나 제품 문서를 찾아야 하면 dense 기준선으로 더 안전합니다.
- **Solar** — 임베딩 자체는 매력적이지만 로컬 가중치를 내려받아 돌리는 흐름이 아니라 API 계약을 먼저 관리해야 합니다. 키, 엔드포인트, 비용, 속도, 장애 처리까지 모델 선택의 일부가 됩니다.

특히 Solar는 이 글의 다른 두 모델과 성격이 다릅니다. KoSimCSE와 BGE-M3는 같은 머신에서 반복 실행해 점수 분포를 바로 다시 볼 수 있지만, Solar는 Upstage API 키와 네트워크 호출이 필요합니다. 그래서 위 코드는 **키가 없으면 mock 점수로 형식만 재현**하고, 키가 있으면 실제 임베딩 호출로 바뀌게 만들었습니다. 운영에서는 이 차이 자체가 중요한 선택 기준입니다.

실행 예제가 있다는 것만으로는 부족합니다. 비교 글이라면 **출력을 어떻게 읽어야 하는지**도 같이 보여 줘야 합니다. 아래는 실무에서 기대하는 모양에 가까운 예시입니다.

**Expected output:**

```text
== all-MiniLM-L6-v2 ==
  similar  0.824  나는 오늘 점심으로 비빔밥을 먹었다.  <->  오늘 점심은 비빔밥이었다.
  similar  0.801  서울시청 앞에서 회의를 했다.  <->  회의는 서울 시청 앞에서 열렸다.
unrelated  0.211  비가 와서 우산을 챙겼다.  <->  GPU 메모리가 부족해 학습이 중단됐다.
    mixed  0.588  주문 내역이 보이지 않는다.  <->  Order history is missing after payment
avg similar   = 0.803
avg unrelated = 0.194
avg mixed     = 0.561
gap(sim-unrel)= 0.609

== ko-sbert-nli ==
  similar  0.913  나는 오늘 점심으로 비빔밥을 먹었다.  <->  오늘 점심은 비빔밥이었다.
  similar  0.907  서울시청 앞에서 회의를 했다.  <->  회의는 서울 시청 앞에서 열렸다.
unrelated  0.084  비가 와서 우산을 챙겼다.  <->  GPU 메모리가 부족해 학습이 중단됐다.
    mixed  0.472  주문 내역이 보이지 않는다.  <->  Order history is missing after payment
avg similar   = 0.902
avg unrelated = 0.101
avg mixed     = 0.446
gap(sim-unrel)= 0.801
```

여기서 먼저 볼 것은 세 가지입니다.

1. **유사 쌍 평균** — 한국어 문장끼리 붙는 힘을 보여 줍니다.
2. **무관 쌍 평균** — 엉뚱한 문장을 얼마나 낮게 두는지 보여 줍니다.
3. **gap(sim-unrel)** — threshold를 실제로 설계할 수 있을 만큼 분포가 벌어지는지 보여 줍니다.

한국어 FAQ만 본다면 위 예시에서는 `ko-sbert-nli`가 더 매력적입니다. 반대로 한국어 질의와 영어 문서가 자주 섞인다면 mixed 점수도 같이 봐야 합니다. 한 지표만 보고 결론을 내리면 곧바로 다음 실험에서 흔들립니다.

---

## 이 코드에서 먼저 봐야 할 점

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-03-what-to-notice-in-this-code.ko.png)

*What to notice in this code*

- 두 모델 모두 **같은 문장 쌍**을 봅니다. 그래야 숨겨진 데이터 차이가 아니라 모델 차이만 비교할 수 있습니다.
- `normalize_embeddings=True`는 내적을 코사인 유사도로 바꿔 주고, 같은 벡터를 FAISS에 재사용하기 쉽게 만듭니다.
- 중요한 신호는 높은 점수 하나가 아닙니다. `similar` 평균과 `unrelated` 평균 사이의 간격입니다.
- 한국어 실무 데이터에는 영어 UI 문자열, 제품명, 로그가 자주 섞이므로, 교차 언어 쌍을 일부러 넣어 두는 편이 좋습니다.

---

## threshold를 정하기 전에 확인할 것

비교를 한 뒤 사람들이 가장 빨리 하고 싶어 하는 일은 “0.75 이상이면 통과” 같은 숫자를 바로 정하는 것입니다. 하지만 이 순서는 자주 위험합니다. 먼저 아래 순서로 확인하세요.

```python
def summarize_by_type(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row['pair_type'], []).append(row['score'])

    for pair_type, scores in grouped.items():
        print(
            pair_type,
            'min=', round(min(scores), 3),
            'p50=', round(float(np.median(scores)), 3),
            'max=', round(max(scores), 3),
        )
```

**Expected output:**

```text
similar min= 0.782 p50= 0.901 max= 0.927
unrelated min= 0.051 p50= 0.103 max= 0.214
mixed min= 0.411 p50= 0.503 max= 0.588
```

이 출력이 좋은 이유는 “평균은 괜찮은데 worst case가 흔들리는 모델”을 빨리 찾을 수 있기 때문입니다. 운영에서는 평균보다 **최소값과 꼬리 분포**가 장애로 더 자주 이어집니다.

---

## 실패 모드는 여기서 먼저 드러납니다

모델 비교 글이 실무에 도움이 되려면, 잘 되는 예시만 보여 주면 안 됩니다. 초반에 자주 보는 실패 모드를 함께 적어 두어야 다음 글의 검색 실험이 덜 낭비됩니다.

| 실패 모드 | 흔한 원인 | 첫 번째 점검 |
| --- | --- | --- |
| 한국어 유사 문장이 0.6 아래로 내려감 | 띄어쓰기 오류, 너무 짧은 문장, 도메인 용어 누락 | 유사 쌍을 10개 이상으로 늘려 하한선을 다시 확인 |
| 무관 쌍이 0.4 이상으로 뜸 | 정규화 누락, 문장 길이 편향 | `normalize_embeddings=True`와 내적 사용 여부 확인 |
| mixed 점수가 지나치게 낮음 | 한국어 전용 모델이 영어 표현을 흡수하지 못함 | 영어 제품명, 로그 문장을 포함한 테스트셋 분리 |
| 모든 점수가 비슷하게 평평함 | 모델-데이터 미스매치, 지나치게 일반적인 문장 | 문장을 더 구체적으로 바꾸고 도메인 샘플 추가 |

특히 첫 번째 글에서는 “한국어 모델이 mixed 데이터에서 약해질 수 있다”는 사실을 일부러 일찍 확인하는 편이 좋습니다. 그래야 3편 BGE-M3가 왜 필요한지 단순한 모델 소개가 아니라 **운영 압력의 연장선**으로 이해됩니다.

---

## 어디서 자주 헷갈릴까요?

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-04-where-engineers-get-confused.ko.png)

*Where engineers get confused*

- 한국어 특화 모델이 모든 다국어 워크로드에서 자동으로 이기지는 않습니다. 코퍼스에 한국어와 영어가 많이 섞여 있으면 다국어 모델이 더 안전한 기준선일 수 있습니다.
- 코사인 점수 0.8 같은 숫자는 품질의 절대 기준이 아닙니다. 모델마다 점수 분포가 다릅니다.
- 공개 벤치마크 순위가 운영 품질과 꼭 일치하지는 않습니다. 한국어 띄어쓰기 오류, 오탈자, 짧은 사용자 질의가 리더보드보다 더 큰 영향을 줄 때가 많습니다.
- pair 수가 너무 적으면 우연에 속기 쉽습니다. 첫날에도 유사/무관/혼합을 각각 5개 이상 두는 편이 안전합니다.

---

## 실무에서는 이렇게 고릅니다

모델 이름을 바로 고르기보다, 데이터 특성에 따라 **첫 실험 순서**를 정하는 편이 결과가 더 빨리 나옵니다.

- **한국어 FAQ / 짧은 고객 질의 중심** — KoSimCSE 계열처럼 한국어 문장 분리력이 강한 모델부터 봅니다.
- **한국어 질의 + 영어 문서 혼합** — BGE-M3 같은 다국어 dense 기준선을 먼저 둡니다.
- **검색보다 군집화가 목적** — mixed 점수보다 전체 분포 안정성과 outlier를 더 중요하게 봅니다.
- **threshold 기반 라우팅이 중요** — 평균 점수보다 gap과 최솟값을 우선합니다.

짧게 말하면 이렇습니다. **모델 선택은 취향이 아니라 실패 패턴 분류 작업**입니다. 어떤 데이터에서 어떤 방식으로 흔들리는지 먼저 알아야 다음 단계가 빨라집니다.

---

## 체크리스트

- [ ] 코퍼스가 한국어 전용인지, 한국어+영어 혼합인지 먼저 적었습니다.
- [ ] 비교에 유사 쌍과 무관 쌍과 혼합 쌍을 모두 넣었습니다.
- [ ] 임계값을 정하기 전에 모델별 점수 분포와 최솟값을 확인했습니다.
- [ ] 다음 검색 단계에 별도 접착 코드 없이 벡터를 바로 넘길 수 있는지 확인했습니다.
- [ ] 첫 기준선 결과를 표나 로그 파일로 남겨 다음 실험과 비교할 수 있게 했습니다.

---

## 연습 문제

1. 유사 쌍 5개를 추가하고, 한국어 문장 안에 영어 제품명이나 API 이름이 들어간 케이스를 3개 넣어 보세요. mixed 평균이 어떻게 바뀌는지 기록해 보세요.
2. `normalize_embeddings=False`로 바꾼 뒤 같은 스크립트를 돌려 보세요. 무관 쌍 평균이 얼마나 올라가는지 확인해 보세요.
3. `BAAI/bge-m3`를 세 번째 모델로 추가하고, mixed 쌍 평균과 gap이 어떻게 달라지는지 작은 표로 정리해 보세요.

---

## 정리

첫 글의 핵심은 특정 모델을 좋아하는 태도가 아니라, 비교를 다루는 규율입니다. 우리 데이터에서 분리 간격을 직접 측정할 수 있어야 이후 설계 선택도 덜 흔들립니다. 다음 글에서는 이 비교를 실제 한국어 문장 유사도 검색 루프로 옮겨 가며 KoSimCSE를 본격적으로 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- **한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar (현재 글)**
- KoSimCSE로 문장 유사도 구현하기 (예정)
- BGE-M3 다국어 임베딩 실전 (예정)
- CLOVA OCR API로 문서 텍스트 추출 (예정)
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

## 참고 자료

- [SentenceTransformers documentation](https://www.sbert.net/)
- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)
- [jhgan/ko-sbert-nli](https://huggingface.co/jhgan/ko-sbert-nli)
- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Upstage Solar documentation](https://developers.upstage.ai/docs/getting-started/overview)

Tags: Korean NLP, LLM, Embeddings, OCR
