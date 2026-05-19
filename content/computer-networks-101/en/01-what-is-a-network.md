---
series: computer-networks-101
episode: 1
title: What Is a Network?
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
  - Internet
  - Packet
  - Layered Model
  - OSI
seo_description: A network is not cables but a bundle of agreements. Learn the three words that organize the rest of the series — packet, protocol, layered model.
last_reviewed: '2026-05-15'
---

# What Is a Network?

> Computer Networks 101 series (1/10)

<!-- a-grade-intro:begin -->

**Core question**: When you hear the word "network", what picture should be in your head so that IP, TCP, DNS, and HTTP all sit on the same canvas later?

> A network is not cables. It is a bundle of agreements. Two computers exchange data only because they have agreed who speaks first, how to cut the data into pieces, and how to put it back together. Those agreements are protocols, and the way they stack on top of each other is the layered model. Before we start the series, draw that picture in your head.

<!-- a-grade-intro:end -->

This is the first post in the Computer Networks 101 series.

## What You Will Learn

- The difference between a network and the Internet
- Packets as the basic unit of data
- Why we need a layered model (OSI / TCP-IP)
- What the word "protocol" actually means

## Why It Matters

Open any networking book and a flood of acronyms appears at once: IP, TCP, UDP, DNS, HTTP, TLS, BGP, NAT. If you memorize them without a mental picture, you cannot see how they connect, and you forget all of them. The layered model is the bookshelf where these words go. Without a shelf, the books pile on the floor and never come out again.

> Learning networking is not memorizing new words. It is deciding which shelf each word belongs on.

## Concept at a Glance

> Data is cut into small units called packets and pushed through the network. At each layer, a different kind of agreement takes responsibility — physical signals, frames between adjacent devices, packets routed worldwide, reliable connections, and finally meaningful messages such as HTTP requests. That division of labor is the layered model.

![Layered model and packet travel across a network](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/01/01-01-concept-at-a-glance.en.png)
*Packets are encapsulated layer by layer, traverse intermediate devices, and are reassembled at the destination.*

## Key Terms

| Term | Meaning |
| --- | --- |
| Packet | The basic unit of data flowing across a network |
| Protocol | An agreement (format + procedure) for two nodes to communicate |
| Layered model | A structure that splits communication responsibility into layers |
| Host | An endpoint of communication (computer, server, phone) |
| Router | A device that forwards packets to the next network |

## Before / After

**Before — "the Internet is magic":**

```text
browser  →  ???  →  server
the middle is one big black box
```

**After — "each layer has a responsibility":**

```text
HTTP (message) → TCP (reliability) → IP (routing) → Ethernet (link) → signal
each layer wraps the upper layer's data in its own envelope (encapsulation)
```

Once you know the responsibility of each layer, you can isolate where a problem happened — application? TCP? routing?

## Hands-on: Step by Step

### Step 1: see a packet round-trip with ping

```bash
ping -c 3 example.com
# 64 bytes from 93.184.216.34: icmp_seq=1 ttl=53 time=12.3 ms
```

ping uses ICMP, a network-layer protocol. The output shows the packet size, the round-trip time, and the TTL.

### Step 2: see the path with traceroute

```bash
traceroute example.com    # or mtr example.com
# 1  router.local  1.1 ms
# 2  isp-gw        5.4 ms
# ...
# N  93.184.216.34 12.3 ms
```

It prints the routers your packets cross from your machine to the destination, one per line. The fact that the Internet is "a router of routers of routers" becomes visible.

### Step 3: the smallest client and server

```python
# server.py
import socket
s = socket.socket()
s.bind(('127.0.0.1', 5000)); s.listen()
while True:
    c, _ = s.accept()
    c.sendall(b'hello\n'); c.close()
```

```python
# client.py
import socket
s = socket.socket(); s.connect(('127.0.0.1', 5000))
print(s.recv(1024))
```

A socket is the network interface that the OS exposes. It will keep showing up across the series.

### Step 4: capture the packets

```bash
sudo tcpdump -i lo -nn -c 5 'port 5000'
# Run server/client above and you will see SYN, SYN-ACK, ACK, PSH+ACK, FIN
```

tcpdump and Wireshark are the X-rays of all networking learning. We will use them again in episode 4 (DNS) and episode 5 (HTTP).

