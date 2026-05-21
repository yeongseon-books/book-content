---
title: "Python 101 (2/10): 변수, 타입, 연산자"
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

# Python 101 (2/10): 변수, 타입, 연산자

Python에서 변수는 값을 담는 상자가 아니라 객체에 붙는 이름표입니다. 이 모델 하나만 정확히 잡아도 할당, 비교, 복사에서 헷갈리는 지점이 크게 줄어듭니다.

이 글은 Python 101 시리즈의 두 번째 글입니다.

## 먼저 던지는 질문

- `total = total + items` 했더니 숫자에 문자열을 더했다는 `TypeError`가 납니다?
- `if user.age == "18":` 처럼 비교했더니 영원히 `False`가 나옵니다?
- `0.1 + 0.2 == 0.3`이 `False`라서 결제 금액 검증이 실패합니다?

## 큰 그림

![Python 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/02/02-01-mental-model.ko.png)

*Python 101 2장 흐름 개요*

이 그림에서는 변수, 타입, 연산자를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 변수, 타입, 연산자의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 멘탈 모델

> Python에서 변수는 값을 담는 상자가 아니라 객체에 붙는 이름표라는 한 가지 모델만 머릿속에 두면, 할당·비교·복사에서 일어나는 거의 모든 함정이 같은 그림으로 설명됩니다.
Python에서 변수는 값을 담는 상자가 아닙니다. **객체에 붙는 이름표**입니다. 같은 객체에 여러 이름표가 붙을 수도 있고, 이름표를 다른 객체로 옮길 수도 있습니다.

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

## 실전 앵커: 객체 모델, 참조 카운트, 연산 비용을 눈으로 확인하기

변수는 상자가 아니라 이름 바인딩이라는 설명을 들으면 대부분 이해했다고 느낍니다. 하지만 실제로는 연산자와 타입 변환이 섞이는 순간 다시 헷갈립니다. 여기서는 REPL 출력으로 객체 모델을 고정해 보겠습니다.

```pycon
>>> x = 10
>>> y = x
>>> id(x), id(y)
(4381320848, 4381320848)
>>> y += 1
>>> x, y
(10, 11)
>>> id(x), id(y)
(4381320848, 4381320880)
```

정수는 불변 객체이므로 `y += 1`은 같은 객체를 수정한 것이 아니라 새 객체에 재바인딩한 것입니다. 반대로 가변 타입은 다르게 동작합니다.

```pycon
>>> a = [1, 2]
>>> b = a
>>> b.append(3)
>>> a
[1, 2, 3]
```

이 차이를 이해하지 못하면 함수 인자 전달에서 버그가 발생합니다. 특히 기본값 인자와 결합되면 문제 재현이 어렵습니다.

```python
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item('A'))
print(add_item('B'))
```

출력:

```text
['A']
['A', 'B']
```

이 코드는 호출마다 빈 리스트가 생길 것 같지만, 기본값은 함수 정의 시 한 번만 평가됩니다. 안전한 패턴은 `None` 센티널을 쓰는 것입니다.

```python
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

연산자 섹션에서는 `==`와 `is`를 반드시 분리해야 합니다. `==`는 값 동등성, `is`는 객체 동일성입니다.

| 비교 | 의미 | 사용 시점 |
|---|---|---|
| `a == b` | 값이 같은가 | 숫자/문자열/시퀀스 비교 |
| `a is b` | 같은 객체인가 | `None` 비교, 싱글턴 확인 |

실전 예시:

```pycon
>>> a = 256
>>> b = 256
>>> a is b
True
>>> c = 257
>>> d = 257
>>> c is d
False
```

작은 정수 캐싱 구현 세부에 기대어 `is`를 값 비교로 쓰면 안 됩니다.

간단한 성능 감각도 이 시점에서 같이 잡아 두면 좋습니다.

```python
import timeit

