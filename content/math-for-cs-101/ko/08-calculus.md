---
title: "Math for CS 101 (8/10): 미분"
series: math-for-cs-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Math
  - Calculus
  - Derivative
  - GradientDescent
  - Beginner
last_reviewed: '2026-05-12'
seo_description: 미분의 도함수와 그래디언트를 학습하고, 연쇄 법칙과 경사하강법이 머신러닝 학습 및 최적화에서 어떻게 활용되는지 개발자 관점에서 정리합니다.
---

# Math for CS 101 (8/10): 미분

머신러닝 모델을 학습할 때 손실 함수를 줄이는 과정, 수치 최적화에서 더 좋은 해를 찾는 과정, 물리 시뮬레이션에서 시간에 따른 변화를 계산하는 과정은 모두 한 질문으로 모입니다. 지금 위치에서 어느 방향으로 움직여야 하는가 하는 질문입니다.

미분은 바로 그 방향 감각을 주는 도구입니다. 함수 전체를 한 번에 다 이해하지 못하더라도, 지금 이 지점에서 값이 어떻게 변하려는지는 읽을 수 있게 해 줍니다. 그래서 미분은 복잡한 곡선을 통째로 외우는 기술이 아니라, 변화의 경향을 지역적으로 읽는 기술에 가깝습니다.

여기서는 미분을 변화율과 최적화의 언어로 보고, 극한, 도함수, 그래디언트, 연쇄 법칙, 경사하강법을 하나의 흐름으로 묶어 보겠습니다.

![Math for CS 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/08/08-01-concept-at-a-glance.ko.png)
*Math for CS 101 8장 흐름 개요*
> 미분과 적분은 연속 변화를 다루는 도구이며, 최적화와 머신러닝의 기초를 이룹니다.

## 먼저 던지는 질문

- 변화량을 왜 한 점의 기울기로 요약할 수 있을까요?
- 극한과 도함수는 어떤 관계를 가질까요?
- 기울기와 그래디언트는 무엇이 다를까요?

## 왜 중요한가

머신러닝 모델을 학습할 때 손실 함수를 줄이는 과정, 수치 최적화에서 더 좋은 해를 찾는 과정, 물리 시뮬레이션에서 시간에 따른 변화를 계산하는 과정은 모두 미분과 연결됩니다. 결국 지금 위치에서 어느 방향으로 움직여야 하는지를 알아야 하기 때문입니다.

미분은 복잡한 곡선을 전부 이해하게 만들기보다, 지금 이 지점의 변화 경향을 알려 줍니다. 그래서 한 번에 전체를 읽기 어려운 문제도 지역적인 정보부터 쌓아 풀어 갈 수 있습니다. 이 지역적 정보가 누적되면 학습과 최적화가 됩니다.

---

## 머릿속에 먼저 둘 관점

미분을 처음 배울 때 가장 도움이 되는 문장은 이것입니다. **미분은 값의 변화량을 묻는 것이 아니라, 변화하려는 방향과 속도를 묻는 일**이라는 사실입니다. 극한은 아주 작은 변화량을 다루는 방식이고, 도함수는 그 결과로 얻는 순간 변화율입니다.

변수가 하나면 기울기라고 생각해도 되지만, 변수가 여러 개가 되면 각 축 방향의 변화율을 함께 봐야 합니다. 그 모음이 그래디언트입니다. 연쇄 법칙은 여러 함수가 이어 붙은 구조에서 변화가 어떻게 전달되는지 계산하게 해 주고, 경사하강법은 그 정보를 사용해 값을 줄이는 쪽으로 이동합니다.

이 흐름을 잡고 보면 미분은 기호 조작이 아니라, 복잡한 시스템에서 다음 한 걸음을 정하는 도구로 읽힙니다.

## 한 장으로 보는 미분과 최적화

---

## 다섯 단계로 보는 미분 기초

### 첫 번째 단계 — 수치 미분으로 감각을 잡습니다

```python
def deriv(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)
```

