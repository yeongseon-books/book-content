---
series: computer-architecture-101
episode: 10
title: "Computer Architecture 101 (10/10): 성능을 이해하는 법"
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
  - 성능
  - 프로파일링
  - 최적화
  - 측정
seo_description: 지연시간과 처리량, USE, 프로파일링으로 성능을 설명하는 사고법을 정리합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (10/10): 성능을 이해하는 법

"느리다"는 말은 너무 자주 나오지만, 무엇이 얼마나 느린지 말하지 않으면 아무것도 해결되지 않습니다. 이 글은 Computer Architecture 101 시리즈의 마지막 글입니다. 여기서는 CPU, 메모리, 캐시, I/O, 병렬성까지 앞선 모든 내용을 모아 성능을 어떻게 측정하고 설명할지 하나의 사고 도구로 정리하겠습니다.

성능 문제는 거의 항상 추측에서 시작됩니다. 하지만 시니어 엔지니어는 측정 없이 코드를 바꾸지 않습니다. 최적화는 신념이 아니라 증거 위에서만 성립하기 때문입니다.


![Computer Architecture 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/10/10-01-big-picture.ko.png)
*Computer Architecture 101 10장 흐름 개요*

## 먼저 던지는 질문

- 지연시간과 처리량은 어떻게 다를까요?
- USE 방법론은 병목을 어떻게 찾을까요?
- 샘플링 프로파일링과 계측은 무엇이 다를까요?

## 왜 중요한가

성능은 모든 시스템의 기능입니다. 더 빠른 페이지는 더 많은 사용자를 붙잡고, 더 효율적인 배치는 더 적은 서버 비용으로 돌아가며, 더 낮은 지연은 더 좋은 사용자 경험을 만듭니다.

문제는 "최적화"라는 말이 종종 잘못된 직관과 결합한다는 점입니다. 진짜 병목이 SQL인데 Python을 의심하고, 진짜 병목이 I/O인데 CPU 튜닝부터 시작하는 식입니다. 그래서 측정이 먼저입니다.

## 한눈에 보는 개념

성능에는 지연시간과 처리량이라는 두 축이 있습니다. 병목을 찾을 때는 CPU, 메모리, 디스크, 네트워크 같은 자원의 Utilization, Saturation, Errors를 봅니다. 프로파일링은 대략적으로 자주 샘플링하는 방식과, 함수 경계에 직접 측정 코드를 넣는 방식으로 나뉩니다.

```text
   latency                       throughput
   --------------------          --------------------
   time per single request       requests per unit time
   ms, us                        req/s, MB/s
   user experience               server cost

   v find bottlenecks
   USE method
   +----------+----------+----------+
   | CPU      | Memory   | Disk/Net |
   | Util %   | Used %   | Util %   |
   | Sat: queue| Sat: swap| Sat: queue|
   | Errors   | OOM      | I/O err  |
   +----------+----------+----------+
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Latency | 한 작업이 끝날 때까지 걸리는 시간 |
| Throughput | 단위 시간당 완료한 작업 수 |
| p99 | 100개 중 가장 느린 1개에 가까운 꼬리 지연 |
| USE | Utilization / Saturation / Errors |
| Sampling profiler | 주기적으로 호출 스택을 수집하는 프로파일러 |
| Instrumentation | 함수 경계에 직접 측정 코드를 넣는 방식 |

## 적용 전과 후

**Before — 추측으로 최적화:**

```python
# "Python must be slow" so it gets ported to Cython
# The real bottleneck was an N+1 SQL query
def slow_endpoint(user_ids):
    users = []
    for uid in user_ids:
        users.append(db.query("SELECT * FROM users WHERE id = ?", uid))
    return users
```

**After — 측정 후 실제 병목 수정:**

```python
# Profiler shows SQL spending 95% of the time
def fast_endpoint(user_ids):
    return db.query(
        "SELECT * FROM users WHERE id IN (?)",
        user_ids,
    )   # one query, 100x faster
```

병목을 정확히 봤을 때만 최적화는 실제 체감으로 이어집니다.

## 단계별로 따라가기

### 1단계: 지연시간과 처리량 측정

```python
import time

def task():
    return sum(i * i for i in range(10_000))

