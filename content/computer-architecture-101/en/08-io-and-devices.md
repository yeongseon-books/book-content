---
series: computer-architecture-101
episode: 8
title: I/O and Devices
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Computer Architecture
  - IO
  - Interrupts
  - DMA
  - Devices
seo_description: How CPUs talk to slow devices through polling, interrupts, and DMA, and why memory-mapped I/O underpins every async program.
last_reviewed: '2026-05-04'
---

# I/O and Devices

> Computer Architecture 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: A single disk read takes 100,000 times longer than a memory access. What is the CPU doing during that time?

> The CPU is fast and devices are slow. Keyboards live at human speed, disks at milliseconds, networks somewhere beyond. Polling, interrupts, and DMA are the mechanisms that bridge the gap, and memory-mapped I/O is how the CPU sees a device as just another set of addresses. This article looks inside, and ties together the starting point for every system call and every async program.

<!-- a-grade-intro:end -->

This is post 8 in the Computer Architecture 101 series.

## What You Will Learn

- The speed gap between CPU and devices, and what it implies
- The difference between polling and interrupts
- The role of DMA (Direct Memory Access)
- Memory-mapped I/O versus port-mapped I/O

## Why It Matters

Every async program, every event loop, every system call is, ultimately, an abstraction for "handle slow devices efficiently." Without interrupts and DMA, every keystroke would freeze the CPU. Knowing these mechanisms is what makes tools like epoll, async/await, and kqueue stop looking arbitrary.

> A fast CPU was designed to never wait for a slow device, and your code should follow the same principle.

## Concept at a Glance

> CPU and devices are connected by a bus. Polling — having the CPU keep asking — is simple but wastes cycles. An interrupt lets the device signal the CPU when it is ready. DMA lets a device write directly to RAM without involving the CPU. Memory-mapped I/O makes device registers look like ordinary memory addresses.

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

## Key Terms

| Term | Description |
| --- | --- |
| Polling | CPU repeatedly checks device state |
| Interrupt | Device signals the CPU |
| ISR | Interrupt service routine, the handler |
| DMA | Device-to-memory transfer without CPU |
| MMIO | Memory-mapped I/O, devices exposed via addresses |
| System call | User-mode entry into kernel I/O services |

## Before / After

**Before — polling for a device:**

```python
# Synthetic polling loop
def wait_for_data(device):
    while not device.is_ready():
        pass   # CPU pegged at 100%, no other work
    return device.read()
```

**After — interrupt + callback:**

```python
# Synthetic interrupt model
def on_data_ready(device):
    data = device.read()
    process(data)

device.register_interrupt(on_data_ready)
do_other_work()   # CPU continues working
# When the device is ready, on_data_ready is called automatically
```

Same outcome, completely different CPU utilization. The OS exposes this interrupt mechanism to user code as `select`, `epoll`, or `async`.

## Hands-on: Step by Step

### Step 1: Build a device-speed table

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

This gap is why async programming exists. The CPU has to do other work during these waits.

### Step 2: Polling vs interrupt simulation

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

Polling is simple, but for 100ms the CPU does nothing else. Embedded systems may use it; general-purpose OSes use interrupts.

### Step 3: Interrupt model simulation

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

`queue.Queue` is not exactly an OS interrupt, but it shows the model: device events arrive asynchronously.

### Step 4: Mimic DMA — separating the work

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

Real DMA is performed cooperatively by the OS and a device controller, but the essence is the same: data transfer barely costs the CPU any cycles.

### Step 5: Use `select` for a real interrupt-style pattern

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

`select` is the oldest interface that exposes the OS interrupt mechanism to user code. `epoll`, `kqueue`, and IOCP are more efficient variants of the same idea.

## What to Notice in This Code

- Devices can be 10,000 to 100,000,000 times slower than the CPU
- Polling is simple but burns the CPU
- Interrupts let the CPU work on something else
- DMA frees the CPU even from data movement

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Synchronous I/O on the hot path | One request blocks all others | async/await, epoll |
| Busy-loop waiting | CPU 100%, heat and power | sleep or wait on an event |
| Heavy work in an interrupt handler | Other interrupts delayed | Keep handler short, queue the rest |
| Skipping cache flush after DMA | Reading stale data | Memory barriers, explicit flush |
| Ignoring device register alignment | Hitting wrong bits | Follow the datasheet bitmap |

## How This Shows Up in Production

- Web servers: epoll/kqueue event loops (nginx, Node.js) handle tens of thousands of connections
- Databases: async I/O and DMA fully utilize disk bandwidth
- Embedded: GPIO interrupts react to sensors instantly
- GPU computing: PCIe DMA moves memory between host and device
- Operating systems: interrupt controllers enforce device priorities

## How a Senior Engineer Thinks

A senior engineer looks at the I/O model first. One blocking call on the hot path caps the throughput of the whole system. When designing a new system, they ask "is this work CPU-bound or I/O-bound?" before they pick a thread model, async model, or queue structure.

A senior also keeps the rule "always measure I/O cost." Whether one disk access takes 100us or 10ms, whether a network round trip is 1ms or 100ms — the same algorithm means completely different things. Latency Numbers is a starting point; the real numbers in your system are the truth.

## Checklist

- [ ] You know main-memory and SSD costs to the order of magnitude
- [ ] You can explain polling vs interrupts
- [ ] You know what DMA wins back for the CPU
- [ ] You know which OS mechanism `select`/`epoll` exposes
- [ ] You can describe sync vs async I/O tradeoffs

## Practice Problems

1. Use the `LATENCY` table to compute the time for "1000 SSD random reads" vs "1000 memory accesses." Decide whether async I/O is justified.

2. Use `select.select` on stdin and two pipes simultaneously, printing different messages depending on which fires first.

3. Compare a sync HTTP client (e.g., `requests`) to an async one (e.g., `httpx.AsyncClient`) on 100 concurrent requests. Measure time, CPU, and memory.

## Wrap-up and Next Steps

Polling, interrupts, and DMA bridge the huge speed gap between CPU and devices. They surface in user code as `select`, `epoll`, and `async/await`, and that is where every async program starts. Looking at the I/O model first is the entry point of system design.

Next we cross beyond a single core, into parallelism and multicore. We will cover models for cooperating CPUs and the synchronization problems that arise inside them.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [CPU and Instructions](./03-cpu-and-instructions.md)
- [Registers and the ALU](./04-registers-and-alu.md)
- [Memory Organization](./05-memory-organization.md)
- [Cache and Locality](./06-cache-and-locality.md)
- [Pipelining](./07-pipelining.md)
- **I/O and Devices (current)**
- Parallelism and Multicore (upcoming)
- Understanding Performance (upcoming)
<!-- toc:end -->

## References

- [Wikipedia — Direct memory access](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Wikipedia — Interrupt](https://en.wikipedia.org/wiki/Interrupt)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [The C10K problem (Dan Kegel)](http://www.kegel.com/c10k.html)

Tags: Computer Science, Computer Architecture, IO, Interrupts, DMA, Devices
