---
series: programming-languages-101
episode: 6
title: "Programming Languages 101 (6/10): 객체와 프로토타입"
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
  - Objects
  - Prototype
  - Class
  - Inheritance
seo_description: 상태와 동작을 묶는 객체지향의 본질을 정의하고, 클래스와 프로토타입 기반 모델의 메서드 탐색 차이를 위임과 MRO 관점에서 비교 설명합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (6/10): 객체와 프로토타입

Java의 클래스도 객체지향이고, JavaScript의 프로토타입도 객체지향이라고 합니다. 그런데 둘의 표면은 꽤 다릅니다. 무엇이 같고 무엇이 다를까요.

이 글은 Programming Languages 101 시리즈의 여섯 번째 글입니다.

이 글에서는 객체를 상태와 동작을 묶는 단위로 먼저 정의한 뒤, 그 묶음을 만드는 두 가지 대표 방식인 클래스 기반 모델과 프로토타입 기반 모델을 비교하겠습니다. 핵심 차이는 결국 메서드를 어디서 어떻게 찾느냐에 있습니다.

## 먼저 던지는 질문

- 객체를 가장 간단히 정의하면 무엇일까요?
- 클래스 기반 모델과 프로토타입 기반 모델은 메서드 탐색이 어떻게 다를까요?
- Python에서 클래스 자체가 객체라는 말은 무슨 뜻일까요?

## 큰 그림

![Programming Languages 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/06/06-01-concept-at-a-glance.ko.png)

*Programming Languages 101 6장 흐름 개요*

## 왜 중요한가

객체 모델을 정확히 이해하면 “왜 이 메서드가 호출되지?”, “왜 `super`가 이렇게 동작하지?” 같은 질문이 하나의 설명으로 정리됩니다. 새로운 객체지향 언어를 만나도 표면 문법보다 탐색 규칙을 먼저 보면 훨씬 빠르게 적응할 수 있습니다.

## 핵심 개념 한눈에 보기

위쪽은 클래스 기반 탐색, 아래쪽은 프로토타입 체인입니다. 공통 구조는 단순합니다. 현재 객체에 없으면 한 단계 위로 위임합니다. 객체 모델의 핵심은 이 위임 규칙을 어디에 두느냐입니다.

## 먼저 알아둘 용어

- 인스턴스: 어떤 시점의 실제 상태를 담는 구체 객체입니다.
- 클래스: 인스턴스의 형태와 동작을 정의하는 청사진입니다.
- 프로토타입: 다른 객체가 위임할 수 있는 기준 객체입니다.
- 메서드 해석 순서: 메서드를 찾을 때 어떤 경로를 따라 올라갈지 정한 규칙입니다.
- 위임: 현재 객체에 값이 없을 때 다른 객체에 조회를 넘기는 일입니다.

## 먼저 보는 예시

### 데이터와 함수가 분리돼 있을 때

```python
def make_user(name, age):
    return {"name": name, "age": age}

def greet(user):
    return f"hi, {user['name']}"

u = make_user("kim", 30)
print(greet(u))
```

호출자는 데이터와 함수를 함께 들고 다녀야 합니다. 구조가 단순할 때는 괜찮지만, 책임이 늘수록 관리가 어려워집니다.

### 클래스에 묶었을 때

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name, self.age = name, age
    def greet(self) -> str:
        return f"hi, {self.name}"

print(User("kim", 30).greet())
```

상태와 동작이 한 단위로 묶였기 때문에 호출자는 하나의 객체만 다루면 됩니다. 객체지향의 가장 실질적인 장점이 여기에 있습니다.

## 두 모델을 단계적으로 따라가기

### 1단계 — 클래스 기반 탐색

```python
# 1_class.py
class A:
    def hi(self): return "A.hi"

class B(A):
    pass

print(B().hi())          # 'A.hi' — not on B, delegated upward
print(B.__mro__)          # the lookup order
```

`B`에 `hi`가 없으니 상위 클래스로 올라갑니다. `__mro__`는 Python이 실제로 따르는 탐색 경로를 그대로 보여 줍니다.

### 2단계 — 클래스도 객체다

```python
# 2_class_is_object.py
class A: ...
print(type(A))         # <class 'type'>  — a class is an instance of type
A.tag = "v1"            # you can attach attributes to a class object
print(A.tag)
```

Python에서는 클래스도 일급 객체입니다. 그래서 클래스에 속성을 붙이거나, 메타프로그래밍으로 동작을 바꾸는 일이 가능합니다.

### 3단계 — 사전으로 흉내 내는 프로토타입 방식

```python
# 3_prototype.py
base = {"hi": lambda self: "base.hi"}

