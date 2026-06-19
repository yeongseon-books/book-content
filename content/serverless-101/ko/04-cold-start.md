---
series: serverless-101
episode: 4
title: "Serverless 101 (4/10): 콜드 스타트"
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
  - ColdStart
  - Performance
  - Latency
  - Cloud
seo_description: 서버리스 콜드 스타트의 원인, 측정 방법, 패키지 최적화와 프로비저닝 전략을 설명합니다
last_reviewed: '2026-05-12'
---

# Serverless 101 (4/10): 콜드 스타트

서버리스 함수를 처음 호출했을 때만 유독 느려지는 순간이 있습니다. 평균 지표만 보면 잘 안 보이지만, 실제 사용자 경험과 SLO에는 크게 영향을 줍니다. 그래서 콜드 스타트는 입문자가 가장 늦게 이해하면 안 되는 주제 중 하나입니다.

이 글은 Serverless 101 시리즈의 4번째 글입니다.

![Serverless 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/serverless-101/04/04-01-concept-at-a-glance.ko.png)
*Serverless 101 4장 흐름 개요*
> Cold start는 플랫폼이 함수를 필요할 때 올리는 시간이고, 서버리스의 모든 아키텍처 결정은 호출 비용과 이 시작 세금 사이의 trade-off입니다.

## 이 글에서 다룰 문제

- 함수의 첫 호출은 왜 느릴까요?
- 콜드 스타트는 어떤 단계들의 합으로 생길까요?
- 평균이 아니라 p99를 봐야 하는 이유는 무엇일까요?
- 패키지 크기와 의존성은 어떻게 초기화 시간에 영향을 줄까요?
- 프로비저닝된 동시성은 언제 선택해야 할까요?

## 왜 이 주제가 중요한가

콜드 스타트는 "가끔 느리다"는 수준에서 끝나지 않습니다. 로그인, 결제, 웹훅 응답처럼 지연 시간에 민감한 경로에서는 p99가 바로 사용자 불만과 SLA 위반으로 이어질 수 있습니다.

문제는 평균값이 이를 감추기 쉽다는 사실입니다. 재사용된 웜 인스턴스가 대부분이면 평균은 좋아 보입니다. 하지만 몇 번의 콜드 스타트가 꼬리 지연 시간을 끌어올리면 실제 운영에서는 그 몇 번이 더 중요해집니다. 그래서 콜드 스타트는 성능 최적화 팁이 아니라, 어떤 경로에 얼마만큼의 지연을 허용할지 결정하는 설계 변수입니다.

## 한눈에 보는 구조

이 흐름을 보면 콜드 스타트가 단일 원인이 아니라는 점이 보입니다. 실행 환경 생성, 런타임 초기화, 코드와 의존성 로딩이 모두 합쳐져 첫 호출 지연으로 나타납니다. 그래서 해결책도 하나가 아니라 여러 층에서 나옵니다.

## 콜드 스타트 단계 분해

Lambda 기준으로 콜드 스타트는 크게 네 단계로 나뉩니다.

| 단계 | 설명 | 제어 가능 여부 |
|------|------|--------------|
| 실행 환경 생성 | EC2 microVM 할당, 네트워크 설정 | 불가 (플랫폼 책임) |
| 런타임 초기화 | Python/Node.js 인터프리터 시작 | 런타임 선택으로 일부 제어 |
| 패키지 로딩 | 코드와 의존성 압축 해제 및 로드 | 패키지 크기·구조로 제어 |
| 핸들러 초기화 | 전역 변수, DB 연결, SDK 초기화 | 코드 구조로 제어 |

이 중에서 개발자가 가장 직접 제어할 수 있는 부분은 마지막 두 단계입니다.

## 콜드 스타트 측정하기

CloudWatch Logs Insights로 초기화 시간을 추출하면 다음과 같습니다.

```sql
fields @timestamp, @message, @initDuration, @duration
| filter @type = "REPORT"
| filter ispresent(@initDuration)
| stats
    count() as cold_starts,
    avg(@initDuration) as avg_init_ms,
    pct(@initDuration, 99) as p99_init_ms,
    max(@initDuration) as max_init_ms
| sort cold_starts desc
```

