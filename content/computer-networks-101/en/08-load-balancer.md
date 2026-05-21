---
series: computer-networks-101
episode: 8
title: "Computer Networks 101 (8/10): Load Balancer"
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
  - Load Balancer
  - L4
  - L7
  - Health Check
seo_description: How a load balancer distributes traffic and isolates failures, the differences between L4 and L7, and the cost of sticky sessions in production.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (8/10): Load Balancer

> Computer Networks 101 series (8/10)

**Core question**: With 100 servers behind one domain, how does the client always reach a "live and good enough" server?

> A load balancer hides many backends behind one virtual IP, distributes traffic, and removes dead servers. An L4 LB balances based on IP and port. An L7 LB understands HTTP and routes by path or header. Both are the front door of modern services and the first line of reliability.

This is post 8 in the Computer Networks 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Load Balancer?
- Which signal should the example or diagram make visible for Load Balancer?
- What failure should be prevented first when Load Balancer reaches a real system?

## Big Picture

![computer networks 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/08/08-01-concept-at-a-glance.en.png)

*computer networks 101 chapter 8 flow overview*

This picture places Load Balancer inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The difference between an L4 LB and an L7 LB
- Distribution algorithms (round-robin, least connections, hash)
- Health checks and graceful drain
- Sticky sessions and their cost

## Why It Matters

A load balancer is more than a distributor — it is the device that decides reliability and deployment strategy. Blue-green deploys, canary releases, region failover, and autoscaling all happen on top of the LB. One wrong line in a health check sends traffic to a dead server or removes a healthy one entirely.

> A load balancer is not a tool for picking the "best" server. It is a tool for picking a "good enough, live" server quickly.

An L4 LB sees only TCP flows. An L7 LB balances per HTTP request.

## Key Terms

| Term | Meaning |
| --- | --- |
| Virtual IP (VIP) | The LB address that clients see |
| Health check | Periodic check that the backend is alive |
| Round-robin | Distribute in order |
| Least connections | Send to the backend with the fewest current connections |
| Sticky session | Same client always to the same backend (cookie or IP hash) |

## Before / After

**Before — "one server until it dies":**

```text
client → app1
app1 dies → service down
```

**After — "many backends + LB":**

```text
client → LB → [app1, app2, app3]
app1 dies → health check removes it, traffic flows to the rest
```

## Hands-on: Step by Step

### Step 1: bring up two backends

```python
# backend.py — Flask
from flask import Flask
import os, sys
name = sys.argv[1] if len(sys.argv) > 1 else 'a'
app = Flask(__name__)
@app.get('/')
def home(): return f'hello from {name}\n'
@app.get('/health')
def health(): return 'ok', 200
if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 9001)))
```

```bash
PORT=9001 python backend.py app1 &
PORT=9002 python backend.py app2 &
```

### Step 2: an L7 LB with nginx

```nginx
# nginx.conf (snippet)
upstream backend {
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
server {
    listen 8080;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

```bash
nginx -c $(pwd)/nginx.conf
for i in 1 2 3 4; do curl -s localhost:8080/; done
# hello from app1
# hello from app2
# hello from app1
# hello from app2
```

The default is round-robin.

### Step 3: add a health check

```nginx
upstream backend {
    server 127.0.0.1:9001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:9002 max_fails=2 fail_timeout=10s;
}
```

If `/health` keeps failing, nginx pauses traffic to that backend for a while. For richer active health checks, use nginx Plus, envoy, or HAProxy.

### Step 4: change the algorithm

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

When request times vary, least connections lowers average latency.

### Step 5: sticky session

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:9001;
    server 127.0.0.1:9002;
}
```

`ip_hash` sends the same client IP to the same backend. It is a temporary fix when sessions live in memory; the right answer is to make the service stateless.

## Step 6: Design graceful drain and canary together

The load balancer matters most during a deploy, not during a demo. Instead of flipping all traffic at once, let only a small share of new connections hit the new version while old connections drain naturally.

