---
series: devops-101
episode: 5
title: Infrastructure as Code
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - IaC
  - Terraform
  - Cloud
  - Automation
seo_description: Terraform으로 인프라를 코드화해 재현성과 리뷰 가능성을 확보하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# Infrastructure as Code

이 글은 DevOps 101 시리즈의 다섯 번째 글입니다.

## 이 글에서 다룰 문제

- 콘솔에서 클릭해 만든 인프라는 왜 다른 환경에서 재현하기 어려울까요?
- IaC는 운영팀의 편의가 아니라 팀 전체의 변경 품질과 어떻게 연결될까요?
- Terraform의 기본 흐름은 plan과 apply를 중심으로 어떻게 이해하면 좋을까요?
- state 파일은 무엇이며 왜 원격 백엔드에서 관리해야 할까요?
- IaC를 도입하고도 실무에서 자주 생기는 함정은 무엇일까요?

> **멘탈 모델**: IaC는 인프라를 코드처럼 다루게 만들어, 누가 언제 무엇을 바꿨는지 기록하고 검토하고 재현할 수 있게 합니다. 결국 핵심은 클라우드를 잘 클릭하는 것이 아니라, 인프라 변경을 소프트웨어 변경처럼 다루는 데 있습니다.

## 왜 중요한가

콘솔로 만든 인프라는 기억과 화면 기록에만 남기 쉽습니다. 같은 구성을 다른 리전이나 다른 계정에 다시 만들려면 사람이 다시 클릭해야 하고, 그 과정에서 조금씩 다른 값이 들어가면서 드리프트가 발생합니다.

IaC는 이 문제를 구조적으로 줄입니다. 인프라를 코드로 정의하면 변경 이력이 남고, PR 리뷰가 가능해지고, 같은 정의를 여러 환경에 반복 적용할 수 있습니다.

> 코드는 단일 출처의 진실(SSOT)이어야 합니다.

## 한눈에 보는 개념

![한눈에 보는 개념](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/05/05-01-diagram.ko.png)

*한눈에 보는 개념*

이 흐름의 의미는 단순합니다. 먼저 코드로 정의하고, 변경 결과를 눈으로 확인한 뒤, 실제 클라우드에 반영하고, 그 결과를 state에 기록합니다.

## 핵심 용어

- **IaC**: 인프라를 코드로 정의하고 관리하는 방식입니다.
- **Provider**: AWS, GCP, Azure 같은 클라우드 API 어댑터입니다.
- **Resource**: 인스턴스, 버킷 같은 생성 단위입니다.
- **State**: 현재 실제 인프라 상태를 기록한 파일입니다.
- **Module**: 반복해서 재사용할 수 있는 인프라 묶음입니다.

이 용어들을 이해하면 Terraform 문법보다 먼저 운영 원리가 보입니다. 특히 state를 이해하지 못하면 plan과 apply의 의미도 반쯤만 이해하게 됩니다.

## Before/After

**Before (console clicks)**

```text
- No record of *who* created what *when*
- Replicating to another region means *starting over*
- No change history
```

이 구조에서는 운영 지식이 문서와 사람 기억에 분산됩니다. 같은 서버를 하나 더 만들거나 태그 정책을 통일하는 일도 매번 손으로 다시 해야 합니다.

**After (Terraform)**

```hcl
# main.tf
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs"
  tags   = { Env = "prod" }
}
```

코드화가 되면 인프라 변경도 코드 리뷰와 이력 추적의 대상이 됩니다. 그 순간부터 인프라는 개인 노하우가 아니라 팀 자산이 됩니다.

## Terraform으로 시작하는 5단계

### 1단계 - Provider 정의

어떤 클라우드와 어떤 버전을 대상으로 할지 먼저 명시해야 합니다. 이는 단순한 문법이 아니라 실행 환경을 고정하는 선언입니다.

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
provider "aws" { region = "us-east-1" }
```

### 2단계 - Resource 작성

이제 실제로 만들고 싶은 인프라를 코드로 표현합니다. 중요한 점은 사람 설명이 아니라 선언형 코드로 남긴다는 사실입니다.

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs-${var.env}"
}
```

### 3단계 - plan으로 변경 확인

IaC에서 가장 중요한 습관 중 하나는 apply 전에 plan을 읽는 것입니다. 눈으로 변경 내용을 확인하지 않고 바로 반영하면 자동화가 아니라 자동 사고가 됩니다.

```bash
terraform init
terraform plan
# Plan: 1 to add, 0 to change, 0 to destroy.
```

### 4단계 - apply

apply는 실제 클라우드를 변경하는 순간입니다. 그래서 더더욱 plan 리뷰와 실행 권한, 환경 분리가 함께 설계돼야 합니다.

