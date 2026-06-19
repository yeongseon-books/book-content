---
series: programming-languages-101
episode: 3
title: "Programming Languages 101 (3/10): 타입 시스템"
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
  - TypeSystem
  - Static
  - Dynamic
  - Inference
seo_description: 정적/동적 타입과 강한/약한 타입의 차이를 정리하고, 제네릭과 타입 추론이 안전성과 생산성을 어떻게 동시에 보장하는지 코드 예시로 설명합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (3/10): 타입 시스템

동적 언어로도 코드는 잘 돌아갑니다. 그런데 프로젝트가 커질수록 사람들은 다시 타입 힌트를 붙이고, 검사기를 CI에 넣고, 인터페이스를 더 정확히 적기 시작합니다. 왜 이런 수고를 되풀이할까요.

이 글은 Programming Languages 101 시리즈의 3번째 글입니다.

이 글에서는 타입 시스템을 단순한 자료형 표기가 아니라, 프로그램이 말도 안 되는 조합을 실행 전에 걸러 내는 장치로 보겠습니다. 정적 타입과 동적 타입, 강한 타입과 약한 타입, 타입 추론과 제네릭이 각각 무엇을 사고파는지 차분히 정리해 보겠습니다.

![Programming Languages 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/03/03-01-concept-at-a-glance.ko.png)
*Programming Languages 101 3장 흐름 개요*

> 타입 시스템은 런타임 에러를 컴파일 타임으로 끌어오는 '시간 이동 장치'입니다 — 정적/동적, 강/약, nominal/structural 같은 축을 머릿속에 잡아 두면 Python type hint·TypeScript·Rust가 같은 그림의 서로 다른 좌표라는 것이 보입니다.

## 이 글에서 다룰 문제

- 타입은 정확히 어떤 역할을 할까요?
- 정적 타입과 동적 타입은 무엇을 언제 검사할까요?
- 강한 타입과 약한 타입은 왜 다른 축일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

현대 언어 대부분은 어떤 형태로든 타입 시스템을 품고 있습니다. Python도 타입 힌트와 mypy, JavaScript도 TypeScript를 통해 점점 더 정적인 방향을 받아들였습니다. 자동 완성, 안전한 리팩터링, 빌드 단계의 오류 검출을 잘 활용하려면 타입이 무엇을 보장하고 무엇을 보장하지 않는지부터 알아야 합니다.

## 먼저 알아둘 용어

- **정적 타입**: 실행 전에 타입을 검사합니다.
- **동적 타입**: 실행 중에 타입 오류가 드러납니다.
- **강한 타입**: 암묵적 형변환이 드뭅니다.
- **약한 타입**: 암묵적 형변환이 자주 일어납니다.
- **타입 추론**: 명시하지 않아도 컴파일러나 검사기가 타입을 알아냅니다.
- **제네릭**: 여러 타입에 대해 안전하게 재사용되도록 코드를 매개변수화합니다.

## 타입 시스템 분류 다이어그램

타입 시스템은 두 독립된 축으로 분류됩니다.

```text
           강한 타입 (암묵적 형변환 드묾)
                |
    Python -----+------ Haskell, Rust
    (동적,강함)  |      (정적, 강함)
                |
동적 타입 ------+------ 정적 타입
(실행 중 검사)  |      (실행 전 검사)
                |
   JavaScript --+------ C (일부 암묵적 변환)
    (동적,약함)  |
                |
           약한 타입 (암묵적 형변환 허용)
```

Python은 동적이지만 강합니다. `1 + "2"`는 실행 중에 `TypeError`를 냅니다. JavaScript는 동적이면서 약합니다. `1 + "2"`가 `"12"`로 조용히 변환됩니다.

## 먼저 보는 예시

### 타입 정보가 없을 때

```python
def discount(price, rate):
    return price - price * rate

# 누군가 이렇게 호출합니다
discount("1000", 0.1)  # TypeError at runtime
```

함수 시그니처만으로는 호출자가 무엇을 넘겨야 하는지 알기 어렵고, 잘못된 값이 들어와도 실행하기 전까지는 모릅니다.

### 타입을 적어 두었을 때

```python
def discount(price: int, rate: float) -> float:
    return price - price * rate

discount("1000", 0.1)  # mypy rejects this at the call site
```

이제 `mypy` 같은 정적 검사기가 호출 지점에서 문제를 잡아 줍니다. 시그니처 자체도 작은 문서 역할을 합니다.

## 타입을 단계적으로 붙여 보기

### 1단계 — 타입 힌트 추가하기

