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
last_reviewed: '2026-05-17'
---

# set과 집합 연산

이 글은 Data Structures with Python 101 시리즈의 아홉 번째 글입니다.

## 이 글에서 다룰 문제

- `set`은 왜 중복 제거와 membership test에 강할까요?
- 충돌과 hashability는 set에서 어떤 의미를 가질까요?
- 왜 `frozenset`은 set 원소나 dict 키가 될 수 있고 plain `set`은 안 될까요?
- 합집합, 교집합, 차집합은 저장 모델과 어떻게 연결될까요?

> 멘탈 모델: Python의 `set`은 값만 저장하는 해시 테이블입니다. 중복과 위치 정보를 포기하는 대신, 빠른 존재 확인과 강력한 집합 연산을 얻습니다.

## 왜 이 글이 중요한가

중복 제거, 존재 여부 확인, 컬렉션 비교는 권한 관리, 태그 시스템, 데이터 정제, 처리 완료 추적처럼 실무의 거의 모든 영역에 등장합니다. list로도 구현할 수 있지만, 데이터가 커질수록 비용 차이가 급격히 벌어집니다.

> `set`은 값을 저장하지 않는 dict와 같은 해시 테이블 계열 구조입니다.

그래서 set을 배울 때는 `|`, `&` 같은 문법만 익히는 것으로 끝나면 안 됩니다. hashability, collision, uniqueness가 어떻게 맞물리는지까지 이해해야 실전에서 제대로 사용할 수 있습니다.

## 핵심 개념 한눈에 보기

> `set` = 중복 없는 키만 저장하는 해시 테이블 기반 컬렉션

```text
A = {1, 2, 3, 4}      B = {3, 4, 5, 6}

union        A | B  = {1, 2, 3, 4, 5, 6}
intersection A & B  = {3, 4}
difference   A - B  = {1, 2}
sym. diff.   A ^ B  = {1, 2, 5, 6}
```

## set 저장 모델을 그림으로 보면

![set 저장 모델을 그림으로 보면](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/09/09-01-set.ko.png)

*set이 고유한 키만 저장하기 때문에 중복 제거와 집합 연산이 같은 저장 모델에서 자연스럽게 나오는 구조임을 보여 주는 그림*

## 핵심 개념

| 용어 | 설명 |
|------|------|
| set | 중복 없는 키만 저장하는 해시 기반 컬렉션입니다 |
| hashability | 원소가 안정적인 해시와 equality 의미를 가져야 한다는 조건입니다 |
| collision | 서로 다른 값이 같은 lookup/probe path를 공유하는 상황입니다 |
| `frozenset` | 자기 자신도 해시 가능한 불변 set입니다 |
| 집합 연산 | 합집합, 교집합, 차집합, 대칭차집합처럼 membership 기반으로 계산하는 연산입니다 |

## Before / After

list 기반 중복 제거와 set 기반 중복 제거를 비교해 보겠습니다.

```python
# before: list로 중복 제거 — O(n^2)
values = [1, 2, 3, 4, 2, 3]
unique = []
for value in values:
    if value not in unique:
        unique.append(value)
```

```python
# after: set으로 중복 제거 — 평균 O(n)
values = [1, 2, 3, 4, 2, 3]
unique = set(values)
print(unique)  # {1, 2, 3, 4}
```

좋은 점은 속도만이 아닙니다. set을 쓰는 순간 “여기서는 순서보다 membership과 uniqueness가 중요하다”는 의도가 코드에 바로 드러납니다.

## 단계별 실습

### Step 1: 기본 set 연산 확인하기

```python
fruits = {"apple", "banana", "cherry"}

fruits.add("date")
fruits.discard("banana")

print("apple" in fruits)  # True
print(len(fruits))         # 3
```

### Step 2: 충돌을 강제로 만들고도 dedup이 유지되는지 보기

```python
class Tag:
    def __init__(self, name: str):
        self.name = name

    def __hash__(self) -> int:
        return 7

    def __eq__(self, other) -> bool:
        return isinstance(other, Tag) and self.name == other.name

    def __repr__(self) -> str:
        return f"Tag({self.name!r})"


seen = {Tag("python"), Tag("api"), Tag("python")}

print(seen)
print(Tag("python") in seen)  # True
print(len(seen))               # 2
```

예시 출력은 다음과 같습니다.

```text
{Tag('api'), Tag('python')}
True
2
```

#### 이 결과를 읽는 법

- 세 객체 모두 같은 해시값을 쓰게 했으므로 충돌은 반드시 발생합니다.
- 그런데도 set에는 논리적으로 두 원소만 남습니다. `Tag("python")` 두 개가 equality 기준으로 같은 키이기 때문입니다.
- 즉, set의 속도는 해시 테이블에서 오지만, 정확성은 안정적인 해시와 올바른 equality 의미에 달려 있습니다.

### Step 3: “list는 안 된다”를 넘어서 `frozenset`이 왜 되는지 증명하기

```python
try:
    invalid = {{1, 2}}
except TypeError as error:
    print(type(error).__name__, error)

allowed = {frozenset({"read", "write"}), frozenset({"read"})}
print(frozenset({"read", "write"}) in allowed)  # True

role_map = {frozenset({"read", "write"}): "editor"}
print(role_map[frozenset({"write", "read"})])   # editor
```

예시 출력은 다음과 같습니다.

```text
TypeError unhashable type: 'set'
True
editor
```

#### 이 결과를 읽는 법

