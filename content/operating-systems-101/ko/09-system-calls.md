---
series: operating-systems-101
episode: 9
title: "Operating Systems 101 (9/10): 시스템 콜"
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
  - syscall
  - strace
  - 커널
  - 사용자공간
seo_description: 사용자 코드가 커널에 일을 맡기는 시스템 콜의 동작과 비용을 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (9/10): 시스템 콜

사용자 코드가 디스크나 네트워크 카드에 직접 손을 댈 수는 없습니다. 커널 자원을 쓰려면 반드시 좁은 입구를 통과해야 하고, 그 입구가 바로 시스템 콜입니다.

같은 결과를 내는 두 프로그램이 시스템 콜 횟수 때문에 몇 배씩 차이 나는 경우가 흔합니다. 그래서 시스템 콜은 성능과 보안을 함께 읽는 기본 단위입니다.

이 글은 Operating Systems 101 시리즈의 9번째 글입니다.

![Operating Systems 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/09/09-01-the-privilege-boundary-a-syscall-crosses.ko.png)
*Operating Systems 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 사용자 공간과 커널 공간은 무엇이 다를까요?
- 시스템 콜 한 번에는 어떤 전환 비용이 들어갈까요?
- `strace`는 왜 OS 문제를 볼 때 가장 빠른 도구일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 기본 모델

> 사용자 공간은 일반 프로그램이 도는 곳, 커널 공간은 OS의 핵심 코드가 도는 곳입니다. 둘 사이에는 권한 경계가 있고, 사용자 코드는 시스템 콜이라는 좁은 진입점만 통해 커널로 진입합니다. 진입할 때마다 컨텍스트 전환과 보안 검증이 일어나기 때문에 비쌉니다.

### 시스템 콜이 지나가는 권한 경계

```text
[user space]
  print(...) → write(fd, buf, n)  ← syscall entry
                       ↓
                 mode switch (user → kernel)
                       ↓
                 argument check, resource access
                       ↓
                 mode switch (kernel → user)
                       ↓
                 return value
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "한 번에 1바이트씩 쓴다":**

```python
with open('out.bin', 'wb', buffering=0) as f:
    for c in b'A' * 100_000:
        f.write(bytes([c]))     # one syscall each
# 100,000 write syscalls
```

**바꿔서 보면 — "버퍼링으로 묶어 쓴다":**

```python
with open('out.bin', 'wb') as f:    # default buffering
    f.write(b'A' * 100_000)         # effectively one write
```

같은 결과, 호출 횟수는 5자리 수 차이. 시스템 콜은 횟수가 비용입니다.

## 단계별로 확인하기

### 1단계: 시스템 콜 추적 도구로 호출 보기

```bash
strace -c python3 -c "print('hello')"
# Summary: which syscalls were called, how often, total time
```

`-c`는 카운트 요약. `-e trace=open,read,write`로 특정 syscall만 따로 볼 수도 있습니다.

### 2단계: 읽기 크기에 따른 비용 비교

```python
import os, time
fd = os.open('big.bin', os.O_RDONLY)
sizes = [1, 64, 4096, 65536]
for s in sizes:
    os.lseek(fd, 0, 0)
    t = time.time()
    while os.read(fd, s):
        pass
    print(s, time.time() - t)
os.close(fd)
```

작은 read는 syscall 비용이 지배합니다. 보통 4KB~64KB 사이가 sweet spot입니다.

### 3단계: 커널 진입 없는 시간 조회 효과

```python
import time
N = 1_000_000
t = time.time()
for _ in range(N):
    time.time()         # very fast via vDSO
print('time.time x 1M:', time.time() - t)
```

`time.time()`은 매번 syscall로 가지 않고 vDSO를 통해 사용자 공간에서 처리됩니다. 그래서 빠릅니다.

### 4단계: 벡터 입출력으로 시스템 콜 줄이기

```python
import os
fd = os.open('out.bin', os.O_WRONLY | os.O_CREAT, 0o644)
os.writev(fd, [b'header\n', b'body\n', b'footer\n'])    # one syscall
os.close(fd)
```

여러 버퍼를 한 syscall로 처리합니다. 로그 라인 묶어 쓰기 등에 유용합니다.

### 5단계: 보안 필터로 시스템 콜 제한

```bash
# Container runtimes apply a default seccomp profile
docker info | grep -i seccomp
# If ENABLED, processes inside containers can call only an allowed set of syscalls
```

보안 측면에서 syscall은 공격 표면입니다. 필요한 것만 허용하면 익스플로잇 표면이 좁아집니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 작은 단위 read/write | syscall 폭증 | 버퍼링, 배치 |
| 루프 안에서 open/close 반복 | 파일 디스크립터 누수 + 비용 | 파일 한 번 열고 재사용 |
| strace를 운영에서 상시 실행 | 성능 저하 | 짧게 샘플링 |
| 시간 측정에 syscall 가정 | vDSO 무시 | 측정 도구로 실제 비용 확인 |
| 컨테이너에서 모든 syscall 허용 | 보안 위험 | seccomp 프로파일 유지 |

## 실무에서는 이렇게 본다

- 고성능 I/O: io_uring으로 syscall 묶음 처리
- 데이터베이스: writev/sendfile로 syscall 횟수 최소화
- 컨테이너: seccomp + capabilities로 syscall 표면 제한
- 디버깅: strace, ltrace, perf로 syscall 단위 분석
- 모니터링: eBPF로 syscall 트레이스를 실시간 수집

## 운영 체크리스트

- [ ] 사용자 공간과 커널 공간의 차이를 안다
- [ ] strace로 syscall 카운트를 볼 수 있다
- [ ] 버퍼링/배치로 syscall 횟수를 줄여 본 적이 있다
- [ ] vDSO의 의미를 안다
- [ ] seccomp가 보안에 어떻게 기여하는지 안다

## 시스템 관찰: strace 트레이스를 읽는 실전 패턴

### 파일 열기·읽기·닫기 트레이스

아래는 파일 열기 후 읽고 닫는 최소 프로그램의 `strace` 출력 예시입니다.

```text
openat(AT_FDCWD, "data.txt", O_RDONLY) = 3
read(3, "hello\n", 4096)               = 6
read(3, "", 4096)                      = 0
close(3)                                = 0
```

핵심 읽기 포인트:
- fd `3`을 받았고, 표준 입출력(0/1/2) 외 추가 디스크립터를 사용합니다.
- EOF는 `read=0`으로 표현됩니다.
- 음수 반환값은 에러이며 `errno`가 설명합니다.

### 네트워크 서버 트레이스 축약 예시

```text
socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
bind(3, ...) = 0
listen(3, 128) = 0
epoll_wait(5, ..., 1024, 1000) = 4
accept4(3, ...) = 10
read(10, ..., 4096) = 512
write(10, ..., 1024) = 1024
close(10) = 0
```

이 패턴이 보이면 이벤트 루프 기반 서버임을 빠르게 식별할 수 있습니다.

### 호출 횟수 줄이기 전후 비교

```bash
# 버퍼링 없이 1바이트씩 쓸 때
strace -c python3 -c "
f = open('/tmp/t.bin', 'wb', buffering=0)
for _ in range(10000): f.write(b'x')
f.close()
"

