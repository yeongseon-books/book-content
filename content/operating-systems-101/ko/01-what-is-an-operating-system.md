---
series: operating-systems-101
episode: 1
title: "Operating Systems 101 (1/10): 운영체제란 무엇인가?"
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
  - 시스템
  - 기초
  - 커널
  - 추상화
seo_description: 운영체제의 정의와 역할, 커널과 사용자 모드, 핵심 추상화를 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (1/10): 운영체제란 무엇인가?

운영체제를 처음 배우면 보통 커널, 시스템 콜, 드라이버 같은 용어부터 만납니다. 그런데 운영 환경에서 더 자주 마주치는 질문은 따로 있습니다. 왜 같은 코드가 어떤 서버에서는 느리고, 어떤 환경에서는 파일을 못 열고, 어떤 순간에는 메모리 부족으로 죽는가입니다.

이 질문을 풀려면 운영체제를 교과서 속 배경지식이 아니라, 매 순간 CPU·메모리·디스크를 대신 조정하는 실행 환경으로 봐야 합니다. 이 글에서는 그 출발점을 잡겠습니다.

이 글은 Operating Systems 101 시리즈의 첫 번째 글입니다.


![Operating Systems 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/01/01-01-diagram.ko.png)
*Operating Systems 101 1장 흐름 개요*

## 먼저 던지는 질문

- 운영체제는 정확히 어떤 문제를 해결하려고 존재할까요?
- 커널 모드와 사용자 모드는 왜 굳이 분리되어 있을까요?
- 프로세스, 파일, 소켓 같은 추상화는 실제로 무엇을 감추고 있을까요?

## 기본 모델
> 운영체제는 사용자 프로그램과 하드웨어 사이에 위치하는 소프트웨어 계층입니다. 위로는 응용 프로그램에게 시스템 콜을 통해 단순한 인터페이스를 제공하고, 아래로는 CPU 스케줄링, 메모리 할당, 디바이스 드라이버, 파일 시스템을 통해 하드웨어를 직접 다룹니다.

### 운영체제가 끼어드는 위치

```text
+---------------------------------------------+
|  Application (Python, Browser, IDE, ...)    |
+---------------------------------------------+
|  System Call Interface  (read, write, ...)  |
+---------------------------------------------+
|  Kernel                                     |
|   - Process scheduler                       |
|   - Memory manager                          |
|   - File systems / VFS                      |
|   - Network stack                           |
|   - Device drivers                          |
+---------------------------------------------+
|  Hardware (CPU, RAM, Disk, NIC, ...)        |
+---------------------------------------------+
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "운영체제는 그냥 컴퓨터를 켜 주는 것":**

```python
with open("data.txt") as f:
    print(f.read())
```

이 세 줄이 실행되려면, 누군가는 디스크의 어느 블록에 `data.txt`가 있는지 찾고, 디스크 컨트롤러에 명령을 내리고, 결과를 메모리에 옮기고, 그 메모리를 우리 프로세스가 읽을 수 있도록 매핑해야 합니다.

**바꿔서 보면 — "운영체제가 매 줄마다 일하고 있다"는 모델:**

```text
open()  -> system call -> kernel walks the file system, finds the inode
                       -> hands a file descriptor back to user space
read()  -> system call -> queues an I/O request to the disk driver
                       -> data flows: kernel buffer -> user buffer
print() -> system call (write to stdout)
                       -> handed to the terminal device driver
```

세 줄짜리 파이썬 코드는 사실 시스템 콜의 연속입니다.

## 단계별로 확인하기

### 1단계: 시스템 콜 추적해 보기

```bash
# Linux: see exactly which syscalls one Python line triggers
strace -e trace=openat,read,write,close \
    python3 -c "open('data.txt').read()"
```

실행하면 `openat(AT_FDCWD, "data.txt", O_RDONLY) = 3` 같은 줄이 보입니다. 이 숫자 `3`이 우리가 받은 파일 디스크립터입니다. 실제 디스크 작업은 모두 커널이 합니다.

### 2단계: 사용자 모드와 커널 모드 시간 측정

```bash
/usr/bin/time -v python3 -c "
with open('/etc/hosts') as f:
    for _ in range(100000):
        f.seek(0); f.read()
