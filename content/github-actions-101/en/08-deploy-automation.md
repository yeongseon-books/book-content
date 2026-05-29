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

- How do you separate staging auto-deploy from production approval gates?
- Why do GitHub Environments become the center of deployment policy?
- How does OIDC replace long-lived cloud keys?

## Why It Matters

Manual deploys lose reproducibility easily. Even the same person following the same document can produce different results when environment variables, command order, or checkout state differ slightly. When you codify deployment as a workflow, you can trace exactly which commit went through which steps to reach which environment.

I see the biggest value of deployment automation in traceability rather than speed. When records exist, you can narrow down incident causes; approval procedures can be preserved as operational rules. GitHub Actions is well-suited for binding these records to code.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| Environment | GitHub's deployment environment unit | Good for separating staging and production policies |
| Required reviewers | Per-environment approvers | Connects the production gate to code |
| OIDC | Short-lived token-based cloud trust | The key mechanism for reducing long-lived access keys |
| Promotion | Moving from staging to production | Passes a verified artifact to the next stage |
| Rollback | Reverting to the previous stable deployment | Operational procedures are also automation targets |

## Before/After

In manual deployment, someone runs `kubectl apply` from a local terminal. Which manifest was used, which image tag was applied, what warnings appeared — all depend on human memory. In this structure, even when mistakes happen, it is difficult to trace back.

When you auto-deploy to staging after PR merge and then promote to production through approval using the same flow, every step is recorded in Actions logs and environment history. This difference directly connects to incident response speed.

## Deploy Automation in 5 Steps

### Step 1 — Define environments first

```text
Repo > Settings > Environments
- staging: no protection rules
- production: 1 required reviewer, 5-min wait timer
```

The reason to define environment policy before writing deployment code is clear: you need to decide first which environments allow automatic deployment and which require human approval before proceeding.

### Step 2 — Auto-deploy to staging

```yaml
deploy-staging:
  needs: build
  environment: staging
  runs-on: ubuntu-latest
  steps:
    - run: kubectl apply -f k8s/staging/
```

Staging's character is more about being a fast verification lane than about deployment itself. An automatic deployment pattern on main push is therefore natural.

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

The important thing here is that the single `environment` line is not just a label — it connects to policy. If you have set required reviewers on production, this job cannot proceed without approval.

### Step 4 — OIDC for short-lived credentials

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

Keeping long-lived AWS keys in secrets is risky. OIDC receives trust only briefly at execution time, making it far better for reducing the exposure surface.

### Step 5 — Rollback as a workflow

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

If the rollback procedure exists only in documentation, it is hard to find during a 3 AM incident. Making it an executable workflow lets operators respond much faster.

## What Success Looks Like at This Point

```text
deploy-staging  Pass
waiting on environment protection rules for production
deploy-production  Pending approval
```

When staging finishes automatically and production pauses in a waiting state because of environment rules, that is close to the intended structure. After approval, the production job should continue using the same artifact and same manifest — that is what makes it a true promotion flow.

## If Deploy Blocks or Fails, Check These First

- **Production runs immediately**: the Environment protection rules in repository settings are not actually wired up.
- **OIDC authentication fails**: verify both `id-token: write` permission and the cloud-side trust policy conditions (audience, subject).
- **Staging and production behave differently**: check whether the image tag or manifest differs between environments. Promotion should be a flow of moving the same artifact.

## Keep Automatic Zones and Approval Zones Intentionally Separate

Staging is your fast feedback channel, so automatic deployment usually makes sense. Production, on the other hand, is safer when you bundle human approval, wait timers, environment-scoped secrets, and deployment URL tracking together. If you treat both environments with the same policy, staging becomes too slow and production becomes too casual — an awkward structure.

## Deployment Strategy Workflows

Depending on the deployment method, the workflow structure changes. Here is a comparison of the main strategies.

| Strategy | Behavior | Risk | Suitable Environment |
| --- | --- | --- | --- |
| Direct replace | Swap existing instances with new version | High | Dev/Test |
| Blue-green | Spin up new environment and switch traffic | Medium | Staging/Production |
| Canary | Route only partial traffic to new version | Low | Production |
| Rolling | Replace instances sequentially | Medium | Production |

### Blue-Green Deployment Workflow

```yaml
jobs:
  deploy-blue-green:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6

      - name: Deploy new environment (Green)
        run: |
          ./scripts/deploy-green.sh ${{ github.sha }}

      - name: Health check
        run: |
          timeout 120 bash -c '
            until curl -sf https://green.example.com/health; do
              sleep 5
            done
          '

      - name: Smoke test
        run: |
          pytest tests/smoke -q --base-url=https://green.example.com

      - name: Switch traffic
        run: |
          ./scripts/switch-traffic.sh green

      - name: Clean up previous environment (Blue)
        run: |
          sleep 300  # 5-minute wait (rollback buffer)
          ./scripts/cleanup-blue.sh
```

The key to this pattern is switching traffic only after health checks and smoke tests pass on the new environment. If they fail, remove Green and keep the existing Blue.

