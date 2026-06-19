---
series: operating-systems-101
episode: 3
title: "Operating Systems 101 (3/10): 스케줄링"
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
  - 운영체제
  - 스케줄링
  - CPU
  - 시스템
  - 성능
seo_description: OS 스케줄러의 역할과 정책, 컨텍스트 스위치 비용, 조정 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (3/10): 스케줄링

한 머신 안에는 늘 여러 작업이 동시에 살아 있습니다. 그런데 CPU 코어 수는 한정되어 있으니, 결국 운영체제는 매 순간 누가 다음 차례를 가져갈지 정해야 합니다.

이 선택이 응답성, 처리량, 공정성, 전력 소비를 함께 흔듭니다. 그래서 스케줄링을 알면 단순한 CPU 사용률 그래프보다 훨씬 많은 것이 보입니다.

이 글은 Operating Systems 101 시리즈의 3번째 글입니다.

![Operating Systems 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/03/03-01-how-tasks-move-through-the-scheduler.ko.png)
*Operating Systems 101 3장 흐름 개요*

## 이 글에서 다룰 문제

- 스케줄러는 어떤 목표들 사이에서 균형을 잡을까요?
- 선점, 타임 슬라이스, 우선순위는 실제로 어떤 차이를 만들까요?
- 컨텍스트 스위치는 왜 보이지 않아도 비용이 클까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 기본 모델

> 스케줄러는 실행 가능한(runnable) 작업의 큐에서 다음에 실행할 작업을 골라 CPU에 올립니다. 작업이 I/O를 기다리거나, 시간 할당량을 다 쓰거나, 더 높은 우선순위의 작업이 깨어날 때 스케줄러가 다시 호출됩니다.

### 스케줄러가 고르는 다음 실행자

```text
Runnable queue        Running              Blocked (waiting I/O)
+--------------+      +----------+         +-------------------+
| T1, T3, T5   | ---> |   T2     |         |  T4 (read)        |
+--------------+      +----------+         |  T6 (sleep)       |
       ^                   |               +-------------------+
       |                   v
       +-- preempt /  time slice expires --+
                           |
                           +--> back to runnable queue
```

### 프로세스/스레드 상태 전이도

```text
NEW
 |
 v
READY (runnable) <---+------ RUNNING -----> TERMINATED
                     |           |
                     |   preempt / yield
                     |           |
                     +<---  I/O complete
                                 |
                                 v
                             BLOCKED (waiting for I/O, lock, sleep...)
```

리눅스 `ps` 출력의 `S`(sleeping), `R`(running), `D`(uninterruptible wait)는 이 상태들에 대응합니다.

## 같은 코드를 다르게 읽는 법

**이전 관점 — "운영체제가 알아서 골고루 돌리겠지":**

```bash
# Run four heavy background tasks at once
./heavy_task & ./heavy_task & ./heavy_task & ./heavy_task &
```

같은 시간에 끝날까? 한 작업이 다른 작업을 굶길까? 응답성에 어떤 영향이 갈까? 짐작만으로는 알 수 없습니다.

**바꿔서 보면 — "각 작업의 상태와 시간을 추적할 수 있다":**

```text
T1: ran 50ms -> time slice expired -> back to runnable
T2: blocked on I/O -> data arrived -> runnable again
T3: high priority -> preempts T2 the moment it wakes up
T4: nice +10 -> gets less of the shared CPU
```

스케줄러는 이런 작은 결정을 초당 수천 번 합니다.

## 단계별로 확인하기

### 1단계: 컨텍스트 스위치 횟수 측정

```bash
/usr/bin/time -v python3 -c "
import threading
def loop():
    for _ in range(10**6): pass
ts = [threading.Thread(target=loop) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
" 2>&1 | grep -E "context switches"
```

`Voluntary context switches`(자기가 양보)와 `Involuntary`(스케줄러가 빼앗음)를 구분해서 보여 줍니다. 자발/비자발 비율이 시스템의 부하를 짐작하게 합니다.

