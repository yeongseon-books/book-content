---
series: data-structures-python-101
episode: 10
title: "Data Structures with Python 101 (10/10): 자료구조 선택 기준"
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
  - 시간 복잡도
  - 성능 최적화
  - 자료구조 비교
seo_description: 데이터 특성과 연산 빈도에 따른 Python 자료구조 선택 기준을 정리합니다. 시간 복잡도 비교, 벤치마크, 복합 구조 활용 패턴을 익힙니다.
last_reviewed: '2026-05-15'
---

# Data Structures with Python 101 (10/10): 자료구조 선택 기준

이 글은 Data Structures with Python 101 시리즈의 마지막 글입니다.


![Data Structures with Python 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/10/10-01-decision-flow-at-a-glance.ko.png)
*Data Structures with Python 101 10장 흐름 개요*

## 먼저 던지는 질문

- list, dict, set 중 무엇을 선택해야 할지 어떤 기준으로 판단할까요?
- 자료구조 선택에서 가장 먼저 봐야 할 연산은 무엇일까요?
- 여러 구조를 조합해 요구사항을 동시에 만족시키는 방법은 무엇일까요?

## 왜 이 글이 중요한가

개별 자료구조의 특성을 아는 것과, 상황에 맞는 구조를 고르는 것은 전혀 다른 능력입니다. 잘못된 자료구조를 선택하면 코드가 불필요하게 복잡해지고, 성능도 예측하기 어려워집니다. 반대로 올바른 구조를 고르면 코드와 성능이 동시에 단순해집니다.

> “어떤 자료구조를 써야 하나?”에 답하려면 먼저 “어떤 연산을 가장 자주 하는가?”를 물어야 합니다.

면접에서도 구현 능력보다 선택 이유를 더 중요하게 보는 경우가 많습니다. 실무에서도 마찬가지입니다. 병목이 생긴 뒤에 구조를 바꾸는 것보다, 처음부터 핵심 연산을 기준으로 설계하는 편이 훨씬 싸게 먹힙니다.

## 핵심 개념 한눈에 보기

> 자료구조 선택 = 데이터 특성과 연산 빈도를 함께 보는 설계 판단

```text
Frequent lookups?
  +-- Key-value mapping? -> dict
  +-- Existence only? -> set

Order matters?
  +-- Append/remove from end only? -> list (stack)
  +-- Both ends? -> deque (queue)
  +-- Mid-list insert/delete? -> consider linked lists

Need priority? -> heapq

Hierarchical structure? -> tree
Relationship network? -> graph
```

## 선택 흐름을 그림으로 보면

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 시간 복잡도 | 데이터가 커질 때 연산 시간이 얼마나 증가하는지 나타내는 기준입니다 |
| 공간 복잡도 | 자료구조가 사용하는 메모리 양입니다 |
| 트레이드오프 | 한 연산을 빠르게 만들면 다른 연산이 느려질 수 있다는 뜻입니다 |
| 프로파일링 | 실제 코드에서 병목이 어디인지 측정하는 작업입니다 |
| 벤치마킹 | 여러 구현이나 구조의 성능을 비교하는 실험입니다 |

## 적용 전후 비교
자료구조를 습관적으로 고르는 경우와 의도적으로 고르는 경우를 비교해 보겠습니다.

```python
# before: 모든 곳에 list 사용 — 비효율적
seen = []
for item in data:
    if item not in seen:  # O(n) lookup
        seen.append(item)
        process(item)
```

```python
# after: 올바른 data structure 선택 — 효율적
seen = set()
for item in data:
    if item not in seen:  # O(1) lookup
        seen.add(item)
        process(item)
```

기능만 보면 두 코드는 거의 같습니다. 하지만 연산 빈도를 기준으로 보면 차이가 큽니다. 존재 여부 확인이 반복되는 순간, list는 불리하고 set이 자연스러운 선택이 됩니다. 자료구조 선택은 결국 이런 판단의 축적입니다.

## 단계별 실습

### 단계 1: 시간 복잡도 비교표 살펴보기

