---
title: "바이브코딩을 위한 Python 기초 (6/10): AI가 만든 함수 시그니처 읽고 수정하기"
series: python-101
episode: 6
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
- 함수시그니처
- args-kwargs
- 타입힌트
seo_description: "바이브코딩 시대, AI가 만든 함수 시그니처를 읽고 수정하는 법. def, args, kwargs, default, lambda 완전 정리"
---

# 바이브코딩을 위한 Python 기초 (6/10): AI가 만든 함수 시그니처 읽고 수정하기

AI에게 "CSV 파일 읽어서 통계 내는 함수 만들어줘"라고 했더니 이런 코드가 돌아왔습니다.

```python
def process_csv(
    filepath: str,
    /,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
    skip_header: bool = True,
    aggregation: str = "mean"
) -> dict:
    ...
```

이걸 보고 바로 쓸 수 있나요? `filepath` 뒤에 있는 `/`는 뭔지, `*` 이후에 나오는 인자들은 왜 따로 분리돼 있는지, `-> dict`는 무슨 뜻인지 모르면 이 함수를 제대로 호출할 수 없습니다.

더 자주 일어나는 상황은 이겁니다. AI가 만든 함수를 그냥 복붙했는데 호출할 때 이런 에러가 납니다.

```
TypeError: process_csv() takes 1 positional argument but 2 were given
```

왜 이런 에러가 나는지 모르면 AI에게 다시 물어봐야 합니다. 물어봐도 AI가 설명해주는 걸 이해 못하면 또 막힙니다. 바이브코딩이 막히는 지점이 정확히 여기입니다.

함수 시그니처를 읽는 눈이 생기면 AI가 만든 코드를 그냥 복붙하는 게 아니라, 내 상황에 맞게 조정할 수 있게 됩니다. 기본값을 바꾸거나, 인자를 하나 더 추가하거나, 타입 힌트를 추가하거나. 이게 바이브코딩의 핵심 역량입니다.

> AI가 만든 함수는 "계약서"입니다. 시그니처를 읽을 줄 알아야 계약 내용을 이해하고 수정할 수 있습니다.

---

## 이 글에서 다룰 문제

- AI가 만든 함수에 `/`와 `*`가 있는데, 이게 뭘 뜻하는 건가요?
- `*args`와 `**kwargs`가 있는 함수는 어떻게 호출해야 하나요?
- 기본값이 `[]`나 `{}`로 돼 있는 함수, 그냥 써도 되나요?
- AI가 `return`을 빠뜨린 것 같은데 어떻게 확인하나요?
- 함수에 새 인자를 추가할 때 기존 호출 코드를 안 깨는 방법이 있나요?

---

## AI 코드를 읽으려면 이것을 알아야

### 시그니처는 "호출 계약서"다

함수 시그니처는 이 함수를 쓰는 사람이 무엇을 줘야 하고, 무엇을 돌려받는지를 명시한 계약입니다. AI는 이 계약을 다양한 방식으로 작성하는데, 각 부분이 뭘 의미하는지 읽을 수 있어야 합니다.

```python
def make_greeting(name: str, *, lang: str = "en", formal: bool = False) -> str:
```

이걸 분해하면:
- `name: str` — 이름을 문자열로 받는다 (필수)
- `*` — 이 뒤로는 반드시 이름을 붙여서 호출해야 한다
- `lang: str = "en"` — 언어 코드, 기본값은 영어
- `formal: bool = False` — 격식체 여부, 기본값은 비격식
- `-> str` — 문자열을 돌려준다

### 다섯 가지 인자 형태

AI가 만드는 함수에서 보이는 인자 형태는 다섯 가지입니다.

**1. 일반 인자 (positional/keyword 모두 가능)**

```python
def greet(name, message):
    return f"{message}, {name}"

greet("ada", "hello")               # positional
greet(name="ada", message="hello")  # keyword — 둘 다 됩니다
```

**2. 기본값 인자**

```python
def power(base, exp=2):
    return base ** exp

power(3)       # exp는 2로 자동 적용
power(3, 3)    # exp를 3으로 직접 지정
```

**3. `*args` — 개수 모를 때**

```python
def add_all(*args):
    return sum(args)

add_all(1, 2, 3, 4)  # (1, 2, 3, 4) 튜플로 모임
```

**4. `**kwargs` — 이름 모를 때**

```python
def show_info(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")

show_info(name="ada", role="admin")
```

**5. keyword-only (`*` 뒤) 와 positional-only (`/` 앞)**

```python
def write(path, /, *, mode="w", encoding="utf-8"):
    ...

# path는 무조건 위치로, mode와 encoding은 무조건 이름으로
write("a.txt", mode="w")           # OK
write(path="a.txt")                # TypeError! path는 positional-only
write("a.txt", "w")                # TypeError! mode는 keyword-only
```

### AI가 `**kwargs`를 남긴 이유

AI는 종종 이런 패턴을 씁니다.

```python
def with_logging(fn):
    def wrapper(*args, **kwargs):
        print("call", fn.__name__)
        result = fn(*args, **kwargs)
        print("done")
        return result
    return wrapper
```

`*args, **kwargs`는 "이 함수를 감싸는 래퍼"에서 가장 자주 쓰입니다. 감싸는 대상 함수가 어떤 인자를 받든 그대로 통과시켜야 하기 때문입니다. 이 패턴을 보면 "아, 이건 데코레이터구나"라고 읽으면 됩니다.

### `return`이 없으면 `None`이 나온다

AI가 종종 `return`을 빠뜨리는 경우가 있습니다.

