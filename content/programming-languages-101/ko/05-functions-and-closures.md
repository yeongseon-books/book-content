---
series: programming-languages-101
episode: 5
title: 함수와 클로저
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
  - Functions
  - Closure
  - FirstClass
  - Capture
seo_description: 일급 함수와 렉시컬 스코프가 결합된 클로저 원리를 정리합니다. 캡처와 늦은 바인딩 함정, 데코레이터로 함수가 환경을 보존하는 법을 정리합니다.
last_reviewed: '2026-05-15'
---

# 함수와 클로저

함수가 자신이 정의된 자리의 변수를 기억하는 것처럼 보일 때가 있습니다. 처음 보면 마법처럼 느껴지지만, 실제로는 지난 글의 스코프 규칙과 함수가 값처럼 다뤄질 수 있다는 사실이 자연스럽게 합쳐진 결과입니다.

이 글은 Programming Languages 101 시리즈의 다섯 번째 글입니다.

이 글에서는 클로저를 “설명하기 어려운 특별한 기능”이 아니라, 렉시컬 스코프와 일급 함수가 만났을 때 생기는 평범한 결과로 보겠습니다. 함수가 값을 붙잡는 것이 아니라 바인딩을 붙잡는다는 점까지 분명히 이해하면 콜백, 데코레이터, 메모이제이션이 한 번에 연결됩니다.

## 이 글에서 다룰 문제

- 일급 함수와 고차 함수는 무엇이 다를까요?
- 클로저는 정확히 무엇을 캡처할까요?
- 왜 반복문 안에서 만든 람다가 같은 값만 출력할까요?
- 클로저는 객체와 어떤 점에서 닮아 있을까요?

> 클로저는 “함수 + 그 함수가 자라난 환경”입니다. 함수가 만들어질 때 바깥 스코프의 바인딩을 함께 들고 나가기 때문에, 나중에 호출해도 그 환경 위에서 계속 계산할 수 있습니다.

## 왜 중요한가

클로저는 콜백, 데코레이터, 부분 적용, 모듈 스타일 캡슐화의 바탕입니다. 이 구조를 정확히 이해하지 못하면 반복문 안 람다가 모두 같은 값을 출력하는 고전적인 문제를 계속 만나게 됩니다. 반대로 클로저를 이해하면 상태를 숨기면서 동작을 전달하는 구조를 훨씬 단순하게 설계할 수 있습니다.

## 핵심 개념 한눈에 보기

![클로저가 함수와 캡처한 바인딩을 함께 들고 가는 구조](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/05/05-01-concept-at-a-glance.ko.png)

*클로저가 함수와 캡처한 바인딩을 함께 들고 가는 구조*

`make_adder(10)`이 반환한 `add`는 단순한 함수 객체가 아닙니다. `x = 10`이라는 바인딩까지 함께 들고 다닙니다. 호출자는 안쪽을 볼 수 없지만, `add`는 그 환경을 바탕으로 계속 계산할 수 있습니다.

## 먼저 알아둘 용어

- 일급 함수: 함수를 변수에 담고, 인자로 넘기고, 반환값으로 돌려줄 수 있습니다.
- 고차 함수: 함수를 인자로 받거나 함수를 반환하는 함수입니다.
- 클로저: 바깥 스코프의 바인딩을 붙잡은 함수입니다.
- 참조 캡처: 값 복사본이 아니라 같은 바인딩을 참조합니다.
- 늦은 바인딩: 캡처한 이름의 현재 값을 호출 시점에 읽습니다.

## 먼저 보는 예시

### 전역 상태에 기대는 방식

```python
total = 0
def add(n):
    global total
    total += n
add(3); add(4)
print(total)  # 7
```

전역 상태를 쓰면 함수 하나를 두 군데에서 독립적으로 쓰기 어렵습니다. 상태가 한곳에 묶여 있기 때문입니다.

### 클로저로 상태를 분리하는 방식

```python
def make_accumulator():
    total = 0
    def add(n):
        nonlocal total
        total += n
        return total
    return add

a = make_accumulator()
b = make_accumulator()
print(a(3), a(4))  # 3 7
print(b(10))       # 10  (independent of a)
```

각 호출은 자기만의 `total`을 따로 붙잡습니다. 이 고립된 상태가 바로 클로저의 힘이고, 다음 글에서 볼 객체의 감각과도 이어집니다.

## 클로저를 다섯 각도에서 보기

### 1단계 — 가장 단순한 클로저

```python
# 1_basic.py
def make_adder(x):
    def add(n):
        return x + n
    return add

add10 = make_adder(10)
add20 = make_adder(20)
print(add10(5), add20(5))  # 15 25
```

`add10`과 `add20`은 같은 함수 모양을 가졌지만 서로 다른 바인딩을 붙잡고 있습니다.

### 2단계 — 값이 아니라 바인딩을 공유한다는 증거

```python
# 2_reference.py
def make_pair():
    state = {"n": 0}
    def get(): return state["n"]
    def inc(): state["n"] += 1
    return get, inc

g, i = make_pair()
i(); i(); i()
print(g())  # 3
```

