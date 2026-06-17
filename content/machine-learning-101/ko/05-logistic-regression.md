---
series: machine-learning-101
episode: 5
title: "Machine Learning 101 (5/10): Logistic Regression"
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
  - LogisticRegression
  - Classification
  - scikit-learn
  - Beginner
seo_description: 로지스틱 회귀가 선형 점수를 확률로 바꾸는 방식과 임계값, 정밀도, 재현율을 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (5/10): Logistic Regression

0 또는 1을 예측하는데 왜 이름은 회귀인지, 입문 단계에서 가장 많이 받는 질문 중 하나입니다. 이 혼란은 자연스럽습니다. 로지스틱 회귀는 클래스를 곧바로 내놓는 모델처럼 보이지만, 실제로는 먼저 연속적인 확률을 계산한 뒤 임계값을 기준으로 분류를 결정합니다. 그래서 분류 문제를 다루지만 내부 동작은 확률 모델로 이해하는 편이 맞습니다.

이 글은 머신러닝 101 시리즈의 5번째 글입니다. 여기서는 시그모이드 함수, 임계값, 정밀도·재현율·F1의 의미를 함께 보면서 로지스틱 회귀를 분류의 가장 기본적인 기준선으로 정리해 보겠습니다.

![Machine Learning 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/05/05-01-diagram.ko.png)
*Machine Learning 101 5장 흐름 개요*
> 로지스틱 회귀는 선형 점수를 확률로 짜낸 다음, 두 클래스 사이 어디에 경계선을 그을지 결정하는 모델입니다.

## 이 글에서 다룰 문제

- 0 또는 1을 예측하는데 왜 이름은 회귀일까요?
- 시그모이드는 선형 점수를 어떻게 확률로 바꿀까요?
- 왜 0.5 임계값을 항상 정답처럼 쓰면 안 될까요?

## 시그모이드 함수의 직관

로지스틱 회귀의 핵심은 **시그모이드 함수**입니다. 시그모이드는 어떤 실수 값이든 0과 1 사이로 보냅니다.

$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

### 왜 시그모이드를 쓸까요?

1. 선형 회귀 `y_hat = Xw + b`는 `-∞`부터 `+∞`까지의 값을 낼 수 있습니다.
2. 분류 문제에서는 0와 1 사이의 확률을 내고 싶습니다.
3. 시그모이드는 실수를 `(0, 1)` 구간으로 압축하므로 이 역할을 합니다.

### 시그모이드의 특징

- `z = 0` 일 때 `σ(0) = 0.5`입니다.
- `z`가 클수록 `σ(z) → 1`입니다.
- `z`가 작을수록 `σ(z) → 0`입니다.
- S자 모양의 부드러운 곡선입니다.

로지스틱 회귀는 선형 점수를 먼저 계산한 뒤, 시그모이드로 감싸서 확률로 바꿔 줍니다.

## Python 예제: predict_proba로 확률 확인

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)

# 확률 확인
proba = model.predict_proba(Xte)[:5]
print("Class 0 | Class 1")
for p0, p1 in proba:
    print(f"{p0:.3f}   | {p1:.3f}")

