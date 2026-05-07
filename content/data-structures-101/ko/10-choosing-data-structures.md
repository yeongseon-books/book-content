---
series: data-structures-101
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
  - Computer Science
  - 자료구조
  - 선택 기준
  - 시간 복잡도
  - 워크로드
  - 설계
seo_description: 시리즈를 마무리하며 자료구조 선택의 의사결정 트리, 워크로드 분석 방법, 그리고 흔한 잘못된 선택을 정리합니다.
last_reviewed: '2026-05-04'
---

# 자료구조 선택 기준

> Data Structures 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 지금까지 9가지 자료구조를 배웠습니다. 새 문제를 만나면 무엇부터 떠올려야 할까요?

> 자료구조 선택은 "무엇을 저장하느냐"가 아니라 "어떤 연산이 가장 자주 일어나느냐"로 결정됩니다. 같은 사용자 데이터를 다루더라도 검색이 잦으면 해시 테이블, 정렬 순회가 잦으면 BST, 양 끝만 자주 다루면 deque, 우선순위 처리가 잦으면 힙입니다. 이 글에서는 시리즈를 마무리하며 워크로드를 분석하는 방법, 의사결정 트리, 그리고 실전에서 흔히 마주치는 잘못된 선택들을 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 워크로드를 정의하는 핵심 질문 5가지
- 자료구조 선택의 의사결정 트리
- 시간 복잡도 비교표 한눈에 보기
- 흔히 발생하는 잘못된 선택과 교정

## 왜 중요한가

알고리즘은 자료구조 위에서 동작하므로, 자료구조 선택은 시스템 성능의 상한을 결정합니다. 한 번 잘못 고른 자료구조는 알고리즘 최적화로 만회하기 어렵습니다. 그러나 정확한 워크로드 분석 없이 자료구조를 고르는 것도 위험합니다. "익숙한 것"이나 "이론적으로 가장 빠른 것"이 늘 옳은 답은 아닙니다.

> 자료구조 선택 = 워크로드 분석 + 트레이드오프 이해 + 측정.

## 개념 한눈에 보기

> 좋은 선택은 "데이터의 특성"이 아니라 "연산의 빈도와 패턴"에서 시작합니다. 어떤 연산이 핫 패스인지, 입력은 얼마나 큰지, 메모리 제약은 무엇인지 먼저 정의해야 합니다.

```text
                "어떤 연산이 가장 자주?"
                       │
        ┌──────────────┼──────────────┐
       검색            삽입/삭제       순회
        │                │              │
   ┌────┴───┐       ┌────┴────┐    ┌────┴────┐
  키로?  범위로?  양 끝?  임의 위치?  순서대로?  정렬?
   │       │       │        │         │        │
  dict    BST    deque   linked    list/array  BST
                                              /sorted
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 워크로드(workload) | 시스템이 실제로 수행하는 연산의 종류와 빈도 |
| 핫 패스(hot path) | 가장 자주 실행되는 코드 경로 |
| 빅오(Big-O) | 입력 크기에 따른 증가율의 상한 |
| 분할 상환(amortized) | 여러 연산의 평균 비용 |
| 캐시 친화성(cache locality) | CPU 캐시에 잘 올라가는 메모리 접근 패턴 |

## Before / After

**Before — "그냥 dict 쓰자":**

```python
# 순서대로 처리해야 하는데 dict를 사용
events = {}
events["e1"] = 1; events["e2"] = 2; events["e3"] = 3
# 우선순위 처리 시 매번 정렬 필요 → 느림
```

**After — 워크로드 분석 후 힙 사용:**

```python
import heapq
events = []
heapq.heappush(events, (1, "e1"))
heapq.heappush(events, (2, "e2"))
# 매번 가장 우선순위 높은 것 O(log n)에 꺼냄
```

## 실습: 단계별로 따라하기

### 1단계: 워크로드 정의 5가지 질문

```python
# 새 자료구조를 고르기 전 항상 답해야 할 다섯 질문
workload_questions = [
    "1. 어떤 연산이 가장 자주 일어나는가?",
    "2. 입력의 크기는 어느 정도인가? (수십, 수만, 수억?)",
    "3. 데이터에 순서/정렬이 필요한가?",
    "4. 메모리 제약은 어느 정도인가?",
    "5. 동시성·영속성 요구가 있는가?",
]
for q in workload_questions:
    print(q)
