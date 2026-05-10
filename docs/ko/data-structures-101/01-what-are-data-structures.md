---
series: data-structures-101
episode: 1
title: 자료구조란 무엇인가?
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
  - 추상 자료형
  - 알고리즘 기초
  - 시간 복잡도
  - 전공 개요
seo_description: 자료구조가 무엇인지, 왜 같은 데이터를 다루는데도 자료구조 선택이 성능을 결정하는지 전체 그림을 그립니다.
last_reviewed: '2026-05-04'
---

# 자료구조란 무엇인가?

> Data Structures 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 데이터를 다루는데도 어떤 코드는 1초 만에 끝나고 어떤 코드는 1시간이 걸립니다. 무엇이 차이를 만들까요?

> 자료구조는 데이터를 메모리에 어떤 모양으로 배치하고, 어떤 연산을 효율적으로 지원할지를 정의합니다. 같은 "사용자 1,000만 명 검색하기"라는 작업도 배열에서 찾으면 평균 500만 번 비교가 필요하지만, 해시 테이블에서 찾으면 한 번이면 충분합니다. 이 글에서는 자료구조의 정의, 추상 자료형(ADT)과의 차이, 그리고 시리즈 전체에서 다룰 자료구조들의 지도를 그립니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 자료구조와 추상 자료형(ADT)의 관계
- 자료구조 선택이 성능에 미치는 영향
- 시리즈에서 다룰 9가지 자료구조의 큰 그림
- 자료구조를 평가할 때 사용하는 기준

## 왜 중요한가

코드를 잘 짠다는 것은 결국 "데이터를 어떻게 표현할 것인가"를 잘 결정한다는 뜻입니다. 알고리즘은 자료구조 위에서 동작합니다. 잘못된 자료구조를 고르면 아무리 좋은 알고리즘을 써도 느려집니다.

> 알고리즘 + 자료구조 = 프로그램 — Niklaus Wirth

이 시리즈는 9가지 핵심 자료구조의 동작 원리, 시간/공간 복잡도, 그리고 언제 어떤 것을 선택해야 하는지를 정리합니다.

## 개념 한눈에 보기

> 자료구조는 "데이터의 논리적 구조"와 "메모리상의 물리적 구조" 두 층으로 이해해야 합니다. ADT가 무엇을 할 수 있는지를 정의하고, 자료구조는 그것을 어떻게 구현할지를 결정합니다.

```text
            ADT (추상 자료형)
              "무엇을 할 수 있는가"
                    |
        ┌───────────┼───────────┐
        |           |           |
      List         Set         Map
        |           |           |
   ┌────┴────┐  ┌───┴───┐  ┌───┴───┐
  배열    연결리스트  해시  트리   해시  트리
        |
   (구체 자료구조: 메모리 배치 방식)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 자료구조(data structure) | 데이터를 메모리에 저장하고 조작하는 구체적 방식 |
| 추상 자료형(ADT) | 데이터와 연산을 인터페이스 수준에서 정의한 것 |
| 시간 복잡도 | 입력 크기에 따른 연산 시간의 증가율 |
| 공간 복잡도 | 입력 크기에 따른 메모리 사용량의 증가율 |
| 분할 상환(amortized) | 연산을 여러 번 수행했을 때의 평균 비용 |

## Before / After

**Before — 자료구조를 의식하지 않을 때:**

```python
# 1,000만 명의 사용자에서 특정 ID를 찾는다
users = [{"id": i, "name": f"user{i}"} for i in range(10_000_000)]


def find_user(target_id: int):
    for user in users:
        if user["id"] == target_id:
            return user
    return None


# 평균 500만 번 비교, 최악 1,000만 번
```

**After — 자료구조를 의식할 때:**

```python
# 같은 데이터를 해시 테이블로 인덱싱한다
users = {i: {"id": i, "name": f"user{i}"} for i in range(10_000_000)}


def find_user(target_id: int):
    return users.get(target_id)


# 평균 1번 비교
```

## 실습: 단계별로 따라하기

### 1단계: 같은 데이터, 다른 자료구조

```python
import time

