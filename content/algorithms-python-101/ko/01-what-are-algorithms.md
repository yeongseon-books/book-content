---
series: algorithms-python-101
episode: 1
title: 알고리즘이란 무엇인가?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - 알고리즘
  - Algorithm
  - 입문
  - 문제 해결
seo_description: 알고리즘의 정의와 특성을 이해하고 Python으로 첫 알고리즘을 작성합니다.
last_reviewed: '2026-05-11'
---

# 알고리즘이란 무엇인가?

프로그래밍은 결국 문제를 푸는 일입니다. 같은 문제라도 어떤 알고리즘을 고르느냐에 따라 실행 시간이 크게 달라집니다. 알고리즘을 이해하면 더 빠르고 정확한 코드를 작성할 수 있습니다.

코딩 테스트, 성능 최적화, 시스템 설계처럼 개발자가 자주 마주치는 주제 전반에서 알고리즘 사고력은 중요한 기본기입니다.

이 글은 Algorithms with Python 101 시리즈의 첫 번째 글입니다. 여기서는 알고리즘의 정의와 특성을 먼저 잡고, Python으로 첫 번째 알고리즘을 작성하는 출발점을 마련하겠습니다.

## 이 글에서 다룰 문제

> 알고리즘 = 입력을 받아 원하는 출력을 만드는 명확한 단계의 집합

## 핵심 개념 잡기

> 알고리즘 = 유한한 단계로 문제를 해결하는 명확한 절차

```text
[문제] → [알고리즘] → [해답]

예: 리스트에서 최댓값 찾기
입력: [3, 7, 2, 9, 4]
알고리즘:
  1. 첫 번째 값을 최댓값으로 설정
  2. 나머지 값을 순서대로 비교
  3. 더 큰 값이 있으면 최댓값 갱신
출력: 9
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 알고리즘 | 문제를 해결하는 명확하고 유한한 단계의 절차입니다 |
| 입력(input) | 알고리즘에 주어지는 데이터입니다 |
| 출력(output) | 알고리즘이 생성하는 결과입니다 |
| 정확성(correctness) | 모든 입력에 대해 올바른 출력을 생성하는 성질입니다 |
| 효율성(efficiency) | 시간과 메모리를 얼마나 적게 사용하는가의 척도입니다 |

## Before / After

리스트에서 최댓값을 찾는 두 가지 접근을 비교합니다.

```python
# 이전 방식: 매번 정렬한 뒤 최댓값 추출 — O(n log n)
data = [3, 7, 2, 9, 4]
sorted_data = sorted(data)
maximum = sorted_data[-1]
```

```python
# 개선 방식: 한 번 순회하여 최댓값 추출 — O(n)
data = [3, 7, 2, 9, 4]
maximum = data[0]
for x in data[1:]:
    if x > maximum:
        maximum = x
```

## 단계별 실습

### Step 1: 최댓값 찾기 알고리즘

```python
def find_max(numbers: list[int]) -> int:
    """리스트에서 최댓값을 찾는 알고리즘"""
    if not numbers:
        raise ValueError("빈 리스트에서 최댓값을 찾을 수 없습니다")
    maximum = numbers[0]
    for num in numbers[1:]:
        if num > maximum:
            maximum = num
    return maximum

data = [3, 7, 2, 9, 4]
print(f"최댓값: {find_max(data)}")  # 최댓값: 9
```

### Step 2: 합계와 평균 알고리즘

```python
def compute_stats(numbers: list[int]) -> dict:
    """리스트의 합계, 평균, 최솟값, 최댓값을 계산합니다"""
    if not numbers:
        raise ValueError("빈 리스트입니다")
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

### Step 3: 문자열 뒤집기 알고리즘

```python
def reverse_string(text: str) -> str:
    """문자열을 뒤집는 알고리즘 — 슬라이싱 없이 직접 구현"""
    result = []
    for i in range(len(text) - 1, -1, -1):
        result.append(text[i])
    return "".join(result)

print(reverse_string("algorithm"))  # mhtirogla
print(reverse_string("Python"))     # nohtyP

# 비교: Python 내장 방식을 사용한 예
print("algorithm"[::-1])  # mhtirogla
```

### Step 4: 두 알고리즘의 효율성 비교

