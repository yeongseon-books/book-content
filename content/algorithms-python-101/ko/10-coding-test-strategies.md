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

## 먼저 던지는 질문

- 입력 크기 제약을 보고 어떤 알고리즘을 먼저 버려야 할까요?
- 문제 유형을 알고리즘에 어떻게 연결할까요?
- 한 문제를 이해, 계획, 구현, 검증으로 어떻게 끝까지 끌고 갈까요?

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

## 적용 전후 비교
문제 접근 방식의 차이를 비교해 보겠습니다.

```python
# before: 바로 코딩 시작 — 잘못된 알고리즘 선택 위험
def solve(data):
    # 생각 없이 중첩 루프부터 작성하면 → 시간 초과
    for i in range(len(data)):
        for j in range(len(data)):
            pass  # O(N²) — exceeds time limit when N is 1,000,000
```

```python
# after: 먼저 입력 크기를 분석한 뒤 알고리즘 선택
def solve(data):
    # N=1,000,000 → O(N) 또는 O(N log N) 필요
    # sorting + two pointers 접근
    data.sort()  # O(N log N)
    left, right = 0, len(data) - 1
    # ... O(N) scan 수행
```

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

만약 샘플조차 틀리면 먼저 정렬된 값만 보고 원본 인덱스를 잃어버리지 않았는지 확인하면 됩니다.

### 단계 5: 검증 루프로 엣지 케이스까지 닫습니다

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

## 심화 실전 노트: 실전 풀이를 재현 가능한 루프로 만들기

### 구현 앵커: 문제 템플릿 자동 점검

```python
def analyze_constraints(n_max: int, time_limit_sec: int = 1) -> str:
    # 매우 거친 가이드라인
    if n_max <= 20:
        return "O(2^n)까지 검토 가능"
    if n_max <= 5_000:
        return "O(n^2) 가능, O(n^3) 주의"
    if n_max <= 200_000:
        return "O(n log n) 이하 권장"
    return "O(n) 중심으로 설계"

print(analyze_constraints(200_000))
```

문제를 읽자마자 복잡도 상한을 문장으로 적어 두면, 구현 중에 잘못된 방향으로 새지 않습니다.

### 인터뷰형 분해 카드

| 단계 | 30초 안에 할 질문 | 산출물 |
|------|-------------------|--------|
| 입력 분석 | `N` 최대값은? | 허용 복잡도 |
| 유형 분류 | 정렬/그래프/DP/그리디 중 무엇인가 | 후보 알고리즘 2개 |
| 설계 | 상태/포인터/자료구조는? | 의사코드 |
| 검증 | 최소 반례 5개는? | 테스트 목록 |

### 실행 추적: 투 포인터 디버깅 로그

```text
sorted values: [1,2,7,9,11], target=10
left=0,right=4,sum=12 -> right--
left=0,right=3,sum=10 -> found
```

포인터 문제는 상태 로그 두세 줄만으로 버그 위치를 즉시 좁힐 수 있습니다.

### 복잡도 선택표: 자주 틀리는 경계

| 제약 | 흔한 오판 | 안전한 기본값 |
|------|-----------|---------------|
| `N=100,000` | 이중 루프 시도 | 정렬+선형, 해시 |
| `N=1,000,000` | `O(n log n)` 남발 | 단일 순회 우선 검토 |
| 그래프 `V=10^5,E=2*10^5` | 인접행렬 사용 | 인접리스트 + BFS/DFS |

### 검증 루프 확장: 실패 원인 분류

```python
def classify_failure(name: str, expected, actual) -> str:
    if expected is None and actual is not None:
        return f"{name}: 종료 조건 점검"
    if expected is not None and actual is None:
        return f"{name}: 탐색 범위 누락 점검"
    if expected != actual:
        return f"{name}: 인덱스/정렬 기준 점검"
    return f"{name}: pass"
```

정답/오답만 보면 개선이 느립니다. 어떤 종류의 실패인지 라벨링하면 복구 속도가 빨라집니다.

### 시간 복잡도 증명 습관

풀이를 제출하기 전, 다음 한 문장을 반드시 적는 습관이 좋습니다.

- "정렬 `O(n log n)` 후 포인터 선형 스캔 `O(n)`이므로 총 `O(n log n)`입니다."
- "해시 삽입/조회가 평균 `O(1)`이므로 전체 `O(n)`입니다."
- "그래프 탐색은 각 정점/간선을 한 번씩만 보므로 `O(V+E)`입니다."

### 실수-수정 페어

| 실수 | 증상 | 수정 |
|------|------|------|
| 템플릿 없이 즉시 코딩 | 방향성 상실 | 제약-분류-설계-검증 카드 고정 |
| 경계 테스트 생략 | 제출 후 오답 | 최소/중복/음수/해답없음 케이스 추가 |
| 라이브러리 사용법 불안 | 구현 지연 | `heapq`, `bisect`, `deque` 기본 패턴 암기 |

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

## 처음 질문으로 돌아가기

- **입력 크기 제약을 보고 어떤 알고리즘을 먼저 버려야 할까요?**
  - 먼저 최대 입력 크기와 시간 제한을 보고 허용 가능한 복잡도를 역산한 뒤, 그보다 느린 접근을 바로 탈락시켜야 합니다. 이 글의 `N = 200,000` 예시에서는 `wrong_two_sum()` 같은 `O(N^2)` 이중 반복을 구현 전에 버리는 판단이 핵심이었습니다.
- **문제 유형을 알고리즘에 어떻게 연결할까요?**
  - 배열인지, 그래프인지, 상태를 저장해야 하는지, 정렬 후 양끝에서 좁힐 수 있는지를 질문하면 유형을 빠르게 연결할 수 있습니다. 본문은 Two Sum을 정렬 + 투 포인터 문제로 분류하고, `(값, 원래 인덱스)` 쌍을 정렬해 `solve_two_sum()`으로 이어 가는 흐름을 예로 들었습니다.
- **한 문제를 이해, 계획, 구현, 검증으로 어떻게 끝까지 끌고 갈까요?**
  - 이해 단계에서는 제약과 목표를 읽고, 계획 단계에서는 목표 복잡도와 자료구조를 정한 뒤, 구현 후에는 샘플·해답 없음·중복·음수·최소 입력 순으로 검증 루프를 닫아야 합니다. `verification_cases`와 `defaultdict`, `Counter`, `heapq` 예시는 문제 풀이를 한 번의 감이 아니라 재현 가능한 절차로 만드는 도구였습니다.

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
