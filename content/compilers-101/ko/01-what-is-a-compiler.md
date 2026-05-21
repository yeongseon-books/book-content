---
series: compilers-101
episode: 1
title: "Compilers 101 (1/10): 컴파일러란 무엇인가?"
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
  - Pipeline
  - AST
  - Bytecode
  - Frontend
seo_description: 소스 코드를 타깃 언어로 번역하는 컴파일러의 6단계 파이프라인 구조와 인터프리터의 차이점을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Compilers 101 (1/10): 컴파일러란 무엇인가?

이 글은 Compilers 101 시리즈의 첫 번째 글입니다.

`2 + 3 * 4` 같은 짧은 식이 왜 바로 실행되지 않고 여러 단계를 거쳐 번역되는지 이해하면, 컴파일러를 더 이상 마법 상자가 아니라 단계별 변환 시스템으로 보게 됩니다.


![Compilers 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/compilers-101/01/01-01-big-picture.ko.png)
*Compilers 101 1장 흐름 개요*

## 먼저 던지는 질문

- 컴파일러를 한 줄로 어떻게 정의할 수 있을까요?
- 표준적인 컴파일러 파이프라인은 어떤 단계로 나뉠까요?
- 인터프리터와 트랜스파일러는 이 파이프라인을 어디까지 공유할까요?

## 왜 중요한가

오류 메시지를 볼 때 “이건 문법 오류인가, 의미 오류인가?”, 빌드가 느릴 때 “최적화 단계가 병목인가?”, 새 언어가 어떻게 만들어지는지 이해할 때 “어느 단계가 추가되는가?” 같은 질문은 모두 파이프라인의 어느 지점에 서 있는지와 연결됩니다. 단계를 알아야 도구가 읽히고, 도구가 읽혀야 문제를 정확히 분해할 수 있습니다.

> 컴파일러를 안다는 것은 결국 “이 한 줄이 어디까지 번역됐고, 어디에서 멈췄는가?”를 답할 수 있다는 뜻입니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    A["source code"] --> B["lexer (tokens)"]
    B --> C["parser (AST)"]
    C --> D["semantic analyzer (types/scope)"]
    D --> E["intermediate representation"]
    E --> F["optimizer"]
    F --> G["code generator"]
    G --> H["target (bytecode/native)"]
```

위 여섯 단계는 그대로 이 시리즈의 목차이기도 합니다. 이후 글에서 각 단계를 하나씩 떼어 자세히 다룹니다.

## 핵심 용어

- **컴파일러**: 소스 언어를 타깃 언어로 번역하는 프로그램입니다.
- **인터프리터**: 소스 프로그램을 직접 실행하는 프로그램입니다. 보통 프런트엔드 단계는 컴파일러와 많이 겹칩니다.
- **트랜스파일러**: TypeScript → JavaScript처럼 추상화 수준이 비슷한 언어 사이를 번역하는 컴파일러입니다.
- **파이프라인**: 입력을 단계적으로 변환하는 구조입니다.
- **프런트엔드 / 백엔드**: 소스 언어에 가까운 단계 / 타깃에 가까운 단계입니다.

## 변경 전후

**Before — “컴파일은 마법”이라는 막연한 그림**

```text
.c → ??? → a.out
```

**After — 단계가 분리된 파이프라인**

```text
.c → lex → parse → check → IR → optimize → codegen → a.out
```

각 단계는 입력과 출력이 분명한 함수처럼 동작합니다. 이 분리가 바로 컴파일러를 이해하고 검증할 수 있게 만드는 힘입니다.

## 실습: 식 하나가 지나가는 전체 여정

### 1단계 — 토큰화: 텍스트를 의미 있는 조각으로 나누기

```python
# 1_lex.py
import re
from dataclasses import dataclass

@dataclass
class Token:
    kind: str
    text: str

