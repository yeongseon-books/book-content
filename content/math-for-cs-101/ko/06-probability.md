---
episode: 6
language: ko
last_reviewed: '2026-05-12'
seo_description: 확률 기초와 조건부 확률, 베이즈 정리, 기댓값, 분산을 배우고 A/B 테스트 등 실무 의사결정에서의 활용을 정리합니다.
series: math-for-cs-101
status: publish-ready
tags:
- Math
- Probability
- Statistics
- Bayes
- Beginner
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Math for CS 101 (6/10): 확률"
---

# Math for CS 101 (6/10): 확률

실무에서는 불확실성을 피할 수 없습니다. A/B 테스트 결과가 우연인지, 분류기의 오탐률이 허용 가능한지, 장애 가능성이 어느 정도인지 같은 질문은 모두 확률 문제입니다. 다만 확률을 모르면 숫자를 보면서도 해석은 직관에 기대게 됩니다.

확률의 진짜 가치는 미래를 완벽하게 맞히는 데 있지 않습니다. 불확실성을 구조화해서 비교 가능한 판단으로 바꾸는 데 있습니다. 어떤 결과가 가능한지, 어떤 사건이 관심 대상인지, 어떤 조건이 이미 주어졌는지 분리하는 순간 막연한 감이 계산 가능한 모델이 됩니다.

이 글은 Math for CS 101 시리즈의 6번째 글입니다.

여기서는 확률을 숫자 놀음이 아니라, 불확실성을 설명하는 언어로 보고 표본공간, 조건부 확률, 베이즈 정리, 기댓값, 분산을 차근차근 연결해 보겠습니다.


![Math for CS 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/06/06-01-concept-at-a-glance.ko.png)
*Math for CS 101 6장 흐름 개요*
> 확률은 불확실성을 감으로 다루는 대신, 기댓값과 분포로 정량적 의사결정을 가능하게 합니다.

## 먼저 던지는 질문

- 불확실성을 감으로 넘기지 않고 어떻게 수치로 다룰까요?
- 표본공간과 사건은 무엇이 다를까요?
- 조건부 확률은 왜 문맥을 붙인 확률이라고 할 수 있을까요?

## 왜 중요한가

A/B 테스트 결과를 읽을 때도, 분류기의 오탐률을 볼 때도, 장애 가능성을 계산할 때도 우리는 이미 확률 문제를 다루고 있습니다. 다만 확률을 모르면 숫자를 보면서도 해석은 직관에 기대게 됩니다. 숫자는 있는데 의미는 없는 상태가 되는 것입니다.

확률은 불확실성을 없애지 않습니다. 대신 불확실성을 구조화합니다. 어떤 경우가 가능한지, 어떤 사건이 관심 대상인지, 이미 알고 있는 조건은 무엇인지 구분하게 해 줍니다. 이 구조가 있어야 같은 숫자도 맥락을 잃지 않고 읽을 수 있습니다.

---

## 머릿속에 먼저 둘 관점

확률을 이해할 때 가장 먼저 잡아야 할 문장은 이것입니다. **확률은 숫자 하나가 아니라, 가능한 결과와 조건을 함께 다루는 구조**라는 점입니다. 표본공간은 가능한 모든 결과의 집합이고, 사건은 그 안에서 우리가 관심 있는 부분집합입니다.

조건부 확률은 여기서 한 걸음 더 나아갑니다. 이미 어떤 정보가 주어졌을 때 전체 공간이 어떻게 달라지는지 보는 것입니다. 그래서 확률 계산에서 가장 중요한 일은 분자를 잘 세는 것만이 아니라, 분모가 어떤 세계를 가리키는지 놓치지 않는 일입니다.

베이즈 정리는 새로운 증거를 받아 믿음을 갱신하는 방식입니다. 기댓값은 평균적인 결과를, 분산은 그 결과의 흔들림을 보여 줍니다. 결국 확률은 가능성뿐 아니라 위험도 같이 말하게 해 주는 언어입니다.

## 한 장으로 보는 확률의 흐름

---

## 다섯 단계로 보는 확률 기초

### 첫 번째 단계 — 가장 기본 확률을 씁니다

```python
def prob(favorable, total):
    return favorable / total
```

가장 기본 형태입니다. 관심 있는 경우 수를 전체 경우 수로 나누는 사고는 이후 모든 확률 계산의 출발점이 됩니다. 단순해 보여도 어떤 경우를 전체로 볼지 먼저 정해야 한다는 점이 중요합니다.

