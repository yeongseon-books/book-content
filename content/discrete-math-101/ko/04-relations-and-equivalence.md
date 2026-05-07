---
series: discrete-math-101
episode: 4
title: 관계와 동치관계
status: content-ready
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
seo_description: 이항관계의 정의와 반사·대칭·추이 성질, 동치관계와 분할, 부분순서와 위상 정렬을 다룹니다.
last_reviewed: '2026-05-04'
---

# 관계와 동치관계

> Discrete Math 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 데이터베이스의 "관계(relation)", `==` 연산자, 의존성 그래프의 위상 정렬 — 이들의 공통 수학 구조는 무엇일까요?

> 관계(relation)는 곱집합의 부분집합으로 정의되며, 두 원소 사이의 "어떤 연결"을 표현합니다. 반사·대칭·추이 같은 성질의 조합으로 동치관계(equivalence)와 부분순서(partial order)가 정의되고, 이들은 분할·정렬·계층 구조의 수학적 기반이 됩니다. 이 글에서는 관계의 표현, 핵심 성질, 동치류, 그리고 위상 정렬까지 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 이항관계의 정의와 표현 방법
- 반사·대칭·추이·반대칭 성질
- 동치관계와 동치류, 분할 정리
- 부분순서와 위상 정렬

## 왜 중요한가

데이터베이스의 "관계 모델"은 관계 이론에서 직접 유래했습니다. Git의 커밋 그래프, npm의 의존성 해석, 빌드 도구의 작업 스케줄링은 모두 부분순서 위의 위상 정렬입니다. `==`, `is` 연산자와 캐싱 전략은 동치관계의 응용입니다.

> 관계 = 데이터 사이의 구조를 표현하는 가장 기본적인 도구

## 개념 한눈에 보기

> 관계는 (a, b) 쌍의 집합. 어떤 성질을 만족하는지에 따라 동치관계, 부분순서 등으로 분류됩니다.

```text
   관계 R ⊆ A × A
        │
   ┌────┴────┬──────────┐
 반사       대칭       추이
   │         │          │
   └────┬────┘          │
   동치관계 ↔ 분할       │
                         │
   반사 ∧ 반대칭 ∧ 추이 = 부분순서 → 위상 정렬
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 이항관계 | A × A의 부분집합 |
| 반사적 | 모든 a에 대해 (a, a) ∈ R |
| 대칭적 | (a, b) ∈ R ⇒ (b, a) ∈ R |
| 추이적 | (a, b), (b, c) ∈ R ⇒ (a, c) ∈ R |
| 동치관계 | 반사 + 대칭 + 추이 |

## Before / After

**Before — 관계 사고 없이:**

```python
# "이 두 객체가 같은가?"를 ad-hoc 비교
def same_user(a, b):
    return a.id == b.id and a.email == b.email
```

**After — 동치관계로 명시:**

```python
# 동치류로 객체를 그룹화 — 캐시 키로 활용 가능
def equivalence_class(item, items, eq):
    return {x for x in items if eq(item, x)}
```

## 실습: 단계별로 따라하기

### 1단계: 관계의 표현

```python
# 관계는 (a, b) 쌍의 집합
people = {"alice", "bob", "carol"}
friends = {("alice", "bob"), ("bob", "alice"), ("bob", "carol"), ("carol", "bob")}

print(f"alice의 친구: {[b for (a, b) in friends if a == 'alice']}")

# 행렬 표현
import numpy as np

names = sorted(people)
n = len(names)
M = np.zeros((n, n), dtype=int)
for a, b in friends:
    M[names.index(a)][names.index(b)] = 1

print(f"인접 행렬:\n{M}")
```

관계는 (a, b) 쌍 집합으로도, 인접 행렬로도, 인접 리스트로도 표현됩니다. 8장에서 그래프로 다시 등장합니다.

### 2단계: 관계의 핵심 성질

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
print(f"반사: {is_reflexive(R_eq, A)}")
print(f"대칭: {is_symmetric(R_eq)}")
print(f"추이: {is_transitive(R_eq)}")
```

### 3단계: 동치관계와 동치류

```python
# 동치관계: 반사 + 대칭 + 추이
# 예: 정수의 mod 3 동치
def mod_equivalent(a: int, b: int, n: int = 3) -> bool:
    return (a - b) % n == 0


numbers = list(range(10))


def equivalence_class(x: int, domain: list, eq) -> set:
    return {y for y in domain if eq(x, y)}


for i in range(3):
    cls = equivalence_class(i, numbers, mod_equivalent)
    print(f"[{i}] = {sorted(cls)}")

# 동치류는 정의역을 분할(partition)합니다
all_classes = {frozenset(equivalence_class(x, numbers, mod_equivalent)) for x in numbers}
print(f"분할: {[sorted(c) for c in all_classes]}")
```

