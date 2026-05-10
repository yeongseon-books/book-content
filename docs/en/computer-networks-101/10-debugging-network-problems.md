---
series: computer-networks-101
episode: 10
title: Debugging Network Problems
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
  - Networking
  - Debugging
  - tcpdump
  - Troubleshooting
  - Diagnostics
seo_description: How to narrow a network problem layer by layer with ping, dig, nc, openssl, curl, ss, and tcpdump, and how to read what each tool tells you.
last_reviewed: '2026-05-04'
---

# Debugging Network Problems

> Computer Networks 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: When the report is "the site is broken," what do you check first, and in what order, to find the cause as quickly as possible?

> Network debugging is not guesswork. It is **walking down the layers and killing hypotheses one at a time**. Link → routing → DNS → TCP → TLS → HTTP. Five short commands usually decide which layer owns the problem within a minute. A good tool is one that quickly invalidates a wrong hypothesis, not one that gives you more output to stare at.

<!-- a-grade-intro:end -->

## What You Will Learn

- A layer-by-layer approach to narrowing a network problem
- What `ping`, `dig`, `curl`, `ss`, and `tcpdump` actually tell you
- How to distinguish common failure shapes — timeout vs reset vs DNS failure
- How everything from this series comes together when something breaks

## Why It Matters

Under pressure, the first instinct is "what did we just change?" That is necessary but not enough. Without knowing where the path breaks, code changes are guesses. The habit of confirming "this layer is fine" one step at a time is what lets you stay calm at 3 a.m.

> Debugging is less about finding what is broken and more about **confirming, one layer at a time, what is fine**.

## Concept at a Glance

```mermaid
flowchart TB
    A["User: the site is down"] --> B["1. Link/path: ping, traceroute"]
    B --> C["2. Name resolution: dig"]
    C --> D["3. TCP connect: nc, ss"]
    D --> E["4. TLS: openssl s_client"]
    E --> F["5. HTTP: curl -v"]
    F --> G["6. Packets: tcpdump"]
```

Each step you confirm as healthy cuts the hypothesis space roughly in half.

## Key Terms

- **ICMP**: The diagnostic IP protocol used by `ping` and `traceroute`.
- **RTT (Round Trip Time)**: How long a packet takes to reach the destination and come back.
- **Connection refused**: The host is alive but no process is listening on that port.
- **RST**: A TCP signal meaning "drop this connection now." Often sent by firewalls.
- **Capture filter**: The BPF expression you give `tcpdump` so it captures only the packets you care about.

## Before/After

**Before — guess-driven debugging**

```text
service is down
→ check recent commits
→ reinstall the suspicious library
→ restart the server
→ still down
→ one hour gone
```

Touching things you suspect, with no idea where the break is, only fixes problems by luck.

**After — narrow by layer**

```bash
# 1) Is the host alive? (link / path)
ping -c 3 api.example.com

# 2) Does the name resolve? (DNS)
dig +short api.example.com

# 3) Is the port open? (TCP)
nc -vz api.example.com 443

# 4) Does the TLS handshake complete? (TLS)
openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null

# 5) What does HTTP return? (HTTP)
curl -v https://api.example.com/health
```

Each line kills or supports the next hypothesis. Five lines decide most cases.

## Hands-on: Trace a Single Request End to End in Five Steps

### Step 1 — Link and path

```bash
ping -c 3 api.example.com
traceroute api.example.com   # or mtr api.example.com
```

100% loss usually means the host is dead or ICMP is blocked. Partial loss hints at congestion somewhere on the path; `traceroute` shows which hop. Remember that ICMP can be blocked even when the host is healthy, so a `ping` failure alone is never proof.

### Step 2 — DNS

```bash
dig +short api.example.com
# 1.2.3.4

dig +trace api.example.com   # walks the delegation chain
```

If this returns nothing, do not bother going lower. Suspect `/etc/resolv.conf`, your corporate DNS resolver, or the authoritative records — not your application.

### Step 3 — TCP

```bash
nc -vz api.example.com 443
# Connection to api.example.com port 443 [tcp/https] succeeded!
```

Distinguish three outcomes carefully:

- **succeeded**: The port is open and the SYN/SYN-ACK exchange completed. Move to the next layer.
- **Connection refused**: The host is up but no process is listening. The service is down or you are using the wrong port.
- **timeout**: No response to SYN. Almost always a firewall silently dropping packets.

On the server side, confirm what is actually listening:

```bash
ss -tlnp | grep :443
# LISTEN 0 511 0.0.0.0:443  users:(("nginx",pid=1234,fd=6))
```

### Step 4 — TLS handshake

```bash
openssl s_client -connect api.example.com:443 \
                 -servername api.example.com </dev/null
```

The crucial flag is `-servername` (SNI). Without it, the virtual host can return the wrong certificate and mask the real issue. Look for `Verify return code: 0 (ok)`. Anything else points to expired, mis-chained, or wrong-name certificates.

### Step 5 — HTTP, with human eyes