PATTERNS = [
    ("NUM", r"\d+"),
    ("OP",  r"[+\-*/]"),
    ("WS",  r"\s+"),
]

def lex(src: str) -> list[Token]:
    tokens, i = [], 0
    while i < len(src):
        for kind, pat in PATTERNS:
            m = re.match(pat, src[i:])
            if m:
                if kind != "WS":
                    tokens.append(Token(kind, m.group()))
                i += m.end()
                break
        else:
            raise SyntaxError(src[i])
    return tokens

print(lex("2 + 3 * 4"))
```

문자열은 `[NUM 2, OP +, NUM 3, OP *, NUM 4]`처럼 의미 있는 단위로 바뀝니다.

### 2단계 — 파싱: 토큰을 트리로 바꾸기

```python
# 2_parse.py
from dataclasses import dataclass
@dataclass
class Num: value: int
@dataclass
class BinOp: op: str; left: object; right: object

# input: 2 + 3 * 4 (precedence ignored for this sketch)
def parse(tokens):
    def parse_expr(i):
        left = Num(int(tokens[i].text)); i += 1
        while i < len(tokens) and tokens[i].kind == "OP":
            op = tokens[i].text; i += 1
            right = Num(int(tokens[i].text)); i += 1
            left = BinOp(op, left, right)
        return left, i
    tree, _ = parse_expr(0)
    return tree

# Real precedence handling shows up in ep03. For now we just need a tree.
```

이제 입력은 텍스트가 아니라 트리가 됩니다. 의미를 묻고 타입을 따지고 최적화하기에 훨씬 좋은 형태입니다.

### 3단계 — 의미 분석: “이 표현은 말이 되는가?”

```python
# 3_check.py
def check(node):
    if isinstance(node, Num):
        return "int"
    t1 = check(node.left); t2 = check(node.right)
    if t1 != "int" or t2 != "int":
        raise TypeError("only int supported")
    return "int"
