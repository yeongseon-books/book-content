---
episode: 9
language: ko
last_reviewed: '2026-05-03'
series: ai-data-preparation-101
status: content-ready
tags:
- Train/Test Split
- Contamination
- Data Leakage
- Stratification
- Temporal Split
- scikit-learn
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: true
title: 학습/평가/테스트 분할과 Contamination 통제
seo_description: train_test_split(data, test_size=0.2)로 끝낸 모델이 production에서 무너지는 패턴은
  매년 반복됩니다.
---

# 학습/평가/테스트 분할과 Contamination 통제

> AI Data Preparation 101 시리즈 (9/10)

---
## "그냥 random_split 쓰면 되는 거 아닌가요?"

`train_test_split(data, test_size=0.2)`로 끝낸 모델이 production에서 무너지는 패턴은 매년 반복됩니다. 이유는 두 가지입니다.

1. **분포 불일치**: random split은 시간 순서나 user 단위 grouping을 무시합니다. validation 점수가 production 점수와 다릅니다.
2. **Contamination**: pretraining corpus가 evaluation benchmark를 이미 본 적이 있으면 점수가 부풀려집니다. 이건 LLM 시대의 가장 큰 평가 문제입니다.

이번 편은 split 전략 4가지와 contamination 탐지/방어를 다룹니다.

## Split 전략 1 — Random split (baseline)

가장 단순. iid 가정이 성립하는 경우에만 valid.

```python
from sklearn.model_selection import train_test_split

train, temp = train_test_split(data, test_size=0.3, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)
# 결과: 70% train, 15% val, 15% test
```

**언제 쓰면 안 되나**:

- 시간이 변수인 데이터 (news, 가격 예측, churn)
- 같은 user/session에서 여러 sample이 나오는 경우
- class imbalance가 심한 경우 (StratifiedShuffleSplit으로 대체)

## Split 전략 2 — Stratified split (class imbalance)

label 분포를 train/val/test에서 동일하게 유지합니다.

```python
from sklearn.model_selection import StratifiedShuffleSplit

X, y = features, labels
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

# 검증
import numpy as np
print("train:", np.bincount(y_train) / len(y_train))
print("test :", np.bincount(y_test) / len(y_test))
```

minority class가 5% 미만이면 random split에서 test set에 0개가 들어갈 수 있습니다. stratified는 이걸 방지합니다.

## Split 전략 3 — Group split (user/session leakage 방지)

같은 user의 sample이 train과 test에 동시에 들어가면 model이 user identity로 답을 맞추는 leak이 발생합니다.

```python
from sklearn.model_selection import GroupShuffleSplit

groups = df["user_id"].values
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in gss.split(df, groups=groups):
    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

# 검증: 두 set에 같은 user_id가 없어야 함
assert set(train_df["user_id"]) & set(test_df["user_id"]) == set()
```

추천 시스템, fraud detection, 의료 patient 단위 평가에서 필수입니다.

## Split 전략 4 — Temporal split (시간 leakage 방지)

미래 데이터로 과거를 예측하는 leakage를 막습니다. production deployment와 가장 가까운 평가 방식입니다.

```python
import pandas as pd

df = df.sort_values("timestamp")
n = len(df)
train = df.iloc[: int(n * 0.7)]
val   = df.iloc[int(n * 0.7) : int(n * 0.85)]
test  = df.iloc[int(n * 0.85) :]

# rolling-window backtest (선택)
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5, test_size=int(n * 0.1))
for fold, (tr, te) in enumerate(tscv.split(df)):
    print(f"fold {fold}: train={len(tr)}, test={len(te)}")
```

뉴스 분류, 추천, demand forecasting, churn 모델은 거의 전부 temporal split를 써야 합니다. random split는 미래 정보를 train에 누설합니다.

## Contamination — LLM eval의 가장 큰 함정

GPT-4 같은 거대 모델은 web 전체를 학습했습니다. MMLU, HumanEval, GSM8K 같은 benchmark text가 pretraining corpus에 포함될 가능성이 높습니다. 점수는 높게 나오지만 generalization 점수가 아닙니다.

