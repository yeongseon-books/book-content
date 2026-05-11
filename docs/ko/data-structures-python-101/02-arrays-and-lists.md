---
series: data-structures-python-101
episode: 2
title: 배열과 리스트
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
  - 자료구조
  - list
  - array
  - 시간 복잡도
seo_description: Python list의 내부 구조와 배열 기반 연산의 시간 복잡도를 설명합니다.
last_reviewed: '2026-05-04'
---

# 배열과 리스트

> Data Structures with Python 101 시리즈 (2/10)


## 이 글에서 다룰 문제

list는 Python에서 가장 많이 사용하는 자료구조입니다. 그런데 list의 내부 동작을 모르면 비효율적인 코드를 작성하기 쉽습니다. 예를 들어, 리스트 앞에 원소를 삽입하는 코드가 왜 느린지 모르면 성능 문제의 원인을 찾기 어렵습니다.

> list 하나를 제대로 이해하면 스택, 큐, 힙 등 다른 자료구조의 기반을 이해한 것입니다.

list는 다른 자료구조를 구현하는 기반이기도 합니다. 스택은 list의 append/pop으로, 힙은 list 위에 heapq로 구현됩니다. list를 깊이 이해하면 나머지 자료구조를 배우기가 수월해집니다.

## 핵심 개념 잡기

> 동적 배열 = 크기가 자동으로 늘어나는 배열

```
[정적 배열]     크기 고정, 선언 시 결정
  ┌───┬───┬───┬───┐
  │ 1 │ 2 │ 3 │ 4 │  ← 4칸 고정
  └───┴───┴───┴───┘

[동적 배열]     공간 부족 시 2배로 확장
  ┌───┬───┬───┬───┬───┬───┬───┬───┐
  │ 1 │ 2 │ 3 │ 4 │   │   │   │   │  ← 여유 공간 확보
  └───┴───┴───┴───┴───┴───┴───┴───┘
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 정적 배열 | 크기가 고정된 배열로, C의 `int arr[10]`과 같습니다 |
| 동적 배열 | 원소가 추가되면 자동으로 크기가 늘어나는 배열입니다 |
| 인덱스 접근 | 배열에서 위치로 원소를 O(1)에 가져오는 연산입니다 |
| 슬라이싱 | list[start:end]로 부분 리스트를 만드는 연산입니다 |
| amortized O(1) | append 시 가끔 배열 확장이 발생하지만 평균적으로 O(1)입니다 |

## Before / After

리스트 앞에 원소를 삽입하는 비효율적 방법과 효율적 방법을 비교합니다.

```python
# before: list 앞에 삽입 — O(n), 모든 원소를 한 칸씩 이동
data = [1, 2, 3, 4, 5]
data.insert(0, 0)  # 전체 원소를 오른쪽으로 밀어야 합니다
```

```python
# after: deque로 앞에 삽입 — O(1)
from collections import deque
data = deque([1, 2, 3, 4, 5])
data.appendleft(0)  # O(1)로 앞에 삽입합니다
```

## 단계별 실습

### Step 1: list 기본 연산과 시간 복잡도 확인

```python
numbers = [10, 20, 30, 40, 50]

# 인덱스 접근 — O(1)
print(numbers[2])     # 30

# 끝에 추가 — amortized O(1)
numbers.append(60)
print(numbers)        # [10, 20, 30, 40, 50, 60]

# 끝에서 제거 — O(1)
last = numbers.pop()
print(last)           # 60
```

### Step 2: 중간 삽입·삭제의 비용 측정

```python
import time

size = 100_000
data = list(range(size))

# 앞에 삽입 — O(n)
start = time.perf_counter()
data.insert(0, -1)
insert_front = time.perf_counter() - start

# 끝에 삽입 — O(1)
start = time.perf_counter()
data.append(-1)
insert_end = time.perf_counter() - start

