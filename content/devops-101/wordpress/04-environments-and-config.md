---
title: "바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리"
series: devops-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 만든 앱을 여러 환경에서 안전하게 운영하려면 설정 관리가 핵심입니다. dev, staging, prod 환경 분리와 시크릿 관리 원칙을 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 4번째 글입니다.

AI 코딩 도구로 빠르게 앱을 만들다 보면 자주 이런 일이 생깁니다. 로컬에서는 잘 동작하는 코드가 서버에 올리면 에러를 냅니다. 데이터베이스 주소가 코드에 하드코딩되어 있어서 팀원이 같은 코드를 받아 실행하면 자기 환경이 아닌 곳에 연결됩니다. 또는 API 키를 실수로 GitHub에 올렸다가 보안 사고로 이어집니다.

환경 분리와 설정 관리는 이런 문제를 구조적으로 해결합니다. 같은 코드가 dev에서는 개발용 데이터베이스에, production에서는 실제 데이터베이스에 연결되는 구조를 만드는 것입니다. 코드는 하나, 설정은 환경마다 다르게.

AI에게 "환경 변수 설정 코드 만들어줘"라고 요청할 수 있습니다. 그런데 어떤 값을 환경 변수로 빼야 하는지, 시크릿은 어떻게 관리해야 하는지 모르면 AI가 만들어준 코드에서 보안 구멍이 생길 수 있습니다.

> 코드는 하나이고, 달라지는 것은 환경별 설정뿐입니다.

---

## 이 글에서 다룰 문제
- dev, staging, prod 환경을 왜 분리해야 할까요?
- 코드에서 무엇을 환경 변수로 빼야 할까요?
- 환경 변수와 시크릿은 어떻게 다르며 왜 따로 관리해야 할까요?
- .env 파일을 production에서 쓰면 왜 위험할까요?
- AI가 생성한 설정 코드에서 자주 생기는 보안 문제는 무엇일까요?

## 설정 관리 도구 비교

| 도구 | 용도 | 보안 수준 | 주의사항 |
|---|---|---|---|
| .env 파일 | 로컬 개발 | 낮음 (평문) | .gitignore 필수, production 부적합 |
| GitHub Secrets | CI/CD에서 시크릿 주입 | 중간 | 로그에 노출 안 되도록 주의 |
| AWS Secrets Manager | 운영 환경 시크릿 | 높음 | IAM 권한 설계 필요 |
| HashiCorp Vault | 복잡한 시크릿 관리 | 높음 | 서버 운영 필요, 학습 곡선 있음 |

대부분의 바이브코딩 프로젝트는 로컬은 .env, CI는 GitHub Secrets, 운영은 클라우드 Secrets Manager로 시작하면 충분합니다.

## 설정을 코드에서 분리하는 패턴

```python
# 나쁜 예: 코드에 하드코딩
DB_URL = "postgres://prod-db.example.com/app"
API_KEY = "sk-1234abcd"

# 좋은 예: 환경에서 주입
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str
    api_key: str
    environment: str = "dev"

    class Config:
        env_file = ".env"

settings = Settings()  # 시작 시점에 검증, 값 없으면 즉시 오류
```

pydantic-settings를 쓰면 필수 설정이 빠졌을 때 앱이 시작하는 순간에 오류가 납니다. 나중에 실행 중에 터지는 것보다 훨씬 낫습니다.

## Before / After

**Before**: "API 키를 .env 파일에 넣었는데 팀원이 실수로 GitHub에 커밋했다. API 키를 즉시 교체해야 했고, Git 히스토리에서 완전히 지우는 데도 시간이 걸렸다."

**After**: "API 키는 .env에는 있지만 .gitignore에 포함되어 있다. CI/CD에서는 GitHub Secrets로 주입된다. Production에서는 AWS Secrets Manager에서 자동으로 가져온다. 코드 어디에도 실제 키 값이 없다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 시크릿을 코드에 하드코딩하는 실수 | Git 히스토리에 영구적으로 남아 보안 사고로 이어짐 | 모든 민감 값을 환경 변수로 분리 |
| .env 파일을 production에서 사용하는 실수 | 평문 파일은 서버 침해 시 모든 값이 노출됨 | 운영 환경은 Secrets Manager 사용 |
| AI가 생성한 코드에 테스트용 API 키가 포함된 실수 | AI가 예시용으로 가짜처럼 보이는 키를 넣을 수 있음 | AI 생성 코드에서 키 형태의 값 전수 확인 |
| 모든 환경에서 같은 시크릿을 사용하는 실수 | 하나가 노출되면 모든 환경이 위험해짐 | 환경별로 별도의 시크릿 발급 |
| 설정 검증을 런타임으로 미루는 실수 | 운영 중에 터지면 더 큰 피해 | 앱 시작 시점에 필수 설정 검증 |

## AI에게 설정 관련 질문하는 팁

설정 관리 코드를 AI에게 요청할 때 이 정보를 포함하면 보안이 고려된 결과를 받습니다:

```
언어/프레임워크: [Python + FastAPI 등]
환경 종류: [dev, staging, production]
시크릿 종류: [DB URL, API 키, JWT 시크릿 등]
시크릿 저장 위치: [GitHub Secrets, AWS Secrets Manager 등]
검증 요구사항: [필수 값 누락 시 즉시 실패]
```

AI가 생성한 설정 코드를 받았다면 반드시 확인할 것: 시크릿이 하드코딩된 곳이 없는지, .env 파일이 .gitignore에 포함되었는지, 필수 값 검증이 있는지.

## 운영 체크리스트

- [ ] .env 파일이 .gitignore에 포함되어 있습니다
- [ ] 시크릿이 코드나 설정 파일에 하드코딩되어 있지 않습니다
- [ ] 환경별로 별도의 시크릿이 사용됩니다
- [ ] 앱 시작 시점에 필수 설정 값이 검증됩니다
- [ ] Production 시크릿은 전용 저장소(Secrets Manager)에 보관됩니다

## 처음 질문으로 돌아가기

"환경 변수로 설정을 분리하는 게 왜 그렇게 중요한가요?"

코드에 시크릿을 박으면 Git에 영구 기록됩니다. 어떤 방법으로도 완전히 지우기 어렵습니다. 또한 같은 코드를 dev에서 테스트하고 production에 배포하려면 환경별로 다른 값이 주입되는 구조가 반드시 필요합니다. 바이브코딩으로 빠르게 만든 코드도 보안 사고 앞에서는 예외가 없습니다.

## 정리

설정 관리는 코드와 환경을 분리하는 기초입니다. 코드는 하나, 설정은 환경마다 다르게. 시크릿은 코드가 아닌 전용 저장소에. 이 원칙이 잡히면 같은 코드를 여러 환경에 안전하게 배포할 수 있습니다. 다음 글에서는 인프라 자체를 코드로 관리하는 IaC를 다룹니다.

## 참고 자료
### 공식 문서
- [The Twelve-Factor App — Config](https://12factor.net/config)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- **바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리 (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, Configuration, Secrets
