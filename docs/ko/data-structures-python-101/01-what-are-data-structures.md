---
series: data-structures-python-101
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
  - Python
  - 자료구조
  - Data Structures
  - 알고리즘
  - 프로그래밍 기초
seo_description: 자료구조의 개념과 Python에서 자료구조가 중요한 이유를 설명합니다.
last_reviewed: '2026-05-04'
---

# 자료구조란 무엇인가?

> Data Structures with Python 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 데이터를 변수에 담으면 끝 아닌가요? 왜 자료구조를 따로 배워야 할까요?

> 데이터가 많아지면 변수 하나로는 부족합니다. 어떤 구조에 데이터를 담느냐에 따라 검색, 삽입, 삭제 속도가 수백 배 달라집니다. 이 글에서는 자료구조가 무엇인지, 왜 중요한지, Python에서 어떤 자료구조를 제공하는지 개관합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 자료구조의 정의와 역할
- 자료구조 선택이 성능에 미치는 영향
- Python 내장 자료구조의 종류와 특징
- 이 시리즈에서 다룰 자료구조 로드맵

## 왜 중요한가

프로그램은 데이터를 입력받아 처리하고 결과를 출력합니다. 데이터를 어떤 구조로 저장하느냐에 따라 같은 작업도 0.001초에 끝날 수 있고, 10초가 걸릴 수도 있습니다. 자료구조는 이 차이를 만드는 핵심입니다.

> 자료구조는 데이터를 효율적으로 저장하고 접근하기 위한 구조화 방법입니다. 올바른 자료구조를 선택하면 코드가 간결해지고 성능이 향상됩니다.

코딩 면접에서 자료구조 질문이 빠지지 않는 이유도 여기에 있습니다. 자료구조를 이해하면 문제를 보는 시야가 넓어지고, 최적의 해법을 설계할 수 있습니다.

## 핵심 개념 잡기

> 자료구조 = 데이터를 조직화하여 효율적으로 접근·수정할 수 있게 하는 방법

```
[변수 하나]        →  값 1개 저장
[리스트]           →  순서 있는 값 N개 저장
[딕셔너리]         →  키-값 쌍 N개 저장 (O(1) 검색)
[트리]             →  계층 구조 표현 (O(log n) 검색)
[그래프]           →  관계 네트워크 표현
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 자료구조 | 데이터를 조직화하는 방법으로, 삽입·삭제·검색 효율을 결정합니다 |
| 시간 복잡도 | 연산이 데이터 크기에 따라 얼마나 오래 걸리는지 나타냅니다 |
| 공간 복잡도 | 자료구조가 얼마나 많은 메모리를 사용하는지 나타냅니다 |
| 추상 자료형(ADT) | 연산의 명세만 정의하고 구현은 숨기는 개념입니다 |
| 내장 자료구조 | Python이 기본으로 제공하는 list, dict, set, tuple 등입니다 |

## Before / After

자료구조를 모를 때와 알 때의 차이를 비교합니다.

```python
# before: 리스트에서 값을 검색 — O(n)
users = ["alice", "bob", "charlie", "diana"]
if "charlie" in users:
    print("found")
```

```python
# after: set으로 검색 — O(1)
users = {"alice", "bob", "charlie", "diana"}
if "charlie" in users:
    print("found")
```

## 단계별 실습

### Step 1: 리스트와 set의 검색 속도 비교

```python
import time

data_list = list(range(1_000_000))
data_set = set(range(1_000_000))

target = 999_999

start = time.perf_counter()
_ = target in data_list
list_time = time.perf_counter() - start

start = time.perf_counter()
_ = target in data_set
set_time = time.perf_counter() - start

print(f"list 검색: {list_time:.6f}초")
print(f"set  검색: {set_time:.6f}초")
print(f"set이 {list_time / set_time:.0f}배 빠릅니다")
```

### Step 2: dict로 키-값 매핑 확인

```python
scores = {"alice": 95, "bob": 82, "charlie": 90}
print(scores["bob"])          # 82 — O(1) 접근
print(scores.get("diana", 0)) # 0 — 키 없을 때 기본값
```

### Step 3: tuple로 불변 데이터 표현

```python
point = (3, 4)
# point[0] = 5  # TypeError — tuple은 수정 불가
print(f"x={point[0]}, y={point[1]}")
```

### Step 4: 리스트를 스택처럼 사용

```python
stack = []
stack.append("a")
stack.append("b")
stack.append("c")
print(stack.pop())  # "c" — 마지막에 넣은 것이 먼저 나옵니다
print(stack.pop())  # "b"
```

### Step 5: collections 모듈 살펴보기

```python
from collections import deque, Counter, defaultdict

# deque: 양쪽 끝에서 O(1) 삽입/삭제
dq = deque([1, 2, 3])
dq.appendleft(0)
print(list(dq))  # [0, 1, 2, 3]

