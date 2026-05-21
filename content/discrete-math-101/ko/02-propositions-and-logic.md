---
series: discrete-math-101
episode: 2
title: "Discrete Math 101 (2/10): 명제와 논리"
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
  - 명제 논리
  - 추론
  - 진리표
  - 술어 논리
seo_description: 명제, 진리값, 논리 연산자, 진리표, 술어와 양화사로 컴퓨터 추론의 기초를 정리합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (2/10): 명제와 논리

이 글은 Discrete Math 101 시리즈의 2번째 글입니다.

## 먼저 던지는 질문

- 명제와 비명제는 어떻게 구분할까요?
- 다섯 가지 기본 논리 연산자는 어떻게 동작할까요?
- 진리표로 논리적 동치를 어떻게 확인할까요?

## 큰 그림

![Discrete Math 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/02/02-01-big-picture.ko.png)

*Discrete Math 101 2장 흐름 개요*

## 왜 중요한가

모든 `if` 문은 명제의 평가입니다. 모든 데이터베이스 질의는 어떤 술어가 만족되는지 묻습니다. 모든 디지털 회로 게이트는 논리 연산입니다. 명제 논리를 이해하지 못하면 복잡한 조건문을 줄이거나, 조건의 의미를 엄밀하게 검증하거나, 엣지 케이스를 자신 있게 다룰 수 없습니다.

> 명제 논리는 정확한 추론을 위한 기호 체계입니다.

이 글에서 세운 논리의 기초는 다음 글의 집합 이론으로 자연스럽게 이어집니다.

## 한눈에 보는 개념

> 명제는 진리값을 가지고, 논리 연산자는 그 진리값을 결합합니다. 연산의 의미는 모두 진리표로 정의됩니다.

```text
  Props P, Q  ──→  Operators  ──→  Compound prop.
                 ┌──────────┐
                 │ ¬ (NOT)  │
                 │ ∧ (AND)  │
                 │ ∨ (OR)   │
                 │ → (impl) │
                 │ ↔ (iff)  │
                 └──────────┘
                       ↓
                  Truth tables
                       ↓
                Logical equivalence
```

## 핵심 용어

| 용어 | 기호 | 의미 |
| --- | --- | --- |
| Negation | ¬P | P가 거짓일 때 참 |
| Conjunction | P ∧ Q | 둘 다 참일 때만 참 |
| Disjunction | P ∨ Q | 하나 이상 참이면 참 |
| Implication | P → Q | P 참, Q 거짓일 때만 거짓 |
| Biconditional | P ↔ Q | 두 진리값이 같을 때 참 |

## Before / After

**Before — without logic:**

```python
# Nested conditions, no simplification
if not (x > 0 and y > 0):
    if not (x > 0):
        handle_x()
    if not (y > 0):
        handle_y()
```

**After — De Morgan's law applied:**

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
if x <= 0 or y <= 0:
    if x <= 0:
        handle_x()
    if y <= 0:
        handle_y()
```

## 단계별로 따라가기

### 1단계: 명제와 진리값

```python
# A proposition is unambiguously true or false
# A question is not a proposition

propositions = {
    "2 is even": True,
    "Paris is the capital of the United States": False,
    "100 is prime": False,
    "1 + 1 = 2": True,
}

for statement, truth in propositions.items():
    print(f"{statement}: {truth}")
```

명제는 참이나 거짓이 분명해야 합니다. 질문, 명령, 감탄처럼 진리값이 정해지지 않는 문장은 명제가 아닙니다. 이 구분이 흐려지면 이후의 모든 논리식도 애매해집니다.

### 2단계: 기본 연산자

```python
def NOT(p: bool) -> bool:
    return not p

def AND(p: bool, q: bool) -> bool:
    return p and q

def OR(p: bool, q: bool) -> bool:
    return p or q

def IMPLIES(p: bool, q: bool) -> bool:
    """P → Q: false only when P true and Q false"""
    return (not p) or q

def IFF(p: bool, q: bool) -> bool:
    """P ↔ Q: true when both have the same value"""
    return p == q

print(IMPLIES(True, False))  # False
print(IMPLIES(False, True))  # True (false premise → always true)
print(IFF(True, True))       # True
```

초보자가 가장 많이 놀라는 부분은 함의입니다. `P → Q`는 P가 거짓이면 참이 됩니다. “비가 오면 우산을 챙긴다”는 약속은 비가 오지 않은 날 위반되지 않는다고 생각하면 직관이 맞춰집니다.

### 3단계: 진리표 생성

```python
from itertools import product

def truth_table(variables: list[str], expr) -> None:
    """Print the truth table for a given expression."""
    header = " | ".join(variables) + " | result"
    print(header)
    print("-" * len(header))
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        result = expr(**env)
        row = " | ".join(str(v)[0] for v in values) + f" | {str(result)[0]}"
        print(row)

# Truth table for (P ∧ Q) → P
truth_table(["P", "Q"], lambda P, Q: IMPLIES(AND(P, Q), P))
```

진리표는 명제 논리의 실행 표와 같습니다. 입력 조합을 모두 열거하기 때문에 동치 여부를 가장 확실하게 확인할 수 있습니다.

### 4단계: 드모르간 법칙 검증

```python
# ¬(P ∧ Q) ≡ ¬P ∨ ¬Q
# ¬(P ∨ Q) ≡ ¬P ∧ ¬Q

