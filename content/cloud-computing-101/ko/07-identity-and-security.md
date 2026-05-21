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

## 먼저 던지는 질문

- IAM 사용자, 그룹, 역할, 정책은 어떻게 구분할까요?
- 최소 권한 원칙은 왜 기본값이어야 할까요?
- MFA와 키 회전은 왜 운영 루틴이 되어야 할까요?

## 큰 그림

![Cloud Computing 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/07/07-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 7장 흐름 개요*

IAM은 '누가' 클라우드 리소스에 접근할 수 있는지를 제어합니다. 권한(Permission)은 구체적인 액션(예: s3:GetObject), 리소스(어느 S3 버킷), 조건(IP 범위, 시간)을 명시합니다. 역할(Role)은 권한의 집합이고, 사용자나 서비스가 역할을 맡습니다. 정책(Policy)은 역할에 붙는 권한 문서입니다.

> IAM은 기능 이름이 아니라, 어떤 경계에서 누가 무엇을 할 수 있는지 명확히 정하는 결정입니다.

## 왜 중요한가

대부분의 사고는 과도한 권한 하나에서 시작됩니다. `Action: *` 하나, Git에 올라간 키 하나, MFA가 빠진 관리자 계정 하나가 전체 시스템을 흔들 수 있습니다. 반대로 IAM이 단단하면 실수가 나더라도 영향 범위를 좁힐 수 있습니다.

클라우드 환경은 API 중심이기 때문에 권한 모델이 곧 운영 모델입니다. 누가 어떤 자원에 접근할 수 있는지 अस्पष्ट하면 자동화가 늘수록 위험도 함께 커집니다.

## 한눈에 보는 개념

사람은 사용자와 그룹으로 관리하는 경우가 많고, 애플리케이션은 역할을 통해 임시 자격 증명을 받는 구조가 일반적입니다. 정책은 이 둘에게 어떤 자원에 무엇을 할 수 있는지 정의합니다.

## 핵심 용어

- **User**: 사람 또는 장기 자격 증명을 가진 주체입니다.
- **Group**: 여러 사용자에게 같은 정책을 묶어 적용하는 단위입니다.
- **Role**: 임시 자격 증명을 발급받는 정체성입니다.
- **Policy**: 허용과 거부를 JSON으로 표현한 규칙입니다.
- **KMS**: 암호화 키를 중앙에서 관리하는 서비스입니다.

## Before / After

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

## 체크리스트

- [ ] 루트 계정 MFA가 활성화되어 있는가.
- [ ] 키 회전 일정이 있는가.
- [ ] 사용자 키보다 역할을 우선 사용하고 있는가.
- [ ] CloudTrail이 활성화되어 있는가.

## 연습 문제

1. 사용자와 역할의 근본적인 차이를 한 줄로 적어 보세요.
2. 최소 권한 S3 정책의 `Resource` 필드를 한 줄로 써 보세요.
3. 고객 관리형 KMS 키가 AWS 관리형 키보다 적합한 상황 하나를 설명해 보세요.

## 정리 및 다음 단계

권한 구성을 바로 세웠다면 이제 시스템에서 실제로 무슨 일이 일어나는지 관찰할 수 있어야 합니다. 다음 글에서는 Metrics, Logs, Traces를 다루는 Monitoring으로 넘어가겠습니다.

사용자가 나이고, 일반 개발자는 애플리케이션을 배포하고 로그를 읽을 수 있지만 IAM 정책은 수정할 수 없습니다. 이렇게 역할을 작게 나누면 보안 사고의 범위를 제한할 수 있습니다.

MFA는 암호 외에 추가 인증 요소(예: 핸드폰)를 요구합니다. 관리자 계정이나 프로덕션 배포 권한은 반드시 MFA로 보호해야 합니다.
  - 본문의 기준은 Identity와 Security를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
암호화 키 관리 전용 서비스(예: AWS KMS)를 쓰면 키 생성, 저장, 회전을 안전하게 자동화할 수 있습니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **MFA와 키 회전은 왜 운영 루틴이 되어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

## IAM 최소 권한 적용 예시

| 역할 | 허용 작업 | 금지/제한 포인트 |
| --- | --- | --- |
| app-runtime-role | S3 읽기, SQS 소비 | IAM 수정 불가 |
| ci-deploy-role | 배포 관련 서비스 갱신 | 프로덕션 DB 접근 불가 |
| analyst-role | Athena/로그 조회 | 리소스 생성 불가 |

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::my-app-prod/*"]
    },
    {
      "Effect": "Deny",
      "Action": ["s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::my-app-prod/*"]
    }
  ]
}
```



### 운영 리뷰 질문 세트

아래 질문은 설계 문서 리뷰와 장애 회고에서 반복적으로 사용할 수 있는 체크 질문입니다.

| 질문 | 확인 포인트 | 흔한 실패 |
| --- | --- | --- |
| 책임 경계가 명확한가 | 공급자/사용자 책임 문서화 | "누가 고칠지" 미정 상태 |
| 변경 영향이 예측 가능한가 | 롤백/격리 경로 존재 | 단일 경로 의존 |
| 비용 신호가 보이는가 | 태그/예산/알림 연동 | 비용 급증 사후 인지 |
| 보안 기준이 자동화되었는가 | 정책 코드화, 주기 점검 | 수동 예외 누적 |
| 복구 가능성이 검증되었는가 | 정기 복원 리허설 | 백업만 있고 복원 실패 |

이 질문 세트는 기술 스택과 무관하게 적용할 수 있습니다. 중요한 것은 문장으로 "대답할 수 있는가"가 아니라, 로그/정책/테스트로 "증명할 수 있는가"입니다.

### 팀 운영 계약 예시

```yaml
team_operating_contract:
  deploy:
    requires_review: true
    rollback_plan_required: true
  security:
    least_privilege_default: true
    mfa_for_privileged_actions: true
  reliability:
    monthly_recovery_drill: true
    incident_postmortem_required: true
  cost:
    budget_alert_thresholds: [50, 80, 100]
    untagged_resource_policy: deny
```

운영 계약을 명시하면 담당자가 바뀌어도 품질 기준이 유지됩니다. 클라우드의 핵심은 리소스를 빨리 만드는 능력이 아니라, 같은 품질을 반복해서 만드는 능력입니다. 따라서 이 문서와 같은 계약은 초기에 작게 시작해도 반드시 있어야 하며, 분기 단위로 업데이트하는 루틴을 두는 편이 안정적입니다.

### 장애/비용/보안을 함께 보는 회고 포맷

1. 무엇이 실패했는가를 한 문장으로 기록합니다.
2. 탐지 시점과 첫 대응 시점을 분 단위로 기록합니다.
3. 영향 범위(사용자 수, 금액, 데이터 범위)를 숫자로 기록합니다.
4. 재발 방지 항목을 자동화/문서/훈련으로 분류합니다.
5. 다음 점검 날짜를 지정하고 담당자를 명시합니다.

위 다섯 단계는 단순하지만 반복 효과가 큽니다. 특히 비용 이슈도 장애와 같은 수준으로 회고에 포함하면, 기술 선택과 운영 비용을 분리해서 보는 습관을 줄일 수 있습니다.



### 실무 적용 시나리오

다음 시나리오는 교육용 예시이지만, 실제 프로젝트에서 의사결정을 정리할 때 그대로 활용할 수 있습니다.

| 상황 | 선택 | 이유 | 검증 방법 |
| --- | --- | --- | --- |
| 신규 서비스 초기 론칭 | 단순한 기본 아키텍처 + 필수 가드레일 | 속도와 안정성의 균형 | 체크리스트 기반 사전 점검 |
| 트래픽 급증 이벤트 | 자동 확장 + 임계값 알림 강화 | 수동 대응 지연 방지 | 부하 테스트 + 알람 리허설 |
| 보안 감사 대응 | 권한 축소 + 로그 보존 정책 정리 | 증빙 가능성 확보 | 감사 항목 매핑 문서 |
| 비용 급증 발생 | 태그 누락/유휴 자원 우선 정리 | 즉시 효과가 큼 | 주간 비용 리포트 비교 |

시나리오 기반으로 운영하면 기술 논의가 추상적 취향 싸움으로 흐르지 않습니다. 각 선택에 대해 "왜 이 결정을 했는가"와 "어떻게 검증할 것인가"를 짝지어 기록하면, 팀이 커져도 의사결정 품질을 유지할 수 있습니다. 또한 운영 회고에서 같은 포맷을 재사용하면 변경 누락과 책임 공백을 줄일 수 있습니다.



### 빠른 점검 메모

운영 단계에서는 정답 하나보다 반복 가능한 점검 리듬이 더 중요합니다. 배포 전 점검, 주간 운영 점검, 월간 개선 회고를 분리해 기록하면 누락이 줄어듭니다. 특히 신규 팀원이 합류할 때는 문서의 완성도보다 문서의 최신성이 더 큰 가치를 만듭니다. 따라서 작은 변경이라도 근거와 검증 결과를 함께 남기는 습관이 필요합니다.



짧은 결론으로 정리하면, 운영 품질은 도구 선택 자체보다 기준의 일관성과 검증 습관에서 결정됩니다. 기준이 문서와 자동화로 남아 있어야 다음 변경에서도 같은 품질을 반복할 수 있습니다.

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
```

| 항목 | 최소 권한 구성 | 과도 권한 구성 |
| --- | --- | --- |
| 허용 범위 | 필요한 액션만 명시 | `*` 와일드카드 중심 |
| 사고 영향 범위 | 역할 단위로 제한 | 계정 전체로 확장 가능 |
| 감사 용이성 | 원인 추적 쉬움 | 원인 추적 어려움 |

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

Tags: Cloud, Security, IAM, AWS, Architecture
