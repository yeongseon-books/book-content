---
series: discrete-math-101
episode: 10
title: 알고리즘과 이산수학의 연결
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
  - 알고리즘
  - 복잡도
  - NP
  - 응용
seo_description: 이산수학의 핵심 개념이 알고리즘 분석, 정확성, 복잡도 판단에 연결되는 방식을 정리합니다.
last_reviewed: '2026-05-12'
---

# 알고리즘과 이산수학의 연결

이 글은 Discrete Math 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

- 점화식과 마스터 정리는 시간 복잡도와 어떻게 연결될까요?
- 귀납법과 루프 불변식은 알고리즘 정확성을 어떻게 보장할까요?
- P, NP, NP-완전은 어떤 직관으로 이해해야 할까요?
- 지금까지 배운 주제는 알고리즘 도구 상자에서 어떻게 다시 정리될까요?

> 이산수학은 알고리즘의 언어입니다. 점화식은 시간 복잡도를 설명하고, 조합론은 경우의 수를 세며, 그래프 이론은 의존성과 경로 문제를 모델링하고, 증명 기법은 정확성을 보장합니다. 이 마지막 글에서는 시리즈 전체를 알고리즘 관점에서 다시 묶고, P와 NP 같은 상위 개념까지 짧게 연결합니다.

## 왜 중요한가

이산수학을 각 장마다 따로 배우면 추상적으로 느껴질 수 있습니다. 하지만 알고리즘과 붙이면 곧바로 실무 도구가 됩니다. 면접, 시스템 설계, 성능 최적화의 기본 어휘는 모두 여기까지 모아 온 개념 위에 서 있습니다.

> 이산수학이 없으면 알고리즘은 마법처럼 보이고, 있으면 추론의 결과로 보입니다.

## 한눈에 보는 개념

> 알고리즘 분석의 세 축은 정확성, 효율성, 자원 사용입니다. 이산수학의 각 주제는 그중 하나 이상에 직접 연결됩니다.

```text
discrete-math tool      algorithmic application
propositions, logic →   assertions, unit tests, formal verification
sets, functions    →    hash sets, indexing, functional programming
relations, eq.     →    Union-Find, graph classification
proof techniques   →    correctness, loop invariants
recurrences        →    time-complexity analysis (T(n) = 2T(n/2) + n)
combinatorics      →    counting, probability, backtracking
graphs             →    networks, dependencies, shortest paths
trees, traversal   →    BFS, DFS, MST, sorting
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Big-O O(f) | 실행 시간의 최악 상한 |
| Master Theorem | 분할 정복 점화식의 표준 해법 |
| Loop invariant | 반복마다 유지되는 명제 |
| P | 다항 시간에 풀 수 있는 문제 |
| NP | 다항 시간에 검증할 수 있는 문제 |

## Before / After

**Before — performance work via measurement only:**

```python
import time

start = time.time()
result = my_algorithm(big_input)
print(f"elapsed: {time.time() - start}")  # only comparable across input sizes
```

**After — predicting first, then measuring:**

```python
def analyze(n: int) -> str:
    """T(n) = 2T(n/2) + n → O(n log n) by the Master Theorem."""
    return f"for input size {n}, expect about {n * (n.bit_length() - 1)} comparisons"


print(analyze(1024))
```

시니어 엔지니어의 흐름은 보통 이론으로 먼저 예측하고, 그다음 측정으로 검증하는 순서입니다.

## 단계별로 따라가기

### 1단계: 점화식과 시간 복잡도

```python
def merge_sort(arr: list) -> list:
    """T(n) = 2T(n/2) + n → O(n log n)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(a: list, b: list) -> list:
    result, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result


print(merge_sort([5, 2, 8, 1, 9, 3]))
```

`T(n) = aT(n/b) + f(n)`에서 a, b, f(n)의 관계를 읽으면 복잡도를 상당히 빨리 예측할 수 있습니다. 병합 정렬을 이해했다면 이미 이산수학이 알고리즘을 해석하는 방식에 들어선 셈입니다.

### 2단계: 귀납법과 루프 불변식

```python
def sum_of_first_n(n: int) -> int:
    """The return value always equals 1 + 2 + ... + n — provable by induction."""
    total = 0
    for i in range(1, n + 1):
        # Loop invariant: total == i*(i-1)/2 at the top of each iteration
        total += i
    # On exit: total == n*(n+1)/2
    return total


assert sum_of_first_n(10) == 55
```

루프 불변식은 반복문이 매 단계에서 지키는 명제입니다. 귀납법으로 그것을 증명하면 왜 알고리즘이 정답을 내는지도 함께 설명됩니다.

### 3단계: 조합론과 백트래킹

```python
def subsets(nums: list) -> list:
    """All subsets of a set of size n — there are 2^n."""
    result = [[]]
    for x in nums:
        result.extend([s + [x] for s in result])
    return result


def permutations(nums: list) -> list:
    """All permutations of a set of size n — there are n!. Backtracking."""
    if not nums:
        return [[]]
    out = []
    for i, x in enumerate(nums):
        for rest in permutations(nums[:i] + nums[i + 1:]):
            out.append([x] + rest)
    return out


print(f"subset count:      {len(subsets([1, 2, 3]))}")
print(f"permutation count: {len(permutations([1, 2, 3]))}")
```

경우의 수를 미리 알면 애초에 시도하면 안 되는 알고리즘을 빠르게 걸러낼 수 있습니다. `n!`이나 `2^n`이 붙는 순간 입력 범위 판단이 먼저 나와야 합니다.

### 4단계: 그래프 알고리즘의 실전 사용

```python
from collections import defaultdict, deque


def topological_sort(graph: dict) -> list:
    """Topological sort of a DAG — Kahn's algorithm (BFS-based)."""
    in_deg = defaultdict(int)
    for u in graph:
        for v in graph[u]:
            in_deg[v] += 1
    queue = deque([u for u in graph if in_deg[u] == 0])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                queue.append(v)
    return order