```python
# data structure와 연산별 시간 복잡도
complexity = """
| Operation      | list   | dict   | set    | deque  | heapq     |
|---------------|--------|--------|--------|--------|-----------|
| Index access  | O(1)   | -      | -      | O(n)   | -         |
| Search (in)   | O(n)   | O(1)   | O(1)   | O(n)   | O(n)      |
| Append end    | O(1)*  | O(1)*  | O(1)*  | O(1)   | O(log n)  |
| Prepend       | O(n)   | -      | -      | O(1)   | -         |
| Insert mid    | O(n)   | -      | -      | -      | -         |
| Delete end    | O(1)   | -      | -      | O(1)   | O(log n)  |
| Delete any    | O(n)   | O(1)*  | O(1)*  | O(n)   | O(n)      |
| Min value     | O(n)   | O(n)   | O(n)   | O(n)   | O(1)      |
| Sort          | O(nlogn)| -     | -      | -      | -         |

* amortized
"""
print(complexity)
```

### 단계 2: 선택 함수 구현하기

```python
def suggest_data_structure(
    need_order: bool,
    need_key_value: bool,
    frequent_search: bool,
    need_priority: bool,
    need_both_ends: bool,
) -> str:
    if need_priority:
        return "heapq (priority queue)"
    if need_key_value:
        return "dict (hash table)"
    if frequent_search and not need_order:
        return "set (hash set)"
    if need_both_ends:
        return "deque (double-ended queue)"
    if need_order:
        return "list (dynamic array)"
    return "list (default choice)"

# Example usage
print(suggest_data_structure(
    need_order=False,
    need_key_value=False,
    frequent_search=True,
    need_priority=False,
    need_both_ends=False,
))
# set (hash set)
```

### 단계 3: 실제 벤치마크 실행하기

```python
import time

def benchmark(name, setup, operation, n=100_000):
    data = setup(n)
    start = time.perf_counter()
    operation(data, n)
    elapsed = time.perf_counter() - start
    print(f"{name:20s}: {elapsed:.4f}s")

# Search benchmark
target = 99_999
benchmark(
    "list search",
    lambda n: list(range(n)),
    lambda data, n: target in data,
)
benchmark(
    "set search",
    lambda n: set(range(n)),
    lambda data, n: target in data,
)
benchmark(
    "dict search",
    lambda n: {i: i for i in range(n)},
    lambda data, n: target in data,
)
```

### 단계 4: 복합 자료구조 사용
```python
from collections import defaultdict, deque

# 패턴 1: dict + list — 그룹화
students_by_grade = defaultdict(list)
students = [("Alice", "A"), ("Bob", "B"), ("Charlie", "A"), ("Diana", "B")]
for name, grade in students:
    students_by_grade[grade].append(name)
print(dict(students_by_grade))
# {'A': ['Alice', 'Charlie'], 'B': ['Bob', 'Diana']}

# 패턴 2: dict + set — 중복 없는 그룹화
unique_tags = defaultdict(set)
articles = [("post1", "python"), ("post2", "python"), ("post1", "flask")]
for title, tag in articles:
    unique_tags[title].add(tag)
print(dict(unique_tags))
# {'post1': {'python', 'flask'}, 'post2': {'python'}}

# 패턴 3: list + set — 순서 보존 + 빠른 탐색
class OrderedSet:
    def __init__(self):
        self._items = []
        self._set = set()

    def add(self, item):
        if item not in self._set:
            self._items.append(item)
            self._set.add(item)

    def __contains__(self, item):
        return item in self._set

    def __iter__(self):
        return iter(self._items)

os = OrderedSet()
for x in [3, 1, 4, 1, 5, 9, 2, 6, 5]:
    os.add(x)
print(list(os))  # [3, 1, 4, 5, 9, 2, 6]
```

### 단계 5: 시나리오별 최적 선택 요약
```python
scenarios = {
    "Cache (key-value store, O(1) lookup)": "dict",
    "Deduplication": "set",
    "Task queue (FIFO)": "deque",
    "Undo stack (LIFO)": "list (stack)",
    "Top-K extraction": "heapq",
    "Maintaining sorted data": "bisect + list or SortedList",
    "Graph adjacency list": "dict[str, list[str]]",
    "Frequency counting": "Counter (dict-based)",
    "Config/options management": "dict or dataclass",
    "Immutable coordinates/keys": "tuple",
}

for scenario, choice in scenarios.items():
    print(f"  {scenario:45s} -> {choice}")
```

## 이 코드에서 먼저 봐야 할 점

- 자료구조 선택의 출발점은 “가장 자주 수행하는 연산”을 식별하는 것입니다.
- dict + list, dict + set처럼 구조를 조합하면 요구사항을 더 정확히 만족시킬 수 있습니다.
- 벤치마크는 이론을 검증하는 좋은 방법이지만, 실제 코드는 프로파일링으로 확인해야 합니다.
- Python 내장 자료구조만으로도 대부분의 요구사항을 해결할 수 있습니다.

