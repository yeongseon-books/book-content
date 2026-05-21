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

## 전후 비교

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

## 실전 확장: 경우의 수를 단계별로 계산하는 절차

조합 문제는 공식을 암기하기보다, "선택 순서", "중복 허용 여부", "순서 민감도"를 먼저 판정해야 정확해집니다.

### 워크드 예시 1: 비밀번호 공간

- 소문자 26개, 길이 6, 중복 허용: `26^6 = 308,915,776`
- 대소문자+숫자 62개, 길이 8: `62^8 = 218,340,105,584,896`

탐색 공간은 길이와 문자 집합이 조금만 늘어도 폭발합니다.

### 워크드 예시 2: 순열과 조합 구분

직원 10명 중 발표자 3명을 순서 있게 배치: `10P3 = 10*9*8 = 720`.
같은 조건에서 위원회 3명 선발: `10C3 = 120`.

### 워크드 예시 3: 포함-배제

1부터 200까지에서 2 또는 3 또는 5의 배수 개수:

- `|A2|=100`, `|A3|=66`, `|A5|=40`
- `|A2∩A3|=33`, `|A2∩A5|=20`, `|A3∩A5|=13`
- `|A2∩A3∩A5|=6`

따라서
`100+66+40-33-20-13+6 = 146`.

### 계산 코드 앵커

```python
import math

def npr(n: int, r: int) -> int:
    return math.factorial(n) // math.factorial(n - r)

def ncr(n: int, r: int) -> int:
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))

print("10P3", npr(10, 3))
print("10C3", ncr(10, 3))
```

### 비둘기집 원리 워크드 예시

365일보다 많은 366명을 모으면 반드시 생일이 같은 두 사람이 있습니다. 일반화하면 상자 `m`개에 물건 `m+1`개를 넣으면 어떤 상자에는 최소 2개가 들어갑니다. 해시 충돌, 샤딩 불균형, 로그 파티션 설계에서 자주 쓰이는 직관입니다.

### 짧은 증명 앵커

명제: `nCk = nC(n-k)`.

증명: `nCk = n!/(k!(n-k)!)`이고 `k`와 `n-k`를 바꾸어도 값이 같습니다. 의미적으로는 `k`개를 고르는 일과 `고르지 않을 n-k개`를 고르는 일이 1:1 대응됩니다.

## 심화 워크숍: 조합 계산 실수 줄이기

### 중복 조합과 별-막대 기법

서로 구분되지 않는 공 10개를 상자 3개에 나누는 경우의 수는 `x1+x2+x3=10`의 음이 아닌 정수해 개수와 같습니다. 별-막대 기법으로 `C(10+3-1,3-1)=C(12,2)=66`입니다.

### 포함-배제 확장 예시

1000개 ID 중 규칙 위반 집합을 `A(길이<8)`, `B(숫자 없음)`, `C(특수문자 없음)`이라 두면 안전하지 않은 개수는
`|A∪B∪C| = |A|+|B|+|C|-|A∩B|-|A∩C|-|B∩C|+|A∩B∩C|`.

현업에서는 이 식을 대시보드 지표로 그대로 구현해 품질 상태를 모니터링합니다.

### 확률 연결

조합은 확률 계산의 분모를 제공합니다. 예를 들어 52장 카드에서 5장을 뽑는 전체 경우는 `52C5`이고, 풀하우스 사건의 경우를 나눠 확률을 계산할 수 있습니다.

### 구현 앵커: 큰 수 안정 계산

```python
from math import comb

def hypergeom_success(total: int, success: int, draw: int, k: int) -> float:
    return comb(success, k) * comb(total - success, draw - k) / comb(total, draw)
```

`comb`를 사용하면 팩토리얼 중간 오버플로를 피하면서 정확한 조합 값을 얻을 수 있습니다.

## 부록: 검증 가능한 실습 패턴 모음

아래 패턴은 각 장의 개념을 실습으로 고정하기 위한 공통 템플릿입니다. 핵심은 계산 결과를 맞히는 것보다, 어떤 정의를 적용했는지 문장으로 남기는 것입니다.

### 패턴 1: 정의를 먼저 쓰고 계산하기

1. 문제에서 사용하는 대상 집합을 명시합니다.
2. 관계 또는 함수를 기호로 정의합니다.
3. 계산을 수행하고, 결과가 정의를 만족하는지 다시 확인합니다.

이 순서를 지키면 중간에 식이 길어져도 논리의 출발점을 잃지 않습니다.

### 패턴 2: 반례를 의도적으로 만들기

정리나 가설을 세웠다면, 반례 후보를 최소 3개 만듭니다.

- 경계값 입력(0, 1, 최대값)
- 중복/충돌 입력
- 공집합 또는 단일 원소 입력

