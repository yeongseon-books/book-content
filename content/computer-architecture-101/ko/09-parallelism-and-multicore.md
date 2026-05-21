---
series: computer-architecture-101
episode: 9
title: "Computer Architecture 101 (9/10): 병렬성과 멀티코어"
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
  - 병렬성
  - 멀티코어
  - 동시성
  - 동기화
seo_description: 멀티코어에서 속도가 왜 코어 수만큼 늘지 않는지 병렬성 관점에서 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (9/10): 병렬성과 멀티코어

코어가 8개라면 프로그램도 정확히 8배 빨라질까요? 대부분은 그렇지 않습니다. 이 글은 Computer Architecture 101 시리즈의 아홉 번째 글입니다. 여기서는 멀티코어 시대의 기본 사고법인 동시성과 병렬성의 차이, 동기화 비용, 캐시 일관성, 그리고 Amdahl의 법칙을 정리하겠습니다.

클럭 속도 상승이 멈춘 뒤 성능 향상의 대부분은 코어를 더하는 방향으로 왔습니다. 하지만 코어를 더하는 것과 코드를 빠르게 만드는 것은 전혀 같은 일이 아닙니다.


![Computer Architecture 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/09/09-01-big-picture.ko.png)
*Computer Architecture 101 9장 흐름 개요*

## 먼저 던지는 질문

- 동시성과 병렬성은 무엇이 다를까요?
- 멀티코어에서는 어떤 비용이 새로 생길까요?
- 락 경합과 false sharing은 왜 위험할까요?

## 왜 중요한가

오늘날의 서버, 노트북, 휴대폰은 모두 멀티코어입니다. 한 코어만 더 빠르게 돌아가던 시대는 끝났고, 성능을 끌어내려면 일을 여러 코어에 나누는 감각이 필요합니다.

하지만 병렬성은 공짜가 아닙니다. 락 경합, 캐시 핑퐁, false sharing, 작업 분배 오버헤드는 코어를 추가해도 속도가 기대만큼 오르지 않는 이유가 됩니다.

## 한눈에 보는 개념

동시성은 여러 작업을 다루는 구조이고, 병렬성은 여러 작업을 물리적으로 동시에 실행하는 능력입니다. 멀티코어는 병렬성을 가능하게 하지만 순차 구간과 동기화 비용은 남아 있습니다.

```text
   concurrency                          parallelism
   --------------------                 ---------------------
   structural ability to                physical ability to
   deal with many tasks                 run them simultaneously
                                        (multicore required)

   single-core OK                       multicore required
   async/await, generators              threads, processes, SIMD
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Concurrency | 여러 작업을 교차 진행하도록 구조화하는 능력 |
| Parallelism | 여러 작업을 실제로 동시에 실행하는 능력 |
| SMP | 대칭형 멀티프로세싱, 코어가 거의 동등한 구조 |
| NUMA | 코어 위치에 따라 메모리 접근 비용이 달라지는 구조 |
| Cache coherence | 코어별 캐시 내용을 일관되게 유지하는 메커니즘 |
| Amdahl's law | 순차 비율이 속도 향상 상한을 정한다는 법칙 |

## 적용 전과 후

**Before — 모든 코어를 아무 생각 없이 사용:**

```python
# "8 cores so it must be 8x faster"
from multiprocessing import Pool

def task(x):
    return x * 2

with Pool(8) as p:
    result = p.map(task, range(100))   # tasks too small, overhead dominates
```

**After — 작업 크기와 통신 비용 먼저 보기:**

```python
from multiprocessing import Pool

def heavy_task(n):
    return sum(i * i for i in range(n))

with Pool(8) as p:
    result = p.map(heavy_task, [10_000_000] * 8)   # enough work per core
```

같은 도구도 작업 크기에 따라 정반대 결과를 냅니다.

## 단계별로 따라가기

### 1단계: 코어 수와 단순 병렬화 확인

```python
import os, time
from multiprocessing import Pool

