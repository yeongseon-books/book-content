---
series: devops-101
episode: 6
title: "DevOps 101 (6/10): 컨테이너와 빌드"
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
  - Docker
  - Container
  - Security
  - Build
seo_description: 재현 가능한 컨테이너 빌드, 멀티 스테이지 Dockerfile, 이미지 보안 스캔 전략을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (6/10): 컨테이너와 빌드

컨테이너는 "내 컴퓨터에서는 됩니다" 문제를 해결하는 가장 현실적인 방법입니다. 하지만 단순히 Dockerfile을 만드는 것으로는 충분하지 않습니다. 이미지 크기, 빌드 시간, 보안, 레이어 캐시 활용이 모두 운영 품질에 직접 영향을 줍니다.

이 글은 DevOps 101 시리즈의 여섯 번째 글입니다.

![DevOps 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/06/06-01-diagram.ko.png)
*DevOps 101 6장 흐름 개요*
> 좋은 컨테이너 이미지는 작고, 재현 가능하며, 취약점이 최소화된 이미지입니다.

## 이 글에서 다룰 문제

- 멀티 스테이지 빌드는 왜 필수인가요?
- 이미지 레이어 캐시를 어떻게 활용해야 빌드가 빨라질까요?
- 컨테이너 이미지 보안 스캔은 어떻게 파이프라인에 통합할까요?
- 루트가 아닌 사용자로 실행해야 하는 이유는 무엇일까요?

## 멀티 스테이지 Dockerfile

단일 스테이지 이미지는 빌드 도구, 테스트 의존성, 소스 코드가 모두 포함되어 이미지가 비대해집니다. 멀티 스테이지 빌드로 최종 실행 이미지만 최소화합니다.

```dockerfile
# Dockerfile
# ── 스테이지 1: 의존성 빌드 ────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# 의존성 파일만 먼저 복사 (레이어 캐시 최적화)
COPY requirements.txt .

# 의존성을 /install에 설치 (최종 이미지에 복사할 위치)
RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt

# ── 스테이지 2: 최종 실행 이미지 ─────────────────────────────────
FROM python:3.12-slim AS runtime

# 보안: 루트 사용자 대신 전용 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 빌더에서 의존성만 복사
COPY --from=builder /install /usr/local

# 소스 코드 복사
COPY --chown=appuser:appuser src/ ./src/

# 비루트 사용자로 전환
USER appuser

# 컨테이너 헬스 체크
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 이미지 크기 비교

| 빌드 방식 | 이미지 크기 | 빌드 시간 |
|----------|-----------|---------|
| python:3.12 (풀 이미지) | ~1.1GB | 느림 |
| python:3.12-slim 단일 스테이지 | ~400MB | 보통 |
| 멀티 스테이지 (slim 기반) | ~150MB | 첫 빌드 느림, 이후 캐시 빠름 |
| python:3.12-alpine 기반 | ~80MB | 빌드 복잡 (musl libc 이슈) |

Alpine 기반은 작지만 musl libc 호환성 문제로 NumPy, scipy 같은 과학 라이브러리에서 문제가 생깁니다. `-slim` 기반이 대부분의 Python 서비스에 적합합니다.

## 레이어 캐시 최적화

Docker는 Dockerfile의 각 명령을 레이어로 캐시합니다. 변경이 없는 레이어는 재사용합니다. 자주 변경되는 파일을 나중에 복사하면 캐시 히트율이 높아집니다.

```dockerfile
# 나쁜 예: 소스 코드 복사 후 의존성 설치 (소스 변경마다 pip install 재실행)
COPY . .
RUN pip install -r requirements.txt

# 좋은 예: 의존성 먼저 설치, 소스 나중에
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
```

BuildKit의 캐시 마운트를 활용하면 pip 캐시를 빌드 간 재사용합니다.

```dockerfile
# BuildKit 캐시 마운트 - pip 캐시를 빌드 간 재사용
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt
```

## CI에서 이미지 빌드와 푸시

```yaml
# .github/workflows/docker-build.yml
name: Docker Build

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: AWS 인증 (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ap-northeast-2

      - name: ECR 로그인
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Docker Buildx 설정
        uses: docker/setup-buildx-action@v3

      - name: 이미지 빌드 및 푸시
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ${{ steps.ecr-login.outputs.registry }}/order-service:${{ github.sha }}
            ${{ steps.ecr-login.outputs.registry }}/order-service:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Trivy 이미지 스캔
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.ecr-login.outputs.registry }}/order-service:${{ github.sha }}
          format: sarif
          output: trivy-image-results.sarif
          severity: HIGH,CRITICAL
          exit-code: 1

      - name: 스캔 결과 업로드
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-image-results.sarif
```

## 이미지 취약점 대응 런북

**HIGH/CRITICAL 취약점 발견 시 대응 절차**

1. 취약점 상세 확인:
```bash
# 로컬 스캔
trivy image --severity HIGH,CRITICAL \
  --format table \
  registry.example.com/order-service:latest

# 수정 가능한 취약점만 표시
trivy image --severity HIGH,CRITICAL \
  --ignore-unfixed \
  registry.example.com/order-service:latest
```

2. 원인 파악:
   - 애플리케이션 의존성 취약점 → `pip-audit`으로 확인 후 업그레이드
   - 베이스 이미지 취약점 → `FROM python:3.12-slim` 최신 태그로 갱신

3. 수정 및 재빌드:
```bash
# 취약 패키지 업그레이드
pip install --upgrade <패키지명>
pip freeze > requirements.txt

# 이미지 재빌드
docker build --no-cache -t order-service:patched .

# 패치 확인
trivy image --severity HIGH,CRITICAL order-service:patched
```

4. 즉각 패치 불가 시:
   - `.trivyignore` 파일에 CVE ID와 이유 및 해결 예정일 기록
   - 이슈 트래커에 취약점 추적 티켓 생성

## Kubernetes 컨테이너 보안 설정

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault

      containers:
        - name: order-service
          image: registry.example.com/order-service:latest

          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

          resources:
            requests:
              memory: 256Mi
              cpu: 100m
            limits:
              memory: 512Mi
              cpu: 500m

          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 단일 스테이지 빌드 | 이미지에 빌드 도구, 테스트 파일 포함 | 멀티 스테이지로 빌드 환경과 실행 환경 분리 |
| root 사용자로 실행 | 컨테이너 탈출 시 호스트 권한 획득 가능 | 비루트 사용자 생성 후 USER 지정 |
| `COPY . .`를 의존성 설치 전에 위치 | 소스 변경마다 pip install 재실행 | 의존성 파일 먼저 복사, 소스 나중에 |
| 이미지 보안 스캔 없음 | 알려진 CVE가 프로덕션에 배포됨 | Trivy를 CI 필수 단계로 포함 |
| :latest 태그만 사용 | 이전 버전으로 롤백 불가 | SHA 또는 버전 태그 병행 사용 |
| 읽기 전용 파일시스템 미설정 | 컨테이너 내부 파일 변조 가능 | `readOnlyRootFilesystem: true` 설정 |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- **DevOps 101 (6/10): 컨테이너와 빌드 (현재 글)**
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [Docker 멀티 스테이지 빌드](https://docs.docker.com/build/building/multi-stage/)
- [Trivy 문서](https://trivy.dev/)
- [Kubernetes Security Context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
