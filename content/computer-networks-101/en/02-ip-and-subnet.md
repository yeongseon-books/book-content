---
series: computer-networks-101
episode: 2
title: "Computer Networks 101 (2/10): IP and Subnet"
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
  - IP
  - Subnet
  - CIDR
  - Routing
seo_description: IP addresses and subnets explained — how CIDR splits an address into network and host parts and why routing, NAT, and firewall rules all start here.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (2/10): IP and Subnet

> Computer Networks 101 series (2/10)

**Core question**: Is an "IP address" just a number stuck on one computer, or is it a coordinate that also tells you which neighborhood the computer lives in?

> An IP address has to be read as two parts — which network, and which host inside that network. The subnet mask defines that split, and CIDR is the short way to write it. Routing, NAT, firewall rules, and container networks all run on top of this split.

This is post 2 in the Computer Networks 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying IP and Subnet?
- Which signal should the example or diagram make visible for IP and Subnet?
- What failure should be prevented first when IP and Subnet reaches a real system?

## Big Picture

![computer networks 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/02/02-01-concept-at-a-glance.en.png)

*computer networks 101 chapter 2 flow overview*

This picture places IP and Subnet inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The difference between IPv4 and IPv6
- Subnet masks and CIDR notation
- How to calculate the network address, broadcast address, and number of usable hosts
- Private vs public IPs

## Why It Matters

If you memorize an IP address as "the number for one machine", routing, NAT, and firewalls look like magic. Every network device actually splits the IP into a network part and a host part and decides where to forward based only on the network part. If you cannot read a subnet, cloud VPCs, Kubernetes network policies, and corporate firewall rules all become guessing games.

> What a router sees is not the IP address but the network part of the IP address.

> An IP address is a 32-bit number (IPv4) or a 128-bit number (IPv6). The subnet mask is a ruler that says where the network part ends and the host part begins. CIDR (`/24`, `/16`, etc.) writes the length of that ruler in bits.

## Key Terms

| Term | Meaning |
| --- | --- |
| IPv4 / IPv6 | 32-bit / 128-bit address spaces |
| Subnet mask | Bit pattern that separates network and host parts |
| CIDR | Prefix-length notation like `192.168.10.0/24` |
| Network address | Address with all host bits set to 0 |
| Broadcast address | Address with all host bits set to 1 (IPv4) |
| Private IP | Ranges that are not routed on the Internet (10/8, 172.16/12, 192.168/16) |

## Before / After

**Before — "an IP is just a number":**

```text
"192.168.0.5 is my laptop's number" — done.
```

**After — "an IP is network + host":**

```text
192.168.0.5/24
└─ host 5 inside network 192.168.0.0/24
nodes inside the same /24 talk directly without a router
to reach a different network, packets must cross a router
```

## Hands-on: Step by Step

### Step 1: check your IP

```bash
ip addr show       # Linux
ifconfig           # macOS
ipconfig           # Windows
```

A line like `inet 192.168.0.42/24` shows both the IP and the prefix.

### Step 2: read the routing table

```bash
ip route
# default via 192.168.0.1 dev wlan0
# 192.168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.42
```

Destinations in the same `/24` go directly. Everything else goes to the default gateway (192.168.0.1).

### Step 3: subnet calculation in code

```python
import ipaddress

net = ipaddress.ip_network('192.168.10.0/24')
print(net.network_address)   # 192.168.10.0
print(net.broadcast_address) # 192.168.10.255
print(net.num_addresses)     # 256
print(list(net.hosts())[:3]) # [192.168.10.1, .2, .3]

ip = ipaddress.ip_interface('192.168.10.42/24')
print(ip.network)            # 192.168.10.0/24
```

### Step 4: same-subnet check

```python
import ipaddress

a = ipaddress.ip_address('192.168.10.42')
b = ipaddress.ip_address('192.168.10.99')
c = ipaddress.ip_address('192.168.20.1')
net = ipaddress.ip_network('192.168.10.0/24')

print(a in net, b in net, c in net)   # True True False
```