print(f"앞 삽입: {insert_front:.6f}초")
print(f"끝 삽입: {insert_end:.6f}초")
print(f"앞 삽입이 {insert_front / max(insert_end, 1e-9):.0f}배 느립니다")
```

### Step 3: 슬라이싱 활용

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(data[2:5])    # [2, 3, 4]
print(data[::2])    # [0, 2, 4, 6, 8] — 짝수 인덱스
print(data[::-1])   # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] — 역순
```

### Step 4: list comprehension으로 변환

```python
# 제곱수 리스트
squares = [x ** 2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 조건 필터링
evens = [x for x in range(20) if x % 2 == 0]
print(evens)    # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Step 5: array 모듈과 비교

```python
from array import array

# array: 타입이 고정된 배열 — 메모리 효율적
int_array = array('i', [1, 2, 3, 4, 5])  # 'i' = signed int
print(int_array[0])  # 1

# list는 다양한 타입 혼합 가능
mixed = [1, "hello", 3.14, True]
print(mixed)
```

## 이 코드에서 주목할 점

- list의 인덱스 접근과 append는 O(1)이지만, insert(0, x)는 O(n)입니다
- 슬라이싱은 새로운 list를 만들므로 O(k) 시간과 공간이 필요합니다 (k = 슬라이스 길이)
- list comprehension은 for 루프보다 빠르고 가독성이 좋습니다
- array 모듈은 동일 타입만 저장하여 메모리를 절약하지만 일반적으로 list를 사용합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 루프 안에서 list.insert(0, x) 반복 | O(n²)이 되어 대규모 데이터에서 극도로 느립니다 | deque.appendleft()를 사용합니다 |
| list를 복사할 때 `b = a` 사용 | 같은 객체를 참조하여 한쪽 수정이 다른 쪽에 영향줍니다 | `b = a[:]` 또는 `b = a.copy()`를 사용합니다 |
| 중첩 list를 `[[] * 3]`으로 초기화 | 같은 내부 list를 참조합니다 | `[[] for _ in range(3)]`을 사용합니다 |
| 순회 중 list 수정 | 인덱스가 밀려 예상과 다른 결과가 나옵니다 | 새 list를 만들거나 역순으로 순회합니다 |
| len() 호출이 O(n)이라고 오해 | 불필요하게 길이를 변수에 캐싱합니다 | Python의 len()은 O(1)입니다 — 직접 호출해도 됩니다 |

## 실무에서 이렇게 쓰입니다

- API 응답의 JSON 배열을 list로 받아 처리합니다
- 로그 데이터를 list에 쌓고 배치 처리합니다
- list comprehension으로 데이터 변환 파이프라인을 구성합니다
- 슬라이싱으로 페이지네이션을 구현합니다 (items[offset:offset+limit])
- 대규모 수치 데이터는 array 대신 NumPy 배열을 사용합니다

## 현업 개발자는 이렇게 생각합니다

대부분의 상황에서 Python list는 충분히 빠릅니다. 성능 최적화는 프로파일링으로 병목을 확인한 후에 합니다. 하지만 "list 앞에 삽입하면 느리다"는 사실을 알고 있으면 처음부터 올바른 자료구조를 선택할 수 있습니다.

실무에서 list를 사용할 때는 "이 list에 어떤 연산을 주로 하는가?"를 먼저 생각합니다. 끝에서만 추가/제거하면 list가 적합하고, 양쪽 끝에서 조작하면 deque, 검색이 잦으면 set이나 dict가 적합합니다.

## 체크리스트

- [ ] Python list가 동적 배열로 구현됨을 설명할 수 있다
- [ ] list의 주요 연산별 시간 복잡도를 말할 수 있다
- [ ] insert(0, x)가 append(x)보다 느린 이유를 설명할 수 있다
- [ ] 슬라이싱과 list comprehension을 활용할 수 있다
- [ ] array 모듈과 list의 차이를 설명할 수 있다

## 정리 및 다음 글 안내

Python list는 동적 배열로 구현되어 인덱스 접근은 O(1), 끝 삽입/삭제는 amortized O(1), 중간 삽입/삭제는 O(n)입니다. 다음 글에서는 list를 활용한 스택과 큐 자료구조를 다룹니다.

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
