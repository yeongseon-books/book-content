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

지금 당장 가장 좋아 보이는 선택을 계속 고르면 정말 전체 최적해에 도달할까요? 그리고 어떤 문제에서는 왜 그 방식이 조용히 실패할까요? 여기서는 그리디가 통하는 조건, 정당화 방법, 그리고 DP로 돌아서야 하는 경계선을 다룹니다.

이 글은 Algorithms 101 시리즈의 7번째 글입니다.

![Algorithms 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/07/07-01-big-picture.ko.png)
*Algorithms 101 7장 흐름 개요*

## 이 글에서 다룰 문제

- 그리디 알고리즘이 옳으려면 어떤 두 조건이 필요할까요?
- 교환 논증은 그리디 선택을 어떻게 정당화할까요?
- 활동 선택, 거스름돈, Huffman coding은 무엇을 보여 줄까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

그리디 알고리즘은 가장 단순하고 빠른 부류에 속합니다. 적용만 된다면 구현과 운영이 모두 쉽고, 시간 복잡도도 O(n log n) 이하인 경우가 많습니다. 다만 정당화 없이 쓰면 틀린 답을 배포하고도 눈치채지 못할 수 있습니다. 그리디를 잘 다룬다는 것은 "언제 되는지"를 정확히 안다는 뜻입니다.

> 그리디는 단순함의 알고리즘이지만, 정확성에 대한 부담은 더 큽니다.

> 그리디 선택 속성은 "국소적으로 고른 선택을 포함하는 최적해가 존재한다"는 뜻입니다. 최적 부분 구조는 "그 선택 이후의 남은 문제도 같은 규칙으로 최적으로 풀린다"는 뜻입니다. 두 조건이 모두 있어야 그리디가 성립합니다. 이를 증명하는 대표 도구가 교환 논증입니다.

```text
Conditions for greedy to be correct
    1) Greedy-choice property : an optimal solution containing the greedy first choice exists
    2) Optimal substructure   : the remaining subproblem is also solved greedily

Exchange argument
    Take any optimal solution OPT.
    Swap its first choice for the greedy choice.
    Show the modified solution is still optimal.
    Therefore, greedy is optimal.
```

| 용어 | 설명 |
| --- | --- |
| 그리디 선택 | 매 단계에서 가장 좋아 보이는 국소 선택 |
| 그리디 선택 속성 | 그 선택을 포함하는 최적해가 존재하는 성질 |
| 최적 부분 구조 | 남은 부분 문제도 같은 방식으로 최적으로 풀리는 성질 |
| 교환 논증 | 최적해의 선택을 그리디 선택으로 바꿔도 최적성을 유지함을 보이는 논증 |
| Huffman 코드 | 빈도 기반 무손실 압축의 대표 그리디 예제 |

## 개선 전 / 개선 후

**Before — 동전 거스름돈에 잘못 적용한 그리디:**

```python
def greedy_change_wrong(coins, amount):
    coins = sorted(coins, reverse=True)
    count = 0
    for c in coins:
        count += amount // c
        amount %= c
    return count

# 동전 [1, 3, 4]로 6을 만들기
print(greedy_change_wrong([1, 3, 4], 6))   # 3 (4+1+1) — 최적은 2 (3+3)
```

**After — 그리디가 실패하면 DP로 전환:**

```python
def min_coins_dp(coins, amount):
    INF = float('inf')
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

print(min_coins_dp([1, 3, 4], 6))   # 2 (3+3)
```

## 단계별로 따라가기

### 1단계: 활동 선택 — 가장 빨리 끝나는 것부터

```python
def activity_selection(intervals):
    """
    종료 시간이 가장 빠른 활동부터 선택.
    교환 논증: 어떤 최적해에서도 첫 번째로 선택된 활동을 가장 일찍 끝나는 것으로
    교체해도 최적성이 유지된다.
    """
    intervals = sorted(intervals, key=lambda x: x[1])  # 종료 시간 기준 정렬
    chosen, last_end = [], -1
    for s, e in intervals:
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen

activities = [(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]
result = activity_selection(activities)
print(f"선택된 활동 수: {len(result)}, 목록: {result}")   # 4개
```

