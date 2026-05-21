---
series: computer-architecture-101
episode: 4
title: "Computer Architecture 101 (4/10): 레지스터와 ALU"
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
  - 레지스터
  - ALU
  - CPU
  - 연산
seo_description: CPU 안에서 값이 잠시 머무는 레지스터와 실제 연산을 수행하는 ALU를 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (4/10): 레지스터와 ALU

소스 코드는 거의 그대로인데도, 살아 있는 변수가 하나 더 늘었다는 이유만으로 루프가 갑자기 느려질 때가 있습니다. 그때 병목은 단순히 "ALU가 덧셈을 했다"가 아니라, 값이 어디에 머물렀는지, 어떤 명령어가 FLAGS를 세웠는지, 레지스터를 넘친 값이 스택으로 얼마나 흘러갔는지에 달려 있습니다.

이 글은 Computer Architecture 101 시리즈의 네 번째 글입니다. 여기서는 레지스터, FLAGS, ALU를 CPU의 즉시 작업 공간으로 보고, 실제 어셈블리로 레지스터 압박과 스필이 어떤 모양으로 나타나는지 짚어보겠습니다.

레지스터 수와 ALU 처리량은 코드의 성능 상한을 직접 결정합니다. 변수가 레지스터에 머물면 빠르고, 스택이나 메모리로 밀려나면 느려집니다. 그래서 핫 패스 최적화의 출발점은 종종 "이 변수는 지금 레지스터에 있나"입니다.


![Computer Architecture 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/04/04-01-registers-alu-dataflow.ko.png)
*Computer Architecture 101 4장 흐름 개요*

## 먼저 던지는 질문

- 레지스터는 메모리와 무엇이 다를까요?
- 일반 목적 레지스터와 특수 레지스터는 어떻게 나뉠까요?
- ALU는 어떤 연산을 실제로 수행할까요?

## 왜 중요한가

레지스터 수는 CPU가 한 번에 손에 쥘 수 있는 변수의 수입니다. 적으면 값이 메모리로 자주 흘러나가고, 많으면 컴파일러가 더 자유롭게 최적화할 수 있습니다. ALU 처리량은 한 사이클에 끝낼 수 있는 연산량의 상한을 만듭니다.

따라서 레지스터와 ALU를 이해하면 "왜 이 함수가 갑자기 메모리를 많이 치는가", "왜 변수 수를 줄였더니 빨라졌는가" 같은 질문에 답하기 쉬워집니다.

## 한눈에 보는 개념

레지스터는 코어 내부의 매우 작은 저장소이고, ALU는 두 입력을 받아 한 결과를 내놓는 연산 회로입니다. 비교 결과 같은 상태는 FLAGS 같은 특수 레지스터에 저장됩니다.

### 레지스터와 ALU 데이터 흐름

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Register | CPU 코어 안의 가장 빠른 저장소 |
| General-purpose | 임의의 데이터를 담는 일반 목적 레지스터 |
| PC | 다음 명령어 주소를 담는 프로그램 카운터 |
| SP | 함수 호출과 스택을 위한 스택 포인터 |
| FLAGS | 비교 결과를 담는 상태 레지스터 |
| ALU | 산술·논리 연산을 수행하는 회로 |

## 적용 전과 후

**Before — "변수는 그냥 변수다":**

```python
def hot_loop():
    s = 0
    for i in range(1000):
        s += i * 2 + 1
    return s
```

**After — "변수는 레지스터를 차지한다":**

```text
함수 진입 시 컴파일러는 대략 이렇게 둘 수 있습니다:
- s   -> R0
- i   -> R1
- temp (i*2+1) -> R2

한 번의 반복:
- R2 = R1 << 1    # 시프트로 i * 2 계산
- R2 = R2 + 1
- R0 = R0 + R2
- R1 = R1 + 1
- 비교 후 분기
```

루프가 레지스터 안에 머무르면 메모리 접근 없이 돌아갈 수 있습니다.

## 단계별로 따라가기

### 1단계: 실제 핫 루프부터 보기

