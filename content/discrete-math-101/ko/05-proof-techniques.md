---
series: discrete-math-101
episode: 5
title: "Discrete Math 101 (5/10): 증명 방법"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 이산수학
  - 수학적 증명
  - 귀납법
  - 귀류법
  - 알고리즘 정확성
seo_description: 직접, 대우, 귀류, 귀납 증명과 알고리즘 정확성 검증의 연결을 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (5/10): 증명 방법

이 글은 Discrete Math 101 시리즈의 5번째 글입니다.

## 먼저 던지는 질문

- 직접 증명과 대우 증명은 언제 쓰일까요?
- 귀류법은 어떤 명제에서 특히 강력할까요?
- 수학적 귀납법과 강한 귀납법은 어떻게 작동할까요?

## 큰 그림

![Discrete Math 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/05/05-01-big-picture.ko.png)

*Discrete Math 101 5장 흐름 개요*

## 왜 중요한가

테스트는 버그의 존재를 보여 줄 수는 있어도 부재를 보장하지는 못합니다. 분산 합의 알고리즘, 암호 프로토콜, 컴파일러 최적화는 모두 결국 형식적 증명을 필요로 합니다. 재귀 함수의 정확성은 귀납법으로, 종료성은 잘 기초가 잡힌 측도 감소로 증명합니다.

> 증명은 모든 입력에 대한 보장입니다.

## 한눈에 보는 개념

> 어떤 증명 기법을 선택할지는 명제의 형태가 결정합니다. `P → Q`는 직접이나 대우, `¬P`류는 귀류, `∀n: P(n)`은 귀납이 자연스럽습니다.

```text
   Statement to prove
        │
   ┌────┼────────────┬─────────────┐
   ↓    ↓            ↓             ↓
  P→Q  P→Q          ¬P            ∀n: P(n)
  Direct Contrap.   Contradict.   Induction
                                    │
                                    ↓
                             Base + Inductive step
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Direct proof | P를 가정하고 Q를 도출 |
| Contrapositive | ¬Q를 가정하고 ¬P를 도출 |
| Contradiction | ¬P를 가정하고 모순을 유도 |
| Induction | 기저 사례와 귀납 단계로 전체를 보임 |
| Tautology | 모든 경우에 참인 명제 |

## Before / After

**Before — no proof:**

```python
# "100 tests passed, so it must work" — no guarantee on all inputs
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
```

**After — correctness reasoning attached:**

```python
def gcd(a: int, b: int) -> int:
    """Euclidean algorithm.

    Correctness: gcd(a, b) = gcd(b, a mod b) (mathematical theorem)
    Termination: b strictly decreases each iteration on the naturals → well-founded
    """
    while b:
        a, b = b, a % b
    return a
```

## 단계별로 따라가기

### 1단계: 직접 증명

```python
# Claim: the square of an even number is even
# Proof: assume n = 2k. Then n² = 4k² = 2(2k²), which is even.

def verify_direct(limit: int = 1000) -> bool:
    """Empirical check (the math proof is what really establishes it)"""
    for k in range(limit):
        n = 2 * k
        assert (n ** 2) % 2 == 0
    return True

print(f"Verified: {verify_direct()}")
```

직접 증명은 가장 기본적이고도 가장 강력한 방식입니다. 다만 코드 검증과 수학적 증명은 다르다는 점을 분리해서 봐야 합니다. 코드로 몇 천 개 사례를 돌려 보는 것은 확인일 뿐, 증명 자체는 아닙니다.

### 2단계: 대우 증명

```python
# Claim: if n² is even, then n is even
# Direct is awkward, but the contrapositive is easy:
# Contrapositive: if n is odd, then n² is odd.
# n = 2k + 1 → n² = 4k² + 4k + 1 = 2(2k² + 2k) + 1 → odd

