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

이 글은 DevOps 101 시리즈의 네 번째 글입니다.

![DevOps 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/04/04-01-diagram.ko.png)
*DevOps 101 4장 흐름 개요*
> 환경 분리의 핵심은 기술 설정이 아니라, 각 환경의 위험과 검증 수준을 얼마나 명확히 정의하느냐입니다.

## 먼저 던지는 질문

- dev, stage, prod 환경을 분리하는 이유는 무엇일까요?
- 같은 코드베이스를 여러 환경에 배포하려면 무엇을 코드 밖으로 빼야 할까요?
- 환경변수와 시크릿은 어떻게 다르며 왜 따로 관리해야 할까요?

## 왜 중요한가

데이터베이스 주소, 도메인, 외부 API 키는 환경마다 달라집니다. 이 값을 코드에 직접 박아 두면 dev에서는 되지만 stage에서 안 되고, prod에서는 다시 별도 빌드를 해야 하는 식으로 운영 복잡도가 빠르게 커집니다.

설정 관리는 단순히 값을 숨기는 문제가 아닙니다. 같은 산출물을 서로 다른 환경에 자신 있게 재사용할 수 있는가의 문제입니다. 이 원칙이 무너지면 배포 안정성과 재현성도 함께 무너집니다.

> Build once, run anywhere.

## 한눈에 보는 개념

핵심은 간단합니다. 코드는 하나이고, 달라지는 것은 환경별 설정뿐입니다. 같은 빌드 산출물이 dev, stage, prod에 각각 다른 설정을 주입받아 실행돼야 합니다.

## 핵심 용어

- **Environment**: dev, stage, prod처럼 실행 문맥이 다른 환경입니다.
- **Config**: 데이터베이스 URL, 도메인처럼 환경마다 달라지는 값입니다.
- **Secret**: API 키, 비밀번호처럼 민감한 값입니다.
- **.env**: 주로 로컬 개발에 쓰는 간단한 환경 설정 파일입니다.
- **Secrets manager**: Vault, AWS Secrets Manager처럼 암호화된 시크릿 저장소입니다.

같은 설정이라도 민감도와 수명 주기가 다릅니다. 그래서 단순한 환경변수와 시크릿 저장소를 같은 것으로 취급하면 운영 사고로 이어지기 쉽습니다.

## 환경 관리 도구 비교

환경별 설정 관리는 단순히 값을 저장하는 문제가 아닙니다. 보안 수준, 접근 통제, 회전 정책, 감사 로그가 모두 달라집니다. 아래 표는 대표적인 도구를 비교합니다.

| 도구 | 보안 수준 | 적합 규모 | 회전/접근통제 | 주의사항 |
|---|---|---|---|---|
| dotenv (.env) | 낮음 (평문 파일) | 로컬 개발 | 없음 | .gitignore 필수, 프로덕션 부적합 |
| HashiCorp Vault | 높음 (암호화, 동적 시크릿) | 모든 규모 | 회전 지원, 세밀한 접근 제어 | 서버 운영 필요, 학습 곡선 있음 |
| AWS Secrets Manager | 높음 (암호화, IAM 통합) | AWS 기반 팀 | 자동 회전 지원 | AWS 종속성, 비용 발생 |
| Kubernetes ConfigMap/Secret | 중간 (base64 인코딩) | Kubernetes 환경 | 외부 도구와 연동 필요 | Secret은 암호화 필수, 단독 사용 시 한계 |

대부분 팀은 로컬에서는 dotenv, 프로덕션에서는 Vault 또는 클라우드 기반 Secrets Manager를 선택합니다. 중요한 것은 하나의 도구로 모든 환경을 커버하려고 하지 말고, 환경의 보안 요구사항에 맞는 도구를 고르는 것입니다.

## 파이썬 설정 로딩 예제

설정 관리의 핀은 단순히 값을 읽는 것이 아니라, 필수 값이 빠졌을 때 실행을 멈추고, 타입을 검증하며, 기본값을 투명하게 관리하는 것입니다. 아래는 pydantic-settings를 사용한 모범 사례입니다.

```python
# config.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
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

# Usage
settings = Settings()
print(f"Running in {settings.environment} with log level {settings.log_level}")
```

