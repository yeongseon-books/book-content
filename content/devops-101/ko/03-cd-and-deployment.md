---
series: devops-101
episode: 3
title: "DevOps 101 (3/10): CD와 배포 전략"
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
  - CD
  - Deployment
  - BlueGreen
  - Canary
seo_description: 되돌릴 수 있는 자동 배포를 위해 CD와 배포 전략의 핵심을 비교합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (3/10): CD와 배포 전략

배포 전략은 단순히 새 코드를 올리는 방식의 차이가 아닙니다. 실패했을 때 얼마나 빠르게 되돌릴 수 있고, 영향 범위를 얼마나 작게 제한할 수 있는지를 결정하는 구조적 차이입니다.

이 글은 DevOps 101 시리즈의 세 번째 글입니다.

![DevOps 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/03/03-01-diagram.ko.png)
*DevOps 101 3장 흐름 개요*
> 모든 배포는 되돌릴 수 있어야 합니다. 배포 전략은 그 되돌림의 속도와 영향 범위를 설계하는 방법입니다.

## 이 글에서 다룰 문제

- Continuous Delivery와 Continuous Deployment의 차이는 무엇일까요?
- Rolling, Blue-Green, Canary 전략은 각각 어떤 위험을 줄이기 위해 쓰일까요?
- 코드 배포와 기능 활성화를 왜 분리해야 할까요?
- 배포 파이프라인에서 자동 롤백은 어떻게 설계할까요?

## Continuous Delivery vs Continuous Deployment

| 구분 | Continuous Delivery | Continuous Deployment |
|------|--------------------|-----------------------|
| 정의 | 언제든 배포 가능한 상태를 유지 | 모든 통과 변경을 자동으로 프로덕션에 배포 |
| 승인 | 마지막 단계에 수동 승인 | 승인 없이 자동 배포 |
| 적합 | 규제 산업, 대형 서비스 | 빠른 이터레이션이 중요한 서비스 |
| 전제 | 강력한 테스트 커버리지, 모니터링 | Delivery의 전제 + 자동 롤백 |

## 배포 전략 비교

| 전략 | 설명 | 장점 | 단점 |
|------|------|------|------|
| 재배포 (Recreate) | 기존 종료 후 새 버전 시작 | 단순, 비용 낮음 | 다운타임 발생 |
| 롤링 (Rolling) | 인스턴스를 순서대로 교체 | 다운타임 없음, 추가 리소스 불필요 | 롤백 느림, 두 버전 공존 |
| 블루-그린 (Blue-Green) | 동일 환경 두 벌 유지, 전환 | 즉각 롤백, 안정적 테스트 | 비용 2배, 데이터 동기화 복잡 |
| 카나리 (Canary) | 일부 트래픽만 새 버전으로 | 위험 최소화, 점진적 신뢰 구축 | 모니터링 복잡, 두 버전 공존 |

## 카나리 배포 구현

```yaml
# Argo Rollouts 카나리 배포 예시
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-api
spec:
  replicas: 10
  selector:
    matchLabels:
      app: order-api
  template:
    metadata:
      labels:
        app: order-api
    spec:
      containers:
        - name: order-api
          image: registry.example.com/order-api:v2.0.0
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          resources:
            requests:
              memory: 256Mi
              cpu: 100m
            limits:
              memory: 512Mi
              cpu: 500m

  strategy:
    canary:
      steps:
        # 1단계: 10% 트래픽으로 시작
        - setWeight: 10
        - pause:
            duration: 5m    # 5분 대기 후 지표 확인

        # 2단계: 지표 확인 후 25%로 증가
        - setWeight: 25
        - pause:
            duration: 10m

        # 3단계: 에러율이 임계값 이하인 경우 50%로
        - setWeight: 50
        - pause:
            duration: 10m

        # 4단계: 100%
        - setWeight: 100

      # 자동 분석 - 오류율 임계값 초과 시 자동 롤백
      analysis:
        templates:
          - templateName: error-rate-check
        startingStep: 1
        args:
          - name: service-name
            value: order-api
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-check
spec:
  args:
    - name: service-name
  metrics:
    - name: error-rate
      interval: 1m
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              job="{{ args.service-name }}",
              status_code=~"5.."
            }[2m])) /
            sum(rate(http_requests_total{
              job="{{ args.service-name }}"
            }[2m])) * 100
      successCondition: result[0] < 1.0    # 오류율 1% 미만
      failureCondition: result[0] >= 5.0   # 오류율 5% 이상이면 실패
```