```bash
terraform apply
# enters yes to actually create
```

### 5단계 - module로 재사용

환경마다 비슷한 인프라를 반복해야 한다면 모듈화가 필요합니다. 좋은 모듈은 팀 표준을 코드 수준에서 강제합니다.

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  cidr    = "10.0.0.0/16"
}
```

## 원격 state와 잠금은 왜 먼저 갖춰야 할까

Terraform을 혼자 연습할 때는 로컬 state도 얼핏 괜찮아 보입니다. 하지만 팀이 둘만 되어도 state 저장 위치와 잠금이 곧 운영 이슈가 됩니다. 한 사람은 `apply` 중인데 다른 사람도 같은 시점에 `plan`이나 `apply`를 돌리면, state 충돌과 잘못된 diff가 빠르게 쌓입니다.

그래서 실무에서는 리소스를 늘리기보다 먼저 원격 state와 locking을 잡습니다. AWS 예시라면 S3 + DynamoDB 조합이 가장 흔합니다.

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "network/prod.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

이 구성의 핵심은 저장 위치보다 팀 동시성 제어입니다. 잠금이 없으면 plan 결과를 믿기 어려워지고, 결국 IaC가 오히려 더 위험한 자동화가 됩니다.

## 드리프트를 찾는 확인 절차

IaC를 써도 콘솔 수동 변경이 완전히 사라지지는 않습니다. 그래서 운영팀은 plan을 단순 생성 단계로 보지 않고, 실제 상태와 코드가 어긋났는지 감시하는 드리프트 점검 절차로도 사용합니다.

```bash
terraform plan -detailed-exitcode
# 0 = no changes
# 2 = drift or intentional change detected
# 1 = error
```

이 명령을 PR 검증이나 야간 점검에 넣어 두면 "누가 콘솔에서 손댔는지"를 늦지 않게 발견할 수 있습니다. IaC의 가치는 선언형 문법보다 이런 반복 검증 루프에서 더 크게 드러납니다.

## 이 코드에서 먼저 봐야 할 점

- apply 전에 plan을 보고 변경을 시각적으로 검토해야 합니다.
- state는 로컬이 아니라 원격 백엔드에 있어야 합니다.
- 모듈은 환경 차이를 변수로만 남기게 해 줍니다.

IaC의 운영 품질은 문법을 얼마나 아느냐보다, 변경을 얼마나 안전하게 검토하고 공유할 수 있느냐에서 갈립니다.

## 자주 하는 실수 5가지

1. **state를 로컬에 두는 실수**입니다. 팀 협업 충돌과 유실 위험이 커집니다.
2. **state에 시크릿을 평문으로 남기는 실수**입니다. 백엔드 암호화와 접근 통제가 필수입니다.
3. **콘솔에서 수동 변경하는 실수**입니다. 그 순간 코드와 실제 인프라가 어긋나기 시작합니다.
4. **apply를 수동으로만 돌리는 실수**입니다. 오타와 사고 가능성이 커집니다.
5. **production에 destroy를 직접 치는 실수**입니다. 환경 분리와 승인 게이트가 반드시 필요합니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 Terraform Cloud나 Atlantis로 PR 기반 plan/apply를 자동화합니다. 인프라 변경도 애플리케이션 코드와 같은 수준으로 리뷰하고 승인하는 문화가 자리 잡습니다.

작은 팀이라면 먼저 원격 state, plan 리뷰, 환경별 변수 분리 세 가지부터 갖추는 편이 좋습니다. 그 세 가지가 IaC의 재현성과 안전성을 대부분 결정합니다.

## 시니어 엔지니어는 이렇게 봅니다

- 콘솔은 읽기 전용에 가깝게 다뤄야 합니다.
- state는 백업과 locking이 필수입니다.
- 모듈은 팀 표준을 강제하는 도구입니다.
- PR에서 plan diff는 핵심 리뷰 정보입니다.
- 태그 정책은 비용과 소유권 추적의 기본입니다.

## 체크리스트

- [ ] 모든 인프라가 코드로 정의되어 있습니다.
- [ ] state가 원격 백엔드에 저장됩니다.
- [ ] PR마다 plan 결과를 확인할 수 있습니다.
- [ ] 태그 정책이 적용됩니다.

## 연습 문제

1. Terraform으로 S3 버킷 하나를 직접 만들어 보세요.
2. 변수로 환경을 나눠 dev/prod에 같은 코드를 적용해 보세요.
3. S3 + DynamoDB 조합으로 원격 state를 구성해 보세요.

## 정리 및 다음 단계

IaC는 재현 가능한 인프라를 만드는 방법입니다. 다음 글에서는 같은 재현성을 애플리케이션 실행 환경에 제공하는 컨테이너와 빌드를 다룹니다.

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
