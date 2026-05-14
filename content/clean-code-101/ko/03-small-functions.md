---
series: clean-code-101
episode: 3
title: 함수 작게 만들기
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
  - CleanCode
  - Functions
  - SRP
  - Refactoring
  - Readability
seo_description: 함수가 한 가지 일만 하도록 작게 쪼개는 원칙과 추출 방법을 배웁니다. 가독성을 높이고 테스트와 재사용이 쉬운 코드를 만드는 기법을 익힙니다.
last_reviewed: '2026-05-15'
---

# 함수 작게 만들기

긴 함수는 처음에는 편하지만 시간이 갈수록 설명과 예외 처리가 한데 뭉치면서 읽기 어려워집니다.

이 글은 Clean Code 101 시리즈의 3번째 글입니다.

여기서는 함수가 충분히 작다는 말이 실제로 무엇을 뜻하는지, 그리고 큰 함수를 어떻게 안전하게 쪼갤 수 있는지 살펴보겠습니다.

---

## 이 글에서 다룰 문제

- 작은 함수가 주는 효과는 무엇일까요?
- Extract Function은 어떤 순서로 적용해야 안전할까요?
- 부수 효과를 줄이는 대표 패턴은 무엇일까요?
- Command-Query Separation은 왜 디버깅 시간을 줄일까요?
- 매개변수 객체는 언제 도입하는 편이 좋을까요?

> 함수가 작아질수록 주석보다 이름이 더 많은 일을 하게 되고, 테스트도 훨씬 쉬워집니다.

## 왜 중요한가

작은 함수의 장점은 단순히 줄 수가 적다는 데 있지 않습니다. 핵심은 “이 함수가 한 가지 일만 한다”는 사실이 이름과 본문에서 동시에 드러난다는 점입니다. 그 상태가 되면 함수 본문은 설명문이 아니라 목차처럼 읽히기 시작합니다.

반대로 큰 함수는 계속 주석을 요구합니다. 그리고 주석이 많아질수록 코드와 설명이 어긋날 가능성도 커집니다. 그래서 작은 함수는 가독성 문제이면서 동시에 유지보수와 테스트 전략의 문제이기도 합니다.

## 한눈에 보는 개념

![함수 작게 만들기](../../../assets/clean-code-101/03/03-01-concept-at-a-glance.ko.png)

*큰 함수를 잘게 나누는 흐름: 추출이 이름을 만들고, 이름이 재사용과 테스트를 쉽게 만듭니다.*

추출은 이름을 가능하게 만들고, 좋은 이름은 재사용과 테스트를 쉽게 만듭니다.

## 핵심 용어

- **SRP (Single Responsibility)**: 변경 이유가 하나인 상태입니다.
- **Extract Function**: 블록을 별도 함수로 뽑아내는 리팩토링입니다.
- **Command-Query Separation**: 함수는 하거나 답하거나 둘 중 하나만 해야 한다는 원칙입니다.
- **Pure function**: 같은 입력에 같은 출력을 내고, 부수 효과가 없는 함수입니다.
- **Parameter Object**: 여러 인자를 하나의 객체로 묶는 방식입니다.

## Before/After

**Before**

```python
def checkout(cart, user, addr, coupon):
    # 60 lines: validate + price + tax + ship + log + email + save
    ...
```

**After**

```python
def checkout(cart, user, addr, coupon):
    items = validate_cart(cart, user)
    total = price_with_tax(items, addr)
    order = save_order(user, items, total, coupon)
    notify_user(user, order)
    return order
```

두 번째 버전의 본문은 구현 세부보다 흐름을 먼저 보여 줍니다. 좋은 함수 본문은 설명문이 아니라 목차처럼 읽혀야 합니다.

## 실전 적용: 안전하게 추출하기

### Step 1 — Partial extraction

```python
# 1_extract.py
def total(items):
    s = 0
    for it in items:
        s += it.price * it.qty
    return s
```

반복문은 추출 후보가 되기 좋습니다. 계산이 하나의 의미 단위로 보이기 시작하면 별도 함수 이름을 붙일 수 있습니다.

### Step 2 — Intent name

```python
# 2_intent.py
def line_total(item): return item.price * item.qty
def total(items): return sum(line_total(it) for it in items)
```

이름을 붙이는 순간 코드 길이는 비슷해도 이해 비용은 줄어듭니다. 좋은 추출은 줄 수보다 의미를 더 잘 드러내는 데 있습니다.