```

이 단계는 “타입이 맞는가?”, “변수가 선언됐는가?” 같은 질문을 처리합니다.

### 4단계 — 평가: 작은 인터프리터 만들기

```python
# 4_eval.py
def evaluate(node):
    if isinstance(node, Num):
        return node.value
    a, b = evaluate(node.left), evaluate(node.right)
    return {"+": a+b, "-": a-b, "*": a*b, "/": a//b}[node.op]
```

여기서 멈추면 이 프로그램은 **인터프리터**입니다. 같은 트리를 뒤 단계로 더 보내 코드로 내보내면 컴파일러가 됩니다.

### 5단계 — 코드 생성: 가짜 어셈블리 내보내기

```python
# 5_codegen.py
def emit(node, out=None):
    out = out if out is not None else []
    if hasattr(node, "value"):
        out.append(f"PUSH {node.value}")
        return out
    emit(node.left, out)
    emit(node.right, out)
    out.append({"+":"ADD","-":"SUB","*":"MUL","/":"DIV"}[node.op])
    return out
```

같은 AST에서 어셈블리나 바이트코드를 뽑아내는 순간이 바로 컴파일러의 마지막 단계입니다.

## 이 코드에서 먼저 봐야 할 점

- 같은 AST를 평가하면 인터프리터이고, 코드로 방출하면 컴파일러입니다.
- 각 단계의 입력과 출력이 분리돼 있어서 단위 테스트가 쉽습니다.
- 프런트엔드(lex → check)는 언어가 결정하고, 백엔드(IR → codegen)는 타깃이 결정합니다.
- 토큰과 AST는 텍스트보다 **추론하기 쉬운 형태**입니다.

## 자주 하는 실수 다섯 가지

1. **lexer와 parser를 한 함수에 섞는 것**입니다. 디버깅 난도가 급격히 올라갑니다.
2. **의미 분석을 원문 텍스트에서 바로 하려는 것**입니다. 우선순위와 중첩 구조가 무너집니다.
3. **타입 검사를 코드 생성에 섞는 것**입니다. 오류가 너무 늦게 드러납니다.
4. **인터프리터가 컴파일러보다 본질적으로 훨씬 단순하다고 믿는 것**입니다. 둘은 프런트엔드를 많이 공유합니다.
5. **에러에 line/column 정보를 붙이지 않는 것**입니다. 모든 단계는 원본 위치를 끝까지 들고 가야 합니다.

## 실무에서는 이렇게 나타납니다

같은 파이프라인은 GCC, Clang, V8, CPython, Babel, TypeScript 같은 실제 도구 안에 모두 들어 있습니다. LLVM은 이 구조를 백엔드 관점에서 가장 잘 모듈화한 대표 사례입니다. 사내 DSL을 만들 때도 패턴은 반복됩니다. `tokenize → parse → AST → walk`가 사실상 기본 골격입니다.

## 숙련된 엔지니어는 이렇게 봅니다

- 먼저 “프런트엔드는 어디서 끝나고 백엔드는 어디서 시작되는가?”를 묻습니다.
- 손수 파서를 쓰기 전에 PEG나 ANTLR 같은 도구를 검토합니다.
- 오류 메시지 품질을 단계 분리의 결과로 봅니다.
- AST 노드에 항상 위치 정보를 붙입니다.
- 인터프리터, 컴파일러, 트랜스파일러를 같은 그림의 변형으로 봅니다.

## 체크리스트

- [ ] 컴파일러를 한 줄로 정의할 수 있습니까?
- [ ] 여섯 단계 파이프라인을 직접 그릴 수 있습니까?
- [ ] 인터프리터가 어느 단계를 공유하는지 설명할 수 있습니까?
- [ ] AST가 왜 텍스트보다 다루기 쉬운지 한 줄로 말할 수 있습니까?
- [ ] 프런트엔드/백엔드 분리의 이점을 한 줄로 설명할 수 있습니까?

## 연습 문제

1. 위 1~5단계를 한 스크립트로 합쳐 `2 + 3 * 4`에 대해 토큰, AST, 계산 결과(`14`), 가짜 어셈블리를 모두 출력해 보세요.
2. 같은 코드에 CLI 플래그를 추가해서 인터프리터 모드와 코드 생성 모드를 전환해 보세요.
3. 자주 쓰는 언어 하나를 골라 프런트엔드/백엔드 경계가 어디인지 한 단락으로 설명해 보세요.

## 정리와 다음 글

컴파일러는 여러 단계를 분해해서 볼 때 비로소 구조가 보이는 시스템입니다. 다음 글에서는 그 첫 단계인 lexical analysis를 자세히 보며, 텍스트가 어떻게 토큰이 되는지 다룹니다.

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

- **컴파일러를 한 줄로 어떻게 정의할 수 있을까요?**
  - 본문의 기준은 컴파일러란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **표준적인 컴파일러 파이프라인은 어떤 단계로 나뉠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **인터프리터와 트랜스파일러는 이 파이프라인을 어디까지 공유할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **컴파일러란 무엇인가? (현재 글)**
- 렉시컬 분석 (예정)
- 파싱과 AST (예정)
- 시맨틱 분석 (예정)
- 심볼 테이블과 스코프 (예정)
- 중간 표현 (예정)
- 최적화 기초 (예정)
- 코드 생성 (예정)
- JIT vs AOT (예정)
- 작은 인터프리터 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Compilers: Principles, Techniques, and Tools (Aho et al.)](https://suif.stanford.edu/dragonbook/)
- [Crafting Interpreters (Robert Nystrom)](https://craftinginterpreters.com/)
- [LLVM Project](https://llvm.org/)
- [PEP 339 — Design of the CPython compiler](https://peps.python.org/pep-0339/)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/compilers-101/ko)

Tags: Computer Science, Compilers, Pipeline, AST, Bytecode, Frontend
