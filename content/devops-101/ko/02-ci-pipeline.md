---
series: devops-101
episode: 2
title: "DevOps 101 (2/10): CI 파이프라인"
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
  - CI
  - GitHub Actions
  - Automation
  - Pipeline
seo_description: 모든 PR에 같은 검사를 적용하는 CI 파이프라인 설계 원칙을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (2/10): CI 파이프라인

CI를 처음 시작할 때 가장 먼저 부딪히는 질문이 "GitHub Actions를 써야 하나, Jenkins를 써야 하나?"입니다. 하지만 도구보다 더 중요한 것은 "어떤 검사를 자동화할 것인가"입니다. CI 파이프라인은 팀의 합격선을 코드로 고정하는 장치입니다.

이 글은 DevOps 101 시리즈의 두 번째 글입니다.

![DevOps 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/02/02-01-diagram.ko.png)
*DevOps 101 2장 흐름 개요*
> CI 파이프라인은 모든 PR에 동일한 품질 기준을 적용해 사람의 실수를 줄이고 피드백을 빠르게 만드는 자동화 장치입니다.

## 이 글에서 다룰 문제

- CI 파이프라인은 단순한 테스트 자동화와 어떻게 다를까요?
- build, test, lint, scan 단계를 왜 한 흐름으로 묶어야 할까요?
- 빠른 피드백을 주는 파이프라인은 어떤 순서로 설계해야 할까요?
- 파이프라인 실패를 팀이 어떻게 다루어야 할까요?

## CI 도구 선택 기준

| 도구 | 장점 | 단점 | 적합한 팀 |
|------|------|------|----------|
| GitHub Actions | 코드와 동일 저장소, 무료 분 제공 | 자체 호스팅 시 관리 필요 | GitHub 사용 팀 |
| GitLab CI | 내장 레지스트리, 통합 강함 | GitLab 종속 | GitLab 사용 팀 |
| Jenkins | 완전한 커스터마이징 | 유지보수 부담 높음 | 복잡한 온프레미스 환경 |
| CircleCI | 설정 간결, 병렬 실행 좋음 | 유료 플랜 필요 | SaaS 중심 팀 |

도구 선택보다 "파이프라인이 5분 안에 완료되는가"가 더 중요합니다. 피드백이 느리면 개발자가 파이프라인을 기다리지 않고 다음 작업을 시작합니다.

## 파이프라인 단계 설계

좋은 CI 파이프라인은 빠른 실패(fast fail) 원칙을 따릅니다. 가장 빠른 검사를 먼저 실행해 문제를 조기에 발견합니다.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"
  POETRY_VERSION: "1.8.0"

jobs:
  # 1단계: 빠른 정적 검사 (1-2분)
  static-checks:
    name: 린트와 타입 검사
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: 의존성 설치 (dev)
        run: pip install -r requirements-dev.txt

      - name: ruff 린트
        run: ruff check . --output-format=github

      - name: ruff 포맷 검사
        run: ruff format . --check

      - name: mypy 타입 검사
        run: mypy src/ --ignore-missing-imports

  # 2단계: 테스트 (3-5분)
  test:
    name: 테스트
    runs-on: ubuntu-latest
    needs: static-checks    # 린트 통과 후 실행
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: 의존성 설치
        run: pip install -r requirements-dev.txt

      - name: 테스트 실행
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          ENVIRONMENT: test
        run: |
          pytest \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=80 \
            -v \
            --tb=short

      - name: 커버리지 업로드
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  # 3단계: 보안 스캔 (2-3분, 테스트와 병렬)
  security-scan:
    name: 보안 스캔
    runs-on: ubuntu-latest
    needs: static-checks
    steps:
      - uses: actions/checkout@v4

      - name: Trivy 파일시스템 스캔
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
          exit-code: 1
          format: sarif
          output: trivy-results.sarif

      - name: GitHub Security에 결과 업로드
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif

  # 4단계: Docker 이미지 빌드 검증
  build:
    name: 빌드 검증
    runs-on: ubuntu-latest
    needs: [test, security-scan]
    steps:
      - uses: actions/checkout@v4

      - name: Docker Buildx 설정
        uses: docker/setup-buildx-action@v3

      - name: 이미지 빌드 (푸시 없음)
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## 빠른 피드백을 위한 설계 원칙

**원칙 1: 병렬 실행**

의존성이 없는 단계는 병렬로 실행합니다. 테스트와 보안 스캔은 독립적이므로 동시에 실행해 전체 시간을 줄입니다.

**원칙 2: 캐싱 활용**

pip, npm, Maven 캐시를 활용하면 의존성 설치 시간을 대폭 줄일 수 있습니다.

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: pip          # requirements.txt 기반 캐싱
    cache-dependency-path: requirements*.txt
