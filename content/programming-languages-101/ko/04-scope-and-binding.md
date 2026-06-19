---
series: programming-languages-101
episode: 4
title: "Programming Languages 101 (4/10): 스코프와 바인딩"
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

# Programming Languages 101 (4/10): 스코프와 바인딩

같은 변수 이름이 함수 안팎에서 서로 다른 값을 가리키는데도 프로그램은 대체로 예측 가능하게 동작합니다. 이 당연해 보이는 일이 사실은 언어 설계에서 아주 중요한 규칙 위에 서 있습니다.

이 글은 Programming Languages 101 시리즈의 4번째 글입니다.

이 글에서는 이름에 값을 붙이는 바인딩과, 그 바인딩이 보이는 범위인 스코프를 함께 보겠습니다. 특히 현대 언어 대부분이 택한 렉시컬 스코프가 왜 읽기 좋은 코드를 만들고, 어디서 흔히 헷갈리는지도 같이 정리하겠습니다.

![Programming Languages 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/04/04-01-concept-at-a-glance.ko.png)
*Programming Languages 101 4장 흐름 개요*

> '이 변수 이름이 가리키는 값은 어디서 결정되는가'라는 질문 하나가 lexical scope·dynamic scope·closure·hoisting을 모두 같은 그림으로 묶어 줍니다 — JavaScript의 `this`나 Python의 late binding은 이 한 모델 위에서만 일관되게 설명됩니다.

## 이 글에서 다룰 문제

- 스코프와 바인딩은 정확히 무엇이 다를까요?
- 렉시컬 스코프와 동적 스코프는 결과를 어떻게 바꿀까요?
- 같은 이름을 안쪽에서 다시 쓰는 섀도잉은 왜 위험할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

"왜 이 변수는 갱신되지 않았지?", "왜 갑자기 NameError가 나지?" 같은 질문은 스코프를 모르면 미스터리처럼 보입니다. 하지만 스코프를 이해하면 함수, 모듈, 클로저가 모두 같은 규칙의 다른 표현이라는 사실이 보입니다.

## 먼저 알아둘 용어

- **바인딩**: 이름에 값을 연결하는 일입니다.
- **스코프**: 그 연결이 보이는 코드 범위입니다.
- **렉시컬 스코프**: 코드가 어디에 쓰였는지를 기준으로 스코프를 정합니다.
- **동적 스코프**: 실행 중 호출 경로를 따라 스코프를 정합니다.
- **섀도잉**: 안쪽 스코프가 바깥쪽의 같은 이름을 가리는 현상입니다.

## Python의 LEGB 규칙

Python의 이름 탐색 순서는 LEGB로 요약됩니다.

```text
L (Local)     — 현재 함수 안
    |
E (Enclosing) — 바깥 함수 (중첩 함수일 때)
    |
G (Global)    — 모듈 최상위
    |
B (Built-in)  — Python 내장 이름 (len, sum, print...)
```

안쪽에서 바깥쪽으로 순서대로 찾습니다. 가장 먼저 발견한 바인딩이 이깁니다. 이 단순한 규칙 하나가 함수 동작의 대부분을 설명해 줍니다.

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
# local
# enclosing
# global
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

## 언어별 스코프 규칙 비교

Python의 LEGB와 JavaScript의 호이스팅, Go의 블록 스코프는 같은 개념을 다르게 구현합니다.

```python
# Python: 함수 스코프
def f():
    x = 1
    if True:
        x = 2      # 같은 x를 수정
    print(x)       # 2

# Python: 클로저에서 루프 변수 캡처 함정
fns = [lambda: i for i in range(3)]
print([f() for f in fns])  # [2, 2, 2] — 모두 마지막 i를 참조
```

```javascript
// JavaScript: var는 함수 스코프 + 호이스팅
function f() {
    console.log(x);   // undefined (호이스팅으로 선언은 됨, 값은 없음)
    var x = 1;
}

// let/const는 블록 스코프
function g() {
    // console.log(y);  // ReferenceError: 선언 전 접근 불가
    let y = 1;
    console.log(y);    // 1
}

// 루프 클로저: var vs let
const fns_var = [];
for (var i = 0; i < 3; i++) {
    fns_var.push(() => i);
}
console.log(fns_var.map(f => f()));  // [3, 3, 3] — var는 공유

const fns_let = [];
for (let i = 0; i < 3; i++) {
    fns_let.push(() => i);
}
console.log(fns_let.map(f => f()));  // [0, 1, 2] — let은 반복마다 새 바인딩
```

