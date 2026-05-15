---
series: discrete-math-101
episode: 3
title: 집합과 함수
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
  - 이산수학
  - 집합론
  - 함수
  - 데이터베이스
  - 자료구조
seo_description: 집합 연산과 함수의 분류를 통해 자료구조와 데이터베이스의 수학적 기반을 설명합니다.
last_reviewed: '2026-05-12'
---

# 집합과 함수

이 글은 Discrete Math 101 시리즈의 3번째 글입니다.

## 이 글에서 다룰 문제

- 집합 표기와 기본 연산은 어떻게 읽어야 할까요?
- 합집합, 교집합, 차집합, 곱집합은 실무에서 어디에 쓰일까요?
- 함수의 정의역, 공역, 치역은 무엇이 다를까요?
- 단사, 전사, 전단사는 왜 중요한가요?

> 집합은 서로 다른 원소의 모임이고, 함수는 한 집합에서 다른 집합으로 가는 잘 정의된 대응입니다. `set`, `dict`, 관계형 데이터베이스, 함수형 프로그래밍의 `map`은 모두 이 두 개념의 직접적인 구현입니다. 이 글에서는 집합 연산, 곱집합, 함수의 분류, 합성과 역함수를 한 흐름으로 정리합니다.

## 왜 중요한가

데이터베이스의 한 행은 곱집합의 원소입니다. JOIN은 곱집합 위에서 술어를 평가합니다. 해시맵은 키 집합에서 값 집합으로 가는 부분 함수로 볼 수 있습니다. 함수형 프로그래밍의 `map` 역시 집합 사이에 함수를 적용하는 구조입니다. 집합과 함수를 모르면 이런 도구의 본질을 끝까지 설명하기 어렵습니다.

> 자료구조는 집합이나 함수를 효율적으로 구현한 결과물입니다.

## 한눈에 보는 개념

> 집합은 원소의 컬렉션이고, 함수는 집합 사이의 대응입니다. 둘을 함께 보면 거의 모든 데이터 구조가 설명됩니다.

```text
   Set A           Function f: A → B           Set B
  ┌─────┐                                    ┌─────┐
  │ a₁  │ ─────────── f(a₁) ─────────────── │ b₁  │
  │ a₂  │ ─────────── f(a₂) ─────────────── │ b₂  │
  │ a₃  │ ─────────── f(a₃) ─────────────── │ b₃  │
  └─────┘                                    └─────┘
   domain                                    codomain
                                              range
                                              ⊆ codomain
```

## 핵심 용어

| 용어 | 기호 | 의미 |
| --- | --- | --- |
| Element | a ∈ A | a가 집합 A의 원소 |
| Subset | A ⊆ B | A의 모든 원소가 B에 포함 |
| Cartesian product | A × B | 순서쌍 (a, b)의 집합 |
| Function | f: A → B | A의 각 원소를 B의 한 원소로 대응 |
| Injective | one-to-one | 서로 다른 입력이 서로 다른 출력으로 감 |

## Before / After

**Before — without set thinking:**

```python
# Manually deduplicate
result = []
for item in items:
    if item not in result:
        result.append(item)
```

**After — using sets:**

```python
# Leverage the set's intrinsic property
result = list(set(items))
```

## 단계별로 따라가기

### 1단계: 집합 표기

```python
# Roster notation: list elements
A = {1, 2, 3, 4, 5}

# Set-builder notation: state a condition
B = {x for x in range(1, 11) if x % 2 == 0}

# Power set: the set of all subsets
from itertools import chain, combinations


def power_set(s: set) -> list[set]:
    items = list(s)
    return [
        set(combo)
        for r in range(len(items) + 1)
        for combo in combinations(items, r)
    ]


print(f"A = {A}")
print(f"B = {B}")
print(f"|A| = {len(A)}, |P(A)| = {2 ** len(A)}")
print(f"P({{1,2}}) = {power_set({1, 2})}")
```

