---
series: compilers-101
episode: 5
title: 심볼 테이블과 스코프
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
  - Compilers
  - SymbolTable
  - Scope
  - Lookup
seo_description: 심볼 테이블과 스코프가 이름 해석과 IDE 기능의 기반이 되는 이유를 설명합니다
last_reviewed: '2026-05-12'
---

# 심볼 테이블과 스코프

이 글은 Compilers 101 시리즈의 다섯 번째 글입니다. 함수 안의 `x`와 바깥의 `x`를 컴파일러가 어떻게 서로 다른 변수로 구분하는지 이해하면, 이름 해석이 결국 자료구조 설계 문제라는 사실이 선명해집니다.

## 이 글에서 다룰 문제

- 심볼 테이블은 정확히 무엇이며 왜 컴파일러의 핵심 자료구조일까요?
- 스코프는 스택이나 연결 딕셔너리로 어떻게 표현할 수 있을까요?
- shadowing과 lookup은 왜 자연스럽게 따라올까요?
- 함수, 블록, 모듈 스코프는 어떻게 같은 틀로 표현할까요?
- rename, go-to-definition 같은 IDE 기능은 왜 심볼 테이블 위에 세워질까요?

> 심볼 테이블은 “이 이름이 어떤 선언을 가리키는가?”를 기억하는 컴파일러의 메모리이며, 중첩 스코프와 shadowing은 이 자료구조의 모양으로 직접 표현됩니다.

## 왜 중요한가

이전 글에서는 환경을 단일 딕셔너리로 표현했습니다. 하지만 실제 언어에는 함수, 블록, 클래스, 모듈처럼 여러 스코프가 존재합니다. 결국 스코프를 어떻게 설계하느냐가 그 언어의 가시성 규칙을 결정합니다.

> “이 변수가 여기서 보이는가?”라는 질문에 한 번에 답할 수 있어야 합니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart TB
    A["module scope"] --> B["function scope"]
    B --> C["block scope (if)"]
    C --> D["block scope (for)"]
```

스코프는 트리이자 스택입니다. lookup은 안쪽에서 바깥쪽으로 진행됩니다.

## 핵심 용어

- **심볼(Symbol)**: 선언 엔트리입니다. 보통 `(name, kind, type, location)`을 갖습니다.
- **스코프(Scope)**: 같은 가시성 규칙을 공유하는 심볼 집합입니다.
- **shadowing**: 안쪽 스코프의 이름이 바깥 스코프의 같은 이름을 가리는 현상입니다.
- **lookup**: 안쪽에서 바깥으로 걸어 올라가며 처음 맞는 선언을 찾는 과정입니다.
- **forward declaration**: 선언이 사용보다 뒤에 나오는 경우입니다.

## Before / After

**Before — 평평한 딕셔너리**

```python
env = {"x": "int"}  # cannot express x inside a function
```

**After — 연결된 딕셔너리**

```python
class Scope:
    def __init__(self, parent=None):
        self.parent, self.table = parent, {}
```

부모 포인터 하나만으로 함수, 블록, 모듈을 같은 자료구조 안에 넣을 수 있습니다.

## 실습: 심볼 테이블을 단계별로 만들기

### 1단계 — 가장 단순한 Scope

```python
# 1_scope.py
class Scope:
    def __init__(self, parent=None):
        self.parent, self.table = parent, {}
    def define(self, name, sym):
        if name in self.table:
            raise SyntaxError(f"redeclared: {name}")
        self.table[name] = sym
    def resolve(self, name):
        if name in self.table: return self.table[name]
        if self.parent: return self.parent.resolve(name)
        return None

g = Scope(); g.define("x", "int")
f = Scope(g); print(f.resolve("x"))  # int
```

단 하나의 `parent` 포인터가 중첩 lookup을 자동으로 만들어 줍니다.

### 2단계 — shadowing

```python
# 2_shadow.py
g = Scope(); g.define("x", "int(global)")
f = Scope(g); f.define("x", "int(local)")
print(f.resolve("x"))   # int(local) — inner hides outer
print(g.resolve("x"))   # int(global)
```

안쪽 스코프에서 같은 이름을 다시 정의하면 자동으로 바깥쪽을 가립니다. 이것이 shadowing입니다.

### 3단계 — 스코프 스택 운영하기

```python
# 3_stack.py
class Analyzer:
    def __init__(self):
        self.scopes = [Scope()]
    def enter(self): self.scopes.append(Scope(self.scopes[-1]))
    def exit(self): self.scopes.pop()
    def current(self): return self.scopes[-1]

a = Analyzer()
a.current().define("x", "int")
a.enter()
a.current().define("y", "int")
print(a.current().resolve("x"))  # int (found in outer scope)
a.exit()
```

`enter / exit`가 블록 진입과 종료를 표현합니다. AST를 걷는 동안 이 균형이 반드시 맞아야 합니다.

### 4단계 — 함수 스코프

```python
# 4_function.py
def visit_function(name, params, body, analyzer):
    analyzer.current().define(name, "fn")
    analyzer.enter()
    for p in params:
        analyzer.current().define(p, "param")
    for stmt in body:
        visit(stmt, analyzer)
    analyzer.exit()
