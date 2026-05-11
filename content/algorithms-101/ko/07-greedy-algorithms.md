---
series: algorithms-101
episode: 7
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
  - Computer Science
  - 알고리즘
  - 그리디
  - 교환 논증
  - 최적화
  - 활동 선택
seo_description: 그리디 알고리즘이 통하는 조건과 교환 논증의 사고법, 대표 그리디 문제들, 그리고 그리디처럼 보이지만 DP가 필요한 함정을 정리합니다.
last_reviewed: '2026-05-04'
---

# 그리디 알고리즘

> Algorithms 101 시리즈 (7/10)


## 이 글에서 다룰 문제

그리디는 가장 단순하고 가장 빠른 부류의 알고리즘입니다. 통한다면 작성과 운영이 쉬우며, O(n log n) 정도로 끝나는 경우가 많습니다. 단점은 정당성 증명을 게을리하면 잘못된 답을 내고도 그것을 알아채기 어렵다는 점입니다. 그리디를 잘 다룬다는 것은 "언제 통하는지"를 정확히 안다는 것과 같습니다.

> 그리디는 단순함의 알고리즘이지만, 정확성에 대한 책임은 더 무겁습니다.

## 전체 흐름
> 그리디 선택 속성은 "지금의 국소 최적이 전체 최적의 일부일 수 있다"는 것이며, 최적 부분 구조는 "남은 문제도 같은 그리디 규칙으로 풀린다"는 것입니다. 두 조건이 동시에 성립해야 그리디가 옳습니다. 일반적으로는 교환 논증으로 증명합니다.

```text
그리디가 옳기 위한 조건
    1) 그리디 선택 속성  : 첫 그리디 선택을 포함한 최적해가 존재
    2) 최적 부분 구조    : 그 선택 이후의 부분 문제도 같은 방식으로 최적해

교환 논증
    임의의 최적해 OPT의 첫 선택을 그리디 선택과 교환해도
    여전히 최적해임을 보임
```

## Before / After

**Before — 동전 거스름돈에 잘못된 그리디:**

```python
# 동전 [1, 3, 4]로 6원을 거슬러주기
def greedy_change(coins, amount):
    coins = sorted(coins, reverse=True)
    n = 0
    for c in coins:
        n += amount // c
        amount %= c
    return n

print(greedy_change([1, 3, 4], 6))   # 3 (4+1+1) — 최적은 2 (3+3)
```

**After — 그리디가 통하지 않을 때는 DP:**

```python
def min_coins(coins, amount):
    INF = float('inf')
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

print(min_coins([1, 3, 4], 6))   # 2
```

## 단계별로 따라하기

### 1단계: 활동 선택 — 끝나는 시각이 빠른 것부터

```python
def activity_selection(intervals):
    """[(start, end), ...] → 겹치지 않는 최대 개수"""
    intervals = sorted(intervals, key=lambda x: x[1])
    chosen, last_end = 0, -1
    for s, e in intervals:
        if s >= last_end:
            chosen += 1
            last_end = e
    return chosen

print(activity_selection([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]))   # 4
```

"끝나는 시각이 빠른 것"을 그리디로 고르면 항상 최적입니다. 교환 논증으로 증명할 수 있습니다.

### 2단계: 회의실 배정 — 시작 시간이 아닌 종료 시간 정렬

```python
meetings = [(1, 5), (2, 3), (3, 4), (4, 6), (6, 8)]
print(activity_selection(meetings))   # 3 — (2,3), (3,4), (4,6) ... 가장 많은 회의 수
```

같은 알고리즘이 회의실 배정·강의실 스케줄링에 그대로 적용됩니다. 정렬 키 한 줄이 정확성을 좌우합니다.

### 3단계: 거스름돈 — 그리디가 통하는 동전 시스템

```python
def coin_change_greedy(coins, amount):
    coins = sorted(coins, reverse=True)
    used = []
    for c in coins:
        while amount >= c:
            amount -= c
            used.append(c)
    return used if amount == 0 else None

# 한국·미국식 동전 시스템은 그리디가 최적
print(coin_change_greedy([500, 100, 50, 10], 1260))
```

