---
series: computer-science-101
episode: 7
title: Networks
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
  - Networks
  - TCP/IP
  - HTTP
  - DNS
  - Sockets
seo_description: How TCP/IP, HTTP, and DNS actually work — explained with hands-on socket programming as part of the CS 101 series.
last_reviewed: '2026-05-15'
---

# Networks

Typing a domain into a browser does not trigger one magical request. It kicks off a layered exchange where DNS, TCP, TLS, and HTTP each do a different job. Engineers who can draw those layers mentally usually find latency and failure faster.

This is post 7 in the Computer Science 101 series.

In this article, we'll build a practical network model through the TCP/IP layers, HTTP messages, DNS lookups, and direct socket examples.

## Questions This Article Answers

- What path does data follow after you type an address into a browser?
- What does each of IP, TCP, HTTP, and DNS do in its own layer?
- What does an HTTP request and response look like on the wire?
- Why do DNS lookup time and the TLS handshake count toward latency?
- When should you choose TCP versus UDP for a workload?

## What You Will Learn

- The roles of the four TCP/IP layers
- The structure of an HTTP request and response
- DNS and how name resolution works
- Talking to a server directly using the socket API

## Why It Matters

When an API response is slow, when a certificate error pops up, when an odd timeout occurs — the cause is somewhere in the network stack. Knowing the layers lets you ask, and answer, "Which layer is the problem?"

> Network = layered agreements.

Each layer trusts the one below it and focuses on its own job.

## Concept at a Glance

> Data flows down through the layers (each adding a header) on the sending side, and up the layers (each stripping its header) on the receiving side.

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/07/07-01-concept-at-a-glance.en.png)
*A request starts at the application layer and picks up lower-layer headers on the way down*

## Key Terms

| Term | Description |
| --- | --- |
| IP | Protocol that delivers a packet to the destination host (addressing) |
| Port | Identifies which process on the host should receive the data (0–65535) |
| TCP | Connection-oriented protocol that guarantees reliability, ordering, and retransmission |
| UDP | Lightweight, connectionless protocol with no reliability guarantees |
| HTTP | The web's application-layer protocol (request/response model) |
| DNS | The system that translates domain names into IP addresses |

## Before / After

**Before — code that treats HTTP as magic:**

```python
import urllib.request

# You have no idea what is actually exchanged
data = urllib.request.urlopen("https://httpbin.org/get").read()
print(data[:80])
```

**After — code that looks at HTTP one line at a time:**

```python
import socket
import ssl

# HTTPS = TCP + TLS + HTTP
ctx = ssl.create_default_context()
with socket.create_connection(("httpbin.org", 443)) as sock:
    with ctx.wrap_socket(sock, server_hostname="httpbin.org") as tls:
        request = (
            "GET /get HTTP/1.1\r\n"
            "Host: httpbin.org\r\n"
            "Connection: close\r\n\r\n"
        )
        tls.send(request.encode())
        response = b""
        while chunk := tls.recv(4096):
            response += chunk

print(response.split(b"\r\n\r\n", 1)[0].decode())   # response headers
```

## Hands-On: Step by Step

### Step 1: Run a DNS lookup yourself

```python
import socket

host = "www.python.org"
ip = socket.gethostbyname(host)
print(f"{host} -> {ip}")

# Find every address (IPv4, IPv6)
for info in socket.getaddrinfo(host, 443):
    family, _, _, _, sockaddr = info
    print(family.name, sockaddr)
```

### Step 2: A TCP echo server and client

```python
# server.py — a simple echo server that accepts one client
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.bind(("127.0.0.1", 5050))
    srv.listen(1)
    print("listening on 127.0.0.1:5050")
    conn, addr = srv.accept()
    with conn:
        print("connected:", addr)
        while data := conn.recv(1024):
            conn.sendall(data)               # echo back exactly what came in
```

```python
# client.py — sends a message to the server above and prints the reply
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
    cli.connect(("127.0.0.1", 5050))
    cli.sendall(b"Hello, network!")
    print(cli.recv(1024).decode())
```

### Step 3: Build an HTTP request by hand

```python
import socket

with socket.create_connection(("example.com", 80)) as sock:
    sock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n")
    raw = b""
    while chunk := sock.recv(4096):
        raw += chunk

header, _, body = raw.partition(b"\r\n\r\n")
print(header.decode())
print("body bytes:", len(body))
```

### Step 4: TCP vs UDP

