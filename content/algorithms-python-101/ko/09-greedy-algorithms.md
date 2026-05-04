---
series: algorithms-python-101
episode: 9
title: 그리디 알고리즘
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
  - 그리디
  - 탐욕법
  - 최적화
seo_description: Python으로 그리디 알고리즘의 원리를 이해하고 대표 문제를 풀어봅니다.
last_reviewed: '2026-05-04'
---

# 그리디 알고리즘

> Algorithms with Python 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 매 순간 최선의 선택이 전체 최적해를 보장할 수 있을까요?

> 그리디 알고리즘은 각 단계에서 현재 최선의 선택을 하여 전체 최적해에 도달하는 전략입니다. 항상 최적해를 보장하지는 않지만, 특정 조건이 만족되면 DP보다 빠르고 간결합니다. 이 글에서는 그리디가 적용되는 조건과 대표 문제를 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 그리디 알고리즘이 적용 가능한 조건
- 거스름돈, 활동 선택, 분할 가능 배낭 문제
- 그리디와 DP의 비교
- 그리디의 정당성을 검증하는 방법

## 왜 중요한가

그리디 알고리즘은 구현이 간결하고 실행 속도가 빠릅니다. 정렬 + 한 번 순회로 O(n log n)에 끝나는 문제가 많아, DP의 O(n²)보다 훨씬 효율적입니다.

> 그리디 = 매 단계에서 지역적 최적(local optimum)을 선택하여 전역적 최적(global optimum)에 도달하는 전략

다만 그리디가 항상 최적해를 주는 것은 아닙니다. "그리디 선택 속성"과 "최적 부분 구조"가 모두 성립해야 합니다.

## 핵심 개념 잡기

> 그리디 선택 속성 = 현재의 최적 선택이 이후 선택에 영향을 주지 않는 성질

```
거스름돈 문제 (동전: 500, 100, 50, 10):
1,260원 거스름돈:
→ 500 × 2 = 1,000 (남은: 260)
→ 100 × 2 = 200   (남은: 60)
→  50 × 1 = 50    (남은: 10)
→  10 × 1 = 10    (남은: 0)
총 6개 — 그리디로 최적해
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 그리디 선택 속성(greedy choice property) | 지역 최적 선택이 전역 최적해에 포함되는 성질입니다 |
| 최적 부분 구조(optimal substructure) | 부분 문제의 최적해로 전체 최적해를 구성할 수 있는 성질입니다 |
| 활동 선택 문제(activity selection) | 겹치지 않는 최대 활동 수를 선택하는 문제입니다 |
| 분할 가능 배낭(fractional knapsack) | 물건을 쪼갤 수 있는 배낭 문제로, 그리디로 풀립니다 |
| 반례(counterexample) | 그리디가 최적해를 주지 않는 입력입니다 |

## Before / After

겹치지 않는 최대 활동 수를 구하는 두 가지 방법을 비교합니다.

```python
# before: 모든 조합 탐색 — O(2^n)
from itertools import combinations

def max_activities(activities):
    best = 0
    for r in range(len(activities), 0, -1):
        for combo in combinations(activities, r):
            if not overlapping(combo):
                return r
    return best
```

```python
# after: 그리디 — O(n log n)
def max_activities(activities):
    activities.sort(key=lambda x: x[1])  # 종료 시간 기준 정렬
    count, last_end = 0, 0
    for start, end in activities:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

## 단계별 실습

### Step 1: 거스름돈 문제

```python
def coin_change_greedy(amount: int, coins: list[int] | None = None) -> dict[int, int]:
    """그리디 거스름돈 — 큰 동전부터 사용"""
    if coins is None:
        coins = [500, 100, 50, 10]
    result: dict[int, int] = {}

    for coin in sorted(coins, reverse=True):
        if amount >= coin:
            count = amount // coin
            result[coin] = count
            amount -= coin * count

    return result

change = coin_change_greedy(1260)
total = sum(change.values())
print(f"거스름돈: {change}")  # {500: 2, 100: 2, 50: 1, 10: 1}
print(f"동전 개수: {total}")  # 6
```

### Step 2: 활동 선택 문제

```python
def activity_selection(
    activities: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """겹치지 않는 최대 활동 선택 — O(n log n)"""
    sorted_acts = sorted(activities, key=lambda x: x[1])
    selected: list[tuple[int, int]] = []
    last_end = 0

    for start, end in sorted_acts:
        if start >= last_end:
            selected.append((start, end))
            last_end = end

    return selected

activities = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
              (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
result = activity_selection(activities)
print(f"선택된 활동: {result}")
# [(1, 4), (5, 7), (8, 11), (12, 16)]
print(f"최대 활동 수: {len(result)}")  # 4
```

### Step 3: 분할 가능 배낭 문제

```python
def fractional_knapsack(
    items: list[tuple[int, int]], capacity: int
) -> float:
    """분할 가능 배낭 — O(n log n)"""
    # (가중치, 가치) → 단위 가치 기준 내림차순 정렬
    sorted_items = sorted(
        items, key=lambda x: x[1] / x[0], reverse=True
    )
    total_value = 0.0

    for weight, value in sorted_items:
        if capacity >= weight:
            total_value += value
            capacity -= weight
        else:
            fraction = capacity / weight
            total_value += value * fraction
            break

    return total_value

items = [(10, 60), (20, 100), (30, 120)]  # (무게, 가치)
print(fractional_knapsack(items, 50))  # 240.0
```

