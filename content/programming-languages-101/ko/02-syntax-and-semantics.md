---
series: programming-languages-101
episode: 2
title: "Programming Languages 101 (2/10): 구문과 의미"
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
  - Programming Languages
  - Syntax
  - Semantics
  - Grammar
  - 파싱
seo_description: 렉서, 파서, AST, 평가기로 이어지는 흐름을 통해 구문 합법성과 의미 해석의 차이를 명확히 구분하고 에러의 층위를 이해하는 법을 다룹니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (2/10): 구문과 의미

빌드는 통과했는데 프로그램이 이상하게 동작하는 경우가 있습니다. 반대로 쉼표 하나 빠졌다는 이유로 아예 실행조차 못 하는 경우도 있습니다. 둘 다 에러이지만 같은 종류의 에러는 아닙니다.

이 글은 Programming Languages 101 시리즈의 두 번째 글입니다.

이 글에서는 언어를 이루는 두 축인 구문과 의미를 분리해서 보겠습니다. 문자가 합법적으로 배열됐는지와, 그 배열이 실제로 무엇을 뜻하는지는 다른 질문이라는 점을 분명히 잡아 두면 이후의 타입 시스템, 스코프, 클로저도 훨씬 쉽게 읽힙니다.

## 먼저 던지는 질문

- 구문과 의미의 경계는 정확히 어디일까요?
- 토큰, 문법, AST는 어떤 순서로 이어질까요?
- 합법적인 코드인데도 의도와 다르게 동작하는 이유는 무엇일까요?

## 큰 그림

![Programming Languages 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/02/02-01-concept-at-a-glance.ko.png)

*Programming Languages 101 2장 흐름 개요*

## 왜 중요한가

새 언어를 배울 때 문법을 빠르게 익히는 일, 에러 메시지를 빠르게 읽는 일, 같은 기호가 언어마다 왜 다르게 동작하는지 이해하는 일은 모두 이 두 축을 분리해서 볼 때 쉬워집니다. 특히 뒤에서 다룰 타입 시스템과 스코프는 같은 구문 위에 서로 다른 의미 규칙이 올라간 사례들입니다.

## 핵심 개념 한눈에 보기

렉서는 문자를 토큰으로 자르고, 파서는 토큰 순서가 문법에 맞는지 확인한 뒤 AST를 만듭니다. 여기까지가 구문 단계입니다. 그 다음 AST를 어떻게 해석할지, 어떤 타입 규칙을 적용할지, 실행하면 무슨 결과가 나올지를 정하는 단계가 의미입니다.

## 먼저 알아둘 용어

- 토큰: 더 이상 잘게 나누기 어려운 의미 단위입니다.
- 문법: 토큰이 어떤 순서로 놓일 수 있는지 정하는 규칙입니다.
- 추상 구문 트리(AST): 파서가 만든 코드의 트리 표현입니다.
- 정적 의미: 실행 전에 결정되는 의미 규칙입니다.
- 동적 의미: 실제 실행 중에 드러나는 의미 규칙입니다.

## 먼저 보는 예시

### 서로 다른 층위의 두 에러

```text
# Both are "errors," but they live in different layers.
print("hello"   # SyntaxError
divide(10, 0)   # legal syntax, throws ZeroDivisionError at runtime
```

첫 줄은 파서가 아예 받아들이지 못하는 코드입니다. 둘째 줄은 구문상 합법이지만, 실행하다가 0으로 나누는 순간에야 문제가 드러납니다. 둘을 같은 에러라고 묶어 보면 디버깅이 자꾸 헷갈립니다.

### 구문 통과 여부를 분리해서 보기

```python
import ast

src_ok  = "total = 3 + 4"
src_bad = "total = 3 +"

print(ast.parse(src_ok))   # passes syntax → produces an AST
ast.parse(src_bad)         # SyntaxError: invalid syntax
```

`ast.parse`는 구문이 통과했는지만 보여 줍니다. 의도와 맞는 의미인지까지 보장해 주지는 않습니다. 이 차이를 분리해서 보는 습관이 중요합니다.

## 작은 표현식을 직접 파싱해 보기

