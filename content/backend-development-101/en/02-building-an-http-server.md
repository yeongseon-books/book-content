---
series: backend-development-101
episode: 2
title: "Backend Development 101 (2/10): Building an HTTP Server"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Backend
  - HTTP
  - Python
  - FastAPI
  - Networking
seo_description: Build an HTTP server from a raw socket up to FastAPI to truly understand requests, responses, status codes, and headers.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (2/10): Building an HTTP Server

After using frameworks for a while, it is easy to forget what an HTTP server is actually doing. The moment a response gets truncated, a header disappears, or behavior changes behind a proxy, you have to go back down to raw requests and responses.

This is the 2nd post in the Backend Development 101 series. Here, we start from the fact that HTTP is text over a socket and use both a raw socket server and FastAPI to rebuild that mental model from the bottom up.


![backend development 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/02/02-01-concept-at-a-glance.en.png)
*backend development 101 chapter 2 flow overview*

## Questions to Keep in Mind

- The actual shape of an HTTP request and response?
- How HTTP rides on top of TCP?
- The meaning of status codes and headers?

## Why It Matters

Once you have *seen* what frameworks hide, every future debugging session gets faster. Without it, you guess at why a status code looks wrong or why a header is missing.

> Frameworks are convenient, but seniors know what is *behind* the framework.

Both request and response are just *blocks of text*.

## Key Terms

- **Request line**: `GET /path HTTP/1.1` — method, path, version.
- **Status line**: `HTTP/1.1 200 OK` — the first line of the response.
- **Header**: `Key: Value` metadata.
- **Body**: actual data (JSON, HTML, files).
- **Method**: GET, POST, PUT, DELETE — kinds of action.

## Before/After

**Before (the library hides everything)**

```python
import requests
print(requests.get("https://example.com").status_code)
```

**After (you watch the bytes)**

```python
import socket
s = socket.create_connection(("example.com", 80))
s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
print(s.recv(4096).decode()[:200])
```

Same effect, but the *protocol text* is now visible.

## Hands-on: Five Steps to a Real Server

### Step 1 — Raw socket server

```python
# 1_socket_server.py
import socket
srv = socket.socket()
srv.bind(("127.0.0.1", 9000))
srv.listen()
conn, _ = srv.accept()
data = conn.recv(1024)
print(data.decode())
conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello")
conn.close()
```

Open `http://127.0.0.1:9000/` in a browser to see `hello`.

### Step 2 — Same thing with FastAPI

```python
# 2_fastapi.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return "hello"
```

```bash
uvicorn 2_fastapi:app --port 9000
```

### Step 3 — Choose your status code

```python
# 3_status.py
from fastapi import FastAPI, HTTPException
app = FastAPI()

@app.get("/items/{i}")
def get_item(i: int):
    if i < 0:
        raise HTTPException(400, "i must be >= 0")
    return {"i": i}
```

### Step 4 — Custom headers

```python
# 4_headers.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/")
def root():
    return JSONResponse({"ok": True}, headers={"X-App": "demo"})
```

### Step 5 — Inspect with curl

```bash
curl -i http://127.0.0.1:9000/
```

`-i` shows the *headers and status line* alongside the body.

## Verification points

**Expected output:** the raw socket server should print the incoming request text in the terminal, and the browser or `curl -i` should show `HTTP/1.1 200 OK` plus `hello`.

### First failure modes to check

- If the browser hangs, inspect `Content-Length` and whether the connection gets closed.
- If the response parses oddly, confirm the line endings are `\r\n` rather than plain `\n`.
- If the FastAPI example does not boot, re-check the import path in `uvicorn 2_fastapi:app --port 9000`.

## What to Notice in This Code

- Without `Content-Length`, the client cannot know where the body ends.
- HTTP requires `\r\n` line endings — plain `\n` will break parsers.
- Same URL plus a different method means a *different action*.

## Five Common Mistakes

1. **Returning 200 even on errors.** Your monitoring breaks.
2. **Forgetting `Content-Type`.** Clients cannot decode JSON.
3. **Never closing the body.** Connections leak forever.
4. **Sending a body with GET.** Caches and proxies will drop it.
5. **Using only 200 and 500.** You lose the meaning of all the 4xx codes.

## Status Code Decision Table

Status codes are not documentation decoration. Caches, retry logic, alarms, dashboards, and SLA calculations all depend on them.

