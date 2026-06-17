---
series: machine-learning-101
episode: 3
title: "Machine Learning 101 (3/10): Train/Test Split"
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
  - TrainTestSplit
  - Generalization
  - CrossValidation
  - scikit-learn
seo_description: 일반화를 측정하기 위한 train/test split의 의미와 누수, stratify, random_state, 교차검증까지 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (3/10): Train/Test Split

훈련 정확도가 99%라고 해서 실제 서비스에서도 잘 동작한다는 뜻은 아닙니다. 머신러닝 입문에서 가장 자주 생기는 착각도 바로 여기서 나옵니다. 같은 데이터로 학습하고 같은 데이터로 점수를 재면 숫자는 좋아 보이지만, 그 숫자로는 배포 후 성능을 설명할 수 없습니다.

이 글은 머신러닝 101 시리즈의 3번째 글입니다. 여기서는 train/test split이 왜 일반화 측정의 최소 장치인지, 그리고 `random_state`, `stratify`, K-fold 교차검증이 각각 어떤 역할을 하는지 정리해 보겠습니다.

![Machine Learning 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/03/03-01-diagram.ko.png)
*Machine Learning 101 3장 흐름 개요*
> Train/Test split은 모델이 처음 보는 데이터에서 어떻게 동작할지 가늠하는 유일하게 정직한 방법이고, 여기서 한 번이라도 새면 측정값 전체가 흔들립니다.

## 이 글에서 다룰 문제

- 훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을까요?
- `random_state`를 왜 항상 고정하라고 할까요?
- `stratify`는 클래스 불균형에서 어떤 도움을 줄까요?
- 분할 전략 비교에서 가장 흔한 실수는 무엇일까요?
- 이 개념을 실무 프로젝트에 적용할 때 가장 먼저 확인할 점은 무엇일까요?

- 데이터 누수(Data Leakage)의 핵심 원리를 한 문장으로 설명하면 무엇일까요?

## 분할 전략 비교

| 전략 | 장점 | 단점 | 적합 상황 |
|---|---|---|---|
| 홀드아웃(Hold-out) | 빠름 | 한 번의 분할에 의존 | 데이터가 충분히 많을 때 |
| K-fold | 모든 데이터 활용 | 시간이 더 걸림 | 표본 수가 적을 때 |
| Stratified | 클래스 비율 유지 | 설정이 하나 더 | 불균형 데이터 |
| 시계열 분할 | 누수 방지 | 훈련 데이터 감소 | 시간 순서가 중요한 문제 |

분할 전략의 선택은 데이터의 특성과 문제 유형에 따라 결정됩니다. 무작위 분할이 항상 정답은 아닙니다.

일반화를 측정하지 못하면 모델을 고를 수도, 비교할 수도 없습니다. 훈련 점수는 보기에는 좋지만 그대로 배포할 수 있는 숫자가 아닙니다. 어떤 분할 전략을 썼는지가 결국 모델 선택과 MLOps 게이트의 기준을 결정합니다.

- **Train**: 모델을 학습시키는 데이터입니다.
- **Validation**: 하이퍼파라미터를 조정하는 데 쓰는 데이터입니다.
- **Test**: 마지막에 한 번만 보는 홀드아웃 데이터입니다.
- **Stratify**: 분할 뒤에도 클래스 비율이 유지되도록 맞춥니다.
- **K-fold**: 데이터를 K개로 나누고 테스트 폴드를 돌아가며 바꿔 가는 방식입니다.

## 적용 전과 후
**Before**: 전체 데이터에 학습하고 같은 데이터로 점수를 재서 성능을 과대평가합니다.

**After**: train으로 학습하고 홀드아웃 test로 평가해, 숫자가 현실에 더 가깝도록 만듭니다.

## 실습: 5단계로 분할하고 평가하기

### 단계 1 — 데이터

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
```

### 단계 2 — 분할

```python
from sklearn.model_selection import train_test_split
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### 단계 3 — 모델

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### 단계 4 — 평가

```python
print("train:", model.score(Xtr, ytr))
print("test :", model.score(Xte, yte))
```

### 단계 5 — 교차검증

```python
from sklearn.model_selection import cross_val_score
print(cross_val_score(model, X, y, cv=5).mean())
```

**예상 출력:** 훈련 점수는 테스트 점수보다 약간 높게 나오고, 교차검증 평균은 그 주변 값에 모이는 편이 자연스럽습니다. 세 숫자가 크게 벌어지면 모델보다 먼저 **분할 전략**을 의심해야 합니다.

## 데이터 누수(Data Leakage)

데이터 누수는 훈련 데이터에 테스트 데이터의 정보가 섞여 들어가는 현상으로, 가장 위험한 오류 중 하나입니다.

### 누수가 발생하는 주요 경우

