---
series: discrete-math-101
episode: 3
title: 집합과 함수
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
  - 이산수학
  - 집합론
  - 함수
  - 데이터베이스
  - 자료구조
seo_description: 집합 연산, 함수의 정의역과 치역, 단사·전사·일대일 대응을 통해 데이터 구조의 수학적 기반을 익힙니다.
last_reviewed: '2026-05-04'
---

# 집합과 함수

> Discrete Math 101 시리즈 (3/10)


## 이 글에서 다룰 문제

데이터베이스의 행은 곱집합의 원소이고, JOIN은 곱집합 위의 술어 평가입니다. 해시맵은 키 집합에서 값 집합으로의 부분 함수입니다. 함수형 프로그래밍의 `map`은 집합 사이의 함수 적용입니다. 집합과 함수를 모르면 이런 도구의 본질을 이해할 수 없습니다.

> 자료구조 = 집합과 함수의 효율적 구현

## 전체 흐름
> 집합은 원소의 모임, 함수는 집합 사이의 대응. 두 개념의 조합으로 모든 데이터 구조가 표현됩니다.

```text
   집합 A          함수 f: A → B          집합 B
  ┌─────┐                                ┌─────┐
  │ a₁  │ ─────────── f(a₁) ─────────── │ b₁  │
  │ a₂  │ ─────────── f(a₂) ─────────── │ b₂  │
  │ a₃  │ ─────────── f(a₃) ─────────── │ b₃  │
  └─────┘                                └─────┘
   정의역(domain)                       공역(codomain)
                                          치역(range)
                                          ⊆ 공역
```

## Before / After

**Before — 집합 사고 없이:**

```python
# 중복 제거를 직접 구현
result = []
for item in items:
    if item not in result:
        result.append(item)
```

**After — 집합 사용:**

```python
# 집합의 본질적 성질 활용
result = list(set(items))
```

## 단계별로 따라하기

### 1단계: 집합 표기법

```python
# 외연적 표기: 원소 나열
A = {1, 2, 3, 4, 5}

# 내포적 표기: 조건 명시
B = {x for x in range(1, 11) if x % 2 == 0}

# 멱집합(power set): 모든 부분집합의 집합
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

|A| = n이면 |P(A)| = 2ⁿ입니다. 부분집합의 개수가 지수적으로 증가하는 것은 알고리즘 복잡도의 핵심 이유 중 하나입니다.

### 2단계: 집합 연산

```python
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}
U = set(range(1, 11))  # 전체 집합

print(f"A ∪ B = {A | B}")        # 합집합
print(f"A ∩ B = {A & B}")        # 교집합
print(f"A - B = {A - B}")        # 차집합
print(f"A △ B = {A ^ B}")        # 대칭차
print(f"A^c (∈ U) = {U - A}")     # 여집합
print(f"|A ∪ B| = |A| + |B| - |A ∩ B| = {len(A) + len(B) - len(A & B)}")
```

마지막 등식은 포함-배제 원리(inclusion-exclusion)의 가장 단순한 형태로, 7장에서 다시 다룹니다.

### 3단계: 곱집합과 관계

```python
from itertools import product

A = {1, 2, 3}
B = {"x", "y"}

# A × B = {(a, b) | a ∈ A, b ∈ B}
cartesian = set(product(A, B))
print(f"A × B = {cartesian}")
print(f"|A × B| = |A| × |B| = {len(cartesian)}")

# 데이터베이스 테이블의 행은 곱집합의 원소
users = {"alice", "bob"}
roles = {"admin", "user"}
permissions = set(product(users, roles))
print(f"가능한 (user, role) 쌍: {permissions}")
```

데이터베이스 테이블의 스키마 자체가 곱집합입니다. CROSS JOIN은 곱집합을 직접 계산하는 연산입니다.

### 4단계: 함수의 종류

```python
def is_injective(f: dict) -> bool:
    """단사: 서로 다른 입력은 서로 다른 출력"""
    return len(set(f.values())) == len(f)


