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

## 먼저 던지는 질문

- 프로세스 메모리는 어떤 구역으로 나뉘어 있을까요?
- `malloc`과 `free`, 가비지 컬렉션은 각각 무엇을 맡을까요?
- 메모리 누수와 단편화는 어떻게 다른 문제일까요?

## 큰 그림

![Operating Systems 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/06/06-01-the-four-major-regions-of-process-memory.ko.png)

*Operating Systems 101 6장 흐름 개요*

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
# Allocate large blocks then free every other one
xs = []
for i in range(1000):
    xs.append(bytearray(1024 * 1024))   # 1MB
for i in range(0, 1000, 2):
    xs[i] = None                        # free even indices

# ~500MB free, but a single contiguous 1GB block is hard to get
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


## 운영체제 개념을 실무 판단으로 연결하기

### 스케줄링 정책을 숫자로 비교하는 방법
스케줄링은 이론 용어보다 대기시간과 응답시간으로 비교할 때 이해가 빠릅니다. 예를 들어 작업 집합이 `P1(도착 0, 실행 7)`, `P2(도착 2, 실행 4)`, `P3(도착 4, 실행 1)`일 때 FCFS와 SRTF의 결과를 비교하면 차이가 명확합니다.

- FCFS 평균 대기시간: `(0 + 5 + 7) / 3 = 4.0`
- SRTF 평균 대기시간: `(5 + 1 + 0) / 3 = 2.0`

같은 작업 집합이라도 정책에 따라 사용자 체감 지연이 크게 달라집니다. 서버가 인터랙티브 트래픽 중심인지, 배치 작업 중심인지에 따라 정책 선택 기준이 달라져야 합니다.

### 메모리 계층과 페이지 교체를 그림으로 정리하기
가상 메모리에서는 "어떤 페이지를 언제 내보내는가"가 성능을 좌우합니다. 아래 개념도는 자주 발생하는 페이지 폴트 경로를 보여줍니다.

```text
CPU 접근 -> 페이지 테이블 조회 -> miss
miss -> 페이지 폴트 트랩 -> 커널 핸들러
핸들러 -> victim 페이지 선택(LRU 근사)
victim dirty? yes -> 디스크 write-back
새 페이지 read -> 매핑 갱신 -> 재실행
```

핵심은 디스크 I/O가 개입되는 순간 지연이 급증한다는 점입니다. 따라서 워킹셋을 메모리에 유지하도록 데이터 구조와 접근 패턴을 설계해야 합니다. 순차 접근과 지역성 높은 캐시 친화 구조가 중요한 이유가 여기에 있습니다.

### 시스템 콜 경계에서 비용이 발생하는 이유
애플리케이션 코드는 사용자 모드에서 실행되지만, 파일 I/O와 네트워크 I/O는 커널 모드 전환이 필요합니다. 전환이 잦으면 오버헤드가 누적되므로 호출 단위를 조정하는 것이 좋습니다.

| syscall | 용도 | 성능 관점 포인트 |
| --- | --- | --- |
| `read` | 파일/소켓 입력 | 작은 크기로 반복 호출하면 전환 비용 증가 |
| `write` | 파일/소켓 출력 | 버퍼링 없이 자주 호출하면 처리량 저하 |
| `open` | 파일 디스크립터 획득 | 반복 open/close는 캐시 이점 상실 |
| `epoll_wait` | 이벤트 대기 | 다중 연결 처리에서 busy loop 방지 |
| `mmap` | 파일 메모리 매핑 | 랜덤 접근 workload에서 복사 비용 절감 가능 |

예를 들어 로그 수집기를 구현할 때 `write`를 1줄마다 호출하기보다 버퍼 단위로 모아 호출하면 syscall 횟수가 줄어 처리량이 개선됩니다. 운영체제 지식이 코드 수준 최적화로 직접 이어지는 지점입니다.

### 병행성 디버깅 체크리스트
경합 문제를 조사할 때는 증상만 보지 말고 스케줄링, 락 소유 시간, I/O 대기 시간을 함께 봐야 합니다.

1. `pidstat -w`로 컨텍스트 스위치 급증 여부 확인
2. `vmstat 1`로 run queue 길이와 I/O wait 확인
3. `strace -f -tt`로 블로킹 syscall 지점 식별
4. 락 획득/반납 시각을 애플리케이션 로그에 기록

이 네 단계를 함께 적용하면 "CPU가 느린 문제"인지 "락 경합 문제"인지 "디스크 대기 문제"인지를 분리할 수 있습니다. 운영체제 개념은 결국 문제를 정확히 분해하는 관측 프레임입니다.

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

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Python resource module](https://docs.python.org/3/library/resource.html)
- [Linux cgroup v2 memory controller](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory)

Tags: Computer Science, 운영체제, 메모리, heap, stack, allocator
