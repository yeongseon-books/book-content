---
series: computer-science-101
episode: 5
title: "Computer Science 101 (5/10): 컴퓨터 구조"
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
  - 메모리
  - 캐시
  - 성능
seo_description: CPU, 메모리, 캐시 계층이 코드의 실제 성능을 어떻게 바꾸는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (5/10): 컴퓨터 구조

Big-O가 같은데도 어떤 코드는 유난히 빠르고 어떤 코드는 묵직하게 느린 경우가 있습니다. 이 차이는 알고리즘 설명만으로는 부족하고, 코드가 하드웨어를 어떤 순서와 밀도로 건드리는지까지 봐야 풀립니다.

이 글은 Computer Science 101 시리즈의 5번째 글입니다.

여기서는 폰 노이만 구조, CPU 실행 단계, 메모리 계층, 캐시 친화성 같은 개념이 실제 코드 성능에 어떻게 드러나는지 정리하겠습니다.


![Computer Science 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/05/05-01-concept-at-a-glance.ko.png)
*Computer Science 101 5장 흐름 개요*

## 먼저 던지는 질문

- 같은 Big-O라도 실제 실행 시간이 크게 다른 이유는 무엇일까요?
- CPU, 레지스터, 캐시, RAM은 어떤 속도 차이와 역할 차이를 가질까요?
- 행 우선 순회와 열 우선 순회가 왜 캐시 성능을 갈라놓을까요?

## 이 글에서 배울 것

- 폰 노이만 구조의 핵심 구성 요소
- CPU가 명령어를 실행하는 기본 단계
- 레지스터→캐시→RAM→디스크로 이어지는 메모리 계층
- 지역성과 캐시 친화적 코드의 의미

## 왜 중요한가

알고리즘만으로는 설명되지 않는 성능 차이가 항상 존재합니다. 같은 O(n) 코드가 두 배 빠른 이유, 행렬을 어떤 순서로 순회하느냐로 10배 차이가 나는 이유는 모두 메모리 계층 때문입니다.

> CPU는 빠르고, 메모리는 느립니다. 그 격차를 줄이는 것이 캐시입니다.

하드웨어를 모르고 짠 알고리즘은 종이 위에서만 빠릅니다.

## 한눈에 보는 개념

> 메모리 계층이 위로 갈수록 빠르고 비싸고 작으며, 아래로 갈수록 느리고 싸고 큽니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| CPU | 명령어를 해석하고 연산을 수행하는 장치 |
| Register | CPU 내부에 있는 가장 빠른 저장소 |
| Cache | CPU와 메모리 사이의 빠른 중간 저장소 |
| RAM | 프로그램 실행 중 사용하는 주기억장치 |
| Bus | CPU·메모리·장치 사이에서 데이터를 오가는 경로 |
| Clock | CPU가 초당 수행하는 사이클 속도 |

## 적용 전후 비교
**Before — 캐시 비친화적 코드:**

```python
# 2D list를 열 우선 순회 — cache miss 빈번
N = 2000
matrix = [[0] * N for _ in range(N)]

for j in range(N):           # outer loop is the column
    for i in range(N):       # inner loop is the row
        matrix[i][j] += 1    # jump to a different row on every access
```

**After — 캐시 친화적 코드:**

```python
# 행 우선 순회 — 인접 메모리에 순차 접근
for i in range(N):           # outer loop is the row
    for j in range(N):       # inner loop is the column
        matrix[i][j] += 1    # adjacent memory access within the same row
```

같은 O(n²)이지만 두 번째 코드는 캐시 라인을 효율적으로 사용해 더 빠릅니다.

## 단계별로 따라하기

### 1단계: 메모리 접근 패턴이 만드는 성능 차이

```python
import time

N = 2000
matrix = [[0] * N for _ in range(N)]

start = time.perf_counter()
for i in range(N):
    for j in range(N):
        matrix[i][j] += 1
print(f"row-major   : {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
for j in range(N):
    for i in range(N):
        matrix[i][j] += 1
print(f"column-major: {time.perf_counter() - start:.3f}s")
```

**Expected output:** 같은 O(n²)라도 `row-major`가 `column-major`보다 빠르게 찍혀 캐시 친화성의 차이를 체감할 수 있어야 합니다.

### 2단계: NumPy로 메모리 레이아웃 확인

