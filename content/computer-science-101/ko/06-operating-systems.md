---
series: computer-science-101
episode: 6
title: "Computer Science 101 (6/10): 운영체제"
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
  - 프로세스
  - 스레드
  - 가상 메모리
  - 동시성
seo_description: 운영체제가 프로세스, 스레드, 메모리, 시스템 콜을 어떻게 관리하는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (6/10): 운영체제

한 대의 컴퓨터에서 수십 개 프로그램이 동시에 도는 것처럼 보이는 순간, 우리는 이미 운영체제의 추상화 위에서 일하고 있습니다. 웹 서버가 멈추는 이유도, 메모리 누수가 보이는 방식도, 스레드가 기대만큼 빨라지지 않는 이유도 결국 OS 관점으로 돌아옵니다.

이 글은 Computer Science 101 시리즈의 6번째 글입니다.

여기서는 프로세스와 스레드, 가상 메모리, 시스템 콜, 동시성과 병렬성의 차이를 실전 감각으로 정리하겠습니다.


![Computer Science 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/06/06-01-concept-at-a-glance.ko.png)
*Computer Science 101 6장 흐름 개요*

## 먼저 던지는 질문

- 하나의 머신에서 많은 프로그램이 동시에 실행되는 것처럼 보이는 이유는 무엇일까요?
- 프로세스와 스레드는 메모리와 격리 측면에서 어떻게 다를까요?
- 가상 메모리는 왜 필요한 추상화일까요?

## 이 글에서 배울 것

- 프로세스와 스레드의 차이
- 가상 메모리와 주소 공간의 기본 개념
- 시스템 콜과 user/kernel mode 경계
- 동시성·병렬성·GIL의 실무적 의미

## 왜 중요한가

웹 서버가 멈추는 이유, 메모리 누수가 OS에 어떻게 보이는지, 멀티스레딩이 항상 빠르지 않은 이유는 모두 운영체제를 이해해야 답할 수 있습니다.

> 운영체제 = 자원 관리자 + 추상화 계층

OS의 추상화를 모르면 디버깅은 마법이 됩니다.

## 한눈에 보는 개념

> 프로세스는 격리된 실행 단위, 스레드는 같은 프로세스 안에서 메모리를 공유하는 실행 흐름입니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Process | 자기만의 메모리 공간을 가진 실행 단위 |
| Thread | 같은 프로세스 안에서 메모리를 공유하는 실행 흐름 |
| Context switch | OS가 CPU에서 실행할 프로세스나 스레드를 바꾸는 일 |
| Virtual memory | 각 프로세스에 독립적인 연속 주소 공간을 주는 추상화 |
| System call | 사용자 프로그램이 커널 서비스에 요청을 보내는 인터페이스 |
| Scheduler | 누가 CPU를 받을지 결정하는 OS 구성 요소 |

## 적용 전후 비교
**Before — OS를 의식하지 않은 코드:**

```python
# URL 100개를 순차 요청 — 대부분 대기 시간
import urllib.request

urls = [f"https://httpbin.org/delay/1?n={i}" for i in range(100)]
results = [urllib.request.urlopen(u).read() for u in urls]
# 약 100초 — CPU는 유휴 상태로 I/O만 대기
```

**After — OS의 비동기 I/O를 활용:**

```python
# 같은 작업을 동시 처리 — I/O 대기를 겹쳐서 수행
from concurrent.futures import ThreadPoolExecutor
import urllib.request

def fetch(url: str) -> bytes:
    return urllib.request.urlopen(url).read()

with ThreadPoolExecutor(max_workers=20) as pool:
    results = list(pool.map(fetch, urls))
# 약 5-10초 — 하나가 대기하는 동안 다른 요청 진행
```

## 단계별로 따라하기

### 1단계: 프로세스와 스레드 만들어 보기

```python
import os
import threading
import multiprocessing

def show_id(label: str) -> None:
    print(f"{label}: pid={os.getpid()}, tid={threading.get_ident()}")

print("[main]")
show_id("main")

print("\n[thread]")
t = threading.Thread(target=show_id, args=("thread",))
t.start()
t.join()

print("\n[process]")
p = multiprocessing.Process(target=show_id, args=("process",))
p.start()
p.join()
```

### 2단계: GIL과 멀티스레딩의 한계