def contrapositive_check(limit: int = 1000) -> None:
    for n in range(limit):
        if n % 2 == 1:           # n odd
            assert (n ** 2) % 2 == 1   # n² odd

contrapositive_check()
print("Contrapositive cases verified")
```

대우 증명은 `P → Q`를 `¬Q → ¬P`로 바꾸어 푸는 방식입니다. 원문보다 대우가 훨씬 쉬운 경우가 많고, 두 명제는 논리적으로 완전히 동치입니다.

### 3단계: 귀류법

```python
# Claim: √2 is irrational
# Assume √2 = p/q in lowest terms. Then 2q² = p².
# → p² is even → p is even → p = 2k
# → 2q² = 4k² → q² = 2k² → q² is even → q is even
# → both p and q even ⊥ "lowest terms" assumption

import math

def is_rational_approx(x: float, max_q: int = 10000) -> bool:
    """Empirical: does x have an exact fraction with denominator ≤ max_q?"""
    for q in range(1, max_q):
        p = round(x * q)
        if abs(x - p / q) < 1e-15:
            return True
    return False

print(f"Is √2 expressible as fraction with q ≤ 10000? {is_rational_approx(math.sqrt(2))}")
```

귀류법은 결론의 부정을 가정하고, 그 가정이 모순으로 이어짐을 보입니다. 분산 시스템의 불가능성 정리처럼 직접적인 구성보다 “그럴 수 없음을 보이는” 문제가 특히 이 기법과 잘 맞습니다.

### 4단계: 수학적 귀납법

```python
# Claim: 1 + 2 + ... + n = n(n+1)/2
# Base P(1): 1 = 1·2/2 = 1 ✓
# Inductive step: assuming P(k), prove P(k+1)
#   1 + 2 + ... + k + (k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2 ✓

def gauss_sum(n: int) -> int:
    return n * (n + 1) // 2

def actual_sum(n: int) -> int:
    return sum(range(1, n + 1))

for n in [1, 10, 100, 1000]:
    assert gauss_sum(n) == actual_sum(n)
    print(f"n={n}: formula={gauss_sum(n)}, actual={actual_sum(n)}")
```

귀납법은 가장 작은 사례를 먼저 고정하고, 거기서 다음 사례로 넘어가는 사슬을 만드는 방식입니다. 재귀 정의와 반복문의 올바름을 증명할 때 거의 표준 도구처럼 쓰입니다.

### 5단계: 알고리즘 정확성 증명

```python
# Claim: this returns the correct index of target in a sorted array,
# or -1 if absent.