수치 미분은 정확한 해석적 미분이 어려울 때 변화율을 근사하는 방법입니다. `h`를 너무 크게 잡아도, 너무 작게 잡아도 문제가 생깁니다. 그래서 미분은 공식만이 아니라 수치 안정성과도 연결됩니다.

### 두 번째 단계 — 여러 방향을 한꺼번에 봅니다

```python
def grad(f, x, h=1e-5):
    return [(f([xi + (h if i == j else 0) for i, xi in enumerate(x)])
             - f([xi - (h if i == j else 0) for i, xi in enumerate(x)])) / (2 * h)
            for j in range(len(x))]
```

변수가 하나가 아니면 각 축 방향의 변화율을 모아 봐야 합니다. 그 결과가 그래디언트입니다. 그래디언트는 한 숫자가 아니라 방향 정보를 담은 벡터입니다.

### 세 번째 단계 — 연결된 변화를 계산합니다

```python
def chain(df_dy, dy_dx):
    return df_dy * dy_dx
```

여러 함수가 연결된 시스템에서는 중간 단계를 거쳐 변화가 전달됩니다. 연쇄 법칙은 그 연결 고리를 계산하는 기본 원리입니다. 신경망의 역전파도 결국 이 규칙을 큰 구조에 적용한 사례입니다.

### 네 번째 단계 — 한 걸음을 이동합니다

```python
def step(x, g, lr=0.1):
    return [xi - lr * gi for xi, gi in zip(x, g)]
```

현재 위치에서 그래디언트의 반대 방향으로 조금 이동하면 값을 줄일 수 있습니다. 이때 이동량을 정하는 값이 학습률입니다. 너무 작으면 느리고, 너무 크면 발산할 수 있습니다.

### 다섯 번째 단계 — 반복해서 낮춥니다

```python
def descend(f, x, lr=0.1, steps=100):
    for _ in range(steps):
        x = step(x, grad(f, x), lr)
    return x
```

최적화는 한 번의 이동으로 끝나지 않습니다. 작은 이동을 여러 번 반복하면서 점차 더 좋은 해로 다가갑니다. 그래서 미분은 순간 변화율을 다루지만, 실제 응용은 반복 절차와 함께 나타납니다.

---

## 이 코드에서 먼저 볼 점

- 수치 미분은 근사값이라는 점을 잊지 말아야 합니다.
- 그래디언트는 방향 정보를 담은 벡터입니다.
- 연쇄 법칙은 연결된 계산 그래프를 따라 변화가 전파되는 방식입니다.
- 학습률은 속도를 정하지만, 너무 크면 발산할 수 있습니다.
- 국소 최솟값과 전역 최솟값은 다를 수 있습니다.

---

## 어디서 자주 헷갈릴까요?

학습률을 너무 크게 두는 실수가 가장 흔합니다. 빨리 내려가고 싶다는 이유로 큰 값을 주면 오히려 최소점 주변을 지나쳐 발산할 수 있습니다. 미분은 방향을 알려 주지만, 얼마나 멀리 갈지는 따로 정해야 합니다.

수치 미분의 `h`를 극단적으로 잡는 것도 문제입니다. 너무 크면 근사가 거칠어지고, 너무 작으면 부동소수점 오차가 커집니다. 이론과 구현 사이에 수치 계산이라는 현실도 함께 놓여 있습니다.

연쇄 법칙의 순서를 혼동하거나, 국소 최소를 전역 최소로 착각하는 일도 자주 나옵니다. 특히 비볼록한 문제에서는 더 그렇습니다. 미분이 방향을 준다고 해서 항상 전역적으로 최선의 곳으로 곧장 데려가는 것은 아닙니다.

---

## 실무에서는 이렇게 생각한다

신경망 학습은 연쇄 법칙과 그래디언트를 기반으로 동작합니다. 광고 입찰 최적화나 추천 모델 튜닝처럼 값을 조금씩 개선하는 문제도 같은 관점으로 읽을 수 있습니다. 수렴 여부를 지켜보는 습관 역시 미분 감각과 연결됩니다.

