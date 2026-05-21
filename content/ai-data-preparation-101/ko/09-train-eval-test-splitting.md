---
episode: 9
language: ko
last_reviewed: '2026-05-12'
seo_description: 단순 random split이 운영에서 무너지는 이유와, contamination을 막는 시간/사용자 단위 분할 전략을
  정리합니다.
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
  medium: false
  mkdocs: true
  tistory: true
title: "AI Data Preparation 101 (9/10): 학습/평가/테스트 분할과 Contamination 통제"
---

# AI Data Preparation 101 (9/10): 학습/평가/테스트 분할과 Contamination 통제

오프라인 실험이 늘 잘 보이는데 운영에 들어가면 성능이 무너지는 팀에는 공통 패턴이 있습니다. 데이터를 나누는 기준이 실제 배포 환경과 맞지 않거나, 평가셋이 이미 학습 코퍼스에 오염돼 있다는 점입니다.

특히 LLM 시대에는 contamination 문제가 더 커졌습니다. 모델이 이미 웹 전체를 학습했다면 benchmark 점수가 높은 이유가 일반화인지 암기인지 구분하기 어려워집니다. 단순 random split만으로는 이 문제를 전혀 막지 못합니다.

운영에서는 split이 단순한 utility 함수가 아닙니다. 시간, 사용자 그룹, 클래스 비율, benchmark 오염 여부까지 반영해 평가 질문 자체를 정의하는 단계입니다. 잘못 나누면 이후 모든 지표가 잘못된 질문에 답하게 됩니다.

시니어 엔지니어 관점에서 좋은 분할은 “편하게 나눴다”가 아니라 “실제 서빙 조건을 최대한 닮게 나눴다”로 평가해야 합니다.

이 글은 AI Data Preparation 101 시리즈의 9번째 글입니다.

여기서는 random, stratified, group, temporal split의 적용 기준과, LLM 평가에서 contamination을 어떻게 감지하고 방어할지 정리하겠습니다.


![AI 데이터 준비 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/09/09-01-big-picture.ko.png)
*AI 데이터 준비 9장 흐름 개요*
> 학습/평가/테스트 분할과 Contamination 통제의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 단순 `train_test_split`이 실제 운영 조건을 놓치는 대표적인 경우는 무엇일까요?
- 클래스 불균형, 사용자 누수, 시계열 데이터는 왜 서로 다른 split 전략을 요구할까요?
- LLM benchmark contamination은 기존 데이터 누수와 무엇이 다르고 왜 더 위험할까요?

## 왜 이 글이 중요한가

분할 전략을 올바르게 선택하면 오프라인 지표가 실제 배포 성능과 더 가까워집니다. 특히 시간 기반 서비스나 사용자 단위 모델에서는 split 설계 하나만으로 실험 결과 해석이 완전히 달라질 수 있습니다.

반대로 무작위 분할에 익숙한 습관을 그대로 유지하면 미래 정보가 학습으로 새고, 같은 사용자가 train/test 양쪽에 섞이고, benchmark 문장이 pretraining corpus에 있었는지조차 모른 채 높은 점수만 보고 배포하게 됩니다.

이 글의 목적은 split을 데이터셋 마무리 작업이 아니라 평가 무결성을 정의하는 핵심 설계 단계로 명확히 자리 잡게 만드는 것입니다.

## 핵심 관점

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
# 결과: train 70%, val 15%, test 15%
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

# 검증: 공유된 user_id가 없음
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

# 롤링 윈도우 백테스트 (선택)
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

