---
series: computer-architecture-101
episode: 3
title: CPU와 명령어
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
  - 컴퓨터 구조
  - CPU
  - 명령어
  - ISA
  - 어셈블리
seo_description: CPU의 fetch-decode-execute 사이클과 ISA가 코드를 어떻게 명령어로 바꾸는지 설명합니다.
last_reviewed: '2026-05-12'
---

# CPU와 명령어

고수준 코드는 친절하지만, CPU는 결국 명령어만 읽습니다. 이 글은 Computer Architecture 101 시리즈의 세 번째 글입니다. 여기서는 CPU가 한 사이클마다 실제로 무엇을 하는지, 그리고 우리가 작성한 코드가 어떤 명령어의 나열로 바뀌는지 fetch-decode-execute 관점에서 정리하겠습니다.

성능 최적화는 결국 "이 코드는 몇 개의 명령어가 되었고, CPU는 그것을 얼마나 빨리 처리하는가"로 수렴합니다. 이 사이클을 머릿속에 넣어 두면 프로파일러 출력과 어셈블리 리스트가 비로소 읽히기 시작합니다.

## 이 글에서 다룰 문제

- CPU는 한 사이클에 정확히 무엇을 할까요?
- ISA는 무엇을 약속하는 계약일까요?
- 명령어는 opcode와 operand로 어떻게 구성될까요?
- 분기 명령어는 프로그램 흐름을 어떻게 바꿀까요?

> 모든 고수준 코드는 결국 명령어의 연속이며, CPU는 그 명령어를 가져오고 해석하고 실행하는 일을 반복합니다.

## 왜 중요한가

성능 작업은 결국 명령어 수준으로 내려갑니다. 코드가 몇 개의 명령어로 변했는지, 그 명령어가 메모리 접근을 얼마나 포함하는지, 분기가 얼마나 많은지가 실제 실행 시간을 바꿉니다.

따라서 CPU 사이클을 모르면 프로파일러 결과가 흐릿하고, 어셈블리를 한 번도 읽어 보지 않았다면 컴파일러가 무엇을 잘했는지 놓쳤는지 판단하기 어렵습니다.

## 한눈에 보는 개념

CPU는 매 사이클마다 PC가 가리키는 주소의 명령어를 가져오고, 비트 패턴을 해석하고, 실행합니다. 분기가 없다면 PC는 다음 명령어로 이동하고, 분기가 있다면 다른 주소로 점프합니다.

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

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| ISA | 명령어 형식과 의미를 정의하는 계약 |
| opcode | 무엇을 할지 나타내는 부분 |
| operand | 어디에 적용할지 나타내는 부분 |
| PC | 다음 명령어 주소를 가리키는 프로그램 카운터 |
| Branch | PC를 다른 곳으로 보내는 명령어 |
| Cycle | CPU의 한 박자 |

## Before / After

**Before — "코드가 그냥 실행된다":**

```python
def add(a, b):
    return a + b
```

**After — "이 함수는 몇 개의 명령어인가":**

```text
# x86-64 assembly (simplified)
add:
    mov   rax, rdi      # first argument (a) into rax
    add   rax, rsi      # add the second argument (b)
    ret                 # return the result

# ~3 instructions, ~3 cycles (cache hits assumed)
```

같은 함수라도 어셈블리 계층에서 보면 비용 구조가 더 분명해집니다.

## 단계별로 따라가기

### 1단계: 바이트코드 비교하기

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

작은 `if` 하나도 비교, 분기, 점프를 늘립니다. 조건 검사는 명령어 수를 빠르게 키웁니다.

### 2단계: 작은 fetch-decode-execute 시뮬레이터 만들기

```python
class TinyCPU:
    """Toy CPU: memory, registers, and PC."""
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
        self.pc += 1                   # advance PC

cpu = TinyCPU([
    ("MOV", "R0", 3),
    ("MOV", "R1", 5),
    ("ADD", "R2", "R0", "R1"),
    ("PRINT", "R2"),
])
for _ in range(4):
    cpu.step()
```

실제 CPU도 본질적으로는 이 흐름의 반복입니다. 물론 실제 속도와 복잡도는 훨씬 큽니다.

### 3단계: 분기 명령어 추가하기

```python
class TinyCPU2(TinyCPU):
    def step(self):
        instr = self.memory[self.pc]
        op, *args = instr
        if op == "JMP":
            self.pc = args[0]          # move PC directly
            return
        if op == "JNZ":                # jump if non-zero
            if self.regs[args[0]] != 0:
                self.pc = args[1]
                return
        super().step()
        return
```

분기가 들어오면 PC는 더 이상 단순히 `+1`로 움직이지 않습니다. 이 지점이 파이프라인과 분기 예측의 출발점입니다.

### 4단계: 명령어 종류 나누기

```python
INSTRUCTION_CATEGORIES = {
    "Arithmetic/Logic": ["ADD", "SUB", "MUL", "DIV", "AND", "OR", "XOR", "SHL", "SHR"],
    "Memory":           ["LOAD", "STORE", "MOV"],
    "Branch":           ["JMP", "JNZ", "JE", "CALL", "RET"],
    "Special":          ["NOP", "HLT", "SYSCALL"],
}

for cat, ops in INSTRUCTION_CATEGORIES.items():
    print(f"{cat}: {', '.join(ops)}")
```

