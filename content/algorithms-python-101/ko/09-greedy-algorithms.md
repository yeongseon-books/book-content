---
series: algorithms-python-101
episode: 9
title: "Algorithms with Python 101 (9/10): 그리디 알고리즘"
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
  - Greedy
  - Optimization
  - Activity Selection
seo_description: 그리디 알고리즘 원리와 최적해 보장 조건을 파이썬으로 배웁니다. 활동 선택과 배낭 문제를 통해 그리디 전략 유효 상황과 반례 구별법을 익힙니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (9/10): 그리디 알고리즘

그리디 알고리즘은 어려워 보이는 문제를 짧고 빠른 구현으로 바꿔 주는 경우가 많아서 매력적입니다. 올바른 상황에서는 매 단계의 똑똑한 선택 하나만으로도 충분합니다.

이 글은 Algorithms with Python 101 시리즈의 아홉 번째 글입니다. 여기서는 그리디 전략이 유효해지는 조건을 살펴보고, 대표적인 Python 예제로 검증해 보겠습니다.

다만 그리디 논리는 어디에나 안전하지 않습니다. 어떤 문제에서는 통하고 다른 문제에서는 실패하는 이유를 알아야, 단순함이 함정이 되지 않습니다.

![Algorithms with Python 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/09/09-01-concept-overview.ko.png)
*Algorithms with Python 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 그리디 알고리즘이 최적해를 만드는 조건은 무엇일까요?
- 동전 거스름돈, 활동 선택, 분할 가능한 배낭 문제는 어떻게 풀까요?
- 그리디는 동적 계획법과 어떤 차이가 있을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> 그리디는 매 단계에서 지역적으로 최선인 선택을 하고, 그것이 전체 최적해로 이어지기를 기대하는 전략입니다.

## 개념 한눈에 보기

> 그리디 선택 속성 = 지역 최적 선택이 전체 최적해의 일부가 된다

```text
Coin change (denominations: 500, 100, 50, 10):
Make change for 1,260:
→ 500 × 2 = 1,000 (remaining: 260)
→ 100 × 2 = 200   (remaining: 60)
→  50 × 1 = 50    (remaining: 10)
→  10 × 1 = 10    (remaining: 0)
Total: 6 coins — optimal via greedy
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Greedy choice property | 지역 최적 선택이 전체 최적해에 포함되는 성질입니다 |
| Optimal substructure | 최적해가 부분 최적해들로 구성되는 성질입니다 |
| Activity selection | 겹치지 않는 활동을 최대한 많이 고르는 문제입니다 |
| Fractional knapsack | 물건을 쪼갤 수 있는 배낭 문제로, 그리디가 통합니다 |
| Counterexample | 그리디가 최적해를 내지 못하는 입력 사례입니다 |

## 그리디 vs DP 비교

| 기준 | 그리디 | 동적 계획법 |
|------|--------|-------------|
| 결정 방식 | 현재 최선 선택 (되돌리기 없음) | 모든 경우 고려 후 최적 선택 |
| 시간 복잡도 | 보통 `O(n log n)` | 보통 `O(n^2)` 이상 |
| 정당성 보장 | 증명 필요 (항상 성립 X) | 점화식이 올바르면 항상 성립 |
| 적용 조건 | 그리디 선택 속성 + 최적 부분 구조 | 최적 부분 구조 + 중복 부분 문제 |

## 적용 전후 비교

겹치지 않는 활동을 최대한 많이 고르는 두 가지 접근입니다.

```python
# before: 모든 조합 brute-force — O(2^n)
from itertools import combinations

def max_activities_brute(activities):
    n = len(activities)
    best = 0
    for r in range(1, n + 1):
        for combo in combinations(activities, r):
            ordered = sorted(combo)
            ok = all(ordered[i][1] <= ordered[i+1][0] for i in range(len(ordered)-1))
            if ok:
                best = max(best, r)
    return best
```

```python
# after: greedy 방식 — O(n log n)
def max_activities_greedy(activities):
    activities.sort(key=lambda x: x[1])  # 종료 시간 기준 정렬
    count, last_end = 0, 0
    for start, end in activities:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

## 단계별 실습

### 단계 1: 거스름돈 문제

```python
def coin_change_greedy(amount: int, coins: list[int] | None = None) -> dict[int, int]:
    """표준 화폐 체계에서 그리디 거스름돈."""
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
print(f"Change: {change}")  # {500: 2, 100: 2, 50: 1, 10: 1}
print(f"Coins used: {total}")  # 6
```

### 단계 2: 활동 선택 문제

```python
def activity_selection(
    activities: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """겹치지 않는 활동 최대 선택 — O(n log n)."""
    # 핵심: 종료 시간 기준 정렬
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
print(f"Selected: {result}")
# [(1, 4), (5, 7), (8, 11), (12, 16)]
print(f"Maximum activities: {len(result)}")  # 4
```

