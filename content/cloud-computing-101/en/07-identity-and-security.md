---
series: cloud-computing-101
episode: 7
title: "Cloud Computing 101 (7/10): Identity and Security"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Cloud
  - Security
  - IAM
  - AWS
  - Architecture
seo_description: IAM users, roles, policies, MFA, and KMS — cloud security fundamentals taught with least-privilege boto3 examples for beginners.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (7/10): Identity and Security

Most cloud security incidents do not begin with a cinematic attack chain. They begin with ordinary mistakes: permissions that are too broad, access keys that live too long, and credentials that were easier to create than to rotate.

This is the 7th post in the Cloud Computing 101 series.

IAM defines who can do what on which resources. Authentication proves who you are. Encryption protects data in transit and at rest. The shared responsibility model splits ownership: the provider secures the hardware and platform; you secure your applications, keys, and access rules.

In this post, we'll break down users, groups, roles, policies, MFA, and KMS through the lens of least privilege and temporary credentials.

> Cloud security starts by shrinking blast radius: prefer temporary credentials, keep permissions narrow, and make encryption plus audit trails the default.


![cloud computing 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/07/07-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 7 flow overview*
> Security is not a feature added at the end. It is a set of boundaries you decide to enforce from the start.

## Questions to Keep in Mind

- How do IAM users, groups, roles, and policies differ?
- Why should least privilege be the default?
- Why should MFA and key rotation be operational routines?

## Why It Matters

Most security incidents start with excessive permissions and forgotten keys. A single `Action: *`, a single key committed to Git, or a single admin account without MFA can shake an entire system. Solid IAM shrinks the blast radius of any single mistake.

Cloud environments are API-centric, so the permission model *is* the operational model. When access boundaries are unclear, risk scales with every new automation.

## Authentication vs Authorization

Before discussing IAM details, distinguish authentication from authorization. They are frequently confused but serve different purposes.

| Aspect | Authentication | Authorization |
| --- | --- | --- |
| Question | "Who are you?" | "Are you allowed to do this?" |
| Timing | At the start of a request | After authentication passes |
| Mechanism | Password, MFA, certificate, SSO token | IAM policy, RBAC, ABAC |
| Failure response | 401 Unauthorized | 403 Forbidden |
| AWS example | STS issues temporary credentials | IAM policy evaluation engine |

Even if authentication passes, the request fails when authorization denies it. Conversely, even the most precise authorization rules are useless if authentication is compromised. Both layers must be solid.

## Key Terms

- **User**: a person or long-lived credential.
- **Group**: a bundle of users that receives policies.
- **Role**: an identity that hands out *temporary* credentials.
- **Policy**: an allow/deny rule, written as JSON.
- **KMS**: a central service for managing encryption keys.
- **MFA**: an additional authentication factor beyond passwords.
- **STS**: Security Token Service — issues temporary credentials.
- **CloudTrail**: an audit log service that records API calls.

## IAM Policy Structure

An IAM policy is a JSON document. Each Statement contains four key elements:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificS3Read",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-prod",
        "arn:aws:s3:::my-app-prod/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        },
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

| Element | Role | Watch out |
| --- | --- | --- |
| Effect | Allow or Deny | Explicit Deny always wins over Allow |
| Action | API operations to allow/deny | Wildcard `*` is the most expensive choice at audit time |
| Resource | Target ARN | Bucket and bucket objects need separate ARNs |
| Condition | Additional restrictions | Combine IP, MFA, time, tags to narrow scope |

Conditions let you restrict even an Allow policy to "office IP only," "after MFA only," or "tagged resources only."

## RBAC Design Pattern

Role-Based Access Control manages permissions per role, not per user. As teams grow, attaching policies to individual users becomes unmanageable.

| Role | Target | Allowed Actions | Restrictions |
| --- | --- | --- | --- |
| admin-role | Platform team | IAM management, network config | No direct production data access |
| app-runtime-role | EC2/ECS services | S3 read, SQS consume, DynamoDB CRUD | No IAM modification, no cross-account |
| ci-deploy-role | CI/CD pipeline | ECR push, ECS service update | No production DB access |
| analyst-role | Data analysts | Athena queries, CloudWatch logs | No resource creation/deletion |
| readonly-role | New members, auditors | Describe/List/Get only | No write operations |

The key to RBAC design: define "what is the minimum permission this role needs to do its job?" first, then start from there.

## Before/After

**Before**: access keys hardcoded in source — eventually leaked.

**After**: an EC2 role attached to the instance, with auto-refreshed temporary tokens.

This matters because it makes security less dependent on human memory.

## Hands-on: Least-Privilege Policy

### Step 1 — Client

```python
import boto3, json
iam = boto3.client("iam")
```

### Step 2 — Policy document

```python
policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["s3:GetObject"],
        "Resource": "arn:aws:s3:::my-bucket/*",
    }],
}
```

### Step 3 — Create the policy

```python
def create_policy(name, doc):
    res = iam.create_policy(
        PolicyName=name, PolicyDocument=json.dumps(doc),
    )
    return res["Policy"]["Arn"]
```

### Step 4 — Create role and trust

```python
trust = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "ec2.amazonaws.com"},
        "Action": "sts:AssumeRole",
    }],
}

def create_role(name):
    res = iam.create_role(
        RoleName=name, AssumeRolePolicyDocument=json.dumps(trust),
    )
    return res["Role"]["Arn"]
```

### Step 5 — Attach

```python
def attach(role_name, policy_arn):
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
```

A role is not just a permission bundle. It requires both a trust policy (who may assume it) and a permissions policy (what it may do after assumption).

## Cross-Account Access: AssumeRole

Separating production and development into different AWS accounts reduces blast radius. Cross-account access is implemented via AssumeRole.

```bash
# Assume a production-account role from the dev account
aws sts assume-role \
  --role-arn arn:aws:iam::111122223333:role/prod-readonly \
  --role-session-name cross-account-audit \
  --duration-seconds 3600
```

The same pattern in Python:

```python
import boto3

sts = boto3.client("sts")

response = sts.assume_role(
    RoleArn="arn:aws:iam::111122223333:role/prod-readonly",
    RoleSessionName="cross-account-audit",
    DurationSeconds=3600,
)

credentials = response["Credentials"]
s3 = boto3.client(
    "s3",
    aws_access_key_id=credentials["AccessKeyId"],
    aws_secret_access_key=credentials["SecretAccessKey"],
    aws_session_token=credentials["SessionToken"],
)
```

Cross-account access requires two conditions: the target account's role trust policy must allow the calling account, and the calling account's user/role must have `sts:AssumeRole` permission.

## MFA Enforcement

Admin accounts and production-deploy permissions must be protected by MFA.

```bash
# Create virtual MFA device
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name admin-mfa \
  --outfile /tmp/qr.png \
  --bootstrap-method QRCodePNG

# Enable MFA (requires two TOTP codes)
aws iam enable-mfa-device \
  --user-name admin-user \
  --serial-number arn:aws:iam::123456789012:mfa/admin-mfa \
  --authentication-code1 123456 \
  --authentication-code2 789012
```

Enforce MFA via a Condition block in your policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyWithoutMFA",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

Attach this policy to a group and no action can be performed without MFA authentication.

## Security Audit Checklist and CLI Commands

Production accounts need periodic security reviews. Common audit commands:

```bash
# Find access keys unused for 90+ days
aws iam generate-credential-report
aws iam get-credential-report --output text --query Content | \
  base64 -d | cut -d',' -f1,9,11 | grep -v "N/A"

# Detect overly-broad policies: users with AdministratorAccess
aws iam list-entities-for-policy \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# List users without MFA
aws iam list-users --query 'Users[].UserName' --output text | \
  xargs -I{} sh -c \
  'aws iam list-mfa-devices --user-name {} --query "MFADevices" --output text | grep -q "." || echo "No MFA: {}"'

# Detect unused roles (check last-used date)
aws iam list-roles --query 'Roles[].RoleName' --output text | \
  xargs -I{} aws iam get-role --role-name {} \
  --query 'Role.{Name:RoleName,LastUsed:RoleLastUsed.LastUsedDate}'
```

| Audit Item | Frequency | Risk Level |
| --- | --- | --- |
| Disable unused access keys | Weekly | High |
| Remove users without MFA | Weekly | High |
| Count AdministratorAccess users | Monthly | Medium |
| Clean up unused roles | Monthly | Medium |
| Verify CloudTrail is enabled | Quarterly | High |

## Encryption: At-Rest, In-Transit, Client-Side

Data protection operates at three layers:

| Aspect | At-Rest | In-Transit | Client-Side |
| --- | --- | --- | --- |
| Target | Disk, S3, RDS | Network segments | Application memory |
| Mechanism | AES-256, KMS | TLS 1.2+ | App encrypts/decrypts directly |
| Key management | KMS or service default key | Certificates (ACM) | App holds keys |
| AWS example | S3 SSE-KMS, EBS encryption | ALB HTTPS, RDS SSL | S3 client-side encryption |
| Advantage | Transparent, low perf impact | Prevents eavesdropping | Provider cannot see plaintext |
| Disadvantage | Provider can access keys | Certificate management | Increased app complexity |

KMS automates key creation, rotation, and retirement. Customer-managed keys (CMK) allow fine-grained access control via key policies, and key usage is logged in CloudTrail.

```bash
# Create a KMS key
aws kms create-key --description "my-app encryption key"

# Enable automatic rotation (annual)
aws kms enable-key-rotation --key-id <key-id>

# Check key status
aws kms describe-key --key-id <key-id> \
  --query 'KeyMetadata.{State:KeyState,Rotation:KeyRotationEnabled}'
```

## Secrets Management: Secrets Manager vs Parameter Store

Sensitive information (DB passwords, API keys, certificates) must never live in code.

| Comparison | Secrets Manager | Parameter Store (SecureString) |
| --- | --- | --- |
| Auto-rotation | Built-in (Lambda-based) | Must implement yourself |
| Cost | $0.40/secret/month + API calls | Standard parameters free |
| Size limit | 64 KB | 8 KB |
| Cross-account sharing | Via resource policy | Limited |
| Best for | DB credentials, auto-rotation needed | Config values, cost-sensitive |

```python
import boto3

secrets = boto3.client("secretsmanager")

# Retrieve a secret
response = secrets.get_secret_value(SecretId="my-app/db-password")
password = response["SecretString"]

# Parameter Store retrieval
ssm = boto3.client("ssm")
param = ssm.get_parameter(Name="/my-app/api-key", WithDecryption=True)
api_key = param["Parameter"]["Value"]
```

Both services encrypt with KMS and control access via IAM. For DB credentials requiring rotation, use Secrets Manager. For simple config values, Parameter Store is the common choice.

## Multi-Cloud Verification Commands

Writing a policy is not enough — verify that permissions are restricted as expected.

```bash
# AWS: check current caller identity and role policies
aws sts get-caller-identity
aws iam list-attached-role-policies --role-name my-app-role
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/my-app-role \
  --action-names s3:GetObject s3:DeleteObject \
  --resource-arns arn:aws:s3:::my-app-prod/example.txt

# Azure: inspect role assignments
az role assignment list --assignee <principal-id> --all

# Google Cloud: inspect project IAM bindings
gcloud projects get-iam-policy my-gcp-project --format=json
```

`simulate-principal-policy` lets you test whether specific actions are allowed before applying a policy in production — useful for tightening least-privilege policies incrementally.

## IaC for IAM Management

Managing IAM policies manually in the console makes change tracking difficult. Codifying policies with Terraform enables review, version control, and rollback.

```hcl
resource "aws_iam_role" "app" {
  name = "my-app-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "app_readonly" {
  name = "my-app-s3-readonly"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::my-app-prod/*"]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "app" {
  role       = aws_iam_role.app.name
  policy_arn = aws_iam_policy.app_readonly.arn
}
```

With IaC, colleagues review permission changes during PR review, and `terraform plan` shows the change scope before apply.

## Least Privilege vs Excessive Permissions

| Aspect | Least Privilege | Excessive Permissions |
| --- | --- | --- |
| Scope | Only required actions specified | Wildcard `*` heavy |
| Incident blast radius | Limited to role boundary | Can expand to entire account |
| Audit ease | Easy root-cause tracing | Difficult root-cause tracing |
| Initial setup cost | High (precise design needed) | Low (allow everything first) |
| Long-term ops cost | Low (fewer incidents) | High (incident response cost) |

## Service Control Policies (SCP) and Permission Boundaries

With AWS Organizations you can apply Service Control Policies to OUs. An SCP sets the maximum permissions any IAM entity in an account can have.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyLeaveOrganization",
      "Effect": "Deny",
      "Action": "organizations:LeaveOrganization",
      "Resource": "*"
    },
    {
      "Sid": "DenyDisableCloudTrail",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail"
      ],
      "Resource": "*"
    }
  ]
}
```

When an SCP denies an action, no IAM policy within that account can override it. This prevents individual account admins from accidentally disabling audit logs or leaving the organization.

Permission Boundaries apply a similar ceiling at the individual role/user level — useful when developers need IAM role creation rights but must not create roles with higher privileges than their own.

```bash
# Set a Permission Boundary
aws iam put-role-permissions-boundary \
  --role-name developer-created-role \
  --permissions-boundary arn:aws:iam::123456789012:policy/BoundaryPolicy
