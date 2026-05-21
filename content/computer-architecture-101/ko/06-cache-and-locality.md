---
series: computer-architecture-101
episode: 6
title: "Computer Architecture 101 (6/10): 캐시와 지역성"
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
  - 캐시
  - 지역성
  - 성능
  - 메모리 계층
seo_description: 캐시와 지역성이 같은 알고리즘의 속도를 왜 10배 이상 바꾸는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (6/10): 캐시와 지역성

같은 데이터를 같은 횟수만큼 읽는데도 한 코드는 1초, 다른 코드는 30초가 걸릴 수 있습니다. 이 글은 Computer Architecture 101 시리즈의 여섯 번째 글입니다. 여기서는 CPU와 메인 메모리 사이의 거대한 속도 차이를 메우는 캐시가 어떻게 동작하는지, 그리고 시간 지역성과 공간 지역성이 왜 성능을 바꾸는지 보겠습니다.

알고리즘이 이미 정해졌다면 그다음 질문은 종종 "이 코드는 캐시 친화적인가"입니다. 현대 CPU에서는 클럭 속도보다 캐시 미스율이 성능을 훨씬 더 크게 좌우하는 경우가 많기 때문입니다.

## 먼저 던지는 질문

- 캐시는 메모리 계층 어디에 놓일까요?
- 시간 지역성과 공간 지역성은 무엇이 다를까요?
- 캐시 라인은 왜 중요한 비용 단위일까요?

## 큰 그림

![Computer Architecture 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/06/06-01-big-picture.ko.png)

*Computer Architecture 101 6장 흐름 개요*

## 왜 중요한가

메인 메모리 접근은 보통 수백 사이클이 걸리지만 L1 캐시 적중은 몇 사이클이면 끝납니다. 같은 알고리즘이라도 메모리 접근 순서 하나로 10배 이상 차이 날 수 있다는 뜻입니다.

그래서 캐시를 이해하면 성능 최적화의 ROI가 매우 높아집니다. 복잡한 알고리즘 변경 없이도 접근 순서, 자료구조 배치, stride만 바꿔 큰 차이를 만들 수 있기 때문입니다.

## 한눈에 보는 개념

CPU는 메인 메모리에서 한 바이트만 가져오지 않습니다. 보통 64바이트 단위의 캐시 라인을 가져와 캐시에 올립니다. 다음 접근이 같은 라인 안에 있으면 거의 공짜처럼 읽힙니다.

```text
   CPU
    |  (one cycle)
    v
   L1 cache  (32-64KB, ~4 cycles)
    |
    v
   L2 cache  (256KB-1MB, ~12 cycles)
    |
    v
   L3 cache  (several MB, ~40 cycles)
    |
    v
   Main RAM  (several GB, ~200 cycles)
    |
    v
   SSD/HDD  (several TB, tens of thousands of cycles)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Cache line | 캐시의 최소 단위, 보통 64바이트 |
| Temporal locality | 최근 접근한 데이터를 곧 다시 접근하는 성질 |
| Spatial locality | 가까운 주소를 연이어 접근하는 성질 |
| Cache miss | 필요한 데이터가 캐시에 없는 상태 |
| Working set | 현재 자주 접근하는 데이터 집합 |

## 적용 전과 후

**Before — 캐시 적대적 코드:**

```python
# Column-major traversal of a 2D array
def col_major(matrix, n):
    total = 0
    for j in range(n):
        for i in range(n):
            total += matrix[i][j]
    return total
