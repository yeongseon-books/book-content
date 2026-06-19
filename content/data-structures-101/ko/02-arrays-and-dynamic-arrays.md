---
series: data-structures-101
episode: 2
title: "Data Structures 101 (2/10): 배열과 동적 배열"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
seo_description: 메모리 연속 배치와 인덱싱의 원리, 동적 배열의 확장 전략 및 분할 상환 비용 분석을 통해 배열 자료구조의 핵심을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (2/10): 배열과 동적 배열

> 배열은 메모리의 연속 구간입니다. `arr[i]`는 시작 주소 + `i × 원소 크기`로 계산하므로 O(1)입니다. 동적 배열은 capacity가 부족해지면 보통 두 배 큰 블록을 새로 할당하고 기존 값을 복사합니다.

이 글은 Data Structures 101 시리즈의 두 번째 글입니다.

![Data Structures 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/02/02-01-big-picture.ko.png)
*Data Structures 101 2장 흐름 개요*

## 이 글에서 다룰 문제

- 고정 배열은 왜 인덱싱이 O(1)일까요?
- 동적 배열은 공간이 모자랄 때 어떻게 늘어나고, 왜 append가 평균적으로 빠를까요?
- 파이썬의 `list`는 내부적으로 어떤 자료구조에 가까울까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

배열은 가장 기본적이면서도 가장 빠른 자료구조 중 하나입니다. CPU 캐시와 궁합이 좋고, 인덱싱은 O(1)이며, 해시 테이블·힙·동적 배열 같은 구조도 내부적으로는 배열 위에 세워집니다.

> 배열을 깊이 이해하지 못하면 다른 자료구조도 끝까지 깊게 이해하기 어렵습니다.

이 글에서는 "값을 여러 개 담는 컨테이너" 수준에서 멈추지 않고, 메모리 배치·재할당·캐시 친화성까지 함께 봅니다.

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

| 용어 | 의미 |
| --- | --- |
| 고정 배열 | 생성 시 크기가 고정되는 배열 |
| 동적 배열 | 필요할 때 크기를 늘릴 수 있는 배열 |
| 용량(capacity) | 현재 확보된 최대 저장 공간 |
| 재할당(reallocation) | 더 큰 블록을 새로 잡고 원소를 복사하는 과정 |
| 분할 상환 비용 | 여러 번의 연산 전체를 평균냈을 때의 비용 |

## 전후 비교

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

### 1단계: 인덱싱은 정말 상수 시간일까

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
# n번 append 동안 총 복사 횟수 계산
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

# 동일한 100만 개 정수 합계 계산
list_data = list(range(1_000_000))

start = time.perf_counter()
total = 0
for x in list_data:
    total += x
print(f"list iteration: {(time.perf_counter() - start) * 1000:.2f} ms")

# dict와 비교 — 더 느림
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

## 배열 vs 연결 리스트 비교

| 연산 | 고정 배열 | 동적 배열 | 연결 리스트 |
| --- | --- | --- | --- |
| 인덱스 접근 | O(1) | O(1) | O(n) |
| 끝 삽입 | 불가(크기 고정) | O(1) amortized | O(1) (tail 있을 때) |
| 앞 삽입 | O(n) | O(n) | O(1) |
| 중간 삽입 | O(n) | O(n) | O(1) (위치 알 때) |
| 메모리 | 연속, 낭비 없음 | 연속, 일부 여유 | 분산, 포인터 오버헤드 |
| 캐시 효율 | 우수 | 우수 | 불량 |

## 디버깅 시나리오

### 시나리오 1: 리스트 연결 연산으로 O(n²) 발생

```python
import time

N = 50_000

# 잘못된 패턴
start = time.perf_counter()
result = []
for i in range(N):
    result = result + [i]  # 매번 전체 복사 O(n)
print(f"concat loop: {time.perf_counter() - start:.2f}s")

# 올바른 패턴
start = time.perf_counter()
result = []
for i in range(N):
    result.append(i)  # O(1) amortized
print(f"append loop: {time.perf_counter() - start:.4f}s")

# 더 나은 패턴 — 컴프리헨션
start = time.perf_counter()
result = [i for i in range(N)]
print(f"comprehension: {time.perf_counter() - start:.4f}s")
```

### 시나리오 2: 슬라이싱이 반복 호출 경로에 있을 때