```

| Mechanism | Applied To | Purpose |
| --- | --- | --- |
| SCP | Organization/OU/Account | Permission ceiling for the entire account |
| Permission Boundary | Individual role/user | Permission ceiling for delegated admin-created roles |
| IAM Policy | Individual role/user | Actual allow/deny specification |

An action executes only when all three layers allow it. Understanding this intersection model reduces confusion when debugging "I attached the policy but it's still denied."

## What to Notice in This Code

- A role needs both a *trust* policy and a *permissions* policy.
- Keep `Resource` as narrow as possible.
- Avoid wildcards in `Action`.

## Five Common Mistakes

1. **Granting `Action: *`.**
2. **Committing access keys to git.**
3. **Doing daily work as the root account.**
4. **Skipping MFA.**
5. **Never rotating keys.**

## How This Shows Up in Production

EC2 roles access S3. KMS encrypts data at rest. AWS SSO handles staff login. MFA is required for every user.

## How a Senior Engineer Thinks

- Least privilege is the default.
- Prefer roles; user keys are the exception.
- Every key has a rotation schedule.
- Audit logging is on by default.
- Separation — `prod` and `dev` live in *different* accounts.

## Checklist

- [ ] Root account MFA enabled.
- [ ] Key rotation schedule in place.
- [ ] Roles preferred over user keys.
- [ ] CloudTrail enabled.
- [ ] Condition blocks narrow policy scope.
- [ ] Cross-account access uses AssumeRole.
- [ ] Secrets live in Secrets Manager/Parameter Store, not in code.

## Practice Problems

1. State the fundamental difference between a User and a Role in one line.
2. Write the `Resource` field of a least-privilege S3 policy in one line.
3. Give one scenario where a customer-managed KMS key is preferable to an AWS-managed one.
4. Explain why the MFA enforcement policy uses `BoolIfExists` in its Condition block.
5. Choose between Secrets Manager and Parameter Store for a DB password, and explain why.

## Wrap-up and Next Steps

Once permissions are right, the next question is *what is actually happening*. The next post covers Monitoring.

## Answering the Opening Questions

- **How do IAM users, groups, roles, and policies differ?**
  - A user has long-term credentials, a group bundles users, a role issues temporary credentials, and a policy is a JSON permission document attached to any of these.
- **Why should least privilege be the default?**
  - Excessive permissions expand incident blast radius to the entire account, make auditing difficult, and increase long-term operational costs. Starting narrow and widening when needed is always easier than the reverse.
- **Why should MFA and key rotation be operational routines?**
  - MFA blocks the impact of credential leaks, and key rotation limits the validity window of compromised keys. Both require periodic verification—not one-time setup—to remain effective.
<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region and Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- **Identity and Security (current)**
- Monitoring (upcoming)
- Cost Management (upcoming)
- Cloud Architecture Basics (upcoming)

<!-- toc:end -->

## References

- [AWS IAM user guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)

Tags: Cloud, Security, IAM, AWS, Architecture
