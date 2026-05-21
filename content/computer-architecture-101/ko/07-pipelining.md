---
series: computer-architecture-101
episode: 7
title: "Computer Architecture 101 (7/10): 파이프라인"
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
  - 파이프라인
  - 분기 예측
  - 성능
  - CPU
seo_description: 파이프라인과 분기 예측이 CPU 처리량을 어떻게 끌어올리는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (7/10): 파이프라인

명령어 하나를 처리하는 데 다섯 단계가 필요하다면, 왜 CPU는 평균적으로 한 사이클에 한 명령어를 끝내는 것처럼 보일까요? 이 글은 Computer Architecture 101 시리즈의 일곱 번째 글입니다. 여기서는 파이프라인이라는 겹쳐 처리하기 기법과, 그 흐름을 자주 깨뜨리는 분기·의존성·메모리 지연을 보겠습니다.

파이프라인은 평균을 빠르게 만듭니다. 하지만 그 평균은 분기 예측 한 번이 틀리는 순간 무너질 수 있습니다. 그래서 핫 루프의 분기 패턴을 이해하는 습관이 생각보다 큰 성능 차이를 만듭니다.

## 먼저 던지는 질문

- 파이프라인은 어떻게 처리량을 높일까요?
- 데이터 해저드와 제어 해저드는 무엇이 다를까요?
- 분기 예측은 어떤 가정을 바탕으로 동작할까요?

## 큰 그림

![Computer Architecture 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/07/07-01-big-picture.ko.png)

*Computer Architecture 101 7장 흐름 개요*

## 왜 중요한가

현대 CPU는 깊은 파이프라인과 슈퍼스칼라 설계를 사용합니다. 그러나 분기 예측이 한 번 틀리면 이미 가져온 명령어를 버리고 다시 채워야 해서 10~20사이클 비용이 날 수 있습니다.

그래서 파이프라인 친화적인 코드, 예측 가능한 분기, 적절한 데이터 배치는 작은 차이처럼 보여도 누적되면 크게 작동합니다.

## 한눈에 보는 개념

5단계 파이프라인에서는 서로 다른 명령어가 동시에 Fetch, Decode, Execute, Memory, Writeback 단계를 점유합니다. 한 명령어는 끝까지 5사이클이 걸리지만, 처리량은 사이클당 1개에 가까워집니다.

```text
cycle:        1    2    3    4    5    6    7
instr 1:      F    D    E    M    W
instr 2:           F    D    E    M    W
instr 3:                F    D    E    M    W
instr 4:                     F    D    E    M
instr 5:                          F    D    E
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Pipeline | 명령어 단계를 겹쳐 처리하는 구조 |
| Hazard | 파이프라인을 멈추거나 깨뜨리는 조건 |
| Data hazard | 앞선 결과를 다음 명령어가 기다리는 상황 |
| Control hazard | 분기 때문에 다음 명령어를 확신할 수 없는 상황 |
| Branch prediction | 분기 방향을 미리 추측하는 기법 |
| Stall | 유효한 작업 없이 파이프라인이 쉬는 사이클 |

## 적용 전과 후

**Before — 분기가 많은 코드:**

```python
def count_positive(arr):
    count = 0
    for x in arr:
        if x > 0:           # ~50% mispredict on random data
            count += 1
    return count
```

**After — 분기를 산술로 대체:**

```python
def count_positive_branchless(arr):
    return sum((x > 0) for x in arr)   # bool->int, no branch
```

CPU 입장에서는 가장 좋은 분기는 없는 분기이고, 그다음은 예측하기 쉬운 분기입니다.

## 단계별로 따라가기

### 1단계: 정렬된 데이터와 무작위 데이터 비교

```python
import time, numpy as np

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
print(f"sorted:   {time.perf_counter() - start:.2f} s")

start = time.perf_counter(); count_positive(random_data)
print(f"random:   {time.perf_counter() - start:.2f} s")
```

같은 코드라도 정렬된 데이터는 예측기가 잘 맞히고, 무작위 데이터는 자주 틀립니다.

### 2단계: 파이프라인 시뮬레이터

```python
def pipeline(instructions, stages=("F", "D", "E", "M", "W")):
    """Each instruction advances one stage per cycle."""
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

출력은 명령어가 한 단계씩 어긋나며 동시에 흐르는 구조를 보여 줍니다.

### 3단계: 데이터 해저드 모델링

