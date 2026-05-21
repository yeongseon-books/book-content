---
series: computer-architecture-101
episode: 1
title: "Computer Architecture 101 (1/10): 컴퓨터 구조란 무엇인가?"
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
  - 하드웨어
  - 기초
  - 시스템
  - 폰 노이만
seo_description: 컴퓨터 구조의 정의와 폰 노이만 모델, 추상화 계층을 통해 코드가 하드웨어 위에서 실제로 실행되는 흐름을 정리합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (1/10): 컴퓨터 구조란 무엇인가?

파이썬 한 줄은 그냥 "실행된다"고만 생각하면 성능 문제를 만날 때마다 길을 잃게 됩니다. 이 글은 Computer Architecture 101 시리즈의 첫 번째 글입니다. 여기서는 프로그램이 하드웨어 위에서 실제로 어떻게 흘러가는지, 그리고 왜 컴퓨터 구조가 그 흐름을 읽는 기본 지도가 되는지를 먼저 잡겠습니다.

컴퓨터 구조를 배운다는 것은 회로 설계자가 되겠다는 뜻이 아닙니다. 개발자가 코드를 더 빠르게 만들고, 병목을 더 정확히 찾고, 추상화 아래에서 무슨 일이 벌어지는지 설명할 수 있게 되는 쪽에 가깝습니다. 같은 알고리즘도 메모리 접근 패턴, 분기, 명령어 수에 따라 전혀 다른 성능을 보이는 이유가 여기서 시작됩니다.

## 먼저 던지는 질문

- 컴퓨터 구조를 한 문장으로 정의하면 무엇일까요?
- 폰 노이만 모델의 다섯 구성 요소는 어떻게 연결될까요?
- Python 같은 고수준 코드가 실제 하드웨어까지 내려가는 경로는 어떻게 생겼을까요?

## 큰 그림

![Computer Architecture 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/01/01-01-big-picture.ko.png)

*Computer Architecture 101 1장 흐름 개요*

## 왜 중요한가

같은 알고리즘도 메모리 접근 패턴, 분기 동작, 명령어 조합에 따라 10배 이상 느려질 수 있습니다. 모든 추상화는 결국 새기고 있는 하드웨어의 제약과 비용을 완전히 숨기지 못합니다. 시스템이 느려질 때 원인은 대개 내가 보던 계층이 아니라 그 바로 아래 계층에 있습니다.

그래서 컴퓨터 구조를 모르면 성능 디버깅은 거의 항상 추측이 됩니다. 반대로 구조를 알면 "이건 알고리즘 문제인가, 인터프리터 비용인가, 캐시 미스인가, I/O 대기인가"를 나눠서 볼 수 있습니다.

## 한눈에 보는 개념

폰 노이만 모델은 명령어와 데이터를 같은 메모리에 두고, CPU가 한 번에 한 명령어씩 가져와 실행하는 구조입니다. 오늘날의 거의 모든 범용 컴퓨터는 이 모델의 변형 위에서 동작합니다.

```text
  +-----------+      +-------------------+      +-----------+
  |  Input    | ---> |  CPU              | ---> |  Output   |
  |  Device   |      |  +------+ +-----+ |      |  Device   |
  +-----------+      |  | ALU  | | CU  | |      +-----------+
                     |  +------+ +-----+ |
                     +---------+---------+
                               |
                               v
                       +---------------+
                       |    Memory     |
                       |  (code + data)|
                       +---------------+
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| ISA | CPU가 외부에 제공하는 명령어 집합 계약 |
| 마이크로아키텍처 | ISA를 실제 회로로 구현하는 내부 설계 |
| 클럭 | CPU의 박자, 한 사이클은 한 번의 비트 |
| 메모리 계층 | 레지스터부터 캐시, RAM, 디스크까지의 저장 계층 |
| 추상화 계층 | 언어에서 회로까지 내려가는 층위 |

## 적용 전과 후

**Before — "코드는 그냥 실행된다":**

```python
total = 0
for n in range(10**7):
    total += n
