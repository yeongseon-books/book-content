
# 병렬성과 멀티코어

> Computer Architecture 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 코어가 8개라면 프로그램이 정확히 8배 빨라질까요? 그렇지 않다면, 무엇이 그 한계를 정할까요?

> 클럭 속도는 2005년 무렵 멈췄고, 그 이후 모든 성능은 코어 수와 병렬성에서 옵니다. 하지만 코어를 더한다고 자동으로 빨라지지 않습니다. 어떤 일은 본질적으로 순차적이고, 코어 사이의 통신 비용은 절대 공짜가 아닙니다. 이 글은 멀티코어를 잘 쓰기 위한 머릿속 모델, 즉 동시성과 병렬성의 구분, 동기화 비용, Amdahl 법칙을 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 동시성(concurrency)과 병렬성(parallelism)의 차이
- 멀티코어 하드웨어 모델 (SMP, NUMA, 캐시 일관성)
- 동기화 원시 연산(lock, atomic, barrier)의 비용
- Amdahl의 법칙과 확장성의 한계

## 왜 중요한가

오늘날 모든 서버, 노트북, 휴대폰은 멀티코어입니다. 한 코어의 클럭은 더 이상 빨라지지 않으니, 성능을 끌어내려면 일을 여러 코어에 나누는 수밖에 없습니다. 하지만 잘못 나누면 더 느려지기까지 합니다. 락 경합, 캐시 핑퐁, false sharing 같은 함정이 곳곳에 있습니다.

> 병렬성은 공짜가 아닙니다. 매번 "이 일은 정말 병렬화할 만한가?"를 먼저 물어야 합니다.

## 개념 한눈에 보기

> 동시성은 "여러 일을 다루는 능력", 병렬성은 "여러 일을 동시에 실행". 멀티코어는 병렬성을 가능하게 하지만, 코어 사이에서 데이터를 주고받는 비용이 발생합니다. 캐시 일관성 프로토콜이 데이터를 자동으로 동기화해 주지만, 자주 같은 캐시라인을 다투면 성능이 급락합니다. Amdahl의 법칙은 "순차 부분이 5%면 코어를 무한히 늘려도 20배 이상은 못 간다"고 말합니다.

```text
   동시성 (concurrency)               병렬성 (parallelism)
   ───────────────────                ─────────────────────
   여러 작업을 다루는                  여러 작업을 동시에
   구조적 능력                         실행하는 물리적 능력
                                       (멀티코어 필요)

   single-core 가능                   multi-core 필요
   async/await, generator             threads, processes, SIMD
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 동시성 | 여러 작업을 인터리브하여 진행하는 구조 |
| 병렬성 | 여러 작업을 물리적으로 동시에 실행 |
| SMP | Symmetric Multi-Processing, 동등한 코어들 |
| NUMA | 코어마다 메모리 거리 다른 아키텍처 |
| 캐시 일관성 | 코어 간 캐시 데이터를 일관되게 유지 |
| Amdahl의 법칙 | 순차 부분이 전체 속도 향상의 상한 결정 |

## Before / After

**Before — 모든 코어를 의심 없이 사용:**

```python
# 8 코어니까 8배 빠를 거라고 가정
from multiprocessing import Pool

def task(x):
    return x * 2

with Pool(8) as p:
    result = p.map(task, range(100))   # 작업이 너무 작아 오버헤드가 더 큼
```

**After — 일의 크기와 통신 비용을 본다:**

```python
# 일이 충분히 크고 독립적인지 확인 후 병렬화
from multiprocessing import Pool

def heavy_task(n):
    return sum(i * i for i in range(n))

with Pool(8) as p:
    result = p.map(heavy_task, [10_000_000] * 8)   # 코어당 충분한 일
```

같은 도구지만 결과는 정반대입니다. 일이 너무 작으면 프로세스 간 통신이 계산보다 비싸집니다.

## 실습: 단계별로 따라하기

### 1단계: 코어 수 확인과 단순 병렬화

```python
import os, time
from multiprocessing import Pool