이 코드는 세 가지 핵심 원칙을 따릅니다. 첨째, 필수 값이 빠지면 시작 시점에 즉시 실패합니다. 둘째, 값의 유효성을 validator로 검증합니다. 셋째, 기본값이 코드에 명시되어 투명성을 높입니다.

## 환경 간 차이를 줄이는 패턴

환경 간 차이가 클수록 재현성이 떨어지고, 버그는 특정 환경에서만 나타나며, 운영 비용이 증가합니다. 아래는 환경 간 일관성을 높이는 실용적 패턴입니다.

### 패턴 1 - 컨테이너로 종속성 고정

Python 버전, 시스템 라이브러리가 환경마다 다르면 같은 코드가 다르게 동작합니다. 컨테이너 이미지로 고정하면 dev와 prod가 동일한 실행 환경을 공유합니다.

### 패턴 2 - 환경별 YAML 파일 분리

환경별 차이를 코드에 분기문으로 넣지 말고, 설정 파일로 빼면 변경 이력이 명시적으로 남습니다.

```bash
configs/
  dev.yaml
  stage.yaml
  prod.yaml
```

### 패턴 3 - 로컬에서도 프로덕션 설정 테스트

프로덕션 설정에 문제가 있는지는 배포 후가 아니라 배포 전에 알아야 합니다. 로컬에서 프로덕션 YAML을 로딩해보는 테스트를 추가하면 조기 발견이 가능합니다.

```python
# tests/test_config.py
import pytest
from config import Settings

def test_prod_config_loads():
    """Ensure production config has all required fields."""
    import os
    os.environ["ENV_FILE"] = "configs/prod.yaml"
    settings = Settings()
    assert settings.environment == "prod"
    assert settings.db_url.startswith("postgres://")
```

### 패턴 4 - Parity 체크리스트

Twelve-Factor App은 dev/stage/prod parity를 강조합니다. 아래 체크리스트로 확인할 수 있습니다.

- [ ] 데이터베이스 종류가 같습니다 (예: 로컬 SQLite, 프로덕션 PostgreSQL은 비권장)
- [ ] 컨테이너 이미지가 같습니다
- [ ] Python 버전이 같습니다
- [ ] 의존성 버전이 고정되어 있습니다 (requirements.txt 또는 poetry.lock)

이 네 가지만 맞춰도 환경 간 문제는 크게 줄어듭니다.
## 전환 전후

**Before (코드에 설정 하드코딩)**

```python
DB_URL = "postgres://prod-db.example.com/app"   # hardcoded
API_KEY = "sk-1234..."                           # secret in code
```

이 구조는 처음에는 편해 보여도 금방 한계가 드러납니다. 코드 변경 없이 값을 바꿀 수 없고, 시크릿이 Git 히스토리에 영구적으로 남기 때문입니다.

**After (환경에서 주입)**

```python
import os
DB_URL = os.environ["DB_URL"]
API_KEY = os.environ["API_KEY"]
```

코드가 값을 소유하지 않고 환경이 값을 주입하면, 같은 애플리케이션을 여러 환경에 일관되게 올릴 수 있습니다.

## 설정 관리를 위한 5단계

### 1단계 - 로컬은 .env로 분리

로컬 개발에서는 단순하고 빠른 방식이 필요합니다. 다만 .env는 어디까지나 로컬 편의 장치이지, 프로덕션 비밀 저장소가 아닙니다.

```bash
# .env (gitignored)
DB_URL=postgres://localhost/app
API_KEY=test-key-1234
```

### 2단계 - pydantic-settings로 검증

설정은 실행 도중 뒤늦게 실패하는 것보다 시작 시점에 즉시 검증되는 편이 훨씬 낫습니다. 빠르게 실패해야 배포도 빨리 고칠 수 있습니다.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str
    api_key: str

settings = Settings()   # auto-loads from env
```

### 3단계 - 환경별 설정 분리

환경 차이는 코드 분기가 아니라 설정 파일에서 표현해야 합니다. 운영자는 값 차이를 볼 수 있어야 하고, 리뷰어는 변경 범위를 추적할 수 있어야 합니다.

```yaml
# k8s/values-prod.yaml
db_url: postgres://prod-db.example.com/app
api_key:
  valueFrom:
    secretKeyRef: { name: api-key, key: value }
