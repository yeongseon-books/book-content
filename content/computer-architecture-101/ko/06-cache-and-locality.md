---
series: computer-architecture-101
episode: 6
title: 캐시와 지역성
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
  - 캐시
  - 지역성
  - 성능
  - 메모리 계층
seo_description: CPU 캐시의 동작 원리와 시간/공간 지역성, 캐시 친화적 코드 작성법을 정리합니다.
last_reviewed: '2026-05-04'
---

# 캐시와 지역성

> Computer Architecture 101 시리즈 (6/10)


## 이 글에서 다룰 문제

현대 CPU에서 가장 큰 성능 변수는 클럭 속도가 아니라 캐시 미스율입니다. 한 번의 메인 메모리 접근은 100~300 사이클을 잡아먹는 반면, L1 캐시 적중은 4 사이클이면 끝납니다. 같은 알고리즘이라도 메모리 접근 패턴 하나로 10배 이상의 차이가 납니다. 캐시를 의식하는 것은 가장 비용 대비 효과가 큰 최적화 기법입니다.

> 알고리즘이 같다면, 다음 질문은 "이 코드가 캐시 친화적인가?"입니다.

## 개념 한눈에 보기

> 캐시는 자주·최근에 접근한 데이터를 가까이 두는 작은 빠른 저장소입니다. CPU는 메인 메모리에서 한 바이트만 가져오지 않고, 보통 64바이트 단위(캐시 라인)로 가져와 캐시에 보관합니다. 같은 라인에 있는 다른 데이터는 다음 접근 시 거의 무료로 읽을 수 있습니다.

```text
   CPU
    │  (한 사이클)
    v
   L1 Cache  (32~64KB, ~4 cycles)
    │
    v
   L2 Cache  (256KB~1MB, ~12 cycles)
    │
    v
   L3 Cache  (수 MB, ~40 cycles)
    │
    v
   Main RAM  (수 GB, ~200 cycles)
    │
    v
   SSD/HDD  (수 TB, ~수만 cycles)
```

## Before / After

**Before — 캐시 적대적 코드:**

```python
# 2D 배열을 열 우선으로 순회 (Python list of lists)
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

같은 합을 구하지만 행 우선 순회는 같은 캐시 라인에 있는 인접 원소를 연속으로 읽으므로 훨씬 빠릅니다.

## 실습: 단계별로 따라하기

### 1단계: 행/열 우선 순회 시간 비교

```python
import time, numpy as np

N = 4096
m = np.random.randint(0, 100, (N, N), dtype=np.int32)

start = time.perf_counter()
total = 0
for i in range(N):
    for j in range(N):
        total += m[i, j]