여기서 중요한 태도는 “고급 구조를 쓰는 것이 곧 좋은 설계”라는 오해를 버리는 것입니다. 대부분의 경우는 list, dict, set, deque의 올바른 조합만으로 충분합니다. 복잡도보다 적합도가 더 중요합니다.

추가로 메모리 비용과 변환 비용도 설계의 일부입니다. 예를 들어 membership test를 빠르게 하려고 매 요청마다 list를 set으로 바꾸면, 조회는 빨라져도 변환 O(n)이 누적되어 오히려 느려질 수 있습니다. 데이터가 오래 살아남는지, 한 번만 순회하는지, 지속적으로 갱신되는지도 함께 봐야 합니다.

실패 패턴도 미리 떠올려야 합니다. 순서를 유지해야 하는데 set을 쓰면 재현하기 어려운 버그가 생기고, 우선순위가 핵심인데 list 정렬을 반복하면 부하가 커질 때 지연이 급증합니다. 좋은 선택 기준은 “평균적으로 빠른 구조”가 아니라 “내 워크로드에서 가장 비싼 연산을 안전하게 낮추는 구조”입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 곳에 list 사용 | 조회가 O(n)이라 규모가 커지면 느려집니다 | 조회 빈도가 높으면 dict/set으로 바꿉니다 |
| 프로파일링 없이 최적화 | 병목이 아닌 부분에 시간을 씁니다 | 실제 병목을 먼저 측정합니다 |
| 데이터 규모 무시 | 작은 입력에서는 괜찮아도 운영에서는 문제가 됩니다 | 예상 입력 크기와 패턴을 먼저 확인합니다 |
| 불필요하게 복잡한 구조 선택 | 코드 가독성과 유지보수성이 떨어집니다 | 단순한 구조로 시작하고 필요할 때만 확장합니다 |
| 변환 비용 무시 | list→set 변환도 O(n) 비용이 있습니다 | 처음부터 맞는 구조를 고르는 편이 낫습니다 |

## 실무에서 이렇게 쓰입니다

- API 응답 캐시는 dict로 관리합니다.
- 최근 N개 로그 이벤트는 `deque(maxlen=N)`으로 유지합니다.
- 추천 시스템은 set 교집합으로 공통 관심사를 계산합니다.
- 우선순위 작업 처리는 `heapq` 기반 큐와 잘 맞습니다.
- 설정 파일은 dict로 읽고 dataclass로 변환해 타입 안전성을 확보합니다.

## 실무에서는 이렇게 생각합니다

“너무 이른 최적화는 모든 악의 근원”이라는 말은 여전히 유효합니다. 하지만 처음부터 맞는 자료구조를 고르는 것은 과한 최적화가 아니라 기본 설계입니다. 자료구조 선택은 나중에 덧붙이는 개선이 아니라, 애초에 코드가 어떤 비용 구조를 가질지를 결정하는 일입니다.

또한 실무에서는 자료구조 하나만 단독으로 쓰는 경우보다, 여러 구조를 조합해 요구사항을 나누어 처리하는 경우가 많습니다. dict + set, dict + list, heapq + dict 같은 조합이 좋은 이유는 각 구조의 강점을 필요한 위치에만 가져오기 때문입니다.

## 체크리스트

- [ ] 주요 자료구조의 핵심 연산 시간 복잡도를 비교할 수 있다
- [ ] 상황별 자료구조 선택 의사결정 흐름을 설명할 수 있다
- [ ] 복합 자료구조(dict + list, dict + set)를 활용할 수 있다
- [ ] 벤치마크와 프로파일링의 역할 차이를 설명할 수 있다
- [ ] 시리즈에서 다룬 10개 주제의 핵심 특성을 요약할 수 있다

## 연습 문제

1. 문자열 100만 개에서 가장 자주 나온 10개 문자열을 찾는 코드를 작성하고, 어떤 자료구조 조합이 적절한지 설명해 보세요.
2. dict + 이중 연결 리스트 또는 `OrderedDict`를 사용해 LRU 캐시를 구현해 보세요.
3. 실시간 주가 스트림에서 최근 5분간의 최대값, 최소값, 평균을 효율적으로 계산하는 클래스를 설계하고, 어떤 자료구조를 왜 선택했는지 설명해 보세요.

