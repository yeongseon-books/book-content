---
episode: 9

language: ko

last_reviewed: '2026-05-12'

series: ai-data-preparation-101

status: publish-ready

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

오프라인 실험이 늘 잘 보이는데 운영에 들어가면 성능이 무너지는 팀에는 공통 패턴이 있습니다. 데이터를 나누는 기준이 실제 배포 환경과 맞지 않거나, 평가셋이 이미 학습 코퍼스에 오염돼 있다는 점입니다.

특히 LLM 시대에는 contamination 문제가 더 커졌습니다. 모델이 이미 웹 전체를 학습했다면 benchmark 점수가 높은 이유가 일반화인지 암기인지 구분하기 어려워집니다. 단순 random split만으로는 이 문제를 전혀 막지 못합니다.

운영에서는 split이 단순한 utility 함수가 아닙니다. 시간, 사용자 그룹, 클래스 비율, benchmark 오염 여부까지 반영해 평가 질문 자체를 정의하는 단계입니다. 잘못 나누면 이후 모든 지표가 잘못된 질문에 답하게 됩니다.

시니어 엔지니어 관점에서 좋은 분할은 “편하게 나눴다”가 아니라 “실제 서빙 조건을 최대한 닮게 나눴다”로 평가해야 합니다.

이 글은 AI Data Preparation 101 시리즈의 9번째 글입니다.

여기서는 random, stratified, group, temporal split의 적용 기준과, LLM 평가에서 contamination을 어떻게 감지하고 방어할지 정리하겠습니다.

## 이 글에서 다룰 문제

- 단순 `train_test_split`이 실제 운영 조건을 놓치는 대표적인 경우는 무엇일까요?
- 클래스 불균형, 사용자 누수, 시계열 데이터는 왜 서로 다른 split 전략을 요구할까요?
- LLM benchmark contamination은 기존 데이터 누수와 무엇이 다르고 왜 더 위험할까요?
- 13-gram overlap은 contamination 감지에서 어떤 practical baseline 역할을 할까요?
- test set을 한 번만 써야 한다는 원칙을 실제 팀 프로세스로 어떻게 지킬 수 있을까요?

## 왜 이 글이 중요한가

분할 전략을 올바르게 선택하면 오프라인 지표가 실제 배포 성능과 더 가까워집니다. 특히 시간 기반 서비스나 사용자 단위 모델에서는 split 설계 하나만으로 실험 결과 해석이 완전히 달라질 수 있습니다.

반대로 무작위 분할에 익숙한 습관을 그대로 유지하면 미래 정보가 학습으로 새고, 같은 사용자가 train/test 양쪽에 섞이고, benchmark 문장이 pretraining corpus에 있었는지조차 모른 채 높은 점수만 보고 배포하게 됩니다.

이 글의 목적은 split을 데이터셋 마무리 작업이 아니라 평가 무결성을 정의하는 핵심 설계 단계로 명확히 자리 잡게 만드는 것입니다.

## 분할 전략을 이해하는 가장 좋은 방법: 데이터 특징에 맞는 평가 시뮬레이터를 고르는 것입니다

분할은 단순히 80/10/10 비율을 만드는 문제가 아닙니다. 어떤 미래를 예측하는 모델인지, 같은 사용자가 여러 샘플을 갖는지, 소수 클래스가 얼마나 작은지에 따라 적합한 split이 달라집니다.

LLM 평가에서는 여기서 한 단계 더 나아갑니다. benchmark 자체가 pretraining corpus에 있었는지 확인해야 하므로, contamination detection과 decontamination 전략이 split 설계의 일부가 됩니다.

좋은 split은 실험을 더 어렵게 만들 수도 있습니다. 하지만 그 어려움이 실제 운영 난이도에 가깝다면, 그 지표가 훨씬 더 쓸모 있습니다.

> split의 목표는 데이터를 예쁘게 나누는 것이 아니라, 실제 배포 환경을 최대한 정직하게 흉내 내는 평가 조건을 만드는 것입니다.

## 핵심 개념

### Split 전략은 데이터 특성에 따라 바뀝니다

#### 1. Random split

```python
from sklearn.model_selection import train_test_split

train, temp = train_test_split(data, test_size=0.3, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)
# Result: 70% train, 15% val, 15% test
```

iid 가정이 맞을 때만 유효합니다. 시계열, 사용자 반복 샘플, 심한 class imbalance가 있으면 baseline 이상으로 쓰기 어렵습니다.

#### 2. Stratified split

```python
from sklearn.model_selection import StratifiedShuffleSplit

X, y = features, labels
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in sss.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

# Verify
import numpy as np
print("train:", np.bincount(y_train) / len(y_train))
print("test :", np.bincount(y_test) / len(y_test))
```

소수 클래스가 작을수록 stratified split은 사실상 필수입니다. 테스트셋에 해당 클래스가 거의 없으면 모델 품질을 재는 질문 자체가 무너집니다.

#### 3. Group split

```python
from sklearn.model_selection import GroupShuffleSplit

groups = df["user_id"].values
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in gss.split(df, groups=groups):
    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

# Verify: no shared user_id
assert set(train_df["user_id"]) & set(test_df["user_id"]) == set()
```

추천 시스템, fraud detection, 의료 데이터처럼 사용자·세션·환자 단위 누수가 중요한 문제에서는 반드시 그룹 기반 분할을 써야 합니다.

#### 4. Temporal split

```python
import pandas as pd

df = df.sort_values("timestamp")
n = len(df)
train = df.iloc[: int(n * 0.7)]
val   = df.iloc[int(n * 0.7) : int(n * 0.85)]
test  = df.iloc[int(n * 0.85) :]

# Rolling-window backtest (optional)
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5, test_size=int(n * 0.1))
for fold, (tr, te) in enumerate(tscv.split(df)):
    print(f"fold {fold}: train={len(tr)}, test={len(te)}")
```

