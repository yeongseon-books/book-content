---
series: data-structures-101
episode: 4
title: "Data Structures 101 (4/10): 스택과 큐"
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
  - 스택
  - 큐
  - LIFO
  - FIFO
seo_description: LIFO와 FIFO라는 단순한 규칙이 시스템 동작을 결정하는 스택과 큐의 원리 및 구현 방식과 실무 활용 사례를 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (4/10): 스택과 큐

이 글은 Data Structures 101 시리즈의 네 번째 글입니다.


![Data Structures 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/04/04-01-big-picture.ko.png)
*Data Structures 101 4장 흐름 개요*

## 먼저 던지는 질문

- 스택과 큐라는 ADT는 각각 어떤 규칙을 가질까요?
- 파이썬에서는 어떤 자료구조로 스택과 큐를 구현하는 편이 자연스러울까요?
- 함수 호출, BFS, 메시지 큐 같은 시스템은 왜 이 두 구조 위에서 이해할 수 있을까요?

## 왜 중요한가

스택과 큐는 언어 실행 모델, 운영체제 스케줄링, 비동기 메시징의 기본 어휘입니다. 이 둘을 깊이 이해하지 못하면 재귀, DFS, BFS, 이벤트 루프를 운영 관점에서 설명하기 어렵습니다.

> 스택을 모르면 재귀를 디버깅하기 어렵고, 큐를 모르면 비동기 시스템을 설계하기 어렵습니다.

## 핵심 한눈에 보기

> 스택은 “위에 넣고 위에서 꺼내는” 모델이고, 큐는 “뒤로 들어오고 앞으로 나가는” 모델입니다. 두 ADT 모두 양 끝만 만지므로, 적절한 기반 구조를 쓰면 핵심 연산을 O(1)로 유지할 수 있습니다.

```text
Stack (LIFO)              Queue (FIFO)
        push                  enqueue       dequeue
          ↓                      ↓             ↑
       ┌─────┐              ┌─────────────────┐
       │  C  │ ← top         │ A → B → C → D │
       │  B  │                └─────────────────┘
       │  A  │              front           back
       └─────┘
          ↑
         pop
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 스택 | Last-In-First-Out ADT |
| 큐 | First-In-First-Out ADT |
| push / pop | 스택 삽입 / 제거 |
| enqueue / dequeue | 큐 삽입 / 제거 |
| deque | 양 끝 삽입·삭제를 모두 지원하는 일반화 구조 |

## 전후 비교

**Before — using a list as a queue directly:**

```python
queue = []
queue.append("A")
queue.append("B")
front = queue.pop(0)   # O(n) — every element shifts one slot
```

**After — using deque as a queue:**

```python
from collections import deque

queue = deque()
queue.append("A")
queue.append("B")
front = queue.popleft()   # O(1)
```

동작은 같아 보이지만 큐 길이가 길어질수록 차이는 급격히 커집니다. 파이썬에서 큐를 list로 구현하면 거의 항상 잘못된 출발입니다.

## 단계별로 따라하기

### 1단계: 스택 직접 구현

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if not self._data:
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def __len__(self):
        return len(self._data)

s = Stack()
for v in [1, 2, 3]:
    s.push(v)
print(s.pop(), s.pop(), s.pop())   # 3 2 1
```

배열의 한쪽 끝만 사용하면 각 연산이 O(1)이므로, 파이썬 list는 이미 좋은 스택입니다.

### 2단계: 큐 직접 구현

```python
from collections import deque

class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, value):
        self._data.append(value)

    def dequeue(self):
        if not self._data:
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def __len__(self):
        return len(self._data)

q = Queue()
for v in ["A", "B", "C"]:
    q.enqueue(v)
print(q.dequeue(), q.dequeue(), q.dequeue())   # A B C
```

`deque`는 양 끝이 모두 O(1)이므로 큐의 기반 구조로 이상적입니다.

### 3단계: 스택의 고전 예시 — 괄호 균형 검사

```python
def is_balanced(expr: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set("([{")
    stack = []

    for ch in expr:
        if ch in opens:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack

print(is_balanced("({[]})"))   # True
print(is_balanced("({[})"))    # False
print(is_balanced("(("))       # False
```

여는 괄호에서 push하고 닫는 괄호에서 pop해 대응 관계를 확인합니다. 파서와 컴파일러도 같은 원리 위에 서 있습니다.

### 4단계: 큐의 고전 예시 - 너비 우선 탐색

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