### 2단계: 나이스 값으로 우선순위 조정

```bash
# Default priority
nice -n 0  python3 -c "x=0
for _ in range(10**8): x+=1" &
# Lower priority
nice -n 19 python3 -c "x=0
for _ in range(10**8): x+=1" &
wait
```

`top`이나 `htop`에서 두 프로세스의 CPU 점유율을 비교해 보면, `nice 19` 쪽이 시스템이 한가할 때만 양보받아 늘어나는 모습을 볼 수 있습니다.

### 3단계: 프로세서 고정으로 특정 코어에 묶기

```bash
# Run only on CPU 0
taskset -c 0 python3 my_workload.py
# Inspect the affinity mask
taskset -p $(pgrep -f my_workload.py)
```

CPU 어피니티는 캐시 친화성을 높이거나, 특정 코어를 다른 작업으로부터 보호하는 데 사용됩니다.

### 4단계: 스레드별 상태 모니터링

```bash
# All threads of a PID, refreshed once per second
ps -L -p <PID> -o pid,tid,stat,wchan,comm
```

`stat`의 `R`은 실행/실행 가능, `S`는 대기, `D`는 디스크 I/O로 인터럽트 불가능 대기를 뜻합니다. 응답성이 이상할 때 스레드 상태 분포를 보면 단서가 잡힙니다.

### 5단계: 실시간 우선순위로 스케줄링 정책 바꾸기

```bash
# Inspect current policy
chrt -p $(pgrep -f my_workload.py)
# Switch to round-robin real-time (root required)
sudo chrt -r -p 50 $(pgrep -f my_workload.py)
```

리눅스는 일반(SCHED_OTHER, CFS) 외에도 SCHED_FIFO/SCHED_RR 같은 실시간 정책을 제공합니다. 잘못 쓰면 시스템 응답성이 크게 무너지므로, 실시간성이 정말 필요한 경우에만 사용합니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| CPU 사용률만 보기 | 컨텍스트 스위치/대기 시간 놓침 | `vmstat`, `pidstat`로 종합 관찰 |
| 스레드를 늘리면 항상 빠르다 가정 | 컨텍스트 스위치 폭주로 오히려 느려짐 | 코어 수 근방에서 멈춰보고 측정 |
| `nice -n -20`이 모든 걸 빠르게 해줄 거라 기대 | 다른 작업 굶기고 시스템 불안정 | 진짜 필요한 만큼만, 결과 측정 |
| 컨테이너 CPU 제한 무시 | cgroup throttling으로 응답성 폭락 | `cpu.cfs_quota_us` 등 한계 인지 |
| `D` 상태 프로세스를 그냥 죽이려 함 | `kill`이 안 듣고 좀비처럼 남음 | 디스크/네트워크 원인부터 해결 |

## 실무에서는 이렇게 본다

- 컨테이너 운영: 쿠버네티스의 CPU request/limit가 cgroup 스케줄러로 매핑
- 데이터베이스 튜닝: I/O 대기와 CPU 사용의 비율로 병목 진단
- 게임/오디오: 낮은 지연이 필요한 스레드를 실시간 우선순위로 운영
- 백그라운드 잡: ETL 워커를 `nice`로 낮춰 사용자 응답성 보호
- 노트북 전력 관리: 스케줄러가 코어 주파수와 협력해 절전과 성능 균형

## 운영 체크리스트

- [ ] 스케줄러의 네 가지 목표(응답성, 처리량, 공정성, 전력)를 말할 수 있는가
- [ ] 컨텍스트 스위치 비용의 대략적인 크기를 안다
- [ ] `nice`, 우선순위, 어피니티의 차이를 안다
- [ ] `R`/`S`/`D` 상태를 구분해서 해석할 수 있는가
- [ ] 컨테이너의 CPU 제한이 스케줄러로 어떻게 강제되는지 감이 있는가

## 시스템 관찰: 스케줄러 동작을 지표로 읽기

