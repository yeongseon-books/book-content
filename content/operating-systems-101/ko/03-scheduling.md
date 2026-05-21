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

## 먼저 던지는 질문

- 스케줄러는 어떤 목표들 사이에서 균형을 잡을까요?
- 선점, 타임 슬라이스, 우선순위는 실제로 어떤 차이를 만들까요?
- 컨텍스트 스위치는 왜 보이지 않아도 비용이 클까요?

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

## 연습 문제

1. `vmstat 1`을 10초 동안 실행하고 `cs` 열의 평균을 적어 보세요. 그 뒤 백그라운드에서 무거운 빌드를 돌린 뒤 같은 값을 다시 비교해 보세요.
2. 같은 파이썬 스크립트를 `nice -n 0`과 `nice -n 19`로 동시에 실행하고 `top`에서 CPU 점유율 차이가 언제 커지는지 관찰해 보세요.
3. CPU 바운드 스레드 8개짜리 예제를 `taskset -c 0`으로 묶었을 때와 그렇지 않을 때를 비교하고, 차이가 난 이유를 설명해 보세요.

## 마무리와 다음 글

스케줄러는 실행 가능한 작업 중에서 다음에 CPU를 줄 대상을 고르는 부품이고, 그 결정은 응답성·처리량·공정성·전력 사이의 트레이드오프입니다. 컨텍스트 스위치는 이 결정의 실현 비용이고, `nice`나 어피니티 같은 손잡이로 사용자도 일부 영향을 줄 수 있습니다.

다음 글에서는 여러 흐름이 같은 자원을 동시에 만질 때 발생하는 문제 — race condition을 봅니다. 스케줄러가 언제 흐름을 끊는지를 알면, 이 문제가 왜 그렇게 자주 생기는지가 자연스럽게 보입니다.

## 시스템 관찰 지표와 커널 동작의 연결

### run queue와 CPU 사용률을 함께 읽기
CPU 사용률이 낮다고 항상 여유가 있는 것은 아닙니다. run queue 길이가 길고 I/O wait가 높으면 병목이 디스크나 네트워크일 수 있습니다.

```bash
vmstat 1
mpstat -P ALL 1
iostat -xz 1
```

세 도구를 같이 보면 CPU 바운드인지 I/O 바운드인지 분리할 수 있습니다. 운영체제 관점에서 중요한 것은 단일 지표가 아니라 지표 간 관계입니다.

### 페이지 폴트와 메모리 압박 해석
메모리 문제는 OOM 직전에야 드러나는 경우가 많습니다. 아래 지표를 주기적으로 보면 이상 징후를 조기에 잡을 수 있습니다.

- major page fault 증가: 디스크에서 페이지를 자주 끌어오는 상태
- swap in/out 급증: 워킹셋이 물리 메모리를 초과한 상태
- reclaim 스레드 활동 증가: 커널이 메모리 회수에 과도한 시간을 쓰는 상태

애플리케이션이 GC를 쓰는 런타임이라면, 힙 크기 조정과 객체 생존 시간 최적화가 커널 메모리 압박을 완화하는 직접 수단이 됩니다.

### 시스템 콜 추적으로 성능 병목 찾기
`strace`는 느리지만 원인 파악에는 매우 강력합니다. 호출 빈도와 지연 구간을 보면 어떤 API 사용이 비효율적인지 확인할 수 있습니다.

```bash
strace -f -c -p <pid>
```

요약표에서 `read`, `write`, `futex`, `epoll_wait` 비중이 높게 나오면 각각 I/O, 락 경합, 이벤트 대기 구조를 의심할 수 있습니다. 이후 애플리케이션 코드에서 버퍼 크기, 락 범위, 이벤트 루프 타임아웃을 조정하는 식으로 대응합니다.

### 스케줄링과 우선순위 튜닝 주의점
`nice`와 `ionice`는 빠른 응급처치지만, 남용하면 전체 시스템 공정성을 해칠 수 있습니다. 특정 작업의 우선순위를 올리면 다른 서비스의 tail latency가 악화될 수 있기 때문입니다.

운영 환경에서는 다음 원칙을 권장합니다. 첫째, 우선순위 조정은 임시 대응으로 제한합니다. 둘째, 조정 전후 지표를 캡처해 회귀를 확인합니다. 셋째, 근본 원인은 워크로드 분리, 큐 제어, 배치 시간 분산으로 해결합니다. 운영체제 기능은 문제를 숨기는 도구가 아니라 구조를 개선하기 위한 관측/제어 도구입니다.

## 스케줄링 알고리즘을 간트 차트로 비교하기

같은 작업 집합에서 정책별로 대기시간이 얼마나 달라지는지 간트 차트로 보면 감각이 빠르게 잡힙니다.

작업 집합:
- P1: 도착 0, 실행 8
- P2: 도착 1, 실행 4
- P3: 도착 2, 실행 2

### FCFS

```text
시간: 0        8    12 14
      |---P1---|--P2--|-P3-|
```

대기시간:
- P1 = 0
- P2 = 8 - 1 = 7
- P3 = 12 - 2 = 10
- 평균 = 5.67

### SRTF(선점형 SJF)

```text
시간: 0 1   3     7       14
      |P1|P2|P3|P2|------P1------|
```

대기시간:
- P1 = 14 - 0 - 8 = 6
- P2 = 7 - 1 - 4 = 2
- P3 = 5 - 2 - 2 = 1
- 평균 = 3.0

인터랙티브 시스템에서는 짧은 작업의 응답성을 높이는 SRTF/MLFQ 계열이 체감 품질을 크게 높일 수 있습니다.

### 라운드 로빈 타임퀀텀의 트레이드오프

```text
q=2일 때
0 2 4 6 8 10 12 14
P1 P2 P3 P1 P2 P1 P1
```

퀀텀이 너무 작으면 컨텍스트 스위치 비용이 커지고, 너무 크면 FCFS에 가까워져 응답성이 나빠집니다. 일반적으로 서비스 성격에 맞춰 2~10ms 범위를 실험하고 p95 지연시간으로 결정하는 것이 안전합니다.

## 처음 질문으로 돌아가기

- **스케줄러는 어떤 목표들 사이에서 균형을 잡을까요?**
  - 본문의 기준은 스케줄링를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **선점, 타임 슬라이스, 우선순위는 실제로 어떤 차이를 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컨텍스트 스위치는 왜 보이지 않아도 비용이 클까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
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

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux Kernel Documentation — Scheduler](https://www.kernel.org/doc/html/latest/scheduler/index.html)
- [Brendan Gregg — Linux Performance](https://www.brendangregg.com/linuxperf.html)
- [LWN — The CFS scheduler](https://lwn.net/Articles/230501/)

Tags: Computer Science, 운영체제, 스케줄링, CPU, 시스템, 성능
