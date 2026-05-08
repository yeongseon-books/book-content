
# lock, mutex, semaphore

> Operating Systems 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 동시성 문제를 막아 주는 락은 어떻게 동작하고, 잘못 사용하면 왜 시스템 전체를 멈추게 만들까요?

> Mutex, semaphore, condition variable은 동시성 코드를 다루는 가장 기본적인 OS 수준 도구입니다. 단순해 보이지만, 잡는 순서, 잡는 시간, 잡는 범위에 따라 결과가 극단적으로 달라집니다. 이 글에서는 락의 종류와 차이, 데드락이 어떻게 만들어지고 어떻게 피하는지, 그리고 락을 안 쓰는 대안까지 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- mutex, RLock, semaphore, condition variable의 차이
- 데드락이 만들어지는 네 가지 조건과 회피 방법
- 락의 비용 — 컨텍스트 스위치와 캐시 효과
- 락 없는 동기화 대안 — 큐, 불변, atomic, RCU 개념

## 왜 중요한가

락은 동시성 코드의 안전벨트지만, 잘못 채우면 안전벨트가 좌석에 묶여 못 움직이는 상황이 됩니다. 잡는 순서를 한 곳에서만 어긋내도 시스템 전체가 멈추고, 잡는 범위를 잘못 잡으면 race가 그대로 남습니다. 락을 "그냥 걸면 안전"이라고 생각하면 운영 환경의 미스터리한 정지의 원인이 됩니다.

> 락은 안전을 보장하는 도구가 아니라, 안전한 사용 규칙을 강제하는 도구입니다. 규칙이 잘못되면 락도 잘못됩니다.

## 개념 한눈에 보기

> Mutex는 한 시점에 한 흐름만 임계 구역에 들어가게 합니다. Semaphore는 N개까지 동시에 들어갈 수 있게 합니다. RLock(재진입 락)은 같은 흐름이 같은 락을 여러 번 잡을 수 있게 합니다. Condition variable은 "어떤 조건이 충족될 때까지" 기다리고 깨우는 메커니즘입니다.

```text
Mutex     : 입장 가능 인원 = 1
Semaphore : 입장 가능 인원 = N (예: DB 커넥션 풀 10개)
RLock     : 같은 사람이 여러 번 들어갈 수 있음 (재귀 함수 등)
Condition : "재고가 1 이상이 될 때까지" 같은 조건 대기
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 임계 구역 | 한 번에 하나의 흐름만 들어가야 하는 코드 구간 |
| 데드락 | 둘 이상의 흐름이 서로의 락을 기다리며 영원히 멈춘 상태 |
| 라이브락 | 락은 안 잡혔는데 서로 양보하느라 진행이 안 됨 |
| 기아(starvation) | 어떤 흐름이 계속 락을 못 받아 진행 못 함 |
| 락 호송(convoy) | 한 락을 기다리는 줄에 모든 흐름이 정렬되어 처리량이 폭락 |

## Before / After

**Before — "락만 걸면 안전":**

```python
import threading
lock_a = threading.Lock()
lock_b = threading.Lock()

def task1():
    with lock_a:
        with lock_b:
            ...

def task2():
    with lock_b:    # 순서가 다름!
        with lock_a:
            ...
```

두 함수가 동시에 돌면 데드락이 만들어집니다.

**After — "락 잡는 순서를 한 가지로 강제":**

```text
규칙: 항상 lock_a 먼저, lock_b 다음.
한 곳에서만 어겨도 시스템 전체가 멈출 수 있다.
```

## 실습: 단계별로 따라하기

### 1단계: 기본 mutex 사용

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

### 2단계: RLock으로 재귀 호출 보호

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

### 3단계: Semaphore로 동시 접속 제한

```python
import threading, time

pool = threading.Semaphore(3)   # 최대 3개

def query():
    with pool:
        time.sleep(0.5)         # DB 작업 흉내
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
# 두 스레드는 영원히 끝나지 않음 (Ctrl+C로 종료)
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

## 이 코드에서 주목할 점

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

## 실무에서는 이렇게 쓰입니다

- DB 커넥션 풀: semaphore로 동시 사용 한도 강제
- 캐시 갱신: 단일 mutex 또는 read-write 락으로 보호
- 백엔드 작업 큐: producer/consumer 패턴으로 락 회피
- GUI/게임: 메인 스레드 단일 소유 + 큐로 외부 입력 전달
- 분산 시스템: 같은 개념을 분산 락(예: Redis SETNX, etcd lease)으로 구현

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 락을 추가하기 전에 "이 락이 정확히 무엇을 보호하는가, 누가 풀 책임이 있는가, 어느 순서로 잡혀야 하는가"를 먼저 적습니다. 적을 수 없으면 락을 추가해서는 안 됩니다. 적힌 규칙이 코드 주석으로 남아 있어야 다음 사람이 같은 실수를 반복하지 않습니다.

또한 시니어는 "락 없는 설계가 가능한가"를 먼저 묻습니다. 메시지 통신, 불변 데이터, 단일 소유 같은 패턴은 잘못 쓸 여지를 처음부터 지웁니다. 동시성 코드는 잡은 락이 적을수록 좋고, 잡는 시간이 짧을수록 좋습니다.

## 체크리스트

- [ ] mutex, RLock, semaphore, condition의 차이를 안다
- [ ] 데드락의 네 가지 조건을 말할 수 있는가
- [ ] 락 순서 규약의 필요성을 이해한다
- [ ] 락의 비용(컨텍스트 스위치, 호송)을 안다
- [ ] 락 외 대안(큐, 불변, atomic)을 한 가지 이상 안다

## 연습 문제

1. 일부러 데드락 코드를 작성해 재현하고, 락 순서를 통일하는 것만으로 풀리는지 확인하세요. 결과를 한 문단으로 정리합니다.

2. semaphore로 동시에 3개만 실행되는 워커 풀을 작성하고, 10개 작업을 던졌을 때 처리 순서와 시간이 어떻게 되는지 관찰합니다.

3. 락을 사용하는 코드를 골라, 큐 기반 producer/consumer로 다시 써 보세요. 코드 길이와 이해도가 어떻게 변하는지 비교합니다.

## 정리 및 다음 단계

Mutex, semaphore, RLock, condition variable은 OS가 제공하는 동기화의 기본 도구입니다. 잡는 순서·범위·시간을 정확히 정해야 락이 안전하게 동작하고, 데드락의 네 조건 중 하나만 깨도 데드락은 사라집니다. 가장 안전한 락은 필요 없는 락이라는 사실을 잊지 마세요.

다음 글에서는 OS의 또 다른 기본기 — 메모리 관리로 넘어갑니다. 프로세스의 메모리는 어떻게 할당되고, 운영체제는 그 한정된 RAM을 어떻게 나누는지 봅니다.

- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 race condition](./04-concurrency-and-race-conditions.md)
- **lock, mutex, semaphore (현재 글)**
- 메모리 관리 (예정)
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [The Art of Multiprocessor Programming — Herlihy & Shavit](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Java Concurrency in Practice — Brian Goetz](https://jcip.net/)
- [Python threading.Semaphore](https://docs.python.org/3/library/threading.html#semaphore-objects)

Tags: Computer Science, 운영체제, 동기화, mutex, semaphore, 동시성

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
