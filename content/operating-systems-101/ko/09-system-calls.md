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

## 먼저 던지는 질문

- 사용자 공간과 커널 공간은 무엇이 다를까요?
- 시스템 콜 한 번에는 어떤 전환 비용이 들어갈까요?
- `strace`는 왜 OS 문제를 볼 때 가장 빠른 도구일까요?

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

여러 버퍼를 한 syscall로 처리. 로그 라인 묶어 쓰기 등에 유용합니다.

### 5단계: 보안 필터로 시스템 콜 제한

```bash
# Container runtimes apply a default seccomp profile
docker info | grep -i seccomp
# If ENABLED, processes inside containers can call only an allowed set of syscalls
```

보안 측면에서 syscall은 공격 표면입니다. 필요한 것만 허용하면 익스플로잇 표면이 좁아집니다.

## 여기서 먼저 볼 점

- 시스템 콜은 횟수가 비용이고, 버퍼링/배치로 횟수를 줄이는 것이 첫 번째 최적화
- vDSO 같은 메커니즘은 같은 의미를 가진 syscall을 더 싸게 만듭니다
- strace는 "어디서 시간을 쓰는지" 모를 때 가장 빨리 단서를 주는 도구
- seccomp 같은 syscall 필터는 보안의 기본 도구입니다

## 자주 하는 실수 5가지

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

## 체크리스트

- [ ] 사용자 공간과 커널 공간의 차이를 안다
- [ ] strace로 syscall 카운트를 볼 수 있다
- [ ] 버퍼링/배치로 syscall 횟수를 줄여 본 적이 있다
- [ ] vDSO의 의미를 안다
- [ ] seccomp가 보안에 어떻게 기여하는지 안다

## 연습 문제

1. 같은 데이터를 1B, 4KB, 64KB 단위로 써 보고 `strace -c` 결과와 실행 시간을 비교해 보세요.
2. 지금 서비스에서 자주 호출되는 시스템 콜 하나를 골라, 호출 수를 줄일 수 있는 코드 변경을 제안해 보세요.
3. 컨테이너에서 특정 시스템 콜을 막는 seccomp 프로파일을 만들어 실제로 차단되는지 확인해 보세요.

## 마무리와 다음 글

시스템 콜은 사용자 코드와 커널 사이의 유일한 약속이고, 횟수가 곧 비용입니다. 버퍼링, 배치, vDSO 같은 메커니즘은 같은 의미를 더 싸게 만들고, seccomp는 보안 표면을 좁힙니다. strace는 OS 위 어떤 미스터리든 가장 빠르게 단서를 주는 도구입니다.

다음 글에서는 지금까지 본 OS 기본기가 컨테이너 안에서는 어떻게 다시 조합되는지를 봅니다.

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

### 운영 트러블슈팅 미니 시나리오
실무에서 자주 보는 상황은 "요청량은 비슷한데 지연이 갑자기 증가"하는 경우입니다. 이때 애플리케이션 로그만 보면 원인이 흐려질 수 있으므로, 커널 관점 지표를 먼저 확인하는 편이 정확합니다. 메모리 글에서는 page fault와 swap 동향을 보고 워킹셋 이탈 여부를 판단하고, 파일시스템 글에서는 fsync 빈도와 디스크 큐 대기시간을 함께 봐서 쓰기 경합을 확인하고, 시스템 콜 글에서는 `strace -c`로 호출 분포를 잡아 과도한 모드 전환을 식별합니다. 이 절차를 표준화해 두면 장애 초기에 원인 후보를 빠르게 줄일 수 있습니다.

## 시스템 콜 트레이스를 읽는 실전 예시

아래는 파일 열기 후 읽고 닫는 최소 프로그램의 `strace` 예시입니다.

```text
openat(AT_FDCWD, "data.txt", O_RDONLY) = 3
read(3, "hello
", 4096)               = 6
read(3, "", 4096)                      = 0
close(3)                                = 0
```

이 네 줄에서 확인할 수 있는 핵심은 다음과 같습니다.
- fd `3`을 받았고, 표준 입출력(0/1/2) 외 추가 디스크립터를 사용합니다.
- EOF는 `read=0`으로 표현됩니다.
- 정상 경로에서는 `errno` 없이 0을 반환합니다.

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

### 호출 횟수 줄이기 전후 비교 포인트

- `write`를 한 줄마다 호출: 호출 횟수 급증, 시스템 시간 증가
- `writev`로 배치: 호출 횟수 감소, 처리량 상승
- `sendfile` 사용: 사용자 공간 복사 감소

운영에서는 `strace -c`와 애플리케이션 p95 지연시간을 같은 시점에 비교하면 개선 효과를 명확하게 검증할 수 있습니다.

## 처음 질문으로 돌아가기

- **사용자 공간과 커널 공간은 무엇이 다를까요?**
  - 사용자 공간은 일반 프로그램이 제한된 권한으로 실행되는 영역이고, 커널 공간은 파일시스템·메모리·네트워크 같은 핵심 자원을 직접 제어하는 영역입니다. `write(fd, buf, n)` 한 번에도 사용자 모드에서 커널 모드로 넘어가 인자 검증과 자원 접근을 한 뒤 다시 돌아오므로, 둘 사이에는 명확한 권한 경계가 있습니다.
- **시스템 콜 한 번에는 어떤 전환 비용이 들어갈까요?**
  - 시스템 콜마다 모드 전환, 컨텍스트 저장·복원, 인자 검사, 커널 내부 작업이 따라붙기 때문에 횟수가 많아질수록 시스템 시간이 빠르게 늘어납니다. 1바이트씩 100,000번 `write`하는 예제와 `writev`·버퍼링 예제를 비교하면, 같은 결과라도 호출 수를 줄이는 것이 왜 첫 번째 최적화인지 분명해집니다.
- **`strace`는 왜 OS 문제를 볼 때 가장 빠른 도구일까요?**
  - `strace`는 프로그램이 커널에 무엇을 몇 번 요청했고 어디서 시간을 썼는지를 시스템 콜 단위로 바로 보여 줍니다. `openat`-`read`-`close` 예시로 파일 경로를, `socket`-`bind`-`epoll_wait`-`accept4` 예시로 이벤트 루프 서버 구조를 즉시 읽어낼 수 있어서, OS 경계 문제를 추적할 때 가장 빠른 출발점이 됩니다.

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
- **시스템 콜 (현재 글)**
- 컨테이너와 운영체제 (예정)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux strace man page](https://man7.org/linux/man-pages/man1/strace.1.html)
- [Linux syscalls overview](https://man7.org/linux/man-pages/man2/syscalls.2.html)
- [seccomp — Secure Computing Mode](https://man7.org/linux/man-pages/man2/seccomp.2.html)

Tags: Computer Science, 운영체제, syscall, strace, 커널, 사용자공간