## 정리 및 다음 단계

이 시리즈에서는 list, dict, set, deque, 스택, 큐, 연결 리스트, 트리, 힙, 그래프를 차례로 살펴봤습니다. 결국 좋은 자료구조 선택의 기준은 하나로 모입니다. “내가 가장 자주 수행하는 연산은 무엇인가?” 이 질문에 답할 수 있으면, 코드 구조와 성능은 훨씬 예측 가능해집니다.


## 구조 선택 의사결정 트리

자료구조 선택을 체계적으로 하기 위한 의사결정 프레임워크입니다.

```text
[가장 빈번한 연산이 무엇인가?]
  ├─ 순서가 중요 + 인덱스 접근 → list
  ├─ 키-값 매핑 + O(1) 조회 → dict
  ├─ 중복 제거 + membership → set
  ├─ 양쪽 끝 삽입/삭제 → deque
  ├─ 최솟값/최댓값 반복 추출 → heapq
  ├─ 정렬 상태 유지 + 동적 삽입 → sortedcontainers.SortedList
  └─ 계층 관계 + 탐색 → 트리/그래프
```

이 트리의 핵심은 "가장 빈번한 연산"을 먼저 파악하는 것입니다. 모든 연산을 동시에 최적화하는 구조는 존재하지 않으므로, 가장 자주 실행되는 연산의 비용을 최소화하는 구조를 기본값으로 선택합니다.

### 복합 요구사항 처리 패턴

단일 구조로는 부족할 때 여러 구조를 조합합니다.

```python
from collections import OrderedDict
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class IndexedDict(Generic[K, V]):
    """O(1) 키 조회 + 삽입 순서 유지 + 인덱스 접근을 동시 제공합니다."""

    def __init__(self) -> None:
        self._dict: OrderedDict[K, V] = OrderedDict()
        self._keys: list[K] = []

    def put(self, key: K, value: V) -> None:
        if key not in self._dict:
            self._keys.append(key)
        self._dict[key] = value

    def get(self, key: K) -> V | None:
        return self._dict.get(key)

    def get_by_index(self, index: int) -> tuple[K, V]:
        key = self._keys[index]
        return key, self._dict[key]

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, key: object) -> bool:
        return key in self._dict
```

이 패턴은 dict의 O(1) 조회와 list의 O(1) 인덱스 접근을 동시에 제공합니다. 대신 메모리를 두 배 쓰고, 삭제가 복잡해집니다. 모든 설계는 교환(trade-off)입니다.

## 타입 힌트 기반 성능 프로파일러 구현

어떤 구조를 선택했을 때 실제로 어떤 성능이 나오는지, 자동으로 비교하는 도구를 만들어 봅니다.

```python
from __future__ import annotations

import timeit
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BenchResult:
    structure: str
    operation: str
    n: int
    time_sec: float

    @property
    def ops_per_sec(self) -> float:
        return self.n / self.time_sec if self.time_sec > 0 else float("inf")

    def __repr__(self) -> str:
        return f"{self.structure:>15} | {self.operation:<20} | n={self.n:<8} | {self.time_sec:.6f}s | {self.ops_per_sec:,.0f} ops/s"


def benchmark(structure: str, operation: str, func: Callable[[], None], n: int, trials: int = 5) -> BenchResult:
    total = timeit.timeit(func, number=trials)
    return BenchResult(structure=structure, operation=operation, n=n, time_sec=total / trials)


def compare_membership(n: int = 100_000) -> list[BenchResult]:
    """list vs set vs dict의 membership test를 비교합니다."""
    import random
    data_list = list(range(n))
    data_set = set(range(n))
    data_dict = {i: None for i in range(n)}
    targets = random.sample(range(n), min(1000, n))

    results = []
    results.append(benchmark("list", "membership", lambda: [t in data_list for t in targets], n))
    results.append(benchmark("set", "membership", lambda: [t in data_set for t in targets], n))
    results.append(benchmark("dict", "membership", lambda: [t in data_dict for t in targets], n))
    return results


def compare_append(n: int = 100_000) -> list[BenchResult]:
    """list vs deque의 append/appendleft를 비교합니다."""
    results = []
    results.append(benchmark("list", "append", lambda: [None for _ in range(n)], n))
    results.append(benchmark("list", "insert(0)", lambda: _bench_insert0(n // 10), n // 10))
    results.append(benchmark("deque", "appendleft", lambda: _bench_appendleft(n), n))
    return results


def _bench_insert0(n: int) -> None:
    data: list[int] = []
    for i in range(n):
        data.insert(0, i)


def _bench_appendleft(n: int) -> None:
    data: deque[int] = deque()
    for i in range(n):
        data.appendleft(i)


# 실행
print("=" * 80)
print("Membership Test Comparison")
print("=" * 80)
for r in compare_membership():
    print(r)

print()
print("=" * 80)
print("Append/Insert Comparison")
print("=" * 80)
for r in compare_append():
    print(r)
```

