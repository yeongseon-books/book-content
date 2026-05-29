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

This is the 9th post in the GitHub Actions 101 series. In this post, we will use scope, least privilege, OIDC, and runtime masking to treat secrets as operational resources instead of YAML variables.


![github actions 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/09/09-01-concept-at-a-glance.en.png)
*github actions 101 chapter 9 flow overview*

## Questions to Keep in Mind

- How do repository, environment, and organization secrets differ?
- Why should `GITHUB_TOKEN` permissions be narrowed as much as possible?
- How does OIDC reduce the long-lived key problem?

## Why It Matters

Secret leakage has enormous recovery costs. A failed test can be fixed, but a token printed to a public log is already on the internet. So the secret problem is not about "never making a mistake" — it is about building structures that minimize exposure scope even when mistakes happen.

Secrets are not just a security team concern either. The developer designing CI decides what permissions to grant and which environments to expose values to, so pipeline design itself heavily influences security posture. I believe how a team handles secrets in GitHub Actions reveals its operational maturity well.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| Repository secret | Secret scoped to a single repository | Suitable for single-repo credentials |
| Environment secret | Secret accessible only in a specific environment | Good for narrowing scope like production passwords |
| Organization secret | Secret shared across multiple repos | Useful for central management, but scope carefully |
| `GITHUB_TOKEN` | Short-lived token auto-issued per run | Must be treated with least-privilege principle |
| OIDC | Keyless cloud trust mechanism | Key to reducing long-lived access keys |

## Before/After

Teams with weak secret management commit `.env` files, pass access keys over messenger, or keep using keys known to former employees for years. This structure is quiet normally but costly when incidents happen.

When you manage secrets in the GitHub UI, narrow production values to environment scope, and switch cloud auth to OIDC, the attack surface shrinks significantly. Perfect security does not exist, but at least you can avoid structures that leak easily.

## Secret Management in 5 Steps

### Step 1 — Register secrets in the correct scope

```bash
# Use the gh CLI instead of clicking
gh secret set NPM_TOKEN --body "npm_xxx"
gh secret set --env production DB_PASSWORD --body "***"
```

Where to register a secret is not a technical question but a scope question. If a value is needed only in production, there is no reason to open it to the entire repository.

### Step 2 — Inject via environment variables in workflows

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

Injecting secrets as environment variables is generally safer. Passing them as command-line arguments increases the risk of exposure in process lists or logs.