### Step 3 — Command/Query split

```python
# 3_cqs.py
class Account:
    def withdraw(self, amount):  # command
        self.balance -= amount
    def is_overdrawn(self):      # query
        return self.balance < 0
```

질문하는 함수는 상태를 바꾸지 않는 편이 좋습니다. 읽는 쪽에서 예상 가능한 동작이 디버깅 시간을 줄입니다.

### Step 4 — Parameter object

```python
# 4_param_obj.py
from dataclasses import dataclass
@dataclass
class Range: lo: int; hi: int
def in_range(value, r: Range): return r.lo <= value <= r.hi
```

인자가 많아질수록 호출 지점의 소음도 커집니다. 묶을 수 있는 인자는 객체로 올려서 문맥을 보존하는 편이 낫습니다.

### Step 5 — Make it pure

```python
# 5_pure.py
def discount(price: int, rate: float) -> int:
    return int(price * (1 - rate))
```

순수 함수는 테스트가 가장 쉽습니다. 작은 함수와 순수 함수는 함께 갈수록 효과가 커집니다.

## 검증 방법

```bash
radon cc app/ -a -s
python -m pytest -q tests/test_checkout.py
```

**기대 결과**

- 추출 전후 복잡도와 테스트 안정성이 함께 비교됩니다.
- 함수 본문이 목차처럼 읽히는지 바로 확인할 수 있습니다.

## 실패하기 쉬운 지점

- 추출 뒤 인자 수가 급격히 늘어납니다.
- 질문 함수가 여전히 상태를 바꿉니다.

## 이 코드에서 먼저 봐야 할 점

- 함수 본문은 목차처럼 읽혀야 합니다.
- 이름이 주석을 대신해야 합니다.
- Command/Query를 분리하면 버그 추적이 쉬워집니다.

## 자주 하는 실수 5가지

1. **거대 함수를 변수만 늘려서 정리하기.** 새로운 의미 단위가 생기지 않습니다.
2. **추출 뒤 인자가 폭발하기.** 객체로 묶을 시점인지 봐야 합니다.
3. **질문 함수가 상태를 바꾸기.** 버그의 주요 원인입니다.
4. **테스트 없이 추출하기.** 회귀 위험이 커집니다.
5. **과도하게 잘게 쪼개기.** 한 줄 함수가 너무 많아지면 오히려 흐름이 끊깁니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 함수 길이, 인자 수, 복잡도를 lint와 PR 가이드로 함께 관리합니다. 큰 함수는 자동으로 경고를 띄우고, 리뷰에서는 “한 가지 일만 하는가”를 별도의 질문으로 다룹니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 함수 본문이 목차처럼 읽혀야 합니다.
- 이름이 주석을 대신해야 합니다.
- Query는 상태를 바꾸면 안 됩니다.
- 인자가 셋을 넘으면 냄새일 수 있습니다.
- 순수 함수는 테스트의 가장 좋은 친구입니다.

## 체크리스트

- [ ] 함수가 정확히 한 가지 일만 하는가?
- [ ] 본문이 목차처럼 읽히는가?
- [ ] 인자가 3개 이하인가?
- [ ] Query가 부수 효과를 만들지 않는가?
- [ ] 추출 전후를 지키는 테스트가 있는가?

## 연습 문제

1. 함수 본문이 목차처럼 읽히도록 하나를 다시 써 보세요.
2. 인자가 4개 이상인 함수를 객체 하나로 묶어 보세요.
3. CQS를 어기는 함수 하나를 찾아 고쳐 보세요.

## 정리 및 다음 단계

작은 함수는 좋은 이름과 테스트를 가능하게 만듭니다. 다음 글에서는 큰 함수를 키우는 가장 흔한 원인인 조건문을 어떻게 단순화할지 다룹니다.

<!-- toc:begin -->
- [Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [이름 짓기](./02-naming.md)
- **함수 작게 만들기 (현재 글)**
- 조건문 줄이기 (예정)
- 중복 제거 (예정)
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Clean Code (Ch. 3 Functions)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Refactoring — Extract Function](https://refactoring.com/catalog/extractFunction.html)
- [Martin Fowler — Command Query Separation](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- [Refactoring — Introduce Parameter Object](https://refactoring.com/catalog/introduceParameterObject.html)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
Tags: Computer Science, CleanCode, Functions, SRP, Refactoring, Readability