이 프로파일러를 사용하면 "감으로 고르는" 대신 데이터로 판단할 수 있습니다.

## 메모리 프로파일링: 구조별 비용 총정리

```python
import sys
from collections import deque, OrderedDict


def measure_all(n: int) -> None:
    structures = {
        "list": list(range(n)),
        "tuple": tuple(range(n)),
        "set": set(range(n)),
        "frozenset": frozenset(range(n)),
        "dict": {i: i for i in range(n)},
        "deque": deque(range(n)),
        "OrderedDict": OrderedDict((i, i) for i in range(n)),
    }

    print(f"\n{'Structure':>15} | {'Shallow (bytes)':>15} | {'Per-element':>12}")
    print("-" * 50)
    for name, obj in structures.items():
        size = sys.getsizeof(obj)
        print(f"{name:>15} | {size:>15,} | {size/n:>10.1f}")


measure_all(1_000)
measure_all(10_000)
measure_all(100_000)
```

이 표를 보면 몇 가지 패턴이 드러납니다.

1. **tuple은 list보다 약간 작습니다**: overallocation이 없기 때문입니다.
2. **dict는 set보다 큽니다**: 키뿐 아니라 값 포인터도 저장하기 때문입니다.
3. **OrderedDict는 dict보다 큽니다**: 순서 유지를 위한 이중 연결 리스트를 내부에 갖기 때문입니다.
4. **deque는 list와 비슷합니다**: 내부 블록 구조의 오버헤드가 있지만, 원소당 비용은 유사합니다.

## 성능 벤치마크: 종합 시나리오 비교

실무에서 자주 만나는 세 가지 시나리오를 구조별로 비교합니다.

### 시나리오 1: 로그 수집 후 중복 제거

```python
import random
import timeit


def scenario_list_dedupe(n: int = 50_000) -> None:
    logs = [f"event_{random.randint(0, n//2)}" for _ in range(n)]
    seen: set[str] = set()
    unique: list[str] = []
    for log in logs:
        if log not in seen:
            seen.add(log)
            unique.append(log)


def scenario_dict_dedupe(n: int = 50_000) -> None:
    logs = [f"event_{random.randint(0, n//2)}" for _ in range(n)]
    unique = list(dict.fromkeys(logs))


trials = 10
t1 = timeit.timeit(scenario_list_dedupe, number=trials)
t2 = timeit.timeit(scenario_dict_dedupe, number=trials)

print(f"set + list dedupe: {t1:.4f}s")
print(f"dict.fromkeys:     {t2:.4f}s")
```

`dict.fromkeys()`는 한 줄로 순서 유지 중복 제거를 수행하며, 내부적으로 C 레벨에서 동작해 더 빠릅니다.

### 시나리오 2: 빈도 집계 후 상위 k개 추출

```python
import heapq
import random
import timeit
from collections import Counter


def scenario_counter_topk(n: int = 100_000, k: int = 10) -> None:
    data = [random.randint(0, 1000) for _ in range(n)]
    counter = Counter(data)
    _ = counter.most_common(k)


def scenario_manual_topk(n: int = 100_000, k: int = 10) -> None:
    data = [random.randint(0, 1000) for _ in range(n)]
    freq: dict[int, int] = {}
    for x in data:
        freq[x] = freq.get(x, 0) + 1
    _ = heapq.nlargest(k, freq.items(), key=lambda x: x[1])


trials = 10
t1 = timeit.timeit(scenario_counter_topk, number=trials)
t2 = timeit.timeit(scenario_manual_topk, number=trials)

print(f"Counter.most_common: {t1:.4f}s")
print(f"dict + heapq:        {t2:.4f}s")
```

Counter는 내부적으로 dict이며 `most_common(k)`은 heapq.nlargest를 사용합니다. 직접 구현과 성능이 유사하지만, 코드가 훨씬 간결합니다.