### Step 3 — Minimize `GITHUB_TOKEN` permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  # everything else defaults to 'none'
```

A habit of granting broad default permissions is dangerous. If any single action malfunctions or behaves maliciously, the blast radius is larger.

### Step 4 — Mask runtime-generated values

```yaml
- name: Mask runtime token
  run: |
    TOKEN=$(curl -s https://auth.example.com/token | jq -r .token)
    echo "::add-mask::$TOKEN"
    echo "GENERATED_TOKEN=$TOKEN" >> "$GITHUB_ENV"
```

Not only values stored in GitHub count as secrets. Tokens freshly issued during execution need the same protection. `::add-mask::` is essential for these values.

### Step 5 — Put rotation policy into operations

```text
Settings > Secrets > Dependabot
- dependency update PRs can also access secrets
- put rotation on the calendar quarterly (gh secret set to refresh)
```

Rotation is not "something to do eventually" — it should be a regular operational procedure from the start. Documenting the renewal method alongside the schedule is better than just putting it on a calendar.

## What to Notice in This Code

- Secrets enter through environment variables, not command-line args — safer that way.
- `permissions:` starts from least privilege.
- `::add-mask::` applies to runtime-generated values too.

In other words, secret management is closer to "controlling where a value can be visible" than "hiding a value."

## Five Common Mistakes

1. **`echo $SECRET` for debugging.** It is now permanently in the log.
2. **`pull_request_target` opening secret access to external PRs.** Arbitrary code execution risk.
3. **`GITHUB_TOKEN` left at broad write permissions.** A bad action affects everything.
4. **Exposing secrets to fork PRs.** External contributors can exfiltrate them.
5. **No rotation schedule.** A former employee's key lives on for years.

The second and fourth mistakes are patterns you pick "for convenience" and deeply regret later. It is safer to assume that secrets should never reach paths where external code can execute.

---

## Understanding Secret Scopes in Depth

GitHub Actions secrets are divided into three scopes. Here are the characteristics and appropriate usage for each.

### Repository Secrets

```text
Settings > Secrets and variables > Actions > Repository secrets
```

Accessible only within the specific repository. Most secrets belong here.

### Environment Secrets

```text
Settings > Environments > [environment name] > Secrets
```

Accessible only in jobs configured with that specific environment. Most useful when staging and production have different database URLs.

```yaml
jobs:
  deploy-staging:
    environment: staging
    # DATABASE_URL is the staging environment's value
    steps:
      - run: echo "${{ secrets.DATABASE_URL }}"

  deploy-production:
    environment: production
    # DATABASE_URL is the production environment's value
    steps:
      - run: echo "${{ secrets.DATABASE_URL }}"
```

Same name (`DATABASE_URL`) but different values injected depending on environment. This structure structurally prevents "connecting to production with staging secrets" accidents.

### Organization Secrets

```text
Organization > Settings > Secrets and variables > Actions
```

Can be shared across multiple repositories in the organization. You can restrict which repositories have access, making them suitable for shared infrastructure secrets (Slack webhooks, shared registry auth, etc.).

### Scope Priority

When secrets with the same name exist in multiple scopes, the priority is:

1. Environment secret (highest)
2. Repository secret
3. Organization secret (lowest)

Using this priority, you can place organization defaults in Organization secrets and override with Repository secrets only in specific repositories.

---

## GITHUB_TOKEN Permission Management

`GITHUB_TOKEN` is a token automatically generated per workflow run. It can be used without separate setup, but since default permissions can be broad, you should apply the least-privilege principle.

### Repository Default Permission Setting

```text
Settings > Actions > General > Workflow permissions
→ Select "Read repository contents and packages permissions"
```

Setting the default to `read` means all workflows must explicitly declare permissions. It feels cumbersome at first, but "what permissions does this workflow have" becomes clearly visible in the YAML.

### Job-Level Permission Declaration

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    permissions:
      contents: read  # only checkout needed
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write     # GHCR push
      id-token: write     # OIDC
      deployments: write  # deployment status
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh
```

Granting only the minimum permissions each job needs means that even if the lint job is compromised, package push or deployment remains impossible.

### Available Permissions

| Permission | Purpose |
| --- | --- |
| contents | Repository code read/write |
| packages | Package registry access |
| pull-requests | PR comments, labels |
| issues | Issue management |
| deployments | Deployment status updates |
| id-token | OIDC token issuance |
| checks | Check result writing |
| actions | Workflow management |
| security-events | CodeQL result upload |

---

## Secret Exposure Prevention Techniques

Here are the paths through which secrets get exposed to logs and how to prevent them.

### Limitations of Automatic Masking

GitHub Actions automatically masks values referenced via `secrets.*` with `***` in logs. However, masking does not work in these cases:

1. **Transformed secrets**: base64 encoding or substrings are not masked.
2. **Structured output**: when a secret is embedded in JSON, the entire JSON may not be masked.
3. **Re-referenced as env var in other steps**: when environment variable expansion happens first.

### Manual Masking

```yaml
- name: Generate and mask temporary token
  run: |
    TOKEN=$(./scripts/get-token.sh)
    echo "::add-mask::${TOKEN}"
    echo "token=${TOKEN}" >> "$GITHUB_OUTPUT"
```

`::add-mask::` masks the value in subsequent logs. It must be applied to dynamically generated values (temporary tokens, keys extracted from API responses, etc.).

### Secret Scanning

```yaml
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - name: gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

gitleaks detects secrets accidentally committed in commit history. Including it in PR checks blocks secrets before they merge.

---

## Secret Rotation Automation

Secrets should be rotated regularly, but manual rotation is easy to miss. Here is what you can automate.

```yaml
name: rotate-secrets

on:
  schedule:
    - cron: "0 9 1 * *"  # 1st of each month
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v6

      - name: Generate new key
        id: new-key
        run: |
          NEW_KEY=$(openssl rand -hex 32)
          echo "::add-mask::${NEW_KEY}"
          echo "key=${NEW_KEY}" >> "$GITHUB_OUTPUT"

      - name: Register new key with service
        run: ./scripts/update-service-key.sh "${{ steps.new-key.outputs.key }}"

      - name: Update GitHub Secret
        run: |
          gh secret set API_KEY --body "${{ steps.new-key.outputs.key }}"

      - name: Revoke old key (after grace period)
        run: |
          sleep 300  # 5 minutes with both keys valid
          ./scripts/revoke-old-key.sh
```

The key to this pattern is the grace period. If you revoke the old key immediately after registering the new one, requests still using the old key can fail. You need an appropriate wait time where both keys are valid.

---

## Fork PR Secret Security

Handling secrets for fork PRs in open-source projects requires special care.

| Event | Secret Access in Fork PRs | Safe Usage |
| --- | --- | --- |
| `pull_request` | Not accessible | Safe — for validation without secrets |
| `pull_request_target` | Accessible | Dangerous — do not execute PR code |
| `workflow_run` | Accessible | Safe — only trusted code runs |

```yaml
# Safe pattern: only labeling in pull_request_target
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      # Do NOT checkout PR code!
      - uses: actions/labeler@v5
```

```yaml
# Dangerous pattern: checking out and running PR code
on:
  pull_request_target:

jobs:
  dangerous:
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ github.event.pull_request.head.ref }}  # attacker's code!
      - run: make test  # Makefile could contain secret exfiltration code