```python
class HazardCheck:
    """ADD R3, R1, R2 followed by ADD R4, R3, R5 must wait for R3."""
    @staticmethod
    def has_data_hazard(prev, curr):
        return prev["dst"] in curr["src"]

a = {"dst": "R3", "src": ("R1", "R2")}
b = {"dst": "R4", "src": ("R3", "R5")}   # depends on R3
c = {"dst": "R6", "src": ("R7", "R8")}

print(HazardCheck.has_data_hazard(a, b))   # True
print(HazardCheck.has_data_hazard(a, c))   # False
```

forwarding이 많은 의존성을 완화하지만, 메모리 로드 직후 의존은 여전히 stall을 만들 수 있습니다.

### 4단계: 분기 예측기 시뮬레이션

```python
class BranchPredictor:
    """Simple 2-bit saturating counter."""
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
print(f"hit rate: {hits}/{len(sequence)}")
```

단순한 2비트 예측기조차 패턴이 있는 분기에는 매우 강합니다.

### 5단계: branchless 패턴 보기

```python
def abs_with_branch(x):
    if x < 0:
        return -x
    return x

def abs_branchless(x):
    mask = x >> 31    # -1 if negative, 0 if positive
    return (x ^ mask) - mask

print(abs_with_branch(-7), abs_branchless(-7))
print(abs_with_branch(5), abs_branchless(5))
```

같은 결과를 분기 없이 만들면 예측 실패 비용은 사라지지만, 가독성은 나빠질 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 파이프라인이 깊을수록 처리량은 좋아지지만 예측 실패 비용도 커집니다.
- 분기 예측은 패턴이 있는 분기에 강하고 무작위 분기에 약합니다.
- forwarding이 많은 데이터 의존을 가려 주지만 load-use stall은 남습니다.
- branchless 코드는 빠를 수 있지만 항상 좋은 선택은 아닙니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 핫 루프에 무작위 분기 두기 | 예측 실패 폭증 | 산술/마스크 대체 검토 |
| 데이터 정렬 무시 | 분기 패턴이 불규칙해짐 | 미리 정렬하거나 묶기 |
| 깊은 호출과 간접 분기 남발 | 파이프라인 흐름 악화 | 평탄화나 인라인 검토 |
| `if x`와 `if x > 0` 혼동 | 의도와 다른 조건 | 명시적 비교 사용 |
| 측정 없이 branchless 도입 | 가독성만 손상 | 반드시 전후 측정 |

## 실무에서는 이렇게 드러납니다

- 정렬 알고리즘은 branchless compare를 활용합니다.
- 그래픽스와 SIMD 코드는 마스크 기반 처리로 분기를 줄입니다.
- JIT는 드문 분기를 deopt guard로 빼기도 합니다.
- 데이터베이스는 predicate를 배치 처리해 분기 비용을 줄입니다.
- 보안 코드는 일정 시간 비교로 타이밍 공격을 막습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 핫 루프를 볼 때 분기를 하나씩 셉니다. 거의 늘 같은 방향으로 가는 분기는 거의 공짜에 가깝지만, 랜덤한 분기는 10~20사이클씩 새어 나갈 수 있다는 것을 압니다. 그래서 데이터를 패턴 있게 정렬하거나, 때로는 산술 연산으로 바꾸는 선택을 합니다.

동시에 branchless가 만능이 아니라는 점도 압니다. 예측기가 잘 맞는 경우라면 오히려 일반 분기가 더 나을 수 있고, 컴파일러가 `cmov` 같은 형태로 자동 변환해 줄 수도 있습니다. 그래서 측정 없는 미세 최적화는 경계합니다.

## 체크리스트

- [ ] 파이프라인 5단계를 그릴 수 있는가
- [ ] 데이터 해저드와 제어 해저드를 구분할 수 있는가
- [ ] 분기 예측 적중률이 코드 패턴에 달린다는 점을 아는가
- [ ] 정렬된 데이터가 예측기에 유리한 이유를 설명할 수 있는가
- [ ] branchless의 장단점을 요약할 수 있는가

## 연습 문제

1. `count_positive`를 정렬 데이터와 무작위 데이터에 각각 실행해 차이를 측정해 보세요.

2. `BranchPredictor`에 50/50 분기와 80/20 분기를 넣어 적중률 차이를 확인해 보세요.

3. `abs`, `min`, `max`의 분기 버전과 branchless 버전을 만들어 각각 더 빠른 경우를 비교해 보세요.