print(total)
```

이 코드는 단순한 덧셈처럼 보이지만, 실제로는 수천만 번의 정수 연산, 분기 예측, 메모리 읽기, 캐시 적중과 실패를 동반합니다.

**After — "한 사이클씩 따라가 본다":**

```text
1. PC (program counter) holds the next instruction address
2. CPU fetches the instruction from memory (Fetch)
3. The instruction is interpreted (Decode)
4. The ALU performs the addition (Execute)
5. The result is stored in a register (Writeback)
6. PC advances to the next instruction
```

같은 한 줄의 코드도 결국 이 단계가 수천만 번 반복된 결과입니다.

## 단계별로 따라가기

### 1단계: Python 바이트코드 보기

```python
import dis

def add_one(x):
    return x + 1

dis.dis(add_one)
```

출력 예시는 다음과 같습니다.

```text
  2           0 LOAD_FAST                0 (x)
              2 LOAD_CONST               1 (1)
              4 BINARY_ADD
              6 RETURN_VALUE
```

한 줄의 표현식도 여러 개의 가상 명령어로 분해됩니다. CPython은 이 바이트코드를 C 호출로 바꾸고, C 컴파일러는 다시 기계어로 내립니다.

### 2단계: 컴파일된 어셈블리 보기

```text
# C source:  int add_one(int x) { return x + 1; }
# gcc -S output (excerpt):
#   add_one:
#       lea     eax, [rdi + 1]
#       ret
```

같은 의미가 두 개의 명령어로 줄어듭니다. 여기서 인터프리터의 비용이 눈에 보이기 시작합니다.

### 3단계: 한 사이클의 감각 만들기

```python
CLOCK_GHZ = 3.0  # assume 3 GHz
ns_per_cycle = 1.0 / CLOCK_GHZ

print(f"One cycle: ~{ns_per_cycle:.3f} ns")
print(f"L1 cache hit ~ 4 cycles -> {4 * ns_per_cycle:.2f} ns")
print(f"Main memory access ~ 200 cycles -> {200 * ns_per_cycle:.2f} ns")
```

한 사이클은 0.3ns 수준이지만 메인 메모리 접근은 그보다 200배 이상 느립니다. 캐시와 지역성이 중요한 이유가 바로 이 비대칭입니다.

### 4단계: 접근 패턴의 차이 보기

```python
import time

N = 10_000_000
data = [0] * N

start = time.perf_counter()
for i in range(N):
    data[i] += 1
