---
series: algorithms-python-101
episode: 1
title: 알고리즘이란 무엇인가?
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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

# 알고리즘이란 무엇인가?

프로그래밍은 결국 문제를 푸는 일입니다. 같은 답을 내는 코드라도 입력이 커지면 완전히 다른 성능을 보일 수 있고, 그 차이는 대개 알고리즘에서 시작됩니다. 이 글은 Algorithms with Python 101 시리즈의 첫 번째 글입니다. 여기서는 알고리즘이 무엇인지 정의하고, 핵심 성질을 정리한 뒤, Python으로 간단한 알고리즘을 직접 구현해 보겠습니다.

알고리즘은 코딩 테스트에서만 중요한 주제가 아닙니다. 성능 최적화, 데이터 처리, 시스템에서의 트레이드오프 판단까지, 개발자가 실무에서 문제를 바라보는 방식 자체를 바꿉니다.

## 이 글에서 다룰 문제

- 알고리즘은 정확히 무엇이며, 어떤 성질을 가져야 할까요?
- 알고리즘을 의사코드나 Python 코드로 어떻게 표현할 수 있을까요?
- 같은 문제를 푸는 두 알고리즘은 왜 효율이 크게 달라질까요?
- 정확성과 효율성은 어떻게 구분해서 봐야 할까요?

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

<!-- toc:begin -->
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

Tags: Python, Algorithms, Problem Solving, Programming Basics, Time Complexity