### 단계 3: 분할 가능 배낭 문제

```python
def fractional_knapsack(
    items: list[tuple[int, int]], capacity: int
) -> float:
    """분할 가능 배낭 — 가치/무게 비율 기준 그리디."""
    # (무게, 가치) 형태로 비율 내림차순 정렬
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

items = [(10, 60), (20, 100), (30, 120)]  # (weight, value)
print(fractional_knapsack(items, 50))  # 240.0
```

### 단계 4: 회의실 최소 개수

```python
def min_meeting_rooms(meetings: list[tuple[int, int]]) -> int:
    """최소 필요 회의실 수 — O(n log n)."""
    events: list[tuple[int, int]] = []
    for start, end in meetings:
        events.append((start, 1))   # 시작: +1
        events.append((end, -1))    # 종료: -1

    events.sort(key=lambda x: (x[0], x[1]))  # 시간 오름차순, 종료 우선
    max_rooms = 0
    current = 0
    for _, delta in events:
        current += delta
        max_rooms = max(max_rooms, current)

    return max_rooms

meetings = [(0, 30), (5, 10), (15, 20)]
print(f"Minimum rooms: {min_meeting_rooms(meetings)}")  # 2
```

### 단계 5: Greedy vs DP — 반례 비교

```python
# 표준이 아닌 동전 단위에서는 Greedy가 실패
# Coins: [1, 3, 4], amount: 6
# Greedy: 4+1+1 = 3 coins
# Optimal: 3+3 = 2 coins

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
print(f"Greedy: {coin_change_greedy_count(coins, amount)} coins")  # 3 (4+1+1) — 틀림!
print(f"DP:     {coin_change_dp(coins, amount)} coins")            # 2 (3+3)   — 정답
```

## 단계별 실행 추적 — 활동 선택

`activity_selection([(1,4),(3,5),(0,6),(5,7),(8,11),(12,16)])` 추적:

```text
종료 시간 정렬:
  (1,4), (3,5), (0,6), (5,7), (8,11), (12,16)

last_end=0:
  (1,4): 1 >= 0 → 선택! selected=[(1,4)], last_end=4
  (3,5): 3 >= 4? No → skip
  (0,6): 0 >= 4? No → skip
  (5,7): 5 >= 4 → 선택! selected=[(1,4),(5,7)], last_end=7
  (8,11): 8 >= 7 → 선택! selected=[(1,4),(5,7),(8,11)], last_end=11
  (12,16): 12 >= 11 → 선택! selected=[..., (12,16)], last_end=16

결과: 4개의 활동 선택
```

## 코딩 테스트 풀이 예시

**문제**: 주유 최소 횟수로 목적지까지 가라.

```python
def min_refuels(
    distance: int,
    fuel: int,
    stops: list[tuple[int, int]],
) -> int:
    """
    주유소를 최소 횟수 방문해 목적지에 도달합니다.
    stops: [(위치, 추가 연료)] 형태
    시간 복잡도: O(n log n)
    """
    import heapq

    # 현재 위치와 연료로 갈 수 있는 주유소를 힙에 관리
    stops_with_end = stops + [(distance, 0)]
    stops_with_end.sort()

    max_heap: list[int] = []  # 음수로 최대 힙 흉내
    current_fuel = fuel
    refuels = 0
    prev_pos = 0

    for pos, added_fuel in stops_with_end:
        current_fuel -= (pos - prev_pos)  # 이동 소모

        while current_fuel < 0:
            if not max_heap:
                return -1  # 도달 불가
            current_fuel += -heapq.heappop(max_heap)  # 최대 연료 주유소 선택
            refuels += 1

        heapq.heappush(max_heap, -added_fuel)
        prev_pos = pos

    return refuels


print(min_refuels(100, 10, [(10, 60), (20, 30), (30, 30), (60, 40)]))  # 2
```

**문제**: 가장 많은 구간을 제거해 겹치지 않게 만들어라.

```python
def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    """
    겹치지 않도록 최소 제거 구간 수를 반환합니다.
    종료 시간 오름차순 정렬 후 그리디.
    시간 복잡도: O(n log n)
    """
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[1])  # 종료 시간 정렬
    keep = 1  # 첫 구간은 항상 유지
    last_end = intervals[0][1]

    for start, end in intervals[1:]:
        if start >= last_end:
            keep += 1
            last_end = end
        # else: 겹침 → 제거 (종료 시간이 더 빠른 현재 구간 유지)

    return len(intervals) - keep


print(erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]))  # 1
print(erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]))           # 2
```

