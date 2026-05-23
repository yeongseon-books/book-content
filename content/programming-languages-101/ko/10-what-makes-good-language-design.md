---
series: programming-languages-101
episode: 10
title: "Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?"
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
  - LanguageDesign
  - Consistency
  - Simplicity
  - Expressiveness
seo_description: 좋은 언어 설계를 일관성, 단순성, 표현력, 안전성, 성능으로 살펴봅니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?

어떤 언어를 두고 “잘 설계됐다”라고 말할 때가 있습니다. 하지만 그 말이 구체적으로 무엇을 뜻하는지는 막상 설명하기 어렵습니다. 빠르다는 뜻인지, 배우기 쉽다는 뜻인지, 실수를 잘 막는다는 뜻인지가 섞여 있기 때문입니다.

이 글에서는 좋은 언어 설계를 만능 정답으로 보지 않고, 분명한 우선순위를 가진 트레이드오프로 보겠습니다. 지금까지 다룬 구문, 타입, 스코프, 클로저, 객체, 메모리, 실행 모델, 정적과 동적의 차이를 모두 설계 축 위에 다시 올려 보겠습니다.

![Programming Languages 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/10/10-01-concept-at-a-glance.ko.png)
*Programming Languages 101 10장 흐름 개요*

## 먼저 던지는 질문

- 언어 설계를 볼 때 어떤 축으로 평가해야 할까요?
- 일관성, 단순성, 표현력, 안전성, 성능은 왜 서로 충돌할까요?
- Python, Go, Rust는 같은 문제에 왜 다른 답을 내릴까요?

## 왜 중요한가

설계 감각은 언어를 평가할 때만 쓰이지 않습니다. API 하나를 설계할 때도, 내부 DSL을 만들 때도, 함수 시그니처 하나를 정할 때도 같은 감각이 필요합니다. 언어 설계는 결국 소프트웨어 설계 감각의 큰 버전입니다.

## 핵심 개념 한눈에 보기

다섯 축은 서로 독립적이지 않습니다. 표현력을 높이면 단순성이 줄고, 안전성을 높이면 문법이나 사용법이 무거워질 수 있습니다. 좋은 설계를 보려면 무엇을 얻고 무엇을 포기했는지 함께 읽어야 합니다.

## 먼저 알아둘 용어

- 일관성: 비슷한 문제를 비슷한 코드 모양으로 풀게 만드는 성질입니다.
- 단순성: 배워야 할 규칙과 예외가 적은 정도입니다.
- 표현력: 의도를 짧고 정확하게 적을 수 있는 정도입니다.
- 안전성: 잘못된 프로그램을 빌드나 실행 단계에서 막아 주는 정도입니다.
- 성능: 같은 작업을 더 적은 시간과 메모리로 처리하는 정도입니다.

## 먼저 보는 예시

### 느낌으로만 평가할 때

> "이 언어는 그냥 좋다."

### 설계 축으로 분해할 때

> "이 언어는 표현력과 단순성을 높이는 대신 안전성 일부를 포기했다. 짧은 스크립트에는 강하지만 장기 서비스에는 보완 장치가 더 필요하다."

두 문장은 같은 취향을 말할 수 있지만, 두 번째 문장만이 설계 이유를 설명합니다.

## 세 언어를 다섯 축으로 비교하기

### 1단계 — 같은 문제, 세 가지 답

문자열 리스트의 길이 합을 구하는 같은 문제를 세 언어로 보겠습니다.

```python
# Python
def total_len(xs: list[str]) -> int:
    return sum(len(x) for x in xs)
```

```go
// Go
func TotalLen(xs []string) int {
    n := 0
    for _, x := range xs {
        n += len(x)
    }
    return n
}
```

```rust
// Rust
fn total_len(xs: &[String]) -> usize {
    xs.iter().map(|x| x.len()).sum()
}
```

같은 작업인데도 길이, 명시성, 안전성의 무게 중심이 다릅니다. 언어 설계 차이는 이런 평범한 코드에서 가장 잘 드러납니다.

### 2단계 — 일관성 보기

```python
# 2_consistency.py
# Python: sum/len/for 컬렉션 전체에서 모양 유지 — 높은 일관성
print(sum([1,2,3]))
print(sum((1,2,3)))
print(sum({1,2,3}))
```

비슷한 컬렉션에 같은 인터페이스를 반복해서 쓸 수 있다면 일관성이 높습니다. 배운 패턴이 다른 곳에서도 그대로 통하는 느낌이 강해집니다.

### 3단계 — 단순성과 표현력의 줄다리기

```python
# 3_expressiveness.py
xs = [1, 2, 3, 4, 5]
print([x*x for x in xs if x % 2])     # high expressiveness
# Go에는 리스트 컴프리헨션이 없다 → 더 단순하지만 표현력이 낮음
```

