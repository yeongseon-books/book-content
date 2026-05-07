---
title: 데이터 정제와 중복 제거
series: ai-data-preparation-101
episode: 3
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- Cleaning
- Deduplication
- MinHash
last_reviewed: '2026-05-03'
seo_description: 'The Pile, C4, RedPajama 같은 대규모 코퍼스 작업자들이 입을 모아 강조하는 한 가지가 있습니다:
  dedup 단계가 가장 큰…'
---

# 데이터 정제와 중복 제거

> AI Data Preparation 101 시리즈 (3/10)

---
<!-- a-grade-intro:begin -->
## 핵심 질문

데이터 정제와 중복 제거를 어떤 순서로 해야 품질과 다양성을 동시에 잡을까요?

이 글은 그 질문에 답하기 위해 정제와 중복 제거의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## "중복 제거가 그렇게 중요한가요?"

The Pile, C4, RedPajama 같은 대규모 코퍼스 작업자들이 입을 모아 강조하는 한 가지가 있습니다: **dedup 단계가 가장 큰 품질 향상을 가져온다**. Lee et al.(2021)의 "Deduplicating Training Data Makes Language Models Better" 논문은 학습 데이터의 1% 중복 제거만으로도 perplexity가 의미 있게 떨어진다는 사실을 보여줬습니다.

중복은 단순히 "디스크 낭비"가 아닙니다. 모델이 같은 패턴을 반복 학습하면서 일반화 능력을 잃고, 평가 셋에 같은 문서가 들어가면 메트릭이 부풀려집니다. 이번 편은 정제(cleaning)와 중복 제거(dedup) 두 가지를 다룹니다.

## 정제 (Cleaning) — 6가지 기본 변환

raw text에 가장 흔한 문제 6가지와 처리 코드입니다.

```python
import re
import unicodedata
from html import unescape

def clean_text(text: str) -> str:
    if not text:
        return ""
    # 1. 인코딩 정규화 (NFC: 한글 자모 결합)
    text = unicodedata.normalize("NFC", text)
    # 2. HTML 엔티티 디코딩
    text = unescape(text)
    # 3. HTML 태그 제거
    text = re.sub(r"<[^>]+>", " ", text)
    # 4. 제어 문자 제거 (탭/개행 제외)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    # 5. 연속 공백 압축
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 6. 양끝 공백
    return text.strip()

# 테스트
samples = [
    "<p>Hello&nbsp;<b>world</b>!</p>",
    "안녕하세요\u200b\u200b여러분",  # zero-width space
    "Multi   spaces\n\n\n\nlines",
]
for s in samples:
    print(repr(clean_text(s)))
```

각 단계는 측정 가능한 문제(인코딩 깨짐, HTML 잔재, 제어 문자, 공백 노이즈)를 정확히 하나씩 잡습니다. **임의의 변환을 추가하지 마세요.** 정제 함수가 길어질수록 디버깅이 어려워지고, 의도치 않은 정보 손실이 생깁니다.

## 정제 전후 메트릭 비교

정제 함수를 바꿀 때마다 다음 지표를 같이 봅니다.

```python
def cleaning_diff(before: list[str], after: list[str]) -> dict:
    return {
        "rows_in": len(before),
        "rows_out": sum(1 for t in after if t),  # 빈 문자열 제외
        "avg_len_before": sum(len(t) for t in before) / max(len(before), 1),
        "avg_len_after": sum(len(t) for t in after) / max(len(after), 1),
        "char_reduction_pct": (
            1 - sum(len(t) for t in after) / max(sum(len(t) for t in before), 1)
        ) * 100,
    }
```

전체 문자 수가 5% 이상 줄면 의심합니다. 보통 HTML 태그가 많은 코퍼스에서는 10~20%가 정상이지만, 깨끗한 텍스트에서는 1~2%여야 합니다.

## 중복 제거 — 3가지 단계

dedup은 비용 순서로 단계를 나누어 적용합니다.

