---
series: github-actions-101
episode: 8
title: "GitHub Actions 101 (8/10): Deployment Automation"
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
  - Deploy
  - Environments
  - OIDC
  - CICD
seo_description: Environments, approval, and OIDC. From PR merge to staging and production with safe automated deployment.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (8/10): Deployment Automation

Teams that deploy by hand usually end up with the same blind spots. Staging is automatic but production still depends on a message in chat. Someone can run the command, but no one can reconstruct the exact sequence later. Rollback exists in a document somewhere, yet nobody wants to search for it during an incident.

Good deployment automation is not about removing every human decision. It is about automating the safe, repeatable path while making the risky path explicit through approval rules, environment policy, and short-lived credentials.

This is the 8th post in the GitHub Actions 101 series. In this post, we will design a deployment flow around GitHub Environments, required reviewers, OIDC, and codified rollback.


![github actions 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/08/08-01-concept-at-a-glance.en.png)
*github actions 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Deployment Automation?
- Which signal should the example or diagram make visible for Deployment Automation?
- What failure should be prevented first when Deployment Automation reaches a real system?

## What You Will Learn

- *GitHub Environments* and *required reviewers*
- *OIDC* for short-lived *AWS/GCP* credentials
- The *staging -> production* promotion pattern
- A *rollback* workflow
- Five common pitfalls

## Why It Matters

*Manual deploys* are the cause of *weekend pages*. Automation gives you *reproducibility*, not just speed.

> If the *deployment runbook* lives only in someone's head, an *incident is coming*.

## Key Terms

- **Environment**: GitHub's *deployment environment* (staging, production).
- **Required reviewers**: per-environment *approvers*.
- **OIDC**: a *short-lived token* trust with the cloud.
- **Promotion**: moving *staging to production*.
- **Rollback**: returning to the *previous deployment*.

## Before/After

**Before**: someone runs `kubectl apply` *locally*. No record of what was deployed.

**After**: PR merge -> *automatic staging deploy* -> *approval* -> *production*. Everything traceable in *Actions logs*.

## Hands-on: Deploy Automation in 5 Steps

### Step 1 — Define environments (UI)

```text
Repo > Settings > Environments
- staging: no protection rules
- production: 1 required reviewer, 5-min wait timer
```

### Step 2 — Auto-deploy to staging

```yaml
deploy-staging:
  needs: build
  environment: staging
  runs-on: ubuntu-latest
  steps:
    - run: kubectl apply -f k8s/staging/
```

### Step 3 — Production approval gate

```yaml
deploy-production:
  needs: deploy-staging
  environment:
    name: production
    url: https://app.example.com
  runs-on: ubuntu-latest
  steps:
    - run: kubectl apply -f k8s/production/
```

### Step 4 — OIDC for AWS short-lived credentials

```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
      aws-region: us-west-2
  - run: aws s3 sync ./build s3://my-bucket
```

### Step 5 — Rollback workflow

```yaml
on:
  workflow_dispatch:
    inputs:
      sha:
        description: "git sha to roll back to"
        required: true
jobs:
  rollback:
    environment: production
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh ${{ inputs.sha }}
```

## What success looks like at this point

```text
deploy-staging  Pass
waiting on environment protection rules for production
deploy-production  Pending approval
```

That pattern is usually what you want. Staging finishes automatically, while production stops because environment rules are actually active. After approval, the production job should continue with the same artifact and the same deployment definition rather than rebuilding or improvising a second path.

## If deploy blocks or fails, check these first

- **Production runs immediately**: the environment exists in the repository, but the protection rules are not actually configured.
- **OIDC authentication fails**: verify both `id-token: write` and the cloud-side trust policy conditions such as audience and subject.
- **Staging and production behave differently**: confirm both environments consume the same artifact and only the environment-specific values differ.

## Keep automatic zones and approval zones intentionally separate

Staging is usually your fast feedback lane, so automatic deployment makes sense there. Production is different: required reviewers, wait timers, environment-scoped secrets, and deployment URLs all belong there. If both environments share the same policy, staging often becomes too slow and production too casual.

## What to Notice in This Code

- A single *environment* line attaches an *approval gate*.
- *OIDC* eliminates *long-lived keys*.
- *Rollback* is also *codified as a workflow*.

## Five Common Mistakes

1. **No *required reviewers* on `production`.** Anyone can deploy.
2. **Storing long-lived *AWS keys* in secrets.** Leak risk.
3. **Rollback procedure *only in docs*.** Unfindable at 3 AM.
4. **Different manifests for staging and production.** Drift creeps in.
5. **No deploy notifications to *Slack/Issues*.** History is lost.

## How This Shows Up in Production

Mature teams chain *PR merge -> canary -> blue/green -> full rollout* in *one workflow*, with *automated metric checks* against Datadog/Grafana.

## How a Senior Engineer Thinks

- *Deploys are code*; *manual commands leave no trace*.
- *Production* always has *gates*.
- *Short-lived credentials* are the standard.
- *Rollback is a workflow*, too.
- *staging == production* — same manifest.

## Checklist

- [ ] *Environments* are defined.
- [ ] *production* has *required reviewers*.
- [ ] *OIDC* authenticates to the cloud.
- [ ] A *rollback* workflow exists.

## Practice Problems

1. Define a *staging* environment that auto-deploys on *main push*.
2. Add an *approval gate* to *production*.
3. Build a *workflow_dispatch* rollback workflow.

## Wrap-up and Next Steps

Deployment automation defines your *cost of change*. Next: *Secret management*.

## Answering the Opening Questions

- **How do you separate staging auto-deploy from production approval gates?**
  - The staging environment has no protection rules, deploying automatically on main push. The production environment has required reviewers, preventing deployment without approval. Forcing order with `needs: deploy-staging` embeds the rule "only code verified in staging becomes a production candidate" into the workflow.
- **Why do GitHub Environments become the center of deployment policy?**
  - Environments bundle secret isolation, approval gates, branch restrictions, and wait timers into one configuration. Placing different AWS account or GCP project secrets per environment structurally prevents deploying to production with staging secrets. Deployment history is also tracked per environment.
- **How does OIDC replace long-lived cloud keys?**
  - OIDC issues temporary credentials at workflow runtime. No long-lived keys in GitHub Secrets needed; tokens are valid only during job execution; IAM policies can restrict by repository/branch/environment. No key rotation needed, and even if leaked, tokens can't be reused — fundamentally strengthening security.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): Build Artifacts](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker Build](./07-docker-build.md)
- **Deployment Automation (current)**
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [Using environments for deployment](https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Configuring OpenID Connect in AWS](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)

Tags: GitHubActions, Deploy, Environments, OIDC, CICD
