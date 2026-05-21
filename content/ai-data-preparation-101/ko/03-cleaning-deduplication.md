---
episode: 3
language: ko
last_reviewed: '2026-05-14'
seo_description: 대규모 코퍼스 작업자들이 가장 효과 큰 단계로 꼽는 정제와 중복 제거를, 패턴별 처리 전략과 함께 정리합니다.
series: ai-data-preparation-101
status: publish-ready
tags:
- Data Preparation
- Cleaning
- Deduplication
- MinHash
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: "AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거"
---

# AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거

정제와 중복 제거는 늘 “귀찮지만 필요한 청소 작업”처럼 취급됩니다. 그러나 대규모 코퍼스를 다뤄 본 팀일수록 이 단계를 품질 향상 폭이 가장 큰 구간으로 봅니다. 모델은 그대로 두고 데이터만 정리해도 평가 지표와 일반화 성능이 달라지기 때문입니다.

문제는 정제 함수가 길어질수록 무엇이 데이터를 망가뜨렸는지 추적하기 어려워진다는 점입니다. 중복 제거도 exact dedup에서 멈추면 웹 크롤링 문서 특유의 near-duplicate를 대부분 놓칩니다.

운영 관점에서는 두 가지가 중요합니다. 첫째, 각 정제 변환이 측정 가능한 문제를 겨냥해야 합니다. 둘째, 학습셋과 평가셋 사이 중복 제거를 별도 단계로 두어야 평가 점수를 믿을 수 있습니다.

데이터 정제와 dedup은 단순히 파일 크기를 줄이는 작업이 아니라, 모델이 반복 학습과 누수에서 얼마나 자유로울지를 결정하는 작업입니다.

이 글은 AI Data Preparation 101 시리즈의 3번째 글입니다.

여기서는 원문 정제의 기본 변환과 exact·near·semantic dedup의 차이를 정리하고, 특히 train/eval cross-dedup이 왜 핵심인지 설명하겠습니다.


![AI 데이터 준비 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/03/03-01-big-picture.ko.png)
*AI 데이터 준비 3장 흐름 개요*
> 데이터 정제와 중복 제거의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 정제 함수는 왜 작은 변환들의 합으로 유지해야 할까요?
- exact dedup만으로는 웹 코퍼스 품질 문제가 왜 충분히 해결되지 않을까요?
- MinHash threshold를 너무 낮추거나 높이면 어떤 오류가 생길까요?

## 왜 이 글이 중요한가

정제와 중복 제거를 잘하면 학습 효율이 올라가고, 평가 지표의 신뢰도가 높아집니다. 동일한 문장을 수없이 반복 학습시키지 않아도 되므로 모델이 더 넓은 분포를 보게 되고, 저장·학습 비용도 함께 절약됩니다.

반대로 이 단계를 대충 넘기면 웹 보일러플레이트, 광고 줄, 공백 차이만 있는 복제 문서가 그대로 남습니다. 특히 평가셋과 겹치는 near-duplicate를 막지 못하면 모델이 외운 내용을 일반화 성능처럼 보이게 만듭니다.

이 글은 정제와 dedup을 별개의 유틸리티 함수가 아니라, 품질 측정과 평가 무결성을 동시에 책임지는 파이프라인 단계로 이해하게 만드는 데 목적이 있습니다.

## 핵심 관점

정제는 텍스트를 예쁘게 만드는 작업이 아닙니다. 깨진 인코딩, HTML 잔여물, 제어 문자, 과도한 공백처럼 모델에게 거의 도움이 되지 않는 잡음을 제거하는 단계입니다. 따라서 각 변환은 무엇을 없애는지 설명 가능해야 합니다.

중복 제거는 세 단계로 생각하면 쉽습니다. exact dedup은 완전히 같은 문서를 제거하고, MinHash 기반 near dedup은 거의 같은 문서를 잡고, semantic dedup은 의미상 같은 패러프레이즈까지 다룹니다. 대부분의 운영 파이프라인은 앞의 두 단계까지만으로도 큰 효과를 얻습니다.

무엇보다 중요한 것은 순서입니다. 정제 없이 dedup을 하면 공백과 대소문자 차이만 있는 문서가 그대로 남고, split 전에 cross-dedup 규칙을 세우지 않으면 평가 기준 자체가 흔들립니다.

> 정제와 dedup의 목적은 텍스트를 아름답게 만드는 것이 아니라, 모델이 같은 정보를 반복해서 외우거나 평가셋을 미리 보는 일을 최대한 줄이는 것입니다.

## 핵심 개념