N = 1_000_000

list_data = list(range(N))
set_data = set(list_data)


def measure(label, fn):
    start = time.perf_counter()
    fn()
    elapsed = (time.perf_counter() - start) * 1000
    print(f"{label}: {elapsed:.2f} ms")


measure("list 검색", lambda: (N - 1) in list_data)
measure("set 검색", lambda: (N - 1) in set_data)
```

리스트는 처음부터 끝까지 훑어야 하지만 집합은 해시로 즉시 위치를 찾습니다. 데이터의 양이 많아질수록 격차는 더 벌어집니다.

### 2단계: ADT와 자료구조 분리하기

```python
from abc import ABC, abstractmethod


class Stack(ABC):
    """ADT: 마지막에 넣은 것을 먼저 꺼낸다."""

    @abstractmethod
    def push(self, value): ...

    @abstractmethod
    def pop(self): ...


class ListStack(Stack):
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        return self._data.pop()


class LinkedStack(Stack):
    def __init__(self):
        self._head = None

    def push(self, value):
        self._head = (value, self._head)

    def pop(self):
        value, self._head = self._head
        return value
```

`Stack`이라는 ADT는 동일하지만 구현은 두 가지로 다릅니다. 사용하는 쪽은 인터페이스만 알면 됩니다.

### 3단계: 시간 복잡도 비교표

```python
operations = {
    "Array (배열)":      {"검색": "O(n)",     "삽입": "O(n)", "삭제": "O(n)"},
    "Dynamic Array":      {"검색": "O(n)",     "삽입": "O(1)*", "삭제": "O(n)"},
    "Linked List":        {"검색": "O(n)",     "삽입": "O(1)",  "삭제": "O(1)"},
    "Hash Table":         {"검색": "O(1)",     "삽입": "O(1)",  "삭제": "O(1)"},
    "Balanced BST":       {"검색": "O(log n)", "삽입": "O(log n)", "삭제": "O(log n)"},
    "Heap":               {"검색": "O(n)",     "삽입": "O(log n)", "최솟값": "O(1)"},
}

for ds, ops in operations.items():
    print(f"{ds:<20} {ops}")
```

`*` 표시는 분할 상환 비용입니다. 동적 배열은 가끔 비싼 재할당이 있지만 평균적으로는 O(1)입니다.

### 4단계: 자료구조 선택의 결과

```python
# 시나리오: 1초마다 들어오는 이벤트를 우선순위에 따라 처리한다
import heapq

events = []
# 잘못된 선택: 매번 정렬
def add_wrong(priority, event):
    events.append((priority, event))
    events.sort()

# 올바른 선택: 힙
heap = []
def add_right(priority, event):
    heapq.heappush(heap, (priority, event))


