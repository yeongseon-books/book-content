---
series: operating-systems-101
episode: 2
title: "Operating Systems 101 (2/10): 프로세스와 스레드"
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
  - 동시성
  - 시스템
seo_description: 프로세스의 구성, 스레드와의 차이, fork/exec 모델, 선택 기준을 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (2/10): 프로세스와 스레드

"실행 중인 프로그램"이라는 표현은 익숙하지만, 운영체제 관점에서는 너무 뭉뚱그린 말입니다. 메모리, 열린 파일, 권한, CPU 상태까지 묶인 단위가 무엇인지 분리해서 봐야 동시성 설계가 선명해집니다.

특히 프로세스와 스레드를 섞어 이해하면 공유 범위와 격리 경계를 계속 헷갈리게 됩니다. 그래서 이 글에서는 두 단위를 운영체제가 실제로 다루는 기준으로 다시 정리합니다.

이 글은 Operating Systems 101 시리즈의 2번째 글입니다.

## 먼저 던지는 질문

- 프로세스는 어떤 자원을 자기 것으로 가지고 있을까요?
- 스레드는 무엇을 공유하고 무엇은 따로 가질까요?
- `fork`와 `exec`는 왜 두 단계로 나뉘어 있을까요?

## 큰 그림

![Operating Systems 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/02/02-01-what-the-process-shares-and-what-each-th.ko.png)

*Operating Systems 101 2장 흐름 개요*

## 기본 모델
> 한 프로세스는 자기만의 가상 주소 공간, 파일 디스크립터 테이블, 신호 처리기, 권한을 가집니다. 그 안에 한 개 이상의 스레드가 있고, 스레드는 메모리와 fd는 공유하지만 자신만의 스택과 레지스터 상태를 갖습니다.

### 프로세스와 스레드의 공유 경계

```text
+-----------------------------------------+
|  Process                                |
|  +----------+ +-----------+ +--------+  |
|  | Code     | | Heap      | | Globals|  |
|  +----------+ +-----------+ +--------+  |
|  +-------- File descriptor table -----+ |
|  |  0:stdin  1:stdout  2:stderr  ...  | |
|  +-----------------------------------+  |
|                                         |
|  +-- Thread A --+   +-- Thread B --+    |
|  |  Stack       |   |  Stack       |    |
|  |  Registers   |   |  Registers   |    |
|  +--------------+   +--------------+    |
+-----------------------------------------+
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "스레드와 프로세스는 그냥 둘 다 동시 실행 도구":**

```python
# I want these two tasks to run "at the same time"
import threading, multiprocessing
```

이 한 줄은 둘 중 어느 것을 골라야 하는지 알려 주지 않습니다.

**바꿔서 보면 — "공유하는 것이 다르다"는 모델:**

```text
multiprocessing.Process : separate memory, talk via queue/pipe/shared mem
threading.Thread        : same memory, needs locks, GIL applies

CPU-bound (large numpy matmul)  -> multiprocessing usually wins
I/O-bound (100 HTTP requests)   -> threading or asyncio is enough
```

같은 "동시 실행"이라도 무엇을 공유하느냐로 도구가 갈립니다.

## 단계별로 확인하기

### 1단계: 프로세스 식별자와 부모-자식 관계 보기

```python
import os

print(f"Parent PID (this process): {os.getpid()}")

pid = os.fork()
if pid == 0:
    print(f"Child  PID: {os.getpid()}, parent: {os.getppid()}")
else:
    os.waitpid(pid, 0)
    print(f"Parent: child {pid} exited")
```

`fork`는 한 번 호출되어 두 번 리턴합니다. 부모에는 자식 PID가, 자식에는 0이 돌아옵니다. 같은 코드인데 두 줄기로 갈라지는 경험이 핵심입니다.

### 2단계: 자식 분기 이후의 메모리 격리 확인

```python
import os

x = [1, 2, 3]
if os.fork() == 0:
    x.append(99)
    print(f"Child x:  {x}")
    os._exit(0)