```python
import numpy as np

a = np.arange(12).reshape(3, 4)        # default is C-order (row-major)
print(a.flags["C_CONTIGUOUS"])         # True
print(a.flags["F_CONTIGUOUS"])         # False

b = np.asfortranarray(a)               # Fortran-order (column-major)
print(b.flags["F_CONTIGUOUS"])         # True

# 같은 데이터여도 메모리 layout이 다르면 순회 속도도 달라짐
```

### 3단계: 메모리 계층의 속도 차이 체감

```python
# 크기를 늘려가며 데이터 합산 — cache 계층 차이가 드러남
import time

for power in [10, 14, 18, 22, 24]:
    n = 1 << power                      # 2^power
    data = [1] * n
    start = time.perf_counter()
    total = 0
    for x in data:
        total += x
    print(f"n=2^{power:>2}  size~{n * 28 // 1024:>10} KB  time={time.perf_counter() - start:.3f}s")
```

### 4단계: CPU가 한 사이클에 하는 일

```python
# 3 GHz 클럭 = 초당 30억 cycle
# 단순 덧셈 = 약 1 cycle
# 메인 메모리 접근 = 약 300 cycle(L1 hit 대비 약 100배)

# 명령어 단계(Fetch-Decode-Execute) 의사코드
def cpu_cycle(instruction: str) -> None:
    """1. Fetch  — read the instruction from memory.
       2. Decode — interpret the instruction.
       3. Execute — perform the operation in the ALU.
       4. Write back — store the result in a register or memory."""
    fetch = f"read: {instruction}"
    decode = "decoding"
    execute = "executing"
    write_back = "storing result"
    print(fetch, decode, execute, write_back, sep=" -> ")

cpu_cycle("ADD R1, R2, R3")
```

### 5단계: 지역성을 활용한 데이터 패킹

```python
# 객체 list(분산 메모리)와 필드별 배열(연속 메모리) 비교
import array
import time

N = 1_000_000

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

points = [Point(i, i) for i in range(N)]
xs = array.array("d", [float(i) for i in range(N)])

start = time.perf_counter()
total = sum(p.x for p in points)
print(f"object list : {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
total = sum(xs)
print(f"flat array  : {time.perf_counter() - start:.3f}s")
```

## 이 코드에서 먼저 봐야 할 점

- 같은 알고리즘도 메모리 접근 순서에 따라 성능이 달라집니다
- 인접 메모리에 순차 접근하면 캐시 라인을 한 번에 활용합니다 (공간 지역성)
- 같은 데이터를 여러 번 사용하면 캐시에 머물러 빠릅니다 (시간 지역성)
- Python 객체 리스트는 포인터의 배열이므로 캐시 친화성이 떨어집니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 2차원 배열을 열 우선으로 순회 | 캐시 미스 폭증 | 메모리 레이아웃과 같은 순서로 순회 |
| 큰 객체 그래프를 그대로 처리 | 포인터 추적으로 캐시 비효율 | NumPy 배열, dataclass `__slots__` 활용 |
| 디스크 I/O를 한 줄씩 처리 | 시스템 콜 오버헤드 | 버퍼링·청크 단위 읽기 |
| 메모리 부족 시 가상 메모리 의존 | 스왑 발생 시 1만 배 느려짐 | 데이터 크기와 메모리 한계를 먼저 확인 |
| Python의 `list`가 배열인 줄 안다 | 포인터의 배열이라 산술 연산 느림 | 수치 연산은 `array` 또는 `numpy` |

## 실무에서는 이렇게 쓰입니다

- 데이터 처리 파이프라인에서 NumPy/Pandas로 벡터화하여 캐시 효율 확보
- 게임·그래픽스에서 ECS(Entity-Component-System)로 데이터 지역성 향상
- DB 엔진의 컬럼 스토어(Parquet, ClickHouse) — 분석 쿼리에 유리
- 동시성 코드에서 false sharing(같은 캐시 라인 경합) 회피
- 컨테이너 환경에서 CPU·메모리 limit과 NUMA 인지 스케줄링

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 알고리즘 차수를 낮추고, 그다음에는 메모리 접근 패턴을 의심합니다. O(n^2)라도 캐시에 잘 맞으면 충분히 빠를 수 있고, O(n log n)이라도 포인터 추적이 심하면 체감이 무거워질 수 있다는 감각이 있습니다.

그렇다고 모든 코드를 캐시 최적화 대상으로 보지는 않습니다. 프로파일러가 가리킨 hot path에만 정밀하게 손을 대고, 나머지는 가독성을 우선합니다. 어디를 고쳐야 하는지 모를 때는 먼저 측정합니다.


