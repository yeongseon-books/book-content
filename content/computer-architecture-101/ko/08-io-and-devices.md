---
series: computer-architecture-101
episode: 8
title: "Computer Architecture 101 (8/10): I/O와 장치"
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
  - 컴퓨터 구조
  - I/O
  - 인터럽트
  - DMA
  - 장치
seo_description: 폴링, 인터럽트, DMA가 CPU와 느린 장치 사이의 간극을 어떻게 메우는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Architecture 101 (8/10): I/O와 장치

디스크 한 번 읽는 시간은 메모리 접근보다 수만에서 수십만 배 길 수 있습니다. 그렇다면 CPU는 그동안 무엇을 하고 있을까요? 이 글은 Computer Architecture 101 시리즈의 여덟 번째 글입니다. 여기서는 CPU와 느린 장치 사이의 속도 차이를 폴링, 인터럽트, DMA가 어떻게 메우는지 짚어보겠습니다.

이 주제는 단순히 하드웨어 교양에 머물지 않습니다. `select`, `epoll`, `async/await`, 이벤트 루프, 시스템 콜 같은 운영체제와 애플리케이션 설계의 핵심이 모두 여기서 출발하기 때문입니다.


![Computer Architecture 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/08/08-01-big-picture.ko.png)
*Computer Architecture 101 8장 흐름 개요*

## 먼저 던지는 질문

- CPU와 장치의 속도 차이는 얼마나 클까요?
- 폴링과 인터럽트는 어떻게 다를까요?
- DMA는 왜 CPU를 더 자유롭게 만들까요?

## 왜 중요한가

모든 비동기 프로그램은 결국 느린 장치를 효율적으로 다루는 문제를 추상화한 것입니다. 인터럽트와 DMA가 없다면 키 입력 하나, 디스크 읽기 하나가 CPU 전체를 묶어 버릴 것입니다.

따라서 I/O 모델을 이해하면 `epoll`이나 `async/await`가 임의의 API가 아니라, 하드웨어 현실에 대한 운영체제의 응답이라는 점이 보입니다.

## 한눈에 보는 개념

CPU와 장치는 버스로 연결되고, 폴링은 CPU가 계속 묻는 방식, 인터럽트는 장치가 준비되었음을 알리는 방식, DMA는 장치가 RAM에 직접 쓰는 방식입니다.

```text
   +-----+        +-----+
   | CPU |<------>| RAM |
   +--+--+        +--+--+
      |              ^
      |              |  DMA (device writes RAM directly)
      |              |
   +--+----- BUS ----+--+
      |                |
   +--+--+         +--+--+
   | NIC |         | SSD |
   +-----+         +-----+
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Polling | CPU가 반복해서 장치 상태를 확인하는 방식 |
| Interrupt | 장치가 CPU에 신호를 보내는 방식 |
| ISR | 인터럽트 서비스 루틴 |
| DMA | CPU를 거치지 않고 장치가 메모리로 전송 |
| MMIO | 메모리 매핑 I/O, 장치를 주소처럼 노출 |
| System call | 사용자 모드에서 커널 I/O 서비스로 들어가는 경로 |

## 적용 전과 후

**Before — 폴링으로 장치 대기:**

```python
# Synthetic polling loop
def wait_for_data(device):
    while not device.is_ready():
        pass   # CPU pegged at 100%, no other work
    return device.read()
```

**After — 인터럽트 + 콜백:**

```python
# Synthetic interrupt model
def on_data_ready(device):
    data = device.read()
    process(data)

device.register_interrupt(on_data_ready)
do_other_work()   # CPU continues working
# When the device is ready, on_data_ready is called automatically
```

같은 결과를 얻더라도 CPU 활용 방식은 완전히 달라집니다.

## 단계별로 따라가기

### 1단계: 장치 속도 표 만들기

```python
# Approximate costs (Latency Numbers Every Programmer Should Know, in ns)
LATENCY = {
    "L1 cache":          1,
    "Branch misprediction": 5,
    "L2 cache":          7,
    "Main memory":       100,
    "SSD random read":   100_000,
    "Round trip in DC":  500_000,
    "HDD seek":          10_000_000,
    "Internet (KR<->US)": 150_000_000,
}

