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

## 먼저 던지는 질문

- 같은 Big-O라도 실제 실행 시간이 크게 다른 이유는 무엇일까요?
- CPU, 레지스터, 캐시, RAM은 어떤 속도 차이와 역할 차이를 가질까요?
- 행 우선 순회와 열 우선 순회가 왜 캐시 성능을 갈라놓을까요?

## 큰 그림

![Computer Science 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/05/05-01-concept-at-a-glance.ko.png)

*Computer Science 101 5장 흐름 개요*

이 그림에서는 컴퓨터 구조를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 컴퓨터 구조의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## Before / After

**Before — 캐시 비친화적 코드:**

```python
# Walk a 2D list column-major — frequent cache misses
N = 2000
matrix = [[0] * N for _ in range(N)]

for j in range(N):           # outer loop is the column
    for i in range(N):       # inner loop is the row
        matrix[i][j] += 1    # jump to a different row on every access
```

**After — 캐시 친화적 코드:**

```python
# Walk row-major — sequential access in adjacent memory
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

# Same data, different memory layout -> different traversal speed
```

### 3단계: 메모리 계층의 속도 차이 체감

```python
# Sum data of growing size — the cache tiers become visible
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
# A 3 GHz clock = 3 billion cycles per second
# A simple add = ~1 cycle
# Main memory access = ~300 cycles (about 100x an L1 hit)

# Pseudocode of the instruction stages (Fetch-Decode-Execute)
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
# A list of objects (scattered memory) vs a per-field array (contiguous memory)
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

## 처음 질문으로 돌아가기

- **같은 Big-O라도 실제 실행 시간이 크게 다른 이유는 무엇일까요?**
  - 본문의 기준은 컴퓨터 구조를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **CPU, 레지스터, 캐시, RAM은 어떤 속도 차이와 역할 차이를 가질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **행 우선 순회와 열 우선 순회가 왜 캐시 성능을 갈라놓을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, 컴퓨터 구조, CPU, 메모리, 캐시, 성능