### 메모리 계층별 지연 시간 비교

프로그래머가 체감하는 성능은 대부분 메모리 접근 패턴에서 결정됩니다. 각 계층의 지연 시간을 비교하면 왜 캐시가 중요한지 명확해집니다.

| 계층 | 용량 (일반적) | 지연 시간 | CPU 사이클 기준 | 비유 (1 사이클 = 1초) |
|------|--------------|-----------|-----------------|----------------------|
| 레지스터 | ~1 KB | < 1 ns | 1 사이클 | 1초 |
| L1 캐시 | 32-64 KB | ~1 ns | 3-4 사이클 | 3초 |
| L2 캐시 | 256 KB - 1 MB | ~3-10 ns | 10-30 사이클 | 10초 |
| L3 캐시 | 4-64 MB | ~10-40 ns | 30-120 사이클 | 40초 |
| RAM (DRAM) | 8-128 GB | ~50-100 ns | 150-300 사이클 | 2분 |
| NVMe SSD | 256 GB - 4 TB | ~10-100 μs | 30,000-300,000 | 1-3일 |
| HDD | 1-20 TB | ~5-10 ms | 15,000,000 | 수 개월 |
| 네트워크 (같은 DC) | — | ~0.5 ms | 1,500,000 | 2주 |

L1 캐시 미스 한 번이 RAM 접근으로 이어지면 약 100배 느려집니다. 이것이 같은 Big-O라도 캐시 친화적 코드가 훨씬 빠른 근본 이유입니다.

### CPU 파이프라인과 명령어 수준 병렬성

현대 CPU는 하나의 명령어를 여러 단계로 나누어 동시에 처리합니다.

```text
시간 →   T1    T2    T3    T4    T5    T6    T7
명령어1  [IF] [ID] [EX] [ME] [WB]
명령어2       [IF] [ID] [EX] [ME] [WB]
명령어3            [IF] [ID] [EX] [ME] [WB]

IF = Instruction Fetch, ID = Decode, EX = Execute, ME = Memory, WB = Write Back
```

5단계 파이프라인에서는 매 사이클마다 하나의 명령어가 완료됩니다(이상적인 경우). 하지만 다음 상황에서 파이프라인이 멈춥니다(스톨):

1. **데이터 해저드**: 이전 명령어 결과를 다음 명령어가 즉시 필요로 할 때
2. **분기 해저드**: 조건 분기의 결과를 알기 전까지 다음 명령어를 결정할 수 없을 때
3. **구조 해저드**: 같은 하드웨어 자원을 두 명령어가 동시에 필요로 할 때

```python
# 분기 예측에 불리한 코드 — 랜덤 패턴
import random, time

data = [random.randint(0, 255) for _ in range(1_000_000)]

start = time.perf_counter()
total = sum(x for x in data if x >= 128)
print(f"unsorted: {time.perf_counter() - start:.4f}s, sum={total}")

# 분기 예측에 유리한 코드 — 정렬된 패턴
data.sort()
start = time.perf_counter()
total = sum(x for x in data if x >= 128)
print(f"sorted  : {time.perf_counter() - start:.4f}s, sum={total}")
```

정렬된 데이터에서는 분기 예측기가 패턴을 학습하기 쉬워서 파이프라인 스톨이 줄어듭니다. 이 차이는 같은 O(n) 알고리즘에서도 2-5배 성능 차이를 만들 수 있습니다.

### 캐시 라인과 공간 지역성 실험

CPU는 메모리를 바이트 단위가 아니라 캐시 라인(보통 64바이트) 단위로 읽습니다.

```python
import time
import array

# 연속 접근 (공간 지역성 활용) vs 불연속 접근
SIZE = 4_000_000
arr = array.array('i', range(SIZE))  # int32 배열

# 순차 접근 — 캐시 라인을 연속으로 사용
start = time.perf_counter()
total = 0
for i in range(SIZE):
    total += arr[i]
seq_time = time.perf_counter() - start

# 스트라이드 접근 — 캐시 라인을 낭비
import random
indices = list(range(SIZE))
random.shuffle(indices)

start = time.perf_counter()
total = 0
for i in indices:
    total += arr[i]
rand_time = time.perf_counter() - start

print(f"순차 접근: {seq_time:.4f}s")
print(f"랜덤 접근: {rand_time:.4f}s")
print(f"비율: {rand_time / seq_time:.1f}x 느림")
```

랜덤 접근은 순차 접근보다 통상 3-10배 느립니다. 같은 양의 데이터를 읽어도 접근 패턴이 캐시 미스를 결정합니다.

