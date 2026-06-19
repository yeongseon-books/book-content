---
series: algorithms-python-101
episode: 10
title: "Algorithms with Python 101 (10/10): 코딩 테스트 문제 접근법"
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

# Algorithms with Python 101 (10/10): 코딩 테스트 문제 접근법

이 글은 Algorithms with Python 101 시리즈의 마지막 글입니다. 알고리즘을 안다는 것과 시간 제한 안에서 적용하는 것은 다른 문제이며, 코딩 테스트의 진짜 난점은 구현 전에 제약을 빠르게 읽고 문제를 적절한 패턴에 연결하는 데 있습니다.

이번 글에서는 앞선 내용을 "제약을 먼저 읽고, 틀린 복잡도를 먼저 버린 뒤, 구현과 검증까지 이어 가는 하나의 풀이 흐름"으로 묶어 보겠습니다. 반복 가능한 접근법이 중요한 이유는 시간을 아끼고, 불필요한 실수를 줄이고, 처음 보는 문제에서도 다시 복구할 수 있게 해 주기 때문입니다.

![Algorithms with Python 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/10/10-01-big-picture.ko.png)
*Algorithms with Python 101 10장 흐름 개요*

## 이 글에서 다룰 문제

- 입력 크기 제약을 보고 어떤 알고리즘을 먼저 버려야 할까요?
- 문제 유형을 알고리즘에 어떻게 연결할까요?
- 한 문제를 이해, 계획, 구현, 검증으로 어떻게 끝까지 끌고 갈까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

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

## 문제 유형 분류표

문제를 읽자마자 유형을 분류하면 후보 알고리즘이 바로 좁혀집니다.

| 유형 키워드 | 대표 알고리즘 | 목표 복잡도 |
|-------------|---------------|-------------|
| 두 수의 합, 연속 부분 합 | 투 포인터, 슬라이딩 윈도우 | O(N) ~ O(N log N) |
| 최단 거리, 최소 비용 | BFS (가중치 없음), Dijkstra (가중치 있음) | O(V + E), O(E log V) |
| 최대/최소 부분 구조, 중복 계산 | DP (메모이제이션/타뷸레이션) | O(N²) ~ O(N·K) |
| 항상 최선을 골라도 전체 최적 | 그리디 | O(N log N) |
| 순서 탐색, 연결 여부 | BFS, DFS | O(V + E) |
| 정렬 후 조건 탐색 | 이진 탐색 | O(N log N) |
| 빈도 집계, 중복 제거 | 해시 (Counter, set, dict) | O(N) |

## 단계별 실습

### 단계 1: 제약부터 읽고, 틀린 복잡도를 먼저 버립니다

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

### 단계 2: 잘못된 접근을 먼저 기각합니다

```python
def wrong_two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
```

이 접근은 정답 자체는 구할 수 있지만, 제약과 맞지 않습니다. 따라서 여기서 중요한 것은 "이 코드는 느리다"가 아니라 "제약을 읽은 순간 이 코드를 쓰지 않기로 결정해야 한다"입니다.

### 단계 3: 문제 유형을 분류하고 목표 복잡도를 정합니다

| 질문 | 이번 문제의 답 | 의미 |
|------|----------------|------|
| 배열이 정렬되어 있는가? | 아니요 | 먼저 정렬이 필요합니다 |
| 두 값을 합쳐 목표를 맞추는가? | 예 | 투 포인터 후보입니다 |
| 모든 조합을 다 봐야 하는가? | 아니요 | 브루트포스 탈락입니다 |
| 목표 복잡도는 무엇인가? | `O(N log N)` 이하 | 정렬 + 선형 스캔이 가능합니다 |

이 문제는 DP나 그래프가 아닙니다. 상태를 누적해 최적 부분 구조를 쓰는 문제도 아니고, 정점과 간선을 탐색하는 문제도 아니기 때문입니다. 핵심 힌트는 "두 수의 합"과 "정렬 후 양끝에서 좁히기"입니다.

### 단계 4: 정렬 + 투 포인터로 구현합니다

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

