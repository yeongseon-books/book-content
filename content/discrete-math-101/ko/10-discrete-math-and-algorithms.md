---
series: discrete-math-101
episode: 10
title: "Discrete Math 101 (10/10): 알고리즘과 이산수학의 연결"
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
  - 알고리즘
  - 복잡도
  - NP
  - 응용
seo_description: 이산수학의 핵심 개념이 알고리즘 분석, 정확성, 복잡도 판단에 연결되는 방식을 정리합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (10/10): 알고리즘과 이산수학의 연결

이 글은 Discrete Math 101 시리즈의 마지막 글입니다.

## 먼저 던지는 질문

- 점화식과 마스터 정리는 시간 복잡도와 어떻게 연결될까요?
- 귀납법과 루프 불변식은 알고리즘 정확성을 어떻게 보장할까요?
- P, NP, NP-완전은 어떤 직관으로 이해해야 할까요?

## 큰 그림

![Discrete Math 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/10/10-01-big-picture.ko.png)

*Discrete Math 101 10장 흐름 개요*

이 그림에서는 알고리즘과 이산수학의 연결를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 알고리즘과 이산수학의 연결의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

**Before — 성능 문제를 측정만으로 본다:**

```python
import time

start = time.time()
result = my_algorithm(big_input)
print(f"elapsed: {time.time() - start}")
```

**After — 먼저 예측하고, 그다음 실행해 비교한다:**

```python
def predicted_n_log_n(n: int) -> int:
    """T(n) = 2T(n/2) + n의 대략적 스케일."""
    return n * (n.bit_length() - 1)

print(predicted_n_log_n(32))
```

시니어 엔지니어의 흐름은 보통 이론으로 먼저 예측하고, 그다음 계측이나 비교 출력으로 검증하는 순서입니다.

## 단계별로 따라가기

### 1단계: 먼저 예측하기 — 병합 정렬은 왜 `O(n log n)`일까요?

```python
def predicted_n_log_n(n: int) -> int:
    """상수항을 무시한 n * log2(n) 기준선."""
    return n * (n.bit_length() - 1)

for n in [8, 16, 32, 64]:
    print(f"n={n:>2} -> prediction scale ≈ {predicted_n_log_n(n)}")
```

`T(n) = 2T(n/2) + n`은 “절반 크기 하위 문제 두 개 + 한 번의 선형 병합”이라는 뜻입니다. 마스터 정리로 보면 `a=2`, `b=2`, `f(n)=n`이므로 전체는 `O(n log n)`으로 예측됩니다. 이 단계의 목적은 숫자를 재는 것이 아니라 성장 모양을 먼저 머릿속에 세우는 것입니다.

**예상 출력**

```text
n= 8 -> prediction scale ≈ 24
n=16 -> prediction scale ≈ 64
n=32 -> prediction scale ≈ 160
n=64 -> prediction scale ≈ 384
```

- 이 값은 정확한 비교 횟수가 아니라 기준선입니다.
- 선형 `n`보다는 빠르게 커지지만 제곱 `n²`처럼 폭증하지 않는다는 점이 핵심입니다.

### 2단계: 실제로 돌려서 비교하기 — 예측과 측정 맞춰 보기

```python
def merge_and_count(left: list[int], right: list[int]) -> tuple[list[int], int]:
    merged = []
    i = j = comparisons = 0
    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, comparisons

def merge_sort_count(arr: list[int]) -> tuple[list[int], int]:
    if len(arr) <= 1:
        return arr[:], 0
    mid = len(arr) // 2
    left, left_count = merge_sort_count(arr[:mid])
    right, right_count = merge_sort_count(arr[mid:])
    merged, merge_count = merge_and_count(left, right)
    return merged, left_count + right_count + merge_count

for n in [8, 16, 32, 64]:
    sample = list(range(n, 0, -1))
    sorted_sample, comparisons = merge_sort_count(sample)
    predicted = predicted_n_log_n(n)
    print(
        f"n={n:>2} | comparisons={comparisons:>3} | "
        f"prediction-scale={predicted:>3} | first={sorted_sample[:5]}"
    )
```

