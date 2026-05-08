
# 시스템 콜

> Operating Systems 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 사용자 코드는 어떤 경로로 커널의 자원(파일, 네트워크, 프로세스)을 사용하고, 그 경로의 비용은 얼마일까요?

> 사용자 코드는 디스크나 네트워크 카드를 직접 만지지 않습니다. 모든 요청은 시스템 콜이라는 좁은 문을 통과해 커널로 들어갑니다. 이 문은 안전하지만 비쌉니다. 시스템 콜이 무엇이고 왜 비싼지 알면, 같은 일을 하는 두 코드 중 어느 쪽이 빠를지 미리 보입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 사용자 공간과 커널 공간의 분리
- 시스템 콜이 호출되고 돌아오는 과정
- strace로 실제 시스템 콜을 관찰하기
- 시스템 콜 비용을 줄이는 패턴 — 버퍼링, 배치, vDSO

## 왜 중요한가

같은 데이터를 100MB 처리하는 두 프로그램이 시스템 콜 호출 횟수만 다르면 수 배 빠르거나 느려집니다. 또한 컨테이너의 보안(seccomp), 디버깅(strace), 성능 분석(perf)은 모두 시스템 콜 단위로 이루어집니다. 시스템 콜을 모르면 OS 위에서 일어나는 일의 절반은 보이지 않습니다.

> 시스템 콜은 사용자 코드와 커널 사이의 유일한 약속이고, 그 약속의 횟수와 비용이 시스템의 성능을 결정합니다.

## 개념 한눈에 보기

> 사용자 공간은 일반 프로그램이 도는 곳, 커널 공간은 OS의 핵심 코드가 도는 곳입니다. 둘 사이에는 권한 경계가 있고, 사용자 코드는 시스템 콜이라는 좁은 진입점만 통해 커널로 진입합니다. 진입할 때마다 컨텍스트 전환과 보안 검증이 일어나기 때문에 비쌉니다.

```text
[사용자 공간]
  print(...) → write(fd, buf, n)  ← 시스템 콜 진입
                       ↓
                 모드 전환 (user → kernel)
                       ↓
                 인자 검증, 자원 접근
                       ↓
                 모드 전환 (kernel → user)
                       ↓
                 결과 반환
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 사용자 공간 | 일반 애플리케이션이 도는 메모리/권한 영역 |
| 커널 공간 | OS 핵심 코드가 도는 영역, 직접 접근 불가 |
| 시스템 콜 | 사용자 코드가 커널에 요청을 보내는 유일한 진입점 |
| 컨텍스트 전환 | 모드 전환 시 레지스터/페이지 테이블 등을 바꾸는 비용 |
| vDSO | 자주 쓰는 syscall(예: gettimeofday)을 사용자 공간에서 처리해 비용 절감 |

## Before / After

**Before — "한 번에 1바이트씩":**

```python
with open('out.bin', 'wb', buffering=0) as f:
    for c in b'A' * 100_000:
        f.write(bytes([c]))     # 매번 write syscall
# 100,000번의 write syscall
```

**After — "버퍼링":**

```python
with open('out.bin', 'wb') as f:    # 기본 버퍼 사용
    f.write(b'A' * 100_000)         # 사실상 1번의 write
```

같은 결과, 호출 횟수는 5자리 수 차이. 시스템 콜은 횟수가 비용입니다.

## 실습: 단계별로 따라하기

### 1단계: strace로 시스템 콜 보기

```bash
strace -c python3 -c "print('hello')"
# 어떤 syscall이 몇 번 호출되었고 총 시간을 얼마 썼는지 요약
```

`-c`는 카운트 요약. `-e trace=open,read,write`로 특정 syscall만 따로 볼 수도 있습니다.

### 2단계: read 한 번에 얼마나 읽어야 효율적인가

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

### 3단계: vDSO 효과 — gettimeofday

```python
import time
N = 1_000_000
t = time.time()
for _ in range(N):
    time.time()         # vDSO를 통해 매우 빠름
