---
series: data-structures-python-101
episode: 2
title: "Data Structures with Python 101 (2/10): 배열과 리스트"
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
  - 자료구조
  - list
  - array
  - 시간 복잡도
seo_description: Python list의 동적 배열 구조와 주요 연산의 비용을 설명합니다.
last_reviewed: '2026-05-17'
---

# Data Structures with Python 101 (2/10): 배열과 리스트

이 글은 Data Structures with Python 101 시리즈의 두 번째 글입니다.


![Data Structures with Python 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/02/02-01-capacity.ko.png)
*Data Structures with Python 101 2장 흐름 개요*

## 먼저 던지는 질문

- Python의 `list`는 배열일까요, 연결 리스트일까요?
- `append()`는 list가 계속 커져도 왜 대체로 빠를까요?
- `insert(0, x)`와 중간 삭제는 왜 비쌀까요?

## 왜 이 글이 중요한가

Python에서 가장 자주 만나는 자료구조는 list입니다. 그런데 자주 쓰는 만큼 내부 동작을 너무 당연하게 여기기 쉽습니다. 앞 삽입이 왜 느린지, `append()`가 왜 보통 빠른지 모르면 성능 문제를 만났을 때 원인을 구조가 아니라 코드 스타일 탓으로만 오해하기 쉽습니다.

> list를 깊이 이해한다는 것은 스택, 힙, 큐 같은 다른 구조의 기반을 이해한다는 뜻이기도 합니다.

스택은 `append()`와 `pop()` 위에 자연스럽게 올라가고, `heapq`도 결국 list를 바탕으로 동작합니다. 그래서 list 내부 모델을 먼저 잡아 두면 뒤에서 만나는 자료구조를 훨씬 적은 비용으로 이해할 수 있습니다.

## 핵심 개념 한눈에 보기

> 동적 배열 = 논리 길이는 늘어나지만, 내부적으로는 앞으로의 append를 위해 spare capacity를 함께 예약하는 배열

```text
[static array]     선언 시 크기가 고정됨
  +---+---+---+---+
  | 1 | 2 | 3 | 4 |
  +---+---+---+---+

[dynamic array]    논리 길이 4, 예약 capacity 8
  +---+---+---+---+---+---+---+---+
  | 1 | 2 | 3 | 4 |   |   |   |   |
  +---+---+---+---+---+---+---+---+
```

## 리스트 capacity 증가를 그림으로 보면

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 정적 배열 | C의 `int arr[10]`처럼 크기가 고정된 배열입니다 |
| 동적 배열 | 원소가 늘어나면 더 큰 저장 공간을 확보할 수 있는 배열입니다 |
| 논리 길이 | 현재 실제로 들어 있는 원소 개수입니다 |
| 예약 capacity | 앞으로의 append를 위해 미리 잡아 둔 spare slot 수입니다 |
| amortized O(1) | `append()`가 가끔 확장 비용을 내더라도 평균적으로는 O(1)이라는 뜻입니다 |

## 적용 전후 비교
같은 “앞에 하나 넣기”라도 내부 구조가 다르면 비용이 크게 달라집니다.

```python
# before: list 앞 삽입 — O(n), 기존 원소를 모두 밀어야 함
data = [1, 2, 3, 4, 5]
data.insert(0, 0)
```

```python
# after: deque 앞 삽입 — O(1)
from collections import deque

data = deque([1, 2, 3, 4, 5])
data.appendleft(0)
```

핵심 차이는 저장 방식입니다. list는 하나의 연속 배열을 유지해야 하므로 앞에 빈칸을 만들려면 기존 참조를 전부 오른쪽으로 밀어야 합니다. 반면 deque는 양쪽 끝 연산을 위해 설계되어 그 비용을 피합니다.

## 단계별 실습

### 단계 1: list에서 원래 빠른 연산부터 확인하기

```python
numbers = [10, 20, 30, 40, 50]

print(numbers[2])  # 30   -- 인덱스 조회: O(1)

numbers.append(60)
print(numbers)     # [10, 20, 30, 40, 50, 60]

last = numbers.pop()
print(last)        # 60   -- 끝 pop: O(1)
```

### 단계 2: `sys.getsizeof()`로 overallocation 관찰하기

