---
series: data-structures-101
episode: 10
title: "Data Structures 101 (10/10): 자료구조 선택 기준"
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
  - 선택 기준
  - 시간 복잡도
  - 워크로드
  - 설계
seo_description: 워크로드와 연산 패턴 분석을 통해 시스템 성능을 극대화하는 최적의 자료구조 선택 기준과 실무 원칙을 상세히 설명합니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (10/10): 자료구조 선택 기준

> 좋은 선택은 "데이터의 모양"이 아니라 "연산의 빈도와 패턴"에서 출발합니다. 핫패스에 어떤 연산이 있는지, 입력은 얼마나 큰지, 메모리 제약은 무엇인지 먼저 정리하면 후보가 빠르게 좁혀집니다.

이 글은 Data Structures 101 시리즈의 마지막 글입니다.

![Data Structures 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/10/10-01-big-picture.ko.png)
*Data Structures 101 10장 흐름 개요*

## 이 글에서 다룰 문제

- 새로운 문제를 만났을 때 자료구조 선택은 무엇부터 생각해야 할까요?
- 워크로드를 정의하는 다섯 가지 질문은 무엇일까요?
- 자료구조 선택을 결정 트리처럼 체계화할 수 있을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

알고리즘은 자료구조 위에서 실행되므로, 자료구조는 시스템 성능의 상한을 사실상 결정합니다. 잘못 고른 구조는 알고리즘 튜닝만으로 회복하기 어렵습니다. 반대로 워크로드 분석 없이 "내가 익숙한 구조"나 "이론상 빠른 구조"를 고르는 것도 위험합니다.

> 자료구조 선택 = 워크로드 분석 + 트레이드오프 이해 + 측정입니다.

## 핵심 한눈에 보기

```text
                "Which operation dominates?"
                       │
        ┌──────────────┼──────────────┐
       Search        Insert/Delete   Iterate
        │                │              │
   ┌────┴───┐       ┌────┴────┐    ┌────┴────┐
  by key?  by range? both ends? arbitrary?  in order?  sorted?
   │       │       │        │         │        │
  dict    BST    deque   linked    list/array  BST
                                              /sorted
```

| 용어 | 의미 |
| --- | --- |
| 워크로드 | 시스템이 실제로 수행하는 연산 종류와 그 빈도 |
| 핫패스 | 가장 자주 실행되는 핵심 코드 경로 |
| 빅오 | 입력 증가에 따른 비용 성장 상한 |
| 분할 상환 | 여러 번의 호출을 평균냈을 때의 비용 |
| 캐시 지역성 | CPU 캐시에 잘 맞는 접근 패턴 |

## 전후 비교

**Before — "일단 dict로":**

```python
# 순서가 중요한데도 dict를 사용
events = {}
events["e1"] = 1; events["e2"] = 2; events["e3"] = 3
# 우선순위 처리를 위해 매 접근마다 정렬 필요 — 느림
```

**After — 워크로드를 분석하고 힙을 선택:**

```python
import heapq
events = []
heapq.heappush(events, (1, "e1"))
heapq.heappush(events, (2, "e2"))
# 매번 O(log n)으로 최고 우선순위 항목 pop
```

문제는 데이터가 아니라 연산 패턴입니다. "어떤 값이 있나"보다 "무엇을 반복해서 하나"를 먼저 물으면 선택이 훨씬 정확해집니다.

## 단계별로 따라하기

### 1단계: 다섯 가지 질문으로 워크로드 정의하기

```python
# 데이터 구조를 고르기 전 답할 5가지 질문
workload_questions = [
    "1. Which operation happens most frequently?",
    "2. How large is the input? (tens, tens of thousands, billions?)",
    "3. Does the data need order or sorting?",
    "4. What are the memory constraints?",
    "5. Are there concurrency or persistence requirements?",
]
for q in workload_questions:
    print(q)
```

이 다섯 질문에 답하면 후보는 보통 하나나 둘로 줄어듭니다. 자료구조 선택은 감각이 아니라 분류 작업에 가깝습니다.

### 2단계: 구조별 시간 복잡도 표

```python
table = {
    "list (Python)":          {"index": "O(1)", "search": "O(n)", "append": "O(1)*", "prepend": "O(n)"},
    "deque":                  {"index": "O(n)", "search": "O(n)", "append": "O(1)",  "prepend": "O(1)"},
    "dict / set":             {"search": "O(1)*", "insert": "O(1)*", "sorted iter": "O(n log n)"},
    "balanced BST (Sorted)":  {"search": "O(log n)", "insert": "O(log n)", "sorted iter": "O(n)"},
    "heap":                   {"min": "O(1)", "insert": "O(log n)", "arbitrary search": "O(n)"},
    "graph (adj list)":       {"neighbors": "O(deg)", "BFS/DFS": "O(V+E)"},
}

for ds, ops in table.items():
    print(f"{ds:<25} {ops}")
```

