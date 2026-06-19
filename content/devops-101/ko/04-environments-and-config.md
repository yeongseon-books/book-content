---
series: devops-101
episode: 4
title: "DevOps 101 (4/10): 환경 분리와 설정 관리"
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
  - Configuration
  - Secrets
  - Environment
  - TwelveFactor
seo_description: 같은 빌드 산출물을 여러 환경에 안전하게 배포하는 설정 관리 원칙을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (4/10): 환경 분리와 설정 관리

환경별 설정 관리는 단순히 값을 저장하는 문제가 아닙니다. 보안 수준, 접근 통제, 회전 정책, 감사 로그가 모두 달라집니다.

이 글은 DevOps 101 시리즈의 네 번째 글입니다.

![DevOps 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/04/04-01-diagram.ko.png)
*DevOps 101 4장 흐름 개요*
> 환경 분리의 핵심은 기술 설정이 아니라, 각 환경의 위험과 검증 수준을 얼마나 명확히 정의하느냐입니다.

## 이 글에서 다룰 문제

- dev, stage, prod 환경을 분리하는 이유는 무엇일까요?
- 같은 코드베이스를 여러 환경에 배포하려면 무엇을 코드 밖으로 빼야 할까요?
- 환경변수와 시크릿은 어떻게 다르며 왜 따로 관리해야 할까요?
- Kubernetes에서 외부 시크릿 관리는 어떻게 할까요?

## 핵심 원칙: Build Once, Run Anywhere

데이터베이스 주소, 도메인, 외부 API 키는 환경마다 달라집니다. 이 값을 코드에 직접 박아 두면 dev에서는 되지만 stage에서 안 되고, prod에서는 다시 별도 빌드를 해야 합니다. 코드는 하나이고, 달라지는 것은 환경별 설정뿐이어야 합니다.

| 구분 | 예시 | 저장 방식 |
|------|------|----------|
| Config | DB URL, 서비스 도메인, 타임아웃 | 환경변수, ConfigMap |
| Secret | API 키, DB 패스워드, 인증서 | Secrets Manager, Vault |
| Feature Flag | 기능 활성화 여부 | AppConfig, LaunchDarkly |

## 환경 관리 도구 비교

| 도구 | 보안 수준 | 적합 규모 | 회전/접근통제 | 주의사항 |
|------|----------|----------|--------------|---------|
| dotenv (.env) | 낮음 (평문 파일) | 로컬 개발 | 없음 | .gitignore 필수, 프로덕션 부적합 |
| HashiCorp Vault | 높음 (암호화, 동적 시크릿) | 모든 규모 | 회전 지원, 세밀한 접근 제어 | 서버 운영 필요 |
| AWS Secrets Manager | 높음 (암호화, IAM 통합) | AWS 기반 팀 | 자동 회전 지원 | AWS 종속성, 비용 발생 |
| Kubernetes Secret | 중간 (base64 인코딩) | Kubernetes 환경 | 외부 도구와 연동 필요 | 단독 사용 시 한계 |

## Python 설정 로딩 예제

pydantic-settings를 사용하면 필수 값 누락 시 실행을 멈추고, 타입을 검증하며, 기본값을 투명하게 관리합니다.

```python
# config.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경변수로부터 로드되는 애플리케이션 설정"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    db_url: str = Field(..., description="Database connection URL")
    db_pool_size: int = Field(default=10, ge=1, le=100)

    # API
    api_key: str = Field(..., description="External API key")
    api_timeout: int = Field(default=30, ge=1)

    # Application
    environment: str = Field(default="dev")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["dev", "stage", "prod"]
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"


# 애플리케이션 시작 시 한 번만 초기화
settings = Settings()
```

## AWS Secrets Manager 연동

```python
import json
import boto3
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=None)
def get_secret(secret_name: str, region: str = "ap-northeast-2") -> dict[str, Any]:
    """AWS Secrets Manager에서 시크릿 조회 (캐싱 포함)"""
    client = boto3.client("secretsmanager", region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except client.exceptions.ResourceNotFoundException:
        raise ValueError(f"Secret '{secret_name}' not found")
    except client.exceptions.AccessDeniedException:
        raise PermissionError(f"No access to secret '{secret_name}'")

    if "SecretString" in response:
        return json.loads(response["SecretString"])
    else:
        import base64
        return {"value": base64.b64decode(response["SecretBinary"]).decode()}


class DatabaseConfig:
    """Secrets Manager 기반 DB 설정"""

    def __init__(self):
        secret = get_secret("prod/order-service/database")
        self.host = secret["host"]
        self.port = int(secret.get("port", 5432))
        self.dbname = secret["dbname"]
        self.username = secret["username"]
        self.password = secret["password"]

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}"
```

