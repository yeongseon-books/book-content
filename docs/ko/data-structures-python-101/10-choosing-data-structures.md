---
series: data-structures-python-101
episode: 10
title: 자료구조 선택 기준
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
  - 시간 복잡도
  - 성능 최적화
  - 자료구조 비교
seo_description: 상황별 최적의 자료구조를 선택하는 기준과 의사결정 흐름을 정리합니다.
last_reviewed: '2026-05-04'
---

# 자료구조 선택 기준

> Data Structures with Python 101 시리즈 (10/10)


## 이 글에서 다룰 문제

개별 자료구조를 아는 것과 상황에 맞게 선택하는 것은 다른 능력입니다. 잘못된 자료구조를 선택하면 코드가 복잡해지고 성능이 저하됩니다. 올바른 선택은 코드를 간결하고 빠르게 만듭니다.

> "어떤 자료구조를 쓸까?"라는 질문에 답하려면, 먼저 "어떤 연산을 가장 많이 하는가?"를 물어야 합니다.

면접에서 "왜 이 자료구조를 선택했는가?"는 구현 능력보다 더 중요한 질문입니다. 선택의 근거를 설명할 수 있어야 합니다.

## 핵심 개념 잡기

> 자료구조 선택 = 주요 연산의 빈도와 데이터 특성에 따른 최적화

```
검색이 잦다?
  ├── 키-값 매핑? → dict
  └── 존재 여부만? → set

순서가 중요하다?
  ├── 끝에서만 추가/제거? → list (스택)
  ├── 양쪽 끝? → deque (큐)
  └── 중간 삽입/삭제? → 연결 리스트 고려

우선순위가 필요하다? → heapq

계층 구조? → 트리
관계 네트워크? → 그래프
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 시간 복잡도 | 데이터 크기에 따른 연산 소요 시간의 증가율입니다 |
| 공간 복잡도 | 자료구조가 사용하는 메모리의 양입니다 |
| 트레이드오프 | 한 연산의 성능을 높이면 다른 연산이 느려질 수 있습니다 |
| 프로파일링 | 실제 코드의 병목을 측정하여 최적화 대상을 찾는 것입니다 |
| 벤치마킹 | 서로 다른 구현의 성능을 비교 측정하는 것입니다 |

## Before / After

자료구조를 무작정 선택하는 방식과 체계적으로 선택하는 방식을 비교합니다.

```python
# before: 모든 곳에 list 사용 — 비효율적
seen = []
for item in data:
    if item not in seen:  # O(n) 검색
        seen.append(item)
        process(item)
```

```python
# after: 용도에 맞는 자료구조 선택 — 효율적
seen = set()
for item in data:
    if item not in seen:  # O(1) 검색
        seen.add(item)
        process(item)
```

## 단계별 실습

### Step 1: 시간 복잡도 비교표 확인

```python
# 주요 자료구조별 연산 시간 복잡도
complexity = """
| 연산         | list   | dict   | set    | deque  | heapq     |
|-------------|--------|--------|--------|--------|-----------|
| 인덱스 접근  | O(1)   | -      | -      | O(n)   | -         |
| 검색(in)    | O(n)   | O(1)   | O(1)   | O(n)   | O(n)      |
| 끝 삽입     | O(1)*  | O(1)*  | O(1)*  | O(1)   | O(log n)  |
| 앞 삽입     | O(n)   | -      | -      | O(1)   | -         |
| 중간 삽입   | O(n)   | -      | -      | -      | -         |
| 끝 삭제     | O(1)   | -      | -      | O(1)   | O(log n)  |
| 임의 삭제   | O(n)   | O(1)*  | O(1)*  | O(n)   | O(n)      |
| 최솟값      | O(n)   | O(n)   | O(n)   | O(n)   | O(1)      |
| 정렬        | O(nlogn)| -     | -      | -      | -         |

* amortized
"""
print(complexity)
```

### Step 2: 의사결정 함수 구현

```python
def suggest_data_structure(
    need_order: bool,
    need_key_value: bool,
    frequent_search: bool,
    need_priority: bool,
    need_both_ends: bool,
) -> str:
    if need_priority:
        return "heapq (우선순위 큐)"
    if need_key_value:
        return "dict (해시 테이블)"
    if frequent_search and not need_order:
        return "set (해시 집합)"
    if need_both_ends:
        return "deque (양방향 큐)"
    if need_order:
        return "list (동적 배열)"
    return "list (기본 선택)"

# 사용 예
print(suggest_data_structure(
    need_order=False,
    need_key_value=False,
    frequent_search=True,
    need_priority=False,
    need_both_ends=False,
))
# set (해시 집합)
```

### Step 3: 실제 벤치마크

```python
import time

def benchmark(name, setup, operation, n=100_000):
    data = setup(n)
    start = time.perf_counter()
    operation(data, n)
    elapsed = time.perf_counter() - start
    print(f"{name:20s}: {elapsed:.4f}초")

