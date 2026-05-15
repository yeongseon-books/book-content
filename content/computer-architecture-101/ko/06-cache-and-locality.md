---
series: computer-architecture-101
episode: 6
title: 캐시와 지역성
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

# 캐시와 지역성

같은 데이터를 같은 횟수만큼 읽는데도 한 코드는 1초, 다른 코드는 30초가 걸릴 수 있습니다. 이 글은 Computer Architecture 101 시리즈의 여섯 번째 글입니다. 여기서는 CPU와 메인 메모리 사이의 거대한 속도 차이를 메우는 캐시가 어떻게 동작하는지, 그리고 시간 지역성과 공간 지역성이 왜 성능을 바꾸는지 보겠습니다.

알고리즘이 이미 정해졌다면 그다음 질문은 종종 "이 코드는 캐시 친화적인가"입니다. 현대 CPU에서는 클럭 속도보다 캐시 미스율이 성능을 훨씬 더 크게 좌우하는 경우가 많기 때문입니다.

## 이 글에서 다룰 문제

- 캐시는 메모리 계층 어디에 놓일까요?
- 시간 지역성과 공간 지역성은 무엇이 다를까요?
- 캐시 라인은 왜 중요한 비용 단위일까요?
- 캐시 친화적 코드와 적대적 코드는 어떻게 다를까요?

> 캐시는 CPU 가까이에 자주 쓰는 데이터를 두는 작은 저장소이고, 지역성을 따르는 코드만 그 이득을 크게 얻습니다.

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

## Before / After

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

다음 글에서는 CPU가 명령어 처리량을 높이는 또 다른 장치인 파이프라인을 봅니다. 한 사이클에 한 명령어가 끝나는 것처럼 보이게 만드는 구조와, 분기 예측이 왜 필요한지 살펴보겠습니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
- [레지스터와 ALU](./04-registers-and-alu.md)
- [메모리 구조](./05-memory-organization.md)
- **캐시와 지역성 (현재 글)**
- 파이프라인 (예정)
- I/O와 장치 (예정)
- 병렬성과 멀티코어 (예정)
- 성능을 이해하는 법 (예정)
<!-- toc:end -->

## 참고 자료

- [What Every Programmer Should Know About Memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — CPU cache](https://en.wikipedia.org/wiki/CPU_cache)
- [Wikipedia — Locality of reference](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Mike Acton — Data-Oriented Design and C++ (CppCon 2014)](https://www.youtube.com/watch?v=rX0ItVEVjHc)

Tags: Computer Science, 컴퓨터 구조, 캐시, 지역성, 성능, 메모리 계층