### 두 번째 단계 — 조건을 붙입니다

```python
def cond(p_a_and_b, p_b):
    return p_a_and_b / p_b
```

조건부 확률은 이미 B가 일어났다는 정보를 반영합니다. 전체 공간이 바뀐다는 점이 핵심입니다. 실무에서 많은 오해는 분자가 아니라 분모를 잘못 잡는 데서 나옵니다.

### 세 번째 단계 — 믿음을 갱신합니다

```python
def bayes(p_b_given_a, p_a, p_b):
    return p_b_given_a * p_a / p_b
```

새 증거가 들어왔을 때 추정치를 어떻게 갱신할지 보여 줍니다. 스팸 필터, 진단, 랭킹 계산처럼 관측값을 보고 원인을 추정하는 문제에서 특히 자주 등장합니다.

### 네 번째 단계 — 평균적인 결과를 봅니다

```python
def expect(values, probs):
    return sum(v * p for v, p in zip(values, probs))
```

기댓값은 평균적인 결과를 알려 줍니다. 장기적으로 어떤 선택이 유리한지 비교할 때 특히 중요합니다. 다만 기댓값만으로는 흔들림의 크기를 알 수 없다는 점도 함께 봐야 합니다.

### 다섯 번째 단계 — 흔들림을 분리합니다

```python
def variance(values, probs):
    mu = expect(values, probs)
    return sum(p * (v - mu) ** 2 for v, p in zip(values, probs))
```

평균만 보면 놓치는 위험을 분산이 보여 줍니다. 같은 기댓값이라도 흔들림이 큰 선택과 작은 선택은 의미가 다릅니다. 의사결정에서는 종종 평균 못지않게 이 흔들림이 중요합니다.

---

## 이 코드에서 먼저 볼 점

- 확률값들의 합은 전체 분포 안에서 1이 됩니다.
- 조건부 확률은 분모가 바뀌는 순간 의미가 달라집니다.
- 베이즈 정리는 사전 정보와 새 증거를 함께 봅니다.
- 기댓값은 가중 평균이고, 분산은 흔들림의 크기입니다.
- 독립 가정은 편리하지만 항상 성립하지는 않습니다.

---

## 어디서 자주 헷갈릴까요?

독립이라고 쉽게 가정하는 실수가 가장 흔합니다. 현실 데이터에서는 사건들이 생각보다 자주 얽혀 있습니다. 독립성은 사실이라기보다 가정일 때가 많고, 이 가정을 놓치면 계산이 그럴듯해 보여도 해석이 무너집니다.

베이즈 정리에서 사전 확률을 0으로 두는 것도 위험합니다. 사전 확률이 0이면 이후 어떤 증거가 들어와도 갱신할 수 없기 때문입니다. 확률 모델은 종종 계산보다 초기 가정에서 더 민감하게 흔들립니다.

기댓값과 최빈값을 같은 것으로 보거나, 분산과 표준편차를 혼동하는 일도 자주 나옵니다. 평균적인 결과와 가장 자주 나오는 결과는 다를 수 있고, 흔들림의 제곱 평균과 원래 단위의 편차도 다릅니다.

---

## 실무에서는 이렇게 생각한다

스팸 필터는 베이즈 관점으로 점수를 갱신하고, 추천 시스템은 클릭 확률을 추정합니다. SRE 영역에서는 장애 발생 확률과 SLA 위반 가능성을 봅니다. 실험 설계에서는 결과의 평균뿐 아니라 분산도 함께 봐야 합니다. 결국 확률은 데이터 팀만의 언어가 아니라 운영과 제품 판단의 공통 언어입니다.

좋은 엔지니어는 숫자를 보자마자 조건이 무엇인지 먼저 묻습니다. 이 확률은 어떤 사건에 대한 값인지, 어떤 분포를 가정하는지, 평균만 보면 되는지 아니면 흔들림도 같이 봐야 하는지 확인합니다.

---

## 체크리스트

- [ ] 표본공간과 사건을 구분할 수 있습니다.
- [ ] 어떤 조건이 붙은 확률인지 말할 수 있습니다.
- [ ] 베이즈 정리의 입력값이 무엇인지 설명할 수 있습니다.
- [ ] 기댓값과 분산의 역할 차이를 설명할 수 있습니다.
- [ ] 독립성 가정을 무심코 두면 왜 위험한지 이해했습니다.

