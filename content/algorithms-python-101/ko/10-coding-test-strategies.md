---
series: algorithms-python-101
episode: 10
title: 코딩 테스트 문제 접근법
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Algorithms
  - Coding Test
  - Problem Solving
  - Interview
seo_description: 코딩 테스트 문제 해결을 위한 체계적 전략을 세웁니다. 투 포인터, 슬라이딩 윈도우 등 핵심 패턴과 파이썬 라이브러리 활용 팁을 배웁니다.
last_reviewed: '2026-05-12'
---

# 코딩 테스트 문제 접근법

이 글은 Algorithms with Python 101 시리즈의 마지막 글입니다. 알고리즘을 안다는 것과 시간 제한 안에서 적용하는 것은 다른 문제이며, 코딩 테스트의 진짜 난점은 구현 전에 제약을 빠르게 읽고 문제를 적절한 패턴에 연결하는 데 있습니다.

이번 글에서는 앞선 내용을 "제약을 먼저 읽고, 틀린 복잡도를 먼저 버린 뒤, 구현과 검증까지 이어 가는 하나의 풀이 흐름"으로 묶어 보겠습니다. 반복 가능한 접근법이 중요한 이유는 시간을 아끼고, 불필요한 실수를 줄이고, 처음 보는 문제에서도 다시 복구할 수 있게 해 주기 때문입니다.

## 이 글에서 다룰 문제

- 입력 크기 제약을 보고 어떤 알고리즘을 먼저 버려야 할까요?
- 문제 유형을 알고리즘에 어떻게 연결할까요?
- 한 문제를 이해, 계획, 구현, 검증으로 어떻게 끝까지 끌고 갈까요?
- 제한 시간 안에 도움 되는 Python 패턴은 어떤 것들이 있을까요?

## 왜 중요한가

이 시리즈의 알고리즘을 모두 공부했더라도, 실제 문제 앞에서 무엇을 써야 할지 결정하지 못하면 소용이 없습니다. 핵심은 문제 유형을 빠르게 분류하고, 입력 제약에서 거꾸로 필요한 시간 복잡도를 추론하는 능력입니다.

> Problem-Solving Flow = Analyze Input → Classify Type → Choose Algorithm → Implement → Verify

코딩 테스트는 제한 시간 안에 정확한 코드를 작성하는 시험입니다. 체계적인 접근은 시간을 줄이고 실수를 줄여 줍니다.

## 개념 한눈에 보기

> 입력 크기에서 허용 가능한 시간 복잡도를 역산합니다

```text
Allowed time complexity by input size N (1-second limit):
N ≤ 10        → O(N!)       — brute force / permutations
N ≤ 20        → O(2^N)      — bitmask, backtracking
N ≤ 500       → O(N³)       — Floyd-Warshall
N ≤ 5,000     → O(N²)       — DP, nested loops
N ≤ 1,000,000 → O(N log N)  — sorting, binary search
N ≤ 10^8      → O(N)        — linear scan, two pointers
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Brute force | 가능한 모든 경우를 시도하는 가장 기본적인 접근입니다 |
| Two pointers | 두 포인터를 움직여 `O(N)`에 푸는 패턴입니다 |
| Sliding window | 일정 구간을 밀며 부분 배열 합 등을 계산하는 패턴입니다 |
| Backtracking | 조건이 맞지 않으면 되돌아가며 경우를 탐색합니다 |
| Edge case | 빈 입력, 최소값, 최대값처럼 경계 조건입니다 |

## Before / After

문제 접근 방식의 차이를 비교해 보겠습니다.

```python
# before: start coding immediately — risk of picking the wrong algorithm
def solve(data):
    # jump into nested loops without thinking → time limit exceeded
    for i in range(len(data)):
        for j in range(len(data)):
            pass  # O(N²) — exceeds time limit when N is 1,000,000
```

```python
# after: analyze input size first, then choose the algorithm
def solve(data):
    # N=1,000,000 → need O(N) or O(N log N)
    # approach with sorting + two pointers
    data.sort()  # O(N log N)
    left, right = 0, len(data) - 1
    # ... O(N) scan
