---
episode: 9
language: ko
last_reviewed: '2026-05-15'
seo_description: 정적 언어와 동적 언어가 타입 검사 시점을 달리하는 방식과 안정성, 표현력의 트레이드오프를 비교 분석합니다.
series: programming-languages-101
status: publish-ready
tags:
- Computer Science
- Programming Languages
- StaticTyping
- DynamicTyping
- Tradeoffs
- Safety
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Programming Languages 101 (9/10): 정적 언어와 동적 언어"
---

# Programming Languages 101 (9/10): 정적 언어와 동적 언어

정적 타입이 더 안전하다는 말은 자주 듣지만, 그 안전이 정확히 무엇을 덮는지 묻는 순간 답이 흐려지는 경우가 많습니다. 반대로 동적 언어가 더 빠르다는 말도 자주 나오지만, 실제로는 어떤 종류의 속도를 말하는지 구분이 필요합니다.

이 글은 Programming Languages 101 시리즈의 9번째 글입니다.

이 글에서는 정적 언어와 동적 언어를 우열의 문제가 아니라 검사 시점의 선택으로 보겠습니다. 같은 함수를 타입 힌트 없이 쓴 버전과 명시적으로 쓴 버전을 나란히 놓고, 어떤 종류의 오류를 언제 잡을 수 있는지 현실적으로 정리하겠습니다.

![Programming Languages 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/09/09-01-concept-at-a-glance.ko.png)
*Programming Languages 101 9장 흐름 개요*

> '정적 vs 동적'은 한 축이 아니라 '타입 / 바인딩 / 디스패치' 세 축에서 각각 다르게 갈라집니다 — Python은 동적 타입이지만 정적 바인딩이고, JS는 동적 타입·동적 바인딩이며, Java는 그 반대편입니다. 이 축들이 분리되어야 언어 비교가 흙탕물에서 빠져나옵니다.

## 이 글에서 다룰 문제

- 정적과 동적의 가장 짧은 정의는 무엇일까요?
- 같은 코드가 두 모델에서 어떻게 다르게 검증될까요?
- mypy나 pyright가 잡을 수 있는 것과 없는 것은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

팀이 커질수록 "타입을 더 붙일까?"라는 논의가 반복됩니다. 이때 필요한 것은 신념이 아니라, 정적 검사가 무엇을 보장하고 무엇을 보장하지 않는지 한 문장으로 설명할 수 있는 감각입니다.

## 먼저 알아둘 용어

- **정적 타입**: 변수와 표현식의 타입을 실행 전에 검사합니다.
- **동적 타입**: 값에 타입이 붙고, 검사는 실행 중에 이뤄집니다.
- **강한 타입과 약한 타입**: 암묵적 형변환 허용 범위를 나타내는 별도 축입니다.
- **점진적 타입**: 한 코드베이스 안에 정적 영역과 동적 영역을 함께 두는 방식입니다.
- **건전성**: 검사기가 통과시킨 코드가 타입 규칙을 어기지 않는다는 보장입니다.

## 정적과 동적의 오류 발견 시점

같은 유형의 오류라도 어느 시점에 드러나는지가 다릅니다.

```text
소스 코드 작성
    |
    v
정적 검사 (mypy, pyright, tsc)  ← 정적 타입이 막는 오류
    |
    v
컴파일 / 바이트코드 생성
    |
    v
실행 시작
    |
    v
해당 코드 경로 도달                ← 동적 타입이 드러내는 오류
    |
    v
결과
```

정적 타입은 실행 전에 막고, 동적 타입은 실행 흐름이 그 지점에 도달했을 때 드러납니다.

## 먼저 보는 예시

### 타입 힌트가 없는 함수

```python
def total(items):
    return sum(item.price for item in items)
```

호출자는 각 `item`이 `price`를 가진다고 스스로 가정해야 합니다. 잘못된 입력은 실행 중 `AttributeError`로 터집니다.

### 계약을 드러낸 함수

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    price: int

def total(items: list[Item]) -> int:
    return sum(item.price for item in items)
```

이제 호출자도 함께 검사 대상이 됩니다. 잘못된 입력을 더 앞 단계에서 막을 수 있습니다.

## 같은 코드를 두 모델로 비교하기

### 1단계 — 정적 검사기가 잡는 오류

```python
# 1_mypy.py
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2))
print(add("1", "2"))   # mypy: error — incompatible argument
```

실행하지 않아도 두 번째 호출이 문제라는 사실을 알 수 있습니다. 정적 검사의 가장 직접적인 가치입니다.

### 2단계 — 여전히 실행 중에만 드러나는 오류

```python
# 2_runtime_only.py
import json

