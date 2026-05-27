---
title: "Math for CS 101 (10/10): 알고리즘과 수학"
series: math-for-cs-101
episode: 10
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
  - Algorithms
  - Complexity
  - Capstone
  - Beginner
last_reviewed: '2026-05-12'
seo_description: 알고리즘 설계에서 수학이 모델, 비용, 한계를 어떻게 드러내는지 정리합니다
---

# Math for CS 101 (10/10): 알고리즘과 수학

알고리즘을 처음 배울 때는 대개 구현에 집중합니다. 동작하면 일단 성공처럼 느껴집니다. 하지만 실제 시스템에서는 그다음 질문이 훨씬 중요합니다. 얼마나 빠른지, 어떤 모델로 바꿔야 풀리는지, 무작위성을 써도 되는지, 더 줄일 수 없는 이론적 한계는 무엇인지 같이 봐야 하기 때문입니다.

이 글은 Math for CS 101 시리즈의 마지막 글입니다.

이 지점에서 수학이 시리즈 전체를 다시 하나로 묶습니다. 조합론은 경우의 수 폭발을 설명하고, 그래프는 문제 구조를 드러내고, 확률은 무작위 알고리즘을 가능하게 하고, 미분은 최적화를 움직이며, 정보이론은 넘을 수 없는 바닥선을 알려 줍니다.

여기서는 앞에서 본 수학 도구들이 알고리즘 설계와 분석에서 어떻게 만나고 서로를 보완하는지 묶어 보겠습니다.

![Math for CS 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/10/10-01-concept-at-a-glance.ko.png)
*Math for CS 101 10장 흐름 개요*
> 알고리즘의 성능과 정확성은 복잡도와 증명으로만 보장되며, 수학은 그 검증의 핵심 도구입니다.

## 먼저 던지는 질문

- 이 시리즈에서 본 수학이 알고리즘 설계에 어떻게 합쳐질까요?
- 조합론은 왜 복잡도 분석과 연결될까요?
- 그래프 모델은 문제 해결 방식 자체를 어떻게 바꿀까요?

## 왜 중요한가

알고리즘을 단순한 구현으로만 보면 동작 여부만 확인하고 끝나기 쉽습니다. 하지만 실제로는 얼마나 빠른지, 어떤 구조로 모델링해야 하는지, 무작위성을 넣어도 되는지, 더 줄일 수 없는 이론적 한계는 무엇인지까지 함께 봐야 합니다.

이 글은 시리즈의 마무리로, 앞에서 다룬 수학 개념들이 알고리즘 설계와 분석에서 어떻게 만나고 서로를 보완하는지 묶어 봅니다. 문제를 수학적으로 본다는 말이 추상적인 구호가 아니라 실제 설계 방법이라는 점을 보여 주는 단계입니다.

---

## 머릿속에 먼저 둘 관점

이 시리즈를 하나로 묶는 가장 중요한 문장은 이것입니다. **알고리즘은 구현 이전에 먼저 모델링되고, 그다음에 분석된다**는 점입니다. 어떤 문제를 그래프로 바꾸면 최단 경로 문제로 정리할 수 있고, 경우의 수를 세어 보면 완전 탐색이 불가능하다는 사실을 빨리 알 수 있습니다.

또 확률을 넣으면 근사와 샘플링이 가능해지고, 미분을 넣으면 최적화 절차를 만들 수 있습니다. 정보이론은 아무리 잘 설계해도 넘을 수 없는 하한을 보여 줍니다. 결국 좋은 알고리즘 설계는 구현 요령보다, 어떤 수학 도구로 문제를 다시 쓸지 정하는 일에 더 가깝습니다.

저는 이 관점을 알고리즘 설계의 멘탈 모델이라고 생각합니다. 코드가 아니라 구조를 먼저 보는 눈입니다.

## 한 장으로 보는 알고리즘과 수학의 연결

---

## 다섯 단계로 보는 수학과 알고리즘의 연결

### 첫 번째 단계 — 경우의 수 폭발을 봅니다

```python
def subsets(n):
    return 2 ** n
```

부분집합 수가 `2 ** n`으로 늘어난다는 사실만 알아도, 어떤 문제는 입력이 조금만 커져도 탐색이 금방 감당하기 어려워진다는 점을 알 수 있습니다. 조합론은 구현을 시작하기 전에 이미 위험 신호를 보여 줍니다.

### 두 번째 단계 — 문제를 그래프로 바꿉니다

