---
title: "바이브코딩을 위한 Python 기초 (2/10): 변수, 타입, 연산자"
series: python-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- Python
- AI코딩
- 변수
- 타입
- TypeError
- 부동소수점
seo_description: "바이브코딩 시대, AI가 만든 코드에서 TypeError가 터지는 이유를 이해하려면 Python 변수와 타입 모델을 알아야 합니다."
---

# 바이브코딩을 위한 Python 기초 (2/10): 변수, 타입, 연산자

Claude에게 "쇼핑몰 장바구니 총액 계산 함수 짜줘"라고 했더니 깔끔한 코드가 뚝딱 나왔습니다. 신나서 실행했는데 첫 줄부터 에러가 터집니다.

```
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

에러 메시지를 다시 AI에게 붙여넣었더니 이번엔 `int(quantity)` 변환을 추가해줬습니다. 고쳤더니 이제는 결제 금액이 미묘하게 틀립니다. 총액이 `10890.000000000002`처럼 나오는 겁니다. "부동소수점 오차니까 `round()`로 처리해"라고 AI가 말하는데, 뭔가 찜찜합니다.

이런 상황이 낯설지 않을 겁니다. 바이브코딩에서 AI는 코드를 잘 만들지만, 타입 불일치나 부동소수점 함정은 런타임에 데이터를 만나기 전까지 잡아내지 못할 때가 많습니다. 그 이유는 간단합니다. AI는 코드의 구조를 생성하지만, 실제 입력 데이터가 어떤 타입으로 들어오는지는 실행 환경을 모르기 때문입니다.

여기서 바이브코더의 핵심 역량이 드러납니다. AI가 만든 코드의 에러 메시지를 읽고, 어느 라인에서 어떤 타입 문제가 발생했는지 파악하고, AI에게 더 정확한 지시를 내릴 수 있어야 합니다. 그러려면 Python이 변수와 타입을 어떻게 다루는지 최소한의 모델 하나는 머릿속에 있어야 합니다.

> Python에서 변수는 상자가 아니라 객체에 붙는 이름표입니다. 이 모델 하나가 TypeError의 절반을 설명합니다.

---

## 이 글에서 다룰 문제

- AI가 만든 코드에서 `TypeError: unsupported operand type(s) for +: 'int' and 'str'`이 나는 이유는?
- `if user.age == "18":` 이 왜 항상 `False`가 되는지 AI에게 어떻게 설명하면 될까?
- `0.1 + 0.2 == 0.3`이 `False`라는 사실을 모르면 결제 코드가 어떻게 망가지나?
- AI가 생성한 함수에서 `def f(items=[]):` 패턴이 보이면 왜 즉시 의심해야 하나?
- 타입 힌트가 있는 코드와 없는 코드 중 AI 수정 요청 시 어느 쪽이 더 빠르게 개선되나?

---

## AI가 생성한 코드를 읽으려면 이름표 모델이 필요합니다

Python에서 `x = 42`를 실행하면 정수 객체 `42`가 메모리에 만들어지고, `x`라는 이름표가 그 객체를 가리킵니다. 이어서 `y = x`를 하면 `y`라는 이름표가 추가될 뿐, 새 객체가 생기지 않습니다. 두 이름표가 같은 객체를 가리킵니다.

이 모델을 모르면 AI가 생성한 다음 코드가 왜 예상과 다르게 동작하는지 이해하기 어렵습니다.

```python
# AI가 생성한 코드
def add_tag(item, tags=[]):
    tags.append(item)
    return tags