```

The second pattern must never be used. An attacker can place code in the PR's Makefile or test code that sends secrets to an external server.

---

## Variables vs Secrets

GitHub Actions has Variables in addition to Secrets. Non-sensitive configuration values should go in Variables.

| Aspect | Secrets | Variables |
| --- | --- | --- |
| Purpose | Sensitive values (tokens, passwords) | Configuration (URLs, flags) |
| Log masking | Automatic | None |
| Access method | `${{ secrets.NAME }}` | `${{ vars.NAME }}` |
| Scope | repo/env/org | repo/env/org |
| After modification | Cannot view value again | Can view anytime |

```yaml
jobs:
  deploy:
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: |
          # Variables: non-sensitive configuration
          echo "Deploying to: ${{ vars.DEPLOY_URL }}"
          echo "Region: ${{ vars.AWS_REGION }}"
          
          # Secrets: sensitive credentials
          ./scripts/deploy.sh \
            --url "${{ vars.DEPLOY_URL }}" \
            --token "${{ secrets.DEPLOY_TOKEN }}"
```

Putting values that should be in Variables into Secrets makes debugging harder — masking prevents you from seeing URLs or settings in logs. Conversely, putting secrets in Variables exposes them in logs.

---

## External Secret Manager Integration

In large organizations, GitHub Secrets alone may not suffice. Here are patterns for integrating with external tools like HashiCorp Vault, AWS Secrets Manager, or GCP Secret Manager.

### AWS Secrets Manager Integration

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
          role-to-assume: arn:aws:iam::123456789:role/github-actions
          aws-region: ap-northeast-2

      - name: Fetch secrets
        id: secrets
        run: |
          DB_PASSWORD=$(aws secretsmanager get-secret-value \
            --secret-id prod/db-password \
            --query SecretString --output text)
          echo "::add-mask::${DB_PASSWORD}"
          echo "db_password=${DB_PASSWORD}" >> "$GITHUB_OUTPUT"

      - name: Deploy
        env:
          DB_PASSWORD: ${{ steps.secrets.outputs.db_password }}
        run: ./scripts/deploy.sh
```

Advantages of external secret managers:

- **Centralized management**: manage and audit all secrets in one place.
- **Fine-grained access control**: IAM policies control who accesses which secrets.
- **Automatic rotation**: AWS Secrets Manager can configure automatic rotation via Lambda.
- **Version management**: track secret change history.

### HashiCorp Vault Integration

```yaml
- name: Fetch secrets from Vault
  uses: hashicorp/vault-action@v3
  with:
    url: https://vault.example.com
    method: jwt
    role: github-actions
    secrets: |
      secret/data/prod/db password | DB_PASSWORD ;
      secret/data/prod/api key | API_KEY
```

