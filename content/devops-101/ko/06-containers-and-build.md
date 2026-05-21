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
  - Build
  - Image
seo_description: 재현 가능하고 가벼운 컨테이너 이미지를 만드는 Docker 빌드 원칙을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (6/10): 컨테이너와 빌드

이 글은 DevOps 101 시리즈의 여섯 번째 글입니다.

## 먼저 던지는 질문

- 컨테이너는 VM과 무엇이 다르고 왜 배포 재현성에 유리할까요?
- Dockerfile에서 꼭 이해해야 할 기본 명령은 무엇일까요?
- multi-stage build는 이미지 크기와 보안에 어떤 차이를 만들까요?

## 큰 그림

![DevOps 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/06/06-01-diagram.ko.png)

*DevOps 101 6장 흐름 개요*

이 그림은 코드 변경부터 컨테이너 이미지 빌드, 푸시까지의 자동화 흐름을 보여줍니다. 빌드가 빠르고 일관성 있을수록 배포 신뢰도가 올라갑니다.

> 컨테이너와 빌드 자동화의 핵심은 개발 환경의 '내 컴퓨터에서는 되는데'를 없애는 것입니다.

## 왜 중요한가

같은 빌드 산출물이 모든 환경에서 같은 방식으로 동작해야 배포가 예측 가능해집니다. 컨테이너는 운영체제 라이브러리와 의존성, 애플리케이션 코드를 함께 묶어서 이 문제를 해결합니다.

실무에서 컨테이너의 가치는 단순히 배포가 편해진다는 데 있지 않습니다. 환경 차이 때문에 생기던 "내 로컬에서는 되는데 서버에서는 안 된다"라는 종류의 문제를 구조적으로 줄여 준다는 점이 더 중요합니다.

> 컨테이너는 Build once, run anywhere를 애플리케이션 레벨에서 실현합니다.

## 한눈에 보는 개념

코드가 이미지가 되고, 이미지는 레지스트리에 올라가고, 운영 환경은 그 이미지를 가져다 실행합니다. 이 흐름이 명확할수록 배포는 더 단순해지고 롤백도 쉬워집니다.

## 핵심 용어

- **Image**: 변경 불가능한 실행 패키지입니다.
- **Container**: 이미지를 실제로 실행한 인스턴스입니다.
- **Dockerfile**: 이미지를 만들기 위한 선언형 빌드 레시피입니다.
- **Layer**: Dockerfile 명령마다 쌓이는 읽기 전용 계층입니다.
- **Registry**: 이미지를 저장하고 배포하는 저장소입니다.

이 용어를 구분하면 컨테이너 운영에서 자주 나오는 질문도 훨씬 쉽게 풀립니다. 예를 들어 문제를 고칠 때 컨테이너 안에서 직접 수정하는 것이 아니라 새 이미지를 다시 만드는 이유도 여기서 설명됩니다.

## 전환 전후

**Before (host-dependent)**

```bash
# Install directly on the server
apt install python3.12 postgresql-client
pip install -r requirements.txt
# On another server, *versions differ*
```

호스트에 직접 설치하는 방식은 서버마다 상태가 조금씩 달라지기 쉽습니다. 운영자는 버전을 맞추느라 고생하고, 장애가 나면 "어느 서버에 무엇이 설치됐는지"부터 다시 조사해야 합니다.

**After (Dockerfile)**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

Dockerfile이 있으면 실행 환경이 코드와 함께 버전 관리됩니다. 그 순간부터 환경 차이는 개인의 기억이 아니라 저장소 안의 변경 이력으로 다룰 수 있습니다.

## 실전으로 보는 도커파일 다섯 단계

### 1단계 - 기본 빌드

먼저 이미지를 만들고 실제로 실행해 보아야 합니다. 컨테이너 학습의 출발점은 개념보다 빌드와 실행을 한 번 연결해 보는 경험입니다.

```bash
docker build -t myapp:1.0 .
docker run -p 8000:8000 myapp:1.0
```

### 2단계 - layer cache 최적화

의존성 파일은 자주 안 바뀌고 애플리케이션 코드는 자주 바뀝니다. 이 차이를 Dockerfile 순서에 반영해야 빌드 속도가 빨라집니다.

```dockerfile
COPY requirements.txt .          # rare changes -> cache reuse
RUN pip install -r requirements.txt
COPY . .                          # only the code changes often
```

### 3단계 - multi-stage로 이미지 줄이기

빌드에 필요한 도구와 실행에 필요한 도구는 다릅니다. 이 둘을 분리하면 최종 이미지를 훨씬 작고 안전하게 만들 수 있습니다.