```c
long low_pressure(long *a, long n) {
    long acc = 0;
    for (long i = 0; i < n; ++i) {
        long x = a[i] + i;
        long y = x * 3;
        acc += keep3(x, y, acc);
    }
    return acc;
}

long high_pressure(long *a, long n, long bias) {
    long acc = bias;
    for (long i = 0; i < n; ++i) {
        long v0 = a[i] + bias;
        long v1 = a[i] + i;
        long v2 = v0 ^ v1;
        long v3 = v2 + acc;
        long v4 = v3 + v1;
        long v5 = v4 + v0;
        long v6 = v5 + i;
        long v7 = v6 + bias;
        long v8 = v7 ^ acc;
        long v9 = v8 + v3;
        acc += keep10(v0, v1, v2, v3, v4, v5, v6, v7, v8, v9);
    }
    return acc;
}
```

```bash
clang -target x86_64-apple-macos14 -S -O2 -fno-unroll-loops -x c pressure.c -o -
```

두 함수 모두 산술 연산을 하지만, 두 번째 함수는 중간값을 훨씬 많이 동시에 살려 둡니다. 바로 이런 상황에서 레지스터 압박이 실제 기계어에 드러납니다.

### 2단계: FLAGS가 분기를 먹이는 순간 보기

```text
# x86-64 발췌
testl   %esi, %esi
jle     LBB0_1
...
cmpq    %r12, %rbx
jne     LBB2_4

# ARM64 발췌
subs    x9, x9, #1
b.ne    LBB0_2
```

`testl`, `cmpq`, `subs`는 사용자에게 보이는 값을 저장해서 중요한 것이 아닙니다. 조건 코드를 세우고, 바로 다음 분기가 그 FLAGS를 읽는다는 점이 핵심입니다. 이것이 실전 어셈블리에서 FLAGS가 맡는 역할입니다.

### 3단계: 레지스터 압박이 낮을 때의 코드 읽기

```text
# x86-64, low_pressure (발췌)
movq    (%r14,%r12,8), %rdi
addq    %r12, %rdi
leaq    (%rdi,%rdi,2), %rsi
movq    %r15, %rdx
callq   _keep3
addq    %r15, %rax
incq    %r12
movq    %rax, %r15
```

여기서 중요한 것은 **보이지 않는 것**입니다. 스필 주석도 없고, 임시값을 살리기 위한 추가 push도 거의 없습니다. 로드와 ALU 연산, 함수 호출은 있지만 대부분의 살아 있는 값이 레지스터 안에 들어갑니다.

### 4단계: 레지스터 압박이 높을 때의 코드 읽기

```text
# x86-64, high_pressure (발췌)
movq    %rdx, -48(%rbp)      ## 8-byte Spill
movq    %rsi, -64(%rbp)      ## 8-byte Spill
movq    %rdi, -56(%rbp)      ## 8-byte Spill
...
pushq   %r14
pushq   %r11
pushq   %rax
pushq   %r10
callq   _keep10
addq    $32, %rsp
```

이 부분이 장난감 할당기가 보여 주지 못하던 실제 증거입니다. `-O2`로 컴파일했는데도, 살아 있는 값이 많아지자 스택 슬롯으로 스필이 생기고 호출 전후에 push/pop 성격의 스택 트래픽이 늘어납니다. 이제 비용은 ALU만의 비용이 아니라 메모리 왕복 비용까지 포함합니다.

### 5단계: 방금 본 어셈블리를 아키텍처 용어로 다시 읽기

| 어셈블리에서 보이는 신호 | 의미 |
| --- | --- |
| `movq ... %rdi`, `movq ... %rsi`, `leaq ...` | 호출 전에 레지스터 안에서 값을 준비하는 ALU 경로 |
| `testl`, `cmpq`, `subs` | 다음 분기를 위한 FLAGS 설정 |
| `## Spill`, `pushq`, `-48(%rbp)` 같은 스택 슬롯 | 레지스터 압박이 편한 예산을 넘었다는 신호 |
| `callq _keep3`와 `callq _keep10`의 차이 | 호출이 들어오면 인자 레지스터와 caller-saved 레지스터 관리가 함께 얽히며 압박이 커짐 |

실무에서 레지스터 할당을 본다는 것은 색칠 문제를 떠올리는 것이 아니라, 컴파일러가 작업 집합을 레지스터 안에 붙잡아 둘 수 있는지 아니면 스택을 자꾸 왕복해야 하는지를 읽는 일입니다.