base = LATENCY["L1 cache"]
for name, ns in LATENCY.items():
    print(f"{name:20s} {ns:>15,d} ns   (x{ns / base:>11,.0f} L1)")
```

이 표만 봐도 왜 CPU가 기다리지 않고 다른 일을 해야 하는지 감이 옵니다.

### 2단계: 폴링 시뮬레이션

```python
import time

class Device:
    def __init__(self, ready_after):
        self.start = time.time()
        self.ready_after = ready_after

    def is_ready(self):
        return time.time() - self.start >= self.ready_after

def busy_poll(dev):
    iterations = 0
    while not dev.is_ready():
        iterations += 1
    return iterations

dev = Device(ready_after=0.1)
print("polling iterations:", busy_poll(dev))   # hundreds of thousands
```

단순하지만 CPU는 그 시간 동안 다른 유용한 일을 하지 못합니다.

### 3단계: 인터럽트 모델 시뮬레이션

```python
import threading, time, queue

interrupts = queue.Queue()

def device_thread():
    time.sleep(0.1)              # device gets ready
    interrupts.put("DATA_READY")  # raise an interrupt

threading.Thread(target=device_thread, daemon=True).start()

# CPU does other work and occasionally checks the queue
work_done = 0
while interrupts.empty():
    work_done += 1
    if work_done % 1_000_000 == 0:
        pass

print(f"interrupt arrived; finished {work_done:,} units of work in the meantime")
```

정확한 OS 인터럽트는 아니지만, 이벤트가 비동기로 도착하고 CPU는 그동안 다른 일을 할 수 있다는 모델을 잘 보여 줍니다.

### 4단계: DMA 흉내내기

```python
import threading, time

shared_buffer = []

def dma_transfer(source_size):
    """Device writes RAM directly. CPU is not involved."""
    time.sleep(0.05)
    shared_buffer.extend(range(source_size))

threading.Thread(target=dma_transfer, args=(1_000_000,)).start()

# CPU does its own work meanwhile
total = sum(i * i for i in range(100_000))
print(f"CPU result: {total}")
print(f"buffer after DMA: {len(shared_buffer)}")
```

실제 DMA는 더 정교하지만, 본질은 데이터 이동에서조차 CPU 사이클을 거의 쓰지 않는다는 점입니다.

### 5단계: `select`로 실제 패턴 보기

```python
import select, sys

print("Type something within 2 seconds...")
ready, _, _ = select.select([sys.stdin], [], [], 2.0)
if ready:
    line = sys.stdin.readline()
    print(f"input: {line.strip()}")
else:
    print("timeout: the CPU was free to do other work")
