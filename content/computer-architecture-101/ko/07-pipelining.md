---
series: computer-architecture-101
episode: 7
title: 파이프라인
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
  - 파이프라인
  - 분기 예측
  - 성능
  - CPU
seo_description: CPU 파이프라인의 단계와 해저드, 분기 예측을 통해 한 사이클에 한 명령어가 완료되는 원리를 정리합니다.
last_reviewed: '2026-05-04'
---

# 파이프라인

> Computer Architecture 101 시리즈 (7/10)


## 이 글에서 다룰 문제

현대 CPU는 14단계 이상의 깊은 파이프라인을 갖고 있고, 이론적으로 한 사이클에 여러 명령어를 동시에 끝낼 수 있습니다(슈퍼스칼라). 그러나 분기 예측이 한 번 틀리면 파이프라인을 비우고 다시 채워야 하므로 10~20 사이클이 날아갑니다. 핫 루프의 분기를 줄이거나 예측 가능하게 만드는 것은 작지만 누적되면 큰 최적화입니다.

> 파이프라인은 평균을 빠르게 만들지만, 잘못된 예측 한 번이 그 평균을 깨뜨립니다.

## 전체 흐름
> 5단계 파이프라인(Fetch, Decode, Execute, Memory, Writeback)에서 한 사이클마다 다섯 명령어가 동시에 진행됩니다. 한 명령어 자체는 5 사이클이 걸리지만, 처리량은 사이클당 1 명령어가 됩니다. 분기가 발생하면 잘못 fetch된 명령어들을 모두 버리고 다시 시작해야 합니다.

```text
사이클:        1    2    3    4    5    6    7
명령어 1:      F    D    E    M    W
명령어 2:           F    D    E    M    W
명령어 3:                F    D    E    M    W
명령어 4:                     F    D    E    M
명령어 5:                          F    D    E
```

## Before / After

**Before — 분기가 많은 코드:**

```python
def count_positive(arr):
    count = 0
    for x in arr:
        if x > 0:           # 무작위 데이터면 예측 실패율 ~50%
            count += 1
    return count
```

**After — 분기를 산술로 대체:**

```python
def count_positive_branchless(arr):
    return sum((x > 0) for x in arr)   # bool→int, 분기 없음
```

산술 연산은 항상 같은 명령어 흐름을 갖기 때문에 파이프라인이 멈추지 않습니다. CPU 관점에서 가장 좋은 분기는 없는 분기, 그 다음이 예측 가능한 분기입니다.

## 단계별로 따라하기

### 1단계: 정렬된 vs 무작위 데이터의 분기 비용

```python
import time, random, numpy as np

N = 10_000_000
sorted_data = np.sort(np.random.randint(-100, 100, N))
random_data = np.random.randint(-100, 100, N)

def count_positive(arr):
    c = 0
    for x in arr:
        if x > 0:
            c += 1
    return c

start = time.perf_counter(); count_positive(sorted_data)
print(f"정렬:    {time.perf_counter() - start:.2f} s")

start = time.perf_counter(); count_positive(random_data)
print(f"무작위:  {time.perf_counter() - start:.2f} s")
```

같은 함수, 같은 크기. 정렬된 데이터는 분기 예측이 거의 모두 적중하지만, 무작위 데이터는 절반쯤 빗나가 파이프라인이 자주 비워집니다. C나 Rust에서는 차이가 더 극적입니다.

### 2단계: 파이프라인 시뮬레이터

```python
def pipeline(instructions, stages=("F", "D", "E", "M", "W")):
    """각 명령어가 단계별로 한 사이클씩 진행되는 파이프라인을 시뮬레이션"""
    n_inst = len(instructions)
    total_cycles = n_inst + len(stages) - 1
    grid = [[" " for _ in range(total_cycles)] for _ in range(n_inst)]
    for i in range(n_inst):
        for s, name in enumerate(stages):
            grid[i][i + s] = name
    return grid

for row in pipeline(["I1", "I2", "I3", "I4"]):
    print("".join(row))
```

출력은 명령어가 한 사이클씩 어긋나며 같은 단계에 머무는 구조를 보여 줍니다. 처리량은 사이클당 1 명령어이지만, 분기 한 번이 이 흐름을 깹니다.

### 3단계: 데이터 해저드 모델링

```python
class HazardCheck:
    """ADD R3, R1, R2 다음에 ADD R4, R3, R5가 오면 R3 결과를 기다려야 함"""
    @staticmethod
    def has_data_hazard(prev, curr):
        prev_dst = prev["dst"]
        curr_src = curr["src"]
        return prev_dst in curr_src

a = {"dst": "R3", "src": ("R1", "R2")}
b = {"dst": "R4", "src": ("R3", "R5")}   # R3 의존
c = {"dst": "R6", "src": ("R7", "R8")}

print(HazardCheck.has_data_hazard(a, b))   # True
print(HazardCheck.has_data_hazard(a, c))   # False
```

데이터 해저드는 forwarding(결과를 EX 단계에서 바로 전달)으로 보통 해소되지만, 메모리 로드 직후의 의존은 여전히 1 사이클 stall을 유발합니다.

