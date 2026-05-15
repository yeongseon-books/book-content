---
series: data-structures-python-101
episode: 9
title: set과 집합 연산
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
  - set
  - 집합 연산
  - frozenset
seo_description: 파이썬 set의 해시 원리를 이해하고 중복 제거, 집합 연산, 권한 필터링 등 실무 패턴과 불변 객체인 frozenset 활용법을 익힙니다.
last_reviewed: '2026-05-12'
---

# set과 집합 연산

이 글은 Data Structures with Python 101 시리즈의 아홉 번째 글입니다.

## 이 글에서 다룰 문제

- 중복 제거와 membership test에 set이 왜 강할까요?
- 합집합, 교집합, 차집합, 대칭차집합은 코드에서 어떻게 쓰일까요?
- `frozenset`은 왜 필요하고 언제 써야 할까요?
- 태그 필터링, 권한 비교, 데이터 차집합 같은 실무 문제를 set으로 어떻게 풀 수 있을까요?

> 멘탈 모델: set은 “값만 저장하는 해시 테이블”입니다. 순서와 중복을 포기하는 대신, 빠른 존재 확인과 집합 연산을 얻습니다.

## 왜 이 글이 중요한가

데이터 처리에서 중복 제거, 존재 여부 확인, 두 컬렉션 비교는 매우 자주 등장합니다. list로도 할 수는 있지만, 데이터가 커질수록 비용이 빠르게 커집니다. set은 이런 작업을 O(1) membership test와 간결한 연산자 문법으로 처리하게 해 줍니다.

> set은 값을 저장하지 않는 dict와 거의 같은 해시 기반 구조입니다.

실무에서는 권한 관리, 태그 시스템, 중복 제거, 이미 처리한 작업 추적 같은 패턴에서 set이 반복해서 등장합니다. 즉, set은 문법적으로 단순하지만, 효율성과 표현력을 동시에 가져가는 매우 실전적인 자료구조입니다.

## 핵심 개념 한눈에 보기

> set = 중복 없는 원소 집합이며, 해시 테이블 기반으로 동작하는 구조

```text
A = {1, 2, 3, 4}      B = {3, 4, 5, 6}

union        A | B  = {1, 2, 3, 4, 5, 6}
intersection A & B  = {3, 4}
difference   A - B  = {1, 2}
sym. diff.   A ^ B  = {1, 2, 5, 6}
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| set | 중복을 허용하지 않는 해시 기반 컬렉션입니다 |
| frozenset | 불변 set으로, dict 키나 다른 set의 원소가 될 수 있습니다 |
| 합집합(union) | 두 집합의 원소를 모두 합친 결과입니다 |
| 교집합(intersection) | 두 집합에 공통으로 들어 있는 원소입니다 |
| 차집합(difference) | 한 집합에는 있고 다른 집합에는 없는 원소입니다 |

## Before / After

중복 제거와 공통 원소 추출을 list와 set으로 각각 처리해 보겠습니다.

```python
# before: deduplication and intersection with list — O(n^2)
list_a = [1, 2, 3, 4, 2, 3]
unique = []
for x in list_a:
    if x not in unique:
        unique.append(x)
common = [x for x in list_a if x in [3, 4, 5, 6]]
```

```python
# after: deduplication and intersection with set — O(n)
set_a = {1, 2, 3, 4, 2, 3}   # automatic dedup → {1, 2, 3, 4}
common = set_a & {3, 4, 5, 6}  # O(min(m, n)) intersection
```

set의 가치는 단순히 빠르다는 데만 있지 않습니다. 코드를 읽는 사람도 “여기서는 중복이 의미 없고, 존재 여부가 핵심이구나”를 즉시 이해할 수 있습니다. 즉, 자료구조가 의도까지 표현합니다.

## 단계별 실습

### Step 1: Basic set operations

```python
# Creation
fruits = {"apple", "banana", "cherry"}
numbers = set([1, 2, 3, 2, 1])  # {1, 2, 3}

# Add — O(1)
fruits.add("date")

# Remove — O(1)
fruits.discard("banana")  # no error if missing
# fruits.remove("banana")  # raises KeyError if missing

# Membership test — O(1)
print("apple" in fruits)  # True

# Size
print(len(fruits))  # 3
```

### Step 2: Set operations

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# Union
print(a | b)          # {1, 2, 3, 4, 5, 6, 7, 8}
print(a.union(b))     # same result

# Intersection
print(a & b)              # {4, 5}
print(a.intersection(b))  # same result

# Difference
print(a - b)            # {1, 2, 3}
print(a.difference(b))  # same result

# Symmetric difference (elements in only one set)
print(a ^ b)                      # {1, 2, 3, 6, 7, 8}
print(a.symmetric_difference(b))  # same result
```

### Step 3: Subsets and supersets

```python
a = {1, 2, 3}
b = {1, 2, 3, 4, 5}

print(a <= b)          # True — a is a subset of b
print(a.issubset(b))   # True

print(b >= a)            # True — b is a superset of a
print(b.issuperset(a))   # True

print(a.isdisjoint({6, 7}))  # True — no common elements
```

### Step 4: frozenset usage

```python
# frozenset: immutable set — can be used as a dict key
permissions = frozenset(["read", "write"])
other = frozenset(["read", "write"])

# Use as dict key
role_map = {
    frozenset(["read"]): "viewer",
    frozenset(["read", "write"]): "editor",
    frozenset(["read", "write", "admin"]): "admin",
}
print(role_map[permissions])  # "editor"

# Use as set element
set_of_sets = {frozenset([1, 2]), frozenset([3, 4])}
print(frozenset([1, 2]) in set_of_sets)  # True
```

