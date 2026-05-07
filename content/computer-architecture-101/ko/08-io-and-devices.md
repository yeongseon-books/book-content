---
series: computer-architecture-101
episode: 8
title: I/O와 장치
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
  - 컴퓨터 구조
  - I/O
  - 인터럽트
  - DMA
  - 장치
seo_description: CPU와 장치 사이의 I/O 모델, 폴링과 인터럽트, DMA, 그리고 메모리 매핑 I/O를 정리합니다.
last_reviewed: '2026-05-04'
---

# I/O와 장치

> Computer Architecture 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 디스크 읽기 한 번이 메모리 접근의 10만 배가 걸리는데, 그 시간 동안 CPU는 무엇을 하고 있을까요?

> CPU는 빠르고 장치는 느립니다. 키보드는 사람의 속도, 디스크는 밀리초, 네트워크는 그 너머의 세계에 있습니다. 이 격차를 메우는 방식이 폴링, 인터럽트, DMA이고, 장치를 보는 방식이 메모리 매핑 I/O입니다. 이 글은 그 안쪽을 들여다보면서 모든 시스템 콜과 비동기 프로그래밍의 출발점을 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- CPU와 장치의 속도 격차와 그 의미
- 폴링과 인터럽트 방식의 차이
- DMA(Direct Memory Access)의 역할
- 메모리 매핑 I/O와 포트 매핑 I/O

## 왜 중요한가

모든 비동기 프로그래밍, 모든 이벤트 루프, 모든 시스템 콜은 결국 "느린 장치를 효율적으로 다루기 위한" 추상화입니다. 인터럽트와 DMA가 없으면 한 글자 입력마다 CPU 전체가 멈춥니다. 이 메커니즘을 이해하면 epoll, async/await, kqueue 같은 도구가 왜 그런 모양인지 이해할 수 있습니다.

> 빠른 CPU는 느린 장치를 기다리지 않는 방법으로 설계되었고, 우리 코드도 같은 원리로 짜야 합니다.

## 개념 한눈에 보기

> CPU와 장치는 버스로 연결됩니다. CPU가 장치를 직접 계속 묻는 폴링 방식은 단순하지만 비효율적입니다. 인터럽트는 장치가 준비되면 CPU에 신호를 보내는 방식이고, DMA는 장치가 메모리에 직접 데이터를 쓰는 방식입니다. 메모리 매핑 I/O는 장치 레지스터를 일반 메모리 주소처럼 보이게 만듭니다.

```text
   +-----+        +-----+
   | CPU |<------>| RAM |
   +--+--+        +--+--+
      |              ^
      |              |  DMA (장치가 RAM에 직접 쓰기)
      |              |
   +--+----- BUS ----+--+
      |                |
   +--+--+         +--+--+
   | NIC |         | SSD |
   +-----+         +-----+
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 폴링(polling) | CPU가 장치 상태를 주기적으로 확인 |
| 인터럽트(interrupt) | 장치가 CPU에 신호를 보냄 |
| ISR | 인터럽트 서비스 루틴, 인터럽트 핸들러 |
| DMA | CPU 개입 없이 장치-메모리 데이터 전송 |
| MMIO | 메모리 매핑 I/O, 장치를 주소로 노출 |
| 시스템 콜 | 사용자 모드에서 커널의 I/O 기능 호출 |

## Before / After

**Before — 폴링으로 장치 대기:**

```python
# 가상의 폴링 루프
def wait_for_data(device):
    while not device.is_ready():
        pass   # CPU 100% 사용, 다른 작업 못함
    return device.read()
```

**After — 인터럽트 + 콜백:**

```python
# 가상의 인터럽트 모델
def on_data_ready(device):
    data = device.read()
    process(data)

device.register_interrupt(on_data_ready)
do_other_work()   # CPU는 다른 일을 함
# 장치가 준비되면 자동으로 on_data_ready 호출
```

같은 결과지만 CPU 활용률이 완전히 달라집니다. 운영체제는 이 인터럽트 메커니즘을 사용자 코드에 select/epoll/async로 노출합니다.

## 실습: 단계별로 따라하기

### 1단계: 장치 속도 비교 표 만들기

```python
# 대략적인 비용 (출처: Latency Numbers Every Programmer Should Know, 단위: ns)
LATENCY = {
    "L1 cache":          1,
    "Branch misprediction": 5,
    "L2 cache":          7,
    "Main memory":       100,
    "SSD random read":   100_000,
    "Round trip in DC":  500_000,
    "HDD seek":          10_000_000,
    "Internet (KR↔US)":  150_000_000,
}