```

## 단계별 실습

### Step 1: 제약부터 읽고, 틀린 복잡도를 먼저 버립니다

```python
problem = {
    "name": "Two Sum to Target",
    "input": "정수 배열 nums, 목표값 target",
    "goal": "합이 target과 정확히 같은 두 수의 인덱스를 반환. 없으면 None 반환",
    "constraints": {
        "n_max": 200_000,
        "time_limit_seconds": 1,
        "values": "음수와 중복 포함 가능",
    },
}

print(problem)
```

`N = 200,000`이면 `O(N^2)` 이중 반복은 바로 탈락입니다. 1초 제한에서 4백억 번 비교에 가까운 접근은 구현이 아무리 깔끔해도 시간 초과가 납니다.

### Step 2: 잘못된 접근을 먼저 기각합니다

```python
def wrong_two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
```

이 접근은 정답 자체는 구할 수 있지만, 제약과 맞지 않습니다. 따라서 여기서 중요한 것은 "이 코드는 느리다"가 아니라 "제약을 읽은 순간 이 코드를 쓰지 않기로 결정해야 한다"입니다.

### Step 3: 문제 유형을 분류하고 목표 복잡도를 정합니다

| 질문 | 이번 문제의 답 | 의미 |
|------|----------------|------|
| 배열이 정렬되어 있는가? | 아니요 | 먼저 정렬이 필요합니다 |
| 두 값을 합쳐 목표를 맞추는가? | 예 | 투 포인터 후보입니다 |
| 모든 조합을 다 봐야 하는가? | 아니요 | 브루트포스 탈락입니다 |
| 목표 복잡도는 무엇인가? | `O(N log N)` 이하 | 정렬 + 선형 스캔이 가능합니다 |

이 문제는 DP나 그래프가 아닙니다. 상태를 누적해 최적 부분 구조를 쓰는 문제도 아니고, 정점과 간선을 탐색하는 문제도 아니기 때문입니다. 핵심 힌트는 "두 수의 합"과 "정렬 후 양끝에서 좁히기"입니다.

### Step 4: 정렬 + 투 포인터로 구현합니다

```python
def solve_two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    indexed = sorted((value, index) for index, value in enumerate(nums))
    left, right = 0, len(indexed) - 1

    while left < right:
        current = indexed[left][0] + indexed[right][0]
        if current == target:
            i, j = indexed[left][1], indexed[right][1]
            return tuple(sorted((i, j)))
        if current < target:
            left += 1
        else:
            right -= 1

    return None


sample_nums = [7, 1, 11, 2, 9]
sample_target = 10
sample_answer = solve_two_sum(sample_nums, sample_target)

print(sample_answer)
assert sample_answer == (0, 3)
```

구현에서 중요한 포인트는 세 가지입니다.

1. 원본 인덱스를 잃지 않으려고 `(값, 원래 인덱스)` 쌍으로 정렬합니다.
2. 합이 작으면 왼쪽 포인터를 오른쪽으로 움직이고, 합이 크면 오른쪽 포인터를 왼쪽으로 움직입니다.
3. 답을 찾으면 인덱스를 오름차순으로 정리해 반환합니다.

만약 샘플조차 틀리면 먼저 정렬된 값만 보고 원본 인덱스를 잃어버리지 않았는지 확인하면 됩니다.

### Step 5: 검증 루프로 엣지 케이스까지 닫습니다

```python
verification_cases = [
    {
        "name": "sample",
        "nums": [7, 1, 11, 2, 9],
        "target": 10,
        "expected": (0, 3),
        "inspect_first": "정렬 후에도 원래 인덱스를 함께 들고 있는지 확인합니다.",
    },
    {
        "name": "no_solution",
        "nums": [1, 4, 8],
        "target": 20,
        "expected": None,
        "inspect_first": "while left < right 종료 조건과 None 반환 경로를 확인합니다.",
    },
    {
        "name": "duplicates",
        "nums": [3, 3, 4, 5],
        "target": 6,
        "expected": (0, 1),
        "inspect_first": "같은 값을 두 번 써도 되는 문제인지, 그리고 left < right를 지키는지 확인합니다.",
    },
    {
        "name": "negative_values",
        "nums": [-5, -1, 2, 8],
        "target": 3,
        "expected": (0, 3),
        "inspect_first": "정렬 후 포인터 이동 조건이 음수에서도 그대로 성립하는지 확인합니다.",
    },
    {
        "name": "minimal_input",
        "nums": [42],
        "target": 42,
        "expected": None,
        "inspect_first": "원소가 2개 미만일 때 while 루프가 바로 끝나는지 확인합니다.",
    },
]


