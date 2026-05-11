---
series: operating-systems-101
episode: 1
title: 운영체제란 무엇인가?
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
  - 운영체제
  - 시스템
  - 기초
  - 커널
  - 추상화
seo_description: 운영체제의 정의와 역할, 커널과 사용자 모드, 추상화로서의 OS를 정리합니다.
last_reviewed: '2026-05-04'
---

# 운영체제란 무엇인가?

> Operating Systems 101 시리즈 (1/10)


## 이 글에서 다룰 문제

OS는 평소에 보이지 않습니다. 그래서 문제가 생기기 전까지는 그 존재를 잊기 쉽습니다. 그러나 메모리 부족, 좀비 프로세스, 파일 디스크립터 누수, 갑자기 느려지는 디스크, 막힌 네트워크 — 운영 환경에서 마주치는 거의 모든 시스템 문제는 결국 OS와 어떻게 대화하는지의 문제입니다. OS의 큰 그림을 알면, 에러 메시지가 막연한 "시스템 오류"가 아니라 추적 가능한 신호로 보입니다.

> 응용 프로그램은 OS 위에 얹혀 있고, OS는 하드웨어 위에 얹혀 있습니다. 이 두 경계를 건너는 비용을 모르면 성능도 안정성도 설명할 수 없습니다.

## 전체 흐름
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

## Before / After

**Before — "OS는 그냥 컴퓨터를 켜 주는 것":**

```python
with open("data.txt") as f:
    print(f.read())
```

이 세 줄이 실행되려면, 누군가는 디스크의 어느 블록에 `data.txt`가 있는지 찾고, 디스크 컨트롤러에 명령을 내리고, 결과를 메모리에 옮기고, 그 메모리를 우리 프로세스가 읽을 수 있도록 매핑해야 합니다.

**After — "OS가 매 줄마다 일하고 있다"는 모델:**

```text
open()  → 시스템 콜 → 커널이 파일 시스템에서 inode를 찾고
                    → 파일 디스크립터를 사용자 공간에 돌려줌
read()  → 시스템 콜 → 디스크 드라이버에 I/O 요청
                    → 데이터가 커널 버퍼 → 사용자 버퍼로 복사
print() → 시스템 콜 (write to stdout)
                    → 터미널 디바이스 드라이버로 전달
```

세 줄짜리 파이썬 코드는 사실 시스템 콜의 연속입니다.

## 단계별로 따라하기

### 1단계: 시스템 콜 추적해 보기

```bash
# Linux: strace로 파이썬 한 줄이 만드는 시스템 콜 보기
strace -e trace=openat,read,write,close \
    python3 -c "open('data.txt').read()"
```

실행하면 `openat(AT_FDCWD, "data.txt", O_RDONLY) = 3` 같은 줄이 보입니다. 이 숫자 `3`이 우리가 받은 파일 디스크립터입니다. 실제 디스크 작업은 모두 커널이 합니다.

### 2단계: 사용자 모드와 커널 모드 시간 측정

```bash
# 같은 작업을 user time과 system time으로 분리
/usr/bin/time -v python3 -c "
with open('/etc/hosts') as f:
    for _ in range(100000):
        f.seek(0); f.read()
" 2>&1 | grep -E "User time|System time"
```

`User time`은 우리 코드가 사용자 모드에서 쓴 시간, `System time`은 커널이 우리를 위해 쓴 시간입니다. I/O가 많은 프로그램일수록 `System time`이 늘어납니다.

### 3단계: 프로세스가 OS에게서 받은 자원 확인

```python
import os, resource

print(f"PID            : {os.getpid()}")
print(f"부모 PID        : {os.getppid()}")
print(f"열 수 있는 fd 한계: {resource.getrlimit(resource.RLIMIT_NOFILE)}")
print(f"가상 메모리 한계 : {resource.getrlimit(resource.RLIMIT_AS)}")
```

PID는 OS가 나에게 부여한 식별자, fd 한계와 메모리 한계는 OS가 강제하는 제약입니다. 우리는 OS가 나눠 준 몫 안에서만 살 수 있습니다.

### 4단계: `/proc`로 커널이 우리를 어떻게 보는지 들여다보기

```bash
# 자기 자신의 커널 측 정보
cat /proc/self/status | head -20
# 자기 자신이 열어 둔 파일 디스크립터 목록
ls -l /proc/self/fd
```

리눅스에서 `/proc`는 커널이 가진 정보를 파일처럼 노출하는 가상 파일 시스템입니다. 커널은 우리 프로세스에 대한 메타데이터(상태, 메모리 사용량, 열린 파일)를 모두 알고 있습니다.

### 5단계: OS 없는 세상을 상상해 보기

```text
[OS 없음]                        [OS 있음]
- 모든 앱이 직접 디스크 섹터 접근   - open()/read()로 파일 추상화
- 두 앱이 같은 메모리를 덮어씀       - 가상 메모리로 격리
- 한 앱이 CPU를 영원히 점유          - 스케줄러가 시간 분배
- 디바이스마다 따로 코드 작성        - 드라이버로 단일 인터페이스
```

OS의 가치는 이 둘의 차이입니다. 우리가 평소 느끼는 "그냥 잘 돌아간다"는 감각은 모두 이 추상화 위에 서 있습니다.

## 이 코드에서 주목할 점

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

## 실무에서는 이렇게 쓰입니다

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

## 정리 및 다음 단계

운영체제는 하드웨어 위에 얹혀 자원을 관리하고, 응용 프로그램에게 깔끔한 추상화를 제공하는 소프트웨어 계층입니다. 사용자 모드와 커널 모드의 분리, 시스템 콜이라는 정해진 통로, 그리고 프로세스라는 추상화 — 이 세 가지가 OS를 이해하는 출발점입니다.

다음 글에서는 OS가 만들어 주는 가장 기본적인 추상화인 프로세스를 자세히 봅니다. 프로세스는 무엇으로 구성되어 있고, 스레드와는 어떻게 다른지, 그리고 새 프로세스는 어떻게 만들어지는지를 따라갑니다.

<!-- toc:begin -->
- **운영체제란 무엇인가? (현재 글)**
- 프로세스와 스레드 (예정)
- 스케줄링 (예정)
- 동시성과 race condition (예정)
- lock, mutex, semaphore (예정)
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