Python은 의도를 짧게 적게 해 줍니다. 반면 Go는 이런 압축된 구문을 줄여 배워야 할 규칙을 낮춥니다. 어느 쪽이 더 낫다고 단정하기보다, 무엇을 우선했는지를 읽는 편이 정확합니다.

### 4단계 — 안전성과 단순성의 교환

```rust
// 4_safety.rs
fn first(xs: &[i32]) -> Option<&i32> {
    xs.first()           // forces "no value" handling at compile time
}
```

Rust는 값이 없을 수 있다는 사실을 타입에 올려 강하게 강제합니다. 안전성은 높아지지만 배워야 할 문법과 개념도 늘어납니다. Python의 `None`은 더 가볍지만 덜 엄격합니다.

### 5단계 — 시리즈 전체를 한 표로 묶기

| 주제 | Python | Go | Rust |
| --- | --- | --- | --- |
| 메모리 관리 | GC + refcount | GC | compile-time ownership |
| 실행 모델 | interpreter + bytecode | AOT | AOT |
| 타입 | gradual (optional) | static (simple) | static, rich |
| 객체 모델 | classes, dynamic | structs + interfaces | structs + traits |
| 함수 | first-class, closures | first-class, simple | first-class, explicit lifetimes |

각 언어의 답이 어떤 축에 더 무게를 두는지 한눈에 보입니다. 시리즈에서 본 모든 주제가 사실은 설계 우선순위의 결과라는 말입니다.

### 6단계 — 같은 팀이라도 상황이 바뀌면 답이 달라진다

| 상황 | 더 무게를 둘 축 | 자주 떠오르는 선택 |
| --- | --- | --- |
| 일주일 안에 실험해야 하는 프로토타입 | 단순성, 표현력 | Python |
| 배포 단순성과 짧은 빌드 시간을 중시하는 서비스 | 일관성, 운영 단순성, 성능 | Go |
| 메모리 제어와 강한 안전성이 중요한 시스템 경계 | 안전성, 성능 | Rust |

이 표의 핵심은 특정 언어를 추천하는 데 있지 않습니다. 같은 팀도 프로젝트 단계가 달라지면 우선순위가 바뀌고, 그 순간 “좋은 언어”의 정의도 함께 바뀝니다. 설계 평가는 언제나 맥락을 먼저 적어 두는 쪽이 정확합니다.

## 이 코드에서 먼저 볼 점

- 세 언어의 답은 맞고 틀림의 문제가 아니라 우선순위의 차이입니다.
- 일관성이 높은 언어는 “방금 배운 패턴이 여기서도 통한다”는 느낌을 줍니다.
- 표현력이 높을수록 짧아지지만, 처음 보는 사람에게는 더 읽기 어려울 수 있습니다.
- 안전성이 높을수록 컴파일러와 더 많이 대화하게 되지만, 운영 사고는 줄어드는 편입니다.

## 자주 하는 실수

1. “최고의 언어”를 찾으려 합니다. 좋은 언어는 항상 어떤 작업을 기준으로만 정의됩니다.
2. 표현력이 높을수록 무조건 좋다고 생각합니다. 너무 짧으면 읽기 어려워집니다.
3. 안전성을 언제나 최우선에 둡니다. 일주일짜리 프로토타입에는 과할 수 있습니다.
4. 일관성을 과소평가합니다. 같은 문제를 매번 다른 방식으로 풀게 하면 코드베이스가 빨리 피로해집니다.
5. 좋아하는 언어를 객관적 진실처럼 여깁니다. 설계 축으로 적어 보면 편향이 드러납니다.

## 실무에서는 이렇게 본다

새 프로젝트에서 언어를 고르는 일은 인기투표가 아니라 다섯 축의 가중치를 정하는 일입니다. 짧고 빠른 검증이 중요하면 Python이, 운영 단순성이 중요하면 Go가, 메모리 제어와 안전성이 중요하면 Rust가 자연스럽게 올라옵니다. 언어 선택의 이유를 이렇게 적어 두면 팀 합의도 빨라집니다.

같은 원리는 내부 라이브러리와 API 설계에도 적용됩니다. “이 함수는 표현력을 우선하는가, 안전성을 우선하는가”를 먼저 적어 두면 리뷰가 훨씬 명료해집니다. 언어 설계 감각은 결국 팀의 API 감각으로 이어집니다.

## 체크리스트

- [ ] 다섯 축을 각각 한 줄로 정의할 수 있는가?
- [ ] 가장 자주 쓰는 언어의 트레이드오프를 한 단락으로 적을 수 있는가?
- [ ] 최근 만든 API가 어느 축을 우선했는지 설명할 수 있는가?
- [ ] 맥락 없이 “좋은 언어”라고 단정하지 않는가?
- [ ] 새 언어를 만날 때 다섯 축을 의식적으로 훑는가?

