---
series: discrete-math-101
episode: 4
title: 관계와 동치관계
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 이산수학
  - 관계
  - 동치류
  - 부분순서
  - 데이터 모델링
seo_description: 이항관계의 성질과 동치관계, 분할, 부분순서, 위상 정렬의 연결을 설명합니다.
last_reviewed: '2026-05-12'
---

# 관계와 동치관계

이 글은 Discrete Math 101 시리즈의 4번째 글입니다.

## 이 글에서 다룰 문제

- 이항관계는 어떻게 정의하고 표현할까요?
- 반사, 대칭, 추이, 반대칭 성질은 어떻게 구분할까요?
- 동치관계와 동치류, 분할은 왜 서로 연결될까요?
- 부분순서와 위상 정렬은 실무에서 어디에 쓰일까요?

> 관계는 곱집합의 부분집합으로서 두 원소 사이의 어떤 연결을 표현합니다. 반사, 대칭, 추이 같은 성질의 조합은 동치관계와 부분순서를 만들고, 이 구조는 분할, 계층, 정렬 문제의 기초가 됩니다. 이 글에서는 관계의 정의부터 동치류, 부분순서, 위상 정렬까지 한 흐름으로 정리합니다.

## 왜 중요한가

관계형 데이터베이스 모델은 이름부터 관계 이론에서 왔습니다. Git 커밋 그래프, npm 의존성 해석, 빌드 도구의 작업 스케줄링은 모두 부분순서 위의 위상 정렬 문제입니다. 객체의 동일성 판단, 캐시 키 설계, 중복 제거는 동치관계 문제입니다.

> 관계는 데이터 사이의 구조를 표현하는 가장 기본적인 도구입니다.

## 한눈에 보는 개념

> 관계는 `(a, b)` 쌍의 집합입니다. 어떤 성질을 만족하느냐에 따라 동치관계, 부분순서 등으로 분류됩니다.

```text
   Relation R ⊆ A × A
        │
   ┌────┴────┬──────────┐
 Reflexive   Symmetric  Transitive
   │         │          │
   └────┬────┘          │
   Equivalence ↔ Partition
                         │
   Refl ∧ Antisym ∧ Trans = Partial order → Topological sort
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Binary relation | A × A의 부분집합 |
| Reflexive | 모든 a에 대해 (a, a)가 포함됨 |
| Symmetric | (a, b)가 있으면 (b, a)도 있음 |
| Transitive | (a, b), (b, c)가 있으면 (a, c)도 있음 |
| Equivalence | 반사, 대칭, 추이를 모두 만족 |

## Before / After

**Before — no relational thinking:**

```python
# Ad-hoc comparison: "are these two objects the same?"
def same_user(a, b):
    return a.id == b.id and a.email == b.email
```

**After — explicit equivalence relation:**

```python
# Group items into equivalence classes — usable as cache keys
def equivalence_class(item, items, eq):
    return {x for x in items if eq(item, x)}
```

## 단계별로 따라가기

### 1단계: 관계 표현하기

```python
# A relation is a set of (a, b) pairs
people = {"alice", "bob", "carol"}
friends = {("alice", "bob"), ("bob", "alice"), ("bob", "carol"), ("carol", "bob")}

print(f"alice's friends: {[b for (a, b) in friends if a == 'alice']}")

# Matrix representation
import numpy as np

names = sorted(people)
n = len(names)
M = np.zeros((n, n), dtype=int)
for a, b in friends:
    M[names.index(a)][names.index(b)] = 1

print(f"Adjacency matrix:\n{M}")
```

관계는 순서쌍 집합으로도, 인접 행렬로도, 인접 리스트로도 표현할 수 있습니다. 이 표현 방식은 뒤에서 그래프 이론으로 자연스럽게 이어집니다.

### 2단계: 핵심 성질 확인하기

```python
def is_reflexive(R: set, A: set) -> bool:
    return all((a, a) in R for a in A)


def is_symmetric(R: set) -> bool:
    return all((b, a) in R for (a, b) in R)


def is_transitive(R: set) -> bool:
    return all(
        (a, c) in R
        for (a, b) in R
        for (b2, c) in R
        if b == b2
    )


def is_antisymmetric(R: set) -> bool:
    return all(
        a == b for (a, b) in R if (b, a) in R
    )


A = {1, 2, 3}
R_eq = {(1, 1), (2, 2), (3, 3), (1, 2), (2, 1)}
print(f"Reflexive: {is_reflexive(R_eq, A)}")
print(f"Symmetric: {is_symmetric(R_eq)}")
print(f"Transitive: {is_transitive(R_eq)}")
```

관계의 분류는 결국 성질 조합의 문제입니다. 이 네 가지 성질을 정확히 구분하지 못하면 동치관계와 부분순서를 계속 혼동하게 됩니다.

### 3단계: 동치관계와 동치류

```python
# Equivalence: reflexive + symmetric + transitive
# Example: integers modulo 3
def mod_equivalent(a: int, b: int, n: int = 3) -> bool:
    return (a - b) % n == 0


numbers = list(range(10))


def equivalence_class(x: int, domain: list, eq) -> set:
    return {y for y in domain if eq(x, y)}


for i in range(3):
    cls = equivalence_class(i, numbers, mod_equivalent)
    print(f"[{i}] = {sorted(cls)}")

# Equivalence classes partition the domain
all_classes = {frozenset(equivalence_class(x, numbers, mod_equivalent)) for x in numbers}
print(f"Partition: {[sorted(c) for c in all_classes]}")
```

동치관계는 항상 분할을 만들고, 분할은 항상 어떤 동치관계를 유도합니다. 중복 제거, 캐시 무효화, 클러스터링은 모두 결국 “어떤 것을 같은 것으로 볼 것인가”를 정의하는 작업입니다.

### 4단계: 부분순서와 하세 다이어그램

```python
# Partial order: reflexive + antisymmetric + transitive
# Example: subset relation ⊆
A = [{1}, {2}, {1, 2}, {1, 2, 3}]