print(f"행 우선:   {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
total = 0
for j in range(N):
    for i in range(N):
        total += m[i, j]
print(f"열 우선:   {time.perf_counter() - start:.2f} s")
```

같은 데이터, 같은 횟수, 다른 순서. 행 우선이 보통 5~10배 빠릅니다. 차이는 캐시 미스율에서 옵니다.

### 2단계: 캐시 라인 효과 직접 보기

```python
import time

CACHE_LINE = 64   # 보통 64바이트
INT_SIZE = 8       # numpy int64

stride_bytes = CACHE_LINE
stride_ints = stride_bytes // INT_SIZE   # 8

import numpy as np
N = 100_000_000
arr = np.zeros(N, dtype=np.int64)

start = time.perf_counter()
for i in range(0, N, 1):
    arr[i] += 1
print(f"stride 1 :  {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
for i in range(0, N, stride_ints):
    arr[i] += 1
print(f"stride 8 :  {time.perf_counter() - start:.2f} s")
```

stride 1은 한 캐시 라인 안의 8개 원소를 모두 사용하지만, stride 8은 라인마다 한 개만 씁니다. 메모리 대역폭이 한 자릿수 비율로 낭비됩니다.

### 3단계: 시간 지역성으로 결과 캐싱

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
print(f"캐시 없음: {time.perf_counter() - start:.3f} s")

start = time.perf_counter(); fib_cached(30)
print(f"캐시 사용: {time.perf_counter() - start:.6f} s")
```

같은 입력을 다시 묻는 패턴이 있다면, 결과 자체를 캐시하는 것이 시간 지역성을 가장 직접적으로 활용하는 방법입니다.

### 4단계: 자료구조 레이아웃의 영향 (AoS vs SoA)

```python
import numpy as np, time

N = 1_000_000

# Array of Structs: 각 객체에 모든 필드
class Particle:
    __slots__ = ("x", "y", "z", "vx", "vy", "vz")
    def __init__(self):
        self.x = self.y = self.z = 0.0
        self.vx = self.vy = self.vz = 0.0

aos = [Particle() for _ in range(N // 100)]   # 메모리 절약 위해 1/100

# Struct of Arrays: 각 필드가 별도 배열
soa_x = np.zeros(N); soa_y = np.zeros(N); soa_z = np.zeros(N)

start = time.perf_counter()
for p in aos:
    p.x += 1.0
print(f"AoS x++ : {time.perf_counter() - start:.4f} s")

start = time.perf_counter()
soa_x += 1.0
print(f"SoA x++ : {time.perf_counter() - start:.4f} s")
```

x만 업데이트할 때, SoA는 x만 모인 연속된 배열을 순회하므로 캐시 활용도가 훨씬 높습니다. 게임 엔진과 GPU 코드가 SoA를 선호하는 이유입니다.

### 5단계: 행렬 곱셈 블록화

```python
import numpy as np, time

N = 512
a = np.random.rand(N, N); b = np.random.rand(N, N)

start = time.perf_counter()
c = a @ b   # numpy(BLAS)는 내부적으로 캐시 블록화 사용
print(f"numpy matmul : {time.perf_counter() - start:.3f} s")

start = time.perf_counter()
c2 = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        for k in range(N):
            c2[i, j] += a[i, k] * b[k, j]
# 너무 느려서 작은 N으로만 의미 있음
```

numpy의 `@`는 BLAS 라이브러리를 호출하며, 내부에서 행렬을 캐시에 맞는 작은 블록으로 나눠 처리합니다. 같은 알고리즘이지만 캐시 인식 구현이 100배 이상 빠릅니다.

## 이 코드에서 주목할 점

- 같은 알고리즘, 같은 데이터라도 접근 순서가 성능을 결정합니다
- 캐시 라인은 한 번 가져온 64바이트 전체를 활용해야 효율적입니다
- 시간 지역성은 결과 캐싱으로, 공간 지역성은 인접 접근으로 살립니다
- 자료구조 레이아웃(AoS vs SoA)은 캐시 동작과 직결됩니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 열 우선 순회 | 캐시 미스 폭증 | 메모리 레이아웃에 맞춰 순회 |
| 작은 객체 다수 분산 | 포인터 추적 비용 | 연속 배열로 모음 |
| stride가 큰 접근 | 캐시 라인 낭비 | 인접 인덱스 우선 |
| 결과 재계산 | 시간 지역성 무시 | 메모이제이션, lru_cache |
| 큰 자료구조에 작은 핫 필드 | 캐시 라인 오염 | 핫 필드만 분리한 SoA |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스: 컬럼 스토어(컬럼별 분리 저장)로 분석 쿼리 가속
- 머신러닝: GPU 텐서를 메모리 연속(continguous)으로 유지
- 게임 엔진: ECS(Entity Component System)로 SoA 레이아웃 강제
- 컴파일러: 루프 변환(loop tiling, loop interchange)으로 자동 블록화
- 운영체제: 페이지 캐시로 디스크 I/O를 메모리 캐시로 흡수

## 체크리스트

- [ ] 캐시 라인 크기가 보통 64바이트임을 안다
- [ ] L1, L2, L3, RAM의 비용 차이를 한 자릿수 단위로 안다
- [ ] 시간 지역성과 공간 지역성을 구분할 수 있는가
- [ ] AoS와 SoA의 차이와 선택 기준을 안다
- [ ] 행 우선/열 우선 순회의 차이를 측정해 본 적이 있는가

## 정리 및 다음 단계

캐시는 CPU와 메모리 사이의 속도 격차를 메우는 가장 큰 장치이며, 그 효과는 우리 코드가 지역성을 따르는지에 달려 있습니다. 같은 알고리즘이라도 메모리 접근 패턴 하나로 10배의 차이가 나고, 그 차이는 측정할 수 있고 설계할 수 있는 차이입니다.

다음 글에서는 CPU가 명령어를 더 빠르게 처리하는 또 다른 장치, 파이프라인을 살펴봅니다. 한 사이클에 한 명령어를 끝내는 마법이 어떻게 가능하며, 분기 예측은 왜 등장했는지를 다룹니다.

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

- [What every programmer should know about memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — CPU cache](https://en.wikipedia.org/wiki/CPU_cache)
- [Wikipedia — Locality of reference](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Mike Acton — Data-Oriented Design and C++ (CppCon 2014)](https://www.youtube.com/watch?v=rX0ItVEVjHc)

Tags: Computer Science, 컴퓨터 구조, 캐시, 지역성, 성능, 메모리 계층