### 정제 함수는 여섯 가지 기본 변환에서 출발합니다

과하게 많은 regex를 한 함수에 넣는 순간 디버깅이 어려워집니다. 아래 예제는 raw text에서 자주 만나는 여섯 가지 문제만 다룹니다.

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
    # 4. 제어 문자 처리 (tab/newline 유지)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    # 5. 연속 공백 축약
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 6. Strip
    return text.strip()

# Test
samples = [
    "<p>Hello&nbsp;<b>world</b>!</p>",
    "Hello\u200b\u200bworld",  # zero-width space
    "Multi   spaces\n\n\n\nlines",
]
for s in samples:
    print(repr(clean_text(s)))
```

각 단계는 인코딩 정규화, HTML entity decode, HTML 태그 제거, 제어 문자 정리, 공백 압축, strip처럼 역할이 분명합니다. 중요한 점은 “문제를 하나씩 제거한다”는 태도를 유지하는 것입니다.

### 정제 변경은 항상 diff metric으로 측정해야 합니다

정제 코드를 조금만 바꿔도 데이터 손실이 커질 수 있습니다. 그래서 코드 리뷰보다 먼저 숫자로 비교해야 합니다.

```python
def cleaning_diff(before: list[str], after: list[str]) -> dict:
    return {
        "rows_in": len(before),
        "rows_out": sum(1 for t in after if t),  # exclude empty
        "avg_len_before": sum(len(t) for t in before) / max(len(before), 1),
        "avg_len_after": sum(len(t) for t in after) / max(len(after), 1),
        "char_reduction_pct": (
            1 - sum(len(t) for t in after) / max(sum(len(t) for t in before), 1)
        ) * 100,
    }
```

`char_reduction_pct`가 갑자기 커지면 새 정규식이 데이터를 과하게 잘라냈을 가능성이 큽니다. HTML 비중이 큰 코퍼스가 아니라면 1~2% 수준이 자연스럽고, 10% 이상이면 의심부터 하는 편이 안전합니다.

### dedup은 비용이 싼 순서대로 진행합니다

운영에서는 아래 순서가 가장 실용적입니다.

1. **Exact dedup**: 해시로 동일 문서를 제거합니다.

2. **Near-exact dedup**: MinHash + LSH로 90% 가까이 비슷한 문서를 제거합니다.

3. **Semantic dedup**: 임베딩 기반으로 패러프레이즈까지 제거합니다.

대부분의 프로덕션 파이프라인은 1단계와 2단계까지만 넣어도 충분히 큰 효과를 얻습니다.

#### Stage 1: Exact dedup

```python
import hashlib