```python
# 1_hints.py
def to_kebab(s: str) -> str:
    return s.strip().lower().replace(" ", "-")

print(to_kebab("Hello World"))
```

동작은 같지만 호출 계약이 생겼습니다. 이 작은 차이가 코드베이스가 커질수록 크게 쌓입니다.

### 2단계 — 정적 검사기로 확인하기

```bash
pip install mypy
mypy 1_hints.py    # Success: no issues
```

이 단계에서 생기는 습관이 중요합니다. 실행하기 전에 검사하는 루프가 하나 더 들어옵니다.

### 3단계 — 제네릭 함수 만들기

```python
# 3_generic.py
from typing import TypeVar, Iterable

T = TypeVar("T")

def first(xs: Iterable[T]) -> T:
    for x in xs:
        return x
    raise ValueError("empty")

reveal_type(first([1, 2, 3]))   # Revealed type is "int"
reveal_type(first(["a", "b"]))  # Revealed type is "str"
```

한 함수가 여러 타입을 받아도 반환 타입을 정확히 보존합니다. 재사용성과 정확성을 함께 챙기는 방식입니다.

### 4단계 — 유니온 타입과 좁히기

```python
# 4_union.py
def length(x: str | list) -> int:
    if isinstance(x, str):
        return len(x)
    return sum(len(item) for item in x)
```

`isinstance`를 통과한 뒤 검사기는 각 분기에서 타입을 더 좁게 이해합니다. 동적 언어의 직관을 정적 검사로 끌고 오는 대표적인 패턴입니다.

### 5단계 — 타입이 진짜 버그를 드러내는 순간

```python
# 5_real_bug.py
def total_price(items: list[dict]) -> int:
    return sum(item["price"] for item in items)  # mypy points out the dict value type is unclear
```

정확한 타입을 적으려다 보면 데이터 모델의 애매함이 먼저 드러납니다. 실제 버그는 대개 그 애매한 경계에 숨어 있습니다.

### 6단계 — 경계에서는 입력을 검증하고, 안쪽에서는 구체 타입으로 좁히기

```python
# 6_boundary.py
from typing import TypedDict

class LineItem(TypedDict):
    price: int
    quantity: int

def parse_line_item(raw: dict[str, object]) -> LineItem:
    price = raw.get("price")
    quantity = raw.get("quantity")
    if not isinstance(price, int) or not isinstance(quantity, int):
        raise ValueError("price and quantity must be integers")
    return {"price": price, "quantity": quantity}

def subtotal(item: LineItem) -> int:
    return item["price"] * item["quantity"]

payload = {"price": 1200, "quantity": 3}
item = parse_line_item(payload)
print(subtotal(item))  # 3600
```

정적 타입이 강해지는 지점은 보통 함수 경계 안쪽입니다. 외부 JSON이나 폼 입력처럼 동적으로 들어오는 값은 먼저 런타임 검증으로 좁히고, 그 결과를 `TypedDict`나 dataclass로 넘겨야 타입 검사기의 이점이 제대로 살아납니다.

## 언어별 타입 시스템 비교

같은 동작을 Python, TypeScript, Go, Rust에서 각각 어떻게 표현하는지 보면 각 언어가 선택한 타입 전략이 보입니다.

```python
# Python (점진적 타입, 선택적 정적 검사)
def add(a: int, b: int) -> int:
    return a + b

# 힌트 없이도 동작하지만 검사기가 도움을 못 줌
def add_untyped(a, b):
    return a + b
```

```typescript
// TypeScript (정적 타입, 구조적 서브타이핑)
function add(a: number, b: number): number {
    return a + b;
}

// 인터페이스 없이도 구조가 맞으면 통과
interface HasLength { length: number; }
function printLength(obj: HasLength): void {
    console.log(obj.length);
}
printLength("hello");   // OK — string has .length
printLength([1, 2, 3]); // OK — array has .length
```

```go
// Go (정적 타입, 인터페이스 암묵적 구현)
func add(a, b int) int {
    return a + b
}

// 인터페이스: 구조가 맞으면 자동으로 구현체로 인정
type Stringer interface {
    String() string
}
```

```rust
// Rust (정적 타입, 트레이트 기반, 소유권 포함)
fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 제네릭 + 트레이트 바운드
fn print_display<T: std::fmt::Display>(val: T) {
    println!("{}", val);
}
```

Python은 타입 없이도 동작하지만 검사기 지원이 줄어들고, TypeScript는 구조적 서브타이핑으로 유연하게, Go는 인터페이스 암묵적 구현으로 간결하게, Rust는 트레이트로 가장 엄격하게 타입을 다룹니다.