# Latency: time per call
start = time.time()
task()
print(f"latency: {(time.time()-start)*1000:.2f}ms")

# Throughput: how many in 1 second
end = time.time() + 1.0
count = 0
while time.time() < end:
    task()
    count += 1
print(f"throughput: {count} req/s")
```

어떤 시스템은 지연시간이 중요하고, 어떤 시스템은 처리량이 더 중요합니다. 먼저 무엇을 개선할지 정해야 합니다.

### 2단계: p50/p95/p99 보기

```python
import time, random

def variable_task():
    time.sleep(random.uniform(0.001, 0.020))   # 1-20ms

samples = []
for _ in range(1000):
    start = time.time()
    variable_task()
    samples.append((time.time() - start) * 1000)

samples.sort()
def pct(p): return samples[int(len(samples) * p / 100)]
print(f"p50={pct(50):.2f}ms  p95={pct(95):.2f}ms  p99={pct(99):.2f}ms")
print(f"max={samples[-1]:.2f}ms")
```

평균은 자주 현실을 숨깁니다. 사용자는 꼬리 지연을 체감합니다.

### 3단계: `cProfile`로 병목 찾기

```python
import cProfile, pstats

def heavy():
    total = 0
    for i in range(100_000):
        total += sum(j for j in range(100))
    return total

profiler = cProfile.Profile()
profiler.enable()
heavy()
profiler.disable()

stats = pstats.Stats(profiler).sort_stats("cumulative")
stats.print_stats(10)
```

처음 보는 결과가 직관과 다를 때가 많습니다. 그럴수록 프로파일러를 더 신뢰해야 합니다.

### 4단계: USE 방식 흉내내기

```python
import psutil

def use_snapshot(label):
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    print(f"[{label}] CPU util: {cpu:.1f}%   Mem used: {mem:.1f}%")

use_snapshot("idle")
data = [i * i for i in range(10_000_000)]
use_snapshot("after work")
```

실제 운영에서는 `vmstat`, `iostat`, `top`, APM 도구가 같은 질문을 더 넓게 던집니다. 핵심은 어느 자원이 먼저 한계에 닿았는지 찾는 것입니다.

### 5단계: 단일 변수 통제 벤치마크

```python
import time

def benchmark(name, fn, runs=5):
    times = []
    for _ in range(runs):
        start = time.time()
        fn()
        times.append(time.time() - start)
    times.sort()
    print(f"{name:20s} median={times[len(times)//2]*1000:.2f}ms")

def loop_method():
    out = []
    for i in range(100_000):
        out.append(i * i)
    return out

def comprehension_method():
    return [i * i for i in range(100_000)]

