---
series: operating-systems-101
episode: 4
title: 동시성과 race condition
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
  - 동시성
  - race condition
  - 디버깅
  - 시스템
seo_description: 동시성이 만드는 race condition의 정체와 원자성, 가시성, 순서성의 세 가지 위반을 정리합니다.
last_reviewed: '2026-05-04'
---

# 동시성과 race condition

> Operating Systems 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 단일 스레드에서는 멀쩡하던 코드가 왜 멀티스레드로 옮기면 가끔, 그것도 재현하기 어려운 방식으로 깨질까요?

> Race condition은 둘 이상의 흐름이 같은 데이터에 동시에 접근하면서 그 결과가 실행 순서에 따라 달라지는 상황입니다. 한 줄짜리 `count += 1`도 사실은 읽고-더하고-쓰는 세 단계로 쪼개지고, 그 사이에 다른 스레드가 끼어들 수 있습니다. 이 글에서는 동시성 버그가 왜 그렇게 잘 숨고, 어떤 종류가 있으며, 어떤 원칙으로 막을 수 있는지를 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- Race condition의 정의와 왜 재현이 어려운가
- 동시성 위반의 세 가지 축 — 원자성, 가시성, 순서성
- 메모리 모델과 가시성의 관계
- 동시성 버그를 줄이는 설계 원칙

## 왜 중요한가

동시성 버그는 평소에는 잠잠하다가 운영 환경에서, 그것도 부하가 몰리는 순간 터집니다. 테스트 환경에서는 한 번도 안 보이던 버그가 사용자 트래픽이 몰리는 새벽 두 시에 데이터를 망가뜨립니다. 이 패턴을 한 번이라도 겪으면 "동시성 코드는 신중하게"가 단순한 격언이 아님을 알게 됩니다.

> Race condition은 잘못된 결과보다 더 무서운, "어떤 결과가 나올지 알 수 없음"이라는 상태를 만듭니다.

## 개념 한눈에 보기

> 두 스레드가 같은 변수에 동시에 접근하면, OS의 스케줄러가 임의의 시점에 흐름을 끊을 수 있습니다. 그 결과 한 작업의 중간 단계가 다른 작업의 단계와 섞여 실행되고, 최종 상태는 우리가 의도한 것과 다를 수 있습니다.

```text
초기: count = 0  (두 스레드가 1을 더하려 함)

이상적                          현실
T1 read  0                      T1 read  0
T1 add   1                      T2 read  0   <- 끼어듦
T1 write 1                      T1 add   1
T2 read  1                      T1 write 1
T2 add   2                      T2 add   1
T2 write 2  -> 2                T2 write 1  -> 1 (틀림)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| Race condition | 결과가 실행 순서에 따라 달라지는 상황 |
| 임계 구역(critical section) | 한 번에 하나의 흐름만 들어가야 하는 코드 구간 |
| 원자성(atomicity) | 한 작업이 외부에서 보면 더 쪼개지지 않게 동작하는 성질 |
| 가시성(visibility) | 한 스레드의 변경이 다른 스레드에 보이는 시점 |
| 메모리 모델 | 언어/하드웨어가 보장하는 동시 접근의 규칙 |

## Before / After

**Before — "한 줄이니까 안전하겠지":**

```python
count = 0
def add():
    global count
    for _ in range(100_000):
        count += 1   # 한 줄
```

이 한 줄은 사실 세 줄(읽기, 더하기, 쓰기)입니다.

**After — "쪼개진 단계가 섞일 수 있다":**

```text
스레드 1: load count -> 100
스레드 2: load count -> 100   <- 같은 값을 읽음
스레드 1: add  -> 101
스레드 2: add  -> 101
스레드 1: store -> 101
스레드 2: store -> 101         <- 한 번의 증가가 사라짐
```

이런 식으로 일부 증가가 통째로 사라지는 것이 race condition의 전형적 결과입니다.

## 실습: 단계별로 따라하기

### 1단계: 가장 단순한 race 재현

```python
import threading

count = 0
def add():
    global count
    for _ in range(100_000):
        count += 1

