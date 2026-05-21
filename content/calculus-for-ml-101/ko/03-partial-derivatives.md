---
series: calculus-for-ml-101
episode: 3
title: "Calculus for ML 101 (3/10): 편미분"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Calculus
  - ML
  - PartialDerivative
  - MultiVariable
  - Beginner
seo_description: 편미분, 다변수 함수, 변수 고정, 변수별 기울기와 ML 가중치 직관을 ML 입문자 관점에서 정리한 글
last_reviewed: '2026-05-12'
---

# Calculus for ML 101 (3/10): 편미분

현실의 머신러닝 모델은 입력 하나만 받는 단순한 함수가 아닙니다. 가중치 수백 개, 수천 개, 때로는 수십억 개를 가진 다변수 함수입니다. 이런 함수에서 “지금 어떤 파라미터가 손실에 얼마나 책임이 있는가”를 알려면 전체를 한 번에 보는 대신 각 변수를 따로 떼어 볼 수 있어야 합니다.

편미분은 바로 그 분해를 가능하게 합니다. 나머지 변수는 고정해 두고 하나만 움직였을 때 함수가 어떻게 변하는지를 측정하는 방식입니다. 이 약속이 있어야 모델의 각 가중치에 대해 독립적인 업데이트 신호를 만들 수 있습니다.

이 글은 Calculus for ML 101 시리즈의 세 번째 글입니다.

이 글에서는 다변수 함수, 변수 고정, 변수별 책임 할당이라는 관점에서 편미분을 설명하겠습니다. 핵심은 수학 기호가 아니라, 모델 파라미터마다 “이 변수는 지금 얼마만큼 손실에 기여했는가”를 읽는 방법입니다.

끝까지 읽고 나면 편미분을 단지 미분의 확장판이 아니라, backpropagation이 각 파라미터에 책임을 나눠 주는 기본 단위로 이해하게 됩니다.

## 먼저 던지는 질문

- 입력이 여러 개인 함수에서는 왜 변수별로 기울기를 따로 봐야 할까요?
- 편미분에서 “다른 변수는 고정한다”는 약속은 실제로 무엇을 뜻할까요?
- 같은 함수라도 어떤 변수에 대해 미분하느냐에 따라 왜 다른 값이 나올까요?

## 큰 그림

![Calculus for ML 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/calculus-for-ml-101/03/03-01-concept-at-a-glance.ko.png)

*Calculus for ML 101 3장 흐름 개요*

## 왜 이 글이 중요한가

딥러닝 모델의 손실 함수는 거의 항상 다변수 함수입니다. 하나의 weight만 바꿔도 loss가 달라지고, bias를 바꿔도 loss가 달라지며, 입력 스케일이나 내부 activation 역시 영향을 줍니다. 학습은 결국 이 다변수 함수의 표면에서 적절한 방향을 찾는 과정이므로, 변수별 변화량을 분리해 읽는 편미분이 필수입니다.

실무적으로도 이 개념은 매우 직접적입니다. optimizer는 weight마다 독립된 gradient 값을 사용해 업데이트를 수행합니다. 만약 편미분 개념이 없다면 “모델 전체가 얼마나 나빠졌는가”만 알 수 있을 뿐, 어느 파라미터를 얼마나 바꿔야 하는지는 알 수 없습니다.

또한 편미분을 이해해야 다음 글의 gradient를 벡터로 받아들일 수 있습니다. gradient는 여러 편미분을 한데 묶은 것이므로, 편미분의 의미가 흐리면 gradient도 방향 벡터가 아니라 숫자 목록처럼 보이기 쉽습니다.

## 핵심 관점

편미분을 가장 쉽게 이해하는 방법은 다변수 함수를 3차원 지형처럼 상상한 뒤, 한 축만 따라 잘라 보는 것입니다. $x$를 볼 때는 $y$를 고정하고, $y$를 볼 때는 $x$를 고정합니다. 이렇게 만든 단면에서의 기울기가 바로 편미분입니다.

이 약속은 단순하지만 매우 강력합니다. 함수 전체를 한 번에 다루기 어렵더라도, 변수 하나씩의 국소 반응으로 쪼개면 각 파라미터의 책임을 계산할 수 있기 때문입니다. ML에서 각 weight가 자신의 gradient를 갖는 이유도 이 단면 분석 덕분입니다.

> 편미분은 “전체를 포기한다”가 아니라 “한 번에 하나씩 본다”는 전략입니다. 나머지를 고정하는 약속이 있어야 변수별 책임이 분리됩니다.