plus_cost = timeit.timeit('x + 1', setup='x = 10', number=5_000_000)
inplace_cost = timeit.timeit('x += 1', setup='x = 10', number=5_000_000)
print(plus_cost, inplace_cost)
```

예시 출력:

```text
0.129842851
0.128991044
```

숫자 자체보다 중요한 것은 비교 실험 습관입니다. 감으로 최적화하지 말고, 작은 코드라도 `timeit`으로 검증하는 습관을 초반에 들이면 이후 자료구조 선택(리스트/셋/딕셔너리)에서 훨씬 정확한 판단을 하게 됩니다.

마지막으로 CPython 내부를 한 번 더 보겠습니다.

```python
import sys

name = 'python'
print(sys.getrefcount(name))
alias = name
print(sys.getrefcount(name))
del alias
print(sys.getrefcount(name))
```

변수가 객체 자체가 아니라 참조를 붙잡는다는 감각이 이 출력에서 확실해집니다. 변수/타입/연산자 파트는 문법 암기보다 이 모델을 머리에 고정하는 것이 핵심입니다.

### 추가 실습: 숫자 타입과 부동소수점 오해 정리

연산자 파트에서 가장 흔한 오해는 부동소수점 비교입니다. 다음 출력은 의외처럼 보이지만 정상 동작입니다.

```pycon
>>> 0.1 + 0.2 == 0.3
False
>>> 0.1 + 0.2
0.30000000000000004
```

정밀 비교가 필요하면 `math.isclose`를 기본값으로 사용합니다.

```python
import math
print(math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-9))
```

정수/실수/불리언의 상속 관계도 함께 기억하면 연산 버그를 줄일 수 있습니다.

```pycon
>>> isinstance(True, int)
True
>>> True + True
2
```

불리언이 정수의 하위 타입이라는 사실을 모르면 집계 로직에서 의도치 않은 합산이 생깁니다.

비트 연산도 운영 코드에서 자주 쓰입니다.

```python
READ = 0b001
WRITE = 0b010
EXEC = 0b100
perm = READ | WRITE
print(bool(perm & READ), bool(perm & EXEC))
```

출력:

```text
True False
```

마지막으로 `decimal` 표준 라이브러리는 금액 계산에서 거의 필수입니다.

```python
from decimal import Decimal

price = Decimal('19.90')
qty = Decimal('3')
print(price * qty)
```

REPL에서 `float`와 `Decimal` 결과를 비교해 보면 타입 선택이 왜 중요한지 바로 체감할 수 있습니다.

### 부록: 로컬 실습 로그 템플릿

아래 템플릿은 학습 단계에서 직접 실험한 결과를 남길 때 유용합니다. 중요한 점은 "코드 + 실행 환경 + 출력"을 한 세트로 기록하는 것입니다. 이렇게 남긴 로그는 나중에 문제가 다시 발생했을 때 가장 신뢰할 수 있는 재현 자료가 됩니다.

```text
[환경]
python: 3.12.x
platform: macOS/Linux
venv: .venv

[실험]
목표: 동작 확인 또는 성능 비교
입력: 샘플 데이터 1,000건
실행 명령: python script.py

[출력]
성공/실패 여부
핵심 숫자(timeit, 처리 건수, 예외 메시지)
```

실무 코드 리뷰에서는 결과 숫자만 공유하는 경우가 많지만, 학습 단계에서는 중간 가정까지 함께 적는 편이 더 효과적입니다. 예를 들어 "셋 포함 검사가 빠를 것이다"라는 가정이 맞았는지, "f-string이 항상 더 읽기 쉽다"라는 판단이 팀 컨벤션과 맞는지까지 기록하면 다음 의사결정이 빨라집니다.

디버깅 기록도 같은 형식을 쓰면 좋습니다.

1) 증상: 어떤 입력에서 실패했는가
2) 가설: 어떤 조건문/자료구조/경로가 원인인가
3) 검증: `pdb`, `print`, `timeit`, 단위 테스트 중 무엇으로 확인했는가
4) 결론: 수정 전후 동작 차이가 무엇인가

이 습관은 초급 단계에서는 다소 느리게 느껴질 수 있습니다. 하지만 프로젝트 규모가 커질수록 "정확한 기록"이 가장 빠른 길이 됩니다. Python 문법을 익히는 것과 별개로, 실험을 재현 가능한 형태로 남기는 역량은 개발자로서의 성장 속도를 결정합니다.

### 보강 메모: 실수 줄이는 운영 습관

학습 단계에서 만든 코드를 실제 프로젝트에 옮길 때는 세 가지를 같이 점검하는 편이 좋습니다. 첫째, 입력 검증 경계가 함수 시작 지점에 있는지 확인합니다. 둘째, 실패 시 사용자에게 보여 줄 메시지와 로그 메시지를 분리합니다. 셋째, 성능 판단은 추측이 아니라 `timeit` 또는 샘플 벤치마크로 남깁니다.

간단한 템플릿은 다음과 같습니다.

```python
def safe_run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        # 학습 단계에서는 원인 관찰을 우선
        raise RuntimeError(f'실행 실패: {fn.__name__}') from e