## 이 코드에서 먼저 봐야 할 점

- ALU는 입력값이 이미 레지스터에 있을 때 가장 싸게 느껴집니다.
- 레지스터는 적지만 매우 빠릅니다.
- 비교 결과는 FLAGS에 저장되고 분기나 조건 이동이 곧바로 소비합니다.
- 레지스터 압박은 스필 슬롯, push, reload, 추가 메모리 트래픽으로 드러납니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 변수 수를 과하게 늘림 | 레지스터 압박과 스필 증가 | 핫 함수의 변수 수 줄이기 |
| 모든 것을 인라인하려 함 | 코드가 커지며 레지스터 압박 증가 | 함수 분할도 검토 |
| 부동소수점 ALU와 정수 ALU를 같게 봄 | 실제 유닛 구성을 오해 | FPU/SIMD 비용을 별도로 본다 |
| 비교가 비싸다고 오해 | 실제로는 분기가 더 비쌈 | 비교와 분기 비용을 구분 |
| 레지스터 번호를 소스 변수명처럼 해석 | 어셈블리 독해 오류 | 소스 이름과 물리 레지스터를 분리 |

## 실무에서는 이렇게 드러납니다

- 임베디드 펌웨어는 레지스터 폭에 맞춰 타입을 고릅니다.
- ML 추론은 AVX, NEON 같은 SIMD 레지스터를 적극 활용합니다.
- 그래픽스 셰이더는 막대한 수의 레지스터를 전제로 설계됩니다.
- 컴파일러는 graph coloring 같은 기법으로 스필을 줄입니다.
- 보안 코드는 FLAGS 누출과 분기 패턴까지 신경 씁니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 핫 함수의 지역 변수 개수를 유심히 봅니다. 살아 있는 값이 아키텍처가 제공하는 레지스터 수를 넘기기 시작하면, 컴파일러는 스택을 더 자주 사용하게 되고 반복당 비용이 올라갑니다. 그래서 변수 수를 줄이거나 큰 함수를 나누는 판단도 단순한 취향이 아니라 구조적 비용 계산에서 나옵니다.

또한 FLAGS를 "보이지 않는 부산물"처럼 생각합니다. 최근 비교 결과에 의존하는 분기는 중간에 다른 연산이 끼면 미묘하게 읽기 어려워질 수 있습니다. 직접 어셈블리를 자주 짜지 않더라도, 읽을 수는 있어야 합니다.

## 체크리스트

- [ ] 레지스터와 메모리 차이를 한 문장으로 말할 수 있는가
- [ ] 일반 목적 레지스터와 특수 레지스터 예를 들 수 있는가
- [ ] ALU가 한 사이클에 무엇을 하는지 설명할 수 있는가
- [ ] FLAGS의 역할을 설명할 수 있는가
- [ ] 스필이 왜 비싼지 설명할 수 있는가

## 연습 문제

1. 살아 있는 임시값이 2-3개인 루프와 8-10개인 루프를 각각 컴파일해 보고, high-pressure 버전에만 나타나는 스택 슬롯을 모두 표시해 보세요.

2. 자신의 디스어셈블리에서 `cmp`, `test`, `subs` 중 하나를 찾아, 그 FLAGS를 어느 분기나 조건 이동이 소비하는지 따라가 보세요.

3. godbolt.org나 로컬 컴파일로 함수 하나를 만들고, helper 인자가 3개일 때와 10개일 때를 비교해 보세요. 언제부터 스택 전달 인자와 스필 슬롯이 나타나는지 관찰해 보세요.

## 정리 및 다음 글

레지스터는 CPU가 즉시 손에 쥘 수 있는 가장 빠른 저장소이고, ALU는 그 값들 위에서 실제 연산을 수행하는 핵심 회로입니다. 변수가 레지스터 안에 머무를수록 빠르고, 밖으로 밀려날수록 느려집니다. 이 감각은 이후 캐시와 메모리 계층을 읽을 때도 그대로 이어집니다.