os.wait()
print(f"Parent x: {x}")
```

자식이 `x`를 바꿔도 부모의 `x`는 그대로입니다. 두 프로세스는 같은 메모리를 보지 못합니다(겉보기는 같지만 내부적으로는 copy-on-write).

### 3단계: 스레드는 메모리를 공유한다

```python
import threading

x = [1, 2, 3]
def worker():
    x.append(99)

t = threading.Thread(target=worker)
t.start(); t.join()
print(f"Main x: {x}")
```

같은 `x` 리스트가 보입니다. 스레드는 같은 주소 공간을 공유하기 때문에 동기화가 필요해집니다.

### 4단계: 스레드와 프로세스의 성능 감각 보기

```python
import time, math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_heavy(n):
    return sum(math.sqrt(i) for i in range(n))

N = 5_000_000
tasks = [N] * 4

for Pool, label in [(ThreadPoolExecutor, "Thread"), (ProcessPoolExecutor, "Process")]:
    start = time.perf_counter()
    with Pool(max_workers=4) as ex:
        list(ex.map(cpu_heavy, tasks))
    print(f"{label}: {time.perf_counter() - start:.2f} s")
```

CPU 바운드 작업에서는 보통 프로세스 풀이 빠릅니다. CPython의 GIL 때문에 스레드는 같은 시점에 하나만 파이썬 코드를 실행할 수 있습니다.

### 5단계: 다른 프로그램으로 실행 이미지 바꾸기

```python
import os

if os.fork() == 0:
    os.execvp("ls", ["ls", "-la"])  # child becomes ls
    # this line is never reached
