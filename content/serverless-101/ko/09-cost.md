---
series: serverless-101
episode: 9
title: "Serverless 101 (9/10): 비용"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Serverless
  - Cost
  - FinOps
  - Pricing
  - Cloud
seo_description: 서버리스 비용 구조, GB-초 계산, 메모리 최적화, 비용 알람 설정과 FinOps 전략을 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (9/10): 비용

서버리스는 "사용한 만큼만 지불한다"는 매력적인 가격 모델을 가지고 있습니다. 하지만 이 문장이 자주 "저렴하다"와 혼동됩니다. 사용량이 많아지면 비용도 그만큼 커지고, 주변 서비스(DynamoDB, S3, API Gateway, CloudWatch)의 비용이 Lambda 실행 비용보다 더 커지는 경우도 흔합니다.

이 글은 Serverless 101 시리즈의 9번째 글입니다.

![Serverless 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/09/09-01-concept-at-a-glance.ko.png)
*Serverless 101 9장 흐름 개요*
> 서버리스 비용은 호출 수 × 실행 시간 × 메모리로 계산되지만, 실제 청구서는 주변 서비스까지 포함합니다.

## 이 글에서 다룰 문제

- Lambda 비용은 어떻게 계산되나요?
- 메모리 설정은 비용과 성능에 어떤 영향을 줄까요?
- 주변 서비스 비용은 어떻게 예측할 수 있을까요?
- 비용 급증을 어떻게 빠르게 감지할 수 있을까요?
- 비용을 줄이는 실질적인 방법은 무엇인가요?

## Lambda 비용 계산 구조

Lambda 비용은 두 가지 요소로 구성됩니다.

**1. 요청 수 비용**
- 월 100만 건까지 무료
- 이후 100만 건당 $0.20

**2. 실행 시간 비용 (GB-초)**
- 월 400,000 GB-초까지 무료
- 이후 GB-초당 $0.0000166667

GB-초 계산:
```
GB-초 = (메모리 MB / 1024) × 실행 시간(초)

예시:
- 메모리 512MB, 실행 시간 200ms
- GB-초 = (512 / 1024) × 0.2 = 0.1 GB-초
- 월 100만 건 처리 시: 100,000 GB-초
- 비용: (100,000 - 400,000 무료) = 0 (무료 한도 내)
```

```python
def calculate_lambda_cost(
    monthly_invocations: int,
    avg_duration_ms: float,
    memory_mb: int,
    region: str = "ap-northeast-2",
) -> dict:
    """Lambda 월간 비용 추정"""
    # 가격 (2024년 기준, 리전마다 다를 수 있음)
    REQUEST_PRICE = 0.20 / 1_000_000    # 요청당
    GB_SECOND_PRICE = 0.0000166667      # GB-초당
    FREE_REQUESTS = 1_000_000
    FREE_GB_SECONDS = 400_000

    # 요청 비용
    billable_requests = max(0, monthly_invocations - FREE_REQUESTS)
    request_cost = billable_requests * REQUEST_PRICE

    # 실행 시간 비용
    gb_seconds = (memory_mb / 1024) * (avg_duration_ms / 1000) * monthly_invocations
    billable_gb_seconds = max(0, gb_seconds - FREE_GB_SECONDS)
    compute_cost = billable_gb_seconds * GB_SECOND_PRICE

    total_cost = request_cost + compute_cost

    return {
        "monthly_invocations": monthly_invocations,
        "memory_mb": memory_mb,
        "avg_duration_ms": avg_duration_ms,
        "gb_seconds": round(gb_seconds, 2),
        "request_cost_usd": round(request_cost, 4),
        "compute_cost_usd": round(compute_cost, 4),
        "total_cost_usd": round(total_cost, 4),
    }


# 시나리오 비교
scenarios = [
    {"monthly_invocations": 10_000_000, "avg_duration_ms": 100, "memory_mb": 256},
    {"monthly_invocations": 10_000_000, "avg_duration_ms": 100, "memory_mb": 512},
    {"monthly_invocations": 10_000_000, "avg_duration_ms": 50,  "memory_mb": 512},
]

for s in scenarios:
    result = calculate_lambda_cost(**s)
    print(f"메모리 {s['memory_mb']}MB, 실행 {s['avg_duration_ms']}ms: "
          f"${result['total_cost_usd']:.4f}/월")
```

## 메모리와 비용-성능 트레이드오프

메모리를 늘리면 비용이 늘어나는 것처럼 보이지만, 실행 시간이 줄어들어 전체 GB-초는 오히려 감소할 수 있습니다. Lambda에서 CPU 할당은 메모리에 비례하기 때문입니다.

