---
series: computer-architecture-101
episode: 3
title: CPU와 명령어
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 컴퓨터 구조
  - CPU
  - 명령어
  - ISA
  - 어셈블리
seo_description: CPU의 fetch, decode, execute 사이클과 ISA, 어셈블리 명령어를 통해 컴퓨터의 실행 모델을 정리합니다.
last_reviewed: '2026-05-04'
---

# CPU와 명령어

> Computer Architecture 101 시리즈 (3/10)


## 이 글에서 다룰 문제

성능 최적화를 할 때, 결국 우리는 "이 코드가 몇 개의 명령어로 변하고, 그 명령어들이 한 사이클에 얼마나 빨리 처리되는가"를 다룹니다. CPU 사이클의 큰 그림이 없으면 프로파일러의 출력도 해석할 수 없고, 어셈블리를 한 번도 본 적이 없으면 컴파일러가 무엇을 잘 했고 무엇을 놓쳤는지 알 수 없습니다.

> 모든 고수준 코드는 결국 명령어의 나열입니다. 그 나열을 짧고 단순하게 만드는 것이 컴파일러와 우리의 공동 작업입니다.

## 전체 흐름
> CPU는 매 사이클마다 (1) PC가 가리키는 주소에서 명령어를 가져오고(fetch) (2) 그 비트 패턴을 해석해서(decode) (3) 실행합니다(execute). 한 명령어가 끝나면 PC가 다음 명령어를 가리킵니다. 분기 명령어는 PC를 다른 주소로 보냅니다.

```text
            +------ Fetch ------+
            |                   |
            |   PC --> Memory   |
            |        |          |
            |        v          |
            |   Instruction     |
            +---------+---------+
                      |
                      v
            +------ Decode -----+
            |   opcode + operand|
            +---------+---------+
                      |
                      v
            +------ Execute ----+
            | ALU / Mem / Branch|
            +-------------------+
```

## Before / After

**Before — "코드가 그냥 실행된다"는 모델:**

```python
def add(a, b):
    return a + b
```

**After — "이 함수는 몇 개의 명령어인가"라는 모델:**

```text
# x86-64 어셈블리 (단순화)
add:
    mov   rax, rdi      # 첫 인자(a)를 rax 레지스터로
    add   rax, rsi      # 두 번째 인자(b)를 더함
    ret                 # 결과를 반환

# 약 3개의 명령어, 약 3 사이클 (캐시 히트 가정)
```

같은 함수도 어셈블리 단계에서 보면 정확히 무엇이 일어나는지 보입니다.

## 단계별로 따라하기

### 1단계: 파이썬 함수의 바이트코드와 명령어 수 비교

```python
import dis

def add(a, b):
    return a + b

def add_with_check(a, b):
    if a < 0 or b < 0:
        return 0
    return a + b

print("--- add ---")
dis.dis(add)
print("--- add_with_check ---")
dis.dis(add_with_check)
```

조건 검사가 들어가면 명령어 수가 두세 배로 늘어납니다. 한 줄의 if는 어셈블리에선 비교, 분기, 점프의 조합입니다.

### 2단계: fetch-decode-execute를 시뮬레이터로 그려보기

```python
class TinyCPU:
    """간단한 CPU 시뮬레이터: 메모리, 레지스터, PC를 가짐"""
    def __init__(self, program):
        self.memory = list(program)
        self.regs = {"R0": 0, "R1": 0, "R2": 0}
        self.pc = 0

    def step(self):
        instr = self.memory[self.pc]   # fetch
        op, *args = instr              # decode
        if op == "MOV":
            self.regs[args[0]] = args[1]
        elif op == "ADD":
            self.regs[args[0]] = self.regs[args[1]] + self.regs[args[2]]
        elif op == "PRINT":
            print(self.regs[args[0]])
        self.pc += 1                   # PC 증가

cpu = TinyCPU([
    ("MOV", "R0", 3),
    ("MOV", "R1", 5),
    ("ADD", "R2", "R0", "R1"),
    ("PRINT", "R2"),
])
for _ in range(4):
    cpu.step()
```

CPU의 모든 동작은 이 세 단계의 반복입니다. 실제 CPU는 이 시뮬레이터의 1억 배쯤 빠르게 같은 일을 합니다.

### 3단계: 분기 명령어 추가

```python
class TinyCPU2(TinyCPU):
    def step(self):
        instr = self.memory[self.pc]
        op, *args = instr
        if op == "JMP":
            self.pc = args[0]          # PC를 직접 이동
            return
        if op == "JNZ":                # 0이 아니면 점프
            if self.regs[args[0]] != 0:
                self.pc = args[1]
                return
        super().step()
        return

cpu = TinyCPU2([
    ("MOV", "R0", 3),       # 0
    ("MOV", "R1", 0),       # 1
    ("ADD", "R1", "R1", "R0"),  # 2  R1 += R0
    # 실제 카운터 감소 명령은 생략(예시 단순화)
])
```

