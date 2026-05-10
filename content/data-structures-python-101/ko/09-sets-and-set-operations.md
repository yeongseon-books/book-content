---
series: data-structures-python-101
episode: 9
title: set과 집합 연산
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
  - set
  - 집합 연산
  - frozenset
seo_description: Python set의 내부 구조와 집합 연산을 실습합니다.
last_reviewed: '2026-05-04'
---

# set과 집합 연산

> Data Structures with Python 101 시리즈 (9/10)


## 이 글에서 다룰 문제

데이터 처리에서 중복 제거, 멤버십 검사, 두 집합의 비교는 매우 빈번한 작업입니다. list로 이 작업들을 하면 O(n)이지만, set을 사용하면 O(1)입니다. 데이터 규모가 커질수록 이 차이는 결정적입니다.

> set은 dict에서 값을 제거한 것과 같습니다. 키만 저장하는 해시 테이블입니다.

집합 연산은 데이터 분석, 권한 관리, 태그 시스템 등에서 핵심적으로 사용됩니다.

## 핵심 개념 잡기

> set = 중복 없는 원소의 모음, 해시 테이블 기반

```
A = {1, 2, 3, 4}      B = {3, 4, 5, 6}

합집합  A | B  = {1, 2, 3, 4, 5, 6}
교집합  A & B  = {3, 4}
차집합  A - B  = {1, 2}
대칭차  A ^ B  = {1, 2, 5, 6}
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| set | 중복을 허용하지 않는 해시 기반 컬렉션입니다 |
| frozenset | 불변(immutable) set으로, dict 키나 set 원소로 사용 가능합니다 |
| 합집합(union) | 두 집합의 모든 원소를 합친 결과입니다 |
| 교집합(intersection) | 두 집합에 공통으로 있는 원소입니다 |
| 차집합(difference) | 한 집합에만 있고 다른 집합에는 없는 원소입니다 |

## Before / After

리스트에서 중복을 제거하고 공통 원소를 찾는 비효율적 방법과 set을 사용한 효율적 방법을 비교합니다.

```python
# before: list로 중복 제거와 교집합 — O(n²)
list_a = [1, 2, 3, 4, 2, 3]
unique = []
for x in list_a:
    if x not in unique:
        unique.append(x)
common = [x for x in list_a if x in [3, 4, 5, 6]]
```

```python
# after: set으로 중복 제거와 교집합 — O(n)
set_a = {1, 2, 3, 4, 2, 3}   # 자동 중복 제거 → {1, 2, 3, 4}
common = set_a & {3, 4, 5, 6}  # O(min(m, n))으로 교집합
```

## 단계별 실습

### Step 1: set 기본 연산

```python
# 생성
fruits = {"apple", "banana", "cherry"}
numbers = set([1, 2, 3, 2, 1])  # {1, 2, 3}

# 추가 — O(1)
fruits.add("date")

# 삭제 — O(1)
fruits.discard("banana")  # 없어도 에러 없음
# fruits.remove("banana")  # 없으면 KeyError

# 멤버십 검사 — O(1)
print("apple" in fruits)  # True

# 크기
print(len(fruits))  # 3
```

### Step 2: 집합 연산

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# 합집합
print(a | b)          # {1, 2, 3, 4, 5, 6, 7, 8}
print(a.union(b))     # 같은 결과

# 교집합
print(a & b)              # {4, 5}
print(a.intersection(b))  # 같은 결과

# 차집합
print(a - b)            # {1, 2, 3}
print(a.difference(b))  # 같은 결과

# 대칭 차집합 (한쪽에만 있는 원소)
print(a ^ b)                      # {1, 2, 3, 6, 7, 8}
print(a.symmetric_difference(b))  # 같은 결과
```

### Step 3: 부분집합과 상위집합

```python
a = {1, 2, 3}
b = {1, 2, 3, 4, 5}

print(a <= b)          # True — a는 b의 부분집합
print(a.issubset(b))   # True

print(b >= a)            # True — b는 a의 상위집합
print(b.issuperset(a))   # True

print(a.isdisjoint({6, 7}))  # True — 공통 원소 없음
```

### Step 4: frozenset 활용