for case in verification_cases:
    actual = solve_two_sum(case["nums"], case["target"])
    print(f"{case['name']:>14} | expected={case['expected']} | actual={actual}")
    assert actual == case["expected"], (
        f"{case['name']} failed. Inspect first: {case['inspect_first']}"
    )
```

이 검증 루프가 중요한 이유는 단순히 테스트 개수를 늘리기 위해서가 아닙니다. 실패를 네 가지 유형으로 빠르게 분해하기 위해서입니다.

- 해답이 없는데도 무언가 반환하면 종료 조건이 잘못된 경우가 많습니다.
- 중복 값 케이스가 틀리면 같은 원소를 두 번 쓰는 버그를 먼저 의심해야 합니다.
- 음수 케이스가 틀리면 포인터 이동 규칙을 값의 크기와 합 관점에서 다시 읽어야 합니다.
- 최소 입력에서 터지면 구현보다 먼저 경계 조건 처리가 빠졌는지 봐야 합니다.

### Step 6: 구현 속도를 올려 주는 Python 기본기

```python
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations, permutations
import heapq

# 1. Fast input
input = sys.stdin.readline

# 2. defaultdict — automatic key initialization
graph: dict[int, list[int]] = defaultdict(list)
graph[1].append(2)
graph[1].append(3)
print(dict(graph))  # {1: [2, 3]}

# 3. Counter — frequency counting
text = "hello world"
freq = Counter(text)
print(freq.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]

# 4. heapq — priority queue
heap: list[int] = []
for x in [5, 1, 3, 7, 2]:
    heapq.heappush(heap, x)
print(heapq.heappop(heap))  # 1

# 5. Combinations and permutations
print(list(combinations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,3)]
print(list(permutations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,1), ...]

# 6. Infinity
INF = float("inf")
print(min(INF, 42))  # 42

