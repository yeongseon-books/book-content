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

## 이 글에서 다룰 문제

- 운영체제는 정확히 어떤 문제를 해결하려고 존재할까요?
- 커널 모드와 사용자 모드는 왜 굳이 분리되어 있을까요?
- 프로세스, 파일, 소켓 같은 추상화는 실제로 무엇을 감추고 있을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

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

OS의 두 가지 핵심 역할:

1. **자원 관리자**: CPU 시간, RAM, 디스크 I/O, 네트워크 대역폭을 여러 프로세스에 공정하게 나눕니다.
2. **추상화 제공자**: 디스크 섹터 → 파일, 물리 메모리 주소 → 가상 주소, 네트워크 패킷 → 소켓이라는 깔끔한 인터페이스를 제공합니다.

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

### OS 없이 vs OS 있을 때: 추상화의 가치

```text
[No OS]                              [With OS]
- Apps poke disk sectors directly    - open()/read() abstract files
- Apps overwrite each other's RAM    - virtual memory isolates them
- One app monopolizes the CPU         - scheduler shares CPU time
- Each app ships device-specific code - drivers expose one interface
- One crash takes the whole machine  - process isolation limits damage
```

OS의 가치는 이 둘의 차이입니다. 우리가 평소 느끼는 "그냥 잘 돌아간다"는 감각은 모두 이 추상화 위에 서 있습니다.

## 단계별로 확인하기

### 1단계: 시스템 콜 추적해 보기

```bash
# Linux: see exactly which syscalls one Python line triggers
strace -e trace=openat,read,write,close \
    python3 -c "open('data.txt').read()"
```

실행하면 `openat(AT_FDCWD, "data.txt", O_RDONLY) = 3` 같은 줄이 보입니다. 이 숫자 `3`이 우리가 받은 파일 디스크립터입니다. 실제 디스크 작업은 모두 커널이 합니다.

시스템 콜 요약 통계를 보려면:

```bash
strace -c python3 your_script.py
```

어떤 시스템 콜이 몇 번 불렸는지, 총 시간은 얼마인지 한눈에 볼 수 있습니다. 느린 프로그램이 I/O 바운드인지 CPU 바운드인지 파악하는 첫 번째 도구입니다.

### 2단계: 사용자 모드와 커널 모드 시간 측정

```bash
/usr/bin/time -v python3 -c "
with open('/etc/hosts') as f:
    for _ in range(100000):
        f.seek(0); f.read()
" 2>&1 | grep -E "User time|System time"
```

`User time`은 우리 코드가 사용자 모드에서 쓴 시간, `System time`은 커널이 우리를 위해 쓴 시간입니다. I/O가 많은 프로그램일수록 `System time`이 늘어납니다.

```bash
# 짧게 확인하려면
time python3 -c "open('/dev/null').read()"
# real / user / sys 세 줄로 요약
```

`sys` 숫자가 크면 시스템 콜이 많거나 비싸다는 뜻입니다.

### 3단계: 프로세스가 운영체제에게서 받은 자원 확인

```python
import os, resource

print(f"PID                  : {os.getpid()}")
print(f"Parent PID           : {os.getppid()}")
print(f"Open file limit      : {resource.getrlimit(resource.RLIMIT_NOFILE)}")
print(f"Virtual memory limit : {resource.getrlimit(resource.RLIMIT_AS)}")
print(f"Max processes        : {resource.getrlimit(resource.RLIMIT_NPROC)}")
```

PID는 OS가 나에게 부여한 식별자, fd 한계와 메모리 한계는 OS가 강제하는 제약입니다. 우리는 OS가 나눠 준 몫 안에서만 살 수 있습니다.

### 4단계: 프로세스 정보 파일로 현재 상태 들여다보기

```bash
# Kernel-side view of this process
cat /proc/self/status | head -20
# File descriptors currently open
ls -l /proc/self/fd
# Memory map layout
cat /proc/self/maps | head -20
```