# 검색 벤치마크
target = 99_999
benchmark(
    "list 검색",
    lambda n: list(range(n)),
    lambda data, n: target in data,
)
benchmark(
    "set 검색",
    lambda n: set(range(n)),
    lambda data, n: target in data,
)
benchmark(
    "dict 검색",
    lambda n: {i: i for i in range(n)},
    lambda data, n: target in data,
)
```

### Step 4: 복합 자료구조 활용

```python
from collections import defaultdict, deque

# 패턴 1: dict + list — 그룹핑
students_by_grade = defaultdict(list)
students = [("Alice", "A"), ("Bob", "B"), ("Charlie", "A"), ("Diana", "B")]
for name, grade in students:
    students_by_grade[grade].append(name)
print(dict(students_by_grade))
# {'A': ['Alice', 'Charlie'], 'B': ['Bob', 'Diana']}

# 패턴 2: dict + set — 고유 그룹핑
unique_tags = defaultdict(set)
articles = [("글1", "python"), ("글2", "python"), ("글1", "flask")]
for title, tag in articles:
    unique_tags[title].add(tag)
print(dict(unique_tags))
# {'글1': {'python', 'flask'}, '글2': {'python'}}

# 패턴 3: list + dict — 순서 보존 + 빠른 검색
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

### Step 5: 상황별 최적 선택 정리

```python
scenarios = {
    "캐시 (키-값 저장, O(1) 조회)": "dict",
    "중복 제거": "set",
    "작업 큐 (FIFO)": "deque",
    "실행 취소 (LIFO)": "list (스택)",
    "Top-K 추출": "heapq",
    "정렬된 데이터 유지": "bisect + list 또는 SortedList",
    "그래프 인접 리스트": "dict[str, list[str]]",
    "빈도 세기": "Counter (dict 기반)",
    "설정/옵션 관리": "dict 또는 dataclass",
    "불변 좌표/키": "tuple",
}

for scenario, choice in scenarios.items():
    print(f"  {scenario:40s} → {choice}")
```

## 이 코드에서 주목할 점

- 자료구조 선택의 핵심은 "가장 빈번한 연산"이 무엇인지 파악하는 것입니다
- 복합 자료구조(dict + list, dict + set)로 여러 요구사항을 동시에 만족할 수 있습니다
- 벤치마크로 실제 성능을 측정하면 이론적 분석을 뒷받침할 수 있습니다
- Python 내장 자료구조만으로 대부분의 상황을 커버할 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 곳에 list만 사용 | 검색이 O(n)이라 대규모 데이터에서 느립니다 | 검색 빈도가 높으면 dict/set을 사용합니다 |
| 성능 측정 없이 최적화 | 병목이 아닌 곳을 최적화하여 시간을 낭비합니다 | 프로파일링으로 실제 병목을 찾습니다 |
| 데이터 규모를 고려하지 않음 | 소규모에서는 차이 없지만 대규모에서 문제됩니다 | 예상 데이터 규모를 먼저 확인합니다 |
| 불필요하게 복잡한 자료구조 사용 | 코드 가독성이 떨어집니다 | 가장 단순한 것부터 시작하고 필요시 변경합니다 |
| 자료구조 변환 비용 무시 | list→set 변환도 O(n)입니다 | 처음부터 적합한 자료구조를 선택합니다 |

## 실무에서 이렇게 쓰입니다

- API 응답 캐시를 dict로 구현하여 중복 요청을 방지합니다
- 로그 이벤트를 deque(maxlen=N)으로 최근 N개만 유지합니다
- 추천 시스템에서 사용자 관심사를 set으로 저장하고 교집합으로 유사도를 계산합니다
- 대기열 시스템에서 우선순위 작업을 heapq로 관리합니다
- 설정 파일을 dict로 파싱하고 dataclass로 타입 안전하게 변환합니다

## 현업 개발자는 이렇게 생각합니다

"너무 이른 최적화는 모든 악의 근원이다"라는 격언이 있지만, 올바른 자료구조를 처음부터 선택하는 것은 최적화가 아니라 설계입니다. list, dict, set, deque 네 가지만 정확히 알아도 Python 개발의 90%를 커버할 수 있습니다.

실무에서는 자료구조 하나만 쓰기보다 조합하여 사용하는 경우가 많습니다. dict + set, dict + list, heapq + dict 같은 조합이 복잡한 요구사항을 깔끔하게 해결합니다.

## 체크리스트

- [ ] 주요 자료구조의 연산별 시간 복잡도를 비교할 수 있다
- [ ] 상황에 맞는 자료구조를 선택하는 의사결정 흐름을 설명할 수 있다
- [ ] 복합 자료구조(dict + list, dict + set)를 활용할 수 있다
- [ ] 벤치마크로 자료구조의 실제 성능을 비교할 수 있다
- [ ] 시리즈에서 배운 10가지 자료구조의 핵심 특성을 요약할 수 있다

## 정리 및 다음 글 안내

이 시리즈에서 list, dict, set, deque, 스택, 큐, 연결 리스트, 트리, 힙, 그래프를 다뤘습니다. 자료구조 선택의 핵심은 "가장 빈번한 연산이 무엇인가?"입니다. 올바른 자료구조를 선택하면 코드가 간결해지고 성능이 향상됩니다.

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

- [Python 공식 문서 — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Real Python — Common Python Data Structures](https://realpython.com/python-data-structures/)
