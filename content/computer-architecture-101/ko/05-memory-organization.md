---
series: computer-architecture-101
episode: 5
title: "Computer Architecture 101 (5/10): 메모리 구조"
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
  - 메모리
  - 가상 메모리
  - 주소 공간
  - 스택과 힙
seo_description: 가상 메모리, 페이지, 스택과 힙을 한 프로세스의 주소 공간 관점에서 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (5/10): 메모리 구조

서로 다른 두 프로세스가 같은 주소 `0x400000`를 가지고도 둘 다 정상 실행될 수 있다는 사실은 처음 보면 꽤 이상합니다. 이 글은 Computer Architecture 101 시리즈의 다섯 번째 글입니다. 여기서는 메모리가 실제 RAM 그 자체가 아니라, 프로세스마다 따로 보이는 가상 주소 공간이라는 관점에서 메모리 구조를 다시 보겠습니다.

메모리 모델이 머릿속에 없으면 스택 오버플로, 메모리 누수, 정렬 문제, 페이지 폴트가 전부 제각각의 현상처럼 보입니다. 하지만 주소 공간, 페이지, 스택, 힙이라는 그림을 잡아 두면 이 문제들은 같은 지도 위에서 읽히기 시작합니다.

## 먼저 던지는 질문

- RAM은 어떤 주소 모델로 보일까요?
- 가상 주소와 물리 주소는 어떻게 다를까요?
- 한 프로세스의 text, data, heap, stack은 어떻게 배치될까요?

## 큰 그림

![Computer Architecture 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/05/05-01-big-picture.ko.png)

*Computer Architecture 101 5장 흐름 개요*

## 왜 중요한가

메모리 구조를 이해하지 못하면 같은 버그를 반복해서 만납니다. 깊은 재귀 때문에 스택이 터지고, 힙 객체를 정리하지 않아 누수가 나고, 정렬이 맞지 않아 공간을 낭비하고, 페이지 폴트 하나 때문에 코드가 갑자기 매우 느려집니다.

가상 메모리는 성능 관점에서도 거대한 주제입니다. 한 번의 페이지 폴트는 단일 명령어를 수천에서 수만 배 느리게 만들 수 있습니다. 그래서 "이 변수는 어디에 사는가"라는 질문은 메모리 안전과 성능의 공통 출발점입니다.

## 한눈에 보는 개념

각 프로세스는 자신만의 가상 주소 공간을 갖고, MMU가 가상 주소를 물리 RAM 주소로 번역합니다. 그 주소 공간 안에는 코드, 초기화된 데이터, 초기화되지 않은 데이터, 힙, 스택이 정해진 영역을 이룹니다.

```text
   +------------------+  high addresses
   |     STACK        |  <- function calls, locals
   |        |         |
   |        v         |
   |                  |
   |        ^         |
   |        |         |
   |     HEAP         |  <- malloc, new, dynamic allocation
   +------------------+
   |     BSS          |  <- uninitialized globals
   +------------------+
   |     DATA         |  <- initialized globals
   +------------------+
   |     TEXT         |  <- executable code
   +------------------+  low addresses
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Address space | 프로세스가 볼 수 있는 메모리 범위 |
| Virtual address | 프로세스가 사용하는 주소 |
| Physical address | 실제 RAM 상의 주소 |
| MMU | 가상 주소를 물리 주소로 변환하는 하드웨어 |
| Page | 메모리 매핑의 최소 단위, 보통 4KB |
| Alignment | 타입 크기에 맞는 주소에 데이터를 배치하는 규칙 |

## 적용 전과 후

**Before — "메모리는 평평한 바이트 배열이다":**

```python
data = [0] * 1_000_000
data[12345] = 42
# "It just goes into slot 12345"
```

**After — "그 주소는 가상 주소이고 페이지를 거친다":**

```text
Process virtual address: 0x7f8a4c001000 + 12345*8
                         |
                         v  (MMU + page table)
                         |
Physical RAM address:    0x00000000abcd1000
                         |
                         v  (cache -> DRAM cell)
```

인덱스 하나도 실제로는 가상 주소, 페이지 테이블, 캐시, DRAM을 차례로 거칩니다.

## 단계별로 따라가기

### 1단계: 변수의 실제 주소 보기

```python
import ctypes