print(add_tag("python"))   # ['python']
print(add_tag("AI"))       # 예상: ['AI'] / 실제: ['python', 'AI']
```

`tags=[]`는 함수가 정의되는 시점에 딱 한 번 만들어집니다. 호출할 때마다 새 리스트가 생기는 게 아닙니다. 이름표 모델로 보면, `tags`라는 이름표가 함수 정의 시점에 빈 리스트 하나를 가리키고, 이후 모든 호출이 그 같은 리스트를 계속 가리킵니다.

AI에게 이 문제를 고치라고 할 때 정확히 이렇게 말할 수 있습니다: "mutable default argument 패턴이라 None sentinel로 바꿔줘."

## Python의 다섯 가지 기본 타입과 TypeError의 관계

AI가 생성한 코드에서 TypeError가 터지는 가장 흔한 원인은 타입 불일치입니다. Python의 다섯 가지 기본 타입을 알면 에러 메시지를 읽는 속도가 빨라집니다.

| 타입 | 예시 | 바이브코딩에서 자주 만나는 함정 |
| --- | --- | --- |
| `int` | `42`, `1_000_000` | 사용자 입력은 항상 `str`로 들어옵니다 |
| `float` | `3.14`, `1e-9` | `0.1 + 0.2 != 0.3`. 금액 계산에는 `Decimal` |
| `str` | `"hello"` | 숫자처럼 보여도 `"25"`는 `str`입니다 |
| `bool` | `True`, `False` | `int` 하위 타입. `True + True == 2` |
| `None` | `None` | "없음"을 표현. `is None`으로 비교 |

`TypeError: unsupported operand type(s) for +: 'int' and 'str'`이 나면 AI에게 이렇게 프롬프트를 보낼 수 있습니다: "quantity 변수가 str로 들어오는 것 같아. 함수 시작 부분에 명시적 타입 변환과 입력 검증을 추가해줘."

## 연산자: AI 코드에서 주의할 세 가지 패턴

**정수 나눗셈 vs 실수 나눗셈**

```python
7 / 2     # 3.5 — 항상 float 반환
7 // 2    # 3   — 정수 나눗셈 (바닥 나눗셈)
```

AI가 나눗셈 로직을 생성할 때 `/`와 `//`를 혼동해서 쓰는 경우가 있습니다. 페이지 분할, 인덱스 계산, 비율 계산에서 `/` 대신 `//`가 필요한 상황을 체크하세요.

**논리 연산자의 단락 평가**

```python
name = user.name or "게스트"          # user.name이 falsy면 "게스트"
config = override or default_config
```

AI가 이 패턴을 자주 씁니다. `or`의 왼쪽이 `0`이나 `""`처럼 falsy이면 의도와 다르게 오른쪽 값이 반환될 수 있습니다.

**비교 연산자 체이닝**

```python
0 <= x < 10    # Python에서 유효한 표현식
```

다른 언어 출신이라면 이 표현이 낯설 수 있습니다. AI가 이 패턴을 생성하면 `x >= 0 and x < 10`과 동일하다고 이해하면 됩니다.

## Before / After

**Before — AI가 처음 생성한 코드**

```python
def calc_total(quantity, unit_price, discount):
    return quantity * unit_price * (1 - discount)
```

인자 이름만 봐서는 타입을 알 수 없습니다. `quantity`가 문자열로 들어오면 TypeError, `discount`가 퍼센트 정수로 들어오면 계산이 완전히 틀립니다. AI에게 수정을 요청해도 "어떤 타입으로 들어오는지"를 모르면 엉뚱한 방향으로 고칩니다.

**After — 타입 힌트 추가 후**

```python
def calc_total(quantity: int, unit_price: float, discount_rate: float) -> float:
    """
    Args:
        quantity: 수량 (양의 정수)
        unit_price: 단가 (원)
        discount_rate: 할인율 (0.0 ~ 1.0, 예: 10% → 0.1)
    """
    return quantity * unit_price * (1 - discount_rate)
```

타입 힌트와 독스트링이 있으면 AI가 이 함수를 수정할 때 훨씬 정확하게 맥락을 파악합니다. 다음에 "세금 계산 추가해줘"라고 할 때도 `discount_rate`의 단위(0~1 범위)를 지켜서 `tax_rate: float`를 추가합니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 패턴 | AI가 생성한 코드 예시 | 문제 | 올바른 패턴 |
| --- | --- | --- | --- |
| 사용자 입력 그대로 사용 | `age = input("나이: ")` → `if age > 18` | `str > int` TypeError | `age = int(input("나이: "))` |
| 부동소수 == 비교 | `total == 0.3` | 부동소수 오차로 항상 틀릴 수 있음 | `math.isclose(total, 0.3)` |
| mutable 기본 인자 | `def f(items=[])` | 호출 간 상태 공유 | `def f(items=None)` + 내부 초기화 |
| `is`로 값 비교 | `if name is "admin"` | 구현 세부에 의존 | `if name == "admin"` |
| 금액에 float 사용 | `price = 9900.0` | 부동소수 오차 누적 | `from decimal import Decimal` |

