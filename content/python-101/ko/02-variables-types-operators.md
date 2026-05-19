---
title: 변수, 타입, 연산자
series: python-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- variables
- python-types
- equality-vs-identity
- floating-point
- decimal
- type-hints
last_reviewed: '2026-05-12'
seo_description: Python에서 변수는 값을 담는 상자가 아니라 객체에 붙는 이름표라는 한 가지 모델만 머릿속에 두면, 할당·비교·복사에서
  일어나는 거의…
---

# 변수, 타입, 연산자

Python에서 변수는 값을 담는 상자가 아니라 객체에 붙는 이름표입니다. 이 모델 하나만 정확히 잡아도 할당, 비교, 복사에서 헷갈리는 지점이 크게 줄어듭니다.

이 글은 Python 101 시리즈의 두 번째 글입니다.

## 이 글에서 다룰 문제

변수와 타입은 모든 코드의 뼈대입니다. "그냥 `x = 1`이지 뭐가 어렵냐"고 생각하면 다음과 같은 버그에 반복해서 부딪힙니다.

- `total = total + items` 했더니 숫자에 문자열을 더했다는 `TypeError`가 납니다.
- `if user.age == "18":` 처럼 비교했더니 영원히 `False`가 나옵니다.
- `0.1 + 0.2 == 0.3`이 `False`라서 결제 금액 검증이 실패합니다.
- 함수 인자로 list를 넘겼는데 호출 쪽 list가 같이 바뀌어 있어서 추적이 안 됩니다.

이 문제들의 공통 뿌리는 "변수가 무엇을 가리키는지", "타입이 무엇을 보장하는지"를 정확히 모르는 데 있습니다. 한 번만 제대로 잡고 가면 이후의 자료구조·함수·클래스 단원이 훨씬 가볍습니다.

## 멘탈 모델

> Python에서 변수는 값을 담는 상자가 아니라 객체에 붙는 이름표라는 한 가지 모델만 머릿속에 두면, 할당·비교·복사에서 일어나는 거의 모든 함정이 같은 그림으로 설명됩니다.
Python에서 변수는 값을 담는 상자가 아닙니다. **객체에 붙는 이름표**입니다. 같은 객체에 여러 이름표가 붙을 수도 있고, 이름표를 다른 객체로 옮길 수도 있습니다.

