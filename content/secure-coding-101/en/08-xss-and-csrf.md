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

This is post 8 in the Secure Coding 101 series.

In this chapter, we will treat browser security as a system of output escaping, CSP, cookie policy, and request verification rather than as a single sanitization trick. That framing makes it easier to see when the browser is acting on the application's behalf and when it has effectively become the attacker's tool.

> XSS runs attacker-controlled code in our page. CSRF abuses the user's existing authority to send a request they did not mean to send.

## Questions to Keep in Mind

- What boundary should you inspect first when applying XSS and CSRF Defense?
- Which signal should the example or diagram make visible for XSS and CSRF Defense?
- What failure should be prevented first when XSS and CSRF Defense reaches a real system?

## Big Picture

![secure coding 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/08/08-01-concept-at-a-glance.en.png)

*secure coding 101 chapter 8 flow overview*

This picture places XSS and CSRF Defense inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

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

- **What boundary should you inspect first when applying XSS and CSRF Defense?**
  - The article treats XSS and CSRF Defense as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for XSS and CSRF Defense?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when XSS and CSRF Defense reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
