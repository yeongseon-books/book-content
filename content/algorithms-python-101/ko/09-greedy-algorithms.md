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

## 먼저 던지는 질문

- 그리디 알고리즘이 최적해를 만드는 조건은 무엇일까요?
- 동전 거스름돈, 활동 선택, 분할 가능한 배낭 문제는 어떻게 풀까요?
- 그리디는 동적 계획법과 어떤 차이가 있을까요?

## 왜 중요한가

그리디 알고리즘은 짧고 빠릅니다. 많은 문제가 정렬 한 번과 단일 순회 한 번으로 `O(n log n)`에 해결됩니다. 흔한 `O(n^2)` DP보다 훨씬 효율적일 수 있습니다.

> 그리디는 매 단계에서 지역적으로 최선인 선택을 하고, 그것이 전체 최적해로 이어지기를 기대하는 전략입니다.

하지만 그리디가 항상 최적해를 보장하지는 않습니다. 그리디 선택 속성과 최적 부분 구조가 모두 성립해야 합니다.

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

## Before / After

겹치지 않는 활동을 최대한 많이 고르는 두 가지 접근입니다.

```python
# before: brute-force all combinations — O(2^n)
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
# after: greedy — O(n log n)
def max_activities(activities):
    activities.sort(key=lambda x: x[1])  # sort by end time
    count, last_end = 0, 0
    for start, end in activities:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

## 단계별 실습

### Step 1: Coin Change (Greedy)

```python
def coin_change_greedy(amount: int, coins: list[int] | None = None) -> dict[int, int]:
    """Greedy coin change — use the largest coins first."""
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

표준 화폐 체계처럼 큰 단위가 작은 단위를 잘 포함하는 경우에는 그리디가 깔끔하게 통합니다. 하지만 이 성공을 일반화하면 위험합니다.

### Step 2: Activity Selection

```python
def activity_selection(
    activities: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Select the maximum number of non-overlapping activities — O(n log n)."""
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

활동 선택 문제에서는 빨리 끝나는 활동을 먼저 고르는 기준이 핵심입니다. 정렬 기준 하나가 그리디의 정당성을 결정합니다.

### Step 3: Fractional Knapsack

```python
def fractional_knapsack(
    items: list[tuple[int, int]], capacity: int
) -> float:
    """Fractional knapsack — O(n log n)."""
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

분할 가능한 배낭은 가치 대비 무게 비율이 높은 것부터 고르면 됩니다. 물건을 쪼갤 수 있다는 조건이 그리디를 가능하게 합니다.

### 단계 4: 회의실 배정과 구간 스케줄링

```python
def min_meeting_rooms(meetings: list[tuple[int, int]]) -> int:
    """Minimum meeting rooms required — O(n log n)."""
    events: list[tuple[int, int]] = []
    for start, end in meetings:
        events.append((start, 1))
        events.append((end, -1))

    events.sort()
    max_rooms = 0
    current = 0
    for _, delta in events:
        current += delta
        max_rooms = max(max_rooms, current)

    return max_rooms

meetings = [(0, 30), (5, 10), (15, 20)]
print(f"Minimum rooms: {min_meeting_rooms(meetings)}")  # 2
```

구간 문제는 정렬 후 한 번 훑는 패턴으로 풀리는 경우가 많습니다. 그리디가 자주 등장하는 이유도 여기에 있습니다.

### Step 5: Greedy vs DP

```python
# Greedy fails with non-standard coin denominations
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
print(f"Greedy: {coin_change_greedy_count(coins, amount)} coins")  # 3 (4+1+1)
print(f"DP:     {coin_change_dp(coins, amount)} coins")            # 2 (3+3)
```

이 반례가 아주 중요합니다. 그리디가 간결하다는 이유만으로 정답이라고 가정하면 특정 입력에서 바로 틀릴 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 그리디는 정렬 기준에 크게 의존합니다. 무엇으로 정렬하느냐가 답의 정당성을 좌우합니다.
- 활동 선택은 종료 시간이 빠른 순서라는 기준 덕분에 최적입니다.
- 분할 가능한 배낭은 가치/무게 비율 정렬이 통하지만, 0-1 배낭은 그렇지 않습니다.
- 비표준 동전 예제는 반례 검증이 왜 필요한지 보여 줍니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 그리디의 정당성을 확인하지 않음 | 최적이 아닌 답을 낼 수 있습니다 | 반례를 찾거나 그리디 선택 속성을 증명합니다 |
| 정렬 기준을 잘못 잡음 | 잘못된 순서로 선택합니다 | 정렬 키가 최적 전략과 맞는지 검증합니다 |
| 0-1 배낭에 그리디 적용 | 물건을 쪼갤 수 없어 최적이 아닙니다 | 0-1 배낭은 DP를 사용합니다 |
| 모든 거스름돈 문제를 그리디로 풂 | 비표준 화폐 체계에서 실패합니다 | 화폐 체계 조건을 확인합니다 |
| DP가 필요한 문제에 그리디 강행 | 지역 최적이 전체 최적이 아닐 수 있습니다 | 그리디 선택 속성을 먼저 확인합니다 |