**단계별 추적** (`[[1,2],[2,3],[3,4],[1,3]]` 입력):

```text
종료 시간 정렬: [[1,2],[2,3],[1,3],[3,4]]

keep=1, last_end=2 (첫 구간 [1,2] 유지)

[2,3]: 2 >= 2 → 유지, keep=2, last_end=3
[1,3]: 1 >= 3? No → 겹침 → 제거 (last_end 유지)
[3,4]: 3 >= 3 → 유지, keep=3, last_end=4

제거 수 = 4 - 3 = 1
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 그리디의 정당성을 확인하지 않음 | 최적이 아닌 답을 낼 수 있습니다 | 반례를 찾거나 그리디 선택 속성을 증명합니다 |
| 정렬 기준을 잘못 잡음 | 잘못된 순서로 선택합니다 | 정렬 키가 최적 전략과 맞는지 검증합니다 |
| 0-1 배낭에 그리디 적용 | 물건을 쪼갤 수 없어 최적이 아닙니다 | 0-1 배낭은 DP를 사용합니다 |
| 모든 거스름돈 문제를 그리디로 풂 | 비표준 화폐 체계에서 실패합니다 | 화폐 체계 조건을 확인합니다 |
| DP가 필요한 문제에 그리디 강행 | 지역 최적이 전체 최적이 아닐 수 있습니다 | 그리디 선택 속성을 먼저 확인합니다 |

## 그리디 성공/실패 패턴표

| 문제 | 그리디 성공 여부 | 이유 |
|------|------------------|------|
| 활동 선택 | 성공 | 빠른 종료 선택이 이후 선택 공간 최대화 |
| 분할 가능한 배낭 | 성공 | 비율 선택이 전체 최적과 일치 |
| 0-1 배낭 | 실패 가능 | 분할 불가, 지역 최적이 전역 최적 보장 못함 |
| 비표준 동전 거스름돈 | 실패 가능 | 화폐 체계 구조 조건 불충분 |
| 최소 회의실 | 성공 | 이벤트 정렬 후 최대 동시 발생 횟수 계산 |

## 실무에서는 이렇게 연결됩니다

- 허프만 코딩은 그리디로 최적 압축 트리를 만듭니다.
- 작업 스케줄링은 마감 시간과 이익 기준 선택으로 이어집니다.
- 최소 신장 트리의 Kruskal, Prim도 그리디 전략입니다.
- 캐시 교체 정책은 그리디 휴리스틱에 기반한 경우가 많습니다.
- API rate limit 최적화도 요청을 묶는 그리디 전략으로 이어질 수 있습니다.

## 현업에서는 이렇게 생각합니다

그리디는 "일단 해 보고 맞나 보자" 식의 알고리즘이 아닙니다. 정당성을 확인하지 않으면 대부분 맞다가 특정 엣지 케이스에서 실패하는 코드를 만들게 됩니다.

코딩 테스트에서 그리디 풀이를 제안한다면, 왜 이 선택이 최적인지 한 문장으로 설명할 수 있어야 합니다. 그 설명이 없다면 DP를 먼저 의심하는 편이 안전합니다.

## 운영 체크리스트

- [ ] 그리디가 최적해를 만드는 조건을 설명할 수 있습니다
- [ ] 활동 선택 문제를 그리디로 풀 수 있습니다
- [ ] 분할 가능한 배낭과 0-1 배낭의 차이를 설명할 수 있습니다
- [ ] 그리디가 실패하는 반례를 찾을 수 있습니다
- [ ] 그리디와 DP를 언제 구분해야 하는지 판단할 수 있습니다

## 연습 문제

1. 문자 빈도로 허프만 코딩 트리를 만들어 보세요.
2. 마감 시간과 이익이 있는 작업 목록에서 최대 이익 스케줄을 구해 보세요.
3. 여러 도시를 지나는 동안 최소 횟수로 주유하는 문제를 풀어 보세요.

## 정리와 다음 글

그리디 알고리즘은 매 단계의 지역 최적 선택을 기반으로 합니다. 보통 정렬과 단일 순회로 빠르게 풀리지만, 항상 최적해를 보장하지는 않습니다. 마지막 글에서는 지금까지 배운 내용을 코딩 테스트 문제 풀이 전략으로 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- **Algorithms with Python 101 (9/10): 그리디 알고리즘 (현재 글)**
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Greedy Algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [GeeksforGeeks — Greedy Algorithms](https://www.geeksforgeeks.org/greedy-algorithms/)
- [Real Python — Greedy Algorithms in Python](https://realpython.com/python-greedy-algorithm/)
- [LeetCode — Greedy Problems](https://leetcode.com/tag/greedy/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/09-greedy-algorithms)

Tags: Python, Algorithms, Greedy, Optimization, Activity Selection