```python
import struct
import sys

pointer_size = struct.calcsize("P")
empty_list_size = sys.getsizeof([])

data = []
previous_size = sys.getsizeof(data)

print("len  bytes  approx_capacity")
for value in range(40):
    data.append(value)
    current_size = sys.getsizeof(data)
    if current_size != previous_size:
        approx_capacity = (current_size - empty_list_size) // pointer_size
        print(f"{len(data):>3}  {current_size:>5}  {approx_capacity:>15}")
        previous_size = current_size
```

64비트 CPython에서 볼 수 있는 예시 출력은 다음과 같습니다.

```text
len  bytes  approx_capacity
  1     88                4
  5    120                8
  9    184               16
 17    248               24
 25    312               32
 33    376               40
```

#### 이 결과를 읽는 법

- capacity는 `append()`마다 1씩 늘지 않고, 한동안 plateau를 유지하다가 점프합니다.
- 즉, 현재 길이보다 더 많은 슬롯을 미리 예약해 두는 구간이 존재합니다.
- 이것이 CPython list의 observable overallocation입니다. 지금 약간 더 크게 잡아 두어서 다음 몇 번의 append는 재할당 없이 처리합니다.

### 단계 3: 앞 삽입이 왜 비싼지 측정하기

```python
import time

size = 100_000
data = list(range(size))

start = time.perf_counter()
data.insert(0, -1)
front_insert = time.perf_counter() - start

start = time.perf_counter()
data.append(-1)
end_append = time.perf_counter() - start

print(f"front insert: {front_insert:.6f}s")
print(f"end append : {end_append:.6f}s")
print(f"front insert is {front_insert / max(end_append, 1e-9):.0f}x slower")
```

#### 이 결과를 읽는 법

중요한 것은 Big-O 표기가 아니라 실제 원인입니다. `insert(0, x)`는 맨 앞에 빈칸을 만들기 위해 기존 참조를 한 칸씩 모두 밀어야 합니다. 반면 `append(x)`는 이미 확보해 둔 spare slot에 쓰기만 하면 되는 경우가 많아서 훨씬 싸게 끝납니다.

### 단계 4: slicing도 결국 복사라는 점 기억하기

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(data[2:5])   # [2, 3, 4]
print(data[::2])   # [0, 2, 4, 6, 8]
print(data[::-1])  # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

슬라이싱은 문법이 가벼워 보여도 실제로는 새 list를 만들어 참조를 복사합니다. 그래서 비용은 slice 길이에 비례합니다.

### 단계 5: `array`는 기본값이 아니라 특수 도구로 보기

```python
from array import array

int_array = array("i", [1, 2, 3, 4, 5])
print(int_array[0])  # 1

mixed = [1, "hello", 3.14, True]
print(mixed)
```

`array`는 원소 타입이 하나로 고정되고 메모리 밀도가 중요할 때 의미가 있습니다. 일반적인 Python 애플리케이션 코드에서는 다양한 객체를 자연스럽게 담는 list가 여전히 기본 선택지입니다.

## 이 코드에서 먼저 봐야 할 점

- Python list는 연결 리스트가 아니라 동적 배열입니다.
- capacity 증가는 메모리 크기 plateau와 jump로 실제 관찰할 수 있습니다.
- `append()`가 평균적으로 빠른 이유는 CPython이 spare slot을 미리 확보하기 때문입니다.
- 앞 삽입이 느린 이유는 contiguous storage를 유지하려고 기존 원소를 밀어야 하기 때문입니다.
- slicing은 편하지만 복사 비용이 있는 연산입니다.