```dockerfile
FROM python:3.12 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["python", "main.py"]
```

### 4단계 - non-root user

운영 컨테이너는 기본적으로 루트가 아니어야 합니다. 보안은 별도 옵션이 아니라 기본 실행 계정에서부터 시작합니다.

```dockerfile
RUN useradd --create-home appuser
USER appuser
```

### 5단계 - healthcheck

실행만 된다고 끝이 아닙니다. 컨테이너가 실제로 정상 응답하는지 런타임이 알 수 있어야 운영 자동화가 가능합니다.

```dockerfile
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
```

## 이 코드에서 먼저 봐야 할 점

- 변경 빈도가 낮은 명령을 위에 두어야 캐시를 최대한 재사용할 수 있습니다.
- slim이나 distroless 이미지는 공격 표면을 줄여 줍니다.
- non-root는 권장사항이 아니라 기본값처럼 다뤄야 합니다.

Dockerfile 한 줄 순서가 빌드 시간과 보안 수준을 동시에 바꿀 수 있습니다. 그래서 컨테이너 빌드는 단순 포장 작업이 아니라 운영 품질을 결정하는 설계 작업에 가깝습니다.

## 컨테이너 빌드 최적화

빌드 시간은 개발자 경험과 배포 속도를 동시에 결정합니다. 아래 표는 자주 사용하는 세 가지 최적화 기법과 효과를 정리한 것입니다.

| 기법 | 효과 | 예시 |
| --- | --- | --- |
| 멀티스테이지 빌드 | 최종 이미지 크기 50-70% 감소 | builder stage 분리 |
| layer cache 활용 | 변경 없는 빌드 시간 90% 단축 | requirements.txt 먼저 COPY |
| 경량 베이스 이미지 | 공격 표면 축소, 빌드 시간 10-30% 개선 | python:3.12-slim, distroless |

cache 최적화는 빈번한 재빌드에서 가장 큰 차이를 만듭니다. 의존성이 바뀌지 않았다면 재설치를 건너뛰는 것만으로 CI 대기 시간을 크게 줄일 수 있습니다.

## 파이썬 FastAPI 멀티스테이지 도커파일 예시

실무에서 바로 쓸 수 있는 FastAPI 앱의 멀티스테이지 Dockerfile 구성입니다. 빌드 단계와 실행 단계를 나눠 최종 이미지를 가볍게 유지합니다.

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12 AS builder
WORKDIR /build

# Install dependencies to user directory
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app

# Create non-root user
RUN useradd --create-home --uid 1001 appuser

# Copy dependencies from builder
COPY --from=builder /root/.local /opt/runtime/.local
ENV PATH=/opt/runtime/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 구조는 builder 단계에서 컴파일과 의존성 설치를 모두 끝낸 뒤, 실행 단계에서는 필요한 파일만 복사해 최종 이미지 크기를 최소화합니다. 추가로 non-root 사용자 전환과 health check까지 포함해 프로덕션 수준의 안정성을 갖춥니다.

## 컨테이너 보안 스캔

이미지를 빌드했다면 보안 취약점 스캔을 실행해야 합니다. CI 단계에서 자동 검증하는 것이 가장 효과적입니다.

### Trivy를 사용한 취약점 스캔

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image --severity HIGH,CRITICAL myapp:1.0

# Fail CI if vulnerabilities found
trivy image --exit-code 1 --severity CRITICAL myapp:1.0
```

스캔은 빌드 직후에 실행하고, CRITICAL 취약점이 있으면 파이프라인을 멈춰야 합니다. 이 단계는 선택이 아니라 배포 전 필수 검증입니다.

### 스캔 결과 읽기

Trivy는 CVE 번호, 심각도, 영향받는 패키지, 고정 버전을 함께 보여줍니다. HIGH 이상 취약점은 즉시 대응해야 하고, MEDIUM은 우선순위를 정해 점진적으로 고쳐야 합니다.

```text
Total: 3 (HIGH: 1, CRITICAL: 2)