```

`select`는 사용자 코드가 운영체제의 인터럽트 기반 I/O 모델을 접하는 가장 오래된 창구 중 하나입니다.

## 이 코드에서 먼저 봐야 할 점

- 장치는 CPU보다 1만 배에서 1억 배까지 느릴 수 있습니다.
- 폴링은 단순하지만 CPU를 태웁니다.
- 인터럽트는 CPU가 다른 일을 하게 만듭니다.
- DMA는 데이터 이동 자체에서도 CPU를 해방합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 핫 패스에서 동기 I/O 사용 | 하나의 대기가 전체를 막음 | async/await, epoll 검토 |
| busy loop 대기 | CPU 100%, 발열 증가 | sleep 또는 이벤트 대기 |
| 인터럽트 핸들러에서 무거운 작업 | 다른 인터럽트 지연 | 핸들러는 짧게 유지 |
| DMA 후 캐시 동기화 무시 | 오래된 데이터 읽기 | 메모리 배리어와 flush 사용 |
| 장치 레지스터 정렬 무시 | 잘못된 비트 접근 | 데이터시트 준수 |

## 실무에서는 이렇게 드러납니다

- 웹 서버는 epoll/kqueue 이벤트 루프로 수만 연결을 처리합니다.
- 데이터베이스는 비동기 I/O와 DMA로 디스크 대역폭을 최대화합니다.
- 임베디드는 GPIO 인터럽트로 센서 입력을 즉시 처리합니다.
- GPU 컴퓨팅은 PCIe DMA로 호스트-디바이스 메모리를 옮깁니다.
- 운영체제는 인터럽트 컨트롤러로 장치 우선순위를 관리합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 시스템을 볼 때 먼저 I/O 모델을 봅니다. CPU 바운드인지, I/O 바운드인지, 블로킹 호출이 핫 패스에 있는지 먼저 확인합니다. 같은 알고리즘이라도 병목이 장치 대기라면 스레드 모델, 큐 구조, async 모델 선택이 전부 달라지기 때문입니다.

또한 I/O 비용은 반드시 측정해야 한다고 생각합니다. SSD 한 번이 100μs인지 10ms인지, 네트워크 RTT가 1ms인지 100ms인지에 따라 같은 코드의 의미가 완전히 달라집니다. 대략적인 상식은 출발점일 뿐이고, 실제 시스템 수치가 진실입니다.

## 체크리스트

- [ ] 메인 메모리와 SSD 비용 차이를 대략 설명할 수 있는가
- [ ] 폴링과 인터럽트 차이를 설명할 수 있는가
- [ ] DMA가 CPU에 돌려주는 이득을 말할 수 있는가
- [ ] `select`/`epoll`이 어떤 메커니즘을 노출하는지 아는가
- [ ] 동기 I/O와 비동기 I/O의 트레이드오프를 설명할 수 있는가

## 연습 문제

1. `LATENCY` 표로 메모리 접근 1000번과 SSD 랜덤 읽기 1000번의 차이를 계산해 보세요.

2. `select.select`를 표준 입력과 파이프 둘 이상에 동시에 걸어 어느 이벤트가 먼저 오는지 비교해 보세요.

3. 동기 HTTP 클라이언트와 비동기 클라이언트를 같은 수의 동시 요청으로 비교해 시간과 CPU 사용량 차이를 측정해 보세요.

## 정리 및 다음 글

CPU와 장치 사이의 속도 차이는 너무 크기 때문에, 기다리는 방식 자체를 바꾸지 않으면 시스템 전체가 느려집니다. 폴링, 인터럽트, DMA는 이 간극을 메우는 세 가지 핵심 메커니즘이고, 운영체제는 이를 `select`, `epoll`, `async/await` 같은 인터페이스로 노출합니다.

다음 글에서는 단일 코어의 한계를 넘어 멀티코어 시대로 갑니다. 병렬성과 동시성의 차이, 동기화 비용, 그리고 여러 코어를 잘 쓰는 사고법을 짚어보겠습니다.

## 심화 학습: I/O 메커니즘과 버스 프로토콜 분석

### CPU와 장치의 속도 격차 정량화

```python
def io_speed_comparison():
    """CPU와 다양한 I/O 장치의 속도 격차 비교."""
    # 단위: ns (나노초)
    devices = {
        'CPU 레지스터 접근':        0.3,
        'L1 캐시':                  1,
        'L3 캐시':                  10,
        'DRAM':                     100,
        'NVMe SSD (4KB 랜덤 읽기)': 10_000,       # 10μs
        'SATA SSD':                 100_000,      # 100μs
        'HDD (7200RPM)':            5_000_000,    # 5ms
        '네트워크 (같은 DC)':       500_000,      # 500μs
        '네트워크 (대륙간)':        100_000_000,  # 100ms
    }
    
    cpu_cycle = 0.3  # ns
    print(f"{'장치':<25} {'지연(ns)':>12} {'CPU 사이클 환산':>15}")
    print("-" * 55)
    for name, latency in devices.items():
        cycles = latency / cpu_cycle
        print(f"{name:<25} {latency:>12,.0f} {cycles:>15,.0f}")

