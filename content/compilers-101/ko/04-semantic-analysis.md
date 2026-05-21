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

이 글은 Compilers 101 시리즈의 네 번째 글입니다.

문법은 맞지만 의미가 틀린 코드가 왜 거부되는지 이해하는 순간, 컴파일러가 단순한 문장 검사기가 아니라 프로그램 의미를 판정하는 도구라는 점이 분명해집니다.


![Compilers 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/compilers-101/04/04-01-big-picture.ko.png)
*Compilers 101 4장 흐름 개요*

## 먼저 던지는 질문

- 문법적으로 맞다는 것과 의미적으로 맞다는 것은 어떻게 다를까요?
- 이름 해석은 무엇이며, 식별자는 어디를 가리킬까요?
- 타입 검사는 어떤 규칙으로 동작할까요?

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

## 변경 전후

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

## 정리와 다음 글

시맨틱 분석은 문법만으로는 답할 수 없는 “이 코드가 정말 의미가 맞는가?”라는 질문에 답하는 단계입니다. 다음 글에서는 이 단계의 핵심 도구인 symbol table과 scope를 더 집중해서 살펴봅니다.

## 확장 실습: 프런트엔드부터 LLVM IR 직전까지 한 번에 검증하기

이 시점부터는 단계별 조각 실습을 넘어, 한 입력이 토큰, AST, 타입 정보, IR, 최적화 결과, 코드 생성 결과로 어떻게 이어지는지 한 번에 추적하는 연습이 필요합니다. 핵심은 코드 길이가 아니라 **변환 경계가 보이는 출력**을 남기는 것입니다. 아래 예시는 시리즈 전체를 관통하는 최소 골격입니다.

### 문법 고정: BNF 표기 먼저 확정하기

문법이 흔들리면 파서와 의미 분석 경계도 함께 흔들립니다. 구현 전에 BNF를 먼저 잠그면 우선순위, 결합성, 허용 구문을 팀 단위로 공유할 수 있습니다.

```bnf
<program> ::= <stmt_list>
<stmt_list> ::= <stmt> | <stmt> <stmt_list>
<stmt> ::= "let" <ident> "=" <expr> ";" | "print" <expr> ";"
<expr> ::= <term> | <expr> "+" <term> | <expr> "-" <term>
<term> ::= <factor> | <term> "*" <factor> | <term> "/" <factor>
<factor> ::= <number> | <ident> | "(" <expr> ")"
```

### 렉서 출력 고정: 토큰과 위치 정보를 함께 기록하기

```python
from dataclasses import dataclass
import re

@dataclass
class Token:
    kind: str
    text: str
    line: int
    col: int

SPEC = [
    ("KW", r"\b(let|print)\b"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("NUMBER", r"\d+"),
    ("OP", r"[+\-*/=]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SEMI", r";"),
    ("WS", r"[ \t\n]+"),
]

def lex(src: str) -> list[Token]:
    out: list[Token] = []
    i, line, col = 0, 1, 1
    while i < len(src):
        for kind, pat in SPEC:
            m = re.match(pat, src[i:])
            if not m:
                continue
            text = m.group(0)
            if kind != "WS":
                out.append(Token(kind, text, line, col))
            for ch in text:
                if ch == "
":
                    line += 1
                    col = 1
                else:
                    col += 1
            i += len(text)
            break
        else:
            raise SyntaxError(f"unexpected character {src[i]!r} at {line}:{col}")
    return out
```

이 출력은 이후 단계에서 오류 메시지 기준 좌표가 됩니다. line/col 정보가 없으면 파서와 의미 분석 품질을 끝까지 올리기 어렵습니다.

### AST 노드 정의: 구조를 명시적으로 분리하기

```python
from dataclasses import dataclass

@dataclass
class Number:
    value: int

@dataclass
class Identifier:
    name: str

@dataclass
class Binary:
    op: str
    left: object
    right: object

@dataclass
class LetStmt:
    name: str
    expr: object

@dataclass
class PrintStmt:
    expr: object
```

