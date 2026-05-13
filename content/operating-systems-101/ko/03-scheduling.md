---
series: operating-systems-101
episode: 3
title: 스케줄링
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
  - 운영체제
  - 스케줄링
  - CPU
  - 시스템
  - 성능
seo_description: OS 스케줄러의 역할과 정책, 컨텍스트 스위치 비용, 조정 방법을 정리합니다.
last_reviewed: '2026-05-12'
---

# 스케줄링

한 머신 안에는 늘 여러 작업이 동시에 살아 있습니다. 그런데 CPU 코어 수는 한정되어 있으니, 결국 운영체제는 매 순간 누가 다음 차례를 가져갈지 정해야 합니다.

이 선택이 응답성, 처리량, 공정성, 전력 소비를 함께 흔듭니다. 그래서 스케줄링을 알면 단순한 CPU 사용률 그래프보다 훨씬 많은 것이 보입니다.

이 글은 Operating Systems 101 시리즈의 3번째 글입니다.

## 이 글에서 다룰 문제

- 스케줄러는 어떤 목표들 사이에서 균형을 잡을까요?
- 선점, 타임 슬라이스, 우선순위는 실제로 어떤 차이를 만들까요?
- 컨텍스트 스위치는 왜 보이지 않아도 비용이 클까요?
- `nice`, 우선순위, CPU 어피니티는 언제 조정해야 할까요?

> 스케줄러는 단순히 CPU를 나눠 주는 타이머가 아닙니다. runnable 큐에서 다음 실행자를 고르는 모든 판단이 지연 시간, 처리량, 공정성, 배터리 사용량까지 함께 바꾸는 정책 엔진입니다.

## 기본 모델
> 스케줄러는 실행 가능한(runnable) 작업의 큐에서 다음에 실행할 작업을 골라 CPU에 올립니다. 작업이 I/O를 기다리거나, 시간 할당량을 다 쓰거나, 더 높은 우선순위의 작업이 깨어날 때 스케줄러가 다시 호출됩니다.

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

## 여기서 먼저 볼 점

- 컨텍스트 스위치는 거저 일어나는 것처럼 보여도 비용이 있습니다(보통 수 마이크로초)
- `nice`는 절대 우선순위가 아니라 힌트입니다
- I/O 대기 상태(`S`, `D`)와 실행 가능 상태(`R`)의 구분이 디버깅에 결정적입니다
- 실시간 정책은 강력하지만 시스템 전체의 응답성을 망칠 수 있습니다

## 자주 하는 실수 5가지

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

## 체크리스트

- [ ] 스케줄러의 네 가지 목표를 말할 수 있는가
- [ ] 컨텍스트 스위치 비용의 대략적인 크기를 안다
- [ ] `nice`, 우선순위, 어피니티의 차이를 안다
- [ ] `R`/`S`/`D` 상태를 구분해서 해석할 수 있는가
- [ ] 컨테이너의 CPU 제한이 스케줄러로 어떻게 강제되는지 감이 있는가

## 마무리와 다음 글

스케줄러는 실행 가능한 작업 중에서 다음에 CPU를 줄 대상을 고르는 부품이고, 그 결정은 응답성·처리량·공정성·전력 사이의 트레이드오프입니다. 컨텍스트 스위치는 이 결정의 실현 비용이고, `nice`나 어피니티 같은 손잡이로 사용자도 일부 영향을 줄 수 있습니다.

다음 글에서는 여러 흐름이 같은 자원을 동시에 만질 때 발생하는 문제 — race condition을 봅니다. 스케줄러가 언제 흐름을 끊는지를 알면, 이 문제가 왜 그렇게 자주 생기는지가 자연스럽게 보입니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- **스케줄링 (현재 글)**
- 동시성과 경쟁 상태 (예정)
- 락, 뮤텍스, 세마포어 (예정)
- 메모리 관리 (예정)
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux Kernel Documentation — Scheduler](https://www.kernel.org/doc/html/latest/scheduler/index.html)
- [Brendan Gregg — Linux Performance](https://www.brendangregg.com/linuxperf.html)
- [LWN — The CFS scheduler](https://lwn.net/Articles/230501/)

Tags: Computer Science, 운영체제, 스케줄링, CPU, 시스템, 성능