# 예측 레이블
print("Predicted:", model.predict(Xte)[:5])
```

`.predict()`는 확률이 0.5를 넘으면 1, 아니면 0을 반환합니다. `.predict_proba()`를 보면 모델의 확신 정도를 알 수 있습니다.

## 로지스틱 vs 선형 회귀

| 항목 | 로지스틱 회귀 | 선형 회귀 |
|---|---|---|
| 출력 | 0과 1 사이 확률 | 연속값 |
| 손실함수 | Log Loss (Cross-Entropy) | MSE |
| 활용 | 분류 | 회귀 |

이름이 혼란스러운 이유는 로지스틱 회귀가 확률을 출력하기 때문입니다. 최종 분류는 임계값 적용 후에 결정됩니다.
로지스틱 회귀는 분류 문제의 표준 베이스라인입니다. 해석이 가능하고 빠르며, 임계값을 조정하면 불균형 데이터에서도 꽤 경쟁력 있게 동작합니다.

- **시그모이드**: 어떤 실수 값이든 `(0, 1)` 구간으로 매핑합니다.
- 확률: 클래스 1일 것이라는 모델의 믿음입니다.
- 임계값: 확률을 클래스 레이블로 바꾸는 기준선입니다.
- 정밀도: 양성이라고 예측한 것 중 실제 양성의 비율입니다.
- 재현율: 실제 양성 중 모델이 잡아낸 비율입니다.

## 적용 전과 후
**Before**: "정확도 95%"라는 숫자만 보고 만족합니다. 불균형 데이터에서는 거의 의미가 없습니다.

**After**: 정밀도, 재현율, F1, AUC를 함께 보고 임계값까지 조정합니다.

## 실습: 5단계로 보는 분류

### 단계 1 — 데이터

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### 단계 2 — 분할과 스케일링

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### 단계 3 — 학습

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### 단계 4 — 평가

```python
from sklearn.metrics import classification_report
print(classification_report(yte, model.predict(Xte)))
```

### 단계 5 — 임계값 조정

```python
prob = model.predict_proba(Xte)[:, 1]
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yte).mean())
```

**예상 출력:** `classification_report`는 클래스별 정밀도와 재현율을 보여 주고, 임계값 루프는 같은 모델이라도 cutoff를 바꾸면 결과가 달라진다는 점을 드러냅니다. 즉, 임계값 선택은 표시 옵션이 아니라 **모델링 결정**입니다.

- `predict_proba`는 레이블이 아니라 확률을 반환합니다.
- 임계값은 정밀도-재현율 절충을 조절하는 손잡이입니다.
- `StandardScaler`는 최적화가 수렴하는 데 도움을 줍니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 정확도는 높은데 중요한 양성을 놓친다면, 모델보다 먼저 **재현율**과 **임계값**을 봐야 합니다.
- 확률이 지나치게 자신 있어 보이면 `predict_proba`를 곧바로 믿기보다 **보정(calibration)** 여부를 확인해야 합니다.
- 계수가 불안정하게 흔들리면 solver보다 먼저 **스케일링**과 **클래스 불균형**을 점검하는 편이 낫습니다.

## 자주 하는 실수 5가지

1. **원시 확률이 이미 보정되어 있다고 가정합니다.**
2. **항상 0.5를 임계값으로 사용합니다.**
3. **불균형 데이터에서 정확도만 보고합니다.**
4. **피처 스케일링을 빼먹습니다.**
5. **다중 클래스에서 명시적 multinomial 설정 없이 기본값만 믿습니다.**

## 실무에서는 이렇게 나타납니다

스팸 필터링, 사기 탐지, 이탈 예측처럼 다운스트림 시스템이 **비용을 저울질해야 하는 문제**에서는 확률 출력이 필수입니다. 그래서 로지스틱 회귀는 단순한 분류 모델이 아니라 운영 의사결정의 입력 신호가 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 임계값은 **비즈니스 비용**이 결정합니다.
- 항상 정밀도-재현율 곡선을 그립니다.
- 불균형에는 class weight를 검토합니다.
- 해석 가능성은 중요한 레버리지입니다.
- 확률 보정은 별도로 검증합니다.

## 운영 체크리스트

- [ ] 후속 의사결정에 `predict_proba`를 사용합니다.
- [ ] 정밀도와 재현율을 함께 보고합니다.
- [ ] 비용 기준으로 임계값을 정합니다.
- [ ] 항상 피처를 스케일링합니다.

## 연습 문제

1. 임계값을 0.1부터 0.9까지 바꿔 가며 정밀도와 재현율을 그려 보세요.
2. `class_weight="balanced"`를 적용했을 때 결과를 비교해 보세요.
3. 다중 클래스 데이터셋에 `multi_class="multinomial"`을 적용해 보세요.
