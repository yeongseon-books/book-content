---
series: computer-architecture-101
episode: 10
title: 성능을 이해하는 법
status: publish-ready
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
  - 성능
  - 프로파일링
  - 최적화
  - 측정
seo_description: 지연시간과 처리량, USE, 프로파일링으로 성능을 설명하는 사고법을 정리합니다.
last_reviewed: '2026-05-12'
---

# 성능을 이해하는 법

"느리다"는 말은 너무 자주 나오지만, 무엇이 얼마나 느린지 말하지 않으면 아무것도 해결되지 않습니다. 이 글은 Computer Architecture 101 시리즈의 마지막 글입니다. 여기서는 CPU, 메모리, 캐시, I/O, 병렬성까지 앞선 모든 내용을 모아 성능을 어떻게 측정하고 설명할지 하나의 사고 도구로 정리하겠습니다.

성능 문제는 거의 항상 추측에서 시작됩니다. 하지만 시니어 엔지니어는 측정 없이 코드를 바꾸지 않습니다. 최적화는 신념이 아니라 증거 위에서만 성립하기 때문입니다.

## 이 글에서 다룰 문제

- 지연시간과 처리량은 어떻게 다를까요?
- USE 방법론은 병목을 어떻게 찾을까요?
- 샘플링 프로파일링과 계측은 무엇이 다를까요?
- 측정은 왜 한 번이 아니라 여러 번, 한 변수씩 해야 할까요?

> 측정하지 않은 최적화는 최적화가 아니라 추측이며, 병목을 바꾸지 못하면 체감 성능도 바뀌지 않습니다.

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

## Before / After

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

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
- [레지스터와 ALU](./04-registers-and-alu.md)
- [메모리 구조](./05-memory-organization.md)
- [캐시와 지역성](./06-cache-and-locality.md)
- [파이프라인](./07-pipelining.md)
- [I/O와 장치](./08-io-and-devices.md)
- [병렬성과 멀티코어](./09-parallelism-and-multicore.md)
- **성능을 이해하는 법 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Profiling (computer programming)](https://en.wikipedia.org/wiki/Profiling_(computer_programming))
- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [Donald Knuth — Structured Programming with go to Statements (1974)](https://dl.acm.org/doi/10.1145/356635.356640)

Tags: Computer Science, 컴퓨터 구조, 성능, 프로파일링, 최적화, 측정
