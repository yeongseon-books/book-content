---
series: compilers-101
episode: 7
title: "Compilers 101 (7/10): 최적화 기초"
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
  - Optimization
  - ConstantFolding
  - DeadCode
seo_description: 프로그램의 의미를 보존하면서 성능을 개선하는 컴파일러 최적화의 원리와 주요 패스 구현 방법을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Compilers 101 (7/10): 최적화 기초

이 글은 Compilers 101 시리즈의 일곱 번째 글입니다.

컴파일러가 `2 + 3 * 4`를 실행할 때마다 계산하지 않고 미리 `14`로 바꿔 둘 수 있다는 사실을 이해하면, 최적화가 “더 빠르게”만이 아니라 “의미를 절대 바꾸지 않으면서” 수행되는 정교한 변환이라는 점이 드러납니다.

![Compilers 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/compilers-101/07/07-01-big-picture.ko.png)
*Compilers 101 7장 흐름 개요*

## 먼저 던지는 질문

- 최적화에서 가장 절대적인 규칙은 무엇일까요?
- constant folding은 어떤 식으로 동작할까요?
- dead code elimination은 어떤 정보를 기반으로 할까요?

## 왜 중요한가

같은 알고리즘이라도 최적화가 잘 되면 10배 빠르게 돌거나 크기가 10분의 1로 줄 수 있습니다. 반대로 잘못된 최적화는 프로그램 의미 자체를 바꿔 버립니다. 그래서 최적화기는 성능 도구이면서 동시에 신뢰성 시험대이기도 합니다.

> “더 빠르게, 그러나 의미는 그대로.” 이 두 조건을 동시에 지키는 것이 최적화기의 일입니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    A["IR"] --> B["constant folding"]
    B --> C["dead code elim"]
    C --> D["CSE"]
    D --> E["optimized IR"]