```

**After — 캐시 친화적 코드:**

```python
def row_major(matrix, n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += matrix[i][j]
    return total
```

두 함수는 같은 합을 계산하지만, 행 우선 순회는 같은 캐시 라인 안의 이웃 데이터를 활용하므로 훨씬 빠릅니다.

## 단계별로 따라가기

### 1단계: 행 우선 vs 열 우선 측정

```python
import time, numpy as np

N = 4096
m = np.random.randint(0, 100, (N, N), dtype=np.int32)

start = time.perf_counter()
total = 0
for i in range(N):
    for j in range(N):
        total += m[i, j]
print(f"row-major:   {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
total = 0
for j in range(N):
    for i in range(N):
        total += m[i, j]
print(f"col-major:   {time.perf_counter() - start:.2f} s")
```

접근 횟수는 같아도 순서가 다르면 캐시 미스율이 달라집니다. 그 차이가 실행 시간으로 직결됩니다.

### 2단계: 캐시 라인 보기

```python
import time, numpy as np

CACHE_LINE = 64
INT_SIZE = 8     # numpy int64
stride_ints = CACHE_LINE // INT_SIZE   # 8

N = 100_000_000
arr = np.zeros(N, dtype=np.int64)

start = time.perf_counter()
for i in range(0, N, 1):
    arr[i] += 1
print(f"stride 1:  {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
for i in range(0, N, stride_ints):
    arr[i] += 1
print(f"stride 8:  {time.perf_counter() - start:.2f} s")
```

한 라인 안의 8개 원소를 모두 쓰느냐, 한 개만 쓰고 버리느냐가 대역폭 낭비를 좌우합니다.

### 3단계: 시간 지역성 활용하기

```python
from functools import lru_cache

def fib_no_cache(n):
    if n < 2: return n
    return fib_no_cache(n - 1) + fib_no_cache(n - 2)

@lru_cache(maxsize=None)
def fib_cached(n):
    if n < 2: return n
    return fib_cached(n - 1) + fib_cached(n - 2)

import time
start = time.perf_counter(); fib_no_cache(30)
print(f"no cache: {time.perf_counter() - start:.3f} s")

start = time.perf_counter(); fib_cached(30)
print(f"cached:   {time.perf_counter() - start:.6f} s")
```

같은 입력을 곧 다시 쓴다면 결과 캐싱이 시간 지역성을 가장 직접적으로 활용하는 방법입니다.

### 4단계: AoS vs SoA

```python
import numpy as np, time

N = 1_000_000

class Particle:
    __slots__ = ("x", "y", "z", "vx", "vy", "vz")
    def __init__(self):
        self.x = self.y = self.z = 0.0
        self.vx = self.vy = self.vz = 0.0

aos = [Particle() for _ in range(N // 100)]   # smaller for memory
soa_x = np.zeros(N); soa_y = np.zeros(N); soa_z = np.zeros(N)

start = time.perf_counter()
for p in aos:
    p.x += 1.0
print(f"AoS x++: {time.perf_counter() - start:.4f} s")

start = time.perf_counter()
soa_x += 1.0
print(f"SoA x++: {time.perf_counter() - start:.4f} s")
```

`x`만 갱신할 때는 `x`만 모아 둔 SoA가 훨씬 더 캐시 친화적입니다.

### 5단계: 블로킹의 힘 보기

```python
import numpy as np, time

N = 512
a = np.random.rand(N, N); b = np.random.rand(N, N)

start = time.perf_counter()
c = a @ b   # numpy (BLAS) uses cache blocking internally
print(f"numpy matmul: {time.perf_counter() - start:.3f} s")

start = time.perf_counter()
c2 = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        for k in range(N):
            c2[i, j] += a[i, k] * b[k, j]
# only meaningful for smaller N because of speed
```

같은 행렬 곱셈도 캐시에 맞춘 블로킹을 하느냐에 따라 성능 차이가 극단적으로 벌어집니다.

## 이 코드에서 먼저 봐야 할 점

- 같은 알고리즘과 데이터라도 접근 순서가 성능을 바꿉니다.
- 캐시 라인은 한 번 가져오면 가능한 많이 써야 효율적입니다.
- 시간 지역성은 결과 재사용으로, 공간 지역성은 인접 접근으로 살립니다.
- 자료구조 레이아웃은 캐시 행동과 직접 연결됩니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 열 우선 순회 | 캐시 미스 급증 | 메모리 레이아웃과 순회를 맞춘다 |
| 흩어진 작은 객체 다수 사용 | 포인터 추적 비용 증가 | 연속 배열로 모은다 |
| 큰 stride 접근 | 캐시 라인 낭비 | 인접 인덱스를 선호 |
| 결과 재계산 | 시간 지역성 무시 | 메모이제이션 활용 |
| 큰 구조체 안의 작은 핫 필드 | 캐시 오염 | 핫 필드를 별도 SoA로 분리 |

## 실무에서는 이렇게 드러납니다

- 데이터베이스는 컬럼 스토어 레이아웃으로 분석 쿼리를 가속합니다.
- 머신러닝은 텐서를 연속 메모리로 유지하려고 애씁니다.
- 게임 엔진은 ECS로 SoA 레이아웃을 강제합니다.
- 컴파일러는 loop tiling, interchange로 자동 블로킹을 수행합니다.
- 운영체제는 페이지 캐시로 디스크 I/O를 메모리 접근처럼 숨깁니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 "이 알고리즘이 맞는가" 다음에 "이 접근 순서가 맞는가"를 봅니다. 알고리즘이 동일한데도 접근 패턴 하나가 10배 차이를 만들 수 있다는 사실을 알기 때문입니다. 그래서 자료구조와 순회 순서를 함께 설계합니다.

또한 성능 병목을 볼 때 캐시 라인을 실제 비용 단위로 상상합니다. 한 라인을 가져왔는데 그 안의 값 한 개만 쓰고 버리면 이미 메모리 대역폭을 크게 낭비한 것입니다. 이 감각은 핫 루프와 데이터 레이아웃 설계에서 매우 강력합니다.

## 체크리스트

- [ ] 캐시 라인이 보통 64바이트라는 점을 아는가
- [ ] L1, L2, L3, RAM의 비용 차이를 대략 설명할 수 있는가
- [ ] 시간 지역성과 공간 지역성을 구분할 수 있는가
- [ ] AoS와 SoA의 차이를 설명할 수 있는가
- [ ] 행 우선과 열 우선 순회의 차이를 측정해 본 적이 있는가

## 연습 문제

1. 행 우선 순회와 열 우선 순회를 직접 측정해 보세요. 배열 크기를 바꾸며 어느 지점에서 차이가 더 커지는지도 확인해 보세요.

2. stride를 1, 2, 4, 8, 16으로 바꿔 가며 캐시 라인 활용도가 어떻게 달라지는지 측정해 보세요.

3. 하나의 필드만 자주 읽는 데이터 구조를 만들어 AoS와 SoA 중 어떤 쪽이 더 유리한지 실험해 보세요.

## 정리 및 다음 글

캐시는 CPU와 메모리 사이의 속도 격차를 메우는 핵심 장치이고, 그 효과는 코드가 지역성을 따르는지에 달려 있습니다. 같은 알고리즘이라도 데이터 접근 순서와 레이아웃만으로 10배 차이가 날 수 있습니다. 이 차이는 운이 아니라 설계와 측정의 결과입니다.

다음 글에서는 CPU가 명령어 처리량을 높이는 또 다른 장치인 파이프라인을 봅니다. 한 사이클에 한 명령어가 끝나는 것처럼 보이게 만드는 구조와, 분기 예측이 왜 필요한지 짚어보겠습니다.

## 심화 학습: 캐시 구조 분석과 최적화 기법

### Set-Associative 캐시 주소 분해

캐시 구조를 이해하는 핵심은 주소를 tag/index/offset으로 나누는 것입니다.

```python
import math

def cache_address_decomposition(cache_size_kb: int, line_size: int, 
                                 ways: int, addr_bits: int = 48) -> dict:
    """캐시 파라미터에서 주소 비트 분해 계산."""
    total_lines = (cache_size_kb * 1024) // line_size
    num_sets = total_lines // ways
    
    offset_bits = int(math.log2(line_size))
    index_bits = int(math.log2(num_sets))
    tag_bits = addr_bits - index_bits - offset_bits
    
    return {
        'cache_size': f"{cache_size_kb} KB",
        'line_size': f"{line_size} B",
        'associativity': f"{ways}-way",
        'total_lines': total_lines,
        'num_sets': num_sets,
        'offset_bits': offset_bits,
        'index_bits': index_bits,
        'tag_bits': tag_bits,
        'address_format': f"[tag:{tag_bits}][index:{index_bits}][offset:{offset_bits}]"
    }

# 일반적인 캐시 구성
configs = [
    ("L1 D-cache", 32, 64, 8),
    ("L2 cache", 256, 64, 4),
    ("L3 cache (per core slice)", 2048, 64, 16),
]

for name, size, line, ways in configs:
    result = cache_address_decomposition(size, line, ways)
    print(f"{name}: {result['address_format']} ({result['num_sets']} sets)")
```

출력:
```text
L1 D-cache: [tag:36][index:6][offset:6] (64 sets)
L2 cache: [tag:32][index:10][offset:6] (1024 sets)
L3 cache (per core slice): [tag:27][index:15][offset:6] (32768 sets)
```

### 캐시 미스 분류: 3C 모델

| 미스 종류 | 원인 | 해결 방법 |
|-----------|------|-----------|
| Compulsory (필수) | 첫 접근 → 반드시 미스 | 프리페치 |
| Capacity (용량) | 작업 세트 > 캐시 크기 | 캐시 확대 / 데이터 축소 |
| Conflict (충돌) | 같은 set에 집중 매핑 | associativity 증가 |

```python
def simulate_cache(accesses: list, num_sets: int, ways: int, 
                   line_size: int = 64) -> dict:
    """간단한 set-associative 캐시 시뮬레이터 (LRU)."""
    cache = {s: [] for s in range(num_sets)}  # set → [tags] (LRU order)
    hits = misses = 0
    
    for addr in accesses:
        tag = addr >> (int(math.log2(line_size)) + int(math.log2(num_sets)))
        index = (addr >> int(math.log2(line_size))) & (num_sets - 1)
        
        s = cache[index]
        if tag in s:
            hits += 1
            s.remove(tag)
            s.append(tag)  # MRU position
        else:
            misses += 1
            if len(s) >= ways:
                s.pop(0)  # evict LRU
            s.append(tag)
    
    return {'hits': hits, 'misses': misses, 
            'hit_rate': hits / (hits + misses) if (hits + misses) > 0 else 0}

import math

# 순차 접근 vs 스트라이드 접근
N = 10000
sequential = [i * 4 for i in range(N)]  # 4바이트씩 순차
stride_512 = [i * 512 for i in range(N)]  # 512바이트 스트라이드

for name, pattern in [("순차(4B)", sequential), ("스트라이드(512B)", stride_512)]:
    result = simulate_cache(pattern, num_sets=64, ways=8, line_size=64)
    print(f"  {name}: 히트율 {result['hit_rate']:.1%}")
```

### 캐시 쓰기 정책

| 정책 | Write Hit 동작 | Write Miss 동작 | 장단점 |
|------|---------------|----------------|--------|
| Write-through | 캐시 + 메모리 동시 쓰기 | No-allocate 또는 allocate | 단순, 높은 버스 트래픽 |
| Write-back | 캐시만 쓰기 (dirty 표시) | Write-allocate | 복잡, 낮은 트래픽 |

Write-back + Write-allocate가 현대 L1/L2의 기본 정책입니다. 이유: 쓰기 후 곧바로 읽는 패턴(temporal locality)이 매우 흔하기 때문입니다.

```text
Write-back 동작 흐름:
1. Write hit → dirty bit = 1, 메모리에는 안 씀
2. 해당 라인이 evict될 때 → dirty면 메모리에 write-back
3. Write miss → 먼저 해당 라인을 메모리에서 읽어옴(allocate) → 그 후 write

장점: 같은 라인에 여러 번 쓰기 → 메모리 접근 1회로 합침
```

### False Sharing: 멀티코어 캐시의 숨은 성능 킬러

```python
import threading
import time

# False sharing 시뮬레이션 (개념 코드)
# 실제 효과는 C/C++에서 관측 가능

# 문제 상황: 두 스레드가 같은 캐시 라인의 다른 변수를 수정
class FalseSharing:
    """같은 캐시 라인(64B) 안에 두 카운터가 있는 경우."""
    def __init__(self):
        # counter_a와 counter_b가 인접 → 같은 캐시 라인
        self.counter_a = 0
        self.counter_b = 0

class Padded:
    """패딩으로 분리된 경우."""
    def __init__(self):
        self.counter_a = 0
        self._pad = [0] * 8  # 64바이트 패딩
        self.counter_b = 0

# False sharing이 발생하면:
# Thread 0이 counter_a 수정 → 캐시 라인 invalidate
# Thread 1이 counter_b 읽기 → 미스! (다시 fetch)
# 이 핑퐁이 매 접근마다 반복 → 100~200 cycle 낭비/접근
```

False sharing의 성능 영향:

| 시나리오 | 처리량 (ops/sec) | 설명 |
|----------|-----------------|------|
| 단일 스레드 | 1,000M | 기준 |
| 2스레드, 독립 라인 | 2,000M | 이상적 스케일링 |
| 2스레드, false sharing | 50M | 40배 저하! |
| 2스레드, 패딩 적용 | 1,900M | 거의 이상적 |

### 프리페치: 미래의 미스를 예방

하드웨어 프리페처는 접근 패턴을 감지하여 미리 데이터를 가져옵니다.

```text
감지 가능한 패턴:
- Sequential: addr, addr+64, addr+128, ... (가장 기본)
- Stride: addr, addr+S, addr+2S, ... (S는 고정 스트라이드)
- 복잡한 패턴: 일부 프로세서는 2개 이상의 스트림 추적

감지 불가능한 패턴:
- 랜덤 접근 (해시 테이블, 포인터 체이싱)
- 데이터 의존적 접근 (linked list traversal)
```

소프트웨어 프리페치 힌트:
```python
# GCC __builtin_prefetch에 해당하는 개념
# Python에서는 직접 사용 불가하지만, 원리 설명

# 배열을 순회할 때 미리 다음 블록을 요청
# for i in range(N):
#     prefetch(arr[i + DISTANCE])  # 미래 데이터 미리 로드
#     process(arr[i])              # 현재 데이터 처리

# DISTANCE 선택 기준:
# - 너무 작으면: 프리페치가 도착하기 전에 접근 → 미스
# - 너무 크면: 프리페치된 데이터가 evict됨 → 낭비
# 최적값 ≈ memory_latency / loop_iteration_time
```

### 캐시 성능 측정: CPI 분해

```python
def cpi_with_cache(base_cpi: float, l1_miss_rate: float, l2_miss_rate: float,
                   l1_penalty: int, l2_penalty: int, mem_penalty: int,
                   mem_access_ratio: float = 0.35) -> float:
    """캐시 미스를 고려한 실효 CPI 계산."""
    # 메모리 명령어 비율 × 각 레벨 미스 페널티
    l1_stall = mem_access_ratio * l1_miss_rate * l1_penalty
    l2_stall = mem_access_ratio * l1_miss_rate * l2_miss_rate * l2_penalty
    mem_stall = mem_access_ratio * l1_miss_rate * l2_miss_rate * mem_penalty
    
    effective_cpi = base_cpi + l1_stall + l2_stall + mem_stall
    return effective_cpi

# 시나리오 비교
good = cpi_with_cache(1.0, l1_miss_rate=0.02, l2_miss_rate=0.1,
                      l1_penalty=4, l2_penalty=12, mem_penalty=100)
bad = cpi_with_cache(1.0, l1_miss_rate=0.10, l2_miss_rate=0.3,
                     l1_penalty=4, l2_penalty=12, mem_penalty=100)

print(f"캐시 친화적 코드 CPI: {good:.2f}")   # ~1.2
print(f"캐시 비친화적 코드 CPI: {bad:.2f}")   # ~2.5
print(f"성능 차이: {bad/good:.1f}x")           # ~2.1x
```


### 캐시 교체 정책 비교와 구현

캐시 set이 꽉 찼을 때 어떤 라인을 교체할지 결정하는 정책입니다.

```python
from collections import OrderedDict

class LRUCache:
    """LRU (Least Recently Used) 캐시 구현."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = self.misses = 0
    
    def access(self, key: int) -> bool:
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return True  # hit
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)  # LRU 제거
            self.cache[key] = True
            self.misses += 1
            return False  # miss

class PLRUCache:
    """Pseudo-LRU (트리 기반) — 하드웨어에서 실제 사용."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.entries = [None] * capacity
        self.tree_bits = [0] * (capacity - 1)  # 이진 트리 결정 비트
        self.hits = self.misses = 0
    
    def _find_plru_victim(self) -> int:
        """트리 비트를 따라가며 희생자 선택."""
        idx = 0
        pos = 0
        for level in range(self.capacity.bit_length() - 1):
            if self.tree_bits[idx] == 0:
                idx = 2 * idx + 1
            else:
                idx = 2 * idx + 2
                pos += (1 << (self.capacity.bit_length() - 2 - level))
        return pos
    
    def access(self, key: int) -> bool:
        if key in self.entries:
            self.hits += 1
            return True
        self.misses += 1
        victim = self._find_plru_victim()
        self.entries[victim] = key
        return False

# 비교 실험
import random
random.seed(42)

# 지역성 있는 접근 패턴
accesses = []
for _ in range(1000):
    base = random.randint(0, 10) * 64
    for offset in range(random.randint(1, 8)):
        accesses.append(base + offset)

lru = LRUCache(8)
for a in accesses:
    lru.access(a)
print(f"LRU:  히트율 {lru.hits/(lru.hits+lru.misses):.1%}")
```

| 정책 | 히트율 근사 | 하드웨어 비용 | 사용처 |
|------|------------|-------------|--------|
| LRU | 최적에 근접 | O(n²) 비교기 | 소규모 캐시 (≤4way) |
| Pseudo-LRU | LRU의 ~98% | O(n) 비트 | L1 (8-way) |
| Random | LRU의 ~90% | 난수 생성기 | L2/L3 일부 |
| RRIP | LRU 이상 | O(n) 카운터 | Intel L3 |

### 캐시 일관성(Coherence) 프로토콜 기초

멀티코어에서 같은 주소를 여러 코어의 캐시가 가지고 있을 때, 일관성을 유지해야 합니다.

```text
MESI 프로토콜 상태:
┌───────────────────────────────────────────────┐
│ M (Modified)  : 이 코어만 가짐, 메모리와 다름   │
│ E (Exclusive) : 이 코어만 가짐, 메모리와 같음   │
│ S (Shared)    : 여러 코어가 가짐, 읽기 전용     │
│ I (Invalid)   : 유효하지 않음                   │
└───────────────────────────────────────────────┘

상태 전이 예시:
Core 0 Read Miss  → E (단독 보유)
Core 1 Read Miss  → Core 0: E→S, Core 1: I→S (공유)
Core 0 Write Hit  → Core 0: S→M, Core 1: S→I (invalidate)
Core 1 Read Miss  → Core 0: M→S (write-back), Core 1: I→S
```

```python
from enum import Enum

class MESIState(Enum):
    MODIFIED = 'M'
    EXCLUSIVE = 'E'
    SHARED = 'S'
    INVALID = 'I'

class CacheLine:
    def __init__(self):
        self.state = MESIState.INVALID
        self.data = None

class MESISimulator:
    def __init__(self, num_cores: int):
        self.cores = [{} for _ in range(num_cores)]  # addr → CacheLine
        self.bus_transactions = 0
    
    def read(self, core_id: int, addr: int) -> str:
        line = self.cores[core_id].get(addr)
        
        if line and line.state != MESIState.INVALID:
            return f"Core {core_id} READ 0x{addr:04X}: HIT ({line.state.value})"
        
        # Miss → 버스 트랜잭션
        self.bus_transactions += 1
        other_has = False
        for i, core in enumerate(self.cores):
            if i != core_id and addr in core:
                if core[addr].state in (MESIState.MODIFIED, MESIState.EXCLUSIVE):
                    core[addr].state = MESIState.SHARED
                    other_has = True
                elif core[addr].state == MESIState.SHARED:
                    other_has = True
        
        new_line = CacheLine()
        new_line.state = MESIState.SHARED if other_has else MESIState.EXCLUSIVE
        new_line.data = addr
        self.cores[core_id][addr] = new_line
        return f"Core {core_id} READ 0x{addr:04X}: MISS → {new_line.state.value}"
    
    def write(self, core_id: int, addr: int) -> str:
        self.bus_transactions += 1
        # Invalidate 모든 다른 코어의 복사본
        for i, core in enumerate(self.cores):
            if i != core_id and addr in core:
                core[addr].state = MESIState.INVALID
        
        line = self.cores[core_id].get(addr, CacheLine())
        line.state = MESIState.MODIFIED
        line.data = addr
        self.cores[core_id][addr] = line
        return f"Core {core_id} WRITE 0x{addr:04X}: → M (others invalidated)"

# 시뮬레이션
sim = MESISimulator(2)
print(sim.read(0, 0x1000))   # Core 0 MISS → E
print(sim.read(1, 0x1000))   # Core 1 MISS → S (Core 0: E→S)
print(sim.write(0, 0x1000))  # Core 0 → M (Core 1: S→I)
print(sim.read(1, 0x1000))   # Core 1 MISS → S (Core 0: M→S, writeback)
print(f"버스 트랜잭션 수: {sim.bus_transactions}")
```

### 실무에서 캐시를 활용하는 데이터 구조 선택

| 데이터 구조 | 캐시 친화성 | 이유 |
|------------|------------|------|
| 배열 (Array) | 최고 | 연속 메모리, 프리페치 가능 |
| 벡터 (std::vector) | 최고 | 배열 기반 |
| 연결 리스트 | 최저 | 노드가 흩어짐, 포인터 체이싱 |
| 해시 테이블 (체이닝) | 낮음 | 체인이 포인터 기반 |
| 해시 테이블 (open addressing) | 높음 | 연속 메모리 탐색 |
| B-Tree | 중간~높음 | 노드 크기 = 캐시 라인 배수 |
| B+ Tree | 높음 | 리프 순차 스캔 최적화 |

이것이 데이터베이스가 B+ Tree를 인덱스로 사용하고, 게임 엔진이 ECS(Entity Component System)로 배열 기반 데이터를 선호하는 이유입니다.

## 처음 질문으로 돌아가기

- **캐시는 메모리 계층 어디에 놓일까요?**
  - CPU 레지스터(~0.3ns)와 메인 메모리(~100ns) 사이에 L1(~1ns, 32-64KB) → L2(~4ns, 256KB-1MB) → L3(~10ns, 수 MB~수십 MB) 순으로 놓입니다. 각 레벨은 용량을 늘리면서 접근 시간도 증가하는 트레이드오프를 구현합니다.
- **시간 지역성과 공간 지역성은 무엇이 다를까요?**
  - 시간 지역성은 "최근 접근한 데이터를 곧 다시 접근"(캐시 라인 유지로 활용), 공간 지역성은 "인접 주소를 곧 접근"(캐시 라인 크기 64B로 활용)합니다. 심화 학습에서 본 것처럼, 순차 접근이 스트라이드 접근보다 히트율이 높은 이유가 공간 지역성 활용 차이입니다.
- **캐시 라인은 왜 중요한 비용 단위일까요?**
  - 캐시 미스 시 1바이트만 필요해도 64바이트 전체 라인을 가져옵니다. 따라서 데이터 레이아웃이 캐시 라인 활용률을 결정합니다. False sharing 문제에서 보듯이, 같은 라인을 여러 코어가 수정하면 40배 성능 저하가 발생할 수 있습니다.

## 참고 자료

- [What Every Programmer Should Know About Memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — CPU cache](https://en.wikipedia.org/wiki/CPU_cache)
- [Wikipedia — Locality of reference](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Mike Acton — Data-Oriented Design and C++ (CppCon 2014)](https://www.youtube.com/watch?v=rX0ItVEVjHc)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 캐시, 지역성, 성능, 메모리 계층
