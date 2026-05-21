---
series: operating-systems-101
episode: 5
title: "Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어"
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
  - 동기화
  - 뮤텍스
  - 세마포어
  - 동시성
seo_description: 뮤텍스와 세마포어의 차이를 정의하고 데드락 발생 조건과 회피 전략을 학습합니다. 동기화 도구의 선택과 실무적인 락 회피 패턴을 함께 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어

경쟁 상태를 막으려면 결국 공유 구역의 출입 규칙을 정해야 합니다. 문제는 규칙을 만들었다고 해서 자동으로 안전해지지 않는다는 점입니다.

락은 잘 쓰면 질서를 만들지만, 잘못 쓰면 시스템 전체를 멈추게 합니다. 이 글에서는 가장 흔한 동기화 도구를 역할별로 나눠 보고, 데드락이 어떻게 만들어지는지도 함께 보겠습니다.

이 글은 Operating Systems 101 시리즈의 5번째 글입니다.

![Operating Systems 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/05/05-01-how-synchronization-tools-gate-entry.ko.png)
*Operating Systems 101 5장 흐름 개요*

## 먼저 던지는 질문

- 뮤텍스, 재진입 락, 세마포어, 조건 변수는 무엇이 다를까요?
- 데드락은 어떤 조건이 겹칠 때 만들어질까요?
- 락을 오래 잡으면 왜 처리량과 지연 시간이 같이 나빠질까요?

## 기본 모델
> Mutex는 한 시점에 한 흐름만 임계 구역에 들어가게 합니다. Semaphore는 N개까지 동시에 들어갈 수 있게 합니다. RLock(재진입 락)은 같은 흐름이 같은 락을 여러 번 잡을 수 있게 합니다. Condition variable은 "어떤 조건이 충족될 때까지" 기다리고 깨우는 메커니즘입니다.

### 동기화 도구가 제어하는 입장 수

```text
Mutex     : capacity = 1
Semaphore : capacity = N (e.g., DB connection pool of 10)
RLock     : same owner can re-enter (recursive functions, etc.)
Condition : "wait until inventory >= 1" style predicate waits
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "락만 걸면 안전":**

```python
import threading
lock_a = threading.Lock()
lock_b = threading.Lock()

def task1():
    with lock_a:
        with lock_b:
            ...

def task2():
    with lock_b:    # different order!
        with lock_a:
            ...
```

두 함수가 동시에 돌면 데드락이 만들어집니다.

**바꿔서 보면 — "락 잡는 순서를 한 가지로 강제":**

```text
Rule: always take lock_a first, then lock_b.
Violating it in even one place can stop the whole system.
```

## 단계별로 확인하기

### 1단계: 기본 뮤텍스 사용

```python
import threading
counter = 0
m = threading.Lock()

def add():
    global counter
    for _ in range(100_000):
        with m:
            counter += 1