다음 글에서는 레지스터 바깥의 더 큰 풍경, 즉 메모리 구조를 봅니다. RAM의 주소 모델, 가상 메모리, 스택과 힙이 한 프로세스 안에서 어떻게 배치되는지 짚어보겠습니다.

## 심화 학습: 레지스터 파일 구조와 ALU 내부 설계

### 레지스터 파일의 물리적 구현

레지스터 파일은 SRAM 셀의 배열로, 일반적으로 다중 포트(multi-port) 구조를 가집니다.

```text
레지스터 파일 (32 × 64-bit, 2-read 1-write port)
┌────────────────────────────────────────┐
│  Read Port A ──►  ┌────┐              │
│                   │ x0 │ = 0 (항상)    │
│  Read Port B ──►  │ x1 │ (ra)         │
│                   │ x2 │ (sp)         │
│  Write Port  ──►  │ x3 │              │
│                   │... │              │
│                   │x31 │              │
│                   └────┘              │
│  읽기: 조합 회로 (0.3ns)               │
│  쓰기: 클록 에지에서 래치              │
└────────────────────────────────────────┘
```

**읽기와 쓰기의 비대칭성:**
- 읽기는 멀티플렉서(MUX)로 구현 → 조합 회로 → 즉시 출력
- 쓰기는 디코더 + 래치 → 클록 에지 필요 → 1사이클 지연

이 비대칭성 때문에 파이프라인에서 "Read After Write (RAW) hazard"가 발생합니다. 쓰기가 WB 단계에서 완료되기 전에 다음 명령어가 ID 단계에서 같은 레지스터를 읽으려 하기 때문입니다.

### x86-64 레지스터 맵

```text
64-bit    32-bit   16-bit   8-bit(H/L)   용도
───────────────────────────────────────────────────
RAX       EAX      AX       AH/AL        산술, 반환값
RBX       EBX      BX       BH/BL        베이스 (callee-saved)
RCX       ECX      CX       CH/CL        카운터, 4번째 인자
RDX       EDX      DX       DH/DL        I/O, 3번째 인자
RSI       ESI      SI       SIL          소스 인덱스, 2번째 인자
RDI       EDI      DI       DIL          목적지, 1번째 인자
RBP       EBP      BP       BPL          프레임 포인터
RSP       ESP      SP       SPL          스택 포인터
R8-R15    R8D-R15D R8W-R15W R8B-R15B     추가 범용
───────────────────────────────────────────────────
RIP       EIP      IP       —            명령어 포인터
RFLAGS    EFLAGS   FLAGS    —            상태 플래그
```

```python
# x86-64 호출 규약(System V AMD64 ABI) 시뮬레이션
class X86_64_CallConvention:
    """System V AMD64 ABI 호출 규약."""
    ARG_REGS = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
    CALLEE_SAVED = ['rbx', 'rbp', 'r12', 'r13', 'r14', 'r15']
    CALLER_SAVED = ['rax', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11']
    
    def pass_arguments(self, args: list) -> dict:
        """인자를 레지스터/스택에 배치."""
        placement = {}
        for i, arg in enumerate(args):
            if i < 6:
                placement[self.ARG_REGS[i]] = arg
            else:
                placement[f'[rsp+{(i-6)*8}]'] = arg
        return placement

conv = X86_64_CallConvention()
# func(1, 2, 3, 4, 5, 6, 7, 8) 호출 시
result = conv.pass_arguments([1, 2, 3, 4, 5, 6, 7, 8])
for loc, val in result.items():
    print(f"  {loc:>12} = {val}")
```

### ALU 내부: 리플 캐리 덧셈기 vs 캐리 룩어헤드

**리플 캐리 덧셈기(Ripple Carry Adder):**

```text
 A3 B3    A2 B2    A1 B1    A0 B0
  │ │      │ │      │ │      │ │
  ▼ ▼      ▼ ▼      ▼ ▼      ▼ ▼
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
│ FA  │◄─│ FA  │◄─│ FA  │◄─│ FA  │◄─ Cin=0
└──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘
   │Cout    │C2      │C1      │C0
   ▼        ▼        ▼        ▼
   S3       S2       S1       S0
   
지연: O(n) — 캐리가 순차 전파
```

**캐리 룩어헤드 덧셈기(CLA):**