```go
// Go: 블록 스코프, 선언-전-사용 금지
func f() {
    x := 1
    if true {
        x := 2      // 새 x (섀도잉)
        fmt.Println(x)  // 2
    }
    fmt.Println(x)  // 1
}
```

JavaScript의 `var`와 `let`의 차이는 스코프 규칙이 코드 동작에 얼마나 큰 영향을 주는지를 가장 극적으로 보여 주는 사례입니다.

## 이 코드에서 먼저 볼 점

- 이름이 어떤 값을 가리키는지는 스코프 규칙이 결정합니다.
- 함수 안의 대입 한 줄이 그 함수 전체의 이름 해석 방식을 바꿀 수 있습니다.
- `nonlocal`과 `global`은 흔히 쓰는 도구가 아니라, 의도적인 갱신을 표시하는 표식입니다.
- 렉시컬 스코프의 강점은 "읽어서 알 수 있다"는 점입니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 전역 변수로 상태 공유 | 변경 출처가 흐려져 디버깅이 어려워짐 | 매개변수와 반환값으로 명시적으로 전달 |
| 내장 이름을 변수명으로 사용 | `list`, `dict`, `sum` 등을 덮어써 혼란 발생 | 내장 이름과 겹치지 않는 구체적인 이름 사용 |
| `global`을 쉽게 사용 | 전역 상태 의존성이 함수 사이에 숨겨짐 | 매개변수와 반환값으로 대체 |
| 함수 중간에서 이름 재대입 | UnboundLocalError 발생 | 함수 시작부에 지역 변수 명시적 초기화 |
| 루프 변수 캡처 함정 | 클로저가 반복문 마지막 값만 기억 | 기본 인자로 값 고정 또는 `let`(JS) 사용 |

## 실무에서는 이렇게 본다

좋은 코드는 "이 이름은 어디서 왔지?"라는 질문에 거의 즉시 답할 수 있어야 합니다. 큰 함수를 나누고, 숨은 의존성을 매개변수로 끌어올리고, 모듈 변수 갱신을 한곳에 모으는 습관은 모두 렉시컬 스코프의 장점을 극대화하는 방법입니다.

테스트도 같은 원리로 쉬워집니다. 전역 상태에 기대는 함수는 단위 테스트가 어렵고, 필요한 값을 매개변수로 받는 함수는 테스트가 단순해집니다. 스코프 규칙을 이해하는 일은 결국 읽기 쉬운 코드와 테스트 가능한 코드를 만드는 일과 맞닿아 있습니다.

### 클로저 캡처와 늦은 바인딩 실전 예시

클로저는 값이 아니라 바인딩을 참조합니다. 이 차이가 비동기 콜백이나 이벤트 핸들러에서 가장 자주 문제를 일으킵니다.

```python
# 문제: 루프 변수가 공유됨
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda: i)
    return handlers

print([h() for h in make_handlers()])  # [2, 2, 2]

# 해결: 기본 인자로 값 고정
def make_handlers_fixed() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda i=i: i)
    return handlers

print([h() for h in make_handlers_fixed()])  # [0, 1, 2]
```

변수의 "값"을 캡처하는지, "이름 해석 규칙"을 캡처하는지 구분하지 못하면 비동기 콜백과 지연 실행 코드에서 재현이 어려운 버그가 생깁니다.

## TypeScript에서의 스코프: `let`, `const`, `var` 비교

TypeScript(JavaScript)의 스코프 규칙은 Python보다 더 복잡합니다. 세 가지 선언 키워드가 각각 다른 스코프 규칙을 따르기 때문입니다.

