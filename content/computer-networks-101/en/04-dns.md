---
series: computer-networks-101
episode: 4
title: "Computer Networks 101 (4/10): DNS"
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
  - DNS
  - Resolver
  - Caching
  - TTL
seo_description: How a domain name turns into an IP address — the DNS hierarchy, recursive resolvers, record types, and what TTL really means in production.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (4/10): DNS

> Computer Networks 101 series (4/10)

**Core question**: When you type `example.com` in a browser, how do those letters turn into exactly one IP address so a packet can leave?

> DNS is a "name to address" translation system. It is not a single server but a worldwide hierarchy — root, TLD, authoritative — with resolvers and caches in between so the same query is not repeated. That caching is both the source of the Internet's speed and the source of its most frequent incidents.

This is post 4 in the Computer Networks 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying DNS?
- Which signal should the example or diagram make visible for DNS?
- What failure should be prevented first when DNS reaches a real system?

## Big Picture

![computer networks 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/04/04-01-concept-at-a-glance.en.png)

*computer networks 101 chapter 4 flow overview*

This picture places DNS inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of DNS is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- The DNS hierarchy (root → TLD → authoritative)
- Recursive resolvers and caching
- Record types like A, AAAA, CNAME, MX, TXT
- What TTL means and the operational traps around it

## Why It Matters

Half of "the Internet does not work" turns out to be DNS, and a large share of that is misunderstanding TTL and caches. Without understanding DNS, "it still goes to the old IP after deploy" stays a mystery and service migrations or region failovers take much longer than they should. Every HTTP request also starts with a DNS lookup, so it always shows up in performance analysis.

> "It's always DNS" — a joke among operators that is more than half true.

## Concept at a Glance

> A client asks the OS stub resolver, which usually asks the ISP or company recursive resolver. The recursive resolver walks root → TLD → authoritative, finds the answer, and caches it for the TTL.

## Key Terms

| Term | Meaning |
| --- | --- |
| A / AAAA | Domain → IPv4 / IPv6 address |
| CNAME | Domain → another domain (alias) |
| MX | Domain → mail server |
| TXT | Arbitrary text (SPF, DKIM, domain verification) |
| TTL | Cache time-to-live in seconds |

## Before / After

**Before — "DNS is some big dictionary":**

```text
example.com → how? no idea.
```

**After — "DNS is a distributed tree plus caches":**

```text
. → com → example.com → A 93.184.216.34
each step is a different server; the resolver follows the delegation
```

## Hands-on: Step by Step

### Step 1: a single lookup with dig

```bash
dig example.com +noall +answer
# example.com.  86400  IN  A  93.184.216.34
```

The 86400 is the TTL in seconds. The answer can be cached for up to 24 hours.

### Step 2: trace the delegation

```bash
dig example.com +trace
# .                ← root
# com.             ← TLD
# example.com.     ← authoritative
```

You see the exact path the resolver walks.

### Step 3: different record types

```bash
dig MX gmail.com +short
dig AAAA cloudflare.com +short
dig TXT _dmarc.gmail.com +short
```

A single domain can carry many record types at the same time.

### Step 4: lookup from Python

```python
import socket

print(socket.gethostbyname('example.com'))   # 93.184.216.34
print(socket.getaddrinfo('example.com', 443, type=socket.SOCK_STREAM))
# Uses the OS stub resolver
```

Or more precisely:

```python
import dns.resolver   # pip install dnspython

ans = dns.resolver.resolve('example.com', 'A')
for r in ans:
    print(r.to_text(), 'TTL', ans.rrset.ttl)
```

### Step 5: see DNS packets with tcpdump

```bash
sudo tcpdump -i any -nn 'udp port 53'
# A? example.com
# A 93.184.216.34
```

DNS uses UDP port 53 by default, falling back to TCP for large responses (DNSSEC, EDNS, and so on).

## What to Notice in This Code

- DNS lookup is the first step of every HTTP request — without a cache, it adds hundreds of milliseconds
- TTL is not a hard deadline but a cache "best-before" hint
- One domain can carry many A or AAAA records (round-robin, geo-based)
- A long CNAME chain makes lookups slow

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Leave TTL at 1 day, expect instant IP changes | Slow rollout because of client caches | Lower TTL to 60 seconds before migrating |
| Patch with `/etc/hosts` and forget | Persistent mystery | Revert immediately after testing |
| Trust nslookup alone | App may use a different resolver | Run dig inside the app container |
| Suspect DNS for every issue | Wastes diagnosis time | Combine ping, curl, and dig to isolate |
| Point a CNAME at the root domain | RFC violation, breaks some resolvers | Use ALIAS / ANAME alternatives |

## How This Shows Up in Production

- Service migration: lower TTL beforehand, then change the IP
- CDN: respond with different IPs based on user location (GeoDNS)
- Failover: authoritative returns a different IP based on health checks
- Mail: SPF, DKIM, DMARC are all TXT records
- Containers: in-cluster DNS (coredns) translates Service names to ClusterIP

## How a Senior Engineer Thinks

A senior engineer has the simple habit of checking TTL before changing an IP. They always remember that DNS change is "cache expiry", not "propagation". That single fact — that DNS is not real-time — explains the most common DNS-driven outages.

A senior also does not blindly trust `nslookup`. They check the resolver the application actually uses (resolv.conf inside the container, the coredns policy in Kubernetes, libc vs getaddrinfo differences). The same name can resolve differently across environments, and that is part of the design.

## Checklist

- [ ] I can name the DNS hierarchy (root → TLD → authoritative)
- [ ] I know what A, AAAA, CNAME, MX, and TXT are for
- [ ] I can trace delegations with dig
- [ ] I know how TTL affects operations
- [ ] I lower TTL before changing DNS

## Practice Problems

1. Run dig for the A, MX, and TXT records of a site you visit often, and explain what you see in one paragraph.

2. Assume you operate a temporary domain with TTL 60 seconds. Walk through how user impact changes when the IP is updated.

3. Capture DNS queries and responses with tcpdump, then explain why the second lookup of the same name is faster.

## Wrap-up and Next Steps

DNS is the Internet's phone book and the caching system behind half of operational incidents. Once the hierarchy and TTL click, deploys, migrations, and failovers suddenly become predictable.

Next we look at the message we actually send to the IP we found — HTTP and HTTPS.

## Answering the Opening Questions

- **What boundary should you inspect first when applying DNS?**
  - The article treats DNS as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for DNS?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when DNS reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Networks 101 (1/10): What Is a Network?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP and Subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP and UDP](./03-tcp-and-udp.md)
- **DNS (current)**
- HTTP and HTTPS (upcoming)
- TLS Basics (upcoming)
- Routing and NAT (upcoming)
- Load Balancer (upcoming)
- WebSocket and Real-Time Communication (upcoming)
- Debugging Network Problems (upcoming)

<!-- toc:end -->

## References

- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- [Cloudflare Learning — What is DNS?](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [dnspython documentation](https://www.dnspython.org/)
- [Julia Evans — How DNS works (zine)](https://wizardzines.com/zines/dns/)

Tags: Computer Science, Networking, DNS, Resolver, Caching, TTL
