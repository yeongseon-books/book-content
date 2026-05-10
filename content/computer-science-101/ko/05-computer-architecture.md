---
series: computer-science-101
episode: 5
title: 컴퓨터 구조
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
  - CPU
  - 메모리
  - 캐시
  - 성능
seo_description: CPU, 메모리, 캐시가 어떻게 작동하고 코드 성능에 어떤 영향을 주는지 다루는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-04'
---

# 컴퓨터 구조

> Computer Science 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 Big-O를 가진 두 코드가 실제로는 10배씩 차이 나는 이유는 무엇일까요?

> 알고리즘이 같아도 하드웨어를 어떻게 사용하느냐에 따라 성능은 크게 달라집니다. CPU는 메모리에 직접 접근하지 않고 캐시를 거칩니다. 캐시 친화적인 코드는 캐시 미스가 가득한 코드보다 수십 배 빠릅니다. 이 글에서는 von Neumann 구조, CPU·메모리·캐시 계층, 그리고 그것이 코드 성능에 미치는 영향을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- von Neumann 구조의 핵심 구성 요소
- CPU의 명령어 처리 단계
- 메모리 계층(레지스터 → 캐시 → RAM → 디스크)
- 지역성(locality)과 캐시 친화적 코드

## 왜 중요한가

알고리즘만으로는 설명되지 않는 성능 차이가 항상 존재합니다. 같은 O(n) 코드가 두 배 빠른 이유, 행렬을 어떤 순서로 순회하느냐로 10배 차이가 나는 이유는 모두 메모리 계층 때문입니다.

> CPU는 빠르고, 메모리는 느립니다. 그 격차를 줄이는 것이 캐시입니다.

하드웨어를 모르고 짠 알고리즘은 종이 위에서만 빠릅니다.

## 개념 한눈에 보기

> 메모리 계층이 위로 갈수록 빠르고 비싸고 작으며, 아래로 갈수록 느리고 싸고 큽니다.

```text
계층            대략적 접근 시간    크기
────────────────────────────────────────
레지스터        < 1 ns             수십 바이트
L1 캐시         ~1 ns              32~64 KB
L2 캐시         ~4 ns              수백 KB
L3 캐시         ~10 ns             수십 MB
메인 메모리     ~100 ns            수십 GB
SSD             ~100 µs            수백 GB ~ TB
HDD             ~10 ms             TB
네트워크        ~수 ms ~ 수 s      —
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| CPU | 명령어를 해석하고 연산을 수행하는 장치 |
| 레지스터(register) | CPU 내부의 가장 빠른 저장소 |
| 캐시(cache) | CPU와 메모리 사이의 빠른 임시 저장소 (L1/L2/L3) |
| RAM | 프로그램이 실행될 때 사용되는 주 메모리 |
| 버스(bus) | CPU·메모리·장치 간 데이터 통로 |
| 클럭(clock) | CPU의 동작 속도 (Hz, 초당 사이클 수) |

## Before / After

**Before — 캐시 비친화적 코드:**

```python
# 2차원 리스트를 열 우선으로 순회 — 캐시 미스가 빈번
N = 2000
matrix = [[0] * N for _ in range(N)]

for j in range(N):           # 바깥 루프가 열
    for i in range(N):       # 안쪽 루프가 행
        matrix[i][j] += 1    # 매 접근마다 다른 행으로 점프
```

**After — 캐시 친화적 코드:**

```python
# 행 우선으로 순회 — 인접 메모리에 순차 접근
for i in range(N):           # 바깥 루프가 행
    for j in range(N):       # 안쪽 루프가 열
        matrix[i][j] += 1    # 같은 행 안에서 인접 메모리 접근
```

같은 O(n²)이지만 두 번째 코드는 캐시 라인을 효율적으로 사용해 더 빠릅니다.

## 실습: 단계별로 따라하기

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

### 2단계: NumPy로 메모리 레이아웃 확인

```python
import numpy as np

a = np.arange(12).reshape(3, 4)        # 기본은 C-order(행 우선)
print(a.flags["C_CONTIGUOUS"])         # True
print(a.flags["F_CONTIGUOUS"])         # False