Vault's JWT authentication integrates with GitHub OIDC, enabling access without long-lived tokens.

---

## Secret Audit and Monitoring

A workflow for periodically verifying that secrets are properly managed.

```yaml
name: secret-audit

on:
  schedule:
    - cron: "0 9 * * 1"  # Every Monday

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Check unused secrets
        run: |
          echo "## Secret Usage Audit" > audit.md
          echo "" >> audit.md
          
          # Extract secrets referenced in workflows
          USED_SECRETS=$(grep -roh 'secrets\.\w\+' .github/workflows/ | sort -u | sed 's/secrets\.//')
          
          echo "### Secrets referenced in workflows:" >> audit.md
          echo "$USED_SECRETS" >> audit.md
          echo "" >> audit.md
          
          # Compare with registered secrets (gh cli)
          echo "### Secrets registered in repository:" >> audit.md
          gh secret list >> audit.md

      - uses: actions/upload-artifact@v7
        with:
          name: secret-audit
          path: audit.md
          retention-days: 30
```

This workflow is the starting point for finding "registered but unused secrets." Unused secrets only widen the attack surface and should be removed immediately.

---

## Incident Response for Committed Secrets

The response procedure when a secret is accidentally committed. More important than completely removing it from git history is immediately revoking that secret.

1. **Immediately revoke/rotate the secret**: invalidate the exposed key, token, or password immediately.
2. **Check GitHub notifications**: if GitHub Secret Scanning is enabled, an alert may already be waiting.
3. **Determine blast radius**: identify systems and data accessible with that secret.
4. **Clean git history** (optional): you can remove it from history with `git filter-repo` or BFG, but step 1 is more important since already-cloned copies retain it.
5. **Prevent recurrence**: add gitleaks to pre-commit hooks and enable scanning in CI.

```bash
# Remove file with git filter-repo (caution: force push required)
pip install git-filter-repo
git filter-repo --path credentials.json --invert-paths
```

The key insight is not "it is safe because we removed it from history" but "assume any exposed secret has already been stolen and revoke it."

## Checklist

- [ ] Secret scopes are deliberately chosen between repository, environment, and organization.
- [ ] `permissions:` is set to least privilege.
- [ ] OIDC authenticates to the cloud.
- [ ] A rotation schedule and renewal procedure exist.

## Practice Problems

1. Add a `DB_PASSWORD` secret to the production environment and use it safely in a workflow.
2. Reduce an existing workflow's `permissions:` to a least-privilege baseline.
3. Add a step that masks a runtime-generated token with `::add-mask::`.

## Wrap-up and Next Steps

Secret management in GitHub Actions is about designing storage, exposure, permissions, and rotation together. Keeping secrets outside code, narrowing scope by environment, and minimizing `GITHUB_TOKEN` and cloud auth permissions can significantly reduce most incident possibilities.

Next: a real-world CI/CD pipeline that ties everything together. Triggers, tests, quality gates, artifacts, Docker, deployment, and secrets — the final step to see how they all actually connect.

## Answering the Opening Questions

- **How do repository, environment, and organization secrets differ?**
  - Repository secrets are accessible across the entire repo, environment secrets only in jobs configured with that specific environment, and organization secrets are shared across multiple repos in the org. Priority order: environment > repository > organization. Different DB credentials for staging vs production go in environment secrets; org-wide Slack webhooks go in organization secrets.
- **Why should `GITHUB_TOKEN` permissions be narrowed as much as possible?**
  - Wide default permissions mean a compromised lint job could push packages, approve PRs, or modify code. Setting repository defaults to `read` and specifying only needed permissions per job prevents one job's security incident from escalating to another job's permissions. Since permissions are explicit in YAML, code review naturally asks "why does this job need this permission."
- **How does OIDC reduce the long-lived key problem?**
  - OIDC issues temporary tokens at workflow runtime, eliminating the need for long-lived keys in Secrets. Tokens are valid for only 15 minutes to 1 hour and cannot be reused. IAM policies can restrict tokens to specific repos/branches/environments, making the question "what is at risk if the key leaks" disappear entirely.
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