## 연습 문제

1. 조건부 확률을 한 줄로 정의해 보세요.
2. 베이즈 정리를 한 문장으로 설명해 보세요.
3. 기댓값과 분산의 차이를 정리해 보세요.

## 정리

확률은 불확실성을 포기하지 않고 다루는 방법입니다. 표본공간, 사건, 조건부 확률, 베이즈 정리, 기댓값과 분산을 익히면 감으로만 판단하던 영역을 훨씬 차분하게 다룰 수 있습니다. 다음 글에서는 데이터를 다루는 또 다른 핵심 언어인 선형대수를 보겠습니다.


## 베이즈 정리를 진단 시나리오로 풀기

베이즈 정리는 증거가 들어온 뒤 믿음을 갱신하는 규칙입니다. 의료 검사, 스팸 필터, 이상 탐지에서 거의 같은 형태로 등장합니다.

```python
def bayes_posterior(p_pos_given_disease: float, p_disease: float, p_pos: float) -> float:
    return (p_pos_given_disease * p_disease) / p_pos

# 예시 수치
p_disease = 0.01
p_pos_given_disease = 0.95
p_pos_given_healthy = 0.10
p_pos = p_pos_given_disease * p_disease + p_pos_given_healthy * (1 - p_disease)
posterior = bayes_posterior(p_pos_given_disease, p_disease, p_pos)
```

여기서 핵심은 양성 판정 정확도가 높아도 유병률(사전 확률)이 낮으면 사후 확률이 생각보다 낮을 수 있다는 점입니다. 숫자 해석에서 가장 흔한 오해를 바로잡는 지점입니다.

## 분포 비교 표

| 분포 | 값의 성격 | 대표 예시 | 핵심 파라미터 |
| --- | --- | --- | --- |
| Bernoulli | 0/1 단일 시행 | 클릭 여부 | `p` |
| Binomial | 성공 횟수 | n회 중 성공 수 | `n, p` |
| Poisson | 단위 시간 사건 수 | 분당 요청 수 | `lambda` |
| Normal | 연속값 근사 | 측정 오차 | `mu, sigma` |

분포 선택은 모델 선택입니다. 잘못된 분포 가정은 좋은 코드로도 고치기 어렵습니다.

## 기대값이 같아도 위험이 다른 사례

두 선택지 A, B가 기대값은 같지만 분산이 다르면 운영 의사결정이 달라질 수 있습니다.

```python
def expected_value(values, probs):
    return sum(v * p for v, p in zip(values, probs))


def variance(values, probs):
    mu = expected_value(values, probs)
    return sum(p * (v - mu) ** 2 for v, p in zip(values, probs))
```

A가 안정적인 수익, B가 큰 변동의 수익이라면 같은 평균이어도 리스크 허용도에 따라 선택이 달라집니다. 확률은 "얼마나 자주"뿐 아니라 "얼마나 흔들리는지"까지 함께 보게 만듭니다.

## 몬테카를로로 직관 만들기

해석적 계산이 복잡한 경우 샘플링으로 근사할 수 있습니다.

```python
import random

def estimate_tail_prob(trials: int = 100000) -> float:
    cnt = 0
    for _ in range(trials):
        x = random.random() + random.random()
        if x > 1.6:
            cnt += 1
    return cnt / trials
```

샘플 수를 늘리면 추정치가 안정되는 과정을 관찰할 수 있습니다. 이 방법은 복잡한 폐형식이 없을 때 실무에서 자주 쓰는 전략입니다.

## 확률 모델 리뷰 체크리스트

1. 사건 정의와 분모(전체 공간)가 문서에 명시되어 있는가
2. 독립성 가정이 근거와 함께 기록되어 있는가
3. 평균과 분산을 함께 보고 있는가
4. 수치 실험과 이론 계산을 교차 검증했는가

확률의 목표는 불확실성을 제거하는 것이 아니라, 불확실성을 같은 단위로 비교 가능하게 만드는 것입니다.


## 확률 결과를 제품 지표로 번역하기

확률 계산이 끝난 뒤 실제 의사결정으로 연결하려면 임계값 정책이 필요합니다.

```python
def decide_action(p_risk: float, threshold: float = 0.2) -> str:
    return 'block' if p_risk >= threshold else 'allow'
```