ISA마다 세부 내용은 달라도, 대개 산술/논리, 메모리, 분기, 특수 명령이라는 큰 범주는 비슷합니다.

### 5단계: 실제 컴파일러 출력 읽기

```text
# C source compiled with gcc -O2 -S (excerpt)
#
# int sum_to_n(int n) {
#     int s = 0;
#     for (int i = 1; i <= n; i++) s += i;
#     return s;
# }
#
# The compiler rewrites the loop as n * (n + 1) / 2:
#
#   lea     eax, [rdi + 1]
#   imul    eax, edi
#   sar     eax, 1
#   ret
```

루프 전체가 곱셈과 시프트 몇 개로 줄어듭니다. 컴파일러는 명령어 수를 줄이는 데 매우 강합니다.

## 이 코드에서 먼저 봐야 할 점

- 모든 CPU는 fetch-decode-execute를 반복합니다.
- 명령어는 opcode와 operand의 조합입니다.
- 분기 명령어는 PC를 직접 바꿉니다.
- 컴파일러는 코드를 더 짧은 명령어 시퀀스로 바꾸는 데 능숙합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 코드 한 줄 = 명령어 한 개라고 생각 | 비용 추정이 틀어짐 | `dis`나 어셈블리로 확인 |
| 분기를 공짜처럼 취급 | 예측 실패 시 큰 비용 | 핫 루프의 분기 수를 줄임 |
| 컴파일러를 과소평가 | 손최적화가 오히려 손해 | 먼저 `-O2` 출력 읽기 |
| ISA와 CPU를 동일시 | 같은 ISA도 칩마다 속도 차이 | 마이크로아키텍처도 함께 보기 |
| 인터프리터 최적화에 기대기 | 뜨거운 경로가 계속 느림 | 핫 패스는 컴파일된 경로 검토 |

## 실무에서는 이렇게 드러납니다

- 게임 엔진은 핫 루프의 어셈블리와 SIMD를 직접 확인합니다.
- 컴파일러 개발은 ISA에 맞춘 명령어 선택과 스케줄링을 다룹니다.
- 임베디드 시스템은 명령어 수준의 사이클 계산으로 실시간성을 맞춥니다.
- 보안 분석은 디스어셈블리로 악성 코드 흐름을 추적합니다.
- 데이터베이스는 핵심 연산자에 손튜닝 어셈블리를 쓰기도 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 핫 함수 하나를 보면 "이게 대략 몇 개의 명령어로 펼쳐질까"를 먼저 떠올립니다. 분기가 얼마나 있는지, 메모리 로드는 얼마나 되는지, 시스템 콜로 빠지는 부분은 어디인지 생각합니다. 매일 어셈블리를 쓰지는 않아도, 어셈블리의 모양은 매일 의식합니다.

또한 "ISA는 계약이고 마이크로아키텍처는 구현"이라는 구분을 놓치지 않습니다. 같은 x86-64 명령어도 Intel, AMD, 세대에 따라 비용이 다를 수 있으므로, 보편적 주장보다 측정을 믿습니다.

## 체크리스트

- [ ] fetch-decode-execute 세 단계를 그릴 수 있는가
- [ ] 명령어가 opcode와 operand로 구성된다는 것을 아는가
- [ ] 분기가 PC를 바꾼다는 점을 설명할 수 있는가
- [ ] x86-64, ARM, RISC-V가 서로 다른 ISA라는 점을 아는가
- [ ] 자신의 코드에 대한 어셈블리 출력을 한 번이라도 읽어 본 적이 있는가

## 연습 문제

1. `dis`로 간단한 함수와 조건문이 있는 함수를 비교해 보세요. `if` 하나가 바이트코드 수를 얼마나 늘리는지 확인해 보세요.

2. `TinyCPU`에 `SUB`와 `LOAD`를 추가해 작은 프로그램을 만들어 보세요. 명령어 종류가 늘어날수록 decode 단계가 어떻게 복잡해지는지도 생각해 보세요.

3. 짧은 C 함수 하나를 `gcc -O2 -S`로 컴파일한 뒤, 원래 코드보다 얼마나 짧은 명령어 시퀀스로 바뀌는지 읽어 보세요.

## 정리 및 다음 글

CPU는 메모리에서 명령어를 가져오고, 해석하고, 실행하는 단순한 사이클을 반복하는 기계입니다. 그 단순한 사이클 위에 우리가 아는 모든 추상화가 올라가 있습니다. ISA는 약속이고, 어셈블리는 그 약속이 드러나는 가장 직접적인 표면입니다.

다음 글에서는 명령어가 실제로 값을 다루는 가장 가까운 장소, 즉 레지스터와 ALU를 봅니다. 데이터가 CPU 안에서 잠시 어디에 머무르고 어디서 연산되는지 살펴보겠습니다.

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
- [RISC-V Specifications](https://riscv.org/technical/specifications/)

Tags: Computer Science, 컴퓨터 구조, CPU, 명령어, ISA, 어셈블리