base = LATENCY["L1 cache"]
for name, ns in LATENCY.items():
    print(f"{name:20s} {ns:>15,d} ns   (×{ns / base:>11,.0f} L1)")
```

이 격차가 비동기 프로그래밍의 존재 이유입니다. CPU는 이 시간 동안 다른 일을 해야 합니다.

### 2단계: 폴링 vs 인터럽트 시뮬레이션

```python
import time

class Device:
    def __init__(self, ready_after):
        self.start = time.time()
        self.ready_after = ready_after

    def is_ready(self):
        return time.time() - self.start >= self.ready_after

# 폴링: CPU가 계속 돈다
def busy_poll(dev):
    iterations = 0
    while not dev.is_ready():
        iterations += 1
    return iterations

dev = Device(ready_after=0.1)
print("폴링 반복 수:", busy_poll(dev))   # 수십만~수백만
```

폴링 방식은 단순하지만 100ms 동안 CPU가 다른 일을 못 합니다. 임베디드의 단순 시스템에서는 쓰지만 일반 OS는 인터럽트로 갑니다.

### 3단계: 인터럽트 모델 시뮬레이션

```python
import threading, time, queue

interrupts = queue.Queue()

def device_thread():
    time.sleep(0.1)              # 장치가 준비되기까지 대기
    interrupts.put("DATA_READY")  # 인터럽트 발생

threading.Thread(target=device_thread, daemon=True).start()

# CPU는 다른 일을 하다가 인터럽트 큐를 가끔 확인
work_done = 0
while interrupts.empty():
    work_done += 1
    if work_done % 1_000_000 == 0:
        pass

print(f"인터럽트 도착, 그동안 {work_done:,} 단위 작업 완료")
```

threading.Queue는 OS 인터럽트를 정확히 모사하진 않지만, "장치 이벤트가 비동기로 도착한다"는 모델을 보여 줍니다.

### 4단계: DMA 흉내 — 작업 분리

```python
import threading, time

shared_buffer = []

def dma_transfer(source_size):
    """장치가 RAM에 직접 데이터를 쓰는 흉내. CPU는 개입하지 않음"""
    time.sleep(0.05)
    shared_buffer.extend(range(source_size))

threading.Thread(target=dma_transfer, args=(1_000_000,)).start()

# CPU는 그동안 자기 일
total = sum(i * i for i in range(100_000))
print(f"CPU 작업 결과: {total}")
print(f"DMA 후 버퍼 크기: {len(shared_buffer)}")
```

실제 DMA는 OS와 장치 컨트롤러가 협력해 수행하지만, 본질은 "데이터 전송이 CPU 사이클을 거의 쓰지 않는다"는 점입니다.

### 5단계: select로 진짜 인터럽트 모델 사용

```python
import select, socket, sys

# 표준 입력이 읽을 준비가 됐을 때만 처리하는 패턴
print("문자를 입력하세요(2초 안에)...")
ready, _, _ = select.select([sys.stdin], [], [], 2.0)
if ready:
    line = sys.stdin.readline()
    print(f"입력: {line.strip()}")
else:
    print("타임아웃: CPU는 그동안 자유롭게 다른 일을 할 수 있습니다")