Package: openssl
Vulnerability: CVE-2024-1234
Severity: CRITICAL
Fixed Version: 3.0.13
```

취약점 스캔은 이미지를 빌드한 순간의 상태만 알려 줍니다. 따라서 프로덕션에 배포된 이미지도 주기적으로 재스캔해 새로 발견된 CVE에 대응해야 합니다.

## 자주 하는 실수 5가지

1. **`latest` 태그를 쓰는 실수**입니다. 재현성이 사라지므로 항상 버전을 고정해야 합니다.
2. **`COPY . .`를 처음에 두는 실수**입니다. 캐시가 쉽게 깨져 빌드 시간이 계속 길어집니다.
3. **시크릿을 이미지 안에 굽는 실수**입니다. `docker history`만으로도 흔적이 드러날 수 있습니다.
4. **루트 계정으로 실행하는 실수**입니다. 컨테이너 탈출 시 피해 범위가 커집니다.
5. **이미지를 과도하게 크게 만드는 실수**입니다. push, pull, 콜드 스타트 모두 느려집니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 distroless, SBOM 생성, 이미지 서명, 취약점 스캔을 CI 파이프라인에 붙입니다. 이미지 빌드는 이제 단순 배포 준비가 아니라 소프트웨어 공급망 보안의 일부입니다.

작은 팀도 최소한 이미지 크기 관리, non-root 실행, 취약점 스캔 세 가지는 초기에 습관으로 들이는 편이 좋습니다.

## 시니어 엔지니어는 이렇게 봅니다

- 이미지는 변경 불가능해야 합니다. 수정이 필요하면 새 이미지를 만듭니다.
- 작은 이미지가 더 안전하고 운영 비용도 낮습니다.
- .dockerignore는 .gitignore만큼 중요합니다.
- 빌드 속도는 개발 속도와 직결됩니다.
- 이미지 서명은 공급망 보호의 핵심 장치입니다.

## 체크리스트

- [ ] Dockerfile이 non-root 계정으로 끝납니다.
- [ ] multi-stage로 최종 이미지 크기를 줄였습니다.
- [ ] .dockerignore가 .git, tests, docs를 제외합니다.
- [ ] CI에 취약점 스캔이 포함됩니다.

## 연습 문제

1. 현재 앱의 최종 이미지 크기를 200MB 이하로 줄여 보세요.
2. multi-stage 적용 전후의 빌드 시간을 비교해 보세요.
3. Trivy로 HIGH/CRITICAL 취약점을 점검해 보세요.

## 정리 및 다음 단계

컨테이너는 실행 환경을 얼려서 전달하는 방식입니다. 다음 글에서는 이렇게 배포된 서비스를 운영 중에 어떻게 관찰할지 모니터링과 알림을 다룹니다.

## 컨테이너 빌드를 운영 품질 관점으로 확장하기

컨테이너는 포장 기술이지만, 빌드 방식은 보안과 성능을 동시에 결정합니다. 이미지 크기, 레이어 구성, 베이스 이미지, 서명과 스캔 정책이 모두 운영 리스크에 직접 연결됩니다.

### 오케스트레이션 비교 관점

| 항목 | Docker Compose | Kubernetes |
| --- | --- | --- |
| 목표 | 로컬/소규모 멀티컨테이너 실행 | 대규모 운영 오케스트레이션 |
| 복구 | 수동 또는 단순 재시작 | 자동 스케줄링/자가 복구 |
| 확장 | 제한적 | HPA/클러스터 오토스케일 |
| 네트워크 | 단순 서비스 디스커버리 | Service/Ingress 정책 기반 |
| 운영 난이도 | 낮음 | 높음 |

### 멀티스테이지 Dockerfile 예시

```dockerfile
FROM python:3.12 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH="/root/.local/bin:${PATH}"
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose 배포 검증용 스택

```yaml
version: "3.9"
services:
  api:
    image: ghcr.io/example/api:1.2.0
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 2s
      retries: 3
  redis:
    image: redis:7
```

### 이미지 품질 체크 표

| 항목 | 권장 기준 |
| --- | --- |
| 태그 | `latest` 금지, semver 또는 sha 태그 |
| 크기 | 불필요한 빌드 도구 제거 |
| 계정 | non-root 실행 |
| 취약점 | HIGH/CRITICAL 차단 |
| SBOM | 생성 및 저장 |

### 보안 스캔 자동화 예시

```yaml
- name: Trivy image scan
  uses: aquasecurity/trivy-action@0.24.0
  with:
    image-ref: ghcr.io/example/api:${{ github.sha }}
    severity: HIGH,CRITICAL
    exit-code: "1"
```

### 운영 연결 포인트

1. 빌드 산출물 이미지는 불변(immutable)으로 다룹니다.
2. 장애 대응 시 컨테이너 내부 수정보다 새 이미지 배포를 원칙으로 합니다.
3. 이미지 서명과 검증 정책을 도입해 공급망 위협을 줄입니다.
4. 빌드 시간, 이미지 크기, 취약점 수를 릴리스 지표로 관리합니다.

