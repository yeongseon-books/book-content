---
series: computer-architecture-101
episode: 3
title: "Computer Architecture 101 (3/10): CPU와 명령어"
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

# Computer Architecture 101 (3/10): CPU와 명령어

프로파일러에서 작은 루프 하나가 계속 뜨기 시작하면, 그다음 질문은 더 이상 "내가 무슨 문법을 썼지?"가 아닙니다. 컴파일러가 어떤 명령어를 만들었는지, CPU가 그 명령어를 어떤 순서로 가져오고 해석하고 실행하는지가 진짜 설명이 됩니다.

이 글은 Computer Architecture 101 시리즈의 세 번째 글입니다. 여기서는 x86-64, ARM64, RISC-V를 ISA라는 공통 계약의 예로 놓고, 작은 함수 하나가 실제 명령어 흐름으로 어떻게 내려오는지 짚어보겠습니다.

성능 최적화는 결국 "이 코드는 몇 개의 명령어가 되었고, CPU는 그것을 얼마나 빨리 처리하는가"로 수렴합니다. 이 사이클을 머릿속에 넣어 두면 프로파일러 출력과 어셈블리 리스트가 비로소 읽히기 시작합니다.

## 먼저 던지는 질문

- CPU는 한 사이클에 정확히 무엇을 할까요?
- ISA는 무엇을 약속하는 계약일까요?
- 명령어는 opcode와 operand로 어떻게 구성될까요?

## 큰 그림

![Computer Architecture 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/03/03-01-cpu-fetch-decode-execute.ko.png)

*Computer Architecture 101 3장 흐름 개요*

## 왜 중요한가

성능 작업은 결국 명령어 수준으로 내려갑니다. 코드가 몇 개의 명령어로 변했는지, 그 명령어가 메모리 접근을 얼마나 포함하는지, 분기가 얼마나 많은지가 실제 실행 시간을 바꿉니다.

따라서 CPU 사이클을 모르면 프로파일러 결과가 흐릿하고, 어셈블리를 한 번도 읽어 보지 않았다면 컴파일러가 무엇을 잘했는지 놓쳤는지 판단하기 어렵습니다.

## 한눈에 보는 개념

CPU는 매 사이클마다 PC가 가리키는 주소의 명령어를 가져오고, 비트 패턴을 해석하고, 실행합니다. 분기가 없다면 PC는 다음 명령어로 이동하고, 분기가 있다면 다른 주소로 점프합니다.

### Fetch-decode-execute 흐름

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| ISA | 명령어 형식과 의미를 정의하는 계약 |
| opcode | 무엇을 할지 나타내는 부분 |
| operand | 어디에 적용할지 나타내는 부분 |
| PC | 다음 명령어 주소를 가리키는 프로그램 카운터 |
| Branch | PC를 다른 곳으로 보내는 명령어 |
| Cycle | CPU의 한 박자 |

## 적용 전과 후

**Before — "코드가 그냥 실행된다":**

```python
def add(a, b):
    return a + b
```

**After — "이 함수는 몇 개의 명령어인가":**