이제 점화식 설명이 실제 실험으로 내려옵니다. 여기서 비교하는 것은 “정확히 같은 숫자”가 아니라 성장 패턴입니다. 입력이 커질수록 비교 횟수가 `n log n` 스케일과 함께 커져야 합니다.

**예상 출력**

```text
n= 8 | comparisons= 12 | prediction-scale= 24 | first=[1, 2, 3, 4, 5]
n=16 | comparisons= 32 | prediction-scale= 64 | first=[1, 2, 3, 4, 5]
n=32 | comparisons= 80 | prediction-scale=160 | first=[1, 2, 3, 4, 5]
n=64 | comparisons=192 | prediction-scale=384 | first=[1, 2, 3, 4, 5]
```

**결과를 이렇게 읽으면 됩니다.**

- 비교 횟수는 `12 → 32 → 80 → 192`처럼 증가합니다. 선형보다 빠르지만 제곱보다 훨씬 느리므로 `n log n` 성장과 잘 맞습니다.
- `first=[1, 2, 3, 4, 5]`는 정렬 정확성 확인용입니다. 성능을 보기 전에 결과가 먼저 맞아야 합니다.
- 숫자가 조금 달라도 괜찮습니다. 입력 패턴이 바뀌면 비교 횟수도 달라집니다. 다만 `n`이 커질수록 완만한 `n log n` 스케일을 따라야 합니다.
- 만약 비교 횟수가 `n²`처럼 보인다면 병합 로직이 깨졌거나, 분할이 균형 있게 일어나지 않는 경우를 먼저 의심해 보세요.

### 3단계: 정확성까지 연결하기 — 귀납법과 루프 불변식

```python
def prefix_sum(nums: list[int]) -> list[int]:
    """Invariant: 각 반복이 끝나면 result[-1]은 지금까지의 누적합입니다."""
    result = []
    running = 0
    for x in nums:
        running += x
        result.append(running)
    return result

values = [3, 1, 4, 1]
print(prefix_sum(values))
assert prefix_sum(values) == [3, 4, 8, 9]
```

성능 분석이 예측의 언어라면, 루프 불변식은 정확성의 언어입니다. 이 반복문이 왜 맞는지 설명하려면 “각 단계가 끝날 때 누적합이 유지된다”는 명제를 잡고 귀납적으로 보면 됩니다. 알고리즘을 이해한다는 것은 빠르기만 아는 것이 아니라 왜 맞는지도 말할 수 있다는 뜻입니다.

**예상 출력**

```text
[3, 4, 8, 9]
```

- 각 위치는 해당 인덱스까지의 누적합이어야 합니다.
- 값이 틀리면 `running`을 더하는 시점과 `append` 순서를 먼저 확인해 보세요.

### 4단계: 그래프 알고리즘으로 확장하기 — 위상 정렬은 의존성 검증입니다

```python
from collections import defaultdict, deque

def topological_sort(graph: dict[str, list[str]]) -> list[str]:
    """Deterministic topological sort with cycle detection."""
    in_deg = defaultdict(int)
    for u in graph:
        in_deg[u] += 0
        for v in graph[u]:
            in_deg[v] += 1
    queue = deque(sorted(u for u in graph if in_deg[u] == 0))
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in sorted(graph[u]):
            in_deg[v] -= 1
            if in_deg[v] == 0:
                queue.append(v)
    if len(order) != len(graph):
        raise ValueError("cycle detected")
    return order

deps = {
    "lint": ["test"],
    "test": ["build"],
    "build": ["deploy"],
    "deploy": [],
}
print(f"build order: {topological_sort(deps)}")

cyclic_deps = {
    "parse": ["compile"],
    "compile": ["link"],
    "link": ["parse"],
}

try:
    topological_sort(cyclic_deps)
except ValueError as exc:
    print(exc)
```

위상 정렬은 9편에서 배운 그래프 탐색이 빌드 시스템과 태스크 스케줄러로 이어지는 지점입니다. 여기서 중요한 것은 정상 입력에서 순서를 뽑는 것뿐 아니라, 사이클이 있으면 즉시 실패해야 한다는 점입니다.

**예상 출력**

```text
build order: ['lint', 'test', 'build', 'deploy']
cycle detected
```

