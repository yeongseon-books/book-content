---
series: discrete-math-101
episode: 7
title: "Discrete Math 101 (7/10): 조합과 경우의 수"
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
  - 조합론
  - 순열
  - 비둘기집 원리
  - 확률
seo_description: 순열, 조합, 비둘기집 원리, 포함-배제로 경우의 수와 충돌 확률을 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (7/10): 조합과 경우의 수

이 글은 Discrete Math 101 시리즈의 7번째 글입니다.

## 먼저 던지는 질문

- 곱의 법칙과 합의 법칙은 어떻게 구분할까요?
- 순열과 조합은 언제 달라질까요?
- 이항계수와 파스칼 삼각형은 왜 중요한가요?

## 큰 그림

![Discrete Math 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/07/07-01-big-picture.ko.png)

*Discrete Math 101 7장 흐름 개요*

## 왜 중요한가

암호 키 공간의 크기, 무차별 대입 공격 시간, 생일 역설은 모두 조합론 문제입니다. 어떤 알고리즘이 가능한 모든 입력에서 어떻게 행동할지 평가하려면 먼저 입력 공간의 크기를 알아야 하고, 그 계산을 맡는 것이 조합론입니다.

> 조합론은 가능성의 크기를 정확히 재는 도구입니다.

## 한눈에 보는 개념

> 곱의 법칙과 합의 법칙이라는 두 기본 규칙이 순열, 조합, 이항정리, 비둘기집 원리, 포함-배제로 확장됩니다.

```text
   basic laws
  ┌─────────────┐
  │ product rule │ — independent choices multiply
  │ sum rule     │ — exclusive choices add
  └──────┬───────┘
         ↓
  ┌──────┬──────────┐
  ↓      ↓          ↓
perm. P  comb. C   binomial thm
  │      │          │
  └──┬───┴──────────┘
     ↓
 pigeonhole / inclusion-exclusion
```

## 핵심 용어

| 용어 | 표기 | 설명 |
| --- | --- | --- |
| Permutation | P(n, r) = n!/(n-r)! | n개 중 r개를 순서를 고려해 선택 |
| Combination | C(n, r) = n!/(r!(n-r)!) | n개 중 r개를 순서 없이 선택 |
| Binomial coefficient | (n choose r) | 조합 `C(n, r)`와 동일 |
| Pigeonhole principle | n+1 → n | 적어도 한 칸에는 두 개 이상 들어감 |
| Inclusion-exclusion | \|A∪B\| = \|A\| + \|B\| - \|A∩B\| | 중복 집계를 제거 |

## Before / After

**Before — brute force without counting:**

```python
# "Just try everything" — no idea how long it takes
import itertools
for password in itertools.product("abc", repeat=4):
    pass  # 81 cases — looks small, but...
```

**After — analyzing the space size:**

```python
# 4-char lowercase: 26⁴ = 456,976
# 8-char alphanumeric+symbols: 94⁸ ≈ 6.1 × 10¹⁵
charset = 26
length = 4
print(f"space size: {charset ** length:,}")
```

## 단계별로 따라가기

### 1단계: 곱의 법칙과 합의 법칙

```python
# Product rule: multiply when choices are independent
# Example: 5 shirts, 3 pants → 5 × 3 = 15 outfits

shirts = ["white", "black", "gray", "navy", "beige"]
pants = ["jeans", "chinos", "slacks"]

outfits = [(s, p) for s in shirts for p in pants]
print(f"outfits: {len(outfits)} = {len(shirts)} × {len(pants)}")

# Sum rule: add when choices are exclusive
# Example: lunch is either 4 Korean dishes or 3 Japanese → 4 + 3 = 7
korean = 4; japanese = 3
print(f"lunch options: {korean + japanese}")
```

둘을 섞지 않는 감각이 중요합니다. 동시에 일어나는 독립 선택은 곱하고, 서로 배타적인 선택지는 더합니다.

### 2단계: 순열과 조합

