---
series: devops-101
episode: 4
title: Environments and Configuration
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DevOps
  - Configuration
  - Secrets
  - Environment
  - TwelveFactor
seo_description: Safe patterns for separating dev, stage, and prod environments and managing config and secrets across them.
last_reviewed: '2026-05-15'
---

# Environments and Configuration

Teams usually notice configuration discipline only after it breaks. The application works in development, then stage uses a different secret, production needs a different domain, and suddenly the same code requires a different build for every environment.

Good configuration management prevents that drift. The code stays the same, the build artifact stays the same, and only environment-specific values change. That is what makes deployments repeatable instead of fragile.

This is post 4 in the DevOps 101 series. Here we look at how to separate code from configuration, treat secrets differently from ordinary settings, and keep environment changes reviewable.

## What You Will Learn

- The meaning of *dev / stage / prod* environments
- The *Twelve-Factor* *Config* principle
- The difference between *environment variables* and *secrets*
- A comparison of *.env*, *Vault*, and *AWS Secrets Manager*
- Five common pitfalls

## Why It Matters

*DB addresses, keys, and domains* differ per environment. They must be *decoupled from code* so the *same build artifact* can deploy to *every environment*.

> *Build once, run anywhere*.

## Concept at a Glance

![Concept at a Glance](../../../assets/devops-101/04/04-01-concept-at-a-glance.en.png)

*Concept at a Glance*

## Key Terms

- **Environment**: an *execution context* like *dev/stage/prod*.
- **Config**: per-environment *values* (DB URL, domain, etc.).
- **Secret**: *sensitive information* (API key, password).
- **.env**: a *local-development* config file.
- **Secrets manager**: an *encrypted store* like *Vault, AWS Secrets, Doppler*.

## Before/After

**Before (config baked into code)**

```python
DB_URL = "postgres://prod-db.example.com/app"   # hardcoded
API_KEY = "sk-1234..."                           # secret in code
```

**After (injected from the environment)**

```python
import os
DB_URL = os.environ["DB_URL"]
API_KEY = os.environ["API_KEY"]
```

## Hands-on: Five Steps for Config Management

### Step 1 - Separate locally with .env

```bash
# .env (gitignored)
DB_URL=postgres://localhost/app
API_KEY=test-key-1234
```

### Step 2 - Validate with pydantic-settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str
    api_key: str

settings = Settings()   # auto-loads from env
```

### Step 3 - Split per environment

```yaml
# k8s/values-prod.yaml
db_url: postgres://prod-db.example.com/app
api_key:
  valueFrom:
    secretKeyRef: { name: api-key, key: value }
```

### Step 4 - Keep secrets in a dedicated store

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/api-key
```

### Step 5 - Auto-inject secrets

```yaml
# Kubernetes External Secrets
apiVersion: external-secrets.io/v1
kind: ExternalSecret
spec:
  secretStoreRef: { name: aws-secrets, kind: ClusterSecretStore }
  data:
    - secretKey: api-key
      remoteRef: { key: prod/api-key }
```

## What to Notice in This Code

- *Secrets* never enter the *code repository*.
- Validate config *at startup*. Discovering *missing values* at runtime is too late.
- *Per-environment YAML* increases visibility.

## Five Common Mistakes

1. **Committing secrets *to Git*.** They are *permanently exposed*. Even *git filter-repo* cannot fully erase them.
2. **Using *.env* in *production*.** Move to a secrets manager.
3. **The *same secret* across all environments.** A leak affects *every environment*.
4. **Changing config at runtime *without restart*.** A *split-state* bug appears.
5. **Per-environment *code branches*.** *if env == "prod"* is an anti-pattern.

## How This Shows Up in Production

Large teams keep secrets in *Vault* or *AWS Secrets Manager* and use the *External Secrets Operator* to auto-inject them into *Kubernetes*.

## How a Senior Engineer Thinks

- *One codebase, N environments*. Build once.
- *Secret rotation* must be *automatic*.
- *Config changes* are subject to *PR and review*.
- *Environment branching is config, not code*.
- *Secret leaks are a matter of when*. Build early-detection.

## Checklist

- [ ] *.env* is in *.gitignore*.
- [ ] *Secrets* live in a *dedicated store*.
- [ ] *Per-environment config files* are separated.
- [ ] The app *validates config at startup*.

## Practice Problems

1. Search your project's *git history* for *secrets*.
2. Add config validation with *pydantic-settings*.
3. Split config into *per-environment YAMLs*.

## Wrap-up and Next Steps

Config management is the start of *environment independence*. In the next post we treat *infrastructure itself as code* with *IaC*.

<!-- toc:begin -->
- [What Is DevOps?](./01-what-is-devops.md)
- [CI Pipeline](./02-ci-pipeline.md)
- [CD and Deployment Strategies](./03-cd-and-deployment.md)
- **Environments and Configuration (current)**
- Infrastructure as Code (upcoming)
- Containers and Build (upcoming)
- Monitoring and Alerting (upcoming)
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)
<!-- toc:end -->

## References

- [The Twelve-Factor App — Config](https://12factor.net/config)
- [HashiCorp Vault](https://developer.hashicorp.com/vault)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [External Secrets Operator](https://external-secrets.io/)

Tags: DevOps, Configuration, Secrets, Environment, TwelveFactor