여기서 중요한 점은 문법 요소와 실행 요소를 섞지 않는 것입니다. AST는 실행기가 아니라 구조 표현이어야 하며, 해석/타입/코드 생성은 별도 단계로 분리하는 편이 장기적으로 안정적입니다.

### 의미 분석 골격: 선언, 참조, 타입을 한 번에 점검하기

```python
class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.table: dict[str, str] = {}

    def define(self, name: str, ty: str):
        if name in self.table:
            raise TypeError(f"redeclared variable: {name}")
        self.table[name] = ty

    def resolve(self, name: str) -> str:
        if name in self.table:
            return self.table[name]
        if self.parent:
            return self.parent.resolve(name)
        raise NameError(f"undefined variable: {name}")

def type_of_expr(node, scope: Scope) -> str:
    if isinstance(node, Number):
        return "int"
    if isinstance(node, Identifier):
        return scope.resolve(node.name)
    if isinstance(node, Binary):
        lt = type_of_expr(node.left, scope)
        rt = type_of_expr(node.right, scope)
        if lt != "int" or rt != "int":
            raise TypeError(f"binary op expects int/int, got {lt}/{rt}")
        return "int"
    raise TypeError(f"unknown node: {node}")
```

시맨틱 단계에서 타입과 이름 해석을 확정하면, 뒤 단계(IR/최적화/코드 생성)는 오류 복구 부담을 크게 줄일 수 있습니다.

### IR 생성과 최적화 패스: 변환 파이프라인 분리하기

```python
def lower_expr(node, out, new_temp):
    if isinstance(node, Number):
        t = new_temp()
        out.append(("const", t, node.value))
        return t
    if isinstance(node, Identifier):
        t = new_temp()
        out.append(("load", t, node.name))
        return t
    if isinstance(node, Binary):
        l = lower_expr(node.left, out, new_temp)
        r = lower_expr(node.right, out, new_temp)
        t = new_temp()
        out.append((node.op, t, l, r))
        return t
    raise RuntimeError("unsupported node")

def constant_folding(ir):
    const = {}
    out = []
    for inst in ir:
        if inst[0] == "const":
            const[inst[1]] = inst[2]
            out.append(inst)
            continue
        if inst[0] in {"+", "-", "*", "/"} and inst[2] in const and inst[3] in const:
            a, b = const[inst[2]], const[inst[3]]
            v = {"+": a+b, "-": a-b, "*": a*b, "/": a//b}[inst[0]]
            const[inst[1]] = v
            out.append(("const", inst[1], v))
        else:
            out.append(inst)
    return out
```

`IR -> 최적화 패스 -> IR` 형태를 유지하면 패스를 안전하게 합성할 수 있고, 결과 비교 테스트도 단순해집니다.

### 코드 생성 스니펫: 단순 스택 머신 또는 어셈블리로 내리기

```python
def emit_stack_vm(ir):
    out = []
    for inst in ir:
        op = inst[0]
        if op == "const":
            out.append(f"PUSH {inst[2]}")
        elif op == "load":
            out.append(f"LOAD {inst[2]}")
        elif op == "+":
            out.append("ADD")
        elif op == "-":
            out.append("SUB")
        elif op == "*":
            out.append("MUL")
        elif op == "/":
            out.append("DIV")
    out.append("HALT")
    return out
```

이 수준의 생성기만 있어도 파서/의미 분석/최적화의 결과가 실제 실행 지시어로 어떻게 바뀌는지 빠르게 검증할 수 있습니다.

### LLVM IR 샘플 읽기: SSA 감각 익히기

```llvm
; 입력 소스의 개념: let x = 2 * 3; print x + 1;
define i32 @main() {
entry:
  %x = mul i32 2, 3
  %y = add i32 %x, 1
  ret i32 %y
}
```

SSA에서 `%x`, `%y`처럼 버전이 분리되면 데이터 흐름 분석과 레지스터 할당 전 단계가 단순해집니다. 시리즈 후반 주제(최적화, 코드 생성, JIT/AOT)를 이해할 때 이 표현이 공통 언어가 됩니다.

