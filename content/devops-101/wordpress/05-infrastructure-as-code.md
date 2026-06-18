---
title: "바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code"
series: devops-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 만든 앱을 올릴 인프라도 코드로 관리할 수 있습니다. Terraform으로 클라우드 인프라를 재현 가능하게 만드는 IaC 기초를 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 5번째 글입니다.

AI 코딩 도구로 앱을 만들고 배포하다 보면 이런 상황이 생깁니다. AWS 콘솔에서 클릭해서 서버를 만들었는데, 나중에 같은 구성으로 새 환경을 만들려니 어떻게 설정했는지 기억이 안 납니다. 팀원이 실수로 데이터베이스 설정을 바꿨는데 언제 누가 바꿨는지 모릅니다. 인프라가 점점 복잡해지는데 문서는 항상 현실과 달라져 있습니다.

Infrastructure as Code(IaC)는 인프라를 콘솔 클릭이 아닌 코드로 정의하는 방법입니다. 서버, 네트워크, 데이터베이스 설정이 코드 파일로 남아 Git으로 관리됩니다. 변경 이력이 남고, PR 리뷰가 가능하고, 같은 코드로 여러 환경을 재현할 수 있습니다.

AI에게 "Terraform으로 AWS EC2 서버 만들어줘"라고 요청할 수 있습니다. 하지만 IaC의 핵심인 state 관리, plan/apply 흐름, 롤백 방법을 모르면 AI가 만들어준 코드를 안전하게 실행할 수 없습니다. 잘못된 `terraform apply` 한 번이 운영 환경을 망칠 수 있습니다.

> 인프라 변경도 코드처럼 리뷰하고 이력을 남겨야 합니다.

---

## 이 글에서 다룰 문제
- 콘솔 클릭으로 만든 인프라는 왜 재현하기 어려울까요?
- Terraform의 plan과 apply는 어떤 순서로 이해해야 할까요?
- state 파일이 왜 중요하고 왜 팀이 함께 관리해야 할까요?
- AI가 만든 Terraform 코드를 실행하기 전에 무엇을 확인해야 할까요?
- IaC를 잘못 쓰면 어떤 위험이 생길까요?

## IaC 도구 비교

| 도구 | 접근법 | 언어 | 추천 상황 |
|---|---|---|---|
| Terraform | 선언형 | HCL | 멀티 클라우드, 가장 범용적 |
| Pulumi | 선언형 | Python, TypeScript 등 | 기존 프로그래밍 언어 선호 |
| AWS CloudFormation | 선언형 | YAML/JSON | AWS 전용 환경 |
| Ansible | 절차형 | YAML | 서버 설정 관리 중심 |

바이브코딩 프로젝트에서 처음 IaC를 도입한다면 Terraform이 가장 문서가 풍부하고 커뮤니티도 큽니다. Python을 주로 쓴다면 Pulumi도 좋은 선택입니다.

## Terraform 기본 흐름: plan 먼저, apply는 나중에

```hcl
# main.tf
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "my-tf-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_s3_bucket" "app_logs" {
  bucket = "my-app-logs-${var.env}"
  tags = {
    Environment = var.env
    ManagedBy   = "terraform"
  }
}
```

```bash
terraform init    # provider 다운로드, state backend 초기화
terraform plan    # 무엇이 바뀔지 미리 확인 (반드시 먼저)
terraform apply   # 실제 인프라에 적용 (plan 확인 후)
```

`terraform plan`은 실제 인프라를 변경하지 않습니다. 무엇이 생성, 수정, 삭제될지 미리 보여줍니다. 이 단계를 건너뛰고 `apply`를 실행하면 예상치 못한 변경이 생길 수 있습니다.

## Before / After

**Before**: "AWS 콘솔에서 클릭해서 서버를 만들었다. 6개월 후에 같은 환경을 다시 만들어야 했는데 어떤 설정을 했는지 기억이 없었다. 결국 처음부터 다시 설정하느라 하루가 걸렸다."

**After**: "Terraform 코드가 Git에 있다. 새 환경이 필요하면 환경 변수만 바꿔서 `terraform apply`를 실행하면 된다. 변경 이력도 PR에 남아 있다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| plan 없이 apply 실행하는 실수 | 예상치 못한 리소스 삭제나 변경이 발생할 수 있음 | 반드시 `terraform plan` 먼저 읽고 확인 |
| state를 로컬에 두는 실수 | 팀원과 동시에 작업하면 state 충돌 발생 | S3 + DynamoDB 같은 원격 backend로 이동 |
| AI가 만든 코드를 확인 없이 apply하는 실수 | 의도치 않은 리소스 삭제 포함될 수 있음 | AI 생성 Terraform 코드는 plan 결과를 반드시 검토 |
| 콘솔에서 직접 인프라를 수정하는 실수 | Terraform state와 실제 인프라가 어긋나 drift 발생 | 모든 변경을 코드로만 수행 |
| production에 직접 apply하는 실수 | 실수 비용이 너무 큼 | dev → staging → production 순으로 단계 적용 |

## AI에게 IaC 관련 질문하는 팁

Terraform 코드를 AI에게 요청할 때 이 정보를 포함하면 안전한 코드를 받을 수 있습니다:

```
클라우드 제공자: [AWS, GCP, Azure]
만들고 싶은 리소스: [EC2, RDS, S3, ECS 등]
환경 구분: [dev, staging, production]
State 저장 방식: [로컬 / S3 + DynamoDB]
태그 정책: [Environment, Team, ManagedBy 등]
```

AI가 만든 Terraform 코드를 받았다면 `plan` 결과에서 반드시 확인할 것: 예상하지 못한 `destroy`가 포함되어 있지 않은지, 시크릿이 state에 평문으로 저장되지 않는지, 태그 정책이 적용되어 있는지.

## 운영 체크리스트

- [ ] 모든 인프라가 Terraform 코드로 정의되어 있습니다
- [ ] state가 원격 backend(S3 등)에 저장됩니다
- [ ] apply 전에 항상 plan 결과를 확인합니다
- [ ] 인프라 변경도 PR을 통해 리뷰됩니다
- [ ] production 적용에는 별도 승인 절차가 있습니다

## 처음 질문으로 돌아가기

"IaC가 어렵지 않나요? 그냥 콘솔에서 클릭하면 안 되나요?"

콘솔 클릭은 빠르지만 재현이 안 됩니다. 같은 인프라를 다시 만들거나, 팀원이 변경 이력을 보거나, 실수를 롤백하는 것이 모두 어렵습니다. IaC는 인프라를 코드처럼 다루는 방법입니다. AI가 Terraform 코드를 만들어줄 수 있지만, plan 결과를 읽고 판단하는 것은 사람의 몫입니다.

## 정리

IaC는 인프라를 재현 가능하고 리뷰 가능하게 만드는 방법입니다. Terraform의 핵심은 문법보다 plan → apply 흐름을 습관화하는 것입니다. 다음 글에서는 같은 재현성을 애플리케이션 실행 환경에 제공하는 컨테이너와 빌드를 다룹니다.

## 참고 자료
### 공식 문서
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform AWS Modules](https://registry.terraform.io/namespaces/terraform-aws-modules)
- [Atlantis — Terraform Pull Request Automation](https://www.runatlantis.io/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- **바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, IaC, Terraform