이렇게 보면 list 성능은 더 이상 “그냥 그런가 보다”가 아닙니다. spare capacity가 실제로 보이고, 재할당 시점도 보이고, 느린 연산이 왜 느린지도 저장 모델로 설명할 수 있게 됩니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 루프 안에서 `list.insert(0, x)` 반복 | 사실상 O(n²)이 되어 데이터가 커지면 급격히 느려집니다 | 앞 삽입이 많으면 `deque.appendleft()`를 사용합니다 |
| `b = a`로 list 복사 | 두 변수가 같은 객체를 가리켜 한쪽 변경이 다른 쪽에 반영됩니다 | `a[:]` 또는 `a.copy()`로 복사합니다 |
| `[[]] * 3`으로 중첩 list 초기화 | 모든 내부 list가 같은 객체를 참조합니다 | `[[] for _ in range(3)]`를 사용합니다 |
| 순회 중 list 수정 | 인덱스가 밀려 의도하지 않은 결과가 나옵니다 | 새 list를 만들거나 역순 순회를 사용합니다 |
| slicing을 공짜라고 생각 | 새 list를 만들어 참조를 복사합니다 | 순차 접근만 필요하면 iterator도 검토합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답의 JSON 배열은 대부분 list로 다뤄집니다.
- 배치 파이프라인은 다음 단계로 넘기기 전 데이터를 list에 모으는 경우가 많습니다.
- `heapq`는 힙 원소를 결국 list 안에 저장합니다.
- 페이지네이션과 window 처리에서는 slicing을 자주 쓰지만 복사 비용을 같이 의식해야 합니다.
- 대규모 수치 연산은 layout과 타입 제약이 분명해지는 시점에 NumPy 배열로 넘어갑니다.

## 실무에서는 이렇게 생각합니다

대부분의 상황에서 list는 충분히 빠릅니다. 중요한 것은 list의 강점 구간 안에서 쓰고 있는지 아는 것입니다. 끝 append/pop, 인덱스 접근, 순차 순회가 많다면 list는 아주 좋은 기본값입니다.

설계 질문은 단순합니다. “이 컬렉션에서 가장 자주 하는 연산이 무엇인가?” 끝 중심이면 list, 양쪽 끝이면 deque, 키 기반 membership이 핵심이면 set이나 dict로 넘어가야 합니다.

## 체크리스트

- [ ] Python `list`가 동적 배열이라는 점을 설명할 수 있다
- [ ] 논리 길이와 예약 capacity 차이를 설명할 수 있다
- [ ] `append()` 성능을 overallocation과 연결해 설명할 수 있다
- [ ] `insert(0, x)`가 왜 원소 이동을 일으키는지 설명할 수 있다
- [ ] `array`가 list보다 유리한 제한적 상황을 설명할 수 있다

## 연습 문제

1. capacity 관찰 스크립트를 1,000번 append까지 늘려서 capacity가 바뀌는 시점을 모두 기록해 보세요.
2. 큰 list에서 `insert(0, x)` 1,000번과 `deque.appendleft(x)` 1,000번을 비교해 보세요.
3. 중복 제거를 하되 원래 순서를 유지하는 함수를 작성하고, 왜 출력에는 여전히 list가 필요한지 설명해 보세요.

## 정리 및 다음 글 안내

Python `list`는 논리 길이와 예약 capacity를 분리해 관리하는 동적 배열입니다. 그래서 인덱스 접근은 O(1), `append()`는 평균적으로 O(1), 앞 삽입은 원소 이동 때문에 비쌉니다. 다음 글에서는 이 저장 모델 위에 자주 구현되는 스택과 큐를 봅니다.


## 타입 힌트 기반 동적 배열 구현

Python의 list 내부를 이해하는 가장 좋은 방법은 직접 간소화된 동적 배열을 만들어 보는 것입니다. 아래 구현은 CPython의 overallocation 전략을 흉내 내면서, 타입 힌트로 API 계약을 드러냅니다.