`3 + 4 * 2` 같은 간단한 표현식을 토큰으로 자르고, 문법에 맞춰 트리로 만든 뒤, 마지막에 평가해 보겠습니다.

### 1단계 — 토큰으로 자르기

```python
# 1_lex.py
import re

def tokenize(src: str) -> list[tuple[str, str]]:
    spec = [
        ("NUM", r"\d+"),
        ("OP",  r"[+*\-/()]"),
        ("WS",  r"\s+"),
    ]
    regex = "|".join(f"(?P<{n}>{p})" for n, p in spec)
    return [
        (m.lastgroup, m.group())
        for m in re.finditer(regex, src)
        if m.lastgroup != "WS"
    ]

print(tokenize("3 + 4 * 2"))
# [('NUM', '3'), ('OP', '+'), ('NUM', '4'), ('OP', '*'), ('NUM', '2')]
```

이 단계는 텍스트를 의미 있는 조각으로 나누는 일입니다. 아직 계산의 의미는 해석하지 않습니다.

### 2단계 — 문법 정의하기

BNF에 가까운 표기로 적으면 다음과 같습니다.

```text
expr    = term  ("+" term  | "-" term)*
term    = factor ("*" factor | "/" factor)*
factor  = NUM | "(" expr ")"
```

`*`와 `/`가 `term` 안에 더 깊게 들어가 있기 때문에 우선순위가 생깁니다. 우선순위는 계산기의 감각이 아니라 문법 구조에서 나옵니다.

### 3단계 — 파서가 구문 트리 만들기

```python
# 3_parse.py
class P:
    def __init__(self, toks):
        self.toks, self.i = toks, 0
    def peek(self): return self.toks[self.i] if self.i < len(self.toks) else (None, None)
    def eat(self):  t = self.peek(); self.i += 1; return t
    def expr(self):
        node = self.term()
        while self.peek()[1] in ("+", "-"):
            op = self.eat()[1]; node = (op, node, self.term())
        return node
    def term(self):
        node = self.factor()
        while self.peek()[1] in ("*", "/"):
            op = self.eat()[1]; node = (op, node, self.factor())
        return node
    def factor(self):
        k, v = self.eat()
        if k == "NUM": return int(v)
        if v == "(":
            node = self.expr(); self.eat(); return node
        raise SyntaxError(f"unexpected {v}")

from pprint import pprint
pprint(P(tokenize("3 + 4 * 2")).expr())
# ('+', 3, ('*', 4, 2))
```

트리를 보면 `4 * 2`가 하나의 하위 노드로 묶여 있습니다. 파서는 이런 구조를 통해 계산 우선순위를 코드 바깥이 아니라 트리 안에 저장합니다.

### 4단계 — 의미를 부여해 평가하기

```python
# 4_eval.py
def evaluate(node) -> int:
    if isinstance(node, int):
        return node
    op, a, b = node
    return {
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "*": lambda x, y: x * y,
        "/": lambda x, y: x // y,
    }[op](evaluate(a), evaluate(b))

print(evaluate(("+", 3, ("*", 4, 2))))  # 11
```

이제부터가 동적 의미입니다. 같은 트리라도 어떤 평가기를 붙이느냐에 따라 결과가 달라질 수 있습니다.

### 5단계 — 같은 구문, 다른 의미

```python
# 5_two_semantics.py
def evaluate_strange(node):
    if isinstance(node, int): return node
    op, a, b = node
    if op == "+": return evaluate_strange(a) * evaluate_strange(b)  # + as multiply
    return 0

print(evaluate_strange(("+", 3, ("*", 4, 2))))  # 24 — meaning changed
```

일부러 과장된 예지만 핵심은 분명합니다. 같은 구문 트리라도 다른 의미 규칙을 붙이면 완전히 다른 결과가 나옵니다. 구문과 의미는 정말로 분리된 축입니다.

## 이 코드에서 먼저 볼 점

- 구문은 합법성을, 의미는 해석 결과를 담당합니다.
- AST는 구문 단계의 최종 산출물이면서 의미 단계의 입력입니다.
- 우선순위와 결합 방향은 평가기가 아니라 문법에서 결정됩니다.
- 같은 AST에 다른 평가기를 붙이는 일이 바로 인터프리터와 컴파일러 설계의 핵심이 됩니다.

