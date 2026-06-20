---
series: machine-learning-101
episode: 1
title: "Machine Learning 101 (1/10): Machine Learning이란 무엇인가?"
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
  - AI
  - DataScience
  - Foundations
  - Beginner
seo_description: 머신러닝의 정의와 학습·일반화·예측의 직관, 그리고 통계·규칙 기반 코드와의 차이를 코드와 함께 정리합니다
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (1/10): Machine Learning이란 무엇인가?

추천, 의료, 금융, 자율주행처럼 머신러닝이 등장하지 않는 산업을 찾기 어려워졌습니다. 그런데 입문 단계에서는 오히려 가장 기본적인 질문이 흐려지기 쉽습니다. 머신러닝은 통계의 다른 이름인지, 규칙 기반 프로그래밍의 확장인지, 아니면 전혀 다른 문제 해결 방식인지부터 분명히 잡아야 이후 모델 선택도 흔들리지 않습니다.

이 글은 머신러닝 101 시리즈의 1번째 글입니다. 여기서는 머신러닝을 **데이터에서 함수를 학습해 새로운 입력에 대해 예측하는 방식**이라는 관점으로 정리하고, 학습·일반화·예측이 각각 무엇을 뜻하는지 출발점부터 잡아 보겠습니다.

![Machine Learning 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/01/01-01-diagram.ko.png)
*Machine Learning 101 1장 흐름 개요*
> 머신러닝은 **학습·일반화·예측**이라는 세 가지 단계로 나뉩니다. 이 구조를 이해하면 이후 모든 모델을 다루는 방식이 달라집니다.

## 이 글에서 다룰 문제

- 머신러닝은 정확히 무엇을 학습한다고 봐야 할까요?
- 일반화는 왜 훈련 성능과 다른 개념일까요?
- 통계, 규칙 기반 코드, 머신러닝은 어디서 갈릴까요?
- 지도학습·비지도학습·강화학습은 어떤 상황에서 각각 적합할까요?
- 훈련 정확도가 높은데 실전에서 무너지는 이유는 무엇일까요?
- 머신러닝이 적합하지 않은 문제는 어떤 특징이 있을까요?

## ML 유형 비교

| 유형 | 입력 | 출력 | 대표 예시 |
|---|---|---|---|
| 지도학습 | X, y (레이블 있음) | 분류/회귀 예측 | 스팸 필터, 가격 예측 |
| 비지도학습 | X (레이블 없음) | 구조 발견 | 고객 세그먼트, 이상 탐지 |
| 강화학습 | 상태, 보상 | 행동 정책 | 게임 AI, 로봇 제어 |

입문 단계에서는 지도학습과 비지도학습의 경계가 가장 먼저 보이기 시작합니다. 강화학습은 보상 신호를 어떻게 설계할지부터 문제가 크게 바뀌기 때문에 처음부터 함께 다루지는 않습니다.
추천 시스템, 의료 진단 보조, 금융 리스크 분석, 자율주행처럼 거의 모든 산업이 머신러닝의 영향을 받고 있습니다. 하지만 기초 개념이 약하면 뒤에서 어떤 모델을 올려도 해석이 무너집니다. 훈련 데이터에서 점수가 잘 나왔다고 곧바로 성공이라고 착각하거나, 문제 정의보다 알고리즘 이름에 먼저 끌리는 순간부터 프로젝트는 불안해집니다.

- **학습(Learning)**: 데이터에서 함수를 추정하는 과정입니다.
- **일반화(Generalization)**: 훈련 때 보지 못한 데이터에도 잘 동작하는 성질입니다.
- **예측(Prediction)**: 학습된 함수를 새로운 입력에 적용하는 일입니다.
- **피처(Feature)**: 모델에 들어가는 입력 변수입니다.
- **레이블(Label)**: 예측하려는 정답 또는 목표값입니다.

## 적용 전과 후
**Before**: "`if-else`로 모든 규칙을 직접 코딩한다"는 방식이라서 새로운 패턴이 생길 때마다 코드를 더 붙여야 합니다.

**After**: "데이터를 주면 모델이 규칙을 학습한다"는 방식이라서 코드보다 데이터가 확장의 중심이 됩니다.

## 실습: 5단계로 보는 첫 번째 ML

### 단계 1 — 데이터

```python
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
print(X.shape, y.shape)
```