os.wait()
```

`fork`로 자식을 만들고 곧바로 `exec`로 다른 프로그램이 되는 패턴이 셸이 명령을 실행하는 표준 방식입니다. 자식 프로세스의 메모리는 새 프로그램의 이미지로 통째로 교체됩니다.

## 여기서 먼저 볼 점

- `fork`는 한 번 호출되고 두 번 리턴합니다
- 프로세스 간 메모리는 격리되어 있고, 스레드 간 메모리는 공유됩니다
- CPython의 GIL 때문에 CPU 바운드 + 스레드 조합은 종종 기대만큼 빠르지 않습니다
- `fork`+`exec`는 셸과 컨테이너 런타임의 기본 패턴입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 모든 동시성에 스레드 사용 | CPU 바운드는 GIL로 막힘 | CPU 바운드는 프로세스, I/O 바운드는 스레드/asyncio |
| 자식 프로세스 회수 안 함 | 좀비 프로세스 누적 | `os.wait`/`waitpid`로 회수 |
| 스레드 간 공유 데이터 락 미사용 | race condition, 알 수 없는 버그 | `threading.Lock` 또는 큐 사용 |
| `fork` 직후 큰 라이브러리 임포트 가정 | macOS에서 동작 차이, 안전성 문제 | `multiprocessing.set_start_method('spawn')` 고려 |
| 프로세스를 가볍다고 가정 | 수천 개 프로세스 생성으로 OS 자원 고갈 | 워커 풀 패턴으로 재사용 |

## 실무에서는 이렇게 본다

- 웹 서버: gunicorn은 워커 프로세스, uvicorn은 비동기, 둘을 조합
- 데이터 처리: `multiprocessing.Pool`로 CPU 바운드 ETL 분산
- 컨테이너: 컨테이너 런타임이 `clone`+`exec` 변형으로 격리된 자식 실행
- 백엔드 디버깅: `ps -ef`, `pstree`, `htop`로 프로세스/스레드 트리 확인
- 데이터 과학: `joblib`이 백엔드(스레드/프로세스)를 골라서 병렬화

## 체크리스트

- [ ] 프로세스가 가진 자원 네 가지를 말할 수 있는가
- [ ] 스레드와 프로세스가 공유하는 것과 안 하는 것을 안다
- [ ] CPU 바운드와 I/O 바운드의 적절한 도구를 안다
- [ ] `fork`와 `exec`의 역할 분리를 설명할 수 있는가
- [ ] 자식 프로세스 회수의 필요성을 안다

## 연습 문제

1. `os.fork()` 예제를 직접 실행해서 부모와 자식이 각각 어떤 PID를 보는지 정리해 보세요.
2. 같은 작업을 `ThreadPoolExecutor`와 `ProcessPoolExecutor`로 돌리고, CPU 바운드인지 I/O 바운드인지에 따라 결과가 어떻게 달라지는지 비교해 보세요.
3. `ps -ef`, `pstree`, `htop` 중 하나를 골라 지금 실행 중인 서비스의 프로세스/스레드 구조를 캡처하고, 무엇이 공유되고 무엇이 분리되는지 설명해 보세요.

## 마무리와 다음 글

프로세스는 격리된 자원 묶음이고, 스레드는 그 안에서 흐르는 동시 실행 단위입니다. 둘을 헷갈리면 동시성 코드가 미묘하게 깨지거나 성능이 기대만큼 나오지 않습니다. CPU 바운드와 I/O 바운드, 격리의 필요성, 메모리 공유 정도라는 세 가지 축으로 도구를 고를 수 있습니다.

다음 글에서는 OS가 그 많은 프로세스와 스레드 중 누구에게 CPU를 줄지를 결정하는 메커니즘 — 스케줄링을 봅니다.


## 운영체제 개념을 실무 판단으로 연결하기

### 스케줄링 정책을 숫자로 비교하는 방법
스케줄링은 이론 용어보다 대기시간과 응답시간으로 비교할 때 이해가 빠릅니다. 예를 들어 작업 집합이 `P1(도착 0, 실행 7)`, `P2(도착 2, 실행 4)`, `P3(도착 4, 실행 1)`일 때 FCFS와 SRTF의 결과를 비교하면 차이가 명확합니다.

- FCFS 평균 대기시간: `(0 + 5 + 7) / 3 = 4.0`
- SRTF 평균 대기시간: `(5 + 1 + 0) / 3 = 2.0`

같은 작업 집합이라도 정책에 따라 사용자 체감 지연이 크게 달라집니다. 서버가 인터랙티브 트래픽 중심인지, 배치 작업 중심인지에 따라 정책 선택 기준이 달라져야 합니다.

### 메모리 계층과 페이지 교체를 그림으로 정리하기
가상 메모리에서는 "어떤 페이지를 언제 내보내는가"가 성능을 좌우합니다. 아래 개념도는 자주 발생하는 페이지 폴트 경로를 보여줍니다.

```text
CPU 접근 -> 페이지 테이블 조회 -> miss
miss -> 페이지 폴트 트랩 -> 커널 핸들러
핸들러 -> victim 페이지 선택(LRU 근사)
victim dirty? yes -> 디스크 write-back
새 페이지 read -> 매핑 갱신 -> 재실행
```

핵심은 디스크 I/O가 개입되는 순간 지연이 급증한다는 점입니다. 따라서 워킹셋을 메모리에 유지하도록 데이터 구조와 접근 패턴을 설계해야 합니다. 순차 접근과 지역성 높은 캐시 친화 구조가 중요한 이유가 여기에 있습니다.

### 시스템 콜 경계에서 비용이 발생하는 이유
애플리케이션 코드는 사용자 모드에서 실행되지만, 파일 I/O와 네트워크 I/O는 커널 모드 전환이 필요합니다. 전환이 잦으면 오버헤드가 누적되므로 호출 단위를 조정하는 것이 좋습니다.

| syscall | 용도 | 성능 관점 포인트 |
| --- | --- | --- |
| `read` | 파일/소켓 입력 | 작은 크기로 반복 호출하면 전환 비용 증가 |
| `write` | 파일/소켓 출력 | 버퍼링 없이 자주 호출하면 처리량 저하 |
| `open` | 파일 디스크립터 획득 | 반복 open/close는 캐시 이점 상실 |
| `epoll_wait` | 이벤트 대기 | 다중 연결 처리에서 busy loop 방지 |
| `mmap` | 파일 메모리 매핑 | 랜덤 접근 workload에서 복사 비용 절감 가능 |

예를 들어 로그 수집기를 구현할 때 `write`를 1줄마다 호출하기보다 버퍼 단위로 모아 호출하면 syscall 횟수가 줄어 처리량이 개선됩니다. 운영체제 지식이 코드 수준 최적화로 직접 이어지는 지점입니다.

### 병행성 디버깅 체크리스트
경합 문제를 조사할 때는 증상만 보지 말고 스케줄링, 락 소유 시간, I/O 대기 시간을 함께 봐야 합니다.

1. `pidstat -w`로 컨텍스트 스위치 급증 여부 확인
2. `vmstat 1`로 run queue 길이와 I/O wait 확인
3. `strace -f -tt`로 블로킹 syscall 지점 식별
4. 락 획득/반납 시각을 애플리케이션 로그에 기록

이 네 단계를 함께 적용하면 "CPU가 느린 문제"인지 "락 경합 문제"인지 "디스크 대기 문제"인지를 분리할 수 있습니다. 운영체제 개념은 결국 문제를 정확히 분해하는 관측 프레임입니다.

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


## 프로세스와 스레드를 선택할 때 쓰는 실무 기준표

프로세스와 스레드는 "무엇이 더 빠른가"보다 "무엇을 격리하고 무엇을 공유할 것인가"로 고르는 편이 정확합니다.

| 상황 | 권장 단위 | 이유 |
| --- | --- | --- |
| CPU 바운드 이미지 변환 | 프로세스 풀 | GIL 영향 회피, 장애 격리 |
| I/O 바운드 API 크롤링 | 스레드 또는 asyncio | 공유 메모리로 통신 단순 |
| 멀티테넌트 작업자 | 프로세스 | 테넌트 간 메모리 격리 |
| 고빈도 상태 공유 | 스레드 | 직렬화 비용 없이 공유 |

### `/proc`로 프로세스와 스레드 상태 확인

```bash
PID=$(pgrep -f "gunicorn" | head -n 1)
cat /proc/$PID/status | grep -E "Name|State|Threads|VmRSS"
ps -L -p "$PID" -o pid,tid,stat,pcpu,comm
```

```text
Name:   gunicorn
State:  S (sleeping)
Threads:        33
VmRSS:  512340 kB
```

스레드 수가 급증하고 `VmRSS`도 함께 상승하면, 스레드 스택과 큐 적체를 동시에 의심할 수 있습니다.

### `fork` 이후 copy-on-write가 깨지는 지점

`fork` 직후에는 부모/자식이 페이지를 공유하지만, 자식이 쓰기를 시작하면 페이지 복사가 발생합니다. 대용량 데이터 구조를 가진 부모에서 자식이 초기에 큰 쓰기를 하면 메모리 사용량이 급증합니다.

```python
import os