```text
# x86-64 어셈블리 (단순화)
add:
    mov   rax, rdi      # 첫 번째 인자 a를 rax로 이동
    add   rax, rsi      # 두 번째 인자 b를 더함
    ret                 # 결과 반환

# 대략 3개 명령어, 3사이클 안팎 (캐시 히트 가정)
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

### 2단계: 작은 루프를 실제 x86-64 어셈블리로 보기

```c
int count_positive(int *arr, int n) {
    int s = 0;
    for (int i = 0; i < n; ++i) {
        if (arr[i] > 0) s += arr[i];
    }
    return s;
}
```

```bash
clang -target x86_64-apple-macos14 -S -O0 -x c count_positive.c -o -
clang -target x86_64-apple-macos14 -S -O2 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -x c count_positive.c -o -
```

```text
# x86-64, -O0 (발췌)
movl    $0, -16(%rbp)      # s가 스택에 놓임
movl    $0, -20(%rbp)      # i가 스택에 놓임
LBB0_1:
movl    -20(%rbp), %eax
cmpl    -12(%rbp), %eax
jge     LBB0_6
cmpl    $0, (%rax,%rcx,4)
jle     LBB0_4
addl    -16(%rbp), %eax
movl    %eax, -16(%rbp)
```

```text
# x86-64, -O2 (발췌)
testl   %esi, %esi
jle     LBB0_1
LBB0_4:
movl    (%rdi,%rsi,4), %r8d
testl   %r8d, %r8d
cmovlel %edx, %r8d
addl    %r8d, %eax
incq    %rsi
cmpq    %rsi, %rcx
jne     LBB0_4
```

`-O0`에서는 합계 `s`와 루프 인덱스 `i`를 스택에서 계속 읽고 쓰기 때문에 메모리 왕복이 눈에 띕니다. 반대로 `-O2`에서는 값이 주로 레지스터에 머물고, `testl`이 조건 플래그를 세우고, `cmovlel`과 `cmpq`/`jne`가 분기 흐름을 훨씬 간결하게 만듭니다.

### 3단계: 같은 코드를 ARM64로 비교하기

```bash
clang -target arm64-apple-macos14 -S -O2 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -x c count_positive.c -o -
```

```text
# ARM64, -O2 (발췌)
cmp     w1, #1
b.lt    LBB0_4
LBB0_2:
ldr     w10, [x0], #4
bic     w10, w10, w10, asr #31
add     w8, w10, w8
subs    x9, x9, #1
b.ne    LBB0_2
```

ISA가 달라져도 계약은 비슷합니다. `ldr`가 값을 가져오고, `add`가 누적합을 갱신하고, `subs`가 뺄셈과 FLAGS 갱신을 함께 수행하며, `b.ne`가 그 FLAGS를 읽어 루프를 이어 갑니다. RISC-V도 이름과 인코딩은 다르지만 같은 종류의 fetch-decode-execute 흐름을 따릅니다.

### 4단계: 방금 본 명령어를 종류별로 나누기

| 범주 | x86-64 예시 | ARM64 예시 | 이 코드에서 한 일 |
| --- | --- | --- | --- |
| 산술 / 논리 | `addl`, `testl` | `add`, `subs`, `bic` | 합계 갱신, 부호 검사, FLAGS 설정 |
| 메모리 | `movl (%rdi,%rsi,4), %r8d` | `ldr w10, [x0], #4` | 배열 원소 읽기 |
| 분기 / 제어 흐름 | `jle`, `jne` | `b.lt`, `b.ne` | 조건에 따라 건너뛰거나 루프 반복 |
| 데이터 이동 | `movl`, `cmovlel` | `mov` | 레지스터와 메모리 사이 값 이동 |

ISA마다 세부 명령어 이름은 달라도, 이런 큰 범주는 거의 공통입니다. 차이는 인코딩과 레지스터 구조, 그리고 컴파일러가 얼마나 공격적으로 재배치할 수 있는지에서 드러납니다.

### 5단계: 자신의 코드로 다시 해 보기

```text
1. 분기와 루프가 있는 5-10줄짜리 C, Rust, Zig 함수를 하나 고릅니다.
2. `-O0`와 `-O2`로 각각 컴파일합니다.
3. 루프 카운터가 어디에 있는지, FLAGS를 세우는 명령어가 무엇인지, 그 FLAGS를 읽는 분기가 무엇인지 표시해 봅니다.
4. 빠르게 비교할 때는 Compiler Explorer가 편하지만, 명령어 의미를 확인할 때는 아키텍처 매뉴얼을 기준으로 읽습니다.
```

이 단계가 되면 fetch-decode-execute는 추상 개념이 아니라 실제 로드, 비교, 분기, 레지스터 갱신의 흐름으로 보이기 시작합니다.

## 이 코드에서 먼저 봐야 할 점

- 모든 CPU는 fetch-decode-execute를 반복합니다.
- 명령어는 opcode와 operand의 조합입니다.
- 분기 명령어는 PC를 직접 바꾸거나 다음 명령어 흐름을 갈라놓습니다.
- 최적화된 코드는 핫한 값을 레지스터에 두고 메모리 왕복을 줄이려 합니다.

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

2. 같은 작은 루프를 x86-64와 ARM64로 각각 컴파일해 보고, 두 목록에서 load, arithmetic, branch 역할을 하는 명령어를 찾아 보세요.

3. 짧은 C 함수 하나를 `clang -S`나 godbolt.org로 컴파일한 뒤, `-O0`에서 스택에 있던 값이 `-O2`에서 어떤 레지스터로 옮겨 갔는지 추적해 보세요.

## 정리 및 다음 글

CPU는 메모리에서 명령어를 가져오고, 해석하고, 실행하는 단순한 사이클을 반복하는 기계입니다. 그 단순한 사이클 위에 우리가 아는 모든 추상화가 올라가 있습니다. ISA는 약속이고, 어셈블리는 그 약속이 드러나는 가장 직접적인 표면입니다.

