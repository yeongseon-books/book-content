---
series: computer-science-101
episode: 6
title: 운영체제
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
  - 프로세스
  - 스레드
  - 가상 메모리
  - 동시성
seo_description: 운영체제가 프로세스, 스레드, 메모리, 시스템 콜을 어떻게 관리하는지 다루는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-04'
---

# 운영체제

> Computer Science 101 시리즈 (6/10)


## 이 글에서 다룰 문제

웹 서버가 멈추는 이유, 메모리 누수가 OS에 어떻게 보이는지, 멀티스레딩이 항상 빠르지 않은 이유는 모두 운영체제를 이해해야 답할 수 있습니다.

> 운영체제 = 자원 관리자 + 추상화 계층

OS의 추상화를 모르면 디버깅은 마법이 됩니다.

## 개념 한눈에 보기

> 프로세스는 격리된 실행 단위, 스레드는 같은 프로세스 안에서 메모리를 공유하는 실행 흐름입니다.

```text
프로세스 A                       프로세스 B
┌───────────────────┐           ┌───────────────────┐
│ 가상 주소 공간     │           │ 가상 주소 공간     │
│  ┌─────────────┐  │           │  ┌─────────────┐  │
│  │ 스레드 1     │  │           │  │ 스레드 1     │  │
│  │ 스레드 2     │  │           │  │             │  │
│  └─────────────┘  │           │  └─────────────┘  │
└─────────┬─────────┘           └─────────┬─────────┘
          │                               │
          └────── 운영체제 (커널) ────────┘
                       │
                  하드웨어 (CPU, RAM, 디스크)
```

## Before / After

**Before — OS를 의식하지 않은 코드:**

```python
# 100개 URL을 순차적으로 가져오기 — 대부분의 시간을 대기
import urllib.request

urls = [f"https://httpbin.org/delay/1?n={i}" for i in range(100)]
results = [urllib.request.urlopen(u).read() for u in urls]
# 약 100초 — CPU는 거의 놀고 I/O 대기만 합니다
```

**After — OS의 비동기 I/O를 활용:**

```python
# 같은 작업, 동시에 처리 — I/O 대기 시간을 겹치게 합니다
from concurrent.futures import ThreadPoolExecutor
import urllib.request

def fetch(url: str) -> bytes:
    return urllib.request.urlopen(url).read()


with ThreadPoolExecutor(max_workers=20) as pool:
    results = list(pool.map(fetch, urls))
# 약 5~10초 — I/O 대기 동안 다른 요청이 진행됩니다
```

## 실습: 단계별로 따라하기

### 1단계: 프로세스와 스레드 만들어 보기

```python
import os
import threading
import multiprocessing


def show_id(label: str) -> None:
    print(f"{label}: pid={os.getpid()}, tid={threading.get_ident()}")


print("[메인]")
show_id("main")

print("\n[스레드]")
t = threading.Thread(target=show_id, args=("thread",))
t.start()
t.join()

print("\n[프로세스]")
p = multiprocessing.Process(target=show_id, args=("process",))
p.start()
p.join()
```

### 2단계: GIL과 멀티스레딩의 한계

```python
# CPU 바운드 작업은 스레드로 빨라지지 않습니다 (CPython의 GIL)
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
print(f"순차       : {time.perf_counter() - start:.2f}s")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_heavy, work))
print(f"스레드 x4 : {time.perf_counter() - start:.2f}s")  # 거의 비슷합니다

start = time.perf_counter()
with ProcessPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_heavy, work))
print(f"프로세스 x4: {time.perf_counter() - start:.2f}s")  # 약 4배 빨라집니다
```

### 3단계: 시스템 콜 들여다보기

```python
# Python의 open()은 내부적으로 OS의 open(2) 시스템 콜을 호출합니다
import os

fd = os.open("/tmp/oscourse_demo.txt", os.O_CREAT | os.O_WRONLY, 0o644)
os.write(fd, b"Hello from a system call\n")
os.close(fd)

print(open("/tmp/oscourse_demo.txt").read())
os.remove("/tmp/oscourse_demo.txt")
```

### 4단계: 가상 메모리 관찰하기

```python
# 프로세스의 메모리 사용량 확인 (Linux/macOS)
import os
import resource

print(f"PID            : {os.getpid()}")
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"max RSS (KB)   : {usage.ru_maxrss}")    # 사용한 최대 물리 메모리
print(f"page faults    : {usage.ru_minflt}")    # 페이지 부재 횟수
```

### 5단계: 동시성 vs 병렬성

```python
# 동시성 = 여러 작업이 진행 중인 상태 (시간 분할 가능)
# 병렬성 = 여러 작업이 같은 순간에 실행되는 상태 (다중 CPU 코어)

import asyncio
import time


async def task(name: str, sec: float) -> None:
    print(f"{name} 시작")
    await asyncio.sleep(sec)        # I/O 대기 시뮬레이션
    print(f"{name} 종료")


async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(task("A", 1), task("B", 1), task("C", 1))
    print(f"총 소요: {time.perf_counter() - start:.2f}s")  # 약 1초


asyncio.run(main())
```

## 이 코드에서 주목할 점

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

## 체크리스트

- [ ] 프로세스와 스레드의 차이를 메모리 관점에서 설명할 수 있는가
- [ ] CPython GIL이 무엇이고 어떤 작업에 영향을 주는지 아는가
- [ ] 가상 메모리, 페이지, 스왑의 의미를 이해했는가
- [ ] 시스템 콜이 비용이 있다는 점을 의식하는가
- [ ] 동시성과 병렬성을 구분해서 사용할 수 있는가

## 정리 및 다음 단계

운영체제는 하드웨어를 추상화해 여러 프로그램이 안전하게 공존하도록 만듭니다. 프로세스·스레드·가상 메모리·시스템 콜은 우리가 작성하는 모든 코드의 무대입니다. 동시성 모델은 작업의 성격(CPU/I/O)에 맞게 골라야 합니다.

다음 글에서는 한 컴퓨터를 넘어 여러 컴퓨터가 데이터를 주고받는 방식 — 네트워크 — 를 다룹니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- **운영체제 (현재 글)**
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [Operating Systems: Three Easy Pieces (무료)](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Python — concurrent.futures 문서](https://docs.python.org/3/library/concurrent.futures.html)
- [Linux man-pages — system calls](https://man7.org/linux/man-pages/dir_section_2.html)
- [Andrew Tanenbaum — Modern Operating Systems](https://www.pearson.com/en-us/subject-catalog/p/modern-operating-systems/P200000003311)

Tags: Computer Science, 운영체제, 프로세스, 스레드, 가상 메모리, 동시성
