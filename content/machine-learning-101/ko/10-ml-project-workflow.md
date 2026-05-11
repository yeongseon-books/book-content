---
series: machine-learning-101
episode: 10
title: ML 프로젝트 전체 흐름
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - MachineLearning
  - MLWorkflow
  - Pipeline
  - MLOps
  - Beginner
seo_description: 문제 정의부터 데이터·모델·평가·배포·모니터링까지, 머신러닝 프로젝트 전체 흐름과 sklearn Pipeline까지 정리한 마무리 글
last_reviewed: '2026-05-11'
---

# ML 프로젝트 전체 흐름

## 이 글에서 다룰 문제

- 노트북에서 점수가 잘 나왔는데도 왜 많은 ML 프로젝트는 배포에 실패할까요?
- 문제 정의, 데이터, 모델, 배포, 모니터링은 왜 하나의 루프로 봐야 할까요?
- `Pipeline`은 왜 단순한 편의 기능이 아니라 유지보수 도구일까요?
- 모델 저장과 재현성은 왜 초반부터 설계해야 할까요?
- 배포 이후 모니터링은 왜 끝이 아니라 시작일까요?

머신러닝 입문자는 대개 모델 학습과 점수 출력까지를 프로젝트의 핵심으로 봅니다. 물론 중요합니다. 하지만 실제 영향은 그 뒤에서 갈립니다. 좋은 문제를 고르고, 데이터를 정리하고, 재현 가능한 파이프라인을 만들고, 배포 후 드리프트까지 감시해야 모델이 비로소 사용자에게 닿습니다.

이 글은 Machine Learning 101 시리즈의 마무리로, 지금까지 배운 내용을 하나의 흐름으로 묶습니다. 문제 정의부터 데이터 준비, 모델 학습, 평가, 배포, 모니터링까지를 한 바퀴의 루프로 보면서 왜 "점수"보다 "전체 시스템"이 중요해지는지 설명하겠습니다.

> 머신러닝의 성공은 점수 하나를 높이는 일이 아니라, 문제 정의부터 모니터링까지의 루프를 완성하는 일입니다.

## 왜 중요한가

실무에서 실패하는 프로젝트는 모델 성능이 낮아서만 멈추지 않습니다. 문제 정의가 애매하거나, 데이터가 재현되지 않거나, 전처리가 노트북 셀에 흩어져 있거나, 배포 후 모니터링이 없어서 서서히 망가지는 경우가 더 많습니다.

그래서 ML 프로젝트를 잘 운영하는 팀은 모델 자체보다 워크플로를 먼저 설계합니다. 어떤 지표로 성공을 정의할지, 데이터 버전은 어떻게 남길지, 전처리는 어떻게 고정할지, 모델이 드리프트하면 누가 알림을 받을지 같은 질문이 초반부터 함께 나옵니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    P["1. 문제 정의"] --> D["2. 데이터"]
    D --> F["3. 피처"]
    F --> M["4. 모델"]
    M --> E["5. 평가"]
    E --> Dep["6. 배포"]
    Dep --> Mon["7. 모니터링"]
    Mon --> P
```

## 핵심 용어

- **Pipeline**: 전처리와 모델을 하나로 묶는 객체입니다.
- **재현성**: 시드, 버전, 데이터 스냅샷을 고정해 같은 결과를 다시 만들 수 있는 성질입니다.
- **Model Card**: 모델 메타데이터와 사용 조건을 정리한 문서입니다.
- **Drift**: 입력 분포나 목표 분포가 시간이 지나며 변하는 현상입니다.
- **Shadow deploy**: 예측은 하되 실제 의사결정에는 반영하지 않고 로그만 쌓는 배포 방식입니다.

## Before / After

**Before**: 모델을 학습하고 점수를 출력하면 끝이라고 생각합니다.

**After**: 문제, 데이터, 모델, 평가, 배포, 모니터링이 반복되는 루프로 봅니다.

## 5단계 미니 워크플로우

### Step 1 — 문제와 데이터

예제에서는 이진 분류 문제를 간단히 준비합니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

실제 프로젝트라면 여기서 끝나지 않습니다. 어떤 오류가 더 비싼지, 어떤 데이터가 누락됐는지, 데이터 분할이 시간 누수를 만들지 않는지도 함께 봐야 합니다.

### Step 2 — Pipeline 구성

전처리와 모델을 하나의 객체로 묶습니다.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=2000)),
])
```

`Pipeline`의 장점은 편리함보다 안전성에 있습니다. 학습 시점의 전처리와 예측 시점의 전처리가 어긋나는 일을 크게 줄여 줍니다.

### Step 3 — 학습과 평가

파이프라인 전체를 학습하고 테스트셋에서 확인합니다.

