---
series: model-evaluation-101
episode: 10
title: 평가 리포트 만들기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - ModelEvaluation
  - Reporting
  - ModelCard
  - Reproducibility
  - scikit-learn
seo_description: 데이터·지표·임계값·슬라이스·재현성을 포함하는 모델 평가 리포트 템플릿을 코드와 함께 정리한 글
last_reviewed: '2026-05-04'
---

# 평가 리포트 만들기

> Model Evaluation 101 시리즈 (10/10)


## 이 글에서 다룰 문제

*리뷰* 와 *감사* 그리고 *사고 후 분석* 모두 *동일 리포트* 를 본다. *형식이 일정* 해야 *팀 속도* 가 빨라집니다.

## 전체 흐름
```mermaid
flowchart LR
    Data["data section"] --> Report
    Metric["metrics + threshold"] --> Report
    Slice["slice scores"] --> Report
    Repro["reproducibility"] --> Report
    Risk["known risks"] --> Report
```

## Before/After

**Before**: *Slack 메시지 한 줄로 “acc 0.92 ship”*.

**After**: *5개 섹션의 정형 리포트 + 자동 생성*.

## 5단계 리포트

### 1단계 — 메트릭 모으기

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score, brier_score_loss
X, y = make_classification(n_samples=3000, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
proba = m.predict_proba(Xte)[:, 1]
pred = (proba >= 0.5).astype(int)
metrics = {
    "f1_macro": f1_score(yte, pred, average="macro"),
    "auc_roc": roc_auc_score(yte, proba),
    "brier": brier_score_loss(yte, proba),
}
```

### 2단계 — 슬라이스 점수

```python
slice_mask = Xte[:, 0] > 0
slices = {
    "slice_pos": f1_score(yte[slice_mask], pred[slice_mask]),
    "slice_neg": f1_score(yte[~slice_mask], pred[~slice_mask]),
}
```

### 3단계 — 메타데이터

```python
import hashlib, sys, sklearn
meta = {
    "python": sys.version.split()[0],
    "sklearn": sklearn.__version__,
    "data_hash": hashlib.sha1(X.tobytes()).hexdigest()[:10],
    "threshold": 0.5,
}
```

### 4단계 — 리포트 직렬화

```python
import json
report = {"metrics": metrics, "slices": slices, "meta": meta,
          "risks": ["minor calibration drift", "slice_neg lower F1"]}
print(json.dumps(report, indent=2))
```

### 5단계 — 마크다운으로 변환

```python
def to_md(rep):
    lines = ["# Evaluation Report", "## Metrics"]
    for k, v in rep["metrics"].items():
        lines.append(f"- {k}: {round(v, 3)}")
    lines.append("## Slices")
    for k, v in rep["slices"].items():
        lines.append(f"- {k}: {round(v, 3)}")
    lines.append("## Meta")
    for k, v in rep["meta"].items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)

print(to_md(report))
```

## 이 코드에서 주목할 점

- *JSON 1차* → *MD 2차* 변환 패턴.
- *데이터 해시* 가 *재현성* 의 핵심.
- *임계값* 명시가 *해석 차이* 를 막는다.

## 자주 하는 실수 5가지

1. ***임계값* 을 *기록* 하지 않음.**
2. ***슬라이스 점수* 를 *생략*.**
3. ***버전 정보* 누락.**
4. ***리스크* 섹션을 *비워둠*.**
5. ***수기 작성* 만 의존 → *재현 불가*.**

## 실무에서는 이렇게 쓰입니다

*ML 출시 게이트* 와 *모니터링 알람* 의 *기준 문서* 로 *평가 리포트* 가 사용됩니다.

## 체크리스트

- [ ] *지표 + 임계값* 명시.
- [ ] *슬라이스 점수* 포함.
- [ ] *버전/해시* 메타데이터.
- [ ] *알려진 리스크* 명시.

## 정리 및 다음 단계

10편을 통해 *평가의 어휘* 와 *현실적 함정* 을 정리했습니다. *MLOps* 와 *Error Analysis* 를 더 깊이 다루는 시리즈로 자연스럽게 이어집니다.

<!-- toc:begin -->
- [모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [train/validation/test](./02-train-val-test.md)
- [Accuracy의 한계](./03-limits-of-accuracy.md)
- [Precision과 Recall](./04-precision-and-recall.md)
- [F1 Score](./05-f1-score.md)
- [ROC와 AUC](./06-roc-and-auc.md)
- [Calibration](./07-calibration.md)
- [Cross Validation](./08-cross-validation.md)
- [Error Analysis](./09-error-analysis.md)
- **평가 리포트 만들기 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Google — Model Cards](https://modelcards.withgoogle.com/about)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [MLOps — Production ML guide](https://ml-ops.org/)

Tags: ModelEvaluation, Reporting, ModelCard, Reproducibility, scikit-learn