```python
def carry_lookahead_4bit(a: int, b: int, cin: int = 0) -> tuple:
    """4비트 CLA: Generate/Propagate로 캐리를 병렬 계산."""
    # Generate: G[i] = A[i] & B[i]
    # Propagate: P[i] = A[i] ^ B[i]
    g = [(a >> i & 1) & (b >> i & 1) for i in range(4)]
    p = [(a >> i & 1) ^ (b >> i & 1) for i in range(4)]
    
    # 캐리를 병렬로 계산 (조합 회로 → O(1) 게이트 깊이)
    c = [0] * 5
    c[0] = cin
    c[1] = g[0] | (p[0] & c[0])
    c[2] = g[1] | (p[1] & g[0]) | (p[1] & p[0] & c[0])
    c[3] = g[2] | (p[2] & g[1]) | (p[2] & p[1] & g[0]) | (p[2] & p[1] & p[0] & c[0])
    c[4] = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1]) | (p[3] & p[2] & p[1] & g[0]) | (p[3] & p[2] & p[1] & p[0] & c[0])
    
    # 합 계산
    s = 0
    for i in range(4):
        s |= (p[i] ^ c[i]) << i
    
    return s, c[4]

# 검증: 7 + 5 = 12
result, cout = carry_lookahead_4bit(7, 5)
print(f"7 + 5 = {result}, carry_out = {cout}")  # 12, 0

result, cout = carry_lookahead_4bit(15, 1)
print(f"15 + 1 = {result}, carry_out = {cout}")  # 0, 1 (오버플로)
```

| 덧셈기 | 게이트 깊이 | 게이트 수 | 64비트 지연 |
|--------|------------|-----------|------------|
| Ripple Carry | O(n) | O(n) | ~64 게이트 지연 |
| CLA (4bit groups) | O(log n) | O(n log n) | ~8 게이트 지연 |
| Kogge-Stone | O(log n) | O(n log n) | ~6 게이트 지연 |

현대 64비트 ALU는 Kogge-Stone 또는 Brent-Kung 구조를 사용하며, 1 클록 사이클(~0.3ns at 3GHz) 내에 64비트 덧셈을 완료합니다.

### 레지스터 리네이밍: 비순차 실행의 핵심

프로그램에서 같은 아키텍처 레지스터를 반복 사용하면 "거짓 의존성(False Dependency)"이 생깁니다.

```asm
; WAW (Write After Write) 거짓 의존성
I1: ADD R1, R2, R3    ; R1 = R2 + R3
I2: MUL R4, R1, R5    ; R4 = R1 × R5 (진짜 의존: I1→I2)
I3: ADD R1, R6, R7    ; R1 = R6 + R7 (WAW: I1과 같은 R1 사용)
I4: SUB R8, R1, R9    ; R8 = R1 - R9 (진짜 의존: I3→I4)
```

리네이밍 후:

```asm
I1: ADD P41, P2, P3     ; 물리 레지스터 P41 사용
I2: MUL P42, P41, P5    ; P41에 대한 진짜 의존성 유지
I3: ADD P43, P6, P7     ; 새 물리 레지스터 P43 → I1과 독립!
I4: SUB P44, P43, P9    ; P43에 대한 진짜 의존성 유지
```

리네이밍 덕분에 I3은 I1/I2와 병렬 실행 가능합니다. 현대 CPU는 아키텍처 레지스터(16~32개)보다 훨씬 많은 물리 레지스터(~200개 이상)를 가지고 있어 이 기법을 적용합니다.

### FLAGS 레지스터와 조건 코드

ALU 연산 결과는 FLAGS 레지스터에 상태를 남깁니다.

| 플래그 | 비트 | 의미 | 설정 조건 |
|--------|------|------|-----------|
| CF (Carry) | 0 | 부호없는 오버플로 | unsigned 범위 초과 |
| ZF (Zero) | 6 | 결과가 0 | result == 0 |
| SF (Sign) | 7 | 결과가 음수 | MSB == 1 |
| OF (Overflow) | 11 | 부호있는 오버플로 | signed 범위 초과 |

