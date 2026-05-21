---
series: compilers-101
episode: 4
title: "Compilers 101 (4/10): 시맨틱 분석"
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
  - SemanticAnalysis
  - TypeChecking
  - NameResolution
seo_description: 문법을 넘어 코드의 의미적 타당성을 검사하는 시맨틱 분석의 원리와 이름 해석 및 타입 검사 구현 방법을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Compilers 101 (4/10): 시맨틱 분석

이 글은 Compilers 101 시리즈의 네 번째 글입니다. 문법은 맞지만 의미가 틀린 코드가 왜 거부되는지 이해하는 순간, 컴파일러가 단순한 문장 검사기가 아니라 프로그램 의미를 판정하는 도구라는 점이 분명해집니다.

## 먼저 던지는 질문

- 문법적으로 맞다는 것과 의미적으로 맞다는 것은 어떻게 다를까요?
- 이름 해석은 무엇이며, 식별자는 어디를 가리킬까요?
- 타입 검사는 어떤 규칙으로 동작할까요?

## 큰 그림

![Compilers 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/compilers-101/04/04-01-big-picture.ko.png)

*Compilers 101 4장 흐름 개요*

## 왜 중요한가

파서는 괄호가 맞는지, 문장 구조가 규칙에 맞는지까지만 판단할 수 있습니다. 하지만 `x = y + 1`에서 `y`가 선언된 적이 없는지, 혹은 `y`가 문자열인데 `1`을 더하려는지 같은 문제는 시맨틱 단계에서만 잡을 수 있습니다. 이 단계가 약하면 컴파일은 통과했는데 런타임에서 터지는 코드가 늘어납니다.

> 컴파일러가 신뢰를 얻는 이유는 문법보다 시맨틱에 있습니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    A["AST"] --> B["name resolution"]
    B --> C["type inference / check"]
    C --> D["annotated AST"]
    D --> E["next stage"]
```

결과는 원래의 AST에 “이 이름은 이 선언을 가리킨다”, “이 식의 타입은 int다” 같은 메타데이터가 붙은 형태입니다.

## 핵심 용어

- **이름 해석**: 식별자가 어떤 선언을 가리키는지 결정하는 과정입니다.
- **타입 검사**: 식이 놓인 문맥에서 허용된 타입인지 확인하는 과정입니다.
- **타입 추론**: 코드에 명시되지 않은 타입을 추론해 내는 과정입니다.
- **annotated AST**: 시맨틱 정보가 붙은 AST입니다.
- **강제 변환(coercion)**: `int → float`처럼 호환 가능한 타입 사이의 암묵 변환입니다.

## Before / After

**Before — 파서가 남긴 AST**

```python
ast = Bin("+", Var("x"), Str("hello"))
# nobody knows what x is, or whether the two sides match
```

**After — 의미 정보가 붙은 AST**

```python
# x: int (declared at line 3)
# Bin.+ requires int + int, got int + str → TypeError
```

이제 뒤 단계는 이 AST를 신뢰하고 다음 작업을 진행할 수 있습니다.

## 실습: 작은 시맨틱 분석기 만들기

### 1단계 — 단순한 타입 환경

```python
# 1_env.py
class Env:
    def __init__(self, parent=None):
        self.parent, self.table = parent, {}
    def declare(self, name, ty):
        if name in self.table:
            raise SyntaxError(f"redeclared: {name}")
        self.table[name] = ty
    def lookup(self, name):
        if name in self.table: return self.table[name]
        if self.parent: return self.parent.lookup(name)
        raise NameError(f"undeclared: {name}")
```

이름 해석은 결국 딕셔너리 조회입니다. 부모 포인터 하나만 있으면 중첩 스코프도 자연스럽게 표현됩니다.

### 2단계 — 이름 해석

```python
# 2_resolve.py
from dataclasses import dataclass
@dataclass
class Var: name: str
@dataclass
class Decl:
    name: str; ty: str

env = {"int_globals": "int"}
def resolve(node):
    if isinstance(node, Var):
        if node.name not in env:
            raise NameError(f"'{node.name}' is not defined")
    if isinstance(node, Decl):
        env[node.name] = node.ty