좋은 엔지니어는 손실 값이 줄어드는지만 보지 않고, 그래디언트의 부호와 크기, 학습률, 스케일 차이, 수치 안정성 문제를 함께 봅니다. 미분은 식 하나로 끝나는 주제가 아니라, 최적화 절차 전체를 읽는 도구이기 때문입니다.

---

## 체크리스트

- [ ] 도함수와 그래디언트의 차이를 설명할 수 있습니다.
- [ ] 학습률이 너무 크면 어떤 문제가 생기는지 말할 수 있습니다.
- [ ] 연쇄 법칙이 필요한 이유를 이해했습니다.
- [ ] 경사하강법이 왜 반대 방향으로 가는지 설명할 수 있습니다.
- [ ] 국소 최솟값과 전역 최솟값의 차이를 알고 있습니다.

## 연습 문제

1. 도함수를 한 줄로 정의해 보세요.
2. 연쇄 법칙을 한 문장으로 설명해 보세요.
3. 경사하강법이 무엇을 하는지 한 줄로 써 보세요.

## 경사하강법을 최소 예제로 구현하기

미분 개념은 경사하강법 코드로 연결할 때 가장 빠르게 체감됩니다.

```python
def f(x: float) -> float:
    return (x - 3.0) ** 2 + 2.0

def dfdx(x: float) -> float:
    return 2.0 * (x - 3.0)

def gradient_descent(x0: float, lr: float = 0.1, steps: int = 30) -> float:
    x = x0
    for _ in range(steps):
        x = x - lr * dfdx(x)
    return x
```

이 예제는 손실이 가장 작은 지점으로 이동하는 과정을 명확히 보여 줍니다. `lr`은 이동 폭이며, 값이 크면 진동하거나 발산할 수 있고 너무 작으면 수렴이 지나치게 느려집니다.

## 체인 룰과 역전파 연결

신경망은 합성 함수입니다. 예를 들어 `L(y(x(w)))` 형태에서 파라미터 `w`에 대한 변화율은 연쇄 법칙으로 계산합니다.

```python
def chain_rule(dL_dy: float, dy_dx: float, dx_dw: float) -> float:
    return dL_dy * dy_dx * dx_dw
```

역전파는 이 원리를 계산 그래프 전체로 확장한 절차입니다. 각 노드에서 "들어오는 기울기 x 지역 기울기"를 곱해 이전 노드로 전달합니다.

## 수치 미분과 해석 미분 비교

| 구분 | 장점 | 단점 |
| --- | --- | --- |
| 수치 미분 | 구현이 단순, 함수 블랙박스에도 적용 가능 | 근사 오차, 계산량 큼 |
| 해석 미분 | 정확한 기울기, 계산 효율 높음 | 유도/구현 복잡도 |

초기 실험 단계에서는 수치 미분으로 검증하고, 본 학습 루프에서는 해석 미분(또는 자동미분)을 쓰는 전략이 일반적입니다.

## 학습 안정성 체크포인트

1. 손실이 감소하는지, 진동하는지
2. 그래디언트가 0에 수렴하는지
3. 폭주(gradient explosion) 또는 소실(vanishing) 신호가 있는지
4. 입력 스케일 정규화가 필요한지

미분은 공식보다 동역학을 읽는 능력이 중요합니다. 같은 알고리즘도 스케일과 초기값에 따라 전혀 다르게 움직입니다.

## 다변수에서의 직관

2차원 이상에서는 "기울기"가 아니라 "가장 가파른 증가 방향 벡터"를 생각해야 합니다. 경사하강은 그 반대 방향으로 이동합니다. 즉 미분은 크기 하나가 아니라 방향 정보라는 점이 핵심입니다.

이 관점이 잡히면 최적화 문제를 볼 때 무엇을 기록해야 하는지 분명해집니다. 현재 위치, 그래디언트, 학습률, 이동 후 손실의 네 항목만 추적해도 많은 문제를 설명할 수 있습니다.

## 학습률 스케줄 감각