```nginx
upstream backend {
    server 127.0.0.1:9001 weight=19;
    server 127.0.0.1:9002 weight=1;
}
```

A 19:1 split is roughly a 5% canary. The usual sequence looks like this.

1. Add the new version to the pool at a low weight.
2. Watch error rate plus p95/p99 latency for a short window.
3. Raise the weight gradually if the signals stay clean.
4. Mark the old instance unhealthy for new traffic, let in-flight requests finish, then stop it.

Sticky sessions make this harder because traffic weight no longer maps cleanly to user weight. The same users stay pinned to the same backends, so you lose control over who actually experiences the canary.

## What to Notice in This Code

- The value of an LB is in health checks and deployment strategy, not just distribution
- L4 (TCP) is fast but blind to HTTP. L7 enables routing, retries, and header manipulation
- Sticky sessions are an easy patch that block free scaling
- Where TLS terminates (LB or backend) affects security and operations

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Health check too simple (`/`) | Misses partial failures | `/health` that exercises real dependencies |
| Health-check interval too long | Dead server stays in rotation | 1–5 second intervals + short fail timeout |
| Killing without graceful drain | In-flight requests dropped | SIGTERM → fail health check → drain → kill |
| Sticky sessions everywhere | Hard to scale and deploy | Move sessions to Redis or JWT |
| Trusting only L7 | Bad fit for non-HTTP / low-latency workloads | Use L4 or specialized LBs |

## How This Shows Up in Production

- Cloud: AWS ALB (L7) / NLB (L4), GCP HTTP(S) LB
- Internal microservices: envoy / Istio sidecars
- Proxy + cache: nginx, HAProxy, Caddy
- Databases: pgbouncer, ProxySQL as specialized LBs
- Global traffic: anycast plus DNS-based GeoLB

## How a Senior Engineer Thinks

A senior engineer treats the LB as the first line of service stability, not just a distributor. The first thing they sketch for a new service is the LB's health check and deployment sequence. Patterns like canary, blue-green, and weighted routing become possible or impossible depending on a single LB setting.

A senior also accepts the LB's limits. To prevent the LB itself from being a single point of failure, they make it redundant (active-active or active-standby) and combine higher-layer mechanisms like DNS round-robin and anycast.

## Checklist

- [ ] I know the difference between L4 and L7
- [ ] I can design a health-check policy
- [ ] I know the cost of sticky sessions
- [ ] I know the graceful drain procedure
- [ ] I plan for LB redundancy

## Practice Problems

1. Extend the nginx example, kill one backend, and observe how the health check shifts traffic.

2. Sketch a canary deployment scenario. How must the LB change to send only 5% to a new version?

3. Explain in one paragraph: "Why should sticky sessions be avoided when possible?"

## Wrap-up and Next Steps

A load balancer does the simple job of "hide many servers behind one address and pick a live one" in many variations. Health checks, deployment strategy, sticky-session cost, and TLS termination location — these four levers move reliability the most.

Next we move from request/response to bidirectional streams — WebSocket and real-time communication.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Load Balancer?**
  - The article treats Load Balancer as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Load Balancer?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Load Balancer reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Networks 101 (1/10): What Is a Network?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP and Subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP and UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP and HTTPS](./05-http-and-https.md)
- [Computer Networks 101 (6/10): TLS Basics](./06-tls-basics.md)
- [Computer Networks 101 (7/10): Routing and NAT](./07-routing-and-nat.md)
- **Load Balancer (current)**
- WebSocket and Real-Time Communication (upcoming)
- Debugging Network Problems (upcoming)

<!-- toc:end -->

## References

- [NGINX HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [HAProxy Documentation](https://docs.haproxy.org/)
- [Envoy Proxy Docs](https://www.envoyproxy.io/docs)
- [AWS ELB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/)
- [Google SRE Book — Handling Overload](https://sre.google/sre-book/handling-overload/)

Tags: Computer Science, Networking, Load Balancer, L4, L7, Health Check