```

`select`는 OS의 인터럽트 메커니즘을 사용자 코드에 노출하는 가장 오래된 인터페이스입니다. epoll, kqueue, IOCP는 이를 더 효율적으로 만든 변형입니다.

## 이 코드에서 주목할 점

- 장치 속도는 CPU의 1만 배에서 1억 배까지 느릴 수 있습니다
- 폴링은 단순하지만 CPU를 묶어 둡니다
- 인터럽트는 비동기로 알려주므로 CPU가 다른 일을 할 수 있습니다
- DMA는 데이터 전송 자체에서도 CPU를 해방시킵니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 동기 I/O로 핫 패스 구성 | 한 요청이 전체를 막음 | async/await, epoll |
| busy loop로 대기 | CPU 100%, 발열·전력 | sleep 또는 이벤트 대기 |
| 인터럽트 핸들러에서 무거운 작업 | 다른 인터럽트 지연 | 핸들러는 짧게, 큐로 위임 |
| DMA 후 캐시 동기화 누락 | 잘못된 데이터 읽음 | 메모리 배리어, flush |
| 장치 레지스터 정렬 무시 | 잘못된 비트 위치 접근 | 데이터시트의 비트맵 따름 |

## 실무에서는 이렇게 쓰입니다

- 웹 서버: epoll/kqueue 기반 이벤트 루프(nginx, Node.js)로 수만 연결 처리
- 데이터베이스: 비동기 I/O와 DMA로 디스크 대역폭 최대 활용
- 임베디드: GPIO 인터럽트로 센서 입력 즉시 처리
- GPU 컴퓨팅: PCIe DMA로 호스트-디바이스 메모리 전송
- 운영체제: 인터럽트 컨트롤러로 우선순위 있는 장치 관리

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 코드의 I/O 모델을 가장 먼저 봅니다. 동기 I/O 한 줄이 핫 패스에 끼어 있으면 그 시스템의 처리량 상한이 정해집니다. 그래서 새 시스템을 설계할 때 "이 작업은 CPU 바운드인가 I/O 바운드인가"를 먼저 묻고, 그에 따라 스레드 모델, 비동기 모델, 큐 구조를 다르게 잡습니다.

또한 시니어는 "I/O 비용은 항상 측정한다"는 원칙을 지킵니다. 디스크 한 번이 100us냐 10ms냐, 네트워크 라운드트립이 1ms냐 100ms냐에 따라 같은 알고리즘의 의미가 완전히 달라집니다. Latency Numbers는 출발점일 뿐이고, 실제 시스템의 숫자가 진실입니다.

## 체크리스트

- [ ] 메인 메모리와 SSD의 비용 차이를 한 자릿수 단위로 안다
- [ ] 폴링과 인터럽트의 차이를 설명할 수 있는가
- [ ] DMA가 CPU에 어떤 이득을 주는지 안다
- [ ] select/epoll이 OS의 어떤 메커니즘을 노출하는지 안다
- [ ] 동기 I/O와 비동기 I/O의 트레이드오프를 안다

## 연습 문제

1. 위의 `LATENCY` 표를 사용해, "1000개의 SSD 랜덤 읽기"와 "1000개의 메모리 접근"의 시간을 계산하세요. 그 차이가 비동기 I/O 도입을 정당화하는지 판단합니다.

2. `select.select`로 stdin과 두 개의 가상 파이프를 동시에 모니터링하는 코드를 작성하세요. 어떤 입력이 먼저 오는지에 따라 다른 메시지를 출력합니다.

3. 자신이 사용하는 라이브러리(예: `requests` vs `httpx.AsyncClient`)에서 같은 URL을 100번 동시 요청하는 시간을 비교하세요. 동기와 비동기의 차이를 측정합니다.

## 정리 및 다음 단계

CPU와 장치 사이의 거대한 속도 격차를 메우는 방식이 폴링, 인터럽트, DMA입니다. 이 메커니즘들이 OS의 select, epoll, async/await로 사용자 코드에까지 닿고, 거기서 모든 비동기 프로그래밍이 시작됩니다. I/O 모델을 먼저 보는 습관이 시스템 설계의 출발점입니다.

다음 글에서는 한 코어의 한계를 넘어서는 이야기, 즉 병렬성과 멀티코어를 살펴봅니다. 여러 CPU가 함께 일하는 모델과 그 안에서 생기는 동기화 문제를 다룹니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
- [레지스터와 ALU](./04-registers-and-alu.md)
- [메모리 구조](./05-memory-organization.md)
- [캐시와 지역성](./06-cache-and-locality.md)
- [파이프라인](./07-pipelining.md)
- **I/O와 장치 (현재 글)**
- 병렬성과 멀티코어 (예정)
- 성능을 이해하는 법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Direct memory access](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Wikipedia — Interrupt](https://en.wikipedia.org/wiki/Interrupt)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [The C10K problem (Dan Kegel)](http://www.kegel.com/c10k.html)

Tags: Computer Science, 컴퓨터 구조, I/O, 인터럽트, DMA, 장치