## 정리 및 다음 글

파이프라인은 명령어 단계들을 겹쳐 CPU 처리량을 끌어올리는 핵심 장치입니다. 분기 예측은 그 이득을 분기 위에서도 유지하려는 장치이고, 의존성과 메모리 지연은 그 흐름을 자주 방해합니다. 결국 파이프라인 친화적 사고는 핫 코드의 분기와 데이터 흐름을 읽는 감각으로 이어집니다.

다음 글에서는 CPU 바깥의 느린 세계, 즉 I/O와 장치를 봅니다. 디스크, 네트워크, 키보드 같은 장치가 어떻게 CPU와 연결되고, 왜 비동기 모델이 필요한지 짚어보겠습니다.

## 심화 학습: 파이프라인 해저드와 성능 최적화

### 5단계 파이프라인 타이밍 상세 분석

```text
단일 사이클 vs 파이프라인 비교:

단일 사이클 (각 명령어 800ps):
I1: |████████████████████████████████████████| 800ps
I2:                                          |████████████████████████████████████████| 800ps
I3:                                                                                   |████████...
→ 3개 명령어 완료: 2400ps

5단계 파이프라인 (각 단계 200ps):
      IF    ID    EX   MEM   WB
I1: |████|████|████|████|████|
I2:      |████|████|████|████|████|
I3:           |████|████|████|████|████|
I4:                |████|████|████|████|████|
I5:                     |████|████|████|████|████|
→ 5개 명령어 완료: 1800ps (이상적)
→ 처리량: 1 명령어/200ps vs 1 명령어/800ps = 4배 향상
```

이상적 속도 향상 = 파이프라인 단계 수. 하지만 해저드 때문에 실제로는 이보다 낮습니다.

### 데이터 해저드: 포워딩으로 해결

```text
RAW (Read After Write) 해저드:
I1: ADD R1, R2, R3    ; R1에 쓰기 (WB에서 완료)
I2: SUB R4, R1, R5    ; R1 읽기 (ID에서 필요)

포워딩 없이 (2 cycle stall):
cycle:  1    2    3    4    5    6    7    8
I1:    IF   ID   EX   MEM  WB
I2:         IF   ID   --- | ---  EX   MEM  WB
                      ↑ stall (R1 아직 없음)

포워딩 적용 (EX→EX):
cycle:  1    2    3    4    5    6
I1:    IF   ID   EX   MEM  WB
I2:         IF   ID   EX   MEM  WB
                  ↑    ↑
                  │    └─ EX 결과를 직접 받음 (bypass)
                  ID에서 포워딩 가능 여부 확인
```

```python
def pipeline_cycles_with_forwarding(instructions: list) -> dict:
    """명령어 시퀀스의 파이프라인 실행 사이클 수 계산."""
    stalls = 0
    
    for i in range(1, len(instructions)):
        prev = instructions[i-1]
        curr = instructions[i]
        
        # Load-Use hazard: 포워딩으로도 1 stall 필요
        if prev.get('type') == 'LOAD' and prev.get('rd') in curr.get('src', []):
            stalls += 1
        # EX-EX forwarding: 0 stall (다른 RAW)
        # MEM-EX forwarding: 0 stall
    
    total = len(instructions) + 4 + stalls  # pipeline fill + stalls
    ipc = len(instructions) / (len(instructions) + stalls)
    return {'cycles': total, 'stalls': stalls, 'IPC': ipc}

# 예시 명령어 시퀀스
instrs = [
    {'type': 'LOAD', 'rd': 'R1', 'src': ['R2']},       # LW R1, 0(R2)
    {'type': 'ALU',  'rd': 'R3', 'src': ['R1', 'R4']}, # ADD R3, R1, R4 ← load-use!
    {'type': 'ALU',  'rd': 'R5', 'src': ['R3', 'R6']}, # SUB R5, R3, R6 (forwarding OK)
    {'type': 'STORE','rd': None, 'src': ['R5', 'R7']},  # SW R5, 0(R7) (forwarding OK)
]

result = pipeline_cycles_with_forwarding(instrs)
print(f"Stalls: {result['stalls']}, IPC: {result['IPC']:.2f}")
```

### 제어 해저드: 분기 예측

분기 명령어가 실행될 때까지 다음에 fetch할 주소를 모릅니다.