1. **Exact dedup** (sha256): 완전히 같은 문서. O(N) hashmap.
2. **Near-exact dedup** (MinHash + LSH): 90% 이상 유사한 문서. O(N) 근사.
3. **Semantic dedup** (embedding): 의미가 같은 paraphrase. O(N²) 또는 ANN으로 O(N log N).

대부분의 production 파이프라인은 1단계와 2단계만으로 충분합니다.

### 1단계: Exact dedup

```python
import hashlib

def exact_dedup(docs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for doc in docs:
        # 정규화 후 해시 (whitespace 차이 무시)
        norm = re.sub(r"\s+", " ", doc.strip().lower())
        h = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        if h not in seen:
            seen.add(h)
            out.append(doc)
    return out
```

**핵심 디테일**: 해시 전에 정규화를 거쳐야 의미 없는 공백 차이가 다른 문서로 인식되지 않습니다.

### 2단계: MinHash + LSH

긴 문서에서 일부만 다른 경우(웹 크롤에서 매우 흔함)를 잡으려면 MinHash가 필요합니다.

```python
from datasketch import MinHash, MinHashLSH

def make_minhash(text: str, num_perm: int = 128) -> MinHash:
    m = MinHash(num_perm=num_perm)
    # 5-gram of words (shingle)
    words = text.lower().split()
    for i in range(len(words) - 4):
        shingle = " ".join(words[i:i+5])
        m.update(shingle.encode("utf-8"))
    return m

def near_dedup(docs: list[str], threshold: float = 0.85) -> list[str]:
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    keep: list[int] = []
    for i, doc in enumerate(docs):
        mh = make_minhash(doc)
        if not lsh.query(mh):  # 비슷한 게 없으면 등록
            lsh.insert(str(i), mh)
            keep.append(i)
    return [docs[i] for i in keep]

# 사용 예
docs = [
    "The quick brown fox jumps over the lazy dog repeatedly today.",
    "The quick brown fox jumps over the lazy dog repeatedly today!",  # near-dup
    "Completely different content about machine learning and data.",
]
print(len(near_dedup(docs)))  # -> 2
```

`threshold=0.85`는 Jaccard 유사도 85% 이상이면 중복으로 봅니다. 실험으로 결정하세요. 0.7로 낮추면 false positive(다른 문서를 같다고 봄)가 늘고, 0.95로 올리면 near-dup을 놓칩니다.

### 3단계: Semantic dedup (선택)

paraphrase까지 잡고 싶다면 embedding 기반 유사도를 씁니다.

```python
# pip install sentence-transformers faiss-cpu
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def semantic_dedup(docs: list[str], threshold: float = 0.93) -> list[str]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embs = model.encode(docs, normalize_embeddings=True).astype("float32")
    index = faiss.IndexFlatIP(embs.shape[1])  # inner product = cosine (정규화됨)
    keep: list[int] = []
    for i, e in enumerate(embs):
        if index.ntotal > 0:
            scores, _ = index.search(e.reshape(1, -1), 1)
            if scores[0][0] >= threshold:
                continue  # near-paraphrase, skip
        index.add(e.reshape(1, -1))
        keep.append(i)
    return [docs[i] for i in keep]
```

semantic dedup은 비용이 비쌉니다(임베딩 + ANN 인덱스). 학습 데이터가 1억 row 미만일 때만 고려합니다.

## Train/eval cross-dedup — 가장 중요한 단계

train과 eval 셋 사이의 중복은 평가 메트릭을 망가뜨립니다.

```python
def cross_dedup(train: list[str], eval_set: list[str],
                threshold: float = 0.85) -> tuple[list[str], int]:
    """eval_set과 겹치는 train 샘플 제거. 제거된 개수도 반환."""
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    for i, doc in enumerate(eval_set):
        lsh.insert(f"eval_{i}", make_minhash(doc))
    clean_train: list[str] = []
    removed = 0
    for doc in train:
        if lsh.query(make_minhash(doc)):
            removed += 1
            continue
        clean_train.append(doc)
    return clean_train, removed
```