| 메모리 | 평균 실행 시간 | GB-초/요청 | 상대 비용 |
|--------|-------------|-----------|---------|
| 256 MB | 500 ms | 0.125 | 기준 |
| 512 MB | 220 ms | 0.110 | -12% |
| 1024 MB | 120 ms | 0.120 | -4% |
| 2048 MB | 70 ms  | 0.140 | +12% |

이 예시에서 512MB가 256MB보다 빠르고 저렴합니다. 최적 메모리 설정은 함수마다 다르므로 Lambda Power Tuning으로 측정해야 합니다.

```bash
# Lambda Power Tuning을 Step Functions으로 실행
# https://github.com/alexcasalboni/aws-lambda-power-tuning
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:ap-northeast-2:123456789012:stateMachine:powerTuningStateMachine \
  --input '{
    "lambdaARN": "arn:aws:lambda:ap-northeast-2:123456789012:function:order-processor",
    "powerValues": [128, 256, 512, 1024, 2048, 3008],
    "num": 50,
    "payload": {"order_id": "test-123"},
    "parallelInvocation": true,
    "strategy": "cost"
  }'
```

## 주변 서비스 비용 추정

Lambda 실행 비용보다 주변 서비스 비용이 더 클 수 있습니다.

```python
def estimate_total_serverless_cost(monthly_invocations: int) -> dict:
    """서버리스 아키텍처 전체 비용 추정"""

    # Lambda (위 계산 기반)
    lambda_cost = calculate_lambda_cost(
        monthly_invocations=monthly_invocations,
        avg_duration_ms=200,
        memory_mb=512,
    )["total_cost_usd"]

    # API Gateway (HTTP API 기준)
    # 첫 300만 건: $1.00/백만, 이후: $0.90/백만
    if monthly_invocations <= 3_000_000:
        apigw_cost = monthly_invocations / 1_000_000 * 1.00
    else:
        apigw_cost = 3.00 + (monthly_invocations - 3_000_000) / 1_000_000 * 0.90

    # DynamoDB (온디맨드 모드)
    # 읽기: $0.25/백만 RCU, 쓰기: $1.25/백만 WCU
    # 가정: 요청당 1 읽기 + 0.5 쓰기
    rcu_cost = monthly_invocations / 1_000_000 * 0.25
    wcu_cost = monthly_invocations * 0.5 / 1_000_000 * 1.25
    dynamodb_cost = rcu_cost + wcu_cost

    # CloudWatch Logs
    # $0.76/GB 수집, $0.033/GB 저장
    estimated_log_gb = monthly_invocations * 0.001 / 1024  # 1KB/요청 가정
    logs_cost = estimated_log_gb * 0.76

    # SQS (가정: 10% 요청이 큐 경유)
    sqs_messages = monthly_invocations * 0.1
    sqs_cost = max(0, sqs_messages - 1_000_000) / 1_000_000 * 0.40

    total = lambda_cost + apigw_cost + dynamodb_cost + logs_cost + sqs_cost

    return {
        "monthly_invocations": monthly_invocations,
        "lambda_usd": round(lambda_cost, 2),
        "api_gateway_usd": round(apigw_cost, 2),
        "dynamodb_usd": round(dynamodb_cost, 2),
        "cloudwatch_logs_usd": round(logs_cost, 2),
        "sqs_usd": round(sqs_cost, 2),
        "total_usd": round(total, 2),
    }


# 트래픽 수준별 추정
for invocations in [100_000, 1_000_000, 10_000_000, 100_000_000]:
    estimate = estimate_total_serverless_cost(invocations)
    print(f"월 {invocations:,}건: 총 ${estimate['total_usd']:,.2f}")
    print(f"  Lambda: ${estimate['lambda_usd']}, APIGW: ${estimate['api_gateway_usd']}, "
          f"DynamoDB: ${estimate['dynamodb_usd']}")
```

## CloudWatch 비용 알람

비용 급증을 미리 감지하려면 AWS Budgets와 CloudWatch를 함께 사용합니다.

```yaml
Resources:
  # Lambda 비용 예산 알람
  LambdaCostBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetName: lambda-monthly-budget
        BudgetType: COST
        TimeUnit: MONTHLY
        BudgetLimit:
          Amount: 100
          Unit: USD
        CostFilters:
          Service:
            - "AWS Lambda"
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 80    # 80% 도달 시 알림
          Subscribers:
            - SubscriptionType: EMAIL
              Address: ops-team@example.com
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            Threshold: 100   # 예측 초과 시 알림
          Subscribers:
            - SubscriptionType: SNS
              Address: !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"

  # 전체 계정 비용 예산
  TotalCostBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetName: total-monthly-budget
        BudgetType: COST
        TimeUnit: MONTHLY
        BudgetLimit:
          Amount: 500
          Unit: USD
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 90
          Subscribers:
            - SubscriptionType: SNS
              Address: !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"
```

## 비용 최적화 전략