핫패스에서 가장 자주 일어나는 연산이 무엇인지 확인한 뒤, 그 연산이 빠른 구조를 찾으면 됩니다. `*`는 분할 상환입니다.

### 3단계: 결정 트리를 코드로 표현하기

```python
def recommend_structure(workload):
    """Take a workload dict and return a recommended structure."""
    primary = workload["primary_op"]
    needs_order = workload.get("ordered", False)

    if primary == "key_lookup":
        return "dict / set" if not needs_order else "SortedDict"
    if primary == "min_or_max":
        return "heap (heapq)"
    if primary == "both_ends":
        return "deque"
    if primary == "range_query":
        return "BST / sorted array (with bisect)"
    if primary == "graph_traversal":
        return "Graph (adjacency list) + BFS/DFS"
    if primary == "ordered_iteration":
        return "list / array"
    return "list (default)"

print(recommend_structure({"primary_op": "key_lookup"}))     # dict / set
print(recommend_structure({"primary_op": "min_or_max"}))      # heap
print(recommend_structure({"primary_op": "both_ends"}))       # deque
```

워크로드를 명시적으로 적기 시작하면 자료구조 선택은 훨씬 덜 감각적이고, 훨씬 더 기계적인 작업이 됩니다.

### 4단계: 잘못된 선택의 비용 측정

```python
import time
from collections import deque

# 잘못된 선택: queue로 list 사용
def queue_with_list(n):
    q = []
    for i in range(n):
        q.append(i)
    while q:
        q.pop(0)

# 올바른 선택: queue로 deque 사용
def queue_with_deque(n):
    q = deque()
    for i in range(n):
        q.append(i)
    while q:
        q.popleft()

N = 50_000

start = time.perf_counter()
queue_with_list(N)
print(f"list:  {(time.perf_counter() - start) * 1000:.0f} ms")

start = time.perf_counter()
queue_with_deque(N)
print(f"deque: {(time.perf_counter() - start) * 1000:.0f} ms")
# list:  수백 ms
# deque: 수 ms — 100배 이상 차이
```

같은 동작인데도 100배 이상 차이가 날 수 있습니다. 빅오 분석을 무시하면 결국 측정 결과가 그 비용을 그대로 보여 줍니다.

### 5단계: 실전 카탈로그

```python
cases = [
    ("LRU cache",            "dict + doubly linked list",         "O(1) get/put"),
    ("Task scheduler",       "heap (priority queue)",             "O(log n) for next task"),
    ("Friend suggestions",   "graph + BFS (k-hop)",               "O(V + E)"),
    ("Autocomplete",         "trie (prefix tree)",                "O(prefix length)"),
    ("API request dedup",    "set",                               "O(1) check"),
    ("DB index",             "B+Tree (balanced BST variant)",     "O(log n) sorted lookup"),
    ("undo / redo",          "two stacks",                        "O(1) push/pop"),
    ("Event simulation",     "heap (event queue)",                "O(log n) next event"),
]
for use_case, ds, complexity in cases:
    print(f"  {use_case:<25} → {ds:<38} ({complexity})")
```

실제 시스템은 거의 항상 여러 자료구조의 조합으로 만들어집니다. 중요한 것은 전체를 한 번에 보지 말고, 구성 요소별 워크로드를 따로 분석하는 습관입니다.

## 이 코드에서 주목할 점

- 자료구조 선택은 항상 워크로드 분석에서 시작해야 합니다.
- 같은 ADT라도 입력 패턴에 따라 최적 구현은 달라집니다.
- 잘못된 선택의 비용은 빅오가 예고한 지점에서 정확히 드러납니다.
- 실전 시스템은 단일 구조보다 구조 조합으로 만들어집니다.

## 자료구조 종합 비교표