분기 명령어가 등장하면 PC가 단순히 +1되지 않습니다. 이것이 다음 글의 분기 예측과 파이프라인의 출발점입니다.

### 4단계: 명령어 종류 분류

```python
INSTRUCTION_CATEGORIES = {
    "산술/논리": ["ADD", "SUB", "MUL", "DIV", "AND", "OR", "XOR", "SHL", "SHR"],
    "메모리":    ["LOAD", "STORE", "MOV"],
    "분기":      ["JMP", "JNZ", "JE", "CALL", "RET"],
    "특수":      ["NOP", "HLT", "SYSCALL"],
}

for cat, ops in INSTRUCTION_CATEGORIES.items():
    print(f"{cat}: {', '.join(ops)}")
```

대부분의 ISA는 이 네 가지 범주의 명령어를 갖습니다. 차이는 명령어의 개수, 인코딩 방식, 사이클 비용입니다.

### 5단계: 컴파일러가 만든 진짜 어셈블리 보기

```python
# 다음 C 코드를 gcc -O2 -S 로 컴파일한 결과 (요약)
#
# int sum_to_n(int n) {
#     int s = 0;
#     for (int i = 1; i <= n; i++) s += i;
#     return s;
# }
#
# 컴파일러가 자동 최적화:
#   sum_to_n(n) = n * (n + 1) / 2
#
# x86-64 어셈블리 (대략):
#   lea     eax, [rdi + 1]
#   imul    eax, edi
#   sar     eax, 1
#   ret
```

루프가 통째로 곱셈 한 줄로 변하기도 합니다. 컴파일러는 명령어 수를 줄이는 데 매우 능숙하며, 우리가 그 결과를 읽을 줄 알면 협력이 쉬워집니다.

## 이 코드에서 주목할 점

- 모든 CPU는 fetch-decode-execute의 반복입니다
- 명령어는 opcode와 operand로 구성됩니다
- 분기 명령어는 PC를 직접 바꿉니다
- 컴파일러는 종종 우리가 짠 루프를 더 짧은 명령어 묶음으로 바꿉니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "한 줄 = 한 명령어" 가정 | 비용 추정 부정확 | dis 또는 어셈블리로 확인 |
| 분기를 가볍게 봄 | 예측 실패 시 큰 비용 | 핫 루프의 분기 수 줄이기 |
| 컴파일러 못 믿음 | 손최적화로 더 느려짐 | -O2 결과를 먼저 본다 |
| ISA = CPU라고 봄 | 같은 ISA도 칩별로 성능 다름 | 마이크로아키텍처도 본다 |
| 인터프리터 최적화에 의존 | 핫 패스가 느림 | 컴파일된 코드(C, Rust 등)로 |

## 실무에서는 이렇게 쓰입니다

- 게임 엔진: 핫 루프의 어셈블리를 직접 확인하고 SIMD 활용
- 컴파일러 개발: ISA에 맞게 명령어 선택과 스케줄링
- 임베디드 시스템: 명령어 수와 사이클 비용으로 실시간 보장
- 보안 분석: 디스어셈블러로 악성 코드의 명령어 흐름 추적
- 데이터베이스: 핵심 연산을 손튜닝한 어셈블리로 최적화

## 체크리스트

- [ ] fetch-decode-execute의 세 단계를 그릴 수 있는가
- [ ] 명령어가 opcode와 operand로 구성됨을 안다
- [ ] 분기 명령어가 PC를 바꾼다는 것을 이해했는가
- [ ] x86-64, ARM, RISC-V가 서로 다른 ISA임을 안다
- [ ] 자신의 코드 한 함수의 어셈블리를 한 번이라도 본 적이 있는가

## 정리 및 다음 단계

CPU는 메모리에서 명령어를 한 개씩 가져와 해석하고 실행하는 단순한 기계입니다. 그 단순함이 모든 추상화의 바닥에 있고, 성능을 진지하게 다루려면 한 번은 어셈블리 수준까지 내려가 봐야 합니다. ISA는 약속, 마이크로아키텍처는 구현이라는 구분을 기억하세요.

다음 글에서는 CPU 안에서 실제 계산이 일어나는 곳, 즉 레지스터와 ALU를 살펴봅니다. 명령어가 처리될 때 데이터가 어디에 잠시 머무는지, 그리고 ALU가 어떤 연산을 어떻게 수행하는지를 다룹니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- **CPU와 명령어 (현재 글)**
- 레지스터와 ALU (예정)
- 메모리 구조 (예정)
- 캐시와 지역성 (예정)
- 파이프라인 (예정)
- I/O와 장치 (예정)
- 병렬성과 멀티코어 (예정)
- 성능을 이해하는 법 (예정)
<!-- toc:end -->

## 참고 자료

- [Patterson & Hennessy — Computer Organization and Design](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Intel 64 and IA-32 Architectures Software Developer's Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation)
- [Compiler Explorer (godbolt.org)](https://godbolt.org/)