```

또한 표준 라이브러리 문서를 읽을 때는 "모듈 개요 -> 대표 함수 3개 -> 예외 종류" 순서로 훑는 습관을 들이면 기억이 오래갑니다. 기능을 전부 외우는 것보다, 어떤 상황에서 어떤 모듈을 열어봐야 하는지 아는 것이 더 중요합니다.

짧게 정리하면, 변수 파트의 핵심은 이름 바인딩, 타입 파트의 핵심은 불변/가변 구분, 연산자 파트의 핵심은 비교 의미(`==` 대 `is`)를 헷갈리지 않는 것입니다. 이 세 가지를 기준으로 코드를 읽으면 대부분의 초급 버그를 빠르게 분류할 수 있습니다.

추가 팁: 실수/정수 혼합 계산, 불리언 암묵적 변환, 가변 객체 공유 참조는 초급 단계의 대표 함정입니다. 세 항목을 코드 리뷰 체크리스트에 넣어 두면 회귀 버그를 확실히 줄일 수 있습니다.

한 줄 결론: 값과 객체를 구분해 생각하면 실수 대부분이 사라집니다.

## 처음 질문으로 돌아가기

- **`total = total + items` 했더니 숫자에 문자열을 더했다는 `TypeError`가 납니다?**
  - 본문의 기준은 변수, 타입, 연산자를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`if user.age == "18":` 처럼 비교했더니 영원히 `False`가 나옵니다?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`0.1 + 0.2 == 0.3`이 `False`라서 결제 금액 검증이 실패합니다?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- **변수, 타입, 연산자 (현재 글)**
- 문자열과 포매팅 (예정)
- list, tuple, set, dict (예정)
- 제어 흐름: if, for, while, comprehension (예정)
- 함수와 인자: def, args, kwargs, default, lambda (예정)
- 모듈과 패키지: import, __init__, __name__ (예정)
- 파일 I/O와 예외 처리 (예정)
- 클래스와 객체: 데이터와 동작을 함께 묶기 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — `int`, `float`, `bool`, `None`, truthy/falsy, 시퀀스 공통 규칙의 기준 문서입니다.
- [Python 공식 문서 — Expressions](https://docs.python.org/3/reference/expressions.html) — 산술·비교·`is`·논리 연산의 문법과 평가 순서를 정확히 확인할 수 있습니다.
- [Python 튜토리얼 — Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html) — `0.1 + 0.2` 같은 부동소수 표현 오차를 설명하는 공식 입문 자료입니다.
- [Python 공식 문서 — `decimal`](https://docs.python.org/3/library/decimal.html) — 금액 계산처럼 정확한 십진 연산이 필요한 경우의 대안을 다룹니다.
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) — 타입 힌트가 런타임 강제가 아니라 정적 분석용 계약이라는 점의 출처입니다.
- [Python Data Model](https://docs.python.org/3/reference/datamodel.html) — 객체 정체성, 변경 가능성, 이름이 객체를 가리킨다는 모델을 더 깊게 보완합니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-101/ko)
Tags: variables, python-types, equality-vs-identity, floating-point, decimal, type-hints
