---
series: operating-systems-101
episode: 1
title: 운영체제란 무엇인가?
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
  - 시스템
  - 기초
  - 커널
  - 추상화
seo_description: 운영체제의 정의와 역할, 커널과 사용자 모드, 핵심 추상화를 정리합니다.
last_reviewed: '2026-05-12'
---

# 운영체제란 무엇인가?

운영체제를 처음 배우면 보통 커널, 시스템 콜, 드라이버 같은 용어부터 만납니다. 그런데 운영 환경에서 더 자주 마주치는 질문은 따로 있습니다. 왜 같은 코드가 어떤 서버에서는 느리고, 어떤 환경에서는 파일을 못 열고, 어떤 순간에는 메모리 부족으로 죽는가입니다.

이 질문을 풀려면 운영체제를 교과서 속 배경지식이 아니라, 매 순간 CPU·메모리·디스크를 대신 조정하는 실행 환경으로 봐야 합니다. 이 글에서는 그 출발점을 잡겠습니다.

이 글은 Operating Systems 101 시리즈의 1번째 글입니다.

## 이 글에서 다룰 문제

- 운영체제는 정확히 어떤 문제를 해결하려고 존재할까요?
- 커널 모드와 사용자 모드는 왜 굳이 분리되어 있을까요?
- 프로세스, 파일, 소켓 같은 추상화는 실제로 무엇을 감추고 있을까요?
- 개발자가 운영체제를 이해하면 장애 대응이 왜 쉬워질까요?

> 운영체제는 하드웨어와 응용 프로그램 사이에 끼어 있는 단순한 중계층이 아닙니다. 여러 프로그램이 같은 CPU, 메모리, 디스크, 네트워크를 안전하게 나눠 쓰게 만들고, 그 복잡함을 프로세스·파일·소켓 같은 추상화로 감싸는 조정 계층입니다.

## 기본 모델
> 운영체제는 사용자 프로그램과 하드웨어 사이에 위치하는 소프트웨어 계층입니다. 위로는 응용 프로그램에게 시스템 콜을 통해 단순한 인터페이스를 제공하고, 아래로는 CPU 스케줄링, 메모리 할당, 디바이스 드라이버, 파일 시스템을 통해 하드웨어를 직접 다룹니다.

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

## 마무리와 다음 글

운영체제는 하드웨어 위에 얹혀 자원을 관리하고, 응용 프로그램에게 깔끔한 추상화를 제공하는 소프트웨어 계층입니다. 사용자 모드와 커널 모드의 분리, 시스템 콜이라는 정해진 통로, 그리고 프로세스라는 추상화 — 이 세 가지가 OS를 이해하는 출발점입니다.

다음 글에서는 OS가 만들어 주는 가장 기본적인 추상화인 프로세스를 자세히 봅니다. 프로세스는 무엇으로 구성되어 있고, 스레드와는 어떻게 다른지, 그리고 새 프로세스는 어떻게 만들어지는지를 따라갑니다.

<!-- toc:begin -->
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

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Silberschatz, Galvin, Gagne — Operating System Concepts](https://www.os-book.com/)
- [Linux man-pages project](https://man7.org/linux/man-pages/)
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)

Tags: Computer Science, 운영체제, 시스템, 기초, 커널, 추상화
