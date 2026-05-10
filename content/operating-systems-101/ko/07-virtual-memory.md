---
series: operating-systems-101
episode: 7
title: 가상 메모리
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
  - 가상메모리
  - paging
  - TLB
  - swap
seo_description: 페이지, 페이지 테이블, TLB, swap, page fault — OS가 한정된 RAM을 무한히 큰 것처럼 보이게 만드는 원리를 정리합니다.
last_reviewed: '2026-05-04'
---

# 가상 메모리

> Operating Systems 101 시리즈 (7/10)


## 이 글에서 다룰 문제

가상 메모리를 모르면 "RSS는 작은데 시스템이 느려진다"거나 "swap이 차오르면서 응답이 폭락한다" 같은 현상을 진단할 수 없습니다. 또한 mmap, fork, copy-on-write 같은 강력한 기능은 가상 메모리 위에서 동작합니다. 가상 메모리는 OS가 자원을 가장 우아하게 다루는 부분이고, 동시에 가장 비싼 실수가 일어나는 곳입니다.

> 가상 메모리는 공짜가 아닙니다. 환상은 page fault라는 청구서를 통해 정확히 비용으로 청구됩니다.

## 개념 한눈에 보기

> 모든 프로세스는 자신만의 가상 주소 공간을 가집니다. 가상 주소는 페이지 단위(보통 4KB)로 잘려 페이지 테이블을 통해 물리 주소로 매핑됩니다. CPU는 이 변환을 빠르게 하기 위해 TLB라는 캐시를 가집니다. 매핑이 없거나 페이지가 디스크에 있으면 page fault가 발생합니다.

```text
가상 주소  →  [TLB hit]  →  물리 주소  →  RAM
                ↓ miss
            페이지 테이블 walk
                ↓ not present
            page fault → OS가 처리 (디스크에서 읽기 / 새 페이지 할당)
```

## Before / After

**Before — "RSS만 보면 충분":**

```bash
ps -o pid,rss,cmd -p $$
# 답이 안 보임. 같은 RSS인데 어떤 프로세스는 빠르고 어떤 건 느림
```

**After — "page fault와 TLB miss를 함께 보기":**

```bash
# major fault = 디스크 접근 (느림)
ps -o pid,min_flt,maj_flt,rss,cmd -p $$
# major fault가 쌓이면 swap-in 의심
```

같은 RSS여도 page fault 패턴이 다르면 체감 속도가 다릅니다.

## 실습: 단계별로 따라하기

### 1단계: page fault 카운트 보기

```bash
python3 -c "
import resource
r = resource.getrusage(resource.RUSAGE_SELF)
print('minor faults', r.ru_minflt)
print('major faults', r.ru_majflt)
"
```

minor fault는 RAM에서 새 페이지를 잡는 비용, major fault는 디스크에서 읽어오는 비용입니다. major가 늘면 swap 의심.

### 2단계: mmap으로 큰 파일 읽기

```python
import mmap, os

with open('big.bin', 'wb') as f:
    f.write(b'A' * (10 * 1024 * 1024))     # 10MB

with open('big.bin', 'rb') as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        print(mm[0:10])                     # 필요한 부분만 페이지 단위로 로드
```

mmap은 파일을 가상 메모리로 직접 매핑합니다. 실제 접근하는 페이지만 RAM에 올라와 큰 파일을 메모리처럼 다룰 수 있습니다.

### 3단계: copy-on-write 관찰 (fork)

```python
import os, time

big = bytearray(100 * 1024 * 1024)          # 100MB
pid = os.fork()
if pid == 0:                                 # child
    # 부모와 같은 페이지를 공유 (CoW)
    big[0] = 1                               # 쓰는 순간 페이지 복제 발생
    time.sleep(2)
    os._exit(0)
else:
    os.waitpid(pid, 0)
```

`fork`는 페이지를 즉시 복사하지 않고, 쓰기가 일어날 때만 복사합니다. 메모리를 거의 안 쓰고 자식 프로세스를 만들 수 있는 핵심 기법입니다.

### 4단계: swap 사용량 보기

```bash
free -h
swapon --show
# 또는
cat /proc/swaps
```

swap이 사용되고 있고 응답 시간이 폭락 중이라면 RAM 부족이거나 working set이 RAM을 초과한 것입니다.

### 5단계: 큰 배열 접근 패턴과 TLB

```python
import time
N = 5000
m = [[0]*N for _ in range(N)]

t = time.time()
for i in range(N):
    for j in range(N):
        m[i][j] = 1                          # 행 우선 — 페이지 지역성 좋음
print('row-major', time.time() - t)

t = time.time()
for j in range(N):
    for i in range(N):
        m[i][j] = 1                          # 열 우선 — TLB/캐시 미스 폭증
print('col-major', time.time() - t)
```

같은 데이터, 같은 횟수, 다른 접근 패턴 — 결과는 수 배 차이 납니다. 가상 메모리의 비용은 접근 패턴이 결정합니다.

## 이 코드에서 주목할 점

- mmap은 파일 I/O를 메모리 접근으로 바꿉니다 — 큰 데이터에 자연스러운 추상화
- copy-on-write는 fork를 가볍게 만드는 핵심 기법입니다
- swap이 보이기 시작하면 응답 시간은 이미 무너지고 있습니다
- 같은 RSS여도 접근 지역성에 따라 체감 속도가 크게 달라집니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| RSS만 보고 메모리 판단 | swap, page fault 무시 | major fault, swap 사용량 같이 모니터링 |
| 큰 파일을 모두 read | OOM 또는 swap | mmap 또는 chunk 스트리밍 |
| fork 후 즉시 큰 데이터 수정 | CoW 무력화, 메모리 폭증 | exec 직전까지 쓰기 최소화 |
| 접근 지역성 무시 | TLB miss 폭증 | 데이터 구조와 루프 순서를 함께 설계 |
| swap on이면 안전 | 사실 응답 시간 폭락 | 운영 시스템에서는 swap을 끄거나 최소화 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스: mmap으로 인덱스/페이지 캐시
- 컨테이너: cgroup memory + swap 설정으로 OOM 동작 제어
- ML 학습: 큰 배열은 mmap-backed numpy로 메모리 압박 완화
- 백엔드: fork 기반 워커 모델 (gunicorn, uwsgi)에서 CoW 활용
- 성능 튜닝: perf 등으로 TLB miss / page fault 측정

## 체크리스트

- [ ] 가상 주소와 물리 주소의 차이를 안다
- [ ] minor fault와 major fault의 비용 차이를 안다
- [ ] mmap이 언제 유용한지 안다
- [ ] copy-on-write의 의미를 설명할 수 있다
- [ ] swap이 보이기 시작하면 위험 신호임을 안다

## 정리 및 다음 단계

가상 메모리는 OS가 만든 환상이지만, page fault와 swap이라는 청구서로 정확히 비용을 회수합니다. mmap과 copy-on-write 같은 기법은 이 환상을 응용해 큰 데이터를 우아하게 다룹니다. 가상 메모리를 알면 시스템이 굳는 순간을 짚어낼 수 있습니다.

다음 글에서는 OS가 메모리만큼이나 자주 다루는 자원 — 파일 시스템으로 넘어갑니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 race condition](./04-concurrency-and-race-conditions.md)
- [lock, mutex, semaphore](./05-locks-mutex-semaphore.md)
- [메모리 관리](./06-memory-management.md)
- **가상 메모리 (현재 글)**
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Linux mmap(2) man page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [Python mmap](https://docs.python.org/3/library/mmap.html)

Tags: Computer Science, 운영체제, 가상메모리, paging, TLB, swap