# 13-gram 일치율이 80% 이상이면 오염 가능성이 높습니다.
```

GPT-3와 PaLM 계열 논문도 13-gram 기준을 많이 씁니다. 너무 짧은 n은 false positive가 많고, 너무 긴 n은 패러프레이즈 contamination을 놓칩니다.

### contamination 방어 전략은 네 가지로 정리할 수 있습니다

1. **Held-out only benchmark**: 모델 학습 이후에 공개된 평가셋만 신뢰합니다.

2. **Decontamination**: eval n-gram과 겹치는 pretraining 문서를 제거합니다.

3. **Canary string**: 고유 문자열을 넣어 암기 여부를 검사합니다.

4. **Date cutoff**: 모델 학습 시점 이후에 만들어진 데이터만 평가합니다.

간단한 canary 검사는 아래처럼 넣을 수 있습니다.

```python
# Canary 탐지 (단순 버전)
def canary_check(model_call, canary: str = "Th3_C@nary_X9z!") -> bool:
    rsp = model_call(f"Complete the string: {canary[:5]}")
    return canary in rsp  # True means suspected contamination
```

### 실전에서는 temporal + group/stratify 조합이 많습니다

많은 프로덕션 문제는 시간 축을 먼저 자르고, 그 안에서 group 또는 stratify를 추가하는 형태로 해결됩니다.

```python
def production_split(df: pd.DataFrame, time_col: str, group_col: str | None = None,
                     stratify_col: str | None = None) -> dict:
    # 1) 시간 기반 train/test 분할 (운영 환경을 반영)
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

이 함수가 좋은 이유는 거의 모든 실전 상황을 포괄하기 때문입니다. 먼저 미래 데이터를 test로 떼고, 과거 구간 안에서 사용자 누수나 클래스 불균형을 추가로 다룹니다.

## contamination 검사를 배치 파이프라인으로 내장하기

분할 전략이 아무리 좋아도 contamination 검사를 수동으로 돌리면 운영에서 빠지기 쉽습니다. 따라서 split 단계 바로 뒤에 decontamination 단계를 DAG로 강제하는 편이 안전합니다.

```python
SPLIT_DAG = {
    "build_raw_snapshot": [],
    "split_temporal_group": ["build_raw_snapshot"],
    "cross_dedup_train_eval": ["split_temporal_group"],
    "ngram_contamination_scan": ["cross_dedup_train_eval"],
    "publish_split_manifest": ["ngram_contamination_scan"],
}
```

## 분할 결과 매니페스트 예시

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

manifest = SplitManifest(
    dataset_version="v2.3.0",
    split_strategy="temporal+group",
    train_rows=420_000,
    val_rows=72_000,
    test_rows=88_000,
    time_cutoff="2026-03-01",
    group_column="user_id",
    contamination_ratio_test=0.006,
    overlap_removed_train_rows=5142,
)
```

이 매니페스트가 있어야 실험 결과를 비교할 때 “모델 차이”와 “평가 조건 차이”를 분리할 수 있습니다.

## contamination 샘플 리포트

```python
def collect_contamination_examples(eval_docs, pretrain_docs, overlap_fn, top_k=20):
    rows = []
    for e in eval_docs:
        score, matched = overlap_fn(e, pretrain_docs)
        if score > 0.5:
            rows.append({"eval": e[:160], "score": score, "matched": matched[:160]})
    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows[:top_k]
```

숫자만으로는 현상을 오해하기 쉽습니다. 상위 오염 샘플 몇 건을 사람이 직접 확인하면 threshold 조정이 훨씬 정확해집니다.

## 적용 전후 분할 샘플

```text
[잘못된 분할]
train: 2026-04 데이터 포함
test : 2026-03 데이터 포함

[개선된 분할]
train: <= 2026-02
val  : 2026-02 일부
test : >= 2026-03
```

이처럼 시간 축을 정직하게 맞추면 오프라인 점수는 낮아질 수 있지만, 배포 후 성능과의 괴리는 줄어듭니다.

## DVC stage로 split 재현성 확보

```yaml
stages:
  split_dataset:
    cmd: python pipelines/split_dataset.py --strategy temporal_group --time-col timestamp --group-col user_id
    deps:
      - pipelines/split_dataset.py
      - data/quality/train_filtered.parquet
    outs:
      - data/splits/train.parquet
      - data/splits/val.parquet
      - data/splits/test.parquet
    metrics:
      - reports/split_manifest.json
      - reports/contamination_report.json