```python
def calculate(x, y):
    result = x * y + 10
    # return을 빠뜨림!
```

이 함수를 호출하면 `None`이 돌아옵니다. `result = calculate(3, 4)`를 출력해봤더니 `None`이 나온다면 함수 마지막에 `return`이 있는지 확인하세요.

---

## Before / After

### AI가 처음 만들어준 함수

```python
# AI 초안 — 인자 의미가 불명확
def make_report(data, fmt, enc, verbose, max_rows):
    ...

make_report(records, "csv", "utf-8", True, 1000)
```

`True`가 무엇인지, 다섯 번째 인자가 뭔지 시그니처 없이는 알 수 없습니다. 나중에 내가 수정하거나 AI에게 변경 요청을 할 때도 헷갈립니다.

### 바이브코딩으로 개선한 버전

```python
# 개선 — keyword-only와 기본값으로 의도 표현
def make_report(
    data: list,
    *,
    fmt: str = "csv",
    encoding: str = "utf-8",
    verbose: bool = False,
    max_rows: int = 1000
) -> str:
    ...

# 이제 호출부가 자기 설명을 합니다
make_report(records, fmt="csv", verbose=True)
make_report(records)  # 기본값으로 충분할 때
```

AI에게 이렇게 요청하면 됩니다: "이 함수 시그니처를 keyword-only 인자와 타입 힌트를 써서 다시 작성해줘. 핵심 입력 하나만 positional로 받고 나머지 옵션은 다 keyword-only로 만들어줘."

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `def f(items=[]):` | 기본값 리스트가 호출 간 공유돼 누적됨 | `def f(items=None):` 후 `items = items if items is not None else []` |
| `return` 누락 | 함수가 항상 `None`을 반환 | 함수 마지막 줄에 `return 결과값` 확인 |
| `f(1, a=2)` 혼용 오류 | positional이 이미 `a`에 묶였는데 keyword로 또 넘김 | 시그니처 보고 어떤 인자인지 확인 |
| `**kwargs` 남용 | IDE 자동완성, 타입 검사 불가 | 래퍼 이외에는 명시적 이름 사용 |
| 본문 두 줄짜리 `lambda` | 가독성 저하, 디버깅 어려움 | `def`로 빼서 이름 붙이기 |

---

## AI에게 이 주제 관련 질문하는 팁

**시그니처 설명 요청:**
"이 함수의 `/`와 `*` 구분자가 무슨 의미인지 설명해줘. 어떻게 호출해야 하는지 예시도 보여줘."

**개선 요청:**
"이 함수에 새 옵션 파라미터를 추가해야 하는데, 기존 코드가 깨지지 않게 keyword-only 인자로 추가해줘."

**버그 확인:**
"이 함수를 호출했더니 `None`이 나와. `return`이 제대로 있는지 확인해줘."

**기본값 문제:**
"이 함수에 mutable 기본값 문제가 있는지 확인하고, 있으면 안전한 패턴으로 바꿔줘."

---

## 운영 체크리스트

- [ ] AI가 만든 함수 시그니처에서 `/`와 `*`가 있으면 positional-only/keyword-only 구분을 읽을 수 있다
- [ ] `*args, **kwargs` 패턴이 보이면 "래퍼 함수"라는 걸 인식할 수 있다
- [ ] 함수 결과가 `None`일 때 `return` 누락을 먼저 의심한다
- [ ] 기본값이 `[]`, `{}`, `set()` 같은 mutable 타입이면 위험 신호로 인식한다
- [ ] 새 옵션 인자 추가 시 `*` 뒤 keyword-only로 추가해 기존 호출 코드를 지킨다
- [ ] 타입 힌트(`-> str`, `param: int`)가 있으면 그걸 "계약서"로 읽는다

---

## 처음 질문으로 돌아가기

**`/`와 `*`가 있는 함수는 어떻게 호출하나요?**
`/` 앞의 인자는 위치로만, `*` 뒤의 인자는 이름으로만 넘겨야 합니다. `process_csv("data.csv", delimiter=";")` 처럼 작성하면 됩니다.

**`*args, **kwargs` 함수는 어떻게 호출하나요?**
원래 함수가 받던 것과 똑같이 호출하면 됩니다. 래퍼 함수는 그걸 그대로 통과시킵니다.

**기본값이 `[]`면 그냥 써도 되나요?**
안 됩니다. 호출마다 같은 리스트가 재사용돼 값이 누적됩니다. AI에게 `None` 패턴으로 수정해달라고 요청하세요.

**`return`이 빠진 것 같은데 어떻게 확인하나요?**
함수 결과를 변수에 담아 출력해보세요. `None`이 나오면 `return`을 찾아보면 됩니다.

**인자를 추가할 때 기존 코드를 안 깨는 방법은?**
`*` 뒤에 기본값이 있는 keyword-only 인자로 추가하면 기존 호출 코드는 전혀 건드리지 않아도 됩니다.

---

## 정리

AI가 만들어주는 함수 시그니처는 다양한 패턴을 담고 있습니다. `/`, `*`, `*args`, `**kwargs`, 타입 힌트, 기본값. 이것들을 읽는 눈이 생기면 "AI가 왜 이렇게 짰지?"라는 질문에 스스로 답할 수 있게 됩니다.

특히 실수하기 쉬운 mutable 기본값 문제와 `return` 누락은 AI도 자주 만들어내는 버그입니다. 이걸 잡아내는 것도 바이브코더의 실력입니다.

다음 편에서는 AI가 import한 모듈이 뭔지, 내 프로젝트에 어떻게 넣는지를 다룹니다.