| Family | Meaning | Typical client behavior |
| --- | --- | --- |
| 2xx | Request succeeded | Process success, no retry |
| 3xx | Location/access changed | Follow redirect or apply policy |
| 4xx | Client request problem | Fix input and retry |
| 5xx | Server internal/transient failure | Backoff retry, trigger alarm |

When you need a specific code, this decision table is practical:

| Situation | Recommended code | Why |
| --- | --- | --- |
| New resource created | `201 Created` | States the creation explicitly |
| Async job accepted | `202 Accepted` | Not complete — only accepted |
| No body needed | `204 No Content` | Reduces parsing cost and ambiguity |
| Auth token missing/invalid | `401 Unauthorized` | Signals "authenticate first" |
| Insufficient permissions | `403 Forbidden` | Authenticated but forbidden |
| Resource does not exist | `404 Not Found` | Recoverable lookup failure |
| Input validation failed | `422 Unprocessable Entity` | Conveys field-level errors |
| Internal exception | `500 Internal Server Error` | Declares server responsibility |
| Temporary overload | `503 Service Unavailable` | Signals retry possibility |

Wrong codes create invisible failures. Hiding 500 behind 200 silences error-rate alarms and delays response. Sending 400 as 500 triggers unnecessary client retries that amplify traffic. Returning 404 as 200 lets CDN/browser caches store the wrong page.

## Headers That Cause Outages When Missing

These are not "nice to have" — omitting them commonly leads to production failures.

| Header | Controls | Typical failure when absent |
| --- | --- | --- |
| `Host` | Virtual host routing | Routed to wrong backend, or 400 |
| `Content-Length` | Body boundary | Truncated response, client hangs |
| `Content-Type` | Serialization/parsing | JSON treated as string, 415/422 |
| `Authorization` | Auth context | User identification fails, 401 cascade |
| `Accept` | Response representation | Unexpected format returned |
| `X-Forwarded-For` | Original client IP | Rate limit / audit log corruption |
| `X-Forwarded-Proto` | Original scheme (HTTP/HTTPS) | Redirect loop, secure cookie not set |
| `Connection` | Per-hop connection policy | Keep-alive confusion between proxies |

`Connection` is a hop-by-hop header — proxies must not forward it verbatim. Missing this causes subtle disconnects that only appear "behind the proxy."

## Raw Socket → `http.server` → FastAPI

The same HTTP protocol, but each layer automates more of the repetitive work.

### Level 1: Raw Socket

```python
# Learning: observe request/response boundaries directly
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 9000))
server.listen(5)

while True:
    conn, _ = server.accept()
    data = conn.recv(4096)

    # Demo: print only the first request line
    first_line = data.split(b"\r\n", 1)[0]
    print(first_line.decode("utf-8", errors="replace"))

    body = b'{"ok":true}'
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        + f"Content-Length: {len(body)}\r\n".encode()
        + b"Connection: close\r\n\r\n"
        + body
    )
    conn.sendall(response)
    conn.close()
```

When you build it yourself, the pain is obvious: request parsing, header normalization, exception handling, keep-alive, timeout, logging — all manual.

### Level 2: stdlib `http.server`

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"message":"hello"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

HTTPServer(("127.0.0.1", 9000), Handler).serve_forever()
```

The stdlib handles request-line parsing and basic headers. Routing, input validation, dependency injection, and async are still limited.

### Level 3: FastAPI

```python
from fastapi import FastAPI, HTTPException, Response

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items/{item_id}")
def get_item(item_id: int, response: Response):
    if item_id < 0:
        raise HTTPException(status_code=400, detail="item_id must be >= 0")

    response.headers["Cache-Control"] = "no-store"
    return {"item_id": item_id}