## 핵심 개념

편미분의 흐름은 아래처럼 정리할 수 있습니다.

### 다변수 함수는 입력 축이 여러 개인 함수입니다

```python
def f(x, y):
    return x ** 2 + 3 * y
```

이 함수는 입력이 두 개입니다. $x$를 바꾸면 $x^2$ 항 때문에 함수값이 바뀌고, $y$를 바꾸면 $3y$ 항 때문에 함수값이 바뀝니다. 두 입력이 동시에 영향을 주므로, 어느 입력이 얼마나 기여하는지 따로 분리해 보는 것이 편미분의 출발점입니다.

### x만 움직이면 x에 대한 편미분입니다

```python
def partial_x(f, x, y, h=1e-5):
    return (f(x + h, y) - f(x - h, y)) / (2 * h)
```

여기서는 $y$를 그대로 둔 채 $x$만 좌우로 조금 움직입니다. 이 코드가 암묵적으로 말하는 것은 명확합니다. 지금은 $x$의 책임만 보겠다는 뜻입니다. 다른 변수는 여전히 함수값에 영향을 주지만, 이번 측정에서는 바꾸지 않습니다.

### y만 움직이면 y에 대한 편미분입니다

```python
def partial_y(f, x, y, h=1e-5):
    return (f(x, y + h) - f(x, y - h)) / (2 * h)
```

이번에는 반대로 $x$를 고정하고 $y$만 봅니다. 같은 함수라도 어느 변수를 선택하느냐에 따라 변화율이 달라진다는 사실이 중요합니다. 다변수 함수에서는 “기울기”가 하나의 숫자가 아니라 변수별 숫자 묶음으로 나타나기 시작합니다.

### 여러 편미분을 함께 계산하면 gradient의 재료가 됩니다

```python
def partials(f, x, y):
    return partial_x(f, x, y), partial_y(f, x, y)
```

이 함수는 gradient vector의 가장 단순한 전 단계입니다. 아직 벡터 해석까지는 가지 않더라도, 각 변수마다 독립적인 변화율이 존재하고 이것을 일정한 순서로 묶어 관리해야 한다는 점이 핵심입니다.

### ML에서는 각 가중치가 자기 편미분을 받습니다

```python
def loss(w1, w2):
    return (w1 - 1) ** 2 + (w2 + 2) ** 2

g1, g2 = partials(loss, 0.0, 0.0)  # responsibility per weight
```

이 코드는 두 개의 weight가 각자 어떤 방향으로 움직여야 loss를 줄일 수 있는지 보여 줍니다. $g1$과 $g2$는 같은 loss에서 나왔지만 서로 다른 책임을 갖습니다. backpropagation은 결국 이런 편미분을 네트워크 전체 파라미터에 대해 효율적으로 계산하는 절차입니다.

### 변수 순서와 고정값은 실무에서 중요합니다

gradient를 사용할 때는 변수 순서가 문서화되어 있어야 합니다. 예를 들어 첫 번째 값이 $w1$용인지 $w2$용인지 흐려지면 업데이트 대상이 섞입니다. 또한 “고정된 변수”도 중요합니다. 편미분은 나머지를 없애는 것이 아니라, 현재 값으로 고정한 상태에서 한 변수의 국소 반응만 읽는 것입니다.

## 흔히 헷갈리는 지점

- 편미분을 계산하면서 모든 변수를 동시에 바꾸면 편미분이 아니라 전혀 다른 값을 보게 됩니다.
- 고정된 변수는 중요하지 않다고 오해하기 쉽지만, 실제 편미분 값은 고정된 변수의 현재 값에도 의존할 수 있습니다.
- 변수 순서를 명시하지 않으면 gradient vector 해석이 틀어집니다.
- 편미분과 total derivative를 같은 것으로 생각하면 연쇄 효과를 설명하기 어려워집니다.
- 각 변수에 다른 스케일이 걸려 있을 때 동일한 크기의 gradient를 같은 의미로 받아들이면 안 됩니다.

## 운영 체크리스트

- [ ] 다변수 loss를 볼 때 어떤 변수를 고정하고 무엇을 움직이는지 분명히 한다
- [ ] gradient vector의 변수 순서를 코드와 문서에서 일치시킨다
- [ ] 편미분 값은 각 변수의 책임 신호라는 점을 팀 내 공통 언어로 맞춘다
- [ ] 수치 검증 시 변수마다 같은 방식의 centered difference를 적용한다
- [ ] 고정된 변수의 현재 값도 해석에 영향을 준다는 점을 잊지 않는다