동일한 확률이라도 서비스 성격에 따라 임계값은 달라집니다. 결제 사기 탐지는 보수적으로, 추천 노출은 공격적으로 설정할 수 있습니다. 중요한 점은 임계값을 감으로 두지 않고 비용 함수와 함께 문서화하는 것입니다.


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

### 베이즈 정리 Python 예제

```python
def bayes(p_b_given_a, p_a, p_b_given_not_a, p_not_a):
    p_b = p_b_given_a * p_a + p_b_given_not_a * p_not_a
    return (p_b_given_a * p_a) / p_b

# 질병 유병률 1%, 민감도 95%, 위양성률 5%
result = bayes(0.95, 0.01, 0.05, 0.99)
print(round(result, 4))
```

검사 양성이 곧 높은 사후확률을 뜻하지 않는 이유를 수치로 확인할 수 있습니다. 사전확률이 낮으면 위양성의 영향이 커집니다.

### 분포 비교표

| 분포 | 사용 상황 | 평균 | 분산 | 실무 예시 |
| --- | --- | --- | --- | --- |
| 베르누이 | 성공/실패 한 번 | p | p(1-p) | 클릭 여부 |
| 이항 | 독립 베르누이 n회 | np | np(1-p) | n회 실험 성공 횟수 |
| 포아송 | 단위 시간 희귀 사건 | lambda | lambda | 초당 오류 수 |
| 정규 | 연속 값의 자연 변동 | mu | sigma^2 | 지연 시간 근사 |

### 기댓값/분산 계산 코드

```python
def expected(values, probs):
    return sum(v * p for v, p in zip(values, probs))

def variance(values, probs):
    mu = expected(values, probs)
    return sum(p * (v - mu) ** 2 for v, p in zip(values, probs))

vals = [0, 1, 2, 3]
probs = [0.1, 0.2, 0.5, 0.2]
print(expected(vals, probs), variance(vals, probs))
```

평균이 같아도 분산이 다르면 운영 리스크가 크게 달라집니다. 따라서 성능 지표를 비교할 때 평균만 보는 습관을 버려야 합니다.

### 확률 모델 검증 원칙

독립 가정, 정상성 가정, 표본 대표성은 모두 명시적으로 검증해야 합니다. 모델링 가정을 문서화하지 않으면 계산은 정확해 보여도 결론이 틀릴 수 있습니다.


### 몰테카를로 시뮬레이션

해석적 계산이 어려운 확률 문제는 시뮬레이션으로 근사할 수 있습니다.

```python
import random

def monte_carlo_pi(n: int = 100_000) -> float:
    """단위 원에 점을 랜덤하게 던져 π를 추정합니다."""
    inside = 0
    for _ in range(n):
        x, y = random.random(), random.random()
        if x * x + y * y <= 1.0:
            inside += 1
    return 4 * inside / n

random.seed(42)
print(f"pi estimate: {monte_carlo_pi():.4f}")  # ~3.1416
```

이 방법은 통합 테스트의 성공률 추정, A/B 테스트 신뢰구간 계산, 리스크 분석 등에서 넓게 쓰입니다. 핵심은 표본 수를 늘리면 추정값이 수렴한다는 대수의 법칙입니다.

### 조건부 확률의 함정

조건부 확률에서 가장 흔한 실수는 기저율(base rate)을 무시하는 것입니다.

```python
def false_positive_scenario():
    """
    시스템 이상 탐지 예시:
    - 실제 장애 발생률: 0.1% (1000건 중 1건)
    - 탐지기 민감도: 99% (장애시 알람)
    - 오경보률: 2% (정상인데 알람)
    """
    p_fault = 0.001
    p_alarm_given_fault = 0.99
    p_alarm_given_ok = 0.02
    p_ok = 1 - p_fault

    p_alarm = p_alarm_given_fault * p_fault + p_alarm_given_ok * p_ok
    p_fault_given_alarm = (p_alarm_given_fault * p_fault) / p_alarm

    print(f"알람 발생 확률: {p_alarm:.4f}")
    print(f"알람이 울렸을 때 실제 장애일 확률: {p_fault_given_alarm:.4f}")
    # 알람이 울렸어도 실제 장애일 확률은 ~4.7%에 불과

false_positive_scenario()
```

이 예시는 온콜 모니터링 알람 설계, 보안 이상 탐지, 의료 진단 등에서 반복되는 패턴입니다. 기저율이 낮으면 높은 민감도만으로는 정밀도(precision)를 보장할 수 없습니다.

### 대수의 법칙과 실무 적용