```python
from math import factorial

def permutation(n: int, r: int) -> int:
    """Ordered selection of r items from n."""
    return factorial(n) // factorial(n - r)

def combination(n: int, r: int) -> int:
    """Unordered selection of r items from n."""
    return factorial(n) // (factorial(r) * factorial(n - r))

# Line up 3 people from 5 (order matters)
print(f"P(5, 3) = {permutation(5, 3)}")
# Pick a 3-person committee from 5 (order does not matter)
print(f"C(5, 3) = {combination(5, 3)}")

# Built-in
from itertools import permutations, combinations
print(f"permutations: {len(list(permutations(range(5), 3)))}")
print(f"combinations: {len(list(combinations(range(5), 3)))}")
```

비밀번호는 순열 문제이고, 포커 핸드는 조합 문제입니다. “순서가 의미 있는가”를 먼저 묻는 습관이 실수를 크게 줄입니다.

### 3단계: 이항정리와 파스칼 삼각형

```python
# Binomial theorem: (x + y)ⁿ = Σ C(n, k) xⁿ⁻ᵏ yᵏ
# The coefficients are exactly the combinations.

def pascal_triangle(rows: int) -> list[list[int]]:
    triangle = [[1]]
    for i in range(1, rows):
        prev = triangle[-1]
        new_row = [1] + [prev[j] + prev[j + 1] for j in range(len(prev) - 1)] + [1]
        triangle.append(new_row)
    return triangle

for row in pascal_triangle(7):
    print(" ".join(str(x).rjust(3) for x in row).center(40))

# (x + y)⁴ expansion: coefficients 1, 4, 6, 4, 1
n = 4
print(f"(x+y)^{n} coefficients: {[combination(n, k) for k in range(n + 1)]}")
```

이항정리의 계수가 곧 조합이라는 사실은 대수와 경우의 수가 따로 노는 주제가 아니라는 점을 잘 보여 줍니다.

### 4단계: 비둘기집 원리

```python
# Pigeonhole: put n+1 items in n boxes → at least one box has 2
# Application: hash collisions are inevitable when input > output space

def will_collide(input_space: int, hash_space: int) -> bool:
    return input_space > hash_space

# A 32-bit hash has 4 × 10⁹ outputs.
# Hashing 10 billion IDs into 32 bits guarantees a collision.
print(f"10B → 32-bit collision? {will_collide(10 ** 10, 2 ** 32)}")

# Birthday paradox: with just 23 people, two share a birthday with prob ~50%.
def birthday_collision_prob(n: int, days: int = 365) -> float:
    no_collision = 1.0
    for i in range(n):
        no_collision *= (days - i) / days
    return 1 - no_collision

for n in [10, 23, 50, 100]:
    print(f"n={n}: collision probability = {birthday_collision_prob(n):.3f}")
```

비둘기집 원리는 단순하지만 놀랄 만큼 강력합니다. 모든 입력을 더 짧게 압축하는 무손실 압축기는 존재할 수 없다는 사실도 이 원리의 직접적인 귀결입니다.

### 5단계: 포함-배제

```python
# |A ∪ B| = |A| + |B| - |A ∩ B|
# |A ∪ B ∪ C| = |A| + |B| + |C| - |A∩B| - |A∩C| - |B∩C| + |A∩B∩C|

# Example: 100 students, 60 study English, 40 Japanese, 20 both
def union_two(a: int, b: int, ab: int) -> int:
    return a + b - ab

print(f"studying at least one: {union_two(60, 40, 20)} students")

# Multiples of 2 or 3 or 5 between 1 and 100
def multiples_count(limit: int, n: int) -> int:
    return limit // n

limit = 100
m2, m3, m5 = multiples_count(limit, 2), multiples_count(limit, 3), multiples_count(limit, 5)
m6, m10, m15 = multiples_count(limit, 6), multiples_count(limit, 10), multiples_count(limit, 15)
m30 = multiples_count(limit, 30)

answer = m2 + m3 + m5 - m6 - m10 - m15 + m30
print(f"multiples of 2, 3, or 5 in 1..100: {answer}")
```

포함-배제는 OR 조건이 붙는 순간 거의 자동으로 떠올라야 하는 도구입니다. 데이터베이스 쿼리 옵티마이저가 OR 카디널리티를 추정할 때도 같은 원리를 씁니다.