## 정리

편미분은 여러 입력을 가진 함수에서 하나의 변수만 움직였을 때의 국소 변화율을 측정하는 도구입니다. 나머지를 고정한다는 약속 덕분에, 함수 전체의 복잡성을 잠시 접어 두고 변수별 책임을 분리해서 읽을 수 있습니다.

ML에서 이 개념은 곧 파라미터별 gradient로 이어집니다. 모델이 아무리 커져도 각 weight는 자신의 편미분 값을 받아 업데이트되고, 그 값들이 모여 gradient vector와 optimizer의 입력이 됩니다. 즉 편미분은 수학적 세부사항이 아니라, 학습 책임을 분배하는 기본 단위입니다.

다음 글에서는 이 편미분들을 하나의 벡터로 묶은 gradient를 보겠습니다. 그러면 변수별 책임이 어떻게 하나의 방향 정보로 합쳐지는지 더 선명해집니다.


## 추가 실전 섹션: 미분 신호를 학습 루프로 연결하는 계산 연습

미분 개념을 오래 유지하려면 손으로 계산한 값과 코드에서 나온 값이 같은지 반복 확인하는 연습이 중요합니다. 아래 표는 손실 함수와 gradient를 빠르게 점검할 때 자주 쓰는 비교 축입니다.

| 항목 | 회귀(MSE) | 분류(BCE) | 점검 포인트 |
| --- | --- | --- | --- |
| 손실 형태 | 평균 제곱 오차 | 음의 로그 우도 | 문제 유형 일치 여부 |
| gradient 민감도 | 큰 오차에 더 민감 | 확신한 오답에 큰 페널티 | 폭주/포화 구간 확인 |
| 수치 안정성 | 비교적 안정적 | `log(0)` 방어 필요 | `eps` 처리 |
| 학습 신호 | 선형 오차 비례 | 확률 오차 반영 | calibration 해석 |

### 체인 룰 검증: 수치 미분과 해석 미분 비교

```python
import math

def f(x):
    return math.sin(3 * x + 1)

def analytic_grad(x):
    # d/dx sin(3x+1) = cos(3x+1) * 3
    return math.cos(3 * x + 1) * 3

def numeric_grad(fn, x, h=1e-5):
    return (fn(x + h) - fn(x - h)) / (2 * h)

x = 0.7
print(analytic_grad(x), numeric_grad(f, x))
```

해석 미분과 수치 미분이 비슷하게 나오면 체인 룰 구현이 올바르게 연결되었다는 강한 증거가 됩니다.

### 2변수 손실에서 gradient 벡터 해석

```python
def loss(w1, w2):
    return (w1 - 2) ** 2 + 4 * (w2 + 1) ** 2

def grad(w1, w2):
    return 2 * (w1 - 2), 8 * (w2 + 1)

w1, w2 = 0.0, 0.0
g1, g2 = grad(w1, w2)
print('grad=', (g1, g2))
```

이 예시에서는 두 번째 축 gradient가 더 크게 나오므로 동일 learning rate에서도 `w2` 방향 업데이트가 더 공격적으로 일어납니다. 좌표별 스케일 차이를 optimizer가 어떻게 다루는지 이해하는 출발점입니다.

### 손실 곡선 해석 표

| 관찰 패턴 | 가능한 원인 | 우선 점검 |
| --- | --- | --- |
| 초반 급상승 후 발산 | learning rate 과대, gradient 폭주 | lr 감소, clipping |
| 매우 느린 하강 | learning rate 과소, 특징 스케일 불일치 | lr 증가, 정규화 |
| 진동만 하고 정체 | 비등방 지형, batch noise 과다 | momentum, batch 조정 |
| train 감소 / val 정체 | 과적합 | weight decay, early stopping |

### 미니 실습: 간단한 업데이트 루프

```python
def train_step(w, x, y, lr=0.05):
    pred = w * x
    loss = (pred - y) ** 2
    grad = 2 * (pred - y) * x
    w = w - lr * grad
    return w, loss, grad

w = 0.0
for _ in range(5):
    w, L, g = train_step(w, x=3.0, y=12.0)
    print(f'w={w:.4f}, loss={L:.4f}, grad={g:.4f}')
```

