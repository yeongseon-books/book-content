---
series: devops-101
episode: 5
title: Infrastructure as Code
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - IaC
  - Terraform
  - Cloud
  - Automation
seo_description: Terraform으로 인프라를 코드처럼 버전 관리하고 안전하게 변경하는 IaC의 원칙.
last_reviewed: '2026-05-11'
---

# Infrastructure as Code

> DevOps 101 시리즈 (5/10)


## 이 글에서 다룰 문제

콘솔로 만든 인프라는 기억에만 존재합니다. 다른 환경에 복제하려면 다시 클릭해야 하고, 그 사이 드리프트가 생깁니다.

> *코드만이 진실의 원천(SSOT)* 이다.

## 전체 흐름
```mermaid
flowchart LR
    Code["main.tf"] --> Plan["terraform plan"]
    Plan --> Apply["terraform apply"]
    Apply --> Cloud["AWS/GCP/Azure"]
    Apply --> State["state file"]
```

## Before/After

**Before (콘솔 클릭)**

```text
- 누가 *언제* 만들었는지 모름
- 다른 region에 복제하려면 *처음부터*
- 변경 이력 없음
```

**After (Terraform)**

```hcl
# main.tf
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs"
  tags   = { Env = "prod" }
}
```

## Terraform 5단계

### 1단계 — Provider 정의

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
provider "aws" { region = "us-east-1" }
```

### 2단계 — Resource 작성

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs-${var.env}"
}
```

### 3단계 — Plan으로 변경 확인

```bash
terraform init
terraform plan
# 계획: 추가 1개, 변경 0개, 삭제 0개.
```

### 4단계 — Apply

```bash
terraform apply
# yes 입력 시 실제 생성
```

### 5단계 — Module로 재사용

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  cidr    = "10.0.0.0/16"
}
```

## 이 코드에서 주목할 점

- *plan* 후 *apply* — 변경을 눈으로 확인한 뒤에만 실행합니다.
- *State*는 *원격 백엔드*(S3, GCS)에 저장합니다.
- *Module*로 *환경별 차이*를 변수로만 다룹니다.

## 자주 하는 실수 5가지

1. **State를 로컬에 두기.** 팀원과 충돌하고 *유실 위험*이 큽니다.
2. **State에 시크릿 평문 저장.** S3 백엔드 + KMS 암호화가 필수입니다.
3. **콘솔에서 수동 변경.** 드리프트가 발생합니다.
4. **`apply` 자동화 안 함.** 수동 실행은 *오타와 사고* 의 원인.
5. **`destroy` 명령을 *프로덕션에 직접*.** 환경 분리 + approval 게이트 필수.

## 실무에서는 이렇게 쓰입니다

성숙한 팀은 *Terraform Cloud* 또는 *Atlantis* 로 *PR 기반 plan/apply* 를 자동화합니다. *변경 리뷰* 가 *코드 리뷰* 와 동일하게 됩니다.

## 체크리스트

- [ ] *모든 인프라* 가 코드로 정의되어 있다.
- [ ] *State* 가 *원격 백엔드* 에 있다.
- [ ] *Plan* 이 *PR* 에 자동 표시된다.
- [ ] *Tag 정책* 이 강제된다.

## 정리 및 다음 단계

IaC는 *재현 가능한 인프라*입니다. 다음 글에서는 *애플리케이션*의 재현성을 책임지는 컨테이너를 배웁니다.

<!-- toc:begin -->
- [DevOps란 무엇인가?](./01-what-is-devops.md)
- [CI 파이프라인](./02-ci-pipeline.md)
- [CD와 배포 전략](./03-cd-and-deployment.md)
- [환경 분리와 설정 관리](./04-environments-and-config.md)
- **Infrastructure as Code (현재 글)**
- 컨테이너와 빌드 (예정)
- 모니터링과 알림 (예정)
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [Terraform docs](https://developer.hashicorp.com/terraform)
- [Terraform AWS Modules](https://registry.terraform.io/namespaces/terraform-aws-modules)
- [Atlantis](https://www.runatlantis.io/)
- [HashiCorp — IaC](https://www.hashicorp.com/resources/what-is-infrastructure-as-code)

Tags: DevOps, IaC, Terraform, Cloud, Automation