```python
from collections import deque

def shortest(G, s, t):
    q, seen = deque([(s, 0)]), {s}
    while q:
        v, d = q.popleft()
        if v == t:
            return d
        for n in G[v]:
            if n not in seen:
                seen.add(n)
                q.append((n, d + 1))
    return -1
```

그래프로 모델링하는 순간 최단 경로라는 잘 알려진 문제로 바뀝니다. 모델 선택이 해결 전략을 결정한다는 뜻입니다. 알고리즘은 종종 구현보다 표현에서 먼저 달라집니다.

### 세 번째 단계 — 무작위성으로 근사합니다

```python
import random

def estimate_pi(n=10000):
    inside = sum(1 for _ in range(n) if random.random() ** 2 + random.random() ** 2 < 1)
    return 4 * inside / n
```

무작위성은 근사와 추정을 가능하게 합니다. 항상 같은 답을 주지는 않지만, 계산량과 정확도 사이에서 실용적인 균형을 만들 수 있습니다. 확률은 여기서 계산 오차를 해석하는 언어가 됩니다.

### 네 번째 단계 — 최적화로 더 나은 해를 찾습니다

```python
def minimize(f, x, lr=0.1, steps=100, h=1e-5):
    for _ in range(steps):
        g = (f(x + h) - f(x - h)) / (2 * h)
        x = x - lr * g
    return x
```

최적화는 알고리즘 설계와 별개가 아닙니다. 비용 함수가 정의되면 더 나은 해를 찾는 과정 자체가 알고리즘이 됩니다. 미분은 그 과정에 방향 정보를 공급합니다.

### 다섯 번째 단계 — 한계를 인정합니다

```python
import math

def lower_bound_bits(probs):
    return sum(-p * math.log2(p) for p in probs if p > 0)
```

정보이론은 압축이나 추정에서 이론적 바닥선을 알려 줍니다. 아무리 구현을 잘해도 이 한계 아래로는 내려갈 수 없습니다. 알고리즘 설계는 가능성뿐 아니라 불가능성도 함께 다루는 일입니다.

---

## 이 코드에서 먼저 볼 점

- 조합론은 지수 폭발이 어디서 오는지 설명합니다.
- 그래프는 문제를 푸는 언어를 바꿉니다.
- 무작위성은 근사와 샘플링을 가능하게 합니다.
- 미분은 최적화 절차를 움직이는 힘입니다.
- 정보이론은 가능한 것과 불가능한 것을 가릅니다.

---

## 어디서 자주 헷갈릴까요?

복잡도 분석 없이 구현부터 밀어붙이는 실수가 가장 흔합니다. 작게는 잘 돌아가 보여도, 경우의 수가 이미 폭발하는 구조라면 나중에 손쓸 수 없게 됩니다.

그래프 모델링이 필요한 문제를 목록 처리로만 보는 것도 자주 나옵니다. 관계 중심 문제를 순차 데이터처럼 다루면 문제 자체가 흐려지고, 잘 알려진 해법도 놓치기 쉽습니다.

무작위 알고리즘의 결과를 결정론적 값처럼 해석하거나, 학습률과 수렴 조건을 무시하는 일도 흔합니다. 또 정보이론이 말하는 하한을 잊고 무한정 더 줄일 수 있다고 믿는 것도 위험합니다. 수학은 바로 이런 기대의 경계를 그어 줍니다.

---

## 실무에서는 이렇게 생각한다

검색 인덱스는 그래프와 정보이론의 영향을 받습니다. 추천 시스템은 선형대수와 확률을 동시에 사용합니다. 학습 시스템은 미분과 확률을 함께 쓰고, 설계 리뷰에서는 거의 항상 복잡도 분석이 따라붙습니다. 개별 분야는 달라도 결국 수학 도구들이 함께 움직입니다.

좋은 엔지니어는 구현 아이디어가 떠오르면 곧바로 묻습니다. 이 문제의 모델은 무엇인지, 비용은 어떻게 커지는지, 근사나 무작위화가 가능한지, 이론적 한계는 어디인지 묻는 습관입니다. 이 질문이 있으면 구현은 더 분명해지고, 설계는 더 설득력 있어집니다.

---

## 체크리스트

- [ ] 알고리즘의 복잡도를 말할 수 있습니다.
- [ ] 문제를 적절한 수학 모델로 바꿀 수 있습니다.
- [ ] 무작위성이 들어가는 부분을 분리해 설명할 수 있습니다.
- [ ] 수렴과 이론적 한계를 함께 볼 수 있습니다.
- [ ] 구현 전에 구조적 위험 신호를 먼저 점검할 수 있습니다.