## 자주 하는 실수

1. 모든 에러를 같은 층위로 봅니다. SyntaxError와 RuntimeError는 출발점부터 다릅니다.
2. 빌드가 되면 코드가 맞다고 생각합니다. 구문 통과는 의미 정확성을 보장하지 않습니다.
3. 연산자 우선순위를 외우는 데 집착합니다. 복잡한 표현은 괄호로 의도를 드러내는 편이 낫습니다.
4. 같은 기호가 언어마다 같은 뜻일 것이라고 가정합니다. `+`만 봐도 문자열 처리에서 차이가 큽니다.
5. AST를 한 번도 직접 보지 않습니다. 한 번만 봐도 에러 메시지가 훨씬 또렷해집니다.

## 실무에서는 이렇게 본다

포매터, 린터, 리팩터링 도구, 자동 코드 변환기는 대부분 AST 위에서 동작합니다. 함수 호출을 모두 찾거나, 낡은 API를 새 API로 바꾸는 작업이 정규식보다 AST 기반으로 안정적인 이유도 여기에 있습니다. 결국 도구가 보는 코드는 문자 문자열이 아니라 구조화된 트리입니다.

로그를 읽을 때도 마찬가지입니다. `Unexpected token`은 구문 단계의 메시지고, `is not a function`은 실행 중 의미 단계의 메시지입니다. 어느 층위의 오류인지 먼저 구분하면 디버깅 시작점이 크게 빨라집니다.

## 체크리스트

- [ ] 구문과 의미의 차이를 한 문장으로 설명할 수 있는가?
- [ ] AST가 무엇이고 왜 필요한지 설명할 수 있는가?
- [ ] 정적 의미와 동적 의미를 구별할 수 있는가?
- [ ] 에러 메시지를 보고 어느 층위의 문제인지 가늠할 수 있는가?
- [ ] 같은 구문이 언어마다 다른 의미를 가질 수 있다는 점을 받아들였는가?

## 연습 문제

1. 위 표현식 문법에 `**` 연산자를 추가해 보세요. 문법과 평가기를 모두 바꿔야 합니다.
2. Python과 JavaScript에서 `1 + "2"`를 각각 실행해 보고, 차이가 구문 때문인지 의미 때문인지 한 줄로 설명해 보세요.
3. 최근에 만난 버그 하나를 골라, 그것이 구문 문제인지 정적 의미 문제인지 동적 의미 문제인지 분류해 보세요.

## 정리

구문은 합법성의 문제이고, 의미는 해석의 문제입니다. 이 둘을 분리하면 에러의 정체가 훨씬 선명해지고, 새 언어를 만났을 때 무엇부터 봐야 할지도 분명해집니다. 다음 글에서는 정적 의미의 핵심 도구인 타입 시스템으로 넘어가겠습니다.

## 심화 실전 노트: 타입, 스코프, 메모리 모델을 한 번에 연결하기

프로그래밍 언어를 실제로 운영 코드에 적용할 때는 문법 지식만으로 충분하지 않습니다. 타입 시스템이 어떤 오류를 언제 잡는지, 스코프 규칙이 상태 변경과 캡처를 어떻게 제한하는지, 메모리 모델이 동시성에서 어떤 가시성을 보장하는지를 한 묶음으로 이해해야 합니다. 이 세 축은 각각 독립 주제가 아니라, 코드 리뷰에서 같은 결함을 다른 이름으로 반복해서 만나게 만드는 공통 원인입니다.

### 타입 시스템 관점에서 보는 실패 패턴

다음 예시는 입력 파싱 이후 비즈니스 계층으로 전달되는 값의 타입이 느슨할 때 생기는 대표적인 문제를 보여줍니다.

```python
from typing import TypedDict, Literal

class PaymentCommand(TypedDict):
    order_id: str
    amount: int
    currency: Literal["KRW", "USD"]

def apply_discount(cmd: PaymentCommand) -> PaymentCommand:
    if cmd["currency"] == "KRW":
        cmd["amount"] = int(cmd["amount"] * 0.95)
    return cmd
```