def work(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    print(f"논리 코어 수: {os.cpu_count()}")

    N = 5_000_000
    tasks = [N] * 8

    start = time.time()
    [work(n) for n in tasks]
    print(f"순차 실행: {time.time() - start:.2f}s")

    with Pool(processes=os.cpu_count()) as p:
        start = time.time()
        p.map(work, tasks)
        print(f"병렬 실행: {time.time() - start:.2f}s")
```

대개 4~6배 정도 빨라집니다. 8코어인데 8배가 안 되는 이유가 다음 단계의 주제입니다.

### 2단계: Amdahl 법칙 계산

```python
def amdahl_speedup(p, n):
    """p: 병렬화 가능 비율, n: 코어 수"""
    return 1 / ((1 - p) + p / n)

for serial in [0.05, 0.10, 0.20, 0.50]:
    p = 1 - serial
    print(f"순차 {serial*100:.0f}%:  코어 8 -> {amdahl_speedup(p, 8):.2f}x,"
          f"  코어 ∞ -> {1/serial:.1f}x")
```

순차 부분이 5%만 있어도 무한 코어로 가도 20배가 한계입니다. 이게 모든 분산 시스템의 천장입니다.

### 3단계: 락 경합 측정

```python
import threading, time

counter = 0
lock = threading.Lock()

def with_lock(iters):
    global counter
    for _ in range(iters):
        with lock:
            counter += 1

def without_lock(iters):
    global counter
    for _ in range(iters):
        counter += 1   # race condition, 결과는 신뢰 못함

ITERS = 1_000_000

# 락 사용
counter = 0
threads = [threading.Thread(target=with_lock, args=(ITERS,)) for _ in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"with lock:    {time.time()-start:.2f}s, counter={counter}")
```

스레드를 늘릴수록 빨라지기는커녕 락 경합으로 더 느려지는 지점이 옵니다.

### 4단계: false sharing 보기

```python
import threading, time

# 인접한 인덱스를 다른 스레드가 갱신하면 같은 캐시라인을 공유함
shared = [0] * 4

def bump(idx, iters):
    for _ in range(iters):
        shared[idx] += 1

# 인접 (false sharing 발생)
threads = [threading.Thread(target=bump, args=(i, 5_000_000)) for i in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"adjacent: {time.time()-start:.2f}s")

# 멀리 떨어뜨림 (false sharing 완화)
shared = [0] * 256
threads = [threading.Thread(target=bump, args=(i*64, 5_000_000)) for i in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"spaced:   {time.time()-start:.2f}s")
```

같은 양의 일인데 캐시라인 배치만 바꿔도 시간이 달라집니다. Python GIL 때문에 효과가 크진 않지만, C/Rust/Go에서는 두세 배 차이가 흔합니다.

### 5단계: 동시성 vs 병렬성 모델 비교

```python
import asyncio, time

async def io_task(i):
    await asyncio.sleep(0.1)
    return i

async def main():
    start = time.time()
    await asyncio.gather(*(io_task(i) for i in range(100)))
    print(f"asyncio (concurrency, 1 core): {time.time()-start:.2f}s")

asyncio.run(main())
```

100개의 I/O 작업이 0.1초가 아니라 약 0.1초에 끝납니다. 단일 코어에서도 동시성으로 충분한 경우입니다. 병렬성은 CPU 바운드일 때만 진짜 효과가 있습니다.

## 이 코드에서 주목할 점

- 단순히 코어 수를 늘리는 것만으로는 한계가 있습니다
- Amdahl 법칙은 순차 부분의 비율이 전체 한계를 결정함을 보여 줍니다
- 락 경합과 false sharing은 흔히 무시되는 성능 함정입니다
- I/O 바운드 작업에는 병렬성보다 동시성이 더 효과적입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 작은 일을 잘게 병렬화 | 통신 오버헤드가 더 큼 | 작업 단위를 키움 |
| GIL 잊고 CPU 바운드에 threading | 사실상 단일 코어 | multiprocessing 또는 C 확장 |
| 락 범위를 너무 넓게 | 직렬화로 회귀 | 락 범위 최소화, 락 분할 |
| false sharing 무시 | 캐시 핑퐁으로 성능 급락 | 데이터 패딩, 정렬 |
| 모든 일에 병렬화 시도 | 본질적으로 순차인 일 존재 | Amdahl로 상한 추정 후 결정 |

## 실무에서는 이렇게 쓰입니다

- 데이터 처리: Pandas/NumPy의 SIMD, Spark의 분산 병렬
- 웹 서버: 멀티프로세스 워커 + 비동기 I/O 결합
- 게임 엔진: 렌더링/물리/오디오를 코어별로 분리
- ML 학습: GPU 안의 수천 코어를 SIMD로 활용
- 데이터베이스: 병렬 쿼리, 파티셔닝

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "병렬화로 해결하자"는 말을 들으면 먼저 두 가지를 묻습니다. 하나, 이 작업은 정말 CPU 바운드인가? 둘, 병렬화 가능한 비율은 얼마인가? 대부분의 백엔드 작업은 사실 I/O 바운드이고, 그 경우 답은 동시성이지 병렬성이 아닙니다.

또한 시니어는 병렬화의 비용을 항상 측정합니다. 작업 분배, 결과 수집, 동기화, 캐시 일관성 트래픽 — 이 비용의 합이 병렬화 이득보다 작은지 확인하지 않으면 코어를 늘릴수록 느려지는 시스템을 만들게 됩니다. "작게 측정하고 점진적으로 코어를 늘리며 곡선을 그린다"가 검증된 작업 방식입니다.

## 체크리스트

- [ ] 동시성과 병렬성을 다른 사람에게 설명할 수 있는가
- [ ] Amdahl 법칙으로 상한을 추정할 수 있는가
- [ ] 락 경합과 false sharing을 식별할 수 있는가
- [ ] CPU 바운드와 I/O 바운드를 구분할 수 있는가
- [ ] 작업이 충분히 큰지 판단하고 병렬화 여부를 결정할 수 있는가

## 연습 문제

1. `amdahl_speedup` 함수로 순차 비율 1%, 5%, 10%일 때 코어 16, 64, 256에서의 속도 향상을 표로 그리세요. 어디서 수확체감이 오는지 확인합니다.

2. `multiprocessing.Pool`로 작업 크기를 1만, 10만, 100만, 1천만으로 바꿔 가며 4코어 병렬화 속도 향상을 측정하세요. 어느 크기부터 병렬화가 의미 있는지 찾습니다.

3. `threading`과 `asyncio`로 100개의 HTTP GET 요청을 비교하세요. CPU 사용률, 메모리, 시간을 표로 정리합니다.

## 정리 및 다음 단계

병렬성은 멀티코어 시대의 핵심이지만 자동이 아닙니다. 동시성과 구분해 사용하고, Amdahl 법칙으로 상한을 추정하고, 락 경합과 false sharing 같은 함정을 피해야 합니다. 시니어는 코어 수보다 "병렬화 가능한 비율"을 먼저 봅니다.

다음 글에서는 이 시리즈의 마지막 주제인 성능 측정과 분석을 다룹니다. CPU, 메모리, I/O, 병렬성을 모두 모아 "이 시스템은 왜 이만큼 빠른가/느린가"를 설명하는 사고 도구를 정리합니다.

- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
- [레지스터와 ALU](./04-registers-and-alu.md)
- [메모리 구조](./05-memory-organization.md)
- [캐시와 지역성](./06-cache-and-locality.md)
- [파이프라인](./07-pipelining.md)
- [I/O와 장치](./08-io-and-devices.md)
- **병렬성과 멀티코어 (현재 글)**
- 성능을 이해하는 법 (예정)
## 참고 자료

- [Wikipedia — Amdahl's law](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Wikipedia — Cache coherence](https://en.wikipedia.org/wiki/Cache_coherence)
- [Wikipedia — False sharing](https://en.wikipedia.org/wiki/False_sharing)
- [The Free Lunch Is Over (Herb Sutter, 2005)](http://www.gotw.ca/publications/concurrency-ddj.htm)

Tags: Computer Science, 컴퓨터 구조, 병렬성, 멀티코어, 동시성, 동기화

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