```

분할은 실험 전처리가 아니라 평가 계약입니다. 계약을 코드와 버전으로 남겨야 이후 모델 개선도 신뢰할 수 있습니다.

## split 검증 자동화

좋은 전략을 선택해도 검증을 자동화하지 않으면 쉽게 무너집니다. split 생성 직후 아래 검사를 모두 통과해야 다음 단계로 넘기는 것이 안전합니다.

```python
def validate_split(train_df, val_df, test_df, group_col=None):
    checks = {}
    checks["non_empty"] = len(train_df) > 0 and len(val_df) > 0 and len(test_df) > 0
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

## 클래스 분포 안정성 점검

```python
def class_ratio(df, label_col):
    vc = df[label_col].value_counts(normalize=True)
    return {k: float(v) for k, v in vc.items()}

def max_ratio_delta(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    return max(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)
```

train/val/test 간 최대 분포 차이가 과도하면 분할 기준을 다시 잡아야 합니다. 특히 소수 클래스에서는 1~2% 차이도 실제 운영 지표에 크게 반영될 수 있습니다.

## contamination 대응 단계

1. `ngram overlap > threshold` 샘플을 추출합니다.
2. 사람이 상위 샘플을 검토해 false positive를 제거합니다.
3. 확정된 오염 샘플은 train에서 제거하고 report에 기록합니다.
4. 제거 전/후 성능을 같이 보고 평가 신뢰도 변화를 확인합니다.

이 루프를 자동화하면 “점수는 높은데 믿을 수 없는 평가” 상태를 훨씬 줄일 수 있습니다.

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

### 테스트셋 접근 제어

테스트셋은 배포 직전 검증에만 사용하고, 실험 반복 단계에서는 접근을 제한하는 편이 좋습니다. 저장소 권한과 CI job 분리로 접근 경로를 명시하면 무의식적인 test overfitting을 크게 줄일 수 있습니다.

### 릴리스 노트에 남겨야 할 최소 항목

해당 단계의 변경은 릴리스 노트에도 남겨야 합니다. 최소한 `변경 규칙`, `영향받은 행 수`, `핵심 지표 변화`, `롤백 경로` 네 항목이 있어야 다음 배치에서 같은 판단을 반복할 수 있습니다.

분할 규칙 변경은 항상 독립 실험으로 기록해 모델 변경 효과와 분리해 해석해야 합니다.

시간 기준 분할에서는 서비스 이벤트(프로모션, 장애 공지) 전후 구간을 별도 슬라이스로 점검하면 평가 신뢰도가 더 높아집니다.

또한 split manifest를 실험 로그와 같이 보관해, 모델 점수 변화가 데이터 경계 변경 때문인지 모델 개선 때문인지 명확히 구분해야 합니다. 이 절차가 없으면 팀 내 성능 해석이 자주 충돌합니다.

평가셋 접근 로그를 남기면 무의식적 누수를 사후에라도 추적할 수 있습니다.

분할 결과는 리뷰 승인 후 고정해야 합니다.

검증 로그의 보존 기간도 미리 정하는 것이 좋습니다.

자동 점검을 권장합니다.

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

## 처음 질문으로 돌아가기

- **단순 `train_test_split`이 실제 운영 조건을 놓치는 대표적인 경우는 무엇일까요?**
  - 본문의 기준은 학습/평가/테스트 분할과 Contamination 통제를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **클래스 불균형, 사용자 누수, 시계열 데이터는 왜 서로 다른 split 전략을 요구할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **LLM benchmark contamination은 기존 데이터 누수와 무엇이 다르고 왜 더 위험할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [AI Data Preparation 101 (7/10): 합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [AI Data Preparation 101 (8/10): 데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- **학습/평가/테스트 분할과 Contamination 통제 (현재 글)**
- 프로덕션 데이터 파이프라인 구축 (예정)

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/09-train-eval-test-splitting)

Tags: Train/Test Split, Contamination, Data Leakage, Stratification, Temporal Split, scikit-learn