## 연습 문제

1. 복잡도와 조합론의 연결을 한 줄로 정리해 보세요.
2. 무작위 알고리즘의 장점 하나를 써 보세요.
3. 정보이론이 주는 한계 하나를 설명해 보세요.

## 복잡도 주장도 증명이 필요합니다

알고리즘 설명에서 가장 자주 빠지는 부분은 "왜 `O(n log n)`인지"에 대한 근거입니다. 구현 코드만으로는 점근 상한이 자동으로 보장되지 않습니다. 반복 구조를 점화식으로 쓰고, 이를 푸는 과정이 필요합니다.

```python
def merge_sort_cost(n: int) -> str:
    return 'T(n) = 2T(n/2) + O(n)'
```

이 식은 분할정복 구조를 요약합니다. 각 단계에서 두 하위 문제를 풀고, 병합에 선형 비용이 든다는 가정입니다.

## Master 정리 예시

| 점화식 | a | b | f(n) | 결론 |
| --- | --- | --- | --- | --- |
| `T(n)=2T(n/2)+n` | 2 | 2 | `n` | `Theta(n log n)` |
| `T(n)=2T(n/2)+1` | 2 | 2 | `1` | `Theta(n)` |
| `T(n)=3T(n/2)+n` | 3 | 2 | `n` | `Theta(n^{log_2 3})` |

Master 정리는 분할정복 알고리즘의 성능을 빠르게 분류하는 도구입니다. 단, 전제 조건이 맞는지 먼저 확인해야 합니다.

## 상한/하한/평균을 분리해 기록하기

성능 논의에서 평균만 말하면 위험합니다. 실무에서는 다음을 분리해 기록하는 습관이 필요합니다.

1. 최악 시간복잡도
2. 평균 시간복잡도
3. 공간복잡도
4. 입력 분포 가정

같은 알고리즘도 입력 분포가 바뀌면 체감 성능이 완전히 달라질 수 있습니다.

## 확률적 알고리즘 해석

랜덤화 알고리즘은 단일 실행보다 기대 성능과 오차 확률로 평가합니다.

```python
import random

def randomized_pick(arr: list[int]) -> int:
    return random.choice(arr)
```

단순 예제이지만 관점은 같습니다. 결과 하나의 맞고 틀림보다 반복 실행에서의 통계적 성질을 보는 것이 핵심입니다.

## 모델링이 해법을 바꾼 사례

- 문자열 유사도 문제를 그래프 최단 경로로 바꾸면 동적 계획법과 연결됩니다.
- 캐시 교체 문제를 확률 모델로 보면 기대 미스율 분석이 가능해집니다.
- 압축 문제를 정보이론 하한으로 보면 불가능한 목표를 조기에 배제할 수 있습니다.

즉 수학은 알고리즘 "구현 팁"이 아니라 문제 자체를 다시 쓰는 언어입니다.

## 캡스톤용 최종 체크리스트

1. 문제를 어떤 수학 모델로 표현했는가
2. 올바름 주장을 어떤 증명 전략으로 뒷받침했는가
3. 복잡도 상한을 어떤 근거로 제시했는가
4. 확률/근사 사용 시 오차 한계를 어떻게 설명했는가
5. 이론적 하한으로 배제한 선택지가 있는가

이 다섯 항목을 문서화하면 알고리즘 설계 문서가 구현 기록을 넘어 의사결정 기록으로 바뀝니다.

## 설계 리뷰 문서 예시 틀

알고리즘 문서를 아래 다섯 블록으로 고정하면 팀 커뮤니케이션이 빨라집니다.

```text
1) 문제 모델: 그래프/집합/확률/최적화 중 무엇인가
2) 올바름 주장: 어떤 불변식 또는 증명 전략을 사용했는가
3) 복잡도: 시간/공간 상한과 근거
4) 근사/무작위: 오차 경계와 재현성 정책
5) 한계: 하한 또는 실패 조건
```

이 틀은 시리즈 전편의 내용을 실제 설계 산출물로 바꾸는 최소 단위입니다. 구현 세부를 보지 않아도 의사결정의 품질을 판단할 수 있게 해 줍니다.

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

### Master 정리 예제로 점화식 빠르게 분류하기

