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

이 그림에서는 컴퓨터 구조란 무엇인가?를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 컴퓨터 구조란 무엇인가?의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## Before / After

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

다음 글에서는 이 지도의 가장 아래쪽 표현 단위부터 봅니다. 비트와 바이트, 정수와 부동소수점이 메모리 안에서 어떻게 저장되는지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **컴퓨터 구조를 한 문장으로 정의하면 무엇일까요?**
  - 본문의 기준은 컴퓨터 구조란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **폰 노이만 모델의 다섯 구성 요소는 어떻게 연결될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python 같은 고수준 코드가 실제 하드웨어까지 내려가는 경로는 어떻게 생겼을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **컴퓨터 구조란 무엇인가? (현재 글)**
- 데이터 표현 — bit, byte, integer, floating point (예정)
- CPU와 명령어 (예정)
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
- [Hennessy & Patterson — Computer Architecture: A Quantitative Approach](https://www.elsevier.com/books/computer-architecture/hennessy/978-0-12-811905-1)
- [Wikipedia — Von Neumann Architecture](https://en.wikipedia.org/wiki/Von_Neumann_architecture)
- [CS:APP — Computer Systems: A Programmer's Perspective](https://csapp.cs.cmu.edu/)

Tags: Computer Science, 컴퓨터 구조, 하드웨어, 기초, 시스템, 폰 노이만