다음 글에서는 명령어가 실제로 값을 다루는 가장 가까운 장소, 즉 레지스터와 ALU를 봅니다. 데이터가 CPU 안에서 잠시 어디에 머무르고 어디서 연산되는지 짚어보겠습니다.

## 심화 학습: 명령어 인코딩과 실행 사이클 해부

### RISC-V 명령어 인코딩 분석

RISC-V는 공개 ISA로, 명령어 구조를 투명하게 볼 수 있어 학습에 최적입니다.

```text
R-type (레지스터 연산):
┌────────┬─────┬─────┬──────┬─────┬─────────┐
│ funct7 │ rs2 │ rs1 │funct3│ rd  │ opcode  │
│  7bit  │5bit │5bit │ 3bit │5bit │  7bit   │
└────────┴─────┴─────┴──────┴─────┴─────────┘
  31-25   24-20 19-15 14-12  11-7    6-0

I-type (즉시값 연산):
┌──────────────┬─────┬──────┬─────┬─────────┐
│  imm[11:0]   │ rs1 │funct3│ rd  │ opcode  │
│    12bit     │5bit │ 3bit │5bit │  7bit   │
└──────────────┴─────┴──────┴─────┴─────────┘

S-type (저장):
┌────────┬─────┬─────┬──────┬────────┬─────────┐
│imm[11:5]│ rs2 │ rs1 │funct3│imm[4:0]│ opcode  │
│  7bit   │5bit │5bit │ 3bit │  5bit  │  7bit   │
└─────────┴─────┴─────┴──────┴────────┴─────────┘
```

```python
def decode_r_type(instruction: int) -> dict:
    """RISC-V R-type 명령어 디코딩."""
    return {
        'opcode': instruction & 0x7F,
        'rd':     (instruction >> 7) & 0x1F,
        'funct3': (instruction >> 12) & 0x7,
        'rs1':    (instruction >> 15) & 0x1F,
        'rs2':    (instruction >> 20) & 0x1F,
        'funct7': (instruction >> 25) & 0x7F,
    }

# ADD x3, x1, x2 → 0x002081B3
instr = 0x002081B3
decoded = decode_r_type(instr)
print(decoded)
# {'opcode': 51, 'rd': 3, 'funct3': 0, 'rs1': 1, 'rs2': 2, 'funct7': 0}
# opcode=51(0110011)=R-type, funct7=0+funct3=0 → ADD
# rd=x3, rs1=x1, rs2=x2 → x3 = x1 + x2
```

고정 32비트 인코딩의 장점: 디코더가 비트 위치만으로 필드를 추출할 수 있어 조합 회로로 구현 가능합니다. x86처럼 가변 길이면 "명령어 경계 찾기"부터 시작해야 하므로 프리디코드 단계가 추가됩니다.

### x86-64 vs ARM64 vs RISC-V: 같은 함수의 명령어 밀도

```c
int sum_array(int* arr, int n) {
    int total = 0;
    for (int i = 0; i < n; i++)
        total += arr[i];
    return total;
}
```

**x86-64 (가변 길이, 1~15 바이트):**
```asm
sum_array:
    xor     eax, eax          ; 2B  total = 0
    test    esi, esi          ; 2B  n == 0?
    jle     .done             ; 2B
    lea     rcx, [rdi+rsi*4]  ; 4B  end = arr + n
.loop:
    add     eax, [rdi]        ; 2B  total += *arr
    add     rdi, 4            ; 4B  arr++
    cmp     rdi, rcx          ; 3B  arr < end?
    jne     .loop             ; 2B
.done:
    ret                       ; 1B
    ; 총 ~22 바이트, 9 명령어
```

**ARM64 (고정 4바이트):**
```asm
sum_array:
    mov     w2, #0            ; 4B  total = 0
    cbz     w1, .done         ; 4B  n == 0?
.loop:
    ldr     w3, [x0], #4     ; 4B  w3 = *arr; arr += 4
    add     w2, w2, w3        ; 4B  total += w3
    subs    w1, w1, #1        ; 4B  n--; set flags
    b.ne    .loop             ; 4B  if n != 0 goto loop
.done:
    mov     w0, w2            ; 4B  return total
    ret                       ; 4B
    ; 총 32 바이트, 8 명령어
```

| 비교 | x86-64 | ARM64 |
|------|--------|-------|
| 코드 크기 | ~22 B | 32 B |
| 명령어 수 | 9 | 8 |
| 평균 명령어 길이 | ~2.4 B | 4 B |
| 루프 내 명령어 | 4 | 4 |
| 디코딩 복잡도 | 가변→μop 변환 | 직접 실행 |