`@initDuration` 필드는 콜드 스타트가 일어난 호출에만 나타납니다. 이 필드가 없는 로그는 웜 인스턴스가 처리한 것입니다.

Python으로 직접 측정하려면 핸들러 외부에서 타이밍을 잡아야 합니다.

```python
import time
import json
import boto3

# 핸들러 외부 코드는 콜드 스타트 시에만 실행됩니다
_cold_start_time = time.perf_counter()
_is_cold_start = True
_dynamodb = boto3.resource("dynamodb")

def handler(event, context):
    global _is_cold_start

    request_start = time.perf_counter()

    if _is_cold_start:
        init_ms = (request_start - _cold_start_time) * 1000
        print(json.dumps({
            "event": "cold_start",
            "init_duration_ms": round(init_ms, 2),
            "function_name": context.function_name,
            "memory_mb": context.memory_limit_in_mb,
        }))
        _is_cold_start = False

    # 실제 비즈니스 로직
    result = process(event)

    total_ms = (time.perf_counter() - request_start) * 1000
    print(json.dumps({
        "event": "request_complete",
        "duration_ms": round(total_ms, 2),
    }))

    return {"statusCode": 200, "body": json.dumps(result)}


def process(event):
    return {"message": "processed"}
```

## 런타임별 콜드 스타트 특성

| 런타임 | 평균 콜드 스타트 | 특성 |
|--------|----------------|------|
| Python 3.12 | 200-400ms | 패키지 크기 영향 큼 |
| Node.js 20 | 100-250ms | 상대적으로 빠름 |
| Java 21 (SnapStart 없음) | 1-3초 | JVM 시작 비용 높음 |
| Java 21 (SnapStart) | 200-600ms | 스냅샷 복원 방식 |
| Go 1.x | 50-150ms | 바이너리 직접 실행 |
| .NET 8 | 300-700ms | IL 컴파일 비용 |

Go와 Node.js가 Python보다 콜드 스타트가 빠른 이유는 런타임 초기화 비용이 낮기 때문입니다. 하지만 팀 역량과 생태계를 우선해 언어를 선택하고, 콜드 스타트 최적화는 패키지 구조와 프로비저닝으로 해결하는 것이 실용적입니다.

## 패키지 최적화

의존성 크기가 초기화 시간에 직접 영향을 줍니다. 불필요한 패키지를 제거하고 Lambda Layer를 활용하면 배포 패키지를 줄일 수 있습니다.

```makefile
# 의존성 최소화 빌드 예시
.PHONY: build

build:
	pip install \
	    --target ./package \
	    --platform manylinux2014_x86_64 \
	    --implementation cp \
	    --python-version 3.12 \
	    --only-binary=:all: \
	    -r requirements-prod.txt

	# 불필요한 파일 제거 (테스트, docs, __pycache__)
	find ./package -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
	find ./package -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find ./package -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true

	cd package && zip -r9 ../function.zip . -x "*.pyc"
	zip -g function.zip handler.py
```

핵심 원칙은 `requirements.txt`를 운영용(`requirements-prod.txt`)과 개발용(`requirements-dev.txt`)으로 분리하는 것입니다. pytest, black, mypy 같은 도구는 배포 패키지에 포함할 필요가 없습니다.

## 핸들러 외부 초기화 활용

함수 핸들러 밖에서 초기화한 객체는 웜 인스턴스가 재사용될 때 다시 생성되지 않습니다. DB 연결이나 SDK 클라이언트처럼 초기화 비용이 큰 객체는 핸들러 외부에 두어야 합니다.

```python
import os
import boto3
from botocore.config import Config

# 콜드 스타트 시 한 번만 실행
_region = os.environ["AWS_REGION"]
_table_name = os.environ["TABLE_NAME"]

_config = Config(
    connect_timeout=2,
    read_timeout=5,
    retries={"max_attempts": 3, "mode": "adaptive"},
)
_dynamodb = boto3.resource("dynamodb", region_name=_region, config=_config)
_table = _dynamodb.Table(_table_name)

# SSM Parameter Store 값도 여기서 캐시
_ssm = boto3.client("ssm", region_name=_region)
_api_key = None


def get_api_key() -> str:
    global _api_key
    if _api_key is None:
        response = _ssm.get_parameter(
            Name=os.environ["API_KEY_PARAM"],
            WithDecryption=True,
        )
        _api_key = response["Parameter"]["Value"]
    return _api_key


def handler(event, context):
    key = get_api_key()  # 웜 인스턴스에서는 캐시에서 즉시 반환
    item = _table.get_item(Key={"pk": event["id"]})
    return {"statusCode": 200, "body": str(item.get("Item", {}))}
```