```

### 4단계 - 시크릿은 전용 저장소에 보관

시크릿은 배포 파일이나 Git 저장소에 오래 남아 있으면 안 됩니다. 회전, 접근 통제, 감사 로그를 고려하면 전용 저장소가 사실상 필수입니다.

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/api-key
```

### 5단계 - 시크릿 자동 주입

사람이 직접 값을 복사해서 붙여 넣는 과정이 많을수록 누락과 노출이 함께 늘어납니다. 운영 환경에서는 주입까지 자동화되어야 합니다.

```yaml
# Kubernetes External Secrets
apiVersion: external-secrets.io/v1
kind: ExternalSecret
spec:
  secretStoreRef: { name: aws-secrets, kind: ClusterSecretStore }
  data:
    - secretKey: api-key
      remoteRef: { key: prod/api-key }
```

## 이 코드에서 먼저 봐야 할 점

- 시크릿은 코드 저장소에 들어가면 안 됩니다.
- 설정 검증은 애플리케이션 시작 시점에 끝내야 합니다.
- 환경별 YAML 분리는 가시성과 리뷰 품질을 함께 높여 줍니다.

좋은 설정 관리의 목적은 숨기는 것만이 아닙니다. 누가 어떤 값을 바꿨는지, 어떤 환경에 어떤 차이가 있는지, 누락 시 언제 실패하는지가 분명해야 합니다.

## 자주 하는 실수 5가지

1. **시크릿을 Git에 커밋하는 실수**입니다. 한 번 올라간 시크릿은 완전히 지우기 매우 어렵습니다.
2. **프로덕션에서도 .env에 기대는 실수**입니다. 로컬 편의 도구와 운영 비밀 관리를 구분해야 합니다.
3. **모든 환경에서 같은 시크릿을 쓰는 실수**입니다. 하나가 새면 전 환경이 함께 위험해집니다.
4. **설정을 런타임에 바꾸고 재시작하지 않는 실수**입니다. 인스턴스마다 다른 상태가 남을 수 있습니다.
5. **환경별 코드 분기를 만드는 실수**입니다. `if env == "prod"`는 설정 문제를 코드 문제로 바꿉니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 Vault나 AWS Secrets Manager에 시크릿을 저장하고, External Secrets Operator 같은 구성 요소로 Kubernetes에 자동 주입합니다. 이렇게 해야 시크릿 회전과 접근 관리가 운영 절차 안으로 들어옵니다.

작은 팀도 원칙은 같습니다. 코드와 설정을 분리하고, 시크릿을 Git에서 빼고, 시작 시 검증하도록 바꾸는 세 가지만 해도 운영 리스크가 크게 줄어듭니다.

## 시니어 엔지니어는 이렇게 봅니다

- 하나의 코드베이스로 여러 환경을 운영해야 합니다.
- 시크릿 회전은 자동화 가능한 구조여야 합니다.
- 설정 변경도 PR과 리뷰를 거쳐야 합니다.
- 환경 차이는 코드가 아니라 설정으로 표현해야 합니다.
- 시크릿 유출은 가능성이 아니라 시간 문제라고 가정합니다.

## 체크리스트

- [ ] .env가 .gitignore에 포함되어 있습니다.
- [ ] 시크릿이 전용 저장소에 보관됩니다.
- [ ] 환경별 설정 파일이 분리되어 있습니다.
- [ ] 애플리케이션이 시작 시 설정을 검증합니다.

## 연습 문제

1. 현재 프로젝트 Git 히스토리에서 시크릿 흔적을 찾아보세요.
2. pydantic-settings로 설정 검증을 추가해 보세요.
3. 환경별 YAML 파일로 설정을 분리해 보세요.

## 정리 및 다음 단계

설정 관리는 환경 독립성의 출발점입니다. 다음 글에서는 같은 원리를 더 확장해, 인프라 자체를 코드로 다루는 IaC를 살펴봅니다.

## 환경 분리와 설정 관리를 운영 체계로 만드는 방법