## 블루-그린 배포 구현

```yaml
# GitHub Actions - 블루-그린 배포
name: Blue-Green Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: 현재 활성 환경 확인
        id: current-env
        run: |
          CURRENT=$(aws elbv2 describe-target-groups \
            --names order-api-active \
            --query 'TargetGroups[0].Tags[?Key==`env`].Value' \
            --output text)
          echo "current=$CURRENT" >> $GITHUB_OUTPUT
          echo "next=$([[ "$CURRENT" == "blue" ]] && echo "green" || echo "blue")" >> $GITHUB_OUTPUT

      - name: 비활성 환경에 새 버전 배포
        run: |
          NEXT="${{ steps.current-env.outputs.next }}"
          aws ecs update-service \
            --cluster production \
            --service "order-api-$NEXT" \
            --task-definition "order-api:${{ github.run_number }}" \
            --force-new-deployment

      - name: 배포 완료 대기
        run: |
          aws ecs wait services-stable \
            --cluster production \
            --services "order-api-${{ steps.current-env.outputs.next }}"

      - name: 헬스 체크
        run: |
          NEXT="${{ steps.current-env.outputs.next }}"
          TARGET_GROUP="order-api-$NEXT-tg"

          # 모든 타겟이 healthy 상태인지 확인
          UNHEALTHY=$(aws elbv2 describe-target-health \
            --target-group-arn $(aws elbv2 describe-target-groups \
              --names $TARGET_GROUP \
              --query 'TargetGroups[0].TargetGroupArn' \
              --output text) \
            --query 'TargetHealthDescriptions[?TargetHealth.State!=`healthy`]' \
            --output text)

          if [ -n "$UNHEALTHY" ]; then
            echo "헬스 체크 실패: $UNHEALTHY"
            exit 1
          fi

      - name: 트래픽 전환
        run: |
          NEXT="${{ steps.current-env.outputs.next }}"
          LISTENER_ARN=$(aws elbv2 describe-listeners \
            --load-balancer-arn ${{ secrets.ALB_ARN }} \
            --query 'Listeners[0].ListenerArn' \
            --output text)

          aws elbv2 modify-listener \
            --listener-arn $LISTENER_ARN \
            --default-actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups \
              --names "order-api-$NEXT-tg" \
              --query 'TargetGroups[0].TargetGroupArn' \
              --output text)

      - name: 롤백 (실패 시)
        if: failure()
        run: |
          CURRENT="${{ steps.current-env.outputs.current }}"
          echo "배포 실패. $CURRENT 환경으로 롤백합니다."
          # 트래픽을 기존 환경으로 되돌림
          LISTENER_ARN=$(aws elbv2 describe-listeners \
            --load-balancer-arn ${{ secrets.ALB_ARN }} \
            --query 'Listeners[0].ListenerArn' \
            --output text)
          aws elbv2 modify-listener \
            --listener-arn $LISTENER_ARN \
            --default-actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups \
              --names "order-api-$CURRENT-tg" \
              --query 'TargetGroups[0].TargetGroupArn' \
              --output text)
```

## 피처 플래그로 배포와 기능 분리

코드 배포(기술적 릴리즈)와 기능 활성화(비즈니스 릴리즈)를 분리하면 배포 위험을 크게 줄입니다.