## 단계별 실행 추적: 투 포인터 동작 확인

`nums = [7, 1, 11, 2, 9]`, `target = 10`으로 투 포인터가 어떻게 움직이는지 확인합니다.

```text
정렬 전 원본: [(7,0), (1,1), (11,2), (2,3), (9,4)]
정렬 후:      [(1,1), (2,3), (7,0), (9,4), (11,2)]
               ↑                              ↑
             left=0                        right=4

step 1: left=0 (값=1), right=4 (값=11)
        합 = 1 + 11 = 12 > target(10) → right--

step 2: left=0 (값=1), right=3 (값=9)
        합 = 1 + 9 = 10 == target(10) → 정답 발견
        원본 인덱스: left→1번, right→4번
        오름차순 정렬 → (1, 4) 반환

검증: nums[1]=1, nums[4]=9, 합=10 → 정답
```

포인터가 수렴하면서 정답을 찾는 과정이 명확합니다. 합이 크면 오른쪽 포인터를 줄여 합을 낮추고, 합이 작으면 왼쪽 포인터를 올려 합을 높이는 원리입니다.

### 단계 5: 검증 루프로 엣지 케이스까지 닫습니다

```python
verification_cases = [
    {
        "name": "sample",
        "nums": [7, 1, 11, 2, 9],
        "target": 10,
        "expected": (1, 4),
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

### 단계 6: 구현 속도를 올려 주는 Python 기본기

```python
import sys
from collections import Counter, defaultdict, deque
from itertools import combinations, permutations
import heapq

# 1. Fast input
input = sys.stdin.readline

# 2. defaultdict — key 자동 초기화
graph: dict[int, list[int]] = defaultdict(list)
graph[1].append(2)
graph[1].append(3)
print(dict(graph))  # {1: [2, 3]}

# 3. Counter — 빈도 계산
text = "hello world"
freq = Counter(text)
print(freq.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]

# 4. heapq — priority queue 구현
heap: list[int] = []
for x in [5, 1, 3, 7, 2]:
    heapq.heappush(heap, x)
print(heapq.heappop(heap))  # 1

# 5. Combinations와 permutations
print(list(combinations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,3)]
print(list(permutations([1, 2, 3], 2)))  # [(1,2), (1,3), (2,1), ...]

# 6. Infinity
INF = float("inf")
print(min(INF, 42))  # 42

# 7. 2D array 초기화
rows, cols = 3, 4
grid = [[0] * cols for _ in range(rows)]  # correct
# wrong = [[0] * cols] * rows  # bug: 모든 행이 같은 리스트를 참조
```

코딩 테스트에서는 알고리즘 아이디어만큼 구현 속도도 중요합니다. 표준 라이브러리 활용과 흔한 함정 회피만으로도 큰 차이가 납니다.

## 실전 코딩 테스트 문제 풀이

### 문제 1: Three Sum — 합이 0이 되는 세 수 조합

**문제:** 정수 배열 `nums`에서 합이 0이 되는 서로 다른 세 수의 조합을 모두 반환합니다. 같은 조합이 중복되지 않아야 합니다.

**입력 제약:** `N ≤ 3,000` → `O(N²)` 허용

```python
def three_sum(nums: list[int]) -> list[list[int]]:
    """합이 0인 서로 다른 세 수 조합을 모두 반환합니다.

    전략: 정렬 후 기준 원소를 고정하고 나머지 두 원소를 투 포인터로 탐색합니다.
    시간 복잡도: O(N²) — 기준 O(N) × 투 포인터 O(N)
    공간 복잡도: O(1) — 결과 리스트 제외
    """
    nums.sort()
    result: list[list[int]] = []

    for i in range(len(nums) - 2):
        # 기준 원소가 양수이면 세 수의 합이 0보다 클 수밖에 없어 조기 종료
        if nums[i] > 0:
            break
        # 중복 기준 원소 건너뜀
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                # 중복 건너뜀
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result