def exact_dedup(docs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for doc in docs:
        # 해시 전에 정규화하여 공백 차이를 무시
        norm = re.sub(r"\s+", " ", doc.strip().lower())
        h = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        if h not in seen:
            seen.add(h)
            out.append(doc)
    return out
```

여기서 핵심은 hashing 전에 정규화하는 것입니다. 공백과 대소문자 차이만 있는 문서를 서로 다른 문서로 남겨 두면 exact dedup의 효과가 크게 떨어집니다.

#### Stage 2: MinHash + LSH

```python
from datasketch import MinHash, MinHashLSH

def make_minhash(text: str, num_perm: int = 128) -> MinHash:
    m = MinHash(num_perm=num_perm)
    # 5-gram 단어 shingle 생성
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
        if not lsh.query(mh):  # nothing similar yet, keep
            lsh.insert(str(i), mh)
            keep.append(i)
    return [docs[i] for i in keep]

# Example
docs = [
    "The quick brown fox jumps over the lazy dog repeatedly today.",
    "The quick brown fox jumps over the lazy dog repeatedly today!",  # near-dup
    "Completely different content about machine learning and data.",
]
print(len(near_dedup(docs)))  # -> 2
```

웹 크롤링 문서는 광고 줄 하나, 타임스탬프 한 줄만 달라도 exact dedup을 통과합니다. MinHash는 이 near-duplicate를 잡기 위한 사실상의 필수 단계입니다. 일반 텍스트라면 0.85~0.9 근처에서 시작하는 편이 안전합니다.

#### Stage 3: Semantic dedup

```python
# pip install sentence-transformers faiss-cpu
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def semantic_dedup(docs: list[str], threshold: float = 0.93) -> list[str]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embs = model.encode(docs, normalize_embeddings=True).astype("float32")
    index = faiss.IndexFlatIP(embs.shape[1])  # inner product = cosine on normalized
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

의미 기반 dedup은 강력하지만 비용이 큽니다. 임베딩 생성과 ANN 검색 비용이 있기 때문에, 데이터셋 규모와 목적이 명확할 때만 넣는 편이 좋습니다.

### train/eval cross-dedup이 평가를 살립니다

정제와 dedup 중 가장 중요한 한 단계만 고르라면 저는 cross-dedup을 고르겠습니다. 평가셋과 겹치는 학습 문서가 남아 있으면 지표는 이미 오염됐기 때문입니다.

```python
def cross_dedup(train: list[str], eval_set: list[str],
                threshold: float = 0.85) -> tuple[list[str], int]:
    """Remove train rows that overlap eval_set. Returns also count removed."""
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

중요한 규칙은 하나입니다. **평가셋은 건드리지 않고 학습셋에서만 제거합니다.** 그래야 평가 기준이 바뀌지 않습니다.

### 순서를 잘못 잡으면 dedup이 무력화됩니다

정제와 dedup은 다음 순서로 이어져야 합니다.

1. raw → clean

2. clean → exact dedup

3. exact-deduped → near dedup

4. near-deduped → split

5. split 후 → train을 eval 기준으로 cross-dedup

이 순서를 어기면 공백 차이 복제본이 살아남거나, 어느 쪽을 제거해야 하는지 규칙이 모호해집니다. dedup은 알고리즘 선택만큼 순서 설계가 중요합니다.

## 적용 전후 샘플과 품질 지표를 같이 남기는 방식

정제와 dedup에서 팀 간 합의가 가장 빨리 깨지는 지점은 “이번 규칙이 정말 좋아졌는가”입니다. 이를 막으려면 규칙 설명보다 before/after 샘플과 수치가 먼저 나와야 합니다.

```python
import pandas as pd

def summarize_before_after(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> dict:
    raw_text = raw_df["text"].astype(str)
    clean_text = clean_df["text"].astype(str)
    return {
        "raw_rows": len(raw_df),
        "clean_rows": len(clean_df),
        "row_drop_ratio": 1 - len(clean_df) / max(len(raw_df), 1),
        "raw_dup_ratio": 1 - raw_text.nunique() / max(len(raw_text), 1),
        "clean_dup_ratio": 1 - clean_text.nunique() / max(len(clean_text), 1),
        "raw_avg_len": float(raw_text.str.len().mean()),
        "clean_avg_len": float(clean_text.str.len().mean()),
    }

SAMPLE_BEFORE = "<div>광고문의 010-1111-2222</div>\n\n지금 가입하면 50%"
SAMPLE_AFTER = "지금 가입하면 50%"
```

**Before/After 예시**

```text
before: <div>광고문의 010-1111-2222</div>

지금 가입하면 50%
after : 지금 가입하면 50%
```

이처럼 샘플을 함께 남기면 “숫자는 좋아졌는데 의미가 망가졌다”는 반론을 빨리 검증할 수 있습니다.

## MinHash threshold 튜닝 절차

MinHash의 threshold를 감으로 정하면 false positive와 false negative가 함께 늘어납니다. 실무에서는 라벨링된 pair 샘플로 threshold를 먼저 고정합니다.

```python
CANDIDATE_THRESHOLDS = [0.75, 0.80, 0.85, 0.90]

# hand_labeled_pairs: (doc_a, doc_b, is_duplicate)
def evaluate_threshold(hand_labeled_pairs, near_dup_fn):
    out = []
    for th in CANDIDATE_THRESHOLDS:
        tp = fp = fn = 0
        for a, b, y in hand_labeled_pairs:
            pred = near_dup_fn(a, b, threshold=th)
            if pred and y:
                tp += 1
            elif pred and not y:
                fp += 1
            elif (not pred) and y:
                fn += 1
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        out.append({"threshold": th, "precision": precision, "recall": recall})
    return out
```

운영 기본값은 보통 `precision`을 조금 더 우선합니다. 중복이 아닌 문서를 잘못 제거하면 정보 손실이 즉시 생기기 때문입니다.

## DVC로 dedup 결과 버전 관리

정제와 dedup은 결과물이 크고 반복 실행이 많아서 Git만으로 추적하기 어렵습니다. 아래처럼 DVC를 같이 쓰면 데이터 버전과 코드 커밋을 함께 묶기 쉽습니다.

```bash
dvc add data/clean/train_dedup.parquet
git add data/clean/train_dedup.parquet.dvc dvc.lock dvc.yaml
git commit -m "Add deduplicated train set v1.3"
```

```yaml
stages:
  clean_dedup:
    cmd: python pipelines/clean_dedup.py --input data/raw/train.parquet --output data/clean/train_dedup.parquet
    deps:
      - pipelines/clean_dedup.py
      - data/raw/train.parquet
    outs:
      - data/clean/train_dedup.parquet
    metrics:
      - reports/clean_dedup_metrics.json
```

이 구성을 두면 “어제보다 왜 행 수가 12% 줄었나?” 같은 질문을 코드와 데이터 버전으로 바로 재현할 수 있습니다.

## 데이터 정제 검증 스키마 예시

정제 결과를 JSON 파일로만 남기면 누락 필드가 생겨도 늦게 발견됩니다. 검증 스키마를 두면 품질 회귀를 조기 차단할 수 있습니다.

```python
from pydantic import BaseModel, Field

class CleaningMetrics(BaseModel):
    raw_rows: int = Field(ge=1)
    clean_rows: int = Field(ge=1)
    raw_dup_ratio: float = Field(ge=0.0, le=1.0)
    clean_dup_ratio: float = Field(ge=0.0, le=1.0)
    row_drop_ratio: float = Field(ge=0.0, le=1.0)
    minhash_threshold: float = Field(ge=0.5, le=0.99)

class CleaningGate(BaseModel):
    max_row_drop_ratio: float = 0.30
    max_clean_dup_ratio: float = 0.08

def pass_gate(metrics: CleaningMetrics, gate: CleaningGate) -> bool:
    return metrics.row_drop_ratio <= gate.max_row_drop_ratio and metrics.clean_dup_ratio <= gate.max_clean_dup_ratio
```

## 분할 전후 중복률 비교 표

| 단계 | 중복률 | 메모 |
| --- | ---: | --- |
| raw | 0.31 | 크롤링 footer 복제 다수 |
| clean + exact dedup | 0.14 | 공백/대소문자 차이 제거 |
| + MinHash near dedup | 0.06 | 유사 문서 클러스터 축소 |
| split 후 train/eval cross-dedup | 0.00(교차) | 평가 오염 방지 |

이 표처럼 교차 중복률을 별도 항목으로 보고해야 평가 신뢰도를 실제로 설명할 수 있습니다.

## 운영에서 바로 쓰는 점검 질문

아래 질문은 배포 직전 리뷰에서 실제로 자주 쓰는 체크 항목입니다. 단순 문서 확인이 아니라, 각 질문에 대해 파일 경로나 지표 값으로 즉시 답할 수 있어야 합니다.

1. 이번 데이터셋은 어떤 버전에서 왔고, sha256은 무엇인가요?
2. 지난 배치 대비 duplicate/null/length 분포가 얼마나 변했나요?
3. 제거된 샘플은 어떤 규칙 때문에 빠졌고, 상위 제거 사유는 무엇인가요?
4. train/eval/test 경계에서 누수 가능성은 수치로 얼마나 남아 있나요?
5. 이번 배치에서 사람이 검토한 샘플과 발견된 오류 유형은 무엇인가요?

```python
def release_readiness(summary: dict) -> tuple[bool, list[str]]:
    issues = []
    if not summary.get("dataset_sha256"):
        issues.append("missing_dataset_sha256")
    if summary.get("duplicate_ratio", 1.0) > 0.10:
        issues.append("duplicate_ratio_too_high")
    if summary.get("null_ratio", 1.0) > 0.02:
        issues.append("null_ratio_too_high")
    if summary.get("contamination_ratio", 1.0) > 0.01:
        issues.append("contamination_ratio_too_high")
    if summary.get("human_reviewed_rows", 0) < 100:
        issues.append("insufficient_human_review")
    return len(issues) == 0, issues
```

운영 팀은 이 함수를 그대로 쓰지 않더라도 같은 개념을 파이프라인 게이트로 구현해야 합니다. 핵심은 “준비가 되었는지 느낌으로 판단하지 않는다”는 점입니다.

## 실무 로그 예시

```text
[release-check] dataset=v2.4.1 sha=4fb1...
[release-check] duplicate_ratio=0.061 null_ratio=0.008
[release-check] contamination_ratio=0.004 human_reviewed_rows=240
[release-check] status=PASS
```

이 로그 한 묶음이 있으면 모델 성능이 흔들릴 때도 데이터 준비 단계를 빠르게 제외하거나 집중 점검할 수 있습니다. 데이터 준비의 품질은 글 한 편의 설명보다, 이런 반복 가능한 검증 로그에서 드러납니다.

### dedup 실패 복구 규칙

near-dedup이 과하게 작동해 데이터가 과소 삭제되면 즉시 이전 DVC 아티팩트로 롤백하고 threshold를 한 단계 올려 재실행합니다. 이때 롤백 근거와 재실행 결과를 같은 리포트에 남겨야 의사결정 히스토리가 보존됩니다.

### 릴리스 노트에 남겨야 할 최소 항목

해당 단계의 변경은 릴리스 노트에도 남겨야 합니다. 최소한 `변경 규칙`, `영향받은 행 수`, `핵심 지표 변화`, `롤백 경로` 네 항목이 있어야 다음 배치에서 같은 판단을 반복할 수 있습니다.

운영 기준으로는 threshold 변경 시 이전 배치와 비교표를 반드시 남겨야 합니다.

또한 샘플 기반 수동 검토를 주 1회 유지하면 과삭제 회귀를 조기에 발견할 수 있습니다.

정제 기준은 분기마다 한 번씩 재검토해 도메인 변화에 맞춰 업데이트해야 합니다.

## 흔히 헷갈리는 지점

- **정제는 많이 할수록 좋습니다**: 설명할 수 없는 변환을 계속 추가하면 정보 손실이 커지고 원인 분석이 불가능해집니다.
- **exact dedup이면 충분합니다**: 웹 코퍼스는 광고 줄, 날짜, footer 차이만 있는 near-duplicate가 훨씬 많습니다.
- **MinHash threshold는 기본값을 쓰면 됩니다**: 너무 낮으면 false positive가 늘고, 너무 높으면 진짜 near-duplicate를 놓칩니다. 도메인별 튜닝이 필요합니다.
- **평가셋 쪽에서 겹치는 샘플을 지워도 괜찮습니다**: 평가 정의를 바꾸지 않으려면 항상 학습셋에서만 제거해야 합니다.

## 운영 체크리스트

- [ ] 정제 함수의 각 변환 단계가 어떤 잡음을 줄이기 위한 것인지 설명 가능하다
- [ ] 정제 코드 변경 때 rows_in/out과 char_reduction_pct를 자동 기록한다
- [ ] exact dedup 전에 공백·대소문자 정규화를 적용한다
- [ ] MinHash 기반 near dedup을 split 전에 실행한다
- [ ] 모든 eval set에 대해 train/eval cross-dedup을 별도 단계로 유지한다

## 정리

정제와 중복 제거는 품질 향상 폭이 큰 단계이지만, 임의 규칙을 쌓아 두는 식으로 운영하면 오히려 데이터 손실과 평가 왜곡을 부릅니다. 작은 변환, 명시적 metric, 단계별 로그가 중요합니다.

exact dedup, MinHash 기반 near dedup, 선택적 semantic dedup이라는 세 층을 구분하면 비용과 효과를 균형 있게 가져갈 수 있습니다. 대부분의 실전 파이프라인은 exact와 near dedup만으로도 충분히 좋아집니다.

다음 글에서는 정제된 데이터 안에 남아 있을 수 있는 개인정보를 어떻게 탐지하고, 어떤 방식으로 익명화하며, 감사 로그와 샘플링 검증을 어떻게 붙여야 하는지 다룹니다.

## 처음 질문으로 돌아가기

- **정제 함수는 왜 작은 변환들의 합으로 유지해야 할까요?**
  - 본문의 기준은 데이터 정제와 중복 제거를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **exact dedup만으로는 웹 코퍼스 품질 문제가 왜 충분히 해결되지 않을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **MinHash threshold를 너무 낮추거나 높이면 어떤 오류가 생길까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- **데이터 정제와 중복 제거 (현재 글)**
- 학습 데이터 PII 탐지와 익명화 (예정)
- Tokenization과 Chunking 전략 (예정)
- 데이터 품질 필터링 — Heuristic과 Classifier (예정)
- 합성 데이터 생성 — Self-Instruct부터 Distillation까지 (예정)
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Deduplicating Training Data Makes Language Models Better (Lee et al., 2021)](https://arxiv.org/abs/2107.06499)
- [datasketch - MinHash and LSH library](https://ekzhu.com/datasketch/)
- [C4: Colossal Clean Crawled Corpus](https://huggingface.co/datasets/allenai/c4)
- [The Pile](https://pile.eleuther.ai/)

### 관련 시리즈
- [AI Evaluation 101 — 평가 데이터셋 설계하기](../../ai-evaluation-101/ko/02-evaluation-dataset-design.md)
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/03-cleaning-deduplication)

Tags: Data Preparation, Cleaning, Deduplication, MinHash