리눅스에서 `/proc`는 커널이 가진 정보를 파일처럼 노출하는 가상 파일 시스템입니다. 커널은 우리 프로세스에 대한 메타데이터(상태, 메모리 사용량, 열린 파일)를 모두 알고 있습니다.

### 5단계: 시스템 콜 비용 직접 측정하기

```python
import os, time

# getpid: 가벼운 syscall 기준점 측정
N = 1_000_000
t = time.perf_counter()
for _ in range(N):
    os.getpid()
elapsed = time.perf_counter() - t
print(f"getpid x {N:,}: {elapsed*1000:.1f} ms  ({elapsed/N*1e6:.2f} us/call)")

# read: I/O syscall 비교
buf = bytearray(1)
fd = os.open("/dev/null", os.O_RDONLY)
t2 = time.perf_counter()
for _ in range(100_000):
    os.read(fd, 1)
elapsed2 = time.perf_counter() - t2
os.close(fd)
print(f"read(/dev/null) x 100k: {elapsed2*1000:.1f} ms  ({elapsed2/100_000*1e6:.2f} us/call)")
```

일반적으로 `getpid` 하나에 0.1~0.3 마이크로초가 걸립니다. I/O 시스템 콜은 디스크 대기가 포함되어 수십~수천 마이크로초에 이릅니다. 시스템 콜이 "비싸다"는 말은 이 비용이 누적될 때를 말합니다.

### 6단계: 커널 모드 진입 경로 이해하기

```text
사용자 코드 실행 (ring 3)
        |
        | syscall 명령
        v
커널 코드 실행 (ring 0)  <-- 레지스터 저장, 스택 전환
        |
        | 요청 처리 (I/O, 메모리 할당, 스케줄링 등)
        v
사용자 모드 복귀  <-- 레지스터 복원, 스택 복원
        |
        v
사용자 코드 계속 실행
```

이 전환이 수백 나노초에서 수 마이크로초의 오버헤드를 만듭니다. 루프 안에 시스템 콜이 있다면 이 비용이 쌓입니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| OS를 단순한 부팅 도구로 보기 | 시스템 문제 분석을 못 함 | OS를 자원 관리자로 의식한다 |
| 사용자/커널 모드 비용 무시 | 잦은 시스템 콜로 성능 저하 | 버퍼링·일괄 처리로 호출을 줄인다 |
| 파일 디스크립터를 무한 자원으로 가정 | "Too many open files" 에러 | rlimit를 알고 닫기를 보장한다 |
| 모든 OS가 동일하다고 가정 | 리눅스 코드가 윈도우에서 실패 | OS별 시스템 콜 차이를 안다 |
| 에러 코드를 "그냥 실패"로 처리 | 디버깅 정보 손실 | errno와 시스템 콜 매뉴얼을 본다 |

## 실무에서는 이렇게 본다

- **백엔드 운영**: `top`, `htop`, `iostat`로 OS가 보고하는 자원 사용률 분석
- **컨테이너 트러블슈팅**: `strace`로 컨테이너 내부 시스템 콜 디버깅
- **보안**: 의심 프로세스의 시스템 콜 패턴을 `auditd`로 추적
- **성능 튜닝**: epoll, io_uring 같은 OS 제공 비동기 I/O 메커니즘 활용
- **임베디드/IoT**: 작은 OS(FreeRTOS, Zephyr)를 직접 선택하고 설정

### 실무 진단 흐름 예시

서버가 갑자기 느려졌을 때 OS 관점 접근 순서:

```bash
# 1단계: CPU 바운드인가, I/O 바운드인가
top -b -n 1 | head -20

# 2단계: 어느 프로세스가 문제인가
ps aux --sort=-%cpu | head -10

# 3단계: 무슨 작업을 하고 있는가
strace -p <PID> -c -e trace=read,write,futex 2>&1 | head -30

# 4단계: 어떤 파일/소켓에 접근하는가
lsof -p <PID>
```

