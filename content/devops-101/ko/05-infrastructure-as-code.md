---
series: devops-101
episode: 5
title: "DevOps 101 (5/10): Infrastructure as Code"
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

# DevOps 101 (5/10): Infrastructure as Code

콘솔로 만든 인프라는 기억과 화면 기록에만 남기 쉽습니다. 같은 구성을 다른 리전이나 다른 계정에 다시 만들려면 사람이 다시 클릭해야 하고, 그 과정에서 조금씩 다른 값이 들어가면서 드리프트가 발생합니다.

이 글은 DevOps 101 시리즈의 다섯 번째 글입니다.

![DevOps 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/05/05-01-diagram.ko.png)
*DevOps 101 5장 흐름 개요*
> IaC의 핵심은 문법이 아니라, 인프라를 단일 출처(SSOT)로 관리하고 변경을 추적하는 문화입니다.

## 이 글에서 다룰 문제

- 콘솔에서 클릭해 만든 인프라는 왜 다른 환경에서 재현하기 어려울까요?
- IaC는 운영팀의 편의가 아니라 팀 전체의 변경 품질과 어떻게 연결될까요?
- Terraform의 기본 흐름은 plan과 apply를 중심으로 어떻게 이해하면 좋을까요?
- PR 기반 인프라 변경 워크플로는 어떻게 설계할까요?

## IaC 도구 비교

| 도구 | 접근법 | 언어 | 상태 관리 | 적합 상황 |
|------|--------|------|----------|----------|
| Terraform | 선언형 | HCL (특화 DSL) | 원격 state 파일 | 멀티 클라우드, 모듈 생태계 풍부 |
| Pulumi | 선언형 + 절차형 | Python, TypeScript, Go 등 | 클라우드 state 또는 자체 관리 | 기존 언어 사용 선호, 복잡한 로직 필요 |
| AWS CloudFormation | 선언형 | YAML/JSON | AWS 관리 | AWS 전용, AWS 통합 깊음 |
| Ansible | 절차형 | YAML + Jinja2 | 상태 관리 없음 (멱등성 기반) | 설정 관리 + 인프라 프로비저닝 |

## Terraform 기본 구조

```hcl
# versions.tf - 도구 버전 고정
terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "my-terraform-state-prod"
    key            = "order-service/terraform.tfstate"
    region         = "ap-northeast-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"  # 동시 apply 방지
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "order-service"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

```hcl
# variables.tf - 입력 변수 정의
variable "environment" {
  description = "배포 환경 (dev, stage, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment는 dev, stage, prod 중 하나여야 합니다."
  }
}

variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "service_name" {
  description = "서비스 이름"
  type        = string
  default     = "order-service"
}
```

```hcl
# main.tf - 핵심 리소스
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.service_name}-${var.environment}"
  cidr = "10.0.0.0/16"

  azs             = ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "prod"  # prod는 고가용성 NAT
}

resource "aws_security_group" "order_service" {
  name_prefix = "${var.service_name}-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

## PR 기반 인프라 변경 워크플로

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - "infrastructure/**"
  push:
    branches: [main]
    paths:
      - "infrastructure/**"

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  terraform-plan:
    name: Terraform Plan
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    defaults:
      run:
        working-directory: infrastructure/

    steps:
      - uses: actions/checkout@v4

      - name: AWS 인증 (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_TERRAFORM_ROLE_ARN }}
          aws-region: ap-northeast-2

      - name: Terraform 설치
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.7.0"

      - name: Terraform Init
        run: terraform init

      - name: Terraform 검증
        run: terraform validate

      - name: Terraform Format 검사
        run: terraform fmt -check -recursive

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan \
            -var="environment=prod" \
            -out=tfplan \
            -no-color 2>&1 | tee plan-output.txt
        continue-on-error: true

      - name: PR에 Plan 결과 코멘트
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const planOutput = fs.readFileSync('infrastructure/plan-output.txt', 'utf8');
            const truncated = planOutput.length > 60000
              ? planOutput.substring(0, 60000) + '\n... (잘림)'
              : planOutput;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan 결과\n\`\`\`\n${truncated}\n\`\`\``,
            });

      - name: Plan 실패 시 종료
        if: steps.plan.outcome == 'failure'
        run: exit 1

  terraform-apply:
    name: Terraform Apply
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production    # GitHub Environment 승인 게이트
    defaults:
      run:
        working-directory: infrastructure/

    steps:
      - uses: actions/checkout@v4

      - name: AWS 인증 (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_TERRAFORM_ROLE_ARN }}
          aws-region: ap-northeast-2

      - name: Terraform 설치
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.7.0"

      - name: Terraform Init
        run: terraform init

      - name: Terraform Apply
        run: |
          terraform apply \
            -var="environment=prod" \
            -auto-approve