```python
def alu_operation(a: int, b: int, op: str, bits: int = 32) -> dict:
    """ALU 연산 + FLAGS 계산."""
    mask = (1 << bits) - 1
    
    if op == 'ADD':
        raw = a + b
    elif op == 'SUB':
        raw = a + (~b & mask) + 1  # a - b = a + ~b + 1
    elif op == 'AND':
        raw = a & b
    elif op == 'XOR':
        raw = a ^ b
    else:
        raise ValueError(f"Unknown op: {op}")
    
    result = raw & mask
    
    # FLAGS 계산
    cf = 1 if raw > mask else 0
    zf = 1 if result == 0 else 0
    sf = 1 if result & (1 << (bits - 1)) else 0
    # OF: 두 양수 더해 음수 or 두 음수 더해 양수
    a_sign = (a >> (bits - 1)) & 1
    b_sign = (b >> (bits - 1)) & 1 if op == 'ADD' else ((~b >> (bits - 1)) & 1)
    r_sign = sf
    of = 1 if (a_sign == b_sign and a_sign != r_sign) else 0
    
    return {'result': result, 'CF': cf, 'ZF': zf, 'SF': sf, 'OF': of}

# 예시: 0x7FFFFFFF + 1 (signed overflow)
r = alu_operation(0x7FFFFFFF, 1, 'ADD')
print(f"0x7FFFFFFF + 1 = 0x{r['result']:08X}")
print(f"FLAGS: CF={r['CF']} ZF={r['ZF']} SF={r['SF']} OF={r['OF']}")
# result=0x80000000, OF=1 (양수+양수→음수)
```


### 곱셈기와 나눗셈기: ALU의 비싼 연산

덧셈은 1사이클이면 충분하지만, 곱셈과 나눗셈은 훨씬 비쌉니다.

| 연산 | 일반적 지연 시간 | 파이프라인 처리량 |
|------|----------------|-----------------|
| ADD/SUB | 1 cycle | 1/cycle |
| MUL (정수) | 3 cycles | 1/cycle (파이프라인) |
| DIV (정수 64비트) | 20~90 cycles | 비파이프라인 |
| FP ADD | 3~5 cycles | 1/cycle |
| FP MUL | 4~5 cycles | 1/cycle |
| FP DIV | 10~20 cycles | 1/4~cycle |

이 차이가 실무에서 의미하는 것: 나눗셈을 곱셈으로 대체할 수 있다면(역수 곱셈) 20배 이상 빨라질 수 있습니다. 컴파일러가 `x / 8`을 `x >> 3`으로, `x / 3`을 `x * 0xAAAAAAAB >> 33`으로 변환하는 이유입니다.

```python
# 컴파일러의 나눗셈 → 곱셈 변환 원리
def div_by_constant(n: int, divisor: int, bits: int = 32) -> int:
    """정수 나눗셈을 곱셈+시프트로 구현 (unsigned)."""
    # magic number 계산: ceil(2^(32+shift) / divisor)
    shift = bits
    magic = ((1 << (bits + shift)) + divisor - 1) // divisor
    return (n * magic) >> (bits + shift)

# 검증: 100 / 3 = 33
for n in [100, 255, 1000, 7]:
    fast = div_by_constant(n, 3)
    real = n // 3
    assert fast == real, f"Failed for {n}: got {fast}, expected {real}"
    print(f"{n} / 3 = {fast}")
```

### 시프트 연산과 배럴 시프터

시프트 연산은 곱셈/나눗셈의 2의 거듭제곱 버전이면서, 비트 필드 추출에도 사용됩니다. 하드웨어에서는 배럴 시프터(barrel shifter)로 구현되어 임의 비트 수만큼의 시프트를 1사이클에 처리합니다.

```python
def barrel_shift_left(value: int, amount: int, bits: int = 32) -> int:
    """배럴 시프터 시뮬레이션: 멀티플렉서 트리로 구현."""
    mask = (1 << bits) - 1
    # 각 단계는 2^i 비트 시프트 여부를 결정
    for i in range(bits.bit_length()):
        if amount & (1 << i):
            value = (value << (1 << i)) & mask
    return value

# 검증
print(f"1 << 5 = {barrel_shift_left(1, 5)}")    # 32
print(f"0xFF << 8 = {barrel_shift_left(0xFF, 8):#010x}")  # 0x0000ff00
```