## 실무에서는 이렇게 연결됩니다

- 허프만 코딩은 그리디로 최적 압축 트리를 만듭니다.
- 작업 스케줄링은 마감 시간과 이익 기준 선택으로 이어집니다.
- 최소 신장 트리의 Kruskal, Prim도 그리디 전략입니다.
- 캐시 교체 정책은 그리디 휴리스틱에 기반한 경우가 많습니다.
- API rate limit 최적화도 요청을 묶는 그리디 전략으로 이어질 수 있습니다.

## 현업에서는 이렇게 생각합니다

그리디는 "일단 해 보고 맞나 보자" 식의 알고리즘이 아닙니다. 정당성을 확인하지 않으면 대부분 맞다가 특정 엣지 케이스에서 실패하는 코드를 만들게 됩니다.

코딩 테스트에서 그리디 풀이를 제안한다면, 왜 이 선택이 최적인지 한 문장으로 설명할 수 있어야 합니다. 그 설명이 없다면 DP를 먼저 의심하는 편이 안전합니다.

## 그리디를 실전에 쓰기 전 검증 순서

- 먼저 정렬 기준이나 선택 규칙을 한 문장으로 적어 보고, 그 규칙이 남은 문제를 망치지 않는 이유를 설명해야 합니다.
- 다음으로 작은 반례를 직접 만들어 보는 편이 좋습니다. 표준 입력 몇 개만 통과했다고 규칙이 증명되는 것은 아닙니다.
- 운영 시스템에서는 최적성뿐 아니라 구현 복잡도와 재계산 비용도 같이 봐야 합니다. 약간 덜 최적이더라도 단순한 그리디가 더 유지보수하기 쉬울 수 있습니다.
- 그리디가 자꾸 예외 케이스에 막히면 규칙을 덧대기보다, 문제 자체가 DP나 그래프 최적화인지 다시 분류하는 편이 빠릅니다.

## 체크리스트

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

## 심화 실전 노트: 그리디의 정당성을 반례로 검증하기

### 구현 앵커: 그리디 해와 완전탐색 해 자동 비교

```python
from itertools import combinations


def greedy_interval_count(intervals: list[tuple[int, int]]) -> int:
    intervals = sorted(intervals, key=lambda x: x[1])
    count, end = 0, -10**18
    for s, e in intervals:
        if s >= end:
            count += 1
            end = e
    return count


def brute_interval_count(intervals: list[tuple[int, int]]) -> int:
    best = 0
    n = len(intervals)
    for r in range(1, n + 1):
        for comb in combinations(intervals, r):
            ordered = sorted(comb)
            ok = all(ordered[i][1] <= ordered[i + 1][0] for i in range(len(ordered) - 1))
            if ok:
                best = max(best, r)
    return best
```

작은 입력에서 그리디 해와 완전탐색 해를 비교하면 정당성을 빠르게 점검할 수 있습니다.

### 추적: 활동 선택의 선택 순간

```text
종료시간 정렬: (1,4),(3,5),(0,6),(5,7),(8,11),(12,16)
선택: (1,4)
(3,5) 충돌 -> skip
(0,6) 충돌 -> skip
(5,7) 선택
(8,11) 선택
(12,16) 선택
```

### 비교표: 그리디 성공/실패 패턴

| 문제 | 그리디 성공 여부 | 이유 |
|------|------------------|------|
| 활동 선택 | 성공 | 빠른 종료 선택이 이후 선택 공간 최대화 |
| 분할 가능한 배낭 | 성공 | 비율 선택이 전체 최적과 일치 |
| 0-1 배낭 | 실패 가능 | 부분 분할 불가, 지역 최적이 전역 최적 보장 못함 |
| 비표준 동전 거스름돈 | 실패 가능 | 화폐 체계 구조 조건 불충분 |