io_speed_comparison()
```

출력:
```text
장치                         지연(ns)   CPU 사이클 환산
-------------------------------------------------------
CPU 레지스터 접근                    0              1
L1 캐시                              1              3
L3 캐시                             10             33
DRAM                               100            333
NVMe SSD (4KB 랜덤 읽기)        10,000         33,333
SATA SSD                       100,000        333,333
HDD (7200RPM)                5,000,000     16,666,667
네트워크 (같은 DC)             500,000      1,666,667
네트워크 (대륙간)          100,000,000    333,333,333
```

NVMe SSD 하나 읽는 동안 CPU는 33,000 명령어를 실행할 수 있습니다. 이것이 비동기 I/O와 DMA가 필수인 이유입니다.

### 폴링 vs 인터럽트: 언제 무엇을 선택하는가

```python
def polling_vs_interrupt_cost(event_rate_hz: float, poll_cost_cycles: int,
                               interrupt_cost_cycles: int, 
                               cpu_freq_ghz: float = 3.0) -> dict:
    """폴링과 인터럽트 방식의 CPU 오버헤드 비교."""
    cycles_per_sec = cpu_freq_ghz * 1e9
    
    # 폴링: 매번 상태 확인 (보통 busy-wait 또는 주기적 폴링)
    # 가정: 이벤트 빈도와 같은 빈도로 폴링
    poll_overhead = event_rate_hz * poll_cost_cycles / cycles_per_sec
    
    # 인터럽트: 이벤트 발생 시만 처리
    # 인터럽트 비용 = 컨텍스트 저장 + ISR + 복원
    interrupt_overhead = event_rate_hz * interrupt_cost_cycles / cycles_per_sec
    
    return {
        'polling_cpu_usage': poll_overhead,
        'interrupt_cpu_usage': interrupt_overhead,
        'better': 'polling' if poll_overhead < interrupt_overhead else 'interrupt'
    }

# 다양한 이벤트 빈도에서 비교
print(f"{'이벤트 빈도':>15} {'폴링 CPU%':>10} {'인터럽트 CPU%':>13} {'유리한 방식':>12}")
for rate in [100, 1000, 10000, 100000, 1000000]:
    r = polling_vs_interrupt_cost(rate, poll_cost_cycles=20, interrupt_cost_cycles=500)
    print(f"{rate:>15,} {r['polling_cpu_usage']:>10.4%} "
          f"{r['interrupt_cpu_usage']:>13.4%} {r['better']:>12}")
```

출력:
```text
    이벤트 빈도   폴링 CPU%  인터럽트 CPU%     유리한 방식
            100     0.0001%       0.0017%      polling
          1,000     0.0007%       0.0167%      polling
         10,000     0.0067%       0.1667%      polling
        100,000     0.0667%       1.6667%      polling
      1,000,000     0.6667%      16.6667%      polling
```

고빈도 I/O(네트워크 10Gbps, NVMe)에서는 폴링이 유리합니다. DPDK, SPDK 같은 고성능 I/O 프레임워크가 인터럽트 대신 폴링을 사용하는 이유입니다.

반대로 저빈도 이벤트(키보드, 마우스)에서 폴링은 CPU를 낭비합니다. 인터럽트가 적합합니다.

### DMA 동작 상세

```text
DMA 전송 과정:
┌──────┐  1. 전송 설정      ┌──────────┐
│ CPU  │──────────────────►│ DMA      │
│      │  (소스, 목적지,    │Controller│
│      │   크기, 방향)      │          │
└──┬───┘                   └──┬───────┘
   │                          │
   │ 4. 완료 인터럽트         │ 2. 버스 마스터링
   │◄─────────────────────────│    (CPU 없이 전송)
   │                          │
   │     ┌────────────┐       │ 3. 데이터 전송
   │     │   Memory   │◄──────┘
   │     └────────────┘
   │
   ▼ CPU는 DMA 동안 다른 작업 수행 가능
