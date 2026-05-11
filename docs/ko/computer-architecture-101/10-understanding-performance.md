---
series: computer-architecture-101
episode: 10
title: 성능을 이해하는 법
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
  - 성능
  - 프로파일링
  - 최적화
  - 측정
seo_description: 성능 분석을 위한 사고 모델, 처리량과 지연시간, 병목 식별, 그리고 측정의 원칙을 정리합니다.
last_reviewed: '2026-05-04'
---

# 성능을 이해하는 법

> Computer Architecture 101 시리즈 (10/10)


## 이 글에서 다룰 문제

성능은 모든 시스템의 기능입니다. 빠른 페이지가 더 많은 사용자를 잡고, 효율적인 배치가 더 적은 서버로 돌아가고, 짧은 지연이 더 좋은 사용자 경험을 만듭니다. 하지만 "최적화"라는 단어는 흔히 추측과 만나 잘못된 곳을 손대게 만듭니다. Knuth의 "premature optimization is the root of all evil"이 자주 인용되지만, 그 진의는 "측정 없이 최적화하지 마라"입니다.

> 측정하지 않은 최적화는 최적화가 아니라 신앙입니다.

## 전체 흐름
> 성능에는 두 축이 있습니다. 지연시간(한 작업이 끝나는 데 걸리는 시간)과 처리량(단위 시간당 처리하는 작업 수). 이 둘은 자주 트레이드오프 관계입니다. 병목을 찾을 때는 USE 방법론으로 자원(CPU, 메모리, 디스크, 네트워크)의 활용률, 포화도, 에러율을 봅니다. 프로파일링은 통계적 샘플링과 정밀 instrumentation 두 종류가 있고, 각각 장단점이 다릅니다.

```text
   지연시간(latency)              처리량(throughput)
   ──────────────────             ──────────────────
   요청 1건이 끝나는 시간         단위 시간당 요청 수
   ms, us 단위                    req/s, MB/s 단위
   사용자 경험                     서버 비용

   ↓ 병목 찾기
   USE 방법론
   ┌──────────┬──────────┬──────────┐
   │ CPU      │ Memory   │ Disk/Net │
   │ Util %   │ Used %   │ Util %   │
   │ Sat: 큐  │ Sat: swap│ Sat: 큐  │
   │ Errors   │ OOM      │ I/O err  │
   └──────────┴──────────┴──────────┘
```

## Before / After

**Before — 추측에 기반한 최적화:**

```python
# "Python이 느릴 거야"라며 무작정 Cython으로 변환
# 실제 병목은 SQL N+1 쿼리였음
def slow_endpoint(user_ids):
    users = []
    for uid in user_ids:
        users.append(db.query("SELECT * FROM users WHERE id = ?", uid))
    return users
```

**After — 측정 후 진짜 병목 수정:**

```python
# 프로파일러가 SQL이 95% 시간을 쓴다고 알려줌
def fast_endpoint(user_ids):
    return db.query(
        "SELECT * FROM users WHERE id IN (?)",
        user_ids,
    )   # 한 번의 쿼리, 100배 빨라짐
```

같은 코드, 같은 결과지만 진짜 병목을 본 결과 100배 차이가 납니다. 측정 없는 최적화는 종종 엉뚱한 곳을 더 빠르게 만들고 정작 병목은 그대로 둡니다.

## 단계별로 따라하기

### 1단계: 지연시간과 처리량 측정

```python
import time

def task():
    return sum(i * i for i in range(10_000))

# 지연시간: 1건의 시간
start = time.time()
task()
print(f"latency: {(time.time()-start)*1000:.2f}ms")

# 처리량: 1초 동안 몇 건?
end = time.time() + 1.0
count = 0
while time.time() < end:
    task()
    count += 1
print(f"throughput: {count} req/s")
```

지연시간을 줄이는 최적화와 처리량을 늘리는 최적화는 종종 다릅니다. 어느 쪽이 중요한지 먼저 정해야 합니다.

