---
series: algorithms-101
episode: 7
title: "Algorithms 101 (7/10): 그리디 알고리즘"
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
  - 알고리즘
  - 그리디
  - 교환 논증
  - 최적화
  - 활동 선택
seo_description: 그리디 알고리즘이 옳을 때의 조건, 교환 논증, 대표 문제, 그리고 DP가 필요한 함정을 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (7/10): 그리디 알고리즘

지금 당장 가장 좋아 보이는 선택을 계속 고르면 정말 전체 최적해에 도달할까요? 그리고 어떤 문제에서는 왜 그 방식이 조용히 실패할까요? 이 글은 Algorithms 101 시리즈의 일곱 번째 글입니다. 여기서는 그리디가 통하는 조건, 정당화 방법, 그리고 DP로 돌아서야 하는 경계선을 다룹니다.

## 먼저 던지는 질문

- 그리디 알고리즘이 옳으려면 어떤 두 조건이 필요할까요?
- 교환 논증은 그리디 선택을 어떻게 정당화할까요?
- 활동 선택, 거스름돈, Huffman coding은 무엇을 보여 줄까요?

## 큰 그림

![Algorithms 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/07/07-01-big-picture.ko.png)

*Algorithms 101 7장 흐름 개요*

이 그림에서는 그리디 알고리즘를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 그리디 알고리즘의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

그리디 알고리즘은 가장 단순하고 빠른 부류에 속합니다. 적용만 된다면 구현과 운영이 모두 쉽고, 시간 복잡도도 O(n log n) 이하인 경우가 많습니다. 다만 정당화 없이 쓰면 틀린 답을 배포하고도 눈치채지 못할 수 있습니다. 그리디를 잘 다룬다는 것은 "언제 되는지"를 정확히 안다는 뜻입니다.

> 그리디는 단순함의 알고리즘이지만, 정확성에 대한 부담은 더 큽니다.

## 한눈에 보는 개념

> 그리디 선택 속성은 "국소적으로 고른 선택을 포함하는 최적해가 존재한다"는 뜻입니다. 최적 부분 구조는 "그 선택 이후의 남은 문제도 같은 규칙으로 최적으로 풀린다"는 뜻입니다. 두 조건이 모두 있어야 그리디가 성립합니다. 이를 증명하는 대표 도구가 교환 논증입니다.

```text
Conditions for greedy to be correct
    1) Greedy-choice property : an optimal solution containing the greedy first choice exists
    2) Optimal substructure   : the remaining subproblem is also solved greedily

Exchange argument
    Take any optimal OPT, swap its first choice for the greedy choice;
    show the result is still optimal.
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 그리디 선택 | 매 단계에서 가장 좋아 보이는 국소 선택 |
| 그리디 선택 속성 | 그 선택을 포함하는 최적해가 존재하는 성질 |
| 최적 부분 구조 | 남은 부분 문제도 같은 방식으로 최적으로 풀리는 성질 |
| 교환 논증 | 최적해의 선택을 그리디 선택으로 바꿔도 최적성을 유지함을 보이는 논증 |
| Huffman 코드 | 빈도 기반 무손실 압축의 대표 그리디 예제 |

## Before / After

**Before — 동전 거스름돈에 잘못 적용한 그리디:**

```python
# Make change for 6 with coins [1, 3, 4]
def greedy_change(coins, amount):
    coins = sorted(coins, reverse=True)
    n = 0
    for c in coins:
        n += amount // c
        amount %= c
    return n

print(greedy_change([1, 3, 4], 6))   # 3 (4+1+1) — optimum is 2 (3+3)
```

**After — 그리디가 실패하면 DP로 전환:**

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

## 단계별로 따라가기

### 1단계: 활동 선택 — 가장 빨리 끝나는 것부터

```python
def activity_selection(intervals):
    """[(start, end), ...] -> the largest set of non-overlapping intervals"""
    intervals = sorted(intervals, key=lambda x: x[1])
    chosen, last_end = 0, -1
    for s, e in intervals:
        if s >= last_end:
            chosen += 1
            last_end = e
    return chosen

print(activity_selection([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]))   # 4
```

가장 빨리 끝나는 활동을 고르는 선택은 최적입니다. 교환 논증은 왜 그런지 형식적으로 설명해 줍니다.

### 2단계: 회의실 배정 — 시작 시간이 아니라 종료 시간 정렬

```python
meetings = [(1, 5), (2, 3), (3, 4), (4, 6), (6, 8)]
print(activity_selection(meetings))   # 3 — e.g. (2,3), (3,4), (4,6)
```

같은 알고리즘이 회의실 예약과 수업 배치 문제에도 그대로 적용됩니다. 정확성을 좌우하는 것은 정렬 키 한 줄입니다.

### 3단계: 거스름돈 — 그리디가 실제로 통할 때

```python
def coin_change_greedy(coins, amount):
    coins = sorted(coins, reverse=True)
    used = []
    for c in coins:
        while amount >= c:
            amount -= c
            used.append(c)
    return used if amount == 0 else None

