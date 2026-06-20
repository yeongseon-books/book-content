---
title: "바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할"
series: ai-data-preparation-101
episode: 9
language: ko
tags:
- Train/Test Split
- Contamination
- Data Leakage
- Stratification
- Temporal Split
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 아홉 번째 글입니다.

---

바이브코딩으로 모델을 학습하고 "오프라인 F1이 0.93인데 실제 서비스에서 왜 이렇게 낮지?"라는 상황을 만납니다. 범인이 데이터 분할 방식일 때가 많습니다. `train_test_split(random_state=42)` 한 줄로 나눈 데이터는 이상적으로 보이지만, 미래 데이터가 학습에 섞이거나 같은 사용자가 train과 test 양쪽에 들어가 있을 수 있습니다.

분할은 단순히 80/10/10 비율을 만드는 문제가 아닙니다. 어떤 미래를 예측하는 모델인지, 같은 사용자가 여러 샘플을 갖는지, 소수 클래스가 얼마나 작은지에 따라 적합한 전략이 완전히 달라집니다. 잘못 나누면 이후 모든 지표가 잘못된 질문에 답하게 됩니다.

LLM 시대에는 문제가 한 단계 더 심각합니다. 벤치마크 데이터가 이미 사전학습 코퍼스에 포함돼 있다면, 높은 점수가 일반화 성능인지 암기 성능인지 구분이 어렵습니다. 이를 contamination이라고 합니다.

> \"분할의 목표는 데이터를 예쁘게 나누는 것이 아니라, 실제 배포 환경을 최대한 정직하게 흉내 내는 평가 조건을 만드는 것입니다.\"

## 이 글에서 다룰 질문

1. 단순 random split이 운영 환경에서 무너지는 이유는?
2. 클래스 불균형이 있을 때 어떤 분할 전략을 써야 하나요?
3. 사용자/세션 기반 데이터에서 누수를 막는 방법은?
4. 시계열 데이터는 왜 temporal split이 필수인가요?
5. LLM benchmark contamination을 어떻게 감지하나요?

---

## 분할 전략 비교

| 전략 | 사용 시기 | 핵심 보장 |
|------|----------|----------|
| Random split | iid 데이터, 빠른 베이스라인 | 단순 무작위 |
| Stratified split | 클래스 불균형 | 클래스 비율 보존 |
| Group split | 사용자/세션/환자 반복 | 그룹 누수 방지 |
| Temporal split | 시계열, 미래 예측 | 미래 정보 차단 |

## Before / After: 분할 전략 도입

**Before (무작위 분할로 미래 정보 누수)**
```python
from sklearn.model_selection import train_test_split

# 시계열 데이터인데 무작위로 나눔
train, test = train_test_split(df, test_size=0.2, random_state=42)
# 문제: 2026-04 데이터가 train에, 2026-02 데이터가 test에 섞임
# 미래 정보를 학습에 사용 → 오프라인 지표 부풀려짐
```

**After (temporal + group 조합 분할)**
```python
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

def production_split(df: pd.DataFrame, time_col: str,
                     group_col: str | None = None,
                     stratify_col: str | None = None) -> dict:
    """temporal + group/stratify 조합으로 운영 환경을 반영합니다."""
    # 1) 시간 기반 train/test 분할
    df = df.sort_values(time_col)
    cutoff = df[time_col].quantile(0.85)
    pre, post = df[df[time_col] < cutoff], df[df[time_col] >= cutoff]

    # 2) train 내부에서 group/stratify 기준으로 val 분리
    if group_col:
        from sklearn.model_selection import GroupShuffleSplit
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
        idx_tr, idx_val = next(splitter.split(pre, groups=pre[group_col]))
    elif stratify_col:
        from sklearn.model_selection import StratifiedShuffleSplit
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
        idx_tr, idx_val = next(splitter.split(pre, pre[stratify_col]))
    else:
        cut2 = pre[time_col].quantile(0.82)
        idx_tr = pre[time_col] < cut2
        idx_val = ~idx_tr
        return {"train": pre[idx_tr], "val": pre[idx_val], "test": post}

    return {"train": pre.iloc[idx_tr], "val": pre.iloc[idx_val], "test": post}
```