- 예제 DAG에서는 `lint → test → build → deploy`가 결정적 순서입니다.
- `cycle detected`가 출력되지 않는다면 “의존성 그래프가 DAG인지 검증한다”는 중요한 안전장치를 놓친 것입니다.

### 5단계: 조합론과 난도 감각 — 부분합 문제는 왜 갑자기 어려워질까요?

```python
def subset_sum(nums: list[int], target: int) -> bool:
    """Subset Sum — NP-complete. Brute force is O(2^n)."""
    n = len(nums)
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask & (1 << i))
        if s == target:
            return True
    return False

print(f"target 13 exists: {subset_sum([3, 7, 1, 8, 5], 13)}")
print(f"target 2 exists:  {subset_sum([3, 7, 1, 8, 5], 2)}")
```

부분합 문제는 이제 보조 예제 역할입니다. 이 글의 메인 데모는 병합 정렬의 예측→실행→비교 실험이고, 부분합은 “입력 크기가 커지면 완전 탐색을 기본 전략으로 두면 안 된다”는 마지막 직관을 강화합니다.

**예상 출력**

```text
target 13 exists: True
target 2 exists:  False
```

- `13`은 `8 + 5`로 만들 수 있으므로 `True`입니다.
- `2`는 만들 수 없으므로 `False`입니다.
- 여기서 핵심은 정답 자체보다 `2^n` 탐색이 얼마나 빠르게 폭증하는지입니다.

### P, NP, NP-완전의 직관

P는 다항 시간에 풀 수 있는 문제이고, NP는 답을 받으면 다항 시간에 검증할 수 있는 문제입니다. NP-완전은 그 안에서도 가장 어려운 축에 속합니다. 실무에서는 “정확한 최적해를 끝까지 밀어붙일 것인가, 근사나 휴리스틱으로 전환할 것인가”를 판단하는 신호로 이해하는 편이 더 유용합니다.

## 주목할 점

- 점화식은 먼저 예측을 세우고, 계측은 그 예측을 검증하는 흐름으로 읽어야 합니다.
- 귀납법과 루프 불변식은 성능과 별개로 정확성을 설명하는 언어입니다.
- 위상 정렬처럼 그래프 알고리즘은 “정상 결과”와 “실패해야 하는 경우”를 함께 검증해야 합니다.
- NP-완전 인식은 “최적해 집착을 멈출 시점”을 알려 주는 실무 판단 도구입니다.

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

## 처음 질문으로 돌아가기

- **점화식과 마스터 정리는 시간 복잡도와 어떻게 연결될까요?**
  - 본문의 기준은 알고리즘과 이산수학의 연결를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **귀납법과 루프 불변식은 알고리즘 정확성을 어떻게 보장할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **P, NP, NP-완전은 어떤 직관으로 이해해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): 관계와 동치관계](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): 증명 방법](./05-proof-techniques.md)
- [Discrete Math 101 (6/10): 수열과 점화식](./06-sequences-and-recurrence.md)
- [Discrete Math 101 (7/10): 조합과 경우의 수](./07-combinatorics.md)
- [Discrete Math 101 (8/10): 그래프 이론 기초](./08-graph-theory-basics.md)
- [Discrete Math 101 (9/10): 트리와 그래프 탐색](./09-trees-and-graph-traversal.md)
- **알고리즘과 이산수학의 연결 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms — Cormen et al., Chapters 2, 4, 22, 34](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Mathematics for Computer Science — Lehman, Leighton, Meyer](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Algorithms, 4th Edition — Sedgewick & Wayne, Section 2.2 Mergesort](https://algs4.cs.princeton.edu/22mergesort/)
- [Algorithms, 4th Edition — Sedgewick & Wayne, Section 4.2 Directed Graphs](https://algs4.cs.princeton.edu/42digraphs/)
- [MIT OpenCourseWare 6.046J — Design and Analysis of Algorithms](https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/)
- [Clay Mathematics Institute — P vs NP Problem](https://www.claymath.org/millennium/p-vs-np)

Tags: Computer Science, 이산수학, 알고리즘, 복잡도, NP, 응용
