---
episode: 8
language: ko
last_reviewed: '2026-05-15'
seo_description: 인터프리터와 컴파일러가 소스 코드 번역 시점을 달리하는 방식과 실행 성능, 디버깅 경험에 미치는 영향을 비교합니다.
series: programming-languages-101
status: publish-ready
tags:
- Computer Science
- Programming Languages
- Interpreter
- Compiler
- JIT
- Bytecode
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Programming Languages 101 (8/10): 인터프리터와 컴파일러"
---

# Programming Languages 101 (8/10): 인터프리터와 컴파일러

Python을 흔히 인터프리터 언어라고 부릅니다. 그런데 `.pyc` 파일도 있습니다. 그렇다면 Python은 해석하는 언어일까요, 컴파일하는 언어일까요.

이 글은 Programming Languages 101 시리즈의 여덟 번째 글입니다.

이 글에서는 인터프리터와 컴파일러를 서로 반대 진영으로 보지 않고, 번역이 언제 일어나는지가 다른 두 전략으로 보겠습니다. Python 바이트코드를 직접 들여다보고, AOT와 JIT가 어디서 갈라지는지도 함께 정리하겠습니다.

## 먼저 던지는 질문

- 인터프리터와 컴파일러의 가장 짧은 차이는 무엇일까요?
- Python은 실제로 어떤 실행 경로를 거칠까요?
- `.pyc` 파일은 정확히 무엇일까요?

## 큰 그림

![Programming Languages 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/08/08-01-concept-at-a-glance.ko.png)

*Programming Languages 101 8장 흐름 개요*

이 그림에서는 인터프리터와 컴파일러를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 인터프리터와 컴파일러의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

성능 문제가 생겼을 때 “이 줄이 실제로 어떤 형태로 실행되는가”를 설명할 수 있으면 감으로 디버깅하지 않게 됩니다. 같은 코드가 인터프리터, JIT, AOT 환경에서 왜 다르게 보이는지도 이 시점 차이로 정리할 수 있습니다.

## 핵심 개념 한눈에 보기

CPython은 보통 소스 코드를 바이트코드로 만든 뒤 가상 머신이 한 명령씩 실행합니다. JVM 계열은 자주 실행되는 경로를 JIT로 네이티브 코드로 올리고, C나 Rust는 아예 미리 기계어로 컴파일합니다.

## 먼저 알아둘 용어

- 컴파일러: 소스 코드를 다른 형태로 미리 번역합니다.
- 인터프리터: 실행 중에 코드를 한 단계씩 처리합니다.
- AOT: 전체를 미리 컴파일하고 실행합니다.
- JIT: 실행 중 자주 쓰이는 부분만 골라 컴파일합니다.
- 바이트코드: 소스와 기계어 사이에 놓인 중간 표현입니다.

## 먼저 보는 예시

### 막연한 그림

```text
.py file → ??? → result
```

### 실제로 일어나는 일

```text
.py → tokenize → parse → AST → compile → .pyc bytecode → VM executes one op at a time
```

`.pyc`는 캐시된 바이트코드입니다. Python에도 분명한 컴파일 단계가 있고, 다만 그 결과를 인터프리터가 실행한다는 점이 중요합니다.

## 파이썬 실행 내부를 직접 들여다보기

### 1단계 — 바이트코드 읽기

```python
# 1_dis.py
import dis

def add(a: int, b: int) -> int:
    return a + b

dis.dis(add)
```

여기서 보이는 `LOAD_FAST`, `BINARY_OP`, `RETURN_VALUE` 같은 한 줄이 Python 가상 머신의 한 단계입니다. 성능을 얘기할 때 생각보다 유용한 단위입니다.

### 2단계 — 같은 알고리즘, 다른 명령 수

```python
# 2_optimization.py
import dis

def slow(xs):
    s = 0
    for x in xs:
        s = s + x
    return s

def fast(xs):
    return sum(xs)

print("--- slow ---"); dis.dis(slow)
print("--- fast ---"); dis.dis(fast)
```

`fast`는 훨씬 짧습니다. `sum` 내부 루프가 C로 구현돼 있기 때문에 Python VM이 처리해야 할 명령 수가 크게 줄어듭니다.

### 3단계 — 바이트코드 캐시 파일 확인하기

```python
# 3_pyc.py
import py_compile, dis, marshal, importlib.util, pathlib

src = pathlib.Path("/tmp/sample.py")
src.write_text("def f(): return 42\n")
pyc = py_compile.compile(str(src), doraise=True)

with open(pyc, "rb") as f:
    f.read(16)                # 16-byte header on Python 3.7+
    code = marshal.load(f)
dis.dis(code)
```

`.pyc`는 헤더와 직렬화된 코드 객체의 조합입니다. 이후 import에서는 이 결과를 재사용해 파싱과 컴파일 비용을 줄입니다.

### 4단계 — 미리 번역해 두는 감각 보기

