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
title: 정적 언어와 동적 언어
---

# 정적 언어와 동적 언어

정적 타입이 더 안전하다는 말은 자주 듣지만, 그 안전이 정확히 무엇을 덮는지 묻는 순간 답이 흐려지는 경우가 많습니다. 반대로 동적 언어가 더 빠르다는 말도 자주 나오지만, 실제로는 어떤 종류의 속도를 말하는지 구분이 필요합니다.

이 글은 Programming Languages 101 시리즈의 아홉 번째 글입니다.

이 글에서는 정적 언어와 동적 언어를 우열의 문제가 아니라 검사 시점의 선택으로 보겠습니다. 같은 함수를 타입 힌트 없이 쓴 버전과 명시적으로 쓴 버전을 나란히 놓고, 어떤 종류의 오류를 언제 잡을 수 있는지 현실적으로 정리하겠습니다.

## 이 글에서 다룰 문제

- 정적과 동적의 가장 짧은 정의는 무엇일까요?
- 같은 코드가 두 모델에서 어떻게 다르게 검증될까요?
- mypy나 pyright가 잡을 수 있는 것과 없는 것은 무엇일까요?
- 점진적 타입은 어떤 타협을 가능하게 할까요?

> 정적과 동적의 차이는 좋은 쪽과 나쁜 쪽의 차이가 아니라, 타입 약속을 언제 검사하느냐의 차이입니다. 같은 종류의 오류라도 정적 언어는 빌드 전에, 동적 언어는 실행 중에 드러나게 만드는 편입니다.

## 왜 중요한가

팀이 커질수록 “타입을 더 붙일까?”라는 논의가 반복됩니다. 이때 필요한 것은 신념이 아니라, 정적 검사가 무엇을 보장하고 무엇을 보장하지 않는지 한 문장으로 설명할 수 있는 감각입니다.

## 핵심 개념 한눈에 보기

![같은 타입 오류가 정적 검사와 동적 검사에서 드러나는 시점 비교](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/09/09-01-concept-at-a-glance.ko.png)

*같은 타입 오류가 정적 검사와 동적 검사에서 드러나는 시점 비교*

같은 유형의 오류라도 어느 시점에 드러나는지가 다릅니다. 정적 타입은 실행 전에 막고, 동적 타입은 실행 흐름이 그 지점에 도달했을 때 드러냅니다.

## 먼저 알아둘 용어

- 정적 타입: 변수와 표현식의 타입을 실행 전에 검사합니다.
- 동적 타입: 값에 타입이 붙고, 검사는 실행 중에 이뤄집니다.
- 강한 타입과 약한 타입: 암묵적 형변환 허용 범위를 나타내는 별도 축입니다.
- 점진적 타입: 한 코드베이스 안에 정적 영역과 동적 영역을 함께 두는 방식입니다.
- 건전성: 검사기가 통과시킨 코드가 타입 규칙을 어기지 않는다는 보장입니다.

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

## 이 코드에서 먼저 볼 점

- 정적 타입의 보장은 외부 입력이 들어오는 경계에서 끝나는 경우가 많습니다.
- 점진적 타입은 두 모델을 실용적으로 섞는 방식입니다.
- `Protocol`은 상속 없이도 “같은 모양”을 표현하게 해 줍니다.
- 짧은 스크립트나 메타프로그래밍처럼 동적 모델이 더 자연스러운 영역도 분명히 있습니다.

## 자주 하는 실수

1. 정적은 안전하고 동적은 위험하다고 단순화합니다. 둘은 다른 비용을 냅니다.
2. 타입 힌트만 붙이면 외부 입력 문제까지 해결된다고 믿습니다. 경계 검증은 별도입니다.
3. `Any`를 너무 많이 써서 점진적 타입을 사실상 포기합니다.
4. 힌트만 달고 검사기를 CI에 넣지 않습니다. 그러면 타입은 문서 이상의 역할을 못 합니다.
5. 타입과 테스트를 서로 대체재로 봅니다. 잡는 버그 종류가 다릅니다.

## 실무에서는 이렇게 본다

큰 Python 코드베이스는 이제 거의 예외 없이 mypy나 pyright를 CI에서 돌립니다. JavaScript 진영도 TypeScript를 사실상 표준처럼 받아들였습니다. 이때 성능보다 더 큰 이점은 유지보수입니다. 코드 경계가 많아질수록 타입 정보가 문서와 자동 완성과 리팩터링 안전망 역할을 같이 해 주기 때문입니다.

요즘 많이 쓰는 패턴은 경계에서 강하게 검증하고, 내부에서는 정밀하게 타입을 다루는 방식입니다. `pydantic`, `dataclass`, `Protocol`이 자주 함께 등장하는 이유도 이 조합이 실무에서 잘 맞기 때문입니다.

## 체크리스트

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

<!-- toc:begin -->
- [프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [구문과 의미](./02-syntax-and-semantics.md)
- [타입 시스템](./03-type-system.md)
- [스코프와 바인딩](./04-scope-and-binding.md)
- [함수와 클로저](./05-functions-and-closures.md)
- [객체와 프로토타입](./06-objects-and-prototypes.md)
- [메모리 관리](./07-memory-management.md)
- [인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- **정적 언어와 동적 언어 (현재 글)**
- 좋은 언어 설계란 무엇인가? (예정)
<!-- toc:end -->

## 참고 자료

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [Pyright documentation](https://microsoft.github.io/pyright/)
- [TypeScript Handbook — Basic Types](https://www.typescriptlang.org/docs/handbook/2/basic-types.html)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)

Tags: Computer Science, Programming Languages, StaticTyping, DynamicTyping, Tradeoffs, Safety
