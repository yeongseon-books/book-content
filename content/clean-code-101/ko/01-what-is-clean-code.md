---
series: clean-code-101
episode: 1
title: "Clean Code 101 (1/10): Clean Code란 무엇인가?"
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
  - Readability
  - SoftwareEngineering
  - CodeQuality
  - Refactoring
seo_description: Clean Code의 기준과 변경 비용을 낮추는 핵심 신호를 설명합니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (1/10): Clean Code란 무엇인가?

코드는 일단 동작하면 끝난 것처럼 보이지만, 실제 비용은 그다음 변경에서 드러납니다.

이 글은 Clean Code 101 시리즈의 첫 번째 글입니다.

여기서는 동작하는 코드와 읽기 쉬운 코드, 그리고 바꾸기 쉬운 코드가 어떻게 다른지 한 번에 정리하겠습니다.

## 먼저 던지는 질문

- Clean Code를 판단할 때 어떤 신호를 먼저 봐야 할까요?
- 동작하는 코드와 읽기 쉬운 코드의 차이는 무엇일까요?
- 작은 원칙이 실제 유지보수 비용에 왜 큰 차이를 만들까요?

## 큰 그림

![Clean Code 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/01/01-01-concept-at-a-glance.ko.png)

*Clean Code 101 1장 흐름 개요*

이 그림에서는 Clean Code란 무엇인가?를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Clean Code란 무엇인가?의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

코드는 한 번 작성하고 여러 번 읽습니다. 그래서 가독성은 단순한 미학이 아니라 변경 비용을 결정하는 요소입니다. 이름이 흐리고 분기가 깊고 함수가 길어질수록, 다음 수정은 더 느려지고 더 위험해집니다.

현업에서는 이 차이가 아주 직접적으로 드러납니다. 기능 하나를 추가할 때 “어디를 바꿔야 하는지 바로 보이는 코드”와 “건드리면 다른 곳이 깨질 것 같은 코드”는 같은 기능을 구현해도 속도와 품질이 완전히 달라집니다.

## 한눈에 보는 개념

동작은 시작일 뿐이고, 신뢰는 결국 이해 가능성과 변경 용이성에서 나옵니다.

## 핵심 용어

- **Clean code**: 의도가 분명하고, 바꾸는 비용이 낮은 코드입니다.
- **Readability**: 다른 개발자가 빠르게 이해할 수 있는 상태입니다.
- **Cognitive load**: 코드 한 덩어리를 이해하는 데 필요한 정신적 부담입니다.
- **Smell**: 중복, 거대 함수, 깊은 분기처럼 개선이 필요하다는 신호입니다.
- **Refactoring**: 동작은 유지한 채 내부 구조를 개선하는 작업입니다.

## Before/After

**Before — works, that's all**

```python
def f(d, t):
    return d * (1 + t)
```

**After — intent visible**

```python
def total_with_tax(amount: int, tax_rate: float) -> float:
    return amount * (1 + tax_rate)
```

두 번째 버전은 코드 길이가 거의 늘지 않았지만, 호출하는 쪽에서 의도가 훨씬 분명하게 보입니다. Clean Code의 핵심은 이런 식으로 작은 비용으로 큰 이해도를 얻는 데 있습니다.

## 실전 적용: 지저분함을 먼저 측정하기

### Step 1 — Function length

```python
# 1_length.py
def process(order):
    # 80 lines ...
    pass
```

함수가 20줄을 넘기기 시작하면, 길어진 이유를 먼저 설명할 수 있어야 합니다. 설명이 길어진다면 대개 함수도 이미 너무 많은 일을 하고 있습니다.

### Step 2 — Argument count

```python
# 2_args.py
def create_user(name, email, age, address, role, plan, ref):
    ...
```

인자가 세 개를 넘기기 시작하면, 하나의 객체로 묶을 수 있는지 점검하는 편이 좋습니다. 함수 시그니처는 그 자체로 설계의 부담을 드러냅니다.

### Step 3 — Indentation depth

```python
# 3_depth.py
if a:
    if b:
        if c:
            do()
```

들여쓰기 깊이가 3을 넘으면 추출이나 분기 재구성이 필요하다는 신호로 보는 것이 좋습니다. 깊이는 곧 인지 부담입니다.

### Step 4 — Honest names

