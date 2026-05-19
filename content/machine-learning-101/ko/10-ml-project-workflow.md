---
series: machine-learning-101
episode: 10
title: ML 프로젝트 전체 흐름
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - MachineLearning
  - MLWorkflow
  - Pipeline
  - MLOps
  - Beginner
seo_description: 문제 정의부터 데이터, 모델, 배포, 모니터링까지 ML 프로젝트 전체 워크플로를 정리합니다
last_reviewed: '2026-05-15'
---

# ML 프로젝트 전체 흐름

노트북에서 정확도가 높게 나왔는데도 실제 사용자에게 닿지 못하는 ML 프로젝트는 아주 많습니다. 이유는 대개 모델 점수가 아니라 그 앞뒤에 있습니다. 문제 정의가 약하거나, 데이터가 재현되지 않거나, 전처리가 흩어져 있거나, 배포 후 모니터링이 비어 있으면 좋은 모델도 곧 멈춥니다. ML의 성공은 점수 하나보다 전체 루프를 완성하는 데 달려 있습니다.

이 글은 Machine Learning 101 시리즈의 마지막 글입니다. 여기서는 문제 정의부터 데이터, 피처, 모델, 평가, 배포, 모니터링까지 이어지는 7단계 워크플로를 정리하고, `Pipeline`이 왜 유지보수성과 재현성의 중심인지 살펴보겠습니다.

## 이 글에서 다룰 문제

- 정확도가 높아도 왜 많은 ML 프로젝트는 배포에 실패할까요?
- 문제 정의, 데이터, 모델, 배포, 모니터링을 왜 하나의 루프로 봐야 할까요?
- `Pipeline`은 왜 전처리 누수를 막는 핵심 도구일까요?
- 재현성과 모델 카드가 왜 중요할까요?
- 배포 후 모니터링은 왜 끝이 아니라 시작일까요?

> ML의 성공은 점수 극대화만으로 오지 않습니다. **문제 정의부터 모니터링까지의 루프를 완주하는 것**이 실제 성공입니다.

## 왜 중요한가

노트북에서 0.95 점수를 얻어도 모델이 사용자에게 도달하지 못하면 그 값은 0과 다르지 않습니다. 전체 루프를 소유해야 실제 영향이 생깁니다.

## 한눈에 보는 개념

![한눈에 보는 개념](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/10/10-01-diagram.ko.png)

*문제 정의에서 시작한 ML 프로젝트는 데이터, 모델, 배포, 모니터링을 거쳐 다시 문제 정의로 돌아오는 루프로 운영됩니다.*

## 핵심 용어

- **Pipeline**: 전처리와 모델을 하나로 묶은 객체입니다.
- 재현성: 시드, 버전, 데이터 스냅샷이 고정된 상태입니다.
- **Model Card**: 모델 메타데이터를 정리한 공식 문서입니다.
- **Drift**: 입력 또는 타깃 분포의 변화입니다.
- **Shadow deploy**: 실제로는 행동하지 않고 예측만 기록하는 배포 방식입니다.

## Before/After

**Before**: "모델 학습하고 점수 찍었으니 끝"이라고 생각합니다.

**After**: 문제, 데이터, 모델, 평가, 배포, 모니터링이 순환하는 루프로 봅니다.

## 실습: 5단계 미니 워크플로