" 2>&1 | grep -E "User time|System time"
```

`User time`은 우리 코드가 사용자 모드에서 쓴 시간, `System time`은 커널이 우리를 위해 쓴 시간입니다. I/O가 많은 프로그램일수록 `System time`이 늘어납니다.

### 3단계: 프로세스가 운영체제에게서 받은 자원 확인

```python
import os, resource

print(f"PID                  : {os.getpid()}")
print(f"Parent PID           : {os.getppid()}")
print(f"Open file limit      : {resource.getrlimit(resource.RLIMIT_NOFILE)}")
print(f"Virtual memory limit : {resource.getrlimit(resource.RLIMIT_AS)}")
```

PID는 OS가 나에게 부여한 식별자, fd 한계와 메모리 한계는 OS가 강제하는 제약입니다. 우리는 OS가 나눠 준 몫 안에서만 살 수 있습니다.

### 4단계: 프로세스 정보 파일로 현재 상태 들여다보기

```bash
# Kernel-side view of this process
cat /proc/self/status | head -20
# File descriptors currently open
ls -l /proc/self/fd
```

리눅스에서 `/proc`는 커널이 가진 정보를 파일처럼 노출하는 가상 파일 시스템입니다. 커널은 우리 프로세스에 대한 메타데이터(상태, 메모리 사용량, 열린 파일)를 모두 알고 있습니다.

### 5단계: 운영체제 없는 세상을 상상해 보기

```text
[No OS]                              [With OS]
- Apps poke disk sectors directly    - open()/read() abstract files
- Apps overwrite each other's RAM    - virtual memory isolates them
- One app monopolizes the CPU         - scheduler shares CPU time
- Each app ships device-specific code - drivers expose one interface
```

OS의 가치는 이 둘의 차이입니다. 우리가 평소 느끼는 "그냥 잘 돌아간다"는 감각은 모두 이 추상화 위에 서 있습니다.

## 여기서 먼저 볼 점

- 모든 파일 작업은 사실 시스템 콜의 연속입니다
- 사용자 모드와 커널 모드 사이의 전환은 비용이 있습니다
- 프로세스에게 주어지는 자원은 OS가 정한 한계 안에 있습니다
- `/proc`나 `/sys` 같은 가상 파일 시스템으로 커널과 대화할 수 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| OS를 단순한 부팅 도구로 보기 | 시스템 문제 분석을 못 함 | OS를 자원 관리자로 의식한다 |
| 사용자/커널 모드 비용 무시 | 잦은 시스템 콜로 성능 저하 | 버퍼링·일괄 처리로 호출을 줄인다 |
| 파일 디스크립터를 무한 자원으로 가정 | "Too many open files" 에러 | rlimit를 알고 닫기를 보장한다 |
| 모든 OS가 동일하다고 가정 | 리눅스 코드가 윈도우에서 실패 | OS별 시스템 콜 차이를 안다 |
| 에러 코드를 "그냥 실패"로 처리 | 디버깅 정보 손실 | errno와 시스템 콜 매뉴얼을 본다 |

## 실무에서는 이렇게 본다

- 백엔드 운영: `top`, `htop`, `iostat`로 OS가 보고하는 자원 사용률 분석
- 컨테이너 트러블슈팅: `strace`로 컨테이너 내부 시스템 콜 디버깅
- 보안: 의심 프로세스의 시스템 콜 패턴을 `auditd`로 추적
- 성능 튜닝: epoll, io_uring 같은 OS 제공 비동기 I/O 메커니즘 활용
- 임베디드/IoT: 작은 OS(FreeRTOS, Zephyr)를 직접 선택하고 설정

## 체크리스트

- [ ] 운영체제의 두 가지 역할(자원 관리, 추상화)을 설명할 수 있는가
- [ ] 사용자 모드와 커널 모드의 차이를 설명할 수 있는가
- [ ] 시스템 콜이 무엇이고 왜 비싼지 안다
- [ ] `strace`나 `/proc`로 OS와 대화할 수 있다
- [ ] OS가 주는 자원에는 한계가 있고, 한계는 조정 가능하다는 감각을 갖고 있는가

## 연습 문제

1. `strace -c python3 your_script.py`를 실행해서 가장 많이 호출된 시스템 콜 세 개를 적고, 각 호출이 무엇을 하는지 한 문단으로 설명해 보세요.
2. `ulimit -n`으로 파일 디스크립터 한도를 확인한 뒤, 파일을 반복해서 여는 작은 스크립트를 만들어 어떤 에러가 나는지 직접 확인해 보세요.
3. `/proc/self/status`에서 `VmRSS`, `Threads`, `State`를 읽고, 각 필드가 지금 프로세스의 어떤 상태를 말하는지 자기 말로 정리해 보세요.

## 마무리와 다음 글

운영체제는 하드웨어 위에 얹혀 자원을 관리하고, 응용 프로그램에게 깔끔한 추상화를 제공하는 소프트웨어 계층입니다. 사용자 모드와 커널 모드의 분리, 시스템 콜이라는 정해진 통로, 그리고 프로세스라는 추상화 — 이 세 가지가 OS를 이해하는 출발점입니다.

다음 글에서는 OS가 만들어 주는 가장 기본적인 추상화인 프로세스를 자세히 봅니다. 프로세스는 무엇으로 구성되어 있고, 스레드와는 어떻게 다른지, 그리고 새 프로세스는 어떻게 만들어지는지를 따라갑니다.


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


## 운영자가 바로 써먹는 관찰 루틴

운영체제 개념을 실제 점검 루틴으로 바꾸면 장애 분석 속도가 크게 빨라집니다. 아래 루틴은 CPU, 메모리, 파일 디스크립터, 프로세스 상태를 같은 시간축에서 관찰하도록 설계했습니다.

### `/proc` 출력으로 현재 프로세스 해부하기

```bash
PID=$(pgrep -f "python3 app.py" | head -n 1)
cat /proc/$PID/status | grep -E "Name|State|Threads|VmRSS|VmSize|voluntary_ctxt_switches|nonvoluntary_ctxt_switches"
ls -l /proc/$PID/fd | wc -l
cat /proc/$PID/limits | grep -E "open files|max user processes"
```

```text
Name:   python3
State:  S (sleeping)
Threads:        12
VmRSS:  182340 kB
VmSize: 1042200 kB
voluntary_ctxt_switches:        154233
nonvoluntary_ctxt_switches:     3211
```

이 출력만으로도 "CPU 바운드인가", "I/O 대기가 긴가", "fd 누수가 있는가"를 1차 분류할 수 있습니다. 중요한 점은 지표를 개별 숫자로 보지 않고, 같은 시각의 관계로 보는 것입니다.

### 메모리 레이아웃을 사고 도구로 쓰기

```text
낮은 주소
+-------------------------+
| text / rodata           |  코드, 상수
+-------------------------+
| data / bss              |  전역 변수
+-------------------------+
| heap                    |  동적 할당, 객체
|           ↑             |
|           |             |
|           |             |
|           ↓             |
| stack                   |  함수 호출 프레임
+-------------------------+
높은 주소
```

메모리 문제를 만났을 때 이 그림으로 "어느 영역이 커지는가"를 먼저 고르면 디버깅 범위가 줄어듭니다. 파이썬 서비스라면 힙 증가와 스레드 증가(스택 증가)를 함께 확인해야 합니다.

### 시스템 콜 추적으로 병목 구간 분리

```bash
strace -f -tt -T -e trace=read,write,openat,close,futex,epoll_wait -p "$PID"
```

`futex` 체류 시간이 길면 락 경합, `read`/`write`가 매우 짧은 호출로 과다하면 버퍼링 부족, `epoll_wait` 비중이 크면 I/O 대기 중심 workload일 가능성이 큽니다. 운영체제 관점에서는 코드 줄 수보다 "호출 패턴"이 먼저 보입니다.


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

- **운영체제는 정확히 어떤 문제를 해결하려고 존재할까요?**
  - 본문의 기준은 운영체제란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **커널 모드와 사용자 모드는 왜 굳이 분리되어 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **프로세스, 파일, 소켓 같은 추상화는 실제로 무엇을 감추고 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **운영체제란 무엇인가? (현재 글)**
- 프로세스와 스레드 (예정)
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
- [Silberschatz, Galvin, Gagne — Operating System Concepts](https://www.os-book.com/)
- [Linux man-pages project](https://man7.org/linux/man-pages/)
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)

Tags: Computer Science, 운영체제, 시스템, 기초, 커널, 추상화