```

이 다섯 질문에 답하면 후보 자료구조가 보통 1~2개로 좁혀집니다.

### 2단계: 자료구조별 핵심 시간 복잡도

```python
table = {
    "list (Python)":          {"인덱스": "O(1)",     "검색": "O(n)",     "끝 추가": "O(1)*", "맨 앞 추가": "O(n)"},
    "deque":                  {"인덱스": "O(n)",     "검색": "O(n)",     "끝 추가": "O(1)",  "맨 앞 추가": "O(1)"},
    "linked list":            {"인덱스": "O(n)",     "검색": "O(n)",     "끝 추가": "O(1)",  "맨 앞 추가": "O(1)"},
    "dict / set":             {"인덱스": "—",        "검색": "O(1)*",   "삽입": "O(1)*",  "정렬 순회": "O(n log n)"},
    "balanced BST (Sorted)":  {"인덱스": "O(log n)", "검색": "O(log n)", "삽입": "O(log n)", "정렬 순회": "O(n)"},
    "heap":                   {"인덱스": "—",        "최솟값": "O(1)",   "삽입": "O(log n)", "임의 검색": "O(n)"},
    "graph (adj list)":       {"이웃 순회": "O(deg)", "간선 존재": "O(deg)", "BFS/DFS": "O(V+E)"},
}

for ds, ops in table.items():
    print(f"{ds:<25} {ops}")
```

핫 패스의 연산이 어떤 자료구조에서 빠른지 표로 즉시 확인합니다. `*`는 분할 상환.

### 3단계: 의사결정 트리 코드로 구현

```python
def recommend_structure(workload):
    """워크로드 dict를 받아 추천 자료구조를 반환."""
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

워크로드를 명시적으로 표현하면 자료구조 선택은 거의 기계적인 결정이 됩니다.

### 4단계: 잘못된 선택의 비용 측정

```python
import time
from collections import deque

# 잘못된 선택: 큐로 list 사용
def queue_with_list(n):
    q = []
    for i in range(n):
        q.append(i)
    while q:
        q.pop(0)

# 올바른 선택: 큐로 deque 사용
def queue_with_deque(n):
    q = deque()
    for i in range(n):
        q.append(i)
    while q:
        q.popleft()

N = 50_000

start = time.perf_counter()
queue_with_list(N)
print(f"list: {(time.perf_counter() - start) * 1000:.0f} ms")

start = time.perf_counter()
queue_with_deque(N)
print(f"deque: {(time.perf_counter() - start) * 1000:.0f} ms")
```

같은 동작이지만 시간 차이는 100배 이상입니다. 빅오 분석을 무시하면 비용을 정량적으로 치르게 됩니다.

### 5단계: 실전 사례 모음

```python
cases = [
    ("LRU 캐시",            "dict + doubly linked list",      "O(1) get/put"),
    ("작업 스케줄러",        "heap (priority queue)",         "O(log n) 다음 작업"),
    ("실시간 친구 추천",     "graph + BFS (k-hop 이웃)",      "O(V + E)"),
    ("자동완성",             "trie (prefix tree)",            "O(prefix length)"),
    ("API 요청 중복 제거",   "set",                           "O(1) 검사"),
    ("DB 인덱스",            "B+Tree (균형 BST 일반화)",      "O(log n) 정렬 검색"),
    ("undo/redo",            "stack 두 개",                   "O(1) push/pop"),
    ("이벤트 기반 시뮬",     "heap (event queue)",           "O(log n) 다음 이벤트"),
]
for use_case, ds, complexity in cases:
    print(f"  {use_case:<22} → {ds:<35} ({complexity})")
```

실전 시스템은 단일 자료구조보다 여러 자료구조의 조합으로 만들어집니다. 각 컴포넌트의 워크로드를 따로 분석하는 것이 핵심입니다.

## 이 코드에서 주목할 점