def lookup(obj, key):
    if key in obj: return obj[key]
    if "__proto__" in obj: return lookup(obj["__proto__"], key)
    raise KeyError(key)

inst = {"__proto__": base}
print(lookup(inst, "hi")(inst))   # 'base.hi'
```

Python에는 실제 프로토타입 체인이 없지만, “없으면 위로 넘긴다”는 감각은 동일합니다. 클래스가 아닌 객체 자체를 기준으로 위임하는 것이 핵심 차이입니다.

### 4단계 — 재정의와 상위 호출

```python
# 4_super.py
class A:
    def hi(self): return "A"
class B(A):
    def hi(self): return "B+" + super().hi()

print(B().hi())  # B+A
```

`super()`는 막연히 “부모”를 가리키는 것이 아니라 MRO에서 다음 항목으로 이동합니다. 다중 상속에서도 이 한 줄이 일관된 탐색 규칙을 유지해 줍니다.

### 5단계 — 클로저로 객체 흉내 내기

```python
# 5_object_as_closure.py
def make_user(name):
    def greet(): return f"hi, {name}"
    return {"greet": greet}

u = make_user("kim")
print(u["greet"]())  # hi, kim
```

상태인 `name`과 동작인 `greet`가 클로저로 묶였습니다. 클래스 키워드가 없어도 객체의 핵심이 성립한다는 말입니다.

## 이 코드에서 먼저 볼 점

- 두 모델 모두 “없으면 위로 위임한다”는 공통 원리를 갖습니다.
- Python 클래스가 객체라는 사실이 메타프로그래밍의 기반입니다.
- `super`는 부모라는 감각보다 MRO의 다음 항목이라는 감각으로 이해하는 편이 정확합니다.
- 클로저와 객체는 상태와 동작을 묶는다는 점에서 서로 닮아 있습니다.

## 자주 하는 실수

1. 상속 트리를 너무 깊게 만듭니다. 많은 경우 위임이나 조합이 더 단순합니다.
2. MRO를 모른 채 다중 상속을 사용합니다. 그러면 `super`가 갑자기 불투명해집니다.
3. 상태는 없고 메서드만 잔뜩 든 클래스를 만듭니다. 이런 경우는 모듈이나 네임스페이스가 더 자연스러울 수 있습니다.
4. 프로토타입을 클래스의 열등한 흉내처럼 봅니다. 개별 객체 단위로 동작을 바꿀 수 있다는 힘을 놓치게 됩니다.
5. 클로저와 객체를 무관한 개념으로 봅니다. 둘의 공통 구조를 알면 설계 선택지가 넓어집니다.

## 실무에서는 이렇게 본다

대부분의 백엔드 코드는 클래스 기반 객체지향 위에 서 있습니다. 도메인 모델은 클래스가 되고, 동작은 메서드가 됩니다. 반면 JavaScript는 `class` 문법을 받아들였어도 엔진 내부에서는 여전히 프로토타입 체인을 사용합니다. 그래서 `Object.create`나 `Object.getPrototypeOf` 같은 API가 살아 있습니다.

설계를 시작할 때는 “이 객체가 실제로 어떤 상태를 들고 있나?”를 먼저 묻는 편이 좋습니다. 답이 빈약하다면 클래스를 만들 이유가 약할 수 있습니다. 기본값은 조합이고, 상속은 정말로 is-a 관계가 강할 때만 쓰는 편이 안정적입니다.

## 체크리스트

- [ ] 클래스 기반과 프로토타입 기반의 차이를 한 줄로 설명할 수 있는가?
- [ ] Python의 `__mro__`를 직접 출력해 본 적이 있는가?
- [ ] `super`가 무엇을 하는지 한 문장으로 설명할 수 있는가?
- [ ] 기본 선택으로 조합을 더 선호하는가?
- [ ] 클로저로 객체를 흉내 내 본 적이 있는가?

## 연습 문제

1. 다중 상속 클래스를 두 개 만들고 `__mro__`를 출력한 뒤, 그 순서가 왜 그렇게 나오는지 적어 보세요.
2. 클로저 기반 객체 예제에 상태를 바꾸는 연산을 추가해 보세요. `nonlocal`이 필요합니다.
3. 최근에 상속을 쓴 클래스 하나를 골라 조합 기반 대안을 설계해 보세요.

## 정리

객체는 상태와 동작을 묶는 단위이고, 클래스와 프로토타입은 그 묶음을 만드는 두 가지 방식입니다. 어느 쪽이든 핵심은 위임입니다. 다음 글에서는 이 객체들이 메모리 안에서 어떻게 살아 있고 사라지는지 보겠습니다.

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

### 추가 사례: 언어 설계 선택이 유지보수 비용에 미치는 영향

실무에서 타입, 스코프, 메모리 모델은 장애 보고서에서 따로 등장하지 않고 함께 엮여 나타납니다. 예를 들어 이벤트 소비자가 `dict[str, Any]`를 그대로 전달하면 타입 경계가 무너지고, 지연 실행 콜백이 외부 가변 상태를 캡처하면 스코프 결함이 생기며, 여러 워커가 같은 캐시 객체를 잠금 없이 접근하면 메모리 가시성 문제가 겹칩니다. 이런 결함은 단위 테스트 한두 개로는 쉽게 드러나지 않습니다.

그래서 언어 기능 선택을 할 때는 "지금 빨리 쓰기 쉬운가"보다 "오류를 조기에 막는가"를 기준으로 삼아야 합니다. 타입 힌트를 강제하고, 클로저 캡처 규칙을 리뷰 체크리스트에 넣고, 공유 상태 대신 메시지 전달을 우선하면 코드가 길어지더라도 운영 리스크가 크게 줄어듭니다. 결과적으로 좋은 설계는 문법의 화려함이 아니라, 팀이 반복 실수 없이 같은 문제를 안정적으로 푸는 능력으로 측정됩니다.


## 실무 앵커: 개념을 코드와 런타임으로 고정하기

이 장에서 다룬 개념을 실무에서 재사용하려면, 문장 설명을 코드와 실행 흔적으로 고정해야 합니다. 아래 예시는 같은 문제를 여러 언어와 실행 맥락으로 비교해 개념 경계를 분명히 만드는 목적입니다.

### 언어 비교 코드: Python, JavaScript, Go, Rust

동일한 입력에서 짝수 값만 두 배로 만들고 합계를 계산하는 예시입니다. 핵심은 문법 차이가 아니라, 오류를 어디서 얼마나 일찍 막는지입니다.

```python
def sum_even_doubled(nums: list[int]) -> int:
    return sum(n * 2 for n in nums if n % 2 == 0)