benchmark("for-append", loop_method)
benchmark("comprehension", comprehension_method)
```

한 번에 한 변수만 바꿔야 무엇이 실제로 도움 됐는지 말할 수 있습니다. 여러 번 반복하고 중앙값을 보는 이유도 여기에 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 지연시간과 처리량은 별개이며 전략도 다를 수 있습니다.
- 평균보다 p95, p99 같은 꼬리 지연이 중요합니다.
- 직관보다 프로파일러를 믿어야 합니다.
- USE는 자원별 병목을 체계적으로 찾게 도와줍니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 측정 없이 최적화 | 엉뚱한 곳을 빠르게 만듦 | 먼저 프로파일링 |
| 평균만 보기 | 꼬리 지연을 놓침 | 분포 전체 확인 |
| 한 번 측정으로 결론 | 노이즈 무시 | 반복 후 중앙값 사용 |
| 여러 변수 동시에 변경 | 원인 분리 불가 | 한 번에 하나씩 바꾸기 |
| 회귀 벤치마크 없음 | 다음 변경에서 다시 느려짐 | 벤치마크 자동화 |

## 실무에서는 이렇게 드러납니다

- APM 도구는 USE 지표를 자동으로 수집합니다.
- 데이터베이스 튜닝은 쿼리 플랜과 캐시 적중률을 함께 봅니다.
- 게임 개발은 프레임 타임 분포로 끊김을 찾습니다.
- 분산 시스템은 평균보다 꼬리 지연이 SLA를 좌우합니다.
- 컴파일러와 런타임은 회귀 벤치마크로 성능을 지킵니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 먼저 "측정 데이터가 있는가"를 묻습니다. 데이터가 없으면 논의는 쉽게 이론 싸움이 되고, 끝없는 추측으로 흐르기 때문입니다. 작은 벤치마크 하나라도 들고 오는 팀이 좋은 팀인 이유가 여기에 있습니다.

또한 "어디가 느린가"보다 먼저 "왜 느린가"를 묻습니다. 같은 함수가 느려도 CPU 바운드인지, 메모리 바운드인지, I/O 바운드인지, 락 경합인지에 따라 처방이 완전히 달라집니다. 이 시리즈에서 다룬 모든 내용이 결국 그 진단 도구가 됩니다.

## 체크리스트

- [ ] 지연시간과 처리량 차이를 설명할 수 있는가
- [ ] 평균이 아니라 꼬리 지연을 봐야 하는 이유를 아는가
- [ ] `cProfile`, `perf`, `py-spy` 같은 도구를 써 본 적이 있는가
- [ ] USE로 자원 병목을 찾는 흐름을 설명할 수 있는가
- [ ] 단일 변수 통제 벤치마크를 작성할 수 있는가

## 연습 문제

1. 자주 쓰는 함수 하나를 `cProfile`로 분석하고, 가장 비싼 함수가 예상과 일치하는지 확인해 보세요.

2. 임의의 웹 API에 여러 요청을 보내 p50, p95, p99, max를 구해 평균과 얼마나 다른지 확인해 보세요.

3. 같은 알고리즘의 구현 두 개를 만들어 단일 변수 통제 벤치마크로 비교하고 중앙값을 기록해 보세요.

## 정리 및 다음 단계

성능은 측정에서 시작합니다. 지연시간과 처리량을 구분하고, 꼬리 지연을 보고, USE로 병목을 찾고, 단일 변수 통제로 검증해야 합니다. 그래야 최적화가 신앙이 아니라 설명 가능한 엔지니어링이 됩니다.

이것으로 Computer Architecture 101 시리즈를 마칩니다. 데이터 표현부터 멀티코어까지 살펴본 모든 주제는 결국 "왜 이 시스템은 이만큼 빠른가, 혹은 왜 이만큼 느린가"를 설명하는 도구였습니다.

## 심화 학습: 성능 분석 방법론과 벤치마크 해석

### 철의 법칙(Iron Law) 심화 적용

```python
def iron_law_analysis(instruction_count: int, cpi: float, 
                      clock_freq_ghz: float) -> dict:
    """프로세서 성능의 철의 법칙."""
    clock_period_ns = 1.0 / clock_freq_ghz
    execution_time_ns = instruction_count * cpi * clock_period_ns
    execution_time_s = execution_time_ns / 1e9
    ips = instruction_count / execution_time_s  # Instructions Per Second
    
    return {
        'execution_time_s': execution_time_s,
        'ips': ips,
        'mips': ips / 1e6,
        'ipc': 1.0 / cpi
    }

# 시나리오 비교: 같은 프로그램, 다른 아키텍처
scenarios = [
    ("CISC (x86)", 1_000_000_000, 1.2, 4.5),     # 적은 명령어, 높은 CPI, 높은 클록
    ("RISC (ARM)", 1_400_000_000, 0.8, 3.0),     # 많은 명령어, 낮은 CPI, 낮은 클록
    ("RISC (Apple M2)", 1_300_000_000, 0.7, 3.5), # 넓은 ILP + 높은 클록
]

print(f"{'아키텍처':<20} {'실행시간(s)':>10} {'IPC':>5} {'MIPS':>8}")
print("-" * 47)
for name, ic, cpi, freq in scenarios:
    r = iron_law_analysis(ic, cpi, freq)
    print(f"{name:<20} {r['execution_time_s']:>10.4f} {r['ipc']:>5.2f} {r['mips']:>8,.0f}")