data = json.loads('{"price": "10"}')   # mypy sees dict[str, Any]
def total(items):
    return sum(i["price"] for i in items)
print(total([data]))                    # runtime TypeError
```

JSON, 데이터베이스, 환경 변수처럼 외부에서 들어오는 값은 컴파일 시점에 형태가 완전히 고정되지 않습니다. 정적 검사의 보장은 보통 코드 경계 안쪽까지입니다.

### 3단계 — 점진적 타입의 현실적인 쓰임

```python
# 3_gradual.py
def parse(raw: str) -> dict:        # only partly typed
    return eval(raw)                # dynamic region (and risky)

def use(d: dict[str, int]) -> int:  # precisely typed
    return sum(d.values())

print(use(parse('{"a": 1, "b": 2}')))
```

가장자리에서는 동적으로 받고, 안쪽 로직에서는 정적으로 다루는 식의 타협이 가능합니다. Python과 TypeScript가 널리 쓰이는 이유 중 하나가 여기에 있습니다.

### 4단계 — 구조가 같으면 통과시키기

```python
# 4_protocol.py
from typing import Protocol

class Pricable(Protocol):
    price: int

def total(items: list[Pricable]) -> int:
    return sum(i.price for i in items)

class Book:
    def __init__(self, price: int) -> None:
        self.price = price

print(total([Book(10), Book(20)]))   # OK — Book has the right shape
```

상속 관계가 없어도 필요한 형태만 맞으면 통과시킬 수 있습니다. 정적 검사 안에서도 덕 타이핑과 비슷한 감각을 살릴 수 있다는 말입니다.

### 5단계 — 동적 언어가 강한 지점

```python
# 5_dynamic_strength.py
def call_all(d: dict, *args):
    for name, fn in d.items():
        print(name, fn(*args))

ops = {
    "add": lambda x, y: x + y,
    "mul": lambda x, y: x * y,
}
call_all(ops, 3, 4)
```

플러그인이나 메타프로그래밍 같은 영역에서는 동적 언어의 표현력이 여전히 매력적입니다. 정적 언어로도 할 수 있지만 보일러플레이트가 늘어나는 경우가 많습니다.

### 6단계 — 경계 검증과 정적 검사를 함께 쓰기

```python
# 6_boundary_validation.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    price: int

def parse_item(raw: dict[str, object]) -> Item:
    price = raw.get("price")
    if not isinstance(price, int):
        raise ValueError("price must be int")
    return Item(price=price)

payload = {"price": 10}
item = parse_item(payload)
print(item.price + 5)  # 15
```

실무에서는 이 조합이 가장 자주 쓰입니다. 경계에서는 런타임 검증으로 데이터를 좁히고, 그다음부터는 정적 타입으로 도구 지원과 리팩터링 안전망을 얻습니다. 정적과 동적은 보통 경쟁자가 아니라 연속된 두 단계입니다.

## 언어별 타입 검사 시점 비교

같은 오류를 각 언어가 언제 잡는지 비교해 보겠습니다.

```python
# Python (동적 타입, 점진적 정적 검사)
def add(a, b):
    return a + b

add(1, "hello")   # 실행해야 TypeError 발생
                  # mypy 없으면 미리 알 수 없음
```

```typescript
// TypeScript (정적 타입, 컴파일 시 검사)
function add(a: number, b: number): number {
    return a + b;
}

add(1, "hello");   // 컴파일 오류: 실행 전에 잡힘
// Argument of type 'string' is not assignable to parameter of type 'number'
```

```go
// Go (정적 타입, 컴파일 시 검사)
func add(a, b int) int {
    return a + b
}

// add(1, "hello") — 컴파일 오류
// cannot use "hello" (untyped string constant) as int value
```

```rust
// Rust (정적 타입, 컴파일 시 검사 + 소유권 검사)
fn add(a: i32, b: i32) -> i32 {
    a + b
}

