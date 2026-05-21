---
series: algorithms-python-101
episode: 1
title: "Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?"
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
  - Problem Solving
  - Programming Basics
  - Time Complexity
seo_description: 알고리즘의 정의와 다섯 가지 핵심 성질을 파이썬 예제로 배우고, 효율적인 문제 해결을 위한 알고리즘적 사고의 기초를 다집니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?

프로그래밍은 결국 문제를 푸는 일입니다. 같은 답을 내는 코드라도 입력이 커지면 완전히 다른 성능을 보일 수 있고, 그 차이는 대개 알고리즘에서 시작됩니다.

이 글은 Algorithms with Python 101 시리즈의 첫 번째 글입니다. 여기서는 알고리즘이 무엇인지 정의하고, 핵심 성질을 정리한 뒤, Python으로 간단한 알고리즘을 직접 구현해 보겠습니다.

알고리즘은 코딩 테스트에서만 중요한 주제가 아닙니다. 성능 최적화, 데이터 처리, 시스템에서의 트레이드오프 판단까지, 개발자가 실무에서 문제를 바라보는 방식 자체를 바꿉니다.

## 먼저 던지는 질문

- 알고리즘은 정확히 무엇이며, 어떤 성질을 가져야 할까요?
- 알고리즘을 의사코드나 Python 코드로 어떻게 표현할 수 있을까요?
- 같은 문제를 푸는 두 알고리즘은 왜 효율이 크게 달라질까요?

## 큰 그림

![Algorithms with Python 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/01/01-01-big-picture.ko.png)

*Algorithms with Python 101 1장 흐름 개요*

## 왜 중요한가

프로그래밍은 문제 해결입니다. 같은 문제라도 어떤 알고리즘을 선택하느냐에 따라 한쪽은 수천 배 더 빠를 수 있습니다. 알고리즘을 이해해야 더 빠르고, 더 정확하며, 더 예측 가능한 코드를 작성할 수 있습니다.

> 알고리즘은 입력을 받아 원하는 출력을 만드는 명확하고 유한한 단계의 집합입니다.

알고리즘적 사고는 코딩 테스트, 성능 최적화, 시스템 설계 전반의 기본기입니다.

## 개념 한눈에 보기

> 알고리즘 = 입력을 원하는 출력으로 바꾸는 유한한 절차

```text
[Problem] → [Algorithm] → [Solution]

Example: Find the maximum value in a list
Input:  [3, 7, 2, 9, 4]
Algorithm:
  1. Set the first value as the maximum
  2. Compare each remaining value
  3. Update maximum when a larger value is found
Output: 9
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Algorithm | 문제를 해결하기 위한 명확하고 유한한 단계의 집합입니다 |
| Input | 알고리즘에 주어지는 데이터입니다 |
| Output | 알고리즘이 만들어 내는 결과입니다 |
| Correctness | 모든 유효한 입력에 대해 올바른 출력을 만드는 성질입니다 |
| Efficiency | 시간과 메모리를 얼마나 아껴 쓰는지를 나타냅니다 |

## Before / After

리스트에서 최댓값을 찾는 두 가지 접근을 비교해 보겠습니다.

```python
# before: sort the list then take the last element — O(n log n)
data = [3, 7, 2, 9, 4]
sorted_data = sorted(data)
maximum = sorted_data[-1]
```

```python
# after: single pass through the list — O(n)
data = [3, 7, 2, 9, 4]
maximum = data[0]
for x in data[1:]:
    if x > maximum:
        maximum = x
```

## 단계별 실습

### Step 1: Find the Maximum Value

```python
def find_max(numbers: list[int]) -> int:
    """Find the maximum value in a list."""
    if not numbers:
        raise ValueError("Cannot find maximum of an empty list")
    maximum = numbers[0]
    for num in numbers[1:]:
        if num > maximum:
            maximum = num
    return maximum

data = [3, 7, 2, 9, 4]
print(f"Maximum: {find_max(data)}")  # Maximum: 9
```

가장 단순한 선형 순회 알고리즘입니다. 정렬 없이 한 번만 훑기 때문에, 같은 문제를 더 직접적으로 푼다는 점이 중요합니다.

### Step 2: Compute Basic Statistics

```python
def compute_stats(numbers: list[int]) -> dict:
    """Compute sum, average, min, and max of a list."""
    if not numbers:
        raise ValueError("Empty list")
    total = 0
    minimum = numbers[0]
    maximum = numbers[0]
    for num in numbers:
        total += num
        if num < minimum:
            minimum = num
        if num > maximum:
            maximum = num
    return {
        "sum": total,
        "average": total / len(numbers),
        "min": minimum,
        "max": maximum,
    }