## AI에게 이 주제 관련 질문하는 팁

**타입 에러를 고칠 때**

나쁜 프롬프트: "에러 고쳐줘"

좋은 프롬프트: "TypeError: unsupported operand type(s) for +: 'int' and 'str' 에러가 나. `quantity` 변수가 웹 폼에서 문자열로 들어오는데, 함수 시작에서 int로 변환하고 변환 실패 시 ValueError를 발생시키도록 해줘."

**부동소수점 금액 문제**

나쁜 프롬프트: "소수점 오류 고쳐줘"

좋은 프롬프트: "결제 금액 계산에 float를 쓰고 있는데 decimal.Decimal로 바꿔줘. 입력이 문자열 '9900'이나 정수 9900 형태로 들어올 수 있어."

**타입 힌트 추가 요청**

좋은 프롬프트: "이 모듈의 모든 public 함수에 타입 힌트 추가해줘. 반환 타입도 포함해서. mypy strict 모드 통과할 수 있게."

## 운영 체크리스트

- [ ] AI가 생성한 함수에 `def f(x=[]):` 패턴이 있으면 즉시 `None` sentinel 패턴으로 수정 요청
- [ ] 사용자 입력(`input()`, 웹 폼, CSV)을 받는 변수는 명시적 타입 변환 코드가 있는지 확인
- [ ] 금액 계산 코드에 `float` 대신 `Decimal` 사용 여부 확인
- [ ] 부동소수 비교에 `==` 대신 `math.isclose()` 사용 여부 확인
- [ ] `is`를 `None`, `True`, `False` 외의 값 비교에 사용하고 있지 않은지 확인
- [ ] 새로운 함수를 AI에게 만들도록 요청할 때 타입 힌트 포함 요구

## 처음 질문으로 돌아가기

**AI 코드에서 `TypeError: 'int' and 'str'`이 나는 이유는?**
Python은 타입이 다른 객체 간 연산을 자동으로 변환하지 않습니다. 사용자 입력, API 응답, CSV 읽기는 항상 문자열로 들어옵니다. AI는 이 사실을 항상 기억하지 못하므로 입력 경계에서의 명시적 타입 변환 코드를 직접 확인해야 합니다.

**`if user.age == "18":` 이 항상 `False`인 이유는?**
`user.age`가 정수 `18`이고 비교 대상이 문자열 `"18"`이면, Python은 다른 타입 간 `==` 비교에서 `False`를 반환합니다. AI에게 "age 필드가 DB에서 int로 오는지 str로 오는지 확인하고 타입을 통일해줘"라고 요청하세요.

**`0.1 + 0.2 == 0.3`이 `False`인 이유는?**
IEEE 754 부동소수점 표현의 한계입니다. 금액처럼 정확성이 중요한 계산에는 `Decimal`을, 일반 부동소수 비교에는 `math.isclose()`를 씁니다.

**AI의 `def f(items=[]):` 패턴을 즉시 의심해야 하는 이유는?**
기본 인자는 함수 정의 시 한 번만 평가됩니다. 리스트처럼 가변 객체를 기본값으로 쓰면 호출 간에 상태가 공유되어 예상치 못한 누적 버그가 생깁니다.

**타입 힌트가 AI 수정 요청 품질에 미치는 영향은?**
타입 힌트는 AI에게 각 변수의 의도를 명확히 전달하는 계약서입니다. 타입 힌트가 있는 코드는 AI가 수정할 때 타입 불일치를 훨씬 정확하게 파악합니다.

## 정리

바이브코딩에서 변수와 타입을 아는 것은 Python을 완전히 배우기 위해서가 아닙니다. AI가 생성한 코드에서 TypeError 메시지를 읽고, 어느 변수가 어떤 타입이어야 하는지 AI에게 정확히 지시하기 위해서입니다. "이름표 모델"과 다섯 가지 기본 타입을 머릿속에 두면, AI와의 대화에서 에러의 원인을 짚어내는 속도가 눈에 띄게 달라집니다.
