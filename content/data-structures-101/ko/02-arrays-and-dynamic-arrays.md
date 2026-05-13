---
series: data-structures-101
episode: 2
title: 배열과 동적 배열
status: publish-ready
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
seo_description: 배열과 동적 배열의 차이, 파이썬 list의 내부 동작을 설명합니다.
last_reviewed: '2026-05-12'
---

# 배열과 동적 배열

이 글은 Data Structures 101 시리즈의 두 번째 글입니다.

## 이 글에서 다룰 문제

- 고정 배열은 왜 인덱싱이 O(1)일까요?
- 동적 배열은 공간이 모자랄 때 어떻게 늘어나고, 왜 append가 평균적으로 빠를까요?
- 파이썬의 `list`는 내부적으로 어떤 자료구조에 가까울까요?
- 배열이 빠른 상황과 피해야 할 상황은 어떻게 구분할까요?

파이썬 리스트에 `append`를 백만 번 호출해도 꽤 빠르게 끝납니다. 겉으로 보면 매번 메모리를 다시 잡아야 할 것 같지만, 실제 구현은 그렇게 단순하게 동작하지 않습니다.

> 배열은 같은 타입의 원소를 메모리에 연속해서 저장하는 구조입니다. 그래서 인덱싱은 시작 주소에 오프셋을 더하는 계산만으로 끝나며 O(1)입니다. 동적 배열은 여기에 재할당 전략을 추가해, 공간이 다 찼을 때 더 큰 블록을 새로 만들고 기존 원소를 복사함으로써 크기 제한을 우회합니다.

## 왜 중요한가

배열은 가장 기본적이면서도 가장 빠른 자료구조 중 하나입니다. CPU 캐시와 궁합이 좋고, 인덱싱은 O(1)이며, 해시 테이블·힙·동적 배열 같은 구조도 내부적으로는 배열 위에 세워집니다.

> 배열을 깊이 이해하지 못하면 다른 자료구조도 끝까지 깊게 이해하기 어렵습니다.

이 글에서는 “값을 여러 개 담는 컨테이너” 수준에서 멈추지 않고, 메모리 배치·재할당·캐시 친화성까지 함께 봅니다.

## 핵심 한눈에 보기

> 배열은 메모리의 연속 구간입니다. `arr[i]`는 시작 주소 + `i × 원소 크기`로 계산하므로 O(1)입니다. 동적 배열은 capacity가 부족해지면 보통 두 배 큰 블록을 새로 할당하고 기존 값을 복사합니다.

```text
Fixed array (size = 5)
addr: 100 104 108 112 116
val:  [10][20][30][40][50]
       ↑
  arr[2] = 100 + 2*4 = 108

Dynamic array (size = 3, capacity = 4)
val:  [10][20][30][ - ]   one slot free
append(40) → [10][20][30][40]   capacity full
append(50) → new block (capacity 8) → [10][20][30][40][50][ ][ ][ ]
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 고정 배열 | 생성 시 크기가 고정되는 배열 |
| 동적 배열 | 필요할 때 크기를 늘릴 수 있는 배열 |
| 용량(capacity) | 현재 확보된 최대 저장 공간 |
| 재할당(reallocation) | 더 큰 블록을 새로 잡고 원소를 복사하는 과정 |
| 분할 상환 비용 | 여러 번의 연산 전체를 평균냈을 때의 비용 |

## Before / After

**Before — building a list with `+`:**

```python
result = []
for i in range(1_000_000):
    result = result + [i]   # O(n) copy each time → O(n^2) overall
```

**After — using append:**

```python
result = []
for i in range(1_000_000):
    result.append(i)        # amortized O(1) → O(n) overall
```

겉보기에는 비슷해도 비용 구조는 완전히 다릅니다. 실무에서는 이런 차이가 수백 배에서 수천 배까지 벌어집니다.

## 단계별로 따라하기

### 1단계: 인덱싱은 정말 O(1)일까

```python
import time

data = list(range(10_000_000))

start = time.perf_counter()
_ = data[0]
print(f"data[0]:        {(time.perf_counter() - start) * 1e6:.2f} us")

start = time.perf_counter()
_ = data[5_000_000]
print(f"data[5_000_000]: {(time.perf_counter() - start) * 1e6:.2f} us")

start = time.perf_counter()
_ = data[9_999_999]
print(f"data[-1]:        {(time.perf_counter() - start) * 1e6:.2f} us")
```

세 위치 모두 비슷한 시간이 나옵니다. 배열 인덱싱은 스캔이 아니라 주소 계산이기 때문입니다.

### 2단계: 동적 배열 확장을 직접 구현해 보기

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

capacity가 1, 2, 4, 8, 16처럼 증가하는 모습을 볼 수 있습니다. 이 doubling 전략이 append의 평균 비용을 낮게 유지하는 핵심입니다.

### 3단계: 분할 상환 비용 이해하기

```python
# Count the total copies during n appends
copies = 0
size = 0
capacity = 1

for _ in range(1024):
    if size == capacity:
        copies += size       # copy old elements to the new block
        capacity *= 2
    size += 1

print(f"total appends: {size}, total copies: {copies}")
print(f"average: {copies / size:.2f}")
```

평균 복사 횟수는 1보다 작습니다. 대부분의 append는 빈 슬롯에 값을 쓰기만 하고, 가끔만 비싼 resize를 치릅니다.

### 4단계: 중간과 앞쪽 삽입은 왜 비쌀까

```python
import time

data = list(range(100_000))