stats = compute_stats([10, 20, 30, 40, 50])
print(stats)
# {'sum': 150, 'average': 30.0, 'min': 10, 'max': 50}
```

한 번의 반복으로 여러 값을 함께 계산할 수 있다는 점을 보여 줍니다. 알고리즘을 설계할 때는 같은 순회 안에서 무엇을 같이 처리할 수 있는지 보는 습관이 중요합니다.

### Step 3: Reverse a String

```python
def reverse_string(text: str) -> str:
    """Reverse a string without slicing."""
    result = []
    for i in range(len(text) - 1, -1, -1):
        result.append(text[i])
    return "".join(result)

print(reverse_string("algorithm"))  # mhtirogla
print(reverse_string("Python"))    # nohtyP

# Compare with Python built-in
print("algorithm"[::-1])  # mhtirogla
```

내장 기능이 있어도 직접 구현해 보면 반복, 인덱스, 종료 조건 같은 알고리즘의 기본 단위를 더 분명하게 볼 수 있습니다.

### Step 4: Compare Two Algorithms

```python
import time

def has_duplicate_brute(data: list[int]) -> bool:
    """Check for duplicates — brute force O(n^2)."""
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j]:
                return True
    return False

def has_duplicate_set(data: list[int]) -> bool:
    """Check for duplicates — set-based O(n)."""
    return len(data) != len(set(data))

test_data = list(range(10_000))

start = time.perf_counter()
has_duplicate_brute(test_data)
brute_time = time.perf_counter() - start

start = time.perf_counter()
has_duplicate_set(test_data)
set_time = time.perf_counter() - start

print(f"Brute force: {brute_time:.4f}s")
print(f"Set-based:   {set_time:.6f}s")
```

같은 문제라도 알고리즘 선택에 따라 실행 시간이 얼마나 달라지는지 직접 체감할 수 있는 예제입니다. 알고리즘 학습이 추상적인 이유가 아니라, 실제 비용 차이 때문이라는 점을 보여 줍니다.

### Step 5: Verify the Five Properties

```python
def is_palindrome(text: str) -> bool:
    """Check whether a string is a palindrome.

    Demonstrates the five properties of an algorithm:
    1. Input: string text
    2. Output: True or False
    3. Definiteness: every step is unambiguous
    4. Finiteness: the loop runs at most len(text)/2 times
    5. Effectiveness: uses only basic comparisons
    """
    cleaned = text.lower().replace(" ", "")
    left = 0
    right = len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
