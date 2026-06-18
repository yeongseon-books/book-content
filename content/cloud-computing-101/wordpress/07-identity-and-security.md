---
series: cloud-computing-101
episode: 7
title: "바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 클라우드
  - IAM
  - 보안
  - AWS
language: ko
---

# 바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security

이 글은 **바이브코딩을 위한 클라우드 컴퓨팅 기초** 시리즈의 7편입니다. AI가 만든 앱을 클라우드에 올리려면 보안 설정을 제대로 알아야 합니다. 10편에 걸쳐 클라우드의 핵심 개념을 바이브코딩 관점에서 정리합니다.

---

바이브코딩으로 AI 앱을 개발하다가 AWS 자격 증명을 실수로 GitHub에 push한 경험, 있으신가요? 그 키가 public repository에 올라가면 수십 분 안에 봇이 감지하고 AWS 계정을 탈취합니다. 피해가 가장 많은 시나리오 중 하나는 탈취된 계정으로 대규모 EC2 인스턴스를 띄워 비트코인을 채굴하는 것입니다. 청구서가 하루 만에 수십만 원이 되기도 합니다.

클라우드 보안 사고의 많은 출발점은 정교한 해킹이 아니라 과도한 권한과 방치된 키입니다.

> "IAM은 기능 이름이 아니라, 어떤 경계에서 누가 무엇을 할 수 있는지 명확히 정하는 결정입니다."

## 이 글에서 다룰 질문들

- IAM 사용자, 그룹, 역할, 정책은 어떻게 다른가요?
- AI 앱이 AWS 서비스를 사용할 때 키를 코드에 넣으면 왜 안 되나요?
- 최소 권한 원칙이란 무엇이고 AI 앱에 어떻게 적용하나요?
- API 키, DB 비밀번호를 안전하게 관리하는 방법은 무엇인가요?
- MFA는 언제 반드시 필요한가요?

---

## 바이브코딩 AI 앱의 가장 흔한 보안 실수

### Before: 키를 코드에 하드코딩

```python
import boto3

# 절대 이렇게 하면 안 됨!
s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",       # GitHub에 올라가면 탈취됨
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG"   # 수십 분 내 계정 해킹
)
```

### After: 역할(Role) 또는 환경 변수 사용

```python
import boto3
import os

# 방법 1: EC2/Lambda 역할 사용 (가장 권장)
# IAM 역할을 인스턴스에 붙이면 SDK가 자동으로 임시 자격 증명 사용
s3 = boto3.client("s3")  # 자격 증명 없어도 역할에서 자동 로드

# 방법 2: 환경 변수 (로컬 개발 시)
# .env 파일에 저장, .gitignore에 추가
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
s3_local = boto3.client("s3")  # 환경 변수에서 자동 로드

# 방법 3: Secrets Manager (프로덕션 비밀 관리)
def get_db_password() -> str:
    secrets = boto3.client("secretsmanager")
    response = secrets.get_secret_value(SecretId="prod/ai-app/db-password")
    return response["SecretString"]
```

---

## IAM 개념 한눈에 보기

| 개념 | 설명 | AI 앱 예시 |
| --- | --- | --- |
| 사용자(User) | 사람 또는 장기 키를 가진 주체 | 개발자 계정 |
| 역할(Role) | 임시 자격 증명을 발급받는 정체성 | AI 앱 서버 EC2 역할 |
| 정책(Policy) | 허용/거부 규칙 JSON | "S3 버킷만 읽기 허용" |
| 그룹(Group) | 정책을 여러 사용자에게 묶어 적용 | "개발팀" 그룹 |

---

## AI 앱을 위한 최소 권한 정책

```python
import boto3
import json

iam = boto3.client("iam")

# AI 앱에 필요한 최소 권한만 부여
ai_app_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3AppBucketOnly",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            # 앱 버킷만 허용, 다른 버킷은 접근 불가
            "Resource": "arn:aws:s3:::my-ai-app-bucket/*"
        },
        {
            "Sid": "CloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
        # s3:* 나 * 같은 와일드카드는 사용하지 않음
    ]
}

# 나쁜 예 (절대 이렇게 하지 말 것)
# bad_policy = {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}
```

---

## API 키와 비밀번호 관리: Secrets Manager vs 환경 변수

| 방법 | 적합한 상황 | 주의사항 |
| --- | --- | --- |
| IAM 역할 | EC2, Lambda, ECS 등 AWS 서비스 | 가장 권장, 키 없음 |
| Secrets Manager | DB 비밀번호, API 키 (자동 회전 필요) | 월 $0.40/비밀 + API 호출 |
| Parameter Store | 설정값, 간단한 비밀 | 무료(표준), 회전 직접 구현 |
| 환경 변수(.env) | 로컬 개발만 | .gitignore 필수, 프로덕션 비권장 |
| 코드 하드코딩 | 절대 안 됨 | 즉시 탈취 위험 |