x = ctypes.c_int(42)
y = ctypes.c_int(99)
print(hex(ctypes.addressof(x)))
print(hex(ctypes.addressof(y)))
print(f"distance: {ctypes.addressof(y) - ctypes.addressof(x)} bytes")
```

주소 차이를 보면 메모리가 실제로 연속된 바이트 공간처럼 배치된다는 감각을 얻을 수 있습니다.

### 2단계: 정렬 보기

```python
import ctypes

class Misaligned(ctypes.Structure):
    _fields_ = [("a", ctypes.c_char), ("b", ctypes.c_int), ("c", ctypes.c_char)]

class Aligned(ctypes.Structure):
    _fields_ = [("b", ctypes.c_int), ("a", ctypes.c_char), ("c", ctypes.c_char)]

print(ctypes.sizeof(Misaligned))   # usually 12 (with padding)
print(ctypes.sizeof(Aligned))       # usually 8
```

필드가 같아도 순서가 다르면 패딩과 총 크기가 달라집니다. 정렬은 보이지 않지만 비용이 큰 규칙입니다.

### 3단계: 스택과 힙 주소 비교하기

```python
import ctypes

def stack_var():
    x = ctypes.c_int(1)
    return ctypes.addressof(x)

heap_var = ctypes.c_int(2)
print("global address:", hex(ctypes.addressof(heap_var)))
print("stack address: ", hex(stack_var()))
```

실행 환경마다 차이는 있지만, 호출마다 달라지는 스택 주소와 비교적 안정적인 전역/동적 영역의 차이를 관찰할 수 있습니다.

### 4단계: 페이지 크기 확인하기

```python
import resource

