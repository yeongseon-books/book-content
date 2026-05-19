---
series: programming-languages-101
episode: 4
title: 스코프와 바인딩
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
  - Scope
  - Binding
  - Lexical
  - Dynamic
seo_description: 이름을 값에 연결하는 바인딩과 스코프 규칙을 LEGB 사례로 풀이하고, 렉시컬 스코프가 왜 코드 가독성과 유지보수성에 중요한지 정리합니다.
last_reviewed: '2026-05-15'
---

# 스코프와 바인딩

같은 변수 이름이 함수 안팎에서 서로 다른 값을 가리키는데도 프로그램은 대체로 예측 가능하게 동작합니다. 이 당연해 보이는 일이 사실은 언어 설계에서 아주 중요한 규칙 위에 서 있습니다.

이 글은 Programming Languages 101 시리즈의 네 번째 글입니다.

이 글에서는 이름에 값을 붙이는 바인딩과, 그 바인딩이 보이는 범위인 스코프를 함께 보겠습니다. 특히 현대 언어 대부분이 택한 렉시컬 스코프가 왜 읽기 좋은 코드를 만들고, 어디서 흔히 헷갈리는지도 같이 정리하겠습니다.

## 이 글에서 다룰 문제

- 스코프와 바인딩은 정확히 무엇이 다를까요?
- 렉시컬 스코프와 동적 스코프는 결과를 어떻게 바꿀까요?
- 같은 이름을 안쪽에서 다시 쓰는 섀도잉은 왜 위험할까요?
- Python의 LEGB 규칙은 어떤 순서로 이름을 찾을까요?

> 바인딩은 이름을 값에 연결하는 행위이고, 스코프는 그 연결이 보이는 범위입니다. 현대 언어가 렉시컬 스코프를 택한 이유는 소스 코드만 읽어도 값의 출처를 추적할 수 있게 만들기 위해서입니다.

## 왜 중요한가

“왜 이 변수는 갱신되지 않았지?”, “왜 갑자기 NameError가 나지?” 같은 질문은 스코프를 모르면 미스터리처럼 보입니다. 하지만 스코프를 이해하면 함수, 모듈, 클로저가 모두 같은 규칙의 다른 표현이라는 사실이 보입니다.

## 핵심 개념 한눈에 보기

![이름을 찾을 때 안쪽에서 바깥쪽으로 올라가는 LEGB 순서](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/04/04-01-concept-at-a-glance.ko.png)

*이름을 찾을 때 안쪽에서 바깥쪽으로 올라가는 LEGB 순서*

Python의 LEGB 규칙은 안쪽에서 바깥쪽으로 이름을 찾는 순서입니다. 가장 먼저 발견한 바인딩이 이깁니다. 이 단순한 규칙 하나가 함수 동작의 대부분을 설명해 줍니다.

## 먼저 알아둘 용어

- 바인딩: 이름에 값을 연결하는 일입니다.
- 스코프: 그 연결이 보이는 코드 범위입니다.
- 렉시컬 스코프: 코드가 어디에 쓰였는지를 기준으로 스코프를 정합니다.
- 동적 스코프: 실행 중 호출 경로를 따라 스코프를 정합니다.
- 섀도잉: 안쪽 스코프가 바깥쪽의 같은 이름을 가리는 현상입니다.

## 먼저 보는 예시

### 전역에 기대는 코드

```python
LIMIT = 10

def is_ok(x):
    return x < LIMIT

def main():
    LIMIT = 5      # a new local — has no effect on is_ok
    print(is_ok(7))  # True
```

`main` 안의 `LIMIT`은 `is_ok`에서 보이지 않습니다. `is_ok`는 자신이 정의된 위치를 기준으로 이름을 찾기 때문입니다. 이것이 렉시컬 스코프입니다.

### 의존성을 드러내는 코드

```python
def is_ok(x, limit=10):
    return x < limit

print(is_ok(7, limit=5))  # False
```

숨은 의존성을 매개변수로 끌어올리면 코드가 훨씬 읽기 쉬워집니다. 테스트도 쉬워집니다.

## 꼭 알아야 할 네 가지 예제

### 1단계 — 이름 탐색 순서 보기

```python
# 1_legb.py
x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)
    inner()
    print(x)

outer()
print(x)
# local / enclosing / global
```

같은 이름이라도 가장 안쪽 바인딩부터 차례로 찾습니다. 이름 하나가 항상 값 하나만 뜻하는 것은 아닙니다.

### 2단계 — 지역 변수 바인딩 오류의 실제 원인

```python
# 2_unbound.py
x = 1
def f():
    print(x)   # UnboundLocalError
    x = 2

f()
```

함수 안에 `x = 2`가 등장하는 순간 Python은 함수 전체에서 `x`를 지역 변수로 봅니다. 그래서 `print(x)`는 아직 바인딩되지 않은 지역 변수를 읽으려다 실패합니다.

### 3단계 — 바깥 함수 값을 갱신할 때

```python
# 3_nonlocal.py
def make_counter():
    n = 0
    def step():
        nonlocal n
        n += 1
        return n
    return step

c = make_counter()
print(c(), c(), c())  # 1 2 3
```