```

### Roofline 모델: 연산 강도로 병목 진단

```python
def roofline_model(peak_flops_gflops: float, peak_bandwidth_gbs: float,
                   operational_intensity: float) -> dict:
    """Roofline 모델로 병목 유형 판단."""
    # Operational Intensity = FLOPs / Bytes transferred
    # 기울기 전환점 (ridge point)
    ridge_point = peak_flops_gflops / peak_bandwidth_gbs
    
    # 달성 가능 성능
    memory_bound_perf = operational_intensity * peak_bandwidth_gbs
    compute_bound_perf = peak_flops_gflops
    achievable = min(memory_bound_perf, compute_bound_perf)
    
    bottleneck = 'memory' if operational_intensity < ridge_point else 'compute'
    
    return {
        'ridge_point': ridge_point,
        'achievable_gflops': achievable,
        'bottleneck': bottleneck,
        'utilization': achievable / peak_flops_gflops
    }

# Intel Core i7 (예시 스펙)
peak_flops = 200  # GFLOPS (AVX2 포함)
peak_bw = 50      # GB/s (DDR4 dual-channel)

# 다양한 알고리즘의 연산 강도
algorithms = [
    ("벡터 덧셈 (STREAM)", 0.125),     # 1 FLOP / 8 bytes
    ("행렬-벡터 곱 (BLAS2)", 0.25),    # N FLOPs / 4N bytes  
    ("행렬 곱 (BLAS3)", 16.0),         # 2N³ FLOPs / 12N² bytes (N=1024 기준)
    ("합성곱 (CNN)", 10.0),            # 높은 재사용
    ("SpMV (희소 행렬)", 0.17),         # 대부분 메모리 바운드
]

print(f"Ridge Point: {peak_flops/peak_bw:.1f} FLOP/Byte")
print(f"{'알고리즘':<25} {'OI':>6} {'달성(GFLOPS)':>12} {'병목':>8} {'활용률':>7}")
print("-" * 63)
for name, oi in algorithms:
    r = roofline_model(peak_flops, peak_bw, oi)
    print(f"{name:<25} {oi:>6.2f} {r['achievable_gflops']:>12.1f} "
          f"{r['bottleneck']:>8} {r['utilization']:>7.0%}")
```

출력:
```text
Ridge Point: 4.0 FLOP/Byte
알고리즘                       OI   달성(GFLOPS)     병목     활용률
---------------------------------------------------------------
벡터 덧셈 (STREAM)           0.12          6.2   memory      3%
행렬-벡터 곱 (BLAS2)         0.25         12.5   memory      6%
행렬 곱 (BLAS3)             16.00        200.0  compute    100%
합성곱 (CNN)                10.00        200.0  compute    100%
SpMV (희소 행렬)             0.17          8.3   memory      4%
```

대부분의 실제 워크로드는 메모리 바운드입니다. CPU 성능이 아무리 올라도 데이터를 충분히 빠르게 공급하지 못하면 활용률이 3~6%에 머뭅니다.

### USE 방법론: 체계적 병목 진단

```python
def use_method_checklist():
    """USE (Utilization, Saturation, Errors) 방법론 체크리스트."""
    resources = {
        'CPU': {
            'utilization': 'mpstat, top, htop → %usr + %sys',
            'saturation': 'vmstat → run queue length, load average',
            'errors': 'dmesg → MCE (Machine Check Exception)',
        },
        'Memory': {
            'utilization': 'free -m → used/total 비율',
            'saturation': 'vmstat → si/so (swap in/out)',
            'errors': 'dmesg → ECC corrected/uncorrected',
        },
        'Storage': {
            'utilization': 'iostat → %util',
            'saturation': 'iostat → avgqu-sz (평균 큐 깊이)',
            'errors': 'smartctl → reallocated sectors',
        },
        'Network': {
            'utilization': 'sar -n DEV → rxkB/s, txkB/s vs 링크 속도',
            'saturation': 'netstat → Recv-Q, Send-Q (큐 백로그)',
            'errors': 'ip -s link → errors, dropped',
        },
    }
    
    for resource, metrics in resources.items():
        print(f"\n{resource}:")
        for metric_type, command in metrics.items():
            print(f"  {metric_type:>12}: {command}")