```

```python
def dma_vs_programmed_io(data_size_bytes: int, bus_width: int = 8,
                          cpu_freq_ghz: float = 3.0,
                          dma_setup_cycles: int = 1000) -> dict:
    """DMA vs Programmed I/O 비교."""
    cycles_per_sec = cpu_freq_ghz * 1e9
    
    # Programmed I/O: CPU가 매 바이트/워드를 직접 전송
    # 전송당 ~10 cycles (load + store + loop overhead)
    pio_transfers = data_size_bytes // bus_width
    pio_cycles = pio_transfers * 10
    pio_cpu_busy = pio_cycles  # CPU 100% 점유
    
    # DMA: 설정 + 완료 인터럽트만 CPU 사용
    dma_cpu_busy = dma_setup_cycles + 500  # setup + interrupt handling
    dma_total_time = dma_setup_cycles + (data_size_bytes / (bus_width * cpu_freq_ghz))
    
    return {
        'pio_cpu_cycles': pio_cpu_busy,
        'dma_cpu_cycles': dma_cpu_busy,
        'cpu_savings': 1 - (dma_cpu_busy / pio_cpu_busy),
        'pio_time_us': pio_cycles / (cycles_per_sec / 1e6),
        'dma_time_us': dma_total_time / (cycles_per_sec / 1e6),
    }

# 1MB 전송 비교
result = dma_vs_programmed_io(1024 * 1024)
print(f"1MB 전송:")
print(f"  PIO CPU 사이클: {result['pio_cpu_cycles']:,}")
print(f"  DMA CPU 사이클: {result['dma_cpu_cycles']:,}")
print(f"  CPU 시간 절감: {result['cpu_savings']:.1%}")
```

### PCIe 대역폭 계산

```python
def pcie_bandwidth(gen: int, lanes: int) -> dict:
    """PCIe 세대와 레인 수에 따른 대역폭 계산."""
    # GT/s (Gigatransfers/second) per lane
    rate_per_lane = {1: 2.5, 2: 5.0, 3: 8.0, 4: 16.0, 5: 32.0, 6: 64.0}
    # 인코딩 오버헤드
    encoding_efficiency = {1: 8/10, 2: 8/10, 3: 128/130, 4: 128/130, 5: 128/130, 6: 242/256}
    
    raw_rate = rate_per_lane[gen] * lanes  # GT/s
    effective_rate = raw_rate * encoding_efficiency[gen]  # Gb/s
    bandwidth_GBs = effective_rate / 8  # GB/s
    
    return {
        'generation': f"PCIe Gen{gen} x{lanes}",
        'raw_rate_GTs': raw_rate,
        'bandwidth_GBs': bandwidth_GBs
    }

print(f"{'구성':<20} {'대역폭 (GB/s)':>15}")
print("-" * 37)
configs = [(3,4), (3,16), (4,4), (4,16), (5,16), (6,16)]
for gen, lanes in configs:
    r = pcie_bandwidth(gen, lanes)
    print(f"{r['generation']:<20} {r['bandwidth_GBs']:>12.1f}")
```

출력:
```text
구성                     대역폭 (GB/s)
-------------------------------------
PCIe Gen3 x4                    3.9
PCIe Gen3 x16                  15.8
PCIe Gen4 x4                    7.9
PCIe Gen4 x16                  31.5
PCIe Gen5 x16                  63.0
PCIe Gen6 x16                 121.0
```

NVMe SSD는 PCIe Gen4 x4(~7.9 GB/s)를 사용하며, GPU는 Gen4 x16(~31.5 GB/s)을 사용합니다.

### 인터럽트 컨트롤러와 우선순위

```text
인터럽트 처리 흐름:
장치 → PIC/APIC → CPU
       (우선순위   (현재 실행 중단
        중재)      → ISR 점프)

현대 x86 APIC (Advanced PIC) 구조:
┌─────────────┐      ┌─────────────┐
│  장치 A     │──►   │             │
│  장치 B     │──►   │  I/O APIC   │──► 인터럽트 메시지 ──► Local APIC (코어별)
│  장치 C     │──►   │  (칩셋)     │
│  타이머     │──►   │             │
└─────────────┘      └─────────────┘