이 패턴의 주의점은 전역 상태가 요청 간에 공유된다는 사실입니다. 요청별로 달라져야 하는 데이터(사용자 컨텍스트, 요청 ID 등)는 핸들러 내부에서 관리해야 합니다.

## 프로비저닝된 동시성 (Provisioned Concurrency)

프로비저닝된 동시성을 설정하면 Lambda가 지정한 수의 인스턴스를 미리 초기화해 두고 대기 상태로 유지합니다. 콜드 스타트가 없어지는 것이 아니라, 미리 콜드 스타트를 끝내 두는 방식입니다.

```yaml
# SAM 템플릿에서 프로비저닝된 동시성 설정
Resources:
  PaymentFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: payment-processor
      Handler: handler.lambda_handler
      Runtime: python3.12
      MemorySize: 512
      Timeout: 30
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 5
      Environment:
        Variables:
          TABLE_NAME: !Ref PaymentTable
          AWS_REGION: !Ref AWS::Region

  # Application Auto Scaling으로 시간대별 동적 조정
  PaymentFunctionScalableTarget:
    Type: AWS::ApplicationAutoScaling::ScalableTarget
    Properties:
      MaxCapacity: 20
      MinCapacity: 2
      ResourceId: !Sub "function:${PaymentFunction}:live"
      ScalableDimension: lambda:function:ProvisionedConcurrency
      ServiceNamespace: lambda

  PaymentFunctionScalingPolicy:
    Type: AWS::ApplicationAutoScaling::ScalingPolicy
    Properties:
      PolicyName: payment-function-scaling
      PolicyType: TargetTrackingScaling
      ScalingTargetId: !Ref PaymentFunctionScalableTarget
      TargetTrackingScalingPolicyConfiguration:
        TargetValue: 0.7  # 활용률 70% 목표
        PredefinedMetricSpecification:
          PredefinedMetricType: LambdaProvisionedConcurrencyUtilization
```

프로비저닝된 동시성은 비용이 추가됩니다. 실행하지 않는 대기 시간에도 과금됩니다. 따라서 모든 함수에 적용하기보다는 SLO가 엄격하고 트래픽이 예측 가능한 경로(결제, 로그인)에만 선택적으로 적용해야 합니다.

## 콜드 스타트 운영 판단 기준

```python
def should_use_provisioned_concurrency(
    p99_latency_ms: float,
    slo_ms: float,
    cold_start_rate: float,
    monthly_invocations: int,
) -> dict:
    """프로비저닝된 동시성 필요 여부 판단"""

    # SLO 위반 위험이 있는지 확인
    latency_risk = p99_latency_ms > slo_ms * 0.8

    # 콜드 스타트 비율이 높은지 확인 (5% 이상)
    high_cold_start_rate = cold_start_rate > 0.05

    # 충분한 트래픽이 있는지 (비용 효율성)
    sufficient_traffic = monthly_invocations > 100_000

    recommendation = "not_needed"
    if latency_risk and high_cold_start_rate and sufficient_traffic:
        recommendation = "strongly_recommended"
    elif latency_risk and high_cold_start_rate:
        recommendation = "consider_if_budget_allows"
    elif latency_risk:
        recommendation = "investigate_other_optimizations_first"

    return {
        "recommendation": recommendation,
        "latency_risk": latency_risk,
        "high_cold_start_rate": high_cold_start_rate,
        "sufficient_traffic": sufficient_traffic,
    }
```

## 운영 알람 설정

CloudWatch 알람으로 콜드 스타트 급증을 감지합니다.

```yaml
Resources:
  ColdStartAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: payment-function-cold-starts-high
      AlarmDescription: "콜드 스타트 비율이 임계값 초과"
      MetricName: InitDuration
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: payment-processor
      Statistic: SampleCount
      Period: 300        # 5분
      EvaluationPeriods: 2
      Threshold: 50      # 5분간 50건 이상 콜드 스타트
      ComparisonOperator: GreaterThanThreshold
      TreatMissingData: notBreaching
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"

  P99LatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: payment-function-p99-latency-high
      MetricName: Duration
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: payment-processor
      ExtendedStatistic: p99
      Period: 60
      EvaluationPeriods: 5
      Threshold: 3000    # p99 3초 초과 시 알람
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:ops-alerts"
```

