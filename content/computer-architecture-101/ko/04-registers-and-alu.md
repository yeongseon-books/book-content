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

## 먼저 던지는 질문

- 레지스터는 메모리와 무엇이 다를까요?
- 일반 목적 레지스터와 특수 레지스터는 어떻게 나뉠까요?
- ALU는 어떤 연산을 실제로 수행할까요?

## 큰 그림

![Computer Architecture 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/04/04-01-registers-alu-dataflow.ko.png)

*Computer Architecture 101 4장 흐름 개요*

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

## Before / After

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

## 심화 실습: 비트 연산 · 캐시 계산 · 파이프라인 관찰

컴퓨터 구조를 실제로 이해하려면 정의를 암기하는 대신 숫자를 직접 계산해 보는 과정이 필요합니다. 같은 명령이라도 비트 표현, 메모리 계층, 파이프라인 충돌 조건을 동시에 보면 성능 병목의 원인이 선명해집니다.

### 2의 보수와 비트 마스크를 수치로 확인하기

```python
def to_u8(n: int) -> int:
    return n & 0xFF

def to_s8(n: int) -> int:
    n &= 0xFF
    return n - 0x100 if n & 0x80 else n

x = to_u8(-5)          # 251 (0b11111011)
y = to_u8(12)          # 12  (0b00001100)
print(bin(x), bin(y))
print(to_s8(x + y))    # 7
print(to_s8(x - y))    # -17
```

핵심은 ALU가 "부호 있는 정수"와 "부호 없는 정수"를 따로 계산하지 않는다는 점입니다. 동일한 비트열을 어떻게 해석하느냐가 결과 의미를 바꿉니다. 그래서 ISA 문서에는 signed/unsigned 비교 명령이 따로 존재합니다.

### 캐시 인덱스 계산을 손으로 풀기

가정:
- L1 D-cache = 32KiB
- line size = 64B
- 8-way set associative

계산:
- 총 line 수 = 32KiB / 64B = 512
- set 수 = 512 / 8 = 64
- set index 비트 수 = log2(64) = 6
- block offset 비트 수 = log2(64) = 6
- tag 비트 수(48-bit VA 가정) = 48 - 6 - 6 = 36

즉 주소 비트 분해는 `[tag:36][index:6][offset:6]`이 됩니다. 두 주소가 같은 set에 매핑되는지 확인하려면 offset을 제거한 뒤 index 6비트를 비교하면 됩니다.

### 캐시 미스 패턴을 추적하는 간단 코드

```python
# stride 접근이 캐시 locality에 미치는 영향 관찰
N = 1024 * 1024
arr = [0] * N

def walk(step: int):
    s = 0
    for i in range(0, N, step):
        s += arr[i]
    return s

for step in [1, 2, 4, 8, 16, 32, 64, 128]:
    walk(step)
```

이 코드는 단순하지만 실험 관점에서는 매우 유용합니다. `step`이 커질수록 한 cache line에서 활용하는 유효 데이터가 줄고 miss 비율이 올라갑니다. 프로파일러에서는 CPI 증가와 함께 메모리 stall 시간이 늘어나는 형태로 관측됩니다.

### 5단계 파이프라인에서 hazard를 그림으로 보기

```mermaid
flowchart LR
    IF["IF"] --> ID["ID"] --> EX["EX"] --> MEM["MEM"] --> WB["WB"]
    EX -->|"branch decision"| IF
```

간단한 명령 시퀀스:
- `I1: LOAD R1, [R2]`
- `I2: ADD R3, R1, R4`

`I2`는 `R1`이 필요하지만 `I1`의 결과는 MEM/WB 이후에 준비됩니다. Forwarding이 없으면 stall이 필요하고, forwarding이 있으면 일부 cycle을 절약할 수 있습니다. 이 차이가 곧 IPC 차이로 이어집니다.

### 파이프라인 타이밍 표를 직접 작성하기

```text
cycle:   1   2   3   4   5   6
I1      IF  ID  EX MEM  WB
I2          IF  ID STALL EX MEM WB
I3              IF STALL ID  EX MEM WB
```

이 표를 직접 그려 보면 왜 분기 예측 실패가 큰 비용인지, 왜 load-use hazard가 민감한지 바로 이해할 수 있습니다. 이론보다 "cycle 단위로 어디가 비는지"를 보는 것이 훨씬 빠릅니다.

### 성능 근사식으로 병목 분해하기

성능은 보통 다음으로 근사합니다.

`Execution Time = Instruction Count × CPI × Clock Cycle Time`

여기서 구조 개선은 보통 세 축으로 나타납니다.
- 명령 수 감소: 컴파일러 최적화/벡터화
- CPI 감소: cache miss 감소, branch mispredict 감소, forwarding 개선
- cycle time 단축: 더 높은 클록, 더 짧은 임계 경로

실무에서는 한 축을 개선하면 다른 축이 악화될 수 있습니다. 예를 들어 파이프라인 단계를 늘려 클록을 높이면 분기 실패 패널티가 커질 수 있습니다. 따라서 "한 지표만" 보고 결론 내리면 위험합니다.

### 점검 체크리스트

- 주소 하나를 보고 `tag/index/offset`으로 즉시 분해할 수 있는가
- load-use, branch hazard를 cycle 표로 그릴 수 있는가
- signed/unsigned 연산 차이를 비트 패턴으로 설명할 수 있는가
- CPI 상승의 원인을 cache/branch/structural hazard로 나눠 추적할 수 있는가

이 체크리스트를 통과하면, 컴퓨터 구조 지식이 암기에서 운영 가능한 문제해결 도구로 바뀝니다.

## 처음 질문으로 돌아가기

- **레지스터는 메모리와 무엇이 다를까요?**
  - 본문의 기준은 레지스터와 ALU를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **일반 목적 레지스터와 특수 레지스터는 어떻게 나뉠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **ALU는 어떤 연산을 실제로 수행할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Architecture 101 (1/10): 컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): 데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [Computer Architecture 101 (3/10): CPU와 명령어](./03-cpu-and-instructions.md)
- **레지스터와 ALU (현재 글)**
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
- [Intel 64 and IA-32 Architectures Optimization Reference Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel64-and-ia32-architectures-optimization.html)
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation)
- [Agner Fog — Optimization Manuals](https://www.agner.org/optimize/)

Tags: Computer Science, 컴퓨터 구조, 레지스터, ALU, CPU, 연산