`|A| = n`이면 멱집합의 크기는 `2ⁿ`입니다. 부분집합의 수가 지수적으로 늘어난다는 사실은 알고리즘 복잡도가 왜 갑자기 폭발하는지를 설명하는 가장 기본적인 감각입니다.

### 2단계: 집합 연산

```python
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}
U = set(range(1, 11))  # universal set

print(f"A ∪ B = {A | B}")        # union
print(f"A ∩ B = {A & B}")        # intersection
print(f"A - B = {A - B}")        # difference
print(f"A △ B = {A ^ B}")        # symmetric difference
print(f"A^c (∈ U) = {U - A}")     # complement
print(f"|A ∪ B| = |A| + |B| - |A ∩ B| = {len(A) + len(B) - len(A & B)}")
```

마지막 식은 포함-배제 원리의 가장 단순한 형태입니다. 조합론 장으로 넘어가면 이 아이디어가 훨씬 큰 계산으로 확장됩니다.

### 3단계: 곱집합과 관계

```python
from itertools import product

A = {1, 2, 3}
B = {"x", "y"}

# A × B = {(a, b) | a ∈ A, b ∈ B}
cartesian = set(product(A, B))
print(f"A × B = {cartesian}")
print(f"|A × B| = |A| × |B| = {len(cartesian)}")

# A database row is an element of a Cartesian product
users = {"alice", "bob"}
roles = {"admin", "user"}
permissions = set(product(users, roles))
print(f"Possible (user, role) pairs: {permissions}")
```

데이터베이스 테이블 스키마는 그 자체로 곱집합입니다. `CROSS JOIN`은 말 그대로 그 곱집합을 계산합니다.

### 4단계: 함수의 종류

```python
def is_injective(f: dict) -> bool:
    """Injective: distinct inputs map to distinct outputs"""
    return len(set(f.values())) == len(f)


def is_surjective(f: dict, codomain: set) -> bool:
    """Surjective: every codomain element is hit"""
    return set(f.values()) == codomain


def is_bijective(f: dict, codomain: set) -> bool:
    """Bijective: both injective and surjective"""
    return is_injective(f) and is_surjective(f, codomain)


f1 = {1: "a", 2: "b", 3: "c"}     # injective; surjectivity depends on codomain
f2 = {1: "a", 2: "a", 3: "b"}     # not injective
codomain = {"a", "b", "c"}

print(f"f1 injective: {is_injective(f1)}")
print(f"f1 surjective onto {codomain}: {is_surjective(f1, codomain)}")
print(f"f1 bijective: {is_bijective(f1, codomain)}")
print(f"f2 injective: {is_injective(f2)}")
```

해시 충돌은 함수가 단사가 아니라는 뜻입니다. 좋은 해시 함수는 완전한 단사는 아니어도 실무적으로 충분히 “거의 단사처럼” 행동하도록 설계됩니다.

### 5단계: 합성과 역함수

```python
def compose(g, f):
    """(g ∘ f)(x) = g(f(x))"""
    return lambda x: g(f(x))


def inverse(f: dict) -> dict:
    """Inverse exists only when f is injective"""
    if not is_injective(f):
        raise ValueError("non-injective functions have no inverse")
    return {v: k for k, v in f.items()}


f = lambda x: x + 1
g = lambda x: x * 2

h = compose(g, f)  # h(x) = 2(x + 1)
print(f"h(3) = {h(3)}")  # 8

mapping = {1: "a", 2: "b", 3: "c"}
inv = inverse(mapping)
print(f"Inverse: {inv}")
```

함수 합성은 함수형 프로그래밍의 핵심이고, 역함수는 암호학과 데이터 변환에서 빠지지 않는 개념입니다. 파이프라인 설계를 수학적으로 읽는 기본 도구라고 보면 됩니다.

## 주목할 점