### Step 5: replay the flow with the layers in mind

Map the flow above to the layers.

```text
client.recv() ↔ server.sendall()    ← application layer (message)
TCP            ↔ TCP                ← transport layer (connection, order, retransmission)
IP(loopback)   ↔ IP(loopback)       ← network layer (routing)
loopback driver                      ← link + physical layer
```

A single line of code triggers a five-layer collaboration.

## What to Notice in This Code

- Data is always cut into packets and reassembled
- Each layer wraps the upper layer's data in its own envelope (encapsulation) and hands it down
- ICMP, TCP, and IP are not abstractions in a textbook — they are real things you can see in ping and tcpdump
- "From my machine to that server" is always a collaboration of many routers

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Treating the Internet as one system | Ignores routing, AS, latency | Run traceroute and see the reality |
| Knowing only HTTP, not TCP/IP | Cannot diagnose connection, retransmission, NAT issues | Sort the words by layer |
| Blaming "DNS" for every failure | Wastes diagnosis time | Cut the problem with ping → curl → tcpdump in order |
| Assuming packets always take the same path | Tracing flows fails | The Internet routes per packet |
| Believing TCP is always reliable, UDP always lossy | Inaccurate | Reliability vs speed is a tradeoff (episode 3) |

## How This Shows Up in Production

- Backend APIs: HTTP/HTTPS over TCP, often HTTP/2 or HTTP/3
- Games and video calls: custom protocols on top of UDP
- Containers: virtual networks built with network namespaces
- CDNs: routing to the closest user plus caches
- Monitoring: layer-specific metrics (packet loss, RTT, HTTP 5xx) observed separately

## How a Senior Engineer Thinks

When a senior engineer hears about a network incident, the first question is "which layer is this?". Is it a 5xx in the service, a TCP retransmission storm, a DNS resolve failure, a routing problem? Without separating the layers, the discussion goes in circles forever. The layered model is not a textbook diagram — it is the first triage table for incident analysis.

A senior also stays aware of the cost of every abstraction. A single HTTP request includes DNS, TCP handshake, TLS handshake, HTTP header transfer, and N router hops. Most of the time those costs are hidden, but during an incident the bill is itemized exactly along these lines.

## Checklist

- [ ] I can explain the difference between "network" and "the Internet"
- [ ] I know what packets, protocols, and the layered model are
- [ ] I have used ping, traceroute, and tcpdump at least once
- [ ] I know which layer HTTP runs on
- [ ] When something breaks, I ask "which layer?" first

## Practice Problems

1. Run traceroute against a site you visit often, then summarize the number of routers and average RTT in one paragraph.

2. Run the client/server above and capture it with tcpdump. Identify the SYN / SYN-ACK / ACK handshake yourself.

3. Imagine an HTTP request just failed. Write a five-step procedure that says which layer to check first and which tool to use at each step.

## Wrap-up and Next Steps

A network is not cables but a bundle of agreements. Three words — packet, protocol, layered model — become the bookshelf for the entire series. Whenever a new word appears, the habit of asking "which shelf does this go on?" decides how fast you learn.

Next we move to the most basic addressing system on the Internet — IP and subnet.

<!-- toc:begin -->
- **What Is a Network? (current)**
- IP and subnet (upcoming)
- TCP and UDP (upcoming)
- DNS (upcoming)
- HTTP and HTTPS (upcoming)
- TLS basics (upcoming)
- Routing and NAT (upcoming)
- Load Balancer (upcoming)
- WebSocket and real-time (upcoming)
- Debugging network problems (upcoming)
<!-- toc:end -->

## References

- [Tanenbaum & Wetherall — Computer Networks](https://www.pearson.com/store/p/computer-networks/P100000875375)
- [Kurose & Ross — Computer Networking: A Top-Down Approach](https://gaia.cs.umass.edu/kurose_ross/)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [Cloudflare Learning — What is the Internet?](https://www.cloudflare.com/learning/network-layer/what-is-the-internet/)
- [RFC 1122 — Requirements for Internet Hosts](https://www.rfc-editor.org/rfc/rfc1122)

Tags: Computer Science, Networking, Internet, Packet, Layered Model, OSI