### 행 우선 vs 열 우선 순회의 캐시 영향

2차원 배열에서 이 원리가 극명하게 드러납니다.

```python
import time

N = 2000
# Python list-of-lists(행 우선 저장)
matrix = [[i * N + j for j in range(N)] for i in range(N)]

# 행 우선 순회: matrix[i][j] — 연속 메모리 접근
start = time.perf_counter()
total = 0
for i in range(N):
    for j in range(N):
        total += matrix[i][j]
row_time = time.perf_counter() - start

# 열 우선 순회: matrix[j][i] — 불연속 메모리 접근 (stride = N)
start = time.perf_counter()
total = 0
for j in range(N):
    for i in range(N):
        total += matrix[i][j]
col_time = time.perf_counter() - start

print(f"행 우선: {row_time:.4f}s")
print(f"열 우선: {col_time:.4f}s")
print(f"비율: {col_time / row_time:.1f}x")
```

C/Python에서 2차원 배열은 행 우선(row-major)으로 저장됩니다. `matrix[i][j]`를 `j` 순서로 순회하면 메모리를 연속으로 읽어 캐시 라인을 효율적으로 씁니다. 열 우선 순회는 매번 N칸을 건너뛰므로 캐시 미스가 폭증합니다.

NumPy에서 `order='C'`(행 우선)와 `order='F'`(열 우선, Fortran 스타일)를 선택할 수 있는 이유가 바로 이 때문입니다.

### 가상 메모리와 페이지 테이블

운영체제는 프로세스에 연속된 가상 주소 공간을 제공하지만, 물리 메모리는 실제로 흩어져 있을 수 있습니다.

```text
가상 주소 공간 (프로세스 A)         물리 메모리
┌──────────────────┐               ┌──────────────────┐
│ 0x0000 코드 영역  │ ──── 페이지 ───→ │ 프레임 7          │
│ 0x1000 데이터     │ ──── 테이블 ───→ │ 프레임 2          │
│ 0x2000 힙        │ ──── 변환  ───→ │ 프레임 15         │
│ ...              │               │ ...              │
│ 0xF000 스택      │ ─────────────→ │ 프레임 42         │
└──────────────────┘               └──────────────────┘
```

- **페이지**: 가상 메모리의 고정 크기 블록 (보통 4 KB)
- **프레임**: 물리 메모리의 같은 크기 블록
- **TLB (Translation Lookaside Buffer)**: 페이지 테이블의 캐시. 미스 시 페이지 테이블을 메모리에서 읽어야 하므로 수십 ns 추가

대용량 데이터를 처리할 때 2 MB 또는 1 GB 대형 페이지(huge page)를 사용하면 TLB 미스를 크게 줄일 수 있습니다. Linux에서는 `madvise(MADV_HUGEPAGE)` 또는 transparent huge pages로 활성화합니다.

### NUMA와 멀티 소켓 시스템

서버급 시스템은 여러 CPU 소켓이 각자의 로컬 메모리를 가집니다(Non-Uniform Memory Access).

```text
┌─────────────────┐         ┌─────────────────┐
│   Socket 0      │         │   Socket 1      │
│ ┌─────────────┐ │  QPI/   │ ┌─────────────┐ │
│ │ CPU 코어 0-7│ │  UPI    │ │ CPU 코어 8-15│ │
│ └─────────────┘ │ ←────→  │ └─────────────┘ │
│ ┌─────────────┐ │ 인터    │ ┌─────────────┐ │
│ │ 로컬 RAM    │ │ 커넥트  │ │ 로컬 RAM    │ │
│ │ 64 GB       │ │         │ │ 64 GB       │ │
│ └─────────────┘ │         │ └─────────────┘ │
└─────────────────┘         └─────────────────┘
```

Socket 0의 코어가 Socket 1의 RAM에 접근하면 인터커넥트를 경유하므로 지연이 1.5-2배 늘어납니다. 데이터베이스 같은 메모리 집약적 프로그램은 `numactl --membind` 옵션으로 데이터와 스레드를 같은 NUMA 노드에 배치해 성능을 확보합니다.

### 성능 측정 도구와 해석

이론을 확인하려면 측정이 필수입니다. Linux에서 사용하는 주요 도구를 정리합니다.

