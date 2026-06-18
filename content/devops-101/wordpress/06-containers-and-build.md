---
title: "바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드"
series: devops-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 만든 앱을 어디서나 같은 방식으로 실행하려면 컨테이너가 필요합니다. Docker 빌드 원칙과 바이브코딩 환경에서의 실전 팁을 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 6번째 글입니다.

AI 코딩 도구로 앱을 만들다 보면 자주 겪는 고통이 있습니다. "내 컴퓨터에서는 되는데 서버에서는 안 됩니다." Python 버전이 다르거나, 특정 시스템 라이브러리가 서버에 없거나, 의존성 버전이 조금 달라서 에러가 납니다. AI가 짜준 코드가 완벽해도 실행 환경이 다르면 동작하지 않습니다.

컨테이너는 이 문제를 해결합니다. 코드뿐 아니라 Python 버전, 시스템 라이브러리, 의존성까지 하나의 패키지로 묶어서 어느 환경에서도 같은 방식으로 실행되게 합니다. Docker로 이미지를 한 번 만들면 로컬에서도, CI에서도, 프로덕션 서버에서도 같은 결과가 납니다.

AI에게 "Dockerfile 만들어줘"라고 요청할 수 있습니다. 하지만 이미지 크기, 보안, 빌드 속도에 영향을 주는 설계 원칙을 모르면 AI가 만든 Dockerfile이 운영에 적합하지 않을 수 있습니다. 500MB짜리 이미지, 루트 계정으로 실행, 보안 취약점을 포함한 오래된 기반 이미지 같은 문제는 Dockerfile 몇 줄의 차이에서 나옵니다.

> 컨테이너는 실행 환경을 코드처럼 관리하게 해줍니다.

---

## 이 글에서 다룰 문제
- 컨테이너는 왜 "내 컴퓨터에서는 됩니다" 문제를 해결할까요?
- Dockerfile에서 빌드 속도와 이미지 크기를 동시에 개선하는 방법은?
- multi-stage 빌드는 어떻게 이미지를 작고 안전하게 만들까요?
- AI가 만든 Dockerfile에서 자주 생기는 보안 문제는 무엇일까요?
- 컨테이너 보안 기본 원칙 세 가지는 무엇일까요?

## 컨테이너 빌드 최적화 방법 비교

| 방법 | 효과 | 설명 |
|---|---|---|
| Layer cache 활용 | 빌드 시간 90% 단축 | 자주 바뀌는 파일은 나중에 COPY |
| multi-stage 빌드 | 이미지 크기 50-70% 감소 | 빌드 도구를 최종 이미지에서 제거 |
| 경량 기반 이미지 | 이미지 크기 30-50% 감소 | python:3.12-slim 또는 distroless |
| non-root 사용자 | 보안 위험 감소 | 컨테이너 탈출 시 피해 범위 제한 |

## 실전 Dockerfile: 바이브코딩 Python 앱용

```dockerfile
# Stage 1: 의존성 설치
FROM python:3.12 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: 실행 환경 (빌드 도구 없음)
FROM python:3.12-slim
WORKDIR /app

# non-root 사용자 생성
RUN useradd --create-home appuser
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 앱 코드 복사 (의존성 변경 없으면 cache 재사용)
COPY --chown=appuser:appuser . /app
USER appuser

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt`를 먼저 COPY하는 이유: 의존성이 바뀌지 않으면 `pip install` 단계가 캐시에서 재사용됩니다. 코드만 바꾸면 마지막 `COPY`만 다시 실행됩니다.

## Before / After

**Before**: "Dockerfile에서 `COPY . .`를 먼저 하고 `pip install`을 나중에 했더니 코드를 조금만 수정해도 매번 의존성을 전부 다시 설치했다. CI 빌드에 8분이 걸렸다."

**After**: "requirements.txt를 먼저 COPY하고 pip install을 실행하도록 순서를 바꿨다. 코드만 바꾸면 의존성 캐시가 재사용되어 빌드가 1분으로 줄었다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| `latest` 태그 사용 실수 | 언제 이미지가 바뀔지 모르고 재현이 안 됨 | `python:3.12.3-slim`처럼 버전 고정 |
| 루트 계정으로 실행하는 실수 | 컨테이너 취약점 발견 시 서버 전체가 위험 | non-root 사용자로 전환 |
| 시크릿을 이미지에 넣는 실수 | `docker history`로 노출 가능 | 시크릿은 환경 변수로 런타임에 주입 |
| multi-stage 없이 큰 이미지 만드는 실수 | 배포 시간, 스토리지 비용, 공격 표면 증가 | builder 단계와 runtime 단계 분리 |
| .dockerignore 없는 실수 | 불필요한 파일이 이미지에 포함되어 크기 증가 | .git, __pycache__, .env 제외 |

## AI에게 컨테이너 관련 질문하는 팁

Dockerfile을 AI에게 요청할 때 이 정보를 포함하면 보안과 성능이 고려된 결과를 받습니다:

```
언어/런타임: [Python 3.12, Node.js 20 등]
프레임워크: [FastAPI, Express 등]
실행 명령: [uvicorn, node, gunicorn 등]
이미지 크기 목표: [200MB 이하]
보안 요구사항: [non-root, 취약점 스캔]
헬스체크 경로: [/health]
```

AI가 만든 Dockerfile을 받았다면 반드시 확인할 것: `latest` 태그를 쓰는지, 루트 계정으로 실행하는지, 시크릿이 포함되어 있는지, COPY 순서가 캐시 친화적인지.

## 운영 체크리스트

- [ ] Dockerfile이 non-root 사용자로 끝납니다
- [ ] multi-stage 빌드로 최종 이미지 크기를 줄였습니다
- [ ] .dockerignore가 불필요한 파일을 제외합니다
- [ ] CI에서 이미지 취약점 스캔이 실행됩니다
- [ ] 기반 이미지 버전이 고정되어 있습니다

## 처음 질문으로 돌아가기

"컨테이너를 꼭 써야 하나요? 그냥 서버에 직접 설치하면 안 되나요?"

직접 설치는 처음에는 빠르지만 환경마다 미묘하게 달라집니다. AI가 짜준 코드가 로컬에서는 되는데 서버에서 안 되는 원인의 상당수는 실행 환경 차이입니다. 컨테이너는 이 차이를 없애줍니다. 또한 같은 이미지를 CI, 스테이징, 프로덕션에서 쓰면 "CI에서는 됐는데 운영에서는 안 된다"는 문제도 없어집니다.

## 정리

컨테이너는 실행 환경의 차이를 코드로 고정하는 방법입니다. Dockerfile 몇 줄의 순서와 설계 선택이 빌드 속도, 이미지 크기, 보안을 동시에 결정합니다. 다음 글에서는 이렇게 배포된 서비스를 운영 중에 어떻게 관찰할지 모니터링과 알림을 다룹니다.

## 참고 자료
### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Distroless Images](https://github.com/GoogleContainerTools/distroless)
- [Trivy](https://trivy.dev/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- **바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드 (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, Docker, Container