```python
import os
import json
import boto3
from functools import lru_cache
from typing import Any


class FeatureFlags:
    """AWS AppConfig 기반 피처 플래그"""

    def __init__(self):
        self._client = boto3.client("appconfig")
        self._app = os.environ["APPCONFIG_APP"]
        self._env = os.environ["APPCONFIG_ENV"]
        self._profile = os.environ["APPCONFIG_PROFILE"]
        self._flags: dict = {}

    def refresh(self) -> None:
        """플래그 설정 최신화"""
        response = self._client.get_configuration(
            Application=self._app,
            Environment=self._env,
            Configuration=self._profile,
            ClientId="order-service",
        )
        if response["Content"].read():
            self._flags = json.loads(response["Content"].read())

    def is_enabled(self, flag_name: str, user_id: str = None) -> bool:
        """피처 플래그 활성화 여부 확인"""
        flag = self._flags.get(flag_name, {})

        if not flag.get("enabled", False):
            return False

        # 특정 사용자 화이트리스트
        if user_id and user_id in flag.get("whitelist", []):
            return True

        # 비율 기반 롤아웃
        rollout_pct = flag.get("rollout_percentage", 0)
        if rollout_pct >= 100:
            return True
        if rollout_pct <= 0:
            return False
        if user_id:
            # 사용자 ID 기반 결정적 해시 (같은 사용자는 항상 같은 결과)
            hash_val = hash(f"{flag_name}:{user_id}") % 100
            return hash_val < rollout_pct

        return False


_feature_flags = FeatureFlags()


def handler(event: dict, context: Any) -> dict:
    user_id = event.get("user_id")

    # 새 결제 플로우 피처 플래그 확인
    if _feature_flags.is_enabled("new-checkout-flow", user_id=user_id):
        return new_checkout(event)
    else:
        return legacy_checkout(event)


def new_checkout(event: dict) -> dict:
    return {"flow": "new", "status": "success"}


def legacy_checkout(event: dict) -> dict:
    return {"flow": "legacy", "status": "success"}
```

## 배포 후 자동 검증

```python
import time
import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class HealthCheckResult:
    passed: bool
    endpoint: str
    status_code: Optional[int]
    response_time_ms: float
    error: Optional[str] = None


def run_post_deploy_checks(base_url: str, timeout_seconds: int = 300) -> bool:
    """배포 후 헬스 체크 실행"""
    checks = [
        {"path": "/health", "expected_status": 200},
        {"path": "/ready", "expected_status": 200},
        {"path": "/api/v1/orders", "expected_status": 401},  # 인증 필요
    ]

    deadline = time.time() + timeout_seconds

    for check in checks:
        url = f"{base_url}{check['path']}"
        passed = False

        while time.time() < deadline:
            start = time.perf_counter()
            try:
                response = requests.get(url, timeout=5)
                duration_ms = (time.perf_counter() - start) * 1000

                if response.status_code == check["expected_status"]:
                    print(f"PASS {url} ({response.status_code}) {duration_ms:.0f}ms")
                    passed = True
                    break
                else:
                    print(f"WAIT {url} ({response.status_code} != {check['expected_status']})")

            except requests.RequestException as e:
                print(f"WAIT {url}: {e}")

            time.sleep(5)

        if not passed:
            print(f"FAIL {url}: 타임아웃")
            return False

    return True
```

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 배포와 기능 노출을 동시에 | 롤백 시 코드와 기능이 함께 내려감 | 피처 플래그로 코드 배포와 기능 활성화 분리 |
| 롤백 계획 없이 배포 | 실패 시 수동 복구로 수 시간 소요 | 배포 전 롤백 절차 문서화 및 자동화 |
| 카나리 비율 너무 빠르게 증가 | 문제 파악 전 전체 트래픽 노출 | 최소 5분 이상 각 단계 관찰 |
| 블루-그린에서 DB 마이그레이션 동시 진행 | 두 버전 공존 중 스키마 불일치 | 하위 호환 마이그레이션 먼저, 기능 배포 후 정리 |
| 배포 후 모니터링 미확인 | 느린 오류 증가를 한참 후 발견 | 배포 후 15분간 핵심 지표 의무 확인 |
| CD 없이 수동 배포 | 배포마다 다른 결과, 실수 가능성 | 모든 배포를 파이프라인을 통해서만 진행 |

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- **DevOps 101 (3/10): CD와 배포 전략 (현재 글)**
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)

<!-- toc:end -->

## 참고 자료

- [Martin Fowler — Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Argo Rollouts](https://argoproj.github.io/rollouts/)
- [LaunchDarkly — Feature Flags](https://launchdarkly.com/blog/what-are-feature-flags/)
- [Spinnaker](https://spinnaker.io/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)