분할 정복 점화식은 Master 정리로 1차 분류할 수 있습니다. 예를 들어 병합 정렬의 `T(n) = 2T(n/2) + n`은 `a=2, b=2, f(n)=n`이고 `n^{log_b a}=n`과 같은 차수이므로 `Theta(n log n)`입니다.

```python
import math

def master_case(a, b, k):
    alpha = math.log(a, b)
    if k < alpha:
        return "case1: Theta(n^{log_b a})"
    if abs(k - alpha) < 1e-12:
        return "case2: Theta(n^k log n)"
    return "case3: Theta(n^k) (regularity check needed)"

print(master_case(2, 2, 1))
print(master_case(3, 2, 1))
```

Master 정리는 엄밀 증명 전체를 대체하지 않지만, 설계 초기에 비용 급을 빠르게 분류하는 데 큰 도움이 됩니다.

### 복잡도 증명 패턴

복잡도 증명은 보통 세 패턴으로 정리됩니다. 1) 합 공식 사용, 2) 점화식 전개, 3) 상하한 샌드위치. 구현이 끝난 뒤 벤치마크만 붙이는 것보다, 설계 단계에서 패턴을 적용해 상한을 먼저 제시해야 기술 의사결정이 빨라집니다.

### NP 관련 문제 분류 표

| 문제 | 분류 | 설명 |
| --- | --- | --- |
| 정렬 | P | 다항시간 알고리즘 존재 |
| 최단 경로(음수 사이클 없음) | P | 다익스트라/벨만-포드 등 |
| SAT | NP-Complete | NP 완전의 대표 문제 |
| 해밀토니안 순환 | NP-Complete | 그래프 순환 존재 판정 |
| TSP(결정형) | NP-Complete | 거리 제한 이하 순회 존재 |
| TSP(최적화형) | NP-Hard | 최적해 탐색이 어려움 |

NP 표를 외우는 목적은 시험 대비가 아니라 "정확 최적해" 집착을 줄이는 데 있습니다. NP-Hard 문제를 만나면 근사, 휴리스틱, 문제 완화 전략을 조기에 검토해야 현실적인 일정이 나옵니다.

### 알고리즘 리뷰 체크포인트

알고리즘 설계 리뷰에서는 반드시 다음을 기록합니다. 입력 모델, 최악/평균 복잡도, 증명 스케치, 실패 조건, 근사 허용 범위, 모니터링 지표. 수학적 근거가 문서화되면 구현 변경이 생겨도 품질 기준을 유지할 수 있습니다.

## 상각 분석(Amortized Analysis)

어떤 연산이 가끔 비싸지만 평균적으로는 저렴한 경우, 최악 복잡도만 보면 실제 성능을 과대 평가합니다. 상각 분석은 n번의 연산 전체 비용을 n으로 나누어 한 연산당 평균 비용을 구합니다.

```python
class DynamicArray:
    """동적 배열: append의 상각 O(1)을 보여주는 예시."""

    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity
        self._total_cost = 0  # 누적 비용 추적

    def append(self, value):
        # 용량 초과 시 2배로 확장 (O(n) 복사)
        if self._size == self._capacity:
            self._capacity *= 2
            new_data = [None] * self._capacity
            for i in range(self._size):
                new_data[i] = self._data[i]
            self._data = new_data
            self._total_cost += self._size  # 복사 비용

        self._data[self._size] = value
        self._size += 1
        self._total_cost += 1  # 삽입 비용

    @property
    def amortized_cost(self) -> float:
        return self._total_cost / self._size if self._size else 0

# 실험: 10000번 append 후 상각 비용 확인
arr = DynamicArray()
for i in range(10000):
    arr.append(i)

print(f"총 삽입: {arr._size}")
print(f"총 비용: {arr._total_cost}")
print(f"상각 비용: {arr.amortized_cost:.3f}")  # ~3.0 (O(1))
print(f"최종 용량: {arr._capacity}")  # 16384 (2^14 >= 10000)
```

상각 분석의 세 가지 방법:

| 방법 | 핵심 아이디어 | 적용 예시 |
|------|-------------|----------|
| 집합 분석(Aggregate) | 전체 비용/n | 동적 배열 |
| 회계 분석(Accounting) | 저렴한 연산에 예치금 저축 | 스택 다중 pop |
| 포텐셜 분석(Potential) | 자료구조 '에너지' 함수 정의 | 스플레이 트리 |

Python의 `list.append()`가 O(1) 상각인 이유가 정확히 이 분석에 기반합니다. CPython 소스의 `list_resize()`는 약 1.125배로 성장시켜 메모리 낭비와 복사 빈도 사이의 균형을 잡습니다.