### run queue와 CPU 사용률을 함께 읽기

CPU 사용률이 낮다고 항상 여유가 있는 것은 아닙니다. run queue 길이(`r` 열)가 길고 I/O wait(`wa`)가 높으면 병목이 CPU가 아니라 디스크나 네트워크입니다.

```bash
vmstat 1
# r=runqueue, b=blocked, wa=iowait, cs=context switches
# 출력 예시:
# r  b   swpd   free   buff  cache  si  so    bi    bo    in   cs us sy id wa
# 2  0      0  1234M   234M  2048M   0   0     1     5   500 1200 25  5 68  2
```

컨텍스트 스위치(`cs`) 값이 갑자기 치솟으면, 스레드 수가 코어 수를 크게 초과해 스케줄러가 끊임없이 전환을 반복하는 상태입니다.

### 스케줄링 알고리즘을 간트 차트로 비교하기

같은 작업 집합에서 정책별로 대기시간이 얼마나 달라지는지 간트 차트로 보면 감각이 빠르게 잡힙니다.

작업 집합:
- P1: 도착 0, 실행 8
- P2: 도착 1, 실행 4
- P3: 도착 2, 실행 2

**FCFS (First Come, First Served)**

```text
시간: 0        8    12 14
      |---P1---|--P2--|-P3-|
```

대기시간: P1=0, P2=7, P3=10 → 평균 5.67

**SRTF (선점형 SJF, Shortest Remaining Time First)**

```text
시간: 0 1   3     7       14
      |P1|P2|P3|P2|------P1------|
```

대기시간: P1=6, P2=2, P3=1 → 평균 3.0

인터랙티브 시스템에서는 짧은 작업의 응답성을 높이는 SRTF/MLFQ 계열이 체감 품질을 크게 높일 수 있습니다.

**라운드 로빈 (q=2)**

```text
0  2  4  6  8  10 12 14
P1 P2 P3 P1 P2 P1 P1
```

퀀텀이 너무 작으면 컨텍스트 스위치 비용이 커지고, 너무 크면 FCFS에 가까워져 응답성이 나빠집니다.

### 컨텍스트 스위치 비용을 직접 측정하기

```python
import os, time

# getpid()는 간단한 syscall이지만 컨텍스트 전환 비용의 기준값이 됩니다
N = 1_000_000
t = time.perf_counter()
for _ in range(N):
    os.getpid()
elapsed = time.perf_counter() - t
print(f"syscall overhead: {elapsed/N*1e6:.2f} us/call")

# 파이프를 통한 컨텍스트 스위치 비용
r, w = os.pipe()
t = time.perf_counter()
for _ in range(10_000):
    os.write(w, b'x')
    os.read(r, 1)
elapsed = time.perf_counter() - t
print(f"pipe roundtrip: {elapsed/10_000*1e6:.1f} us/roundtrip")
os.close(r); os.close(w)
```

파이프 왕복 한 번이 수 마이크로초에서 수십 마이크로초 사이입니다. 이것이 컨텍스트 스위치의 하한 비용입니다.

### 스케줄링과 우선순위 튜닝 주의점

`nice`와 `ionice`는 빠른 응급처치지만, 남용하면 전체 시스템 공정성을 해칩니다.

운영 환경 권장 원칙:
1. 우선순위 조정은 임시 대응으로 제한합니다.
2. 조정 전후 지표(`vmstat`, `pidstat`)를 캡처해 회귀를 확인합니다.
3. 근본 원인은 워크로드 분리, 큐 제어, 배치 시간 분산으로 해결합니다.

### 리눅스 CFS 스케줄러의 실제 동작

```bash
# CFS 스케줄링 통계 확인
cat /proc/sched_debug | head -40

# 특정 프로세스의 스케줄링 통계
cat /proc/<PID>/sched | grep -E "nr_voluntary|nr_involuntary|se.sum_exec_runtime"
```