### Step 5: Practical pattern — tag filtering

```python
articles = [
    {"title": "Python Intro", "tags": {"python", "beginner"}},
    {"title": "Django REST", "tags": {"python", "django", "api"}},
    {"title": "React Hooks", "tags": {"javascript", "react"}},
    {"title": "Flask API", "tags": {"python", "flask", "api"}},
]

# Articles with BOTH python AND api tags
required = {"python", "api"}
matches = [a for a in articles if required <= a["tags"]]
for m in matches:
    print(m["title"])
# Django REST
# Flask API

# Articles with python OR javascript tags
any_of = {"python", "javascript"}
matches = [a for a in articles if a["tags"] & any_of]
print([m["title"] for m in matches])
# ['Python Intro', 'Django REST', 'React Hooks', 'Flask API']
```

## 이 코드에서 먼저 봐야 할 점

- set의 `in` 연산은 O(1)이므로 대규모 membership test에 매우 유리합니다.
- `|`, `&`, `-`, `^` 연산자는 집합의 의도를 짧고 명확하게 드러냅니다.
- `<=`는 부분집합 관계를 검사하는 매우 실용적인 문법입니다.
- `frozenset`은 불변이므로 dict 키나 다른 set의 원소로 안전하게 사용할 수 있습니다.

set을 잘 쓰는 개발자는 중복 제거 로직을 반복문으로 길게 쓰지 않습니다. 데이터가 “순서가 중요한가, 중복이 중요한가, 존재 여부가 중요한가”를 먼저 판단하고, 그에 맞는 구조를 바로 고릅니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 빈 set을 `{}`로 생성 | `{}`는 빈 dict입니다 | 빈 set은 `set()`으로 만듭니다 |
| list를 set 원소로 사용 | list는 해시할 수 없어 `TypeError`가 납니다 | tuple로 바꿉니다 |
| set 순서에 의존 | set은 순서를 보장하지 않습니다 | 순서가 필요하면 `sorted()`나 list를 사용합니다 |
| 없는 원소에 `remove()` 사용 | `KeyError`가 발생합니다 | 에러 없이 무시하려면 `discard()`를 씁니다 |
| set comprehension에서 중복을 기대 | 중복은 자동 제거됩니다 | 의도한 결과인지 먼저 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 권한 집합의 교집합으로 접근 가능 여부를 확인합니다.
- 데이터 정제에서 set 변환으로 중복을 즉시 제거합니다.
- 두 데이터 소스의 차이를 차집합으로 계산합니다.
- 태그 기반 필터링은 부분집합·교집합 검사와 잘 맞습니다.
- 이미 처리한 항목을 set에 기록해 재처리를 막습니다.

## 실무에서는 이렇게 생각합니다

set은 종종 과소평가됩니다. 많은 코드가 list로도 돌아가지만, 검색과 중복 제거가 핵심인 로직에 set을 쓰면 코드가 짧아지고 성능도 좋아집니다. 특히 membership test가 반복되는 루프에서 차이가 크게 납니다.

좋은 기준은 단순합니다. “중복이 의미가 없나?”, “존재 여부만 빠르게 확인하면 되나?”, “두 집합 관계를 계산해야 하나?”라는 질문 중 하나라도 Yes라면 set을 가장 먼저 떠올리는 습관이 필요합니다.

## 체크리스트

- [ ] set의 기본 연산(add, discard, in)을 사용할 수 있다
- [ ] 합집합, 교집합, 차집합, 대칭차집합을 설명할 수 있다
- [ ] frozenset의 용도를 설명할 수 있다
- [ ] set으로 중복 제거와 membership test를 O(1)에 처리할 수 있다
- [ ] 부분집합과 상위집합 관계를 확인할 수 있다

## 연습 문제

1. 두 list의 공통 원소를 set 연산으로 구하되, 결과는 원래 순서를 유지해 반환하는 함수를 작성해 보세요.
2. 여러 학생의 수강 과목을 set으로 관리하고, 모든 학생이 공통으로 듣는 과목을 찾아 보세요.
3. 두 텍스트 파일의 단어 집합을 만들고, 각 파일에만 있는 단어를 대칭차집합으로 구해 보세요.

## 정리 및 다음 글 안내

set은 해시 테이블 기반으로 O(1) membership test와 풍부한 집합 연산을 제공하는 구조입니다. 중복 제거, 존재 확인, 데이터 비교 문제에서는 매우 강력한 기본 선택지입니다. 다음 글에서는 시리즈 전체를 마무리하며, 상황별로 어떤 자료구조를 골라야 하는지 의사결정 기준을 정리하겠습니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- [해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [연결 리스트](./05-linked-lists.md)
- [트리와 이진 트리](./06-trees-and-binary-trees.md)
- [힙과 우선순위 큐](./07-heaps-and-priority-queues.md)
- [그래프 표현](./08-graph-representations.md)
- **set과 집합 연산 (현재 글)**
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Python Docs — Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [Real Python — Sets in Python](https://realpython.com/python-sets/)
- [Python TimeComplexity — Set](https://wiki.python.org/moin/TimeComplexity)
- [GeeksforGeeks — Python Set](https://www.geeksforgeeks.org/python-set/)

Tags: Python, 자료구조, set, 집합 연산, frozenset