네 단계 모두 OS가 노출하는 인터페이스를 쓰는 진단입니다.

## 운영 체크리스트

- [ ] 운영체제의 두 가지 역할(자원 관리, 추상화)을 설명할 수 있는가
- [ ] 사용자 모드와 커널 모드의 차이를 설명할 수 있는가
- [ ] 시스템 콜이 무엇이고 왜 비싼지 안다
- [ ] `strace`나 `/proc`로 OS와 대화할 수 있다
- [ ] OS가 주는 자원에는 한계가 있고, 한계는 조정 가능하다는 감각을 갖고 있는가

## 시스템 관찰: CPU, I/O, 모드 전환을 함께 읽기

### run queue와 CPU 사용률을 함께 읽기

CPU 사용률이 낮다고 항상 여유가 있는 것은 아닙니다. run queue 길이가 길고 I/O wait가 높으면 병목이 디스크나 네트워크일 수 있습니다.

```bash
vmstat 1
# r(run queue), b(blocked), wa(I/O wait)를 같이 본다
mpstat -P ALL 1
iostat -xz 1
```

| vmstat 컬럼 | 의미 | 주의 신호 |
| --- | --- | --- |
| r | run queue 길이 | CPU 수보다 지속적으로 크면 CPU 포화 |
| b | I/O 대기로 블록된 프로세스 수 | 0보다 크면 I/O 병목 |
| wa | CPU가 I/O 완료를 기다리는 시간 비율 | 20% 이상이면 I/O 바운드 의심 |
| si/so | swap in / swap out (KB/s) | 0 이상이면 메모리 부족 신호 |

세 도구를 같이 보면 CPU 바운드인지 I/O 바운드인지 분리할 수 있습니다. 운영체제 관점에서 중요한 것은 단일 지표가 아니라 지표 간 관계입니다.

### 시스템 콜 비용을 직접 측정하기

모드 전환 비용은 추상적으로만 설명하면 감이 오지 않습니다. 아래 코드로 직접 재면 기준값이 생깁니다.

```python
import os, time

# getpid: 가벼운 syscall 기준
N = 1_000_000
t = time.perf_counter()
for _ in range(N):
    os.getpid()
elapsed = time.perf_counter() - t
print(f"getpid x {N:,}: {elapsed*1000:.1f} ms  ({elapsed/N*1e6:.2f} us/call)")
```

일반적으로 getpid 하나에 0.1~0.3 마이크로초가 걸립니다. I/O 시스템 콜은 디스크 대기가 포함되어 수십~수천 마이크로초에 이릅니다. 시스템 콜이 "비싸다"는 말은 이 비용이 누적될 때를 말합니다.

### 시스템 콜 비용 비교표

| 시스템 콜 | 대표 비용 | 비용 원인 |
| --- | --- | --- |
| `getpid` (vDSO) | 5~20 ns | 커널 진입 없이 사용자 공간에서 처리 |
| `getpid` (일반) | 100~300 ns | 모드 전환 + 레지스터 저장/복원 |
| `read` (캐시 히트) | 1~5 µs | 커널 버퍼 복사 |
| `read` (디스크) | 50 µs ~ 10 ms | 디스크 I/O 대기 |
| `fsync` | 1~10 ms | 디스크에 물리적으로 플러시 |

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