```python
from __future__ import annotations

import ctypes
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class DynamicArray(Generic[T]):
    """CPython list의 핵심 동작을 흉내 낸 동적 배열입니다."""

    def __init__(self) -> None:
        self._logical_size: int = 0
        self._capacity: int = 4
        self._array: ctypes.Array[ctypes.py_object] = self._make_array(self._capacity)

    @staticmethod
    def _make_array(capacity: int) -> ctypes.Array[ctypes.py_object]:
        return (capacity * ctypes.py_object)()

    def __len__(self) -> int:
        return self._logical_size

    def __getitem__(self, index: int) -> T:
        if index < 0:
            index += self._logical_size
        if not 0 <= index < self._logical_size:
            raise IndexError(f"index {index} out of range")
        return self._array[index]

    def __setitem__(self, index: int, value: T) -> None:
        if index < 0:
            index += self._logical_size
        if not 0 <= index < self._logical_size:
            raise IndexError(f"index {index} out of range")
        self._array[index] = value

    def append(self, value: T) -> None:
        if self._logical_size == self._capacity:
            self._resize(self._capacity + (self._capacity >> 3) + 6)
        self._array[self._logical_size] = value
        self._logical_size += 1

    def insert(self, index: int, value: T) -> None:
        if index < 0:
            index += self._logical_size
        index = max(0, min(index, self._logical_size))
        if self._logical_size == self._capacity:
            self._resize(self._capacity + (self._capacity >> 3) + 6)
        for i in range(self._logical_size, index, -1):
            self._array[i] = self._array[i - 1]
        self._array[index] = value
        self._logical_size += 1

    def pop(self, index: int = -1) -> T:
        if self._logical_size == 0:
            raise IndexError("pop from empty array")
        if index < 0:
            index += self._logical_size
        if not 0 <= index < self._logical_size:
            raise IndexError(f"index {index} out of range")
        value = self._array[index]
        for i in range(index, self._logical_size - 1):
            self._array[i] = self._array[i + 1]
        self._logical_size -= 1
        return value

    def _resize(self, new_capacity: int) -> None:
        new_array = self._make_array(new_capacity)
        for i in range(self._logical_size):
            new_array[i] = self._array[i]
        self._array = new_array
        self._capacity = new_capacity

    @property
    def capacity(self) -> int:
        return self._capacity

    def __iter__(self) -> Iterator[T]:
        for i in range(self._logical_size):
            yield self._array[i]

    def __repr__(self) -> str:
        items = ", ".join(repr(self._array[i]) for i in range(self._logical_size))
        return f"DynamicArray([{items}])"
```

### 구현에서 주목할 세 가지

1. **`_resize` 전략**: `capacity + (capacity >> 3) + 6`은 CPython 3.12의 실제 공식과 유사합니다. 단순히 2배로 늘리지 않고, 큰 배열일수록 증가폭을 억제해 메모리 낭비를 줄입니다.
2. **`insert`의 O(n) 루프**: 삽입 지점 이후의 모든 원소를 뒤로 밀어야 합니다. 이 루프가 정확히 "앞 삽입이 비싼 이유"를 코드로 보여줍니다.
3. **음수 인덱스 처리**: Python list의 관례를 따라 `-1`은 마지막 원소를 가리킵니다. 이 변환을 빠뜨리면 API 호환성이 깨집니다.

## 메모리 프로파일링: list vs array vs DynamicArray

자료구조를 선택할 때 시간 복잡도만 보면 절반만 보는 것입니다. 메모리 사용량도 중요한 판단 기준입니다.

```python
import sys
from array import array


def measure_memory(label: str, obj: object) -> None:
    size = sys.getsizeof(obj)
    print(f"{label:>20}: {size:>8} bytes")


n = 10_000
py_list = list(range(n))
int_array = array("i", range(n))

measure_memory("list[int] (10k)", py_list)
measure_memory("array('i') (10k)", int_array)
```

예상 출력 (64-bit CPython 3.12):

```text
     list[int] (10k):    85176 bytes
   array('i') (10k):    40064 bytes
```

list는 각 원소에 대한 포인터(8바이트)를 저장하고, 원소 자체는 별도의 `int` 객체(28바이트)입니다. 반면 `array('i')`는 원소를 C의 `int`(4바이트)로 직접 저장합니다. 이 차이가 10,000개일 때 약 2배, 100만 개일 때는 훨씬 더 벌어집니다.

### 깊은 크기 측정: 포인터만이 아니라 객체까지

`sys.getsizeof()`는 컨테이너의 "얕은" 크기만 반환합니다. list 안에 들어 있는 각 int 객체의 크기는 포함하지 않습니다. 진짜 메모리 비용을 알려면 재귀적으로 측정해야 합니다.

```python
import sys
from typing import Any


def deep_getsizeof(obj: Any, seen: set[int] | None = None) -> int:
    """객체와 그 참조 대상의 총 메모리 사용량을 재귀 측정합니다."""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_getsizeof(item, seen) for item in obj)
    return size


n = 10_000
py_list = list(range(n))
shallow = sys.getsizeof(py_list)
deep = deep_getsizeof(py_list)

print(f"list shallow: {shallow:>10} bytes")
print(f"list deep:    {deep:>10} bytes")
print(f"overhead per element: {(deep - shallow) / n:.1f} bytes")
```

