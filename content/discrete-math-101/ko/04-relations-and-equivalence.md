---
series: discrete-math-101
episode: 4
title: "Discrete Math 101 (4/10): 관계와 동치관계"
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
  - 관계
  - 동치류
  - 부분순서
  - 데이터 모델링
seo_description: 이항관계의 성질과 동치관계, 분할, 부분순서, 위상 정렬의 연결을 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (4/10): 관계와 동치관계

이 글은 Discrete Math 101 시리즈의 4번째 글입니다.


![Discrete Math 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/04/04-01-big-picture.ko.png)
*Discrete Math 101 4장 흐름 개요*

## 먼저 던지는 질문

- 이항관계는 어떻게 정의하고 표현할까요?
- 반사, 대칭, 추이, 반대칭 성질은 어떻게 구분할까요?
- 동치관계와 동치류, 분할은 왜 서로 연결될까요?

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

## 전후 비교

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

## 실전 확장: 동치관계와 부분순서를 설계 규칙으로 쓰기

관계 모델은 "같다"와 "앞선다"를 분리할 때 특히 유용합니다. 동치관계는 분류 기준을 만들고, 부분순서는 의존 순서를 만들며, 둘을 혼동하면 설계가 흔들립니다.

### 동치관계 예시: 문자열 정규화

동치관계 `~`를 "공백 제거 후 소문자 변환 결과가 동일"로 정의하면:

- `"ABC" ~ "abc"`
- `"a b c" ~ "ABC"`
- `"Ab C" ~ "aBc"`

이 관계는 반사성, 대칭성, 추이성을 만족합니다. 따라서 동치류 기반 캐시 키를 만들 수 있습니다.

```python
def normalize(s: str) -> str:
    return "".join(s.split()).lower()

def equivalent(a: str, b: str) -> bool:
    return normalize(a) == normalize(b)
```

### 부분순서 예시: 빌드 의존성

`A ≤ B`를 "A가 B의 선행 작업"으로 두면 반사성, 반대칭성, 추이성을 만족하는 부분순서가 됩니다.

| 작업 | 선행 작업 |
| --- | --- |
| 테스트 | 빌드 |
| 패키징 | 테스트 |
| 배포 | 패키징 |

이 구조는 DAG(유향 비순환 그래프)로 표현할 수 있고, 위상 정렬로 실행 순서를 구합니다.

```python
from collections import deque

def topo_sort(graph: dict[str, list[str]]) -> list[str]:
    indeg = {v: 0 for v in graph}
    for v in graph:
        for nxt in graph[v]:
            indeg[nxt] = indeg.get(nxt, 0) + 1
    q = deque([v for v, d in indeg.items() if d == 0])
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for nxt in graph.get(v, []):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return order
```

### 동치류 분할 예시

정수 집합을 4로 나눈 나머지 기준으로 분할하면 `[0], [1], [2], [3]` 네 동치류가 만들어집니다. 서로 다른 동치류는 교집합이 공집합입니다. 이 성질이 있어야 분류 체계가 충돌 없이 동작합니다.

### 짧은 증명 앵커

명제: 동치관계의 동치류들은 전체 집합을 분할합니다.

증명 스케치: 임의의 원소 `x`는 반사성으로 `x~x`이므로 어떤 동치류에 속합니다. 두 동치류가 교집합을 가지면 대칭성과 추이성으로 서로 포함되어 결국 같은 동치류가 됩니다. 따라서 분할 조건이 만족됩니다.

## 심화 워크숍: 관계 모델 품질 점검 절차

### 관계 행렬로 결함 찾기

작은 도메인에서는 관계를 행렬로 그리면 결함이 빨리 보입니다. 대각선이 모두 1인지 보면 반사성을, 전치 대칭인지 보면 대칭성을, 경로 합성으로 추이성을 점검할 수 있습니다.

### 추천 규칙의 부분순서 모델

우선순위 규칙 `긴급 > 중요 > 일반`은 전순서에 가깝지만, 실제 운영에서는 팀별 예외가 있어 부분순서가 됩니다. 부분순서로 모델링하면 비교 불가능한 쌍을 자연스럽게 표현할 수 있습니다.

```python
def is_antisymmetric(rel: set[tuple[str, str]]) -> bool:
    for a, b in rel:
        if a != b and (b, a) in rel:
            return False
    return True
```

### 동치류를 이용한 중복 제거

문서 제목 정규화 동치류를 기준으로 대표 원소를 하나만 남기면, 검색 색인 중복을 줄일 수 있습니다. 이때 대표 선택 규칙(최신 생성일, 높은 품질 점수)을 명시해야 결과 재현성이 생깁니다.

### 짧은 증명 앵커

명제: 부분순서 집합의 하세 다이어그램은 반사 간선을 생략해도 정보를 잃지 않습니다.

이유: 반사 관계 `x≤x`는 모든 원소에 공통으로 존재하므로 도식에서 생략해도 순서 비교 결과가 변하지 않습니다.

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

- **이항관계는 어떻게 정의하고 표현할까요?**
  - 본문의 기준은 관계와 동치관계를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **반사, 대칭, 추이, 반대칭 성질은 어떻게 구분할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **동치관계와 동치류, 분할은 왜 서로 연결될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- **관계와 동치관계 (현재 글)**
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 9](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Equivalence Relation](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Wikipedia — Partially Ordered Set](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Wikipedia — Topological Sorting](https://en.wikipedia.org/wiki/Topological_sorting)

Tags: Computer Science, 이산수학, 관계, 동치류, 부분순서, 데이터 모델링