환경 분리는 단순히 서버를 나누는 작업이 아닙니다. 위험 수준이 다른 실행 문맥을 분리하고, 동일한 산출물을 안전하게 이동시키는 설계입니다. 설정 관리가 약하면 배포가 느려지고, 배포가 느리면 검증 루프도 길어집니다.

### 환경 분리 기준표

| 환경 | 목적 | 데이터 정책 | 변경 허용도 | 실패 허용도 |
| --- | --- | --- | --- | --- |
| dev | 기능 개발/실험 | 샘플 데이터 | 높음 | 높음 |
| stage | 배포 전 검증 | 익명화 실데이터 또는 유사 데이터 | 중간 | 중간 |
| prod | 실제 사용자 서비스 | 실제 운영 데이터 | 낮음 | 매우 낮음 |

핵심은 환경 이름이 아니라 운영 의도입니다. 예를 들어 stage가 dev와 크게 다르면 prod 문제를 사전에 잡기 어렵습니다.

### 설정 계층 분리 원칙

| 계층 | 예시 | 저장 위치 |
| --- | --- | --- |
| 공통 설정 | 로깅 포맷, 타임아웃 기본값 | 코드/버전관리 |
| 환경 설정 | DB host, endpoint | 환경별 values 파일 |
| 시크릿 | API 키, 비밀번호 | Secrets Manager/Vault |

### Docker Compose 기반 개발 환경 예시

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
    ports:
      - "5432:5432"
```

개발 환경에서는 Compose가 빠른 피드백에 유리합니다. 다만 prod까지 같은 패턴을 강제하기보다, dev 편의와 운영 안전의 경계를 명확히 구분해야 합니다.

### 설정 검증 코드 예시

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str
    db_url: str
    api_key: str

    model_config = {
        "env_file": ".env",
        "extra": "forbid",
    }

settings = Settings()
```

시작 시점 검증은 "나중에 터지는 설정 오류"를 배포 초기에 차단하는 가장 값싼 방법입니다.

### 시크릿 운영 체크포인트

| 항목 | 권장 기준 |
| --- | --- |
| 저장 | Git 미저장, 전용 비밀 저장소 |
| 접근 | 최소 권한 IAM |
| 회전 | 분기 또는 반기 자동 회전 |
| 감사 | 누가 읽었는지 감사 로그 보관 |
| 노출 방지 | 로그/에러 메시지 마스킹 |

### 운영 실수 방지 패턴

1. `if env == "prod"` 같은 코드 분기 대신 설정으로 차이를 표현합니다.
2. 환경 간 drift를 주기적으로 비교합니다.
3. stage 배포를 main merge 직후 자동화해 prod 직전 위험을 낮춥니다.
4. 긴급 핫픽스도 동일한 파이프라인을 사용해 예외 습관을 줄입니다.

설정 관리의 목적은 편의성이 아니라 신뢰성입니다. 같은 코드가 환경마다 다르게 동작하는 불확실성을 제거할수록 운영 품질이 올라갑니다.

### 환경 드리프트를 줄이는 운영 절차

설정은 분리해 두는 것만으로 충분하지 않습니다. 실제 값이 문서와 일치하는지 정기 검증이 필요합니다. 많은 팀이 stage와 prod의 환경변수 차이를 정확히 모른 채 운영하고, 장애가 난 뒤에야 누락 값을 발견합니다.

```bash
python scripts/diff_env_keys.py --from stage --to prod
python scripts/check_required_env.py --env prod
```

위와 같은 점검을 배포 파이프라인 전 단계에 넣으면 설정 누락 사고를 크게 줄일 수 있습니다. 핵심은 "값 비교"보다 "필수 키 존재 여부"를 자동 검증하는 것입니다.

운영 시크릿 회전 절차도 미리 정의해야 합니다. 키를 회전할 때는 새 키 발급, 이중 키 허용 기간, 구 키 폐기 순서를 자동화해야 무중단 전환이 가능합니다. 이 절차를 문서로만 두지 말고 분기별 리허설로 검증하는 것이 안전합니다.

### 설정 변경 배포 절차 예시

설정 변경은 코드 변경보다 가볍게 보이지만, 실제 장애 비율은 오히려 높은 편입니다. 따라서 설정 변경도 코드 변경과 같은 수준의 검증 절차를 갖춰야 합니다.

