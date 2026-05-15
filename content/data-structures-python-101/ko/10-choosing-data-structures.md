---
series: data-structures-python-101
episode: 10
title: 자료구조 선택 기준
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
  - 시간 복잡도
  - 성능 최적화
  - 자료구조 비교
seo_description: 데이터 특성과 연산 빈도에 따른 Python 자료구조 선택 기준을 정리합니다. 시간 복잡도 비교, 벤치마크, 복합 구조 활용 패턴을 익힙니다.
last_reviewed: '2026-05-12'
---

# 자료구조 선택 기준

이 글은 Data Structures with Python 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

- list, dict, set 중 무엇을 선택해야 할지 어떤 기준으로 판단할까요?
- 자료구조 선택에서 가장 먼저 봐야 할 연산은 무엇일까요?
- 여러 구조를 조합해 요구사항을 동시에 만족시키는 방법은 무엇일까요?
- 벤치마크와 프로파일링은 실제 선택 과정에서 어떤 역할을 할까요?

> 멘탈 모델: 자료구조 선택은 “어느 구조가 더 고급인가”를 고르는 일이 아니라, “가장 자주 수행할 연산에 무엇을 최적화할 것인가”를 결정하는 일입니다.

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

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 시간 복잡도 | 데이터가 커질 때 연산 시간이 얼마나 증가하는지 나타내는 기준입니다 |
| 공간 복잡도 | 자료구조가 사용하는 메모리 양입니다 |
| 트레이드오프 | 한 연산을 빠르게 만들면 다른 연산이 느려질 수 있다는 뜻입니다 |
| 프로파일링 | 실제 코드에서 병목이 어디인지 측정하는 작업입니다 |
| 벤치마킹 | 여러 구현이나 구조의 성능을 비교하는 실험입니다 |

## Before / After

자료구조를 습관적으로 고르는 경우와 의도적으로 고르는 경우를 비교해 보겠습니다.

```python
# before: using list everywhere — inefficient
seen = []
for item in data:
    if item not in seen:  # O(n) lookup
        seen.append(item)
        process(item)
```

```python
# after: choosing the right data structure — efficient
seen = set()
for item in data:
    if item not in seen:  # O(1) lookup
        seen.add(item)
        process(item)
```

기능만 보면 두 코드는 거의 같습니다. 하지만 연산 빈도를 기준으로 보면 차이가 큽니다. 존재 여부 확인이 반복되는 순간, list는 불리하고 set이 자연스러운 선택이 됩니다. 자료구조 선택은 결국 이런 판단의 축적입니다.

## 단계별 실습

### Step 1: Review the time complexity comparison table

```python
# Time complexity by data structure and operation
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

### Step 2: Implement a decision function

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

### Step 3: Run a real benchmark

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

### Step 4: Use composite data structures

```python
from collections import defaultdict, deque

# Pattern 1: dict + list — grouping
students_by_grade = defaultdict(list)
students = [("Alice", "A"), ("Bob", "B"), ("Charlie", "A"), ("Diana", "B")]
for name, grade in students:
    students_by_grade[grade].append(name)
print(dict(students_by_grade))
# {'A': ['Alice', 'Charlie'], 'B': ['Bob', 'Diana']}

# Pattern 2: dict + set — unique grouping
unique_tags = defaultdict(set)
articles = [("post1", "python"), ("post2", "python"), ("post1", "flask")]
for title, tag in articles:
    unique_tags[title].add(tag)
print(dict(unique_tags))
# {'post1': {'python', 'flask'}, 'post2': {'python'}}

# Pattern 3: list + set — order preservation + fast search
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

### Step 5: Summarize optimal choices by scenario

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

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- [해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [연결 리스트](./05-linked-lists.md)
- [트리와 이진 트리](./06-trees-and-binary-trees.md)
- [힙과 우선순위 큐](./07-heaps-and-priority-queues.md)
- [그래프 표현](./08-graph-representations.md)
- [set과 집합 연산](./09-sets-and-set-operations.md)
- **자료구조 선택 기준 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Python Docs — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Real Python — Common Python Data Structures](https://realpython.com/python-data-structures/)

Tags: Python, 자료구조, 시간 복잡도, 성능 최적화, 자료구조 비교
