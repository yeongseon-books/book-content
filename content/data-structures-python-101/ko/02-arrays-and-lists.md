---
series: data-structures-python-101
episode: 2
title: 배열과 리스트
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
  - 자료구조
  - list
  - array
  - 시간 복잡도
seo_description: Python list의 동적 배열 구조와 주요 연산의 비용을 설명합니다.
last_reviewed: '2026-05-12'
---

# 배열과 리스트

이 글은 Data Structures with Python 101 시리즈의 두 번째 글입니다.

## 이 글에서 다룰 문제

- Python의 list는 배열일까요, 연결 리스트일까요?
- 동적 배열은 어떤 방식으로 크기를 늘리며 왜 append가 빠를까요?
- list에서 앞 삽입과 중간 삭제가 느린 이유는 무엇일까요?
- `array` 모듈과 list는 언제 다르게 써야 할까요?

> 멘탈 모델: Python의 list는 “아무 값이나 담는 상자”가 아니라, 내부적으로는 자동 확장되는 동적 배열입니다. 그래서 인덱스 접근은 빠르지만, 앞쪽 삽입은 비쌉니다.

## 왜 이 글이 중요한가

Python에서 가장 자주 만나는 자료구조는 list입니다. 그런데 가장 익숙한 구조일수록 내부 동작을 당연하게 여기기 쉽습니다. 예를 들어 list 앞에 데이터를 계속 넣는 코드가 왜 느린지 모르고 있으면, 성능 문제를 만났을 때 원인을 코드 로직이 아니라 엉뚱한 곳에서 찾게 됩니다.

> list를 깊이 이해한다는 것은 스택, 큐, 힙 같은 다른 구조의 기반을 이해한다는 뜻이기도 합니다.

실제로 list는 다른 자료구조의 토대가 됩니다. 스택은 list의 `append`와 `pop`으로 자연스럽게 구현되고, 힙도 list 위에 `heapq`를 얹어 동작합니다. 그래서 list를 제대로 이해해 두면 뒤에서 나오는 여러 자료구조를 훨씬 적은 비용으로 익힐 수 있습니다.

## 핵심 개념 한눈에 보기

> 동적 배열 = 원소가 늘어나면 내부 저장 공간도 자동으로 확장되는 배열

```text
[static array]     fixed size, determined at declaration
  +---+---+---+---+
  | 1 | 2 | 3 | 4 |  <- 4 slots, fixed
  +---+---+---+---+

[dynamic array]    doubles when capacity is exceeded
  +---+---+---+---+---+---+---+---+
  | 1 | 2 | 3 | 4 |   |   |   |   |  <- extra capacity reserved
  +---+---+---+---+---+---+---+---+
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 정적 배열 | C의 `int arr[10]`처럼 크기가 고정된 배열입니다 |
| 동적 배열 | 원소가 추가되면 내부 저장 공간을 확장할 수 있는 배열입니다 |
| 인덱스 접근 | 위치를 통해 원소를 O(1)에 가져오는 연산입니다 |
| 슬라이싱 | `list[start:end]`처럼 부분 list를 새로 만드는 연산입니다 |
| amortized O(1) | append가 가끔 확장을 일으켜도 평균적으로는 O(1)로 동작함을 뜻합니다 |

## Before / After

list를 무심코 쓰는 경우와, 연산 패턴에 맞는 구조를 고르는 경우를 비교해 보겠습니다.

```python
# before: insert at front of list — O(n), shifts all elements
data = [1, 2, 3, 4, 5]
data.insert(0, 0)  # every element shifts one position to the right
```

```python
# after: insert at front with deque — O(1)
from collections import deque
data = deque([1, 2, 3, 4, 5])
data.appendleft(0)  # O(1) insertion at the front
```

같은 “앞에 하나 넣기” 연산이라도 내부 구조가 다르면 비용이 완전히 달라집니다. list는 연속 메모리를 유지해야 해서 요소들을 밀어야 하고, deque는 양쪽 끝 연산을 위해 설계되어 있어 이동 비용이 거의 없습니다.

## 단계별 실습

### Step 1: Verify basic list operations and their time complexity

```python
numbers = [10, 20, 30, 40, 50]

# index access — O(1)
print(numbers[2])     # 30

# append — amortized O(1)
numbers.append(60)
print(numbers)        # [10, 20, 30, 40, 50, 60]

# pop from end — O(1)
last = numbers.pop()
print(last)           # 60
```

### Step 2: Measure the cost of mid-list insertion and deletion

```python
import time

size = 100_000
data = list(range(size))

# insert at front — O(n)
start = time.perf_counter()
data.insert(0, -1)
insert_front = time.perf_counter() - start

# insert at end — O(1)
start = time.perf_counter()
data.append(-1)
insert_end = time.perf_counter() - start

print(f"front insert: {insert_front:.6f}s")
print(f"end   insert: {insert_end:.6f}s")
print(f"front insert is {insert_front / max(insert_end, 1e-9):.0f}x slower")
```

### Step 3: Use slicing

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(data[2:5])    # [2, 3, 4]
print(data[::2])    # [0, 2, 4, 6, 8] — even indices
print(data[::-1])   # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] — reversed
```

### Step 4: Transform with list comprehension