buf = bytearray(200 * 1024 * 1024)
pid = os.fork()
if pid == 0:
    for i in range(0, len(buf), 4096):
        buf[i] = 1  # 페이지 단위로 CoW 유발
    os._exit(0)
os.waitpid(pid, 0)
```

이 패턴은 워커 모델의 시작 지연과 메모리 폭증을 동시에 만들 수 있습니다.


## 심화 실습: 운영체제 문제를 계층별로 좁히는 워크북

실무에서 운영체제 문제는 보통 "느리다", "가끔 멈춘다", "재시작하면 잠깐 괜찮다"처럼 모호한 문장으로 시작합니다. 이때 중요한 것은 추측을 늘리는 것이 아니라, 관찰 단위를 줄여서 재현 가능한 사실로 바꾸는 일입니다. 아래 워크북은 CPU 스케줄링, 메모리 압박, 시스템 콜 패턴, 파일 시스템 내구성, 락 경합을 같은 순서로 점검하도록 구성했습니다.

### 1) 증상 분류: 실행 대기인가, I/O 대기인가

```bash
vmstat 1
pidstat -w -p <PID> 1
iostat -xz 1
```

- `r`(run queue)가 길고 `wa`가 낮으면 CPU 경쟁이 중심입니다.
- `wa`가 높고 디스크 지연이 길면 I/O 병목 가능성이 큽니다.
- 컨텍스트 스위치(`cs`)가 급증하면 락 경합이나 과도한 타임슬라이스 분할을 의심합니다.

이 단계의 목표는 "CPU가 부족하다" 같은 포괄 진단이 아니라, "CPU runnable 대기"와 "디스크 대기"를 명확히 분리하는 것입니다.

### 2) 메모리 계층 점검: RSS, 페이지 폴트, 스왑

```bash
cat /proc/<PID>/status | grep -E "VmRSS|VmSize|Threads"
cat /proc/<PID>/stat | awk '{print "minflt=" $10 ", majflt=" $12}'
free -h
cat /proc/swaps
```

- `majflt` 증가: 디스크에서 페이지를 자주 가져오는 상태입니다.
- 스왑 사용 증가: 워킹셋이 물리 메모리를 넘어 응답성이 무너지기 쉬운 상태입니다.
- 스레드 수 급증 + RSS 증가: 스택 증가와 큐 적체를 같이 확인해야 합니다.

메모리 이슈는 OOM 시점보다 그 이전 신호를 보는 것이 중요합니다. RSS만 보면 늦고, 페이지 폴트와 스왑 추세를 같이 봐야 앞단에서 대응할 수 있습니다.

### 3) 시스템 콜 트레이스: 호출 의미를 비용으로 읽기

```bash
strace -f -tt -T -c -p <PID>
```

요약표에서 자주 보는 패턴:
- `read`/`write` 호출 수 과다: 버퍼링 단위가 너무 작을 가능성
- `futex` 비중 과다: 락 경합, 임계 구역 과대
- `epoll_wait` 비중 높음: 이벤트 대기 중심 workload
- `openat`/`close` 반복 과다: 핸들 재사용 부족

시스템 콜 추적은 "언어 런타임 이슈"를 "커널 경계 비용"으로 번역해 줍니다. 이 번역이 되면 코드 수정 지점이 훨씬 구체적으로 보입니다.

### 4) 스케줄링 정책을 간단 모델로 검증

아래처럼 작은 작업 집합을 만들어 정책 차이를 먼저 머리로 검증해 두면, 실제 서비스 지표 해석이 쉬워집니다.

```text
작업 집합: A(도착0,실행6), B(도착1,실행2), C(도착2,실행1)