![Mental Model](https://yeongseon-books.github.io/book-public-assets/assets/python-101/02/02-01-mental-model.ko.png)

*Mental Model*
위 그림에서 `a = 42; b = a`를 실행하면 `a`와 `b`는 모두 같은 정수 객체 `42`를 가리킵니다. 그리고 `a = "hi"`를 실행하면 `a`만 새 문자열 객체로 옮겨가고, `b`는 여전히 `42`를 가리킵니다.

왼쪽이 `b = a` 직후의 모습이고, 오른쪽이 `a = "hi"`로 이름표만 옮긴 뒤의 모습입니다. 객체 자체는 변하지 않습니다. 변하는 것은 어떤 이름표가 어떤 객체를 가리키는가뿐입니다.

이 모델을 머릿속에 그리고 있으면 다음 두 동작이 자연스럽게 이해됩니다.

- `id(a) == id(b)`로 두 이름표가 같은 객체를 가리키는지 확인할 수 있습니다.
- list처럼 변경 가능한(mutable) 객체에 두 이름표가 붙어 있으면, 한쪽으로 수정한 결과를 다른 쪽에서도 똑같이 봅니다.

## 핵심 개념

### 1) 동적 타입과 type hint

Python은 변수 자체에 타입을 묶지 않습니다. 타입은 변수가 가리키는 객체에 붙어 있습니다.

```python
x = 1          # the name now points at an int object
x = "hello"    # the same name now points at a str object
```

이 자유 덕분에 빠르게 짤 수 있지만, 큰 코드베이스에서는 "이 함수가 무엇을 받고 무엇을 돌려주는지"가 흐려집니다. 그래서 PEP 484 이후 Python은 **type hint**를 표준으로 채택했습니다.

```python
def total_price(quantity: int, unit_price: float) -> float:
    return quantity * unit_price
```

타입 힌트는 런타임 동작을 강제하지 않습니다. `mypy`나 `pyright` 같은 정적 분석기가 별도로 검증합니다. "런타임에는 자유, 빌드 단계에서는 안전"이 Python이 선택한 균형입니다.

### 2) 다섯 가지 기본 타입

| 타입 | 예시 | 메모 |
| --- | --- | --- |
| `int` | `42`, `-7`, `1_000_000` | 임의 정밀도. 오버플로가 없습니다. |
| `float` | `3.14`, `1e-9` | 64-bit IEEE 754. 부동소수 오차가 있습니다. |
| `str` | `"hello"`, `'world'` | 불변(immutable). 유니코드 텍스트입니다. |
| `bool` | `True`, `False` | `int`의 하위 타입입니다 (`True == 1`). |
| `None` | `None` | "값이 없음"을 나타내는 단 하나의 객체입니다. |

세 가지를 꼭 기억하세요. 첫째, `int`는 임의 정밀도라 C/Java처럼 오버플로 걱정을 하지 않아도 됩니다. 둘째, `float`는 IEEE 754라서 `0.1 + 0.2`가 정확히 `0.3`이 아닙니다. 셋째, `None`은 "비어 있음"을 표현하는 표준 방법이라서 `if x is None:`처럼 비교합니다.

### 3) 연산자

산술은 익숙한 그대로지만, 정수 나눗셈과 거듭제곱은 처음 보면 헷갈립니다.

```python
7 / 2     # 3.5 (always returns a float)
7 // 2    # 3   (floor division)
7 % 2     # 1   (remainder)
2 ** 10   # 1024 (exponentiation)
```

비교 연산자는 chain이 가능합니다. `0 <= x < 10`은 `x >= 0 and x < 10`과 같습니다. 이 표현은 가독성이 좋아서 적극적으로 사용해도 됩니다.

논리 연산자는 short-circuit 평가를 합니다. `a and b`에서 `a`가 falsy면 `b`는 평가하지 않습니다. 그래서 다음 패턴이 자주 쓰입니다.

```python
name = user.name or "guest"          # if user.name is empty, fall back to "guest"
config = override_config or default_config
```

## 전후 비교

타입 힌트와 명시적인 변수가 코드 가독성을 어떻게 바꾸는지 짧게 비교해 봅니다.

**Before — 의도가 코드에 안 보입니다**

```python
def calc(q, p, r):
    return q * p * (1 - r)
```

`q`가 수량인지 품질인지, `r`이 할인율인지 환율인지 함수 이름과 인자만 봐서는 알 수 없습니다.

**After — 이름과 타입으로 의도를 드러냅니다**

```python
def discounted_total(quantity: int, unit_price: float, discount_rate: float) -> float:
    return quantity * unit_price * (1 - discount_rate)
```

이름이 길어진 만큼 호출하는 쪽 코드는 짧아집니다. `discounted_total(3, 9_900, 0.1)`만 봐도 무엇을 하는지 알 수 있습니다.

## 단계별 실습

REPL을 열고 한 줄씩 따라 입력해 보세요. 결과가 책과 다르면 그 자리에서 멈추고 왜 그런지 생각해 봅니다.

### 1) 같은 객체와 다른 객체

```text
>>> a = [1, 2]
>>> b = [1, 2]
>>> a == b      # value comparison: True
True
>>> a is b      # identity comparison: False (two distinct list objects)
False
>>> c = a
>>> c is a      # True — two name tags on the same list object
True
```

위 예제에서 `a`와 `b`는 내용이 같은 list지만 서로 다른 객체입니다. 그래서 `a == b`는 `True`, `a is b`는 `False`입니다. 반면 `c = a`로 이름표를 하나 더 붙이면 `c`와 `a`는 같은 객체를 가리키므로 `c is a`는 `True`입니다. 핵심은 `==`은 값을, `is`는 객체 정체성을 본다는 점입니다. None을 비교할 때만 `is None`을 쓰고, 그 외에는 거의 항상 `==`을 씁니다.

### 2) 부동소수의 함정

```text
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
>>> import math
>>> math.isclose(0.1 + 0.2, 0.3)
True
```

계산 결과로 나온 float를 비교할 때, 허용 오차가 필요하면 `math.isclose`를 씁니다. 정확한 값이 필요하면 `Decimal`로 갈아탑니다. 상수 쪽이 정확히 표현되더라도, 반대편이 계산 결과인 float라면 반올림 오차가 남을 수 있으므로 일반화하지 않는 편이 안전합니다.

### 3) 타입 변환

```text
>>> int("42")           # 42
>>> float("3.14")       # 3.14
>>> str(42)             # '42'
>>> bool(0), bool(1)    # (False, True)
>>> bool(""), bool("hi")  # (False, True)
>>> int("3.14")         # ValueError
```

`int("3.14")`가 에러인 이유는 정수 리터럴 형식이 아니기 때문입니다. 소수점이 섞인 문자열을 정수로 바꾸려면 `int(float("3.14"))`처럼 두 단계로 변환합니다.

## 이 코드에서 주목할 점

- `a == b`와 `a is b`를 한 줄 차이로 보여 준 이유 — 값과 정체성은 별개의 개념입니다. `==`은 값을, `is`는 객체 자체를 봅니다. 둘이 같은 결과를 줄 때도 많지만, 같다는 보장은 없습니다.
- `math.isclose(0.1 + 0.2, 0.3)` — 부동소수 비교의 표준 도구입니다. 직접 `abs(a - b) < 1e-9`처럼 적기보다 표준 라이브러리에 있는 함수를 쓰는 편이 의도가 분명합니다.
- `int("3.14")`가 `ValueError`라는 사실 — Python의 변환은 "리터럴 형식"을 엄격히 요구합니다. 소수점이 섞인 문자열은 `int(float("3.14"))`처럼 두 단계를 거칩니다.
- `bool("")`, `bool(0)`이 `False`라는 점 — Python의 falsy 값 규칙을 한 줄로 보여 줍니다. 빈 컨테이너, 0, `None`이 모두 falsy입니다. `if items:`가 `if len(items) > 0:`보다 읽기 좋은 이유입니다.
- `c = a` 후 `c is a`가 `True` — 할당이 값을 복사하지 않고 이름표만 추가한다는 사실을 객체 정체성으로 검증합니다. 셸 출력으로 직접 본 결과만큼 확실한 증거는 없습니다.

## 자주 하는 실수

**1. `==`와 `is`를 섞어 쓰기**
객체 정체성을 비교하려는 의도가 아니면 `==`을 사용합니다. `if name is "admin":`은 CPython 구현 디테일에 따라 우연히 동작할 수 있어도 잘못된 코드입니다.

**2. 부동소수를 `==`로 비교**
앞에서 본 `0.1 + 0.2 != 0.3`이 대표 사례입니다. 금액·세금·할인율은 `decimal.Decimal`을 사용하고, 일반 부동소수 비교는 `math.isclose`를 씁니다.

**3. 변경 가능한 기본 인자**
함수 기본 인자는 정의 시점에 한 번만 평가됩니다. `def f(x, items=[]):`처럼 쓰면 호출 사이에 list가 누적됩니다. 기본값으로 `None`을 두고 함수 안에서 새 list를 만드는 패턴을 사용합니다.

```python
def append_id(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**4. 문자열과 숫자 혼동**
사용자 입력은 항상 문자열로 들어옵니다. `input("나이: ")`의 결과는 `"25"`이지 `25`가 아닙니다. 비교 전에 `int(...)`로 명시적으로 변환합니다.

**5. boolean을 정수처럼 더하기**
`True + True`는 `2`입니다. 트릭처럼 쓸 수는 있어도 가독성이 떨어지므로, 카운트는 `sum(1 for x in xs if cond(x))`처럼 의도를 드러냅니다.

**6. 큰 숫자를 가독성 없이 적기**
`10000000`보다 `10_000_000`이 읽기 쉽습니다. Python은 정수 리터럴 안의 밑줄을 무시하므로 자릿수 구분에 자유롭게 쓰세요.

## 실무에서는 이렇게 생각합니다

**1. mypy로 타입 힌트 검증**
타입 힌트는 적어 두기만 해서는 안전을 주지 않습니다. CI에서 `mypy src/`를 돌려야 의미가 있습니다. `pyproject.toml`에 다음을 넣어 두면 strict 모드로 검증합니다.

```toml
[tool.mypy]
strict = true
python_version = "3.12"
```

**2. 금액·세금에는 `Decimal`을 사용**
`float`로 결제 금액을 다루면 반올림 버그가 누적됩니다.

```python
from decimal import Decimal

price = Decimal("9900")
tax = price * Decimal("0.1")
total = price + tax  # Decimal('10890')
```

문자열 리터럴로 만드는 것이 핵심입니다. `Decimal(0.1)`은 이미 부동소수 오차가 들어 있는 값을 받으므로 의미가 없습니다.

**3. 환경 변수는 항상 캐스팅**
`os.environ["PORT"]`은 문자열입니다. 비교나 산술에 쓰기 전에 `int(...)`로 변환하고, 변환에 실패할 가능성을 핸들링합니다.

```python
import os

port = int(os.environ.get("PORT", "8000"))
```

**4. `dataclass`로 가벼운 값 객체 만들기**
서너 개 필드가 모이면 dict 대신 `dataclass`를 씁니다. 타입 힌트와 기본값이 한 곳에 모이고, IDE가 자동완성을 도와줍니다.

```python
from dataclasses import dataclass

@dataclass
class Order:
    order_id: str
    quantity: int
    unit_price: float
```

## 체크리스트

다음 글로 넘어가기 전에 한 번씩 손으로 확인해 보세요.

- [ ] REPL에서 `a = [1, 2]; b = [1, 2]; print(a == b, a is b)`를 실행해 보았다
- [ ] `0.1 + 0.2`가 `0.3`과 같지 않다는 것을 직접 확인했다
- [ ] `int`, `float`, `str`, `bool`, `None`을 한 줄씩 설명할 수 있다
- [ ] type hint가 런타임을 바꾸지 않는다는 점을 이해했다
- [ ] mypy를 한 번이라도 실행해 보았다
- [ ] `Decimal`로 금액 계산을 한 번 해 보았다

## 정리·다음 글

- Python 변수는 객체에 붙는 이름표입니다. `=`은 값을 복사하지 않고 이름표를 옮깁니다.
- 동적 타입은 자유롭지만, 큰 코드에서는 type hint와 mypy로 안전을 보강합니다.
- `int`는 오버플로가 없고, `float`는 부동소수 오차가 있으며, `bool`은 `int`의 하위 타입입니다.
- `==`은 값을, `is`는 객체 정체성을 비교합니다. None만 `is None`으로 비교합니다.
- 금액은 `Decimal`로, float 비교는 `math.isclose`로, 사용자 입력은 명시적으로 캐스팅합니다.

다음 글에서는 문자열을 깊이 있게 다룹니다. f-string과 format spec, str·bytes 차이, 정규표현식의 첫 만남까지 짚어 봅니다.

<!-- toc:begin -->
- [왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- **변수, 타입, 연산자 (현재 글)**
- 문자열과 포매팅 (예정)
- list, tuple, set, dict (예정)
- 제어 흐름: if, for, while, comprehension (예정)
- 함수와 인자: def, args, kwargs, default, lambda (예정)
- 모듈과 패키지: import, __init__, __name__ (예정)
- 파일 I/O와 예외 처리 (예정)
- 클래스와 객체 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — `int`, `float`, `bool`, `None`, truthy/falsy, 시퀀스 공통 규칙의 기준 문서입니다.
- [Python 공식 문서 — Expressions](https://docs.python.org/3/reference/expressions.html) — 산술·비교·`is`·논리 연산의 문법과 평가 순서를 정확히 확인할 수 있습니다.
- [Python 튜토리얼 — Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html) — `0.1 + 0.2` 같은 부동소수 표현 오차를 설명하는 공식 입문 자료입니다.
- [Python 공식 문서 — `decimal`](https://docs.python.org/3/library/decimal.html) — 금액 계산처럼 정확한 십진 연산이 필요한 경우의 대안을 다룹니다.
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) — 타입 힌트가 런타임 강제가 아니라 정적 분석용 계약이라는 점의 출처입니다.
- [Python Data Model](https://docs.python.org/3/reference/datamodel.html) — 객체 정체성, 변경 가능성, 이름이 객체를 가리킨다는 모델을 더 깊게 보완합니다.

Tags: variables, python-types, equality-vs-identity, floating-point, decimal, type-hints