ts = [threading.Thread(target=add) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
print(count)   # 기대: 800_000, 실제: 그보다 작음 (실행마다 다름)
```

같은 코드를 여러 번 돌려 보면 매번 다른 값이 나옵니다. 이 비결정성이 가장 큰 단서입니다.

### 2단계: `dis`로 한 줄이 여러 단계임을 확인

```python
import dis

def add_one(d):
    d['k'] += 1

dis.dis(add_one)
```

`LOAD_FAST`, `LOAD_CONST`, `INPLACE_ADD`, `STORE_SUBSCR` 같은 여러 바이트코드로 분해됩니다. 그 중간에 다른 스레드가 들어올 수 있습니다.

### 3단계: 락으로 임계 구역 보호

```python
import threading

count = 0
lock = threading.Lock()

def add():
    global count
    for _ in range(100_000):
        with lock:
            count += 1

ts = [threading.Thread(target=add) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
print(count)   # 항상 800_000
```

락은 임계 구역에 한 번에 한 스레드만 들어가도록 강제합니다. 결과가 이제 결정적이 됩니다.

### 4단계: 가시성 문제 직관

```python
import threading, time

stop = False
def worker():
    while not stop:
        pass

t = threading.Thread(target=worker)
t.start()
time.sleep(0.1)
stop = True
t.join()
```

CPython에서는 보통 동작하지만, 일반적으로(다른 언어/JIT 환경에서는) `stop`의 변경이 다른 스레드에 즉시 보이지 않을 수 있습니다. 이런 가시성 문제는 변수의 값이 "캐시"에 머무르는 한 끝나지 않습니다.

### 5단계: 원자적 연산으로 race 회피

```python
from collections import Counter
import threading

counter = Counter()
def add():
    for _ in range(100_000):
        counter['k'] += 1   # 여전히 안전하지 않음! 비교 대상

# 안전한 대안: queue 또는 thread-local로 모은 후 합치기
from queue import Queue
q = Queue()
def safe_add():
    local = 0
    for _ in range(100_000):
        local += 1
    q.put(local)

ts = [threading.Thread(target=safe_add) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
total = 0
while not q.empty():
    total += q.get()
print(total)
```

공유 상태를 줄이는 것이 락을 잘 쓰는 것보다 자주 더 안전합니다.

## 이 코드에서 주목할 점

- "한 줄"이라는 외관은 원자성과 무관합니다
- 같은 코드가 매번 다른 결과를 내면 race를 의심합니다
- 락은 강력하지만 잡는 시간이 길어지면 성능을 죽입니다
- 공유 상태를 줄이는 설계가 락보다 자주 더 좋은 답입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| "테스트 통과했으니 안전" | 부하 환경에서만 깨짐 | 부하 테스트와 fuzz 테스트로 검증 |
| 락을 너무 좁게 잡음 | 보호 안 된 시점에서 race | 임계 구역 전체를 한 번에 감싸기 |
| 락을 너무 넓게 잡음 | 사실상 직렬화, 성능 폭락 | 가능한 좁게, 측정으로 균형 |
| `print`로 디버그 | 출력 자체가 락을 잡아 버그가 사라짐 | 로깅으로 분리, 결정적 테스트 |
| 가시성 문제 무시 | 한 스레드의 변경이 다른 곳에 안 보임 | 메모리 모델 학습, 적절한 동기화 사용 |

## 실무에서는 이렇게 쓰입니다

- 백엔드 캐시: 동시 갱신을 락 또는 CAS(compare-and-swap)로 보호
- 카운터/메트릭: thread-local 누산 → 주기적 합치기 패턴
- 데이터베이스: 트랜잭션 격리 수준이 본질적으로 race 방지 메커니즘
- 분산 시스템: 여러 노드의 race는 분산 락 또는 원자적 연산으로 해결
- UI: 메인 스레드 외 접근을 차단하는 단일 소유 모델

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "동시성 버그가 가끔 보인다"는 보고를 받으면 곧장 코드 수정에 들어가지 않습니다. 먼저 어떤 데이터가 공유되는지, 누가 읽고 누가 쓰는지, 락은 무엇이 보호하고 있는지를 표로 정리합니다. 이 표가 명확해야 비로소 수정이 의미 있는 수정이 됩니다.

또한 시니어는 "락이 답이 아닐 때가 많다"는 점을 압니다. 공유 상태를 없애기, 메시지로 통신하기, 불변 데이터 사용하기 — 이런 설계는 잘못 쓸 여지를 처음부터 줄여 줍니다. 가장 안전한 임계 구역은 존재하지 않는 임계 구역입니다.

## 체크리스트

- [ ] Race condition을 한 문장으로 정의할 수 있는가
- [ ] 원자성, 가시성, 순서성을 구분할 수 있는가
- [ ] "한 줄짜리 코드"가 원자적이지 않을 수 있다는 점을 안다
- [ ] 락 외의 동시성 전략(불변, 메시지, thread-local)을 안다
- [ ] 동시성 버그를 디버깅할 때 비결정성이 단서임을 안다

## 연습 문제

1. 8개의 스레드가 같은 정수를 1만 번씩 증가시키는 코드를 작성하고, (a) 락 없음, (b) 좁은 락, (c) 넓은 락 세 버전을 실행해 결과와 시간을 비교하세요. 표로 정리합니다.

2. 자신의 프로젝트에서 공유 상태가 있는 코드를 찾아, "공유를 줄이는" 설계로 다시 써 보세요. 어떤 부분이 단순해지고 어떤 부분이 복잡해지는지 한 문단으로 정리합니다.

3. `print` 대신 `logging`을 사용하도록 동시성 디버그 코드를 바꾸어 보세요. 출력이 섞이는 정도가 어떻게 달라지는지, 그리고 그 이유를 설명합니다.

## 정리 및 다음 단계

Race condition은 "한 줄"이라는 외관 뒤에 숨은 여러 단계가 섞이면서 발생합니다. 원자성, 가시성, 순서성이라는 세 축을 알면 이 버그를 정의할 언어가 생기고, 락 외에도 불변성·메시지·thread-local 같은 도구가 있다는 것을 알면 설계 단계에서부터 줄일 수 있습니다.

다음 글에서는 가장 자주 쓰이는 동기화 도구인 락(mutex)과 그 친척인 세마포어를 자세히 봅니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- **동시성과 race condition (현재 글)**
- lock, mutex, semaphore (예정)
- 메모리 관리 (예정)
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Java Concurrency in Practice — Brian Goetz](https://jcip.net/)
- [The Art of Multiprocessor Programming — Herlihy & Shavit](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Python threading documentation](https://docs.python.org/3/library/threading.html)

Tags: Computer Science, 운영체제, 동시성, race condition, 디버깅, 시스템