```text
분기 예측 실패 시 penalty:
cycle:  1    2    3    4    5    6    7
BEQ:   IF   ID   EX   MEM  WB
I(X):       IF   ID   ← 취소 (flush)
I(X+1):          IF   ← 취소 (flush)
Target:               IF   ID   EX   MEM  WB
→ 2 cycle 페널티 (5단계 파이프라인)
```

현대 프로세서는 더 깊은 파이프라인(14~20단계)을 가지므로 예측 실패 페널티가 훨씬 큽니다.

| 프로세서 | 파이프라인 깊이 | 예측 실패 페널티 |
|----------|---------------|----------------|
| MIPS R4000 | 8단계 | 3 cycles |
| Pentium 4 (Prescott) | 31단계 | ~20 cycles |
| Apple M1 (Firestorm) | ~13단계 | ~14 cycles |
| AMD Zen 4 | ~19단계 | ~13 cycles |

```python
def branch_prediction_impact(prediction_accuracy: float, 
                              branch_ratio: float,
                              penalty_cycles: int,
                              base_cpi: float = 1.0) -> float:
    """분기 예측이 CPI에 미치는 영향 계산."""
    miss_rate = 1 - prediction_accuracy
    branch_penalty = branch_ratio * miss_rate * penalty_cycles
    return base_cpi + branch_penalty

# 다양한 예측 정확도 시나리오
for acc in [0.80, 0.90, 0.95, 0.97, 0.99]:
    cpi = branch_prediction_impact(acc, branch_ratio=0.20, penalty_cycles=15)
    print(f"  예측 정확도 {acc:.0%}: CPI = {cpi:.2f}")
```

출력:
```text
  예측 정확도 80%: CPI = 1.60
  예측 정확도 90%: CPI = 1.30
  예측 정확도 95%: CPI = 1.15
  예측 정확도 97%: CPI = 1.09
  예측 정확도 99%: CPI = 1.03
```

### 분기 예측 알고리즘

```python
class TwoBitPredictor:
    """2-bit 포화 카운터 분기 예측기."""
    # 상태: 00(Strong NT) → 01(Weak NT) → 10(Weak T) → 11(Strong T)
    
    def __init__(self, num_entries: int = 1024):
        self.table = [0b10] * num_entries  # 초기: Weak Taken
        self.correct = self.incorrect = 0
    
    def predict(self, pc: int) -> bool:
        idx = pc % len(self.table)
        return self.table[idx] >= 2  # 2 이상이면 Taken 예측
    
    def update(self, pc: int, actually_taken: bool):
        idx = pc % len(self.table)
        predicted = self.table[idx] >= 2
        
        if actually_taken:
            self.table[idx] = min(3, self.table[idx] + 1)
        else:
            self.table[idx] = max(0, self.table[idx] - 1)
        
        if predicted == actually_taken:
            self.correct += 1
        else:
            self.incorrect += 1
    
    @property
    def accuracy(self) -> float:
        total = self.correct + self.incorrect
        return self.correct / total if total > 0 else 0

# 시뮬레이션: for 루프 패턴 (99번 taken, 1번 not-taken)
predictor = TwoBitPredictor(1024)
pc = 0x1000

for iteration in range(10):  # 10번 루프
    for i in range(100):
        taken = (i < 99)  # 마지막만 not-taken
        predictor.predict(pc)
        predictor.update(pc, taken)

print(f"2-bit 예측 정확도: {predictor.accuracy:.1%}")
# 기대값: ~98% (루프 시작과 끝에서만 실패)
```

### 슈퍼스칼라와 비순차 실행

현대 프로세서는 한 사이클에 여러 명령어를 발행(issue)합니다.

```text
4-wide 슈퍼스칼라 파이프라인:
         Fetch(4)   Decode(4)   Rename   Schedule   Execute   Commit
cycle 1: I1,I2,I3,I4
cycle 2: I5,I6,I7,I8  I1,I2,I3,I4
cycle 3: ...           I5,I6,I7,I8   I1,I2,I3,I4
...

실행 유닛 구성 (예: Apple M1 Firestorm):
- 정수 ALU × 4
- 정수 MUL × 1
- Branch × 2
- Load × 2
- Store × 1  
- FP/SIMD × 4
→ 이론상 피크 IPC: ~8
→ 실제 평균 IPC: 3~5 (의존성, 미스 등)
```

### 파이프라인 최적화: 컴파일러의 역할