print(three_sum([-1, 0, 1, 2, -1, -4]))  # [[-1, -1, 2], [-1, 0, 1]]
print(three_sum([0, 0, 0]))              # [[0, 0, 0]]
print(three_sum([1, 2, 3]))              # []
```

**단계별 실행 추적:** `nums = [-1, 0, 1, 2, -1, -4]`, 정렬 후 `[-4, -1, -1, 0, 1, 2]`

```text
i=0, nums[i]=-4
  left=1(값=-1), right=5(값=2): 합 = -4-1+2 = -3 < 0 → left++
  left=2(값=-1), right=5(값=2): 합 = -4-1+2 = -3 < 0 → left++
  left=3(값=0),  right=5(값=2): 합 = -4+0+2 = -2 < 0 → left++
  left=4(값=1),  right=5(값=2): 합 = -4+1+2 = -1 < 0 → left++
  left=5 ≥ right=5: 종료

i=1, nums[i]=-1
  left=2(값=-1), right=5(값=2): 합 = -1-1+2 = 0 → 결과 추가 [-1,-1,2]
  중복 건너뜀 후 left=3, right=4
  left=3(값=0),  right=4(값=1): 합 = -1+0+1 = 0 → 결과 추가 [-1,0,1]
  left=4, right=3: left≥right 종료

i=2, nums[i]=-1 == nums[1]=-1: 중복 건너뜀

i=3, nums[i]=0 → 이후 세 수의 합 ≥ 0+1+2 > 0, break

최종 결과: [[-1,-1,2], [-1,0,1]]
```

### 문제 2: 슬라이딩 윈도우 — 길이 K인 부분 배열의 최대 합

**문제:** 정수 배열 `nums`에서 연속된 `k`개 원소의 합이 최대인 값을 반환합니다.

**입력 제약:** `N ≤ 10^5` → `O(N)` 필요

```python
def max_subarray_sum(nums: list[int], k: int) -> int:
    """연속 k개 원소의 최대 합을 반환합니다.

    전략: 슬라이딩 윈도우 — 첫 윈도우를 구한 뒤 왼쪽 원소를 빼고 오른쪽 원소를 더하며 이동
    시간 복잡도: O(N)
    공간 복잡도: O(1)
    """
    if len(nums) < k:
        return 0

    window_sum = sum(nums[:k])
    max_sum = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum


print(max_subarray_sum([2, 1, 5, 1, 3, 2], 3))  # 9 (5+1+3)
print(max_subarray_sum([2, 3, 4, 1, 5], 2))      # 7 (3+4)
print(max_subarray_sum([1], 2))                   # 0 (k > N)
```

**단계별 실행 추적:** `nums = [2, 1, 5, 1, 3, 2]`, `k = 3`

```text
초기 윈도우: [2, 1, 5] → window_sum = 8, max_sum = 8

i=3: 추가=nums[3]=1, 제거=nums[0]=2
     window_sum = 8 + 1 - 2 = 7 (윈도우=[1,5,1])
     max_sum = max(8, 7) = 8

i=4: 추가=nums[4]=3, 제거=nums[1]=1
     window_sum = 7 + 3 - 1 = 9 (윈도우=[5,1,3])
     max_sum = max(8, 9) = 9

i=5: 추가=nums[5]=2, 제거=nums[2]=5
     window_sum = 9 + 2 - 5 = 6 (윈도우=[1,3,2])
     max_sum = max(9, 6) = 9

최종 결과: 9
```

### 문제 3: 해시 활용 — 가장 긴 중복 없는 부분 문자열

**문제:** 문자열 `s`에서 같은 문자가 반복되지 않는 가장 긴 부분 문자열의 길이를 반환합니다.

**입력 제약:** `N ≤ 5 × 10^4` → `O(N)` 필요

```python
def length_of_longest_substring(s: str) -> int:
    """중복 없는 가장 긴 부분 문자열의 길이를 반환합니다.

    전략: 슬라이딩 윈도우 + 해시로 마지막 등장 위치 추적
    시간 복잡도: O(N) — 각 문자를 최대 두 번 방문
    공간 복잡도: O(문자 집합 크기) — 최대 O(128) for ASCII
    """
    last_seen: dict[str, int] = {}
    max_len = 0
    start = 0

    for end, char in enumerate(s):
        if char in last_seen and last_seen[char] >= start:
            start = last_seen[char] + 1
        last_seen[char] = end
        max_len = max(max_len, end - start + 1)

    return max_len


