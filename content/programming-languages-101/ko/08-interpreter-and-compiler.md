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

이 글은 Programming Languages 101 시리즈의 8번째 글입니다.

이 글에서는 인터프리터와 컴파일러를 서로 반대 진영으로 보지 않고, 번역이 언제 일어나는지가 다른 두 전략으로 보겠습니다. Python 바이트코드를 직접 들여다보고, AOT와 JIT가 어디서 갈라지는지도 함께 정리하겠습니다.

![Programming Languages 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/08/08-01-concept-at-a-glance.ko.png)
*Programming Languages 101 8장 흐름 개요*

> 인터프리터와 컴파일러의 경계는 흐릿하고, 현대 언어는 거의 다 그 사이 어딘가에 있습니다 — Python은 bytecode 컴파일 + VM 인터프리터, JS는 JIT, Java는 AOT+JIT, 이 스펙트럼이 머릿속에 있어야 '왜 빠르고 왜 느린지'를 설명할 수 있습니다.

## 이 글에서 다룰 문제

- 인터프리터와 컴파일러의 가장 짧은 차이는 무엇일까요?
- Python은 실제로 어떤 실행 경로를 거칠까요?
- `.pyc` 파일은 정확히 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

성능 문제가 생겼을 때 "이 줄이 실제로 어떤 형태로 실행되는가"를 설명할 수 있으면 감으로 디버깅하지 않게 됩니다. 같은 코드가 인터프리터, JIT, AOT 환경에서 왜 다르게 보이는지도 이 시점 차이로 정리할 수 있습니다.

## 먼저 알아둘 용어

- **컴파일러**: 소스 코드를 다른 형태로 미리 번역합니다.
- **인터프리터**: 실행 중에 코드를 한 단계씩 처리합니다.
- **AOT**: 전체를 미리 컴파일하고 실행합니다.
- **JIT**: 실행 중 자주 쓰이는 부분만 골라 컴파일합니다.
- **바이트코드**: 소스와 기계어 사이에 놓인 중간 표현입니다.

## 실행 모델 스펙트럼

번역 시점과 대상에 따라 실행 모델을 스펙트럼으로 볼 수 있습니다.

```text
순수 인터프리터        바이트코드 + VM       JIT          AOT 컴파일러
     |                    |                  |               |
한 줄씩 즉시 실행    중간 코드 컴파일     실행 중 최적화   기계어로 미리 번역
(초기 Basic, 쉘)   (Python, Java, .NET)  (V8 JS, JVM)   (C, Go, Rust)
```

Python, Java, .NET은 모두 이 스펙트럼의 중간 어딘가에 있습니다. 언어를 "인터프리터"나 "컴파일러"로 단정하는 것은 실제로는 부정확합니다.

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

## 언어별 실행 모델 비교

같은 덧셈 함수가 각 실행 환경에서 어떻게 처리되는지 비교해 보겠습니다.

```python
# Python (CPython): 바이트코드 → VM 인터프리터
def add(a: int, b: int) -> int:
    return a + b

# dis.dis(add) 출력 예시:
#   LOAD_FAST   0 (a)
#   LOAD_FAST   1 (b)
#   BINARY_OP   0 (+)
#   RETURN_VALUE
```

```javascript
// JavaScript (V8): 바이트코드 → JIT 컴파일
// 처음 몇 번은 인터프리터, 자주 호출되면 TurboFan이 네이티브 코드로 컴파일
function add(a, b) {
    return a + b;
}

// 100만 번 호출하면 JIT 최적화 대상이 됨
for (let i = 0; i < 1_000_000; i++) {
    add(i, i + 1);
}
```

```go
// Go: AOT 컴파일 → 네이티브 기계어 직접 실행
// go build 시점에 완전한 기계어로 번역됨
func add(a, b int) int {
    return a + b
}
// 워밍업 없음, 시작부터 최고 속도
```

```rust
// Rust: AOT 컴파일 + 공격적인 최적화 (LLVM)
fn add(a: i32, b: i32) -> i32 {
    a + b
}
// 최적화 레벨에 따라 인라인되거나 단일 명령어로 변환될 수 있음
```

Python은 유연하지만 각 명령이 VM을 통해 실행되어 오버헤드가 있고, Go와 Rust는 AOT로 시작부터 빠르고, JavaScript는 JIT로 중간 지점을 찾습니다.

## 이 코드에서 먼저 볼 점

- Python을 인터프리터 언어라고 부르는 말은 주로 실행 단계를 가리킵니다.
- `dis` 출력 한 줄은 VM의 한 사이클에 가깝습니다.
- `.pyc`는 신비한 실행 파일이 아니라 캐시된 바이트코드입니다.
- JIT는 "전부 컴파일"과 "전부 해석" 사이의 현실적인 중간 지점입니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 인터프리터와 컴파일러를 진영 싸움으로 봄 | 언어 선택 논쟁이 불필요하게 감정적이 됨 | 번역 시점의 차이, 워크로드에 맞는 선택 기준으로 |
| `.pyc`를 독립 실행 파일처럼 생각 | 배포 시 VM 없이 실행 불가 | `.pyc`는 여전히 Python VM이 필요한 바이트코드 |
| 알고리즘보다 언어 탓을 먼저 함 | 실제 병목이 O(n²) 알고리즘인데 Python을 교체하려 함 | 프로파일링으로 병목 확인 후 C 구현 라이브러리 고려 |
| JIT가 언제나 빠르다고 생각 | 짧은 실행에서 워밍업 비용이 더 큰 경우 | 워크로드 패턴에 따른 실제 측정 필수 |
| `dis`를 한 번도 열지 않고 성능 추측 | 직관과 실제 VM 동작이 다른 경우를 놓침 | 핵심 함수는 `dis.dis()`로 바이트코드 직접 확인 |