def work(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    print(f"logical cores: {os.cpu_count()}")

    N = 5_000_000
    tasks = [N] * 8

    start = time.time()
    [work(n) for n in tasks]
    print(f"sequential: {time.time() - start:.2f}s")

    with Pool(processes=os.cpu_count()) as p:
        start = time.time()
        p.map(work, tasks)
        print(f"parallel:   {time.time() - start:.2f}s")
```

8코어여도 보통 8배에 도달하지는 않습니다. 그 이유를 다음 단계에서 공식으로 봅니다.

### 2단계: Amdahl의 법칙 계산

```python
def amdahl_speedup(p, n):
    """p: parallelizable fraction, n: cores"""
    return 1 / ((1 - p) + p / n)

for serial in [0.05, 0.10, 0.20, 0.50]:
    p = 1 - serial
    print(f"serial {serial*100:.0f}%: cores 8 -> {amdahl_speedup(p, 8):.2f}x,"
          f"  cores inf -> {1/serial:.1f}x")
```

순차 구간이 5%만 남아도 무한 코어에서 상한은 20배입니다.

### 3단계: 락 경합 보기

```python
import threading, time

counter = 0
lock = threading.Lock()

def with_lock(iters):
    global counter
    for _ in range(iters):
        with lock:
            counter += 1

ITERS = 1_000_000
counter = 0
threads = [threading.Thread(target=with_lock, args=(ITERS,)) for _ in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"with lock: {time.time()-start:.2f}s, counter={counter}")
```

스레드를 늘려도 락 범위가 넓으면 실제로는 직렬화가 다시 생깁니다.

### 4단계: false sharing 보기

```python
import threading, time

# Adjacent indices updated by different threads share a cache line
shared = [0] * 4

def bump(idx, iters):
    for _ in range(iters):
        shared[idx] += 1

# Adjacent (false sharing)
threads = [threading.Thread(target=bump, args=(i, 5_000_000)) for i in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"adjacent: {time.time()-start:.2f}s")

# Spaced apart (false sharing reduced)
shared = [0] * 256
threads = [threading.Thread(target=bump, args=(i*64, 5_000_000)) for i in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"spaced:   {time.time()-start:.2f}s")
```

같은 양의 일도 캐시 라인을 공유하느냐에 따라 성능이 크게 달라질 수 있습니다.

### 5단계: I/O에서는 동시성이 더 중요할 때

```python
import asyncio, time

async def io_task(i):
    await asyncio.sleep(0.1)
    return i

async def main():
    start = time.time()
    await asyncio.gather(*(io_task(i) for i in range(100)))
    print(f"asyncio (concurrency, 1 core): {time.time()-start:.2f}s")

asyncio.run(main())
```

I/O 바운드 작업은 한 코어에서도 동시성으로 크게 개선될 수 있습니다. 병렬성은 CPU 바운드일 때 더 직접적입니다.

## 이 코드에서 먼저 봐야 할 점

- 코어를 추가하는 것만으로는 속도 향상이 보장되지 않습니다.
- Amdahl의 법칙은 순차 비율이 상한을 정한다는 점을 보여 줍니다.
- 락 경합과 false sharing은 흔한 병렬성 함정입니다.
- I/O 바운드 작업에는 병렬성보다 동시성이 더 맞을 수 있습니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 너무 작은 작업 병렬화 | 통신 오버헤드가 계산보다 큼 | 작업 단위를 키운다 |
| Python에서 CPU 바운드에 threading 사용 | GIL 때문에 단일 코어에 묶임 | multiprocessing 사용 |
| 락 범위를 넓게 둠 | 사실상 직렬화 복귀 | 락 범위 최소화 |
| false sharing 무시 | 캐시 핑퐁으로 성능 급락 | 패딩과 정렬 사용 |
| 모든 작업을 병렬화하려 함 | 본질적으로 순차인 부분 존재 | 먼저 상한을 추정 |

## 실무에서는 이렇게 드러납니다

- 데이터 처리는 SIMD와 분산 병렬을 함께 사용합니다.
- 웹 서버는 멀티프로세스와 비동기 I/O를 결합합니다.
- 게임 엔진은 렌더링, 물리, 오디오를 다른 코어에 배치합니다.
- ML 학습은 GPU 안의 막대한 병렬 레인을 활용합니다.
- 데이터베이스는 병렬 쿼리와 파티셔닝으로 확장합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 "병렬화하자"는 말이 나오면 먼저 두 가지를 묻습니다. 이 작업은 정말 CPU 바운드인가, 그리고 병렬화 가능한 비율은 얼마인가입니다. 많은 백엔드 작업은 I/O 바운드이므로, 거기서는 병렬성보다 동시성이 먼저 답이 됩니다.

또한 병렬화 자체의 비용을 측정합니다. 작업 분배, 결과 수집, 동기화, 캐시 일관성 트래픽이 얻는 이익보다 크면 코어를 늘릴수록 더 느려질 수 있습니다. 그래서 작은 규모에서 먼저 측정하고 점진적으로 확장합니다.

## 체크리스트

- [ ] 동시성과 병렬성 차이를 설명할 수 있는가
- [ ] Amdahl의 법칙으로 상한을 계산할 수 있는가
- [ ] 락 경합과 false sharing을 식별할 수 있는가
- [ ] CPU 바운드와 I/O 바운드를 구분할 수 있는가
- [ ] 병렬화할 만큼 작업이 충분히 큰지 판단할 수 있는가

## 연습 문제

1. 순차 비율 1%, 5%, 10%에 대해 16, 64, 256코어에서 Amdahl 속도 향상을 계산해 보세요.

2. `multiprocessing.Pool`에서 작업 크기를 바꿔 가며 언제부터 병렬화가 이득인지 찾아보세요.

3. `threading`과 `asyncio`를 I/O 작업에 각각 적용해 CPU 사용량과 시간을 비교해 보세요.

## 정리 및 다음 글

병렬성은 멀티코어 시대의 핵심이지만 자동으로 따라오지 않습니다. 동시성과 구분해 이해해야 하고, 순차 구간과 동기화 비용이 만드는 상한을 항상 함께 봐야 합니다. 코어 수보다 먼저 병렬화 가능한 비율을 보는 습관이 중요합니다.

다음 글은 이 시리즈의 마지막 글입니다. 지금까지 본 CPU, 메모리, 캐시, I/O, 병렬성을 모두 묶어 성능을 어떻게 측정하고 설명할지 정리하겠습니다.

## 심화 학습: 멀티코어 동기화와 메모리 순서 모델

### 암달의 법칙(Amdahl's Law) 정량 분석

```python
def amdahl_speedup(parallel_fraction: float, num_cores: int) -> float:
    """암달의 법칙: 병렬화 가능 비율과 코어 수에 따른 속도 향상."""
    serial_fraction = 1 - parallel_fraction
    return 1.0 / (serial_fraction + parallel_fraction / num_cores)

def gustafson_speedup(parallel_fraction: float, num_cores: int) -> float:
    """구스타프슨의 법칙: 문제 크기를 키울 때의 속도 향상."""
    serial_fraction = 1 - parallel_fraction
    return serial_fraction + parallel_fraction * num_cores

# 비교: 90% 병렬화 가능 코드
print(f"{'코어 수':>6} {'Amdahl':>8} {'Gustafson':>10}")
print("-" * 26)
for cores in [1, 2, 4, 8, 16, 32, 64, 128]:
    a = amdahl_speedup(0.90, cores)
    g = gustafson_speedup(0.90, cores)
    print(f"{cores:>6} {a:>8.2f}x {g:>9.1f}x")
```

출력:
```text
  코어 수   Amdahl  Gustafson
--------------------------
     1    1.00x       1.0x
     2    1.82x       1.9x
     4    3.08x       3.7x
     8    4.71x       7.3x
    16    6.40x      14.5x
    32    7.80x      28.9x
    64    8.77x      57.7x
   128    9.34x     115.3x
```

암달의 법칙에서 90% 병렬화 코드도 128코어에서 9.3배가 한계입니다. 10%의 직렬 부분이 병목이 됩니다. 구스타프슨의 법칙은 "문제 크기를 키우면 병렬 부분이 더 커진다"고 가정하여 더 낙관적 예측을 합니다.

### MESI 프로토콜과 캐시 일관성 비용

```python
from enum import Enum

class MESIState(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E' 
    SHARED = 'S'
    INVALID = 'I'

def mesi_transition(current: MESIState, event: str, 
                     other_cores_have: bool = False) -> tuple:
    """MESI 상태 전이 + 버스 트래픽."""
    bus_traffic = None
    new_state = current
    
    if event == 'local_read':
        if current == MESIState.INVALID:
            if other_cores_have:
                new_state = MESIState.SHARED
                bus_traffic = 'BusRd (공유 응답)'
            else:
                new_state = MESIState.EXCLUSIVE
                bus_traffic = 'BusRd (독점)'
    elif event == 'local_write':
        if current == MESIState.INVALID:
            new_state = MESIState.MODIFIED
            bus_traffic = 'BusRdX (invalidate all)'
        elif current == MESIState.SHARED:
            new_state = MESIState.MODIFIED
            bus_traffic = 'BusUpgr (invalidate others)'
        elif current == MESIState.EXCLUSIVE:
            new_state = MESIState.MODIFIED
            bus_traffic = None  # silent upgrade
    elif event == 'remote_read':
        if current == MESIState.MODIFIED:
            new_state = MESIState.SHARED
            bus_traffic = 'Flush (write-back + share)'
        elif current == MESIState.EXCLUSIVE:
            new_state = MESIState.SHARED
            bus_traffic = None
    elif event == 'remote_write':
        if current in (MESIState.MODIFIED, MESIState.EXCLUSIVE, MESIState.SHARED):
            new_state = MESIState.INVALID
            bus_traffic = 'Invalidate 수신'
    
    return new_state, bus_traffic

# 시뮬레이션: ping-pong 패턴 (false sharing)
print("=== False Sharing Ping-Pong ===")
core0_state = MESIState.INVALID
core1_state = MESIState.INVALID

events = [
    ('Core 0 write', 'local_write', 0),
    ('Core 1 write', 'local_write', 1),
    ('Core 0 write', 'local_write', 0),
    ('Core 1 write', 'local_write', 1),
]

for desc, event, core in events:
    if core == 0:
        core0_state, traffic = mesi_transition(core0_state, event, 
                                                core1_state != MESIState.INVALID)
        if core1_state != MESIState.INVALID:
            core1_state, _ = mesi_transition(core1_state, 'remote_write')
    else:
        core1_state, traffic = mesi_transition(core1_state, event,
                                                core0_state != MESIState.INVALID)
        if core0_state != MESIState.INVALID:
            core0_state, _ = mesi_transition(core0_state, 'remote_write')
    
    print(f"  {desc}: Core0={core0_state.value} Core1={core1_state.value} "
          f"Bus: {traffic or 'none'}")
```

### 메모리 순서 모델(Memory Ordering)

```text
x86 TSO (Total Store Order):
- Store→Store: 순서 보장 ✓
- Load→Load: 순서 보장 ✓
- Load→Store: 순서 보장 ✓
- Store→Load: 재배치 가능! (Store Buffer 때문)
→ 대부분의 경우 "직관적"이지만 Store→Load에서 놀라움

ARM/RISC-V (Relaxed):
- 모든 조합에서 재배치 가능
- 명시적 fence (dmb, fence) 명령어로 순서 강제
→ 더 높은 성능 가능, 프로그래밍 더 어려움
```

```python
# 메모리 순서 문제를 보여주는 예제 (개념)
import threading

# Dekker 알고리즘의 간소화: 상호 배제 시도
# x86에서도 Store→Load 재배치 때문에 실패할 수 있음

flag_a = False
flag_b = False
critical_count = 0

def thread_a():
    global flag_a, critical_count
    flag_a = True        # STORE flag_a
    # 여기에 메모리 배리어 필요!
    if not flag_b:       # LOAD flag_b (Store→Load 재배치 위험)
        critical_count += 1

def thread_b():
    global flag_b, critical_count
    flag_b = True        # STORE flag_b
    if not flag_a:       # LOAD flag_a
        critical_count += 1

# 올바른 구현은 atomic 연산 또는 fence가 필요
```

### 원자적 연산(Atomic Operations)과 하드웨어 지원

| 연산 | x86 명령어 | ARM64 명령어 | 용도 |
|------|-----------|-------------|------|
| Compare-And-Swap | `LOCK CMPXCHG` | `LDXR/STXR` (LL/SC) | Lock-free 자료구조 |
| Fetch-And-Add | `LOCK XADD` | `LDADD` | 카운터 |
| Test-And-Set | `LOCK BTS` | `LDSET` | 스핀락 |
| Load-Linked/Store-Conditional | — | `LDXR/STXR` | CAS 구현 |

```python
import threading
import time

class SpinLock:
    """CAS 기반 스핀락 (개념 구현)."""
    def __init__(self):
        self._lock = 0
        self._real_lock = threading.Lock()  # Python GIL 우회용
    
    def acquire(self):
        # 실제 하드웨어에서는 LOCK CMPXCHG로 구현
        while True:
            with self._real_lock:
                if self._lock == 0:
                    self._lock = 1
                    return
            # 스핀 대기 (CPU 시간 소모)
    
    def release(self):
        with self._real_lock:
            self._lock = 0

class TicketLock:
    """공정한 스핀락: FIFO 순서 보장."""
    def __init__(self):
        self.next_ticket = 0
        self.now_serving = 0
        self._lock = threading.Lock()
    
    def acquire(self) -> int:
        with self._lock:
            my_ticket = self.next_ticket
            self.next_ticket += 1
        # 내 차례가 올 때까지 대기
        while self.now_serving != my_ticket:
            pass  # spin
        return my_ticket
    
    def release(self):
        self.now_serving += 1
```

### 락 경합(Lock Contention) 성능 모델링

```python
def lock_contention_model(num_threads: int, critical_section_ratio: float,
                           lock_overhead_cycles: int = 50) -> dict:
    """락 경합에 따른 확장성 예측."""
    # 이상적: 모든 스레드가 독립 실행
    ideal_speedup = num_threads
    
    # 현실: 임계 구역은 직렬화됨
    # 유효 병렬 비율 = 1 - critical_section_ratio
    # + 락 오버헤드 (원자적 연산, 캐시 일관성 트래픽)
    serial_with_overhead = critical_section_ratio * (1 + lock_overhead_cycles / 1000)
    actual_speedup = 1.0 / (serial_with_overhead + (1 - critical_section_ratio) / num_threads)
    
    efficiency = actual_speedup / ideal_speedup
    
    return {
        'threads': num_threads,
        'ideal_speedup': ideal_speedup,
        'actual_speedup': actual_speedup,
        'efficiency': efficiency
    }

print(f"{'스레드':>6} {'이상적':>7} {'실제':>7} {'효율':>7}")
print("-" * 30)
for t in [1, 2, 4, 8, 16, 32]:
    r = lock_contention_model(t, critical_section_ratio=0.05)
    print(f"{r['threads']:>6} {r['ideal_speedup']:>7.1f}x {r['actual_speedup']:>6.1f}x "
          f"{r['efficiency']:>6.0%}")
```

### False Sharing 진단과 해결

```python
import sys

# False sharing 발생 조건 확인
CACHE_LINE_SIZE = 64  # bytes

class BadLayout:
    """두 스레드의 카운터가 같은 캐시 라인에 위치."""
    def __init__(self):
        self.counter_a = 0  # Thread A가 수정
        self.counter_b = 0  # Thread B가 수정
        # 두 변수가 인접 → 같은 64B 캐시 라인 안에 있을 확률 높음

class GoodLayout:
    """패딩으로 캐시 라인 분리."""
    def __init__(self):
        self.counter_a = 0
        self._pad_a = bytearray(CACHE_LINE_SIZE)  # 64B 패딩
        self.counter_b = 0
        self._pad_b = bytearray(CACHE_LINE_SIZE)

# 실무에서의 해결법:
# C/C++: alignas(64) 또는 __attribute__((aligned(64)))
# Java: @Contended 어노테이션 (JDK 8+)
# Rust: #[repr(align(64))]

print(f"BadLayout 크기 추정: counter 간 거리 < {CACHE_LINE_SIZE}B → false sharing 위험")
print(f"GoodLayout 크기 추정: counter 간 거리 >= {CACHE_LINE_SIZE}B → 안전")
```


### 이종 코어(Heterogeneous) 아키텍처

Apple M1/M2, Intel Alder Lake는 성능 코어(P-core)와 효율 코어(E-core)를 함께 배치합니다.

```text
Apple M1 구성:
┌─────────────────────────────────────────┐
│  Performance Cores (Firestorm) × 4      │
│  - 넓은 디코더 (8-wide)                 │
│  - 깊은 비순차 실행 (~630 entries ROB)   │
│  - 높은 클록 (~3.2 GHz)                 │
│  - 높은 전력 (~10W/core)                │
├─────────────────────────────────────────┤
│  Efficiency Cores (Icestorm) × 4        │
│  - 좁은 디코더 (4-wide)                 │
│  - 얕은 비순차 실행                      │
│  - 낮은 클록 (~2.0 GHz)                 │
│  - 낮은 전력 (~1W/core)                 │
├─────────────────────────────────────────┤
│  GPU Cores × 8, Neural Engine × 16      │
│  통합 메모리 (LPDDR5, 모든 유닛 공유)    │
└─────────────────────────────────────────┘
```

```python
def heterogeneous_scheduling(tasks: list, p_cores: int = 4, e_cores: int = 4,
                              p_speed: float = 1.0, e_speed: float = 0.4) -> dict:
    """이종 코어 스케줄링 시뮬레이션."""
    # 작업을 중요도(interactive vs background)로 분류
    interactive = [t for t in tasks if t.get('priority') == 'high']
    background = [t for t in tasks if t.get('priority') == 'low']
    
    # P-core에 interactive, E-core에 background 할당
    p_throughput = min(len(interactive), p_cores) * p_speed
    e_throughput = min(len(background), e_cores) * e_speed
    
    # 전력 효율
    p_power = min(len(interactive), p_cores) * 10  # W
    e_power = min(len(background), e_cores) * 1    # W
    total_power = p_power + e_power
    total_throughput = p_throughput + e_throughput
    
    return {
        'throughput': total_throughput,
        'power_watts': total_power,
        'perf_per_watt': total_throughput / total_power if total_power > 0 else 0
    }

tasks = ([{'priority': 'high'}] * 3 + [{'priority': 'low'}] * 6)
result = heterogeneous_scheduling(tasks)
print(f"처리량: {result['throughput']:.1f} units")
print(f"전력: {result['power_watts']:.0f}W")
print(f"성능/와트: {result['perf_per_watt']:.2f}")
```

### SIMD/벡터 병렬성

단일 코어 내에서도 데이터 병렬성을 활용할 수 있습니다.

```text
스칼라 덧셈:           SIMD 덧셈 (256-bit AVX2):
A[0] + B[0] = C[0]    A[0..7] + B[0..7] = C[0..7]
A[1] + B[1] = C[1]    (한 명령어로 8개 float32 동시 처리)
A[2] + B[2] = C[2]
...                    
A[7] + B[7] = C[7]    
→ 8개 명령어           → 1개 명령어
```

```python
import numpy as np
import time

# NumPy의 SIMD 활용 측정
n = 10_000_000
a = np.random.randn(n).astype(np.float32)
b = np.random.randn(n).astype(np.float32)

# 벡터 연산 (내부적으로 AVX/NEON 사용)
start = time.perf_counter()
for _ in range(100):
    c = a + b
simd_time = time.perf_counter() - start

# 순수 Python 루프 (SIMD 없음)
start = time.perf_counter()
c_list = [a[i] + b[i] for i in range(min(n, 100000))]  # 일부만
scalar_time = (time.perf_counter() - start) * (n / 100000)

print(f"NumPy (SIMD): {simd_time:.3f}초 (1천만 × 100회)")
print(f"Python 루프 (추정): {scalar_time:.1f}초 (1천만 × 1회)")
print(f"속도 차이: ~{scalar_time * 100 / simd_time:.0f}배")
```

| SIMD 확장 | 벡터 너비 | float32 동시 처리 | 프로세서 |
|-----------|-----------|-----------------|----------|
| SSE4 | 128 bit | 4개 | x86 (2006~) |
| AVX2 | 256 bit | 8개 | x86 (2013~) |
| AVX-512 | 512 bit | 16개 | x86 서버 (2017~) |
| NEON | 128 bit | 4개 | ARM (2009~) |
| SVE/SVE2 | 128~2048 bit | 4~64개 | ARM 서버 (2020~) |

### GPU 병렬성: 수천 코어의 활용

```text
CPU vs GPU 구조:
CPU (8코어):                    GPU (수천 코어):
┌──────────────────┐           ┌──────────────────────────┐
│ 큰 코어 × 8      │           │ 작은 코어 × 5120         │
│ 복잡한 제어 로직  │           │ 단순한 제어 (SIMT)       │
│ 큰 캐시          │           │ 작은 캐시 (공유 메모리)   │
│ 높은 단일 성능   │           │ 높은 집합 처리량         │
│ 다양한 작업      │           │ 동일 작업 대량 병렬      │
└──────────────────┘           └──────────────────────────┘

적합한 작업:
CPU: 분기 많음, 캐시 활용, 직렬 의존성 → 웹 서버, 컴파일러, DB
GPU: 동일 연산 반복, 데이터 독립 → 행렬 곱셈, 렌더링, AI 추론
```

## 처음 질문으로 돌아가기

- **동시성과 병렬성은 무엇이 다를까요?**
  - 동시성(concurrency)은 여러 작업이 논리적으로 겹쳐 진행되는 것(단일 코어에서도 가능, 컨텍스트 스위칭)이고, 병렬성(parallelism)은 물리적으로 동시에 실행되는 것(멀티코어 필수)입니다. 동시성은 구조의 문제이고, 병렬성은 실행의 문제입니다.
- **멀티코어에서는 어떤 비용이 새로 생길까요?**
  - 캐시 일관성 유지(MESI 프로토콜의 invalidate 메시지), 원자적 연산의 버스 트래픽, 메모리 순서 보장을 위한 fence 명령어, 그리고 락 경합 시 직렬화 비용이 새로 발생합니다. 심화 학습에서 본 것처럼, ping-pong 패턴은 매 접근마다 캐시 라인을 코어 간 이동시켜 수십 배 성능 저하를 일으킵니다.
- **락 경합과 false sharing은 왜 위험할까요?**
  - 락 경합은 임계 구역을 직렬화하여 암달의 법칙에 의한 확장성 상한을 만듭니다. False sharing은 논리적으로 독립인 데이터가 같은 캐시 라인에 있어 불필요한 일관성 트래픽을 발생시킵니다. 둘 다 코어를 추가해도 성능이 오르지 않거나 오히려 떨어지는 원인입니다.

<!-- toc:begin -->
## 이 시리즈
- [Computer Architecture 101 (1/10): 컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): 데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [Computer Architecture 101 (3/10): CPU와 명령어](./03-cpu-and-instructions.md)
- [Computer Architecture 101 (4/10): 레지스터와 ALU](./04-registers-and-alu.md)
- [Computer Architecture 101 (5/10): 메모리 구조](./05-memory-organization.md)
- [Computer Architecture 101 (6/10): 캐시와 지역성](./06-cache-and-locality.md)
- [Computer Architecture 101 (7/10): 파이프라인](./07-pipelining.md)
- [Computer Architecture 101 (8/10): I/O와 장치](./08-io-and-devices.md)
- **Computer Architecture 101 (9/10): 병렬성과 멀티코어 (현재 글)**
- Computer Architecture 101 (10/10): 성능을 이해하는 법 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Amdahl's law](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Wikipedia — Cache coherence](https://en.wikipedia.org/wiki/Cache_coherence)
- [Wikipedia — False sharing](https://en.wikipedia.org/wiki/False_sharing)
- [The Free Lunch Is Over (Herb Sutter, 2005)](http://www.gotw.ca/publications/concurrency-ddj.htm)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 병렬성, 멀티코어, 동시성, 동기화