print(is_palindrome("A man a plan a canal Panama"))  # True
```

좋은 알고리즘은 단지 동작하는 코드가 아닙니다. 입력과 출력이 분명하고, 단계가 모호하지 않으며, 반드시 끝나고, 실제로 계산 가능한 연산으로 이루어져 있어야 합니다.

## 이 코드에서 먼저 봐야 할 점

- 같은 문제라도 알고리즘에 따라 성능 차이가 매우 크게 날 수 있습니다. `O(n^2)`와 `O(n)`의 차이는 입력이 커질수록 극단적으로 벌어집니다.
- 알고리즘은 입력, 출력, 명확성, 유한성, 효과성이라는 다섯 성질로 설명할 수 있습니다.
- `max`, `sorted` 같은 Python 내장 함수도 알고리즘입니다. 직접 구현해 보면 원리를 더 잘 이해할 수 있습니다.
- 빈 리스트나 빈 문자열 같은 경계 조건을 처리하는 태도가 좋은 알고리즘 설계의 출발점입니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 경계 조건을 건너뜀 | 빈 입력에서 바로 실패할 수 있습니다 | 입력 검증을 먼저 합니다 |
| 무한 루프를 만듦 | 종료 조건이 없거나 잘못되면 끝나지 않습니다 | 루프 변수가 종료 조건에 수렴하는지 확인합니다 |
| Off-by-one 오류 | 인덱스가 1만큼 어긋납니다 | 경계값 테스트를 꼼꼼히 합니다 |
| 비효율적인 알고리즘 선택 | 데이터가 커질수록 실행 시간이 폭증합니다 | 먼저 시간 복잡도를 따져 봅니다 |
| 정확성을 검증하지 않음 | 일부 입력에서만 우연히 맞을 수 있습니다 | 다양한 입력으로 테스트합니다 |

## 실무에서는 이렇게 연결됩니다

- 검색 엔진은 수십억 개의 페이지 중에서 결과를 빠르게 찾아야 합니다.
- 추천 시스템은 사용자 선호 데이터를 분석해 적절한 콘텐츠를 제안합니다.
- 내비게이션 앱은 실시간으로 더 좋은 경로를 계산합니다.
- 압축 알고리즘은 저장 공간을 줄이기 위해 데이터를 재배열합니다.
- 암호화 알고리즘은 전송 중이거나 저장된 데이터를 보호합니다.

## 현업에서는 이렇게 생각합니다

일상적인 개발에서 알고리즘을 처음부터 직접 구현할 일은 많지 않습니다. 대부분은 라이브러리와 프레임워크가 이미 최적화된 구현을 제공합니다. 그래도 알고리즘적 사고는 문제를 분석하고, 병목을 찾고, 더 나은 접근을 고르는 데 꼭 필요합니다.

"왜 이 코드는 느릴까?", "더 나은 방법이 있을까?"라는 질문에 답하려면 알고리즘의 기본 개념이 머릿속에 잡혀 있어야 합니다.

## 체크리스트

- [ ] 알고리즘의 정의와 다섯 가지 성질을 설명할 수 있습니다
- [ ] 같은 문제를 푸는 두 알고리즘의 효율 차이를 비교할 수 있습니다
- [ ] Python으로 간단한 알고리즘(최댓값 찾기, 회문 검사)을 구현할 수 있습니다
- [ ] 경계 조건을 처리하는 알고리즘을 작성할 수 있습니다
- [ ] 브루트포스와 최적화된 접근의 성능 차이를 측정할 수 있습니다

## 연습 문제

1. 리스트에서 두 번째로 큰 값을 한 번의 순회로 찾는 알고리즘을 작성해 보세요.
2. 문자열에서 가장 자주 등장하는 문자를 찾는 알고리즘을 작성해 보세요.
3. 1부터 N까지의 합을 구하는 세 가지 방법(반복문, 수학 공식, 재귀)을 구현하고 성능을 비교해 보세요.

## 정리와 다음 글

알고리즘은 문제를 해결하는 명확한 절차이며, 어떤 알고리즘을 선택하느냐가 성능과 확장성을 크게 좌우합니다. 다음 글에서는 이 효율을 더 객관적으로 비교하는 도구인 시간 복잡도와 Big-O 표기법을 다룹니다.

## 실전 패턴 추가: 정렬과 탐색 구현을 문제 유형별로 선택하기

알고리즘 문제에서는 코드 길이보다 선택 기준이 더 중요합니다. 입력 크기, 데이터 분포, 정렬 여부에 따라 정렬/탐색 전략이 달라집니다. 아래 예시는 같은 정수 배열을 다루더라도 어떤 조건에서 어떤 구현을 고르는지 보여 줍니다.

```python
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def merge_sort(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])

    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    less = [x for x in nums if x < pivot]
    equal = [x for x in nums if x == pivot]
    greater = [x for x in nums if x > pivot]
    return quick_sort(less) + equal + quick_sort(greater)
```

실무 판단은 보통 이렇게 정리됩니다. 이미 정렬된 리스트에서 존재 여부를 반복 조회하면 이진 탐색이 기본 선택입니다. 입력이 계속 바뀌고 안정 정렬이 필요하면 병합 정렬 계열이 유리하고, 평균 성능과 구현 단순성을 우선하면 퀵 정렬 계열이 자주 선택됩니다. 코딩 테스트에서는 Python 내장 `sort()`가 Timsort 기반이라 거의 항상 가장 실용적인 기본값이지만, 원리를 직접 구현해 보면 경계 조건과 복잡도 해석 능력이 크게 좋아집니다.

## 심화 실전 노트: 알고리즘 사고를 코드로 고정하는 방법

### 구현 앵커: 사양-검증-복잡도 로그를 함께 남기는 템플릿

```python
def run_algorithm_contract(name: str, func, cases: list[tuple[tuple, object]]) -> None:
    """알고리즘 함수의 계약을 검증하고 실패 지점을 바로 출력합니다."""
    for index, (args, expected) in enumerate(cases, start=1):
        actual = func(*args)
        if actual != expected:
            raise AssertionError(
                f"[{name}] case#{index} failed: args={args}, expected={expected}, actual={actual}"
            )


def max_linear(nums: list[int]) -> int:
    if not nums:
        raise ValueError("empty input")
    current_max = nums[0]
    for value in nums[1:]:
        if value > current_max:
            current_max = value
    return current_max