```python
# CPU-bound 작업은 thread로 빨라지지 않음(CPython GIL)
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_heavy(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total

N = 10_000_000
work = [N] * 4

start = time.perf_counter()
[cpu_heavy(n) for n in work]
print(f"sequential : {time.perf_counter() - start:.2f}s")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_heavy, work))
print(f"threads x4 : {time.perf_counter() - start:.2f}s")  # roughly the same

start = time.perf_counter()
with ProcessPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_heavy, work))
print(f"processes x4: {time.perf_counter() - start:.2f}s")  # about 4x faster
```

**Expected output:** CPU 바운드 작업에서는 `threads x4`가 `sequential`과 비슷하고, `processes x4`가 더 빨라 GIL의 한계가 드러나야 합니다.

### 3단계: 시스템 콜 들여다보기

```python
# Python의 open()은 결국 OS의 open(2) system call 호출
import os

fd = os.open("/tmp/oscourse_demo.txt", os.O_CREAT | os.O_WRONLY, 0o644)
os.write(fd, b"Hello from a system call\n")
os.close(fd)

print(open("/tmp/oscourse_demo.txt").read())
os.remove("/tmp/oscourse_demo.txt")
```

### 4단계: 가상 메모리 관찰하기

```python
# 프로세스 메모리 사용량 확인(Linux/macOS)
import os
import resource

print(f"PID            : {os.getpid()}")
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"max RSS (KB)   : {usage.ru_maxrss}")    # peak resident set size
print(f"page faults    : {usage.ru_minflt}")    # page-fault count
```

### 5단계: 동시성 vs 병렬성

```python
# Concurrency = 여러 작업이 동시에 진행 중인 상태(time-sliced)
# Parallelism = 여러 작업이 같은 순간에 실행되는 상태(multi-core)

import asyncio
import time

async def task(name: str, sec: float) -> None:
    print(f"{name} starting")
    await asyncio.sleep(sec)        # simulate I/O wait
    print(f"{name} done")

async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(task("A", 1), task("B", 1), task("C", 1))
    print(f"total elapsed: {time.perf_counter() - start:.2f}s")  # about 1s

asyncio.run(main())
```

## 이 코드에서 먼저 봐야 할 점

- 프로세스는 메모리를 공유하지 않고, 스레드는 공유합니다
- CPython의 GIL 때문에 CPU 바운드 작업은 스레드보다 프로세스가 유리합니다
- I/O 바운드 작업은 스레드 또는 비동기로 충분히 빨라집니다
- 시스템 콜은 사용자 모드에서 커널 모드로 전환되며 비용이 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| CPU 바운드 작업에 스레드 사용 | GIL로 효과 없음 | `multiprocessing` 또는 `ProcessPoolExecutor` |
| 시스템 콜을 한 줄씩 호출 | 컨텍스트 스위치 오버헤드 | 버퍼링·일괄 처리 |
| 자식 프로세스를 `join` 없이 종료 | 좀비 프로세스, 자원 누수 | `with` 문 또는 명시적 `join`/`wait` |
| 스레드 간 공유 변수 무방어 | 경쟁 조건(race condition) | `threading.Lock`, 큐 기반 패턴 |
| 메모리 사용량을 RSS만 보고 판단 | 가상 메모리·공유 메모리 무시 | `pmap`, `smem` 등 도구로 분해 |

## 실무에서는 이렇게 쓰입니다

- 웹 서버에서 워커 프로세스 + 비동기 이벤트 루프 (Gunicorn + Uvicorn)
- 컨테이너(cgroup) 기반 자원 격리와 OOM Killer 동작 이해
- 데이터 파이프라인의 멀티프로세싱 vs 분산 처리 선택
- 디버깅 도구(`strace`, `dtruss`, `perf`)로 시스템 콜·스케줄링 분석
- 서비스 메모리 누수 분석에서 RSS, swap, page fault 추세 모니터링

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 병목이 CPU인지 I/O인지부터 묻습니다. CPU 바운드라면 알고리즘과 병렬성을, I/O 바운드라면 async·스레드·큐잉을 먼저 생각합니다.

또한 운영체제 추상화가 완전하지 않다는 사실을 압니다. 가상 메모리는 무한해 보이지만 실제 RAM과 swap에는 한계가 있고, 파일 시스템은 단순한 폴더 트리처럼 보여도 inode와 mount 경계가 있습니다. 운영 버그는 늘 그 가장자리에서 커집니다.