```

**원칙 3: 실패 단계 명확화**

각 단계가 실패했을 때 어디서 실패했는지 즉시 알 수 있어야 합니다.

```python
# 테스트 실패 시 명확한 메시지 출력
import pytest

def test_order_processing():
    """주문 처리 성공 케이스"""
    order = {"id": "123", "amount": 10000, "items": [{"sku": "A1", "qty": 1}]}
    result = process_order(order)
    assert result["status"] == "processed", (
        f"주문 처리 실패: 예상 'processed', 실제 '{result['status']}'"
    )
    assert result["order_id"] == order["id"]
```

## 모노레포에서의 CI 최적화

규모가 큰 모노레포는 변경된 패키지만 빌드하고 테스트하는 영향 분석을 붙입니다.

```yaml
# 변경된 경로만 탐지해 관련 서비스만 CI 실행
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      api-changed: ${{ steps.changes.outputs.api }}
      worker-changed: ${{ steps.changes.outputs.worker }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            api:
              - 'services/api/**'
              - 'shared/**'
            worker:
              - 'services/worker/**'
              - 'shared/**'

  test-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api-changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd services/api && pytest

  test-worker:
    needs: detect-changes
    if: needs.detect-changes.outputs.worker-changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd services/worker && pytest
```

## 파이프라인 품질 지표 모니터링

```python
import json
import requests
from datetime import datetime, timedelta


def get_pipeline_metrics(repo: str, token: str, days: int = 7) -> dict:
    """GitHub Actions 파이프라인 성과 지표 수집"""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    base_url = f"https://api.github.com/repos/{repo}"

    cutoff = datetime.now() - timedelta(days=days)

    response = requests.get(
        f"{base_url}/actions/runs",
        headers=headers,
        params={"per_page": 100, "status": "completed"},
    )
    runs = response.json().get("workflow_runs", [])

    recent_runs = [
        r for r in runs
        if datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).replace(tzinfo=None) >= cutoff
    ]

    if not recent_runs:
        return {"error": "데이터 없음"}

    total = len(recent_runs)
    successful = sum(1 for r in recent_runs if r["conclusion"] == "success")
    failed = sum(1 for r in recent_runs if r["conclusion"] == "failure")

    durations = []
    for run in recent_runs:
        if run.get("run_started_at") and run.get("updated_at"):
            start = datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
            durations.append((end - start).total_seconds() / 60)

    return {
        "period_days": days,
        "total_runs": total,
        "success_rate_pct": round(successful / total * 100, 1),
        "failure_rate_pct": round(failed / total * 100, 1),
        "avg_duration_min": round(sum(durations) / len(durations), 1) if durations else 0,
        "p95_duration_min": round(sorted(durations)[int(len(durations) * 0.95)], 1) if durations else 0,
    }
```

## 파이프라인 실패 처리 원칙

CI 파이프라인이 실패하면 팀 전체가 하던 일을 멈추고 수정해야 합니다. 이것이 "파이프라인은 절대 빨간 상태로 두지 않는다"는 원칙의 근거입니다.

파이프라인 실패 시 처리 절차:

1. 실패한 단계와 오류 메시지를 즉시 확인합니다.
2. 로컬에서 재현합니다 (`act` 도구로 로컬 Actions 실행 가능).
3. 5분 안에 수정이 어려우면 해당 PR을 닫고 별도 브랜치에서 수정합니다.
4. 수정 후 파이프라인이 녹색이 되면 다시 PR을 엽니다.
5. 반복적으로 실패하는 테스트는 격리 표시 후 별도 이슈로 추적합니다.

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 파이프라인 단계를 직렬로만 구성 | 전체 CI 시간이 10분 이상 | 독립적인 단계는 병렬로 실행 |
| 실패한 파이프라인을 방치 | 모든 PR이 실패 상태로 머지됨 | 실패 즉시 최우선 수정 원칙 |
| 테스트 커버리지 없이 운영 | 회귀 버그를 CI에서 잡지 못함 | 최소 80% 커버리지 기준 설정 |
| 시크릿을 코드에 하드코딩 | 보안 취약점, 스캔에서 발견됨 | GitHub Secrets 또는 Vault 사용 |
| 의존성 캐시 없음 | 매 실행마다 pip install로 3-5분 낭비 | `cache: pip` 설정 |
| 보안 스캔 미포함 | 알려진 취약점 라이브러리가 프로덕션에 포함 | Trivy 또는 Snyk을 CI에 필수 추가 |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- **DevOps 101 (2/10): CI 파이프라인 (현재 글)**
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [Trivy](https://trivy.dev/)
- [Bazel](https://bazel.build/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