use_method_checklist()
```

### 샘플링 프로파일링 vs 계측(Instrumentation)

| 특성 | 샘플링 | 계측 |
|------|--------|------|
| 원리 | 주기적으로 PC 기록 | 모든 함수 진입/퇴출에 코드 삽입 |
| 오버헤드 | 1~5% | 10~100% |
| 정확도 | 통계적 (충분한 샘플 필요) | 정확 (모든 호출 기록) |
| 도구 | perf, py-spy, async-profiler | cProfile, gprof, Callgrind |
| 적합 환경 | 프로덕션, 상시 모니터링 | 개발, 정밀 분석 |

```python
import time
import random

# 샘플링 프로파일러 개념 구현
class SimpleSamplingProfiler:
    """간단한 샘플링 프로파일러 시뮬레이션."""
    def __init__(self):
        self.samples = {}  # function_name → count
        self.total_samples = 0
    
    def record_sample(self, function_name: str):
        self.samples[function_name] = self.samples.get(function_name, 0) + 1
        self.total_samples += 1
    
    def report(self) -> str:
        lines = [f"Total samples: {self.total_samples}"]
        sorted_funcs = sorted(self.samples.items(), key=lambda x: -x[1])
        for func, count in sorted_funcs[:10]:
            pct = count / self.total_samples * 100
            bar = '#' * int(pct / 2)
            lines.append(f"  {pct:5.1f}% {bar:<25} {func}")
        return '\n'.join(lines)

# 시뮬레이션: 가상의 프로그램 실행
profiler = SimpleSamplingProfiler()
# 가중치: compute_heavy가 60%, io_wait 25%, parse 10%, other 5%
weights = [('compute_heavy', 60), ('io_wait', 25), ('parse_data', 10), ('misc', 5)]
for _ in range(10000):
    r = random.randint(1, 100)
    cumulative = 0
    for func, weight in weights:
        cumulative += weight
        if r <= cumulative:
            profiler.record_sample(func)
            break

print(profiler.report())
```

### 벤치마크 함정: 숫자의 올바른 해석

```python
def benchmark_pitfalls():
    """흔한 벤치마크 해석 실수."""
    pitfalls = [
        {
            'mistake': '평균만 보고 결론',
            'example': '평균 응답 100ms → 99th percentile 2000ms일 수 있음',
            'fix': 'p50, p95, p99, p99.9 분위수를 함께 측정'
        },
        {
            'mistake': '웜업 없이 측정',
            'example': 'JIT 컴파일 전 측정 → 실제 성능의 1/10만 반영',
            'fix': '충분한 웜업 후 안정 상태에서 측정'
        },
        {
            'mistake': '마이크로벤치마크 일반화',
            'example': '1000번 반복 측정 → 캐시에 다 올라간 상태 (비현실적)',
            'fix': '실제 작업 크기와 접근 패턴 반영'
        },
        {
            'mistake': '다른 조건에서 비교',
            'example': 'A는 SSD, B는 HDD에서 실행 후 "A가 빠르다"',
            'fix': '하나의 변수만 변경하고 나머지 통제'
        },
        {
            'mistake': 'MIPS로 CPU 비교',
            'example': 'CISC 1000 MIPS vs RISC 2000 MIPS → CISC가 더 빠를 수 있음',
            'fix': '동일 워크로드의 실행 시간으로 비교'
        },
    ]
    
    for i, p in enumerate(pitfalls, 1):
        print(f"{i}. {p['mistake']}")
        print(f"   예: {p['example']}")
        print(f"   해법: {p['fix']}\n")