### 프로세스 상태 전이 다이어그램

운영체제에서 프로세스는 다섯 가지 주요 상태를 오갑니다.

```text
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌──────┐  fork  ┌──────┐  dispatch  ┌──────────┐        │
│ New  │ ─────→ │Ready │ ─────────→ │ Running  │        │
└──────┘        └──────┘            └──────────┘        │
                  ▲   ▲                │  │  │          │
                  │   │    preempt     │  │  │          │
                  │   └────────────────┘  │  │          │
                  │                       │  │  exit    │
                  │   I/O complete        │  │    ┌─────────┐
                  │                       │  └──→│Terminated│
                  │     ┌──────────┐      │      └─────────┘
                  └─────│ Blocked  │←─────┘
                        │(Waiting) │  I/O request
                        └──────────┘
```

| 상태 | 설명 | 전이 조건 |
|------|------|-----------|
| New | 프로세스 생성 중 | fork/exec 호출 |
| Ready | CPU 할당 대기 | 스케줄러 큐에 진입 |
| Running | CPU에서 실행 중 | dispatch(스케줄러 선택) |
| Blocked | I/O 또는 이벤트 대기 | read/recv/sleep 등 |
| Terminated | 실행 완료 또는 강제 종료 | exit/signal |

### CPU 스케줄링 알고리즘 비교

```python
from dataclasses import dataclass

@dataclass
class Process:
    name: str
    arrival: int    # 도착 시각
    burst: int      # CPU 버스트 시간
    remaining: int = 0

    def __post_init__(self):
        self.remaining = self.burst

def fcfs(processes: list[Process]) -> list[tuple[str, int, int]]:
    """First-Come First-Served 스케줄링"""
    timeline = []
    current_time = 0
    for p in sorted(processes, key=lambda x: x.arrival):
        start = max(current_time, p.arrival)
        end = start + p.burst
        timeline.append((p.name, start, end))
        current_time = end
    return timeline

def sjf(processes: list[Process]) -> list[tuple[str, int, int]]:
    """Shortest Job First (비선점)"""
    remaining = sorted(processes, key=lambda x: x.arrival)
    timeline = []
    current_time = 0
    done = []

    while remaining:
        available = [p for p in remaining if p.arrival <= current_time]
        if not available:
            current_time = remaining[0].arrival
            continue
        shortest = min(available, key=lambda x: x.burst)
        remaining.remove(shortest)
        start = current_time
        end = start + shortest.burst
        timeline.append((shortest.name, start, end))
        current_time = end
    return timeline

# 예시 프로세스
procs = [
    Process("P1", arrival=0, burst=6),
    Process("P2", arrival=1, burst=3),
    Process("P3", arrival=2, burst=1),
    Process("P4", arrival=3, burst=4),
]

print("FCFS 스케줄링:")
for name, start, end in fcfs(procs):
    print(f"  {name}: {start}-{end} (대기: {start - next(p.arrival for p in procs if p.name == name)})")

print("\nSJF 스케줄링:")
for name, start, end in sjf(procs):
    print(f"  {name}: {start}-{end}")
```

| 알고리즘 | 장점 | 단점 | 사용처 |
|----------|------|------|--------|
| FCFS | 구현 단순, 기아 없음 | 호위 효과(큰 작업이 뒤를 막음) | 배치 시스템 |
| SJF | 평균 대기 시간 최소 | 긴 작업 기아, 버스트 예측 필요 | 이론적 최적 |
| Round Robin | 응답 시간 균등 | 타임 퀀텀 선택이 성능 결정 | 범용 시분할 |
| Priority | 중요 작업 우선 | 낮은 우선순위 기아 | 실시간 시스템 |
| CFS (Linux) | 공정 CPU 분배 | 복잡한 구현 | Linux 커널 |

Linux의 CFS(Completely Fair Scheduler)는 레드-블랙 트리로 가상 실행 시간이 가장 적은 프로세스를 O(log n)에 선택합니다.

### 동기화 기본 요소와 교착 상태

멀티스레드 프로그램에서 공유 자원을 보호하는 기본 도구들입니다.