### Canary Deployment Workflow

```yaml
jobs:
  canary:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6

      - name: Canary deploy (10% traffic)
        run: ./scripts/deploy-canary.sh ${{ github.sha }} --weight=10

      - name: Observe metrics (10 minutes)
        run: |
          sleep 600
          ERROR_RATE=$(./scripts/check-error-rate.sh canary)
          echo "Error rate: ${ERROR_RATE}%"
          if (( $(echo "$ERROR_RATE > 1.0" | bc -l) )); then
            echo "::error::Canary error rate too high: ${ERROR_RATE}%"
            ./scripts/rollback-canary.sh
            exit 1
          fi

      - name: Full rollout
        run: ./scripts/promote-canary.sh --weight=100
```

Canary deployment is the final stage of automation. It makes automatic rollback decisions based on metrics like error rate.

---

## GitHub Environments Deep Dive

Environments are not simple secret groups — they are the center of deployment policy.

### Protection Rules

```yaml
jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh production
```

Protection rules you can configure on an environment in the GitHub UI:

| Rule | Effect |
| --- | --- |
| Required reviewers | Designated person must approve before deploy proceeds |
| Wait timer | Wait N minutes after approval (final cancel opportunity) |
| Branch restrictions | Allow deployment only from specific branches |
| Custom deployment rules | Integration with external system verification |

```yaml
# staging is automatic, production needs approval
jobs:
  deploy-staging:
    environment: staging
    # No protection rules → auto-deploy
    ...

  deploy-production:
    needs: deploy-staging
    environment: production
    # Required reviewers set → awaiting approval
    ...
```

In this structure, staging deployment proceeds automatically while production deployment starts only after a reviewer approves, following staging success.

---

## OIDC-Based Cloud Authentication

Storing long-lived access keys in GitHub Secrets carries three problems: key rotation burden, exposure risk, and permission excess. OIDC (OpenID Connect) solves these fundamentally.

### AWS OIDC Integration

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
          aws-region: ap-northeast-2

      - run: aws ecs update-service --cluster prod --service app --force-new-deployment
```

How OIDC works:

1. GitHub Actions generates a JWT token (containing workflow, repository, and branch information).
2. AWS IAM validates this token and issues temporary credentials.
3. The temporary credentials are valid only during job execution.

Comparison with long-lived keys:

| Aspect | Long-lived Keys | OIDC |
| --- | --- | --- |
| Validity period | Permanent until manual rotation | Valid only during job execution (15min-1hr) |
| Storage location | GitHub Secrets | None (issued in real-time) |
| Permission scope | All permissions granted to the key | Restricted by IAM Role conditional policies |
| Exposure risk | Can leak from logs/forks | Token cannot be reused |

### GCP OIDC Integration

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/repo
    service_account: deploy@project.iam.gserviceaccount.com

- uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: app
    image: gcr.io/project/app:${{ github.sha }}
```

Both AWS and GCP require `permissions: id-token: write`. Without this permission, JWT token generation fails.

---

## Rollback Automation

A workflow for quickly reverting to the previous version when problems are discovered after deployment.

```yaml
name: rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        required: true
      version:
        description: "Version tag or SHA to roll back to"
        required: true
        type: string
      reason:
        description: "Rollback reason"
        required: true
        type: string

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ inputs.version }}

      - name: Rollback start notification
        run: |
          echo "::notice::Rolling back ${{ inputs.environment }} to ${{ inputs.version }}"
          echo "Reason: ${{ inputs.reason }}"

      - name: Deploy
        run: ./scripts/deploy.sh ${{ inputs.environment }} ${{ inputs.version }}

      - name: Health check
        run: |
          timeout 60 bash -c '
            until curl -sf ${{ vars.HEALTH_URL }}/health; do sleep 5; done
          '

      - name: Rollback complete notification
        run: |
          ./scripts/notify.sh "Rollback complete: ${{ inputs.environment }} → ${{ inputs.version }} (Reason: ${{ inputs.reason }})"
```

Important points in the rollback workflow:

- **Make the reason field required.** You need to be able to track why the rollback happened later.
- **Environment protection rules apply.** Production rollbacks may also require approval.
- **Include health checks.** The rollback itself can fail, so verification is necessary.

---

## Deploy Notifications and Audit Logs

As deployment automation matures, tracking "who deployed what and when" becomes important.

```yaml
- name: Record deployment
  run: |
    gh api repos/${{ github.repository }}/deployments \
      -f ref=${{ github.sha }} \
      -f environment=${{ inputs.environment || 'staging' }} \
      -f description="Deployed by ${{ github.actor }}"

- name: Slack notification
  if: always()
  uses: slackapi/slack-github-action@v2.0.0
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    webhook-type: incoming-webhook
    payload: |
      {
        "text": "Deploy ${{ job.status }}: ${{ inputs.environment }} @ ${{ github.sha }}\nBy: ${{ github.actor }}\nRun: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
      }
```

