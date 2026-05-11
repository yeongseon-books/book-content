---
series: algorithms-python-101
episode: 10
title: 코딩 테스트 문제 접근법
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - 알고리즘
  - 코딩 테스트
  - 문제 풀이
  - 면접
seo_description: 코딩 테스트에서 문제 유형을 파악하고 체계적으로 풀어가는 전략을 다룹니다.
last_reviewed: '2026-05-04'
---

# 코딩 테스트 문제 접근법

> Algorithms with Python 101 시리즈 (10/10)


## 이 글에서 다룰 문제

알고리즘을 배웠어도 실전 문제 앞에서 어떤 알고리즘을 쓸지 판단하지 못하면 소용없습니다. 문제 유형을 빠르게 분류하고, 제약 조건에서 필요한 시간 복잡도를 역으로 추론하는 능력이 핵심입니다.

> 문제 접근법 = 입력 분석 → 유형 분류 → 알고리즘 선택 → 구현 → 검증

코딩 테스트는 제한 시간 안에 정확한 코드를 작성하는 시험입니다. 체계적인 접근법이 있으면 시간을 절약하고 실수를 줄일 수 있습니다.

## 핵심 개념 잡기

> 입력 크기 → 허용 시간 복잡도 역추론

```
입력 크기(N)에 따른 허용 시간 복잡도 (1초 기준):
N ≤ 10        → O(N!)       — 완전 탐색
N ≤ 20        → O(2^N)      — 비트마스크, 백트래킹
N ≤ 500       → O(N³)       — 플로이드-워셜
N ≤ 5,000     → O(N²)       — DP, 이중 루프
N ≤ 1,000,000 → O(N log N)  — 정렬, 이진 탐색
N ≤ 10^8      → O(N)        — 선형 탐색, 투 포인터
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 완전 탐색(brute force) | 모든 가능한 경우를 탐색하는 가장 기본적인 접근입니다 |
| 투 포인터(two pointers) | 두 개의 포인터를 이동시키며 O(N)에 해결하는 기법입니다 |
| 슬라이딩 윈도우(sliding window) | 고정 크기 구간을 이동시키며 부분합 등을 구하는 기법입니다 |
| 백트래킹(backtracking) | 조건을 만족하지 않으면 되돌아가는 탐색입니다 |
| 에지 케이스(edge case) | 빈 입력, 최댓값, 최솟값 등 경계 조건입니다 |

## Before / After

문제 풀이 접근 방식을 비교합니다.

```python
# before: 바로 코딩 시작 — 잘못된 알고리즘 선택 위험
def solve(data):
    # 생각 없이 이중 루프 → 시간 초과
    for i in range(len(data)):
        for j in range(len(data)):
            pass  # O(N²) — N이 100만이면 시간 초과
```

```python
# after: 입력 크기 분석 후 알고리즘 선택
def solve(data):
    # N=1,000,000 → O(N) 또는 O(N log N) 필요
    # 정렬 + 투 포인터로 접근
    data.sort()  # O(N log N)
    left, right = 0, len(data) - 1
    # ... O(N) 탐색
```

## 단계별 실습

### Step 1: 문제 풀이 4단계 프레임워크

```python
"""
문제 풀이 4단계:

1. 이해(Understand)
   - 입력/출력 형식 확인
   - 제약 조건(N의 범위, 시간 제한) 확인
   - 예제를 손으로 따라가기

2. 계획(Plan)
   - 입력 크기에서 허용 시간 복잡도 역추론
   - 문제 유형 분류 (탐색, 정렬, DP, 그래프 등)
   - 핵심 아이디어 정리

3. 구현(Implement)
   - 의사 코드를 먼저 작성
   - 한 단계씩 구현하며 중간 결과 확인
   - 에지 케이스 처리

4. 검증(Verify)
   - 예제 입력으로 테스트
   - 에지 케이스 테스트: 빈 입력, 최솟값, 최댓값, 중복
   - 시간 복잡도 재확인
"""
```

### Step 2: 투 포인터 패턴

```python
def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int] | None:
    """정렬된 배열에서 합이 target인 두 수 찾기 — O(N)"""
    left, right = 0, len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return (left, right)
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return None

nums = [1, 2, 4, 6, 8, 10]
print(two_sum_sorted(nums, 10))  # (1, 4) → 2+8=10


def remove_duplicates(nums: list[int]) -> int:
    """정렬된 배열에서 중복 제거 — O(N), 제자리"""
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1
    return write

nums = [1, 1, 2, 2, 3, 4, 4, 5]
k = remove_duplicates(nums)
print(nums[:k])  # [1, 2, 3, 4, 5]
```

### Step 3: 슬라이딩 윈도우 패턴

```python
def max_subarray_sum(nums: list[int], k: int) -> int:
    """길이 k인 연속 부분 배열의 최대 합 — O(N)"""
    if len(nums) < k:
        return 0

    window_sum = sum(nums[:k])
    max_sum = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum

nums = [2, 1, 5, 1, 3, 2]
print(max_subarray_sum(nums, 3))  # 9 (5+1+3)


def longest_unique_substring(s: str) -> int:
    """중복 없는 가장 긴 부분 문자열 — O(N)"""
    char_index: dict[str, int] = {}
    max_len = 0
    left = 0

    for right, char in enumerate(s):
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len