가장 빨리 끝나는 활동을 고르는 선택은 최적입니다. 정렬 키 하나가 정확성 논증 전체를 결정합니다.

### 2단계: 시작 시간 정렬의 실패 반례

```python
# 시작 시간으로 정렬하면 왜 깨질까?
def activity_selection_wrong(intervals):
    intervals = sorted(intervals, key=lambda x: x[0])  # 시작 시간 기준 (잘못)
    chosen, last_end = [], -1
    for s, e in intervals:
        if s >= last_end:
            chosen.append((s, e))
            last_end = e
    return chosen

activities = [(0, 10), (1, 2), (3, 4)]  # 최적: (1,2), (3,4) = 2개
wrong = activity_selection_wrong(activities)
correct = activity_selection(activities)
print(f"잘못된 방법: {len(wrong)}개 — {wrong}")   # 1개 (0,10 하나만)
print(f"올바른 방법: {len(correct)}개 — {correct}")  # 2개
```

### 3단계: 거스름돈 — 그리디가 실제로 통할 때

```python
def coin_change_greedy(coins, amount):
    """표준 코인 시스템(canonical)에서만 최적."""
    coins = sorted(coins, reverse=True)
    used = []
    for c in coins:
        while amount >= c:
            amount -= c
            used.append(c)
    return used if amount == 0 else None

# 표준 코인에서는 그리디가 최적
print(coin_change_greedy([500, 100, 50, 10], 1260))
# 비표준 코인에서는 실패
print("그리디:", coin_change_greedy([1, 3, 4], 6))   # [4, 1, 1] = 3개
print("DP 최적:", min_coins_dp([1, 3, 4], 6))        # 2개
```

동전 시스템이 canonical하면 그리디가 최적입니다. 임의의 동전 집합에는 그런 보장이 없으므로 DP가 더 안전합니다.

### 4단계: Huffman code — 우선순위 큐 위의 그리디

```python
import heapq

def huffman(freq):
    """
    빈도 기반 최적 prefix code.
    그리디 선택: 가장 빈도가 낮은 두 노드를 반복해서 합침.
    """
    h = [[w, [c, ""]] for c, w in freq.items()]
    heapq.heapify(h)
    while len(h) > 1:
        a = heapq.heappop(h)   # 가장 낮은 빈도
        b = heapq.heappop(h)   # 두 번째로 낮은 빈도
        for item in a[1:]:
            item[1] = '0' + item[1]
        for item in b[1:]:
            item[1] = '1' + item[1]
        heapq.heappush(h, [a[0] + b[0]] + a[1:] + b[1:])
    return sorted(h[0][1:], key=lambda x: len(x[1]))

freq = {"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45}
codes = huffman(freq)
for char, code in codes:
    print(f"  '{char}': {code} (빈도 {freq[char]})")
```

### 5단계: Fractional knapsack — 분할 가능성과 0/1의 차이

```python
def fractional_knapsack(weights, values, W):
    """
    단위 무게당 가치가 높은 것부터 선택. 분할 가능하므로 그리디 최적.
    0/1 knapsack에서는 이 방법이 실패함 — 분할 불가.
    """
    items = sorted(zip(weights, values), key=lambda x: -x[1] / x[0])
    total = 0.0
    for w, v in items:
        if W >= w:
            W -= w
            total += v
        else:
            total += v * (W / w)   # 분할
            break
    return total

print(fractional_knapsack([10, 20, 30], [60, 100, 120], 50))   # 240.0
```

분수 knapsack은 그리디로 최적이지만 0/1 knapsack은 그렇지 않습니다. 물건을 쪼갤 수 있는지가 적용 가능성을 가릅니다.

### 6단계: 그리디 vs DP 판별 연습