benchmark_pitfalls()
```

### 성능 카운터(PMU) 활용

현대 CPU는 하드웨어 성능 카운터를 내장하고 있습니다.

| 카운터 | 측정 대상 | 병목 진단 |
|--------|-----------|-----------|
| Instructions Retired | 완료된 명령어 수 | IPC 계산 기준 |
| CPU Cycles | 소비된 사이클 | CPI 계산 기준 |
| L1D Cache Misses | L1 데이터 캐시 미스 | 메모리 접근 패턴 |
| L3 Cache Misses | 마지막 캐시 미스 | DRAM 의존도 |
| Branch Mispredictions | 분기 예측 실패 | 제어 흐름 복잡도 |
| TLB Misses | TLB 미스 | 작업 세트 크기, huge page 필요성 |

```python
def diagnose_from_counters(instructions: int, cycles: int, 
                           l1_misses: int, l3_misses: int,
                           branch_mispred: int) -> list:
    """PMU 카운터에서 성능 병목 진단."""
    ipc = instructions / cycles
    l1_miss_rate = l1_misses / instructions
    l3_miss_rate = l3_misses / instructions
    branch_miss_rate = branch_mispred / instructions
    
    diagnosis = []
    
    if ipc < 1.0:
        diagnosis.append(f"낮은 IPC ({ipc:.2f}): 메모리 또는 분기 병목 가능")
    if l3_miss_rate > 0.01:
        diagnosis.append(f"높은 L3 미스율 ({l3_miss_rate:.3%}): DRAM 대역폭 병목")
    if branch_miss_rate > 0.02:
        diagnosis.append(f"높은 분기 미스율 ({branch_miss_rate:.3%}): 분기 예측 실패")
    if l1_miss_rate > 0.05:
        diagnosis.append(f"높은 L1 미스율 ({l1_miss_rate:.3%}): 데이터 지역성 개선 필요")
    if not diagnosis:
        diagnosis.append(f"양호 (IPC={ipc:.2f}): compute-bound로 추정")
    
    return diagnosis

# 예시 분석
results = diagnose_from_counters(
    instructions=10_000_000_000,
    cycles=15_000_000_000,
    l1_misses=200_000_000,
    l3_misses=50_000_000,
    branch_mispred=100_000_000
)
for d in results:
    print(f"  → {d}")
```


### Little의 법칙: 시스템 용량 계산

```python
def littles_law(arrival_rate: float, avg_latency: float) -> dict:
    """Little의 법칙: L = λ × W."""
    # L: 시스템 내 평균 항목 수 (동시 요청)
    # λ: 도착률 (requests/sec)
    # W: 평균 체류 시간 (latency)
    concurrent_requests = arrival_rate * avg_latency
    
    return {
        'arrival_rate': arrival_rate,
        'avg_latency_ms': avg_latency * 1000,
        'concurrent_requests': concurrent_requests
    }

# 웹 서버 용량 계획
scenarios = [
    ("현재 트래픽", 100, 0.050),     # 100 req/s, 50ms 응답
    ("2배 트래픽", 200, 0.050),     # 200 req/s, 50ms
    ("2배 + 지연 증가", 200, 0.200), # 200 req/s, 200ms (DB 느려짐)
    ("블랙프라이데이", 1000, 0.100),  # 1000 req/s, 100ms
]

print(f"{'시나리오':<20} {'요청률':>8} {'지연':>8} {'동시 요청':>10}")
print("-" * 50)
for name, rate, latency in scenarios:
    r = littles_law(rate, latency)
    print(f"{name:<20} {rate:>6}/s {r['avg_latency_ms']:>6.0f}ms {r['concurrent_requests']:>10.0f}")
```

이 법칙은 "서버가 동시에 처리해야 하는 요청 수"를 결정합니다. 스레드 풀 크기, 커넥션 풀 크기, 큐 용량을 설정할 때 필수적인 계산입니다.

### 지연 시간 분포와 꼬리 지연(Tail Latency)

```python
import random
import math

def simulate_tail_latency(num_requests: int = 100000, 
                           num_services: int = 1) -> dict:
    """꼬리 지연 시뮬레이션: 팬아웃이 클수록 악화."""
    # 개별 서비스 지연: 대부분 빠르지만 가끔 느림
    def single_request_latency() -> float:
        base = random.gauss(5.0, 1.0)  # 평균 5ms
        # 1% 확률로 GC pause 등 → 50~200ms
        if random.random() < 0.01:
            base += random.uniform(50, 200)
        return max(0.1, base)
    
    latencies = []
    for _ in range(num_requests):
        if num_services == 1:
            latencies.append(single_request_latency())
        else:
            # 팬아웃: 모든 서비스 중 가장 느린 것이 응답 시간
            service_latencies = [single_request_latency() for _ in range(num_services)]
            latencies.append(max(service_latencies))
    
    latencies.sort()
    return {
        'p50': latencies[int(0.50 * len(latencies))],
        'p95': latencies[int(0.95 * len(latencies))],
        'p99': latencies[int(0.99 * len(latencies))],
        'p999': latencies[int(0.999 * len(latencies))],
    }