핵심은 금액이 숫자라는 사실만으로 충분하지 않다는 점입니다. 정수인지, 소수점 정책이 무엇인지, 통화별 반올림 규칙이 무엇인지가 타입 설계에 반영되어야 합니다. 실무에서는 `int` 하나로 시작해 빠르게 배포한 뒤 정산 단계에서 누적 오차를 발견하는 일이 자주 발생합니다. 따라서 도메인 타입을 좁히는 전략이 필요합니다. 예를 들어 금액을 `Money` 값 객체로 감싸고, 생성 시점에 통화와 스케일을 강제하면 연산 단계를 통과하는 데이터 품질이 크게 올라갑니다.

### 스코프와 클로저를 리뷰할 때 보는 체크 포인트

클로저 자체는 강력한 도구이지만, 루프 변수 캡처와 가변 상태 결합이 만나면 예상과 다른 동작이 나옵니다.

```python
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda: i)
    return handlers

print([h() for h in make_handlers()])  # [2, 2, 2]
```

위 코드는 각 단계의 `i`를 복사하지 않고 같은 이름 해석 지점을 참조합니다. 의도한 결과가 `[0, 1, 2]`라면 기본 인자로 값을 고정해야 합니다.

```python
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda i=i: i)
    return handlers
```

이 차이는 단순 문법 이슈가 아니라 스코프 체계의 본질입니다. 변수의 "값"을 캡처하는지, "이름 해석 규칙"을 캡처하는지 구분하지 못하면 비동기 콜백, 이벤트 핸들러, 지연 실행 코드에서 재현 어려운 버그가 생깁니다.

### 메모리 모델을 읽는 최소 다이어그램

동시성 코드를 검토할 때는 아래처럼 책임 경계를 먼저 그려 두면 문제 재현과 해결 속도가 빨라집니다.

```text
[Thread A] write shared_flag=True
      |
      |  (reorder 가능성, 캐시 지연)
      v
[Memory Visibility Boundary]
      |
      v
[Thread B] read shared_flag
```

언어와 런타임은 이 경계에서 서로 다른 규칙을 제공합니다. 어떤 언어는 메모리 장벽이나 원자 연산을 명시적으로 요구하고, 어떤 언어는 메시지 전달 모델로 공유 메모리 자체를 줄입니다. 따라서 "동작한다"는 테스트 한 번으로 안전성을 결론 내리면 안 됩니다. 스레드 스케줄이 바뀌어도 같은 결과가 유지되는지, happens-before 관계가 코드 구조에 드러나는지 확인해야 합니다.

### 통합 적용 예시: 타입 + 스코프 + 메모리

작은 작업 큐 소비자를 예로 들면, 메시지 스키마를 엄격히 정의하고, 핸들러 생성 시 캡처 대상을 고정하고, 상태 공유를 최소화하는 세 가지를 함께 적용해야 안정성이 올라갑니다. 이 세 가지 중 하나만 빠져도 나머지 두 가지가 문제를 완전히 막아주지 못합니다. 결국 좋은 언어 사용 습관은 "문법 숙련"보다 "오류를 설계 단계에서 조기 차단하는 구조"에 가깝습니다.

## 처음 질문으로 돌아가기

- **구문과 의미의 경계는 정확히 어디일까요?**
  - 본문의 기준은 구문과 의미를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **토큰, 문법, AST는 어떤 순서로 이어질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **합법적인 코드인데도 의도와 다르게 동작하는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- **구문과 의미 (현재 글)**
- 타입 시스템 (예정)
- 스코프와 바인딩 (예정)
- 함수와 클로저 (예정)
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Python ast module documentation](https://docs.python.org/3/library/ast.html)
- [Crafting Interpreters (Bob Nystrom)](https://craftinginterpreters.com/)
- [Compilers: Principles, Techniques, and Tools (Dragon Book)](https://suif.stanford.edu/dragonbook/)
- [Backus–Naur Form (Wikipedia)](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form)

Tags: Computer Science, Programming Languages, Syntax, Semantics, Grammar, 파싱
