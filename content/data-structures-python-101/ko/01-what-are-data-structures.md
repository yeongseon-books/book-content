---
series: data-structures-python-101
episode: 1
title: 자료구조란 무엇인가?
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
  - Data Structures
  - 알고리즘
  - 프로그래밍 기초
seo_description: 자료구조가 왜 중요한지와 Python 내장 구조의 선택 기준을 설명합니다.
last_reviewed: '2026-05-12'
---

# 자료구조란 무엇인가?

이 글은 Data Structures with Python 101 시리즈의 첫 번째 글입니다.

## 이 글에서 다룰 문제

- 자료구조는 정확히 무엇이고 왜 따로 배워야 할까요?
- 같은 데이터를 저장해도 자료구조에 따라 성능이 왜 크게 달라질까요?
- Python이 기본으로 제공하는 list, dict, set, tuple은 각각 어떤 역할에 맞을까요?
- 이 시리즈에서 앞으로 어떤 구조를 어떤 순서로 익히게 될까요?

> 멘탈 모델: 자료구조는 “데이터를 어디에 담을까”의 문제가 아니라 “이 데이터를 앞으로 어떻게 읽고, 찾고, 바꿀까”를 미리 설계하는 일입니다.

## 왜 이 글이 중요한가

프로그램은 데이터를 입력받고, 처리하고, 다시 출력합니다. 이때 데이터를 어떤 구조로 저장하느냐에 따라 같은 기능도 밀리초 안에 끝날 수 있고, 불필요하게 오래 걸릴 수도 있습니다. 자료구조는 그 차이를 만드는 가장 기본적인 레버입니다.

> 자료구조는 데이터를 효율적으로 저장하고 접근하고 수정하기 위한 조직화 방식입니다. 올바른 자료구조를 고르면 코드가 더 단순해지고, 성능도 더 안정적으로 나옵니다.

자료구조가 코딩 면접의 단골 주제인 이유도 여기에 있습니다. 단순히 문제 풀이 기술을 묻는 것이 아니라, 데이터를 어떻게 모델링하고 연산 비용을 어떻게 판단하는지를 보기 때문입니다. 현업에서도 상황은 같습니다. 성능 문제는 종종 복잡한 알고리즘보다, 잘못 고른 자료구조 하나에서 시작합니다.

## 핵심 개념 한눈에 보기

> 자료구조 = 데이터를 효율적으로 접근·수정할 수 있도록 정리하는 방식

```text
[single variable]    →  stores 1 value
[list]               →  stores N values in order
[dict]               →  stores N key-value pairs (O(1) lookup)
[tree]               →  represents hierarchies (O(log n) search)
[graph]              →  represents networks of relationships
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 자료구조 | 데이터를 어떻게 저장하고 꺼낼지를 정하는 구조로, 삽입·삭제·검색 비용을 좌우합니다 |
| 시간 복잡도 | 데이터 크기가 커질 때 연산 시간이 어떻게 증가하는지 설명하는 개념입니다 |
| 공간 복잡도 | 자료구조가 데이터를 저장하기 위해 얼마나 많은 메모리를 쓰는지 설명합니다 |
| 추상 자료형(ADT) | 구현 세부사항을 숨기고 “어떤 연산이 가능한가”만 정의하는 개념입니다 |
| 내장 자료구조 | Python이 기본으로 제공하는 list, dict, set, tuple 같은 구조입니다 |

## Before / After

자료구조를 모르고 코드를 쓰는 경우와, 연산 특성을 고려해 구조를 고른 경우를 비교해 보겠습니다.

```python
# before: searching in a list — O(n)
users = ["alice", "bob", "charlie", "diana"]
if "charlie" in users:
    print("found")
```

```python
# after: searching in a set — O(1)
users = {"alice", "bob", "charlie", "diana"}
if "charlie" in users:
    print("found")
```

list는 순서 보존에는 좋지만 검색은 선형으로 진행됩니다. 반면 set은 순서를 포기하는 대신 membership test를 매우 빠르게 수행합니다. 자료구조를 배운다는 것은 이런 교환관계를 이해하는 일입니다.

## 단계별 실습

### Step 1: Compare search speed between list and set

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

print(f"list search: {list_time:.6f}s")
print(f"set  search: {set_time:.6f}s")
print(f"set is {list_time / set_time:.0f}x faster")
```

### Step 2: Verify O(1) key-value lookup with dict

```python
scores = {"alice": 95, "bob": 82, "charlie": 90}
print(scores["bob"])          # 82 — O(1) access
print(scores.get("diana", 0)) # 0 — default when key is missing
```

### Step 3: Represent immutable data with tuple

```python
point = (3, 4)
# point[0] = 5  # TypeError — tuples are immutable
print(f"x={point[0]}, y={point[1]}")
```

### Step 4: Use a list as a stack

```python
stack = []
stack.append("a")
stack.append("b")
stack.append("c")
print(stack.pop())  # "c" — last in, first out
print(stack.pop())  # "b"
```

