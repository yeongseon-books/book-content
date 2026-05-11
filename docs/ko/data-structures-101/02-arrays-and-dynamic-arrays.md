---
series: data-structures-101
episode: 2
title: 배열과 동적 배열
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 자료구조
  - 배열
  - 동적 배열
  - 메모리
  - 파이썬 리스트
seo_description: 고정 크기 배열과 동적 배열의 차이, 파이썬 list의 내부 구조, 그리고 분할 상환 O(1)의 의미를 이해합니다.
last_reviewed: '2026-05-04'
---

# 배열과 동적 배열

> Data Structures 101 시리즈 (2/10)


## 이 글에서 다룰 문제

배열은 가장 기본이면서 가장 빠른 자료구조 중 하나입니다. CPU 캐시와 가장 잘 맞물리고, 인덱싱이 O(1)이며, 모든 고급 자료구조의 기반이 됩니다. 해시 테이블·동적 배열·힙은 모두 내부적으로 배열을 사용합니다.

> 배열을 모르면 다른 자료구조를 깊이 이해할 수 없습니다.

이 글에서는 단순한 "값들의 모음"을 넘어 메모리 레이아웃·재할당·캐시 친화성까지 함께 살펴봅니다.

## 전체 흐름
> 배열은 메모리상의 연속된 블록입니다. `arr[i]`는 시작 주소에 `i × 원소 크기`를 더해 즉시 위치를 계산하므로 O(1)입니다. 동적 배열은 capacity가 모자라면 보통 2배 크기로 새 메모리를 할당하고 기존 원소를 복사합니다.

```text
고정 배열 (size = 5)
주소: 100 104 108 112 116
값:  [10][20][30][40][50]
       ↑
  arr[2] = 100 + 2*4 = 108

동적 배열 (size = 3, capacity = 4)
값:  [10][20][30][ - ]   capacity 여유 1
append(40) → [10][20][30][40]   capacity 여유 0
append(50) → 새 블록(capacity 8)에 복사 → [10][20][30][40][50][ ][ ][ ]
```

## Before / After

**Before — 매번 새 리스트를 만들 때:**

```python
result = []
for i in range(1_000_000):
    result = result + [i]   # O(n) 복사를 매번 수행 → 전체 O(n^2)
```

**After — append를 사용할 때:**

```python
result = []
for i in range(1_000_000):
    result.append(i)        # 분할 상환 O(1) → 전체 O(n)
```

겉보기에는 비슷해 보이지만 시간 차이는 1,000배 이상입니다.

## 단계별로 따라하기

### 1단계: 인덱싱은 정말로 O(1)인가

```python
import time

data = list(range(10_000_000))

start = time.perf_counter()
_ = data[0]
print(f"data[0]:        {(time.perf_counter() - start) * 1e6:.2f} µs")

start = time.perf_counter()
_ = data[5_000_000]
print(f"data[5_000_000]: {(time.perf_counter() - start) * 1e6:.2f} µs")

start = time.perf_counter()
_ = data[9_999_999]
print(f"data[-1]:        {(time.perf_counter() - start) * 1e6:.2f} µs")
```

세 접근 모두 거의 같은 시간이 걸립니다. 인덱스에 곱셈과 덧셈만 있을 뿐 데이터를 훑지 않습니다.

### 2단계: 동적 배열의 확장 직접 구현

```python
class DynamicArray:
    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

    def append(self, value):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_cap

    def __getitem__(self, i):
        if not 0 <= i < self._size:
            raise IndexError(i)
        return self._data[i]

    def __len__(self):
        return self._size


arr = DynamicArray()
for i in range(10):
    arr.append(i)
    print(f"size={len(arr)}, capacity={arr._capacity}")
```

capacity가 1, 2, 4, 8, 16... 으로 두 배씩 늘어나는 것을 볼 수 있습니다. 두 배 확장 전략이 분할 상환 O(1)의 핵심입니다.

### 3단계: 분할 상환 비용 이해하기

```python
# n번의 append 동안 일어나는 총 복사 횟수를 세어 봅시다
copies = 0
size = 0
capacity = 1

for _ in range(1024):
    if size == capacity:
        copies += size       # 기존 원소를 새 블록으로 복사
        capacity *= 2
    size += 1

print(f"총 append: {size}, 총 복사: {copies}")
print(f"평균: {copies / size:.2f}")
```

평균 복사 횟수는 1 미만입니다. 가끔 비싼 재할당이 있지만 대부분의 append는 그냥 한 자리에 값을 쓰는 일뿐입니다.

### 4단계: 중간 삽입은 비싸다