| 구조 | 조회 | 삽입 | 삭제 | 순서 유지 | 메모리 | 대표 사용처 |
| --- | --- | --- | --- | --- | --- | --- |
| 동적 배열 | O(1) 인덱스 | 끝 O(1)* | 끝 O(1), 중간 O(n) | 삽입 순서 | 연속, 효율 최고 | 읽기 중심, 랜덤 접근 |
| 연결 리스트 | O(n) | 위치 알면 O(1) | 위치 알면 O(1) | 삽입 순서 | 포인터 오버헤드 | 잦은 중간 삽입·삭제 |
| 해시 테이블 | O(1)* | O(1)* | O(1)* | 없음 (py3.7+ 삽입 순서) | 로드팩터 의존 | 키 기반 빠른 조회 |
| BST (균형) | O(log n) | O(log n) | O(log n) | 정렬 순서 | 포인터 구조 | 범위 질의, 정렬 유지 |
| 힙 | 최솟값 O(1) | O(log n) | 루트 O(log n), 임의 O(n) | 부분 순서 | 연속 배열 | 우선순위 큐 |
| 그래프 | O(V+E) 순회 | O(1) 간선 추가 | O(V+E) | 없음 | O(V+E) | 관계 모델링 |

## 디버깅 시나리오

### 시나리오 1: "dict로 했는데 왜 느리죠?"

**증상:** 로그 분석 시스템에서 특정 IP의 로그를 "최근 순서대로" 출력해야 하는데 매번 정렬이 필요합니다.

```python
# 문제: dict는 검색에 최적, 순서 유지는 부가적
logs = {}
for timestamp, ip, msg in log_stream:
    if ip not in logs:
        logs[ip] = []
    logs[ip].append((timestamp, msg))

# 최근 순서로 정렬이 필요할 때마다
for ip, entries in logs.items():
    entries.sort(key=lambda x: x[0])   # 매번 O(n log n)

# 해결: 삽입 순서가 이미 정렬되어 있다면 deque로 tail만 유지
from collections import defaultdict, deque

recent_logs = defaultdict(lambda: deque(maxlen=1000))
for timestamp, ip, msg in log_stream:
    recent_logs[ip].append((timestamp, msg))   # 자동으로 최근 1000개만 유지
```

### 시나리오 2: 중간 삽입이 많은데 list를 쓰고 있음

**증상:** 정렬된 상태를 유지하면서 데이터를 계속 삽입하는 코드가 점점 느려집니다.

```python
# 문제: bisect로 위치를 O(log n)에 찾아도 삽입이 O(n)
import bisect
sorted_list = []
for value in data_stream:
    bisect.insort(sorted_list, value)   # O(n) due to shifting

# 해결: 정렬 순회가 핵심이라면 SortedList
from sortedcontainers import SortedList
sl = SortedList()
for value in data_stream:
    sl.add(value)   # O(log n)
```

### 시나리오 3: 구조 선택 없이 구현부터 시작

**증상:** 초기 설계에서 구조를 정하지 않고 구현하다가 중간에 변경이 어려워집니다.

**해결:** 구현 전에 워크로드를 명시적으로 문서화합니다.

```python
# 설계 단계에서 워크로드 명세를 코드로 표현
class WorkloadSpec:
    """설계 단계에서 명세를 먼저 작성"""
    primary_op = "key_lookup"       # 80% 이상이 키 기반 조회
    ordered = False                  # 순서 불필요
    max_size = 10_000               # 최대 항목 수
    read_write_ratio = "95:5"       # 읽기 중심

# → dict 선택이 명확해짐
```

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "일단 dict로" 접근함 | 정렬 순회나 우선순위 처리에서 비효율 | 워크로드에 맞는 구조를 고릅니다 |
| 빅오만 보고 결정함 | 상수 항과 캐시 지역성을 놓침 | 측정과 메모리 특성을 함께 봅니다 |
| 너무 이른 최적화 | 복잡한 구조가 유지보수 부담이 됨 | 단순하게 시작하고 측정 뒤 교체합니다 |
| 라이브러리를 피함 | 검증된 구현을 다시 만들게 됨 | 표준 라이브러리와 유명 라이브러리를 먼저 봅니다 |
| 하나의 구조로 모든 연산을 해결하려 함 | 어느 연산도 충분히 빠르지 않음 | dict + linked list처럼 조합합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스는 워크로드에 따라 B+Tree, Hash, GIN, GiST 같은 인덱스를 고릅니다.
- 캐시 시스템은 TTL, LRU, LFU 정책마다 다른 구조 조합을 사용합니다.
- 검색 엔진의 역색인은 해시 테이블과 정렬된 posting list의 조합입니다.
- 추천 시스템은 사용자-아이템 그래프와 밀집 임베딩을 함께 씁니다.
- 스트림 처리에서 슬라이딩 윈도우는 deque, top-k는 최소 힙이 자주 쓰입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 기본 구조에서 시작합니다. list와 dict로 첫 버전을 만들고, 실제 병목이 드러났을 때만 더 복잡한 구조로 교체합니다. 자료구조 수준에서도 성급한 최적화는 적입니다.