탐지 방법은 substring overlap이 가장 단순합니다.

```python
import hashlib

def make_ngrams(text: str, n: int = 13) -> set[str]:
    tokens = text.split()
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def contamination_overlap(eval_doc: str, pretrain_chunks: list[str], n: int = 13) -> float:
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

# 13-gram 매치가 80% 이상이면 contamination 의심
```

GPT-3 paper, PaLM paper 모두 13-gram 기준을 씁니다. n을 너무 크게 잡으면 paraphrase된 contamination을 놓치고, 너무 작게 잡으면 false positive가 폭발합니다.

production 규모에서는 MinHash + LSH로 가속합니다 (Episode 3 참고).

## Contamination 방어 — 4가지 전략

1. **Held-out only benchmark**: model 학습 후 처음 공개되는 eval set만 신뢰
2. **Decontamination**: pretraining corpus에서 eval n-gram match를 가진 문서를 제거
3. **Canary string**: eval set에 unique한 string을 심어 model이 외운 적 있는지 detect
4. **Date-cutoff**: model 학습 cutoff 이후의 데이터로만 평가

```python
# Canary detection (간단)
def canary_check(model_call, canary: str = "Th3_C@nary_X9z!") -> bool:
    rsp = model_call(f"Complete the string: {canary[:5]}")
    return canary in rsp  # True면 contamination 의심
```

## 실전 split workflow

```python
def production_split(df: pd.DataFrame, time_col: str, group_col: str | None = None,
                     stratify_col: str | None = None) -> dict:
    # 1) 시간 기반 train/test 분리 (production 패턴 모사)
    df = df.sort_values(time_col)
    cutoff = df[time_col].quantile(0.85)
    pre, post = df[df[time_col] < cutoff], df[df[time_col] >= cutoff]
    # 2) train 내부에서 val을 group/stratify로 분리
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

이 함수가 거의 모든 production case를 커버합니다.

## 흔한 실수 5가지

1. **시계열 데이터에 random split**: 미래가 train에 누설되어 validation 점수가 부풀려집니다.
2. **User leakage 무시**: 같은 user의 sample이 train/test에 동시 등장하면 model은 user identity로 cheat합니다.
3. **Contamination 검증 생략**: LLM 평가에서 13-gram overlap을 측정하지 않으면 점수의 신뢰성이 없습니다.
4. **Test set을 hyperparameter tuning에 사용**: test는 단 한 번만 보아야 합니다. tuning은 validation으로.
5. **Stratify를 multi-label에 단순 적용**: multi-label에는 `iterstrat.MultilabelStratifiedShuffleSplit`을 씁니다.

## 핵심 요약

- Split 전략은 데이터 특성에 맞게 선택합니다: random / stratified / group / temporal.
- 시간 변수 데이터는 거의 전부 temporal split를 써야 합니다.
- 같은 user의 sample이 train/test에 섞이지 않도록 group split을 적용합니다.
- LLM 평가는 13-gram contamination overlap을 측정합니다.
- 방어 전략: held-out, decontamination, canary, date-cutoff.
- Test set은 final 측정 1회용입니다.
- 다음 편(10편)은 production data pipeline 구축입니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- **학습/평가/테스트 분할과 Contamination 통제 (현재 글)**
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Language Models are Few-Shot Learners (GPT-3, Brown et al., 2020) - 13-gram contamination](https://arxiv.org/abs/2005.14165)
- [Investigating Data Contamination in Modern Benchmarks (Yang et al., 2024)](https://arxiv.org/abs/2311.09783)
- [scikit-learn Cross-validation Guide](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Hidden Stratification and Spurious Correlations in ML (Oakden-Rayner et al., 2020)](https://arxiv.org/abs/1909.12475)

Tags: Train/Test Split, Contamination, Data Leakage, Stratification, Temporal Split, scikit-learn