run_algorithm_contract(
    "max_linear",
    max_linear,
    [
        ((([3, 1, 2],),), 3),
        ((([-5, -1, -7],),), -1),
        ((([42],),), 42),
    ],
)
```

작은 예제에서 맞는 코드를 쓰는 것만으로는 부족합니다. 입력 계약, 경계값, 실패 메시지를 함께 고정해 두어야 다음 리팩터링에서도 알고리즘의 의도가 유지됩니다.

### 실행 추적: 값이 바뀌는 순간만 기록하는 방식

```text
입력: [8, 3, 9, 2, 9, 1]
초기 max = 8
3 비교 -> 유지(8)
9 비교 -> 갱신(9)
2 비교 -> 유지(9)
9 비교 -> 유지(9)
1 비교 -> 유지(9)
결과: 9
```

이런 추적은 코드 설명용이 아니라 디버깅용입니다. 인터뷰에서도 "왜 이 줄에서 값이 바뀌는가"를 설명할 수 있으면 정답률보다 신뢰도를 크게 높일 수 있습니다.

### 복잡도 비교표: 연산 수를 숫자로 보는 습관

| 접근 | 아이디어 | 시간 복잡도 | 공간 복잡도 | 입력 100만에서 예상 경향 |
|------|----------|-------------|-------------|---------------------------|
| 정렬 후 마지막 원소 | 전체 순서 확정 | `O(n log n)` | `O(n)` 또는 구현 의존 | 불필요한 정렬 비용 발생 |
| 단일 순회 최댓값 | 현재 최댓값 유지 | `O(n)` | `O(1)` | 선형 증가, 예측 가능 |
| 모든 쌍 비교 | 두 값 관계 확인 | `O(n^2)` | `O(1)` | 대규모 입력에서 비실용 |

문제의 본질이 "순서"가 아니라 "극값"이면 정렬을 피하는 것이 원칙입니다. 정렬은 강력하지만 비용이 비쌉니다.

### 인터뷰형 문제 분해: 질문을 네 줄로 쪼개기

- 입력 범위: `n`이 최대 얼마인가
- 출력 형식: 값 하나인지, 인덱스인지, 경로인지
- 허용 오차: 정수 정확 일치인지, 근사 허용인지
- 실패 조건: 빈 입력, 중복, 음수 처리 규칙이 있는지

문제를 풀기 전에 이 네 줄을 메모하면, 대부분의 설계 오류는 구현 전에 걸러집니다.

### 시간 복잡도 간단 증명: 왜 `O(n)`인가

최댓값 단일 순회 알고리즘은 첫 원소를 초기화한 뒤 나머지 `n-1`개를 한 번씩만 비교합니다. 각 반복은 상수 시간 연산(비교, 대입)만 수행하므로 총 연산 수는 `a + b(n-1)` 형태입니다. 상수항과 계수를 제거하면 성장률은 `O(n)`입니다.

### 실수-수정 페어

| 실수 | 증상 | 수정 |
|------|------|------|
| 빈 배열 처리 누락 | `IndexError` 발생 | 함수 시작에서 입력 검증 |
| 정렬 후 원본 인덱스 필요 문제를 값 문제로 오해 | 정답 형식 오답 | 값이 아닌 `(값, 인덱스)` 유지 |
| 디버깅 없이 통과만 목표 | 반례에서 즉시 실패 | 실행 추적 + 검증 케이스 고정 |

알고리즘 입문 단계에서 가장 큰 차이는 "코드 길이"가 아니라 "검증 루프를 붙이는 습관"에서 생깁니다.

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

## 처음 질문으로 돌아가기

- **알고리즘은 정확히 무엇이며, 어떤 성질을 가져야 할까요?**
  - 본문의 기준은 알고리즘이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **알고리즘을 의사코드나 Python 코드로 어떻게 표현할 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **같은 문제를 푸는 두 알고리즘은 왜 효율이 크게 달라질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **알고리즘이란 무엇인가? (현재 글)**
- 시간 복잡도와 Big-O (예정)
- 선형 탐색과 이진 탐색 (예정)
- 정렬 알고리즘 (예정)
- 재귀와 분할 정복 (예정)
- 동적 계획법 기초 (예정)
- 그래프 탐색 — BFS와 DFS (예정)
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)

<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms (CLRS) — MIT Press](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Real Python — Sorting Algorithms in Python](https://realpython.com/sorting-algorithms-python/)
- [GeeksforGeeks — Fundamentals of Algorithms](https://www.geeksforgeeks.org/fundamentals-of-algorithms/)
- [Khan Academy — Algorithms](https://www.khanacademy.org/computing/computer-science/algorithms)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/01-what-are-algorithms)

Tags: Python, Algorithms, Problem Solving, Programming Basics, Time Complexity