## 실무에서는 이렇게 본다

CPython은 바이트코드 캐시와 인터프리터만으로도 대부분의 작업을 충분히 처리합니다. 수치 계산처럼 뜨거운 경로는 NumPy나 PyTorch처럼 내부가 C/C++로 구현된 라이브러리에 넘기는 편이 흔합니다. PyPy는 같은 Python 코드를 JIT로 돌려 단순 루프에서 큰 차이를 보이기도 합니다.

JVM은 기본적으로 JIT 경로를 탑니다. Go, Rust, C는 AOT라서 시작이 빠르고 배포 형태도 단순합니다. 결국 중요한 것은 "어느 쪽이 더 우월한가"가 아니라 "이 워크로드에 어떤 실행 모델이 맞는가"입니다.

### 핫 경로를 찾고 최적화하는 실전 흐름

```python
import cProfile
import pstats
import io

def hot_function(n: int) -> int:
    result = 0
    for i in range(n):
        result += i * i
    return result

# 프로파일링으로 실제 병목 측정
pr = cProfile.Profile()
pr.enable()
hot_function(1_000_000)
pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(10)
print(s.getvalue())
```

`dis`로 바이트코드를 확인하고, `cProfile`로 어디서 시간이 쓰이는지 찾은 다음, NumPy나 C 확장으로 핫 경로를 내리는 순서가 실무에서 가장 효과적인 Python 최적화 흐름입니다.

## WebAssembly: 브라우저 안의 AOT

WebAssembly(Wasm)는 브라우저 안에서 네이티브에 가까운 속도로 실행되는 컴팩트한 바이너리 형식입니다. C, C++, Rust 같은 언어를 Wasm으로 컴파일하면, 브라우저의 JavaScript 엔진이 이를 AOT 또는 JIT로 실행합니다.

```text
소스 코드 (C/C++/Rust)
    |
    | emcc / wasm-pack
    v
WebAssembly 바이너리 (.wasm)
    |
    | 브라우저 JS 엔진 (V8, SpiderMonkey)
    v
기계어 (JIT 최적화 포함)
```

Python은 `wasmtime`이나 Pyodide 프로젝트를 통해 Wasm 환경에서 실행될 수 있습니다. 실행 모델 스펙트럼에 브라우저라는 타깃이 하나 더 추가된 셈입니다.

## 최신 Python 실행 최적화 옵션

CPython 3.11 이후 더 적극적인 최적화가 도입됐습니다. 실행 모델의 변화를 이해해 두면 버전 선택 기준이 더 명확해집니다.

```python
# Python 3.11+: 전문화된 적응적 인터프리터 (Specializing Adaptive Interpreter)
# 같은 코드를 반복 실행하면 VM이 자동으로 타입 특화 명령어로 교체

def add_numbers(a: int, b: int) -> int:
    return a + b

# 반복 호출 시 Python 3.11+는 내부적으로 더 효율적인 경로 사용
import timeit
result = timeit.timeit(lambda: add_numbers(1, 2), number=10_000_000)
print(f"10M calls: {result:.3f}s")

# Python 3.13+: 실험적 JIT (no-GIL 실험 빌드와 함께)
# 아직 기본 활성화가 아니지만, 실행 모델이 계속 진화 중임을 보여 줌
```

```text
CPython 버전별 실행 모델 진화:
3.10 이하  : 고전적 바이트코드 인터프리터
3.11       : 적응적 인터프리터 (타입 특화, 10-60% 속도 향상)
3.12       : 개선된 적응적 최적화
3.13+      : 실험적 JIT 컴파일러 (선택적 빌드)
```

실행 모델은 언어의 버전에 따라 계속 변합니다. Python을 "항상 느린 인터프리터"로 단정하는 것은 3.11 이후의 현실을 반영하지 못합니다.

## 운영 체크리스트

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
  - 컴파일러는 소스 코드를 실행 전에 다른 형태(기계어, 바이트코드)로 번역합니다. 인터프리터는 실행 중에 코드를 한 단계씩 처리합니다. 핵심 차이는 번역이 실행 전에 일어나는지, 실행 중에 일어나는지입니다.
- **Python은 실제로 어떤 실행 경로를 거칠까요?**
  - `.py` 파일을 렉싱, 파싱해 AST를 만들고, AST를 바이트코드로 컴파일해 `.pyc`에 저장합니다. 이후 Python VM(CPython)이 바이트코드를 한 명령씩 실행합니다. Python은 컴파일 단계도 있고 인터프리터 단계도 있는 하이브리드입니다.
- **`.pyc` 파일은 정확히 무엇일까요?**
  - 소스를 파싱하고 컴파일한 결과를 캐시해 둔 바이트코드 파일입니다. 소스가 바뀌지 않으면 다음 실행 시 컴파일 비용을 생략하고 바이트코드를 바로 VM에 전달합니다. 독립 실행 파일이 아니므로 Python VM이 없으면 실행할 수 없습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- **Programming Languages 101 (8/10): 인터프리터와 컴파일러 (현재 글)**
- [Programming Languages 101 (9/10): 정적 언어와 동적 언어](./09-static-vs-dynamic.md)
- [Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?](./10-what-makes-good-language-design.md)

<!-- toc:end -->

## 참고 자료

- [Python — dis module](https://docs.python.org/3/library/dis.html)
- [Python — py_compile module](https://docs.python.org/3/library/py_compile.html)
- [PyPy — How does PyPy work?](https://doc.pypy.org/en/latest/architecture.html)
- [Just-in-time compilation (Wikipedia)](https://en.wikipedia.org/wiki/Just-in-time_compilation)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, Interpreter, Compiler, JIT, Bytecode