```

FastAPI automates routing, validation, documentation (OpenAPI), serialization, and exception mapping. The server's nature does not change — the safety nets increase.

## HTTP/1.1 Keep-Alive and Connection Reuse

HTTP/1.0 defaulted to closing after each response. HTTP/1.1 defaults to keep-alive. Modern environments assume "multiple requests over the same connection."

| Aspect | HTTP/1.0 default | HTTP/1.1 default |
| --- | --- | --- |
| Connection policy | Close after request-response | Reuse connection |
| Performance | Repeated handshake cost | Latency/CPU savings |
| Failure mode | Disconnects are relatively clear | Boundary errors cascade |

HTTP/1.1 pipelining theoretically allows sending multiple requests without waiting for responses, but head-of-line blocking and middlebox compatibility issues kept real-world adoption low. Today's production uses HTTP/1.1 keep-alive with multiple connections, or HTTP/2 multiplexing.

The key point: keep-alive itself is not the problem. The problem is that incorrect boundary information (wrong `Content-Length`) corrupts subsequent requests on the same connection.

## Operational Failure Patterns

### 1) Response appears truncated: wrong `Content-Length`

Symptom: intermittent JSON parse errors on mobile; occasional `net::ERR_CONTENT_LENGTH_MISMATCH` in browsers.

Cause: body is 512 bytes but `Content-Length: 480` was sent.

Fix: avoid manual length calculation — let the framework serialize. If a proxy handles gzip/brotli, clarify which layer owns the length.

### 2) Auth breaks only behind a proxy: hop-by-hop header mishandling

Symptom: local/direct calls work fine; sessions become unstable through the API Gateway.

Cause: an intermediate proxy forwards or strips tokens declared in the `Connection` header, removing expected headers.

Fix: distinguish end-to-end headers (`Authorization`, `X-Request-Id`) from hop-by-hop headers, and audit proxy rules.

### 3) Client waits forever: missing close or missing boundary

Symptom: some SDK calls hang until timeout.

Cause: no `Content-Length`, no `Transfer-Encoding: chunked`, and the connection is never closed.

Fix: satisfy at least one of: explicit length, chunked encoding, explicit connection close.

### 4) Monitoring shows all 200 but user complaints rise

Symptom: error dashboard at 0%; support tickets about failures increasing.

Cause: business failures sent as `{ "ok": false }` inside a 200 response.

Fix: use 4xx/5xx matching the failure type. Reserve 2xx for actual success. Align monitoring SLIs with the response contract.

## Debugging Tools: How Deep to Go

### 1) `curl -v`

```bash
curl -v -H "Accept: application/json" http://127.0.0.1:9000/items/1
```

- Shows request and response headers simultaneously.
- Quick hints on TLS, redirects, and connection reuse.

### 2) HTTPie

```bash
http --print=HhBb GET :9000/items/1 Authorization:"Bearer demo"
```

- Human-readable output separating headers from body.
- Useful for regression checks on API contracts.

### 3) tcpdump / Wireshark

- Final ground truth when application logs and proxy logs disagree.
- Packet capture is expensive — narrow down with `curl -v` and access logs first, then capture only the minimal segment.

## Common Mistakes and Their Real Cost

| Mistake | Why it happens | Actual cost |
| --- | --- | --- |
| Returning all failures as 200 | "Easier for the client to parse" misconception | Alarms silenced, incident detection delayed |
| Omitting `Content-Type` | Assuming the framework will add it | Parsing mismatch across languages/SDKs |
| Designing meaningful body on GET | Internal-only thinking | Proxy/cache/SDK compatibility collapse |
| Undefined proxy trust boundary | Unclear infra/app team ownership | IP spoofing accepted, HTTPS detection fails |
| Default timeout left unchanged | Hard to reproduce locally | Thread exhaustion, queue backlog, cascading failure |

The common thread: verifying "it works now" without considering "how long this contract lives." HTTP contracts are not team-internal rules — they are a shared language interpreted by browsers, mobile SDKs, proxies, and monitoring systems together.

## Verifying the Request-Response Contract

Functional tests passing does not mean the HTTP contract is intact. Serialization library upgrades, proxy config changes, or compression toggles can alter the protocol surface. Stability requires a "protocol test" layer separate from business tests.

A minimal routine a team can adopt immediately:

1. **Capture a contract snapshot.** Use `curl -v` or HTTPie to record 5–10 representative requests. Save status code, headers, and body samples as a baseline.
2. **Compare in the deploy pipeline.** Even if regression tests pass, flag a failure when a status code changes or `Cache-Control` disappears.
3. **Verify through the proxy separately.** Compare direct-to-app results with gateway-routed results to catch hop-by-hop issues early.

A table-based checklist reduces omissions:

| Check item | Expected value | Impact on failure |
| --- | --- | --- |
| Create API status code | `201` | Client follow-up branch fails |
| Validation failure status | `422` or `400` | Retry policy distortion |
| Response `Content-Type` | `application/json` | SDK parsing failure |
| Response `Cache-Control` | Matches endpoint policy | Over-cache or over-fetch |
| `X-Request-Id` propagation | Consistent ingress→app→egress | Incident trace time increases |

## Same Body, Different Headers — the Difference It Makes

Even identical JSON bodies produce different client behavior depending on headers.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 11

{"ok":true}
```