print(sum_even_doubled([1, 2, 3, 4, 5, 6]))  # 24
```

```javascript
function sumEvenDoubled(nums) {
  return nums.filter((n) => n % 2 === 0).map((n) => n * 2).reduce((a, b) => a + b, 0);
}

console.log(sumEvenDoubled([1, 2, 3, 4, 5, 6])); // 24
```

```go
package main

import "fmt"

func sumEvenDoubled(nums []int) int {
    total := 0
    for _, n := range nums {
        if n%2 == 0 {
            total += n * 2
        }
    }
    return total
}

func main() {
    fmt.Println(sumEvenDoubled([]int{1, 2, 3, 4, 5, 6})) // 24
}
```

```rust
fn sum_even_doubled(nums: &[i32]) -> i32 {
    nums.iter()
        .filter(|n| *n % 2 == 0)
        .map(|n| n * 2)
        .sum()
}

fn main() {
    println!("{}", sum_even_doubled(&[1, 2, 3, 4, 5, 6])); // 24
}
```

네 언어 모두 같은 답을 내지만, 타입 선언 강도, 표준 라이브러리 관용구, 에러 처리 문화가 다릅니다. 팀 기준을 세울 때는 성능 벤치마크보다 먼저, 리뷰 단계에서 실수를 드러내는 신호가 충분한지 확인하는 편이 안전합니다.

### 타입 시스템 앵커: 실패를 어디서 잡는가

아래 상황은 실무에서 자주 발생합니다. 문자열 숫자와 정수 숫자가 섞여 들어올 때, 파이프라인 초입에서 명시적으로 정규화하지 않으면 나중 단계에서 장애가 커집니다.

```python
from typing import Iterable