```python
import threading
import time

# 경쟁 조건 시연
counter = 0

def increment_unsafe():
    global counter
    for _ in range(100_000):
        counter += 1  # read-modify-write가 원자적이지 않음

threads = [threading.Thread(target=increment_unsafe) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"예상: 400,000 / 실제: {counter}")  # 대부분 400,000보다 작음

# Lock으로 해결
counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment_safe) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(f"예상: 400,000 / 실제: {counter}")  # 정확히 400,000
```

교착 상태(deadlock)는 네 가지 조건이 모두 성립할 때 발생합니다.

| 조건 | 설명 | 방지 전략 |
|------|------|-----------|
| 상호 배제 | 자원을 한 번에 하나만 사용 | 공유 가능한 자원으로 변경 |
| 점유 대기 | 자원을 갖고 다른 자원을 요청 | 모든 자원을 한 번에 요청 |
| 비선점 | 강제로 빼앗지 못함 | 타임아웃 후 반환 |
| 순환 대기 | 환형으로 서로를 기다림 | 자원에 순서를 부여 |

실무에서는 데이터베이스 트랜잭션 교착 상태가 흔합니다. PostgreSQL은 `deadlock_timeout`(기본 1초) 후 하나의 트랜잭션을 강제 롤백해 풀어줍니다.

### 파일 시스템 내부 구조

파일을 열고 쓸 때 OS 내부에서 벌어지는 일을 단계별로 추적합니다.

```text
사용자: open("data.txt", O_WRONLY)
  │
  ├─→ VFS (Virtual File System): 파일 시스템 종류 판별
  │     └─→ ext4 드라이버: inode 조회
  │           └─→ 디렉터리 엔트리에서 inode 번호 검색
  │                 └─→ inode 로드 (소유자, 권한, 블록 포인터)
  │
  ├─→ 파일 디스크립터 할당 (프로세스별 fd 테이블에 등록)
  │
사용자: write(fd, buf, 4096)
  │
  ├─→ 페이지 캐시에 쓰기 (메모리에만 반영, dirty page)
  │
  └─→ (나중에) pdflush/writeback이 디스크에 반영
```

`fsync(fd)` 호출 전까지는 데이터가 메모리에만 있을 수 있습니다. 정전 시 데이터 유실을 방지하려면 중요한 쓰기 후 반드시 `fsync`를 호출해야 합니다. 데이터베이스가 WAL(Write-Ahead Log)을 먼저 기록하는 이유도 이 때문입니다.

### 시스템 콜과 컨텍스트 스위치 비용

사용자 프로그램이 OS 기능을 사용하려면 시스템 콜을 통해 커널 모드로 전환해야 합니다.

```text
사용자 모드                           커널 모드
─────────────────────────────────────────────────────
프로그램 실행 ──→ syscall 명령 ──→ 커널 진입
                 (레지스터 저장)    (핸들러 실행)
                                   (결과 생성)
프로그램 재개 ←── sysret 명령 ←── 커널 복귀
                 (레지스터 복원)
```

시스템 콜 하나의 오버헤드는 약 100-1000 ns입니다. 네트워크 서버가 `epoll`로 수천 개 소켓을 하나의 시스템 콜로 처리하는 이유는 이 비용을 줄이기 위해서입니다.

컨텍스트 스위치(프로세스 전환)는 더 비쌉니다.

| 전환 유형 | 비용 | 이유 |
|-----------|------|------|
| 스레드 전환 (같은 프로세스) | ~1-5 μs | 레지스터 + 스택 포인터만 교체 |
| 프로세스 전환 | ~5-30 μs | + 페이지 테이블 교체 + TLB 플러시 |
| VM 전환 (가상 머신) | ~50-200 μs | + VMCS 저장/복원 |

이 비용을 줄이기 위해 Linux 커널은 프로세스 전환 시 TLB를 완전히 비우지 않고 PCID(Process Context ID)를 사용해 이전 매핑을 일부 유지합니다.

### 컨테이너와 OS 가상화

Docker 같은 컨테이너는 VM과 달리 호스트 커널을 공유합니다.

| 구분 | 가상 머신 | 컨테이너 |
|------|-----------|----------|
| 격리 수준 | 하드웨어 수준 (하이퍼바이저) | OS 수준 (namespace + cgroup) |
| 부팅 시간 | 수십 초 | 수백 ms |
| 메모리 오버헤드 | 수백 MB (게스트 OS) | 수 MB |
| 보안 격리 | 강함 | 커널 취약점 공유 위험 |

