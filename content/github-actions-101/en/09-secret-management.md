---
series: github-actions-101
episode: 9
title: "GitHub Actions 101 (9/10): Secret Management"
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
  - Secret
  - Security
  - OIDC
  - CICD
seo_description: Repository, environment, and organization secrets with OIDC, masking, and rotation policy for safe handling of sensitive values in workflows.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (9/10): Secret Management

As automation becomes more capable, more sensitive values start flowing through the pipeline: package tokens, cloud credentials, database passwords, certificates, and service keys. The hard part is that once one of them lands in a log or commit history, the recovery cost is far higher than a normal CI failure.

That makes secret handling a design problem rather than a convenience feature. You need to decide where secrets live, which environments can read them, how much power `GITHUB_TOKEN` gets, and how to avoid turning one careless debug command into a permanent leak.

This is post 9 in the GitHub Actions 101 series. In this post, we will use scope, least privilege, OIDC, and runtime masking to treat secrets as operational resources instead of YAML variables.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Secret Management?
- Which signal should the example or diagram make visible for Secret Management?
- What failure should be prevented first when Secret Management reaches a real system?

## Big Picture

![github actions 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/09/09-01-concept-at-a-glance.en.png)

*github actions 101 chapter 9 flow overview*

This picture places Secret Management inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Secret Management is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- The difference between *repository, environment, and organization* secrets
- The *least-privilege* `permissions:` discipline for `GITHUB_TOKEN`
- *OIDC* as a way to *retire long-lived keys*
- Masking dynamic values with *`::add-mask::`*
- Five common pitfalls

## Why It Matters

*A leaked secret is unrecoverable*. Once it lands in a public log, it is on the internet *forever*.

> *The biggest risk to a secret is not a hacker; it is *us*. One careless echo and it is over.*

## Concept at a Glance

## Key Terms

- **Repository secret**: scoped to *one repo*.
- **Environment secret**: scoped *per environment* (staging, production).
- **Organization secret**: *shared* across many repos.
- **GITHUB_TOKEN**: a short-lived token *issued automatically* per run.
- **OIDC**: *keyless trust* with the cloud.

## Before/After

**Before**: `.env` files are committed, or an `AWS_KEY` gets shared over Slack DM. Rotation is *manual, once a year*.

**After**: secrets live only in the *GitHub UI*. *OIDC* means *zero long-lived keys*. *Quarterly rotation* is on the calendar.

## Hands-on: Secret Management in 5 Steps

### Step 1 — Register a repository secret

```bash
# Use the gh CLI instead of clicking
gh secret set NPM_TOKEN --body "npm_xxx"
gh secret set --env production DB_PASSWORD --body "***"
```

### Step 2 — Use it inside a workflow

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Step 3 — `GITHUB_TOKEN` least privilege

```yaml
permissions:
  contents: read
  pull-requests: write
  # everything else defaults to 'none'
```

### Step 4 — Mask dynamic values

```yaml
- name: Mask runtime token
  run: |
    TOKEN=$(curl -s https://auth.example.com/token | jq -r .token)
    echo "::add-mask::$TOKEN"
    echo "GENERATED_TOKEN=$TOKEN" >> "$GITHUB_ENV"
```

### Step 5 — Dependabot secrets and rotation

```text
Settings > Secrets > Dependabot
- dependency update PRs can also access secrets
- put rotation on the calendar quarterly (gh secret set to refresh)
```

## What to Notice in This Code

- Secrets enter through *environment variables*, never *command-line args*.
- Start `permissions:` at *deny-all* and grant only what you need.
- *`::add-mask::`* protects values *generated at runtime*, too.

## Five Common Mistakes

1. **`echo $SECRET` for debugging.** It is now *permanently in the log*.
2. **Granting secret access to PRs via `pull_request_target`.** *Arbitrary code execution* risk.
3. **`GITHUB_TOKEN` left at *write-all*.** A bad action affects *everything*.
4. **Exposing secrets to *fork PRs*.** External contributors can exfiltrate them.
5. **No rotation schedule.** A former employee's key lives on for *years*.

## How This Shows Up in Production

Mature teams keep a *single source of truth* in *HashiCorp Vault*, *Doppler*, or *1Password Secrets Automation*, and let GitHub Actions *borrow short-lived credentials* via *OIDC*.

## How a Senior Engineer Thinks

- *If a secret is in the code, it has already leaked*.
- *Least privilege* is the default.
- *Long-lived keys are a liability*; *OIDC is an asset*.
- *Rotation is automation, not a calendar reminder*.
- *Never* hand secrets to a *fork PR*.

## Checklist

- [ ] *Repository / environment / organization* scopes are deliberate.
- [ ] `permissions:` is set to *least privilege*.
- [ ] *OIDC* authenticates to the cloud.
- [ ] A *rotation schedule* exists.

## Practice Problems

1. Add a `DB_PASSWORD` secret to the *production* environment and use it safely in a workflow.
2. Change a workflow's `permissions:` from *write-all* to a *deny-all baseline plus what is needed*.
3. Add a step that masks a *runtime-generated token* with `::add-mask::`.

## Wrap-up and Next Steps

Secret management prevents *most* security incidents. Next: a *real-world CI/CD pipeline* that ties everything together.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Secret Management?**
  - The article treats Secret Management as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Secret Management?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Secret Management reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): Build Artifacts](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker Build](./07-docker-build.md)
- [GitHub Actions 101 (8/10): Deployment Automation](./08-deploy-automation.md)
- **Secret Management (current)**
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [Using secrets in GitHub Actions](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)
- [Automatic token authentication](https://docs.github.com/actions/security-guides/automatic-token-authentication)
- [Security hardening for GitHub Actions](https://docs.github.com/actions/security-guides/security-hardening-for-github-actions)
- [Workflow commands - add-mask](https://docs.github.com/actions/using-workflows/workflow-commands-for-github-actions#masking-a-value-in-a-log)

Tags: GitHubActions, Secret, Security, OIDC, CICD