CFS(Completely Fair Scheduler)는 각 프로세스가 사용한 "가상 시간"을 추적해 가장 적게 쓴 프로세스를 다음에 실행합니다. `nice` 값은 이 가상 시간의 증가 속도를 바꿉니다.

## 처음 질문으로 돌아가기

- **스케줄러는 어떤 목표들 사이에서 균형을 잡을까요?**
  - 응답성(짧은 인터랙션 지연), 처리량(단위 시간당 완료 작업 수), 공정성(특정 프로세스가 굶지 않도록), 전력 효율(불필요한 CPU 웨이크업 최소화)이라는 네 가지 목표는 서로 충돌합니다. 스케줄러 정책은 이 균형점을 워크로드 특성에 맞게 선택합니다.
- **선점, 타임 슬라이스, 우선순위는 실제로 어떤 차이를 만들까요?**
  - 선점은 "더 급한 작업이 현재 실행 중인 작업을 밀어내는 능력"입니다. 타임 슬라이스는 한 번에 CPU를 쓸 수 있는 최대 시간이고, 짧을수록 응답성은 좋아지지만 컨텍스트 스위치 비용이 늘어납니다. 우선순위는 같은 runnable 큐 안에서 누가 먼저 선택받는지를 결정합니다.
- **컨텍스트 스위치는 왜 보이지 않아도 비용이 클까요?**
  - 스위치 자체는 수 마이크로초지만, 이전 프로세스가 CPU 캐시에 올려 놓은 데이터가 날아가 다음 프로세스가 캐시를 새로 채워야 합니다. 이 캐시 콜드 비용이 수백 마이크로초에 달해, 스위치 횟수가 많아지면 전체 처리량이 크게 떨어집니다.

## 연습 문제

1. `vmstat 1`을 10초 동안 실행하고 `cs` 열의 평균을 적어 보세요. 그 뒤 백그라운드에서 무거운 빌드를 돌린 뒤 같은 값을 다시 비교해 보세요.
2. 같은 파이썬 스크립트를 `nice -n 0`과 `nice -n 19`로 동시에 실행하고 `top`에서 CPU 점유율 차이가 언제 커지는지 관찰해 보세요.
3. CPU 바운드 스레드 8개짜리 예제를 `taskset -c 0`으로 묶었을 때와 그렇지 않을 때를 비교하고, 차이가 난 이유를 설명해 보세요.

## 마무리와 다음 글

스케줄러는 실행 가능한 작업 중에서 다음에 CPU를 줄 대상을 고르는 부품이고, 그 결정은 응답성·처리량·공정성·전력 사이의 트레이드오프입니다. 컨텍스트 스위치는 이 결정의 실현 비용이고, `nice`나 어피니티 같은 손잡이로 사용자도 일부 영향을 줄 수 있습니다.

다음 글에서는 여러 흐름이 같은 자원을 동시에 만질 때 발생하는 문제 — race condition을 봅니다. 스케줄러가 언제 흐름을 끊는지를 알면, 이 문제가 왜 그렇게 자주 생기는지가 자연스럽게 보입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- **Operating Systems 101 (3/10): 스케줄링 (현재 글)**
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): 메모리 관리](./06-memory-management.md)
- [Operating Systems 101 (7/10): 가상 메모리](./07-virtual-memory.md)
- [Operating Systems 101 (8/10): 파일 시스템](./08-file-systems.md)
- [Operating Systems 101 (9/10): 시스템 콜](./09-system-calls.md)
- [Operating Systems 101 (10/10): 컨테이너와 운영체제](./10-containers-and-the-os.md)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux Kernel Documentation — Scheduler](https://www.kernel.org/doc/html/latest/scheduler/index.html)
- [Brendan Gregg — Linux Performance](https://www.brendangregg.com/linuxperf.html)
- [LWN — The CFS scheduler](https://lwn.net/Articles/230501/)

Tags: Computer Science, 운영체제, 스케줄링, CPU, 시스템, 성능