print(length_of_longest_substring("abcabcbb"))  # 3 ("abc")
print(length_of_longest_substring("bbbbb"))     # 1 ("b")
print(length_of_longest_substring("pwwkew"))    # 3 ("wke")
print(length_of_longest_substring(""))          # 0
```

**단계별 실행 추적:** `s = "abcabcbb"`

```text
start=0, last_seen={}, max_len=0

end=0, char='a': 미등장 → last_seen={'a':0}, max_len=max(0,1)=1
end=1, char='b': 미등장 → last_seen={'a':0,'b':1}, max_len=2
end=2, char='c': 미등장 → last_seen={..,'c':2}, max_len=3
end=3, char='a': last_seen['a']=0 ≥ start=0 → start=1
                  last_seen={'a':3,'b':1,'c':2}, max_len=max(3,3)=3
end=4, char='b': last_seen['b']=1 ≥ start=1 → start=2
                  last_seen={..,'b':4}, max_len=max(3,3)=3
end=5, char='c': last_seen['c']=2 ≥ start=2 → start=3
                  last_seen={..,'c':5}, max_len=max(3,3)=3
end=6, char='b': last_seen['b']=4 ≥ start=3 → start=5
                  last_seen={..,'b':6}, max_len=max(3,2)=3
end=7, char='b': last_seen['b']=6 ≥ start=5 → start=7
                  last_seen={..,'b':7}, max_len=max(3,1)=3

최종 결과: 3
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 입력 크기를 확인하지 않음 | 잘못된 복잡도의 알고리즘을 골라 시간 초과가 납니다 | 먼저 `N` 범위를 보고 탈락시킬 접근부터 정합니다 |
| 경계 조건을 무시함 | 빈 입력이나 `N=1`에서 런타임 오류가 납니다 | 경계 조건을 먼저 처리합니다 |
| 문제 유형 분류 없이 바로 구현 | DP, 그래프, 투 포인터 중 엉뚱한 방향으로 갑니다 | 정렬 여부, 목표 연산, 허용 복잡도를 먼저 적습니다 |
| 원본 인덱스를 잃어버림 | 값은 맞는데 정답 형식이 틀립니다 | 정렬 전에 `(값, 인덱스)` 쌍으로 묶습니다 |
| 2D 배열 초기화 버그 | `[[0]*n]*m`은 모든 행이 같은 객체를 참조합니다 | `[[0]*n for _ in range(m)]` 패턴을 사용합니다 |
| 중복 스킵 로직 누락 | Three Sum 등에서 같은 조합이 여러 번 결과에 포함됩니다 | 포인터 이동 후 같은 값이면 계속 건너뜁니다 |
| 슬라이딩 윈도우 제거 원소 위치 오류 | `nums[i-k]` 대신 `nums[i-k-1]`처럼 오프셋이 틀립니다 | 윈도우 크기 `k` 확인 후 인덱스 관계를 한 번 더 검증합니다 |

## 인터뷰형 분해 카드

문제를 받으면 30초 안에 이 4단계를 입으로 말하거나 종이에 적는 습관을 들입니다.

| 단계 | 30초 안에 할 질문 | 산출물 |
|------|-------------------|--------|
| 입력 분석 | `N` 최대값은? 값 범위는? 중복 가능한가? | 허용 복잡도 상한 |
| 유형 분류 | 정렬/그래프/DP/그리디/해시 중 무엇인가 | 후보 알고리즘 2개 |
| 설계 | 상태/포인터/자료구조는? 종료 조건은? | 의사코드 5줄 |
| 검증 | 최소 반례 5가지는? 실패 시 먼저 볼 지점은? | 테스트 목록 |

## 복잡도 선택 기준표