Most clients parse this as JSON immediately. But without `Content-Type`:

```http
HTTP/1.1 200 OK
Content-Length: 11

{"ok":true}
```

Browser `fetch` may require a manual `JSON.parse` call, and some internal SDKs default to `text/plain` and throw a parse error. From the server's perspective "the body is the same," but from the consumer's perspective the contract is entirely different.

`Cache-Control` works similarly. Omitting a cache-allow policy on a read API means every call reaches the origin server, creating a bottleneck at peak. Omitting `no-store` on sensitive-data responses lets information linger on shared terminals. Headers are operational parameters controlling both performance and security.

## How This Shows Up in Production

In production, FastAPI handles the socket plumbing for you. But when an outage hits — responses missing, connections truncated — you still have to drop down to sockets and headers. tcpdump, Wireshark, and curl are the basic backend debugger trio.

## How a Senior Engineer Thinks

A senior does not abandon frameworks to write socket code every day. The opposite: they use frameworks aggressively but design observation points so they can drop to protocol level during incidents. For example, they decide during feature development "which layer issues the request ID and how far it propagates" and "what rules classify 4xx/5xx for the dashboard."

Status codes and headers are not implementation details — they are the surface of operational policy. A team that documents only 200/400/500 and a team that specifies 201/202/204/409/422/503 differ in incident recovery speed. The latter makes failures into classifiable events, so retry policies, user messages, and alert thresholds all align.

In environments with growing network boundaries, "what the client actually received" matters more than "what my service sent." Load balancers, CDNs, and API Gateways can add, remove, or transform headers. Seniors trust end-to-end capture and log correlation over local success screens. Building an HTTP server means more than writing endpoint functions — it includes operational design that maintains the end-to-end contract.

## Checklist

- [ ] You can read the first line of an HTTP request.
- [ ] You can tell 4xx from 5xx.
- [ ] You can use `curl -i` to see headers.
- [ ] You can set a status code in FastAPI.
- [ ] You have run a raw-socket server at least once.

## Practice Problems

1. Modify the raw-socket server to return JSON with a `Content-Type: application/json` header.
2. In FastAPI, add a `/error` route that returns 503.
3. Use `curl -v` against your server and capture the entire request and response text.

## Wrap-up and Next Steps

An HTTP server is a *text-protocol program*. Next, we add the layer that decides *which function handles which path* — the router.

## Answering the Opening Questions

- **What does an HTTP request and response actually look like as text?**
  - Request line/status line, headers, blank line, body—with `\r\n` boundaries and `Content-Length` as parsing anchors. Human-readable text that machines interpret strictly.
- **How does HTTP operate on top of TCP?**
  - Open a TCP connection (connect), send request bytes, receive response bytes, close or reuse (keep-alive). In HTTP/1.1 connection reuse is default, so a wrong response boundary cascades errors into subsequent requests.
- **Why are status codes and headers contracts, not decoration?**
  - Status codes are branch conditions for retry, cache, and monitoring; headers are inputs for routing, auth, parsing, and security policy. Misusing them creates observability gaps—"monitoring says OK but users fail"—and delays incident response.

<!-- toc:begin -->
## In this series

- [Backend Development 101 (1/10): What Is Backend Development?](./01-what-is-backend-development.md)
- **Building an HTTP Server (current)**
- Routing and Controllers (upcoming)
- The Service Layer (upcoming)
- The Database Layer (upcoming)
- Authentication and Authorization (upcoming)
- Logging and Error Handling (upcoming)
- Testing the Backend (upcoming)
- Deploying the Backend (upcoming)
- A Production-Ready Backend Structure (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [HTTP messages (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)
- [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [FastAPI responses](https://fastapi.tiangolo.com/advanced/response-directly/)

### Further Reading

- [curl manual](https://curl.se/docs/manual.html)

Tags: Backend, HTTP, Python, FastAPI, Networking
