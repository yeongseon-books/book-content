---
series: operating-systems-101
episode: 4
title: 동시성과 경쟁 상태
status: publish-ready
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
  - 경쟁 상태
  - 디버깅
  - 시스템
seo_description: 동시성이 만드는 경쟁 상태와 원자성, 가시성, 순서성의 핵심을 정리합니다.
last_reviewed: '2026-05-12'
---

# 동시성과 경쟁 상태

동시성 버그는 보통 개발 환경에서 크게 소리를 내지 않습니다. 테스트를 여러 번 통과하다가도, 부하가 올라가는 순간에만 데이터를 깨뜨리고 사라집니다.

이런 버그가 무서운 이유는 한 번 틀리는 것이 아니라, 어떤 결과가 나올지 예측하기 어려워진다는 데 있습니다. 그래서 경쟁 상태는 증상보다 구조를 먼저 이해해야 합니다.

이 글은 Operating Systems 101 시리즈의 4번째 글입니다.

## 이 글에서 다룰 문제

- 경쟁 상태는 정확히 언제 발생한다고 말할 수 있을까요?
- 원자성, 가시성, 순서성은 어떤 식으로 서로 다른 실패를 만들까요?
- 왜 "한 줄짜리 코드"도 안전하다고 볼 수 없을까요?
- 락 말고도 경쟁 상태를 줄이는 설계 방법은 무엇일까요?

> 경쟁 상태는 두 흐름이 같은 데이터를 건드린다는 사실만으로 생기지 않습니다. 그 결과가 실행 순서에 따라 달라질 때 비로소 문제가 되며, 운영체제의 스케줄러는 그 순서를 언제든 바꿀 수 있습니다.

## 기본 모델
> 두 스레드가 같은 변수에 동시에 접근하면, OS의 스케줄러가 임의의 시점에 흐름을 끊을 수 있습니다. 그 결과 한 작업의 중간 단계가 다른 작업의 단계와 섞여 실행되고, 최종 상태는 우리가 의도한 것과 다를 수 있습니다.

```text
Initial: count = 0   (both threads want to add 1)

Ideal                          Real
T1 read  0                     T1 read  0
T1 add   1                     T2 read  0   <- interleaves
T1 write 1                     T1 add   1
T2 read  1                     T1 write 1
T2 add   2                     T2 add   1
T2 write 2  -> 2               T2 write 1  -> 1 (lost update)
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "한 줄이니까 안전하겠지":**

```python
count = 0
def add():
    global count
    for _ in range(100_000):
        count += 1   # one line
```

이 한 줄은 사실 세 줄(읽기, 더하기, 쓰기)입니다.

**바꿔서 보면 — "쪼개진 단계가 섞일 수 있다":**

```text
T1: load count -> 100
T2: load count -> 100   <- same value
T1: add  -> 101
T2: add  -> 101
T1: store -> 101
T2: store -> 101         <- one increment vanished
```

이런 식으로 일부 증가가 통째로 사라지는 것이 경쟁 상태의 전형적 결과입니다.

## 단계별로 확인하기

### 1단계: 가장 단순한 경쟁 상태 재현

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
print(count)   # expected: 800_000, actual: usually less, varies per run
```

같은 코드를 여러 번 돌려 보면 매번 다른 값이 나옵니다. 이 비결정성이 가장 큰 단서입니다.

### 2단계: 바이트코드 분해로 한 줄이 여러 단계임을 확인

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
print(count)   # always 800_000
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

### 5단계: 공유를 줄여 경쟁 상태 피하기

```python
from queue import Queue
import threading

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

## 여기서 먼저 볼 점

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

## 실무에서는 이렇게 본다

- 백엔드 캐시: 동시 갱신을 락 또는 CAS(compare-and-swap)로 보호
- 카운터/메트릭: thread-local 누산 → 주기적 합치기 패턴
- 데이터베이스: 트랜잭션 격리 수준이 본질적으로 race 방지 메커니즘
- 분산 시스템: 여러 노드의 race는 분산 락 또는 원자적 연산으로 해결
- UI: 메인 스레드 외 접근을 차단하는 단일 소유 모델

## 체크리스트

- [ ] Race condition을 한 문장으로 정의할 수 있는가
- [ ] 원자성, 가시성, 순서성을 구분할 수 있는가
- [ ] "한 줄짜리 코드"가 원자적이지 않을 수 있다는 점을 안다
- [ ] 락 외의 동시성 전략(불변, 메시지, thread-local)을 안다
- [ ] 동시성 버그를 디버깅할 때 비결정성이 단서임을 안다

## 마무리와 다음 글

Race condition은 "한 줄"이라는 외관 뒤에 숨은 여러 단계가 섞이면서 발생합니다. 원자성, 가시성, 순서성이라는 세 축을 알면 이 버그를 정의할 언어가 생기고, 락 외에도 불변성·메시지·thread-local 같은 도구가 있다는 것을 알면 설계 단계에서부터 줄일 수 있습니다.

다음 글에서는 가장 자주 쓰이는 동기화 도구인 락(mutex)과 그 친척인 세마포어를 자세히 봅니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- **동시성과 경쟁 상태 (현재 글)**
- 락, 뮤텍스, 세마포어 (예정)
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

Tags: Computer Science, 운영체제, 동시성, 경쟁 상태, 디버깅, 시스템