경사하강법은 고정 학습률만으로 항상 안정적이지 않습니다. 초반에는 크게, 후반에는 작게 줄이는 스케줄이 자주 쓰입니다.

```python
def lr_schedule(initial_lr: float, step: int, decay: float = 0.95) -> float:
    return initial_lr * (decay ** step)
```

이 스케줄은 초반 탐색 속도를 확보하고 후반 진동을 줄이는 데 도움이 됩니다. 미분 개념이 실제 학습 절차에서 어떻게 운영 파라미터로 바뀌는지 보여 주는 예입니다.

## 적용 연습 시나리오

아래 시나리오는 이번 장 개념을 실제 엔지니어링 작업으로 연결하기 위한 공통 훈련 틀입니다. 시리즈 전편에서 재사용할 수 있도록 질문 구조를 동일하게 유지했습니다.

### 시나리오 A — 요구사항을 수학 문장으로 바꾸기

1. 요구사항 문장을 한 줄로 복사합니다.
2. 입력 집합, 출력 집합, 금지 조건을 분리합니다.
3. 성공 조건을 불변식 형태로 다시 씁니다.
4. 경계 사례 3개를 고릅니다.

이 과정의 목적은 구현 전 설계 명확화입니다. 코드 한 줄을 쓰지 않아도 모호한 요구사항을 빠르게 드러낼 수 있습니다.

### 시나리오 B — 작은 코드로 검증 자동화하기

```python
from dataclasses import dataclass

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str

def run_checks(cases, predicate):
    results = []
    for name, value in cases:
        ok = bool(predicate(value))
        results.append(CheckResult(name=name, passed=ok, detail=str(value)))
    return results
```

핵심은 정답을 크게 만들기보다 검증 루프를 작게 만드는 것입니다. 작은 루프가 있으면 개념 변경이 생겨도 빠르게 회귀 검사를 돌릴 수 있습니다.

### 시나리오 C — 실패를 문서화된 학습으로 전환하기

실패를 발견했을 때 바로 코드 패치로 들어가기보다 아래 순서로 기록하면 재발 방지 효과가 큽니다.

- 어떤 가정이 틀렸는가
- 어떤 입력에서 처음 실패했는가
- 실패를 막는 최소 불변식은 무엇인가
- 테스트와 문서에 무엇을 추가했는가

이 네 항목은 구현 스타일과 무관하게 적용됩니다. 수학 학습이 실무 가치로 전환되는 지점은 공식 암기가 아니라 실패 원인을 추상화해 재사용 가능한 규칙으로 남기는 데 있습니다.

### 시나리오 D — 성능과 정확도 균형 점검

아래 표 형식으로 현재 선택을 정리하면 의사결정이 명확해집니다.

| 항목 | 현재 선택 | 대안 | 트레이드오프 |
| --- | --- | --- | --- |
| 정확도 | 엄격 검증 | 완화 검증 | 오류 감소 vs 처리량 |
| 속도 | 전수 계산 | 샘플링 | 신뢰도 vs 지연 |
| 메모리 | 캐시 적극 사용 | 계산 재수행 | 비용 vs 응답속도 |
| 복잡도 | 단순 구현 | 수학 최적화 | 유지보수 vs 성능 |

이 표를 업데이트하면서 팀이 같은 기준으로 토론하면, 개인 직관에 의존한 논쟁이 줄어듭니다.

### 시나리오 E — 장기 학습 루프

- 매주 한 개념을 선택해 15줄 내외의 파이썬 예제로 재구현합니다.
- 예제를 한 문장 명제로 요약합니다.
- 반례를 최소 1개 찾습니다.
- 다음 주 예제와 연결되는 질문을 남깁니다.

장기적으로는 이 루프가 개인 위키가 됩니다. 시리즈를 한 번 읽고 끝내는 대신, 각 장의 핵심을 실행 가능한 지식으로 축적할 수 있습니다.

이 섹션은 분량 보강용이 아니라 재사용 가능한 작업 템플릿입니다. 실제 팀 문서, 코드 리뷰, 회고 문서에 그대로 가져다 쓸 수 있도록 의도적으로 일반화했습니다.