deps = {
    "compile": ["link"],
    "lex": ["parse"],
    "parse": ["compile"],
    "link": [],
}
print(f"build order: {topological_sort(deps)}")
```

위상 정렬은 의존성 해석의 핵심입니다. 빌드 시스템, 패키지 매니저, 태스크 스케줄러에서 그래프 이론이 왜 기본 언어가 되는지 가장 잘 보여 주는 예입니다.

### 5단계: P, NP, NP-완전의 직관

```python
def subset_sum(nums: list, target: int) -> bool:
    """Subset Sum — NP-complete. Brute force is O(2^n) up to n."""
    n = len(nums)
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask & (1 << i))
        if s == target:
            return True
    return False


print(subset_sum([3, 7, 1, 8, 5], 13))
```

P는 다항 시간에 풀 수 있는 문제이고, NP는 답을 받으면 다항 시간에 검증할 수 있는 문제입니다. NP-완전은 그 안에서도 가장 어려운 축에 속합니다. 실무에서는 “정확한 최적해를 끝까지 밀어붙일 것인가, 근사나 휴리스틱으로 전환할 것인가”를 판단하는 신호로 이해하는 편이 더 유용합니다.

## 주목할 점

- 점화식은 알고리즘 비용 모형이고, 마스터 정리는 분할 정복의 표준 도구입니다.
- 귀납법은 순수 수학을 넘어 알고리즘 정확성 증명의 기본 도구입니다.
- 조합론은 입력 크기가 감당 가능한지 판단하는 직관을 만듭니다.
- NP-완전 인식은 “최적해 집착을 멈출 시점”을 알려 줍니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 평균과 최악을 섞어 말한다 | Big-O 해석이 흔들린다 | 분포를 모르면 최악 기준으로 본다 |
| 형식이 안 맞는데 마스터 정리를 억지로 쓴다 | 분석 자체가 틀린다 | 직접 전개나 재귀 트리로 바꾼다 |
| 입력 크기를 과소평가한다 | `n=30`에서도 지수 시간이 터진다 | 먼저 n의 범위를 본다 |
| “NP니까 불가능”으로 단정한다 | 작은 입력에서도 쓸 수 있는 방법을 놓친다 | 크기와 시간 예산을 함께 본다 |
| 정확성 증명을 빼먹는다 | 돌아가지만 가끔 틀린 코드가 된다 | 불변식과 테스트를 함께 둔다 |

## 실무에서는 이렇게 사용합니다

- 시스템 설계 면접에서 점화식과 Big-O로 후보 알고리즘을 비교합니다.
- 데이터 파이프라인 최적화에서 그래프 탐색으로 조인 순서를 정합니다.
- 패키지 매니저와 빌드 시스템은 위상 정렬과 사이클 검출에 의존합니다.
- 추천과 검색은 그래프와 행렬 분해 기법을 활용합니다.
- 컴파일러 최적화는 데이터 흐름 분석과 그래프 구조를 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 코드를 쓰기 전에 입력 크기, 시간 복잡도, 메모리 한계를 먼저 추정합니다. 이는 측정이 아니라 이산수학적 추론입니다. 또한 NP-완전 문제를 만나면 최적해를 고집하기보다 근사, 휴리스틱, 문제 축소로 빠르게 전략을 바꿉니다. 포기할 시점을 아는 것도 분석의 결과입니다.

## 체크리스트

- [ ] Big-O와 점화식의 관계를 설명할 수 있다
- [ ] 마스터 정리가 적용되는 경우를 안다
- [ ] 루프 불변식으로 정확성을 검증할 수 있다
- [ ] P와 NP의 차이를 설명할 수 있다
- [ ] 시리즈 전체를 알고리즘 도구 상자로 다시 매핑할 수 있다

## 연습 문제

1. 마스터 정리로 `T(n) = 3T(n/2) + n²`의 시간 복잡도를 구해 보세요.

2. 이진 탐색의 정확성을 루프 불변식과 귀납법으로 증명해 보세요.

3. 자신의 프로젝트에서 NP-완전하거나 그에 준하는 어려운 문제를 하나 찾고, 어떻게 우회했는지 또는 우회할지 설명해 보세요.

## 정리 및 다음 단계

이산수학은 알고리즘의 언어입니다. 명제, 집합, 증명, 점화식, 조합론, 그래프는 모두 시간 복잡도, 정확성, 자료구조 선택, 시스템 설계 판단으로 바로 이어집니다.

이 시리즈를 마쳤다면 다음 단계는 세 가지입니다. 자료구조와 알고리즘 학습으로 더 깊이 들어가고, 시스템 설계에서 이산수학 도구가 어떻게 결합되는지 계속 관찰하고, 실제 코드에서 복잡도와 증명 감각을 일상 습관으로 만드는 것입니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- [증명 방법](./05-proof-techniques.md)
- [수열과 점화식](./06-sequences-and-recurrence.md)
- [조합과 경우의 수](./07-combinatorics.md)
- [그래프 이론 기초](./08-graph-theory-basics.md)
- [트리와 그래프 탐색](./09-trees-and-graph-traversal.md)
- **알고리즘과 이산수학의 연결 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms — Cormen et al.](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Discrete Mathematics and Its Applications — Kenneth Rosen](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Master Theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Wikipedia — P versus NP problem](https://en.wikipedia.org/wiki/P_versus_NP_problem)

Tags: Computer Science, 이산수학, 알고리즘, 복잡도, NP, 응용