# 버퍼링으로 묶어 쓸 때
strace -c python3 -c "
f = open('/tmp/t.bin', 'wb')
f.write(b'x' * 10000)
f.close()
"
```

`write` 시스템 콜 횟수가 10,000 대 수 개로 바뀌고, `System time` 비율도 크게 낮아집니다.

### io_uring — 차세대 비동기 I/O

기존 epoll/select는 준비된 fd를 알려주지만, 각 I/O는 여전히 syscall입니다. io_uring은 ring buffer로 I/O를 배치로 제출해 syscall 횟수를 수십 분의 일로 줄입니다.

```python
# liburing 파이썬 바인딩 예시 (iouringmodule)
# 기본 개념: sqe(제출 큐 엔트리) → cqe(완료 큐 엔트리)
# 여러 I/O를 한 번의 io_uring_enter 호출로 제출
```

## 처음 질문으로 돌아가기

- **사용자 공간과 커널 공간은 무엇이 다를까요?**
  - 사용자 공간은 CPU의 비특권 링(ring 3)에서 실행되어 하드웨어 자원에 직접 접근할 수 없습니다. 커널 공간은 특권 링(ring 0)에서 실행되어 모든 하드웨어를 직접 다룹니다. 이 분리로 사용자 프로그램의 버그가 시스템 전체를 무너뜨리지 않습니다.
- **시스템 콜 한 번에는 어떤 전환 비용이 들어갈까요?**
  - 레지스터 저장, 권한 검증, 스택 전환, 커널 코드 실행, 결과 반환, 레지스터 복원 순으로 진행됩니다. 전환 자체는 약 100~300ns지만, CPU 파이프라인 플러시와 캐시 교란이 추가됩니다. 이것이 syscall 횟수가 누적되면 성능에 영향을 미치는 이유입니다.
- **`strace`는 왜 OS 문제를 볼 때 가장 빠른 도구일까요?**
  - `strace`는 프로그램이 어떤 syscall을 얼마나 자주, 얼마나 오래 호출하는지 실시간으로 보여줍니다. 소스 코드 없이도 "어디서 막히는가"를 정확히 짚을 수 있습니다. `read`가 오래 걸리면 I/O 대기, `futex`가 많으면 락 경합, `open`이 실패하면 권한/경로 문제입니다.

## 연습 문제

1. 같은 데이터를 1B, 4KB, 64KB 단위로 써 보고 `strace -c` 결과와 실행 시간을 비교해 보세요.
2. 지금 서비스에서 자주 호출되는 시스템 콜 하나를 골라, 호출 수를 줄일 수 있는 코드 변경을 제안해 보세요.
3. 컨테이너에서 특정 시스템 콜을 막는 seccomp 프로파일을 만들어 실제로 차단되는지 확인해 보세요.

## 마무리와 다음 글

시스템 콜은 사용자 코드와 커널 사이의 유일한 약속이고, 횟수가 곧 비용입니다. 버퍼링, 배치, vDSO 같은 메커니즘은 같은 의미를 더 싸게 만들고, seccomp는 보안 표면을 좁힙니다. strace는 OS 위 어떤 미스터리든 가장 빠르게 단서를 주는 도구입니다.

다음 글에서는 지금까지 본 OS 기본기가 컨테이너 안에서는 어떻게 다시 조합되는지를 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): 메모리 관리](./06-memory-management.md)
- [Operating Systems 101 (7/10): 가상 메모리](./07-virtual-memory.md)
- [Operating Systems 101 (8/10): 파일 시스템](./08-file-systems.md)
- **Operating Systems 101 (9/10): 시스템 콜 (현재 글)**
- [Operating Systems 101 (10/10): 컨테이너와 운영체제](./10-containers-and-the-os.md)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux strace man page](https://man7.org/linux/man-pages/man1/strace.1.html)
- [Linux syscalls overview](https://man7.org/linux/man-pages/man2/syscalls.2.html)
- [seccomp — Secure Computing Mode](https://man7.org/linux/man-pages/man2/seccomp.2.html)

Tags: Computer Science, 운영체제, syscall, strace, 커널, 사용자공간
