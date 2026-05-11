---
series: computer-architecture-101
episode: 1
title: 컴퓨터 구조란 무엇인가?
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
  - 하드웨어
  - 기초
  - 시스템
  - 폰 노이만
seo_description: 컴퓨터 구조의 정의와 폰 노이만 모델, 추상화 계층을 통해 컴퓨터가 코드를 실행하는 방식을 정리합니다.
last_reviewed: '2026-05-11'
---

# 컴퓨터 구조란 무엇인가?

> Computer Architecture 101 시리즈 (1/10)


## 이 글에서 다룰 문제

같은 알고리즘이라도 메모리 접근 패턴, 분기 빈도, 명령어 종류에 따라 실행 시간이 10배 이상 차이가 납니다. 모든 추상화는 결국 하드웨어 위에서 깨질 수 있고, 시스템이 느려질 때 그 원인은 거의 언제나 한 계층 아래에 있습니다. 컴퓨터 구조를 모르면 성능 문제 앞에서 추측만 하게 됩니다.

> 컴퓨터 구조는 "왜 이 코드는 빠른가"가 아니라 "왜 이 코드는 이 정도밖에 안 나오는가"를 설명합니다.

## 전체 흐름
> 폰 노이만 구조는 명령어와 데이터를 같은 메모리에 두고, CPU가 한 명령어씩 가져와 실행하는 모델입니다. 입력 장치로 데이터가 들어오고, CPU가 ALU와 제어 장치를 사용해 연산하며, 결과는 메모리를 거쳐 출력 장치로 나갑니다. 오늘날 거의 모든 일반 컴퓨터가 이 모델의 변형 위에서 동작합니다.

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
                       |  (코드 + 데이터) |
                       +---------------+
```

## Before / After

**Before — "코드는 그냥 실행된다"는 모델:**

```python
total = 0
for n in range(10**7):
    total += n
print(total)
```

이 코드는 "그냥 더하기"처럼 보이지만, 실제로는 1천만 번의 정수 덧셈, 분기 예측, 메모리 접근, 캐시 적중·실패가 일어납니다.

**After — "한 사이클씩 따라가는" 모델:**

```text
1. PC(프로그램 카운터)가 다음 명령어 주소를 가리킨다
2. CPU가 메모리에서 그 명령어를 가져온다 (Fetch)
3. 명령어를 해석한다 (Decode)
4. ALU가 더하기를 수행한다 (Execute)
5. 결과를 레지스터에 저장한다 (Writeback)
6. PC를 다음 명령어로 옮긴다
```

같은 한 줄의 코드도 이 다섯 단계가 수천만 번 반복된 결과입니다.

## 단계별로 따라하기

### 1단계: 파이썬 코드의 바이트코드 들여다보기

```python
import dis

def add_one(x):
    return x + 1

dis.dis(add_one)
```

출력 예시:

```text
  2           0 LOAD_FAST                0 (x)
              2 LOAD_CONST               1 (1)
              4 BINARY_ADD
              6 RETURN_VALUE
```

`x + 1`이라는 한 줄이 네 개의 가상 명령어로 분해됩니다. CPython 인터프리터는 이 바이트코드를 다시 C 코드로, C 코드는 컴파일러에 의해 기계어로 번역됩니다.

### 2단계: 컴파일된 함수의 어셈블리 보기

```python
# C로 작성한 동일한 함수의 어셈블리 (gcc -S 결과 일부)
# 원본 C 함수: int add_one(int x) { return x + 1; }
#
# 어셈블리 핵심 부분:
#   레이블: add_one:
#   명령 1: lea     eax, [rdi + 1]
#   명령 2: ret
```

같은 의미라도 컴파일된 결과는 단 두 줄의 명령어입니다. 인터프리터의 비용이 어디서 오는지가 보입니다.

### 3단계: 한 사이클의 비용 직관 잡기

```python
import time

CLOCK_GHZ = 3.0  # 가정: 3 GHz
ns_per_cycle = 1.0 / CLOCK_GHZ

print(f"한 사이클은 약 {ns_per_cycle:.3f} ns")
print(f"L1 캐시 히트 ≈ 4 사이클 → {4 * ns_per_cycle:.2f} ns")
print(f"메인 메모리 접근 ≈ 200 사이클 → {200 * ns_per_cycle:.2f} ns")
```

CPU 한 사이클은 0.3나노초 수준이고, 메인 메모리 접근은 그 200배 이상입니다. 이 비대칭이 캐시와 지역성의 출발점입니다.

### 4단계: 메모리 접근 패턴이 만드는 차이

```python
import time