## 주목할 점

- 조합론은 입력 공간의 정확한 크기를 계산합니다.
- 순열은 순서를 따지고, 조합은 따지지 않습니다.
- 비둘기집 원리는 충돌이 피할 수 없는 이유를 설명합니다.
- 포함-배제는 OR 조건의 개수를 세는 표준 도구입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 순열과 조합을 섞는다 | 경우의 수를 틀리게 센다 | 순서가 중요한지 먼저 묻는다 |
| 곱의 법칙과 합의 법칙을 섞는다 | 독립 선택과 배타 선택을 혼동한다 | 동시에 일어나는지, 둘 중 하나인지 구분한다 |
| 중복 허용을 놓친다 | 같은 원소 재선택을 빼먹는다 | 반복 허용 여부를 먼저 확인한다 |
| 비둘기집 원리를 느슨하게 적용한다 | `n+1 → n` 조건이 빠진다 | 정확한 조건을 써 본다 |
| 포함-배제 부호를 틀린다 | 교집합 항의 더하기·빼기가 뒤집힌다 | 일반 부호 패턴을 유지한다 |

## 실무에서는 이렇게 사용합니다

- 비밀번호 정책의 키 공간 크기를 계산합니다.
- 해시 충돌 확률을 생일 역설로 추정합니다.
- A/B 테스트 표본 크기 계산에 씁니다.
- 데이터베이스 OR 쿼리의 카디널리티를 추정합니다.
- UUID, Snowflake 같은 ID 설계에서 충돌 확률을 판단합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 “이 설계면 충분한가”를 감으로 넘기지 않고 숫자로 답합니다. UUID v4의 충돌 가능성, 32비트 해시의 한계, 비밀번호 정책의 강도는 모두 조합론으로 즉시 계산합니다. 알고리즘을 고를 때도 “가능한 입력 수가 얼마나 큰가”를 먼저 묻습니다.

## 체크리스트

- [ ] 곱의 법칙과 합의 법칙을 구분할 수 있다
- [ ] 순열과 조합 중 무엇을 써야 할지 판단할 수 있다
- [ ] 비둘기집 원리로 해시 충돌의 필연성을 설명할 수 있다
- [ ] 포함-배제로 OR 카디널리티를 계산할 수 있다
- [ ] 생일 역설에 대한 직관이 있다

## 연습 문제

1. 대문자, 소문자, 숫자, 특수문자 8개를 사용하는 8자리 비밀번호의 키 공간을 계산하고 초당 `10⁹`회 추측 시 평균 크랙 시간을 추정해 보세요.

2. 포함-배제로 1부터 1000까지에서 7 또는 11 또는 13의 배수 개수를 구해 보세요.

3. UUID v4 충돌 확률을 생일 역설로 근사해 보세요. 1조 개를 생성했을 때 충돌 가능성은 어느 정도인가요?

## 정리 및 다음 단계

조합론은 가능성의 크기를 재는 수학입니다. 곱과 합의 법칙, 순열과 조합, 이항정리, 비둘기집 원리, 포함-배제는 보안, 해시, 확률, 완전 탐색 분석에서 반복적으로 등장합니다.

다음 글에서는 이산수학의 또 다른 핵심 분야인 그래프 이론으로 넘어가겠습니다.

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

- **곱의 법칙과 합의 법칙은 어떻게 구분할까요?**
  - 본문의 기준은 조합과 경우의 수를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **순열과 조합은 언제 달라질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **이항계수와 파스칼 삼각형은 왜 중요한가요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): 관계와 동치관계](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): 증명 방법](./05-proof-techniques.md)
- [Discrete Math 101 (6/10): 수열과 점화식](./06-sequences-and-recurrence.md)
- **조합과 경우의 수 (현재 글)**
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 6](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Combinatorics](https://en.wikipedia.org/wiki/Combinatorics)
- [Wikipedia — Pigeonhole Principle](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Wikipedia — Birthday Problem](https://en.wikipedia.org/wiki/Birthday_problem)

Tags: Computer Science, 이산수학, 조합론, 순열, 비둘기집 원리, 확률