### Step 5: Explore the collections module

```python
from collections import deque, Counter, defaultdict

# deque: O(1) insert/delete at both ends
dq = deque([1, 2, 3])
dq.appendleft(0)
print(list(dq))  # [0, 1, 2, 3]

# Counter: frequency counting
counter = Counter("abracadabra")
print(counter.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]

# defaultdict: dict with default values
dd = defaultdict(list)
dd["fruits"].append("apple")
print(dd)  # defaultdict(<class 'list'>, {'fruits': ['apple']})
```

## 이 코드에서 먼저 봐야 할 점

- list의 `in` 연산은 O(n)이지만 set의 `in` 연산은 O(1)입니다.
- dict는 키 기반 조회를 O(1)에 제공하므로 검색이 많은 코드에서 기본 선택지가 됩니다.
- tuple은 불변이라 dict의 키나 set의 원소처럼 해시 가능한 위치에 넣을 수 있습니다.
- `collections` 모듈은 “기본 자료구조로는 살짝 불편한 패턴”을 보완해 주는 특화 구조를 제공합니다.

핵심은 Python이 자료구조를 이미 많이 제공한다는 사실입니다. 대부분의 경우 새로운 구조를 발명할 필요는 없습니다. 대신 각 구조의 연산 특성을 알고 상황에 맞게 고르는 능력이 더 중요합니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 곳에 list 사용 | 검색이 O(n)이라 데이터가 커질수록 느려집니다 | 조회가 많으면 set이나 dict를 우선 검토합니다 |
| list를 dict 키로 사용 | list는 가변 객체라 해시할 수 없습니다 | tuple로 변환한 뒤 키로 사용합니다 |
| 자료구조 크기를 무시 | 메모리 사용량이 급격히 커질 수 있습니다 | 데이터 규모와 생명주기를 함께 봅니다 |
| set에 순서를 기대 | set은 순서를 보장하지 않습니다 | 순서가 중요하면 list나 다른 구조를 사용합니다 |
| 시간 복잡도 확인 없이 구현 | 작은 데이터에서는 지나가도 규모가 커지면 병목이 됩니다 | 구조를 고르기 전에 주요 연산의 비용을 먼저 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 캐시 시스템은 O(1) 조회를 위해 dict를 사용합니다.
- 중복 제거 파이프라인은 set으로 고유값만 유지합니다.
- 작업 큐는 deque로 FIFO 처리를 구현합니다.
- 좌표나 설정 키처럼 바뀌면 안 되는 값은 tuple로 고정합니다.
- 로그 분석과 빈도 집계는 Counter로 간결하게 처리합니다.

## 실무에서는 이렇게 생각합니다

경험 있는 개발자는 코드를 쓰기 전에 “이 데이터를 어디에 담을까?”보다 “이 데이터를 가장 자주 어떻게 다룰까?”를 먼저 묻습니다. 검색이 많은지, 순서가 중요한지, 중복 허용 여부가 핵심인지에 따라 출발점이 달라지기 때문입니다.

실무에서는 Python 내장 자료구조만으로도 대부분의 문제를 충분히 해결할 수 있습니다. 결국 중요한 것은 list, dict, set, tuple의 차이를 정확히 알고, 그 차이가 성능과 가독성에 어떤 영향을 주는지 설명할 수 있는가입니다.

## 체크리스트

- [ ] 자료구조의 정의와 역할을 설명할 수 있다
- [ ] list, dict, set, tuple의 차이를 설명할 수 있다
- [ ] set이 list보다 조회에 유리한 이유를 설명할 수 있다
- [ ] collections 모듈의 deque, Counter, defaultdict를 사용할 수 있다
- [ ] 시간 복잡도 개념을 자료구조 선택에 연결해 설명할 수 있다

## 연습 문제

1. 정수 100만 개가 들어 있는 list와 set에서 같은 값을 찾는 코드를 작성하고 실행 시간을 비교해 보세요.
2. 문자열 list에서 원래 순서를 유지한 채 중복만 제거하는 함수를 작성해 보세요. 힌트: `dict.fromkeys()`를 활용할 수 있습니다.
3. 학생 이름과 점수를 dict에 저장한 뒤, 점수 기준 내림차순으로 출력하는 코드를 작성해 보세요.

## 정리 및 다음 글 안내

자료구조는 데이터를 효율적으로 저장하고 접근하기 위한 기본 설계 도구입니다. Python은 list, dict, set, tuple처럼 강력한 내장 구조를 이미 갖추고 있고, 개발자는 각 구조의 특성을 이해한 뒤 상황에 맞게 선택하면 됩니다. 다음 글에서는 이 시리즈의 출발점이 되는 배열과 리스트를 더 깊이 들여다보겠습니다.

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

Tags: Python, 자료구조, Data Structures, 알고리즘, 프로그래밍 기초