```python
pipe.fit(Xtr, ytr)
print("test:", pipe.score(Xte, yte))
```

이 단계에서 점수가 나온다고 프로젝트가 끝난 것은 아닙니다. 오히려 여기부터 배포 가능성, 재현성, 모니터링 계획이 더 중요해집니다.

### Step 4 — 저장과 재현성

학습한 객체를 저장하고 다시 불러옵니다.

```python
import joblib
joblib.dump(pipe, "model.joblib")
loaded = joblib.load("model.joblib")
print("loaded:", loaded.score(Xte, yte))
```

모델 저장은 단순 백업이 아닙니다. 정확히 어떤 전처리와 어떤 파라미터가 들어간 객체인지 고정하는 일입니다. 재현성이 없으면 운영 이슈가 생겼을 때 되돌아갈 기준점도 사라집니다.

### Step 5 — 모니터링 시뮬레이션

입력 분포가 조금 흔들렸을 때 점수가 어떻게 달라지는지 간단히 살펴봅니다.

```python
import numpy as np
fresh = Xte + np.random.normal(0, 0.1, Xte.shape)
print("drifted:", loaded.score(fresh, yte))
```

입력에 작은 노이즈만 들어가도 점수가 내려갈 수 있습니다. 이것이 드리프트 감시가 필요한 이유입니다. 배포 시점의 테스트 통과가 영구적인 안전을 보장하지는 않습니다.

## 이 코드에서 주목할 점

- `Pipeline`은 전처리 누수를 구조적으로 줄입니다.
- `joblib` 저장은 재현 가능한 배포의 출발점입니다.
- 작은 입력 변화만으로도 점수가 떨어질 수 있어 모니터링이 필수라는 점을 보여 줍니다.

## 실무에서는 이렇게 이어집니다

추천, 검색, 사기 탐지 팀은 모델을 하나 잘 만드는 것보다 전체 루프를 얼마나 안정적으로 자동화하느냐에서 경쟁력이 갈립니다. 학습 파이프라인, 피처 버전 관리, 배포 승인, 드리프트 알림, 재학습 정책이 모두 연결되어야 합니다.

또한 모델은 혼자 운영되지 않습니다. 데이터 엔지니어, 백엔드 엔지니어, 제품 관리자, 운영 담당자가 같은 흐름을 공유해야 장애와 성능 저하를 빠르게 읽을 수 있습니다. 그래서 ML 워크플로는 개인 노트북의 기술이 아니라 팀 시스템의 기술입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 문제 정의가 전체 가치의 절반 이상을 결정합니다.
- `Pipeline`은 유지보수성과 재현성을 동시에 좌우합니다.
- 모니터링은 마지막 단계가 아니라 실제 운영의 시작입니다.
- 드리프트는 예외가 아니라 기본값입니다.
- Model Card 같은 문서는 조직 자산이 됩니다.

## 자주 하는 실수 5가지

1. 전처리를 노트북 셀 여기저기에 흩어 놓습니다.
2. 시드와 버전을 기록하지 않아 재현성을 잃습니다.
3. 모니터링 없이 배포만 하고 끝냅니다.
4. 모델 설명 문서 없이 팀 밖으로 공유합니다.
5. 오래된 평가 데이터로 현실과 동떨어진 결론을 냅니다.

## 체크리스트

- [ ] 전처리와 모델을 `Pipeline`으로 묶을 수 있습니다.
- [ ] `joblib`로 저장하고 다시 불러올 수 있습니다.
- [ ] 시드와 버전 고정이 왜 필요한지 설명할 수 있습니다.
- [ ] 드리프트 모니터링 계획을 세워야 한다는 점을 이해했습니다.

## 연습 문제

1. 파이프라인에 `PCA`를 추가하고 점수를 비교해 보세요.
2. 저장한 모델을 별도 스크립트에서 불러와 다시 평가해 보세요.
3. 입력 노이즈 크기를 늘리며 점수 하락 곡선을 그려 보세요.

## 정리 및 다음 글

머신러닝 프로젝트는 모델을 학습하는 순간보다 그 앞뒤가 더 길고 더 중요합니다. 문제 정의, 데이터 준비, 전처리, 모델링, 평가, 배포, 모니터링이 하나라도 빠지면 높은 점수는 쉽게 무력해집니다.

이 시리즈를 마무리하며 꼭 기억할 점은 세 가지입니다. 첫째, 좋은 모델보다 좋은 워크플로가 더 오래 갑니다. 둘째, `Pipeline`과 재현성은 운영 품질의 기초입니다. 셋째, 배포는 끝이 아니라 관측과 개선의 시작입니다. 이제 Machine Learning 101을 마쳤으니, 다음 단계에서는 Model Evaluation 101이나 MLOps 101처럼 더 깊은 주제로 이어갈 수 있습니다.

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