## 콜드 스타트 진단 런북

콜드 스타트 관련 알람이 발생했을 때 따르는 절차입니다.

**1단계: 콜드 스타트 규모 확인**

```bash
# 최근 1시간 콜드 스타트 건수와 비율 조회
aws logs start-query \
  --log-group-name "/aws/lambda/payment-processor" \
  --start-time $(date -d "1 hour ago" +%s) \
  --end-time $(date +%s) \
  --query-string '
    fields @type
    | filter @type = "REPORT"
    | stats
        count() as total,
        count(ispresent(@initDuration)) as cold_starts,
        (count(ispresent(@initDuration)) / count()) * 100 as cold_start_pct,
        avg(@initDuration) as avg_init_ms,
        pct(@initDuration, 99) as p99_init_ms
  '
```

**2단계: 패키지 크기 확인**

```bash
aws lambda get-function \
  --function-name payment-processor \
  --query 'Configuration.{CodeSize:CodeSize,MemorySize:MemorySize,Runtime:Runtime}'
```

패키지가 50MB 이상이면 Layer 분리 또는 의존성 정리를 검토합니다.

**3단계: 메모리 설정 검토**

Lambda Power Tuning을 사용해 메모리 대비 성능 곡선을 그립니다. 메모리를 늘리면 CPU 할당이 함께 늘어나 초기화 시간이 줄어드는 경우가 있습니다.

**4단계: 프로비저닝 적용 여부 결정**

SLO 위반이 명확하고 트래픽 패턴이 예측 가능하면 프로비저닝된 동시성을 설정합니다. 비용과 효과를 24시간 후 다시 확인합니다.

## 자주 하는 실수

| 실수 유형 | 증상 | 올바른 접근 |
|-----------|------|------------|
| 평균 지연만 모니터링 | 콜드 스타트 문제를 알람으로 잡지 못함 | p99, p95 지표를 별도 알람으로 추적 |
| 불필요한 의존성 포함 | 패키지 크기 증가로 초기화 지연 | `requirements-prod.txt` 분리, 사이즈 측정 자동화 |
| DB 연결을 핸들러 내부에서 생성 | 매 요청마다 연결 비용 발생 | 핸들러 외부에서 초기화, 재사용 |
| 모든 함수에 프로비저닝 동시성 적용 | 불필요한 비용 증가 | SLO 기준으로 필요한 경로에만 선택 적용 |
| Java를 SnapStart 없이 사용 | 3초 이상 콜드 스타트 | SnapStart 활성화 또는 런타임 재검토 |
| 웜업 요청을 비즈니스 로직으로 혼동 | 핸들러에서 웜업 판별 불가 | 이벤트에 `source: "warmup"` 필드 추가해 분기 |

<!-- toc:begin -->
## 시리즈 목차

- [Serverless 101 (1/10): 서버리스란 무엇인가?](./01-what-is-serverless.md)
- [Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가?](./02-function-as-a-service.md)
- [Serverless 101 (3/10): 트리거와 이벤트](./03-trigger-and-event.md)
- **Serverless 101 (4/10): 콜드 스타트 (현재 글)**
- [Serverless 101 (5/10): 스케일링](./05-scaling.md)
- [Serverless 101 (6/10): 상태 관리](./06-state-management.md)
- [Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처](./07-queue-and-event-driven.md)
- [Serverless 101 (8/10): 관측성](./08-observability.md)
- [Serverless 101 (9/10): 비용](./09-cost.md)
- [서버리스 앱 설계](./10-serverless-app-design.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/serverless-101/ko

### 공식 문서

- [Lambda 런타임 환경과 콜드 스타트](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)
- [Provisioned Concurrency](https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html)
- [패키지 최적화 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

### 패턴과 코드

- [Lambda Power Tuning (GitHub)](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [AWS SnapStart for Java](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html)

Tags: Serverless, ColdStart, Performance, Latency, Cloud
