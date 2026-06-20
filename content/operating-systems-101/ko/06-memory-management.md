---
series: operating-systems-101
episode: 6
title: "Operating Systems 101 (6/10): 메모리 관리"
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
  - 메모리
  - heap
  - stack
  - allocator
seo_description: 프로세스 메모리 구조를 파악하고 누수와 단편화 원인 및 해결 방법을 학습합니다. 가비지 컬렉션의 한계와 실무적인 메모리 관리 기법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (6/10): 메모리 관리

서버가 며칠 뒤부터 천천히 느려지는 문제는 CPU보다 메모리에서 시작할 때가 많습니다. 캐시가 끝없이 커지거나, 누수가 누적되거나, 회수 시점이 불분명하면 증상은 늦게 보이지만 복구 비용은 커집니다.

메모리 관리의 핵심은 더 할당하는 법보다 언제 어떻게 되돌려 줄지를 정하는 데 있습니다. 그래서 이 글에서는 힙과 스택을 넘어서 소유권과 회수 정책까지 함께 봅니다.

이 글은 Operating Systems 101 시리즈의 6번째 글입니다.

![Operating Systems 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/06/06-01-the-four-major-regions-of-process-memory.ko.png)
*Operating Systems 101 6장 흐름 개요*

## 이 글에서 다룰 문제

- 프로세스 메모리는 어떤 구역으로 나뉘어 있을까요?
- `malloc`과 `free`, 가비지 컬렉션은 각각 무엇을 맡을까요?
- 메모리 누수와 단편화는 어떻게 다른 문제일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 기본 모델

> 프로세스 메모리는 크게 네 영역으로 나뉩니다. 코드(text), 전역 변수(data/bss), heap, stack. heap은 동적 할당, stack은 함수 호출에 따라 자동으로 자라고 줄어듭니다. OS는 가상 주소를 줘서 모든 프로세스가 자신만의 메모리를 가진 것처럼 보이게 합니다.

### 프로세스 메모리의 큰 네 구역

```text
high addr
+---------+
|  stack  |  ← function calls / locals, auto-managed
|    ↓    |
|         |
|    ↑    |
|  heap   |  ← malloc/new, freed explicitly or by GC
+---------+
| bss/data|  ← globals / statics
| text    |  ← executable code
low addr
```

### 각 영역의 역할과 특성

| 영역 | 역할 | 크기 관리 | 수명 |
| --- | --- | --- | --- |
| text | 실행 코드 (기계어) | 프로그램 시작 시 고정 | 프로세스 종료까지 |
| data | 초기화된 전역/정적 변수 | 컴파일 시간에 결정 | 프로세스 종료까지 |
| bss | 0으로 초기화된 전역/정적 변수 | 컴파일 시간에 결정 | 프로세스 종료까지 |
| heap | 동적 할당 객체 | 런타임에 가변 (위로 자람) | malloc/free 또는 GC로 결정 |
| stack | 함수 호출 프레임, 지역 변수 | 런타임에 가변 (아래로 자람) | 함수 반환 시 자동 해제 |

### Stack vs Heap 비교

```python
# Stack에 저장되는 것 (지역 변수, 함수 인자)
def add(a: int, b: int) -> int:
    result = a + b  # result는 스택에 할당
    return result   # 함수 반환 시 result 자동 해제

# Heap에 저장되는 것 (동적 할당 객체)
def create_large_buffer() -> bytearray:
    buf = bytearray(10 * 1024 * 1024)  # 10MB, 힙에 할당
    return buf  # 반환하면 참조만 이동, 메모리는 힙에 남음

# 스택 오버플로우 예시
def recurse():
    recurse()  # 재귀 호출이 쌓이면 스택이 넘침

# 실무에서: 재귀 깊이 제한
import sys
sys.setrecursionlimit(500)  # 기본값 1000에서 줄이거나
# 또는 반복문으로 변환하는 것이 근본 해결책
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "메모리는 무한하다":**

```python
cache = {}
def handle(req):
    cache[req.id] = expensive(req)   # grows forever
    return cache[req.id]
```

며칠 후 OOM. 누수는 명시적 free가 없는 GC 언어에서도 똑같이 발생합니다.

**바꿔서 보면 — "회수 정책을 명시한다":**

```python
from functools import lru_cache

@lru_cache(maxsize=10_000)
def handle(req_id):
    return expensive(req_id)
