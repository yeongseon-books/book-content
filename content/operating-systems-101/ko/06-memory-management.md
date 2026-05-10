---
series: operating-systems-101
episode: 6
title: 메모리 관리
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
  - 메모리
  - heap
  - stack
  - allocator
seo_description: stack과 heap, malloc과 free, 메모리 누수와 단편화, 그리고 OS가 RAM을 어떻게 나누는지를 정리합니다.
last_reviewed: '2026-05-04'
---

# 메모리 관리

> Operating Systems 101 시리즈 (6/10)


## 이 글에서 다룰 문제

서버가 "어느 순간부터 느려진다"는 증상의 가장 흔한 원인은 메모리 누수, OOM 직전의 GC 폭주, 잘못된 캐시 크기입니다. 메모리 동작을 모르면 CPU 그래프만 들여다봐도 답이 안 보입니다. 메모리는 보이지 않는 자원이지만, 한계에 닿는 순간 가장 시끄러운 자원입니다.

> 메모리 관리는 "할당"보다 "회수"가 어렵습니다. 회수의 책임이 누구에게 있는지가 시스템 설계의 핵심입니다.

## 개념 한눈에 보기

> 프로세스 메모리는 크게 네 영역으로 나뉩니다. 코드(text), 전역 변수(data/bss), heap, stack. heap은 동적 할당, stack은 함수 호출에 따라 자동으로 자라고 줄어듭니다. OS는 가상 주소를 줘서 모든 프로세스가 자신만의 메모리를 가진 것처럼 보이게 합니다.

```text
높은 주소
+---------+
|  stack  |  ← 함수 호출/지역 변수, 자동 정리
|    ↓    |
|         |
|    ↑    |
|  heap   |  ← malloc/new로 할당, 명시적 또는 GC로 정리
+---------+
| bss/data|  ← 전역/정적 변수
| text    |  ← 실행 코드
낮은 주소
```

## Before / After

**Before — "메모리는 무한":**

```python
cache = {}
def handle(req):
    cache[req.id] = expensive(req)   # 영원히 쌓임
    return cache[req.id]
```

며칠 후 OOM. 누수는 명시적 free가 없는 GC 언어에서도 똑같이 발생합니다.

**After — "회수 정책을 명시":**

```python
from functools import lru_cache

@lru_cache(maxsize=10_000)
def handle(req_id):
    return expensive(req_id)
```

상한과 회수 정책이 명시되어 있으면 누수가 아닙니다.

## 실습: 단계별로 따라하기

### 1단계: 프로세스 메모리 사용량 보기

```bash
python3 -c "
import os, resource
print('PID', os.getpid())
print('peak RSS (KB)', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
"
```

`ru_maxrss`는 프로세스가 실제로 점유한 RAM의 최대값입니다.

### 2단계: 누수 만들어 보기

```python
import resource, gc

def show():
    print('RSS', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

leak = []
for i in range(5):
    leak.extend([0] * 1_000_000)
    gc.collect()
    show()
```

GC가 있어도, 참조가 살아 있으면 회수되지 않습니다. 메모리는 GC가 아니라 참조가 결정합니다.

### 3단계: 단편화 관찰

```python
# 큰 블록 + 작은 블록을 번갈아 할당/해제
xs = []
for i in range(1000):
    xs.append(bytearray(1024 * 1024))   # 1MB
for i in range(0, 1000, 2):
    xs[i] = None                        # 짝수만 해제

# 빈 공간은 ~500MB 있지만 연속 1GB 블록은 잡기 어려움
```

총량은 충분한데 연속 공간이 부족한 상태가 단편화입니다.

### 4단계: 약한 참조로 누수 회피

```python
import weakref

class Conn: pass

pool = weakref.WeakValueDictionary()
def get(name):
    c = pool.get(name)
    if c is None:
        c = Conn(); pool[name] = c
    return c
```

`WeakValueDictionary`는 외부 참조가 사라지면 자동으로 항목을 제거합니다.

### 5단계: 컨테이너 메모리 한도 보기

```bash
# Docker 컨테이너의 메모리 한도와 사용량
cat /sys/fs/cgroup/memory.max 2>/dev/null || echo 'not in container'
cat /sys/fs/cgroup/memory.current 2>/dev/null || echo 'not in container'
```

컨테이너에서는 cgroup이 부모 OS와 별개로 한도를 강제합니다. 한도를 모르고 캐시를 키우면 OOM-kill됩니다.

## 이 코드에서 주목할 점

- 가비지 컬렉션은 "참조가 끊긴" 객체만 회수합니다
- 누수는 "안 쓰는데 참조가 살아 있는" 상태에서 만들어집니다
- 단편화는 총량이 아니라 "연속 공간"의 문제입니다
- 약한 참조와 회수 정책(LRU 등)은 누수의 가장 흔한 처방입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 무제한 캐시 | OOM | 상한과 회수 정책 명시(LRU 등) |
| 글로벌 리스트에 무한 append | 누수 | 약한 참조 또는 만료 시간 |
| 큰 객체를 클로저에 캡처 | 회수 안 됨 | 필요한 값만 추출해 캡처 |
| 컨테이너 한도 무시 | OOM-kill | cgroup 한도 기준으로 캐시/풀 설정 |
| GC 언어니까 안전 | 누수 가능 | 참조 그래프를 의식적으로 설계 |

## 실무에서는 이렇게 쓰입니다

- 캐시: 항상 상한과 회수 정책이 함께 정의됨
- 백엔드: 워커당 메모리 한도 + OOM 방어선
- 데이터 처리: chunk 단위 스트리밍으로 peak RSS 제한
- 게임/임베디드: 풀 할당으로 단편화 회피
- 컨테이너: cgroup 한도를 기준으로 capacity 계획

## 체크리스트

- [ ] 프로세스 메모리 영역(text/data/heap/stack)을 안다
- [ ] 누수와 단편화의 차이를 안다
- [ ] 캐시에 capacity와 eviction policy를 둘 다 적는다
- [ ] 컨테이너에서는 cgroup 한도를 의식한다
- [ ] RSS 추세를 모니터링 대상에 넣는다

## 정리 및 다음 단계

메모리 관리는 할당보다 회수의 문제입니다. 누가, 언제, 어떻게 회수하는지를 코드와 운영 양쪽에서 명시해야 시스템이 OOM 없이 오래 돕니다. 캐시 상한과 회수 정책을 같이 적는 습관 하나로 누수의 80%를 막을 수 있습니다.

다음 글에서는 OS가 한정된 RAM을 무한히 큰 것처럼 보이게 만드는 마법 — 가상 메모리로 넘어갑니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 race condition](./04-concurrency-and-race-conditions.md)
- [lock, mutex, semaphore](./05-locks-mutex-semaphore.md)
- **메모리 관리 (현재 글)**
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Python resource module](https://docs.python.org/3/library/resource.html)
- [Linux cgroup v2 memory controller](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory)

Tags: Computer Science, 운영체제, 메모리, heap, stack, allocator