print(bfs(graph, "A"))   # ['A', 'B', 'C', 'D', 'E']
```

큐를 쓰면 가까운 노드부터 방문합니다. 같은 코드에서 큐 대신 스택을 넣으면 DFS가 됩니다.

### 5단계: 덱은 두 방향 연산을 모두 지원한다

```python
from collections import deque

dq = deque()
# 스택으로 사용
dq.append(1); dq.append(2); dq.append(3)
print(dq.pop())    # 3 (LIFO)

# 큐로 사용
dq.append(1); dq.append(2); dq.append(3)
print(dq.popleft()) # 1 (FIFO)
```

deque는 양 끝 조작이 모두 빠르기 때문에 스택과 큐를 모두 표현할 수 있는 일반화된 구조입니다.

## 이 코드에서 주목할 점

- 파이썬에서는 스택은 list, 큐는 deque가 표준 선택입니다.
- `list.pop(0)`로 큐를 구현하면 O(n)이므로 피해야 합니다.
- 스택과 큐의 차이는 “어느 끝에서 꺼내는가” 하나뿐입니다.
- DFS와 BFS의 구조적 차이도 결국 스택 vs 큐입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `list.pop(0)`로 큐를 구현함 | 연산마다 O(n) 이동 발생 | `collections.deque`를 사용합니다 |
| 빈 컨테이너에서 pop함 | `IndexError`가 발생함 | 길이 검사나 예외 처리를 넣습니다 |
| 재귀 깊이 한계를 무시함 | `RecursionError` 가능 | 명시적 스택으로 바꿉니다 |
| BFS에서 visited를 늦게 표시함 | 중복 방문 또는 무한 순회 | enqueue 시점에 바로 표시합니다 |
| 우선순위 큐를 일반 큐처럼 다룸 | 처리 순서가 틀어짐 | 별도로 힙을 사용합니다 |

## 실무에서는 이렇게 쓰입니다

- 함수 호출과 스택 트레이스는 스택 위에서 이해할 수 있습니다.
- 브라우저의 뒤로 가기와 앞으로 가기는 보통 두 개의 스택으로 모델링됩니다.
- RabbitMQ, Kafka 같은 메시지 시스템은 큐 개념의 실전 확장판입니다.
- 운영체제 스케줄러는 FIFO 큐와 우선순위 큐를 조합합니다.
- 그래프 탐색에서는 BFS가 큐를, DFS가 스택 또는 재귀를 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 재귀 함수를 보는 순간 머릿속에 호출 스택을 같이 그립니다. 입력 깊이가 커질 수 있다면 재귀 한계를 먼저 의식하고, 필요하면 곧바로 명시적 스택 기반 반복으로 바꿉니다.

또한 “작업 큐”라는 말도 뭉뚱그리지 않습니다. 단순 FIFO, 우선순위 큐, 지연 큐, backpressure가 있는 큐는 시스템 거동이 완전히 다릅니다. 이름이 같다고 같은 구조라고 가정하지 않습니다.

## 체크리스트

- [ ] LIFO와 FIFO의 의미를 설명할 수 있습니다
- [ ] 파이썬에서 큐를 list로 구현하면 안 되는 이유를 알고 있습니다
- [ ] 괄호 균형 검사처럼 스택이 자연스러운 문제를 구분할 수 있습니다
- [ ] BFS와 DFS의 차이가 자료구조 선택이라는 점을 이해했습니다
- [ ] deque가 스택과 큐를 모두 지원한다는 점을 알고 있습니다

## 연습 문제

1. 두 개의 스택으로 큐를 구현해 보세요. `enqueue`는 첫 번째 스택에 push하고, `dequeue`는 두 번째 스택이 비었을 때 첫 번째를 옮긴 뒤 pop합니다. 분할 상환 비용은 얼마일까요?

2. 스택으로 후위 표기식 계산기를 구현해 보세요. 예를 들어 `"3 4 + 2 *"`는 14가 되어야 합니다.

3. 위 BFS 코드에서 deque를 list 기반 스택으로 바꿔 보세요. DFS로 바뀌는지, 방문 순서는 어떻게 달라지는지 확인해 보세요.

## 정리 및 다음 단계

스택과 큐는 가장 단순하면서 가장 자주 만나는 ADT입니다. 스택은 LIFO로 함수 호출·파싱·DFS를 설명하고, 큐는 FIFO로 BFS·스케줄링·메시징을 설명합니다. 파이썬에서는 스택은 list, 큐는 `collections.deque`가 표준 선택입니다. 차이는 “어느 끝에서 꺼내는가” 하나지만, 그 하나가 시스템의 동작 방식을 완전히 바꿉니다.

다음 글에서는 키로 값을 거의 즉시 찾게 해 주는 해시 테이블을 다룹니다. 평균 O(1) 탐색이 어떻게 가능한지, 충돌은 어떻게 처리하는지 이어서 보겠습니다.


## 구현 관점 보강: 복잡도와 선택 기준

자료구조를 비교할 때는 평균 시간 복잡도만으로 결론을 내리면 정확도가 떨어집니다. 실제 시스템에서는 데이터 분포, 갱신 비율, 메모리 제약, 동시성 요구가 동시에 작동하기 때문입니다. 따라서 아래 표처럼 연산별 상한과 운영 조건을 함께 보는 기준이 필요합니다.

| 구조 | 조회 | 삽입 | 삭제 | 메모리 특성 | 적합한 상황 |
| --- | --- | --- | --- | --- | --- |
| 배열/동적 배열 | O(1) 인덱스, O(n) 탐색 | 끝 O(1) amortized, 중간 O(n) | 중간 O(n) | 연속 메모리, 캐시 효율 우수 | 읽기 중심, 랜덤 액세스 필요 |
| 연결 리스트 | O(n) | 노드 위치 확보 시 O(1) | 노드 위치 확보 시 O(1) | 포인터 오버헤드 큼 | 중간 삽입/삭제 빈번 |
| 해시 테이블 | 평균 O(1), 최악 O(n) | 평균 O(1) | 평균 O(1) | 버킷/재해시 비용 존재 | 키 기반 빠른 조회 |
| 균형 트리 | O(log n) | O(log n) | O(log n) | 포인터 구조, 정렬 유지 | 범위 질의, 순서 보존 |

구현 단계에서는 연산 정의를 코드 시그니처로 먼저 고정하는 방식이 안전합니다. 예를 들어 `insert`, `remove`, `contains`, `iterate`의 사전/사후 조건을 먼저 문서화하고, 그 뒤에 내부 저장 구조를 바꾸면 테스트 재사용성이 크게 올라갑니다. 같은 인터페이스에 배열 기반 구현과 링크 기반 구현을 각각 붙여 벤치마크하면, 개념 설명에서 보던 복잡도 표가 실제 지연 시간으로 어떻게 드러나는지 확인할 수 있습니다.

또한 사용 사례 비교는 데이터 흐름 단위로 해야 합니다. 예를 들어 이벤트 로그 파이프라인에서는 "대량 append + 배치 스캔" 패턴이 많아 동적 배열이 유리하지만, 작업 스케줄러에서는 "우선순위 갱신 + 최소값 추출"이 반복되어 힙이 더 적합합니다. 반대로 온라인 추천 시스템의 피처 저장소는 키 조회 비율이 매우 높아 해시 기반 구조가 기본 선택이 됩니다.

실습 팁으로는 동일한 입력 집합에 대해 최소 두 가지 구조를 구현하고, 다음 항목을 비교 기록하는 방식이 좋습니다: (1) 연산당 평균 지연 시간, (2) p95 지연 시간, (3) 메모리 사용량, (4) 구현 복잡도. 이 네 가지를 같이 보면 단순 Big-O 표기법이 놓치는 현실 제약까지 반영한 결정을 내릴 수 있습니다.

실무 적용 관점에서는 입력 데이터의 크기뿐 아니라 업데이트 패턴, 동시 접근, 메모리 상한을 함께 고려해 구조를 선택해야 안정적인 성능이 나옵니다.


## 실전 앵커: 구현과 복잡도 검증

개념을 정확히 이해하려면 설명 문장만 보는 것으로는 부족합니다. 손으로 구현하고, 연산 단위를 측정하고, 메모리 배치를 눈으로 그려 보는 과정이 함께 있어야 합니다. 아래 앵커는 이 시리즈 전체에서 공통으로 재사용할 수 있는 검증 틀입니다.

### 파이썬 미니 구현 묶음

```python
from collections import deque

