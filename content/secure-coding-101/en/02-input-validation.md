---
series: secure-coding-101
episode: 2
title: "Secure Coding 101 (2/10): Input Validation"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - InputValidation
  - SecureCoding
  - Pydantic
  - OWASP
  - AppSec
seo_description: Allowlists, schema-based validation, and a five-step playbook for safe, predictable input handling at every trust boundary.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (2/10): Input Validation

Most applications first become unstable at the input boundary. A login form, search box, JSON body, file name, or query string may look harmless, but the moment the server trusts it too early, ordinary bugs and attack paths start to overlap. SQL injection, XSS, path traversal, and unsafe deserialization all begin with the same mistake: giving external input more trust than it deserves.

This is the 2nd post in the Secure Coding 101 series.

In this chapter, we will frame validation as a contract that makes the system predictable at every trust boundary, not as a scattered pile of `if` statements. Once that idea is clear, schema validation, allowlists, normalization, and safe error handling stop feeling like separate tricks and start looking like one coherent design choice.

> Input validation is the first security control most systems execute, and the first reliability control they cannot afford to skip.


![secure coding 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/02/02-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Input Validation?
- Which signal should the example or diagram make visible for Input Validation?
- What failure should be prevented first when Input Validation reaches a real system?

## Questions This Chapter Answers

- The difference between *allowlists* and *denylists*
- The power of *schema-based* validation
- What an *input boundary* really is
- A five-step routine for *type, range, format* checks
- Five common mistakes

## Why It Matters

Half of the OWASP Top 10 comes from *trusting input*. SQL injection, XSS, path traversal, unsafe deserialization — all are the result of a server *trusting the client too much*.

> *The client is *hostile*. Validate again on the *server*.*

## Key Terms

- **Allowlist**: only *what is allowed* gets through.
- **Denylist**: blocks *what is forbidden* (always incomplete).
- **Schema**: a *contract for shape*.
- **Sanitization**: strip or escape *dangerous parts*.
- **Canonicalization**: normalize input to a *single canonical form*.

## Before/After

**Before**: every route validates with ad-hoc *if statements*. The one you forget becomes a *bug*.

**After**: a *schema* validates once; the route reads *business rules* only.

## Hands-on: Validate in Five Steps

### Step 1 — Start with type

```python
def to_int(raw: str) -> int:
    if not raw.lstrip("-").isdigit():
        raise ValueError("not an integer")
    return int(raw)
```

### Step 2 — Check range and length

```python
def parse_quantity(n: int) -> int:
    if not (1 <= n <= 1000):
        raise ValueError("quantity out of range")
    return n
```

### Step 3 — Format with an allowlist regex

```python
import re
USERNAME = re.compile(r"^[a-z0-9_]{3,20}$")

def parse_username(raw: str) -> str:
    if not USERNAME.match(raw):
        raise ValueError("invalid username")
    return raw
```

### Step 4 — One schema for the whole payload

```python
from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    username: str = Field(pattern=r"^[a-z0-9_]{3,20}$")
    age: int = Field(ge=0, le=150)
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
```

### Step 5 — Make the boundary explicit

```python
def handle_signup(payload: dict):
    user = CreateUser(**payload)  # boundary
    save_user(user)               # downstream code is now trusted
```

## What to Notice in This Code

- *Allowlists* leak less than *denylists*.
- Schema validation is *documentation and code at once*.
- A clear *boundary* removes defensive code from inner functions.

## Five Common Mistakes

1. **Using *denylists only*.** Bypasses keep getting invented.
2. **Trusting *client-side checks* on the server.** Clients *change*.
3. **Passing *raw dicts* through the system.** You never know what keys arrive.
4. **Echoing the *raw input* in error messages.** That becomes an XSS path.
5. **Truncating internationalized input by *bytes*.** Non-ASCII text *breaks*.

## How This Shows Up in Production

Most FastAPI / Flask teams use *Pydantic* or *marshmallow* to validate at the *route entry point*. Valid payloads flow on as *typed objects*; invalid ones return *422*.

## How a Senior Engineer Thinks

- *Schemas are *contracts*.*
- *Validate at *every boundary explicitly*.*
- *Attackers also read your *error messages*.*
- *The default is *deny*; allow is the *exception*.*
- *Normalize *before* validation.*

## Checklist

- [ ] Every route runs through a *schema*.
- [ ] *Allowlist* is the default.
- [ ] *Error messages* are safe to display.
- [ ] Lengths, ranges, formats are *explicit*.

## Practice Problems

1. Build a *Pydantic schema* for a postal address.
2. Write a regex that prevents *path traversal* in a filename.
3. Run the same input through *two normalization rules* — how do the results differ?

## Wrap-up and Next Steps

With validation, behavior becomes *predictable*. Next we look at *who is who* — *authentication and session*.

## Answering the Opening Questions

- **What distinguishes allowlist from denylist?**
  - As the USERNAME regex example showed, an allowlist declares "only this is permitted," keeping the attack surface small. A denylist requires continuously adding forbidden patterns, and as the encoding normalization attack demonstrated, the same character in a different representation bypasses it.
- **What improves when using an input schema over ad-hoc validation?**
  - As the Pydantic `CreateUser` example showed, a schema consolidates validation rules, API documentation, and error message formatting in one place. Scattering `if` statements across routes makes finding omissions difficult, but a single schema reveals the entire contract.
- **Where exactly is the input boundary?**
  - The single line `CreateUser(**payload)` in `handle_signup` is the boundary. Before it is adversarial external data; after it is a validated internal object. As the layer breakdown table showed, boundaries exist at multiple levels: network, framework, schema, domain, and storage.

## Deep Dive: Path Traversal, ReDoS, File Upload, and Encoding Attacks

Knowing the principles is one thing; real attacks arrive through paths you did not anticipate. This section reproduces the four most commonly exploited input-validation gaps and shows defense code for each.

### Path Traversal — Reproduction and Defense

An attacker submits `../../etc/passwd` in a file-download parameter. If the server concatenates that value directly into a filesystem path, files outside the intended directory become accessible.

```python
# Vulnerable — user input joined directly to path
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/download")
def download(filename: str):
    # DANGER: ../ reaches parent directories
    path = f"/var/uploads/{filename}"
    return FileResponse(path)
```

```python
# Defended — canonicalize, then verify containment
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()
UPLOAD_DIR = Path("/var/uploads").resolve()

@app.get("/download")
def download(filename: str):
    # 1) Block path separators and null bytes
    if "\x00" in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="invalid filename")

    # 2) resolve() expands symlinks and ..
    target = (UPLOAD_DIR / filename).resolve()

    # 3) Confirm target stays inside the upload directory
    if not str(target).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="path traversal blocked")

    if not target.is_file():
        raise HTTPException(status_code=404, detail="not found")

    return FileResponse(target)
```

The key is calling `resolve()` to canonicalize the path, then comparing with a known-safe prefix. Stripping `..` from the string alone fails against double-encoding (`%2e%2e%2f`) and OS-specific quirks.

### ReDoS (Regular Expression Denial of Service)

A regex with nested quantifiers can trigger exponential backtracking, letting a single request monopolize server CPU.

```python
import re
import time

# Dangerous — nested repetition causes exponential backtracking
DANGEROUS = re.compile(r"^(a+)+$")

# 'a' * 25 + 'b' fails to match, backtracking explodes
start = time.time()
DANGEROUS.match("a" * 25 + "b")
elapsed = time.time() - start
print(f"elapsed: {elapsed:.2f}s")  # seconds to tens of seconds
```

```python
# Safe alternative — remove nested quantifier, or enforce a timeout
import re
import signal

SAFE = re.compile(r"^a+$")  # no nesting

class RegexTimeout(Exception):
    pass

def handler(signum, frame):
    raise RegexTimeout("regex timed out")

def safe_match(pattern: re.Pattern, text: str, timeout_sec: float = 1.0):
    """Wrapper that kills regex matching after a deadline."""
    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, timeout_sec)
    try:
        return pattern.match(text)
    except RegexTimeout:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
```

In production, run a ReDoS detection tool (e.g., `rxxr2`, `safe-regex`) in CI every time a regex is added. Capping input length also prevents backtracking from reaching dangerous depths.

### File Upload Validation

Checking only the extension is insufficient — attackers embed PHP or shell code inside valid-looking JPEG headers. A robust upload handler verifies extension, size, magic bytes, and generates a safe filename.

```python
import magic
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
ALLOWED_MIMES = {"image/png", "image/jpeg", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload")
async def upload_image(file: UploadFile):
    # 1) Extension check
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="disallowed extension")

    # 2) Size check (streaming)
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="file too large")

    # 3) Magic-byte content-type verification
    detected_mime = magic.from_buffer(content[:2048], mime=True)
    if detected_mime not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=400,
            detail=f"content type mismatch: {detected_mime}",
        )

    # 4) Generate a safe filename (never use the original)
    import uuid
    safe_name = f"{uuid.uuid4().hex}{ext}"
    save_path = Path("/var/uploads") / safe_name
    save_path.write_bytes(content)

    return {"filename": safe_name}
```

Attackers rename `.php` files to `.jpg`, forge MIME headers, or embed scripts after valid image headers. Combining magic-byte inspection with a fresh UUID filename blocks web-shell uploads.

### Encoding Normalization Attacks

Unicode allows the same visual glyph to exist under multiple code points. Without normalization, an attacker can bypass allowlists using look-alike characters (homoglyphs).

```python
import unicodedata

def normalize_and_validate(raw: str) -> str:
    """NFC-normalize then reject mixed-script homoglyph attempts."""
    # 1) NFC normalization: combine decomposed forms
    normalized = unicodedata.normalize("NFC", raw)

    # 2) Strip control characters
    cleaned = "".join(
        ch for ch in normalized
        if unicodedata.category(ch) not in ("Cc", "Cf")
    )

    # 3) Detect mixed scripts (homoglyph defense)
    scripts = set()
    for ch in cleaned:
        try:
            script = unicodedata.name(ch).split()[0]
            scripts.add(script)
        except ValueError:
            pass

    # Latin + Cyrillic mix is suspicious
    if "CYRILLIC" in scripts and "LATIN" in scripts:
        raise ValueError("mixed script detected — possible homoglyph attack")

    return cleaned

# Example: Cyrillic 'а' vs Latin 'a' — visually indistinguishable
try:
    normalize_and_validate("pаypal")  # contains Cyrillic а
except ValueError as e:
    print(f"Blocked: {e}")
```

The same problem affects URLs and email addresses. Punycode domains like `xn--pypal-4ve.com` render as `paypal.com` in phishing attacks. Normalizing input and detecting mixed scripts is the baseline defense.

### SSRF Prevention via URL Validation

When a server fetches a user-supplied URL without inspection, internal networks become exposed.

```python
import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]

ALLOWED_SCHEMES = {"http", "https"}

def validate_url(url: str) -> str:
    """Allow only external URLs — blocks SSRF."""
    parsed = urlparse(url)

    # 1) Restrict scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise HTTPException(status_code=400, detail="scheme not allowed")

    # 2) Resolve hostname
    import socket
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="no hostname")

    try:
        resolved = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="DNS resolution failed")

    # 3) Reject internal IPs
    for family, _, _, _, sockaddr in resolved:
        ip = ipaddress.ip_address(sockaddr[0])
        for net in BLOCKED_NETWORKS:
            if ip in net:
                raise HTTPException(
                    status_code=400,
                    detail="internal network access blocked",
                )

    return url
```

To defend against DNS rebinding, connect using the resolved IP directly or re-validate at request time. When following redirects, repeat the same check at every hop.

### Input Validation Layer Summary

| Layer | Validates | Tool / Pattern | Failure Response |
| --- | --- | --- | --- |
| Network | Request size, rate | nginx / WAF config | 413, 429 |
| Framework | Content-Type, encoding | FastAPI auto-parsing | 422 |
| Schema | Type, range, format | Pydantic, marshmallow | 400 + per-field errors |
| Domain | Business constraints | Service-layer checks | 409, 422 |
| Storage | FK existence, uniqueness | DB constraints | 409 |

Each layer catches failures independently. If an upper layer is breached, the next layer acts as the last line of defense. This structure is defense-in-depth applied to input validation.

### Mass Assignment Defense

When an API maps a JSON payload directly to an ORM model, clients can inject fields the API never intended to expose. For example, a user-registration endpoint receiving `{"username": "alice", "role": "admin"}` might persist the `role` field unchanged.

```python
from pydantic import BaseModel, Field
from fastapi import FastAPI

# Safe pattern: separate input schema from internal model
class UserCreateRequest(BaseModel):
    """Only the fields a client is allowed to send."""
    username: str = Field(min_length=3, max_length=20)
    email: str
    password: str = Field(min_length=8)

class UserInternal(BaseModel):
    """Full internal representation — includes server-controlled fields."""
    username: str
    email: str
    password_hash: str
    role: str = "user"        # default locked, not settable externally
    is_active: bool = True

app = FastAPI()

@app.post("/users")
def create_user(req: UserCreateRequest):
    # Only use fields the input schema permits
    internal = UserInternal(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        # role and is_active are server-decided
    )
    return save_user(internal)
```

The key is separating the input schema (`UserCreateRequest`) from the internal model (`UserInternal`). Creating a model with `**payload` lets clients overwrite any field. In Django, the `ModelForm.fields` declaration serves the same purpose; in SQLAlchemy, explicitly listing allowed attributes in `__init__` applies the same principle.

### Multipart Requests and Mixed JSON Attacks

When file uploads and JSON fields arrive together in a multipart request, each part needs independent validation. A common gap: parsing a JSON part inside a `multipart/form-data` request while skipping type validation.

```python
from pydantic import BaseModel, Field
from fastapi import FastAPI, UploadFile, Form, HTTPException
import json

class MetadataSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    tags: list[str] = Field(max_length=10)

app = FastAPI()

@app.post("/documents")
async def upload_document(
    file: UploadFile,
    metadata: str = Form(...),  # arrives as a JSON string
):
    # Parse and schema-validate the JSON metadata
    try:
        meta_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="invalid JSON in metadata")

    meta = MetadataSchema(**meta_dict)  # schema enforcement

    # File validation is separate
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large")

    return {"title": meta.title, "filename": file.filename}
```

Each part of a multipart request requires its own validation rules — file parts need size and type checks, text parts need schema enforcement. One request does not mean one validation pass.

<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- **Input Validation (current)**
- Authentication and Session (upcoming)
- Authorization and Permissions (upcoming)
- Safe Data Storage (upcoming)
- Secret and Key Management (upcoming)
- SQL Injection and Safe ORM Usage (upcoming)
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Pydantic docs](https://docs.pydantic.dev/)
- [OWASP — Mass Assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [PortSwigger — Input validation](https://portswigger.net/web-security)
- [Unicode Technical Standard #39 — Unicode Security Mechanisms](https://unicode.org/reports/tr39/)

Tags: InputValidation, SecureCoding, Pydantic, OWASP, AppSec