이 결과는 list가 "보기보다 훨씬 많은 메모리를 쓴다"는 것을 숫자로 보여줍니다. 대규모 데이터를 다룰 때 `array`나 NumPy로 전환하는 이유가 바로 이 overhead입니다.

## 성능 벤치마크: timeit으로 연산별 비용 측정

단일 `time.perf_counter()` 측정은 노이즈가 많습니다. `timeit`은 여러 번 반복해 안정적 수치를 제공합니다.

```python
import timeit
from collections import deque


def bench_append_list(n: int = 100_000) -> None:
    data: list[int] = []
    for i in range(n):
        data.append(i)


def bench_append_deque(n: int = 100_000) -> None:
    data: deque[int] = deque()
    for i in range(n):
        data.append(i)


def bench_front_insert_list(n: int = 10_000) -> None:
    data: list[int] = []
    for i in range(n):
        data.insert(0, i)


def bench_front_insert_deque(n: int = 10_000) -> None:
    data: deque[int] = deque()
    for i in range(n):
        data.appendleft(i)


trials = 5

t1 = timeit.timeit(bench_append_list, number=trials)
t2 = timeit.timeit(bench_append_deque, number=trials)
t3 = timeit.timeit(bench_front_insert_list, number=trials)
t4 = timeit.timeit(bench_front_insert_deque, number=trials)

print(f"append list (100k x{trials}):          {t1:.4f}s")
print(f"append deque (100k x{trials}):         {t2:.4f}s")
print(f"front insert list (10k x{trials}):     {t3:.4f}s")
print(f"front insert deque (10k x{trials}):    {t4:.4f}s")
print(f"front insert: list/deque = {t3/t4:.1f}x")
```

예상 결과:

```text
append list (100k x5):          0.0312s
append deque (100k x5):         0.0298s
front insert list (10k x5):     0.8721s
front insert deque (10k x5):    0.0034s
front insert: list/deque = 256.5x
```

끝 append에서는 list와 deque가 거의 동일합니다. 하지만 앞 삽입에서는 200배 이상 차이가 납니다. 이 숫자가 "어디서 deque를 써야 하는가"에 대한 명확한 답을 줍니다.

## unittest로 DynamicArray 동작 검증

직접 만든 자료구조는 반드시 테스트로 계약을 고정해야 합니다.

```python
import unittest


class TestDynamicArray(unittest.TestCase):
    def setUp(self) -> None:
        self.arr: DynamicArray[int] = DynamicArray()

    def test_append_and_len(self) -> None:
        for i in range(100):
            self.arr.append(i)
        self.assertEqual(len(self.arr), 100)

    def test_getitem(self) -> None:
        for i in range(10):
            self.arr.append(i * 10)
        self.assertEqual(self.arr[0], 0)
        self.assertEqual(self.arr[9], 90)
        self.assertEqual(self.arr[-1], 90)

    def test_setitem(self) -> None:
        self.arr.append(1)
        self.arr[0] = 42
        self.assertEqual(self.arr[0], 42)

    def test_insert_front(self) -> None:
        for i in range(5):
            self.arr.append(i)
        self.arr.insert(0, 99)
        self.assertEqual(self.arr[0], 99)
        self.assertEqual(len(self.arr), 6)

    def test_pop_last(self) -> None:
        self.arr.append(10)
        self.arr.append(20)
        value = self.arr.pop()
        self.assertEqual(value, 20)
        self.assertEqual(len(self.arr), 1)

    def test_pop_middle(self) -> None:
        for i in range(5):
            self.arr.append(i)
        value = self.arr.pop(2)
        self.assertEqual(value, 2)
        self.assertEqual(list(self.arr), [0, 1, 3, 4])

    def test_capacity_grows(self) -> None:
        initial_cap = self.arr.capacity
        for i in range(initial_cap + 1):
            self.arr.append(i)
        self.assertGreater(self.arr.capacity, initial_cap)

    def test_index_error(self) -> None:
        with self.assertRaises(IndexError):
            _ = self.arr[0]
        with self.assertRaises(IndexError):
            self.arr.pop()


if __name__ == "__main__":
    unittest.main()
```

이 테스트가 검증하는 경계 조건은 다섯 가지입니다.