```bash
curl -v https://api.example.com/health
```

`-v` is the point. It shows DNS, TCP connect, TLS negotiation, request headers, and response headers in one go. If you reach a 4xx or 5xx response, the problem is no longer the network — it is the application. If everything looks healthy here, suspicion shifts to the client environment.

## What to Notice in This Code

- Each tool eliminates a different hypothesis: `ping` for link, `dig` for name, `nc` for port, `openssl` for cert, `curl` for application behavior.
- The work is to **make tool output confirm "fine here"** instead of trusting your gut.
- Many cloud security groups block ICMP. A failing `ping` is not proof the host is down — fall back to `nc` or `curl`.
- A single `curl -v` covers most of steps 1 through 5. People forget that.

## Five Common Mistakes

1. **Skipping DNS.** "Nothing changed in our code but it broke" is very often DNS — TTL expiry, cache, recent record change. Suspect it first.
2. **Treating timeout and refused as the same.** Refused is strong evidence the host is up; timeout almost always points at a firewall. Your next action is completely different.
3. **Forgetting `-servername` with `openssl s_client`.** Without SNI you can fetch the wrong certificate and chase a fake error.
4. **Reaching for tcpdump first.** It is a great tool, but a capture without a hypothesis is just a big file. Use the five steps above first; bring out tcpdump when you are stuck.
5. **Calling a restart a fix.** If a restart hid the symptom, it will return next week. Write down the hypothesis you actually validated.

## How This Shows Up in Production

In incident response, two engineers usually move in parallel: one runs the five steps from outside as a user; the other looks from inside with `ss`, logs, and `tcpdump`. They sync every few minutes and merge what each saw to narrow the hypothesis.

`tcpdump` is the last weapon. Reach for it when you genuinely need to know "is the packet even arriving?" Always restrict it with a capture filter, or your disk fills up fast.

```bash
sudo tcpdump -i eth0 -n -s 0 'host api.example.com and tcp port 443' -w cap.pcap
```

Open the resulting `cap.pcap` in Wireshark. Retransmits suggest path loss; RSTs suggest a firewall or a hard server-side reject; clean FINs suggest a normal close. The TCP states and TLS handshake details from earlier in this series are exactly what you read with.

## How a Senior Engineer Thinks

- They write the hypothesis first and use tools to kill it. They do not start with a tool and then invent a story.
- They debug from two viewpoints — client and server — at the same time.
- They distrust "a restart fixed it." They assume they will see the same symptom again next week.
- They memorize the five-step command set so 3 a.m. them does not have to search.
- They leave a short post-mortem after every incident. The next person owes them five minutes back.

## Checklist

- [ ] Did you confirm the host is alive (`ping`, or `nc` if ICMP is blocked)?
- [ ] Did you confirm DNS resolves (`dig +short`)?
- [ ] Did you confirm TCP can connect (`nc -vz`)?
- [ ] Did you confirm the TLS handshake (`openssl s_client -servername`)?
- [ ] Did you look at the HTTP response yourself (`curl -v`)?
- [ ] Did you defer `tcpdump` until simpler tools ran out?

## Practice Problems

1. Give a one-line next action for each case: `nc -vz host port` returns "Connection refused"; `nc -vz host port` returns "timeout."
2. A user reports that the site "suddenly stopped working." Write the five commands you will run, in order, and what each output must look like for you to move on.
3. Write a `tcpdump` command that captures only traffic to and from `api.example.com` on port 443 and writes it to `cap.pcap`.

## Wrap-up and Next Steps

Network debugging is, in the end, **walking the layers and killing hypotheses**. Five lines — `ping`, `dig`, `nc`, `openssl s_client`, `curl -v` — usually decide where the problem lives within a minute. Only when those run out do you reach for `tcpdump`.

That closes Computer Networks 101. From "what is a network" through IP, TCP, DNS, HTTP, TLS, routing, load balancers, WebSocket, and now debugging — you have walked one full loop of what happens when you load a web page. The next time a pager fires at 3 a.m., I hope the first five commands come out without thinking.

<!-- toc:begin -->
- [What is a network?](./01-what-is-a-network.md)
- [IP and subnets](./02-ip-and-subnet.md)
- [TCP and UDP](./03-tcp-and-udp.md)
- [DNS](./04-dns.md)
- [HTTP and HTTPS](./05-http-and-https.md)
- [TLS basics](./06-tls-basics.md)
- [Routing and NAT](./07-routing-and-nat.md)
- [Load Balancer](./08-load-balancer.md)
- [WebSocket and Real-Time Communication](./09-websocket-and-realtime.md)
- **Debugging Network Problems (current)**
<!-- toc:end -->

## References

- [tcpdump Manual](https://www.tcpdump.org/manpages/tcpdump.1.html)
- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/)
- [`ss(8)` Linux Manual](https://man7.org/linux/man-pages/man8/ss.8.html)
- [Julia Evans — Networking debugging zines](https://wizardzines.com/zines/networking/)
