---
series: devops-101
episode: 1
title: "DevOps 101 (1/10): DevOps란 무엇인가?"
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
  - Culture
  - CI
  - CD
  - Engineering
seo_description: 개발과 운영을 함께 책임지는 DevOps의 정의와 시작 방법을 정리합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (1/10): DevOps란 무엇인가?

DevOps를 처음 이해하려 할 때 가장 혼란스러운 부분은 이것이 기술이 아니라 문화 전환이라는 사실입니다. 아래 표는 전통 운영과 DevOps가 같은 문제를 어떻게 다르게 풀어내는지 정리한 것입니다.

이 글은 DevOps 101 시리즈의 첫 번째 글입니다.

![DevOps 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/01/01-01-diagram.ko.png)
*DevOps 101 1장 흐름 개요*
> DevOps는 개발팀과 운영팀이 함께 제품 전체 생명주기를 책임지는 문화이자 실천 방식입니다.

## 이 글에서 다룰 문제

- DevOps는 무엇이며, 왜 개발과 운영을 따로 보는 방식이 한계에 부딪혔을까요?
- DevOps를 도구가 아니라 문화라고 말하는 이유는 무엇일까요?
- CI, CD, SRE 같은 용어는 DevOps 흐름 안에서 어떤 역할을 할까요?
- 팀이 처음 DevOps를 시작할 때 무엇부터 바꿔야 할까요?

## 전통 운영과 DevOps의 차이

| 관점 | 전통 운영 | DevOps |
|------|----------|--------|
| 책임 경계 | 개발팀은 코드, 운영팀은 배포·운영 | 한 팀이 개발부터 운영까지 |
| 배포 주기 | 분기 또는 월 단위 대규모 배포 | 작은 변경을 자주 배포 |
| 장애 대응 | 운영팀이 온콜, 개발팀은 티켓 수신 | 개발자가 온콜, 자기 코드 책임 |
| 인프라 관리 | 수동 설정, 개인 지식 의존 | 코드로 관리, 리뷰·버전 관리 |
| 피드백 루프 | 느림 (운영 → 개발 이슈 트래킹) | 빠름 (모니터링 → 개발자 직접 확인) |

전통 방식에서 가장 큰 문제는 피드백 루프가 길다는 것입니다. 배포 후 문제가 생겨도 운영팀이 이슈를 만들고 개발팀이 검토하기까지 며칠이 걸립니다. DevOps에서는 개발자가 자기 서비스의 알람을 직접 받고 대응합니다.

## CALMS 프레임워크

CALMS는 DevOps 실천을 평가하는 다섯 가지 축입니다.

| 축 | 의미 | 초기 지표 예시 |
|----|------|--------------|
| Culture | 책임 공유, 실패를 학습으로 보는 시각 | 블레임 없는 포스트모텀 문화 |
| Automation | 반복 작업의 자동화 | CI 파이프라인 도입률 |
| Lean | 작은 배치, 빠른 흐름 | 배포당 변경 파일 수 감소 |
| Measurement | 데이터 기반 의사결정 | DORA 지표 측정 여부 |
| Sharing | 지식과 도구 공유 | 런북, 포스트모텀 공유 비율 |

## DORA 지표로 DevOps 성숙도 측정

DORA(DevOps Research and Assessment) 지표는 DevOps 팀의 성과를 측정하는 산업 표준입니다.

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class DeploymentRecord:
    deployed_at: datetime
    commit_sha: str
    lead_time_hours: float      # 첫 커밋부터 프로덕션 배포까지
    restored_at: Optional[datetime] = None  # 장애 복구 시각
    failed: bool = False


