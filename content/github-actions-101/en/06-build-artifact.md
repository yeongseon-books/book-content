---
series: github-actions-101
episode: 6
title: "GitHub Actions 101 (6/10): Build Artifacts"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - GitHubActions
  - Artifact
  - Build
  - Release
  - CICD
seo_description: From upload-artifact and download-artifact to Releases. Safely store and pass build outputs across jobs and to users.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (6/10): Build Artifacts

If a CI run finishes the build and then throws the output away, the pipeline is only half done. The logs say “success,” but no one can later confirm which wheel, archive, or report actually passed validation, and deploy often ends up rebuilding work it should have reused.

That is why artifacts matter more than they first appear to. They preserve the exact output a workflow produced and give later jobs, release tooling, and humans a traceable handoff point.

This is post 6 in the GitHub Actions 101 series. In this post, we will use artifacts to keep build outputs, move them across jobs, and carry them into GitHub Releases when the workflow becomes an external delivery channel.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Build Artifacts?
- Which signal should the example or diagram make visible for Build Artifacts?
- What failure should be prevented first when Build Artifacts reaches a real system?

## Big Picture

![github actions 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/06/06-01-concept-at-a-glance.en.png)

*github actions 101 chapter 6 flow overview*

This picture places Build Artifacts inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- Using *upload-artifact / download-artifact*
- Patterns for *cross-job* output passing
- Cost control with *retention-days*
- Cutting *Releases* via *softprops/action-gh-release*
- Five common pitfalls

## Why It Matters

A workflow that *throws build outputs away* offers *no reuse, no trace*. Artifacts are *evidence and assets*.

> *Every merge* should leave a *traceable build*.

## Key Terms

- **Artifact**: a *file bundle produced* by a workflow.
- **upload-artifact**: the *upload* action.
- **download-artifact**: downloads from *another job*.
- **retention-days**: *how long* it's kept.
- **Release**: GitHub's *official artifact page*.

## Before/After

**Before**: when the build job's runner *vanishes*, `dist/*.whl` *vanishes with it*.

**After**: `dist/*.whl` is *stored as an artifact* and the *deploy job* downloads and uses it.

## Hands-on: Artifacts in 5 Steps

### Step 1 — Upload

```yaml
- run: python -m build
- uses: actions/upload-artifact@v7
  with:
    name: dist
    path: dist/*
    retention-days: 14
```

### Step 2 — Download

```yaml
deploy:
  needs: build
  runs-on: ubuntu-latest
  steps:
    - uses: actions/download-artifact@v8
      with:
        name: dist
        path: dist/
    - run: ls dist/
```

### Step 3 — Bundle by patterns

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: reports
    path: |
      coverage.xml
      report.xml
      logs/*.log
```

### Step 4 — Auto-publish a Release

```yaml
- uses: softprops/action-gh-release@v2
  if: startsWith(github.ref, 'refs/tags/')
  with:
    files: dist/*
    generate_release_notes: true
```

### Step 5 — Retention policy

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: nightly-build
    path: dist/
    retention-days: 7
```

## What to Notice in This Code

- *retention-days* controls *storage cost*.
- *generate_release_notes* writes the *changelog*.
- *download-artifact* works only *within the same workflow* (use the API otherwise).

## Five Common Mistakes

1. **`upload-artifact@v3` is *deprecated*.** Upgrade to v4.
2. **Uploading *everything*.** Cost explodes.
3. **No `retention-days`.** Defaults to *90 days* and accumulates.
4. **Reusing *artifact names*.** A second upload with the same name *errors*.
5. **No checksum on *Releases*.** No tamper detection.

## How This Shows Up in Production

Mature teams emit *checksum + SBOM* with every build and *sign* releases (e.g., sigstore).

## How a Senior Engineer Thinks

- *Traceable builds* are the start of *supply-chain security*.
- *Retention* is *cost plus compliance*.
- *Releases* are an *external interface*.
- *Artifact names* must be *unique*.
- *Checksums and signatures* are *culture*.

## Checklist

- [ ] Use *upload-artifact@v7*.
- [ ] *retention-days* is set.
- [ ] *Releases* are auto-published on *tag push*.
- [ ] *Checksums* or *signatures* are attached.

## Practice Problems

1. Upload *pytest report + coverage* as a *single artifact*.
2. Have the *deploy job* download *build job* output.
3. Auto-publish a *Release* on *tag push*.

## Wrap-up and Next Steps

Artifacts are the *receipts of your build*. Next: *Docker build*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Build Artifacts?**
  - The article treats Build Artifacts as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Build Artifacts?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Build Artifacts reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- **Build Artifacts (current)**
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [actions/upload-artifact](https://github.com/actions/upload-artifact)
- [actions/download-artifact](https://github.com/actions/download-artifact)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [About artifacts](https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts)

Tags: GitHubActions, Artifact, Build, Release, CICD