또한 "핵심 자료구조의 한계가 곧 시스템의 한계"라는 사실을 압니다. 중심 데이터를 담는 구조를 잘못 고르면 알고리즘 미세 조정이나 인프라 확장으로는 회복하기 어렵습니다. 그래서 설계 단계에서 더 오래 고민하고, 한 번 결정한 뒤 바꾸기 어렵다는 점도 처음부터 감안합니다.

마지막으로, 자료구조 선택은 성능뿐 아니라 가독성과 유지보수성의 문제이기도 합니다. 잘 고른 구조는 알고리즘을 짧고 명확하게 만듭니다.

## 운영 체크리스트

- [ ] 워크로드를 정의하는 다섯 질문에 답할 수 있습니다
- [ ] 선택한 구조에서 핫패스 연산의 복잡도를 매핑할 수 있습니다
- [ ] 빅오 외에 캐시 지역성, 메모리, 구현 복잡도도 고려합니다
- [ ] 표준 라이브러리로 시작하고 측정 후 교체하는 원칙을 이해합니다
- [ ] 실제 시스템은 여러 자료구조 조합으로 구성된다는 점을 알고 있습니다

## 연습 문제

1. 최근에 작성한 코드 하나를 골라 사용한 자료구조를 모두 나열하고, 각 구조의 핫패스 연산을 분석해 보세요. 더 적합한 대안이 있었나요?

2. LRU 캐시를 두 방식 — `OrderedDict`, 직접 만든 dict + 이중 연결 리스트 — 으로 각각 구현해 시간과 코드 복잡도를 비교해 보세요.

3. 초당 100만 이벤트를 받는 시스템을 설계한다고 가정해 보세요. (a) 가장 최근 1만 개 유지, (b) 우선순위 상위 100개 유지, (c) 카테고리별 빠른 개수 집계라는 요구에 각각 어떤 자료구조 조합이 맞는지 설계해 보세요.

## 정리 및 다음 단계

자료구조 선택은 컴퓨터과학 기초의 마지막 관문이면서 실무에서 매일 반복되는 결정입니다. "데이터의 모양"이 아니라 "연산의 빈도와 패턴"에서 시작하고, 빅오와 함께 캐시 지역성, 메모리, 구현 복잡도까지 함께 봐야 합니다. 하나의 구조로 모든 문제를 해결하려 하지 말고, 워크로드에 맞게 여러 구조를 조합하는 것이 가장 실전적인 접근입니다.

이 시리즈에서 다룬 아홉 가지 자료구조 — 배열, 연결 리스트, 스택, 큐, 해시 테이블, 트리, BST, 힙, 그래프 — 는 거의 모든 알고리즘과 시스템 설계의 어휘입니다. 다음 단계는 알고리즘 시리즈입니다. 정렬, 탐색, 동적 계획법, 그래프 알고리즘처럼, 이제 이 구조들 위에서 실제로 무엇을 할지로 넘어갑니다.

## 처음 질문으로 돌아가기

- **새로운 문제를 만났을 때 자료구조 선택은 무엇부터 생각해야 할까요?**
  - 핫패스 연산을 먼저 정의합니다. 검색인지, 삽입·삭제인지, 순회인지에 따라 후보가 바뀝니다. 데이터 크기와 메모리 제약도 함께 봅니다.
- **워크로드를 정의하는 다섯 가지 질문은 무엇일까요?**
  - 가장 빈번한 연산, 입력 크기, 순서 필요 여부, 메모리 제약, 동시성·영속성 요구입니다.
- **자료구조 선택을 결정 트리처럼 체계화할 수 있을까요?**
  - 네. 주 연산 → 순서 필요 여부 → 크기와 메모리 → 동시성 순으로 좁히면 대부분 한두 후보로 귀결됩니다. 마지막은 측정으로 확정합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- [Data Structures 101 (6/10): 트리](./06-trees.md)
- [Data Structures 101 (7/10): 이진 탐색 트리](./07-binary-search-trees.md)
- [Data Structures 101 (8/10): 힙](./08-heaps.md)
- [Data Structures 101 (9/10): 그래프](./09-graphs.md)
- **자료구조 선택 기준 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)
- [System Design Primer — Data Structures](https://github.com/donnemartin/system-design-primer)

Tags: Computer Science, 자료구조, 선택 기준, 시간 복잡도, 워크로드, 설계