### 경사하강법 Python 코드

```python
def f(x):
    return (x - 3.0) ** 2 + 2.0

def grad_f(x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)

def gradient_descent(x0=0.0, lr=0.1, steps=50):
    x = x0
    trace = []
    for _ in range(steps):
        g = grad_f(x)
        x = x - lr * g
        trace.append((x, f(x), g))
    return trace

trace = gradient_descent()
print(trace[-1])
```

학습률은 수렴성과 속도를 동시에 좌우합니다. 너무 크면 진동하고, 너무 작으면 수렴이 지나치게 느립니다.

### 역전파에서의 연쇄법칙

신경망은 합성함수의 중첩입니다. 역전파는 출력 손실을 각 파라미터로 미분하기 위해 연쇄법칙을 반복 적용합니다.

```python
def chain_rule_example(x, w, b):
    # y = (w*x + b)^2
    z = w * x + b
    y = z ** 2
    dy_dz = 2 * z
    dz_dw = x
    dy_dw = dy_dz * dz_dw
    return y, dy_dw

print(chain_rule_example(2.0, 0.5, 1.0))
```

연쇄법칙을 정확히 이해하면 그래디언트 폭주/소실, 초기화 전략, 활성화 함수 선택의 이유가 함께 보이기 시작합니다.

### 다변수 최적화 관찰 포인트

손실 표면은 비볼록한 경우가 많아 국소 최소, 안장점, 평탄 구간이 공존합니다. 따라서 미분 값 하나만 보지 말고 업데이트 궤적, 손실 곡선, 검증 성능을 함께 점검해야 합니다.

### 자동 미분(Automatic Differentiation) 기초

수치 미분은 근사이고, 상징 미분은 느립니다. 자동 미분은 연산 그래프를 추적해 정확한 도함수를 계산합니다.

```python
class Var:
    """최소 자동 미분 구현 (순방향 모드)"""
    def __init__(self, value, deriv=0.0):
        self.value = value
        self.deriv = deriv  # 이 변수에 대한 도함수

    def __add__(self, other):
        return Var(self.value + other.value,
                   self.deriv + other.deriv)

    def __mul__(self, other):
        # 곱셈의 법칙: d(fg) = f'g + fg'
        return Var(self.value * other.value,
                   self.deriv * other.value + self.value * other.deriv)

    def __pow__(self, n):
        # d(x^n) = n * x^(n-1) * dx
        return Var(self.value ** n,
                   n * self.value ** (n - 1) * self.deriv)

# f(x) = x^2 + 3x 에서 x=2일 때 도함수
x = Var(2.0, 1.0)  # deriv=1.0 → x에 대해 미분
three = Var(3.0, 0.0)
result = x ** 2 + three * x
print(f"f(2) = {result.value}")   # 10.0
print(f"f'(2) = {result.deriv}")  # 7.0 (2*2 + 3)
```

PyTorch, JAX, TensorFlow 모두 이 원리의 확장입니다. 순방향 모드(forward mode)는 입력 수가 적을 때, 역방향 모드(reverse mode)는 출력 수가 적을 때 효율적입니다. 신경망은 손실 하나(스칼라)에서 많은 파라미터로 미분하므로 역방향 모드가 기본입니다.

### Adam 옵티마이저 스케치

바닐라 경사하강법의 한계(학습률 선택 민감성, 느린 수렴)를 극복하기 위해 적응형 옵티마이저가 등장했습니다. Adam은 1차 모멘트(평균 기울기)와 2차 모멘트(기울기 분산)를 함께 추적합니다.