start = time.perf_counter()
data.append(-1)              # append at the end: O(1)
print(f"append: {(time.perf_counter() - start) * 1e6:.2f} us")

data = list(range(100_000))
start = time.perf_counter()
data.insert(0, -1)           # insert at the front: O(n)
print(f"insert(0): {(time.perf_counter() - start) * 1e6:.2f} us")
```

앞에 삽입하면 뒤 원소를 전부 한 칸씩 밀어야 합니다. 이런 패턴이 핵심이라면 연결 리스트나 deque가 더 잘 맞습니다.

### 5단계: 캐시 친화성

```python
import time

# Sum the same one million integers
list_data = list(range(1_000_000))

start = time.perf_counter()
total = 0
for x in list_data:
    total += x
print(f"list iteration: {(time.perf_counter() - start) * 1000:.2f} ms")

# Compare with a dict — slower
dict_data = {i: i for i in range(1_000_000)}

start = time.perf_counter()
total = 0
for v in dict_data.values():
    total += v
print(f"dict iteration: {(time.perf_counter() - start) * 1000:.2f} ms")
```

연속 메모리는 CPU 캐시 라인에 잘 실립니다. 그래서 원소 수가 같아도 list 순회가 dict보다 유리한 경우가 많습니다.

## 이 코드에서 주목할 점

- 인덱싱은 주소 계산이므로 위치와 무관하게 O(1)입니다.
- doubling 전략 덕분에 append의 분할 상환 비용이 O(1)로 유지됩니다.
- 중간이나 앞쪽 삽입은 구조적으로 O(n)입니다.
- 연속 메모리는 캐시 친화적이라 실제 벤치마크에서도 강합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `+`로 리스트를 반복 확장함 | O(n^2) 복사 폭발 | `append`나 컴프리헨션을 사용합니다 |
| 앞쪽 삽입을 자주 함 | 매번 O(n) 이동 발생 | `collections.deque`를 사용합니다 |
| capacity와 size를 혼동함 | 메모리 추정이 틀어짐 | size는 사용량, capacity는 확보량으로 구분합니다 |
| 큰 슬라이스를 반복 생성함 | 메모리와 시간이 낭비됨 | 가능하면 슬라이스 대신 인덱스를 씁니다 |
| 정렬된 리스트를 선형 탐색함 | O(log n) 기회를 버림 | `bisect`를 검토합니다 |

## 실무에서는 이렇게 쓰입니다

- NumPy `ndarray`는 C 레벨의 배열 모델로 수치 계산을 가속합니다.
- Pandas 열(column)은 내부적으로 연속 배열 기반입니다.
- 파일 I/O 버퍼, 네트워크 패킷, 이미지 픽셀 데이터는 모두 배열적 성격이 강합니다.
- 게임 엔진의 ECS는 캐시 친화성을 위해 배열을 적극 활용합니다.
- 컬럼형 데이터베이스는 정렬된 배열처럼 스캔하고 압축합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 “list”와 “array”를 같은 말로 뭉뚱그리지 않습니다. 파이썬의 `list`는 동적 배열 계열이지만, 다른 언어의 컬렉션은 전혀 다른 의미를 가질 수 있기 때문입니다. `ArrayList`, `std::vector`, `Vec`는 한 가족이지만 `LinkedList`는 성격이 완전히 다릅니다.

또한 최종 크기를 안다면 capacity를 미리 확보합니다. `[None] * n`처럼 한 번에 메모리를 잡으면 재할당 비용을 모두 제거할 수 있습니다. 작은 차이처럼 보여도 핫패스에서는 체감 성능 차이가 분명합니다.

## 체크리스트

- [ ] 배열 인덱싱이 왜 O(1)인지 메모리 배치로 설명할 수 있습니다
- [ ] doubling과 분할 상환 비용의 관계를 이해했습니다
- [ ] capacity와 size를 구분할 수 있습니다
- [ ] 앞쪽 삽입이 왜 비싼지 알고 있습니다
- [ ] 캐시 친화성이 성능에 미치는 영향을 이해했습니다

## 연습 문제

1. 위 `DynamicArray`에 `pop()`과 `__delitem__()`을 추가해 보세요. size가 capacity의 1/4 아래로 떨어지면 절반으로 줄이는 축소 전략도 함께 넣어 보세요.

2. 백만 번 `append`하는 방식과 `[None] * 1_000_000`으로 미리 할당한 뒤 인덱스로 쓰는 방식을 비교해 보세요. 차이는 얼마나 날까요?

3. 정렬된 리스트에서 `bisect.insort`의 시간 복잡도는 무엇일까요? 검색은 O(log n)인데 삽입은 왜 그렇지 않을까요?

## 정리 및 다음 단계

배열은 같은 크기의 원소를 메모리에 연속 배치하는 구조라 인덱싱이 O(1)이고 캐시 친화적입니다. 동적 배열은 공간이 부족해질 때 capacity를 키워 끝 삽입의 분할 상환 비용을 O(1)로 유지합니다. 하지만 중간이나 앞쪽 삽입은 여전히 O(n)이므로, 그런 패턴이 지배적이라면 다음 글의 연결 리스트나 deque가 더 적합할 수 있습니다.

다음 글에서는 포인터로 이어진 노드 구조인 연결 리스트를 봅니다. 배열의 “비싼 중간 삽입” 문제를 어떻게 해결하고, 대신 무엇을 포기하는지 비교하겠습니다.

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

Tags: Computer Science, 자료구조, 배열, 동적 배열, 메모리, 파이썬 리스트