def calculate_dora_metrics(deployments: list[DeploymentRecord], days: int = 30) -> dict:
    """DORA 4대 지표 계산"""
    cutoff = datetime.now() - timedelta(days=days)
    recent = [d for d in deployments if d.deployed_at >= cutoff]

    if not recent:
        return {"error": "배포 기록 없음"}

    # 1. 배포 빈도 (Deployment Frequency)
    deploy_freq_per_day = len(recent) / days

    # 2. 변경 리드 타임 (Lead Time for Changes)
    avg_lead_time_hours = sum(d.lead_time_hours for d in recent) / len(recent)

    # 3. 변경 실패율 (Change Failure Rate)
    failed_count = sum(1 for d in recent if d.failed)
    change_failure_rate = failed_count / len(recent) * 100

    # 4. 복구 시간 (Time to Restore Service)
    failed_with_restore = [
        d for d in recent if d.failed and d.restored_at
    ]
    if failed_with_restore:
        restore_times = [
            (d.restored_at - d.deployed_at).total_seconds() / 3600
            for d in failed_with_restore
        ]
        avg_restore_hours = sum(restore_times) / len(restore_times)
    else:
        avg_restore_hours = 0

    # 성숙도 등급 분류 (DORA 2023 기준)
    def classify_freq(f: float) -> str:
        if f >= 1: return "Elite (하루 1회 이상)"
        if f >= 1/7: return "High (주 1회 이상)"
        if f >= 1/30: return "Medium (월 1회 이상)"
        return "Low (월 1회 미만)"

    return {
        "period_days": days,
        "total_deployments": len(recent),
        "deploy_frequency_per_day": round(deploy_freq_per_day, 3),
        "deploy_frequency_grade": classify_freq(deploy_freq_per_day),
        "avg_lead_time_hours": round(avg_lead_time_hours, 1),
        "change_failure_rate_pct": round(change_failure_rate, 1),
        "avg_restore_time_hours": round(avg_restore_hours, 1),
    }
```

## 2주 부트스트랩: DevOps 시작하기

처음부터 거대한 플랫폼을 만들 필요는 없습니다. 핵심 자동화를 먼저 구축하면 2주 안에 체감 가능한 변화를 만들 수 있습니다.

```yaml
# GitHub Actions - 2주 부트스트랩 CI 파이프라인
name: bootstrap-ci

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: 의존성 설치
        run: pip install -r requirements-dev.txt

      - name: 린트 (ruff)
        run: ruff check .

      - name: 타입 검사 (mypy)
        run: mypy src/

      - name: 테스트 (pytest)
        run: pytest --cov=src --cov-report=term-missing

      - name: 취약점 스캔 (trivy)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
          exit-code: 1
```

## DevOps가 아닌 것들

DevOps를 도입하면서 자주 빠지는 함정이 있습니다.

**DevOps는 팀 이름이 아닙니다.** "DevOps 팀"을 만들어서 개발팀과 운영팀 사이에 끼워 넣으면, 경계만 하나 더 추가됩니다. DevOps는 기존 팀의 작동 방식이 바뀌는 것입니다.

**DevOps는 도구 집합이 아닙니다.** Kubernetes, Terraform, Prometheus를 도입해도 개발자가 자기 서비스의 운영 상태를 신경 쓰지 않으면 DevOps가 아닙니다.

**DevOps는 개발자가 운영까지 다 하는 것이 아닙니다.** 개발자가 온콜을 서야 한다는 뜻이지만, 플랫폼 팀이 도구와 인프라를 제공해 개발자가 운영 부담을 최소화할 수 있도록 지원해야 합니다.

## CI, CD, SRE의 관계

| 용어 | 범위 | DevOps 흐름에서의 역할 |
|------|------|----------------------|
| CI (Continuous Integration) | 코드 병합 ~ 테스트 | 품질 게이트 자동화 |
| CD (Continuous Delivery/Deployment) | 테스트 통과 ~ 배포 | 안전한 릴리즈 자동화 |
| SRE (Site Reliability Engineering) | 운영 ~ 복구 ~ 개선 | 신뢰성 목표 정의와 달성 |

SRE는 DevOps의 특정 구현 방식으로 볼 수 있습니다. Google이 제시한 SRE 방식은 소프트웨어 엔지니어링 원칙으로 운영 문제를 해결합니다. SLO, 에러 버짓, 포스트모텀이 SRE의 핵심 도구입니다.

## 운영 가시성 기초

DevOps의 측정 원칙을 실현하려면 서비스 상태를 한눈에 볼 수 있어야 합니다.

```python
import time
import json
from datetime import datetime, timezone
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 핵심 4대 황금 지표 (Google SRE Book)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "총 HTTP 요청 수",
    ["method", "path", "status_code"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP 요청 처리 시간",
    ["method", "path"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)
ERROR_COUNT = Counter(
    "http_errors_total",
    "HTTP 오류 수",
    ["method", "path", "error_type"],
)
ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "현재 처리 중인 요청 수",
)