표본 크기가 커질수록 표본 평균이 모평균에 수렴합니다. 이 원리는 A/B 테스트 설계의 근거입니다.

```python
import random

def demonstrate_lln(p_true: float = 0.52, trials: list = None):
    """동전 던지기로 대수의 법칙을 확인합니다."""
    if trials is None:
        trials = [10, 100, 1000, 10000, 100000]
    random.seed(123)
    for n in trials:
        heads = sum(1 for _ in range(n) if random.random() < p_true)
        print(f"n={n:>7d}: observed={heads/n:.4f}, true={p_true}")

demonstrate_lln()
# n=     10: observed=0.6000, true=0.52
# n=    100: observed=0.5500, true=0.52
# n=   1000: observed=0.5240, true=0.52
# n=  10000: observed=0.5212, true=0.52
# n= 100000: observed=0.5198, true=0.52
```

A/B 테스트에서 "표본이 충분한가?"를 판단할 때 이 원리가 작동합니다. 표본이 작으면 노이즈가 커서 차이를 신뢰할 수 없고, 표본이 충분하면 작은 차이도 통계적으로 유의해집니다.

### 독립 사건과 종속 사건 구분

두 사건 A, B가 독립이라는 말은 P(A ∩ B) = P(A) × P(B)를 의미합니다. 실무에서 이 가정을 잘못 적용하는 경우가 많습니다.

| 상황 | 독립 여부 | 이유 |
| --- | --- | --- |
| 서로 다른 리전의 서버 장애 | 대체로 독립 | 물리적 분리 |
| 같은 서버의 CPU와 메모리 경고 | 종속 | 리소스 공유 |
| 사용자 A의 클릭과 사용자 B의 클릭 | 독립 | 별개 행위자 |
| 사용자의 첫 클릭과 두 번째 클릭 | 종속 | 세션 내 행동 연쇄 |

독립 가정을 잘못 적용하면 장애 확률을 과소평가하거나 전환율을 잘못 계산합니다. 모델링 전에 "이 두 사건이 정말 독립인가?"를 먼저 묻는 습관이 필요합니다.

### 확률 분포 시각화로 직관 얻기

확률 분포를 코드로 시각화하면 모양이 직관적으로 들어옵니다.

```python
import random
from collections import Counter

def simulate_poisson_histogram(lam: float = 3.0, n: int = 10000):
    """Poisson 분포를 시뮬레이션해 히스토그램으로 보여줍니다."""
    # Poisson 시뮬레이션 (Knuth 알고리즘)
    import math
    samples = []
    for _ in range(n):
        L = math.exp(-lam)
        k, p = 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        samples.append(k - 1)

    counts = Counter(samples)
    max_k = max(counts.keys())
    for k in range(max_k + 1):
        bar = '#' * (counts.get(k, 0) // 50)
        print(f"k={k:2d}: {bar} ({counts.get(k, 0)})")

random.seed(42)
simulate_poisson_histogram()
```

이 코드는 Poisson 분포의 모양을 텍스트 히스토그램으로 보여줍니다. 람다(λ)가 평균이자 분산인 특성을 눈으로 확인할 수 있습니다. 서버 오류 수, 초당 요청 수 같은 희귀 사건 모델링에 Poisson이 자연스럽게 등장하는 이유입니다.

## 처음 질문으로 돌아가기

- **불확실성을 감으로 넘기지 않고 어떻게 수치로 다룰까요?**
  - 본문의 기준은 확률를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **표본공간과 사건은 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **조건부 확률은 왜 문맥을 붙인 확률이라고 할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): 그래프](./04-graphs.md)
- [Math for CS 101 (5/10): 조합](./05-combinatorics.md)
- **확률 (현재 글)**
- 선형대수 (예정)
- 미분 (예정)
- 정보이론 (예정)
- 알고리즘과 수학 (예정)

<!-- toc:end -->

## 참고 자료

- [Probability - Khan Academy](https://www.khanacademy.org/math/statistics-probability/probability-library)
- [Bayes Theorem - Stanford Encyclopedia](https://plato.stanford.edu/entries/bayes-theorem/)
- [Introduction to Probability - Blitzstein](https://projects.iq.harvard.edu/stat110)
- [Python statistics Module](https://docs.python.org/3/library/statistics.html)
- [SciPy GitHub repository](https://github.com/scipy/scipy)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/math-for-cs-101/ko)

Tags: Math, Probability, Statistics, Bayes, Beginner