```python
# 4_compile_call.py
import time

PY_SRC = "result = sum(range(10_000_000))"
code = compile(PY_SRC, "<inline>", "exec")

t0 = time.perf_counter(); exec(code, {}); t1 = time.perf_counter()
print("compiled-once exec:", t1 - t0)

t0 = time.perf_counter()
for _ in range(3):
    exec(PY_SRC, {})           # compiled fresh each iteration
print("recompiled each time:", time.perf_counter() - t0)
```

한 번 번역한 결과를 여러 번 실행하면 더 빠릅니다. 이것이 AOT가 주는 기본 직관입니다.

### 5단계 — 뜨거운 경로만 올리는 전략 보기

```python
# 5_hot_path.py
from collections import Counter

calls: Counter[str] = Counter()

def trace(name: str) -> None:
    calls[name] += 1

for _ in range(1_000_000):
    trace("inner")             # one million calls — JIT would target this
trace("outer")                  # only once

print(calls.most_common(2))
```

JIT는 이런 호출 빈도를 보다가 충분히 뜨거운 경로만 골라 네이티브 코드로 올립니다. 모든 것을 미리 컴파일하지도 않고, 모든 것을 끝까지 해석하지도 않는 실용적인 절충안입니다.

## 이 코드에서 먼저 볼 점

- Python을 인터프리터 언어라고 부르는 말은 주로 실행 단계를 가리킵니다.
- `dis` 출력 한 줄은 VM의 한 사이클에 가깝습니다.
- `.pyc`는 신비한 실행 파일이 아니라 캐시된 바이트코드입니다.
- JIT는 “전부 컴파일”과 “전부 해석” 사이의 현실적인 중간 지점입니다.

## 자주 하는 실수

1. 인터프리터와 컴파일러를 진영 싸움처럼 봅니다. 실제로는 번역 시점의 차이입니다.
2. `.pyc`를 독립 실행 파일처럼 생각합니다. 여전히 Python VM이 필요합니다.
3. 진짜 해결책이 C 구현 라이브러리 사용인데도 알고리즘을 먼저 갈아엎습니다.
4. JIT가 언제나 빠르다고 생각합니다. 짧은 실행에서는 워밍업 비용이 더 클 수 있습니다.
5. `dis`를 한 번도 열어 보지 않고 성능을 추측합니다.

## 실무에서는 이렇게 본다

CPython은 바이트코드 캐시와 인터프리터만으로도 대부분의 작업을 충분히 처리합니다. 수치 계산처럼 뜨거운 경로는 NumPy나 PyTorch처럼 내부가 C/C++로 구현된 라이브러리에 넘기는 편이 흔합니다. PyPy는 같은 Python 코드를 JIT로 돌려 단순 루프에서 큰 차이를 보이기도 합니다.

JVM은 기본적으로 JIT 경로를 탑니다. Go, Rust, C는 AOT라서 시작이 빠르고 배포 형태도 단순합니다. 결국 중요한 것은 “어느 쪽이 더 우월한가”가 아니라 “이 워크로드에 어떤 실행 모델이 맞는가”입니다.

## 체크리스트

- [ ] 인터프리터와 컴파일러의 차이를 한 줄로 설명할 수 있는가?
- [ ] `dis`로 함수 바이트코드를 읽어 본 적이 있는가?
- [ ] `.pyc`가 무엇인지 한 문장으로 설명할 수 있는가?
- [ ] AOT와 JIT의 차이를 말할 수 있는가?
- [ ] 뜨거운 루프를 C 구현 라이브러리로 내리는 패턴을 알고 있는가?

## 연습 문제

1. `slow`와 `fast`를 큰 입력으로 측정한 뒤, 성능 차이를 `dis` 출력과 연결해 설명해 보세요.
2. 같은 루프를 PyPy나 Cython 같은 다른 실행 모델에서 돌려 보고 차이를 적어 보세요.
3. 자주 쓰는 모듈 하나에서 `compileall`을 돌린 뒤 import 시간 변화를 관찰해 보세요.

## 정리

인터프리터, 컴파일러, JIT는 서로 적대적인 개념이 아니라 같은 번역 문제에 대한 다른 답입니다. 다음 글에서는 실행 모델과 더불어 언어 성격을 크게 바꾸는 또 하나의 축, 정적과 동적 언어의 차이를 보겠습니다.

## 처음 질문으로 돌아가기

- **인터프리터와 컴파일러의 가장 짧은 차이는 무엇일까요?**
  - 본문의 기준은 인터프리터와 컴파일러를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Python은 실제로 어떤 실행 경로를 거칠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`.pyc` 파일은 정확히 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- **인터프리터와 컴파일러 (현재 글)**
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Python — dis module](https://docs.python.org/3/library/dis.html)
- [Python — py_compile module](https://docs.python.org/3/library/py_compile.html)
- [PyPy — How does PyPy work?](https://doc.pypy.org/en/latest/architecture.html)
- [Just-in-time compilation (Wikipedia)](https://en.wikipedia.org/wiki/Just-in-time_compilation)

Tags: Computer Science, Programming Languages, Interpreter, Compiler, JIT, Bytecode