### 4단계: 분기 예측 시뮬레이터

```python
class BranchPredictor:
    """간단한 2비트 saturating counter 예측기"""
    def __init__(self):
        self.state = 2   # 0:strong NT, 1:weak NT, 2:weak T, 3:strong T

    def predict(self):
        return self.state >= 2

    def update(self, taken):
        if taken and self.state < 3: self.state += 1
        if not taken and self.state > 0: self.state -= 1

bp = BranchPredictor()
sequence = [True, True, True, False, True, True, False, True]
hits = 0
for actual in sequence:
    pred = bp.predict()
    hits += (pred == actual)
    bp.update(actual)
print(f"적중률: {hits}/{len(sequence)}")
```

2비트 예측기는 단순하지만 거의 늘 같은 방향으로 가는 분기에 대해 95%+의 적중률을 보입니다. 무작위 분기에서는 50% 근처로 떨어집니다.

### 5단계: 분기 없는(branchless) 패턴

```python
def abs_with_branch(x):
    if x < 0:
        return -x
    return x

def abs_branchless(x):
    # 비트 연산으로 부호 비트 추출
    mask = x >> 31    # 음수면 -1(=...111), 양수면 0
    return (x ^ mask) - mask

print(abs_with_branch(-7), abs_branchless(-7))
print(abs_with_branch(5), abs_branchless(5))
```

같은 결과를 분기 없이 만들어 내는 패턴은 핫 루프의 예측 실패 비용을 0으로 만듭니다. 가독성과 트레이드오프가 있어, 측정으로 가치를 검증한 뒤에만 도입합니다.

## 이 코드에서 주목할 점

- 파이프라인은 단계가 깊을수록 처리량이 좋지만 분기 실패 비용도 큽니다
- 분기 예측은 패턴이 있는 분기에 매우 강하고, 무작위 분기에 약합니다
- 데이터 의존은 forwarding으로 대부분 해소되지만 메모리 로드는 stall이 남습니다
- 분기 없는 코드는 빠르지만 가독성을 희생합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 핫 루프에 무작위 분기 | 예측 실패 폭증 | 가능하면 산술/마스크로 |
| 데이터 정렬 무시 | 분기 패턴 불규칙 | 정렬 후 처리 검토 |
| 깊은 함수 호출 체인 | 분기·간접 호출 누적 | 인라인 또는 평탄화 |
| `if x` vs `if x > 0` 혼동 | 의도와 다른 비교 | 명시적 비교 사용 |
| 측정 없는 branchless 도입 | 가독성만 깎고 효과 없음 | 항상 before/after 측정 |

## 실무에서는 이렇게 쓰입니다

- 정렬 알고리즘: 분기 없는 비교(branchless compare)로 가속
- 그래픽스/SIMD: 마스크 기반 처리로 분기 제거
- JIT 컴파일러: 핫 트레이스에서 자주 가지 않는 분기를 가드로 처리
- 데이터베이스 옵티마이저: predicate를 일괄 처리해 분기 줄임
- 보안: 일정 시간(constant-time) 비교로 타이밍 공격 방지

## 체크리스트

- [ ] 파이프라인의 5단계를 그릴 수 있는가
- [ ] 데이터 해저드와 제어 해저드를 구분할 수 있는가
- [ ] 분기 예측의 적중률이 코드 패턴에 따라 다름을 안다
- [ ] 정렬된 데이터가 분기 예측에 유리한 이유를 설명할 수 있는가
- [ ] branchless 패턴의 장단점을 한 문단으로 말할 수 있는가

## 정리 및 다음 단계

파이프라인은 CPU의 처리량을 단계 수만큼 끌어올리는 핵심 장치이며, 분기 예측은 그 이득을 분기 위에서도 유지하기 위한 발명입니다. 핫 코드의 분기 패턴을 의식하는 것은 작지만 누적되면 큰 차이를 만듭니다. 다만 모든 최적화가 그렇듯 측정이 가설보다 먼저입니다.

다음 글에서는 CPU 바깥 세계, 즉 I/O와 장치를 살펴봅니다. 디스크, 네트워크, 키보드 같은 느린 장치들이 어떻게 빠른 CPU와 연결되는지를 다룹니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
- [레지스터와 ALU](./04-registers-and-alu.md)
- [메모리 구조](./05-memory-organization.md)
- [캐시와 지역성](./06-cache-and-locality.md)
- **파이프라인 (현재 글)**
- I/O와 장치 (예정)
- 병렬성과 멀티코어 (예정)
- 성능을 이해하는 법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Instruction pipelining](https://en.wikipedia.org/wiki/Instruction_pipelining)
- [Wikipedia — Branch predictor](https://en.wikipedia.org/wiki/Branch_predictor)
- [Stack Overflow — Why is processing a sorted array faster?](https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array)
- [Agner Fog — Software optimization resources](https://www.agner.org/optimize/)

Tags: Computer Science, 컴퓨터 구조, 파이프라인, 분기 예측, 성능, CPU