배럴 시프터의 핵심: n비트 시프터는 log₂(n)단의 멀티플렉서로 구성됩니다. 32비트 배럴 시프터는 5단(2⁰, 2¹, 2², 2³, 2⁴ 비트 시프트)으로 0~31 어떤 시프트 양이든 동일한 지연으로 처리합니다.

### 레지스터 윈도우: SPARC의 접근법

x86/ARM과 달리 SPARC 아키텍처는 함수 호출 시 레지스터 세트를 "슬라이드"하는 레지스터 윈도우를 사용합니다.

```text
Window N-1 (caller)     Window N (current)    Window N+1 (callee)
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Out[0..7]       │───►│ In[0..7]        │    │                 │
│                 │    │ Local[0..7]     │    │                 │
│                 │    │ Out[0..7]       │───►│ In[0..7]        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

장점: 함수 호출/반환 시 레지스터 저장/복원 불필요 → 빠른 호출
단점: 레지스터 파일 크기 폭증 (128~520개), 윈도우 오버플로 시 메모리 스필

현대에는 x86/ARM 방식(소프트웨어 호출 규약 + 하드웨어 레지스터 리네이밍)이 승리했습니다. 레지스터 윈도우 방식은 전력과 면적 비용 대비 이점이 줄었기 때문입니다.

## 처음 질문으로 돌아가기

- **레지스터는 메모리와 무엇이 다를까요?**
  - 레지스터는 CPU 내부의 SRAM 셀로, 접근 시간이 ~0.3ns이며 수십 개뿐입니다. 메모리(DRAM)는 ~100ns 접근 시간에 수 GB 용량을 가집니다. 본문에서 본 것처럼, 레지스터 파일은 다중 포트로 한 사이클에 2개 읽기 + 1개 쓰기를 동시에 처리할 수 있어 파이프라인의 병목이 되지 않도록 설계됩니다.
- **일반 목적 레지스터와 특수 레지스터는 어떻게 나뉠까요?**
  - 일반 목적 레지스터(x86: RAX~R15, ARM: X0~X30)는 임의의 값을 저장하는 범용 저장소이고, 특수 레지스터(PC/IP, SP, FLAGS/CPSR)는 CPU 상태를 제어합니다. 호출 규약이 특정 범용 레지스터에 역할(인자 전달, 반환값, callee-saved)을 부여하지만 이는 소프트웨어 약속이지 하드웨어 제약은 아닙니다.
- **ALU는 어떤 연산을 실제로 수행할까요?**
  - 산술(ADD, SUB, MUL), 논리(AND, OR, XOR, NOT), 시프트(SHL, SHR, SAR), 비교(SUB 후 FLAGS만 갱신)를 수행합니다. 심화 학습에서 구현한 것처럼, 모든 연산은 결과와 함께 FLAGS(CF, ZF, SF, OF)를 갱신하여 후속 조건 분기가 이를 참조할 수 있게 합니다.

<!-- toc:begin -->
## 이 시리즈
- [Computer Architecture 101 (1/10): 컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): 데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [Computer Architecture 101 (3/10): CPU와 명령어](./03-cpu-and-instructions.md)
- **Computer Architecture 101 (4/10): 레지스터와 ALU (현재 글)**
- Computer Architecture 101 (5/10): 메모리 구조 (예정)
- Computer Architecture 101 (6/10): 캐시와 지역성 (예정)
- Computer Architecture 101 (7/10): 파이프라인 (예정)
- Computer Architecture 101 (8/10): I/O와 장치 (예정)
- Computer Architecture 101 (9/10): 병렬성과 멀티코어 (예정)
- Computer Architecture 101 (10/10): 성능을 이해하는 법 (예정)

<!-- toc:end -->

## 참고 자료

- [Patterson & Hennessy — Computer Organization and Design](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Intel 64 and IA-32 Architectures Software Developer's Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [Intel 64 and IA-32 Architectures Optimization Reference Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel64-and-ia32-architectures-optimization.html)
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation)
- [Agner Fog — Optimization Manuals](https://www.agner.org/optimize/)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 레지스터, ALU, CPU, 연산