def normalize(values: Iterable[str]) -> list[int]:
    result: list[int] = []
    for v in values:
        result.append(int(v))
    return result

print(normalize(["1", "2", "3"]))
```

```typescript
function normalize(values: string[]): number[] {
  return values.map((v) => Number.parseInt(v, 10));
}

console.log(normalize(["1", "2", "3"]));
```

정적 타입 언어에서는 함수 경계에서 계약을 강하게 걸 수 있고, 동적 타입 언어에서는 런타임 검증 코드를 명시적으로 두는 습관이 중요합니다. 결론은 어느 쪽이 우월하냐가 아니라, 실패 지점을 팀이 의도적으로 앞당겼는가입니다.

### 메모리 모델 다이어그램: 공유 상태의 책임 경계

```text
[Producer Goroutine/Thread]
  write task -> queue
       |
       | happens-before 보장 지점
       v
[Queue Synchronization Boundary]
       |
       v
[Consumer Goroutine/Thread]
  read task -> process
```

동시성 결함 대부분은 계산 로직보다 경계 정의가 흐릴 때 생깁니다. 어떤 자료구조가 동기화 책임을 가지는지, 어느 호출 지점에서 메모리 가시성이 확보되는지를 코드 리뷰 항목으로 고정해야 재현 어려운 버그를 줄일 수 있습니다.

### 간단 파서 구현 앵커: 구문과 의미를 분리하기

토큰 배열을 받아 산술식 `NUM (+ NUM)*`를 계산하는 최소 파서 예시입니다.

```python
def parse_addition(tokens: list[str]) -> int:
    if not tokens:
        raise ValueError("empty")
    total = int(tokens[0])
    i = 1
    while i < len(tokens):
        op = tokens[i]
        rhs = int(tokens[i + 1])
        if op != "+":
            raise ValueError(f"unexpected operator: {op}")
        total += rhs
        i += 2
    return total

print(parse_addition(["10", "+", "20", "+", "7"]))  # 37
```

이 구조의 핵심은 두 단계 분리입니다. 먼저 구문 오류를 검사하고, 그다음 의미 계산을 수행합니다. 이 원칙을 지키면 오류 메시지가 명확해지고, 연산자 우선순위나 괄호 지원 같은 확장을 추가하기 쉬워집니다.

### REPL 세션 앵커: 실행 관찰 습관

```text
$ python3
>>> from demo import parse_addition
>>> parse_addition(["2", "+", "3"])
5
>>> parse_addition(["2", "*", "3"])
Traceback (most recent call last):
  ...
ValueError: unexpected operator: *
```

REPL은 작은 단위 가설을 빠르게 검증하는 도구입니다. 문서로 정리한 개념과 실제 런타임 동작이 어긋나지 않는지 확인할 때, 테스트 코드 작성 전 첫 관찰 지점으로 활용하면 품질이 안정적으로 올라갑니다.

### 적용 체크리스트

- 입력 경계에서 타입과 형식을 정규화했는가
- 공유 상태보다 메시지 경계가 먼저 보이도록 설계했는가
- 파서/검증/실행 단계를 분리해 오류 원인을 즉시 설명할 수 있는가
- REPL 또는 단위 테스트로 실패 사례를 먼저 고정했는가

이 체크리스트는 특정 언어 문법보다 오래 갑니다. 새 언어를 배우더라도 같은 질문으로 코드를 점검하면, 기능 개발 속도를 유지하면서도 운영 안정성을 함께 끌어올릴 수 있습니다.



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

## 처음 질문으로 돌아가기

- **객체를 가장 간단히 정의하면 무엇일까요?**
  - 본문의 기준은 객체와 프로토타입를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **클래스 기반 모델과 프로토타입 기반 모델은 메서드 탐색이 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python에서 클래스 자체가 객체라는 말은 무슨 뜻일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- **객체와 프로토타입 (현재 글)**
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Python Data Model — object](https://docs.python.org/3/reference/datamodel.html)
- [MDN — Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)
- [Self: The Power of Simplicity (Ungar & Smith)](https://bibliography.selflanguage.org/_static/self-power.pdf)
- [Composition over inheritance (Wikipedia)](https://en.wikipedia.org/wiki/Composition_over_inheritance)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Objects, Prototype, Class, Inheritance