def binary_search(arr: list, target: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        # Invariant: if target is in arr, it lies in arr[low..high]
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

# Termination: high - low strictly decreases each iteration
# Correctness: loop invariant + termination condition
# Both formal proofs use induction.

for arr, target in [([1, 3, 5, 7, 9], 5), ([1, 3, 5, 7, 9], 4)]:
    print(f"binary_search({arr}, {target}) = {binary_search(arr, target)}")
```

루프 불변식은 알고리즘 정확성 증명의 핵심입니다. 반복문이 한 번 돌 때마다 무엇이 항상 유지되는지를 잡아내면, 종료 시점에 왜 정답이 되는지도 자연스럽게 따라옵니다.

## 주목할 점

- 검증과 증명은 다릅니다. 검증은 일부 사례를, 증명은 전체 경우를 다룹니다.
- 직접 증명이 어렵다면 대우나 귀류가 더 자연스러울 수 있습니다.
- 귀납법은 자연수와 재귀 구조의 표준 증명 도구입니다.
- 알고리즘 정확성은 루프 불변식 위에 세워집니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 검증을 증명으로 착각한다 | 일부 입력만 확인하고 끝낸다 | 형식적 논증을 따로 세운다 |
| 귀납법의 기저를 생략한다 | 시작점 없는 사슬이 된다 | P(0) 또는 P(1)을 명시한다 |
| 귀류법의 부정을 잘못 잡는다 | 무엇을 가정한 것인지 흐려진다 | 원명제의 정확한 부정을 먼저 쓴다 |
| 역과 대우를 혼동한다 | 잘못된 명제를 증명한다 | 동치는 대우뿐임을 기억한다 |
| 종료성 증명을 빼먹는다 | 정답을 내더라도 끝나지 않을 수 있다 | 감소하는 well-founded 측도를 제시한다 |

## 실무에서는 이렇게 사용합니다

- Paxos, Raft 같은 합의 알고리즘의 안전성과 생존성을 증명합니다.
- 암호 프로토콜의 보안 속성을 형식적으로 분석합니다.
- 컴파일러 최적화가 의미를 보존하는지 증명합니다.
- TLA+, Coq, Lean 같은 도구는 이런 사고를 기계화합니다.
- 코드 리뷰의 “이게 항상 맞나요?”라는 질문은 비공식 증명입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 코드를 읽을 때 머릿속에서 작은 증명을 돌립니다. “루프 불변식이 무엇인가”, “무엇이 감소하는가”, “종료 조건에 도달한 뒤 무엇이 보장되는가”를 자연스럽게 따집니다. 테스트를 많이 돌리는 것과 별개로, 증명 스타일의 사고가 정확성의 마지막 안전장치가 됩니다.

## 체크리스트

- [ ] 네 가지 증명 기법을 설명할 수 있다
- [ ] 귀납법의 두 단계(기저, 귀납 단계)를 기억한다
- [ ] 역과 대우를 구분할 수 있다
- [ ] 루프 불변식의 역할을 이해한다
- [ ] 검증과 증명의 차이를 명확히 안다

## 연습 문제

1. “n이 3으로 나누어떨어지면 n²도 3으로 나누어떨어진다”를 직접 증명해 보세요.

2. `1² + 2² + ... + n² = n(n+1)(2n+1)/6`을 귀납법으로 증명해 보세요.

3. 자신이 작성한 `while` 루프 하나를 골라 루프 불변식과 종료 측도를 적어 보세요.

## 정리 및 다음 단계

증명은 모든 가능한 입력에 대해 정확성을 보장하는 도구입니다. 직접, 대우, 귀류, 귀납이라는 네 가지 기법은 이산수학의 거의 모든 명제를 다루는 기본 세트이며, 알고리즘 정확성 검증에도 그대로 사용됩니다.

다음 글에서는 귀납법과 가장 가까운 주제인 수열과 점화식으로 넘어가겠습니다.

## 실전 보강: 증명, 집합 연산, 그래프 알고리즘을 연결해서 보기

이산수학은 정의를 외우는 과목이 아니라, 명제를 세우고 검증하는 절차를 훈련하는 과목입니다. 아래 내용은 증명 예시, 집합 연산표, 그래프 알고리즘을 하나의 흐름으로 연결합니다.

### 1) 짧은 직접 증명 예시

명제: 임의의 정수 `n`에 대해 `n`이 짝수이면 `n^2`도 짝수입니다.

증명: `n`이 짝수이므로 어떤 정수 `k`가 존재하여 `n = 2k`입니다. 그러면
`n^2 = (2k)^2 = 4k^2 = 2(2k^2)` 이고, `2k^2`는 정수이므로 `n^2`는 짝수입니다.
따라서 명제가 성립합니다.

핵심은 결론을 먼저 믿는 것이 아니라, 정의(짝수의 정의)를 대입해 식을 변형하는 것입니다.

### 2) 집합 연산표로 규칙 확인

전체집합 `U = {1,2,3,4,5,6}`, `A = {1,2,3,4}`, `B = {3,4,5}`일 때:

| 연산 | 결과 |
| --- | --- |
| `A ∪ B` | `{1,2,3,4,5}` |
| `A ∩ B` | `{3,4}` |
| `A \ B` | `{1,2}` |
| `B \ A` | `{5}` |
| `A^c` (in U) | `{5,6}` |

이 표는 드모르간 법칙 검증에도 바로 사용됩니다.
`(A ∪ B)^c = A^c ∩ B^c`를 실제 원소로 계산해 양변이 같음을 확인할 수 있습니다.

### 3) 귀납법 예시

명제: `1 + 2 + ... + n = n(n+1)/2`.

- 기저 단계: `n=1`에서 좌변 `1`, 우변 `1(2)/2 = 1`로 성립.
- 귀납 가정: `n=k`에서 성립한다고 가정.
- 귀납 단계:
  `1+...+k+(k+1) = k(k+1)/2 + (k+1)`
  `= (k+1)(k+2)/2`.

따라서 모든 자연수 `n`에 대해 성립합니다.

귀납법의 핵심은 “k에서 참이면 k+1도 참”이라는 연결 고리를 명시하는 것입니다.

### 4) 그래프 알고리즘: BFS 거리 계산

```python
from collections import deque

def bfs_distance(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    dist = {start: 0}
    q = deque([start])
    while q:
        v = q.popleft()
        for nxt in graph.get(v, []):
            if nxt not in dist:
                dist[nxt] = dist[v] + 1
                q.append(nxt)
    return dist

G = {
    1: [2, 3],
    2: [4],
    3: [4, 5],
    4: [6],
    5: [],
    6: [],
}
print(bfs_distance(G, 1))
```

BFS는 간선 가중치가 동일할 때 최단 거리 계층을 계산합니다. 증명 관점에서는 “큐에서 먼저 나온 정점의 거리는 이미 최단”이라는 불변식을 유지하는 것이 핵심입니다.

### 5) DFS와 BFS 선택 기준

| 기준 | BFS | DFS |
| --- | --- | --- |
| 주 용도 | 최단 거리(무가중치) | 경로 존재성, 사이클 탐지 |
| 자료구조 | Queue | Stack(또는 재귀) |
| 메모리 특성 | 폭이 넓으면 증가 | 깊이가 깊으면 증가 |
| 직관 | 레벨 단위 탐색 | 한 경로 끝까지 탐색 |

문제의 요구가 “최소 단계”인지 “탐색 가능성”인지 먼저 구분하면 알고리즘 선택이 쉬워집니다.

### 6) 이산수학에서 알고리즘으로 넘어갈 때 체크 포인트

- 명제를 자연어로 쓴 뒤 기호화할 수 있는가
- 필요한 정의(짝수, 함수, 관계, 연결성)를 정확히 호출했는가
- 반례 하나로 거짓을 보일 수 있는 문제인지 확인했는가
- 증명 불변식을 코드 루프 불변식으로 옮길 수 있는가

이산수학의 강점은 계산 자체보다 **판단 근거를 명시하는 습관**입니다. 이 습관이 자료구조, 알고리즘, 시스템 설계까지 그대로 이어집니다.

## 처음 질문으로 돌아가기

- **직접 증명과 대우 증명은 언제 쓰일까요?**
  - 본문의 기준은 증명 방법를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **귀류법은 어떤 명제에서 특히 강력할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **수학적 귀납법과 강한 귀납법은 어떻게 작동할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): 관계와 동치관계](./04-relations-and-equivalence.md)
- **증명 방법 (현재 글)**
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Book of Proof — Richard Hammack (Free)](https://www.people.vcu.edu/~rhammack/BookOfProof/)
- [How to Prove It — Daniel Velleman](https://www.cambridge.org/core/books/how-to-prove-it/6D2965D6905658D704B782B9D67E2989)
- [Wikipedia — Mathematical Proof](https://en.wikipedia.org/wiki/Mathematical_proof)
- [MIT OCW — Mathematics for Computer Science, Lecture 2-5](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, 이산수학, 수학적 증명, 귀납법, 귀류법, 알고리즘 정확성
