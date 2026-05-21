---
series: computer-networks-101
episode: 6
title: "Computer Networks 101 (6/10): TLS Basics"
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
  - TLS
  - Certificates
  - Encryption
  - PKI
seo_description: How the TLS handshake delivers confidentiality, integrity, and identity at the same time, and what role certificates and PKI play in production.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (6/10): TLS Basics

> Computer Networks 101 series (6/10)

**Core question**: How does the "S" in HTTPS stop eavesdropping, tampering, and impersonation all at once?

> TLS combines three techniques in one beat. Asymmetric crypto handles identity and key agreement, symmetric crypto handles fast bulk encryption, and AEAD handles integrity. Certificates and PKI prove "this key really belongs to this domain". With that picture in your head, expired certificates, self-signed servers, and MITM all fit on the same diagram.

This is post 6 in the Computer Networks 101 series.


![computer networks 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/06/06-01-concept-at-a-glance.en.png)
*computer networks 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying TLS Basics?
- Which signal should the example or diagram make visible for TLS Basics?
- What failure should be prevented first when TLS Basics reaches a real system?

## What You Will Learn

- The three TLS guarantees (confidentiality, integrity, identity)
- The handshake flow (client hello → server hello → key exchange → finished)
- Certificates, CAs, chains, and trust stores
- Differences between TLS 1.2 and TLS 1.3

## Why It Matters

Without TLS in your head, certificate-expiry incidents are paralyzing and dangerous code that "ignores self-signed" sneaks in. Modern infrastructure — mTLS, service mesh, zero-trust — all assumes TLS by default. If you cannot explain "why is it safe?" in your own words, security design drifts unconsciously.

> TLS is not "this channel is safe". It is the combination "this key really belongs to this domain, and only that key can decrypt".

A symmetric session key is derived from the asymmetric agreement, and from that point all data is encrypted fast with that key.

## Key Terms

| Term | Meaning |
| --- | --- |
| Symmetric crypto | Same key for encrypt and decrypt (e.g. AES) |
| Asymmetric crypto | Public/private key pair (e.g. RSA, ECDSA) |
| AEAD | Encryption + integrity together (e.g. AES-GCM, ChaCha20-Poly1305) |
| Certificate | A document binding a public key to a domain plus a signature |
| CA | A trusted authority that signs certificates |
| Chain | Verification path from server cert → intermediate CA → root CA |

## Before / After

**Before — "https just means safe":**

```text
A padlock icon means safe — done.
```

**After — "TLS = key + identity + integrity":**

```text
- Whose key is it?            → certificate signed by a CA
- Who can decrypt?            → symmetric session key
- Was it tampered with?       → AEAD / MAC
Safe as long as none of these break at the same time
```

## Hands-on: Step by Step

### Step 1: look at a certificate

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
# subject= /CN=*.example.com
# issuer = /CN=DigiCert Global G2
# notBefore=...  notAfter=...
```

### Step 2: verify the chain

```bash
openssl s_client -showcerts -connect example.com:443 -servername example.com </dev/null
# every certificate in the chain is printed
```

The browser walks this chain up to a root CA, verifying signatures along the way.

### Step 3: a safe call from Python

```python
import ssl, socket

ctx = ssl.create_default_context()   # uses the OS trust store
with socket.create_connection(('example.com', 443)) as s:
    with ctx.wrap_socket(s, server_hostname='example.com') as ts:
        print(ts.version())          # TLSv1.3
        print(ts.getpeercert()['subject'])
```

### Step 4: create a self-signed certificate

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -subj "/CN=localhost" -keyout key.pem -out cert.pem
```

```python
# Flask + TLS
from flask import Flask
app = Flask(__name__)

@app.get('/')
def home(): return 'hello'

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), port=8443)
```

```bash
curl -k https://localhost:8443/    # -k allows self-signed (learning only)
```

### Step 5: see expiry and impersonation cases

```bash
curl -v https://expired.badssl.com/        # expired
curl -v https://wrong.host.badssl.com/     # name mismatch
curl -v https://untrusted-root.badssl.com/ # untrusted root
```

Each case prints exactly which validation step failed.

## What to Notice in This Code

- The trust store is the list of root CAs the OS or browser ships with
- A certificate bundles "key + domain + expiry + signature"
- Self-signed is for learning only — production uses Let's Encrypt and friends
- TLS version and cipher choice are a large part of security

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using `verify=False` or `-k` in production | MITM exposure | Use trusted CA certificates |
| No certificate-expiry monitoring | Sudden outage | Automate alerts 30 days before expiry |
| Missing intermediate certificate | Some clients fail to validate | Deploy the full chain |
| Allowing weak ciphers or old TLS versions | Exposed to known attacks | TLS 1.2+ with safe ciphers only |
| Domain not in SAN | Some browsers block | Include all domains in SAN |

## How This Shows Up in Production

- Web and mobile: Let's Encrypt with automated renewal
- Microservices: mTLS for service-to-service identity
- Message queues and DB clients: enable TLS options
- VPN and QUIC: TLS is a core component
- IoT: client certificates issued at factory provisioning

## How a Senior Engineer Thinks

A senior engineer sees TLS as a key-management system, not a "safe = ON" switch. Renewal cadence, private-key protection, root-CA trust policy, mTLS policy — these operational pieces matter more than the algorithms themselves. The hour during which a certificate expires can decide a quarter's revenue.

A senior is also wary of the simple conclusion "we encrypted it, so we are safe". They draw out which key exposes which metadata to whom, and what breaks if a key is leaked.

## Checklist

- [ ] I know the three TLS guarantees
- [ ] I know certificates, CAs, chains, and trust stores
- [ ] I can sketch the major handshake steps
- [ ] I never use `verify=False` in production
- [ ] I monitor certificate expiry automatically

## Practice Problems

1. Pull a favorite site's certificate with openssl and write down its issuer, expiry, and SAN list.

2. Bring up a local HTTPS server with a self-signed cert and demonstrate both a passing and a failing call from Python's `ssl` module.

3. Explain in one paragraph: "Why is mTLS important in zero-trust infrastructure?"

## Wrap-up and Next Steps

TLS combines asymmetric crypto for identity and key agreement, symmetric crypto for fast bulk encryption, and AEAD for integrity. Certificates and PKI prove "this key really belongs to this domain". With that picture, every HTTPS incident sits on the same shelf.

Next we follow how the TLS-protected packet actually moves across the Internet — routing and NAT.

## Answering the Opening Questions

- **What boundary should you inspect first when applying TLS Basics?**
  - The article treats TLS Basics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for TLS Basics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when TLS Basics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Networks 101 (1/10): What Is a Network?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP and Subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP and UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP and HTTPS](./05-http-and-https.md)
- **TLS Basics (current)**
- Routing and NAT (upcoming)
- Load Balancer (upcoming)
- WebSocket and Real-Time Communication (upcoming)
- Debugging Network Problems (upcoming)

<!-- toc:end -->

## References

- [RFC 8446 — TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Bulletproof TLS — Ivan Ristic](https://www.feistyduck.com/books/bulletproof-tls-and-pki/)
- [RFC 5280 — PKIX Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280)

Tags: Computer Science, Networking, TLS, Certificates, Encryption, PKI