N = 10_000_000
data = [0] * N

start = time.perf_counter()
for i in range(N):
    data[i] += 1
print(f"순차 접근: {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
for i in range(0, N, 16):
    data[i] += 1
print(f"띄엄띄엄 접근(1/16만): {time.perf_counter() - start:.2f} s")
```

같은 양의 작업처럼 보여도 캐시 라인을 어떻게 쓰는지에 따라 시간이 달라집니다. 컴퓨터 구조를 모르면 이 차이를 설명할 수 없습니다.

### 5단계: 추상화 계층 직접 그려보기

```text
[애플리케이션]   Python · JavaScript
       │
[런타임/VM]     CPython · V8 · JVM
       │
[컴파일러/OS]   GCC · LLVM · Linux Kernel
       │
[ISA]           x86-64 · ARMv8 · RISC-V
       │
[마이크로아키텍처] 캐시·파이프라인·분기 예측
       │
[디지털 회로]    게이트·플립플롭·트랜지스터
```

각 계층은 그 위 계층에게 단순한 인터페이스를 제공합니다. 컴퓨터 구조는 주로 ISA와 마이크로아키텍처 사이를 다룹니다.

## 이 코드에서 주목할 점

- 파이썬 한 줄은 인터프리터 바이트코드로, 다시 기계어로 번역됩니다
- 같은 결과라도 명령어 수와 메모리 접근 패턴에 따라 비용이 다릅니다
- 한 사이클 ≈ 0.3 ns, 메인 메모리 접근 ≈ 60 ns의 비대칭이 핵심입니다
- 추상화 계층은 편리하지만 성능을 따질 때는 한 계층 아래를 봐야 합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "추상화 위에서만" 사고 | 성능 문제 원인을 못 찾음 | 한 계층 아래까지 내려가서 본다 |
| 클럭 속도 = 성능 | 사이클당 명령어와 메모리도 봐야 함 | IPC, 캐시 미스율을 함께 본다 |
| 메모리는 평탄하다고 가정 | 같은 알고리즘인데 N배 차이 | 메모리 계층과 지역성을 의식한다 |
| ISA = 마이크로아키텍처 | 같은 명령어도 칩마다 다르게 동작 | 둘을 분리해서 본다 |
| 인터프리터 ≈ 컴파일러 성능 | 10~100배 차이 | 핫 패스는 컴파일된 코드로 |

## 실무에서는 이렇게 쓰입니다

- 백엔드 성능 튜닝: 핫 함수의 캐시 미스와 분기 예측 실패 분석
- 임베디드 개발: 정해진 ISA 위에서 메모리·전력 한계 안에 코드 맞추기
- 머신러닝: GPU 메모리 계층을 의식한 행렬 연산 최적화
- 보안: 사이드 채널 공격(Spectre 등) 이해와 완화
- 데이터베이스 엔진: 캐시 친화적 자료구조와 SIMD 활용

## 체크리스트

- [ ] 폰 노이만 모델의 다섯 구성 요소를 말할 수 있는가
- [ ] ISA와 마이크로아키텍처의 차이를 설명할 수 있는가
- [ ] 한 사이클과 메인 메모리 접근의 비용 차이를 안다
- [ ] 추상화 계층을 위에서 아래로 한 번 그릴 수 있는가
- [ ] "성능 문제는 한 계층 아래에 있다"는 감각을 갖고 있는가

## 정리 및 다음 단계

컴퓨터 구조는 코드가 하드웨어 위에서 실제로 어떻게 실행되는지를 설명하는 추상화입니다. 폰 노이만 모델은 그 출발점이고, 추상화 계층은 위에서 아래까지 길게 이어집니다. 성능 문제는 거의 언제나 한 계층 아래에 있고, 그것을 들여다볼 수 있으려면 구조의 큰 그림이 먼저 있어야 합니다.

다음 글에서는 가장 아래에서부터 올라옵니다. 컴퓨터가 다루는 모든 데이터의 단위인 비트와 바이트, 정수와 부동소수점이 메모리에 어떻게 저장되는지를 살펴봅니다.

<!-- toc:begin -->
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