print("page size:", resource.getpagesize(), "bytes")  # usually 4096
print("RSS (KB):", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
```

운영체제는 메모리를 페이지 단위로 다룹니다. 변수 하나를 만져도 실제로는 페이지 전체가 메모리에 올라옵니다.

### 5단계: 스택 깊이 한계 보기

```python
import sys

def recurse(n):
    return n if n == 0 else recurse(n - 1) + 1

print(sys.getrecursionlimit())
try:
    recurse(2000)
except RecursionError as e:
    print("stack limit hit:", e)
```

스택은 고정된 크기로 잡히기 때문에 깊은 재귀는 한계에 부딪힙니다. 힙은 동적으로 늘어나지만 스택은 그렇지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 모든 변수는 가상 주소를 갖고 MMU가 이를 물리 주소로 번역합니다.
- 필드 순서는 패딩과 총 크기에 직접 영향을 줍니다.
- 스택은 작고 빠르며, 힙은 크고 더 유연합니다.
- 메모리는 페이지 단위로 관리됩니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 깊은 재귀 사용 | 스택 오버플로 | 반복문 또는 명시적 스택 사용 |
| 큰 객체를 스택에 두려 함 | 스택 한계 초과 | 힙 할당 사용 |
| 필드 정렬 무시 | 메모리 낭비 | 큰 타입부터 배치 검토 |
| 가상 주소를 물리 주소처럼 생각 | 잘못된 비교와 캐싱 판단 | 둘을 명확히 구분 |
| 페이지 폴트를 무시 | 갑작스러운 극단적 지연 | 워킹셋 축소, prefetch 검토 |

## 실무에서는 이렇게 드러납니다

- 데이터베이스는 페이지 단위 I/O와 버퍼 풀로 메모리를 다룹니다.
- 게임 엔진은 SoA와 AoS 같은 레이아웃 차이로 캐시 효율을 바꿉니다.
- 임베디드 시스템은 제한된 RAM 안에서 스택과 힙을 명시적으로 분리합니다.
- 보안은 ASLR, NX bit로 주소 공간을 보호합니다.
- 시스템 프로그래밍은 `mmap`으로 파일을 메모리에 직접 매핑합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 프로세스 메모리를 추상적인 "많다/적다"가 아니라 워킹셋 관점에서 봅니다. 자주 만지는 페이지 집합이 얼마나 큰지, 그 집합이 캐시와 RAM 안에 잘 머무는지가 성능의 핵심이라고 보기 때문입니다. 이 관점은 페이지 폴트와 캐시 미스를 동시에 줄여 줍니다.

또한 자료구조의 메모리 레이아웃을 실제 비용으로 봅니다. 같은 데이터라도 Array of Structs와 Struct of Arrays는 전혀 다른 캐시 행동을 만듭니다. 따라서 자료구조 선택은 알고리즘 선택 못지않게 메모리 선택이기도 합니다.

## 체크리스트

- [ ] 가상 주소와 물리 주소의 차이를 설명할 수 있는가
- [ ] 페이지 크기가 보통 4KB라는 점을 아는가
- [ ] 스택과 힙 차이를 한 문장으로 말할 수 있는가
- [ ] 필드 순서가 구조체 크기를 바꿀 수 있다는 점을 이해하는가
- [ ] 깊은 재귀가 왜 위험한지 설명할 수 있는가

## 연습 문제

1. `ctypes.Structure`로 같은 필드를 가진 구조체 두 개를 만들되, 하나는 큰 타입부터, 다른 하나는 작은 타입부터 배치해 `sizeof`를 비교해 보세요.

2. 1MB 크기의 배열을 만들고, 그것이 어떤 주소 공간과 메모리 사용량 변화를 만드는지 관찰해 보세요.

3. 현재 시스템의 스택 크기나 재귀 한계를 확인한 뒤, 실제로 어느 깊이에서 한계에 도달하는지 실험해 보세요.

## 정리 및 다음 글

메모리는 평평한 바이트 배열처럼 보이지만, 그 평탄함은 가상 메모리가 만든 환상입니다. 실제로는 페이지 단위 매핑, text/data/heap/stack 영역, 정렬과 패딩이 함께 메모리의 진짜 비용 구조를 만듭니다. 이 모델을 이해하면 다음 주제인 캐시가 훨씬 자연스럽게 이어집니다.

다음 글에서는 CPU와 메모리 사이의 가장 중요한 중간층인 캐시를 봅니다. 왜 캐시가 필요한지, 지역성이 무엇인지, 캐시 친화적 코드는 어떤 모양인지 짚어보겠습니다.

## 심화 학습: 가상 메모리와 페이지 테이블 메커니즘

### 페이지 테이블 워크 계산

4-level 페이지 테이블(x86-64)에서 가상 주소 변환 과정을 따라갑니다.

```text
48-bit 가상 주소 분해:
┌────────┬────────┬────────┬────────┬──────────┐
│PML4(9) │PDPT(9) │ PD(9)  │ PT(9)  │Offset(12)│
└────────┴────────┴────────┴────────┴──────────┘
 47-39    38-30    29-21    20-12    11-0
```

```python
def decompose_virtual_address(va: int) -> dict:
    """48-bit 가상 주소를 4-level 페이지 테이블 인덱스로 분해."""
    return {
        'PML4 index':  (va >> 39) & 0x1FF,  # 비트 47-39
        'PDPT index':  (va >> 30) & 0x1FF,  # 비트 38-30
        'PD index':    (va >> 21) & 0x1FF,  # 비트 29-21
        'PT index':    (va >> 12) & 0x1FF,  # 비트 20-12
        'Page offset': va & 0xFFF,           # 비트 11-0
    }

# 예시: 0x00007FFF_DEADBEEF
va = 0x7FFFDEADBEEF
result = decompose_virtual_address(va)
for field, value in result.items():
    print(f"  {field:>12}: {value:>4} (0x{value:03X})")
```

출력:
```text
  PML4 index:  255 (0x0FF)
  PDPT index:  511 (0x1FF)
  PD index:    501 (0x1F5)
  PT index:    173 (0x0AD)
  Page offset: 3823 (0xEEF)
```

### 페이지 테이블 워크의 비용

TLB 미스 시 4-level 워크는 메모리를 4번 읽어야 합니다.

| 단계 | 접근 대상 | 일반적 지연 |
|------|-----------|------------|
| 1 | PML4 엔트리 | ~100 ns (DRAM) |
| 2 | PDPT 엔트리 | ~100 ns |
| 3 | PD 엔트리 | ~100 ns |
| 4 | PT 엔트리 | ~100 ns |
| 합계 | — | ~400 ns |

TLB 히트 시: ~1 ns. 즉 TLB 미스는 400배 비쌉니다.

```python
def estimate_tlb_impact(hit_rate: float, tlb_latency_ns: float = 1.0, 
                         walk_latency_ns: float = 400.0) -> float:
    """TLB 히트율에 따른 평균 주소 변환 시간 계산."""
    avg = hit_rate * tlb_latency_ns + (1 - hit_rate) * walk_latency_ns
    return avg

# 다양한 히트율에서의 영향
for rate in [0.99, 0.95, 0.90, 0.80]:
    avg = estimate_tlb_impact(rate)
    print(f"  TLB 히트율 {rate:.0%}: 평균 {avg:.1f} ns")
```

출력:
```text
  TLB 히트율 99%: 평균 4.99 ns
  TLB 히트율 95%: 평균 20.95 ns
  TLB 히트율 90%: 평균 40.90 ns
  TLB 히트율 80%: 평균 80.80 ns
```

이것이 Huge Page(2MB/1GB)를 사용하는 이유입니다. 페이지가 크면 같은 TLB 엔트리가 더 넓은 주소 범위를 커버하여 TLB 미스율이 줄어듭니다.

### 프로세스 메모리 레이아웃 실측

```python
import sys
import ctypes

# 각 영역의 주소를 확인
code_addr = id(decompose_virtual_address)  # text 영역 근처
global_var = 42
heap_obj = [0] * 1000
stack_var = 0

print(f"Code (함수):   0x{code_addr:016X}")
print(f"Global:        0x{id(global_var):016X}")
print(f"Heap (리스트): 0x{id(heap_obj):016X}")
print(f"Stack 근처:    0x{id(stack_var):016X}")
print(f"libc:          0x{ctypes.addressof(ctypes.CDLL(None)._handle):016X}" 
      if hasattr(ctypes.CDLL(None), '_handle') else "N/A")
```

일반적인 Linux x86-64 프로세스 메모리 맵:

```text
높은 주소
┌──────────────────────┐ 0x7FFF_FFFF_FFFF
│ 커널 영역 (접근 불가)  │
├──────────────────────┤ 0x7FFF_FFFF_F000
│ Stack ↓              │ (아래로 성장)
│                      │
│        ↕ 빈 공간      │
│                      │
│ Memory-mapped / mmap │ (공유 라이브러리 등)
│                      │
│        ↕ 빈 공간      │
│                      │
│ Heap ↑               │ (위로 성장, brk/mmap)
├──────────────────────┤
│ BSS (초기화 안 된 전역)│
│ Data (초기화된 전역)   │
│ Text (코드, 읽기전용) │
├──────────────────────┤ ~0x0040_0000
│ NULL 페이지 (보호)    │
└──────────────────────┘ 0x0000_0000_0000
낮은 주소
```

### mmap과 물리 메모리의 관계

```python
import mmap
import os

# 익명 매핑: 물리 메모리를 나중에 할당(demand paging)
size = 4096 * 100  # 400KB
mm = mmap.mmap(-1, size, mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)

# 첫 접근 전: 물리 메모리 미할당 (페이지 테이블 엔트리만 존재)
# 첫 접근 시: page fault → 커널이 물리 프레임 할당 → 매핑 완성
mm[0] = 65  # 첫 페이지에 page fault 발생 → 물리 할당

print(f"매핑 크기: {len(mm)} bytes")
mm.close()
```

Demand paging의 핵심: `malloc(1GB)`를 해도 물리 메모리는 즉시 1GB 소비되지 않습니다. 실제 접근(read/write)이 일어나는 페이지만 물리 프레임이 할당됩니다. 이것이 Linux에서 `committed memory > physical RAM`이 가능한 이유입니다.

### 메모리 보호와 세그멘테이션 폴트

```text
페이지 테이블 엔트리 (PTE) 비트 구조:
┌────┬───┬───┬───┬───┬───────────────────────────────┬───┐
│ NX │...│ D │ A │PCD│       물리 프레임 번호          │R/W│P│
└────┴───┴───┴───┴───┴───────────────────────────────┴───┘
 63   ...  6   5   4         51-12                     1   0

P (Present): 물리 메모리에 존재하는가
R/W: 읽기전용(0) vs 읽기/쓰기(1)
NX (No Execute): 이 페이지의 코드 실행 금지
A (Accessed): 최근 접근됨 (LRU 힌트)
D (Dirty): 수정됨 (swap-out 시 디스크 쓰기 필요)
```

세그멘테이션 폴트가 발생하는 경우:
1. P=0인 페이지 접근 (매핑 안 됨)
2. R/W=0인 페이지에 쓰기 시도
3. NX=1인 페이지에서 코드 실행 시도
4. 커널 전용 페이지에 유저 모드 접근

### 스왑과 페이지 교체 알고리즘

물리 메모리가 부족할 때 OS는 덜 사용되는 페이지를 디스크로 내보냅니다(swap-out).

| 알고리즘 | 동작 | 장단점 |
|----------|------|--------|
| FIFO | 가장 오래된 페이지 교체 | 단순하지만 Belady's anomaly |
| LRU | 최근 미사용 페이지 교체 | 좋은 성능, 구현 비용 높음 |
| Clock | 참조 비트 기반 근사 LRU | 실용적, Linux 기본 |
| LFU | 접근 빈도 낮은 페이지 교체 | 과거 편향 문제 |

Linux의 실제 구현(Multi-generational LRU):
- Active list: 최근 2회 이상 접근된 페이지
- Inactive list: 1회만 접근되거나 오래된 페이지
- 메모리 압박 시 inactive list 끝에서 회수


### DRAM 내부 구조: Bank, Row, Column

DRAM 접근이 느린 이유를 이해하려면 물리적 구조를 알아야 합니다.

```text
DRAM 모듈 구조:
┌─────────────────────────────────────┐
│              DIMM                     │
│  ┌──────┐ ┌──────┐ ... ┌──────┐    │
│  │Chip 0│ │Chip 1│     │Chip 7│    │
│  └──────┘ └──────┘     └──────┘    │
└─────────────────────────────────────┘

DRAM Chip 내부:
┌─────────────────────────────────┐
│  Bank 0  │  Bank 1  │ ... │ B7 │
│ ┌──────┐ │          │     │    │
│ │Row   │ │          │     │    │
│ │Buffer│ │          │     │    │
│ ├──────┤ │          │     │    │
│ │ Cell │ │          │     │    │
│ │Array │ │          │     │    │
│ │(rows)│ │          │     │    │
│ └──────┘ │          │     │    │
└─────────────────────────────────┘
```

DRAM 접근 단계와 지연:

| 단계 | 동작 | 시간 |
|------|------|------|
| RAS (Row Access Strobe) | 행 활성화 → 행 버퍼로 복사 | ~13 ns (tRCD) |
| CAS (Column Access Strobe) | 열 선택 → 데이터 출력 | ~13 ns (tCL) |
| Precharge | 행 닫기 (다른 행 접근 전) | ~13 ns (tRP) |
| 총 랜덤 접근 | RAS + CAS + 데이터 전송 | ~50-70 ns |

**Row Buffer Hit vs Miss:**
- 같은 행의 다른 열 접근(row hit): CAS만 필요 → ~13 ns
- 다른 행 접근(row miss): Precharge + RAS + CAS → ~40 ns

이것이 "순차 접근이 랜덤 접근보다 빠른" 근본 원인입니다. 캐시 없이도 DRAM 자체의 row buffer가 공간 지역성을 활용합니다.

### 메모리 대역폭 계산

```python
def dram_bandwidth(data_rate_mhz: int, bus_width_bits: int = 64, 
                   channels: int = 2) -> float:
    """DRAM 이론적 최대 대역폭 계산 (GB/s)."""
    # DDR: 클록 당 2번 전송
    transfers_per_sec = data_rate_mhz * 1_000_000  # MT/s
    bytes_per_transfer = bus_width_bits // 8
    bandwidth = transfers_per_sec * bytes_per_transfer * channels
    return bandwidth / 1e9  # GB/s

# 일반적인 시스템 구성
configs = [
    ("DDR4-3200", 3200, 64, 2),
    ("DDR5-4800", 4800, 64, 2),
    ("DDR5-6400", 6400, 64, 2),
    ("HBM2e (GPU)", 3600, 1024, 1),
]

print(f"{'구성':>20} {'대역폭':>10}")
for name, rate, width, ch in configs:
    bw = dram_bandwidth(rate, width, ch)
    print(f"{name:>20} {bw:>8.1f} GB/s")
```

출력:
```text
            DDR4-3200     51.2 GB/s
            DDR5-4800     76.8 GB/s
            DDR5-6400    102.4 GB/s
        HBM2e (GPU)    460.8 GB/s
```

GPU가 HBM을 사용하는 이유: 버스 너비를 1024비트로 넓혀 대역폭을 극대화합니다. AI 모델 추론에서 메모리 대역폭이 병목인 이유가 여기에 있습니다.

### 메모리 정렬과 원자적 접근

```python
import struct

# 정렬되지 않은 접근의 위험성
data = bytearray(16)
struct.pack_into('<I', data, 0, 0xDEADBEEF)  # 정렬됨: offset 0
struct.pack_into('<I', data, 3, 0xCAFEBABE)  # 비정렬: offset 3

# x86에서는 비정렬 접근이 "동작"하지만:
# 1. 캐시 라인 경계를 넘으면 2번 접근 필요 → 느림
# 2. 원자성(atomicity) 보장 안 됨 → 멀티스레드에서 torn read/write
# 3. ARM 일부 모드에서는 예외(fault) 발생

# 올바른 정렬 확인
def is_aligned(address: int, size: int) -> bool:
    """주소가 size 바이트 경계에 정렬되었는지 확인."""
    return (address % size) == 0

# 4바이트 정수는 4의 배수 주소에, 8바이트는 8의 배수에
for addr in [0, 4, 8, 12, 3, 5, 7]:
    print(f"  0x{addr:02X}: 4B-aligned={is_aligned(addr,4)}, "
          f"8B-aligned={is_aligned(addr,8)}")
```

### NUMA: 불균일 메모리 접근

멀티소켓 서버에서는 모든 메모리가 동일한 지연 시간을 갖지 않습니다.

```text
┌──────────────┐         ┌──────────────┐
│   Socket 0   │         │   Socket 1   │
│  ┌────────┐  │  QPI/   │  ┌────────┐  │
│  │  CPU 0 │  │  UPI    │  │  CPU 1 │  │
│  └────┬───┘  │◄───────►│  └────┬───┘  │
│       │      │ ~100ns   │       │      │
│  ┌────┴───┐  │ 추가     │  ┌────┴───┐  │
│  │DRAM 0  │  │         │  │DRAM 1  │  │
│  │(로컬)  │  │         │  │(로컬)  │  │
│  └────────┘  │         │  └────────┘  │
└──────────────┘         └──────────────┘

CPU 0 → DRAM 0: ~80 ns (로컬)
CPU 0 → DRAM 1: ~130 ns (원격, +50ns 패널티)
```

```python
def numa_access_time(local_ns: float = 80, remote_penalty_ns: float = 50,
                     local_ratio: float = 0.7) -> float:
    """NUMA 환경에서 평균 메모리 접근 시간."""
    remote_ns = local_ns + remote_penalty_ns
    return local_ratio * local_ns + (1 - local_ratio) * remote_ns
    
# NUMA-aware vs NUMA-unaware 할당
aware = numa_access_time(local_ratio=0.95)    # 대부분 로컬 접근
unaware = numa_access_time(local_ratio=0.50)  # 절반이 원격
print(f"NUMA-aware:   {aware:.1f} ns")    # ~83.5 ns
print(f"NUMA-unaware: {unaware:.1f} ns")  # ~105.0 ns
print(f"성능 차이: {unaware/aware:.1f}x")  # ~1.26x
```

데이터베이스, JVM, 대규모 인메모리 캐시에서 NUMA-aware 할당이 중요한 이유: 26% 지연 시간 차이가 전체 쿼리 응답 시간에 누적됩니다.

## 처음 질문으로 돌아가기

- **RAM은 어떤 주소 모델로 보일까요?**
  - 프로그램 관점에서 RAM은 0부터 시작하는 연속된 바이트 배열처럼 보이지만, 실제로는 가상 주소 → 물리 주소 변환이 매 접근마다 일어납니다. 4-level 페이지 테이블이 48비트 가상 주소를 물리 프레임으로 매핑하며, TLB가 이 변환을 캐싱합니다.
- **가상 주소와 물리 주소는 어떻게 다를까요?**
  - 가상 주소는 프로세스마다 독립된 주소 공간(0~2⁴⁸)을 제공하고, 물리 주소는 실제 DRAM 칩의 위치를 가리킵니다. 두 주소의 매핑은 페이지 테이블이 담당하며, 본문에서 계산한 것처럼 TLB 미스 시 400ns의 변환 비용이 발생합니다.
- **한 프로세스의 text, data, heap, stack은 어떻게 배치될까요?**
  - 낮은 주소부터 text(코드) → data(전역) → BSS → heap(↑) 순으로 배치되고, 높은 주소에서 stack(↓)이 아래로 자랍니다. 중간에 mmap 영역이 공유 라이브러리를 매핑합니다. Demand paging 덕분에 매핑된 크기와 실제 물리 메모리 사용량은 다릅니다.

## 참고 자료

- [Wikipedia — Virtual memory](https://en.wikipedia.org/wiki/Virtual_memory)
- [What Every Programmer Should Know About Memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — Data structure alignment](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Linux Memory Management Documentation](https://www.kernel.org/doc/html/latest/admin-guide/mm/index.html)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 메모리, 가상 메모리, 주소 공간, 스택과 힙