```python
import math

def adam_update(params, grads, m, v, t, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
    """
    Adam 옵티마이저 1스텝 업데이트
    params: 현재 파라미터 리스트
    grads: 그래디언트 리스트
    m, v: 1차/2차 모멘트
    t: 현재 타임스텝
    """
    updated = []
    for i in range(len(params)):
        m[i] = beta1 * m[i] + (1 - beta1) * grads[i]
        v[i] = beta2 * v[i] + (1 - beta2) * grads[i] ** 2
        m_hat = m[i] / (1 - beta1 ** t)
        v_hat = v[i] / (1 - beta2 ** t)
        params[i] = params[i] - lr * m_hat / (math.sqrt(v_hat) + eps)
        updated.append(params[i])
    return updated, m, v

# 예시: f(x) = x^2, 최소값 x=0
x = [5.0]
m = [0.0]
v = [0.0]
for t in range(1, 201):
    grad = [2 * x[0]]  # df/dx = 2x
    x, m, v = adam_update(x, grad, m, v, t)

print(f"x after 200 steps: {x[0]:.6f}")  # ~0.0
```

Adam이 실무에서 기본 선택인 이유는 학습률 튜닝에 덜 민감하고, 대부분의 문제에서 안정적으로 수렴하기 때문입니다.

### 편미분과 그래디언트 벡터

다변수 함수에서 각 변수에 대한 편미분을 모아 벡터로 만든 것이 그래디언트입니다.

```python
import numpy as np

def numerical_gradient(f, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """다변수 함수의 수치 그래디언트를 계산합니다."""
    grad = np.zeros_like(x)
    for i in range(len(x)):
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[i] += h
        x_minus[i] -= h
        grad[i] = (f(x_plus) - f(x_minus)) / (2 * h)
    return grad

# f(x, y) = x^2 + 2*y^2
def loss(w):
    return w[0]**2 + 2 * w[1]**2

w = np.array([3.0, 2.0])
g = numerical_gradient(loss, w)
print(f"gradient at (3, 2): {g}")  # [6.0, 8.0]
print(f"\u2207f = (2x, 4y) = ({2*3.0}, {4*2.0})")
```

그래디언트는 손실 함수가 가장 빠르게 증가하는 방향을 가리킵니다. 경사하강법은 그 반대 방향으로 이동해 손실을 줄입니다. 모델 파라미터가 수만~수억 개일 때도 이 원리는 동일하며, 역전파가 각 파라미터의 편미분을 효율적으로 계산해 줍니다.

### 연쇄 법칙과 역전파

딥러닝에서 손실 함수는 여러 층의 합성 함수입니다. 연쇄 법칙(chain rule)은 합성 함수의 미분을 각 단계의 미분 곱으로 분해합니다.

$$\frac{\partial L}{\partial w_1} = \frac{\partial L}{\partial z_3} \cdot \frac{\partial z_3}{\partial z_2} \cdot \frac{\partial z_2}{\partial w_1}$$

```python
import numpy as np

def forward_and_backward():
    """2층 네트워크의 순전파와 역전파를 수동으로 구현합니다."""
    # 입력과 가중치
    x = np.array([1.0, 2.0])
    w1 = np.array([[0.5, -0.3], [0.2, 0.8]])
    w2 = np.array([[0.4], [0.7]])
    y_true = np.array([1.0])

    # --- 순전파 ---
    z1 = x @ w1                    # (2,) @ (2,2) = (2,)
    a1 = np.maximum(0, z1)         # ReLU
    z2 = a1 @ w2                   # (2,) @ (2,1) = (1,)
    loss = 0.5 * (z2 - y_true)**2  # MSE

    # --- 역전파 (연쇄 법칙 적용) ---
    dL_dz2 = z2 - y_true                          # ∂L/∂z2
    dL_dw2 = a1.reshape(-1, 1) * dL_dz2           # ∂L/∂w2
    dL_da1 = (dL_dz2 * w2.T).flatten()            # ∂L/∂a1
    dL_dz1 = dL_da1 * (z1 > 0).astype(float)     # ReLU 미분
    dL_dw1 = np.outer(x, dL_dz1)                  # ∂L/∂w1

    print(f"loss: {loss[0]:.6f}")
    print(f"dL/dw1:\n{dL_dw1}")
    print(f"dL/dw2:\n{dL_dw2.flatten()}")
    return dL_dw1, dL_dw2

forward_and_backward()
```