# add_wrong은 매 삽입마다 O(n log n)
# add_right는 매 삽입마다 O(log n)
# 하루 100만 이벤트라면 1,000배 차이
```

### 5단계: 시리즈의 로드맵

```python
roadmap = [
    (1, "자료구조란 무엇인가?", "전체 그림"),
    (2, "배열과 동적 배열", "고정/가변 길이의 연속 메모리"),
    (3, "연결 리스트", "포인터로 이어진 노드들"),
    (4, "스택과 큐", "LIFO와 FIFO"),
    (5, "해시 테이블", "키로 즉시 접근"),
    (6, "트리", "계층 구조의 표현"),
    (7, "이진 탐색 트리", "정렬된 트리에서 빠른 탐색"),
    (8, "힙", "우선순위 큐의 구현"),
    (9, "그래프", "임의의 관계 모델링"),
    (10, "자료구조 선택 기준", "언제 무엇을 쓸 것인가"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## 이 코드에서 주목할 점

- 같은 ADT라도 구현체에 따라 성능이 크게 달라집니다
- 시간 복잡도는 입력이 커질 때의 증가율을 봅니다 (작은 입력에서는 상수 시간이 더 중요할 수도 있습니다)
- "분할 상환"은 동적 배열·해시 테이블처럼 가끔 비싼 연산을 하는 자료구조를 분석할 때 사용합니다
- 자료구조 선택은 알고리즘 선택만큼이나 성능에 결정적입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| ADT와 구현을 혼동 | "Stack은 배열이다"라고 단정 | ADT는 인터페이스, 구현은 다양함을 인지 |
| 작은 입력만 보고 판단 | "리스트가 더 빠르네" | 입력이 커졌을 때의 증가율을 봅니다 |
| 빅오만 보고 결정 | 상수 항을 무시 | 캐시 친화성·실측을 함께 고려합니다 |
| 한 자료구조만 고집 | 모든 문제에 dict | 문제별 패턴에 맞게 선택합니다 |
| 공간 복잡도 무시 | 메모리 부족으로 다운 | 시간만큼 공간도 분석합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스는 B-Tree(트리의 한 종류)로 구현되어 빠른 검색을 제공합니다
- 운영체제의 프로세스 스케줄러는 우선순위 큐(힙)로 다음 작업을 결정합니다
- 웹 브라우저의 뒤로가기는 스택 자료구조를 사용합니다
- 라우팅 테이블, 의존성 그래프, 소셜 네트워크는 모두 그래프로 모델링됩니다
- 메모리 캐시(Redis, Memcached)는 해시 테이블이 핵심 구조입니다

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "어떤 자료구조를 쓸까"를 묻기 전에 "어떤 연산이 가장 자주 일어나는가"를 묻습니다. 검색이 많은가, 삽입이 많은가, 정렬된 순회가 필요한가. 워크로드를 먼저 정의하면 자료구조는 거의 자동으로 결정됩니다.

또한 시니어는 "기본 자료형 + dict + list"로 시작합니다. 처음부터 트리·힙을 쓰지 않습니다. 측정 후 병목이 보일 때만 더 정교한 자료구조로 교체합니다. 조기 최적화는 자료구조에서도 적입니다.

## 체크리스트

- [ ] 자료구조와 추상 자료형(ADT)의 차이를 설명할 수 있는가
- [ ] 같은 ADT를 여러 자료구조로 구현할 수 있다는 것을 이해했는가
- [ ] 시간 복잡도가 입력 크기에 따른 증가율임을 알고 있는가
- [ ] 분할 상환이 무엇이고 언제 적용되는지 파악했는가
- [ ] 시리즈 전체의 로드맵을 확인했는가

## 연습 문제

1. 일상에서 본 시스템(예: 줄 서기, 책장, 전화번호부)을 하나 고르고 어떤 자료구조에 해당하는지 분석해 보세요. 어떤 연산이 빠르고 어떤 연산이 느린가요?

2. 위 1단계의 측정 코드를 N을 10배씩 늘려가며 실행해 보세요. list와 set의 검색 시간 차이가 어떻게 변하나요? 그래프로 그릴 수 있다면 더 좋습니다.

3. 자신이 최근에 작성한 코드를 하나 골라 사용된 자료구조를 모두 나열해 보세요. 더 적합한 자료구조가 있었는지 검토해 봅니다.

## 정리 및 다음 단계

자료구조는 데이터를 메모리에 어떻게 배치하고 어떤 연산을 효율적으로 지원할지 결정합니다. 같은 데이터를 다루더라도 자료구조 선택에 따라 성능이 수십~수천 배 차이납니다. 추상 자료형은 인터페이스를, 자료구조는 구현을 정의합니다. 두 개념을 분리해서 보면 코드 설계가 훨씬 명확해집니다.

다음 글에서는 가장 기본적인 자료구조인 "배열"을 살펴봅니다. 고정 크기 배열과 동적 배열이 어떻게 다르며, 파이썬의 list가 내부적으로 어떻게 동작하는지 알아봅니다.

<!-- toc:begin -->
- **자료구조란 무엇인가? (현재 글)**
- 배열과 동적 배열 (예정)
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

- [Introduction to Algorithms (CLRS) — Cormen et al.](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Open Data Structures — Pat Morin](https://opendatastructures.org/)
- [Wikipedia — Data Structure](https://en.wikipedia.org/wiki/Data_structure)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)