**eval 셋은 절대 건드리지 않습니다.** 항상 train에서만 제거합니다. 그래야 평가 메트릭의 정의가 일관됩니다.

## 처리 순서가 중요하다

cleaning과 dedup은 정해진 순서가 있습니다.

1. raw → clean (정제)
2. clean → exact dedup (정확히 같은 것 제거)
3. exact-deduped → near dedup (MinHash)
4. near-deduped → split (train/eval/test)
5. eval 결정 후 → train cross-dedup against eval

dedup을 cleaning 전에 하면, 공백 차이만 있는 문서가 별개로 남아 있게 됩니다. cross-dedup을 split 전에 하면 어느 쪽에서 제거할지 결정할 수 없습니다.

## 흔한 실수 5가지

1. **Cleaning 함수에 너무 많은 변환을 넣음**: 한 함수에 10개 이상의 정규식이 들어가면 디버깅 불가능. 함수를 작게 쪼개고 단계별 로그를 남깁니다.
2. **Exact dedup만 하고 끝**: 웹 크롤 데이터는 광고 한 줄, 타임스탬프 한 줄 차이로 거의 같은 문서가 수천 개 나옵니다. MinHash 단계를 반드시 추가합니다.
3. **Cross-dedup을 빼먹음**: train/eval 사이 leakage가 메트릭을 5~10%포인트 부풀립니다. 모든 평가 셋에 대해 cross-dedup을 실행합니다.
4. **MinHash threshold를 default 0.5로 사용**: datasketch 기본값은 너무 관대합니다. 0.85~0.9가 일반적인 텍스트 dedup의 안전한 시작점입니다.
5. **Cleaning 메트릭을 안 봄**: 새 정규식을 추가했더니 데이터의 30%가 사라진 사고가 흔합니다. char_reduction_pct를 매번 체크합니다.

## 핵심 요약

- Cleaning은 측정 가능한 문제 6가지(인코딩, HTML, 제어 문자, 공백 등)만 처리합니다. 임의 변환은 금지.
- Dedup은 3단계(exact → MinHash → semantic) 중 1~2단계로 production은 충분합니다.
- Train/eval cross-dedup은 평가 메트릭의 신뢰성을 결정하는 핵심 단계입니다. 항상 train에서만 제거합니다.
- 처리 순서: clean → exact dedup → near dedup → split → cross-dedup against eval.
- 모든 단계에서 입출력 row 수와 char_reduction_pct 같은 메트릭을 자동 기록합니다.
- 다음 편(4편)은 PII 탐지와 익명화입니다.

---

<!-- toc:begin -->
## 시니어 엔지니어는 이렇게 생각합니다

- **정규화가 중복 제거의 전제** — 공백·인코딩 차이가 중복을 숨깁니다.
- **exact dedup 다음 fuzzy dedup** — 두 단계 분리가 비용과 정확도 모두에 유리합니다.
- **MinHash·SimHash가 표준 도구** — 대규모 corpus에서 사실상 표준입니다.
- **중복 제거가 다양성을 해칠 수 있음** — 임계값을 의식적으로 설정합니다.
- **정제 결과를 항상 샘플 검사** — 자동 정제만 믿으면 사고가 됩니다.

## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- **데이터 정제와 중복 제거 (현재 글)**
- 학습 데이터 PII 탐지와 익명화 (예정)
- 토큰화와 청킹 전략 (예정)
- 데이터 품질 필터링 (예정)
- 합성 데이터 생성 (예정)
- 데이터 증강 기법 (예정)
- 학습/평가/테스트 분할과 오염 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Deduplicating Training Data Makes Language Models Better (Lee et al., 2021)](https://arxiv.org/abs/2107.06499)
- [datasketch - MinHash and LSH library](https://ekzhu.com/datasketch/)
- [The Pile paper - dedup methodology](https://arxiv.org/abs/2101.00027)
- [ftfy - fixes text for you](https://ftfy.readthedocs.io/)

Tags: Data Preparation, Cleaning, Deduplication, MinHash
