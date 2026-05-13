---
series: computer-architecture-101
episode: 4
title: 레지스터와 ALU
status: publish-ready
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
  - 레지스터
  - ALU
  - CPU
  - 연산
seo_description: CPU 안에서 값이 잠시 머무는 레지스터와 실제 연산을 수행하는 ALU를 설명합니다.
last_reviewed: '2026-05-12'
---

# 레지스터와 ALU

`x = 3` 같은 대입문도 CPU 안에서는 공기처럼 사라지지 않습니다. 이 글은 Computer Architecture 101 시리즈의 네 번째 글입니다. 여기서는 값이 잠깐 머무는 가장 빠른 저장소인 레지스터와, 실제 산술·논리 연산을 수행하는 ALU가 CPU 안에서 어떤 역할을 맡는지 보겠습니다.

레지스터 수와 ALU 처리량은 코드의 성능 상한을 직접 결정합니다. 변수가 레지스터에 머물면 빠르고, 스택이나 메모리로 밀려나면 느려집니다. 그래서 핫 패스 최적화의 출발점은 종종 "이 변수는 지금 레지스터에 있나"입니다.

## 이 글에서 다룰 문제

- 레지스터는 메모리와 무엇이 다를까요?
- 일반 목적 레지스터와 특수 레지스터는 어떻게 나뉠까요?
- ALU는 어떤 연산을 실제로 수행할까요?
- 레지스터 부족이 왜 성능 문제로 이어질까요?

> 레지스터는 CPU 코어 안의 가장 빠른 저장소이고, ALU는 그 레지스터 값을 받아 실제 연산을 수행하는 회로입니다.

## 왜 중요한가

레지스터 수는 CPU가 한 번에 손에 쥘 수 있는 변수의 수입니다. 적으면 값이 메모리로 자주 흘러나가고, 많으면 컴파일러가 더 자유롭게 최적화할 수 있습니다. ALU 처리량은 한 사이클에 끝낼 수 있는 연산량의 상한을 만듭니다.

따라서 레지스터와 ALU를 이해하면 "왜 이 함수가 갑자기 메모리를 많이 치는가", "왜 변수 수를 줄였더니 빨라졌는가" 같은 질문에 답하기 쉬워집니다.

## 한눈에 보는 개념

레지스터는 코어 내부의 매우 작은 저장소이고, ALU는 두 입력을 받아 한 결과를 내놓는 연산 회로입니다. 비교 결과 같은 상태는 FLAGS 같은 특수 레지스터에 저장됩니다.

```text
   +----------------------- CPU Core ----------------------+
   |                                                       |
   |   +--------+    +-------+    +---------+              |
   |   |  RAX   |--->|       |    |         |              |
   |   |  RBX   |--->|  ALU  |--->|  RAX    |              |
   |   |  RCX   |    |       |    | (result)|              |
   |   |  ...   |    +-------+    +---------+              |
   |   +--------+                                          |
   |                                                       |
   |   PC | SP | FLAGS  <- special registers               |
   +-------------------------------------------------------+
```

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
On entry the compiler may assign:
- s   -> R0
- i   -> R1
- temp (i*2+1) -> R2

One iteration:
- R2 = R1 << 1    # i * 2 via shift
- R2 = R2 + 1
- R0 = R0 + R2
- R1 = R1 + 1
- compare and branch
```

루프가 레지스터 안에 머무르면 메모리 접근 없이 돌아갈 수 있습니다.

## 단계별로 따라가기

### 1단계: 작은 ALU 만들기

```python
class ALU:
    """A few basic arithmetic and logic operations."""
    def execute(self, op, a, b):
        if op == "ADD": return a + b
        if op == "SUB": return a - b
        if op == "AND": return a & b
        if op == "OR":  return a | b
        if op == "XOR": return a ^ b
        if op == "SHL": return a << b
        if op == "SHR": return a >> b
        raise ValueError(op)

alu = ALU()
print(alu.execute("ADD", 3, 5))   # 8
print(alu.execute("SHL", 1, 4))   # 16
```

ALU는 본질적으로 두 입력과 한 출력으로 이뤄진 단순한 함수 모음입니다.

### 2단계: 작은 레지스터 파일 만들기

```python
class RegisterFile:
    def __init__(self, n=8):
        self.regs = [0] * n

    def read(self, idx):
        return self.regs[idx]

    def write(self, idx, value):
        self.regs[idx] = value

    def __repr__(self):
        return " ".join(f"R{i}={v}" for i, v in enumerate(self.regs))