print(f"Sequential: {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
for i in range(0, N, 16):
    data[i] += 1
print(f"Strided (1/16th of work): {time.perf_counter() - start:.2f} s")
```

산술량만 보면 비슷해 보여도 캐시 동작은 전혀 다릅니다. 구조를 모르면 이 차이를 설명할 수 없습니다.

### 5단계: 추상화 계층 그리기

```text
[Application]      Python, JavaScript
       |
[Runtime / VM]     CPython, V8, JVM
       |
[Compiler / OS]    GCC, LLVM, Linux kernel
       |
[ISA]              x86-64, ARMv8, RISC-V
       |
[Microarchitecture] caches, pipeline, branch prediction
       |
[Digital circuits]  gates, flip-flops, transistors
```

각 계층은 아래 계층을 감춥니다. 컴퓨터 구조는 특히 ISA와 마이크로아키텍처 사이를 읽는 데 핵심입니다.

## 이 코드에서 먼저 봐야 할 점

- Python 한 줄도 결국 바이트코드와 기계어의 연쇄입니다.
- 같은 결과라도 명령어 수와 메모리 비용은 크게 다를 수 있습니다.
- 한 사이클과 메인 메모리 접근의 속도 차이가 이후 모든 주제를 지배합니다.
- 추상화는 편리하지만 성능 문제는 늘 한 계층 아래를 보게 만듭니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 맨 위 계층에서만 생각하기 | 성능 원인을 못 찾음 | 한 계층 아래로 내려가서 본다 |
| 클럭 속도만 성능으로 보기 | IPC와 캐시 비용을 놓침 | 캐시 미스와 분기도 함께 본다 |
| 메모리를 평평하다고 가정 | 같은 알고리즘인데 몇 배씩 느려짐 | 메모리 계층을 의식한다 |
| ISA와 마이크로아키텍처 혼동 | 같은 코드가 칩마다 다른 이유를 놓침 | 계약과 구현을 분리한다 |
| 인터프리터와 컴파일러 성능을 비슷하게 보기 | 핫 패스 비용을 과소평가 | 뜨거운 경로는 컴파일된 코드도 본다 |

## 실무에서는 이렇게 드러납니다

- 백엔드 튜닝에서는 캐시 미스와 분기 예측 실패를 추적합니다.
- 임베디드 개발에서는 제한된 ISA와 전력 예산을 함께 봅니다.
- 머신러닝에서는 행렬 배치와 메모리 계층이 성능을 좌우합니다.
- 보안에서는 Spectre 같은 부채널 공격도 구조 지식 위에서 이해됩니다.
- 데이터베이스 엔진은 캐시 친화적인 자료구조를 적극적으로 선택합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 "느리다"는 말을 들으면 바로 레이어를 나눕니다. 알고리즘 문제인지, 인터프리터 문제인지, 메모리 문제인지, I/O 문제인지 먼저 분리합니다. 그 뒤에 각 레이어에 맞는 도구를 씁니다. 프로파일러, 어셈블리 출력, 캐시 미스 통계, 시스템 콜 트레이스가 각각 다른 질문에 답하기 때문입니다.

또한 시니어는 추상화가 무료가 아니라는 사실을 압니다. 가비지 컬렉터, 가상 메모리, 캐시, 분기 예측은 평소에는 보이지 않지만 병목이 생기는 순간 비용 청구서를 내밉니다. 그 청구서를 읽는 능력이 곧 컴퓨터 구조 지식의 실전 가치입니다.

## 체크리스트

- [ ] 폰 노이만 모델의 다섯 구성 요소를 말할 수 있는가
- [ ] ISA와 마이크로아키텍처의 차이를 설명할 수 있는가
- [ ] 한 사이클과 메인 메모리 접근의 대략적 차이를 아는가
- [ ] 추상화 계층을 위에서 아래까지 그릴 수 있는가
- [ ] 성능 문제는 한 계층 아래에 있다는 감각이 생겼는가

## 연습 문제

1. 직접 작성한 함수 두 개에 `dis`를 적용해 바이트코드 길이를 비교해 보세요. 실행 시간 차이가 명령어 수와 비슷하게 움직이는지도 확인해 보세요.

2. 백만 개의 정수를 (a) 순차 접근으로, (b) 무작위 접근으로 더하는 프로그램을 작성해 시간을 비교해 보세요. 차이를 메모리 계층 관점에서 설명해 보세요.

3. 현재 사용 중인 CPU 모델의 클럭, 코어 수, L1/L2/L3 캐시 크기를 확인하고 이 글의 수치와 연결해 보세요.

## 정리 및 다음 글

컴퓨터 구조는 코드가 하드웨어 위에서 실제로 어떻게 실행되는지를 설명하는 지도입니다. 폰 노이만 모델은 그 출발점이고, 언어에서 트랜지스터까지 이어지는 추상화 계층은 그 지도를 읽는 축입니다. 성능 문제는 거의 언제나 내가 보던 계층 바로 아래에 있으므로, 이 큰 그림이 있어야 다음 단계로 내려갈 수 있습니다.

다음 글에서는 이 지도의 가장 아래쪽 표현 단위부터 봅니다. 비트와 바이트, 정수와 부동소수점이 메모리 안에서 어떻게 저장되는지 짚어보겠습니다.

## 심화 학습: 폰 노이만 구조의 본질과 현대 변형

컴퓨터 구조를 처음 배울 때는 폰 노이만 모델의 다섯 블록을 외우는 데서 그치기 쉽습니다. 하지만 실무에서 중요한 것은 "이 모델이 왜 지금도 유효하며, 어디서 병목이 생기는가"입니다.

### 폰 노이만 병목(Von Neumann Bottleneck)

폰 노이만 구조에서 CPU와 메모리는 하나의 버스를 공유합니다. 명령어도 데이터도 같은 통로를 거쳐야 합니다.

```text
┌──────────┐      단일 버스       ┌──────────┐
│   CPU    │◄──────────────────►│  Memory  │
│(제어+ALU)│  명령어 + 데이터     │          │
└──────────┘                     └──────────┘
```

이 구조의 한계를 숫자로 보겠습니다.

| 항목 | 대략적 수치 |
|------|-------------|
| CPU 레지스터 접근 | ~0.3 ns |
| L1 캐시 접근 | ~1 ns |
| DRAM 접근 | ~100 ns |
| CPU 연산 처리량 | 수십 GigaOps/s |
| DRAM 대역폭 | ~50 GB/s |

CPU가 1 ns마다 명령어를 완료할 수 있지만 메모리에서 데이터를 가져오는 데 100 ns가 걸린다면, 명령어 100개분의 시간을 기다리는 셈입니다. 이것이 폰 노이만 병목입니다. 현대 컴퓨터가 캐시 계층, 프리페치, 비순차 실행을 도입한 이유가 바로 이 병목을 완화하기 위함입니다.

### 하버드 구조와의 비교

폰 노이만 병목에 대한 초기 해법 중 하나가 하버드 구조입니다.

```text
┌──────────┐  명령어 버스  ┌──────────────┐
│   CPU    │◄────────────►│ 명령어 메모리 │
│          │              └──────────────┘
│          │  데이터 버스  ┌──────────────┐
│          │◄────────────►│ 데이터 메모리 │
└──────────┘              └──────────────┘
```

| 특성 | 폰 노이만 | 하버드 |
|------|-----------|--------|
| 버스 | 단일 | 분리(명령어/데이터) |
| 동시 접근 | 불가 | 가능 |
| 유연성 | 코드=데이터 가능 | 코드↔데이터 이동 제한 |
| 현대 적용 | 메인 메모리 관점 | L1 캐시 분리(I-cache/D-cache) |

현대 프로세서는 두 구조를 결합합니다. 메인 메모리는 폰 노이만(통합)이지만 L1 캐시는 하버드(분리)로 동작합니다. 이 조합을 수정 하버드 구조(Modified Harvard Architecture)라 부릅니다.

### CISC vs RISC: 설계 철학의 분기점

컴퓨터 구조의 역사에서 가장 큰 설계 논쟁 중 하나가 명령어 집합(ISA) 철학입니다.

```text
CISC (x86 계열)                    RISC (ARM, RISC-V 계열)
┌────────────────────┐            ┌────────────────────┐
│ 복잡한 명령어 다수   │            │ 단순한 명령어 소수   │
│ 가변 길이 인코딩     │            │ 고정 길이 인코딩     │
│ 메모리↔레지스터 연산 │            │ load/store 분리     │
│ 마이크로코드 해석    │            │ 하드와이어드 제어    │
└────────────────────┘            └────────────────────┘
```

| 비교 항목 | CISC (x86-64) | RISC (ARM64) |
|-----------|---------------|--------------|
| 명령어 길이 | 1~15 바이트 | 고정 4 바이트 |
| 레지스터 수 | 16 범용 | 31 범용 |
| 메모리 연산 | ADD 명령이 메모리 직접 참조 가능 | LOAD 후 ADD, 결과 STORE |
| 디코딩 복잡도 | 높음(마이크로옵 변환) | 낮음(직접 실행) |
| 전력 효율 | 상대적 높은 소모 | 상대적 낮은 소모 |
| 대표 사용처 | 데스크톱, 서버 | 모바일, 임베디드, Apple Silicon |

실무에서 이 차이가 드러나는 순간: ARM 서버에서 x86 전용 SIMD intrinsic을 사용한 코드를 재컴파일하면, 동일 알고리즘이라도 벡터 레지스터 너비와 명령어 매핑이 달라 성능 특성이 바뀝니다.

### 추상화 계층과 비용: 소스 코드에서 트랜지스터까지

```text
Layer 7  │ Python source           │ x = a + b
Layer 6  │ Bytecode (CPython)      │ BINARY_ADD
Layer 5  │ C runtime               │ PyNumber_Add()
Layer 4  │ Compiler output (x86)   │ add eax, ebx
Layer 3  │ Microarchitecture       │ μop dispatch → ALU port
Layer 2  │ RTL (Register Transfer) │ R[dst] ← R[src1] + R[src2]
Layer 1  │ Gate level              │ full adder chain
Layer 0  │ Transistor / Physics    │ CMOS switching
```

각 계층을 지날 때마다 추상화 비용이 발생합니다.

**실측 예시: Python `a + b` vs C `a + b` vs 어셈블리 `add`**

```python
# Python: 단순 덧셈의 추상화 비용 측정
import timeit

# Python 정수 덧셈 (Layer 7)
t_python = timeit.timeit("a + b", setup="a=42; b=58", number=10_000_000)
print(f"Python 정수 덧셈 1천만 회: {t_python:.3f}초")

# 비교: numpy를 통한 벡터 연산 (Layer 5~4 사이)
import numpy as np
arr = np.arange(10_000_000, dtype=np.int64)
t_numpy = timeit.timeit(lambda: arr + 1, number=100)
print(f"NumPy 1천만 원소 덧셈 100회: {t_numpy:.3f}초")
```

일반적인 결과:
- Python 순수 루프: ~0.4초 (10M iterations)
- NumPy 벡터화: ~0.02초 (10M elements × 100)

NumPy가 빠른 이유는 Layer 7 반복을 Layer 4(SIMD 명령어)로 내림으로써 인터프리터 오버헤드를 제거하기 때문입니다. 이것이 "추상화 계층을 내려갈수록 성능이 올라간다"는 원리의 구체적 예시입니다.

### ISA가 소프트웨어에 미치는 영향: 실제 어셈블리 비교

같은 C 코드를 x86-64와 ARM64로 컴파일한 결과를 비교합니다.

```c
// 단순 함수
int add_and_check(int a, int b) {
    int sum = a + b;
    if (sum > 100) return sum;
    return 0;
}
```

**x86-64 (gcc -O2):**
```asm
add_and_check:
    lea     eax, [rdi+rsi]      ; a + b → eax (3바이트 명령)
    cmp     eax, 100
    mov     edx, 0
    cmovle  eax, edx            ; 분기 없이 조건부 이동
    ret
```

**ARM64 (gcc -O2):**
```asm
add_and_check:
    add     w0, w0, w1          ; a + b → w0 (4바이트 고정)
    cmp     w0, #100
    csel    w0, w0, wzr, gt     ; 조건부 선택
    ret
```

두 결과 모두 분기를 제거했지만 방식이 다릅니다. x86은 `cmovle`(조건부 이동), ARM64는 `csel`(조건부 선택)을 사용합니다. 명령어 수는 비슷하지만 x86은 가변 길이, ARM64는 고정 길이라서 프리페치 예측 효율이 달라집니다.

### 설계 트레이드오프를 정량화하는 철의 법칙

프로세서 성능의 "철의 법칙(Iron Law)"은 세 요소의 곱입니다.

```text
실행 시간 = 명령어 수 × CPI × 클록 주기

         Instructions   Cycles    Seconds
Time  =  ─────────── × ─────── × ───────
          Program      Instruction  Cycle
```

| 개선 방향 | 영향을 받는 요소 | 부작용 |
|-----------|-----------------|--------|
| 더 강력한 명령어(CISC) | 명령어 수 ↓ | CPI ↑, 클록 주기 ↑ |
| 더 단순한 명령어(RISC) | CPI ↓, 클록 주기 ↓ | 명령어 수 ↑ |
| 파이프라인 깊게 | 클록 주기 ↓ | CPI ↑(hazard penalty) |
| 캐시 확대 | CPI ↓(miss 감소) | 면적/전력 ↑ |

이 법칙이 중요한 이유: "클록이 높으면 빠르다"는 단순한 판단이 왜 틀리는지를 설명해 줍니다. Pentium 4는 높은 클록을 추구했지만 파이프라인이 31단계로 깊어져 분기 실패 패널티가 커졌고, 결국 더 낮은 클록의 Core 아키텍처에 밀렸습니다.

### 컴퓨터 구조 지식이 실무에 적용되는 세 가지 시나리오

**시나리오 1: 메모리 레이아웃 선택**

구조체 배열(AoS) vs 배열 구조체(SoA)는 캐시 라인 활용률에 직접 영향을 줍니다. 컴퓨터 구조를 모르면 "왜 같은 데이터인데 접근 순서만 바꿨는데 3배 빨라지는가"를 설명할 수 없습니다.

**시나리오 2: 브랜치 프리 코드**

위의 `cmov`/`csel` 예시처럼, 분기 예측 실패가 비싼 환경에서는 조건 분기를 제거하는 것이 유리합니다. 이 판단은 파이프라인 길이와 분기 예측기 정확도를 알아야 내릴 수 있습니다.

**시나리오 3: NUMA 인지 할당**

멀티소켓 서버에서는 어떤 CPU가 어떤 메모리 뱅크에 가까운지가 접근 시간을 결정합니다. `numactl --interleave=all`같은 옵션이 왜 필요한지 이해하려면 버스 토폴로지 지식이 선행되어야 합니다.


### 실험으로 확인하는 메모리 계층 지연 시간

아래 Python 코드는 다양한 크기의 배열에 접근하면서 접근 지연 시간의 변화를 관찰합니다. 배열이 L1에 들어가는 크기일 때와 DRAM까지 넘어가는 크기일 때 성능 차이를 직접 체감할 수 있습니다.

```python
import numpy as np
import time

def measure_access_time(size_kb: int, iterations: int = 1000) -> float:
    """특정 크기의 배열에 대한 랜덤 접근 시간 측정."""
    n_elements = (size_kb * 1024) // 8  # int64 기준
    arr = np.random.randint(0, n_elements, size=n_elements, dtype=np.int64)
    
    # 포인터 체이싱 패턴: arr[i]가 다음 인덱스를 가리킴
    indices = np.random.permutation(n_elements).astype(np.int64)
    
    start = time.perf_counter_ns()
    idx = 0
    for _ in range(iterations):
        idx = indices[idx % n_elements]
    elapsed = time.perf_counter_ns() - start
    
    return elapsed / iterations  # ns per access

# 캐시 경계를 넘나드는 크기로 테스트
sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096, 16384]
print(f"{'크기(KB)':>10} {'접근 시간(ns)':>15}")
print("-" * 28)
for size in sizes:
    t = measure_access_time(size)
    print(f"{size:>10} {t:>15.1f}")