```typescript
// TypeScript: var, let, const의 스코프 차이
function scopeDemo(): void {
    // var: 함수 스코프 + 호이스팅
    for (var i = 0; i < 3; i++) {
        // 루프 바깥에서도 i가 보임
    }
    console.log(i);  // 3 — var는 함수 스코프

    // let: 블록 스코프
    for (let j = 0; j < 3; j++) {
        // j는 for 블록 안에서만 보임
    }
    // console.log(j);  // ReferenceError: j is not defined

    // const: 블록 스코프 + 재할당 불가
    const MAX = 100;
    // MAX = 200;  // TypeError: Assignment to constant variable
}

// 클로저와 var vs let의 차이
const varFns: (() => number)[] = [];
for (var k = 0; k < 3; k++) {
    varFns.push(() => k);  // 모두 같은 k를 참조
}
console.log(varFns.map(f => f()));  // [3, 3, 3]

const letFns: (() => number)[] = [];
for (let m = 0; m < 3; m++) {
    letFns.push(() => m);  // 반복마다 새 m이 생성됨
}
console.log(letFns.map(f => f()));  // [0, 1, 2]
```

`var`와 `let`의 차이는 언어 버전(ES5 vs ES6)에서 온 역사적 결정이지만, 스코프 규칙이 코드 동작에 얼마나 깊은 영향을 주는지 보여 주는 가장 실용적인 예시입니다.

## 모듈 스코프: 파일 경계를 이용한 캡슐화

스코프는 함수 안에서만 작동하지 않습니다. 파이썬 모듈과 JavaScript/TypeScript 모듈 모두 파일 경계를 스코프로 씁니다.

```python
# counter.py — 모듈 스코프를 이용한 상태 캡슐화
_count = 0  # 언더스코어로 "모듈 내부 변수" 표시

def increment() -> int:
    global _count
    _count += 1
    return _count

def reset() -> None:
    global _count
    _count = 0

# 사용하는 쪽에서는 _count에 직접 접근하지 않는다는 관례
```

```python
# main.py
from counter import increment, reset

print(increment())  # 1
print(increment())  # 2
reset()
print(increment())  # 1
```

`_count`는 모듈 외부에서도 기술적으로 접근 가능하지만(`import counter; counter._count`), 언더스코어 관례를 통해 "이 변수는 모듈 내부 구현"임을 알립니다. 언어가 강제하지 않아도 스코프를 이용한 캡슐화는 코드 안정성을 높입니다.

## 운영 체크리스트

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

## 처음 질문으로 돌아가기

- **스코프와 바인딩은 정확히 무엇이 다를까요?**
  - 바인딩은 이름과 값을 연결하는 행위입니다. 스코프는 그 연결이 유효한 코드 영역입니다. `x = 1`은 바인딩이고, 이 바인딩이 함수 안에서만 보이면 그 함수가 `x`의 스코프입니다.
- **렉시컬 스코프와 동적 스코프는 결과를 어떻게 바꿀까요?**
  - 렉시컬 스코프는 코드가 쓰인 위치를 기준으로 이름을 찾습니다. 동적 스코프는 실행 중 호출 경로를 따라 이름을 찾습니다. 현대 언어 대부분이 렉시컬 스코프를 택한 이유는 소스 코드만 읽어도 값의 출처를 알 수 있어 가독성이 높기 때문입니다.
- **같은 이름을 안쪽에서 다시 쓰는 섀도잉은 왜 위험할까요?**
  - 안쪽 이름이 바깥 이름을 가려 버리면 두 이름이 같은 것처럼 읽히지만 실제로는 다른 값을 가리킵니다. 특히 내장 함수 이름(`sum`, `list`, `id`)을 변수명으로 쓰면 그 스코프에서 내장 기능을 완전히 잃어버립니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- **Programming Languages 101 (4/10): 스코프와 바인딩 (현재 글)**
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- [Programming Languages 101 (8/10): 인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- [Programming Languages 101 (9/10): 정적 언어와 동적 언어](./09-static-vs-dynamic.md)
- [Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?](./10-what-makes-good-language-design.md)

<!-- toc:end -->

## 참고 자료

- [Python Language Reference — Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
- [Structure and Interpretation of Computer Programs — Chapter 3](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-21.html)
- [Programming Language Pragmatics (Scott) — Chapter 3 Names, Scopes, and Bindings](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)
- [MDN — Scope](https://developer.mozilla.org/en-US/docs/Glossary/Scope)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Scope, Binding, Lexical, Dynamic
