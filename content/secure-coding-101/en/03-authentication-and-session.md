---
series: secure-coding-101
episode: 3
title: "Secure Coding 101 (3/10): Authentication and Session"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Authentication
  - Session
  - Cookie
  - JWT
  - SecureCoding
seo_description: Password hashing, session cookies, JWT trade-offs, MFA, and a five-step playbook for a safe authentication flow.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (3/10): Authentication and Session

When authentication fails, every permission layered on top of it fails with it. Weak password hashing, overly long-lived tokens, missing cookie flags, and login flows that reveal whether an account exists all create quiet failures that often stay invisible until the first takeover or credential-stuffing wave lands.

This is the 3rd post in the Secure Coding 101 series.

Here, we will separate two concerns that are easy to blur together: proving who the user is and remembering that proof safely on later requests. Once you keep those apart, the trade-offs between session cookies and JWTs, logout design, MFA placement, and rate limiting become much easier to reason about.

> Authentication proves identity. Session management preserves that proof across requests. Both need explicit failure handling, not just a happy-path login screen.


![secure coding 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/03/03-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Authentication and Session?
- Which signal should the example or diagram make visible for Authentication and Session?
- What failure should be prevented first when Authentication and Session reaches a real system?

## Questions This Chapter Answers

- The difference between *authentication* and *authorization*
- The principles of *password hashing*
- *Session cookies* vs *JWT* trade-offs
- The role of *MFA*
- A five-step auth flow and five common mistakes

## Why It Matters

When auth leaks, *every permission leaks*. The most common incidents are *weak hashing*, *session fixation*, and *secret leakage*.

> *Auth is the *door*. The session is the *hallway badge*.*

## Key Terms

- **AuthN**: *who are you* (authentication).
- **AuthZ**: *what may you do* (authorization).
- **Hash**: turn the password into something *not reversible*.
- **Salt**: makes the same password produce a *different hash*.
- **MFA**: identity confirmed by *two or more factors*.

## Before/After

**Before**: Passwords stored as *MD5*, session IDs *readable from JS*. One leak exposes *everything*.

**After**: Hashing with *bcrypt or argon2*, cookies marked *HttpOnly + Secure + SameSite*, login behind a *rate limit*.

## Hands-on: A Safe Auth Flow in Five Steps

### Step 1 — Hash the password

```python
from passlib.hash import argon2
hashed = argon2.hash("user-password")
ok = argon2.verify("user-password", hashed)
```

### Step 2 — Handle login

```python
def login(username, password):
    user = users.find(username)
    if not user or not argon2.verify(password, user.hash):
        raise PermissionError("invalid credentials")
    return create_session(user)
```

### Step 3 — Issue a safe cookie

```python
response.set_cookie(
    "session", session_id,
    httponly=True, secure=True, samesite="Lax", max_age=3600,
)
```

### Step 4 — Logout and revoke

```python
def logout(session_id):
    sessions.delete(session_id)  # truly revoked on the server
```

### Step 5 — Rate limit and lockout

```python
def can_attempt(user_id):
    n = redis.incr(f"login:{user_id}")
    redis.expire(f"login:{user_id}", 60)
    return n <= 5
```

## Failure signals and what to verify first

The auth path usually looks healthy until a real incident starts. That is why it helps to define the first checks ahead of time.

```text
Symptom: users say they were logged out unexpectedly
First checks:
1. cookie max_age / expiry changes
2. session-store eviction or Redis restart
3. clock skew across app nodes

Symptom: login errors spike after deployment
First checks:
1. password-hash library version change
2. missing secret used for cookie signing
3. MFA callback or email provider failure
```

This kind of runbook turns "auth is broken" into a bounded investigation. In production, that shortens recovery time more than another generic best-practice bullet ever will.

## What to Notice in This Code

- A safe hash is *intentionally slow*.
- Cookie flags work as a *single set*, not one at a time.
- Sessions must be *server-revocable*.

## Five Common Mistakes

1. **Hashing passwords with *MD5 or SHA1*.** Both are broken.
2. **Hashing without a *salt*.** Rainbow tables apply directly.
3. **Issuing *long-lived JWTs*.** Revocation is *impossible*.
4. **Cookies *without HttpOnly*.** A single XSS steals the session.
5. **Login errors that *reveal account existence*.** Enables *enumeration*.

## How This Shows Up in Production

Most teams hash with *Argon2id* or *bcrypt*, combine *short-lived session cookies* with a *refresh* flow, and require *MFA* for sensitive actions.

## How a Senior Engineer Thinks

- *You should never *need* the password — only the hash.*
- *Sessions should be *short and revocable*.*
- *JWTs are convenient but *hard to revoke* — keep them short.*
- *MFA has the *best ROI* of any control.*
- *Every auth path has a *rate limit*.*

## Checklist

- [ ] *Argon2 or bcrypt* in use.
- [ ] Cookies set *HttpOnly + Secure + SameSite*.
- [ ] *Logout* really invalidates the session.
- [ ] *Rate limiting* is on the login route.

## Practice Problems

1. Measure two different *bcrypt cost* values.
2. Compare JWT vs session cookie in a single *trade-off table*.
3. Write login error messages that prevent *account enumeration*.

## Wrap-up and Next Steps

Auth answers *who*. Next we answer *what may they do* — *authorization and permissions*.

## Answering the Opening Questions

- **What distinguishes authentication from authorization?**
  - Authentication (AuthN) is the procedure confirming "who are you," and authorization (AuthZ) is the procedure deciding "what can you do." In the article, password hashing and sessions belong to authentication, while the policy functions and resource ownership checks covered in chapter 4 belong to authorization.
- **Why must password hashing use intentionally slow algorithms?**
  - As the bcrypt vs Argon2 comparison table showed, fast hashes allow billions of attempts per second on GPU. Intentionally slow hashes (including memory-hard ones) make mass-guessing costs prohibitively high, making recovery difficult even after a breach.
- **What are the tradeoffs between session cookies and JWT?**
  - Session cookies have the server hold state enabling instant revocation but incur storage overhead. JWT is stateless making horizontal scaling easy, but revocation before expiry is difficult after theft. As the token renewal flow showed, the practical standard is combining short-lived tokens with refresh tokens to capture both advantages.
<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- **Authentication and Session (current)**
- Authorization and Permissions (upcoming)
- Safe Data Storage (upcoming)
- Secret and Key Management (upcoming)
- SQL Injection and Safe ORM Usage (upcoming)
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Argon2 — RFC 9106](https://datatracker.ietf.org/doc/rfc9106/)
- [NIST 800-63B — Digital Identity](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [MDN — Secure cookie configuration](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Cookies)

Tags: Authentication, Session, Cookie, JWT, SecureCoding