print('time.time x 1M:', time.time() - t)
```

`time.time()`은 매번 syscall로 가지 않고 vDSO를 통해 사용자 공간에서 처리됩니다. 그래서 빠릅니다.

### 4단계: 시스템 콜을 줄이는 readv/writev

```python
import os
fd = os.open('out.bin', os.O_WRONLY | os.O_CREAT, 0o644)
os.writev(fd, [b'header\n', b'body\n', b'footer\n'])    # 1번의 syscall
os.close(fd)
```

여러 버퍼를 한 syscall로 처리. 로그 라인 묶어 쓰기 등에 유용합니다.

### 5단계: seccomp로 syscall 제한

```bash
# 컨테이너 런타임은 기본적으로 seccomp 필터를 적용합니다
docker info | grep -i seccomp
# ENABLED 면 컨테이너 안의 프로세스가 호출할 수 있는 syscall이 제한됨
```

보안 측면에서 syscall은 공격 표면입니다. 필요한 것만 허용하면 익스플로잇 표면이 좁아집니다.

## 이 코드에서 주목할 점

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

## 실무에서는 이렇게 쓰입니다

- 고성능 I/O: io_uring으로 syscall 묶음 처리
- 데이터베이스: writev/sendfile로 syscall 횟수 최소화
- 컨테이너: seccomp + capabilities로 syscall 표면 제한
- 디버깅: strace, ltrace, perf로 syscall 단위 분석
- 모니터링: eBPF로 syscall 트레이스를 실시간 수집

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 성능 문제가 보고되면 먼저 syscall 횟수와 종류를 확인합니다. CPU나 메모리 그래프보다 빠르게 "어디서 시간이 새는지"를 알려주는 신호이기 때문입니다. strace 한 줄로 풀리는 미스터리가 운영에는 정말 많습니다.

또한 시니어는 보안 관점에서 syscall을 자원으로 봅니다. 모든 syscall이 필요한 프로세스는 거의 없습니다. seccomp로 필요한 것만 허용하면 같은 코드의 공격 표면을 한 자릿수 단위로 줄일 수 있습니다. 성능과 보안 둘 다, syscall은 최적화의 출발점입니다.

## 체크리스트

- [ ] 사용자 공간과 커널 공간의 차이를 안다
- [ ] strace로 syscall 카운트를 볼 수 있다
- [ ] 버퍼링/배치로 syscall 횟수를 줄여 본 적이 있다
- [ ] vDSO의 의미를 안다
- [ ] seccomp가 보안에 어떻게 기여하는지 안다

## 연습 문제

1. 같은 데이터를 1바이트, 4KB, 64KB로 나눠 쓰는 세 코드의 strace 카운트와 시간을 비교하세요. 결과를 한 문단으로 정리합니다.

2. 자주 호출되는 syscall 한 가지를 골라 strace -c로 빈도를 측정하고, 줄일 수 있는 코드 변경을 제안하세요.

3. seccomp 프로파일을 직접 작성해 컨테이너 안에서 특정 syscall(예: ptrace)을 차단해 보세요.

## 정리 및 다음 단계

시스템 콜은 사용자 코드와 커널 사이의 유일한 약속이고, 횟수가 곧 비용입니다. 버퍼링, 배치, vDSO 같은 메커니즘은 같은 의미를 더 싸게 만들고, seccomp는 보안 표면을 좁힙니다. strace는 OS 위 어떤 미스터리든 가장 빠르게 단서를 주는 도구입니다.

다음 글에서는 지금까지 본 OS 기본기가 컨테이너 안에서는 어떻게 다시 조합되는지를 봅니다.

- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 race condition](./04-concurrency-and-race-conditions.md)
- [lock, mutex, semaphore](./05-locks-mutex-semaphore.md)
- [메모리 관리](./06-memory-management.md)
- [가상 메모리](./07-virtual-memory.md)
- [파일 시스템](./08-file-systems.md)
- **시스템 콜 (현재 글)**
- 컨테이너와 운영체제 (예정)
## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux strace man page](https://man7.org/linux/man-pages/man1/strace.1.html)
- [Linux syscalls overview](https://man7.org/linux/man-pages/man2/syscalls.2.html)
- [seccomp — Secure Computing Mode](https://man7.org/linux/man-pages/man2/seccomp.2.html)

Tags: Computer Science, 운영체제, syscall, strace, 커널, 사용자공간

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