```python
# 반례를 만드는 방법
def verify_greedy(greedy_fn, dp_fn, coins_list, amounts):
    """그리디와 DP 결과를 비교해 반례를 탐색."""
    for coins in coins_list:
        for amount in amounts:
            g = greedy_fn(coins, amount)
            d = dp_fn(coins, amount)
            g_count = len(g) if g else float('inf')
            if g_count != d:
                print(f"반례! coins={coins}, amount={amount}: "
                      f"greedy={g_count}, dp={d}")
                return
    print("테스트 범위에서 차이 없음")

# 표준 코인
def greedy_count(coins, amount):
    result = coin_change_greedy(coins, amount)
    return len(result) if result else float('inf')

verify_greedy(greedy_count, min_coins_dp,
              [[1, 3, 4]], range(1, 20))   # 반례 발견
```

## 그리디 vs DP 비교표

| 특성 | 그리디 | 동적 계획법 |
| --- | --- | --- |
| 결정 방식 | 현재 단계에서 최선 | 모든 부분 문제 고려 |
| 되돌림 | 없음 | 없음 (memoization) |
| 시간 복잡도 | 보통 O(n log n) 이하 | 보통 O(n²) 이상 |
| 정확성 보장 | 조건 충족 시만 | 항상 |
| 적용 신호 | 교환 논증 성립 | 중복 부분 문제 + 최적 부분 구조 |
| 활동 선택 | 최적 (종료 시간 정렬) | 적용 가능하나 불필요 |
| 거스름돈(표준) | 최적 | 적용 가능하나 오버 |
| 거스름돈(비표준) | 실패 가능 | 항상 최적 |
| 0/1 knapsack | 실패 | 최적 |
| fractional knapsack | 최적 | 적용 불필요 |

## 이 글에서 먼저 가져갈 점

- 정렬 키 하나가 정확성 논증 대부분을 차지하는 경우가 많습니다.
- 분할 가능성은 fractional과 0/1 문제를 가르는 결정적 기준입니다.
- 우선순위 큐는 그리디 알고리즘의 대표 작업 도구입니다.
- 직관만 믿지 말고 교환 논증으로 확인해야 합니다.
- 작은 반례를 직접 만드는 것이 가장 빠른 정확성 점검입니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 정당화 없이 그리디 사용 | 미묘하게 틀린 답 | 교환 논증으로 먼저 검증합니다 |
| 사실은 DP인데 그리디로 밀어붙임 | 오답 | 작은 반례를 직접 만들어 봅니다 |
| 잘못된 정렬 키 선택 | 거의 맞지만 틀림 | 시작 시각, 종료 시각, 비율 등 후보를 비교합니다 |
| 우선순위 큐 없이 구현 | O(n²) | heap으로 O(n log n)을 확보합니다 |
| 부분 해를 되돌리려 함 | 그리디 원칙 자체 위반 | 되돌림이 필요하면 DP나 탐색으로 전환합니다 |
| 입력 조건을 문서화하지 않음 | 다른 입력에서 재사용 실패 | 그리디가 유효한 전제를 주석으로 남깁니다 |

## 실무에서는 이렇게 쓰입니다

- CPU/GPU 작업 큐 스케줄링
- 네트워크 라우팅의 빠른 휴리스틱
- Huffman, LZ 계열의 데이터 압축
- 광고 입찰 시스템의 즉시 의사결정
- 게임 AI의 실시간 행동 선택

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 알고리즘을 쓰기 전에 "왜 이 선택이 맞는가"를 한 문장으로 먼저 적습니다. 깔끔한 교환 논증이 떠오르지 않으면 DP 가능성을 의심합니다. 또한 손으로 그린 작은 반례를 적극적으로 만들어 보는 편이 가장 빠른 정확성 점검이라는 것도 잘 압니다.

또한 그리디가 유효한 입력 조건을 문서에 남깁니다. 예를 들어 "이 코드는 coin system이 canonical일 때만 맞다"는 문장 하나가, 미래의 잘못된 재사용을 막아 줍니다.

## 운영 체크리스트