```

상한과 회수 정책이 명시되어 있으면 누수가 아닙니다.

### 메모리 관리 전략별 비교

| 전략 | 적합한 상황 | 장점 | 위험 |
| --- | --- | --- | --- |
| 수동 관리 (malloc/free) | C/C++, 임베디드 | 정밀한 제어, 낮은 오버헤드 | 누수, 이중 해제, 댕글링 포인터 |
| 가비지 컬렉션 (GC) | Python, Java, Go | 자동 회수, 코드 단순화 | 참조 누수 가능, GC 일시 중단 |
| 소유권 시스템 (Rust) | 시스템 소프트웨어 | 컴파일 시 안전성 보장 | 학습 곡선 높음 |
| 참조 카운팅 (ARC) | Swift, Python (CPython) | 즉각 회수 | 순환 참조 누수 |
| 메모리 풀 | 게임, 실시간 시스템 | 단편화 없음, 빠른 할당 | 풀 크기 사전 설계 필요 |

## 단계별로 확인하기

### 1단계: 프로세스 메모리 사용량 보기

```python
import os, resource

print('PID', os.getpid())
print('peak RSS (KB)', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
```

`ru_maxrss`는 프로세스가 실제로 점유한 RAM의 최대값입니다.

더 상세한 메모리 사용량을 확인하려면:

```python
import tracemalloc

tracemalloc.start()

# 프로파일링하고 싶은 코드 실행
data = [i for i in range(1_000_000)]

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("Top 5 memory consumers:")
for stat in top_stats[:5]:
    print(stat)
```

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

**참조 카운팅과 순환 참조 문제:**

```python
import gc
import sys

# 순환 참조 예시
class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None

a = Node("A")
b = Node("B")
a.ref = b   # a가 b를 참조
b.ref = a   # b가 a를 참조 (순환!)

# 둘 다 None으로 설정해도 순환 참조로 인해 즉시 해제 안 됨
a = None
b = None

# CPython의 cyclic GC가 처리하지만 타이밍이 불확실
collected = gc.collect()
print(f"Collected {collected} objects")

# 순환 참조 방지: 약한 참조 사용
import weakref

class SafeNode:
    def __init__(self, name):
        self.name = name
        self._parent = None  # weakref.ref로 저장

    @property
    def parent(self):
        if self._parent is not None:
            return self._parent()  # weakref 역참조
        return None

    @parent.setter
    def parent(self, node):
        self._parent = weakref.ref(node) if node else None
```

### 3단계: 단편화 관찰

```python
# 큰 블록을 할당한 뒤 하나 걸러 해제합니다
xs = []
for i in range(1000):
    xs.append(bytearray(1024 * 1024))   # 1MB
for i in range(0, 1000, 2):
    xs[i] = None                        # free even indices

# 500MB가 빈 상태이지만 연속된 1GB 블록을 확보하기는 어렵습니다
```

총량은 충분한데 연속 공간이 부족한 상태가 단편화입니다.

**외부 단편화 vs 내부 단편화:**

```text
외부 단편화 (External Fragmentation):
+--+----+--+----+--+----+--+
|사용|빈칸|사용|빈칸|사용|빈칸|사용|
+--+----+--+----+--+----+--+
→ 각 빈칸은 작아서 큰 요청을 수용 못함

내부 단편화 (Internal Fragmentation):
+--------+--------+
|요청8B  |요청8B  |
|실제8B  |실제8B  |
|[낭비0B]|[낭비0B]|
+--------+--------+
→ 할당기가 8B 단위로만 주기 때문에 5B 요청도 8B 블록 사용
```

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
# Memory limit and current use of a Docker container
cat /sys/fs/cgroup/memory.max 2>/dev/null || echo 'not in container'
cat /sys/fs/cgroup/memory.current 2>/dev/null || echo 'not in container'
```

컨테이너에서는 cgroup이 부모 OS와 별개로 한도를 강제합니다. 한도를 모르고 캐시를 키우면 OOM-kill됩니다.

**컨테이너 메모리 한도 기반 캐시 설정 예시:**

```python
import os

def get_memory_limit_bytes() -> int:
    """cgroup v2에서 컨테이너 메모리 한도를 읽음"""
    cgroup_file = "/sys/fs/cgroup/memory.max"
    try:
        with open(cgroup_file) as f:
            value = f.read().strip()
            if value == "max":
                return 4 * 1024 ** 3  # 기본 4GB
            return int(value)
    except FileNotFoundError:
        return 4 * 1024 ** 3  # 컨테이너 아닌 경우

# 메모리 한도의 30%를 캐시에 할당
MEMORY_LIMIT = get_memory_limit_bytes()
CACHE_BUDGET = int(MEMORY_LIMIT * 0.30)
OBJECT_SIZE_BYTES = 1024  # 평균 객체 크기 추정
MAX_CACHE_ENTRIES = CACHE_BUDGET // OBJECT_SIZE_BYTES

from functools import lru_cache

@lru_cache(maxsize=MAX_CACHE_ENTRIES)
def expensive_compute(key: str) -> bytes:
    # ... 계산 로직
    return b""

print(f"메모리 한도: {MEMORY_LIMIT // 1024 // 1024} MB")
print(f"캐시 예산: {CACHE_BUDGET // 1024 // 1024} MB")
print(f"최대 캐시 항목: {MAX_CACHE_ENTRIES:,}")
```

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 무제한 캐시 | OOM | 상한과 회수 정책 명시(LRU 등) |
| 글로벌 리스트에 무한 append | 누수 | 약한 참조 또는 만료 시간 |
| 큰 객체를 클로저에 캡처 | 회수 안 됨 | 필요한 값만 추출해 캡처 |
| 컨테이너 한도 무시 | OOM-kill | cgroup 한도 기준으로 캐시/풀 설정 |
| GC 언어니까 안전 | 누수 가능 | 참조 그래프를 의식적으로 설계 |

### 클로저 캡처 누수 예시

```python
# 잘못된 방법: 큰 객체 전체를 클로저가 캡처
def create_handler(large_config: dict) -> callable:
    def handler(request):
        return large_config["key"]  # large_config 전체가 캡처됨
    return handler

# 올바른 방법: 필요한 값만 추출
def create_handler_fixed(large_config: dict) -> callable:
    key_value = large_config["key"]  # 필요한 값만 추출
    del large_config  # 명시적으로 참조 해제 힌트 (실제 해제는 호출자 담당)
    def handler(request):
        return key_value  # 작은 값만 캡처
    return handler
```

## 실무에서는 이렇게 본다

- 캐시: 항상 상한과 회수 정책이 함께 정의됨
- 백엔드: 워커당 메모리 한도 + OOM 방어선
- 데이터 처리: chunk 단위 스트리밍으로 peak RSS 제한
- 게임/임베디드: 풀 할당으로 단편화 회피
- 컨테이너: cgroup 한도를 기준으로 capacity 계획

### 대규모 데이터 처리에서의 메모리 관리

```python
# 잘못된 방법: 전체 파일을 메모리에 올림
def process_file_bad(path: str) -> list:
    with open(path) as f:
        lines = f.readlines()  # 수 GB 파일이면 OOM 위험
    return [process_line(line) for line in lines]

# 올바른 방법: 스트리밍으로 청크 단위 처리
def process_file_good(path: str, chunk_size: int = 10_000):
    with open(path) as f:
        chunk = []
        for line in f:  # 파일을 한 줄씩 읽음 (peak RSS 최소화)
            chunk.append(process_line(line))
            if len(chunk) >= chunk_size:
                yield from chunk
                chunk.clear()  # 처리한 chunk 즉시 해제
        if chunk:
            yield from chunk

# pandas에서의 청크 처리
import pandas as pd

def process_csv_chunked(path: str, chunksize: int = 50_000):
    for chunk in pd.read_csv(path, chunksize=chunksize):
        # 청크를 처리하고 결과만 저장
        result = chunk.groupby("user_id")["value"].sum()
        yield result
        # chunk는 다음 반복에서 GC가 처리
```

## 운영 체크리스트

- [ ] 프로세스 메모리 영역(text/data/heap/stack)을 안다
- [ ] 누수와 단편화의 차이를 안다
- [ ] 캐시에 capacity와 eviction policy를 둘 다 적는다
- [ ] 컨테이너에서는 cgroup 한도를 의식한다
- [ ] RSS 추세를 모니터링 대상에 넣는다
- [ ] 순환 참조가 생길 수 있는 구조에서는 weakref를 사용한다
- [ ] 대용량 데이터 처리 시 스트리밍 방식을 기본으로 선택한다

## 시스템 관찰: 메모리 레이아웃과 할당기 동작을 같이 보기

메모리 문제는 언어 런타임 지표만 보면 원인을 놓치기 쉽습니다. OS 관점의 레이아웃과 할당기 동작을 함께 보아야 합니다.

### 프로세스 메모리 레이아웃 상세도

```text
높은 주소
+------------------------------+
| 스레드 N stack               |
+------------------------------+
| ...                          |
+------------------------------+
| 스레드 1 stack               |
+------------------------------+
| mmap 영역(파일 매핑, so)     |
+------------------------------+
| heap (brk/sbrk 확장)         |
+------------------------------+
| .bss / .data                 |
+------------------------------+
| .text                        |
+------------------------------+
낮은 주소
```

### `/proc/<pid>/smaps`로 구간별 RSS 확인

```bash
PID=$(pgrep -f "python3 app.py" | head -n 1)
grep -E "^Size|^Rss|^Pss|^Private_Dirty|^VmFlags" /proc/$PID/smaps | head -n 40
```

`smaps`는 구간별로 RSS/PSS를 보여 주기 때문에, 힙 누수인지 mmap 증가인지 분리할 수 있습니다.

**메모리 관련 주요 /proc 파일 비교:**

| 파일 | 내용 | 사용 상황 |
| --- | --- | --- |
| /proc/PID/status | VmRSS, VmSize 요약 | 빠른 개요 확인 |
| /proc/PID/smaps | 구간별 RSS/PSS 상세 | 누수 구간 추적 |
| /proc/PID/maps | 가상 주소 매핑 목록 | 라이브러리 로딩 확인 |
| /sys/fs/cgroup/memory.current | 컨테이너 현재 사용량 | 컨테이너 메모리 추적 |
| /sys/fs/cgroup/memory.max | 컨테이너 한도 | 캐시 상한 계산 |

### 페이지 폴트와 메모리 압박 해석

메모리 문제는 OOM 직전에야 드러나는 경우가 많습니다. 아래 지표를 주기적으로 보면 이상 징후를 조기에 잡을 수 있습니다.

```bash
# major page fault 증가: 디스크에서 페이지를 자주 끌어오는 상태
# swap in/out 급증: 워킹셋이 물리 메모리를 초과한 상태
vmstat 1
```

애플리케이션이 GC를 쓰는 런타임이라면, 힙 크기 조정과 객체 생존 시간 최적화가 커널 메모리 압박을 완화하는 직접 수단이 됩니다.

**메모리 압박 단계와 OS 반응:**

```text
정상 상태:
  물리 메모리 < 60% 사용
  → 스왑 없음, 페이지 폴트 낮음

주의 단계:
  물리 메모리 60-80% 사용
  → OS가 캐시 페이지 회수 시작
  → 파일 I/O 성능 저하 가능

경계 단계:
  물리 메모리 80-95% 사용
  → 스왑 활성화, 성능 급격히 저하
  → kswapd 데몬 CPU 사용 증가

OOM 단계:
  물리 메모리 > 95% 사용
  → OOM killer가 프로세스를 강제 종료
  → 로그: "Out of memory: Kill process PID"
```

### 단편화 완화 패턴: 버퍼 풀

크기 비슷한 객체는 풀에서 재사용하면 할당/해제 빈도를 줄여 단편화와 할당기 경합을 동시에 완화할 수 있습니다.

```python
class BufferPool:
    def __init__(self, size, n):
        self.size = size
        self.free = [bytearray(size) for _ in range(n)]

    def get(self):
        if self.free:
            return self.free.pop()
        return bytearray(self.size)

    def put(self, buf):
        # 버퍼를 초기화하지 않고 재사용 — 보안 민감 데이터는 주의
        self.free.append(buf)
```

**스레드 안전 버퍼 풀:**

```python
import threading

class ThreadSafeBufferPool:
    def __init__(self, buf_size: int, pool_size: int):
        self.buf_size = buf_size
        self._lock = threading.Lock()
        self._pool = [bytearray(buf_size) for _ in range(pool_size)]

    def acquire(self) -> bytearray:
        with self._lock:
            if self._pool:
                return self._pool.pop()
        return bytearray(self.buf_size)  # 풀이 비면 새로 할당

    def release(self, buf: bytearray) -> None:
        assert len(buf) == self.buf_size, "Wrong buffer size"
        with self._lock:
            self._pool.append(buf)

# 사용 예시
pool = ThreadSafeBufferPool(buf_size=4096, pool_size=100)

def handle_request(data: bytes) -> bytes:
    buf = pool.acquire()
    try:
        buf[:len(data)] = data
        # ... 처리 ...
        return bytes(buf[:len(data)])
    finally:
        pool.release(buf)  # 반드시 반환
```

## 메모리 모니터링 대시보드 설계

실무에서 메모리 문제를 조기에 잡으려면 아래 지표를 모니터링 시스템에 포함해야 합니다.

| 지표 | 측정 방법 | 경보 기준 | 의미 |
| --- | --- | --- | --- |
| RSS 증가율 | /proc/PID/status | 시간당 100MB 이상 증가 | 누수 가능성 |
| GC 빈도 | gc.callbacks 또는 런타임 지표 | 초당 10회 이상 | 힙 압박 |
| 페이지 폴트 | /proc/PID/stat | major fault 분당 100회 이상 | 스왑 압박 |
| 캐시 hit rate | 앱 지표 | 50% 미만 | 캐시 효율 저하 |
| 컨테이너 메모리 | memory.current / memory.max | 80% 초과 | OOM 위험 |

```python
# Prometheus 지표로 내보내기 예시 (prometheus_client 사용)
import gc
import resource
from prometheus_client import Gauge, Counter

rss_gauge = Gauge("process_rss_bytes", "현재 RSS 메모리 사용량")
gc_count = Counter("gc_collections_total", "GC 실행 횟수", ["generation"])

def update_memory_metrics():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    rss_gauge.set(rss)

def on_gc_callback(phase, info):
    if phase == "stop":
        gc_count.labels(generation=info["generation"]).inc()

gc.callbacks.append(on_gc_callback)
```

## 처음 질문으로 돌아가기

- **프로세스 메모리는 어떤 구역으로 나뉘어 있을까요?**
  - text(실행 코드), data/bss(초기화된/미초기화 전역 변수), heap(동적 할당, 위로 자람), stack(함수 호출 프레임, 아래로 자람) 네 구역으로 나뉩니다. 스레드는 스택만 따로 가지고, heap과 전역 변수는 공유합니다.

- **`malloc`과 `free`, 가비지 컬렉션은 각각 무엇을 맡을까요?**
  - `malloc`은 heap에서 연속 블록을 예약하고, `free`는 그 블록을 할당기에 돌려줍니다. GC는 참조가 끊긴 객체를 자동으로 회수합니다. 세 방식 모두 "참조가 남아 있으면 회수하지 않는다"는 공통 규칙을 가집니다. GC가 있어도 참조를 끊지 않으면 누수가 생깁니다.

- **메모리 누수와 단편화는 어떻게 다른 문제일까요?**
  - 누수는 "안 쓰는데 참조가 살아 있어서 회수가 안 되는" 문제입니다. 단편화는 "총량은 충분한데 연속된 큰 블록을 할당할 수 없는" 문제입니다. 누수는 RSS가 계속 오르는 패턴으로, 단편화는 할당 실패 또는 성능 저하로 나타납니다.

## 연습 문제

1. 누수 예제의 RSS 변화를 1분 동안 기록하고, 시간이 지날수록 값이 어떻게 바뀌는지 한 문단으로 정리해 보세요.
2. 무제한 dict 캐시를 `functools.lru_cache(maxsize=...)`로 바꿔 같은 부하를 걸어 보고, 메모리 사용량 차이를 비교해 보세요.
3. 64MB로 제한된 컨테이너에서 안전한 캐시 상한을 직접 계산해 보고, 그 근거를 적어 보세요.
4. 순환 참조를 만드는 코드를 작성하고 `weakref`로 고쳐 보세요.
5. BufferPool 클래스를 구현하고, 100개 연결을 동시에 처리하는 시뮬레이션에서 메모리 사용량 변화를 관찰해 보세요.

## 마무리와 다음 글

메모리 관리는 할당보다 회수의 문제입니다. 누가, 언제, 어떻게 회수하는지를 코드와 운영 양쪽에서 명시해야 시스템이 OOM 없이 오래 돕니다. 캐시 상한과 회수 정책을 같이 적는 습관 하나로 누수의 80%를 막을 수 있습니다.

다음 글에서는 OS가 한정된 RAM을 무한히 큰 것처럼 보이게 만드는 마법 — 가상 메모리로 넘어갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- **Operating Systems 101 (6/10): 메모리 관리 (현재 글)**
- [Operating Systems 101 (7/10): 가상 메모리](./07-virtual-memory.md)
- [Operating Systems 101 (8/10): 파일 시스템](./08-file-systems.md)
- [Operating Systems 101 (9/10): 시스템 콜](./09-system-calls.md)
- [Operating Systems 101 (10/10): 컨테이너와 운영체제](./10-containers-and-the-os.md)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Python resource module](https://docs.python.org/3/library/resource.html)
- [Linux cgroup v2 memory controller](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory)

Tags: Computer Science, 운영체제, 메모리, heap, stack, allocator