def is_surjective(f: dict, codomain: set) -> bool:
    """전사: 공역의 모든 원소가 치역에 포함"""
    return set(f.values()) == codomain


def is_bijective(f: dict, codomain: set) -> bool:
    """일대일 대응: 단사이면서 전사"""
    return is_injective(f) and is_surjective(f, codomain)


f1 = {1: "a", 2: "b", 3: "c"}     # 단사 O, 전사는 공역에 따라
f2 = {1: "a", 2: "a", 3: "b"}     # 단사 X
codomain = {"a", "b", "c"}

print(f"f1 단사: {is_injective(f1)}")
print(f"f1 전사 (공역 {codomain}): {is_surjective(f1, codomain)}")
print(f"f1 일대일 대응: {is_bijective(f1, codomain)}")
print(f"f2 단사: {is_injective(f2)}")
```

해시 함수가 충돌을 일으킬 때, 그것은 함수가 단사가 아니라는 뜻입니다. 좋은 해시 함수는 "거의" 단사가 되도록 설계됩니다.

### 5단계: 함수의 합성과 역함수

```python
def compose(g, f):
    """합성: (g ∘ f)(x) = g(f(x))"""
    return lambda x: g(f(x))


def inverse(f: dict) -> dict:
    """역함수 (단사일 때만 잘 정의됨)"""
    if not is_injective(f):
        raise ValueError("단사가 아니면 역함수가 없습니다")
    return {v: k for k, v in f.items()}


f = lambda x: x + 1
g = lambda x: x * 2

h = compose(g, f)  # h(x) = 2(x + 1)
print(f"h(3) = {h(3)}")  # 8

mapping = {1: "a", 2: "b", 3: "c"}
inv = inverse(mapping)
print(f"역함수: {inv}")
```

함수 합성은 함수형 프로그래밍의 핵심이며, 역함수는 암호학과 데이터 변환에서 필수적입니다.

## 이 코드에서 주목할 점

- 집합의 멱집합 크기는 2ⁿ — 모든 부분집합 탐색은 지수 시간
- 곱집합은 데이터베이스 테이블의 수학적 모델
- 함수의 단사·전사 성질은 해시·암호 설계의 기준
- 합성과 역함수는 변환 파이프라인의 기본 도구

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 집합과 리스트 혼동 | 순서·중복 가정으로 버그 | 집합은 unordered, 중복 없음 |
| 공역과 치역 혼동 | 전사 판정 오류 | 공역은 정의된 도착 집합, 치역은 실제 출력 |
| 부분 함수와 전 함수 혼동 | 미정의 입력에서 예외 | dict 접근 시 KeyError 처리 |
| 함수 합성 순서 바꿈 | (g∘f)(x) ≠ (f∘g)(x) | 오른쪽부터 적용됨을 명심 |
| 역함수 존재 가정 | 단사가 아니면 정의 불가 | 단사 검사 후 역함수 사용 |

## 실무에서는 이렇게 쓰입니다

- Python `set`/`dict`는 집합/함수의 직접 구현
- SQL JOIN은 곱집합 위에서 술어로 필터링
- 해시맵은 키 집합 → 값 집합의 부분 함수
- 데이터 마이그레이션은 스키마 사이의 함수
- ORM은 객체 도메인 → 관계형 도메인의 함수

## 체크리스트

- [ ] 집합과 리스트의 차이를 설명할 수 있는가
- [ ] 멱집합의 크기 공식을 알고 있는가
- [ ] 단사·전사·일대일 대응을 구분할 수 있는가
- [ ] 함수 합성의 순서를 이해했는가
- [ ] 역함수가 존재하기 위한 조건을 이해했는가

## 정리 및 다음 단계

집합은 데이터의 모임이고, 함수는 집합 사이의 명확한 대응입니다. 두 개념은 자료구조와 데이터베이스의 수학적 기반이며, 멱집합·곱집합·합성·역함수의 도구가 모든 변환을 설명합니다.

다음 글에서는 집합 위에 정의되는 가장 중요한 구조 — "관계와 동치관계" — 를 살펴봅니다.

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
