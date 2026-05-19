---
series: computer-networks-101
episode: 5
title: HTTP and HTTPS
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
  - HTTP
  - HTTPS
  - REST
  - Headers
seo_description: HTTP request and response anatomy, methods and status codes, important headers, and what the S in HTTPS actually adds — explained from the wire up.
last_reviewed: '2026-05-15'
---

# HTTP and HTTPS

> Computer Networks 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: What shape of message is HTTP, and what exactly does the "S" add when it appears?

> HTTP is a simple text-based request and response protocol. Method, path, headers, body — those four parts are enough to read every REST API and every website. HTTPS slips TLS underneath to stop eavesdropping, tampering, and impersonation. We cover TLS in detail in episode 6; today we just see its shadow.

<!-- a-grade-intro:end -->

This is post 5 in the Computer Networks 101 series.

## What You Will Learn

- The HTTP message structure (start line, headers, body)
- Common methods and status codes
- Important headers (Content-Type, Cache-Control, Authorization)
- Differences between HTTP/1.1, HTTP/2, and HTTP/3
- The three guarantees HTTPS provides

## Why It Matters

HTTP is the common language of essentially every service — backend, frontend, mobile, data, and ML serving. Misuse of methods and status codes silently breaks caching, retries, and error handling. HTTPS is the default now, but if you cannot answer "why?", certificate expiry, mixed content, and HSTS incidents stay mysteries.

> HTTP is "the agreed shape of a text message", and REST is a style that organizes those agreements around resources.

## Concept at a Glance

![HTTP request and the TLS layer that turns it into HTTPS](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/05/05-01-concept-at-a-glance.en.png)
*HTTP defines the message shape, while HTTPS adds TLS so the same message travels with confidentiality, integrity, and identity checks.*

Both requests and responses are "start line + headers + blank line + body".

## Key Terms

| Term | Meaning |
| --- | --- |
| Method | GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS |
| Status code | 1xx info, 2xx success, 3xx redirect, 4xx client error, 5xx server error |
| Header | Metadata (type, length, cache, auth) |
| Body | Actual data (JSON, HTML, binary) |
| TLS | The encryption layer that makes the S in HTTPS |

## Before / After

**Before — "HTTP is magic":**

```text
the browser fetches a page — done.
```

**After — "HTTP is a text message on top of TCP":**

```text
DNS → TCP handshake → (TLS handshake) → HTTP request/response → close
each step is measurable and debuggable
```

## Hands-on: Step by Step

### Step 1: see request and response with curl

```bash
curl -v https://example.com/
# > GET / HTTP/2
# > Host: example.com
# < HTTP/2 200
# < content-type: text/html; charset=UTF-8
```

`-v` shows headers and the TLS handshake.

### Step 2: a Python client

```python
import requests
r = requests.get(
    'https://api.github.com/repos/python/cpython',
    headers={'Accept': 'application/vnd.github+json'},
    timeout=5,
)
print(r.status_code, r.headers['content-type'])
print(r.json()['stargazers_count'])
```

### Step 3: the smallest HTTP server

```python
# server.py — Flask
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.get('/users/<int:uid>')
def get_user(uid):
    return jsonify(id=uid, name=f'user{uid}'), 200

@app.post('/users')
def create_user():
    body = request.get_json()
    return jsonify(id=99, **body), 201

if __name__ == '__main__':
    app.run(port=8000)
```

```bash
curl -s localhost:8000/users/42
curl -s -X POST localhost:8000/users -H 'Content-Type: application/json' -d '{"name":"a"}'
```

### Step 4: experiment with cache headers

```python
@app.get('/now')
def now():
    from datetime import datetime
    resp = jsonify(now=datetime.utcnow().isoformat())
    resp.headers['Cache-Control'] = 'max-age=60'
    return resp
```

Browsers, CDNs, and reverse proxies cache the same response for 60 seconds. The strongest performance tool in production is one header.

### Step 5: HTTPS verification

```bash
curl -v https://expired.badssl.com/   # expired cert → curl blocks
curl -v https://self-signed.badssl.com/   # self-signed → blocked
```

Browsers and curl validate the certificate chain to stop impersonating servers. We open the box in episode 6 (TLS).

## What to Notice in This Code

- Request and response are text messages (HTTP/2 and /3 use binary frames, but the meaning is identical)
- Methods are meaningful verbs: GET is read-only, POST creates
- Status codes are signals that clients, caches, and retries depend on
- One cache header can cut backend load in half

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using GET to mutate data | Proxies and retries change data unintentionally | Mutations go in POST / PUT / PATCH / DELETE |
| Returning every error as 200 | Breaks monitoring and retry policy | Use proper 4xx / 5xx |
| Skipping Content-Type | Clients fail to parse | Specify explicitly, e.g. `application/json` |
| Disabling HTTPS verification | MITM risk | Never disable in production |
| Sending big responses uncompressed every time | Bandwidth and latency spike | Use gzip / br, ETag, Last-Modified |

## How This Shows Up in Production

- REST APIs: resource + method combinations for CRUD
- GraphQL / gRPC: run on top of HTTP/2
- CDN: Cache-Control and ETag for edge caching
- Auth: Authorization header (bearer tokens, cookies)
- Monitoring: 5xx rate and p99 latency are the core indicators

## How a Senior Engineer Thinks

When designing an API, a senior engineer looks at method, status code, headers, and body together. Designs like "this is 200 but failure is signaled with an `errors` array" break clients and the caching and retry systems together. Following HTTP semantics is what makes external tooling work.

A senior also does not stop thinking at HTTP/1.1. They know how multiplexing in HTTP/2, 0-RTT in HTTP/3, and head-of-line blocking actually move user-perceived latency, and they weigh the risk and reward of adopting new features.

## Checklist

- [ ] I can name the four parts of an HTTP message
- [ ] I know the meaning of common methods and status codes
- [ ] I set Content-Type and Cache-Control correctly
- [ ] I can name the three HTTPS guarantees (confidentiality, integrity, identity)
- [ ] I can summarize HTTP/1.1, /2, and /3 in one line each

## Practice Problems

1. Run `curl -v` against a favorite site, capture the request and response headers, and explain what each header means.

2. Extend the Flask server above with ETag-based caching (`If-None-Match` → 304).

3. Answer in one paragraph from a threat-model perspective: "Why is every site HTTPS now?"

## Wrap-up and Next Steps

HTTP is an agreement about message shape, and REST is a style that organizes that agreement around resources. HTTPS adds the security guarantees of TLS on top. Handling methods, status codes, and headers correctly raises system quality immediately.

Next we open up the "S" — TLS basics.

<!-- toc:begin -->
- [What Is a Network?](./01-what-is-a-network.md)
- [IP and Subnet](./02-ip-and-subnet.md)
- [TCP and UDP](./03-tcp-and-udp.md)
- [DNS](./04-dns.md)
- **HTTP and HTTPS (current)**
- TLS basics (upcoming)
- Routing and NAT (upcoming)
- Load Balancer (upcoming)
- WebSocket and real-time (upcoming)
- Debugging network problems (upcoming)
<!-- toc:end -->

## References

- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN — HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [High Performance Browser Networking — Ilya Grigorik](https://hpbn.co/)

Tags: Computer Science, Networking, HTTP, HTTPS, REST, Headers