1. **전처리 누수**: 분할 전에 전체 데이터로 스케일러를 학습합니다.
2. **타겟 누수**: 피처 안에 타겟 정보가 직접 들어갑니다.
3. **시간 누수**: 미래 정보를 과거 예측에 사용합니다.
4. **그룹 누수**: 같은 사용자/그룹이 train/test에 나뉘어 들어갑니다.

### 예방 방법

- 분할을 가장 먼저 수행합니다.
- 전처리는 훈련 데이터로만 `.fit()`하고 테스트 데이터는 `.transform()`만 합니다.
- 피처 선택 단계에서 타겟 정보가 섞인 컴럼을 제거합니다.
- 시계열 문제에서는 시간 순서를 엄격히 지킵니다.

## Python 예제: train_test_split + cross_val_score

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)

# 홀드아웃 분할
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print("Train:", model.score(Xtr, ytr))
print("Test:", model.score(Xte, yte))

# 교차검증
scores = cross_val_score(model, X, y, cv=5)
print("CV mean:", scores.mean(), "std:", scores.std())
```

교차검증은 한 번의 분할에서 생길 수 있는 우연을 줄여 줍니다. 표본 수가 적을 때 특히 유용합니다.
- `stratify=y`는 두 분할 모두에서 클래스 비율을 유지합니다.
- 고정된 `random_state`는 결과를 재현 가능하게 만듭니다.
- `cross_val_score`는 훈련과 평가를 K번 반복합니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 테스트 점수가 실행할 때마다 크게 흔들리면 표본 수가 너무 작거나 시드가 떠 있는지 먼저 봐야 합니다.
- train과 test가 모두 지나치게 좋다면, 성능보다 먼저 **전처리 누수**를 점검해야 합니다.
- 시계열이나 사용자 그룹 데이터인데 무작위 분할을 썼다면, 지표가 아니라 **분할 방식 자체가 버그**일 수 있습니다.

## 자주 하는 실수 5가지

1. **테스트 세트로 튜닝해서 성능 누수를 만듭니다.**
2. **분할 전에 전체 데이터에 스케일러를 먼저 학습합니다.**
3. **랜덤 시드를 고정하지 않고 노이즈를 쫓습니다.**
4. **불균형 데이터에서 `stratify`를 무시합니다.**
5. **시계열 데이터를 시간 순서가 아니라 무작위로 나눕니다.**

## 실무에서는 이렇게 나타납니다

A/B 실험, 모델 비교, MLOps 게이팅 모두 올바른 분할 전략에 기대고 있습니다. 결국 의사결정을 지배하는 것은 지표 이름만이 아니라 **어떻게 나눴는가**입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 테스트 세트는 **정말 한 번만** 봅니다.
- 검증 세트와 테스트 세트는 분리합니다.
- 시계열 데이터는 시간 순서대로 나눕니다.
- 항상 그룹 누수 가능성을 의심합니다.
- 전처리는 분할 이후에 합니다.

## 운영 체크리스트

- [ ] train, valid, test의 역할을 설명할 수 있습니다.
- [ ] `stratify`가 하는 일을 이해했습니다.
- [ ] `random_state`를 항상 고정합니다.
- [ ] `cross_val_score`를 실행할 수 있습니다.

## 연습 문제

1. `test_size`를 0.1부터 0.3까지 바꿔 가며 테스트 점수를 관찰해 보세요.
2. `stratify=None`일 때 train과 test의 클래스 비율을 비교해 보세요.
3. 5-fold와 10-fold 점수의 분산을 비교해 보세요.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을, 둘째 `random_state`를 왜 항상 고정하라고 할, 셋째 `stratify`는 클래스 불균형에서 어떤 도움을 줄입니다. 분할 전략 비교에서 시작해 실무 적용까지 이어지는 흐름을 따라가면 이 주제의 전체 그림이 잡힙니다.

## 처음 질문으로 돌아가기

- **훈련 세트, 검증 세트, 테스트 세트는 각각 무엇을 맡을까요?**
  - - 테스트 세트는 **정말 한 번만** 봅니다
- **`random_state`를 왜 항상 고정하라고 할까요?**
  - 분할 전략의 선택은 데이터의 특성과 문제 유형에 따라 결정됩니다
- **`stratify`는 클래스 불균형에서 어떤 도움을 줄까요?**
  - 분할 전략의 선택은 데이터의 특성과 문제 유형에 따라 결정됩니다
- **분할 전략 비교에서 가장 흔한 실수는 무엇일까요?**
  - | 전략 | 장점 | 단점 | 적합 상황 |
  - 데이터 누수(Data Leakage)의 핵심 원리를 한 문장으로 설명하면 무엇일까요 — 본문에서 단계별로 설명합니다.