### Step 1 — 문제와 데이터

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Step 2 — Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=2000)),
])
```

### Step 3 — 학습과 평가

```python
pipe.fit(Xtr, ytr)
print("test:", pipe.score(Xte, yte))
```

### Step 4 — 저장(재현성)

```python
import joblib
joblib.dump(pipe, "model.joblib")
loaded = joblib.load("model.joblib")
print("loaded:", loaded.score(Xte, yte))
```

### Step 5 — 모니터링 시뮬레이션

```python
import numpy as np
fresh = Xte + np.random.normal(0, 0.1, Xte.shape)
print("drifted:", loaded.score(fresh, yte))
```

**예상 출력:** 저장한 파이프라인은 다시 불러와도 같은 테스트 점수를 내야 하고, 입력에 노이즈를 넣은 `fresh` 점수는 대체로 더 낮게 나옵니다. 이 차이는 모델 파일을 보관하는 것만으로는 충분하지 않고 **입력 분포 변화**까지 지켜봐야 한다는 사실을 보여 줍니다.

## 이 코드에서 먼저 봐야 할 점

- `Pipeline`은 전처리 누수를 근본에서 막아 줍니다.
- `joblib`는 재현 가능한 배포를 가능하게 합니다.
- 작은 입력 노이즈만으로도 점수가 떨어질 수 있어 drift를 바로 체감하게 합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 배포 직후 성능이 떨어지면, 모델 가중치보다 먼저 **학습 때와 실제 전처리 경로가 같은지** 확인해야 합니다.
- 깨끗한 환경에서 결과를 재현하지 못하면, 노트북 데모가 좋아 보여도 **워크플로 자체가 아직 불완전**합니다.
- 모니터링이 지연 시간과 에러율만 본다면, 서비스는 살아 있어도 **모델 품질**은 이미 무너지고 있을 수 있습니다.

## 자주 하는 실수 5가지

1. **전처리를 노트북 셀 여러 곳에 흩어 놓습니다.**
2. **시드와 버전 고정을 건너뛰어 재현성을 잃습니다.**
3. **모니터링 없이 배포만 합니다.**
4. **모델 카드 없이 모델을 공유합니다.**
5. **현실을 반영하지 않는 낡은 데이터로만 평가합니다.**

## 실무에서는 이렇게 나타납니다

추천, 사기 탐지, 검색 팀은 노트북 하나보다 **전체 ML 루프를 얼마나 잘 자동화했는지**로 경쟁합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 문제 정의가 가치의 60%를 좌우합니다.
- `Pipeline`이 유지보수성을 결정합니다.
- 모니터링이 진짜 시작입니다.
- drift는 반드시 일어납니다.
- 모델 카드는 조직 자산이 됩니다.

## 체크리스트

- [ ] 모든 단계를 `Pipeline` 안에 묶습니다.
- [ ] `joblib`로 저장하고 다시 불러옵니다.
- [ ] 시드와 버전을 고정합니다.
- [ ] drift 모니터링 전략을 세웁니다.

## 연습 문제

1. 파이프라인에 `PCA`를 추가하고 점수를 비교해 보세요.
2. 저장한 모델을 별도 스크립트에서 불러와 다시 평가해 보세요.
3. 입력 노이즈가 커질수록 점수가 어떻게 변하는지 곡선을 그려 보세요.

## 정리

축하합니다. Machine Learning 101 시리즈를 마쳤습니다. 하지만 실제 ML 프로젝트의 끝은 모델 학습이 아니라, 문제 정의부터 모니터링까지 이어지는 루프를 안정적으로 운영하는 데 있습니다.

이 글에서 기억할 핵심은 네 가지입니다. 첫째, 높은 점수만으로는 아무것도 배포되지 않습니다. 둘째, `Pipeline`은 전처리와 모델을 한 몸으로 묶어 누수를 막습니다. 셋째, 재현성은 운영 문제를 되짚는 기준선입니다. 넷째, 배포 후 모니터링이야말로 실제 ML 운영의 출발점입니다.

다음 단계로는 Model Evaluation 101이나 MLOps 101처럼 더 깊은 시리즈로 이어가면 좋습니다.

<!-- toc:begin -->
- [Machine Learning이란 무엇인가?](./01-what-is-machine-learning.md)
- [지도학습과 비지도학습](./02-supervised-and-unsupervised.md)
- [Train/Test Split](./03-train-test-split.md)
- [Linear Regression](./04-linear-regression.md)
- [Logistic Regression](./05-logistic-regression.md)
- [Decision Tree와 Random Forest](./06-decision-tree-and-random-forest.md)
- [Clustering](./07-clustering.md)
- [Overfitting과 Regularization](./08-overfitting-and-regularization.md)
- [Model Evaluation](./09-model-evaluation.md)
- **ML 프로젝트 전체 흐름 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [scikit-learn — Pipelines](https://scikit-learn.org/stable/modules/compose.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Model Cards — Mitchell et al. (2019)](https://arxiv.org/abs/1810.03993)
- [Hidden Technical Debt in ML — Sculley et al.](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

Tags: MachineLearning, MLWorkflow, Pipeline, MLOps, Beginner
