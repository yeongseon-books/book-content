---
series: programming-languages-101
episode: 3
title: type system
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
  - Programming Languages
  - TypeSystem
  - 정적타입
  - 동적타입
  - 추론
seo_description: 타입 시스템은 단순한 자료형 검사가 아니라 잘못된 프로그램을 미리 막아 주는 증명 도구입니다. 기본 개념을 정리합니다.
last_reviewed: '2026-05-04'
---

# type system

> Programming Languages 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 동적 언어로도 잘 돌아가는데, 왜 굳이 타입을 적는 일에 시간을 쓸까요?

> 타입 시스템은 단순한 자료형 표기가 아니라, **"이 프로그램이 의미 없는 짓을 하지 않는다"는 사실을 실행 전에 보증해 주는 도구**입니다. 정적 타입은 안전성과 도구 지원을 얻는 대신 표현의 자유를 약간 내주고, 동적 타입은 그 반대를 택합니다. 이 글은 그 거래의 본질을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 타입의 역할: 검사, 문서, 도구 지원
- 정적 타입 vs 동적 타입의 트레이드오프
- 강한/약한 타입과 정적/동적의 구별
- 타입 추론이 해주는 일
- 제네릭과 합집합/교집합 타입의 직관

## 왜 중요한가

현대 언어는 대부분 어떤 형태의 타입 시스템을 가지고 있고, Python·JavaScript·Ruby 같은 동적 언어조차 점진적 타입 시스템(Type Hints, TypeScript)을 도입했습니다. 타입을 이해해야 자동 완성, 리팩터링 도구, 빌드 단계의 에러 메시지를 제대로 활용할 수 있고, 시리즈 후반의 scope·closure도 타입 위에서 분석됩니다.

> 타입은 "모든 가능한 입력 중 어떤 것이 합법인가"를 미리 좁혀 주는 약속입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    A["Source code"] --> B["Type checker"]
    B -->|pass| C["Compile / Run"]
    B -->|fail| D["Error before run"]
    E["Types as docs"] --> F["IDE: completion, refactor"]
```

타입 검사기는 실행 전에 "잘못 가능한 호출"을 잘라 냅니다. 동시에 IDE에는 자동 완성과 안전한 리팩터링의 근거가 됩니다.

## 핵심 용어 정리

- **Static typing**: 컴파일/검사 단계에서 타입을 확인.
- **Dynamic typing**: 실행 중에 값의 타입을 확인.
- **Strong typing**: 암묵적 형변환을 잘 허용하지 않음.
- **Weak typing**: 암묵적 형변환이 흔함(예: JavaScript의 `+`).
- **Type inference**: 명시하지 않아도 컴파일러가 타입을 추론.
- **Generics**: 같은 코드가 여러 타입에 안전하게 동작하도록 하는 매개변수화.

## Before/After

**Before — 타입 없는 함수**

```python
def discount(price, rate):
    return price - price * rate

# 누가 이렇게 부른다
discount("1000", 0.1)  # 실행 시 TypeError: can't multiply str
```

함수 시그니처만 봐서는 어떤 타입을 기대하는지 알기 어렵고, 잘못된 호출은 실행해야 드러납니다.

**After — 타입을 적은 함수**

```python
def discount(price: int, rate: float) -> float:
    return price - price * rate

discount("1000", 0.1)  # mypy가 호출 단계에서 거부
```

`mypy` 같은 정적 검사기가 실행 전에 잡아 줍니다. 시그니처는 그 자체로 작은 문서가 됩니다.

## 실습: 타입을 단계적으로 도입해 보기

### 1단계 — 타입 힌트 적기

```python
# 1_hints.py
def to_kebab(s: str) -> str:
    return s.strip().lower().replace(" ", "-")

print(to_kebab("Hello World"))
```

`-> str`이 없어도 동작은 같지만, 호출자에게 약속이 생깁니다.

### 2단계 — mypy로 검사

```bash
pip install mypy
mypy 1_hints.py    # Success: no issues
```

빌드 단계에서 검사하는 습관이 시작됩니다.

### 3단계 — 제네릭 함수

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

같은 함수가 여러 타입에 대해 정확한 반환 타입을 유지합니다. 도구 지원이 한 단계 강해집니다.

### 4단계 — 합집합 타입과 좁히기

```python
# 4_union.py
def length(x: str | list) -> int:
    if isinstance(x, str):
        return len(x)
    return sum(len(item) for item in x)
```

`isinstance` 검사 후 타입 검사기는 분기 안에서 타입을 좁혀 줍니다.

### 5단계 — 타입을 도입했더니 잡힌 진짜 버그

```python
# 5_real_bug.py
def total_price(items: list[dict]) -> int:
    return sum(item["price"] for item in items)  # 타입 표기 후 mypy가 dict값 타입 모호함을 지적