### 2단계: p50/p95/p99 분포 보기

```python
import time, random

def variable_task():
    time.sleep(random.uniform(0.001, 0.020))   # 1~20ms

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

평균은 거짓말합니다. 실제 사용자가 느끼는 것은 p95, p99의 꼬리 지연입니다. 모든 SLA가 평균이 아닌 꼬리로 정의되는 이유입니다.

### 3단계: cProfile로 진짜 병목 찾기

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

추측 대신 프로파일러를 신뢰하세요. 처음 본 결과가 직관과 다를 때, 직관이 틀렸을 가능성이 높습니다.

### 4단계: USE 방법론 모방

```python
import psutil, time

def use_snapshot(label):
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    print(f"[{label}] CPU 사용률: {cpu:.1f}%   메모리 사용량: {mem:.1f}%")

use_snapshot("idle")
# 무거운 일을 시뮬레이션
data = [i * i for i in range(10_000_000)]
use_snapshot("after work")
```

실제 시스템에서는 vmstat, iostat, top 같은 도구로 같은 일을 합니다. 핵심은 "어느 자원이 한계에 닿았는가"를 먼저 보는 것입니다.

### 5단계: 단일 변수 통제 실험

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

한 번에 한 변수만 바꿔야 결과를 신뢰할 수 있습니다. 캐시 워밍, 가비지 컬렉션, JIT 같은 노이즈 요인도 제거해야 합니다. 그래서 보통 5~10회 반복 후 중앙값을 봅니다.

## 이 코드에서 주목할 점

- 지연시간과 처리량은 별개의 지표이고 각각 다른 최적화 전략이 필요합니다
- 평균 대신 꼬리 지연(p95, p99)을 보세요
- 프로파일러 결과는 직관보다 신뢰하세요
- USE 방법론으로 자원별 한계를 체계적으로 봅니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 측정 없이 최적화 | 엉뚱한 곳 손대고 시간 낭비 | 프로파일러 먼저 |
| 평균만 본다 | p99에서 사용자 이탈 발생 | 분포 전체 본다 |
| 한 번 측정으로 결론 | 노이즈, 캐시 효과 무시 | 반복 후 중앙값 |
| 여러 변수 동시 변경 | 어느 게 효과인지 모름 | 단일 변수 통제 |
| 성능 회귀 테스트 부재 | 다음 PR에서 다시 느려짐 | 벤치마크 자동화 |

## 실무에서는 이렇게 쓰입니다

- APM 도구: Datadog, New Relic이 USE 지표를 자동 수집
- 데이터베이스 튜닝: 쿼리 플랜과 캐시 적중률 함께 본다
- 게임 개발: 프레임 타임 분포로 끊김 식별
- 분산 시스템: 꼬리 지연이 전체 SLA의 결정 요인
- 컴파일러 최적화: 벤치마크 회귀 테스트로 성능 보장

## 체크리스트

- [ ] 지연시간과 처리량의 차이를 설명할 수 있는가
- [ ] 평균이 아닌 꼬리 지연을 보는 습관이 있는가
- [ ] cProfile, perf, py-spy 같은 도구를 사용해 봤는가
- [ ] USE 방법론으로 자원 병목을 식별할 수 있는가
- [ ] 단일 변수 통제 벤치마크를 작성할 수 있는가

## 정리 및 다음 단계

성능은 측정에서 시작합니다. 지연시간과 처리량을 구분하고, 꼬리 지연을 보고, USE로 병목을 찾고, 단일 변수 통제로 검증하세요. 이 시리즈에서 배운 모든 것 — 데이터 표현부터 멀티코어까지 — 이 결국 성능 진단의 도구입니다.

이것으로 Computer Architecture 101 시리즈를 마칩니다. 다음 시리즈에서는 이 위에 운영체제가 어떻게 추상화를 쌓는지를 다룹니다. 컴퓨터 구조를 알고 OS를 보면 모든 시스템 콜과 스케줄링 결정이 다르게 보입니다.

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