### 검증 기준: 단계별 스냅샷을 항상 남기기

실전에서는 정답 코드보다 검증 루틴이 먼저입니다. 최소한 다음 다섯 가지를 파일로 남기면 회귀를 추적하기 쉽습니다.

1. 토큰 덤프 (`tokens.json`)
2. AST 덤프 (`ast.json`)
3. 시맨틱 결과 (`symbols.json`, 타입 오류 목록)
4. 최적화 전후 IR (`ir_before.txt`, `ir_after.txt`)
5. 최종 코드 생성 결과 (`out.asm` 또는 `out.vm`)

이렇게 하면 “어디서 깨졌는지”가 즉시 분리되고, 팀 협업에서도 디버깅 비용이 크게 줄어듭니다.


### 단계별 실패 시나리오와 복구 전략

실제 프로젝트에서는 정답 입력보다 실패 입력이 더 많이 들어옵니다. 따라서 각 단계가 실패했을 때 **다음 단계로 무엇을 전달할지**를 먼저 정해야 합니다. 다음 표는 최소 운영 기준입니다.

| 단계 | 실패 예시 | 즉시 조치 | 다음 단계 전달 |
| --- | --- | --- | --- |
| 렉서 | 알 수 없는 문자 | 위치 포함 오류 생성 | 복구 가능한 토큰만 전달 |
| 파서 | 괄호 누락, 세미콜론 누락 | 동기화 토큰 기준으로 재시작 | 부분 AST와 오류 목록 전달 |
| 시맨틱 | 미선언 변수, 타입 불일치 | 심볼/타입 오류 축적 | 오류 수가 기준치 이하면 IR 생성 계속 |
| IR 생성 | 미지원 구문 | 노드 단위 경고와 스킵 | 분석 가능한 블록만 전달 |
| 최적화 | 패스 전제 위반 | 패스 비활성화 후 원본 IR 유지 | 코드 생성은 계속 |
| 코드 생성 | 레지스터 부족 | spill 강제, 속도 저하 허용 | 실행 가능한 바이너리 우선 |

이 기준은 "완벽한 컴파일"보다 "재현 가능한 컴파일"에 가깝습니다. 품질이 높은 컴파일러는 한 번에 많은 오류를 보여 주되, 어디까지 복구했는지 명확히 보고합니다.

### 테스트 입력 세트: 경계 조건을 먼저 고정하기

아래 입력 세트는 단계별 회귀를 빠르게 잡는 최소 묶음입니다.

```text
# 정상
let x = 2 + 3 * 4;
print x;

# 문법 오류
let x = (2 + 3;

# 의미 오류
print y;

# 최적화 검증
let z = 1 + 2 + 3 + 4;
print z;
```

각 입력에 대해 토큰, AST, 시맨틱 결과, IR, 최종 코드를 별도 파일로 남기면 변경 전후 차이를 기계적으로 비교할 수 있습니다.

### 간단한 골든 출력 비교 스크립트

```python
import json
from pathlib import Path

def save_snapshot(name: str, payload):
    out_dir = Path("artifacts")
    out_dir.mkdir(exist_ok=True)
    p = out_dir / f"{name}.json"
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

# 예시 사용
save_snapshot("tokens_case1", [{"kind": "NUMBER", "text": "2", "line": 1, "col": 1}])
save_snapshot("ast_case1", {"kind": "Binary", "op": "+"})
```

스냅샷 파일을 Git에 남기면 리팩터링 이후에도 파이프라인의 의미가 바뀌었는지 즉시 검출할 수 있습니다.

### 최적화 패스 예시: 상수 전파와 불필요 대입 제거