## 분할 전략 4가지

**1. Random split (베이스라인)**
```python
from sklearn.model_selection import train_test_split

train, temp = train_test_split(data, test_size=0.3, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)
# 결과: train 70%, val 15%, test 15%
# iid 가정이 맞을 때만 유효
```

**2. Stratified split (클래스 불균형)**
```python
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np

sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

# 검증: 클래스 비율이 유지됐는지 확인
print("train:", np.bincount(y_train) / len(y_train))
print("test :", np.bincount(y_test) / len(y_test))
```

**3. Group split (사용자 누수 방지)**
```python
from sklearn.model_selection import GroupShuffleSplit

groups = df["user_id"].values
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in gss.split(df, groups=groups):
    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

# 검증: 공유된 user_id가 없음을 확인
assert set(train_df["user_id"]) & set(test_df["user_id"]) == set()
```

**4. Temporal split (시계열)**
```python
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

df = df.sort_values("timestamp")
n = len(df)
train = df.iloc[: int(n * 0.7)]
val   = df.iloc[int(n * 0.7) : int(n * 0.85)]
test  = df.iloc[int(n * 0.85) :]

# 롤링 윈도우 백테스트
tscv = TimeSeriesSplit(n_splits=5, test_size=int(n * 0.1))
for fold, (tr, te) in enumerate(tscv.split(df)):
    print(f"fold {fold}: train={len(tr)}, test={len(te)}")
```

## Contamination 감지: 13-gram 방법

```python
def make_ngrams(text: str, n: int = 13) -> set[str]:
    tokens = text.split()
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def contamination_overlap(eval_doc: str, pretrain_chunks: list[str],
                          n: int = 13) -> float:
    """평가 문서와 사전학습 코퍼스 간 n-gram 중복률을 계산합니다."""
    eval_grams = make_ngrams(eval_doc, n)
    if not eval_grams:
        return 0.0
    matched = 0
    for chunk in pretrain_chunks:
        chunk_grams = make_ngrams(chunk, n)
        matched += len(eval_grams & chunk_grams)
        if matched >= len(eval_grams):
            break
    return matched / len(eval_grams)

# 13-gram 일치율이 80% 이상이면 오염 가능성이 높습니다
def canary_check(model_call, canary: str = "Th3_C@nary_X9z!") -> bool:
    """캐너리 문자열로 모델 암기 여부를 확인합니다."""
    rsp = model_call(f"Complete the string: {canary[:5]}")
    return canary in rsp  # True면 contamination 의심
```

## 분할 검증 자동화

```python
def validate_split(train_df, val_df, test_df, group_col=None) -> dict:
    """분할 결과의 무결성을 자동으로 검증합니다."""
    checks = {}
    checks["non_empty"] = (
        len(train_df) > 0 and len(val_df) > 0 and len(test_df) > 0
    )
    checks["disjoint_index"] = (
        set(train_df.index).isdisjoint(val_df.index) and
        set(train_df.index).isdisjoint(test_df.index) and
        set(val_df.index).isdisjoint(test_df.index)
    )
    if group_col:
        checks["group_disjoint"] = (
            set(train_df[group_col]).isdisjoint(val_df[group_col]) and
            set(train_df[group_col]).isdisjoint(test_df[group_col]) and
            set(val_df[group_col]).isdisjoint(test_df[group_col])
        )
    return checks
```

## 분할 결과 매니페스트