- [ ] 그리디 선택 속성과 최적 부분 구조를 점검할 수 있는가
- [ ] 교환 논증을 한 문장으로 설명할 수 있는가
- [ ] 정렬 키가 정확성을 좌우한다는 감각이 있는가
- [ ] 그리디처럼 보이는 DP 문제를 구별할 수 있는가
- [ ] 우선순위 큐 사용이 익숙한가
- [ ] 그리디의 유효 조건을 코드 주석으로 남기는가

## 연습 문제

1. 하나의 회의실에서 가능한 한 많은 회의를 배정해 보세요. 그다음 종료 시간이 아니라 시작 시간으로 정렬하면 왜 깨지는지 반례를 만들어 보세요.

2. 양의 가중치를 가진 작업들의 평균 완료 시간을 최소화하는 스케줄을 그리디로 설계하고, 교환 논증으로 정당화해 보세요.

3. 동전 `[1, 5, 6, 9]`와 목표값 11에 대해 그리디 답과 DP 답을 각각 출력해 보고, 왜 달라지는지 설명해 보세요.

4. Huffman 코딩으로 압축된 비트열의 평균 길이를 계산해 보세요. 고정 길이 인코딩과 비교해 얼마나 더 효율적인지도 출력하세요.

## 정리 및 다음 단계

그리디는 단순함과 속도의 알고리즘이지만, 그만큼 정확성에 대한 부담이 더 큽니다. 그리디 선택 속성과 최적 부분 구조를 교환 논증으로 확인하는 습관이 있어야, 빠르지만 틀린 해법을 피할 수 있습니다.

다음 글에서는 그래프 알고리즘을 다룹니다. BFS와 DFS의 차이, 다익스트라 최단 경로, 최소 신장 트리까지 보면서 그래프가 왜 시스템 사고의 공용 언어인지 봅니다.

## 처음 질문으로 돌아가기

- **그리디 알고리즘이 옳으려면 어떤 두 조건이 필요할까요?**
  - 첫째, 그리디 선택 속성: 국소적으로 최선인 선택을 포함하는 전체 최적해가 존재해야 합니다. 둘째, 최적 부분 구조: 그리디 선택 이후 남은 부분 문제도 같은 방식으로 최적으로 풀려야 합니다. 두 조건 중 하나라도 없으면 그리디는 오답을 낼 수 있습니다.
- **교환 논증은 그리디 선택을 어떻게 정당화할까요?**
  - "임의의 최적해 OPT에서 첫 번째 선택을 그리디 선택으로 교체해도 OPT의 최적성이 유지된다"는 것을 보입니다. 예를 들어 활동 선택에서 OPT가 종료 시간이 가장 빠른 활동 대신 다른 것을 선택했다면, 그것을 가장 빨리 끝나는 활동으로 교체해도 이후 활동 수가 줄어들지 않습니다.
- **활동 선택, 거스름돈, Huffman coding은 무엇을 보여 줄까요?**
  - 활동 선택은 "단조 기준으로 정렬 후 충돌 없으면 선택"이라는 가장 기본적인 그리디 패턴을 보여 줍니다. 거스름돈은 그리디가 통하는 조건(canonical 코인 시스템)과 실패하는 조건(비표준 코인)의 차이를 보여 줍니다. Huffman coding은 우선순위 큐를 도구로 쓰는 그리디의 전형으로, 수학적으로 최적 prefix code임이 증명됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- **Algorithms 101 (7/10): 그리디 알고리즘 (현재 글)**
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- [Algorithms 101 (9/10): 문자열 알고리즘 기초](./09-string-algorithms.md)
- [알고리즘 문제 풀이 전략](./10-problem-solving-strategies.md)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [CLRS — Introduction to Algorithms, Chapter 16](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Wikipedia — Greedy algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Competitive Programmer's Handbook — Chapter 6](https://cses.fi/book/book.pdf)

Tags: Computer Science, 알고리즘, 그리디, 교환 논증, 최적화, 활동 선택