Same subnet means direct delivery. Otherwise the packet must cross a router.

### Step 5: tell private from public

```python
import ipaddress

for s in ['10.0.0.5', '172.16.3.4', '192.168.1.1', '8.8.8.8']:
    ip = ipaddress.ip_address(s)
    print(s, 'private' if ip.is_private else 'public')
```

Devices in homes and offices mostly use private IPs and reach the Internet through NAT (episode 7).

## What to Notice in This Code

- `ip_network` is per network, `ip_interface` is per host with "IP + prefix"
- Prefix length is not just a notation shortcut — it is the basic unit of routing
- Private vs public detection is a standard feature of `ipaddress`
- "Same subnet?" is the same question as "no router needed?"

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Always assuming `/24` | Collisions in VPCs and Kubernetes | State the prefix length explicitly |
| Using network or broadcast address as a host | Communication fails | Pick from `hosts()` only |
| Thinking private IPs are reachable from the Internet | Security and connectivity bugs | Use NAT or assign a public IP |
| IPv4-only code | Fails on dual-stack environments | Abstract through `ip_address` |
| Treating subnets as just grouping | Ignores routing and security policy | Subnets are the unit of routing |

## How This Shows Up in Production

- AWS VPC: a `/16` VPC split into multiple `/24` subnets per availability zone
- Kubernetes: separate prefixes for pod CIDR and service CIDR
- Firewalls: rules like "allow traffic from 10.0.0.0/8"
- VPNs: prefix planning to avoid collisions with other corporate networks
- Game servers: fast internal traffic between adjacent servers in the same subnet

## How a Senior Engineer Thinks

Before designing new infrastructure, a senior engineer draws an "IP plan" first. Which prefix goes where, are there collisions with other corporate networks, and is there enough host capacity for the next N years? Prefix decisions are very hard to undo once they are baked in.

A senior also looks at both endpoints' IPs, subnets, routing tables, and firewall rules first when someone asks "why doesn't this work?". The network topology has to be in your head before any application-level debugging.

## Checklist

- [ ] I know what `/24`, `/16`, and `/8` mean in CIDR
- [ ] I can compute network and broadcast addresses
- [ ] I can decide if two IPs are in the same subnet
- [ ] I know the private vs public ranges
- [ ] I draw an IP plan before drawing a new system

## Practice Problems

1. Compute the network address, broadcast address, and number of usable hosts for `10.20.0.0/22`.

2. Decide whether `172.16.5.10` and `172.16.5.130` are in the same `/25` subnet.

3. Assume your company uses a `/16`. Draw a plan that gives each of five teams its own `/20`.

## Wrap-up and Next Steps

An IP address is not the coordinate of one computer. It is "the Nth host of which network". Subnets and CIDR define that split, and routing, NAT, firewalls, and VPCs all run on top of it.

Next we compare the two transport protocols that ride on top of IP — TCP and UDP.

## Answering the Opening Questions

- **What boundary should you inspect first when applying IP and Subnet?**
  - The article treats IP and Subnet as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for IP and Subnet?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when IP and Subnet reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Networks 101 (1/10): What Is a Network?](./01-what-is-a-network.md)
- **IP and Subnet (current)**
- TCP and UDP (upcoming)
- DNS (upcoming)
- HTTP and HTTPS (upcoming)
- TLS Basics (upcoming)
- Routing and NAT (upcoming)
- Load Balancer (upcoming)
- WebSocket and Real-Time Communication (upcoming)
- Debugging Network Problems (upcoming)

<!-- toc:end -->

## References

- [RFC 791 — Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 4632 — CIDR](https://www.rfc-editor.org/rfc/rfc4632)
- [Python `ipaddress` module documentation](https://docs.python.org/3/library/ipaddress.html)
- [Cloudflare Learning — What is an IP address?](https://www.cloudflare.com/learning/dns/glossary/what-is-my-ip-address/)

Tags: Computer Science, Networking, IP, Subnet, CIDR, Routing