```python
# 문제: 슬라이스는 매번 새 리스트를 만듭니다
data = list(range(1_000_000))

# 나쁜 패턴 — O(n) 복사 반복
def process_bad(data, window=1000):
    results = []
    for i in range(0, len(data), window):
        chunk = data[i:i+window]  # 매번 O(window) 복사
        results.append(sum(chunk))
    return results

# 좋은 패턴 — 인덱스로 접근
def process_good(data, window=1000):
    results = []
    for i in range(0, len(data), window):
        total = sum(data[j] for j in range(i, min(i+window, len(data))))
        results.append(total)
    return results

# 더 나은 패턴 — memoryview 사용 (바이트 데이터의 경우)
import array
byte_data = array.array('i', range(1_000_000))

def process_view(data, window=1000):
    results = []
    view = memoryview(data)
    for i in range(0, len(data), window):
        chunk = view[i:i+window]
        results.append(sum(chunk))
    return results
```

### 시나리오 3: 미리 크기를 알 때 할당 최적화

```python
import time

N = 1_000_000

# append 방식
start = time.perf_counter()
result = []
for i in range(N):
    result.append(i * 2)
print(f"append: {time.perf_counter() - start:.4f}s, capacity growth: dynamic")

# 미리 할당 방식
start = time.perf_counter()
result = [None] * N
for i in range(N):
    result[i] = i * 2
print(f"pre-alloc: {time.perf_counter() - start:.4f}s, realloc count: 0")

# 최종 크기를 알 때는 pre-alloc이 항상 유리합니다
# resize 비용 0회, 메모리 복사 0회
```

## 자주 하는 실수

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

시니어 엔지니어는 "list"와 "array"를 같은 말로 뭉뚱그리지 않습니다. 파이썬의 `list`는 동적 배열 계열이지만, 다른 언어의 컬렉션은 전혀 다른 의미를 가질 수 있기 때문입니다. `ArrayList`, `std::vector`, `Vec`는 한 가족이지만 `LinkedList`는 성격이 완전히 다릅니다.

또한 최종 크기를 안다면 capacity를 미리 확보합니다. `[None] * n`처럼 한 번에 메모리를 잡으면 재할당 비용을 모두 제거할 수 있습니다. 배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다.

## 운영 체크리스트

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

다음 글에서는 포인터로 이어진 노드 구조인 연결 리스트를 봅니다. 배열의 "비싼 중간 삽입" 문제를 어떻게 해결하고, 대신 무엇을 포기하는지 비교하겠습니다.

## 처음 질문으로 돌아가기

- **고정 배열은 왜 인덱싱이 O(1)일까요?**
  - 배열은 같은 크기의 원소를 메모리에 연속 배치하기 때문입니다. `arr[i]`는 시작 주소 + `i × 원소 크기`로 바로 계산할 수 있어 주소 계산 한 번이면 됩니다.
- **동적 배열은 공간이 모자랄 때 어떻게 늘어나고, 왜 append가 평균적으로 빠를까요?**
  - capacity가 가득 차면 보통 두 배 큰 새 블록을 할당하고 기존 원소를 복사합니다. 이 비싼 연산이 드물게 일어나기 때문에 분할 상환 비용은 O(1)로 유지됩니다.
- **파이썬의 `list`는 내부적으로 어떤 자료구조에 가까울까요?**
  - 동적 배열입니다. CPython의 `listobject.c`에서 확인할 수 있으며, capacity와 size를 따로 관리하며 doubling 전략으로 재할당합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- **Data Structures 101 (2/10): 배열과 동적 배열 (현재 글)**
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- [Data Structures 101 (6/10): 트리](./06-trees.md)
- [Data Structures 101 (7/10): 이진 탐색 트리](./07-binary-search-trees.md)
- [Data Structures 101 (8/10): 힙](./08-heaps.md)
- [Data Structures 101 (9/10): 그래프](./09-graphs.md)
- [자료구조 선택 기준](./10-choosing-data-structures.md)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Chapter 2 Array-Based Lists](https://opendatastructures.org/ods-python/2_Array_Based_Lists.html)
- [CPython listobject.c source](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Wikipedia — Dynamic Array](https://en.wikipedia.org/wiki/Dynamic_array)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)

Tags: Computer Science, 자료구조, 배열, 동적 배열, 메모리, 파이썬 리스트