```python
# UDP sends without a connection and does not guarantee delivery
import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
    udp.sendto(b"ping", ("8.8.8.8", 53))     # just fire a datagram
    udp.settimeout(2)
    try:
        data, addr = udp.recvfrom(1024)
        print("received:", len(data), "bytes from", addr)
    except socket.timeout:
        print("no reply — UDP does not retransmit")
```

### Step 5: Measure response time per layer

```python
import socket
import time
import urllib.request

host = "www.python.org"

t0 = time.perf_counter()
ip = socket.gethostbyname(host)
t1 = time.perf_counter()

with socket.create_connection((ip, 443)) as sock:
    t2 = time.perf_counter()

t3 = time.perf_counter()
urllib.request.urlopen(f"https://{host}/").read()
t4 = time.perf_counter()

print(f"DNS    : {(t1 - t0) * 1000:6.1f} ms")
print(f"TCP    : {(t2 - t1) * 1000:6.1f} ms")
print(f"HTTPS  : {(t4 - t3) * 1000:6.1f} ms (total)")
```

**Expected output:** the script should print separate `DNS`, `TCP`, and `HTTPS` timings so you can see which layer dominates the request.

## Notable Points in This Code

- HTTP is, in the end, a chunk of text where headers and body are separated by a blank line.
- TCP requires a connection and guarantees order and retransmission — UDP does not.
- DNS lookups have their own cost; caching dominates response time.
- HTTPS adds a TLS handshake on top of the TCP connection.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Opening a new TCP connection per request | Handshake overhead piles up | Use HTTP keep-alive and a connection pool |
| Skipping DNS caching | Tens of milliseconds per request | Use the OS or library DNS cache |
| Assuming `recv` returns the full message | Truncated data | Length-prefixed or delimiter-based parsing |
| Disabling HTTPS certificate verification | Vulnerable to MITM | Fix the certificate, do not turn verification off |
| Expecting reliability from UDP | Silent loss on packet drop | Use TCP, or build reliability into the protocol |

## How This Is Used in Practice

- Choosing HTTP/2 or gRPC and tuning keep-alive between microservices.
- DNS caching and CDNs to give global users consistent latency.
- Monitoring P50/P95 latencies broken down into DNS, TCP, TLS, and server time.
- API gateways handling TLS termination, load balancing, and retries.
- UDP and QUIC for games and real-time transport to keep latency low.

## How a Senior Engineer Thinks

When a senior engineer hears "it's slow," their first move is to separate where the time is spent. DNS, TCP handshake, TLS, server processing, body download — each is measured on its own. You can only prescribe a fix once you can point at a single layer.

They also write code assuming the network always fails. Timeouts, retries, circuit breakers, and idempotency are defaults, not options. "Network code that only handles the happy path explodes in production" is a saying earned the hard way.

## Checklist

- [ ] I can describe each TCP/IP layer in one sentence
- [ ] I know the wire format of an HTTP request and response
- [ ] I am aware that DNS lookup time is part of total latency
- [ ] I pick TCP or UDP based on the workload
- [ ] I set a timeout on every network call

## Practice Problems

1. Using only `socket`, write a multi-client echo server that handles many clients at once (use `select` or threads).

2. Call the same URL 100 times with both `urllib.request` and `requests`, and compare average response times to measure the keep-alive effect.

3. Write a tiny profiler that takes a domain and prints DNS lookup time, TCP connect time, TLS handshake time, and HTTP response time separately.

## Wrap-Up and Next Steps

A network is a stack of agreements, where each layer trusts the layer below and focuses on its own job. HTTP is a text protocol on top of TCP, and TCP is the reliability layer on top of IP. Breaking down a response time layer by layer is where senior debugging begins.

The next article moves beyond the network to how we store data permanently and query it efficiently — databases.

<!-- toc:begin -->
- [What Is Computer Science?](./01-what-is-computer-science.md)
- [Computation and Programs](./02-computation-and-programs.md)
- [Data Representation](./03-data-representation.md)
- [Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Architecture](./05-computer-architecture.md)
- [Operating Systems](./06-operating-systems.md)
- **Networks (current)**
- [Databases](./08-databases.md)
- [Software Engineering](./09-software-engineering.md)
- [From CS to AI and Data Science](./10-ai-and-data-science.md)
<!-- toc:end -->

## References

- [HTTP/1.1 RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [High Performance Browser Networking — Ilya Grigorik](https://hpbn.co/)
- [Cloudflare Learning Center — DNS](https://www.cloudflare.com/learning/dns/what-is-dns/)

Tags: Computer Science, Networks, TCP/IP, HTTP, DNS, Sockets