### Step 4: 회의실 배정과 구간 스케줄링

```python
def min_meeting_rooms(meetings: list[tuple[int, int]]) -> int:
    """최소 회의실 수 — O(n log n)"""
    events: list[tuple[int, int]] = []
    for start, end in meetings:
        events.append((start, 1))   # 시작: +1
        events.append((end, -1))    # 종료: -1

    events.sort()
    max_rooms = 0
    current = 0
    for _, delta in events:
        current += delta
        max_rooms = max(max_rooms, current)

    return max_rooms

meetings = [(0, 30), (5, 10), (15, 20)]
print(f"최소 회의실: {min_meeting_rooms(meetings)}개")  # 2

meetings2 = [(1, 5), (2, 3), (4, 6), (7, 8)]
print(f"최소 회의실: {min_meeting_rooms(meetings2)}개")  # 2
```

### Step 5: 그리디 vs DP 비교

```python
# 그리디가 실패하는 예: 특수 동전 체계
# 동전: [1, 3, 4]으로 6원을 만들기
# 그리디: 4+1+1 = 3개
# 최적:  3+3 = 2개

def coin_change_greedy_count(coins: list[int], amount: int) -> int:
    count = 0
    for coin in sorted(coins, reverse=True):
        count += amount // coin
        amount %= coin
    return count

def coin_change_dp(coins: list[int], amount: int) -> int:
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1
    return dp[amount]

coins = [1, 3, 4]
amount = 6
print(f"그리디: {coin_change_greedy_count(coins, amount)}개")  # 3 (4+1+1)
print(f"DP:     {coin_change_dp(coins, amount)}개")            # 2 (3+3)
```

## 이 코드에서 주목할 점

- 그리디는 정렬이 핵심입니다. 올바른 기준으로 정렬하면 한 번 순회로 해결됩니다
- 활동 선택 문제는 종료 시간 기준 정렬이 최적 전략입니다
- 분할 가능 배낭은 단위 가치 기준 정렬로 그리디가 최적해를 줍니다
- 특수 동전 체계에서 그리디가 실패하는 예시는 반례의 중요성을 보여줍니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 그리디 정당성을 검증하지 않음 | 최적해가 아닌 결과를 반환합니다 | 반례를 찾거나 수학적으로 증명합니다 |
| 정렬 기준 오류 | 잘못된 순서로 선택합니다 | 문제에 맞는 정렬 기준을 확인합니다 |
| 0-1 배낭에 그리디 적용 | 물건을 쪼갤 수 없으면 최적해가 아닙니다 | DP를 사용합니다 |
| 동전 문제에 항상 그리디 적용 | 특수 동전 체계에서 실패합니다 | 동전이 배수 관계인지 확인합니다 |
| DP가 필요한 문제에 그리디 적용 | 지역 최적이 전역 최적이 아닙니다 | 그리디 선택 속성을 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 허프만 코딩이 그리디로 최적 압축 트리를 만듭니다
- 작업 스케줄링에서 마감 기한이 있는 작업을 최적 배치합니다
- 네트워크에서 최소 신장 트리(크루스칼, 프림)가 그리디입니다
- 캐시 교체 정책(LRU)이 그리디 전략에 기반합니다
- API 요금 최적화에서 요청을 그리디로 배치합니다

## 현업 개발자는 이렇게 생각합니다

그리디는 "일단 해보고 되면 쓰는" 알고리즘이 아닙니다. 정당성을 확인하지 않으면 대부분의 입력에서는 맞지만 특정 엣지 케이스에서 틀리는 위험한 코드가 됩니다.

코딩 면접에서 그리디를 쓸 때는 왜 그리디가 최적인지 한 문장으로 설명할 수 있어야 합니다. 설명할 수 없다면 DP를 고려하는 것이 안전합니다.

## 체크리스트

- [ ] 그리디 알고리즘이 적용 가능한 조건을 설명할 수 있다
- [ ] 활동 선택 문제를 그리디로 풀 수 있다
- [ ] 분할 가능 배낭과 0-1 배낭의 차이를 설명할 수 있다
- [ ] 그리디가 실패하는 반례를 찾을 수 있다
- [ ] 그리디와 DP의 적용 기준을 구분할 수 있다

## 연습 문제

1. 문자열에서 각 문자의 빈도를 구하고 허프만 코딩 트리를 만드세요.
2. 마감 기한과 이익이 주어진 작업 목록에서 최대 이익 스케줄을 구하세요.
3. 주유소 문제: N개 도시 사이를 최소 주유 횟수로 이동하는 전략을 구하세요.

## 정리 및 다음 글 안내

그리디 알고리즘은 매 단계에서 최선의 선택을 반복합니다. 정렬 + 한 번 순회로 효율적이지만, 항상 최적해를 보장하지는 않습니다. 다음 글에서는 시리즈를 마무리하며 코딩 테스트 문제 접근법을 정리합니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법 기초](./06-dynamic-programming-basics.md)
- [그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [최단 경로 기초](./08-shortest-path-basics.md)
- **그리디 알고리즘 (현재 글)**
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Greedy Algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [GeeksforGeeks — Greedy Algorithms](https://www.geeksforgeeks.org/greedy-algorithms/)
- [Real Python — Greedy Algorithms in Python](https://realpython.com/python-greedy-algorithm/)
- [LeetCode — Greedy Problems](https://leetcode.com/tag/greedy/)

Tags: Python, 알고리즘, 그리디, 탐욕법, 최적화