```python
def constant_propagation(ir):
    env = {}
    out = []
    for inst in ir:
        op = inst[0]
        if op == "const":
            env[inst[1]] = inst[2]
            out.append(inst)
        elif op in {"+", "-", "*", "/"}:
            a = env.get(inst[2], inst[2])
            b = env.get(inst[3], inst[3])
            if isinstance(a, int) and isinstance(b, int):
                v = {"+": a+b, "-": a-b, "*": a*b, "/": a//b}[op]
                env[inst[1]] = v
                out.append(("const", inst[1], v))
            else:
                out.append((op, inst[1], a, b))
        else:
            out.append(inst)
    return out

def remove_trivial_moves(ir):
    return [inst for inst in ir if not (inst[0] == "mov" and inst[1] == inst[2])]
```

최적화는 큰 패스 하나보다 작은 패스 여러 개가 유지보수에 유리합니다. 실패하면 해당 패스만 끄고 원본 IR로 복구할 수 있기 때문입니다.

### 코드 생성 검증: 간단한 레지스터 할당 로그 남기기

```python
REGS = ["r1", "r2", "r3"]

def assign_registers(temporaries):
    mapping = {}
    spill = []
    for t in temporaries:
        if len(mapping) < len(REGS):
            mapping[t] = REGS[len(mapping)]
        else:
            spill.append(t)
    return mapping, spill

m, s = assign_registers(["t1", "t2", "t3", "t4", "t5"])
print("reg-map", m)
print("spill ", s)
```

이 정도 로그만 있어도 특정 입력에서 왜 성능이 급락했는지 원인을 좁히기 쉽습니다. 특히 spill 급증은 코드 생성 병목의 대표 신호입니다.

### LLVM IR 비교 기준: 변경 전후를 줄 단위로 확인하기

```llvm
; before optimization
%t1 = mul i32 3, 4
%t2 = add i32 2, %t1
ret i32 %t2

; after optimization
ret i32 14
```

최적화가 의미를 보존하는지 검증할 때는 사람이 읽는 설명보다 IR diff가 더 신뢰할 수 있습니다. 동일 입력에서 `ret i32 14`로 바뀌면 folding이 실제로 적용되었음을 바로 확인할 수 있습니다.

### 팀 운영 체크포인트

1. 파서 변경 PR에는 반드시 BNF 변경 diff를 포함합니다.
2. 시맨틱 규칙 변경 PR에는 실패 사례 3개 이상을 테스트에 추가합니다.
3. 최적화 패스 추가 PR에는 비활성화 플래그를 함께 제공합니다.
4. 코드 생성 변경 PR에는 최소 두 아키텍처 이상의 스냅샷을 첨부합니다.
5. 릴리스 전에는 동일 입력에 대해 인터프리터 결과와 컴파일 결과를 교차 검증합니다.

이 체크포인트를 유지하면 기능 추가 속도보다 품질 일관성을 더 안정적으로 가져갈 수 있습니다.


### 마무리 점검: 단계 경계를 말로 설명해 보기

마지막으로, 구현을 잠시 멈추고 다음 질문에 답해 보기를 권합니다. 이 질문은 코드량이 아니라 이해도를 검증합니다.

- 렉서가 실패했을 때 파서가 받는 입력은 무엇입니까?
- 파서가 복구한 부분 AST를 시맨틱 단계에서 어디까지 신뢰합니까?
- 시맨틱 오류가 있어도 IR 생성을 계속할 조건은 무엇입니까?
- 최적화 패스를 껐을 때도 결과의 의미가 유지되는지 어떻게 확인합니까?
- 코드 생성 이후 실행 결과를 어떤 기준값과 비교합니까?

이 다섯 질문에 팀이 같은 답을 할 수 있으면, 파이프라인 확장 시 품질이 급격히 흔들릴 가능성이 크게 줄어듭니다. 반대로 답이 제각각이면, 새로운 문법이나 최적화 패스를 추가할 때 같은 종류의 회귀가 반복됩니다.

실무에서는 기능 추가보다 경계 합의가 먼저입니다. 경계를 합의한 다음 기능을 추가하면, 동일한 투자로 더 안정적인 컴파일러를 만들 수 있습니다.

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

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/compilers-101/ko)

Tags: Computer Science, Compilers, SemanticAnalysis, TypeChecking, NameResolution