컴파일러는 명령어 순서를 재배치(scheduling)하여 stall을 줄입니다.

```text
최적화 전 (load-use stall 발생):
    LW   R1, 0(R10)     ; load
    ADD  R2, R1, R3     ; R1 사용 → 1 stall
    LW   R4, 4(R10)     ; load
    ADD  R5, R4, R6     ; R4 사용 → 1 stall

최적화 후 (명령어 스케줄링):
    LW   R1, 0(R10)     ; load
    LW   R4, 4(R10)     ; load (R1 안 씀 → stall 없음)
    ADD  R2, R1, R3     ; R1 준비됨 (2 cycle 경과)
    ADD  R5, R4, R6     ; R4 준비됨 (2 cycle 경과)
→ stall 0개, 같은 결과
```

이것이 `-O2` 최적화가 성능을 크게 올리는 이유 중 하나입니다. 명령어의 의미는 같지만 순서가 달라져 파이프라인 활용률이 올라갑니다.


### 구조적 해저드: 자원 충돌

구조적 해저드는 두 명령어가 같은 하드웨어 자원을 동시에 필요로 할 때 발생합니다.

```text
예시: 단일 메모리 포트에서 IF와 MEM 단계 충돌

cycle:  1    2    3    4    5    6
I1:    IF   ID   EX   MEM  WB        ← MEM 단계에서 메모리 접근
I2:         IF   ID   EX   MEM  WB
I3:              IF   ID   EX   MEM  WB
I4:                   IF   ← 메모리 포트 충돌! (I1의 MEM과 동시)

해결: Harvard cache (I-cache / D-cache 분리)
→ IF는 I-cache, MEM은 D-cache → 충돌 없음
```

현대 프로세서에서 구조적 해저드가 드문 이유:
1. L1 캐시를 명령어/데이터로 분리 (Harvard)
2. 실행 유닛을 여러 개 배치 (ALU×4, FPU×4 등)
3. 레지스터 파일에 다중 읽기/쓰기 포트

### 파이프라인 깊이의 트레이드오프

```python
def optimal_pipeline_depth(logic_delay_ns: float, latch_overhead_ns: float,
                           branch_penalty_ratio: float = 0.05) -> dict:
    """파이프라인 깊이에 따른 성능 모델링."""
    results = []
    
    for stages in range(1, 51):
        # 클록 주기 = (로직 지연 / 단계 수) + 래치 오버헤드
        clock_period = (logic_delay_ns / stages) + latch_overhead_ns
        clock_freq_ghz = 1.0 / clock_period
        
        # 이상적 처리량에서 해저드 손실 차감
        # 분기 페널티 ∝ 파이프라인 깊이
        branch_loss = branch_penalty_ratio * stages
        effective_ipc = 1.0 - branch_loss
        
        throughput = effective_ipc * clock_freq_ghz  # GigaInstr/s
        results.append((stages, clock_freq_ghz, effective_ipc, throughput))
    
    # 최적 깊이 찾기
    best = max(results, key=lambda x: x[3])
    return {
        'optimal_stages': best[0],
        'clock_ghz': best[1],
        'ipc': best[2],
        'throughput_gips': best[3],
        'all_results': results
    }

# 현실적 파라미터
result = optimal_pipeline_depth(
    logic_delay_ns=5.0,    # 총 조합 로직 지연
    latch_overhead_ns=0.05, # 래치 당 오버헤드
    branch_penalty_ratio=0.01  # 분기 미스 비율 × 영향
)
print(f"최적 파이프라인 깊이: {result['optimal_stages']}단계")
print(f"클록 주파수: {result['clock_ghz']:.2f} GHz")
print(f"유효 IPC: {result['ipc']:.2f}")
print(f"처리량: {result['throughput_gips']:.2f} GIPS")
```

역사적 교훈 — Pentium 4의 실패:
- Willamette (2001): 20단계, 1.5GHz
- Prescott (2004): 31단계, 3.8GHz
- 클록은 높았지만 분기 페널티(~20 cycles)와 캐시 미스 페널티가 커서
- 더 낮은 클록의 Core 아키텍처(14단계, 2.6GHz)에 성능이 밀림

### 루프 언롤링과 파이프라인 효율