동치관계는 항상 분할을 만들고, 분할은 항상 동치관계를 정의합니다 — 이 둘은 일대일 대응입니다. 캐시 무효화, 데이터 중복 제거, 클러스터링이 모두 동치관계의 응용입니다.

### 4단계: 부분순서와 하세 다이어그램

```python
# 부분순서: 반사 + 반대칭 + 추이
# 예: 부분집합 관계 ⊆
A = [{1}, {2}, {1, 2}, {1, 2, 3}]


def is_subset_of(x: set, y: set) -> bool:
    return x <= y


# (x, y) 쌍 중 x ⊂ y이고 중간에 다른 원소가 없는 경우만 직접 연결
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

부분순서에서는 모든 쌍이 비교 가능할 필요가 없습니다 — 이것이 전순서(total order)와의 차이입니다. 디렉터리 트리, 클래스 상속, Git 커밋 DAG가 모두 부분순서의 예입니다.

### 5단계: 위상 정렬

```python
from collections import defaultdict, deque


def topological_sort(nodes: list, edges: list[tuple]) -> list:
    """부분순서를 만족하는 선형 순서를 반환합니다."""
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
print(f"실행 순서: {topological_sort(tasks, deps)}")
```

위상 정렬은 부분순서의 모든 제약을 만족하는 선형 순서입니다. 빌드 도구(make, gradle), 패키지 매니저, 작업 스케줄러가 모두 사용합니다.

## 이 코드에서 주목할 점

- 관계는 곱집합의 부분집합 — 단순한 정의에서 풍부한 구조가 나옵니다
- 동치관계 ↔ 분할은 일대일 대응
- 부분순서는 전순서보다 약하지만 더 일반적
- 위상 정렬은 사이클이 없는 경우에만 가능

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 동치관계 성질 누락 | 반사 또는 추이 검사 빠뜨림 | 세 성질 모두 명시적으로 확인 |
| 부분순서와 전순서 혼동 | 비교 불가 쌍을 처리 못함 | 부분순서는 일부만 비교 가능 |
| 사이클 있는 그래프에 위상 정렬 | 무한 루프 또는 빈 결과 | 사이클 검사 후 정렬 |
| 동치류와 분할 분리해서 사고 | 같은 개념을 두 번 구현 | 한 번 정의하면 다른 쪽 자동 도출 |
| 대칭과 반대칭 혼동 | "둘 다 아닌" 경우 존재 | 빈 관계는 둘 다 만족할 수도 있음 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 정규화는 함수적 의존성(부분순서)에 기반
- npm/pip 의존성 해석은 위상 정렬
- Git 커밋의 ancestor 관계는 부분순서
- 캐시 키 설계는 동치관계 정의와 동일
- ORM의 `equals()` 구현은 동치관계 성질을 만족해야 함

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 "같다"는 개념을 정의할 때 항상 동치관계의 세 성질을 확인합니다. Java의 `equals()` 계약, Python의 `__eq__` 구현 — 이들이 동치관계가 아니면 컬렉션이 깨집니다. 또한 작업 스케줄링을 설계할 때 "이 의존성이 부분순서인가, 사이클은 없는가"를 가장 먼저 검토합니다.

## 체크리스트

- [ ] 관계의 네 가지 성질을 정의할 수 있는가
- [ ] 동치관계의 세 성질을 기억하는가
- [ ] 동치관계와 분할의 대응을 이해했는가
- [ ] 부분순서와 전순서의 차이를 설명할 수 있는가
- [ ] 위상 정렬이 사이클 없는 그래프에서만 가능함을 아는가

## 연습 문제

1. 정수 집합에서 "같은 부호" 관계가 동치관계인지 확인하고 동치류를 나열하세요.

2. 자신의 디렉터리 구조를 부분순서로 표현하고, 가능한 위상 정렬 하나를 작성하세요.

3. Python의 `__eq__`를 잘못 구현하여 추이성이 깨지는 예를 만들고, 어떤 문제가 발생하는지 설명하세요.

## 정리 및 다음 단계

관계는 곱집합의 부분집합이며, 어떤 성질을 만족하는지에 따라 동치관계와 부분순서로 나뉩니다. 동치관계는 분할을, 부분순서는 위상 정렬을 가능하게 합니다. 이 두 구조는 데이터 모델링과 작업 스케줄링의 수학적 기반입니다.

다음 글에서는 이 모든 주장들을 "엄밀히 증명"하는 방법 — 직접·귀류·귀납 증명을 살펴봅니다.

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