| 도구 | 용도 | 핵심 지표 |
|------|------|----------|
| `perf stat` | 하드웨어 카운터 요약 | IPC, 캐시 미스율, 분기 미스율 |
| `perf record` + `perf report` | 함수별 CPU 점유 분석 | hot function, 호출 그래프 |
| `valgrind --tool=cachegrind` | 캐시 시뮬레이션 | L1/L2/L3 미스 횟수 |
| `time` | 벽시계 시간 | real, user, sys |
| `strace` | 시스템 콜 추적 | I/O 대기, 컨텍스트 스위치 |

```bash
# 예: Python 스크립트의 캐시 미스 측정
perf stat -e cache-misses,cache-references,instructions,cycles \
    python3 matrix_multiply.py

# 출력 예시:
#  2,341,567  cache-misses  (12.3% of cache-references)
# 19,032,456  cache-references
# 891,234,567 instructions  (IPC: 1.23)
# 724,567,890 cycles
```

IPC(Instructions Per Cycle)가 1 미만이면 메모리 대기가 심하다는 뜻입니다. 캐시 미스율이 10%를 넘으면 데이터 접근 패턴을 재검토해야 합니다.
## 체크리스트

- [ ] CPU·메모리·캐시의 속도 차이를 어림으로 말할 수 있는가
- [ ] 공간 지역성과 시간 지역성의 차이를 설명할 수 있는가
- [ ] 2차원 배열을 행 우선으로 순회해야 하는 이유를 아는가
- [ ] Python `list`가 진짜 배열이 아니라는 점을 이해했는가
- [ ] 디스크 I/O 비용이 메모리 대비 얼마나 큰지 감각이 있는가

## 연습 문제

1. 1000x1000 행렬을 행 우선과 열 우선으로 각각 순회하며 실행 시간 비율을 측정해 보세요.
2. `list`, `array.array`, `numpy.ndarray`에 백만 개의 정수를 넣고 합산 시간을 비교해 보세요.
3. `for` 루프, 리스트 내포, NumPy 벡터화로 제곱합을 계산하고 어떤 접근이 왜 빠른지 분석해 보세요.

## 정리 및 다음 단계

CPU는 빠르고 메모리는 느립니다. 캐시는 그 격차를 메우는 계층이며, 캐시를 잘 쓰는 코드는 같은 알고리즘으로도 수십 배 빠릅니다. 좋은 엔지니어는 알고리즘 차수를 낮춘 뒤 메모리 접근 패턴까지 확인합니다.

다음 글에서는 이 하드웨어 위에서 여러 프로그램이 어떻게 공존하고 자원을 나눠 쓰는지 — 운영체제 — 를 다룹니다.


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

컴퓨터 구조 단원에서는 캐시 계층, 분기 예측, 메모리 대역폭 같은 하드웨어 특성이 소프트웨어 성능을 어떻게 규정하는지 연결해 학습합니다.


## 처음 질문으로 돌아가기

- **같은 Big-O라도 실제 실행 시간이 크게 다른 이유는 무엇일까요?**
  - 캐시 적중률, 분기 예측 성공률, 파이프라인 스톨, NUMA 로컬리티 등 하드웨어 요인이 상수항을 수십 배까지 바꿉니다. Big-O는 증가율만 표현하므로 같은 O(n)이라도 메모리 접근 패턴에 따라 실측이 크게 달라집니다.
- **CPU, 레지스터, 캐시, RAM은 어떤 속도 차이와 역할 차이를 가질까요?**
  - 레지스터는 1사이클, L1은 3-4사이클, RAM은 150-300사이클로, 계층이 내려갈수록 용량은 늘고 속도는 수백 배 떨어집니다. CPU는 자주 쓰는 데이터를 상위 계층에 자동으로 올려 평균 접근 시간을 줄입니다.
- **행 우선 순회와 열 우선 순회가 왜 캐시 성능을 갈라놓을까요?**
  - 메모리는 행 우선으로 배치되고 CPU는 64바이트 캐시 라인 단위로 읽습니다. 행 우선 순회는 한 번 읽은 캐시 라인의 모든 원소를 연속 사용하지만, 열 우선 순회는 매번 N칸을 건너뛰어 캐시 라인의 대부분을 낭비합니다.
<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- [Computer Science 101 (4/10): 알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- **컴퓨터 구조 (현재 글)**
- 운영체제 (예정)
- 네트워크 (예정)
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Computer Organization and Design (Patterson & Hennessy)](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [Ulrich Drepper — What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Agner Fog — Optimization Manuals](https://www.agner.org/optimize/)

- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)
Tags: Computer Science, 컴퓨터 구조, CPU, 메모리, 캐시, 성능
