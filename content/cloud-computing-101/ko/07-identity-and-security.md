---
series: cloud-computing-101
episode: 7
title: "Cloud Computing 101 (7/10): Identity와 Security"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Cloud
  - Security
  - IAM
  - AWS
  - Architecture
seo_description: IAM 사용자, 역할, 정책, MFA, KMS의 기본 원칙을 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (7/10): Identity와 Security

클라우드 보안 사고의 많은 출발점은 해커의 정교한 공격보다 과도한 권한과 방치된 키에 있습니다. IAM 사용자와 역할, 정책, MFA, KMS를 제대로 이해하면 단일 실수의 폭발 반경을 크게 줄일 수 있습니다.

입문 단계에서는 보안을 "막는 기술"로만 보기 쉽습니다. 하지만 실제로는 누가 무엇을 언제 할 수 있는지 명확히 모델링하는 작업에 더 가깝습니다.

이 글은 Cloud Computing 101 시리즈의 7번째 글입니다.

여기서는 클라우드 보안을 최소 권한과 역할 기반 위임이라는 관점에서 정리하겠습니다.


![Cloud Computing 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/07/07-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 7장 흐름 개요*
> IAM은 기능 이름이 아니라, 어떤 경계에서 누가 무엇을 할 수 있는지 명확히 정하는 결정입니다.

## 먼저 던지는 질문

- IAM 사용자, 그룹, 역할, 정책은 어떻게 구분할까요?
- 최소 권한 원칙은 왜 기본값이어야 할까요?
- MFA와 키 회전은 왜 운영 루틴이 되어야 할까요?

## 왜 중요한가

대부분의 사고는 과도한 권한 하나에서 시작됩니다. `Action: *` 하나, Git에 올라간 키 하나, MFA가 빠진 관리자 계정 하나가 전체 시스템을 흔들 수 있습니다. 반대로 IAM이 단단하면 실수가 나더라도 영향 범위를 좁힐 수 있습니다.

클라우드 환경은 API 중심이기 때문에 권한 모델이 곧 운영 모델입니다. 누가 어떤 자원에 접근할 수 있는지 불분명하면 자동화가 늘수록 위험도 함께 커집니다.

## 인증과 인가의 차이

보안을 다루기 전에 인증(Authentication)과 인가(Authorization)를 구분해야 합니다. 둘은 자주 혼동되지만 역할이 다릅니다.

| 구분 | 인증(Authentication) | 인가(Authorization) |
| --- | --- | --- |
| 질문 | "당신은 누구입니까?" | "당신은 이것을 할 수 있습니까?" |
| 시점 | 요청 초기 | 인증 통과 후 |
| 수단 | 비밀번호, MFA, 인증서, SSO 토큰 | IAM 정책, RBAC, ABAC |
| 실패 응답 | 401 Unauthorized | 403 Forbidden |
| AWS 예시 | STS로 임시 자격 증명 발급 | IAM 정책 평가 엔진 |

인증이 통과해도 인가가 거부되면 작업은 실행되지 않습니다. 반대로 인가 규칙이 아무리 정교해도 인증이 뚫리면 의미가 없습니다. 두 계층 모두 견고해야 합니다.

## 핵심 용어

- **User**: 사람 또는 장기 자격 증명을 가진 주체입니다.
- **Group**: 여러 사용자에게 같은 정책을 묶어 적용하는 단위입니다.
- **Role**: 임시 자격 증명을 발급받는 정체성입니다.
- **Policy**: 허용과 거부를 JSON으로 표현한 규칙입니다.
- **KMS**: 암호화 키를 중앙에서 관리하는 서비스입니다.
- **MFA**: 비밀번호 외에 추가 인증 요소를 요구하는 메커니즘입니다.
- **STS**: Security Token Service, 임시 자격 증명을 발급합니다.
- **CloudTrail**: API 호출을 기록하는 감사 로그 서비스입니다.

## IAM 정책 구조 분석

IAM 정책은 JSON 문서입니다. 각 Statement에는 네 가지 핵심 요소가 있습니다.

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

| 요소 | 역할 | 주의점 |
| --- | --- | --- |
| Effect | Allow 또는 Deny | 명시적 Deny는 항상 Allow를 이깁니다 |
| Action | 허용/거부할 API 동작 | 와일드카드 `*`는 감사 시 가장 비싼 선택입니다 |
| Resource | 대상 ARN | 버킷과 버킷 내 객체는 별도 ARN입니다 |
| Condition | 추가 제한 조건 | IP, MFA, 시간, 태그 등을 조합할 수 있습니다 |

Condition을 활용하면 같은 Allow 정책이라도 "사무실 IP에서만", "MFA 인증 후에만", "특정 태그가 붙은 리소스에만"처럼 범위를 좁힐 수 있습니다.

## RBAC 설계 패턴

역할 기반 접근 제어(RBAC)는 개별 사용자가 아니라 역할 단위로 권한을 관리합니다. 팀 규모가 커질수록 개별 사용자에게 직접 정책을 붙이면 관리가 불가능해집니다.

| 역할 | 대상 | 허용 작업 | 금지/제한 |
| --- | --- | --- | --- |
| admin-role | 플랫폼 팀 | IAM 관리, 네트워크 설정 | 프로덕션 데이터 직접 접근 불가 |
| app-runtime-role | EC2/ECS 서비스 | S3 읽기, SQS 소비, DynamoDB CRUD | IAM 수정 불가, 다른 계정 접근 불가 |
| ci-deploy-role | CI/CD 파이프라인 | ECR push, ECS 서비스 갱신 | 프로덕션 DB 접근 불가 |
| analyst-role | 데이터 분석가 | Athena 쿼리, CloudWatch 로그 조회 | 리소스 생성/삭제 불가 |
| readonly-role | 신규 팀원, 감사자 | Describe/List/Get 계열만 | 모든 쓰기 작업 불가 |

RBAC 설계의 핵심은 "이 역할이 업무를 수행하는 데 필요한 최소한의 권한은 무엇인가"를 먼저 정의하고, 거기서 출발하는 것입니다.

## 적용 전후 비교
**Before**에서는 액세스 키를 코드에 하드코딩하고, 결국 유출 사고로 이어집니다.

**After**에서는 EC2 역할을 인스턴스에 붙여 임시 토큰을 자동으로 갱신합니다.

이 변화가 중요한 이유는 보안이 사람의 기억력에 덜 의존하게 만들기 때문입니다.

## 실습: 최소 권한 정책 만들기

### 1단계 — 클라이언트

```python
import boto3, json
iam = boto3.client("iam")
```

### 2단계 — 정책 문서

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

### 3단계 — 정책 생성

```python
def create_policy(name, doc):
    res = iam.create_policy(
        PolicyName=name, PolicyDocument=json.dumps(doc),
    )
    return res["Policy"]["Arn"]
```

### 4단계 — 역할 생성 + 신뢰 정책

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

### 5단계 — 부착

```python
def attach(role_name, policy_arn):
    iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
```

이 예제는 역할이 단순한 권한 묶음이 아니라는 점을 보여 줍니다. 역할에는 누가 그 역할을 사용할 수 있는지 정의하는 신뢰 정책과, 실제로 무엇을 할 수 있는지 정의하는 권한 정책이 모두 필요합니다.

## 이 코드에서 먼저 봐야 할 점

- 역할에는 신뢰 정책과 권한 정책 두 가지가 모두 필요합니다.
- `Resource` 범위는 가능한 한 좁게 잡아야 합니다.
- `Action`에 와일드카드를 남용하지 않는 편이 좋습니다.

## 이 예제를 실제로 검증하는 순서

IAM 예제는 정책을 생성하는 순간보다 실제로 어떤 신뢰 관계가 만들어졌는지 읽어 보는 순간에 더 많은 이해가 생깁니다. 역할과 정책 ARN이 생성되었는지, 그리고 역할이 어떤 주체에게만 열려 있는지 확인해 보세요.

```bash
aws iam get-role --role-name my-app-role
aws iam list-attached-role-policies --role-name my-app-role
```

**Expected output:**

- `AssumeRolePolicyDocument` 안에 `ec2.amazonaws.com` 신뢰 대상이 보여야 합니다.
- 연결된 정책 목록에 방금 만든 최소 권한 정책 ARN이 보여야 합니다.
- 이 두 결과를 함께 봐야 "누가 역할을 맡을 수 있는가"와 "맡은 뒤 무엇을 할 수 있는가"가 분리된다는 점이 명확해집니다.

### 자주 막히는 지점

- 권한 정책만 만들고 신뢰 정책을 빼먹으면 역할이 있어도 아무도 사용할 수 없습니다.
- `Action: *`는 당장은 편하지만 감사와 사고 대응 단계에서 가장 비싼 선택이 됩니다.
- 사람과 애플리케이션 모두 장기 액세스 키에 기대기 시작하면 회전과 폐기 절차가 급격히 어려워집니다.

## 크로스 계정 접근: AssumeRole

프로덕션과 개발 환경을 별도 AWS 계정으로 분리하면 폭발 반경을 줄일 수 있습니다. 이때 크로스 계정 접근은 AssumeRole로 구현합니다.

```bash
# 개발 계정에서 프로덕션 계정의 역할을 임시로 맡기
aws sts assume-role \
  --role-arn arn:aws:iam::111122223333:role/prod-readonly \
  --role-session-name cross-account-audit \
  --duration-seconds 3600
```

Python에서도 동일한 패턴을 사용합니다.

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

크로스 계정 접근이 동작하려면 두 가지가 맞아야 합니다. 대상 계정의 역할 신뢰 정책에 호출 계정이 허용되어 있어야 하고, 호출 계정의 사용자/역할에 `sts:AssumeRole` 권한이 있어야 합니다.

## MFA 강제 적용

관리자 계정이나 프로덕션 배포 권한은 반드시 MFA로 보호해야 합니다.

```bash
# 가상 MFA 디바이스 생성
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name admin-mfa \
  --outfile /tmp/qr.png \
  --bootstrap-method QRCodePNG

# MFA 활성화 (TOTP 코드 2개 필요)
aws iam enable-mfa-device \
  --user-name admin-user \
  --serial-number arn:aws:iam::123456789012:mfa/admin-mfa \
  --authentication-code1 123456 \
  --authentication-code2 789012
```

MFA를 강제하는 정책은 Condition 블록으로 구현합니다.

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

이 정책을 그룹에 붙이면 MFA 인증 없이는 어떤 작업도 수행할 수 없습니다.

## 보안 감사 체크리스트와 CLI 명령

운영 중인 계정의 보안 상태를 정기적으로 점검해야 합니다. 아래는 자주 사용하는 감사 명령입니다.

```bash
# 90일 이상 사용하지 않은 액세스 키 찾기
aws iam generate-credential-report
aws iam get-credential-report --output text --query Content | \
  base64 -d | cut -d',' -f1,9,11 | grep -v "N/A"

# 과도한 권한 정책 탐지: AdministratorAccess가 붙은 사용자
aws iam list-entities-for-policy \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# MFA가 없는 사용자 목록
aws iam list-users --query 'Users[].UserName' --output text | \
  xargs -I{} sh -c \
  'aws iam list-mfa-devices --user-name {} --query "MFADevices" --output text | grep -q "." || echo "No MFA: {}"'

# 사용하지 않는 역할 탐지 (최근 사용 날짜 확인)
aws iam list-roles --query 'Roles[].RoleName' --output text | \
  xargs -I{} aws iam get-role --role-name {} \
  --query 'Role.{Name:RoleName,LastUsed:RoleLastUsed.LastUsedDate}'
```

| 점검 항목 | 빈도 | 위험도 |
| --- | --- | --- |
| 미사용 액세스 키 비활성화 | 주 1회 | 높음 |
| MFA 미적용 사용자 제거 | 주 1회 | 높음 |
| AdministratorAccess 사용자 수 확인 | 월 1회 | 중간 |
| 미사용 역할 정리 | 월 1회 | 중간 |
| CloudTrail 활성화 여부 | 분기 1회 | 높음 |

## 암호화: 저장 시, 전송 중, 클라이언트 측

데이터 보호는 세 계층에서 이루어집니다.

| 구분 | 저장 시(at-rest) | 전송 중(in-transit) | 클라이언트 측(client-side) |
| --- | --- | --- | --- |
| 대상 | 디스크, S3, RDS | 네트워크 구간 | 애플리케이션 메모리 |
| 수단 | AES-256, KMS | TLS 1.2+ | 앱이 직접 암/복호화 |
| 키 관리 | KMS 또는 서비스 기본키 | 인증서(ACM) | 앱이 키를 보유 |
| AWS 예시 | S3 SSE-KMS, EBS 암호화 | ALB HTTPS, RDS SSL | S3 client-side encryption |
| 장점 | 투명, 성능 영향 적음 | 도청 방지 | 서비스 제공자도 평문 못 봄 |
| 단점 | 서비스 제공자가 키 접근 가능 | 인증서 관리 필요 | 앱 복잡도 증가 |

KMS를 사용하면 키 생성, 회전, 폐기를 자동화할 수 있습니다. 고객 관리형 키(CMK)는 키 정책으로 접근을 세밀하게 제어할 수 있고, 키 사용 로그가 CloudTrail에 기록됩니다.

```bash
# KMS 키 생성
aws kms create-key --description "my-app encryption key"

# 자동 회전 활성화 (1년 주기)
aws kms enable-key-rotation --key-id <key-id>

# 키 상태 확인
aws kms describe-key --key-id <key-id> \
  --query 'KeyMetadata.{State:KeyState,Rotation:KeyRotationEnabled}'
```

## 비밀 관리: Secrets Manager vs Parameter Store

애플리케이션이 사용하는 DB 비밀번호, API 키, 인증서 같은 민감 정보는 코드에 포함하면 안 됩니다.

| 비교 항목 | Secrets Manager | Parameter Store (SecureString) |
| --- | --- | --- |
| 자동 회전 | 내장 (Lambda 기반) | 직접 구현 필요 |
| 비용 | 비밀당 월 $0.40 + API 호출 | 표준 파라미터 무료 |
| 크기 제한 | 64KB | 8KB (고급: 8KB) |
| 크로스 계정 공유 | 리소스 정책으로 가능 | 제한적 |
| 적합한 용도 | DB 자격 증명, 자동 회전 필요 | 설정값, 비용 민감 환경 |

```python
import boto3

secrets = boto3.client("secretsmanager")

# 비밀 조회
response = secrets.get_secret_value(SecretId="my-app/db-password")
password = response["SecretString"]

# Parameter Store 조회
ssm = boto3.client("ssm")
param = ssm.get_parameter(Name="/my-app/api-key", WithDecryption=True)
api_key = param["Parameter"]["Value"]
```

두 서비스 모두 KMS로 암호화되며 IAM 정책으로 접근을 제어합니다. 자동 회전이 필요한 DB 자격 증명은 Secrets Manager, 단순 설정값은 Parameter Store가 일반적인 선택입니다.

## 사용자와 역할은 실무에서 어떻게 다를까

사용자는 사람 또는 장기 자격 증명을 가진 주체에 가깝습니다. 역할은 애플리케이션이나 서비스가 필요할 때 임시 자격 증명을 받아 쓰도록 만드는 방식에 가깝습니다. 그래서 실무에서는 사용자 키보다 역할을 더 선호합니다.

장기 키는 회전과 보관 부담이 크고 유출 시 영향이 길게 남습니다. 반면 역할 기반 임시 토큰은 만료되며, 자동화와 결합하기도 더 쉽습니다. 보안팀이 아니라 개발팀에게도 역할이 중요한 이유가 여기에 있습니다.

## 자주 하는 실수 5가지

1. `Action: *`처럼 권한을 과도하게 부여합니다.
2. 액세스 키를 Git에 커밋합니다.
3. 루트 계정으로 일상 작업을 처리합니다.
4. MFA를 적용하지 않습니다.
5. 키 회전 정책이 없습니다.

## 실무에서는 이렇게 생각합니다

- 최소 권한은 옵션이 아니라 기본값입니다.
- 가능하면 역할을 우선 사용하고, 사용자 키는 예외로 취급합니다.
- 모든 키에는 회전 일정이 있어야 합니다.
- 감사 로그는 기본적으로 켜 두는 편이 맞습니다.
- `prod`와 `dev`는 가능하면 다른 계정으로 분리합니다.

## IAM 운영 검증과 멀티클라우드 명령 예시

정책을 작성하는 것만으로는 충분하지 않습니다. 실제 계정에서 권한이 기대한 범위로 제한되는지 확인해야 합니다. 아래 명령은 AWS, Azure, Google Cloud에서 정체성과 권한 정보를 빠르게 점검할 때 자주 사용합니다.

```bash
# AWS: 현재 호출 주체와 역할 정책 확인
aws sts get-caller-identity
aws iam list-attached-role-policies --role-name my-app-role
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/my-app-role \
  --action-names s3:GetObject s3:DeleteObject \
  --resource-arns arn:aws:s3:::my-app-prod/example.txt

# Azure: 역할 할당 점검
az role assignment list --assignee <principal-id> --all

# Google Cloud: 프로젝트 IAM 바인딩 점검
gcloud projects get-iam-policy my-gcp-project --format=json
```

`simulate-principal-policy`는 정책을 실제로 적용하기 전에 특정 액션이 허용되는지 미리 테스트할 수 있어서, 최소 권한 정책을 점진적으로 조여 갈 때 유용합니다.

## IaC로 IAM 관리하기

IAM 정책을 콘솔에서 수동으로 관리하면 변경 이력 추적이 어렵습니다. Terraform 같은 IaC 도구로 정책을 코드화하면 리뷰, 버전 관리, 롤백이 가능합니다.

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

IaC로 관리하면 PR 리뷰 과정에서 권한 변경을 동료가 확인할 수 있고, `terraform plan`으로 적용 전에 변경 범위를 미리 볼 수 있습니다.

## 최소 권한 vs 과도 권한 비교

| 항목 | 최소 권한 구성 | 과도 권한 구성 |
| --- | --- | --- |
| 허용 범위 | 필요한 액션만 명시 | `*` 와일드카드 중심 |
| 사고 영향 범위 | 역할 단위로 제한 | 계정 전체로 확장 가능 |
| 감사 용이성 | 원인 추적 쉬움 | 원인 추적 어려움 |
| 초기 설정 비용 | 높음 (정밀 설계 필요) | 낮음 (일단 전체 허용) |
| 장기 운영 비용 | 낮음 (사고 빈도 감소) | 높음 (사고 대응 비용) |

## 서비스 제어 정책(SCP)과 권한 경계

AWS Organizations를 사용하면 조직 단위(OU)에 서비스 제어 정책(SCP)을 적용할 수 있습니다. SCP는 계정 내 모든 IAM 엔티티가 가질 수 있는 권한의 상한선을 정합니다.

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

SCP가 Deny하면 계정 내 어떤 IAM 정책이 Allow하더라도 해당 작업은 실행되지 않습니다. 이 구조 덕분에 개별 계정 관리자가 실수로 감사 로그를 끄거나, 조직을 이탈하는 상황을 방지할 수 있습니다.

Permission Boundary는 비슷한 개념을 개별 역할/사용자 수준에서 적용합니다. 개발자에게 IAM 역할 생성 권한을 줘야 하지만 본인보다 높은 권한을 가진 역할을 만들지 못하게 제한할 때 유용합니다.

```bash
# Permission Boundary 설정
aws iam put-role-permissions-boundary \
  --role-name developer-created-role \
  --permissions-boundary arn:aws:iam::123456789012:policy/BoundaryPolicy
```

| 메커니즘 | 적용 대상 | 용도 |
| --- | --- | --- |
| SCP | 조직/OU/계정 | 계정 전체의 권한 상한선 |
| Permission Boundary | 개별 역할/사용자 | 위임된 관리자가 만드는 역할의 권한 상한선 |
| IAM Policy | 개별 역할/사용자 | 실제 허용/거부할 작업 명세 |

세 계층이 모두 Allow일 때만 작업이 실행됩니다. 이 교차 평가 모델을 이해하면 "정책을 붙였는데 왜 거부되는지" 디버깅할 때 혼란이 줄어듭니다.
## 체크리스트

- [ ] 루트 계정 MFA가 활성화되어 있는가.
- [ ] 키 회전 일정이 있는가.
- [ ] 사용자 키보다 역할을 우선 사용하고 있는가.
- [ ] CloudTrail이 활성화되어 있는가.
- [ ] Condition 블록으로 정책 범위를 좁혔는가.
- [ ] 크로스 계정 접근에 AssumeRole을 사용하는가.
- [ ] 비밀 정보가 코드가 아닌 Secrets Manager/Parameter Store에 있는가.

## 연습 문제

1. 사용자와 역할의 근본적인 차이를 한 줄로 적어 보세요.
2. 최소 권한 S3 정책의 `Resource` 필드를 한 줄로 써 보세요.
3. 고객 관리형 KMS 키가 AWS 관리형 키보다 적합한 상황 하나를 설명해 보세요.
4. MFA 강제 정책에서 Condition 블록이 왜 `BoolIfExists`를 사용하는지 설명해 보세요.
5. Secrets Manager와 Parameter Store 중 DB 비밀번호에 더 적합한 것을 고르고 이유를 써 보세요.

## 처음 질문으로 돌아가기

- **IAM 사용자, 그룹, 역할, 정책은 어떻게 구분할까요?**
  - 사용자는 장기 자격 증명을 가진 주체, 그룹은 사용자를 묶는 단위, 역할은 임시 자격 증명을 발급받는 정체성, 정책은 이들에게 붙는 JSON 권한 문서입니다.
- **최소 권한 원칙은 왜 기본값이어야 할까요?**
  - 과도한 권한은 사고 영향 범위를 계정 전체로 확장시키고, 감사를 어렵게 만들며, 장기 운영 비용을 높입니다. 처음부터 좁게 시작해서 필요할 때 넓히는 것이 반대보다 항상 쉽습니다.
- **MFA와 키 회전은 왜 운영 루틴이 되어야 할까요?**
  - MFA는 자격 증명 유출의 영향을 차단하고, 키 회전은 유출된 키의 유효 기간을 제한합니다. 둘 다 일회성이 아니라 주기적으로 검증해야 효과가 유지됩니다.

## 정리 및 다음 단계

권한 구성을 바로 세웠다면 이제 시스템에서 실제로 무슨 일이 일어나는지 관찰할 수 있어야 합니다. 다음 글에서는 Metrics, Logs, Traces를 다루는 Monitoring으로 넘어가겠습니다.

텍스트 아키텍처 다이어그램:
`Developer -> SSO/MFA -> AssumeRole -> Temporary Credential -> API Call -> CloudTrail Audit`

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- **Identity와 Security (현재 글)**
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [AWS IAM user guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, Security, IAM, AWS, Architecture