- `voluntary_ctxt_switches`가 크면 I/O 대기로 자발적으로 CPU를 양보한 횟수가 많은 것 → I/O 바운드
- `nonvoluntary_ctxt_switches`가 크면 타임슬라이스를 다 써서 강제 교체된 횟수 → CPU 바운드
- fd 수가 수천 개이면 파일 디스크립터 누수 가능성

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
|           ↓             |
| stack                   |  함수 호출 프레임
+-------------------------+
| kernel space            |  사용자 접근 불가
높은 주소
```

메모리 문제를 만났을 때 이 그림으로 "어느 영역이 커지는가"를 먼저 고르면 디버깅 범위가 줄어듭니다. 힙이 계속 크면 누수나 캐시 폭증, 스택이 크면 재귀 깊이 문제, bss가 크면 전역 변수 남용을 의심합니다.

```bash
# 현재 프로세스의 메모리 영역별 배치 확인
cat /proc/self/maps
# 또는 더 상세하게
cat /proc/self/smaps | grep -A 12 "\[heap\]"
```

## 처음 질문으로 돌아가기

- **운영체제는 정확히 어떤 문제를 해결하려고 존재할까요?**
  - OS가 없다면 프로그램이 디스크 섹터를 직접 건드리고, 서로의 RAM을 덮어 쓰고, CPU를 독점합니다. OS는 하드웨어 위에 자원 관리자와 추상화 계층을 올려 이 카오스를 정리합니다. 덕분에 응용 프로그램은 하드웨어 차이를 신경 쓰지 않고 논리에 집중할 수 있습니다.
- **커널 모드와 사용자 모드는 왜 굳이 분리되어 있을까요?**
  - 사용자 코드가 하드웨어를 직접 만지면 버그 하나가 시스템 전체를 무너뜨릴 수 있습니다. 커널 모드로의 진입은 시스템 콜이라는 좁은 경로만 허용해, 커널이 모든 접근을 검증하고 조정합니다. 이 분리가 프로세스 격리와 보안의 물리적 기반입니다.
- **프로세스, 파일, 소켓 같은 추상화는 실제로 무엇을 감추고 있을까요?**
  - 파일은 디스크 블록 번호와 inode를 감춥니다. 프로세스는 CPU 레지스터 세트와 가상 주소 공간 매핑을 감춥니다. 소켓은 네트워크 스택과 버퍼 관리를 감춥니다. 추상화 덕분에 응용 프로그램은 하드웨어 차이를 신경 쓰지 않아도 됩니다.

## 연습 문제

1. `strace -c python3 your_script.py`를 실행해서 가장 많이 호출된 시스템 콜 세 개를 적고, 각 호출이 무엇을 하는지 한 문단으로 설명해 보세요.
2. `ulimit -n`으로 파일 디스크립터 한도를 확인한 뒤, 파일을 반복해서 여는 작은 스크립트를 만들어 어떤 에러가 나는지 직접 확인해 보세요.
3. `/proc/self/status`에서 `VmRSS`, `Threads`, `State`를 읽고, 각 필드가 지금 프로세스의 어떤 상태를 말하는지 자기 말로 정리해 보세요.
4. `getpid` 시스템 콜 1백만 회를 타임잇해 보고, 단순 파이썬 덧셈 1백만 회와 비교해 오버헤드가 얼마나 되는지 계산해 보세요.

## 마무리와 다음 글

운영체제는 하드웨어 위에 얹혀 자원을 관리하고, 응용 프로그램에게 깔끔한 추상화를 제공하는 소프트웨어 계층입니다. 사용자 모드와 커널 모드의 분리, 시스템 콜이라는 정해진 통로, 그리고 프로세스라는 추상화 — 이 세 가지가 OS를 이해하는 출발점입니다.

다음 글에서는 OS가 만들어 주는 가장 기본적인 추상화인 프로세스를 자세히 봅니다. 프로세스는 무엇으로 구성되어 있고, 스레드와는 어떻게 다른지, 그리고 새 프로세스는 어떻게 만들어지는지를 따라갑니다.

<!-- toc:begin -->
## 시리즈 목차

- **Operating Systems 101 (1/10): 운영체제란 무엇인가? (현재 글)**
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
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
- [Silberschatz, Galvin, Gagne — Operating System Concepts](https://www.os-book.com/)
- [Linux man-pages project](https://man7.org/linux/man-pages/)
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)

Tags: Computer Science, 운영체제, 시스템, 기초, 커널, 추상화