def track_request(method: str, path: str):
    """요청 지표 추적 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            ACTIVE_REQUESTS.inc()
            start = time.time()
            status_code = 200
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                ERROR_COUNT.labels(
                    method=method,
                    path=path,
                    error_type=type(e).__name__,
                ).inc()
                raise
            finally:
                duration = time.time() - start
                REQUEST_COUNT.labels(
                    method=method,
                    path=path,
                    status_code=str(status_code),
                ).inc()
                REQUEST_DURATION.labels(method=method, path=path).observe(duration)
                ACTIVE_REQUESTS.dec()
        return wrapper
    return decorator
```

## DORA 지표 등급 기준표

DORA 2023 기준으로 팀 성숙도를 판단할 때 아래 표를 참고합니다.

| 지표 | Elite | High | Medium | Low |
|---|---|---|---|---|
| 배포 빈도 | 하루 여러 번 | 하루~주 1회 | 주 1회~월 1회 | 월 1회 미만 |
| 변경 리드 타임 | 1시간 미만 | 1일 미만 | 1주 미만 | 1개월 이상 |
| 변경 실패율 | 5% 미만 | 10% 미만 | 15% 미만 | 15% 이상 |
| 복구 시간 | 1시간 미만 | 1일 미만 | 1주 미만 | 1주 이상 |

이 네 가지 숫자를 매월 기록하면 팀의 진행 방향을 데이터로 확인할 수 있습니다.

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| DevOps 팀을 별도 조직으로 만듦 | 개발-DevOps-운영 세 계층으로 경계 증가 | 기존 팀의 작동 방식을 변경하는 방향으로 접근 |
| 도구 도입 = DevOps 완료로 인식 | Kubernetes 도입 후 배포 속도나 안정성 개선 없음 | 도구보다 피드백 루프 단축에 집중 |
| DORA 지표 없이 성과 주장 | 개선됐다는 느낌만 있고 측정 데이터 없음 | 배포 빈도, 리드 타임, 실패율 측정부터 시작 |
| 자동화 없이 프로세스만 강화 | 체크리스트가 늘어나고 사람이 수동 검증 | 코드 리뷰 + CI 파이프라인으로 자동화 |
| 블레임 문화에서 포스트모텀 작성 | 보고서가 책임 추궁 문서로 전락 | 비블레임 원칙을 명시하고 학습 중심으로 진행 |
| 배포와 기능 활성화를 구분 안 함 | 배포 = 사용자 노출, 롤백이 어려움 | 피처 플래그로 배포와 기능 노출을 분리 |

## 처음 질문으로 돌아가기

- **DevOps는 무엇이며, 왜 개발과 운영을 따로 보는 방식이 한계에 부딪혔을까요?**
  - DevOps는 개발팀과 운영팀이 제품 전체 생명주기를 함께 책임지는 문화이자 실천 방식입니다. 개발과 운영을 분리하면 피드백 루프가 길어져 문제 발견과 해결 사이의 시간이 늘어납니다. 배포 속도가 느리고, 장애가 나면 책임 소재 논의부터 시작하는 패턴이 반복됩니다.

- **DevOps를 도구가 아니라 문화라고 말하는 이유는 무엇일까요?**
  - Kubernetes, Terraform, Prometheus 같은 도구는 CALMS 프레임워크의 Automation 축에만 해당합니다. Culture, Lean, Measurement, Sharing이 함께 바뀌지 않으면 도구는 복잡성만 추가합니다. 개발자가 자기 서비스의 운영 상태를 책임지는 마인드셋 변화가 도구보다 먼저입니다.

- **CI, CD, SRE 같은 용어는 DevOps 흐름 안에서 어떤 역할을 할까요?**
  - CI는 코드 병합 단계에서 품질 게이트를 자동화합니다. CD는 테스트를 통과한 변경이 안전하게 배포되는 경로를 만듭니다. SRE는 신뢰성 목표(SLO)를 정의하고 에러 버짓을 통해 배포 속도와 안정성 사이의 균형을 데이터로 관리합니다. 세 가지 모두 "개발자가 운영까지 책임진다"는 DevOps 원칙의 구체적인 구현입니다.

- **팀이 처음 DevOps를 시작할 때 무엇부터 바꿔야 할까요?**
  - 두 가지를 먼저 시작합니다. 첫째, DORA 지표 측정입니다. 배포 빈도, 리드 타임, 변경 실패율, 복구 시간을 기록하면 현재 상태를 숫자로 알 수 있습니다. 둘째, CI 파이프라인 구축입니다. 린트, 테스트, 취약점 스캔을 자동화하면 인간의 수동 게이트 의존을 줄일 수 있습니다. 문화 변화는 이 두 가지가 자리를 잡은 뒤에 자연스럽게 따라옵니다.

<!-- toc:begin -->
## 시리즈 목차

- **DevOps 101 (1/10): DevOps란 무엇인가? (현재 글)**
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
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

- [The Phoenix Project (Gene Kim)](https://itrevolution.com/product/the-phoenix-project/)
- [Accelerate (Nicole Forsgren et al.)](https://itrevolution.com/product/accelerate/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [DORA Research](https://dora.dev/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
