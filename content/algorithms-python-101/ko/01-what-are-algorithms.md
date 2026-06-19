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

![Algorithms with Python 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/01/01-01-big-picture.ko.png)
*Algorithms with Python 101 1장 흐름 개요*

## 이 글에서 다룰 문제

- 알고리즘은 정확히 무엇이며, 어떤 성질을 가져야 할까요?
- 알고리즘을 의사코드나 Python 코드로 어떻게 표현할 수 있을까요?
- 같은 문제를 푸는 두 알고리즘은 왜 효율이 크게 달라질까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

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

## 알고리즘의 다섯 가지 성질

좋은 알고리즘은 다음 다섯 가지 성질을 모두 만족합니다.

| 성질 | 설명 | 위반 시 결과 |
|------|------|-------------|
| 입력(Input) | 0개 이상의 외부 데이터를 받습니다 | 입력 없이 동작 불가 |
| 출력(Output) | 1개 이상의 결과를 만듭니다 | 결과가 없으면 알고리즘이 아닙니다 |
| 명확성(Definiteness) | 각 단계가 모호하지 않습니다 | 단계가 불분명하면 구현이 달라집니다 |
| 유한성(Finiteness) | 반드시 종료됩니다 | 무한 루프가 됩니다 |
| 효과성(Effectiveness) | 각 단계를 실제로 수행할 수 있습니다 | 계산 불가 연산을 포함합니다 |

## 적용 전후 비교

리스트에서 최댓값을 찾는 두 가지 접근을 비교해 보겠습니다.

```python
# before: 리스트를 정렬한 뒤 마지막 요소를 가져옴 — O(n log n)
data = [3, 7, 2, 9, 4]
sorted_data = sorted(data)
maximum = sorted_data[-1]
```

```python
# after: 리스트를 한 번만 순회 — O(n)
data = [3, 7, 2, 9, 4]
maximum = data[0]
for x in data[1:]:
    if x > maximum:
        maximum = x
```

정렬은 강력하지만 비쌉니다. 문제의 본질이 "극값"이라면 정렬은 불필요한 비용을 추가합니다.

## 단계별 실습

### 단계 1: 최댓값 찾기

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

가장 단순한 선형 순회 알고리즘입니다. 정렬 없이 한 번만 훑기 때문에, 같은 문제를 더 직접적으로 풉니다.

### 단계 2: 기본 통계 계산

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

한 번의 반복으로 여러 값을 함께 계산합니다. 같은 순회 안에서 무엇을 함께 처리할 수 있는지 보는 습관이 알고리즘 설계의 출발점입니다.

### 단계 3: 문자열 뒤집기

```python
def reverse_string(text: str) -> str:
    """Reverse a string without slicing."""
    result = []
    for i in range(len(text) - 1, -1, -1):
        result.append(text[i])
    return "".join(result)

print(reverse_string("algorithm"))  # mhtirogla
print(reverse_string("Python"))    # nohtyP

# Python built-in과 비교
print("algorithm"[::-1])  # mhtirogla
```

내장 기능이 있어도 직접 구현해 보면 반복, 인덱스, 종료 조건 같은 알고리즘의 기본 단위를 더 분명하게 볼 수 있습니다.

### 단계 4: 두 알고리즘 비교

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

같은 문제라도 알고리즘 선택에 따라 실행 시간이 극단적으로 달라집니다.

### 단계 5: 회문 검사 — 다섯 가지 속성 검증

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

## 단계별 실행 추적

`find_max([8, 3, 9, 2, 9, 1])`의 실행을 한 줄씩 따라가 보겠습니다.

```text
입력: [8, 3, 9, 2, 9, 1]

초기화:
  maximum = 8  (numbers[0])

반복 시작 (numbers[1:]= [3, 9, 2, 9, 1]):
  num=3  → 3 > 8? No  → maximum 유지 (8)
  num=9  → 9 > 8? Yes → maximum 갱신 (9)
  num=2  → 2 > 9? No  → maximum 유지 (9)
  num=9  → 9 > 9? No  → maximum 유지 (9)  ← 같을 때 갱신 안 함
  num=1  → 1 > 9? No  → maximum 유지 (9)

결과: 9
```

이런 추적은 "왜 이 줄에서 값이 바뀌는가"를 설명할 수 있게 해 줍니다. 면접에서도 코드보다 추적을 설명하는 능력이 신뢰를 높입니다.

## 코딩 테스트 풀이 예시

**문제**: 배열에서 두 번째로 큰 값을 한 번의 순회로 찾아라.