print(longest_unique_substring("abcabcbb"))  # 3 ("abc")
print(longest_unique_substring("pwwkew"))    # 3 ("wke")
```

### Step 4: 유형별 판별 기준

```python
"""
문제 유형 판별 체크리스트:

[탐색/정렬]
- "~를 찾아라" + 정렬된 데이터 → 이진 탐색
- "정렬하라" → sorted() 또는 커스텀 정렬
- "k번째 큰/작은" → 정렬 또는 heapq.nlargest

[DP]
- "최솟값/최댓값을 구하라" + "경우의 수" → DP
- "~하는 방법의 수" → DP
- 점화식이 보이면 → DP

[그래프]
- "연결 여부" → BFS/DFS
- "최단 거리" + 가중치 없음 → BFS
- "최단 거리" + 가중치 있음 → 다익스트라
- "사이클 탐지" → DFS

[그리디]
- "~의 최솟값/최댓값" + 정렬로 해결 가능 → 그리디
- 매 선택이 이후에 영향 없음 → 그리디

[문자열]
- "부분 문자열" → 슬라이딩 윈도우 또는 투 포인터
- "패턴 매칭" → KMP 또는 정규표현식
"""
```

### Step 5: Python 코딩 테스트 필수 팁

```python
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations, permutations
import heapq

# 1. 빠른 입력
input = sys.stdin.readline

# 2. defaultdict — 키 초기화 자동
graph: dict[int, list[int]] = defaultdict(list)
graph[1].append(2)
graph[1].append(3)
print(dict(graph))  # {1: [2, 3]}

# 3. Counter — 빈도 계산
text = "hello world"
freq = Counter(text)
print(freq.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]

# 4. heapq — 우선순위 큐
heap: list[int] = []
for x in [5, 1, 3, 7, 2]:
    heapq.heappush(heap, x)
print(heapq.heappop(heap))  # 1

# 5. 조합과 순열
print(list(combinations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,3)]
print(list(permutations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,1), ...]

# 6. 무한대
INF = float("inf")
print(min(INF, 42))  # 42

# 7. 2차원 배열 초기화
rows, cols = 3, 4
grid = [[0] * cols for _ in range(rows)]  # 올바름
# wrong = [[0] * cols] * rows  # 같은 리스트를 참조하는 버그
```

## 이 코드에서 주목할 점

- 입력 크기에서 시간 복잡도를 역추론하는 것이 알고리즘 선택의 출발점입니다
- 투 포인터와 슬라이딩 윈도우는 O(N²)를 O(N)으로 줄이는 핵심 패턴입니다
- defaultdict, Counter, heapq 등 Python 표준 라이브러리를 활용하면 구현 시간을 절약합니다
- 2차원 배열 초기화에서 `[[0]*n]*m` 버그는 매우 흔합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 입력 크기를 확인하지 않음 | 시간 복잡도가 맞지 않아 시간 초과입니다 | N의 범위를 먼저 확인합니다 |
| 에지 케이스 미처리 | 빈 입력, N=1 등에서 런타임 에러입니다 | 경계 조건을 먼저 처리합니다 |
| 완전 탐색부터 시작하지 않음 | 최적화할 기준점이 없습니다 | 완전 탐색 → 최적화 순서로 접근합니다 |
| 의사 코드 없이 바로 코딩 | 논리 오류를 늦게 발견합니다 | 의사 코드를 먼저 작성합니다 |
| 테스트하지 않고 제출 | 사소한 오류를 놓칩니다 | 예제와 에지 케이스를 모두 테스트합니다 |

## 실무에서 이렇게 쓰입니다

- 코딩 면접에서 알고리즘 문제 풀이 능력을 평가합니다
- 성능 최적화에서 O(N²) → O(N log N) 개선이 필요합니다
- 데이터 파이프라인에서 대규모 데이터 처리 로직을 설계합니다
- API 응답 시간 최적화에서 알고리즘 선택이 중요합니다
- 시스템 설계 면접에서 알고리즘 복잡도 분석 능력이 필요합니다

## 현업 개발자는 이렇게 생각합니다

코딩 테스트의 본질은 "제한된 시간 안에 올바른 알고리즘을 선택하고 구현하는 능력"입니다. 많은 문제를 풀어보는 것도 중요하지만, 풀이 과정을 체계화하는 것이 더 효과적입니다.

실무에서도 동일한 사고방식이 필요합니다. "이 데이터 크기에서 이 알고리즘이 충분히 빠른가?"라는 질문은 시스템 설계의 기본입니다.

## 체크리스트

- [ ] 입력 크기에서 허용 시간 복잡도를 역추론할 수 있다
- [ ] 문제를 보고 유형(탐색, DP, 그래프, 그리디)을 분류할 수 있다
- [ ] 투 포인터와 슬라이딩 윈도우 패턴을 적용할 수 있다
- [ ] Python 표준 라이브러리를 활용하여 빠르게 구현할 수 있다
- [ ] 에지 케이스를 체계적으로 테스트할 수 있다

## 정리 및 다음 글 안내

코딩 테스트에서 가장 중요한 것은 문제를 보고 유형을 파악하는 능력입니다. 입력 크기 → 시간 복잡도 → 알고리즘 선택의 흐름을 체화하면 어떤 문제든 체계적으로 접근할 수 있습니다. 이 시리즈에서 다룬 탐색, 정렬, 재귀, DP, 그래프, 그리디가 코딩 테스트의 핵심 도구입니다.

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

- [LeetCode — Top Interview Questions](https://leetcode.com/problem-list/top-interview-questions/)
- [백준 온라인 저지 — 단계별로 풀어보기](https://www.acmicpc.net/step)
- [프로그래머스 — 코딩테스트 연습](https://programmers.co.kr/learn/challenges)
- [Real Python — Python Practice Problems](https://realpython.com/python-practice-problems/)