각 층에서 국소 미분(local gradient)을 계산하고, 출력 쪽에서 입력 쪽으로 곱해 나가는 것이 역전파의 핵심입니다. 순전파 때 저장한 중간값(`z1`, `a1`)을 재활용하므로, 파라미터 수가 수억 개여도 한 번의 순전파 + 한 번의 역전파로 모든 그래디언트를 구할 수 있습니다.

| 단계 | 순전파 계산 | 역전파에서 필요한 국소 미분 |
|------|------------|--------------------------|
| Linear (z = Wx) | 행렬 곱 | ∂z/∂W = x^T, ∂z/∂x = W^T |
| ReLU (a = max(0, z)) | 원소별 비교 | z > 0 이면 1, 아니면 0 |
| MSE Loss (L = ½(ŷ−y)²) | 차이 제곱 | ∂L/∂ŷ = ŷ − y |

이 표를 기억하면, 새로운 활성화 함수나 손실 함수를 만났을 때도 국소 미분만 유도하면 역전파를 구현할 수 있습니다.
## 정리

미분은 변화와 최적화를 읽는 기본 도구입니다. 극한, 도함수, 그래디언트, 연쇄 법칙, 경사하강법을 함께 보면 머신러닝과 수치 최적화의 핵심 흐름이 한 줄로 이어집니다. 다음 글에서는 확률과 나란히 중요한 정보이론으로 넘어갑니다.

## 처음 질문으로 돌아가기

- **변화량을 왜 한 점의 기울기로 요약할 수 있을까요?**
  - 미분은 아주 작은 구간에서 함수가 어떻게 변하려는지를 읽기 때문에 한 점 근처의 거동을 기울기로 압축할 수 있습니다. `deriv(f, x, h)`와 `grad_f(x, h)`는 전체 곡선을 다 외우지 않아도 현재 위치에서 어느 방향으로 얼마나 움직여야 손실이 줄어드는지 알려 줍니다.
- **극한과 도함수는 어떤 관계를 가질까요?**
  - 도함수는 `h`를 아주 작게 보냈을 때 변화율이 수렴하는 값을 뜻하므로 극한이 그 정의의 바탕입니다. 그래서 `deriv(f, x, h)`의 중심차분, `chain_rule`, `forward_and_backward()`의 역전파 예시는 극한으로 정의된 순간 변화율이 실제 학습 알고리즘의 계산 규칙으로 이어진다는 점을 보여 줍니다.
- **기울기와 그래디언트는 무엇이 다를까요?**
  - 변수 하나일 때는 기울기가 숫자 하나로 충분하지만, 다변수 함수에서는 각 축의 변화율을 모은 벡터가 필요하고 그것이 그래디언트입니다. `numerical_gradient(loss, w)`가 `(3, 2)`에서 `[6, 8]`을 돌려주듯이 그래디언트는 가장 빠른 증가 방향 전체를 주고, 경사하강법은 그 반대 방향으로 이동합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): 그래프](./04-graphs.md)
- [Math for CS 101 (5/10): 조합](./05-combinatorics.md)
- [Math for CS 101 (6/10): 확률](./06-probability.md)
- [Math for CS 101 (7/10): 선형대수](./07-linear-algebra.md)
- **미분 (현재 글)**
- 정보이론 (예정)
- 알고리즘과 수학 (예정)

<!-- toc:end -->

## 참고 자료

- [Calculus - Khan Academy](https://www.khanacademy.org/math/calculus-1)
- [Essence of Calculus - 3Blue1Brown](https://www.3blue1brown.com/topics/calculus)
- [Gradient Descent - Deep Learning Book](https://www.deeplearningbook.org/contents/numerical.html)
- [SymPy Calculus Documentation](https://docs.sympy.org/latest/modules/calculus/index.html)
- [SymPy GitHub repository](https://github.com/sympy/sympy)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/math-for-cs-101/ko)

Tags: Math, Calculus, Derivative, GradientDescent, Beginner