x86이 코드 크기에서 유리하지만 디코딩 비용이 숨어 있습니다. 현대 x86 CPU는 내부적으로 RISC-like μop으로 변환한 뒤 실행합니다.

### Fetch-Decode-Execute 사이클 상세

```text
┌─────────────────────────────────────────────────────┐
│                    CPU 내부                           │
│                                                     │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐        │
│  │Fetch │──►│Decode│──►│Execute──►│Write │        │
│  │      │   │      │   │      │   │ Back │        │
│  └──┬───┘   └──────┘   └──────┘   └──────┘        │
│     │                                               │
│     │ PC (Program Counter)                          │
│     ▼                                               │
│  ┌──────────────────┐                               │
│  │ 다음 명령어 주소   │                               │
│  └──────────────────┘                               │
└─────────────────────────────────────────────────────┘
         │                       ▲
         ▼                       │
┌─────────────────────────────────────────────────────┐
│                  메모리                               │
│  주소  │ 내용                                        │
│  0x00  │ ADD x3, x1, x2    (fetch 대상)             │
│  0x04  │ SUB x4, x3, x5                            │
│  0x08  │ BEQ x4, x0, 0x20                          │
│  ...   │ ...                                        │
└─────────────────────────────────────────────────────┘
```

각 단계에서 일어나는 일:

| 단계 | 입력 | 동작 | 출력 |
|------|------|------|------|
| Fetch | PC 값 | 메모리[PC]에서 명령어 읽기, PC += 4 | 명령어 비트열 |
| Decode | 명령어 비트열 | opcode/rd/rs1/rs2/imm 분리, 레지스터 파일 읽기 | 제어 신호 + 피연산자 값 |
| Execute | 피연산자 + 제어 신호 | ALU 연산 또는 주소 계산 | 결과 값 |
| Memory | 주소 + 데이터 | Load: 메모리 읽기 / Store: 메모리 쓰기 | 메모리 데이터 |
| Write Back | 결과 값 | 레지스터 파일에 결과 저장 | 레지스터 갱신 |

### 주소 지정 모드(Addressing Modes)

명령어가 피연산자를 찾는 방식은 ISA마다 다르지만, 공통 패턴이 있습니다.

| 모드 | 예시 (x86) | 유효 주소 | 용도 |
|------|------------|-----------|------|
| 즉시값 | `mov eax, 42` | 명령어 내부 | 상수 로딩 |
| 레지스터 | `add eax, ebx` | 레지스터 | 일반 연산 |
| 직접 | `mov eax, [0x1000]` | 0x1000 | 전역 변수 |
| 간접 | `mov eax, [rbx]` | R[rbx] | 포인터 역참조 |
| 변위 | `mov eax, [rbx+8]` | R[rbx]+8 | 구조체 필드 |
| 인덱스 | `mov eax, [rbx+rcx*4]` | R[rbx]+R[rcx]×4 | 배열 접근 |

```python
# 주소 지정 모드를 시뮬레이션하는 간단한 CPU 모델
class SimpleCPU:
    def __init__(self):
        self.regs = [0] * 32
        self.memory = [0] * 1024
        self.pc = 0
    
    def effective_address(self, mode: str, base: int = 0, 
                          offset: int = 0, index: int = 0, scale: int = 1) -> int:
        if mode == 'immediate':
            return None  # 값이 명령어 내부에 있음
        elif mode == 'register':
            return None  # 레지스터에서 직접 읽음
        elif mode == 'direct':
            return offset
        elif mode == 'indirect':
            return self.regs[base]
        elif mode == 'displacement':
            return self.regs[base] + offset
        elif mode == 'indexed':
            return self.regs[base] + self.regs[index] * scale
        raise ValueError(f"Unknown mode: {mode}")

cpu = SimpleCPU()
cpu.regs[1] = 100   # base register
cpu.regs[2] = 5     # index register

print(cpu.effective_address('displacement', base=1, offset=8))   # 108
print(cpu.effective_address('indexed', base=1, index=2, scale=4)) # 120
```

### 명령어 종류별 분포: 실제 프로그램 프로파일

컴파일된 프로그램에서 명령어 종류별 비율을 알면 "어떤 최적화가 효과적인가"를 판단할 수 있습니다.

| 명령어 종류 | SPEC CPU2017 int 비율 | SPEC CPU2017 fp 비율 |
|------------|---------------------|---------------------|
| Load | ~25% | ~30% |
| Store | ~10% | ~12% |
| 산술/논리 | ~35% | ~25% |
| 분기 | ~20% | ~15% |
| 부동소수점 | ~2% | ~18% |
| 기타 | ~8% | ~0% |