```

선언과 사용을 같은 환경 자료구조로 다뤄야 합니다. AST를 순회하면서 환경을 갱신하고 동시에 조회하는 패턴이 기본입니다.

### 3단계 — 단순 타입 검사

```python
# 3_typecheck.py
def type_of(node, env):
    kind = node[0]
    if kind == "NUM": return "int"
    if kind == "STR": return "str"
    if kind == "VAR": return env[node[1]]
    if kind == "BIN":
        op, l, r = node[1], type_of(node[2], env), type_of(node[3], env)
        if l != r:
            raise TypeError(f"{op}: {l} vs {r}")
        return l

env = {"x": "int"}
print(type_of(("BIN","+",("VAR","x"),("NUM",1)), env))  # int
```

타입은 트리를 따라 아래에서 위로 올라옵니다. 자식 둘이 맞지 않으면 바로 그 지점에서 오류를 냅니다.

### 4단계 — annotated AST 만들기

```python
# 4_annotate.py
def annotate(node, env):
    kind = node[0]
    if kind == "NUM": return ("NUM", node[1], "int")
    if kind == "VAR": return ("VAR", node[1], env[node[1]])
    if kind == "BIN":
        l = annotate(node[2], env); r = annotate(node[3], env)
        if l[-1] != r[-1]:
            raise TypeError(f"{node[1]}: {l[-1]} vs {r[-1]}")
        return ("BIN", node[1], l, r, l[-1])
```

원래 AST 끝에 타입 정보를 붙여 annotated AST를 만듭니다. 다음 단계는 이 트리를 다시 한 번 걷기만 하면 됩니다.

### 5단계 — 좋은 오류 메시지 만들기

```python
# 5_error.py
def report(token, expected, got):
    print(f"  File \"<src>\", line {token['line']}")
    print(f"    {token['text']}")
    print(f"  TypeError: expected {expected}, got {got}")