```

각 패스는 IR을 받아 IR을 내보냅니다. 그래서 작은 변환을 여러 개 합성할 수 있습니다.

## 핵심 용어

- **패스(pass)**: IR을 한 번 순회하며 수행하는 변환입니다.
- **constant folding**: 상수끼리의 계산을 컴파일 시점에 미리 수행하는 최적화입니다.
- **dead code elimination**: 결과가 전혀 사용되지 않는 코드를 제거하는 최적화입니다.
- **common subexpression elimination**: 동일한 표현식의 중복 계산을 제거하는 최적화입니다.
- **strength reduction**: `x * 2`를 `x + x`나 `x << 1`로 바꾸는 식의 저비용 연산 대체입니다.

## 변경 전후

**Before — 순진한 IR**

```text
t1 = 2 * 3
t2 = 1 + t1
t3 = t2
return t3
```

**After — 최적화된 IR**

```text
return 7
```

결과는 같지만 명령어 수는 4개에서 1개로 줄어듭니다.

## 실습: 작은 최적화기 만들기

### 1단계 — IR 명령어 표현

```python
# 1_inst.py
# (op, dst, src1, src2) 튜플 단위로 처리합니다.
code = [
    ("LOAD", "t1", 2, None),
    ("LOAD", "t2", 3, None),
    ("*",    "t3", "t1", "t2"),
    ("LOAD", "t4", 1, None),
    ("+",    "t5", "t4", "t3"),
    ("RET",  None, "t5", None),
]
```

대부분의 변환은 결국 이런 평평한 리스트를 대상으로 동작합니다.

### 2단계 — constant folding

```python
# 2_fold.py
def fold(code):
    consts = {}
    out = []
    for op, dst, a, b in code:
        if op == "LOAD" and isinstance(a, int):
            consts[dst] = a; out.append((op, dst, a, b)); continue
        if op in "+-*/" and a in consts and b in consts:
            v = {"+":consts[a]+consts[b],"-":consts[a]-consts[b],
                 "*":consts[a]*consts[b],"/":consts[a]//consts[b]}[op]
            consts[dst] = v
            out.append(("LOAD", dst, v, None))
        else:
            out.append((op, dst, a, b))
    return out
```

상수 환경을 유지하면서 양쪽 피연산자가 모두 상수면 그 자리에서 계산해 버립니다.

### 3단계 — dead code elimination

```python
# 3_dce.py
def dce(code):
    used = set()
    # 아래에서 위로 use 정보를 수집합니다.
    for op, dst, a, b in reversed(code):
        if op == "RET":
            used.add(a)
        else:
            if dst in used:
                if isinstance(a, str): used.add(a)
                if isinstance(b, str): used.add(b)
    # 한 번 더 순회해 live instruction만 남깁니다.
    return [(op, dst, a, b) for op, dst, a, b in code
            if op == "RET" or dst in used]
```

아래에서 위로 사용 정보를 모은 뒤, 결과가 쓰이지 않는 명령어를 버립니다.

### 4단계 — 패스 조합하기

```python
# 4_pipeline.py
def optimize(code):
    code = fold(code)
    code = dce(code)
    return code

for inst in optimize(code): print(inst)
```

패스는 함수처럼 조합할 수 있습니다. 같은 패스를 두 번 이상 돌리면 더 줄어드는 경우도 많습니다.

### 5단계 — CSE의 직관

```python
# 5_cse.py
# 같은 right-hand side가 두 번 나타난 경우
# t1 = a + b
# t2 = a + b   <- same expression
# 두 번째 줄을 t2 = t1로 바꿉니다.
```

`(op, src1, src2) → dst` 형태의 해시 테이블만 있어도 기본 아이디어는 구현됩니다. SSA 형태에서는 특히 더 단순해집니다.

## 이 코드에서 먼저 봐야 할 점

- 모든 패스는 IR → IR 변환입니다.
- 각 패스는 작고 단순해야 합니다.
- 패스 순서는 결과 품질에 영향을 줍니다.
- “고정점까지 반복 실행” 패턴이 매우 흔합니다.

## 자주 하는 실수 다섯 가지

1. **부작용을 무시한 DCE를 하는 것**입니다. I/O 호출은 결과가 안 쓰여도 살아 있어야 합니다.
2. **부동소수점 계산을 무심코 folding하는 것**입니다. 결합법칙이 깨질 수 있습니다.
3. **분기 구조를 무시한 CSE를 하는 것**입니다. 같은 식이라도 basic block이 다르면 값이 다를 수 있습니다.
4. **패스 순서를 고민하지 않는 것**입니다. 보통 `fold → dce` 순서가 안전한 출발점입니다.
5. **한 번만 실행하고 끝내는 것**입니다. folding이 새 dead code를 만들고, DCE가 새 folding 기회를 만들 수 있습니다.

## 실무에서는 이렇게 나타납니다

LLVM에는 수십 개의 패스가 있으며, `-O2`, `-O3` 같은 플래그는 어떤 패스를 어떤 순서로 돌릴지 묶어 둔 설정입니다. JIT 컴파일러는 hot path에 더 공격적인 최적화를 적용하고, PGO는 실제 실행 데이터를 바탕으로 패스 선택을 더 정교하게 합니다.

## 숙련된 엔지니어는 이렇게 봅니다

- 새 패스를 추가하기 전에 먼저 의미 보존을 검증합니다.
- 패스를 작고 단일 책임으로 유지합니다.
- 고정점 반복이 흔한 패턴이라는 점을 압니다.
- 추측보다 프로파일 기반 판단을 신뢰합니다.
- “이 변환이 어떤 아키텍처에서 실제 이득을 내는가?”를 항상 묻습니다.

## 체크리스트

- [ ] 의미 보존이 최적화의 절대 규칙이라는 점을 받아들였습니까?
- [ ] constant folding을 한 페이지 안에 직접 쓸 수 있습니까?
- [ ] DCE가 사용 정보 분석에서 나온다는 점을 설명할 수 있습니까?
- [ ] 패스 순서가 왜 결과에 영향을 주는지 설명할 수 있습니까?
- [ ] SSA에서 CSE가 더 쉬워지는 직관을 갖고 있습니까?

## 연습 문제

1. 위 `fold`에 strength reduction(`x * 2 → x + x`)을 추가해 보세요.
2. `fold + dce`를 더 이상 줄어들지 않을 때까지 반복하는 고정점 루프를 작성해 보세요.
3. `PRINT`, `STORE` 같은 부작용 명령어를 추가하고 DCE가 지우지 않도록 만들어 보세요.

## 정리와 다음 글

최적화는 IR 위에서 돌아가는 의미 보존 변환들의 연속입니다. 다음 글에서는 이 최적화된 IR을 실제 CPU 명령어로 바꾸는 마지막 단계, code generation을 다룹니다.

## 처음 질문으로 돌아가기

- **최적화에서 가장 절대적인 규칙은 무엇일까요?**
  - 본문의 기준은 최적화 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **constant folding은 어떤 식으로 동작할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **dead code elimination은 어떤 정보를 기반으로 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Compilers 101 (1/10): 컴파일러란 무엇인가?](./01-what-is-a-compiler.md)
- [Compilers 101 (2/10): 렉시컬 분석](./02-lexical-analysis.md)
- [Compilers 101 (3/10): 파싱과 AST](./03-parsing-and-ast.md)
- [Compilers 101 (4/10): 시맨틱 분석](./04-semantic-analysis.md)
- [Compilers 101 (5/10): 심볼 테이블과 스코프](./05-symbol-table-and-scope.md)
- [Compilers 101 (6/10): 중간 표현](./06-intermediate-representation.md)
- **최적화 기초 (현재 글)**
- 코드 생성 (예정)
- JIT vs AOT (예정)
- 작은 인터프리터 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- Alfred V. Aho, Monica S. Lam, Ravi Sethi, Jeffrey D. Ullman, *Compilers: Principles, Techniques, and Tools* (2nd ed.), optimization chapters.
- Keith D. Cooper, Linda Torczon, *Engineering a Compiler* (2nd ed.), scalar-optimization and data-flow chapters.
- [LLVM’s Analysis and Transform Passes](https://llvm.org/docs/Passes.html)
- [LLVM — Using the New Pass Manager](https://llvm.org/docs/NewPassManager.html) — 기본 최적화 파이프라인과 패스 구성 방식.

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/compilers-101/ko)

Tags: Computer Science, Compilers, Optimization, ConstantFolding, DeadCode