# Counter: 빈도 세기
counter = Counter("abracadabra")
print(counter.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]

# defaultdict: 기본값이 있는 dict
dd = defaultdict(list)
dd["fruits"].append("apple")
print(dd)  # defaultdict(<class 'list'>, {'fruits': ['apple']})
```

## 이 코드에서 주목할 점

- list의 `in` 연산은 O(n)이지만 set의 `in` 연산은 O(1)입니다
- dict는 키로 값을 O(1)에 조회할 수 있어 검색이 많은 상황에 적합합니다
- tuple은 불변이므로 dict의 키나 set의 원소로 사용할 수 있습니다
- collections 모듈은 특수 목적의 자료구조를 제공합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 곳에 list 사용 | 검색이 O(n)이라 대규모 데이터에서 느립니다 | 검색이 잦으면 set이나 dict를 사용합니다 |
| dict 키에 list 사용 | list는 mutable이라 해시 불가합니다 | tuple로 변환하여 키로 사용합니다 |
| 자료구조 크기를 고려하지 않음 | 메모리 부족이 발생할 수 있습니다 | 데이터 규모에 맞는 자료구조를 선택합니다 |
| 삽입 순서에 의존하지만 set 사용 | set은 순서를 보장하지 않습니다 | 순서가 필요하면 list나 OrderedDict를 사용합니다 |
| 시간 복잡도를 무시하고 구현 | 작은 데이터에서는 문제없지만 규모가 커지면 장애가 됩니다 | 연산별 시간 복잡도를 확인하고 자료구조를 선택합니다 |

## 실무에서 이렇게 쓰입니다

- 캐시 시스템에서 dict를 사용하여 O(1) 조회를 구현합니다
- 중복 제거 시 set을 사용하여 고유값만 남깁니다
- 작업 큐에서 deque를 사용하여 FIFO 처리를 구현합니다
- 설정값을 tuple로 저장하여 실수로 변경되는 것을 방지합니다
- 로그 분석에서 Counter를 사용하여 빈도를 집계합니다

## 현업 개발자는 이렇게 생각합니다

경험 있는 개발자는 코드를 작성하기 전에 "이 데이터를 어떤 구조로 담을까?"를 먼저 고민합니다. 자료구조 선택이 전체 아키텍처의 성능과 가독성을 결정하기 때문입니다.

실무에서는 Python 내장 자료구조만으로 대부분의 문제를 해결할 수 있습니다. list, dict, set, tuple의 특성을 정확히 이해하고, 상황에 맞게 선택하는 것이 핵심입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **연산 비용 우선** — 선택 기준은 사용 패턴별 연산의 평균/최악 비용입니다.
- **표준 라이브러리** — list/dict/set/heapq/collections로 거의 모든 문제를 풉니다.
- **메모리도 비용** — 공간 복잡도와 캐시 친화도도 함께 봅니다.
- **불변성 활용** — 불변 자료구조가 동시성·테스트를 단순화합니다.
- **측정** — 이론보다 실측이 최종 결정 근거입니다.

## 체크리스트

- [ ] 자료구조의 정의와 역할을 설명할 수 있다
- [ ] list, dict, set, tuple의 차이를 설명할 수 있다
- [ ] 검색이 잦은 상황에서 set이 list보다 유리한 이유를 설명할 수 있다
- [ ] collections 모듈의 deque, Counter, defaultdict를 사용할 수 있다
- [ ] 시간 복잡도 개념을 이해하고 자료구조 선택에 활용할 수 있다

## 연습 문제

1. 100만 개의 정수 리스트에서 특정 값을 찾는 코드를 list와 set으로 각각 작성하고, 실행 시간을 비교하세요.
2. 문자열 리스트에서 중복을 제거하되 원래 순서를 유지하는 함수를 작성하세요. (힌트: dict.fromkeys 활용)
3. 학생 이름-점수 데이터를 dict에 저장하고, 점수가 높은 순서로 정렬하여 출력하는 코드를 작성하세요.

## 정리 및 다음 글 안내

자료구조는 데이터를 효율적으로 저장하고 접근하기 위한 핵심 개념입니다. Python은 list, dict, set, tuple 등 강력한 내장 자료구조를 제공합니다. 다음 글에서는 가장 기본이 되는 배열과 리스트를 깊이 살펴봅니다.

<!-- toc:begin -->
- **자료구조란 무엇인가? (현재 글)**
- 배열과 리스트 (예정)
- 스택과 큐 (예정)
- 해시 테이블과 dict (예정)
- 연결 리스트 (예정)
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Problem Solving with Algorithms and Data Structures using Python](https://runestone.academy/ns/books/published/pythonds3/index.html)
- [Real Python — Common Python Data Structures](https://realpython.com/python-data-structures/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