MSI/MSI-X (Message Signaled Interrupts):
- 장치가 메모리 쓰기로 인터럽트 발생 (별도 핀 불필요)
- 벡터 번호를 직접 지정 → 라우팅 유연
- PCIe 장치는 MSI-X 필수
```

| 인터럽트 방식 | 최대 벡터 | 장점 | 단점 |
|-------------|-----------|------|------|
| Legacy PIC (8259) | 15 | 단순 | 공유, 느림 |
| APIC | 256 | 멀티코어 지원 | 설정 복잡 |
| MSI | 32/장치 | 핀 불필요, 빠름 | — |
| MSI-X | 2048/장치 | 큐별 인터럽트 가능 | — |

### Memory-Mapped I/O vs Port I/O

```text
Memory-Mapped I/O (MMIO):
- 장치 레지스터가 메모리 주소 공간에 매핑
- 일반 load/store 명령어로 접근
- 예: GPU VRAM (0xC0000000~), PCIe BAR

Port I/O (x86 전용):
- 별도 I/O 주소 공간 (0x0000~0xFFFF)
- 전용 명령어: IN, OUT
- 예: 레거시 직렬 포트 (0x3F8), 키보드 (0x60)
```

```python
# MMIO 접근 패턴 (개념 코드)
# 실제로는 커널 드라이버에서 수행

# PCIe 장치의 설정 공간 읽기 시뮬레이션
class PCIeDevice:
    def __init__(self, bar_base: int):
        self.bar_base = bar_base
        self.registers = {
            0x00: 0x8086,   # Vendor ID (Intel)
            0x02: 0x1234,   # Device ID
            0x04: 0x0007,   # Command Register
            0x08: 0x02,     # Revision ID
            0x10: bar_base, # BAR0
        }
    
    def mmio_read(self, offset: int) -> int:
        """MMIO 읽기: CPU가 load 명령어로 접근."""
        return self.registers.get(offset, 0)
    
    def mmio_write(self, offset: int, value: int):
        """MMIO 쓰기: CPU가 store 명령어로 접근."""
        # 하드웨어 레지스터 쓰기는 부작용(side effect)을 일으킴
        # 캐시하면 안 됨! (uncacheable 매핑 필수)
        self.registers[offset] = value

dev = PCIeDevice(bar_base=0xFE000000)
vendor = dev.mmio_read(0x00)
print(f"Vendor ID: 0x{vendor:04X}")  # Intel
```


### I/O 스케줄링: 디스크 접근 최적화

HDD에서 I/O 요청 순서가 성능에 큰 영향을 미칩니다. 헤드 이동(seek) 시간이 밀리초 단위이기 때문입니다.

```python
def elevator_scheduling(requests: list, start_pos: int = 0) -> dict:
    """SCAN (엘리베이터) 알고리즘으로 디스크 접근 순서 결정."""
    sorted_req = sorted(requests)
    
    # FCFS (요청 순서대로)
    fcfs_movement = 0
    pos = start_pos
    for r in requests:
        fcfs_movement += abs(r - pos)
        pos = r
    
    # SCAN (한 방향으로 끝까지 간 뒤 반대 방향)
    above = [r for r in sorted_req if r >= start_pos]
    below = [r for r in sorted_req if r < start_pos]
    below.reverse()
    
    scan_order = above + below
    scan_movement = 0
    pos = start_pos
    for r in scan_order:
        scan_movement += abs(r - pos)
        pos = r
    
    return {
        'fcfs_total_movement': fcfs_movement,
        'scan_total_movement': scan_movement,
        'improvement': 1 - scan_movement / fcfs_movement if fcfs_movement > 0 else 0
    }