```python
import time

data = list(range(100_000))

start = time.perf_counter()
data.append(-1)              # 끝에 추가: O(1)
print(f"append: {(time.perf_counter() - start) * 1e6:.2f} µs")

data = list(range(100_000))
start = time.perf_counter()
data.insert(0, -1)           # 맨 앞에 삽입: O(n)
print(f"insert(0): {(time.perf_counter() - start) * 1e6:.2f} µs")
```

맨 앞에 삽입하면 모든 원소를 한 칸씩 뒤로 밀어야 합니다. 이런 패턴이 자주 일어나면 연결 리스트나 deque를 고려해야 합니다.

### 5단계: 캐시 친화성

```python
import time

# 같은 100만 정수 합산
list_data = list(range(1_000_000))

start = time.perf_counter()
total = 0
for x in list_data:
    total += x
print(f"리스트 순회: {(time.perf_counter() - start) * 1000:.2f} ms")

# 비교: dict는 더 느림
dict_data = {i: i for i in range(1_000_000)}

start = time.perf_counter()
total = 0
for v in dict_data.values():
    total += v
print(f"dict 순회: {(time.perf_counter() - start) * 1000:.2f} ms")
```

연속된 메모리는 CPU 캐시 라인에 한 번에 올라옵니다. 같은 양의 데이터라도 배열이 dict보다 순회가 빠른 이유입니다.

## 이 코드에서 주목할 점

- 인덱싱은 메모리 주소 계산이라서 위치와 무관하게 O(1)입니다
- 두 배 확장 전략 덕분에 append의 분할 상환 비용이 O(1)입니다
- 중간/앞쪽 삽입은 O(n)이며 이는 동적 배열의 본질적 한계입니다
- 메모리가 연속이라서 캐시 친화적이고 실측 성능이 좋습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `+`로 리스트를 누적 | O(n^2) 복사 폭발 | `append` 또는 list comprehension 사용 |
| 맨 앞에 자주 insert | 매번 O(n) 이동 | `collections.deque` 사용 |
| capacity와 size 혼동 | 메모리 사용량 잘못 추정 | 사용량 = size, 할당량 = capacity |
| 큰 리스트를 매번 복사 | 메모리/시간 낭비 | 슬라이싱 대신 인덱스로 참조 |
| 정렬된 리스트에서 검색 | 선형 검색 사용 | `bisect` 모듈로 이진 검색 |

## 실무에서는 이렇게 쓰입니다

- NumPy의 ndarray는 고정 크기 배열을 C 수준에서 다뤄 수치 계산을 가속합니다
- 데이터프레임(pandas)의 컬럼은 내부적으로 연속 배열로 저장됩니다
- 파일 I/O 버퍼, 네트워크 패킷, 이미지 픽셀 데이터는 모두 배열로 표현됩니다
- 게임 엔진의 엔티티 컴포넌트 시스템(ECS)은 캐시 친화성을 위해 배열을 사용합니다
- 데이터베이스의 정렬된 컬럼 스토어는 배열 기반 압축으로 빠른 스캔을 제공합니다

## 체크리스트

- [ ] 배열의 인덱싱이 왜 O(1)인지 메모리 레이아웃으로 설명할 수 있는가
- [ ] 동적 배열의 두 배 확장 전략과 분할 상환의 관계를 이해했는가
- [ ] capacity와 size의 차이를 구분할 수 있는가
- [ ] 맨 앞 삽입이 비싼 이유를 알고 있는가
- [ ] 캐시 친화성이 성능에 영향을 미치는 이유를 이해했는가

## 정리 및 다음 단계

배열은 같은 크기의 원소를 메모리에 연속 배치한 자료구조이며, 인덱싱이 O(1)이고 캐시 친화적이라는 장점이 있습니다. 동적 배열은 capacity가 모자라면 두 배로 확장하는 전략으로 끝쪽 삽입의 분할 상환 비용을 O(1)로 유지합니다. 다만 중간/앞쪽 삽입은 여전히 O(n)이며, 이런 워크로드라면 다음 글의 연결 리스트가 더 적합할 수 있습니다.

다음 글에서는 포인터로 노드를 이어 붙이는 연결 리스트를 살펴봅니다. 배열의 한계인 "중간 삽입의 비용"을 어떻게 해결하는지, 대신 무엇을 잃는지 비교합니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- **배열과 동적 배열 (현재 글)**
- 연결 리스트 (예정)
- 스택과 큐 (예정)
- 해시 테이블 (예정)
- 트리 (예정)
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Chapter 2 Array-Based Lists](https://opendatastructures.org/ods-python/2_Array_Based_Lists.html)
- [CPython listobject.c source](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Wikipedia — Dynamic Array](https://en.wikipedia.org/wiki/Dynamic_array)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)