report({"line": 12, "text": 'x + "hello"'}, "int", "str")
```

시맨틱 오류 메시지는 보통 세 줄이면 충분합니다. 위치, 기대한 것, 실제로 들어온 것입니다.

## 이 코드에서 먼저 봐야 할 점

- 환경(Env)은 부모 포인터를 가진 연결 딕셔너리로 자연스럽게 중첩 스코프를 표현합니다.
- 타입은 별도 자료구조가 아니라 AST에 붙는 추가 정보입니다.
- 오류는 가능한 한 그 위치에 가깝게 보고해야 합니다.
- 한 번의 순회로도 가능하지만, 필요하면 여러 패스로 쪼갤 수 있습니다.

## 자주 하는 실수 다섯 가지

1. **이름(Name)과 심볼(Symbol)을 같은 것으로 보는 것**입니다. 이름은 텍스트이고, 심볼은 선언 엔트리입니다.
2. **첫 번째 타입 오류에서 바로 멈추는 것**입니다. 사용자 경험은 여러 오류를 한 번에 보여 줄 때 좋아집니다.
3. **타입 호환성을 `==`로만 판단하는 것**입니다. 하위 타입, 제네릭, coercion이 들어오면 무너집니다.
4. **선언용 환경과 사용용 환경을 따로 만드는 것**입니다. 진실의 원천은 하나여야 합니다.
5. **스코프 진입/탈출을 부모 포인터 없이 처리하려는 것**입니다. 변수 가리기(shadowing)가 깨집니다.

## 실무에서는 이렇게 나타납니다

언어 서버(LSP)의 핵심 기능 상당수가 여기서 나옵니다. “정의로 이동”은 이름 해석이고, “타입 힌트”는 타입 추론이며, “심볼 이름 바꾸기”는 시맨틱 정보와 심볼 테이블 갱신입니다. 즉, 시맨틱 단계는 IDE 핵심 기능의 기반이기도 합니다.

## 숙련된 엔지니어는 이렇게 봅니다

- 사용자가 가장 많이 읽는 문장은 시맨틱 오류 메시지라는 사실을 압니다.
- 단일 환경을 진실의 원천으로 강하게 유지합니다.
- 시맨틱 정보를 옆으로 흘리지 않고 AST에 직접 붙입니다.
- 한 패스에서 여러 오류를 보고할 수 있게 복구 전략을 설계합니다.
- 확장을 위해 타입 시스템을 lattice처럼 추상화해 생각합니다.

## 체크리스트

- [ ] 문법 오류와 시맨틱 오류의 차이를 한 문장으로 설명할 수 있습니까?
- [ ] 이름 해석이 결국 딕셔너리 조회라는 점을 받아들였습니까?
- [ ] AST에 타입을 붙이는 패턴을 직접 작성해 본 적이 있습니까?
- [ ] 시맨틱 오류 메시지의 표준 형태를 정의해 두었습니까?
- [ ] LSP 기능이 시맨틱 단계와 어떻게 연결되는지 설명할 수 있습니까?

## 연습 문제

1. 위 환경에 함수 진입/탈출을 추가해 중첩 스코프를 처리해 보세요.
2. `int + float`를 `float`로 승격하는 coercion 규칙을 추가해 보세요.
3. 파일 전체의 시맨틱 오류를 모아 마지막에 한 번에 출력하는 구조를 설계해 보세요.

## 정리 및 다음 글

시맨틱 분석은 문법만으로는 답할 수 없는 “이 코드가 정말 의미가 맞는가?”라는 질문에 답하는 단계입니다. 다음 글에서는 이 단계의 핵심 도구인 symbol table과 scope를 더 집중해서 살펴봅니다.

## 심화 실습: Lexer · Parser · AST를 연결해 보는 기준

이 지점에서는 "각 단계가 왜 분리되어야 하는가"를 코드 단위로 확인하는 것이 중요합니다. 핵심은 정답 코드를 외우는 것이 아니라, 같은 입력이 단계별로 어떻게 다른 데이터 구조로 변환되는지 관찰하는 것입니다.

### EBNF로 문법을 먼저 고정하기

문법을 먼저 적어 두면 파서 구현이 훨씬 명확해집니다. 아래 예시는 사칙연산과 괄호를 포함한 최소 문법입니다.

```ebnf
expr    = term , { ("+" | "-") , term } ;
term    = factor , { ("*" | "/") , factor } ;
factor  = number | "(" , expr , ")" ;
number  = digit , { digit } ;
digit   = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

이 문법에서 `expr -> term -> factor`로 내려가는 구조가 바로 연산자 우선순위를 표현합니다. `+`와 `-`는 `expr` 레벨, `*`와 `/`는 `term` 레벨에 있으므로 `2 + 3 * 4`는 자연스럽게 `2 + (3 * 4)`로 해석됩니다.

### 토큰화에서 위치 정보를 끝까지 보존하기

실무 품질을 좌우하는 부분은 토큰의 `kind`보다 `line`, `column`, `offset`입니다. 오류 메시지 품질은 여기서 결정됩니다.

```python
from dataclasses import dataclass
import re

@dataclass
class Token:
    kind: str
    text: str
    line: int
    col: int

TOKEN_PATTERNS = [
    ("NUMBER", r"\d+"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("WS", r"\s+"),
]

def lex(src: str) -> list[Token]:
    i = 0
    line, col = 1, 1
    out: list[Token] = []
    while i < len(src):
        for kind, pat in TOKEN_PATTERNS:
            m = re.match(pat, src[i:])
            if not m:
                continue
            text = m.group(0)
            if kind != "WS":
                out.append(Token(kind, text, line, col))
            for ch in text:
                if ch == "\n":
                    line += 1
                    col = 1
                else:
                    col += 1
            i += len(text)
            break
        else:
            raise SyntaxError(f"unexpected character '{src[i]}' at {line}:{col}")
    return out
```

### AST를 명시적으로 설계하기

파싱이 끝났을 때 결과가 문자열이 아니라 트리여야 이후 단계가 단순해집니다.

```python
from dataclasses import dataclass

@dataclass
class Number:
    value: int

@dataclass
class Binary:
    op: str
    left: object
    right: object

# 예시 AST: 2 + 3 * 4
ast = Binary(
    op="+",
    left=Number(2),
    right=Binary(op="*", left=Number(3), right=Number(4)),
)
```

