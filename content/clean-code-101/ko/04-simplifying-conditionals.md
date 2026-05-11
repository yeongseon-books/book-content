---
series: clean-code-101
episode: 4
title: 조건문 줄이기
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
  - CleanCode
  - Conditionals
  - GuardClauses
  - Refactoring
  - Readability
seo_description: 가드 절, 조기 반환, 다형성과 전략 패턴으로 중첩 조건문을 줄이는 법.
last_reviewed: '2026-05-11'
---

# 조건문 줄이기

> Clean Code 101 시리즈 (4/10)


## 이 글에서 다룰 문제

중첩된 조건문은 복잡도를 가장 빠르게 키우는 원인입니다. 깊이가 한 단계만 줄어도 읽는 부담이 크게 줄어듭니다.

> 깊이는 곧 인지 부담이다.

## 전체 흐름
```mermaid
flowchart LR
    N["중첩 if"] --> G["가드 절"]
    G --> P["다형성"]
    P --> T["테이블 주도"]
    T --> R["평탄한 흐름"]
```

가드 절, 다형성, 테이블 주도 설계를 순서대로 익히면 분기를 훨씬 단순하게 다룰 수 있습니다.

## Before/After

**Before**

```python
def price(user, item):
    if user is not None:
        if user.is_active:
            if item is not None:
                if item.in_stock:
                    return item.price * (0.9 if user.is_member else 1.0)
                else:
                    return None
            else:
                return None
        else:
            return None
    else:
        return None
```

**After**

```python
def price(user, item):
    if user is None or not user.is_active: return None
    if item is None or not item.in_stock: return None
    rate = 0.9 if user.is_member else 1.0
    return item.price * rate
```

중첩 깊이가 4단계에서 1단계로 줄어들었습니다.

## 분기를 줄이는 5단계

### 1단계 — 가드 절로 평탄화

```python
# 예시 파일: 1_guard.py
def total(items):
    if not items:
        return 0
    return sum(it.price for it in items)
```

비어 있는 입력은 바로 반환해 본문을 평평하게 유지합니다.

### 2단계 — 부정 조건 뒤집기

```python
# 예시 파일: 2_positive.py
# 이전 형태: if not user.is_inactive: ...
# 개선 후:
def can_login(user):
    if not user.is_active:
        return False
    return user.email_verified
```

이중 부정은 한 번 더 해석해야 하므로 가능한 한 피하는 편이 좋습니다.

### 3단계 — 다형성으로 분기 제거

```python
# 예시 파일: 3_poly.py
class Shape:
    def area(self): ...
class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14 * self.r * self.r
class Square(Shape):
    def __init__(self, a): self.a = a
    def area(self): return self.a * self.a

def total_area(shapes): return sum(s.area() for s in shapes)
```

타입별 분기를 각 클래스가 맡으면 호출부는 훨씬 단순해집니다.

### 4단계 — 전략 패턴

```python
# 예시 파일: 4_strategy.py
def percent_off(price, rate): return price * (1 - rate)
def fixed_off(price, amount): return max(0, price - amount)

DISCOUNTS = {"member": lambda p: percent_off(p, 0.1),
             "coupon10": lambda p: fixed_off(p, 10)}

def apply(price, kind): return DISCOUNTS[kind](price)
```

분기문 대신 딕셔너리 조회로 정책을 선택합니다.

### 5단계 — 테이블 주도

```python
# 예시 파일: 5_table.py
GRADES = [(90, "A"), (80, "B"), (70, "C"), (0, "F")]
def grade(score):
    return next(g for s, g in GRADES if score >= s)
```

길게 이어진 if/elif 사슬을 자료구조 하나로 바꿀 수 있습니다.

## 이 코드에서 주목할 점

- 가드 절은 본문 들여쓰기를 빠르게 줄여 줍니다.
- 다형성은 타입 분기를 구조로 흡수합니다.
- 테이블은 정책을 코드보다 데이터에 가깝게 표현합니다.

## 자주 하는 실수 5가지

1. **가드 없이 깊이 들어감.** else가 늘어납니다.
2. **부정 조건을 그대로 사용.** 이중 부정 발생.
3. **타입 검사로 분기.** isinstance 남발.
4. **전략에 상태를 둠.** 테스트가 어려워집니다.
5. **테이블 정렬에 의존.** 우선순위가 깨지기 쉽습니다.

## 실무에서는 이렇게 쓰입니다

요금 계산, 권한 체크, 라우팅처럼 정책이 자주 바뀌는 영역은 테이블이나 전략 패턴 후보입니다. 이런 구조를 잡아 두면 정책 변경이 훨씬 안전해집니다.

## 체크리스트

- [ ] 함수 깊이 ≤ 3?
- [ ] 가드 절을 먼저 두었나?
- [ ] 부정 조건을 양수로 바꿨나?
- [ ] 타입 분기는 다형성 후보인가?
- [ ] 정책 분기는 테이블/전략 후보인가?

## 정리 및 다음 단계

조건문은 줄일수록 코드의 핵심 흐름이 또렷해집니다. 다음 글에서는 분기만큼 자주 문제를 만드는 중복을 다뤄 보겠습니다.

<!-- toc:begin -->
- [Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [이름 짓기](./02-naming.md)
- [함수 작게 만들기](./03-small-functions.md)
- **조건문 줄이기 (현재 글)**
- 중복 제거 (예정)
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Refactoring — Replace Nested Conditional with Guard Clauses](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)
- [Refactoring — Replace Conditional with Polymorphism](https://refactoring.com/catalog/replaceConditionalWithPolymorphism.html)
- [Strategy Pattern (Refactoring Guru)](https://refactoring.guru/design-patterns/strategy)
- [Clean Code (Ch. 3 Functions, Ch. 6 Objects)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

Tags: Computer Science, CleanCode, Conditionals, GuardClauses, Refactoring, Readability