```python
import time

def has_duplicate_brute(data: list[int]) -> bool:
    """중복 검사 — 브루트포스 O(n²)"""
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j]:
                return True
    return False

def has_duplicate_set(data: list[int]) -> bool:
    """중복 검사 — set 활용 O(n)"""
    return len(data) != len(set(data))

test_data = list(range(10_000))

start = time.perf_counter()
has_duplicate_brute(test_data)
brute_time = time.perf_counter() - start

start = time.perf_counter()
has_duplicate_set(test_data)
set_time = time.perf_counter() - start

print(f"브루트포스: {brute_time:.4f}초")
print(f"set 활용:   {set_time:.6f}초")
```

### Step 5: 알고리즘의 5가지 특성 확인

```python
def is_palindrome(text: str) -> bool:
    """회문(팰린드롬) 검사 알고리즘
    
    알고리즘의 5가지 특성을 모두 만족합니다:
    1. 입력(input): 문자열 text
    2. 출력(output): True 또는 False
    3. 명확성(definiteness): 각 단계가 모호하지 않음
    4. 유한성(finiteness): 문자열 길이만큼만 반복
    5. 효과성(effectiveness): 기본 연산만 사용
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

print(is_palindrome("racecar"))       # True
print(is_palindrome("hello"))         # False
print(is_palindrome("A man a plan a canal Panama"))  # True
```

## 이 코드에서 주목할 점

- 같은 문제라도 알고리즘에 따라 성능이 크게 달라집니다(O(n²) vs O(n))
- 알고리즘은 입력, 출력, 명확성, 유한성, 효과성 5가지 특성을 가집니다
- Python 내장 함수(max, sorted)도 알고리즘입니다. 직접 구현해 보면 동작 원리를 더 잘 이해할 수 있습니다
- 엣지 케이스(빈 리스트, 빈 문자열)를 처리하는 것이 좋은 알고리즘의 조건입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 엣지 케이스 미처리 | 빈 입력에서 오류가 발생합니다 | 입력 검증을 항상 먼저 합니다 |
| 무한 루프 | 종료 조건 오류로 프로그램이 멈추지 않습니다 | 루프 변수가 종료 조건에 수렴하는지 확인합니다 |
| Off-by-one 오류 | 인덱스가 1만큼 벗어납니다 | 경계값 테스트를 반드시 합니다 |
| 비효율적 알고리즘 선택 | 데이터가 커지면 실행 시간이 급증합니다 | 시간 복잡도를 먼저 분석합니다 |
| 정확성 미검증 | 일부 입력에서만 동작합니다 | 다양한 테스트 케이스로 검증합니다 |

## 실무에서 이렇게 쓰입니다

- 검색 엔진이 수십억 웹 페이지에서 결과를 밀리초 안에 반환합니다
- 추천 시스템이 사용자 선호도를 분석하여 콘텐츠를 제안합니다
- 네비게이션 앱이 최적 경로를 실시간으로 계산합니다
- 압축 알고리즘이 파일 크기를 줄여 저장 공간을 절약합니다
- 암호화 알고리즘이 데이터를 안전하게 보호합니다

## 현업 개발자는 이렇게 생각합니다

일상적인 개발에서 알고리즘을 처음부터 직접 구현할 일은 많지 않습니다. 라이브러리와 프레임워크가 이미 최적화된 알고리즘을 제공하기 때문입니다. 그래도 알고리즘적 사고력은 문제를 분석하고 적절한 도구를 고르는 데 꼭 필요합니다.

"이 코드는 왜 느릴까?", "더 나은 방법은 없을까?" 같은 질문에 답하려면 알고리즘의 기본을 알고 있어야 합니다.

## 체크리스트

- [ ] 알고리즘의 정의와 5가지 특성을 설명할 수 있다
- [ ] 같은 문제를 해결하는 두 알고리즘의 효율성 차이를 설명할 수 있다
- [ ] Python으로 간단한 알고리즘(최댓값, 회문 검사)을 구현할 수 있다
- [ ] 엣지 케이스를 고려한 알고리즘을 작성할 수 있다
- [ ] 브루트포스와 최적화된 알고리즘의 차이를 실측할 수 있다

## 정리 및 다음 글 안내

알고리즘은 문제를 해결하는 명확한 절차이며, 효율성은 알고리즘을 선택할 때 가장 중요한 기준 가운데 하나입니다. 다음 글에서는 알고리즘의 효율성을 객관적으로 설명하는 도구인 시간 복잡도와 Big-O 표기법을 다룹니다.

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

Tags: Python, 알고리즘, Algorithm, 입문, 문제 해결
