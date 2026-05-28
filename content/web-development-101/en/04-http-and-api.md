---
series: web-development-101
episode: 4
title: "Web Development 101 (4/10): HTTP and APIs"
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
  - WebDevelopment
  - HTTP
  - API
  - REST
  - Networking
seo_description: The shape of HTTP requests and responses — methods, status codes, headers, and JSON APIs explained for new web developers with runnable examples.
last_reviewed: '2026-05-15'
---

# Web Development 101 (4/10): HTTP and APIs

Most web bugs eventually reduce to one question: what exactly did the client send, and what exactly did the server send back? If you cannot picture the request line, headers, body, and status code, debugging a frontend fetch call or a backend route quickly turns into guesswork.

This is the 4th post in the Web Development 101 series. Here we treat HTTP as the shared contract between browser, script, and server so you can read methods, status codes, headers, and JSON payloads with much more confidence.


![web development 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/04/04-01-concept-at-a-glance.en.png)
*web development 101 chapter 4 flow overview*

## Questions to Keep in Mind

- The shape of HTTP requests and responses?
- Methods (GET/POST/PUT/DELETE) and status codes?
- The role of headers?

## Why It Matters

Half of web work is *building and reading HTTP messages*. If you cannot picture the message, debugging becomes guesswork. Learn it once and it transfers to every framework.

> HTTP is *a protocol made of plain text*.

Keep this frame in mind while reading every example in the chapter: the client sends method, URL, headers, and possibly a body; the server answers with status, headers, and a body. Everything else is detail layered on top.

### What to verify yourself

- Run `curl -v https://httpbin.org/get` and inspect the raw request and response lines.
- Send both GET and POST requests to the same service and compare how the method changes behavior.
- Confirm that a JSON API returns `Content-Type: application/json` before parsing the body.

**Expected output:** The method changes server intent, and JSON endpoints advertise that intent through both status codes and headers.

**Failure mode to watch for:** If every failure still returns 200, clients lose a reliable error boundary. If `Content-Type` is ignored, HTML and JSON can be parsed the wrong way.

## Key Terms

- **Method**: what to do (GET reads, POST creates, etc.).
- **Status code**: outcome (2xx success, 4xx client error, 5xx server error).
- **Header**: metadata (Content-Type, Authorization, etc.).
- **Body**: actual payload (JSON, HTML, image bytes).
- **API**: a *programmatic endpoint* meant for code, not browsers.

## Before/After

**Before (HTML page request)**

```python
import requests
r = requests.get("https://example.com")
print(r.text[:80])  # <!doctype html>...
```

**After (JSON API call)**

```python
import requests
r = requests.get("https://api.github.com/repos/python/cpython")
data = r.json()
print(data["full_name"], data["stargazers_count"])
```

Same HTTP, different *Content-Type*.

## Hands-on: HTTP Messages in 5 Steps

### Step 1 — A GET request

```python
# 1_get.py
import requests
r = requests.get("https://httpbin.org/get?lang=en")
print(r.status_code)
print(r.json()["args"])  # {'lang': 'en'}
```

### Step 2 — POST with a body

```python
# 2_post.py
import requests
r = requests.post("https://httpbin.org/post", json={"name": "yeongseon"})
print(r.json()["json"])
```

### Step 3 — Inspect headers

```python
# 3_headers.py
import requests
r = requests.get("https://httpbin.org/headers", headers={"X-Custom": "hi"})
print(r.json()["headers"]["X-Custom"])
```

### Step 4 — Branch on status code

```python
# 4_status.py
import requests
for url in ["https://httpbin.org/status/200", "https://httpbin.org/status/404"]:
    r = requests.get(url)
    if r.ok:
        print("OK", r.status_code)
    else:
        print("FAIL", r.status_code)
```

### Step 5 — See it raw

```bash
curl -v https://httpbin.org/get
# > GET /get HTTP/1.1
# > Host: httpbin.org
# < HTTP/1.1 200 OK
# < Content-Type: application/json
```

## What to Notice in This Code

- Whether `Content-Type` is `text/html` or `application/json` changes *everything*.
- POST is the promise that *server state may change*.
- The same URL behaves differently per method.

## Five Common Mistakes

1. **Creating data with GET.** GET is *read-only* by contract.
2. **Returning 200 for every response.** Clients cannot distinguish errors.
3. **Ignoring `Content-Type`.** You parse HTML as JSON.
4. **Free-form error bodies.** Clients cannot extract the message.
5. **Putting auth in the URL.** It leaks into logs forever.

## How This Shows Up in Production

Most mobile and web apps talk to servers as *JSON over HTTP*. GraphQL and gRPC also ride on HTTP. The first thing you reach for in a new service is the *API documentation*.

## How a Senior Engineer Thinks

- Use methods and status codes for their *intended* meaning.
- Standardize the shape of error bodies.
- Auth in *headers*, tokens with *short lifetimes*.
- Always set a *time budget* (timeout).
- API and docs grow together.

## Checklist

- [ ] You know the meaning of the four common methods.
- [ ] You know what 2xx, 4xx, and 5xx ranges mean.
- [ ] You can read `Content-Type` and branch on it.
- [ ] You can set timeout and retry.
- [ ] You can fire a raw curl request.

## Practice Problems

1. Send GET, POST, PUT, and DELETE to `httpbin.org/anything` and compare responses.
2. Write code that does *not* follow a 3xx redirect.
3. Pick a public API and call *three of its endpoints*.

## Wrap-up and Next Steps

HTTP is *a contract made of plain text*. Next, we look at the two sides of that contract — Frontend and Backend.

## Answering the Opening Questions

- **What do client and server actually exchange?**
  They exchange HTTP request and response messages containing method/URL/headers/body and status-code/headers/body respectively. `https://example.com` returns HTML; `https://api.github.com/repos/python/cpython` returns JSON—the difference is response format and contract.
- **What elements compose an HTTP request and response?**
  A request has a start line like `GET /get HTTP/1.1` plus headers and optional body. A response has a status line like `HTTP/1.1 200 OK` plus headers and body. The `curl -v` and `X-Custom` header examples show metadata exchanged in plain text.
- **What does each of GET, POST, PUT, DELETE mean?**
  GET expresses retrieval intent (`httpbin.org/get?lang=en`). POST sends a body to create or process, potentially changing server state. PUT and DELETE express update and deletion contracts on the same URL—distinguishing methods lets client and server communicate with shared semantics.

<!-- toc:begin -->
## In this series

- [Web Development 101 (1/10): How the Web Works](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, and JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): The Browser and the DOM](./03-browser-and-dom.md)
- **HTTP and APIs (current)**
- Frontend and Backend (upcoming)
- Authentication and Sessions (upcoming)
- Connecting to a Database (upcoming)
- Deployment (upcoming)
- Performance and Caching (upcoming)
- Building a Small Web App (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [HTTP request methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [HTTP response status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

### Verification Resources
- [httpbin](https://httpbin.org/)
- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)

Tags: Computer Science, WebDevelopment, HTTP, API, REST, Networking