## 이 코드에서 먼저 볼 점

- 타입은 검사 규칙이면서 문서이면서 도구 입력입니다.
- 정적 검사는 모든 버그를 잡지 못하지만, 값싸고 흔한 오류를 아주 일찍 잡아 줍니다.
- 제네릭은 "한 번 작성해 여러 타입에 안전하게 쓰기"를 가능하게 합니다.
- 유니온 타입과 좁히기는 동적 언어 감각과 정적 검사 사이를 자연스럽게 이어 줍니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| `Any`를 너무 쉽게 사용 | 검사기가 조용해지는 대신 안전성도 함께 사라짐 | 한 단계라도 구체 타입으로 좁히는 전략 |
| 모든 곳에 한꺼번에 타입 도입 | 대규모 리팩터링 작업이 되어버려 완성 못 함 | 공개 함수와 모듈 경계부터 점진적으로 적용 |
| 타입과 실행 시 검증을 동일시 | 외부 입력 오류를 타입으로 막으려 함 | 경계에서 런타임 검증, 내부에서 타입 검사 분리 |
| 지나치게 정교한 타입 추구 | 타입 코드가 비즈니스 코드보다 복잡해짐 | 90%를 깔끔하게 막는 단순한 타입이 더 실용적 |
| 정적 vs 동적을 신념 싸움으로 봄 | 팀 논의가 불필요하게 감정적이 됨 | 팀 규모와 변경 빈도에 따른 실용적 선택 |

## 실무에서는 이렇게 본다

큰 Python 코드베이스는 대개 공개 함수에 타입을 붙이고, CI에서 mypy나 pyright를 돌립니다. JavaScript 생태계에서 TypeScript가 사실상 기본이 된 이유도 같은 맥락입니다. 타입은 라이브러리 사용자에게 가장 먼저 보이는 문서이자, 자동 완성과 리팩터링의 기반입니다.

타입은 리팩터링 안전망으로도 강합니다. 함수 인자 순서를 바꿨을 때 호출 지점이 한꺼번에 드러나면 변경을 훨씬 자신 있게 진행할 수 있습니다. 결국 타입 시스템의 실익은 이론보다 운영과 유지보수에서 더 크게 체감됩니다.

### 도메인 타입을 좁혀 설계하기

금액을 단순히 `int`로 표현하면 통화, 반올림 정책, 최소/최대값이 코드에 드러나지 않습니다.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Money:
    amount: int          # 원 단위 정수
    currency: Literal["KRW", "USD"]

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"amount must be >= 0, got {self.amount}")

def apply_discount(price: Money, rate: float) -> Money:
    if rate < 0 or rate > 1:
        raise ValueError("rate must be between 0 and 1")
    discounted = int(price.amount * (1 - rate))
    return Money(amount=discounted, currency=price.currency)

# 사용
price = Money(amount=10000, currency="KRW")
final = apply_discount(price, 0.1)
print(final)  # Money(amount=9000, currency='KRW')
```

`Money` 타입을 쓰면 통화 단위를 잊거나 다른 통화끼리 더하는 실수를 타입 수준에서 막을 수 있습니다.

## TypeScript의 구조적 타입 시스템

Go와 TypeScript는 명목적(nominal) 타입 시스템이 아닌 구조적(structural) 타입 시스템을 사용합니다. 타입 이름이 아니라 구조(shape)가 호환성을 결정합니다.

```typescript
// TypeScript: 구조적 타입 — 이름이 아닌 구조가 기준
interface Printable {
    name: string;
    print(): void;
}

// Dog 클래스는 Printable을 명시적으로 구현하지 않았지만
class Dog {
    constructor(public name: string) {}
    print(): void { console.log(`Dog: ${this.name}`); }
}

// 구조가 맞으면 할당 가능
const p: Printable = new Dog("Rex");  // 컴파일 통과
p.print();  // "Dog: Rex"

// 인터페이스 없이도 인라인 구조 타입 사용 가능
function greet(obj: { name: string }): string {
    return `Hello, ${obj.name}`;
}

console.log(greet({ name: "Alice" }));   // "Hello, Alice"
console.log(greet(new Dog("Rex")));      // "Hello, Rex" — Dog도 name이 있으므로 통과
```

```python
# Python: Protocol로 구조적 타이핑
from typing import Protocol, runtime_checkable

@runtime_checkable
class Printable(Protocol):
    name: str
    def print(self) -> None: ...

class Dog:
    def __init__(self, name: str) -> None:
        self.name = name
    def print(self) -> None:
        print(f"Dog: {self.name}")

def greet(obj: Printable) -> str:
    return f"Hello, {obj.name}"

