---
series: cloud-computing-101
episode: 7
title: Identity and Security
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

# Identity and Security

Most cloud security incidents do not begin with a cinematic attack chain. They begin with ordinary mistakes: permissions that are too broad, access keys that live too long, and credentials that were easier to create than to rotate.

That is why IAM matters so much. In API-driven infrastructure, identity is not a side concern. It is the operating model that decides who may call what, from where, and for how long.

This is post 7 in the Cloud Computing 101 series.

In this post, we'll break down users, groups, roles, policies, MFA, and KMS through the lens of least privilege and temporary credentials.

> Cloud security starts by shrinking blast radius: prefer temporary credentials, keep permissions narrow, and make encryption plus audit trails the default.

## Questions This Chapter Answers

- IAM users, groups, roles, and policies
- The least privilege principle
- MFA and key rotation
- Encrypting data with KMS
- Five common pitfalls

## Why It Matters

Most security incidents start with excessive permissions and forgotten keys. Solid IAM shrinks the blast radius of any single mistake.

## Concept at a Glance

![Core IAM relationship between users, roles, policies, and protected resources](../../../assets/cloud-computing-101/07/07-01-concept-at-a-glance.en.png)

*Core IAM relationship between users, roles, policies, and protected resources*

## Key Terms

- **User**: a person or long-lived credential.
- **Group**: a bundle of users that receives policies.
- **Role**: an identity that hands out *temporary* credentials.
- **Policy**: an allow/deny rule, written as JSON.
- **KMS**: a central service for managing encryption keys.

## Before/After

**Before**: access keys hardcoded in source — eventually leaked.

**After**: an EC2 role attached to the instance, with auto-refreshed temporary tokens.

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

## What to Notice in This Code

- A role needs both a *trust* policy and a *permissions* policy.
- Keep `Resource` as narrow as possible.
- Avoid wildcards in `Action`.

## How to Verify This Example

In IAM, the most useful verification step is reading the trust relationship and the attached permission scope separately. That is where the conceptual difference between roles and policies becomes operationally obvious.

```bash
aws iam get-role --role-name my-app-role
aws iam list-attached-role-policies --role-name my-app-role
```

**Expected output:**

- `AssumeRolePolicyDocument` should show `ec2.amazonaws.com` as the trusted principal.
- The attached-policy list should include the least-privilege policy ARN you created.
- You need both outputs to answer the two different questions: who may assume the role, and what may the role do after assumption.

### Where teams usually get stuck

- A permissions policy without the right trust policy creates a role that nobody can actually use.
- `Action: *` feels fast today and expensive during every later audit.
- Long-lived user keys become an operational liability long before they become a public incident.

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

## Practice Problems

1. State the fundamental difference between a User and a Role in one line.
2. Write the `Resource` field of a least-privilege S3 policy in one line.
3. Give one scenario where a customer-managed KMS key is preferable to an AWS-managed one.

## Wrap-up and Next Steps

Once permissions are right, the next question is *what is actually happening*. The next post covers Monitoring.

<!-- toc:begin -->
- [What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Region and Availability Zone](./03-region-and-availability-zone.md)
- [Compute](./04-compute.md)
- [Storage](./05-storage.md)
- [Network](./06-network.md)
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