여기서 중요한 관찰은 동일한 AST를 여러 소비자가 사용할 수 있다는 점입니다.
- 의미 분석기: 타입/스코프 검사
- 인터프리터: 즉시 평가
- 코드 생성기: 바이트코드/기계어 방출

즉 파서는 "한 번만 정확히" 만들고, 나머지는 AST 위에서 독립적으로 발전시킬 수 있습니다.

### 재귀 하강 파서의 최소 골격

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def eat(self, kind):
        tok = self.peek()
        if tok is None or tok.kind != kind:
            where = "EOF" if tok is None else f"{tok.line}:{tok.col}"
            raise SyntaxError(f"expected {kind} at {where}")
        self.i += 1
        return tok

    def parse_expr(self):
        node = self.parse_term()
        while self.peek() and self.peek().kind in ("PLUS", "MINUS"):
            op = self.eat(self.peek().kind).text
            rhs = self.parse_term()
            node = Binary(op, node, rhs)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() and self.peek().kind in ("MUL", "DIV"):
            op = self.eat(self.peek().kind).text
            rhs = self.parse_factor()
            node = Binary(op, node, rhs)
        return node

    def parse_factor(self):
        tok = self.peek()
        if tok.kind == "NUMBER":
            self.eat("NUMBER")
            return Number(int(tok.text))
        if tok.kind == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expr()
            self.eat("RPAREN")
            return node
        raise SyntaxError(f"unexpected token {tok.kind} at {tok.line}:{tok.col}")
```

### 디버깅 체크포인트

파이프라인을 운영할 때는 다음 세 지점을 항상 로그로 남겨야 합니다.
1. **Token stream**: 토큰 종류와 위치
2. **AST dump**: 중첩 구조와 연산자 결합 방향
3. **Type/Scope report**: 선언/참조 매칭 결과

세 지점이 분리되어 있으면 오류를 "문법 단계 문제"인지 "의미 단계 문제"인지 즉시 구분할 수 있습니다. 예를 들어 괄호 누락은 파서에서, 미선언 변수 참조는 의미 분석기에서 실패해야 정상입니다.

### 작은 입력으로 검증하는 습관

다음 세 입력을 고정 테스트로 유지하면 회귀를 빠르게 잡을 수 있습니다.
- `2 + 3 * 4` → 우선순위 검증
- `(2 + 3) * 4` → 괄호 우선 검증
- `2 + * 4` → 오류 위치와 메시지 품질 검증

이처럼 Lexer/Parser/AST를 분리한 뒤, 문법과 테스트를 함께 고정하면 이후 최적화나 코드 생성 단계를 추가해도 프런트엔드 품질이 쉽게 무너지지 않습니다.

## 처음 질문으로 돌아가기

- **문법적으로 맞다는 것과 의미적으로 맞다는 것은 어떻게 다를까요?**
  - 본문의 기준은 시맨틱 분석를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **이름 해석은 무엇이며, 식별자는 어디를 가리킬까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **타입 검사는 어떤 규칙으로 동작할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Compilers 101 (1/10): 컴파일러란 무엇인가?](./01-what-is-a-compiler.md)
- [Compilers 101 (2/10): 렉시컬 분석](./02-lexical-analysis.md)
- [Compilers 101 (3/10): 파싱과 AST](./03-parsing-and-ast.md)
- **시맨틱 분석 (현재 글)**
- 심볼 테이블과 스코프 (예정)
- 중간 표현 (예정)
- 최적화 기초 (예정)
- 코드 생성 (예정)
- JIT vs AOT (예정)
- 작은 인터프리터 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Crafting Interpreters — Resolving and Binding](https://craftinginterpreters.com/resolving-and-binding.html)
- [Type system (Wikipedia)](https://en.wikipedia.org/wiki/Type_system)
- [Name resolution (Wikipedia)](https://en.wikipedia.org/wiki/Name_resolution_(programming_languages))
- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/)

Tags: Computer Science, Compilers, SemanticAnalysis, TypeChecking, NameResolution