# 7. 2D array initialization
rows, cols = 3, 4
grid = [[0] * cols for _ in range(rows)]  # correct
# wrong = [[0] * cols] * rows  # bug: all rows reference the same list
```

코딩 테스트에서는 알고리즘 아이디어만큼 구현 속도도 중요합니다. 표준 라이브러리 활용과 흔한 함정 회피만으로도 큰 차이가 납니다.

## 이 코드에서 먼저 봐야 할 점

- 입력 크기에서 허용 시간 복잡도를 역산하는 것이 알고리즘 선택의 출발점입니다.
- 두 포인터는 "정렬 + 양끝 축소" 문제에서 `O(N^2)`를 `O(N log N)` 또는 `O(N)`으로 줄이는 핵심 패턴입니다.
- 구현이 끝난 뒤에는 샘플, 해답 없음, 중복, 음수, 최소 입력 순으로 검증 루프를 돌리는 편이 안전합니다.
- `defaultdict`, `Counter`, `heapq` 같은 표준 라이브러리는 구현 시간을 크게 줄여 줍니다.
- `[[0]*n]*m` 2차원 배열 초기화 버그는 매우 흔하므로 반드시 구분해야 합니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 입력 크기를 확인하지 않음 | 잘못된 복잡도의 알고리즘을 골라 시간 초과가 납니다 | 먼저 `N` 범위를 보고 탈락시킬 접근부터 정합니다 |
| 경계 조건을 무시함 | 빈 입력이나 `N=1`에서 런타임 오류가 납니다 | 경계 조건을 먼저 처리합니다 |
| 문제 유형 분류 없이 바로 구현 | DP, 그래프, 투 포인터 중 엉뚱한 방향으로 갑니다 | 정렬 여부, 목표 연산, 허용 복잡도를 먼저 적습니다 |
| 원본 인덱스를 잃어버림 | 값은 맞는데 정답 형식이 틀립니다 | 정렬 전에 `(값, 인덱스)` 쌍으로 묶습니다 |
| 테스트 없이 제출 | 사소한 버그를 놓칩니다 | 예제와 엣지 케이스를 모두 확인하고 실패 시 먼저 볼 지점을 정합니다 |

## 실무에서는 이렇게 연결됩니다

- 코딩 면접은 알고리즘 문제 해결 능력을 평가합니다.
- 성능 최적화는 종종 `O(N^2)`를 `O(N log N)`으로 낮추는 일에서 시작합니다.
- 데이터 파이프라인 설계도 입력 크기에 맞는 처리 알고리즘 선택이 중요합니다.
- API 응답 시간 최적화 역시 알고리즘 선택과 밀접합니다.
- 시스템 설계 면접에서도 복잡도 분석 능력은 기본입니다.

## 현업에서는 이렇게 생각합니다

코딩 테스트의 본질은 "올바른 알고리즘을 고르고, 시간 안에 정확히 구현하는 것"입니다. 많은 문제를 푸는 것도 중요하지만, 제약을 먼저 읽고 틀린 복잡도를 빨리 버리는 습관을 들이는 편이 더 큰 효과를 냅니다.

이 사고방식은 실무에도 그대로 이어집니다. "이 데이터 크기에서 이 알고리즘이 충분히 빠른가?"라는 질문은 시스템 설계의 기본이기 때문입니다.

## 체크리스트

- [ ] 입력 크기에서 허용 시간 복잡도를 역산할 수 있습니다
- [ ] 문제를 탐색, DP, 그래프, 그리디 등으로 분류할 수 있습니다
- [ ] 두 포인터 문제에서 잘못된 `O(N^2)` 접근을 먼저 기각할 수 있습니다
- [ ] Python 표준 라이브러리로 빠르게 구현할 수 있습니다
- [ ] 엣지 케이스를 체계적으로 테스트하고, 실패 시 먼저 볼 지점을 정할 수 있습니다

## 연습 문제

1. 정수 배열에서 합이 0이 되는 서로 다른 세 수 조합을 모두 찾아 보세요.
2. 문자열에서 가장 긴 팰린드롬 부분 문자열을 찾아 보세요.
3. `N×N` 격자에서 `(0,0)`부터 `(N-1,N-1)`까지의 최소 비용 경로를 구해 보세요.

## 정리와 마무리

코딩 테스트에서 가장 중요한 능력은 문제 유형을 빠르게 알아보고, 제약과 맞지 않는 접근을 초반에 버리는 것입니다. 입력 크기, 시간 복잡도, 알고리즘 선택, 구현, 검증으로 이어지는 흐름이 몸에 익으면 처음 보는 문제도 체계적으로 접근할 수 있습니다. 이 시리즈에서 다룬 탐색, 정렬, 재귀, DP, 그래프, 그리디는 코딩 테스트의 핵심 도구 상자이지만, 마지막 완성도는 결국 검증 루프에서 결정됩니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법 기초](./06-dynamic-programming-basics.md)
- [그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [최단 경로 기초](./08-shortest-path-basics.md)
- [그리디 알고리즘](./09-greedy-algorithms.md)
- **코딩 테스트 문제 접근법 (현재 글)**
<!-- toc:end -->

## 참고 자료

### 언어와 라이브러리 레퍼런스

- [Python Documentation — collections](https://docs.python.org/3/library/collections.html)
- [Python Documentation — heapq](https://docs.python.org/3/library/heapq.html)
- [Python Documentation — itertools](https://docs.python.org/3/library/itertools.html)

### 연습 문제 모음

- [Baekjoon Online Judge — 단계별로 풀어보기](https://www.acmicpc.net/step)
- [Programmers — 코딩테스트 연습](https://programmers.co.kr/learn/challenges)

Tags: Python, Algorithms, Coding Test, Problem Solving, Interview