- 멱집합의 크기는 `2ⁿ`이므로 모든 부분집합을 다 보는 탐색은 지수 시간입니다.
- 곱집합은 데이터베이스 테이블의 수학적 모델입니다.
- 단사성과 전사성은 해시, 암호, 매핑 설계의 기준이 됩니다.
- 합성과 역함수는 변환 파이프라인을 이해하는 핵심 도구입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 집합과 리스트를 섞어 생각한다 | 순서와 중복 가정이 깨진다 | 집합은 무순서, 중복 없음임을 명확히 둔다 |
| 공역과 치역을 혼동한다 | 전사 판정이 틀린다 | 공역은 선언, 치역은 실제 출력이다 |
| 부분 함수와 전함수를 구분하지 않는다 | 누락 입력에서 오류가 난다 | `dict` 같은 구현은 미정의 입력을 따로 처리한다 |
| 합성 순서를 바꾼다 | `(g ∘ f)(x)`를 반대로 읽는다 | 오른쪽에서 왼쪽으로 적용한다 |
| 역함수가 항상 있다고 가정한다 | 비단사 함수에서 정의가 깨진다 | 먼저 단사 여부를 확인한다 |

## 실무에서는 이렇게 사용합니다

- Python `set`과 `dict`는 집합과 함수의 직접 구현입니다.
- SQL JOIN은 곱집합 위에서 술어로 필터링하는 과정입니다.
- 해시맵은 키에서 값으로 가는 부분 함수입니다.
- 데이터 마이그레이션은 스키마 사이의 함수로 읽을 수 있습니다.
- ORM은 객체 도메인과 관계형 도메인 사이의 대응입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 자료구조를 고를 때 “이건 집합인가, 멀티셋인가, 순서가 필요한가”부터 묻습니다. 또한 함수가 단사인지, 역함수를 만들 수 있는지, 동일 입력에 대해 항상 동일 출력이 보장되는지 확인합니다. 이런 감각이 결국 멱등성, 캐시 키 설계, 스키마 변환 안정성으로 이어집니다.

## 체크리스트

- [ ] 집합과 리스트의 차이를 설명할 수 있다
- [ ] `|P(A)| = 2ⁿ` 공식을 기억한다
- [ ] 단사, 전사, 전단사를 구분할 수 있다
- [ ] 함수 합성의 순서를 이해한다
- [ ] 역함수가 존재하는 조건을 안다

## 연습 문제

1. `{a, b, c}`의 멱집합을 모두 나열하고 원소 수가 `2³ = 8`인지 확인해 보세요.

2. `f(x) = x²`가 실수 전체에서는 단사가 아니지만 `[0, ∞)`에서는 단사인 이유를 설명해 보세요.

3. 자신이 다루는 데이터베이스 테이블 하나를 골라, 어떤 곱집합의 부분집합으로 볼 수 있는지 적어 보세요.

## 정리 및 다음 단계

집합은 데이터를 담는 그릇이고, 함수는 집합 사이의 명확한 대응입니다. 멱집합, 곱집합, 합성, 역함수까지 이해하면 자료구조와 데이터베이스를 훨씬 더 본질적으로 읽을 수 있습니다.

다음 글에서는 집합 위에 정의되는 가장 중요한 구조인 관계와 동치관계를 살펴보겠습니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- **집합과 함수 (현재 글)**
- 관계와 동치관계 (예정)
- 증명 방법 (예정)
- 수열과 점화식 (예정)
- 조합과 경우의 수 (예정)
- 그래프 이론 기초 (예정)
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 2](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Set Theory](https://en.wikipedia.org/wiki/Set_theory)
- [Wikipedia — Function (mathematics)](https://en.wikipedia.org/wiki/Function_(mathematics))
- [Python Documentation — set, dict](https://docs.python.org/3/tutorial/datastructures.html#sets)

Tags: Computer Science, 이산수학, 집합론, 함수, 데이터베이스, 자료구조
