---
series: discrete-math-101
episode: 1
title: "Discrete Math 101 (1/10): 이산수학이란 무엇인가?"
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
  - 수학 입문
  - 전공 개요
  - 논리
  - 집합
seo_description: 이산수학의 범위와 연속 수학과의 차이, 그리고 컴퓨터공학의 공용어인 이유를 정리합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (1/10): 이산수학이란 무엇인가?

이 글은 Discrete Math 101 시리즈의 1번째 글입니다.

## 먼저 던지는 질문

- 이산수학과 연속 수학은 무엇이 다를까요?
- 이산수학의 다섯 축은 어떻게 연결될까요?
- 컴퓨터공학 커리큘럼에서 왜 이산수학이 필수일까요?

## 큰 그림

![Discrete Math 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/01/01-01-big-picture.ko.png)

*Discrete Math 101 1장 흐름 개요*

## 왜 중요한가

알고리즘을 분석하려면 점화식과 조합론이 필요합니다. 데이터베이스를 이해하려면 집합과 관계 이론이 필요합니다. 네트워크를 설계하려면 그래프 이론이 필요합니다. 이산수학은 그냥 하나의 수학 과목이 아니라, 컴퓨터공학 전반이 공유하는 사고의 문법입니다.

> 이산수학은 컴퓨터과학자가 생각을 구조화할 때 쓰는 언어입니다.

이 시리즈는 핵심 개념을 한 편씩 분리해서 설명하되, 매번 컴퓨터공학과의 연결을 함께 보여 줍니다.

## 한눈에 보는 개념

> 이산수학은 논리, 집합, 함수, 조합론, 그래프라는 다섯 축 위에 서 있고, 이 모두는 이산성이라는 공통 성질로 묶입니다.

```text
            Logic (propositions, proofs)
                |
        Sets / Functions / Relations
                |
        ┌───────┼───────┐
   Combinatorics  Sequences   Graphs
       (count)   (recurrence) (structure)
        └───────┼───────┘
                |
        Algorithms / Data structures
                |
        Computer science applications
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Discrete | 분리된 단위로 셀 수 있는 성질 |
| Continuous | 끊김 없이 이어지는 성질 |
| Proposition | 참 또는 거짓이 분명한 문장 |
| Set | 서로 구별되는 원소들의 모임 |
| Graph | 정점과 간선으로 이루어진 구조 |

## Before / After

**Before — without discrete math:**

```python
# Hard to answer "why is this O(log n)?"
def binary_search(data, target):
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

**After — with discrete math:**

```python
# Express it as the recurrence T(n) = T(n/2) + 1
# and prove O(log n) via the Master Theorem.
# Also recognize that "sorted array" is a total-order precondition.
def binary_search(data, target):
    """Precondition: data is sorted under a total order.
    Complexity: T(n) = T(n/2) + O(1) ⟹ O(log n)
    """
    low, high = 0, len(data) - 1
    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

## 단계별로 따라가기

### 1단계: 이산과 연속의 차이

```python
# Continuous: infinitely many values in [0, 1]
# Discrete: {0, 1, 2, 3} is clearly countable
import math

continuous_sample = [i * 0.0001 for i in range(10001)]  # an approximation
discrete_set = list(range(11))                          # exact