def equivalent(expr1, expr2, variables: list[str]) -> bool:
    """Two expressions are equivalent if they agree on every input."""
    for values in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, values))
        if expr1(**env) != expr2(**env):
            return False
    return True

lhs = lambda P, Q: NOT(AND(P, Q))
rhs = lambda P, Q: OR(NOT(P), NOT(Q))

print(f"De Morgan holds: {equivalent(lhs, rhs, ['P', 'Q'])}")
```

코드 리뷰에서 자주 쓰는 조건문 단순화는 대부분 이런 동치 변형입니다. 논리식이 짧아질수록 버그 표면적도 함께 줄어듭니다.

### 5단계: 술어와 양화사

```python
# A predicate is a proposition-valued function over a variable
def is_even(n: int) -> bool:
    return n % 2 == 0

# Universal ∀: "for all n"
def for_all(domain, predicate) -> bool:
    return all(predicate(x) for x in domain)

# Existential ∃: "there exists an n"
def there_exists(domain, predicate) -> bool:
    return any(predicate(x) for x in domain)

numbers = [2, 4, 6, 8, 10]

print(f"∀x ∈ {numbers}: x is even = {for_all(numbers, is_even)}")
print(f"∃x ∈ [1,2,3]: x is even = {there_exists([1, 2, 3], is_even)}")
```

양화사는 술어를 실제 명제로 닫아 주는 도구입니다. SQL의 `ALL`, `ANY`와 직접 이어진다고 보면 훨씬 실용적으로 이해할 수 있습니다.

## 주목할 점

- 모든 논리 연산자는 진리표로 정의됩니다.
- `P → Q`는 `¬P ∨ Q`와 논리적으로 같습니다.
- 드모르간 법칙은 부정이 분배되는 방식을 통제합니다.
- 양화사 ∀, ∃는 술어를 명제로 바꿉니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 함의를 직관적으로만 읽는다 | “거짓 전제면 참”이 계속 낯설다 | 정의를 진리표 기준으로 익힌다 |
| AND/OR 우선순위를 대충 처리한다 | 괄호가 빠져 버그가 생긴다 | 복합식은 항상 괄호를 명시한다 |
| 부정을 잘못 분배한다 | `¬(P ∧ Q)`를 잘못 바꾼다 | 드모르간 법칙을 확실히 익힌다 |
| ∀와 ∃의 순서를 바꾼다 | 전혀 다른 명제가 된다 | 양화사 순서를 그대로 유지한다 |
| 술어를 명제로 착각한다 | 자유변수가 남아 의미가 흐려진다 | 양화사로 닫아 준다 |

## 실무에서는 이렇게 사용합니다

- SQL `WHERE` 최적화는 논리적 동치 변형을 활용합니다.
- 코드 리뷰에서는 복잡한 조건문을 드모르간 법칙으로 정리합니다.
- 디지털 회로 설계는 AND, OR, NOT, NAND, NOR 게이트 위에 서 있습니다.
- 형식 검증은 시스템 속성을 명제로 표현합니다.
- 검색 엔진의 불리언 질의는 그대로 명제 논리입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 복잡한 `if` 문을 보면 먼저 “이걸 더 단순하게 만들 수 있는가”를 묻습니다. 머릿속에서 진리표를 그리거나 동치 변형을 적용해 조건을 절반 이하로 줄이는 경우가 흔합니다. 또한 “이 조건은 항상 성립하는가, 가끔만 성립하는가”라는 양화사의 감각으로 엣지 케이스를 점검합니다.

## 체크리스트

- [ ] 다섯 가지 기본 연산자의 진리표를 그릴 수 있다
- [ ] 함의의 의미를 직관적으로 설명할 수 있다
- [ ] 드모르간 법칙을 실제 코드에 적용할 수 있다
- [ ] ∀와 ∃를 SQL 예시로 설명할 수 있다
- [ ] 술어와 명제의 차이를 구분할 수 있다

## 연습 문제

1. `(P → Q) ∧ (Q → R) → (P → R)`의 진리표를 만들어 항진명제인지 확인해 보세요.

2. 자신이 작성한 중첩 `if` 문 하나를 골라 드모르간 법칙으로 단순화해 보세요.

3. 정수 전체에서 `∀x ∃y: x + y = 0`과 `∃y ∀x: x + y = 0`의 참·거짓을 각각 판단하고 이유를 설명해 보세요.

## 정리 및 다음 단계

명제 논리는 모든 컴퓨터 추론의 기초입니다. 다섯 가지 논리 연산자, 진리표, 동치 법칙을 이해하면 복잡한 조건도 정밀하게 조작할 수 있습니다. 여기에 양화사가 더해지면 표현력은 술어 논리로 확장됩니다.

다음 글에서는 논리와 함께 이산수학의 또 다른 기초인 집합과 함수를 살펴보겠습니다.

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

- **명제와 비명제는 어떻게 구분할까요?**
  - 본문의 기준은 명제와 논리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **다섯 가지 기본 논리 연산자는 어떻게 동작할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **진리표로 논리적 동치를 어떻게 확인할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- **명제와 논리 (현재 글)**
- 집합과 함수 (예정)
- 관계와 동치관계 (예정)
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 1](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Stanford Encyclopedia of Philosophy — Propositional Logic](https://plato.stanford.edu/entries/logic-propositional/)
- [Wikipedia — De Morgan's Laws](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
- [MIT OCW — Mathematics for Computer Science, Lecture 1-3](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, 이산수학, 명제 논리, 추론, 진리표, 술어 논리