이 데이터가 말해 주는 것: 메모리 접근(Load+Store)이 전체의 35~42%를 차지합니다. 따라서 캐시 최적화와 메모리 대역폭 확보가 성능에 가장 큰 영향을 미칩니다. "ALU를 빠르게 만드는 것"만으로는 전체 성능의 35%밖에 커버하지 못합니다.


### 시스템 호출: 사용자 코드와 커널의 경계

일반 명령어로는 하드웨어에 직접 접근할 수 없습니다. 파일 읽기, 네트워크 전송 같은 작업은 시스템 호출(syscall)을 통해 커널에 위임합니다.

```text
사용자 모드 (Ring 3)          커널 모드 (Ring 0)
┌──────────────────┐         ┌──────────────────┐
│ printf("hello")  │         │                  │
│     ↓            │         │ sys_write()      │
│ write(1, buf, 5) │────────►│   ↓              │
│                  │ syscall  │ 드라이버 호출     │
│                  │ 명령어   │   ↓              │
│                  │◄────────│ iret / sysret    │
└──────────────────┘         └──────────────────┘
```

x86-64에서 시스템 호출의 실제 비용:
- `syscall` 명령어 자체: ~100 cycles (컨텍스트 스위치 오버헤드)
- 일반 함수 호출: ~2-5 cycles

이 100배 차이가 "시스템 호출을 줄여라"는 최적화 조언의 근거입니다. `read()`를 바이트 단위로 호출하면 버퍼링 대비 수십 배 느려지는 이유가 여기에 있습니다.

### CISC의 복잡한 명령어가 실제로 쓰이는가?

x86에는 `REP MOVSB`(문자열 복사), `LOOP`(루프), `ENTER/LEAVE`(스택 프레임) 같은 복잡한 명령어가 있지만, 현대 컴파일러는 대부분 사용하지 않습니다.

| 명령어 | 설계 의도 | 현대 컴파일러 선택 | 이유 |
|--------|----------|-------------------|------|
| `REP MOVSB` | 메모리 복사 | `memcpy` 최적화 루프 | 마이크로코드 시작 비용 |
| `LOOP` | 카운터 기반 루프 | `dec` + `jnz` | 더 빠른 μop 스케줄링 |
| `ENTER` | 스택 프레임 설정 | `push rbp; mov rbp,rsp` | 4 μop vs 1+1 |
| `BCD 연산` | 이진화 십진 | 사용 안 함 | 64비트 모드에서 제거됨 |

이것이 "ISA에 있다고 다 빠른 것은 아니다"를 보여 줍니다. 마이크로아키텍처 구현에 따라 단순 명령어 조합이 복잡한 단일 명령어보다 빠를 수 있습니다.

## 처음 질문으로 돌아가기

- **CPU는 한 사이클에 정확히 무엇을 할까요?**
  - 파이프라인이 없는 단일 사이클 CPU라면 fetch-decode-execute-memory-writeback 전체를 1사이클에 수행합니다. 파이프라인이 있으면 각 단계가 1사이클씩 차지하되 여러 명령어가 겹쳐 실행됩니다. 본문에서 분석한 것처럼, 현대 슈퍼스칼라 CPU는 한 사이클에 여러 μop을 동시 발행할 수 있어 IPC > 1을 달성합니다.
- **ISA는 무엇을 약속하는 계약일까요?**
  - ISA는 소프트웨어와 하드웨어 사이의 인터페이스 계약으로, "이 비트 패턴을 넣으면 이 동작이 보장된다"를 정의합니다. RISC-V 인코딩 분석에서 본 것처럼, opcode+funct3+funct7 조합이 연산을, rd/rs1/rs2가 피연산자를 지정합니다.
- **명령어는 opcode와 operand로 어떻게 구성될까요?**
  - RISC-V R-type을 예로 들면, 7비트 opcode가 명령어 종류를, funct3+funct7이 구체적 연산을, rs1/rs2가 소스, rd가 목적지를 지정합니다. x86은 가변 길이 접두사+opcode+ModR/M+SIB+displacement+immediate로 더 복잡하지만, 핵심 원리(무엇을+어디서+어디로)는 동일합니다.

## 참고 자료

- [Patterson & Hennessy — Computer Organization and Design](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Intel 64 and IA-32 Architectures Software Developer's Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation)
- [RISC-V Specifications](https://riscv.org/technical/specifications/)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, CPU, 명령어, ISA, 어셈블리