### 단계 2 — 모델 선택

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000)
```

### 단계 3 — 학습

```python
model.fit(X, y)
```

### 단계 4 — 예측

```python
print(model.predict(X[:5]))
```

### 단계 5 — 점수 확인

```python
print("acc:", model.score(X, y))
```

**예상 출력:** `X.shape`, `y.shape`는 `(150, 4)`, `(150,)`처럼 작은 표 데이터를 보여 주고, `predict`는 클래스 ID 배열을 출력합니다. 마지막 정확도는 대체로 높게 나오지만, 여기서는 **훈련 데이터 점수**라는 점을 먼저 기억해야 합니다.

## 모델 비교: 첫 번째 ML의 선택지

처음 머신러닝을 시작할 때 어떤 모델을 골라야 할지 막막합니다. 아래 표는 입문 단계에서 자주 만나는 모델들의 특징을 요약합니다.

| 모델 | 유형 | 해석 가능성 | 전처리 필요도 | 추천 시작 상황 |
|---|---|---|---|---|
| LogisticRegression | 분류 | 높음 | 스케일링 필요 | 이진 분류 베이스라인 |
| LinearRegression | 회귀 | 높음 | 스케일링 권장 | 연속값 예측 베이스라인 |
| DecisionTreeClassifier | 분류 | 중간 | 거의 불필요 | 규칙을 시각화하고 싶을 때 |
| KMeans | 군집 | 낮음 | 스케일링 필수 | 레이블 없는 탐색 |

베이스라인 없이 바로 복잡한 모델로 시작하면 어디서 성능이 나오는지 알 수 없습니다. 항상 단순한 모델부터 시작합니다.

## 규칙 기반 vs 머신러닝 코드 비교

규칙 기반 접근법과 머신러닝 접근법이 같은 문제에서 어떻게 다른지 살펴봅니다.

```python
# 규칙 기반: 사람이 직접 경계를 정합니다
def classify_rule(petal_length):
    if petal_length < 2.0:
        return "setosa"
    elif petal_length < 4.5:
        return "versicolor"
    else:
        return "virginica"

# 머신러닝: 데이터에서 경계를 학습합니다
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print("ML 정확도:", model.score(Xte, yte))
```

규칙 기반은 새로운 품종이 등장하면 사람이 규칙을 다시 써야 합니다. 머신러닝은 새로운 데이터를 주면 모델이 스스로 경계를 다시 그립니다.

## ML이 적합한 문제 vs 부적합한 문제

**적합한 경우:**

- 규칙을 명시하기 어렵지만 데이터는 충분합니다.
- 패턴이 복잡하거나 계속 변합니다.
- 확률적 예측이 유용합니다.

**부적합한 경우:**

- 규칙이 명확하고 안정적입니다.
- 데이터가 거의 없거나 레이블링 비용이 너무 높습니다.
- 결정 과정이 완전히 투명해야 합니다.

머신러닝은 만능 도구가 아닙니다. 문제 정의가 먼저고, 그 뒤에야 알고리즘 선택입니다.

## Python 예제: 3줄로 보는 분류

```python
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
X, y = load_iris(return_X_y=True)
model = LogisticRegression(max_iter=1000).fit(X, y)
print("Accuracy:", model.score(X, y))  # 예: 0.97
```

이 코드는 3줄이지만, 학습·일반화·예측의 전체 파이프라인을 보여 줍니다. 다만 여기서 나온 점수는 **훈련 정확도**이므로 과대평가되었을 가능성이 높습니다.

- `fit / predict / score`는 **scikit-learn의 표준 인터페이스**입니다.
- 여기서 `score`는 **훈련 정확도**일 뿐이며, 일반화 성능을 바로 뜻하지는 않습니다.
- 어떤 모델을 고를지는 **문제 유형**에 따라 달라집니다.

## 학습 파이프라인 전체 예제

실제로 프로젝트를 시작할 때 사용하는 최소한의 패턴입니다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# 1. 데이터
X, y = load_iris(return_X_y=True)

# 2. 분할 (분할이 먼저입니다)
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 3. 전처리 (훈련 데이터만 fit)
sc = StandardScaler().fit(Xtr)
Xtr_s = sc.transform(Xtr)
Xte_s = sc.transform(Xte)

# 4. 학습
model = LogisticRegression(max_iter=1000).fit(Xtr_s, ytr)

# 5. 평가
print("훈련 점수:", model.score(Xtr_s, ytr))
print("테스트 점수:", model.score(Xte_s, yte))
print(classification_report(yte, model.predict(Xte_s)))
```

이 패턴을 지키면 누수와 과적합 진단의 기반이 만들어집니다. 분할을 먼저 하고, 전처리는 훈련 데이터로만 `fit`하는 순서가 핵심입니다.

## 실패 신호를 먼저 이렇게 읽습니다