두 함수가 같은 `state`를 함께 바라봅니다. 복사본을 들고 있는 것이 아니라 같은 바인딩을 공유한다는 말입니다.

### 3단계 — 늦은 바인딩 함정

```python
# 3_late_binding.py
fns = []
for i in range(3):
    fns.append(lambda: i)

print([f() for f in fns])  # [2, 2, 2]  — same i!
```

세 람다는 모두 같은 `i`를 붙잡았습니다. 호출 시점에는 반복문이 이미 끝났기 때문에 전부 2를 봅니다.

### 4단계 — 정의 시점 값으로 고정하기

```python
# 4_fix.py
fns = [(lambda i=i: i) for i in range(3)]
print([f() for f in fns])  # [0, 1, 2]
```

기본 인자는 함수 정의 시점에 계산됩니다. 그래서 그 순간의 값을 얼려 둘 수 있습니다.

### 5단계 — 메모이제이션 만들기

```python
# 5_memo.py
def memo(fn):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

@memo
def slow_square(n):
    return n * n

print(slow_square(7), slow_square(7))  # 49 49 — second is cached
```

`cache`는 `wrapper`의 클로저 안에 살아 있습니다. 바깥에서는 보이지 않지만, 호출 사이에서는 계속 유지됩니다.

## 이 코드에서 먼저 볼 점

- 클로저는 함수만이 아니라 함수와 환경의 묶음입니다.
- 캡처는 값 복사가 아니라 바인딩 참조입니다.
- 늦은 바인딩 문제는 “정의 시점에 값을 고정할 것인가, 참조를 살아 있게 둘 것인가”의 차이에서 나옵니다.
- 데코레이터와 콜백과 팩토리 함수는 대부분 클로저 위에 서 있습니다.

## 자주 하는 실수

1. 반복문 안 람다가 캡처한 변수를 모두 공유한다는 사실을 잊습니다.
2. 클로저와 객체를 전혀 다른 것으로 봅니다. 둘 다 상태와 동작을 묶는 방식입니다.
3. 바깥에서 캡처된 상태를 직접 바꾸려 합니다. 클로저는 일부러 그 상태를 감춥니다.
4. `nonlocal`을 빼먹습니다. `+=`는 새 지역 변수를 만들려 하기 때문입니다.
5. 큰 객체를 캡처한 클로저를 오래 들고 있어 메모리 누수를 만듭니다.

## 실무에서는 이렇게 본다

JavaScript의 이벤트 핸들러, Python의 데코레이터, 함수형 라이브러리의 부분 적용은 모두 클로저를 바탕으로 움직입니다. 버튼을 눌렀을 때 특정 상태를 바꾸는 UI 코드가 자연스럽게 표현되는 이유도 결국 함수가 주변 상태를 함께 들고 다닐 수 있기 때문입니다.

라이브러리를 설계할 때도 “사용자가 넘긴 함수를 우리 환경 안에서 호출한다”는 구조는 대개 클로저로 가장 깔끔하게 표현됩니다. 다만 상태가 너무 커지거나 수명이 길어지면 클래스로 올리는 편이 더 읽기 쉬워질 수 있습니다.

## 체크리스트

- [ ] 일급 함수와 고차 함수의 차이를 한 줄로 설명할 수 있는가?
- [ ] 클로저가 값을 복사하는 것이 아니라 바인딩을 참조한다는 점을 아는가?
- [ ] 늦은 바인딩 함정과 회피법을 설명할 수 있는가?
- [ ] 클로저 안에서 `nonlocal`이 왜 필요한지 설명할 수 있는가?
- [ ] 작은 메모이제이션 함수를 직접 써 본 적이 있는가?

## 연습 문제

1. `memo` 예제에 최대 크기를 넣고 가장 오래된 항목부터 버리게 만들어 보세요.
2. 여러 버튼에 콜백을 등록하는 상황을 떠올리고, 늦은 바인딩 문제가 어떻게 드러나는지 설명해 보세요.
3. 클로저만으로 만든 개인용 카운터와 클래스로 만든 카운터를 각각 작성해 보고, 어느 쪽이 더 자연스러운지 한 줄로 적어 보세요.

## 정리

클로저는 함수와 환경의 결합입니다. 렉시컬 스코프와 일급 함수가 만나면 거의 자연스럽게 생깁니다. 다음 글에서는 같은 아이디어를 다른 모양으로 표현한 객체와 프로토타입을 보겠습니다.

<!-- toc:begin -->
- [프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [구문과 의미](./02-syntax-and-semantics.md)
- [타입 시스템](./03-type-system.md)
- [스코프와 바인딩](./04-scope-and-binding.md)
- **함수와 클로저 (현재 글)**
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)
<!-- toc:end -->

## 참고 자료

- [SICP — Procedures and the Processes They Generate](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-11.html)
- [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures)
- [Python functools — partial, lru_cache](https://docs.python.org/3/library/functools.html)
- [On Lambdas, Captures and Closures (PLT)](https://wiki.c2.com/?ClosuresThatWorkLikeObjects)

Tags: Computer Science, Programming Languages, Functions, Closure, FirstClass, Capture