```

타입을 정확히 적으려고 하면, 데이터 모델 자체의 모호함이 드러납니다. 보통은 그게 진짜 버그의 원인입니다.

## 이 코드에서 주목할 점

- 타입은 "검사"이자 "문서"이자 "도구의 입력"입니다.
- 정적 검사는 모든 버그를 잡지 못하지만, 가장 흔한 종류의 버그를 가장 싸게 잡아 줍니다.
- 제네릭은 "한 번 짜고 여러 타입에 쓰기"의 안전한 방식입니다.
- 합집합 타입과 isinstance 좁히기는 동적 언어 출신에게 익숙한 사고를 정적 검사에 그대로 옮겨 줍니다.

## 자주 하는 실수 5가지

1. **`Any`를 도배한다.** 검사기가 침묵할 뿐, 안전성은 없습니다.
2. **타입을 한 번에 다 붙이려 한다.** 핵심 경계(공개 함수, 모듈 인터페이스)부터 점진적으로.
3. **타입과 런타임 검증을 헷갈린다.** `mypy`는 런타임에 데이터 모양을 검사하지 않습니다. 외부 입력은 별도로 검증해야 합니다.
4. **너무 정교한 타입을 추구한다.** 90% 케이스를 잡아 주는 단순한 타입이, 100% 잡아 주는 복잡한 타입보다 대부분의 경우 더 가치 있습니다.
5. **동적 언어와 정적 언어를 우열로 본다.** 도메인과 팀 크기에 따라 비용/이득이 달라지는 트레이드오프입니다.

## 실무에서는 이렇게 쓰입니다

대형 Python 코드베이스는 mypy/pyright를 빌드 단계에 넣고, 공개 함수의 타입을 강제합니다. JavaScript 진영은 TypeScript가 사실상 표준이 됐습니다. 라이브러리 경계의 타입은 사용자가 받아 보는 1차 문서이고, 자동 완성의 근거이기도 합니다.

타입은 리팩터링의 안전망입니다. "이 함수의 인자 순서를 바꾼다"는 변경이 컴파일 단계에서 모든 호출 지점을 빨갛게 만들면, 그 작업을 자신 있게 할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모듈 경계와 공개 API에 타입을 우선 붙입니다. 내부 헬퍼는 점진적으로.
- `Any`를 발견하면 한 단계 좁힐 방법을 찾습니다.
- 외부 입력은 항상 별도로 검증합니다(타입 ≠ 런타임 검증).
- 정적/동적 선택을 신앙으로 보지 않고, 팀 크기와 변경 빈도로 봅니다.
- 도구 지원(자동 완성, 리팩터링)을 타입의 부수 효과가 아니라 본질로 봅니다.

## 체크리스트

- [ ] 정적 vs 동적, 강한 vs 약한 타입의 차이를 한 줄로 구별할 수 있는가?
- [ ] 점진적 타입 도입의 첫 대상이 어디여야 하는지 답할 수 있는가?
- [ ] `Any`를 무엇으로 좁힐지 한 가지 전략을 갖고 있는가?
- [ ] 타입과 런타임 검증의 차이를 알고 있는가?
- [ ] 제네릭이 왜 단순 매개변수화보다 더 강한지 설명할 수 있는가?

## 연습 문제

1. 위 실습의 `total_price`에 `TypedDict`를 도입해 `item`의 모양을 정확히 적어 보세요.
2. 가장 익숙한 동적 언어로 짠 함수 하나를 골라, 입력과 출력 타입을 글로 적어 보세요. 모호한 부분이 있다면 그게 어떤 의미인지 한 줄로 적으세요.
3. "타입을 도입한 뒤 발견된 진짜 버그"의 사례를 하나 떠올리고, 그게 왜 동적 검사로는 늦게야 잡혔는지 설명해 보세요.

## 정리 및 다음 단계

타입 시스템은 안전성, 문서, 도구 지원을 한 번에 얻을 수 있는 도구입니다. 모든 언어에 모든 수준의 타입이 필요한 것은 아니지만, 경계가 큰 시스템에서는 거의 항상 이득입니다. 다음 글에서는 타입과 함께 모든 언어의 또 다른 기둥 — scope와 binding — 을 살펴봅니다.

<!-- toc:begin -->
- [프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [syntax와 semantics](./02-syntax-and-semantics.md)
- **type system (현재 글)**
- scope와 binding (예정)
- 함수와 closure (예정)
- 객체와 prototype (예정)
- memory management (예정)
- interpreter와 compiler (예정)
- static vs dynamic language (예정)
- 좋은 언어 설계란 무엇인가? (예정)
<!-- toc:end -->

## 참고 자료

- [Types and Programming Languages (Pierce)](https://www.cis.upenn.edu/~bcpierce/tapl/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