컨테이너 빌드가 안정되면 배포 논의가 기술 세부 대신 운영 정책 중심으로 전환됩니다. 이것이 DevOps 성숙의 중요한 신호입니다.


## 운영 앵커: 배포, 인프라, 관측성, 대응을 한 장으로 연결하기

앞선 섹션에서 각 주제를 따로 설명했다면, 이 섹션은 실무에서 한 번에 연결해 쓰는 최소 구성 예시를 제공합니다. 핵심은 화려한 도구 조합이 아니라, 같은 기준으로 변경을 통과시키고 문제를 되돌릴 수 있는가입니다.

### CI/CD 파이프라인 공통 YAML

```yaml
name: delivery-flow
on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q

  deploy-stage:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_stage.sh
      - run: ./scripts/smoke_test.sh https://stage.example.com

  deploy-prod-canary:
    needs: deploy-stage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_prod.sh --strategy canary --percent 10
      - run: ./scripts/check_slo.sh --window 5m
      - run: ./scripts/promote_or_rollback.sh
```

이 흐름의 실전 포인트는 세 가지입니다. 첫째, CI 통과 전에는 어떤 배포도 시작하지 않습니다. 둘째, stage 통과 후에만 production으로 승격합니다. 셋째, production 승격은 canary 관찰 통과를 조건으로 강제합니다.

### Terraform과 Ansible 역할 분리 예시

```hcl
# infra/main.tf
resource "aws_security_group" "api" {
  name        = "api-sg"
  description = "api security group"
}

resource "aws_instance" "api" {
  ami           = var.ami
  instance_type = "t3.small"
  tags = {
    service = "api"
    env     = var.env
  }
}
```

```yaml
# ops/playbooks/hardening.yml
- hosts: api
  become: true
  tasks:
    - name: Install security updates
      apt:
        update_cache: true
        upgrade: dist

    - name: Ensure auditd is installed
      apt:
        name: auditd
        state: present

    - name: Ensure ssh root login is disabled
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin'
        line: 'PermitRootLogin no'
```

Terraform은 "무엇을 만들 것인가"를 선언하고, Ansible은 "만들어진 시스템을 어떤 상태로 유지할 것인가"를 담당합니다. 두 도구를 구분하면 변경 리뷰 범위가 명확해지고, 장애 시 원인 추적도 빨라집니다.

### 모니터링/알림 설정 예시

```yaml
# monitoring/alerts.yml
groups:
  - name: api-slo
    rules:
      - alert: ApiHighErrorRate
        expr: rate(http_requests_total{service="api",status=~"5.."}[5m]) / rate(http_requests_total{service="api"}[5m]) > 0.01
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "API 5xx 비율 1% 초과"
          runbook: "https://internal/wiki/runbooks/api-high-error-rate"

      - alert: ApiHighLatencyP95
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="api"}[5m])) by (le)) > 0.35
        for: 10m
        labels:
          severity: warning
```

알림은 많이 울리는 것이 목표가 아닙니다. 운영자가 실제로 행동할 수 있는 신호만 남기고, 모든 page 알림에 runbook 링크를 붙여 대응 시작 시간을 줄여야 합니다.

### 블루그린/카나리 승격 절차 예시

```bash
# blue-green switch
./scripts/deploy_blue.sh
./scripts/smoke_test.sh https://blue.example.com
./scripts/switch_traffic.sh --from green --to blue

# canary rollout
./scripts/deploy_canary.sh --percent 10
./scripts/check_metrics.sh --window 5m
./scripts/promote_canary.sh --to 50
./scripts/promote_canary.sh --to 100
```

블루그린은 즉시 전환과 즉시 롤백에 유리하고, 카나리는 위험을 작게 나눠 검증하는 데 유리합니다. 서비스 특성과 팀 역량에 따라 전략을 고르되, 승격/철수 명령을 반드시 런북과 자동화 스크립트로 함께 유지해야 합니다.

### 인시던트 대응 런북 예시

```markdown
# Runbook: API 5xx 급증

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

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

## 처음 질문으로 돌아가기

- **컨테이너는 VM과 무엇이 다르고 왜 배포 재현성에 유리할까요?**
  - 본문의 기준은 컨테이너와 빌드를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Dockerfile에서 꼭 이해해야 할 기본 명령은 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **multi-stage build는 이미지 크기와 보안에 어떤 차이를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- **컨테이너와 빌드 (현재 글)**
- 모니터링과 알림 (예정)
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [Docker docs](https://docs.docker.com/)
- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [Trivy](https://trivy.dev/)
- [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, Docker, Container, Build, Image