# 1) 리스트: 끝 append/pop은 빠르고, 앞쪽 연산은 느립니다.
arr = []
arr.append(10)
arr.append(20)
arr.pop()

# 2) 스택: list로 LIFO 구현
stack = []
stack.append('A')
stack.append('B')
stack.pop()

# 3) 큐: deque로 FIFO 구현
queue = deque()
queue.append('job-1')
queue.append('job-2')
queue.popleft()

# 4) 트리 노드
class Node:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

# 5) 그래프 인접 리스트와 너비 우선 탐색
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['D'],
    'D': []
}

def bfs(start):
    seen = {start}
    q = deque([start])
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in graph[cur]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order
```

### 연산 복잡도 비교표

| 구조 | 핵심 연산 | 평균 시간 | 최악 시간 | 메모리 관찰 포인트 |
| --- | --- | --- | --- | --- |
| 동적 배열 | 인덱스 조회 | O(1) | O(1) | 연속 메모리, 캐시 친화적 |
| 동적 배열 | 중간 삽입/삭제 | O(n) | O(n) | 이동 비용이 성능 병목 |
| 스택 | push/pop | O(1) | O(1) | 한쪽 끝 연산으로 단순 |
| 큐(덱) | enqueue/dequeue | O(1) | O(1) | 양 끝 연산이 안정적 |
| 트리(균형) | 탐색/삽입/삭제 | O(log n) | O(log n) | 높이 유지가 관건 |
| 그래프 | 순회(BFS/DFS) | O(V+E) | O(V+E) | 정점/간선 수에 비례 |

### 메모리 배치 그림

```text
동적 배열
[0][1][2][3][4]  (연속 주소)
  |  |  |  |
  +-- 인덱스로 즉시 접근