// add(1, "hello") — 컴파일 오류
// mismatched types: expected `i32`, found `&str`
```

TypeScript, Go, Rust는 실행 전에 타입 오류를 잡습니다. Python은 mypy/pyright를 CI에 포함하지 않으면 실행 시에야 드러납니다.

## 이 코드에서 먼저 볼 점

- 정적 타입의 보장은 외부 입력이 들어오는 경계에서 끝나는 경우가 많습니다.
- 점진적 타입은 두 모델을 실용적으로 섞는 방식입니다.
- `Protocol`은 상속 없이도 "같은 모양"을 표현하게 해 줍니다.
- 짧은 스크립트나 메타프로그래밍처럼 동적 모델이 더 자연스러운 영역도 분명히 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 정적은 안전, 동적은 위험으로 단순화 | 팀 논의가 이분법적으로 흐름 | 두 모델은 다른 비용을 냄, 컨텍스트에 따른 선택 |
| 타입 힌트만으로 외부 입력 문제 해결 기대 | JSON 경계 이후에도 타입 오류 발생 | 경계에서 런타임 검증 + 내부에서 타입 검사 분리 |
| `Any` 과다 사용 | 점진적 타입이 사실상 동적 타입과 동일해짐 | `Any` 사용처를 주기적으로 감사하고 좁혀 나가기 |
| 타입 힌트만 달고 검사기를 CI에 미포함 | 타입이 문서 역할만 하고 오류를 못 잡음 | mypy 또는 pyright를 CI 필수 단계로 추가 |
| 타입과 테스트를 대체재로 봄 | 타입 검사를 추가했는데 테스트를 줄임 | 타입은 구조적 오류, 테스트는 동작 오류를 잡음 |

## 실무에서는 이렇게 본다

큰 Python 코드베이스는 이제 거의 예외 없이 mypy나 pyright를 CI에서 돌립니다. JavaScript 진영도 TypeScript를 사실상 표준처럼 받아들였습니다. 이때 성능보다 더 큰 이점은 유지보수입니다. 코드 경계가 많아질수록 타입 정보가 문서와 자동 완성과 리팩터링 안전망 역할을 같이 해 주기 때문입니다.

요즘 많이 쓰는 패턴은 경계에서 강하게 검증하고, 내부에서는 정밀하게 타입을 다루는 방식입니다. `pydantic`, `dataclass`, `Protocol`이 자주 함께 등장하는 이유도 이 조합이 실무에서 잘 맞기 때문입니다.

### pydantic으로 경계 검증과 타입 통합하기

```python
from pydantic import BaseModel, field_validator

class OrderRequest(BaseModel):
    order_id: str
    amount: int
    currency: str

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v: str) -> str:
        if v not in {"KRW", "USD", "EUR"}:
            raise ValueError(f"unsupported currency: {v}")
        return v

# JSON에서 들어온 값을 자동으로 검증하고 타입 변환
raw = {"order_id": "ord-1", "amount": "1000", "currency": "KRW"}
req = OrderRequest.model_validate(raw)
print(req.amount + 100)  # 1100 (str "1000" → int 1000으로 자동 변환 후 검증)
```

`pydantic`은 런타임 검증과 정적 타입 힌트를 동시에 제공합니다. 경계에서 들어오는 `dict[str, Any]`를 강타입 모델로 변환하는 가장 실용적인 방법입니다.

## TypeScript: 동적 JavaScript 위에 정적 검사 얹기

TypeScript는 JavaScript의 동적 타이핑 위에 정적 타입 레이어를 추가한 대표적인 사례입니다. 점진적 타입이 실제로 어떻게 작동하는지 잘 보여 줍니다.

```typescript
// TypeScript: 점진적 타입 도입
// 1단계: any 타입으로 시작 (동적과 동일)
function processData(data: any): any {
    return data.value * 2;
}

// 2단계: 구체적 타입으로 좁히기
interface DataPoint {
    value: number;
    label: string;
}

function processDataTyped(data: DataPoint): number {
    return data.value * 2;  // value가 number임을 컴파일러가 알고 있음
}

// 3단계: 제네릭으로 타입 안전성 유지하면서 재사용성 높이기
function first<T>(items: T[]): T | undefined {
    return items[0];
}

const num = first([1, 2, 3]);   // 타입: number | undefined
const str = first(["a", "b"]);  // 타입: string | undefined