```text
원본 루프 (매 4 cycle마다 분기):
.loop:
    LW    R1, 0(R10)      ; load
    ADD   R2, R1, R3      ; use (1 stall)
    ADDI  R10, R10, 4     ; ptr++
    BNE   R10, R11, .loop ; 분기 (예측 실패 시 2 stall)
→ 4 명령어 / 루프, 분기 1회

2배 언롤링:
.loop:
    LW    R1, 0(R10)
    LW    R4, 4(R10)      ; 독립 load (stall 채움)
    ADD   R2, R1, R3
    ADD   R5, R4, R6      ; 독립 연산
    ADDI  R10, R10, 8
    BNE   R10, R11, .loop
→ 6 명령어 / 루프, 분기 1회 (분기 비율 50% 감소)
→ load-use stall도 자연스럽게 숨겨짐
```

| 언롤 배수 | 명령어/반복 | 분기 비율 | load-use stall | 코드 크기 |
|-----------|------------|-----------|----------------|-----------|
| 1배 (원본) | 4 | 25% | 1/반복 | 16B |
| 2배 | 6 | 17% | 0/반복 | 24B |
| 4배 | 10 | 10% | 0/반복 | 40B |
| 8배 | 18 | 6% | 0/반복 | 72B |

코드 크기가 커지면 I-cache 미스가 증가할 수 있으므로, 무조건 많이 언롤하는 것이 좋지는 않습니다. 컴파일러는 보통 루프 크기와 캐시 용량을 고려하여 최적 언롤 배수를 결정합니다.

### VLIW: 명시적 병렬 파이프라인

슈퍼스칼라(하드웨어가 병렬성 발견)의 대안으로 VLIW(컴파일러가 병렬성 명시)가 있습니다.

```text
VLIW 명령어 번들 (예: Itanium):
┌─────────────┬─────────────┬─────────────┐
│  Slot 0     │  Slot 1     │  Slot 2     │
│  ALU op     │  Memory op  │  Branch op  │
│  ADD R1,R2  │  LD R3,[R4] │  BNE R5,.L  │
└─────────────┴─────────────┴─────────────┘
128비트 번들: 3개 명령어를 동시 실행 보장 (NOP으로 채울 수도 있음)
```

| 특성 | 슈퍼스칼라 (x86, ARM) | VLIW (Itanium, DSP) |
|------|---------------------|---------------------|
| 병렬성 발견 | 하드웨어 (런타임) | 컴파일러 (컴파일 타임) |
| 하드웨어 복잡도 | 높음 (스케줄러) | 낮음 |
| 바이너리 호환성 | 세대 간 유지 | 세대 변경 시 재컴파일 |
| 코드 밀도 | 높음 | 낮음 (NOP 패딩) |
| 현재 상태 | 주류 | 니치 (DSP, GPU 일부) |

## 처음 질문으로 돌아가기

- **파이프라인은 어떻게 처리량을 높일까요?**
  - 명령어 실행을 여러 단계로 나누고 각 단계를 겹쳐 실행합니다. 5단계 파이프라인은 이상적으로 5배 처리량 향상을 주며, 한 사이클마다 1개 명령어가 완료됩니다. 슈퍼스칼라 구조는 여러 파이프라인을 병렬 배치하여 IPC > 1을 달성합니다.
- **데이터 해저드와 제어 해저드는 무엇이 다를까요?**
  - 데이터 해저드는 명령어 간 데이터 의존성(RAW: 이전 결과가 아직 안 나옴)으로 발생하며, 포워딩으로 대부분 해결됩니다. 제어 해저드는 분기 결과를 모르면 다음 fetch 주소를 결정할 수 없어 발생하며, 분기 예측으로 완화합니다.
- **분기 예측은 어떤 가정을 바탕으로 동작할까요?**
  - "과거 패턴이 미래에도 반복된다"는 가정입니다. 2-bit 포화 카운터는 연속 같은 방향 분기를 학습하고, 루프의 경우 99%+ 정확도를 달성합니다. 심화 학습에서 본 것처럼, 예측 정확도가 97%에서 99%로 오르면 CPI가 1.09에서 1.03으로 개선됩니다.

## 참고 자료

- [Wikipedia — Instruction pipelining](https://en.wikipedia.org/wiki/Instruction_pipelining)
- [Wikipedia — Branch predictor](https://en.wikipedia.org/wiki/Branch_predictor)
- [Stack Overflow — Why is processing a sorted array faster?](https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array)
- [Agner Fog — Software optimization resources](https://www.agner.org/optimize/)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 파이프라인, 분기 예측, 성능, CPU