```python
# 4_name.py
def calc(x):  # of what?
    ...
def calculate_invoice_total(line_items):
    ...
```

이름이 거짓말하면 코드를 읽는 사람도 잘못된 기대를 갖습니다. 반대로 정직한 이름은 주석 몇 줄을 대신합니다.

### Step 5 — Measure cognitive load

```bash
# 5_cc.sh
radon cc app/ -a -s
```

순환 복잡도가 10을 넘는 곳은 분해 후보로 보는 편이 안전합니다. 측정하지 않으면 개선도 우선순위도 흐려집니다.

## 검증 방법

```bash
radon cc app/ -a -s
ruff check app/
```

**기대 결과**

- 복잡도 등급이 높은 함수가 어디인지 바로 보입니다.
- 이름과 분기, 함수 길이가 한 번에 점검됩니다.

## 실패하기 쉬운 지점

- 복잡도 수치만 보고 이름과 책임 분리를 놓칩니다.
- lint 경고가 많아서 진짜 설계 냄새가 묻힙니다.

## 이 코드에서 먼저 봐야 할 점

- 이름은 가장 먼저 의도를 보여 주는 인터페이스입니다.
- 함수 길이, 분기 깊이, 인자 수는 감상이 아니라 측정 가능한 신호입니다.
- 작은 규칙이 누적되면 코드베이스 전체의 변경 비용이 달라집니다.

## 자주 하는 실수 5가지

1. **"동작하니 됐다"에서 멈추기.** 몇 달 뒤에는 그 한 줄이 기술 부채가 됩니다.
2. **거대 함수를 방치하기.** 디버깅과 변경이 동시에 어려워집니다.
3. **거짓말하는 이름 붙이기.** 코드와 이름이 다르면 읽는 사람이 계속 속습니다.
4. **깊은 들여쓰기 유지하기.** 핵심 흐름이 분기에 묻힙니다.
5. **측정하지 않기.** 나빠지는 추세를 수치로 잡지 못합니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 함수 길이, 복잡도, 이름 기준을 코드 리뷰 가이드에 명시합니다. 그리고 lint나 정적 분석으로 반복되는 문제를 자동으로 드러내서, 리뷰어가 더 중요한 설계 판단에 집중할 수 있게 만듭니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 코드는 한 번 쓰고 여러 번 읽습니다.
- 이름이 문서의 절반을 대신합니다.
- 측정 가능한 것은 개선할 수 있습니다.
- 작은 규칙이 큰 품질 차이를 만듭니다.
- Clean Code는 결국 다음 사람의 시간을 아끼는 일입니다.

## 체크리스트

- [ ] 함수가 20줄 이하인가?
- [ ] 인자가 3개 이하인가?
- [ ] 들여쓰기 깊이가 3 이하인가?
- [ ] 이름이 의도를 말하는가?
- [ ] 복잡도를 실제로 측정하는가?

## 연습 문제

1. 저장소에서 가장 긴 함수를 하나 골라 분해 계획을 적어 보세요.
2. 거짓말하는 이름 세 개를 찾아 더 정직하게 바꿔 보세요.
3. 프로젝트에 lint 규칙 세 개를 추가해 보세요.

## 정리 및 다음 단계

Clean Code는 추상적인 취향이 아니라, 측정 가능한 작은 원칙의 합입니다. 다음 글에서는 그중에서도 가장 즉각적인 효과를 내는 주제인 이름 짓기를 다룹니다.

## 처음 질문으로 돌아가기

- **Clean Code를 판단할 때 어떤 신호를 먼저 봐야 할까요?**
  - 본문의 기준은 Clean Code란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **동작하는 코드와 읽기 쉬운 코드의 차이는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **작은 원칙이 실제 유지보수 비용에 왜 큰 차이를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Clean Code란 무엇인가? (현재 글)**
- 이름 짓기 (예정)
- 함수 작게 만들기 (예정)
- 조건문 줄이기 (예정)
- 중복 제거 (예정)
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [A Philosophy of Software Design — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [Google — Code Health Articles](https://testing.googleblog.com/search/label/Code%20Health)
- [Ruff rule reference](https://docs.astral.sh/ruff/rules/)
- [radon documentation](https://radon.readthedocs.io/en/latest/)
Tags: Computer Science, CleanCode, Readability, SoftwareEngineering, CodeQuality, Refactoring