```python
from dataclasses import dataclass

@dataclass
class SplitManifest:
    dataset_version: str
    split_strategy: str
    train_rows: int
    val_rows: int
    test_rows: int
    time_cutoff: str
    group_column: str | None
    contamination_ratio_test: float
    overlap_removed_train_rows: int

# 이 매니페스트가 있어야 실험 결과를 비교할 때
# "모델 차이"와 "평가 조건 차이"를 분리할 수 있습니다
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------||
| 시계열 데이터에 random split | 미래 정보가 학습에 섞임 | temporal split으로 cutoff date 명시 |
| 사용자 데이터에 random split | 같은 사용자가 train/test 양쪽에 | group split으로 user_id 기준 분리 |
| test set을 튜닝에도 사용 | test는 더 이상 최종 측정이 아님 | validation으로 역할 분리 |
| contamination 검사 생략 | 점수가 높아도 해석 불가 | 13-gram overlap 검사 추가 |

## AI 팁

분할 전략은 문제 특성에 따라 조합합니다. 시간 축을 먼저 자르고, 그 안에서 group 또는 stratify를 추가하는 형태가 대부분의 프로덕션 문제를 커버합니다.

```python
# 실전 조합 예시
SPLIT_DAG = {
    "build_raw_snapshot": [],
    "split_temporal_group": ["build_raw_snapshot"],
    "cross_dedup_train_eval": ["split_temporal_group"],
    "ngram_contamination_scan": ["cross_dedup_train_eval"],
    "publish_split_manifest": ["ngram_contamination_scan"],
}
```

contamination 방어 전략 4가지를 순서대로 적용하세요:
1. Held-out only benchmark (학습 이후 공개된 평가셋만 신뢰)
2. Decontamination (eval n-gram과 겹치는 사전학습 문서 제거)
3. Canary string (고유 문자열로 암기 여부 검사)
4. Date cutoff (모델 학습 시점 이후 데이터만 평가)

## 체크리스트

- [ ] 문제 유형에 맞는 split 전략(random/stratified/group/temporal)을 선택했다
- [ ] 같은 user_id/session_id가 train/test 양쪽에 없는지 검증한다
- [ ] LLM 평가셋에 대해 13-gram contamination 검사를 실행한다
- [ ] test set은 하이퍼파라미터 튜닝과 분리했다
- [ ] SplitManifest로 분할 결과를 버전 관리한다

## 처음 질문으로 돌아가기

**random split이 운영에서 무너지는 이유는?** 시계열 데이터에서 미래 정보가 학습에 섞이거나, 사용자 데이터에서 같은 사람이 train/test 양쪽에 들어가 평가가 실제보다 쉬워집니다.

**클래스 불균형 시 분할 전략은?** StratifiedShuffleSplit으로 각 split에서 클래스 비율을 동일하게 유지합니다. 소수 클래스가 test에 거의 없으면 평가 질문 자체가 무너집니다.

**사용자 누수 방지 방법은?** GroupShuffleSplit에 user_id를 groups로 넘기면 같은 사용자가 train/test에 동시에 들어가지 않습니다. 분할 후 assert로 검증하세요.

**시계열에서 temporal split이 필수인 이유는?** random split은 미래 데이터를 학습에 섞어 모델이 이미 알고 있는 답을 맞추게 됩니다. 반드시 timestamp 기준으로 과거/미래를 잘라야 합니다.

**LLM contamination 감지 방법은?** 13-gram overlap으로 평가 문서와 사전학습 코퍼스 간 중복률을 계산합니다. 80% 이상이면 오염 가능성이 높으므로 제거합니다.

## 정리

좋은 분할은 데이터를 일정 비율로 나누는 것이 아니라, 실제 배포 환경을 반영한 평가 조건을 만드는 일입니다. 시간, 사용자 그룹, 클래스 비율에 따라 random, stratified, group, temporal을 다르게 적용해야 합니다.

다음 글에서는 이 모든 단계를 하나의 반복 가능한 **프로덕션 데이터 파이프라인**으로 묶는 방법을 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: 학습/평가/테스트 분할](../ko/09-train-eval-test-splitting.md)
- [GPT-3 13-gram contamination (Brown et al., 2020)](https://arxiv.org/abs/2005.14165)
- [scikit-learn Cross-validation Guide](https://scikit-learn.org/stable/modules/cross_validation.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. **바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할 (현재 글)**
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Train/Test Split, Contamination, Data Leakage, Stratification, Temporal Split, 바이브코딩