```python
# OpenAI API 키를 Secrets Manager에서 가져오기
import boto3
import json

def get_openai_key() -> str:
    """Secrets Manager에서 OpenAI API 키 조회"""
    client = boto3.client("secretsmanager", region_name="ap-northeast-2")
    response = client.get_secret_value(SecretId="prod/ai-app/openai-key")
    secret = json.loads(response["SecretString"])
    return secret["OPENAI_API_KEY"]

# 사용
import openai
openai.api_key = get_openai_key()  # 코드에 키 없음
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| API 키를 코드에 하드코딩 | GitHub push 시 즉시 탈취 위험 | 환경 변수 또는 Secrets Manager |
| 루트 계정으로 일상 작업 | 전체 계정 권한으로 실수 가능 | IAM 사용자 생성 후 루트 잠금 |
| `Action: *` 과도한 권한 | 탈취 시 계정 전체 제어 가능 | 필요한 작업만 명시 |
| MFA 미설정 | 비밀번호 유출 시 계정 탈취 | 루트 및 관리자 계정에 MFA 필수 |
| 오래된 키 방치 | 유출 여부 모르고 계속 사용됨 | 90일마다 키 회전 또는 역할로 교체 |

---

## AI 팁: 바이브코딩과 보안

1. **`.gitignore` 먼저 설정**: 새 프로젝트 시작 시 `.env`, `*.pem`, `credentials` 파일을 gitignore에 추가하세요.
2. **IAM 역할 활용**: AI 앱 서버에 역할을 붙이면 키 관리가 필요 없어집니다. AI에게 "EC2에 S3 읽기 권한 IAM 역할 생성 Terraform 코드 작성해줘"라고 요청하세요.
3. **git-secrets 도구**: 실수로 키를 커밋하기 전에 차단해주는 도구입니다. 바이브코딩 환경에서도 꼭 설치하세요.
4. **Secrets Manager 자동화**: AI에게 "Secrets Manager에서 OpenAI 키 가져오는 Python 코드 작성해줘"라고 하면 바로 사용할 수 있는 코드를 만들어줍니다.

---

## 실전 체크리스트

- [ ] 루트 계정 MFA가 활성화되어 있다
- [ ] API 키가 코드나 GitHub에 없다
- [ ] AI 앱 서버에 IAM 역할이 붙어 있다 (키 대신)
- [ ] IAM 정책에 필요한 권한만 명시되어 있다 (`*` 없음)
- [ ] DB 비밀번호가 Secrets Manager에 저장되어 있다
- [ ] .env 파일이 .gitignore에 포함되어 있다

---

## 처음 질문으로 돌아가기

- **AI 앱이 AWS 서비스를 사용할 때 키를 코드에 넣으면 왜 안 되나요?**
  GitHub 등 코드 저장소에 올라가는 순간 봇이 수집해서 계정을 탈취합니다. EC2나 Lambda에 IAM 역할을 붙이면 키 없이도 AWS 서비스를 안전하게 사용할 수 있습니다.

- **최소 권한 원칙이란 무엇인가요?**
  AI 앱이 S3만 쓴다면 S3 권한만, 그것도 해당 버킷만 허용하는 것입니다. `Action: *`이나 `Resource: *`은 탈취 시 계정 전체를 내줍니다.

- **MFA는 언제 반드시 필요한가요?**
  루트 계정과 관리자 권한이 있는 모든 IAM 사용자에게 필수입니다. AI 앱 배포 권한이 있는 CI/CD 계정에도 권장됩니다.

---

## 정리

클라우드 보안에서 바이브코더가 가장 먼저 지켜야 할 세 가지는 루트 MFA 활성화, API 키를 코드에 넣지 않기, IAM 역할 우선 사용입니다. 이 세 가지만 지켜도 대부분의 보안 사고를 예방할 수 있습니다. 다음 글에서는 AI 앱이 정상적으로 동작하는지 감시하는 Monitoring을 다룹니다.

---

## 참고 자료

- [AWS IAM 사용자 가이드](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)
- [AWS IAM 모범 사례](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (1/10): Cloud Computing이란 무엇인가?
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (3/10): Region과 Availability Zone
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network
- **바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security (현재 글)**
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (8/10): Monitoring
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (9/10): Cost Management
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, 클라우드, IAM, 보안, AWS