### 인터뷰형 분해 질문

- 선택 규칙을 한 문장으로 말할 수 있는가
- 그 규칙이 이후 선택 가능성을 줄이지 않는가
- 작은 반례를 즉석에서 만들 수 있는가
- 규칙이 실패하면 대안(DP/그래프)이 무엇인가

### 증명 스케치: 활동 선택

최적해 중 가장 먼저 끝나는 활동을 포함하지 않는 해가 있다고 가정합니다. 그 해의 첫 활동을 가장 먼저 끝나는 활동으로 교체해도 이후 가능한 활동 집합은 줄어들지 않습니다. 따라서 가장 먼저 끝나는 활동을 선택하는 그리디 선택은 최적해로 확장 가능합니다.

### 실수-수정 페어

| 실수 | 결과 | 수정 |
|------|------|------|
| 정렬 기준을 시작 시간으로 둠 | 선택 수 감소 | 종료 시간 기준 정렬 |
| 반례 확인 없이 제출 | 특정 입력 오답 | 작은 입력 완전탐색 대조 |
| 문제를 그리디로 고정 | 예외 대응 실패 | 정당성 안 나오면 DP 전환 |

## 실전 검증 부록: 성능 측정과 반례 설계

알고리즘 학습에서 구현 자체보다 오래 남는 자산은 검증 습관입니다. 아래 체크는 주제와 무관하게 거의 모든 문제에서 공통으로 적용됩니다.

### 1) 마이크로 벤치마크 규칙

```python
import time


def benchmark(func, *args, repeat: int = 5) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best
```

- 단일 실행 시간은 노이즈가 큽니다.
- 최소/중앙값 기준으로 비교하는 편이 안정적입니다.
- 입력 크기를 여러 단계로 늘려 증가 추세를 기록해야 합니다.

### 2) 반례 세트 템플릿

```text
A. 최소 입력: 빈 배열, 원소 1개
B. 중복 입력: 같은 값 다수
C. 정렬/역정렬 입력: 경계 인덱스 오류 탐지
D. 음수/0 포함 입력: 비교식 방향 오류 탐지
E. 해답 없음 케이스: 종료 조건 검증
```

테스트를 통과했는지보다, 어떤 종류의 실패를 막았는지 기록하는 편이 품질에 더 직접적입니다.

### 3) 복잡도-메모리 트레이드오프 표

| 개선 전략 | 시간 영향 | 공간 영향 | 적용 판단 |
|-----------|-----------|-----------|-----------|
| 캐시/메모이제이션 | 감소 | 증가 | 중복 계산이 명확할 때 |
| 정렬 후 탐색 | 대체로 감소 | 동일/약간 증가 | 질의가 여러 번일 때 |
| 해시 사용 | 평균 감소 | 증가 | 순서보다 조회가 중요할 때 |
| 힙 사용 | 상위/최소 유지에 유리 | 증가 | 우선순위 선택이 핵심일 때 |

### 4) 인터뷰 답변 스크립트

- "먼저 입력 제약을 보고 가능한 복잡도 상한을 정하겠습니다."
- "현재 접근의 시간/공간 복잡도를 계산해 보겠습니다."
- "경계 입력 다섯 가지로 검증 계획을 먼저 제시하겠습니다."
- "필요하면 정답 유지 조건을 짧게 증명하겠습니다."

이 스크립트를 반복하면 설명의 밀도가 올라가고, 구현 중 길을 잃는 빈도가 줄어듭니다.

## 케이스 스터디 확장: 입력 규모가 커질 때의 판단

### 시나리오 1: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 2: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 3: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 4: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 5: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

## 처음 질문으로 돌아가기

- **그리디 알고리즘이 최적해를 만드는 조건은 무엇일까요?**
  - 본문의 기준은 그리디 알고리즘를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **동전 거스름돈, 활동 선택, 분할 가능한 배낭 문제는 어떻게 풀까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **그리디는 동적 계획법과 어떤 차이가 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
- **그리디 알고리즘 (현재 글)**
- 코딩 테스트 문제 접근법 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Greedy Algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [GeeksforGeeks — Greedy Algorithms](https://www.geeksforgeeks.org/greedy-algorithms/)
- [Real Python — Greedy Algorithms in Python](https://realpython.com/python-greedy-algorithm/)
- [LeetCode — Greedy Problems](https://leetcode.com/tag/greedy/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/09-greedy-algorithms)

Tags: Python, Algorithms, Greedy, Optimization, Activity Selection