## unittest로 IndexedDict 검증

```python
import unittest


class TestIndexedDict(unittest.TestCase):
    def setUp(self) -> None:
        self.d: IndexedDict[str, int] = IndexedDict()

    def test_put_and_get(self) -> None:
        self.d.put("a", 1)
        self.d.put("b", 2)
        self.assertEqual(self.d.get("a"), 1)
        self.assertEqual(self.d.get("b"), 2)

    def test_get_missing(self) -> None:
        self.assertIsNone(self.d.get("missing"))

    def test_get_by_index(self) -> None:
        self.d.put("x", 10)
        self.d.put("y", 20)
        self.d.put("z", 30)
        self.assertEqual(self.d.get_by_index(0), ("x", 10))
        self.assertEqual(self.d.get_by_index(2), ("z", 30))

    def test_overwrite(self) -> None:
        self.d.put("key", 1)
        self.d.put("key", 2)
        self.assertEqual(self.d.get("key"), 2)
        self.assertEqual(len(self.d), 1)

    def test_contains(self) -> None:
        self.d.put("present", 1)
        self.assertIn("present", self.d)
        self.assertNotIn("absent", self.d)


if __name__ == "__main__":
    unittest.main()
```

## 선택 기준 요약표

| 요구사항 | 1순위 구조 | 2순위 대안 | 이유 |
|---------|-----------|-----------|------|
| 순서 유지 + 인덱스 접근 | list | tuple (불변) | O(1) 인덱스 접근 |
| 키-값 매핑 + 빠른 조회 | dict | defaultdict | O(1) 해시 기반 조회 |
| 중복 제거 | set | dict.fromkeys() | O(1) membership |
| 양쪽 끝 삽입/삭제 | deque | - | O(1) 양 끝 연산 |
| 우선순위 처리 | heapq | queue.PriorityQueue | O(log n) 삽입/추출 |
| 불변 키/원소 | tuple/frozenset | @dataclass(frozen) | hashable 보장 |
| 빈도 집계 | Counter | defaultdict(int) | most_common() 내장 |
| 정렬 유지 + 동적 삽입 | SortedList | bisect + list | O(log n) 삽입 |

## 처음 질문으로 돌아가기

- **list, dict, set 중 무엇을 선택해야 할지 어떤 기준으로 판단할까요?**
  - "가장 빈번한 연산이 무엇인가"를 기준으로 판단합니다. 순서와 인덱스가 중요하면 list, 키 기반 조회가 핵심이면 dict, 중복 제거와 membership test가 많으면 set입니다. 모든 연산을 동시에 최적화하는 구조는 없으므로, 핵심 연산 하나를 정하고 그에 맞는 구조를 선택합니다.
- **자료구조 선택에서 가장 먼저 봐야 할 연산은 무엇일까요?**
  - 읽기(조회/검색)입니다. 대부분의 시스템에서 읽기는 쓰기보다 훨씬 빈번합니다. 읽기 패턴이 "키로 찾기"인지, "인덱스로 접근"인지, "존재 여부 확인"인지에 따라 dict, list, set으로 자연스럽게 분기됩니다.
- **여러 구조를 조합해 요구사항을 동시에 만족시키는 방법은 무엇일까요?**
  - 두 구조를 동시에 유지합니다. IndexedDict 예시처럼 dict + list를 함께 쓰면 O(1) 키 조회와 O(1) 인덱스 접근을 동시에 제공할 수 있습니다. LRU 캐시의 OrderedDict, Counter의 dict + heap 조합도 같은 원리입니다. 대가는 메모리와 동기화 복잡성입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): 스택과 큐](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): 해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): 연결 리스트](./05-linked-lists.md)
- [Data Structures with Python 101 (6/10): 트리와 이진 트리](./06-trees-and-binary-trees.md)
- [Data Structures with Python 101 (7/10): 힙과 우선순위 큐](./07-heaps-and-priority-queues.md)
- [Data Structures with Python 101 (8/10): 그래프 표현](./08-graph-representations.md)
- [Data Structures with Python 101 (9/10): set과 집합 연산](./09-sets-and-set-operations.md)
- **자료구조 선택 기준 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python 공식 문서 — collections](https://docs.python.org/3/library/collections.html)
- [Python 공식 문서 — heapq](https://docs.python.org/3/library/heapq.html)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)

Tags: Python, 자료구조, 시간 복잡도, 성능 최적화, 자료구조 비교
