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

## 먼저 던지는 질문

- 프로세스 메모리는 어떤 구역으로 나뉘어 있을까요?
- `malloc`과 `free`, 가비지 컬렉션은 각각 무엇을 맡을까요?
- 메모리 누수와 단편화는 어떻게 다른 문제일까요?

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

## 단계별로 확인하기

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
# 큰 블록을 할당한 뒤 하나 걸러 해제합니다
xs = []
for i in range(1000):
    xs.append(bytearray(1024 * 1024))   # 1MB
for i in range(0, 1000, 2):
    xs[i] = None                        # free even indices

# 500MB가 빈 상태이지만 연속된 1GB 블록을 확보하기는 어렵습니다
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
# Memory limit and current use of a Docker container
cat /sys/fs/cgroup/memory.max 2>/dev/null || echo 'not in container'
cat /sys/fs/cgroup/memory.current 2>/dev/null || echo 'not in container'
```

컨테이너에서는 cgroup이 부모 OS와 별개로 한도를 강제합니다. 한도를 모르고 캐시를 키우면 OOM-kill됩니다.

## 여기서 먼저 볼 점

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

## 실무에서는 이렇게 본다

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

## 연습 문제

1. 누수 예제의 RSS 변화를 1분 동안 기록하고, 시간이 지날수록 값이 어떻게 바뀌는지 한 문단으로 정리해 보세요.
2. 무제한 dict 캐시를 `functools.lru_cache(maxsize=...)`로 바꿔 같은 부하를 걸어 보고, 메모리 사용량 차이를 비교해 보세요.
3. 64MB로 제한된 컨테이너에서 안전한 캐시 상한을 직접 계산해 보고, 그 근거를 적어 보세요.

## 마무리와 다음 글

메모리 관리는 할당보다 회수의 문제입니다. 누가, 언제, 어떻게 회수하는지를 코드와 운영 양쪽에서 명시해야 시스템이 OOM 없이 오래 돕니다. 캐시 상한과 회수 정책을 같이 적는 습관 하나로 누수의 80%를 막을 수 있습니다.

다음 글에서는 OS가 한정된 RAM을 무한히 큰 것처럼 보이게 만드는 마법 — 가상 메모리로 넘어갑니다.

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

## 메모리 레이아웃과 할당기 동작을 같이 보기

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

### 단편화 완화 패턴

- 크기 비슷한 객체는 풀에서 재사용합니다.
- 수명이 짧은 임시 객체를 배치로 처리합니다.
- 대형 버퍼는 재할당 대신 재사용합니다.

```python
class BufferPool:
    def __init__(self, size, n):
        self.free = [bytearray(size) for _ in range(n)]

    def get(self):
        return self.free.pop() if self.free else bytearray(len(self.free[0]))

    def put(self, buf):
        self.free.append(buf)
```

할당/해제 빈도를 줄이면 할당기 메타데이터 경합과 단편화를 동시에 완화할 수 있습니다.

## 처음 질문으로 돌아가기

- **프로세스 메모리는 어떤 구역으로 나뉘어 있을까요?**
  - 본문의 기준은 메모리 관리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`malloc`과 `free`, 가비지 컬렉션은 각각 무엇을 맡을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **메모리 누수와 단편화는 어떻게 다른 문제일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- **메모리 관리 (현재 글)**
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Python resource module](https://docs.python.org/3/library/resource.html)
- [Linux cgroup v2 memory controller](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory)

Tags: Computer Science, 운영체제, 메모리, heap, stack, allocator