Using the GitHub Deployments API, you can visually check deployment history in the repository's Environments tab. Slack notifications help the team track deployment status in real time.

---

## Post-Deploy Verification Automation

A pattern for automatically verifying after deployment. Relying on manual checks delays incident discovery.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    outputs:
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - uses: actions/checkout@v6
      - id: deploy
        run: |
          URL=$(./scripts/deploy.sh staging)
          echo "url=${URL}" >> "$GITHUB_OUTPUT"

  post-deploy-check:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Health check
        run: |
          for i in {1..10}; do
            STATUS=$(curl -so /dev/null -w "%{http_code}" ${{ needs.deploy.outputs.url }}/health)
            if [ "$STATUS" = "200" ]; then
              echo "Health check passed"
              exit 0
            fi
            sleep 10
          done
          echo "::error::Health check failed after 100s"
          exit 1

      - name: Smoke test
        run: pytest tests/smoke -q --base-url=${{ needs.deploy.outputs.url }}

      - name: Basic performance check
        run: |
          RESPONSE_TIME=$(curl -so /dev/null -w "%{time_total}" ${{ needs.deploy.outputs.url }}/api/ping)
          echo "Response time: ${RESPONSE_TIME}s"
          if (( $(echo "$RESPONSE_TIME > 2.0" | bc -l) )); then
            echo "::warning::Response time exceeds 2s: ${RESPONSE_TIME}s"
          fi

  auto-rollback:
    needs: [deploy, post-deploy-check]
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Auto-rollback
        run: ./scripts/rollback.sh staging
      - name: Notify
        run: ./scripts/notify.sh "Auto-rollback triggered for staging"
```

The structure of this workflow:

1. **deploy**: deploys and outputs the URL.
2. **post-deploy-check**: verifies health check, smoke tests, and response time.
3. **auto-rollback**: automatically reverts to the previous version if verification fails.

`if: failure()` is the key. The rollback job runs only when the preceding job fails. This pattern builds a basic safety net without human intervention.

---

## Deployment Maturity Stages

The workflow structure evolves with the team's deployment maturity.

| Maturity | Deploy Frequency | Workflow Characteristics |
| --- | --- | --- |
| Early | Weekly manual | workflow_dispatch, single environment |
| Intermediate | Daily automatic | Staging auto + production approval |
| Mature | Per PR merge | Canary + auto-rollback + metric-based decisions |

At the early stage, automating manual deployment with `workflow_dispatch` alone is a big step forward. It structurally prevents mistakes like "skipped a step" or "pointed at the wrong environment" that happen in manual deployments.

At the intermediate stage, you separate staging auto-deploy from the production approval gate. The rhythm becomes: deploy to staging daily, let the team verify, then promote to production.

At the mature stage, canary deployments start automatically with each PR merge, and promotion or rollback is decided based on metrics. At this point, deployment becomes routine rather than a special event.

## Five Common Mistakes

1. **No required reviewers on production.** Anyone can deploy.
2. **Storing long-lived AWS keys in secrets.** Leak risk.
3. **Rollback procedure only in docs.** Unfindable at 3 AM.
4. **Different manifests for staging and production.** Drift creeps in.
5. **No deploy notifications to Slack/Issues.** History is lost.

The fourth mistake is particularly insidious. Once you start maintaining separate manifests citing environment-specific differences, "it works in staging but not in production" type drift accumulates easily.

## Checklist

- [ ] GitHub Environments are defined.
- [ ] Production has required reviewers.
- [ ] OIDC authenticates to the cloud.
- [ ] A rollback workflow exists.

## Practice Problems

1. Create a staging environment that auto-deploys on main push.
2. Add an approval gate to the production environment.
3. Write a `workflow_dispatch` rollback workflow.

## Wrap-up and Next Steps

The goal of deployment automation is not unconditionally fast deployment but reproducible deployment. Designing staging auto-deploy, production approval, OIDC, and rollback workflows together lets you achieve both deployment speed and operational stability.

Next: Secret Management. As deployment becomes more automated, the secret exposure surface widens, so we need to establish principles for handling credentials and permissions.

## Answering the Opening Questions

- **How do you separate staging auto-deploy from production approval gates?**
  - The staging environment has no protection rules, deploying automatically on main push. The production environment has required reviewers, preventing deployment without approval. Forcing order with `needs: deploy-staging` embeds the rule "only code verified in staging becomes a production candidate" into the workflow.
- **Why do GitHub Environments become the center of deployment policy?**
  - Environments bundle secret isolation, approval gates, branch restrictions, and wait timers into one configuration. Placing different AWS account or GCP project secrets per environment structurally prevents deploying to production with staging secrets. Deployment history is also tracked per environment.
- **How does OIDC replace long-lived cloud keys?**
  - OIDC issues temporary credentials at workflow runtime. No long-lived keys in GitHub Secrets needed; tokens are valid only during job execution; IAM policies can restrict by repository/branch/environment. No key rotation needed, and even if leaked, tokens cannot be reused — fundamentally strengthening security.
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
