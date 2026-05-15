---
series: computer-networks-101
episode: 3
title: TCP and UDP
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Networking
  - TCP
  - UDP
  - Transport Layer
  - Reliability
seo_description: TCP and UDP compared along four axes — reliability, order, connection, and speed — with guidance on which one to pick for which workload.
last_reviewed: '2026-05-15'
---

# TCP and UDP

> Computer Networks 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: Are TCP and UDP just a contrast of "reliable vs fast", or are they two designs that show two different ways to split responsibility?

> Both are transport-layer protocols on top of IP. TCP handles connection, order, retransmission, and flow and congestion control. UDP pushes all of that onto the application and just throws packets. There is no winner — there is only the right choice for a workload.

<!-- a-grade-intro:end -->

This is post 3 in the Computer Networks 101 series.

## What You Will Learn

- The four responsibilities of TCP (connection, order, retransmission, congestion control)
- What UDP intentionally does not do
- The 3-way handshake and 4-way close
- When to pick which one

## Why It Matters

The transport-protocol choice directly affects system performance and user experience. Pick TCP for a game or a video call and one lost frame can stall the whole stream. Pick UDP for payment processing and transactions disappear. If you cannot answer "why this protocol?", system design becomes a cargo cult.

> Protocol choice is a tradeoff — what to guarantee and what to give up.

## Concept at a Glance

> TCP creates a virtual circuit between two hosts and guarantees data flows in order, with no loss, and not too fast. UDP places packets on top of IP one at a time, with no circuit. If reliability is needed, the application has to build it.

![TCP and UDP split responsibility in different ways](../../../assets/computer-networks-101/03/03-01-concept-at-a-glance.en.png)
*TCP puts reliability in the operating system, while UDP leaves it to the application so you can pay only for what the workload needs.*

## Key Terms

| Term | Meaning |
| --- | --- |
| 3-way handshake | TCP connection setup with SYN, SYN-ACK, ACK |
| ACK | Acknowledgement that data arrived |
| Retransmission | Resending when no ACK comes back |
| Flow control | Slow down the sender if the receiver cannot keep up |
| Congestion control | Slow down the sender if the network is congested |

## Before / After

**Before — "TCP good, UDP risky":**

```text
TCP for everything
```

**After — "pick per workload":**

```text
Web / API / file transfer  → TCP (HTTP, HTTPS)
DNS lookup                 → UDP (small and idempotent)
Video calls / games        → UDP + custom reliability
QUIC (HTTP/3)              → New reliability layer on top of UDP
```

## Hands-on: Step by Step

### Step 1: TCP echo server

```python
# tcp_server.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 5001)); s.listen()
while True:
    c, _ = s.accept()
    data = c.recv(1024)
    c.sendall(data); c.close()
```

```python
# tcp_client.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5001))
s.sendall(b'hello tcp')
print(s.recv(1024))   # b'hello tcp'
```

### Step 2: UDP echo server

```python
# udp_server.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5002))
while True:
    data, addr = s.recvfrom(1024)
    s.sendto(data, addr)
```

```python
# udp_client.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'hello udp', ('127.0.0.1', 5002))
print(s.recvfrom(1024))   # (b'hello udp', ('127.0.0.1', 5002))
```

UDP has no `connect`, `listen`, or `accept`. You just send and receive.

### Step 3: see the handshake with tcpdump

```bash
sudo tcpdump -i lo -nn 'port 5001'
# SYN → SYN-ACK → ACK → PSH+ACK(data) → ACK → FIN → FIN+ACK → ACK
```

UDP?

```bash
sudo tcpdump -i lo -nn 'port 5002'
# UDP, length 9   (one line and done)
```

### Step 4: drop packets on purpose

```python
# UDP packet-loss simulation
import socket, random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5003))
while True:
    data, addr = s.recvfrom(1024)
    if random.random() < 0.3:
        continue   # 30% drop
    s.sendto(data, addr)
```

A drop in UDP is just a loss. TCP would have retransmitted automatically; UDP makes the application handle it.

### Step 5: a tiny taste of building reliability

```python
# Simple ACK + retransmit on top of UDP
import socket, time

def send_reliable(sock, data, addr, retries=3, timeout=0.5):
    for _ in range(retries):
        sock.sendto(data, addr)
        sock.settimeout(timeout)
        try:
            ack, _ = sock.recvfrom(1024)
            if ack == b'ACK':
                return True
        except socket.timeout:
            continue
    return False
```

QUIC, RTP, and game protocols are all sophisticated versions of this pattern.

## What to Notice in This Code

- TCP is a stream abstraction (ordered, no boundaries). UDP is a datagram abstraction (boundaries, no order).
- TCP's `recv(1024)` does not always return exactly 1024 bytes (no message boundaries)
- UDP's `recvfrom` returns one datagram as a whole
- Reliability is not free — it costs handshakes, ACKs, and retransmissions

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Assuming TCP `recv` returns one message | Messages get split or merged | Frame with length prefix or delimiter |
| Believing UDP always loses packets | Forces TCP onto real-time workloads | Use UDP plus your own reliability |
| Generalizing TCP as "slow" | Misses HTTP/2 and HTTP/3 progress | Measure actual RTT and throughput |
| Forgetting to close on both ends | TIME_WAIT and resource leaks | Use `with` or try/finally |
| Ignoring congestion control | Low throughput or packet floods | Understand TCP defaults (BBR, CUBIC) |

## How This Shows Up in Production

- Web and APIs: HTTP / HTTPS over TCP, gradually moving to HTTP/3 (QUIC over UDP)
- DNS: UDP by default, falls back to TCP for large responses
- Video conferencing (Zoom, Meet): media on UDP (RTP), signaling on TCP
- Games: position and input on UDP, chat and payments on TCP
- Databases: almost always TCP for transactional integrity

## How a Senior Engineer Thinks

A senior engineer does not treat "TCP vs UDP" as a holy war. Both are tools, and the right one depends on workload requirements — latency, loss tolerance, message size, security. They keep both protocols' cost models in their head — handshake RTT, retransmission timeouts, MTU and fragmentation — and weigh them at design time, not after an incident.

QUIC matters to seniors. It came from the insight that TCP lives in the OS kernel and is hard to change, while reliability rebuilt on top of UDP can evolve much faster.

## Checklist

- [ ] I know TCP's four responsibilities
- [ ] I know what UDP intentionally does not do
- [ ] I can draw the 3-way handshake
- [ ] I can pick TCP or UDP per workload
- [ ] I know why HTTP/3 sits on UDP

## Practice Problems

1. Capture a TCP close (4-way) with tcpdump and write down the order of FINs and ACKs.

2. Extend the ACK + retransmit example with sequence numbers and add logic that drops duplicates.

3. Answer in one paragraph: "Is my service TCP or UDP, and why?"

## Wrap-up and Next Steps

TCP and UDP ride on the same IP but show two different ways to split responsibility. TCP puts reliability in the operating system; UDP puts it in the application. The point is to choose by workload.

Next we look at how the human-readable domain name turns into an IP address — DNS.

<!-- toc:begin -->
- [What Is a Network?](./01-what-is-a-network.md)
- [IP and Subnet](./02-ip-and-subnet.md)
- **TCP and UDP (current)**
- DNS (upcoming)
- HTTP and HTTPS (upcoming)
- TLS basics (upcoming)
- Routing and NAT (upcoming)
- Load Balancer (upcoming)
- WebSocket and real-time (upcoming)
- Debugging network problems (upcoming)
<!-- toc:end -->

## References

- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)

Tags: Computer Science, Networking, TCP, UDP, Transport Layer, Reliability
