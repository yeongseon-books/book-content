---
series: web-development-101
episode: 1
title: How the Web Works
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
  - WebDevelopment
  - HTTP
  - DNS
  - Browser
  - Frontend
seo_description: What really happens when you type a URL and hit Enter — DNS, HTTP, server, and browser rendering explained as five steps for new web developers.
last_reviewed: '2026-05-04'
---

# How the Web Works

> Web Development 101 series (1/10)

<!-- a-grade-intro:begin -->

**Core question**: When you type `https://example.com` and hit Enter, what *exactly* happens?

> DNS lookup, then TCP/TLS connect, then HTTP request, then server response, then browser rendering. Five steps in concert.

<!-- a-grade-intro:end -->

## What You Will Learn

- The full path from URL to pixels on the screen
- The role of DNS, HTTP, and the browser renderer
- Where the client ends and the server begins
- How to observe a real network request
- A map of this whole series

## Why It Matters

Web developers must see the *whole picture*. Knowing one layer well lets you build, but it does not let you debug. Once the five-step flow is in your head, every tool finds its place.

> The web runs on *agreed protocols*, not magic.

## Concept at a Glance

```mermaid
flowchart LR
    User["User"] --> Browser["Browser"]
    Browser --> DNS["DNS"]
    DNS --> Browser
    Browser -->|"HTTP request"| Server["Web server"]
    Server -->|"HTML/CSS/JS"| Browser
    Browser --> Render["Render to screen"]
```

Five beats: DNS, connect, request, response, render.

## Key Terms

- **URL**: address of a resource (scheme + host + path).
- **DNS**: phone book that maps a domain to an IP.
- **HTTP**: protocol for requests and responses.
- **Server**: program that turns requests into responses.
- **Browser**: program that turns responses into pixels.

## Before/After

**Before (raw IP)**

```python
# Hard to remember
import socket
ip = "93.184.216.34"
```

**After (use a domain)**

```python
import socket
ip = socket.gethostbyname("example.com")
print(ip)
```

DNS is the bridge between *human language* and *machine language*.

## Hands-on: Trace One Request in Five Steps

### Step 1 — DNS lookup

```python
# 1_dns.py
import socket
print(socket.gethostbyname("example.com"))
```

A domain becomes an IP.

### Step 2 — HTTP request

```python
# 2_http.py
import requests
r = requests.get("https://example.com")
print(r.status_code, len(r.text))
```

You should see `200` and a body length.

### Step 3 — Read response headers

```python
# 3_headers.py
import requests
r = requests.get("https://example.com")
for k, v in r.headers.items():
    print(k, ":", v)
```

`Content-Type`, `Server`, `Cache-Control` — the *metadata* of the response.

### Step 4 — Parse HTML

```python
# 4_parse.py
import re, requests
html = requests.get("https://example.com").text
title = re.search(r"<title>(.*?)</title>", html).group(1)
print(title)
```

The browser turns HTML into a tree, then paints pixels.

### Step 5 — Watch in DevTools

```text
Open browser, press F12, Network tab, reload example.com
```

Every request, timing, and transfer size is right there.

## What to Notice in This Code

- DNS happens *once*, then is cached.
- HTTPS is HTTP on top of TCP and TLS.
- HTML, CSS, and JS start arriving in *parallel*.

## Five Common Mistakes

1. **Mixing DNS and HTTP.** They are different stages.
2. **Thinking HTTPS is a different protocol from HTTP.** It is HTTP plus a TLS layer.
3. **Believing the *server* renders the page.** The browser does, by default.
4. **Blurring the client/server boundary.** No one knows who owns what.
5. **Debugging without DevTools.** The Network tab is the fastest diagnostic tool.

## How This Shows Up in Production

When something breaks, the first question is *which step*: DNS, TLS, server, or render? Knowing the names of the stages turns a 30-minute debug into 3 minutes. Every monitoring tool — New Relic, Datadog, Sentry — measures these same five steps.

## How a Senior Engineer Thinks

- Set a *time budget* per stage (DNS 50ms, TLS 100ms, etc.).
- Cache anything that *can* be cached.
- Always ask: should this run on the *browser* or the *server*?
- Use DevTools Network as a debugger, not a viewer.
- Measure, do not guess.

## Checklist

- [ ] You can describe URL-to-pixels in five steps.
- [ ] You can explain the difference between DNS and HTTP.
- [ ] You can open DevTools Network and analyze a single request.
- [ ] You can read a status code from a response.
- [ ] You know where caching happens.

## Practice Problems

1. Open a favorite site and find the *largest* request in the Network tab.
2. Use `dig` or `nslookup` to look up three domains.
3. Use `requests` to call the same URL 100 times and print the average time.

## Wrap-up and Next Steps

The web is a *concert of protocols*. Next, we look at the three things the browser actually downloads — HTML, CSS, and JavaScript.

<!-- toc:begin -->
- **How the Web Works (current)**
- HTML, CSS, and JavaScript (upcoming)
- The Browser and the DOM (upcoming)
- HTTP and APIs (upcoming)
- Frontend and Backend (upcoming)
- Authentication and Sessions (upcoming)
- Connecting to a Database (upcoming)
- Deployment (upcoming)
- Performance and Caching (upcoming)
- Building a Small Web App (upcoming)
<!-- toc:end -->

## References

- [How the Web works (MDN)](https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works)
- [What is DNS? (Cloudflare Learning)](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Chrome DevTools Network](https://developer.chrome.com/docs/devtools/network/)

Tags: Computer Science, WebDevelopment, HTTP, DNS, Browser, Frontend