print(f"{'팬아웃':>8} {'p50':>8} {'p95':>8} {'p99':>8} {'p99.9':>8}")
print("-" * 44)
for fan_out in [1, 5, 20, 50]:
    r = simulate_tail_latency(num_services=fan_out)
    print(f"{fan_out:>8} {r['p50']:>7.1f}ms {r['p95']:>7.1f}ms "
          f"{r['p99']:>7.1f}ms {r['p999']:>7.1f}ms")
```

팬아웃이 50인 마이크로서비스에서는 개별 서비스의 p99가 전체의 p50이 됩니다. 이것이 "꼬리가 개를 흔든다(tail at scale)" 문제입니다. Google의 Jeff Dean이 제안한 해법: hedged requests, tied requests, 적극적 타임아웃.

### 성능 회귀 감지 자동화

```python
import statistics

def detect_regression(baseline: list, current: list, 
                      threshold_pct: float = 5.0) -> dict:
    """성능 회귀 자동 감지."""
    baseline_mean = statistics.mean(baseline)
    baseline_stdev = statistics.stdev(baseline) if len(baseline) > 1 else 0
    current_mean = statistics.mean(current)
    
    change_pct = (current_mean - baseline_mean) / baseline_mean * 100
    
    # 통계적 유의성: 변화가 baseline 노이즈(2σ)보다 큰가?
    significant = abs(current_mean - baseline_mean) > 2 * baseline_stdev
    regression = change_pct > threshold_pct and significant
    
    return {
        'baseline_mean': baseline_mean,
        'current_mean': current_mean,
        'change_pct': change_pct,
        'significant': significant,
        'regression': regression,
        'verdict': 'REGRESSION' if regression else 'OK'
    }

# 예시: 응답 시간 (ms)
baseline_runs = [45.2, 44.8, 46.1, 45.5, 44.9, 45.3, 45.7, 44.6]
current_runs = [48.1, 49.2, 47.8, 48.5, 49.0, 48.3, 47.9, 48.7]

result = detect_regression(baseline_runs, current_runs)
print(f"Baseline: {result['baseline_mean']:.1f}ms")
print(f"Current:  {result['current_mean']:.1f}ms")
print(f"변화:     {result['change_pct']:+.1f}%")
print(f"판정:     {result['verdict']}")
```

이런 자동화된 성능 회귀 감지를 CI/CD 파이프라인에 통합하면, 코드 변경이 성능을 악화시키는 것을 배포 전에 잡을 수 있습니다.

## 처음 질문으로 돌아가기

- **지연시간과 처리량은 어떻게 다를까요?**
  - 지연시간(latency)은 한 작업이 시작부터 완료까지 걸리는 시간이고, 처리량(throughput)은 단위 시간당 완료되는 작업 수입니다. 파이프라인은 지연시간을 줄이지 않지만 처리량을 높입니다. Roofline 모델에서 보듯이, 동일 하드웨어에서도 연산 강도에 따라 달성 가능 처리량이 달라집니다.
- **USE 방법론은 병목을 어떻게 찾을까요?**
  - 모든 자원(CPU, 메모리, 스토리지, 네트워크)에 대해 Utilization(사용률), Saturation(포화도), Errors(에러)를 체계적으로 점검합니다. 심화 학습의 체크리스트처럼, 각 자원별로 구체적인 측정 명령어와 임계값이 정해져 있어 누락 없이 진단할 수 있습니다.
- **샘플링 프로파일링과 계측은 무엇이 다를까요?**
  - 샘플링은 주기적으로 실행 위치를 기록하여 "어디에서 시간을 많이 쓰는가"를 통계적으로 파악합니다(오버헤드 ~1-5%). 계측은 모든 함수 호출을 기록하여 정확한 호출 횟수와 시간을 알지만 오버헤드가 10~100%입니다. 프로덕션에는 샘플링, 정밀 분석에는 계측이 적합합니다.

## 참고 자료

- [Wikipedia — Profiling (computer programming)](https://en.wikipedia.org/wiki/Profiling_(computer_programming))
- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [Donald Knuth — Structured Programming with go to Statements (1974)](https://dl.acm.org/doi/10.1145/356635.356640)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 성능, 프로파일링, 최적화, 측정