## 연습 문제

1. 가장 자주 쓰는 두 언어를 다섯 축으로 비교해 보고, 차이를 한 단락으로 정리해 보세요.
2. 최근 만든 공개 API 하나를 골라 더 표현력 높은 버전과 더 안전한 버전을 각각 스케치해 보세요.
3. 이 시리즈에서 가장 인상 깊었던 주제를 하나 골라, 그것이 다섯 축 중 어디와 가장 강하게 연결되는지 적어 보세요.

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

## 실전 시나리오: 장애를 줄이는 언어 설계 점검

현업에서 언어 개념을 배울 때 가장 빠른 방법은 장애 시나리오를 기준으로 역추적하는 것입니다. 아래는 주문 이벤트 처리 파이프라인을 가정한 점검 예시입니다. 핵심은 기능 구현보다 경계 확인입니다.

```text
입력(JSON) -> 역직렬화 -> 타입 검증 -> 규칙 실행 -> 상태 반영 -> 로그/메트릭
```

각 단계에서 질문을 고정하면 품질이 크게 올라갑니다. 역직렬화 단계에서는 필수 필드 누락을 즉시 중단하는가, 타입 검증 단계에서는 문자열/숫자 혼합을 허용하지 않는가, 규칙 실행 단계에서는 부수효과를 최소화했는가, 상태 반영 단계에서는 재시도 시 멱등성이 보장되는가를 확인해야 합니다.

### 미니 구현: 입력 검증과 멱등 키

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderEvent:
    event_id: str
    amount: int

def parse_event(raw: dict) -> OrderEvent:
    if "event_id" not in raw or "amount" not in raw:
        raise ValueError("missing required field")
    event_id = str(raw["event_id"]).strip()
    amount = int(raw["amount"])
    if amount < 0:
        raise ValueError("amount must be >= 0")
    return OrderEvent(event_id=event_id, amount=amount)
```

이 예시는 단순하지만 기준이 분명합니다. 입력을 받는 즉시 도메인 객체로 변환해 이후 단계의 가정을 안정화하고, `event_id`를 멱등 키로 사용해 중복 처리를 통제할 수 있습니다. 언어 기능 자체보다도, 타입 경계를 어디에서 확정하는지가 운영 안정성을 좌우합니다.

### REPL 확인

```text
$ python3
>>> from order_demo import parse_event
>>> parse_event({"event_id": "ev-1", "amount": "120"})
OrderEvent(event_id='ev-1', amount=120)
>>> parse_event({"event_id": "ev-2", "amount": -1})
Traceback (most recent call last):
  ...
ValueError: amount must be >= 0
```

짧은 REPL 검증을 반복하면 설계 문서의 문장이 실제 런타임에서 유지되는지 빠르게 확인할 수 있습니다. 이 습관이 쌓이면 언어를 바꿔도 문제 분석 속도와 리뷰 품질이 함께 유지됩니다.

## 정리

좋은 언어 설계는 다섯 축을 어떻게 가중했는지 솔직하게 드러내는 설계입니다. 구문, 타입, 스코프, 클로저, 객체, 메모리, 실행 모델, 정적과 동적의 차이는 모두 그 가중치의 결과였습니다. 이 시리즈는 여기서 끝나지만, 다음 단계는 이 감각을 여러분 자신의 코드와 API 설계에 가져가는 일입니다.

이 시리즈는 여기서 마무리합니다. 다음 읽을거리로는 [compilers-101](../../compilers-101/), [api-design-101](../../api-design-101/), [software-design-101](../../software-design-101/) 시리즈를 추천합니다.

## 처음 질문으로 돌아가기

- **언어 설계를 볼 때 어떤 축으로 평가해야 할까요?**
  - 본문의 기준은 좋은 언어 설계란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **일관성, 단순성, 표현력, 안전성, 성능은 왜 서로 충돌할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python, Go, Rust는 같은 문제에 왜 다른 답을 내릴까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- [Programming Languages 101 (8/10): 인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- [Programming Languages 101 (9/10): 정적 언어와 동적 언어](./09-static-vs-dynamic.md)
- **좋은 언어 설계란 무엇인가? (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Rob Pike — Less is exponentially more (Go)](https://commandcenter.blogspot.com/2012/06/less-is-exponentially-more.html)
- [The Zen of Python (PEP 20)](https://peps.python.org/pep-0020/)
- [The Go FAQ — language design](https://go.dev/doc/faq)
- [The Rust Programming Language — Foreword](https://doc.rust-lang.org/book/foreword.html)
- [Programming Language Pragmatics (Scott)](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, LanguageDesign, Consistency, Simplicity, Expressiveness