# Korean and US coin systems are canonical, so greedy is optimal
print(coin_change_greedy([500, 100, 50, 10], 1260))
```

동전 시스템이 canonical하면 그리디가 최적입니다. 임의의 동전 집합에는 그런 보장이 없으므로 DP가 더 안전합니다.

### 4단계: Huffman code — 우선순위 큐 위의 그리디

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

가장 빈도가 낮은 두 노드를 반복해서 합치면 최적 prefix code가 만들어집니다. 우선순위 큐가 그리디의 핵심 도구로 쓰이는 대표 사례입니다.

### 5단계: Fractional knapsack — 분할 가능성과 0/1의 차이

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

분수 knapsack은 그리디로 최적이지만 0/1 knapsack은 그렇지 않습니다. 물건을 쪼갤 수 있는지가 적용 가능성을 갈라 놓습니다.

## 이 글에서 먼저 가져갈 점

- 정렬 키 하나가 정확성 논증 대부분을 차지하는 경우가 많습니다.
- 분할 가능성은 fractional과 0/1 문제를 가르는 결정적 기준입니다.
- 우선순위 큐는 그리디 알고리즘의 대표 작업 도구입니다.
- 직관만 믿지 말고 교환 논증으로 확인해야 합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정당화 없이 그리디 사용 | 미묘하게 틀린 답 | 교환 논증으로 먼저 검증합니다 |
| 사실은 DP인데 그리디로 밀어붙임 | 오답 | 작은 반례를 직접 만들어 봅니다 |
| 잘못된 정렬 키 선택 | 거의 맞지만 틀림 | 시작 시각, 종료 시각, 비율 등 후보를 비교합니다 |
| 우선순위 큐 없이 구현 | O(n²) | heap으로 O(n log n)을 확보합니다 |
| 부분 해를 되돌리려 함 | 그리디 원칙 자체 위반 | 되돌림이 필요하면 DP나 탐색으로 전환합니다 |

## 실무에서는 이렇게 쓰입니다

- CPU/GPU 작업 큐 스케줄링
- 네트워크 라우팅의 빠른 휴리스틱
- Huffman, LZ 계열의 데이터 압축
- 광고 입찰 시스템의 즉시 의사결정
- 게임 AI의 실시간 행동 선택

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 알고리즘을 쓰기 전에 "왜 이 선택이 맞는가"를 한 문장으로 먼저 적습니다. 깔끔한 교환 논증이 떠오르지 않으면 DP 가능성을 의심합니다. 또한 손으로 그린 작은 반례를 적극적으로 만들어 보는 편이 가장 빠른 정확성 점검이라는 것도 잘 압니다.

또한 그리디가 유효한 입력 조건을 문서에 남깁니다. 예를 들어 "이 코드는 coin system이 canonical일 때만 맞다"는 문장 하나가, 미래의 잘못된 재사용을 막아 줍니다.

## 체크리스트

- [ ] 그리디 선택 속성과 최적 부분 구조를 점검할 수 있는가
- [ ] 교환 논증을 한 문장으로 설명할 수 있는가
- [ ] 정렬 키가 정확성을 좌우한다는 감각이 있는가
- [ ] 그리디처럼 보이는 DP 문제를 구별할 수 있는가
- [ ] 우선순위 큐 사용이 익숙한가

## 연습 문제

1. 하나의 회의실에서 가능한 한 많은 회의를 배정해 보세요. 그다음 종료 시간이 아니라 시작 시간으로 정렬하면 왜 깨지는지 반례를 만들어 보세요.

2. 양의 가중치를 가진 작업들의 평균 완료 시간을 최소화하는 스케줄을 그리디로 설계하고, 교환 논증으로 정당화해 보세요.

3. 동전 `[1, 5, 6, 9]`와 목표값 11에 대해 그리디 답과 DP 답을 각각 출력해 보고, 왜 달라지는지 설명해 보세요.

## 정리 및 다음 단계

그리디는 단순함과 속도의 알고리즘이지만, 그만큼 정확성에 대한 부담이 더 큽니다. 그리디 선택 속성과 최적 부분 구조를 교환 논증으로 확인하는 습관이 있어야, 빠르지만 틀린 해법을 피할 수 있습니다.

다음 글에서는 그래프 알고리즘을 다룹니다. BFS와 DFS의 차이, 다익스트라 최단 경로, 최소 신장 트리까지 보면서 그래프가 왜 시스템 사고의 공용 언어인지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **그리디 알고리즘이 옳으려면 어떤 두 조건이 필요할까요?**
  - 본문의 기준은 그리디 알고리즘를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **교환 논증은 그리디 선택을 어떻게 정당화할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **활동 선택, 거스름돈, Huffman coding은 무엇을 보여 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
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