```python
def find_second_max(numbers: list[int]) -> int | None:
    """
    한 번의 순회로 두 번째 최댓값을 찾습니다.
    시간 복잡도: O(n), 공간 복잡도: O(1)
    """
    if len(numbers) < 2:
        return None

    first = second = float("-inf")
    for num in numbers:
        if num > first:
            second = first
            first = num
        elif num > second and num != first:
            second = num

    return second if second != float("-inf") else None


# 테스트
print(find_second_max([3, 7, 2, 9, 4]))   # 7
print(find_second_max([5, 5, 5]))          # None (중복만 있는 경우)
print(find_second_max([1]))               # None (원소 1개)
print(find_second_max([-3, -1, -7]))      # -3
```

**단계별 추적** (`[3, 7, 2, 9, 4]` 입력):

```text
초기: first=-inf, second=-inf

num=3: 3 > -inf → first=3, second=-inf
num=7: 7 > 3   → first=7, second=3
num=2: 2 > 7?  No. 2 > 3? No → 변화 없음
num=9: 9 > 7   → first=9, second=7
num=4: 4 > 9?  No. 4 > 7? No → 변화 없음

결과: second = 7
```

**문제**: 가장 자주 등장하는 문자를 찾아라.

```python
def most_frequent_char(text: str) -> str:
    """
    문자열에서 가장 자주 등장하는 문자를 반환합니다.
    시간 복잡도: O(n), 공간 복잡도: O(k) (k = 고유 문자 수)
    """
    if not text:
        raise ValueError("Empty string")

    freq: dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    return max(freq, key=freq.get)


print(most_frequent_char("hello world"))  # l
print(most_frequent_char("aabbcc"))       # a (동률 시 첫 번째)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 경계 조건을 건너뜀 | 빈 입력에서 바로 실패할 수 있습니다 | 함수 첫 줄에 입력 검증을 추가합니다 |
| 무한 루프를 만듦 | 종료 조건이 없거나 잘못되면 끝나지 않습니다 | 루프 변수가 종료 조건에 수렴하는지 확인합니다 |
| Off-by-one 오류 | 인덱스가 1만큼 어긋납니다 | 경계값 테스트(n=0, n=1)를 꼼꼼히 합니다 |
| 비효율적인 알고리즘 선택 | 데이터가 커질수록 실행 시간이 폭증합니다 | 구현 전에 시간 복잡도를 먼저 따져 봅니다 |
| 정확성을 검증하지 않음 | 일부 입력에서만 우연히 맞을 수 있습니다 | 경계, 중복, 음수 등 다양한 입력으로 테스트합니다 |

## 복잡도 비교표

| 접근 | 아이디어 | 시간 복잡도 | 공간 복잡도 | 비고 |
|------|----------|-------------|-------------|------|
| 정렬 후 마지막 원소 | 전체 순서 확정 | `O(n log n)` | `O(n)` | 불필요한 정렬 비용 |
| 단일 순회 최댓값 | 현재 최댓값 유지 | `O(n)` | `O(1)` | 권장 |
| 모든 쌍 비교 | 두 값 관계 확인 | `O(n^2)` | `O(1)` | 대규모 입력에서 비실용 |

## 실무에서는 이렇게 연결됩니다

- 검색 엔진은 수십억 개의 페이지 중에서 결과를 빠르게 찾아야 합니다.
- 추천 시스템은 사용자 선호 데이터를 분석해 적절한 콘텐츠를 제안합니다.
- 내비게이션 앱은 실시간으로 더 좋은 경로를 계산합니다.
- 압축 알고리즘은 저장 공간을 줄이기 위해 데이터를 재배열합니다.
- 암호화 알고리즘은 전송 중이거나 저장된 데이터를 보호합니다.

## 현업에서는 이렇게 생각합니다

일상적인 개발에서 알고리즘을 처음부터 직접 구현할 일은 많지 않습니다. 대부분은 라이브러리와 프레임워크가 이미 최적화된 구현을 제공합니다. 그래도 알고리즘적 사고는 문제를 분석하고, 병목을 찾고, 더 나은 접근을 고르는 데 꼭 필요합니다.

"왜 이 코드는 느릴까?", "더 나은 방법이 있을까?"라는 질문에 답하려면 알고리즘의 기본 개념이 머릿속에 잡혀 있어야 합니다.

## 운영 체크리스트

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
## 시리즈 목차

- **Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가? (현재 글)**
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Introduction to Algorithms (CLRS) — MIT Press](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Real Python — Sorting Algorithms in Python](https://realpython.com/sorting-algorithms-python/)
- [GeeksforGeeks — Fundamentals of Algorithms](https://www.geeksforgeeks.org/fundamentals-of-algorithms/)
- [Khan Academy — Algorithms](https://www.khanacademy.org/computing/computer-science/algorithms)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/01-what-are-algorithms)

Tags: Python, Algorithms, Problem Solving, Programming Basics, Time Complexity