```python
# frozenset: 불변 set — dict 키로 사용 가능
permissions = frozenset(["read", "write"])
other = frozenset(["read", "write"])

# dict 키로 사용
role_map = {
    frozenset(["read"]): "viewer",
    frozenset(["read", "write"]): "editor",
    frozenset(["read", "write", "admin"]): "admin",
}
print(role_map[permissions])  # "editor"

# set의 원소로 사용
set_of_sets = {frozenset([1, 2]), frozenset([3, 4])}
print(frozenset([1, 2]) in set_of_sets)  # True
```

### Step 5: 실무 패턴 — 태그 필터링

```python
articles = [
    {"title": "Python 입문", "tags": {"python", "beginner"}},
    {"title": "Django REST", "tags": {"python", "django", "api"}},
    {"title": "React Hooks", "tags": {"javascript", "react"}},
    {"title": "Flask API", "tags": {"python", "flask", "api"}},
]

# python AND api 태그가 모두 있는 글
required = {"python", "api"}
matches = [a for a in articles if required <= a["tags"]]
for m in matches:
    print(m["title"])
# Django REST
# Flask API

# python OR javascript 태그가 있는 글
any_of = {"python", "javascript"}
matches = [a for a in articles if a["tags"] & any_of]
print([m["title"] for m in matches])
# ['Python 입문', 'Django REST', 'React Hooks', 'Flask API']
```

## 이 코드에서 주목할 점

- set의 `in` 연산은 O(1)이므로 대규모 데이터 검색에 적합합니다
- `|`, `&`, `-`, `^` 연산자로 집합 연산을 간결하게 표현합니다
- `<=` 연산자로 부분집합 관계를 확인할 수 있습니다
- frozenset은 불변이므로 dict 키나 다른 set의 원소로 사용합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 빈 set을 `{}`로 생성 | `{}`는 빈 dict입니다 | `set()`으로 빈 set을 생성합니다 |
| list를 set 원소로 사용 | list는 unhashable이라 TypeError 발생합니다 | tuple로 변환하여 사용합니다 |
| set 순서에 의존 | set은 순서를 보장하지 않습니다 | 순서가 필요하면 sorted()를 사용합니다 |
| remove()로 없는 원소 삭제 | KeyError가 발생합니다 | discard()를 사용하면 에러 없이 무시합니다 |
| set comprehension에서 중복 의도 | 자동으로 중복이 제거됩니다 | 의도한 동작인지 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 사용자 권한을 set으로 관리하고 교집합으로 접근 제어를 확인합니다
- 중복 데이터를 set으로 즉시 제거합니다
- 두 데이터 소스의 차이를 차집합으로 구합니다
- 태그 기반 필터링에 set 연산을 활용합니다
- 이미 처리한 항목을 set으로 추적하여 중복 처리를 방지합니다

## 현업 개발자는 이렇게 생각합니다

set은 과소평가되는 자료구조입니다. 많은 개발자가 list만 사용하지만, 검색과 중복 제거가 필요한 상황에서 set을 사용하면 코드가 간결해지고 성능이 향상됩니다.

"이 데이터에서 중복이 있는가?", "두 컬렉션에 공통 원소가 있는가?"라는 질문이 나오면 가장 먼저 set을 떠올려야 합니다.

## 체크리스트

- [ ] set의 기본 연산(add, discard, in)을 사용할 수 있다
- [ ] 합집합, 교집합, 차집합, 대칭 차집합을 설명할 수 있다
- [ ] frozenset의 용도를 설명할 수 있다
- [ ] set으로 중복 제거와 멤버십 검사를 O(1)에 수행할 수 있다
- [ ] 부분집합과 상위집합 관계를 확인할 수 있다

## 정리 및 다음 글 안내

set은 해시 테이블 기반으로 O(1) 검색과 풍부한 집합 연산을 제공합니다. 중복 제거, 멤버십 검사, 데이터 비교에 강력합니다. 다음 글에서는 상황에 맞는 자료구조를 선택하는 기준을 종합 정리합니다.

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

- [Python 공식 문서 — Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [Real Python — Sets in Python](https://realpython.com/python-sets/)
- [Python TimeComplexity — Set](https://wiki.python.org/moin/TimeComplexity)
- [GeeksforGeeks — Python Set](https://www.geeksforgeeks.org/python-set/)

Tags: Python, 자료구조, set, 집합 연산, frozenset