plain `set`은 가변 객체라서 자기 자신을 다른 set의 원소나 dict 키로 넣을 수 없습니다. 반면 `frozenset`은 생성 후 내용이 바뀌지 않으므로 안정적인 해시를 만들 수 있고, 그래서 중첩 set이나 dict 키 역할을 안전하게 수행합니다.

### Step 4: 집합 연산을 저장 모델과 연결해 보기

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(a | b)  # union
print(a & b)  # intersection
print(a - b)  # difference
print(a ^ b)  # symmetric difference
```

이 연산자들이 자연스러운 이유는 set이 애초부터 “고유한 키의 membership” 중심 구조이기 때문입니다.

### Step 5: 태그 필터링은 proof가 아니라 응용으로 보기

```python
articles = [
    {"title": "Python Intro", "tags": {"python", "beginner"}},
    {"title": "Django REST", "tags": {"python", "django", "api"}},
    {"title": "React Hooks", "tags": {"javascript", "react"}},
    {"title": "Flask API", "tags": {"python", "flask", "api"}},
]

required = {"python", "api"}
matches = [article for article in articles if required <= article["tags"]]
print([article["title"] for article in matches])
```

태그 필터링은 좋은 실무 예시입니다. 다만 이 예시가 의미 있으려면 먼저 membership과 subset 검사가 왜 빠른지 내부 모델부터 이해해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- set은 key-only hash table로 이해하는 편이 가장 정확합니다.
- set에서도 collision은 발생하지만 uniqueness와 membership semantics는 깨지지 않습니다.
- dedup은 해시가 탐색 범위를 좁히고 equality가 동일성을 확정하기 때문에 성립합니다.
- `frozenset`은 이름만 다른 alias가 아니라, 해시 가능한 불변 set이라는 중요한 역할을 가집니다.
- 집합 연산이 간결한 이유는 구조 자체가 unique-key membership 중심이기 때문입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 빈 set을 `{}`로 생성 | `{}`는 빈 dict입니다 | `set()`을 사용합니다 |
| 충돌은 일어나지 않는다고 생각 | 해시 테이블에서 충돌은 정상입니다 | 안정적인 `__hash__`와 `__eq__`를 설계합니다 |
| 가변 값을 set 원소로 사용 | 해시할 수 없거나 안전하지 않습니다 | `tuple`, `frozenset` 같은 불변 값을 사용합니다 |
| set 순서가 의미 있다고 가정 | 반복 순서는 안정적인 의미 계약이 아닙니다 | 출력 순서가 필요하면 명시적으로 정렬합니다 |
| `frozenset`을 단지 문법 취향으로 생각 | 중첩 set과 dict key 문제를 해결합니다 | set 자체를 원소/키로 써야 할 때 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 권한 집합은 교집합·부분집합 검사와 함께 관리됩니다.
- 데이터 정제 파이프라인은 raw 값을 먼저 set으로 바꿔 중복을 제거합니다.
- 이미 처리한 ID를 set에 기록해 중복 작업을 막습니다.
- feature flag와 태그는 membership 중심이라 set과 잘 맞습니다.
- 두 데이터셋의 차이를 루프보다 차집합으로 표현하면 의도와 비용이 함께 명확해집니다.

## 실무에서는 이렇게 생각합니다

숙련된 개발자는 순서가 제품 요구사항이 아니라 membership이 핵심일 때 가장 먼저 set을 떠올립니다. 이 한 번의 선택만으로 코드가 짧아지고 accidental O(n²)도 줄어듭니다.

또한 정확성은 원소 semantics에 달려 있다는 점도 압니다. equality나 해시가 불안정하면 set은 더 이상 믿을 수 있는 dedup 도구가 아닙니다.

## 체크리스트

- [ ] set이 dict와 같은 해시 테이블 계열 구조라는 점을 설명할 수 있다
- [ ] collision과 equality가 어떻게 함께 올바른 dedup을 만드는지 설명할 수 있다
- [ ] `set`과 `frozenset`의 hashability 경계를 설명할 수 있다
- [ ] 합집합, 교집합, 차집합, 대칭차집합을 상황에 맞게 사용할 수 있다
- [ ] 순서보다 membership이 중요할 때 set을 선택할 수 있다

## 연습 문제

1. `Tag` 예시를 확장해 5개의 객체가 모두 같은 해시값을 갖게 만든 뒤, membership이 여전히 올바르게 동작하는지 확인해 보세요.
2. `frozenset` 권한 묶음들의 set을 만들고, 그중 `read`와 `write`를 모두 가진 묶음을 찾아 보세요.
3. 큰 입력에서 list 기반 중복 제거 루프와 `set(values)`를 비교하고, 왜 차이가 나는지 저장 모델로 설명해 보세요.

## 정리 및 다음 글 안내

Python `set`은 key-only hash table입니다. 그래서 빠른 membership test, 자동 dedup, 간결한 집합 연산이 모두 같은 저장 모델에서 나옵니다. 그리고 그 정확성은 안정적인 해시와 equality에 달려 있습니다. 다음 글에서는 시리즈를 마무리하며 상황별로 어떤 자료구조를 선택해야 하는지 기준을 정리하겠습니다.

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
- [CPython set implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/setobject.c)
- [Python Data Model — `__hash__` and `__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Real Python — Sets in Python](https://realpython.com/python-sets/)
- [Python TimeComplexity — Set](https://wiki.python.org/moin/TimeComplexity)

Tags: Python, 자료구조, set, 집합 연산, frozenset
