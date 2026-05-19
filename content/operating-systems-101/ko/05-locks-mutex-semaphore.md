---
series: operating-systems-101
episode: 5
title: 락, 뮤텍스, 세마포어
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

# 락, 뮤텍스, 세마포어

경쟁 상태를 막으려면 결국 공유 구역의 출입 규칙을 정해야 합니다. 문제는 규칙을 만들었다고 해서 자동으로 안전해지지 않는다는 점입니다.

락은 잘 쓰면 질서를 만들지만, 잘못 쓰면 시스템 전체를 멈추게 합니다. 이 글에서는 가장 흔한 동기화 도구를 역할별로 나눠 보고, 데드락이 어떻게 만들어지는지도 함께 보겠습니다.

이 글은 Operating Systems 101 시리즈의 5번째 글입니다.

## 이 글에서 다룰 문제

- 뮤텍스, 재진입 락, 세마포어, 조건 변수는 무엇이 다를까요?
- 데드락은 어떤 조건이 겹칠 때 만들어질까요?
- 락을 오래 잡으면 왜 처리량과 지연 시간이 같이 나빠질까요?
- 락을 줄이고도 안전성을 지킬 수 있는 대안은 무엇일까요?

> 락은 안전을 자동으로 보장하지 않습니다. 어떤 데이터를 무엇으로 보호할지, 어느 순서로 잡을지, 얼마나 짧게 쥘지를 명확히 정했을 때만 안전 규칙을 강제하는 도구가 됩니다.

## 기본 모델
> Mutex는 한 시점에 한 흐름만 임계 구역에 들어가게 합니다. Semaphore는 N개까지 동시에 들어갈 수 있게 합니다. RLock(재진입 락)은 같은 흐름이 같은 락을 여러 번 잡을 수 있게 합니다. Condition variable은 "어떤 조건이 충족될 때까지" 기다리고 깨우는 메커니즘입니다.

### 동기화 도구가 제어하는 입장 수

![동기화 도구가 제어하는 입장 수](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/05/05-01-how-synchronization-tools-gate-entry.ko.png)
*동기화 도구마다 임계 구역에 들어갈 수 있는 수와 기다리는 방식이 다릅니다.*

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
# Both threads wait forever (Ctrl+C to stop)
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

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- **락, 뮤텍스, 세마포어 (현재 글)**
- 메모리 관리 (예정)
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [The Art of Multiprocessor Programming — Herlihy & Shavit](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Java Concurrency in Practice — Brian Goetz](https://jcip.net/)
- [Python threading.Semaphore](https://docs.python.org/3/library/threading.html#semaphore-objects)

Tags: Computer Science, 운영체제, 동기화, 뮤텍스, 세마포어, 동시성