## 마스터 정리(Master Theorem)

분할 정복 알고리즘의 복잡도를 T(n) = aT(n/b) + f(n) 형태로 표현할 때, 마스터 정리로 즉시 해를 구할 수 있습니다.

| Case | 조건 | 결론 |
|------|------|------|
| 1 | f(n) = O(n^(log_b(a) - ε)) | T(n) = Θ(n^log_b(a)) |
| 2 | f(n) = Θ(n^log_b(a)) | T(n) = Θ(n^log_b(a) · log n) |
| 3 | f(n) = Ω(n^(log_b(a) + ε)) | T(n) = Θ(f(n)) |

```python
import math

def master_theorem(a: int, b: int, k: int, p: int = 0) -> str:
    """
    T(n) = aT(n/b) + n^k * (log n)^p 형태의 점화식을 풀어 복잡도를 반환합니다.
    a: 부분 문제 수, b: 분할 비율, k: f(n) = n^k
    """
    c = math.log(a) / math.log(b)  # log_b(a)
    if k < c:
        return f"Case 1: Θ(n^{c:.2f})"
    elif abs(k - c) < 1e-9:
        if p > -1:
            return f"Case 2: Θ(n^{c:.2f} · log^{p+1} n)"
        else:
            return f"Case 2b: Θ(n^{c:.2f} · log log n)"
    else:
        return f"Case 3: Θ(n^{k})"

# 대표적 알고리즘별 적용
examples = [
    ("Merge Sort:  T(n) = 2T(n/2) + n",     2, 2, 1),
    ("Binary Search: T(n) = T(n/2) + 1",    1, 2, 0),
    ("Strassen:   T(n) = 7T(n/2) + n^2",    7, 2, 2),
    ("Karatsuba:  T(n) = 3T(n/2) + n",      3, 2, 1),
]

for desc, a, b, k in examples:
    result = master_theorem(a, b, k)
    print(f"{desc:45s} → {result}")
```

마스터 정리를 외우면 분할 정복 알고리즘의 복잡도를 증명 없이 즉시 판별할 수 있습니다. 면접에서 "Merge Sort의 복잡도를 증명하세요"라는 질문을 받았을 때, 재귀식을 세우고 마스터 정리 Case 2를 적용하면 깔끔하게 답할 수 있습니다.

## 환원(Reduction)과 문제 분류

환원은 '문제 A를 문제 B로 변환'하는 기법입니다. A를 B로 환원할 수 있다면, B가 A보다 어렵거나 같습니다(A ≤_p B).

```python
def reduce_sorting_to_convex_hull():
    """
    정렬 문제를 Convex Hull로 환원하여
    Convex Hull의 하한이 O(n log n)임을 증명합니다.
    """
    # 아이디어: 숫자 x_i 점을 (x_i, x_i^2)로 변환
    # 이 점들의 Convex Hull을 구하면 정렬된 순서가 나옴
    numbers = [5, 2, 8, 1, 9, 3]

    # 환원: 숫자 → 포물선 위의 점
    points = [(x, x**2) for x in numbers]
    print(f"원본 숫자: {numbers}")
    print(f"환원된 점: {points}")
    print()
    print("포물선 위의 점들의 Convex Hull = 좌에서 우로 정렬된 순서")
    print(f"정렬 결과: {sorted(numbers)}")
    print()
    print("논증: 정렬의 하한 O(n log n) ≤ Convex Hull의 복잡도")
    print("따라서 Convex Hull도 Ω(n log n)이다.")

reduce_sorting_to_convex_hull()
```

환원이 실무에서 중요한 이유는 다음과 같습니다.

1. **불가능성 증명**: 새 문제가 NP-Hard임을 보이려면, 알려진 NP-Complete 문제를 새 문제로 환원합니다.
2. **하한 증명**: 정렬의 Ω(n log n) 하한을 환원으로 다른 문제에 전이할 수 있습니다.
3. **설계 전략**: NP-Hard 판정이 나면 정확해 대신 근사/휴리스틱으로 방향을 전환합니다.

## 확률적 알고리즘의 수학적 기반

랜덤 선택을 사용하면 최악 입력에도 기대 성능이 보장됩니다.