짧은 루프지만 forward-loss-backward-update가 모두 포함되어 있습니다. 이 구조를 이해하면 어떤 딥러닝 프레임워크의 학습 코드도 핵심 의미를 잃지 않고 읽을 수 있습니다.

### 실전 점검 루틴

1. 해석 미분과 수치 미분을 작은 예제로 한 번 맞춰 봅니다.
2. gradient norm을 함께 기록해 신호 크기 변화를 확인합니다.
3. learning rate를 3개 이상 비교해 수렴 민감도를 봅니다.
4. train/validation 손실을 동시에 관찰해 과적합 신호를 분리합니다.
5. 이상 징후가 생기면 모델 구조보다 손실/미분/업데이트 순서를 먼저 점검합니다.

이 루틴이 자리 잡으면 미분 개념이 수학 노트에 머무르지 않고 실제 모델 훈련 의사결정으로 연결됩니다.



## 추가 보강: 검증 가능한 예제 세트

### 입력 크기 대비 알고리즘/학습 선택 표

| 상황 | 빠른 선택 | 검증 기준 |
| --- | --- | --- |
| 작은 입력, 빠른 프로토타입 | 단순 구현 우선 | 정답 검증 테스트 3종 |
| 큰 입력, 지연시간 민감 | 차수 낮은 알고리즘 또는 안정적 optimizer | 시간/메모리 동시 측정 |
| 운영 장애 재현 필요 | 로그/추적 필드 강화 | 동일 입력 재실행 가능성 |

### 짧은 비교 코드

```python
import time

def measure(fn, *args, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best
```

측정 코드는 화려할 필요가 없습니다. 같은 입력, 같은 환경, 같은 반복 기준을 유지하는 것이 더 중요합니다. 이 습관이 있어야 최적화 전후의 차이를 신뢰할 수 있습니다.

### 실전 점검 질문

1. 지금 선택한 방법의 시간/공간 비용을 한 문장으로 설명할 수 있는가
2. 경계 입력에서 동작이 바뀌는 지점을 테스트로 고정했는가
3. 운영 로그만으로 실패 원인을 분리할 수 있는가

이 질문에 즉답할 수 있으면 구현이 아니라 설계 수준에서 품질을 확보한 상태에 가깝습니다.



### 보강 메모: 경계 입력과 수치 검증

경계 입력을 별도 표로 관리하면 알고리즘/학습 루프의 취약점을 빠르게 찾을 수 있습니다.

| 케이스 | 기대 동작 |
| --- | --- |
| 빈 입력 또는 최소 크기 | 예외 없이 명시적 반환 |
| 중복값 다수 | 안정성/경계 갱신 유지 |
| 극단적으로 큰 값 | 오버플로우/수치 불안정 방어 |

```python
def sanity_cases(fn, cases):
    out=[]
    for c in cases:
        out.append(fn(*c) if isinstance(c, tuple) else fn(c))
    return out
```

작은 검증 루틴을 글과 코드에 함께 남기면 이후 변경에서 같은 종류의 실수를 반복할 가능성이 크게 줄어듭니다.

## 처음 질문으로 돌아가기

- **입력이 여러 개인 함수에서는 왜 변수별로 기울기를 따로 봐야 할까요?**
  - 본문의 기준은 편미분를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **편미분에서 “다른 변수는 고정한다”는 약속은 실제로 무엇을 뜻할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **같은 함수라도 어떤 변수에 대해 미분하느냐에 따라 왜 다른 값이 나올까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Calculus for ML 101 (1/10): 미분이란 무엇인가](./01-what-is-derivative.md)
- [Calculus for ML 101 (2/10): 함수와 기울기](./02-functions-and-slope.md)
- **편미분 (현재 글)**
- Gradient (예정)
- 연쇄 법칙 (예정)
- 손실 함수 (예정)
- 경사하강법 (예정)
- 최적화 (예정)
- 역전파 직관 (예정)
- 딥러닝에서의 미분 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Partial Derivatives - Khan Academy](https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives)
- [Multivariable Calculus - MIT OCW](https://ocw.mit.edu/courses/18-02-multivariable-calculus-fall-2007/)
- [Deep Learning Book - Chapter 4](https://www.deeplearningbook.org/contents/numerical.html)
- [JAX Automatic Differentiation](https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html)

### 관련 시리즈
- [Linear Algebra 101](../../linear-algebra-101/ko/)
- [MLOps 101](../../mlops-101/ko/)

Tags: Calculus, ML, PartialDerivative, MultiVariable, Beginner