반례가 발견되면 결론을 버리는 것이 아니라, 가정과 정의를 수정합니다. 이 절차가 수학적 엄밀성과 엔지니어링 실용성을 동시에 만족시킵니다.

### 패턴 3: 표와 코드 출력을 함께 남기기

진리표, 집합 연산표, 점화식 전개표 중 하나를 반드시 포함합니다. 그리고 같은 내용을 계산하는 짧은 코드를 붙여 결과를 재현합니다.

```python
def verify_identity(left: set[int], right: set[int]) -> bool:
    return left == right
```

작은 검증 함수 하나라도 문서에 남기면 팀원 간 해석 차이를 줄일 수 있습니다.

### 패턴 4: 증명 구조를 고정하기

증명은 다음 네 문장 구조를 기본으로 씁니다.

- 가정: 무엇을 참이라고 두는가
- 전개: 어떤 정의/정리를 사용해 변형하는가
- 핵심 전환: 결론으로 넘어가는 결정적 단계는 무엇인가
- 결론: 원래 명제가 왜 성립하는가

이 구조는 직접 증명, 대우 증명, 귀류법, 귀납법 모두에 적용됩니다.

### 패턴 5: 알고리즘과 수학 근거 연결하기

알고리즘 설명에는 다음 항목을 최소로 넣습니다.

- 불변식 1개 이상
- 종료 조건 1개
- 복잡도 식 1개
- 반례 테스트 1개

이 네 항목이 있으면 코드가 바뀌어도 정확성 근거를 유지할 수 있습니다.

### 미니 문제 세트

1. 두 집합 `A`, `B`를 임의로 만들고 `A∩B`, `A∪B`, `A\B`를 계산한 뒤 포함관계를 설명하세요.
2. 명제식 `(P→Q) ∧ (Q→R) → (P→R)`의 진리표를 작성하고 항진명제 여부를 확인하세요.
3. 점화식 `T(n)=T(n-1)+n`의 닫힌형을 추측한 다음 귀납법으로 검증하세요.
4. 인접 리스트 그래프 하나를 만든 뒤 BFS/DFS 방문 순서를 비교하세요.
5. `nCk = nC(n-k)`를 식과 의미 해석(선택 vs 비선택) 두 방식으로 설명하세요.

### 마무리

각 장의 주제가 달라 보여도 훈련 루프는 같습니다. 정의를 선언하고, 계산을 수행하고, 반례로 검증하고, 증명 또는 불변식으로 고정하면 됩니다. 이 루프를 반복하면 새로운 문제에서도 같은 품질로 사고할 수 있습니다.


## 추가 심화: 오류 사례와 교정 로그

실무에서 이산수학 개념이 흔들리는 지점은 대부분 "정의 생략"에서 시작합니다. 아래는 자주 나오는 오류와 교정 방식입니다.

### 오류 사례 1: 조건 누락

- 증상: 코드가 특정 입력에서만 실패합니다.
- 원인: 명제식에서 한 항을 자연어로만 설명하고 코드에 반영하지 않았습니다.
- 교정: 조건을 변수화해 논리식으로 명시하고, 진리표의 위험 조합을 테스트로 고정합니다.

### 오류 사례 2: 집합 경계 불일치

- 증상: 제외되어야 할 원소가 결과에 섞입니다.
- 원인: 전체집합 `U`를 정의하지 않아 여집합 계산이 흔들립니다.
- 교정: `U`를 먼저 확정하고 `A^c = U \ A`를 코드와 문서에 동시에 기록합니다.

### 오류 사례 3: 그래프 방향성 오해

- 증상: 탐색 결과가 기대보다 과도하거나 부족합니다.
- 원인: 유향/무향 그래프를 혼동해 간선을 양방향으로 추가했습니다.
- 교정: 입력 스키마 단계에서 방향성을 필드로 분리하고, 예제 그래프를 최소 1개 유지합니다.

### 오류 사례 4: 점화식 기저 조건 누락

- 증상: 재귀가 종료되지 않거나 값이 어긋납니다.
- 원인: `n=0`, `n=1`에서의 정의를 생략했습니다.
- 교정: 기저 조건을 본문과 코드 첫 줄에 병기하고, 단위 테스트를 별도로 둡니다.

### 교정 루프

1. 정의를 다시 선언합니다.
2. 최소 반례를 구성합니다.
3. 식과 코드를 동시에 수정합니다.
4. 표/출력으로 재검증합니다.

이 루프를 문서화하면 팀 단위 품질이 안정됩니다.


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

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 6](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Combinatorics](https://en.wikipedia.org/wiki/Combinatorics)
- [Wikipedia — Pigeonhole Principle](https://en.wikipedia.org/wiki/Pigeonhole_principle)
- [Wikipedia — Birthday Problem](https://en.wikipedia.org/wiki/Birthday_problem)

Tags: Computer Science, 이산수학, 조합론, 순열, 비둘기집 원리, 확률