```python
# list of squares
squares = [x ** 2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# filter with condition
evens = [x for x in range(20) if x % 2 == 0]
print(evens)    # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Step 5: Compare the array module with list

```python
from array import array

# array: type-fixed array — memory efficient
int_array = array('i', [1, 2, 3, 4, 5])  # 'i' = signed int
print(int_array[0])  # 1

# list can mix types
mixed = [1, "hello", 3.14, True]
print(mixed)
```

## 이 코드에서 먼저 봐야 할 점

- list의 인덱스 접근과 끝 append는 O(1)이지만, `insert(0, x)`는 O(n)입니다.
- 슬라이싱은 보기에는 가볍지만 실제로는 새 list를 만들기 때문에 O(k) 시간과 공간이 듭니다.
- list comprehension은 단순 반복보다 짧고 읽기 쉬울 뿐 아니라, 대개 더 효율적으로 동작합니다.
- `array` 모듈은 타입이 고정된 데이터를 메모리 효율적으로 담지만, Python에서는 범용성 때문에 list가 기본 선택지입니다.

실무 감각으로 옮기면 질문은 단순합니다. “이 list에서 가장 자주 하는 연산이 무엇인가?” 끝에서 넣고 빼는 것이 대부분이면 list는 훌륭합니다. 반대로 양쪽 끝을 자주 다루면 deque가 더 자연스럽습니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 루프 안에서 `list.insert(0, x)` 반복 | 사실상 O(n²)이 되어 데이터가 커지면 급격히 느려집니다 | 앞 삽입이 많으면 `deque.appendleft()`를 사용합니다 |
| `b = a`로 list 복사 | 두 변수가 같은 객체를 가리켜 한쪽 변경이 다른 쪽에 반영됩니다 | `a[:]` 또는 `a.copy()`로 복사합니다 |
| `[[] * 3]`으로 중첩 list 초기화 | 모든 내부 list가 같은 객체를 참조합니다 | `[[] for _ in range(3)]`를 사용합니다 |
| 순회 중 list 수정 | 인덱스가 밀려 의도하지 않은 결과가 나옵니다 | 새 list를 만들거나 역순 순회를 사용합니다 |
| `len()`을 비싼 연산으로 오해 | 불필요한 캐싱과 코드 복잡도가 생깁니다 | Python의 `len()`은 O(1)이므로 직접 호출합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답의 JSON 배열은 대부분 list로 다뤄집니다.
- 로그나 이벤트를 list에 모아 배치 처리하는 패턴이 흔합니다.
- list comprehension은 데이터 변환 파이프라인의 기본 도구입니다.
- 슬라이싱은 페이지네이션이나 부분 처리 로직에서 자주 사용됩니다.
- 대규모 수치 계산은 일반 list 대신 NumPy 배열로 넘어가는 출발점이 됩니다.

## 실무에서는 이렇게 생각합니다

대부분의 상황에서 Python list는 충분히 빠릅니다. 그래서 현업에서는 무조건 다른 구조로 바꾸기보다, 먼저 병목이 어디인지 확인합니다. 다만 “list 앞 삽입은 느리다” 같은 기본 원리를 알고 있으면, 병목을 만들지 않는 방향으로 처음부터 설계를 시작할 수 있습니다.

좋은 개발자는 list를 만능 기본값으로 쓰되, 그 기본값이 깨지는 조건도 함께 알고 있습니다. 순서가 중요하고 끝 연산이 많다면 list, 양쪽 끝이 중요하면 deque, 빠른 조회가 핵심이면 set이나 dict입니다.

## 체크리스트

- [ ] Python list가 동적 배열로 구현된다는 점을 설명할 수 있다
- [ ] list의 주요 연산별 시간 복잡도를 말할 수 있다
- [ ] `insert(0, x)`가 `append(x)`보다 느린 이유를 설명할 수 있다
- [ ] 슬라이싱과 list comprehension의 비용과 장점을 설명할 수 있다
- [ ] `array` 모듈과 list의 차이를 설명할 수 있다

## 연습 문제

1. 원소 100,000개인 list에서 `insert(0, x)`를 1,000번 수행하는 시간과 `deque.appendleft(x)`를 1,000번 수행하는 시간을 비교해 보세요.
2. 5x5 2차원 list를 올바르게 초기화하고, `(2, 3)` 위치 값을 바꿔도 다른 행이 영향을 받지 않는지 확인해 보세요.
3. 1부터 100까지의 수 중 3의 배수이면서 5의 배수는 아닌 값만 담은 list를 comprehension으로 만들어 보세요.

## 정리 및 다음 글 안내

Python의 list는 동적 배열로 구현되어 인덱스 접근은 O(1), 끝 append/pop은 평균적으로 O(1), 앞이나 중간 삽입·삭제는 O(n)입니다. list를 제대로 이해하면 “익숙한 자료구조”를 넘어서, 다른 구조를 선택해야 하는 시점도 함께 판단할 수 있습니다. 다음 글에서는 list 위에서 자주 구현되는 스택과 큐를 살펴보겠습니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- **배열과 리스트 (현재 글)**
- 스택과 큐 (예정)
- 해시 테이블과 dict (예정)
- 연결 리스트 (예정)
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [CPython list implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Real Python — Python Lists and Tuples](https://realpython.com/python-lists-tuples/)

Tags: Python, 자료구조, list, array, 시간 복잡도