1. **기본 계약**: append 후 길이가 정확히 증가하는지 확인합니다.
2. **인덱싱**: 양수·음수 인덱스 모두 올바른 값을 반환하는지 확인합니다.
3. **삽입 후 순서**: 중간·앞 삽입 후 기존 원소가 밀려나는지 확인합니다.
4. **capacity 성장**: 논리 길이가 capacity를 초과하면 재할당이 일어나는지 확인합니다.
5. **예외 경계**: 빈 배열에서 접근·삭제 시 `IndexError`가 발생하는지 확인합니다.

## list 컴프리헨션과 제너레이터의 메모리 차이

실무에서 list를 만들 때 컴프리헨션을 자주 씁니다. 하지만 결과를 한꺼번에 메모리에 올린다는 점을 잊기 쉽습니다.

```python
import sys

# 컴프리헨션: 전체를 메모리에 적재
squares_list = [x * x for x in range(1_000_000)]
print(f"list comprehension: {sys.getsizeof(squares_list):>10} bytes")

# 제너레이터: 하나씩 생산, 전체를 저장하지 않음
squares_gen = (x * x for x in range(1_000_000))
print(f"generator expr:     {sys.getsizeof(squares_gen):>10} bytes")
```

결과는 약 8MB vs 200바이트입니다. 전체 결과가 필요 없고 순차 처리만 하면 되는 경우, 제너레이터로 바꾸면 메모리를 극적으로 줄일 수 있습니다. 반대로 인덱스 접근이나 길이 확인이 필요하면 list로 실체화해야 합니다. 이 판단이 "list를 언제 쓰는가"의 또 다른 축입니다.

## sorted()와 list.sort()의 차이

정렬은 list에서 가장 자주 하는 연산 중 하나입니다. 두 가지 방법의 차이를 명확히 해두면 실수를 줄일 수 있습니다.

```python
original = [3, 1, 4, 1, 5, 9, 2, 6]

# sorted(): 새 list를 반환, 원본 불변
new_sorted = sorted(original)
print(f"original:   {original}")
print(f"new_sorted: {new_sorted}")

# list.sort(): 제자리 정렬, None 반환
result = original.sort()
print(f"after sort: {original}")
print(f"result:     {result}")  # None
```

`sorted()`는 원본을 보존해야 할 때, `.sort()`는 추가 메모리 없이 제자리 정렬이 필요할 때 사용합니다. 실수가 잦은 패턴은 `x = original.sort()`인데, 이 경우 `x`는 `None`이 됩니다.

CPython의 정렬 알고리즘은 Timsort(합병 정렬 + 삽입 정렬 혼합)로, 이미 정렬된 부분 배열이 많을수록 더 빠르게 동작합니다. 최선의 경우 O(n), 최악의 경우 O(n log n)입니다.

## 처음 질문으로 돌아가기

- **Python의 `list`는 배열일까요, 연결 리스트일까요?**
  - 동적 배열입니다. 내부적으로 연속된 메모리 블록에 객체 포인터를 저장하므로, 인덱스 접근이 O(1)입니다. 연결 리스트라면 인덱스 접근이 O(n)이 되어야 하지만, 실측에서 list[500000]이 list[0]과 동일한 속도로 접근되는 것이 이를 증명합니다.
- **`append()`는 list가 계속 커져도 왜 대체로 빠를까요?**
  - CPython이 overallocation 전략을 사용하기 때문입니다. 현재 길이보다 더 많은 spare slot을 미리 확보해 두어, 대부분의 append는 이미 준비된 빈 슬롯에 포인터를 쓰기만 하면 됩니다. capacity를 초과할 때만 재할당이 일어나고, 그 비용을 전체 append 횟수로 나누면 amortized O(1)이 됩니다.
- **`insert(0, x)`와 중간 삭제는 왜 비쌀까요?**
  - 연속 배열이므로 삽입 지점 이후의 모든 포인터를 한 칸씩 밀어야(또는 당겨야) 합니다. 원소 수에 비례하는 복사가 발생하므로 O(n)입니다. DynamicArray의 insert 메서드에서 for 루프가 정확히 이 비용을 보여줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
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
- [Python 공식 문서 — `sys.getsizeof`](https://docs.python.org/3/library/sys.html#sys.getsizeof)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [CPython list implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Real Python — Python Lists and Tuples](https://realpython.com/python-lists-tuples/)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)

Tags: Python, 자료구조, list, array, 시간 복잡도