Linux namespace가 격리하는 자원:
- **PID**: 프로세스 ID 공간 분리
- **NET**: 네트워크 인터페이스, IP, 포트 분리
- **MNT**: 파일 시스템 마운트 포인트 분리
- **USER**: UID/GID 매핑 분리
- **IPC**: 공유 메모리, 세마포어 분리

cgroup은 CPU, 메모리, I/O 등 자원 사용량의 상한을 설정합니다. Kubernetes가 Pod에 리소스 제한을 거는 것이 cgroup의 직접적 활용입니다.
## 체크리스트

- [ ] 프로세스와 스레드의 차이를 메모리 관점에서 설명할 수 있는가
- [ ] CPython GIL이 무엇이고 어떤 작업에 영향을 주는지 아는가
- [ ] 가상 메모리, 페이지, 스왑의 의미를 이해했는가
- [ ] 시스템 콜이 비용이 있다는 점을 의식하는가
- [ ] 동시성과 병렬성을 구분해서 사용할 수 있는가

## 연습 문제

1. CPU 바운드 함수와 I/O 바운드 함수를 각각 스레드 4개, 프로세스 4개로 실행해 시간을 비교해 보세요.
2. `multiprocessing.Process`로 부모와 자식 프로세스가 같은 변수를 어떻게 다르게 보게 되는지 확인해 보세요.
3. `threading.Lock` 유무에 따라 여러 스레드가 카운터를 증가시킬 때 결과가 어떻게 달라지는지 관찰해 보세요.

## 정리 및 다음 단계

운영체제는 하드웨어를 추상화해 여러 프로그램이 안전하게 공존하도록 만듭니다. 프로세스·스레드·가상 메모리·시스템 콜은 우리가 작성하는 모든 코드의 무대입니다. 동시성 모델은 작업의 성격(CPU/I/O)에 맞게 골라야 합니다.

다음 글에서는 한 컴퓨터를 넘어 여러 컴퓨터가 데이터를 주고받는 방식 — 네트워크 — 를 다룹니다.


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

운영체제 단원에서는 프로세스/스레드 모델 차이, 동기화 비용, 시스템 콜 경계의 의미를 코드 실행 관점에서 추적합니다.


## 처음 질문으로 돌아가기

- **하나의 머신에서 많은 프로그램이 동시에 실행되는 것처럼 보이는 이유는 무엇일까요?**
  - CPU 스케줄러가 밀리초 단위로 프로세스를 전환(context switch)하기 때문입니다. Round Robin이나 CFS 같은 알고리즘이 각 프로세스에 타임 슬라이스를 배분하고, 사람이 인지하지 못할 정도로 빠르게 교대하므로 동시 실행처럼 보입니다.
- **프로세스와 스레드는 메모리와 격리 측면에서 어떻게 다를까요?**
  - 프로세스는 독립된 가상 주소 공간을 가져 서로의 메모리를 직접 접근할 수 없습니다. 스레드는 같은 프로세스 내에서 힙과 코드 영역을 공유하되 각자의 스택만 분리합니다. 공유 메모리 덕에 스레드 간 통신이 빠르지만, 동기화 없이 접근하면 경쟁 조건이 발생합니다.
- **가상 메모리는 왜 필요한 추상화일까요?**
  - 각 프로세스에 연속된 주소 공간을 제공해 프로그래밍을 단순화하고, 물리 메모리보다 큰 공간을 사용할 수 있게 합니다. 동시에 프로세스 간 메모리를 격리해 한 프로세스의 버그가 다른 프로세스를 망가뜨리지 않도록 보호합니다.
<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- [Computer Science 101 (4/10): 알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): 컴퓨터 구조](./05-computer-architecture.md)
- **운영체제 (현재 글)**
- 네트워크 (예정)
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Operating Systems: Three Easy Pieces (무료)](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Python — concurrent.futures 문서](https://docs.python.org/3/library/concurrent.futures.html)
- [Linux man-pages — system calls](https://man7.org/linux/man-pages/dir_section_2.html)
- [Andrew Tanenbaum — Modern Operating Systems](https://www.pearson.com/en-us/subject-catalog/p/modern-operating-systems/P200000003311)

- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)
Tags: Computer Science, 운영체제, 프로세스, 스레드, 가상 메모리, 동시성