연결 리스트
[값|다음] -> [값|다음] -> [값|다음]
   ^ 포인터를 따라 이동

트리
        [8]
       /   \
     [3]   [10]
     / \
   [1] [6]

그래프(인접 리스트)
A: B, C
B: D
C: D
D: (없음)
```

### 문제 연결 지도

| 유형 | 대표 문제 | 이 글의 관점으로 보는 핵심 |
| --- | --- | --- |
| 배열/투포인터 | LeetCode 1, 88, 283 | 인덱스 이동과 덮어쓰기 비용 관리 |
| 스택 | LeetCode 20, 155, 739 | 상태를 되돌릴 때 LIFO가 자연스러운가 |
| 큐/BFS | LeetCode 102, 994, 542 | 레벨 단위 확산과 최단 거리 |
| 트리 | LeetCode 104, 226, 236 | 재귀와 반복 중 호출 깊이 제어 |
| 그래프 | LeetCode 200, 207, 417 | 방문 집합 설계와 순회 순서 |

실무에서 성능 이슈가 발생하면, 먼저 연산을 위 표의 행으로 대응시켜 병목을 분류한 뒤 구현을 교체하는 순서로 접근하는 편이 안전합니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

스택과 큐는 기능이 단순하지만 운영 사고에서 자주 드러납니다. 재시도 작업이 계속 쌓일 때는 큐 길이와 처리율을 같이 봐야 하고, 파싱 실패가 증가할 때는 스택 깊이 분포를 확인해야 합니다. 자료구조를 선택했다면 관찰 지표까지 같이 정의해야 문제 대응 속도가 빨라집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **스택과 큐라는 ADT는 각각 어떤 규칙을 가질까요?**
  - 스택은 마지막에 넣은 값을 먼저 꺼내는 LIFO 규칙이라 `push` 뒤 `pop` 결과가 3, 2, 1로 나옵니다. 큐는 먼저 들어온 값을 먼저 꺼내는 FIFO 규칙이라 `enqueue`한 `A, B, C`가 `dequeue`에서 같은 순서로 나오는 구조입니다.
- **파이썬에서는 어떤 자료구조로 스택과 큐를 구현하는 편이 자연스러울까요?**
  - 스택은 한쪽 끝 `append`와 `pop`만 빠르게 쓰면 되므로 파이썬 `list`가 자연스럽습니다. 큐는 `list.pop(0)`가 O(n)이라 부적합하고, 양 끝 연산이 O(1)인 `collections.deque`가 본문 `Queue` 구현처럼 표준 선택입니다.
- **함수 호출, BFS, 메시지 큐 같은 시스템은 왜 이 두 구조 위에서 이해할 수 있을까요?**
  - 괄호 균형 검사는 여는 괄호를 push하고 닫는 괄호에서 pop하는 스택 패턴이어서 파서와 호출 스택을 설명하는 데 그대로 연결됩니다. 반대로 BFS는 `deque.popleft()`로 먼저 들어온 노드부터 처리하므로, 메시지 큐나 작업 대기열처럼 순서가 중요한 시스템을 이해하는 기본 모델이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- **스택과 큐 (현재 글)**
- 해시 테이블 (예정)
- 트리 (예정)
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Stacks and Queues](https://opendatastructures.org/ods-python/3_3_SEList_Space_Efficient_.html)
- [Python `collections.deque` docs](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia — Stack (abstract data type)](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
- [Wikipedia — Queue (abstract data type)](https://en.wikipedia.org/wiki/Queue_(abstract_data_type))

Tags: Computer Science, 자료구조, 스택, 큐, LIFO, FIFO