- 훈련 정확도는 높은데 새 데이터에서 바로 무너지면, 모델보다 먼저 **입력 분포 변화**나 **타깃 정의의 모호함**을 의심해야 합니다.
- 팀이 `X`와 `y`가 무엇인지 한 문장으로 설명하지 못하면, 아직 모델 비교 단계가 아니라 **문제 정의 단계**에 머물러 있는 것입니다.
- 노트북에서 늘 같은 샘플 행만 확인하며 잘 된다고 느낀다면, 알고리즘보다 먼저 **누수**와 **암기** 가능성을 살펴봐야 합니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방향 |
|---|---|---|
| 훈련 점수만 보고 성공 판단 | 테스트에서 점수 폭락 | 분리된 테스트 세트로 평가 |
| 피처 스케일링 무시 | 모델 불안정, 수렴 실패 | StandardScaler 적용 |
| 타깃 누수(leakage) | 비현실적으로 높은 점수 | 피처 검토, 분할 순서 확인 |
| 랜덤 시드 미고정 | 결과 재현 불가 | `random_state=42` 등 고정 |
| 결측치·이상치 미처리 | 모델 학습 실패 또는 왜곡 | EDA 단계에서 먼저 처리 |

## 실무에서는 이렇게 나타납니다

추천, 사기 탐지, 수요 예측, 이미지 인식, NLP 챗봇까지, **데이터 → 학습 → 예측** 파이프라인은 거의 모든 ML 제품의 뼈대입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **문제 정의**가 **모델 선택**보다 먼저입니다.
- **데이터 품질**이 **알고리즘 이름**보다 더 중요할 때가 많습니다.
- 일반화는 항상 **분리된 데이터**에서 확인해야 합니다.
- 복잡한 모델보다 먼저 **베이스라인 모델**을 세웁니다.
- 복잡도는 처음이 아니라 **마지막 카드**로 아껴 둡니다.

## 운영 체크리스트

- [ ] `X, y`가 무엇을 뜻하는지 설명할 수 있습니다.
- [ ] `fit / predict / score`를 호출할 수 있습니다.
- [ ] 훈련 정확도와 일반화 성능이 다르다는 점을 이해했습니다.
- [ ] 베이스라인 모델의 가치를 알고 있습니다.

## 처음 질문으로 돌아가기

- **머신러닝은 정확히 무엇을 학습한다고 봐야 할까요?**
  - 데이터에서 입력(X)과 출력(y) 사이의 함수 관계를 추정하는 것입니다. 규칙을 사람이 쓰는 대신 데이터가 규칙을 만들어 냅니다.
- **일반화는 왜 훈련 성능과 다른 개념일까요?**
  - 훈련 데이터를 외우면 훈련 점수는 높지만 새 데이터에서 무너집니다. 일반화는 보지 못한 데이터에서도 동작하는 성질이므로, 분리된 데이터로 따로 확인해야 합니다.
- **통계, 규칙 기반 코드, 머신러닝은 어디서 갈릴까요?**
  - 통계는 모집단 추론에 초점을 맞추고, 규칙 기반은 사람이 조건을 직접 작성하며, 머신러닝은 데이터에서 패턴을 자동으로 학습합니다.
- **지도학습·비지도학습·강화학습은 어떤 상황에서 각각 적합할까요?**
  - 레이블이 있으면 지도학습, 없으면 비지도학습, 보상 신호로 행동을 최적화해야 하면 강화학습이 자연스럽습니다.
- **훈련 정확도가 높은데 실전에서 무너지는 이유는 무엇일까요?**
  - 입력 분포 변화, 타깃 누수, 과적합이 대표 원인입니다. 훈련 데이터만 보고 성공을 판단하면 안 됩니다.
- **머신러닝이 적합하지 않은 문제는 어떤 특징이 있을까요?**
  - 데이터가 부족하거나, 규칙이 명확하거나, 설명 가능성이 절대 요건인 경우에는 ML보다 규칙 기반 접근이 더 안전합니다.

---

## 정리

머신러닝은 데이터에서 함수를 학습해 새로운 입력에 대해 예측하는 방식입니다. 이 글에서 기억할 핵심은 세 가지입니다. 학습은 함수 추정이라는 점, 일반화는 훈련과 분리해서 확인해야 한다는 점, 그리고 모델 선택보다 문제 정의와 데이터 품질이 먼저라는 사실입니다. 다음 글에서는 지도학습과 비지도학습을 더 구체적으로 비교합니다.

## 연습 문제

1. `iris`가 아닌 **자신의 데이터셋**으로 `fit / predict`를 실행해 보세요.
2. `score`가 왜 **과도하게 낙관적**일 수 있는지 설명해 보세요.
3. 피처 스케일링이 결과를 바꾸는 예시를 하나 만들어 보세요.
4. 규칙 기반으로 풀기 어려운 문제를 하나 찾아 머신러닝으로 어떻게 접근할지 설명해 보세요.
5. `train_test_split`을 추가해서 훈련 점수와 테스트 점수의 차이를 관찰해 보세요.