## Kubernetes ExternalSecrets로 시크릿 주입

External Secrets Operator를 사용하면 Vault나 AWS Secrets Manager의 값을 Kubernetes Secret으로 자동 동기화합니다.

```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: order-service-secrets
  namespace: production
spec:
  refreshInterval: 1h       # 1시간마다 최신화

  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore

  target:
    name: order-service-secrets   # 생성될 Kubernetes Secret 이름
    creationPolicy: Owner

  data:
    - secretKey: database-url     # Kubernetes Secret의 키
      remoteRef:
        key: prod/order-service/database    # AWS Secrets Manager 이름
        property: url               # JSON 내 필드
    - secretKey: api-key
      remoteRef:
        key: prod/order-service/api
        property: key
---
# deployment.yaml - Secret 마운트
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: registry.example.com/order-service:latest
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: order-service-secrets
                  key: database-url
            - name: API_KEY
              valueFrom:
                secretKeyRef:
                  name: order-service-secrets
                  key: api-key
```

## 환경별 설정 검증

배포 전에 설정이 올바른지 검증하는 스크립트를 CI/CD에 포함합니다.

```python
import os
import sys
import boto3
from typing import Optional


def validate_production_config() -> list[str]:
    """프로덕션 환경 설정 검증"""
    errors = []

    # 필수 환경변수 확인
    required_vars = [
        "DATABASE_URL",
        "API_KEY",
        "AWS_REGION",
        "ENVIRONMENT",
    ]
    for var in required_vars:
        if not os.environ.get(var):
            errors.append(f"필수 환경변수 없음: {var}")

    # 프로덕션에서는 debug 비활성화 필수
    if os.environ.get("DEBUG", "").lower() in ("true", "1", "yes"):
        errors.append("프로덕션에서 DEBUG=True는 허용되지 않습니다")

    # DB URL 형식 확인
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and not db_url.startswith(("postgresql://", "mysql://", "mongodb://")):
        errors.append(f"DATABASE_URL 형식 오류: {db_url[:20]}...")

    # Secrets Manager 접근 확인
    try:
        boto3.client("secretsmanager").list_secrets(MaxResults=1)
    except Exception as e:
        errors.append(f"Secrets Manager 접근 불가: {e}")

    return errors


if __name__ == "__main__":
    env = os.environ.get("ENVIRONMENT", "unknown")
    if env == "prod":
        errors = validate_production_config()
        if errors:
            print("설정 검증 실패:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        print("설정 검증 통과")
```

## 시크릿 로테이션 운영 런북

시크릿 만료 또는 보안 사고 발생 시 로테이션 절차:

1. 새 시크릿 생성:
```bash
aws secretsmanager rotate-secret \
  --secret-id prod/order-service/database \
  --rotation-lambda-arn arn:aws:lambda:ap-northeast-2:123456789012:function:rotate-db-password
```

2. 서비스 재시작 없이 적용되는지 확인 (캐시 무효화 필요한 경우):
```bash
# 파드 재시작으로 새 시크릿 로드
kubectl rollout restart deployment/order-service -n production
kubectl rollout status deployment/order-service -n production
```

3. 구 시크릿 폐기 확인:
```bash
aws secretsmanager describe-secret \
  --secret-id prod/order-service/database \
  --query 'RotationEnabled'
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 시크릿을 Git에 커밋 | GitHub 스캔 알림, 보안 사고 | git-secrets, gitleaks로 커밋 전 검사 |
| .env 파일을 프로덕션에 사용 | 평문 파일 노출 위험 | 프로덕션은 Secrets Manager 또는 Vault 필수 |
| 환경변수로 모든 설정 관리 | 재시작 없이 값 변경 불가, 타입 검증 없음 | pydantic-settings로 타입 검증 + 필수값 확인 |
| 시크릿을 이미지에 포함 | Docker Hub 이미지 분석으로 노출 | 런타임에 환경변수나 볼륨으로 주입 |
| 모든 환경이 같은 시크릿 공유 | dev 개발자가 prod DB에 접근 가능 | 환경별 별도 시크릿, IAM 정책으로 격리 |
| 로테이션 계획 없음 | 오래된 시크릿이 지속적으로 노출 위험 | 90일 이내 자동 로테이션 정책 설정 |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- **DevOps 101 (4/10): 환경 분리와 설정 관리 (현재 글)**
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [The Twelve-Factor App — Config](https://12factor.net/config)
- [HashiCorp Vault](https://developer.hashicorp.com/vault)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [External Secrets Operator](https://external-secrets.io/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