b = np.asfortranarray(a)               # Fortran-order(열 우선)
print(b.flags["F_CONTIGUOUS"])         # True

# 같은 데이터, 다른 메모리 레이아웃 → 순회 속도가 달라집니다
```

### 3단계: 메모리 계층의 속도 차이 체감

```python
# 데이터 크기를 점점 늘리며 합 계산 — 캐시 단계가 보입니다
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
# CPU 클럭 3 GHz = 초당 30억 사이클
# 단순 덧셈 1회 = 약 1 사이클
# 메인 메모리 접근 = 약 300 사이클 (=L1의 100배)

# 의사 코드로 본 명령어 처리 단계 (Fetch-Decode-Execute)
def cpu_cycle(instruction: str) -> None:
    """1. Fetch  — 메모리에서 명령어를 읽습니다.
       2. Decode — 명령어를 해석합니다.
       3. Execute — ALU에서 연산을 수행합니다.
       4. Write back — 결과를 레지스터/메모리에 씁니다."""
    fetch = f"읽음: {instruction}"
    decode = "해석 중"
    execute = "연산 수행"
    write_back = "결과 저장"
    print(fetch, decode, execute, write_back, sep=" → ")


cpu_cycle("ADD R1, R2, R3")
```

### 5단계: 지역성을 활용한 데이터 패킹

```python
# 객체 리스트(흩어진 메모리) vs 필드별 배열(연속 메모리)
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

## 이 코드에서 주목할 점

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

시니어 엔지니어는 알고리즘 차수를 낮춘 다음, 메모리 접근 패턴을 의심합니다. 같은 O(n²) 알고리즘이라도 캐시 친화적이면 충분히 빠를 수 있고, O(n log n) 알고리즘도 메모리 접근이 흩어져 있으면 느릴 수 있다는 것을 압니다.

또한 모든 코드를 캐시 최적화 할 필요는 없다는 것도 압니다. 핫 패스(자주 실행되는 경로)만 프로파일러로 식별해 정밀하게 다듬고, 나머지는 가독성을 우선합니다. "프로파일러가 가리키는 곳을 고친다"가 원칙입니다.

## 체크리스트

- [ ] CPU·메모리·캐시의 속도 차이를 어림으로 말할 수 있는가
- [ ] 공간 지역성과 시간 지역성의 차이를 설명할 수 있는가
- [ ] 2차원 배열을 행 우선으로 순회해야 하는 이유를 아는가
- [ ] Python `list`가 진짜 배열이 아니라는 점을 이해했는가
- [ ] 디스크 I/O 비용이 메모리 대비 얼마나 큰지 감각이 있는가

## 연습 문제

1. 1000x1000 행렬을 행 우선과 열 우선으로 합산하고 시간을 비교하세요. 차이가 몇 배인지 측정합니다.

2. 정수 100만 개를 `list`, `array.array("i", ...)`, `numpy.ndarray`에 각각 담고 합계 계산 시간을 비교하세요.

3. 같은 데이터에 대해 (a) `for` 루프, (b) 리스트 컴프리헨션, (c) NumPy 벡터화로 제곱합을 계산하고 속도 차이를 분석하세요.

## 정리 및 다음 단계

CPU는 빠르고 메모리는 느립니다. 캐시는 그 격차를 메우는 계층이며, 캐시를 잘 쓰는 코드는 같은 알고리즘으로도 수십 배 빠릅니다. 좋은 엔지니어는 알고리즘 차수를 낮춘 뒤 메모리 접근 패턴까지 확인합니다.

다음 글에서는 이 하드웨어 위에서 여러 프로그램이 어떻게 공존하고 자원을 나눠 쓰는지 — 운영체제 — 를 다룹니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- **컴퓨터 구조 (현재 글)**
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [Computer Organization and Design (Patterson & Hennessy)](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [Ulrich Drepper — What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Agner Fog — Optimization Manuals](https://www.agner.org/optimize/)

Tags: Computer Science, 컴퓨터 구조, CPU, 메모리, 캐시, 성능