뉴스, 수요 예측, churn 같은 문제는 거의 항상 temporal split이 맞습니다. random split은 미래 정보를 학습에 섞어 버리기 때문입니다.

### contamination은 LLM 평가의 가장 큰 함정입니다

benchmark 문장이 pretraining corpus에 이미 있었다면, 높은 점수가 일반화 성능인지 암기 성능인지 분리하기 어렵습니다. 가장 단순한 practical baseline은 n-gram overlap입니다.

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

# 13-gram match >= 80% suggests contamination
```

GPT-3와 PaLM 계열 논문도 13-gram 기준을 많이 씁니다. 너무 짧은 n은 false positive가 많고, 너무 긴 n은 패러프레이즈 contamination을 놓칩니다.

### contamination 방어 전략은 네 가지로 정리할 수 있습니다

1. **Held-out only benchmark**: 모델 학습 이후에 공개된 평가셋만 신뢰합니다.

2. **Decontamination**: eval n-gram과 겹치는 pretraining 문서를 제거합니다.

3. **Canary string**: 고유 문자열을 넣어 암기 여부를 검사합니다.

4. **Date cutoff**: 모델 학습 시점 이후에 만들어진 데이터만 평가합니다.

간단한 canary 검사는 아래처럼 넣을 수 있습니다.

```python
# Canary detection (simple)
def canary_check(model_call, canary: str = "Th3_C@nary_X9z!") -> bool:
    rsp = model_call(f"Complete the string: {canary[:5]}")
    return canary in rsp  # True means suspected contamination
```

### 실전에서는 temporal + group/stratify 조합이 많습니다

많은 프로덕션 문제는 시간 축을 먼저 자르고, 그 안에서 group 또는 stratify를 추가하는 형태로 해결됩니다.

```python
def production_split(df: pd.DataFrame, time_col: str, group_col: str | None = None,
                     stratify_col: str | None = None) -> dict:
    # 1) Time-based train/test split (mirrors production)
    df = df.sort_values(time_col)
    cutoff = df[time_col].quantile(0.85)
    pre, post = df[df[time_col] < cutoff], df[df[time_col] >= cutoff]
    # 2) Within train, separate val by group/stratify
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

이 함수가 좋은 이유는 거의 모든 실전 상황을 포괄하기 때문입니다. 먼저 미래 데이터를 test로 떼고, 과거 구간 안에서 사용자 누수나 클래스 불균형을 추가로 다룹니다.

## 흔히 헷갈리는 지점

- **random split이면 대부분 충분합니다**: 시간, 사용자, 클래스 구조를 무시하면 운영과 전혀 다른 쉬운 평가 문제가 됩니다.
- **LLM benchmark contamination은 피할 수 없으니 신경 쓸 필요가 없습니다**: 완벽히 제거하지 못해도 overlap 측정과 held-out 전략으로 위험을 크게 줄일 수 있습니다.
- **test set도 튜닝 과정에서 조금씩 봐도 됩니다**: 그 순간 test는 더 이상 최종 측정이 아닙니다. validation과 역할을 분리해야 합니다.
- **group split과 stratified split 중 하나만 항상 정답입니다**: 문제 특성에 따라 temporal + group, temporal + stratify처럼 조합하는 경우가 더 많습니다.

## 운영 체크리스트

- [ ] 문제 유형별로 random/stratified/group/temporal 중 어떤 split을 쓰는지 근거를 남겼다
- [ ] 같은 user_id·session_id·patient_id가 train/test 양쪽에 없는지 검증한다
- [ ] LLM 평가셋에 대해 13-gram overlap 또는 동급 contamination 검사를 실행한다
- [ ] test set은 하이퍼파라미터 튜닝과 분리하고 접근 절차를 명시했다
- [ ] temporal split이 필요한 문제에서 cutoff date와 backtest 방식까지 문서화했다

## 정리

좋은 split은 데이터를 일정 비율로 나누는 것이 아니라, 실제 배포 환경을 반영한 평가 조건을 만드는 일입니다. 그래서 데이터 특성에 따라 random, stratified, group, temporal을 다르게 써야 합니다.

LLM 시대에는 contamination 통제가 여기에 추가됩니다. benchmark가 pretraining corpus에 있었는지 확인하지 않으면 높은 점수도 해석이 어렵습니다. 13-gram overlap 같은 practical baseline이 중요한 이유입니다.

다음 글에서는 이 모든 단계를 하나의 반복 가능하고 관측 가능한 프로덕션 데이터 파이프라인으로 묶는 방법을 다룹니다. 결국 split과 contamination 통제도 자동화된 파이프라인 안에 들어가야 운영이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- **학습/평가/테스트 분할과 Contamination 통제 (현재 글)**
- [프로덕션 데이터 파이프라인 구축](./10-production-data-pipeline.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Language Models are Few-Shot Learners (GPT-3, Brown et al., 2020) - 13-gram contamination](https://arxiv.org/abs/2005.14165)
- [Investigating Data Contamination in Modern Benchmarks (Yang et al., 2024)](https://arxiv.org/abs/2311.09783)
- [scikit-learn Cross-validation Guide](https://scikit-learn.org/stable/modules/cross_validation.html)
- [Hidden Stratification and Spurious Correlations in ML (Oakden-Rayner et al., 2020)](https://arxiv.org/abs/1909.12475)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

Tags: Train/Test Split, Contamination, Data Leakage, Stratification, Temporal Split, scikit-learn