print(f"Continuous samples: {len(continuous_sample)}")
print(f"Discrete size: {len(discrete_set)}")
print(f"Continuous gap: {continuous_sample[1] - continuous_sample[0]}")
print(f"Discrete gap: {discrete_set[1] - discrete_set[0]}")
```

컴퓨터 메모리는 비트 단위로 나뉘어 있기 때문에 본질적으로 이산적입니다. 부동소수점 수는 실수를 표현하는 것이 아니라 근사합니다. 이 차이를 이해해야 왜 컴퓨터과학의 기초 수학이 미적분보다 이산수학에 더 가까운지 감이 잡힙니다.

### 2단계: 명제와 진리값

```python
# A proposition: a sentence that is unambiguously true or false
def is_prime(n: int) -> bool:
    """Return True if n is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# "7 is prime" is a true proposition
# "9 is prime" is a false proposition
print(f"7 is prime: {is_prime(7)}")  # True
print(f"9 is prime: {is_prime(9)}")  # False
```

명제 논리는 모든 컴퓨터 추론의 출발점입니다. `if`, `while`, SQL의 `WHERE` 절은 모두 결국 명제의 진리값을 평가합니다.

### 3단계: 집합 연산

```python
# Sets are the most basic discrete structure
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6, 7}

print(f"Union A ∪ B: {A | B}")
print(f"Intersection A ∩ B: {A & B}")
print(f"Difference A - B: {A - B}")
print(f"Symmetric difference A △ B: {A ^ B}")
print(f"Subset A ⊆ {A | B}: {A <= (A | B)}")
```

SQL `JOIN`, `UNION`, `INTERSECT`, `EXCEPT`는 모두 집합 연산의 직접적인 응용입니다. 집합을 이해하면 데이터베이스 연산이 갑자기 훨씬 덜 임의적으로 보입니다.

### 4단계: 그래프로 관계 모델링하기

```python
# A graph is built from vertices and edges
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

def neighbors(g: dict, node: str) -> list:
    """Return neighbors of the given vertex."""
    return g.get(node, [])

for node in graph:
    print(f"{node} neighbors: {neighbors(graph, node)}")
```

소셜 네트워크, 도로망, 의존성 트리, 인터넷 라우팅처럼 관계가 있는 거의 모든 구조는 그래프로 표현됩니다. 이산수학의 넓은 응용 범위를 가장 선명하게 보여 주는 분야가 바로 그래프 이론입니다.

### 5단계: 시리즈 로드맵

```python
roadmap = [
    (1, "What Is Discrete Mathematics?", "the big picture"),
    (2, "Propositions and Logic", "truth values, operators, inference"),
    (3, "Sets and Functions", "set ops, domain, range"),
    (4, "Relations and Equivalence", "properties, classes, partitions"),
    (5, "Proof Techniques", "direct, contradiction, induction"),
    (6, "Sequences and Recurrence", "recursion, Master Theorem"),
    (7, "Combinatorics", "permutations, combinations, pigeonhole"),
    (8, "Graph Theory Basics", "vertices, edges, paths, connectivity"),
    (9, "Trees and Graph Traversal", "BFS, DFS, spanning trees"),
    (10, "Discrete Math and Algorithms", "complexity, NP, applications"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## 주목할 점

- 이산 구조는 컴퓨터가 정확하게 표현할 수 있는 거의 유일한 대상입니다.
- 명제, 집합, 그래프는 서로 다른 추상화처럼 보이지만 모두 이산성을 공유합니다.
- 알고리즘 분석은 점화식과 조합론에 기대고 있습니다.
- SQL, 라우팅, 의존성 관리 같은 실무 도구는 이산수학 개념을 거의 그대로 사용합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 이산수학을 순수한 추상 수학으로만 본다 | 알고리즘 분석에서 바로 막힌다 | 모든 개념을 코드와 함께 연결한다 |
| 증명을 암기만 한다 | 새 문제에 적용하지 못한다 | 구조와 동기를 이해한다 |
| 그래프를 그림으로만 이해한다 | 큰 입력에서 다룰 수 없다 | 인접 리스트와 행렬 표현을 함께 익힌다 |
| 조합과 순열을 자주 섞는다 | 경우의 수를 잘못 센다 | 순서가 중요한지 먼저 묻는다 |
| 명제와 술어를 혼동한다 | 형식 논리에서 막힌다 | ∀, ∃ 양화사까지 함께 익힌다 |

## 실무에서는 이렇게 사용합니다

- 데이터베이스 쿼리 최적화는 집합 이론과 관계대수를 사용합니다.
- 의존성 관리 도구(npm, pip)는 그래프 위상 정렬에 의존합니다.
- 분산 합의 알고리즘은 명제 논리와 일관성 증명을 사용합니다.
- 추천 시스템은 그래프 이론 위에 서 있습니다.
- 컴파일러 최적화는 데이터 흐름 그래프를 분석합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 알고리즘을 볼 때 먼저 그 문제를 이산수학의 언어로 다시 표현합니다. “이건 그래프 탐색 문제다”, “이건 집합 분할 문제다”, “이건 점화식으로 풀 수 있다”처럼 구조를 먼저 이름 붙입니다. 문제의 구조를 정확히 부르는 순간 풀이의 절반은 이미 시작된 셈입니다.

또한 정확성에 집착합니다. “거의 맞다”는 말은 엔지니어링에서도 위험합니다. 이산수학이 참과 거짓의 세계라면, 시니어 엔지니어의 설계 감각도 그 기준을 그대로 가져옵니다.

## 체크리스트

- [ ] 이산과 연속의 차이를 자신의 말로 설명할 수 있다
- [ ] 논리, 집합, 함수, 조합론, 그래프의 다섯 축을 말할 수 있다
- [ ] 컴퓨터공학이 왜 이산수학을 필요로 하는지 이해했다
- [ ] SQL JOIN과 집합 연산의 연결을 설명할 수 있다
- [ ] 시리즈 전체 로드맵을 확인했다

## 연습 문제

1. 일상에서 볼 수 있는 이산적 대상 다섯 가지와 연속적 대상 다섯 가지를 찾아 보세요. 그중 컴퓨터가 정확하게 표현할 수 있는 것은 무엇인가요?

2. `binary_search`가 잘못된 값을 반환하는 정렬되지 않은 배열을 하나 만들어 보세요. 어떤 전제가 깨졌나요?

3. 자신의 소셜 네트워크를 그래프로 그려 보세요. 정점은 무엇이고, 간선은 무엇을 뜻하나요?

## 정리 및 다음 단계

이산수학은 셀 수 있는 대상을 다루는 수학이며, 컴퓨터과학의 공용어입니다. 논리, 집합, 함수, 조합론, 그래프라는 다섯 축은 알고리즘, 데이터베이스, 네트워크를 비롯한 거의 모든 핵심 분야와 직접 연결됩니다.

다음 글에서는 이산수학의 가장 작은 단위인 명제와, 모든 컴퓨터 추론을 움직이는 논리 연산자를 살펴보겠습니다.

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

- **이산수학과 연속 수학은 무엇이 다를까요?**
  - 본문의 기준은 이산수학이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **이산수학의 다섯 축은 어떻게 연결될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컴퓨터공학 커리큘럼에서 왜 이산수학이 필수일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **이산수학이란 무엇인가? (현재 글)**
- 명제와 논리 (예정)
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

- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [MIT OCW — Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
- [Wikipedia — Discrete Mathematics](https://en.wikipedia.org/wiki/Discrete_mathematics)
- [Book of Proof — Richard Hammack](https://www.people.vcu.edu/~rhammack/BookOfProof/)

Tags: Computer Science, 이산수학, 수학 입문, 전공 개요, 논리, 집합