dog = Dog("Rex")
print(greet(dog))          # "Hello, Rex"
print(isinstance(dog, Printable))  # True (runtime_checkable 덕분)
```

구조적 타이핑은 "이름표를 확인하는 것이 아니라 실제로 할 수 있는 것을 확인한다"는 철학입니다. 덕 타이핑의 정적 버전이라고 볼 수 있습니다.

## 타입 추론: 덜 적고도 더 안전하게

현대 정적 타입 언어 대부분은 타입 추론을 제공합니다. 개발자가 모든 곳에 타입을 적지 않아도 컴파일러가 문맥으로 타입을 알아냅니다.

```rust
// Rust: 광범위한 타입 추론
fn main() {
    let x = 5;               // i32로 추론
    let y = 2.0;             // f64로 추론
    let v = vec![1, 2, 3];   // Vec<i32>로 추론

    let doubled: Vec<_> = v.iter().map(|n| n * 2).collect();
    // collect()의 타입은 doubled의 타입 선언에서 역방향으로 추론됨

    println!("{:?}", doubled);  // [2, 4, 6]
}
```

```python
# Python + mypy: 제한적이지만 일부 추론 가능
def double_items(items: list[int]) -> list[int]:
    return [x * 2 for x in items]

nums = [1, 2, 3]
result = double_items(nums)
# mypy는 result가 list[int]임을 알고 있음
```

타입 추론은 타입 안전성과 간결한 코드를 동시에 얻는 핵심 도구입니다. Rust처럼 강한 추론 엔진을 가진 언어에서는 함수 시그니처에만 타입을 적고 함수 본문의 대부분은 컴파일러에게 맡깁니다.

## 운영 체크리스트

- [ ] 정적 타입과 동적 타입, 강한 타입과 약한 타입을 각각 구분할 수 있는가?
- [ ] 점진적으로 타입을 도입할 때 어디부터 시작해야 하는지 아는가?
- [ ] `Any`를 만났을 때 한 단계라도 좁히는 전략이 있는가?
- [ ] 타입과 실행 시 검증의 차이를 설명할 수 있는가?
- [ ] 제네릭이 단순 복사보다 왜 강한지 설명할 수 있는가?

## 연습 문제

1. `total_price` 예제에 `TypedDict`를 도입해 `item` 구조를 정확히 적어 보세요.
2. 자주 쓰는 동적 언어 함수 하나를 골라 입력 타입과 출력 타입을 글로 적어 보세요.
3. 타입을 붙인 뒤에야 드러난 실제 버그 사례를 떠올리고, 왜 더 일찍 발견되지 않았는지 설명해 보세요.

## 정리

타입 시스템은 안전성, 문서성, 도구 지원을 한 번에 제공합니다. 모든 언어가 같은 정도의 타입 강도를 필요로 하지는 않지만, 경계가 많은 큰 시스템일수록 그 이점이 커집니다. 다음 글에서는 또 다른 기본 축인 스코프와 바인딩으로 넘어가겠습니다.

## 처음 질문으로 돌아가기

- **타입은 정확히 어떤 역할을 할까요?**
  - 타입은 세 가지 역할을 합니다. 값의 잘못된 조합을 실행 전에 막는 검사 규칙, 함수가 무엇을 받고 무엇을 돌려주는지 보여 주는 문서, 그리고 IDE 자동 완성과 리팩터링 도구의 입력입니다.
- **정적 타입과 동적 타입은 무엇을 언제 검사할까요?**
  - 정적 타입은 실행 전 컴파일/분석 단계에서 타입 불일치를 잡습니다. 동적 타입은 실행 흐름이 해당 지점에 도달했을 때 비로소 오류가 드러납니다.
- **강한 타입과 약한 타입은 왜 다른 축일까요?**
  - 정적/동적은 "언제 검사하는가"의 문제이고, 강한/약한은 "암묵적 형변환을 얼마나 허용하는가"의 문제입니다. Python은 동적이지만 강하고, JavaScript는 동적이면서 약합니다. 두 축은 독립적으로 선택됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- **Programming Languages 101 (3/10): 타입 시스템 (현재 글)**
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- [Programming Languages 101 (8/10): 인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- [Programming Languages 101 (9/10): 정적 언어와 동적 언어](./09-static-vs-dynamic.md)
- [Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?](./10-what-makes-good-language-design.md)

<!-- toc:end -->

## 참고 자료

- [Types and Programming Languages (Pierce)](https://www.cis.upenn.edu/~bcpierce/tapl/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, TypeSystem, Static, Dynamic, Inference
