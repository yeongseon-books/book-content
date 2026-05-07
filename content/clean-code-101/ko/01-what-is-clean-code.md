---
series: clean-code-101
episode: 1
title: Clean Code란 무엇인가?
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
  - Readability
  - SoftwareEngineering
  - CodeQuality
  - Refactoring
seo_description: Clean Code의 정의, 가독성과 의도, 변경 비용을 줄이는 작은 원칙을 정리합니다.
last_reviewed: '2026-05-04'
---

# Clean Code란 무엇인가?

> Clean Code 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 동작하는 코드와 깨끗한 코드는 어떻게 다른가요?

> 동작은 최소 조건입니다. 깨끗함은 다음 사람을 위한 배려입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- Clean Code의 정의와 4가지 신호
- 동작 vs 가독성 vs 변경 비용
- 작은 원칙들이 모여 만드는 효과
- "깨끗하다"의 객관적 측정 가능한 표지
- 시리즈 전체 지도

## 왜 중요한가

코드는 한 번 쓰이고 100번 읽힙니다. 가독성이 곧 변경 비용을 결정합니다.

> Clean Code는 다음 사람의 시간을 줄이는 일이다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    W["동작"] --> R["가독성"]
    R --> C["변경 용이"]
    C --> T["신뢰"]
```

동작은 시작이고, 신뢰가 끝입니다.

## 핵심 용어 정리

- **Clean Code**: 의도가 분명하고 변경 비용이 낮은 코드.
- **Readability**: 다른 개발자가 빨리 이해.
- **Cognitive load**: 코드 한 단위를 이해하는 데 드는 인지 부담.
- **Smell**: 잘못된 신호(중복, 거대 함수 등).
- **Refactoring**: 동작을 바꾸지 않고 구조 개선.

## Before/After

**Before — 동작만 OK**

```python
def f(d, t):
    return d * (1 + t)
```

**After — 의도 분명**

```python
def total_with_tax(amount: int, tax_rate: float) -> float:
    return amount * (1 + tax_rate)
```

이름과 타입이 의도를 말합니다.

## 실습: 더러움을 측정하기

### 1단계 — 함수 길이

```python
# 1_length.py
def process(order):
    # 80 lines ...
    pass
```

20 lines를 넘으면 "왜?"를 적어 두세요.

### 2단계 — 매개변수 수

```python
# 2_args.py
def create_user(name, email, age, address, role, plan, ref):
    ...
```

3개 넘어가면 객체로 묶을 후보입니다.

### 3단계 — 들여쓰기 깊이

```python
# 3_depth.py
if a:
    if b:
        if c:
            do()
```

3 depth 넘으면 함수 분리 후보입니다.

### 4단계 — 이름의 정직함

```python
# 4_name.py
def calc(x):  # 무엇을?
    ...
def calculate_invoice_total(line_items):
    ...
```

이름이 거짓이면 코드가 거짓입니다.

### 5단계 — 인지 부담 측정

```bash
# 5_cc.sh
radon cc app/ -a -s
```

cyclomatic complexity 10 이상은 분해 후보.

## 이 코드에서 주목할 점

- 이름이 의도를 말합니다.
- 함수 길이/깊이/인자가 측정 가능한 신호.
- 작은 원칙이 모여 큰 차이를 만듭니다.

## 자주 하는 실수 5가지

1. **"동작하면 됐어".** 6개월 후 이 말은 빚이 됩니다.
2. **거대 함수.** 디버깅이 곧 고문.
3. **거짓말하는 이름.** 코드와 이름의 불일치.
4. **깊은 들여쓰기.** 분기가 의도를 가립니다.
5. **측정 안 함.** 좋아지지 않습니다.

## 실무에서는 이렇게 쓰입니다

좋은 팀은 함수 길이/복잡도/이름 길이의 임계값을 코드 리뷰 가이드에 두고, 자동 lint로 점차 강제합니다. 큰 함수는 PR에서 자동 코멘트로 분리 제안.

## 시니어 엔지니어는 이렇게 생각합니다

- 코드는 한 번 쓰고 백 번 읽힌다.
- 이름이 절반의 문서다.
- 측정되는 것이 개선된다.
- 작은 원칙이 큰 코드를 만든다.
- Clean Code는 다음 사람을 위한 배려다.

## 체크리스트

- [ ] 함수가 20 lines 이하인가?
- [ ] 매개변수가 3개 이하인가?
- [ ] 들여쓰기 3 depth 이하인가?
- [ ] 이름이 의도를 말하는가?
- [ ] 복잡도를 측정하는가?

## 연습 문제

1. 본인 저장소에서 가장 긴 함수 1개를 골라 분해 안을 적어 보세요.
2. 거짓말하는 이름 3개를 찾아 다시 지어 보세요.
3. lint 룰 3개를 추가해 보세요.

## 정리 및 다음 단계

Clean Code는 측정 가능한 작은 원칙들의 합입니다. 다음 글에서는 가장 큰 단일 효과 — 이름 짓기 — 를 봅니다.

<!-- toc:begin -->
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

Tags: Computer Science, CleanCode, Readability, SoftwareEngineering, CodeQuality, Refactoring