동전 시스템이 "정규(canonical)"이면 그리디가 최적입니다. 임의의 동전 집합에서는 보장되지 않으므로 DP로 풀어야 합니다.

### 4단계: Huffman 코드 — 우선순위 큐 기반 그리디

```python
import heapq

def huffman(freq):
    h = [[w, c] for c, w in freq.items()]
    heapq.heapify(h)
    while len(h) > 1:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        heapq.heappush(h, [a[0] + b[0], (a, b)])
    return h[0]

print(huffman({"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45}))
```

가장 빈도가 낮은 두 노드를 합치는 것을 반복합니다. 압축 비율 측면에서 무손실 코드의 최적 prefix code를 만들어냅니다.

### 5단계: 분수 knapsack — 0/1과 분수의 차이

```python
def fractional_knapsack(weights, values, W):
    items = sorted(zip(weights, values), key=lambda x: -x[1] / x[0])
    total = 0.0
    for w, v in items:
        if W >= w:
            W -= w; total += v
        else:
            total += v * (W / w); break
    return total

print(fractional_knapsack([10, 20, 30], [60, 100, 120], 50))   # 240.0
```

분수 knapsack은 그리디로 최적이지만 0/1 knapsack은 DP가 필요합니다. "쪼갤 수 있느냐"가 그리디 적용 여부를 가릅니다.

## 이 코드에서 주목할 점

- 정렬 키 하나가 그리디 정당성의 거의 전부
- "쪼갤 수 있는가"가 분수와 0/1을 가르는 결정적 차이
- 우선순위 큐는 그리디 알고리즘의 단골 도구
- 직관에 의존하지 말고 교환 논증으로 정당성 확인

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정당성 증명 없이 그리디 채택 | 미묘하게 틀린 답 | 교환 논증으로 검증 |
| 그리디로 보이는데 사실 DP 문제 | 잘못된 답 | 작은 반례를 손으로 만들어 보기 |
| 잘못된 정렬 키 | 답이 1~2 차이 | 시작/끝/비율 등 후보 비교 |
| 우선순위 큐 누락 | O(n²) | heap 도입으로 O(n log n) |
| 부분 해 되돌리기 | 그리디 본질 위반 | 그리디는 되돌리지 않음, 필요하면 DP |

## 실무에서는 이렇게 쓰입니다

- 작업 스케줄링 (CPU/GPU 작업 큐)
- 네트워크 라우팅의 빠른 휴리스틱
- 데이터 압축 (Huffman, LZ77 변형)
- 광고 입찰 시스템의 즉시 결정
- 게임 AI의 즉각적 행동 선택

## 체크리스트

- [ ] 그리디 선택 속성과 최적 부분 구조를 점검할 수 있는가
- [ ] 교환 논증을 한 문장으로 표현할 수 있는가
- [ ] 정렬 키가 정당성에 미치는 영향을 안다
- [ ] 그리디로 보이는 DP 문제를 구별할 수 있는가
- [ ] 우선순위 큐를 자유롭게 사용하는가

## 정리 및 다음 단계

그리디 알고리즘은 단순함과 속도의 알고리즘이지만, 정당성에 대한 책임이 더 무겁습니다. 그리디 선택 속성과 최적 부분 구조를 교환 논증으로 확인하는 습관을 들이면 잘못된 적용을 줄일 수 있습니다.

다음 글에서는 그래프 알고리즘을 살펴봅니다. BFS와 DFS의 차이, Dijkstra의 최단 경로, MST(최소 신장 트리)까지 다룹니다. 그래프는 그리디와 DP의 사고가 가장 풍부하게 만나는 영역입니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법](./06-dynamic-programming.md)
- **그리디 알고리즘 (현재 글)**
- 그래프 알고리즘 (예정)
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [CLRS — Introduction to Algorithms, Chapter 16](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Wikipedia — Greedy algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Competitive Programmer's Handbook — Chapter 6](https://cses.fi/book/book.pdf)

Tags: Computer Science, 알고리즘, 그리디, 교환 논증, 최적화, 활동 선택