# 디스크 실린더 0~199에서의 요청
requests = [98, 183, 37, 122, 14, 124, 65, 67]
result = elevator_scheduling(requests, start_pos=53)
print(f"FCFS 총 이동: {result['fcfs_total_movement']} 실린더")
print(f"SCAN 총 이동: {result['scan_total_movement']} 실린더")
print(f"개선율: {result['improvement']:.0%}")
```

SSD에서는 seek 시간이 없으므로 I/O 스케줄링이 덜 중요합니다. 대신 쓰기 증폭(Write Amplification), 마모 균등화(Wear Leveling), TRIM이 SSD 성능의 핵심입니다.

### 가상화와 I/O: SR-IOV

클라우드 환경에서 물리 장치를 여러 VM이 공유하려면 하드웨어 지원이 필요합니다.

```text
SR-IOV (Single Root I/O Virtualization):
┌─────────────────────────────────┐
│        물리 NIC (PF)             │
│  ┌─────┐ ┌─────┐ ┌─────┐      │
│  │VF 0 │ │VF 1 │ │VF 2 │ ... │
│  └──┬──┘ └──┬──┘ └──┬──┘      │
└─────┼───────┼───────┼──────────┘
      │       │       │
   VM 0    VM 1    VM 2

PF (Physical Function): 호스트 드라이버가 관리
VF (Virtual Function): VM에 직접 할당 (패스스루)
→ 하이퍼바이저 바이패스 → 네이티브에 근접한 성능
```

| I/O 가상화 방식 | 지연 시간 | CPU 오버헤드 | 유연성 |
|----------------|-----------|-------------|--------|
| 에뮬레이션 (QEMU) | ~100μs | 높음 | 최고 |
| Paravirt (virtio) | ~10μs | 중간 | 높음 |
| SR-IOV (VF 패스스루) | ~2μs | 최저 | 낮음 |
| 네이티브 | ~1μs | 최저 | — |

### 현대 I/O 인터페이스 비교

| 인터페이스 | 대역폭 | 지연 | 용도 |
|-----------|--------|------|------|
| SATA III | 600 MB/s | ~100μs | 레거시 SSD/HDD |
| NVMe (Gen4 x4) | 7.9 GB/s | ~10μs | 고성능 SSD |
| USB 3.2 Gen2 | 1.25 GB/s | ~ms | 외장 장치 |
| Thunderbolt 4 | 5 GB/s | ~μs | 외장 GPU, 스토리지 |
| CXL 2.0 | 64 GB/s | ~100ns | 메모리 확장 |
| InfiniBand HDR | 25 GB/s | ~1μs | HPC 클러스터 |

CXL(Compute Express Link)은 주목할 신기술입니다. CPU 캐시와 일관성을 유지하면서 외부 메모리를 확장할 수 있어, 메모리 용량의 물리적 한계를 넘깁니다.

## 처음 질문으로 돌아가기

- **CPU와 장치의 속도 차이는 얼마나 클까요?**
  - CPU 레지스터(0.3ns)와 NVMe SSD(10μs) 사이에 33,000배, HDD(5ms)와는 1,600만 배 차이가 있습니다. 심화 학습에서 계산한 것처럼, SSD 하나 읽는 동안 CPU는 33,000개 명령어를 실행할 수 있으므로 비동기 I/O가 필수입니다.
- **폴링과 인터럽트는 어떻게 다를까요?**
  - 폴링은 CPU가 능동적으로 장치 상태를 확인하고(오버헤드 낮지만 CPU 점유), 인터럽트는 장치가 CPU에 알림을 보냅니다(오버헤드 높지만 CPU 자유). 고빈도 I/O(100만+ events/sec)에서는 폴링이 유리하고, 저빈도에서는 인터럽트가 적합합니다.
- **DMA는 왜 CPU를 더 자유롭게 만들까요?**
  - Programmed I/O는 매 바이트 전송에 CPU가 개입하지만, DMA는 설정(~1000 cycles)과 완료 통보(~500 cycles)만 CPU를 사용합니다. 1MB 전송 시 CPU 사이클 소모가 99.9% 이상 절감됩니다.

## 참고 자료

- [Wikipedia — Direct memory access](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Wikipedia — Interrupt](https://en.wikipedia.org/wiki/Interrupt)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [The C10K problem (Dan Kegel)](http://www.kegel.com/c10k.html)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, I/O, 인터럽트, DMA, 장치