```python
import random

def randomized_quickselect(arr: list, k: int) -> int:
    """k번째 작은 원소를 O(n) 기대 시간에 찾습니다."""
    if len(arr) == 1:
        return arr[0]

    pivot = random.choice(arr)
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]

    if k < len(lows):
        return randomized_quickselect(lows, k)
    elif k < len(lows) + len(pivots):
        return pivot
    else:
        return randomized_quickselect(highs, k - len(lows) - len(pivots))

# 성능 측정: 1000번 반복
import time
data = list(range(10000))
random.shuffle(data)

start = time.perf_counter()
for _ in range(1000):
    randomized_quickselect(data[:], 5000)  # 중앙값
elapsed = time.perf_counter() - start

print(f"1000회 median 찾기: {elapsed:.3f}s")
print(f"회당 평균: {elapsed/1000*1000:.3f}ms")
print(f"기대 비교 횟수: O(n) = O(10000)")
```

확률적 분석의 핵심:

- **기대값 선형성**: E[X + Y] = E[X] + E[Y] (독립 여부 무관)
- **지시 확률변수**: 조건을 만족하면 1, 아니면 0인 변수로 복잡한 기대값을 분해
- **유니언 바운드**: P(∪ A_i) ≤ Σ P(A_i) — 불리한 사건의 확률 상한

예를 들어, 랜덤 Quick Sort의 기대 비교 횟수를 구하려면: 원소 i와 j가 비교될 확률 = 2/(j-i+1)이므로, 기대 비교 횟수 = ΣΣ 2/(j-i+1) = O(n log n)입니다. 지시 확률변수와 선형성이 없으면 이 증명은 매우 복잡해집니다.
## 정리

이 글로 Math for CS 101 시리즈를 마칩니다. 수학은 코드를 어렵게 만드는 장벽이 아니라, 코드를 더 잘 설계하고 더 빨리 한계를 파악하게 해 주는 지도입니다. 문제를 수학적으로 볼 수 있게 되면 구현은 더 분명해지고, 분석은 더 설득력 있어집니다.

## 처음 질문으로 돌아가기

- **이 시리즈에서 본 수학이 알고리즘 설계에 어떻게 합쳐질까요?**
  - 이 글은 `subsets(n)`, `shortest(G, s, t)`, `estimate_pi`, `minimize`, `lower_bound_bits`를 한 흐름으로 묶어 조합론·그래프·확률·미분·정보이론이 알고리즘 설계의 서로 다른 레버임을 보여 주었습니다. 설계 리뷰 템플릿도 문제 모델, 올바름 주장, 복잡도, 근사/무작위, 한계를 함께 적게 만들어 시리즈 전편의 개념이 실제 문서 형식으로 닫히게 했습니다.
- **조합론은 왜 복잡도 분석과 연결될까요?**
  - 경우의 수를 세지 못하면 탐색 공간이 언제 폭발하는지 알 수 없기 때문입니다. `2 ** n` 부분집합 수, 점화식 `T(n) = 2T(n/2) + O(n)`, Master 정리 표, 상각 분석의 누적 비용 계산은 모두 복잡도 주장이 결국 셈과 구조 분석 위에 서 있음을 보여 줍니다.
- **그래프 모델은 문제 해결 방식 자체를 어떻게 바꿀까요?**
  - 문제를 그래프로 바꾸는 순간 목록 처리로 보이던 일이 최단 경로, 위상 정렬, 사이클 탐지 같은 표준 문제로 재정의됩니다. 이 글에서도 문자열 유사도·캐시·압축 사례를 다시 모델링해, 표현을 바꾸는 일 자체가 알고리즘 선택과 증명 전략을 함께 바꾸는 출발점임을 강조했습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Math for CS 101 (4/10): 그래프](./04-graphs.md)
- [Math for CS 101 (5/10): 조합](./05-combinatorics.md)
- [Math for CS 101 (6/10): 확률](./06-probability.md)
- [Math for CS 101 (7/10): 선형대수](./07-linear-algebra.md)
- [Math for CS 101 (8/10): 미분](./08-calculus.md)
- [Math for CS 101 (9/10): 정보이론](./09-information-theory.md)
- **알고리즘과 수학 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms - CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Algorithm Design - Kleinberg and Tardos](https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003259)
- [Randomized Algorithms - Motwani and Raghavan](https://www.cambridge.org/9780521474658)
- [Convex Optimization - Boyd and Vandenberghe](https://web.stanford.edu/~boyd/cvxbook/)
- [TheAlgorithms/Python GitHub repository](https://github.com/TheAlgorithms/Python)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/math-for-cs-101/ko)

Tags: Math, Algorithms, Complexity, Capstone, Beginner
