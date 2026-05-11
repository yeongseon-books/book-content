---
series: computer-architecture-101
episode: 4
title: 레지스터와 ALU
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
  - 레지스터
  - ALU
  - CPU
  - 연산
seo_description: CPU의 레지스터 파일과 ALU의 역할, 그리고 데이터가 명령어 실행 중 어디에 머무는지 정리합니다.
last_reviewed: '2026-05-04'
---

# 레지스터와 ALU

> Computer Architecture 101 시리즈 (4/10)


## 이 글에서 다룰 문제

레지스터 수는 CPU가 한 번에 손에 쥘 수 있는 변수의 수입니다. 적으면 메모리를 자주 들락거려야 하고(=느림), 많으면 컴파일러가 더 자유롭게 최적화할 수 있습니다. ALU의 처리량은 한 사이클에 끝낼 수 있는 연산의 수를 결정합니다. 두 가지 모두 매일 쓰는 코드의 성능 상한을 결정합니다.

> "이 변수는 레지스터에 있나, 메모리에 있나?"라는 질문은 거의 모든 핫 패스 최적화의 출발점입니다.

## 전체 흐름
> 레지스터는 CPU 코어 안에 있는 작은 저장소입니다. 보통 수십 개, 각각 64비트 폭, 접근 비용은 한 사이클 미만입니다. ALU는 두 레지스터의 값을 입력으로 받아 한 사이클에 결과를 내놓는 회로입니다. 모든 산술·논리 연산은 이 안에서 일어납니다.

```text
   +----------------------- CPU Core ----------------------+
   |                                                       |
   |   +--------+    +-------+    +---------+              |
   |   |  RAX   |--->|       |    |         |              |
   |   |  RBX   |--->|  ALU  |--->|  RAX    |              |
   |   |  RCX   |    |       |    |  (결과)  |              |
   |   |  ...   |    +-------+    +---------+              |
   |   +--------+                                          |
   |                                                       |
   |   PC | SP | FLAGS  ← 특수 레지스터                     |
   +-------------------------------------------------------+
```

## Before / After

**Before — "변수는 그냥 변수다"는 모델:**

```python
def hot_loop():
    s = 0
    for i in range(1000):
        s += i * 2 + 1
    return s
```

**After — "변수는 레지스터를 차지한다"는 모델:**

```text
함수 진입 시 컴파일러:
- s   → R0 에 할당
- i   → R1 에 할당
- 임시 (i*2+1) → R2 에 할당

루프 한 번:
- R2 = R1 << 1     # i * 2 (시프트로)
- R2 = R2 + 1
- R0 = R0 + R2
- R1 = R1 + 1
- 비교 후 분기
```

레지스터를 잘 쓰면 메모리 접근 없이 루프가 돕니다.

## 단계별로 따라하기

### 1단계: 가상 ALU 직접 만들기

```python
class ALU:
    """기본 산술/논리 연산을 한 곳에서 수행"""
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

ALU는 두 입력을 받아 한 결과를 내놓는 단순한 함수의 집합입니다. 실제 회로도 이 추상화에 가깝습니다.

### 2단계: 레지스터 파일 직접 만들기

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

레지스터 파일은 작은 배열에 가깝지만, 회로상 한 사이클 안에 여러 포트로 동시 읽기·쓰기가 됩니다.

### 3단계: ALU + 레지스터 + 명령어 결합

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
    ("SHL", 3, 2, 1),     # 즉시값 1
    ("SUB", 4, 3, 0),
], rf, alu)
print(rf)   # R0=7 R1=3 R2=10 R3=20 R4=13
```

레지스터-레지스터 명령어가 ISA의 절반 이상을 차지합니다. 메모리 접근이 거의 없는 코드가 가장 빠른 코드입니다.

### 4단계: FLAGS 레지스터로 비교 결과 보기

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
cpu.cmp(0, 1); print(cpu.flags)   # Z=1, N=0  (같음)
cpu.rf.write(1, 11)
cpu.cmp(0, 1); print(cpu.flags)   # Z=0, N=1  (작음)
```

`if a == b`, `if a < b` 같은 조건은 모두 SUB 명령어와 FLAGS 검사의 조합으로 구현됩니다.

### 5단계: 컴파일러의 레지스터 할당 흉내내기

```python
def assign_registers(variables, num_regs=4):
    """가장 단순한 first-fit 할당"""
    mapping = {}
    free = list(range(num_regs))
    for v in variables:
        if not free:
            mapping[v] = "STACK"   # 스필
        else:
            mapping[v] = f"R{free.pop(0)}"
    return mapping

print(assign_registers(["a", "b", "c", "d"]))
print(assign_registers(["a", "b", "c", "d", "e", "f"]))
```

레지스터가 부족하면 일부 변수는 스택(메모리)으로 "스필(spill)"됩니다. 그래서 깊은 함수, 큰 표현식은 메모리 접근이 늘어납니다.

## 이 코드에서 주목할 점

- ALU는 두 입력 → 한 결과의 단순한 회로입니다
- 레지스터는 적고 빠릅니다(수십 개, 한 사이클 미만)
- 비교 결과는 FLAGS 레지스터에 저장되어 분기 명령어가 사용합니다
- 변수가 레지스터에 못 들어가면 스택으로 스필되며 메모리 비용이 발생합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 변수 폭증 | 레지스터 부족 → 스필 | 핫 함수의 변수 수 줄이기 |
| 큰 함수 인라인만 의지 | 인라인 후 레지스터 압박 | 함수 분할 검토 |
| 부동소수점 = ALU | 별도 FPU/SIMD 유닛 사용 | 부동소수점 비용 별도 측정 |
| 비교 무겁게 봄 | 한 사이클짜리 SUB+FLAG | 비교가 아니라 분기가 비싸다 |
| 레지스터 = 이름이 있는 변수 | 레지스터 번호와 변수는 별개 | 어셈블리에서 둘을 분리 |

## 실무에서는 이렇게 쓰입니다

- 임베디드 펌웨어: 레지스터 폭과 수를 의식한 데이터 타입 선택
- 머신러닝 추론: SIMD 레지스터(AVX, NEON)로 한 명령어에 여러 값 처리
- 게임/그래픽스: GPU의 수많은 레지스터 활용 셰이더 작성
- 컴파일러: 레지스터 할당 알고리즘(graph coloring)으로 스필 최소화
- 보안: 부채널 공격에서 FLAGS 변화로 정보 누출 방지

## 체크리스트

- [ ] 레지스터와 메모리의 차이를 한 문장으로 말할 수 있는가
- [ ] 일반 목적 레지스터와 특수 레지스터의 예를 안다
- [ ] ALU가 한 사이클에 무엇을 하는지 그릴 수 있는가
- [ ] FLAGS 레지스터의 역할을 안다
- [ ] 레지스터 스필이 왜 비싼지 설명할 수 있는가

## 정리 및 다음 단계

레지스터는 CPU가 한 번에 손에 쥘 수 있는 가장 빠른 저장소이고, ALU는 그 위에서 실제 연산을 수행하는 회로입니다. 모든 변수는 결국 레지스터를 거치고, 레지스터가 부족하면 메모리로 스필됩니다. 핫 함수의 변수 수를 의식하는 습관이 작은 최적화의 출발점입니다.

다음 글에서는 그 너머의 큰 풍경, 즉 메모리 구조를 살펴봅니다. RAM이 어떻게 주소를 가지며, 가상 메모리가 어떻게 그 위에 쌓이는지를 다룹니다.

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