rf = RegisterFile()
rf.write(0, 3)
rf.write(1, 5)
print(rf)   # R0=3 R1=5 R2=0 ...
```

회로 수준의 레지스터 파일은 배열처럼 보이지만, 여러 포트를 통해 한 사이클에 동시 읽기와 쓰기를 지원합니다.

### 3단계: ALU와 레지스터, 명령어 결합하기

```python
def run(program, rf, alu):
    for instr in program:
        op, dst, src1, src2 = instr
        a = rf.read(src1)
        b = src2 if isinstance(src2, int) else rf.read(src2)
        result = alu.execute(op, a, b)
        rf.write(dst, result)

rf, alu = RegisterFile(), ALU()
rf.write(0, 7)
rf.write(1, 3)

# R2 = R0 + R1; R3 = R2 << 1; R4 = R3 - R0
run([
    ("ADD", 2, 0, 1),
    ("SHL", 3, 2, 1),     # immediate 1
    ("SUB", 4, 3, 0),
], rf, alu)
print(rf)   # R0=7 R1=3 R2=10 R3=20 R4=13
```

대부분의 명령어는 결국 레지스터에서 값을 읽고, ALU로 계산하고, 다시 레지스터에 씁니다.

### 4단계: FLAGS 레지스터 보기

```python
class CPU:
    def __init__(self):
        self.rf = RegisterFile()
        self.alu = ALU()
        self.flags = {"Z": 0, "N": 0}   # zero, negative

    def cmp(self, src1, src2):
        diff = self.alu.execute("SUB", self.rf.read(src1), self.rf.read(src2))
        self.flags["Z"] = int(diff == 0)
        self.flags["N"] = int(diff < 0)

cpu = CPU()
cpu.rf.write(0, 10); cpu.rf.write(1, 10)
cpu.cmp(0, 1); print(cpu.flags)   # Z=1, N=0  (equal)
cpu.rf.write(1, 11)
cpu.cmp(0, 1); print(cpu.flags)   # Z=0, N=1  (less)
```

`if a == b`나 `if a < b`도 결국 SUB와 FLAGS 검사 조합으로 구현됩니다.

### 5단계: 레지스터 할당 흉내내기

```python
def assign_registers(variables, num_regs=4):
    """Simplest first-fit allocator."""
    mapping = {}
    free = list(range(num_regs))
    for v in variables:
        if not free:
            mapping[v] = "STACK"   # spill
        else:
            mapping[v] = f"R{free.pop(0)}"
    return mapping

print(assign_registers(["a", "b", "c", "d"]))
print(assign_registers(["a", "b", "c", "d", "e", "f"]))
```

레지스터가 부족하면 변수는 스택으로 밀려납니다. 이 스필이 메모리 트래픽을 만들고 성능을 끌어내립니다.

## 이 코드에서 먼저 봐야 할 점

- ALU는 두 입력과 한 출력을 갖는 단순한 회로입니다.
- 레지스터는 적지만 매우 빠릅니다.
- 비교 결과는 FLAGS에 저장되고 분기가 소비합니다.
- 레지스터에 못 들어간 변수는 스택으로 스필됩니다.

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

1. `RegisterFile` 크기를 2개, 4개, 8개로 바꿔 가며 간단한 변수 목록을 넣어 보고 언제부터 `STACK`이 생기는지 확인해 보세요.

2. `ALU`에 `MUL`과 `DIV`를 추가하고, 산술 연산 종류가 늘어나도 인터페이스는 어떻게 유지되는지 살펴보세요.

3. 짧은 루프 하나를 어셈블리로 본 뒤, 어떤 값이 레지스터에 머무르고 어떤 값이 메모리에서 다시 읽히는지 추적해 보세요.

## 정리 및 다음 글

레지스터는 CPU가 즉시 손에 쥘 수 있는 가장 빠른 저장소이고, ALU는 그 값들 위에서 실제 연산을 수행하는 핵심 회로입니다. 변수가 레지스터 안에 머무를수록 빠르고, 밖으로 밀려날수록 느려집니다. 이 감각은 이후 캐시와 메모리 계층을 읽을 때도 그대로 이어집니다.

다음 글에서는 레지스터 바깥의 더 큰 풍경, 즉 메모리 구조를 봅니다. RAM의 주소 모델, 가상 메모리, 스택과 힙이 한 프로세스 안에서 어떻게 배치되는지 살펴보겠습니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
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
- [Wikipedia — Arithmetic logic unit](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Wikipedia — Processor register](https://en.wikipedia.org/wiki/Processor_register)
- [Intel x86-64 Register Reference](https://wiki.osdev.org/CPU_Registers_x86-64)

Tags: Computer Science, 컴퓨터 구조, 레지스터, ALU, CPU, 연산
