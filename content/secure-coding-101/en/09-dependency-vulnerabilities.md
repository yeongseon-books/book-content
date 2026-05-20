---
series: secure-coding-101
episode: 9
title: "Secure Coding 101 (9/10): Managing Dependency Vulnerabilities"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Dependencies
  - SCA
  - SBOM
  - SupplyChain
  - SecureCoding
seo_description: SCA, SBOM, lockfiles, Dependabot, and a five-step playbook for safe dependency management against supply-chain risk.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (9/10): Managing Dependency Vulnerabilities

Modern services depend more on external code than on code written directly by the team shipping the feature. HTTP clients, template engines, ORM layers, CLI tooling, and build dependencies all become part of the runtime we are responsible for. When one of them fails, the incident does not belong to a vendor anymore. It belongs to the service that deployed it.

This is post 9 in the Secure Coding 101 series.

Here, we will frame dependency management as supply-chain control rather than occasional version cleanup. Lockfiles, SBOMs, SCA gates, and small automated updates all serve one goal: keeping the build reproducible and the incident blast radius knowable.

> Dependencies are not attachments around our code. Once deployed, they are part of our codebase and part of our responsibility.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Managing Dependency Vulnerabilities?
- Which signal should the example or diagram make visible for Managing Dependency Vulnerabilities?
- What failure should be prevented first when Managing Dependency Vulnerabilities reaches a real system?

## Big Picture

![secure coding 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/09/09-01-concept-at-a-glance.en.png)

*secure coding 101 chapter 9 flow overview*

This picture places Managing Dependency Vulnerabilities inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Managing Dependency Vulnerabilities is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Chapter Answers

- What *SCA* (Software Composition Analysis) means
- The role of an *SBOM*
- Why a *lockfile* is non-negotiable
- *Dependabot / Renovate* automation
- A five-step routine and five common mistakes

## Why It Matters

Log4j, event-stream, ua-parser-js — *supply-chain attacks* succeed with *zero lines* of our code. A library you *don't know you depend on* becomes the *door*.

> *Dependencies are *assets that will leak someday*. Tracking them is the start of defense.*

## Concept at a Glance

## Key Terms

- **SCA**: scanning dependencies for *known vulnerabilities*.
- **SBOM**: a list of *every component* you ship.
- **Lockfile**: pins *exact versions and hashes*.
- **Pinning**: explicitly *fixing direct dependency* versions.
- **Transitive dependency**: a dependency *of a dependency*.

## Before/After

**Before**: `requirements.txt` lists only `requests`. Each build picks a *different version*. You don't know *what came in*.

**After**: `uv.lock` / `poetry.lock` *pin hashes*. *Weekly dependency PRs* arrive automatically; CI gates with *SCA*.

## Hands-on: Safer Dependencies in Five Steps

### Step 1 — Generate a lockfile

```bash
uv lock          # or poetry lock, pip-compile
```

### Step 2 — Generate an SBOM

```bash
syft packages dir:. -o cyclonedx-json > sbom.json
```

### Step 3 — Run SCA

```bash
pip-audit                # Python
osv-scanner --lockfile=uv.lock   # generic
```

### Step 4 — Automate updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
```

### Step 5 — Pin and verify

```bash
pip install --require-hashes -r requirements.txt
```

## What to Notice in This Code

- *Lockfile + hashes* is the heart of *reproducible* builds.
- An SBOM lets you check *blast radius in seconds* during an incident.
- *Regular* updates beat *occasional* heroic ones.

## Five Common Mistakes

1. **Using *latest* with no lockfile.** A target for *supply-chain attacks*.
2. **Ignoring *SCA results*.** Real findings get buried in noise.
3. **Ignoring *transitive dependencies*.** Most CVEs are *transitive*.
4. **Sticking with abandoned libraries.** Patches *never come*.
5. **Letting auto-update PRs *pile up*.** Hundreds in a month.

## How This Shows Up in Production

Most teams use *Renovate* or *Dependabot* for *weekly* PRs and put an *SCA gate* in CI. Larger orgs publish *SBOMs* alongside their builds.

## How a Senior Engineer Thinks

- *Dependencies are *our code* — and our responsibility.*
- *No lockfile means no reproducibility.*
- *Small updates prevent *big incidents*.*
- *An SBOM is an *incident-response tool*.*
- *Depending less is itself security.*

## Checklist

- [ ] *Lockfile* committed.
- [ ] *SCA* running in CI.
- [ ] *Auto-update PRs* arriving weekly.
- [ ] *SBOM* published.

## Practice Problems

1. Read one line of *pip-audit* output and explain it.
2. Name a real CVE that came through a *transitive dependency*.
3. List three risks of building *without a lockfile*.

## Wrap-up and Next Steps

Other people's code is *our code*. The last post covers *safe logging and audit*, the evidence that survives an incident.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Managing Dependency Vulnerabilities?**
  - The article treats Managing Dependency Vulnerabilities as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Managing Dependency Vulnerabilities?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Managing Dependency Vulnerabilities reaches a real system?**
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
- [Secure Coding 101 (8/10): XSS and CSRF Defense](./08-xss-and-csrf.md)
- **Managing Dependency Vulnerabilities (current)**
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP — Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [OSV.dev](https://osv.dev/)
- [CycloneDX SBOM](https://cyclonedx.org/)
- [PyPA — Repeatable Installs](https://pip.pypa.io/en/stable/topics/repeatable-installs/)

Tags: Dependencies, SCA, SBOM, SupplyChain, SecureCoding