`nonlocal` 없이 `n += 1`을 쓰면 새 지역 변수를 만들려다 같은 오류가 납니다. `nonlocal`은 의도적으로 바깥 스코프를 갱신하겠다는 표시입니다.

### 4단계 — 렉시컬 스코프와 동적 스코프 비교

```python
# 4_lexical.py
y = "outer"
def show():
    print(y)

def caller():
    y = "inner"
    show()   # lexical scope → prints 'outer'

caller()
```

동적 스코프였다면 `show()`는 호출한 쪽의 `y`를 보고 `inner`를 출력했을 것입니다. 현대 언어가 렉시컬 스코프를 선호하는 이유는 소스만 읽어도 값의 출처를 알 수 있기 때문입니다.

### 5단계 — 섀도잉의 함정

```python
# 5_shadow.py
def total(items):
    sum = 0   # shadowed the built-in sum
    for x in items:
        sum += x
    return sum  # works, but you cannot call sum(...) in this function anymore
```

짧은 함수라서 넘어가기 쉽지만, 내장 함수 이름을 가려 버리면 나중에 원래 `sum(...)`을 쓰고 싶을 때 곧바로 문제가 됩니다.

## 이 코드에서 먼저 볼 점

- 이름이 어떤 값을 가리키는지는 스코프 규칙이 결정합니다.
- 함수 안의 대입 한 줄이 그 함수 전체의 이름 해석 방식을 바꿀 수 있습니다.
- `nonlocal`과 `global`은 흔히 쓰는 도구가 아니라, 의도적인 갱신을 표시하는 표식입니다.
- 렉시컬 스코프의 강점은 “읽어서 알 수 있다”는 점입니다.

## 자주 하는 실수

1. 함수끼리 상태를 공유하려고 전역 변수를 늘립니다. 변경 출처가 흐려져 디버깅이 어려워집니다.
2. `list`, `dict`, `sum` 같은 내장 이름을 변수명으로 씁니다. 나중에 큰 혼란을 부릅니다.
3. `global`을 너무 쉽게 씁니다. 매개변수와 반환값으로 드러내는 편이 거의 항상 낫습니다.
4. 함수 중간에서 이름을 다시 대입해 UnboundLocalError를 만듭니다.
5. 현대 언어에서 동적 스코프처럼 동작할 것이라고 착각합니다.

## 실무에서는 이렇게 본다

좋은 코드는 “이 이름은 어디서 왔지?”라는 질문에 거의 즉시 답할 수 있어야 합니다. 큰 함수를 나누고, 숨은 의존성을 매개변수로 끌어올리고, 모듈 변수 갱신을 한곳에 모으는 습관은 모두 렉시컬 스코프의 장점을 극대화하는 방법입니다.

테스트도 같은 원리로 쉬워집니다. 전역 상태에 기대는 함수는 단위 테스트가 어렵고, 필요한 값을 매개변수로 받는 함수는 테스트가 단순해집니다. 스코프 규칙을 이해하는 일은 결국 읽기 쉬운 코드와 테스트 가능한 코드를 만드는 일과 맞닿아 있습니다.

## 체크리스트

- [ ] LEGB 네 단계를 말할 수 있는가?
- [ ] UnboundLocalError가 왜 생기는지 한 줄로 설명할 수 있는가?
- [ ] `nonlocal`과 `global`을 언제 써야 하는지 아는가?
- [ ] 숨은 의존성을 매개변수로 끌어올린 경험이 있는가?
- [ ] 렉시컬 스코프의 가독성 이점을 한 문장으로 설명할 수 있는가?

## 연습 문제

1. `sum`을 가리는 예제를 고쳐 함수 안에서 원래 `sum(...)`도 쓸 수 있게 바꿔 보세요.
2. 모듈 전역 변수 하나에 의존하는 함수를 골라, 그 값을 매개변수로 받도록 다시 작성해 보세요.
3. 렉시컬 스코프와 동적 스코프의 차이로 결과가 달라지는 상상 코드 한 조각을 직접 만들어 보세요.

## 정리

스코프는 이름이 보이는 범위이고, 바인딩은 이름에 값을 붙이는 행위입니다. 렉시컬 스코프를 제대로 이해하면 다음 글의 클로저는 훨씬 자연스럽게 이어집니다. 클로저는 결국 렉시컬 스코프와 일급 함수가 만나서 생기는 결과이기 때문입니다.

<!-- toc:begin -->
- [프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [구문과 의미](./02-syntax-and-semantics.md)
- [타입 시스템](./03-type-system.md)
- **스코프와 바인딩 (현재 글)**
- 함수와 클로저 (예정)
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)
<!-- toc:end -->

## 참고 자료

- [Python Language Reference — Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
- [Structure and Interpretation of Computer Programs — Chapter 3](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-21.html)
- [Programming Language Pragmatics (Scott) — Chapter 3 Names, Scopes, and Bindings](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)
- [MDN — Scope](https://developer.mozilla.org/en-US/docs/Glossary/Scope)

Tags: Computer Science, Programming Languages, Scope, Binding, Lexical, Dynamic