def is_subset_of(x: set, y: set) -> bool:
    return x <= y


# Cover relation: x ⊂ y with no element strictly in between
def covers(x, y, items):
    if x == y or not is_subset_of(x, y):
        return False
    return not any(
        is_subset_of(x, z) and is_subset_of(z, y) and z != x and z != y
        for z in items
    )


for x in A:
    for y in A:
        if covers(x, y, A):
            print(f"{x} ⋖ {y}")
```

부분순서에서는 모든 원소 쌍이 비교 가능할 필요가 없습니다. 디렉터리 구조, 클래스 상속, Git 커밋 DAG를 생각하면 이 특성이 왜 실무적으로 중요한지 바로 드러납니다.

### 5단계: 위상 정렬

```python
from collections import defaultdict, deque


def topological_sort(nodes: list, edges: list[tuple]) -> list:
    """Return a linear order respecting the partial order."""
    graph = defaultdict(list)
    indegree = {n: 0 for n in nodes}
    for a, b in edges:
        graph[a].append(b)
        indegree[b] += 1

    queue = deque([n for n in nodes if indegree[n] == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return result if len(result) == len(nodes) else []


tasks = ["wake_up", "shower", "breakfast", "work"]
deps = [("wake_up", "shower"), ("shower", "breakfast"), ("breakfast", "work")]
print(f"Execution order: {topological_sort(tasks, deps)}")
```

위상 정렬은 부분순서의 모든 제약을 만족하는 선형 순서를 만들어 냅니다. 빌드 시스템, 패키지 매니저, 작업 스케줄러가 이 알고리즘을 기본으로 쓰는 이유가 여기에 있습니다.

## 주목할 점

- 관계는 곱집합의 부분집합이라는 단순한 정의에서 시작하지만 매우 풍부한 구조를 만듭니다.
- 동치관계와 분할은 사실상 같은 정보를 다른 방식으로 본 것입니다.
- 부분순서는 전순서보다 약하지만 훨씬 더 일반적입니다.
- 위상 정렬은 사이클이 없는 경우에만 가능합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 동치관계 성질 하나를 빼먹는다 | 반사성이나 추이성을 놓친다 | 세 성질을 모두 명시적으로 확인한다 |
| 부분순서와 전순서를 같은 것으로 본다 | 비교 불가능한 쌍을 처리하지 못한다 | 부분순서는 일부만 비교된다는 점을 기억한다 |
| 사이클이 있는 그래프에 위상 정렬을 적용한다 | 정렬 결과가 깨진다 | 먼저 DAG인지 확인한다 |
| 동치류와 분할을 따로 외운다 | 같은 개념을 두 번 배우게 된다 | 하나를 정의하고 다른 하나를 도출한다 |
| 대칭과 반대칭을 직감으로만 구분한다 | 정의를 자꾸 혼동한다 | 조건을 식으로 써 보고 판정한다 |

## 실무에서는 이렇게 사용합니다

- 데이터베이스 정규화는 함수적 의존성과 관계 이론에 기대고 있습니다.
- npm, pip의 의존성 해석은 위상 정렬 문제입니다.
- Git의 조상 관계는 부분순서입니다.
- 캐시 키 설계는 동치관계를 정하는 일과 같습니다.
- ORM의 `equals()` 구현은 동치관계의 세 법칙을 만족해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 “같다”는 말을 쓸 때 반드시 그 기준이 반사, 대칭, 추이를 만족하는지 확인합니다. Java의 `equals()`나 Python의 `__eq__`가 이 법칙을 깨면 컬렉션 전체 동작이 무너질 수 있기 때문입니다. 또한 작업 스케줄링을 설계할 때는 먼저 “이 의존성이 사이클 없는 부분순서인가”를 묻습니다.

## 체크리스트

- [ ] 관계의 네 가지 성질을 정의할 수 있다
- [ ] 동치관계의 세 법칙을 기억한다
- [ ] 동치관계와 분할의 대응을 설명할 수 있다
- [ ] 부분순서와 전순서를 구분할 수 있다
- [ ] 위상 정렬이 사이클 없는 그래프에서만 가능함을 안다

## 연습 문제

1. 정수 집합에서 “부호가 같다”라는 관계가 동치관계인지 판단하고 동치류를 적어 보세요.

2. 자신의 디렉터리 구조를 부분순서로 표현하고 가능한 위상 순서 하나를 써 보세요.

3. 추이성을 위반하는 잘못된 Python `__eq__` 예제를 하나 만들고 어떤 문제가 생기는지 설명해 보세요.

## 정리 및 다음 단계

관계는 곱집합의 부분집합이며, 성질의 조합에 따라 동치관계와 부분순서가 됩니다. 동치관계는 분할을 만들고, 부분순서는 위상 정렬을 가능하게 합니다. 이 둘은 데이터 모델링과 작업 스케줄링을 이해하는 핵심 구조입니다.

다음 글에서는 이런 명제를 엄밀하게 보장하는 증명 방법을 다루겠습니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- **관계와 동치관계 (현재 글)**
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 9](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Equivalence Relation](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Wikipedia — Partially Ordered Set](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Wikipedia — Topological Sorting](https://en.wikipedia.org/wiki/Topological_sorting)

Tags: Computer Science, 이산수학, 관계, 동치류, 부분순서, 데이터 모델링