```

## 상태 드리프트 감지

콘솔에서 수동으로 인프라를 변경하면 코드와 실제 상태가 달라집니다(드리프트). 정기적으로 드리프트를 감지하는 스케줄을 설정합니다.

```yaml
# 주간 드리프트 감지
  drift-detection:
    name: 드리프트 감지
    runs-on: ubuntu-latest
    # on: schedule의 cron에서 실행 (매주 월요일 오전 9시)

    steps:
      - uses: actions/checkout@v4

      - name: AWS 인증
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_TERRAFORM_ROLE_ARN }}
          aws-region: ap-northeast-2

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/

      - name: 드리프트 확인
        id: drift
        run: |
          OUTPUT=$(terraform plan -detailed-exitcode 2>&1 || true)
          EXIT_CODE=$?
          echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
          if [ $EXIT_CODE -eq 2 ]; then
            echo "드리프트 감지됨:"
            echo "$OUTPUT"
          fi
        working-directory: infrastructure/

      - name: 드리프트 알림
        if: steps.drift.outputs.exit_code == '2'
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -H 'Content-type: application/json' \
            --data '{"text": "⚠️ Terraform 드리프트 감지: 콘솔에서 수동 변경이 있을 수 있습니다."}'
```

## Terraform 모듈 구조

재사용 가능한 모듈을 만들어 환경별로 일관된 인프라를 구성합니다.

```
infrastructure/
├── modules/
│   ├── ecs-service/        # ECS 서비스 모듈
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── rds-postgres/       # RDS 모듈
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf         # 모듈 호출
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       └── terraform.tfvars
└── shared/                 # 공유 리소스 (VPC, ECR 등)
    └── main.tf
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| State 파일을 로컬에 저장 | 팀원 간 state 충돌, 인프라 이중 관리 | S3 + DynamoDB 원격 backend 필수 |
| Plan 없이 Apply | 예상치 못한 리소스 삭제 발생 | PR에서 plan 결과 반드시 리뷰 |
| 콘솔 변경 후 코드 미반영 | 드리프트 누적, 다음 apply에서 리셋됨 | 모든 변경은 코드 먼저, 콘솔 직접 변경 금지 |
| 모든 리소스를 하나의 파일에 관리 | 충돌 잦고 리뷰 어려움 | 기능별 파일 분리 (network.tf, ecs.tf, rds.tf) |
| 버전 미고정 | 프로바이더 업그레이드로 갑자기 깨짐 | `required_providers`에 버전 범위 명시 |
| 시크릿을 tfvars에 평문 저장 | Git에 시크릿 노출 | Secrets Manager 참조, tfvars는 gitignore |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- **DevOps 101 (5/10): Infrastructure as Code (현재 글)**
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [Terraform docs](https://developer.hashicorp.com/terraform)
- [Terraform AWS Modules](https://registry.terraform.io/namespaces/terraform-aws-modules)
- [Atlantis](https://www.runatlantis.io/)
- [HashiCorp — IaC](https://www.hashicorp.com/resources/what-is-infrastructure-as-code)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