- 자료구조 선택은 워크로드 분석에서 시작해야 합니다
- 같은 ADT라도 입력 패턴에 따라 적합한 구현이 다릅니다
- 잘못된 선택의 비용은 빅오 차이만큼 정확히 나타납니다
- 실전 시스템은 여러 자료구조의 조합으로 구성됩니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "dict 만능주의" | 정렬 순회나 우선순위 처리에서 비효율 | 워크로드별 적합 자료구조 선택 |
| 빅오만 보고 결정 | 상수와 캐시 친화성 무시 | 측정으로 검증 |
| 조기 최적화 | 복잡한 자료구조 도입 후 유지보수 폭탄 | 단순한 것부터, 측정 후 교체 |
| 라이브러리 무시 | 검증된 구현 대신 직접 작성 | 표준/잘 알려진 라이브러리 우선 |
| 한 자료구조에 모든 책임 | 한 자료구조로 모든 연산을 빠르게 | 조합(예: dict + linked list) |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스: 인덱스 종류(B+Tree, Hash, GIN, GiST)는 워크로드 기준 선택
- 캐시 시스템: TTL/LRU/LFU 등 정책별로 다른 자료구조 조합
- 검색 엔진: 역색인(inverted index) = 해시 테이블 + 정렬 리스트
- 추천 시스템: 사용자-아이템 그래프 + 임베딩(밀집 배열)
- 스트림 처리: 슬라이딩 윈도우 = deque, 상위 k개 = 최소 힙

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "기본부터 시작"합니다. 처음에는 list와 dict로 단순하게 만들고, 측정 후 병목이 보이면 더 정교한 자료구조로 교체합니다. 조기 최적화는 자료구조에서도 적입니다.

또한 시니어는 "자료구조의 한계가 시스템의 한계"임을 압니다. 잘못된 자료구조를 고르면 알고리즘 최적화나 인프라 확장으로 만회하기 어렵습니다. 그래서 핵심 데이터의 자료구조 선택은 설계 단계에서 시간을 들여 결정하고, 변경이 어렵다는 사실을 미리 인지합니다.

마지막으로 시니어는 "자료구조 = 도메인 모델"이라고 봅니다. 적절한 자료구조는 코드의 가독성과 유지보수성도 함께 개선합니다. 잘 고른 자료구조는 알고리즘을 짧고 명확하게 만듭니다.

## 체크리스트

- [ ] 워크로드를 정의하는 다섯 질문에 답할 수 있는가
- [ ] 핫 패스의 연산이 자료구조에서 어떤 시간 복잡도인지 파악했는가
- [ ] 빅오 외에 캐시 친화성·메모리·구현 복잡성을 함께 고려했는가
- [ ] 표준 라이브러리부터 시작하고 측정 후 교체하는 습관을 갖고 있는가
- [ ] 실전 시스템은 자료구조 조합이라는 사실을 이해했는가

## 연습 문제

1. 자신이 최근에 작성한 코드 한 편을 골라 사용된 모든 자료구조를 나열하고, 각각의 핫 패스 연산을 분석해 보세요. 더 적합한 자료구조가 있었나요?

2. LRU 캐시를 두 가지로 구현해 보세요. (a) `OrderedDict` 사용, (b) dict + 이중 연결 리스트 직접 구현. 두 방식의 시간 복잡도와 코드 복잡도를 비교합니다.

3. 1초마다 들어오는 100만 건 이벤트에서 (a) 가장 최근 1만 건을 유지, (b) 우선순위 상위 100건만 유지, (c) 카테고리별 카운트를 빠르게 조회하는 시스템을 설계해 보세요. 각각 어떤 자료구조 조합이 적합할까요?

## 정리 및 다음 단계

자료구조 선택은 컴퓨터과학 학습의 마지막 관문이자, 매일 반복되는 실전 결정입니다. "데이터의 모양"이 아니라 "연산의 빈도와 패턴"에서 시작해야 하며, 빅오뿐 아니라 캐시 친화성·메모리·구현 복잡성을 함께 고려해야 합니다. 단일 자료구조에 모든 책임을 지우려 하지 말고, 워크로드별로 조합하는 것이 실전적인 접근입니다.

이 시리즈에서 다룬 9가지 자료구조(배열·연결 리스트·스택·큐·해시 테이블·트리·BST·힙·그래프)는 거의 모든 알고리즘과 시스템 설계의 어휘입니다. 다음 단계는 알고리즘 시리즈입니다. 정렬, 탐색, 동적 계획법, 그래프 알고리즘 등 자료구조 위에서 동작하는 알고리즘들을 정리합니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- [스택과 큐](./04-stacks-and-queues.md)
- [해시 테이블](./05-hash-tables.md)
- [트리](./06-trees.md)
- [이진 탐색 트리](./07-binary-search-trees.md)
- [힙](./08-heaps.md)
- [그래프](./09-graphs.md)
- **자료구조 선택 기준 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)
- [System Design Primer — Data Structures](https://github.com/donnemartin/system-design-primer)

Tags: Computer Science, 자료구조, 선택 기준, 시간 복잡도, 워크로드, 설계