```python
import boto3
import json
from datetime import datetime, timedelta

ce = boto3.client("ce", region_name="us-east-1")


def get_lambda_cost_by_function(days: int = 7) -> list[dict]:
    """함수별 Lambda 비용 조회"""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    response = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Filter={
            "Dimensions": {
                "Key": "SERVICE",
                "Values": ["AWS Lambda"],
            }
        },
        GroupBy=[
            {"Type": "TAG", "Key": "FunctionName"},
        ],
        Metrics=["UnblendedCost", "UsageQuantity"],
    )

    results = []
    for result in response.get("ResultsByTime", []):
        for group in result.get("Groups", []):
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            if cost > 0:
                results.append({
                    "date": result["TimePeriod"]["Start"],
                    "function": group["Keys"][0],
                    "cost_usd": round(cost, 4),
                })

    return sorted(results, key=lambda x: x["cost_usd"], reverse=True)


def identify_cost_anomalies(threshold_multiplier: float = 3.0) -> list[dict]:
    """비용 이상 탐지 - 평균 대비 임계값 초과 함수"""
    costs = get_lambda_cost_by_function(days=14)

    # 함수별 평균 일일 비용 계산
    from collections import defaultdict
    daily_costs = defaultdict(list)
    for item in costs:
        daily_costs[item["function"]].append(item["cost_usd"])

    anomalies = []
    for function, cost_list in daily_costs.items():
        avg = sum(cost_list) / len(cost_list)
        latest = cost_list[-1] if cost_list else 0
        if avg > 0 and latest > avg * threshold_multiplier:
            anomalies.append({
                "function": function,
                "avg_daily_cost": round(avg, 4),
                "latest_cost": round(latest, 4),
                "multiplier": round(latest / avg, 2),
            })

    return sorted(anomalies, key=lambda x: x["multiplier"], reverse=True)
```

## 비용 최적화 체크리스트

**함수 수준 최적화**
- Lambda Power Tuning으로 최적 메모리 설정 확인
- 불필요한 의존성 제거로 패키지 크기 감소 (초기화 시간 단축 = 비용 감소)
- 핸들러 외부 초기화로 불필요한 SDK 재초기화 방지
- 실행 시간 측정 및 최적화 (p99 기준)

**아키텍처 수준 최적화**
- 짧은 주기 Polling을 이벤트 기반으로 전환
- CloudWatch 로그 보존 기간 설정 (기본값은 무기한)
- S3 Intelligent-Tiering으로 오래된 데이터 비용 절감
- DynamoDB 온디맨드 vs 프로비저닝 모드 트래픽 패턴에 따라 선택

**운영 수준 최적화**
- AWS Budgets로 월간 예산 상한 설정
- Cost Explorer로 주간 비용 추이 리뷰
- 비사용 함수와 Lambda Layer 정기 정리

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| Lambda 비용만 보고 안심 | API Gateway, DynamoDB 등 주변 서비스 비용이 더 큰데 모름 | 전체 서비스 비용을 태그 기반으로 집계 |
| 기본 메모리(128MB)로 운영 | 느린 실행 시간으로 GB-초 비용이 최적 설정보다 높음 | Lambda Power Tuning으로 최적 메모리 측정 |
| CloudWatch 로그 보존 기간 미설정 | 로그가 영구 보관되어 스토리지 비용 누적 | 보존 기간을 30-90일로 제한 |
| 예산 알람 없음 | 비용 급증을 월말 청구서에야 발견 | AWS Budgets로 80%, 100% 알림 설정 |
| 짧은 주기 Cron으로 폴링 | 실제 이벤트 없어도 함수가 계속 실행됨 | 이벤트 소스로 전환 (SQS, EventBridge) |
| 프로비저닝 동시성 과다 설정 | 대기 시간에도 과금, 불필요한 비용 발생 | SLO 기준 필요한 경로에만 선택 적용 |

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- [Serverless 101 (4/10): 콜드 스타트](./04-cold-start.md)
- [Serverless 101 (5/10): 스케일링](./05-scaling.md)
- [Serverless 101 (6/10): 상태 관리](./06-state-management.md)
- [Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처](./07-queue-and-event-driven.md)
- [Serverless 101 (8/10): 관측성](./08-observability.md)
- **Serverless 101 (9/10): 비용 (현재 글)**
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 가격 문서

- [Lambda 요금](https://aws.amazon.com/lambda/pricing/)
- [Cloud Functions 요금](https://cloud.google.com/functions/pricing)
- [Azure Functions 요금](https://azure.microsoft.com/pricing/details/functions/)

### FinOps와 추가 읽을거리

- [FinOps Foundation](https://www.finops.org/)
- [AWS Lambda Power Tuning (GitHub)](https://github.com/alexcasalboni/aws-lambda-power-tuning)

Tags: Serverless, Cost, FinOps, Pricing, Cloud