```yaml
config_change_flow:
  - open_pr: "환경별 설정 diff 확인"
  - validate: "필수 키 존재, 값 형식 검사"
  - deploy_stage: "stage 적용 후 스모크 테스트"
  - deploy_prod: "관찰 지표 통과 시 승격"
  - audit: "변경 이력과 승인자 기록"
```

이 절차를 운영하면 "코드는 안 바뀌었는데 서비스가 깨졌다"는 유형의 사고를 크게 줄일 수 있습니다. 특히 외부 API endpoint, timeout, feature flag 기본값처럼 영향이 큰 설정은 반드시 stage 검증을 거쳐야 합니다.

### 설정 사고를 줄이는 리뷰 질문

환경 설정 PR을 리뷰할 때는 문법보다 운영 영향 질문을 먼저 확인하는 것이 좋습니다.

- 이 값 변경이 트래픽 경로를 바꾸는가
- 타임아웃/재시도 정책이 외부 의존성 부하를 증가시키는가
- 롤백 시 이전 값으로 즉시 복귀 가능한가
- 알림 임계값과 runbook이 함께 갱신되었는가

이 질문을 템플릿화하면 설정 리뷰 품질이 개인 경험에 덜 의존하게 됩니다.

추가로 설정 키 명명 규칙을 통일하면 운영 효율이 좋아집니다. 예를 들어 모든 외부 API 키를 `EXTERNAL_<SERVICE>_API_KEY` 형식으로 고정하면 검색, 감사, 회전 자동화가 쉬워집니다. 작은 규칙이지만 장기 운영에서 큰 차이를 만듭니다.

```text
## 0-5분
1. SEV 판정 (SEV1/SEV2)
2. incident 채널 개설
3. 최근 배포 커밋 확인

## 5-10분
1. canary/최근 릴리스 롤백 시도
2. 에러율, p95, DB 연결수 확인
3. 고객 영향 범위 요약 공지

## 10-20분
1. 임시 완화 조치 적용
2. 영구 수정 owner 지정
3. postmortem 일정 예약
```

운영에서는 "잘 아는 사람"보다 "같은 순서를 따르는 팀"이 더 빠르게 복구합니다. 그래서 runbook은 설명 문서가 아니라 실행 문서여야 하며, 경보에서 한 번에 열 수 있어야 합니다.

## 처음 질문으로 돌아가기

- **dev, stage, prod 환경을 분리하는 이유는 무엇일까요?**
  - 이 글은 dev, stage, prod가 이름만 다른 서버가 아니라 목적과 데이터 정책, 실패 허용도가 다른 실행 문맥이라고 설명합니다. 특히 stage를 prod와 최대한 비슷하게 유지해야 설정 누락이나 배포 전 검증 실패를 운영 전에 잡을 수 있습니다.
- **같은 코드베이스를 여러 환경에 배포하려면 무엇을 코드 밖으로 빼야 할까요?**
  - 데이터베이스 URL, 외부 API 키, 도메인, 타임아웃처럼 환경마다 달라지는 값은 코드 밖으로 빼야 합니다. 본문에서 `pydantic-settings`, 환경별 YAML, `os.environ["DB_URL"]` 예시를 보여 준 이유도 같은 빌드 산출물을 설정만 바꿔 여러 환경에 재사용하기 위해서입니다.
- **환경변수와 시크릿은 어떻게 다르며 왜 따로 관리해야 할까요?**
  - 환경변수는 실행 설정을 주입하는 수단이고, 시크릿은 API 키나 비밀번호처럼 회전과 접근 통제, 감사 로그가 필요한 민감 정보입니다. 그래서 로컬은 `.env`로 시작할 수 있어도 운영 환경에서는 Vault, AWS Secrets Manager, External Secrets 같은 전용 경로로 분리해야 안전합니다.

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- **환경 분리와 설정 관리 (현재 글)**
- Infrastructure as Code (예정)
- 컨테이너와 빌드 (예정)
- 모니터링과 알림 (예정)
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [The Twelve-Factor App — Config](https://12factor.net/config)
- [HashiCorp Vault](https://developer.hashicorp.com/vault)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [External Secrets Operator](https://external-secrets.io/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, Configuration, Secrets, Environment, TwelveFactor