// 컴파일 오류 예시
// processDataTyped({ value: "not a number", label: "x" });
// Error: Type 'string' is not assignable to type 'number'
```

TypeScript의 `tsc --strict` 플래그는 Python의 `mypy --strict`와 같은 역할을 합니다. 기존 JavaScript 코드에서 시작해 점진적으로 타입을 추가하면서 도구 지원과 안전성을 높일 수 있습니다.

## 타입 검사기를 CI에 통합하는 실전 패턴

정적 타입 검사의 가치는 개발자 로컬 환경뿐 아니라 CI 파이프라인에 통합할 때 본격적으로 나타납니다.

```python
# pyproject.toml — mypy 설정 예시
# [tool.mypy]
# python_version = "3.11"
# strict = true
# ignore_missing_imports = false
# disallow_any_explicit = true

# CI에서 실행하는 타입 검사 스크립트
import subprocess
import sys

def run_type_check() -> int:
    """mypy를 실행하고 결과를 반환합니다."""
    result = subprocess.run(
        ["mypy", "src/", "--strict"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("Type errors found:")
        print(result.stdout)
        return 1
    print("All type checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(run_type_check())
```

```text
CI 파이프라인 통합 흐름:
git push
    |
    v
CI 서버 (GitHub Actions / GitLab CI)
    |
    +-- ruff (린팅, 빠른 구문 검사)
    |
    +-- mypy --strict (타입 검사)
    |
    +-- pytest (단위 테스트)
    |
    +-- pytest --cov (커버리지)
    |
    v
PR 머지 허용 / 차단
```

타입 검사기를 CI에 넣으면 "내 컴퓨터에서는 됐는데"라는 말이 사라집니다. 특히 여러 사람이 공유 코드베이스를 수정할 때 타입 회귀(type regression)를 자동으로 잡아 줍니다.

## 운영 체크리스트

- [ ] 정적과 동적의 차이를 한 줄로 설명할 수 있는가?
- [ ] mypy나 pyright를 CI에서 돌리고 있는가?
- [ ] 외부 입력이 들어오는 경계에 검증이 있는가?
- [ ] `Any` 사용량을 의식적으로 관리하는가?
- [ ] 점진적 타입의 의미를 한 문장으로 설명할 수 있는가?

## 연습 문제

1. 최근 함수 하나에 타입 힌트를 추가하고 mypy를 돌린 뒤, 어떤 종류의 오류가 잡히는지 적어 보세요.
2. JSON을 받는 경계에 `pydantic` 모델을 적용해 보고, 이전과 이후의 오류 메시지를 비교해 보세요.
3. `Protocol` 예제를 ABC 기반 상속으로 바꾼 뒤 무엇이 더 번거로워졌는지 정리해 보세요.

## 정리

정적과 동적은 우열이 아니라 선택입니다. 중요한 것은 어떤 오류를 언제 발견하고 싶은가입니다. 다음 마지막 글에서는 지금까지 본 모든 개념을 묶어 좋은 언어 설계가 무엇인지로 넘어가겠습니다.

## 처음 질문으로 돌아가기

- **정적과 동적의 가장 짧은 정의는 무엇일까요?**
  - 정적 타입은 실행 전에 타입을 검사합니다. 동적 타입은 실행 중에 타입 오류가 드러납니다. 핵심은 "언제 검사하는가"입니다.
- **같은 코드가 두 모델에서 어떻게 다르게 검증될까요?**
  - 정적 모델에서는 `add(1, "hello")`가 컴파일 단계에서 오류로 잡힙니다. 동적 모델에서는 이 코드가 실행되는 순간에야 `TypeError`가 나타납니다. 검사 시점이 다를 뿐 오류 자체는 같습니다.
- **mypy나 pyright가 잡을 수 있는 것과 없는 것은 무엇일까요?**
  - 잡을 수 있는 것: 함수 인자 타입 불일치, 없는 속성 접근, 반환 타입 불일치, `None` 역참조 가능성. 잡기 어려운 것: 외부 JSON에서 들어온 값의 타입, 런타임 동적 속성 추가, `Any`를 통과한 값. 경계에서 런타임 검증을 추가하는 이유입니다.

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
- **Programming Languages 101 (9/10): 정적 언어와 동적 언어 (현재 글)**
- [Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?](./10-what-makes-good-language-design.md)

<!-- toc:end -->

## 참고 자료

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [Pyright documentation](https://microsoft.github.io/pyright/)
- [TypeScript Handbook — Basic Types](https://www.typescriptlang.org/docs/handbook/2/basic-types.html)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, StaticTyping, DynamicTyping, Tradeoffs, Safety