```

함수에 들어가면 새 스코프를 만들고, 매개변수를 넣고, 본문을 분석한 뒤 닫습니다. 함수 스코프는 결국 일반 스코프의 한 사례일 뿐입니다.

### 5단계 — go-to-definition을 위한 위치 저장

```python
# 5_goto.py
class Symbol:
    def __init__(self, name, kind, ty, line, col):
        self.name, self.kind, self.ty = name, kind, ty
        self.line, self.col = line, col

def goto(scope, name):
    s = scope.resolve(name)
    return f"{s.name} at line {s.line}, col {s.col}" if s else "not found"
```

선언 위치를 심볼에 저장해 두면, IDE의 go-to-definition은 사실상 평범한 lookup이 됩니다.

## 이 코드에서 먼저 봐야 할 점

- 핵심 자료구조는 부모 포인터를 가진 Scope 하나입니다.
- shadowing은 별도 예외 규칙이 아니라 lookup 알고리즘의 자연스러운 결과입니다.
- 함수, 블록, 모듈은 모두 같은 자료구조 형태로 표현됩니다.
- IDE 기능 대부분은 심볼 테이블 위에서 나옵니다.

## 자주 하는 실수 다섯 가지

1. **스코프를 딕셔너리 하나로 끝내려는 것**입니다. 함수 안의 변수와 바깥 변수를 구분할 수 없습니다.
2. **`enter / exit` 호출 균형을 맞추지 않는 것**입니다. 스코프가 새어 나갑니다.
3. **모든 스코프를 검사해 shadowing 자체를 금지하려는 것**입니다. 많은 언어에서 shadowing은 기능입니다.
4. **forward declaration을 고려하지 않는 것**입니다. 함수 안에서 아래쪽 함수를 호출하는 코드가 깨질 수 있습니다.
5. **심볼에 위치 정보를 저장하지 않는 것**입니다. 나중에 go-to-definition을 붙일 수 없습니다.

## 실무에서는 이렇게 나타납니다

LSP 서버의 중심 자료구조가 바로 심볼 테이블입니다. “모든 참조 찾기”는 스코프를 따라 사용 지점을 모으는 일이고, “이름 바꾸기”는 같은 심볼을 가리키는 모든 사용 지점을 함께 다시 쓰는 일입니다. 결국 IDE의 많은 기능은 심볼 테이블 모델 위에 쌓입니다.

## 숙련된 엔지니어는 이렇게 봅니다

- 새 언어 기능을 보면 먼저 “이것은 어느 스코프에 들어가는가?”를 묻습니다.
- shadowing을 허용할지 경고할지 언어 차원에서 결정합니다.
- 심볼에 위치, 가시성, 사용 횟수 같은 메타데이터를 저장합니다.
- 선언 수집과 사용 분석을 나누는 2패스 접근을 기본으로 생각합니다.
- 심볼 테이블이 곧 IDE의 데이터 모델이라는 점을 압니다.

## 체크리스트

- [ ] Scope가 부모 포인터를 가진 딕셔너리라는 설명을 이해했습니까?
- [ ] shadowing이 lookup 규칙의 자연스러운 결과라는 점을 설명할 수 있습니까?
- [ ] 함수 스코프와 블록 스코프를 같은 자료구조로 표현할 수 있습니까?
- [ ] go-to-definition이 결국 lookup이라는 점이 보입니까?
- [ ] 심볼 테이블을 2패스로 채우는 이유를 말할 수 있습니까?

## 연습 문제

1. 특정 스코프에 정의된 모든 심볼을 나열하는 메서드를 Scope에 추가해 보세요.
2. shadowing이 발생하면 경고를 내는 옵션을 추가해 보세요.
3. forward declaration을 지원하기 위해 선언 수집과 사용 분석을 분리한 2패스 의사코드를 작성해 보세요.

## 정리 및 다음 글

심볼 테이블은 컴파일러가 “이 이름은 무엇인가?”에 답하기 위해 유지하는 메모리입니다. 다음 글에서는 분석이 끝난 AST를 더 단순한 내부 언어로 바꾸는 단계, intermediate representation을 다룹니다.

<!-- toc:begin -->
- [컴파일러란 무엇인가?](./01-what-is-a-compiler.md)
- [렉시컬 분석](./02-lexical-analysis.md)
- [파싱과 AST](./03-parsing-and-ast.md)
- [시맨틱 분석](./04-semantic-analysis.md)
- **심볼 테이블과 스코프 (현재 글)**
- 중간 표현 (예정)
- 최적화 기초 (예정)
- 코드 생성 (예정)
- JIT vs AOT (예정)
- 작은 인터프리터 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Symbol table (Wikipedia)](https://en.wikipedia.org/wiki/Symbol_table)
- [Scope (Wikipedia)](https://en.wikipedia.org/wiki/Scope_(computer_science))
- [Crafting Interpreters — Resolving and Binding](https://craftinginterpreters.com/resolving-and-binding.html)
- [LSP — Document Symbols](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol)

Tags: Computer Science, Compilers, SymbolTable, Scope, Lookup