```

일반적인 결과 패턴:

| 배열 크기 | 예상 지연 시간 | 위치 |
|-----------|---------------|------|
| 4~32 KB | 1~4 ns | L1 캐시 |
| 64~256 KB | 4~12 ns | L2 캐시 |
| 512 KB~4 MB | 12~40 ns | L3 캐시 |
| 16 MB 이상 | 80~120 ns | DRAM |

이 실험은 "메모리는 한 종류"라는 소프트웨어 관점의 환상을 깨뜨립니다. 같은 `arr[i]` 코드가 어디에 있는 데이터를 건드리느냐에 따라 30배 이상 느려질 수 있습니다.

### 무어의 법칙과 구조 설계의 진화

| 시대 | 대표 프로세서 | 트랜지스터 수 | 핵심 구조 혁신 |
|------|-------------|-------------|--------------|
| 1970s | Intel 8080 | ~6,000 | 단일 버스, 축적기 구조 |
| 1980s | Intel 386 | ~275,000 | 보호 모드, 가상 메모리 |
| 1990s | Pentium Pro | ~5,500,000 | 비순차 실행, 분기 예측 |
| 2000s | Core 2 | ~291,000,000 | 멀티코어, 공유 L2 |
| 2010s | Skylake | ~1,750,000,000 | 넓은 슈퍼스칼라, AVX-512 |
| 2020s | Apple M2 | ~20,000,000,000 | 이종 코어(P+E), 통합 메모리 |

트랜지스터가 늘어날 때마다 아키텍트가 선택한 "무엇에 트랜지스터를 쓸 것인가"가 달라집니다. 초기에는 기능 추가(부동소수점 유닛, MMU), 1990~2000년대에는 ILP(Instruction Level Parallelism) 극대화, 2010년대 이후에는 병렬 코어 수 증가와 특수 가속기(GPU, NPU)로 방향이 바뀌었습니다. 이 흐름을 이해하면 "다음 5년간 어떤 구조가 유리한가"를 예측하는 프레임이 생깁니다.

## 처음 질문으로 돌아가기

- **컴퓨터 구조를 한 문장으로 정의하면 무엇일까요?**
  - 컴퓨터 구조란 소프트웨어가 하드웨어에 작업을 지시하는 인터페이스(ISA)와, 그 인터페이스를 구현하는 마이크로아키텍처 설계를 아우르는 학문입니다. 본문에서 본 것처럼 ISA는 "무엇을 할 수 있는가"를 정의하고, 마이크로아키텍처는 "얼마나 빠르게 할 수 있는가"를 결정합니다.
- **폰 노이만 모델의 다섯 구성 요소는 어떻게 연결될까요?**
  - 입력 장치 → 메모리 → CPU(제어 유닛 + ALU) → 메모리 → 출력 장치 순으로 데이터가 흐르며, 제어 유닛이 메모리에서 명령어를 가져와(fetch) 해석(decode)하고 실행(execute)하는 사이클을 반복합니다. 본문의 폰 노이만 병목 분석에서 보았듯이, 명령어와 데이터가 같은 메모리를 공유하기 때문에 대역폭 경쟁이 발생합니다.
- **Python 같은 고수준 코드가 실제 하드웨어까지 내려가는 경로는 어떻게 생겼을까요?**
  - Python 소스 → 바이트코드 → C 런타임 → 기계어 → 마이크로옵 → 게이트 → 트랜지스터까지 7~8개 추상화 계층을 거칩니다. 심화 학습에서 확인한 것처럼, NumPy가 빠른 이유는 이 계층 중 인터프리터 오버헤드를 건너뛰고 SIMD 명령어 레벨에서 직접 연산하기 때문입니다.

## 참고 자료

- [Patterson & Hennessy — Computer Organization and Design](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Hennessy & Patterson — Computer Architecture: A Quantitative Approach](https://www.elsevier.com/books/computer-architecture/hennessy/978-0-12-811905-1)
- [Wikipedia — Von Neumann Architecture](https://en.wikipedia.org/wiki/Von_Neumann_architecture)
- [CS:APP — Computer Systems: A Programmer's Perspective](https://csapp.cs.cmu.edu/)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 하드웨어, 기초, 시스템, 폰 노이만