FCFS:
0      6  8 9
|---A---|-B|-C|
평균 대기시간 = (0 + 5 + 6) / 3 = 3.67

SRTF:
0 1 3 4     9
|A|B|C|--A--|
평균 대기시간 = (3 + 0 + 1) / 3 = 1.33
```

서비스가 인터랙티브 중심이면 짧은 작업 응답성 개선이 체감 품질을 좌우합니다. 반대로 배치 중심이면 컨텍스트 스위치 감소와 처리량 안정성이 더 중요할 수 있습니다.

### 5) 파일 시스템 안정성 검증 시나리오

저장 코드는 정상 흐름이 아니라 비정상 종료를 기준으로 검증해야 합니다.

검증 순서:
1. 임시 파일에 기록
2. `fsync(fd)`
3. `rename`
4. 부모 디렉터리 `fsync(dirfd)`

이 절차를 지키면 전원 장애나 프로세스 크래시에서도 "부분 파일" 위험을 크게 줄일 수 있습니다. 운영체제는 내구성을 제공하지만, 애플리케이션이 내구성 경계를 정확히 호출해 주어야 보장이 성립합니다.

### 6) 데드락과 락 경합을 구분해서 대응

데드락은 진행이 완전히 멈추고, 락 경합은 진행은 되지만 매우 느린 상태입니다. 둘은 대응이 다릅니다.

- 데드락 대응: 락 획득 순서 전역 규약, 타임아웃, 순환 대기 탐지
- 경합 대응: 임계 구역 단축, 락 분할, 공유 상태 축소, 큐 기반 전달

```text
T1: lock(A) -> wait(B)
T2: lock(B) -> wait(A)
=> 순환 대기, 데드락
```

대부분의 서비스 장애는 완전 데드락보다 "느린 경합" 형태로 나타납니다. `futex` 비중, 대기 큐 길이, p95 지연시간을 함께 보면 판별이 쉽습니다.

### 7) 컨테이너 환경에서 반드시 추가할 관찰 항목

컨테이너에서는 호스트와 보이는 값이 다를 수 있으므로 cgroup 파일을 직접 읽어야 합니다.

```bash
cat /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.current
cat /sys/fs/cgroup/cpu.max
cat /proc/1/cgroup
```

- `memory.max` 대비 `memory.current` 추세로 OOM 위험을 예측합니다.
- `cpu.max` 쿼터가 낮으면 runnable 상태여도 실제 처리량이 제한됩니다.
- PID 1 처리(signal, zombie reap) 상태를 확인합니다.

컨테이너 문제는 애플리케이션 버그와 리소스 격리 정책이 겹쳐 보이는 경우가 많기 때문에, OS 계층과 cgroup 계층을 동시에 보아야 합니다.

### 8) 장애 보고서에 남겨야 할 최소 증거

문제를 재현 가능하게 만들려면 지표 스냅샷을 표준 형식으로 남겨야 합니다.

- 시간: 관찰 시작/종료 시각
- CPU: `vmstat`, `pidstat -w`
- 메모리: `/proc/<pid>/status`, major/minor fault
- 시스템 콜: `strace -c` 상위 10개
- 파일/저장: `fsync` 유무, 쓰기 단위, 저장 방식(덮어쓰기/원자적 교체)
- 동기화: 락 순서, 임계 구역 길이, 타임아웃 정책

이 여섯 항목만 확보해도 "느리다"는 제보를 재현 가능한 기술 보고서로 바꿀 수 있습니다.

### 9) 운영체제 학습을 코드 리뷰 기준으로 연결하기

운영체제 지식은 문답형 지식으로 끝나면 금방 사라집니다. 코드 리뷰 체크리스트로 연결해야 팀의 습관으로 남습니다.

- 시스템 콜 경계: 작은 read/write 반복이 없는가
- 메모리 상한: 캐시에 용량/회수 정책이 있는가
- 동기화 경계: 락 순서 규약이 문서화되어 있는가
- 내구성 경계: 원자적 저장 절차를 따르는가
- 관찰 가능성: `/proc`, strace, 메트릭으로 검증 가능한가

이 체크리스트를 PR 템플릿에 넣으면 운영체제 개념이 설계 단계에서 바로 작동합니다.

### 10) 한 줄 정리

운영체제는 배경지식이 아니라, 성능/안정성/보안 문제를 분해하는 좌표계입니다. 좌표계가 있으면 같은 장애도 더 짧은 시간에 더 정확하게 해결할 수 있습니다.

## 처음 질문으로 돌아가기

- **프로세스는 어떤 자원을 자기 것으로 가지고 있을까요?**
  - 본문의 기준은 프로세스와 스레드를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **스레드는 무엇을 공유하고 무엇은 따로 가질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`fork`와 `exec`는 왜 두 단계로 나뉘어 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- **프로세스와 스레드 (현재 글)**
- 스케줄링 (예정)
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
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)
- [Python multiprocessing 문서](https://docs.python.org/3/library/multiprocessing.html)
- [Python threading 문서](https://docs.python.org/3/library/threading.html)

Tags: Computer Science, 운영체제, 프로세스, 스레드, 동시성, 시스템