| 제약 | 흔한 오판 | 안전한 기본값 |
|------|-----------|---------------|
| `N ≤ 1,000` | O(N³) 남발 | O(N²)까지 신중히 |
| `N = 100,000` | 이중 루프 시도 | 정렬+선형 또는 해시 |
| `N = 1,000,000` | O(N log N) 남발 | 단일 순회 우선 검토 |
| 그래프 `V=10^5, E=2×10^5` | 인접행렬 사용 | 인접리스트 + BFS/DFS |
| 최단 경로, 가중치 있음 | BFS 오적용 | Dijkstra 또는 Bellman-Ford |

## 실무에서는 이렇게 연결됩니다

- 코딩 면접은 알고리즘 문제 해결 능력을 평가합니다.
- 성능 최적화는 종종 `O(N^2)`를 `O(N log N)`으로 낮추는 일에서 시작합니다.
- 데이터 파이프라인 설계도 입력 크기에 맞는 처리 알고리즘 선택이 중요합니다.
- API 응답 시간 최적화 역시 알고리즘 선택과 밀접합니다.
- 시스템 설계 면접에서도 복잡도 분석 능력은 기본입니다.

## 현업에서는 이렇게 생각합니다

코딩 테스트의 본질은 "올바른 알고리즘을 고르고, 시간 안에 정확히 구현하는 것"입니다. 많은 문제를 푸는 것도 중요하지만, 제약을 먼저 읽고 틀린 복잡도를 빨리 버리는 습관을 들이는 편이 더 큰 효과를 냅니다.

이 사고방식은 실무에도 그대로 이어집니다. "이 데이터 크기에서 이 알고리즘이 충분히 빠른가?"라는 질문은 시스템 설계의 기본이기 때문입니다.

## 운영 체크리스트

- [ ] 입력 크기에서 허용 시간 복잡도를 역산할 수 있습니다
- [ ] 문제를 탐색, DP, 그래프, 그리디, 해시 등으로 분류할 수 있습니다
- [ ] 투 포인터 문제에서 잘못된 `O(N^2)` 접근을 먼저 기각할 수 있습니다
- [ ] 슬라이딩 윈도우로 연속 부분 배열 문제를 `O(N)`에 풀 수 있습니다
- [ ] Python 표준 라이브러리로 빠르게 구현할 수 있습니다
- [ ] 엣지 케이스를 체계적으로 테스트하고, 실패 시 먼저 볼 지점을 정할 수 있습니다

## 정리와 마무리

- 입력 크기에서 허용 시간 복잡도를 역산하는 것이 알고리즘 선택의 출발점입니다.
- 두 포인터는 "정렬 + 양끝 축소" 문제에서 `O(N^2)`를 `O(N log N)` 또는 `O(N)`으로 줄이는 핵심 패턴입니다.
- 슬라이딩 윈도우는 연속 부분 배열 합, 중복 없는 최장 부분 문자열 문제에 적합합니다.
- 구현이 끝난 뒤에는 샘플, 해답 없음, 중복, 음수, 최소 입력 순으로 검증 루프를 돌리는 편이 안전합니다.
- `defaultdict`, `Counter`, `heapq` 같은 표준 라이브러리는 구현 시간을 크게 줄여 줍니다.
- `[[0]*n]*m` 2차원 배열 초기화 버그는 매우 흔하므로 반드시 구분해야 합니다.

코딩 테스트에서 가장 중요한 능력은 문제 유형을 빠르게 알아보고, 제약과 맞지 않는 접근을 초반에 버리는 것입니다. 입력 크기, 시간 복잡도, 알고리즘 선택, 구현, 검증으로 이어지는 흐름이 몸에 익으면 처음 보는 문제도 체계적으로 접근할 수 있습니다. 이 시리즈에서 다룬 탐색, 정렬, 재귀, DP, 그래프, 그리디는 코딩 테스트의 핵심 도구 상자이지만, 마지막 완성도는 결국 검증 루프에서 결정됩니다.

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
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/10-coding-test-strategies)

Tags: Python, Algorithms, Coding Test, Problem Solving, Interview