ts = [threading.Thread(target=add) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print(counter)
```

`with m:` 블록이 임계 구역입니다. 빠지면 자동으로 풀립니다.

### 2단계: 재진입 락으로 재귀 호출 보호

```python
import threading
lock = threading.RLock()
data = {}

def update(k, v, depth=0):
    with lock:
        data[k] = v
        if depth < 2:
            update(k + '_x', v + 1, depth + 1)
```

일반 `Lock`이라면 같은 스레드가 두 번째 `acquire`에서 막힙니다. `RLock`은 같은 스레드의 재진입을 허용합니다.

### 3단계: 세마포어로 동시 접속 제한

```python
import threading, time

pool = threading.Semaphore(3)   # at most three at once

def query():
    with pool:
        time.sleep(0.5)         # simulate DB work
        print(threading.current_thread().name, 'done')

ts = [threading.Thread(target=query) for _ in range(10)]
for t in ts: t.start()
for t in ts: t.join()
```

10개 스레드가 있어도 동시에 3개만 진행합니다. DB 커넥션 풀 같은 자원에 자연스러운 추상화입니다.

### 4단계: 데드락 일부러 만들어 보기

```python
import threading, time

a = threading.Lock(); b = threading.Lock()

def t1():
    with a:
        time.sleep(0.1)
        with b:  pass

def t2():
    with b:
        time.sleep(0.1)
        with a:  pass

threading.Thread(target=t1).start()
threading.Thread(target=t2).start()
# 두 스레드 모두 영원히 대기합니다(Ctrl+C로 중지)
```

데드락의 네 가지 조건(상호 배제, 점유 대기, 비선점, 순환 대기)이 모두 충족됩니다. 실제 코드에서는 락 잡는 순서를 한 가지로 정해 순환 대기를 깨는 것이 가장 흔한 해법입니다.

### 5단계: 락 없는 대안 — 큐로 통신

```python
from queue import Queue
import threading

q = Queue()

def producer():
    for i in range(5):
        q.put(i)

def consumer():
    while True:
        item = q.get()
        if item is None: break
        print('got', item)
        q.task_done()

threading.Thread(target=producer).start()
c = threading.Thread(target=consumer)
c.start()
q.join(); q.put(None); c.join()
```

직접 락을 잡지 않아도, 큐 자체가 내부적으로 동기화됩니다. 통신이 메모리 공유보다 안전한 이유입니다.

## 여기서 먼저 볼 점

- 락은 정해진 규칙(잡는 순서, 잡는 범위)을 강제하는 도구입니다
- Semaphore는 카운팅 락이고, 자원 풀의 자연스러운 추상화입니다
- 데드락의 네 조건 중 하나만 깨도 데드락은 사라집니다
- 락이 답이 아닐 때, 큐와 메시지로 통신하는 설계가 종종 더 좋습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 락 순서 통일 안 함 | 데드락 | 전역 락 순서 규약(코드에 주석으로 명시) |
| 락 안에서 무거운 I/O | 다른 스레드 모두 대기, 처리량 폭락 | 임계 구역은 짧게, I/O는 밖에서 |
| `Lock`을 재귀에 사용 | 자기 자신이 자기를 막음 | `RLock` 사용 |
| 예외 시 락 안 풀림 | 데드락 또는 좀비 락 | 항상 `with lock:` 사용 |
| 글로벌 락 하나로 모두 보호 | 사실상 직렬화, 멀티스레드의 의미 없음 | 보호 단위를 잘게 나누기 |

## 실무에서는 이렇게 본다

- DB 커넥션 풀: semaphore로 동시 사용 한도 강제
- 캐시 갱신: 단일 mutex 또는 read-write 락으로 보호
- 백엔드 작업 큐: producer/consumer 패턴으로 락 회피
- GUI/게임: 메인 스레드 단일 소유 + 큐로 외부 입력 전달
- 분산 시스템: 같은 개념을 분산 락(예: Redis SETNX, etcd lease)으로 구현

## 체크리스트

- [ ] mutex, RLock, semaphore, condition의 차이를 안다
- [ ] 데드락의 네 가지 조건을 말할 수 있는가
- [ ] 락 순서 규약의 필요성을 이해한다
- [ ] 락의 비용(컨텍스트 스위치, 호송)을 안다
- [ ] 락 외 대안(큐, 불변, atomic)을 한 가지 이상 안다

## 연습 문제

1. 일부러 데드락을 만든 뒤 락 순서를 통일해서 문제를 없애고, 무엇이 달라졌는지 한 문단으로 정리해 보세요.
2. 세마포어로 동시에 세 개만 실행되는 워커 풀을 만들고, 열 개 작업을 넣었을 때 실행 순서를 관찰해 보세요.
3. 락 기반 코드를 큐 기반 producer/consumer로 바꿔 보고, 코드 길이와 이해하기 쉬운 정도를 비교해 보세요.

## 마무리와 다음 글

Mutex, semaphore, RLock, condition variable은 OS가 제공하는 동기화의 기본 도구입니다. 잡는 순서·범위·시간을 정확히 정해야 락이 안전하게 동작하고, 데드락의 네 조건 중 하나만 깨도 데드락은 사라집니다. 가장 안전한 락은 필요 없는 락이라는 사실을 잊지 마세요.

다음 글에서는 OS의 또 다른 기본기 — 메모리 관리로 넘어갑니다. 프로세스의 메모리는 어떻게 할당되고, 운영체제는 그 한정된 RAM을 어떻게 나누는지 봅니다.

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

## 데드락 탐지 코드를 직접 작성해 보기

데드락은 "걸렸을 때 복구"보다 "의존 그래프를 관찰해 조기 감지"가 효과적입니다. 아래 코드는 wait-for graph에서 사이클을 탐지하는 최소 예제입니다.

```python
from collections import defaultdict

class DeadlockDetector:
    def __init__(self):
        self.graph = defaultdict(set)  # A -> B : A가 B가 가진 락을 기다림

    def wait(self, waiter, owner):
        self.graph[waiter].add(owner)

    def release_wait(self, waiter, owner):
        self.graph[waiter].discard(owner)

    def has_cycle(self):
        visited, stack = set(), set()

        def dfs(node):
            visited.add(node)
            stack.add(node)
            for nxt in self.graph[node]:
                if nxt not in visited and dfs(nxt):
                    return True
                if nxt in stack:
                    return True
            stack.remove(node)
            return False

        return any(dfs(n) for n in list(self.graph) if n not in visited)

d = DeadlockDetector()
d.wait('T1', 'T2')
d.wait('T2', 'T3')
d.wait('T3', 'T1')
print('deadlock?', d.has_cycle())  # True
```

운영 환경에서는 락 획득 시도/성공/해제 이벤트를 로그 스트림으로 수집해 그래프를 만들면, 실제 데드락 직전 패턴을 탐지할 수 있습니다.

### 락 설계 표준 규약 예시

1. 락 순서 전역 규약: `L_user -> L_order -> L_inventory`
2. 락 타임아웃 기본값: 200ms
3. 임계 구역 내 I/O 금지
4. 예외 경로에서 반드시 해제(`with`, `try/finally`)

이 네 규약만 지켜도 데드락과 락 호송(lock convoy) 빈도를 크게 낮출 수 있습니다.

## 처음 질문으로 돌아가기

- **뮤텍스, 재진입 락, 세마포어, 조건 변수는 무엇이 다를까요?**
  - 본문의 기준은 락, 뮤텍스, 세마포어를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **데드락은 어떤 조건이 겹칠 때 만들어질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **락을 오래 잡으면 왜 처리량과 지연 시간이 같이 나빠질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- **락, 뮤텍스, 세마포어 (현재 글)**
- 메모리 관리 (예정)
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [The Art of Multiprocessor Programming — Herlihy & Shavit](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Java Concurrency in Practice — Brian Goetz](https://jcip.net/)
- [Python threading.Semaphore](https://docs.python.org/3/library/threading.html#semaphore-objects)

Tags: Computer Science, 운영체제, 동기화, 뮤텍스, 세마포어, 동시성
