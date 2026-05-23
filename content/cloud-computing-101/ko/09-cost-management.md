---
series: cloud-computing-101
episode: 9
title: "Cloud Computing 101 (9/10): Cost Management"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Cloud
  - FinOps
  - Cost
  - AWS
  - Architecture
seo_description: 태그, 예산, 약정 할인, 라이트사이징으로 비용을 관리하는 법을 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (9/10): Cost Management

클라우드에서는 기능을 만드는 속도만큼 비용도 빠르게 늘 수 있습니다. 첫 청구서를 보고 놀라는 일은 너무 흔해서 거의 통과 의례처럼 취급되기도 합니다.

비용을 뒤늦게 확인하는 회계 숫자로만 보면 이미 대응이 늦습니다. 비용을 설계와 운영이 남긴 결과로 읽어야 합니다. 보이지 않는 비용은 줄일 수 없고, 책임이 배정되지 않은 비용은 계속 커집니다.

이 글은 Cloud Computing 101 시리즈의 9번째 글입니다.

여기서는 태그, 예산, Savings Plans, 라이트사이징을 중심으로 비용 관리를 엔지니어링의 일부로 보는 관점을 정리하겠습니다.


![Cloud Computing 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/09/09-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 9장 흐름 개요*
> 비용 관리는 기술 선택이 아니라 가시성과 통제권을 확보하는 운영 결정입니다.

## 먼저 던지는 질문

- 클라우드 비용은 왜 예상보다 자주 높게 나올까요?
- 태그는 비용 배분에서 어떤 역할을 할까요?
- 예산 알림은 언제 만들어야 할까요?

## 왜 중요한가

비용 놀람은 기술 팀이 피할 수 없는 운명이 아닙니다. 대부분은 가시성 부족, 태그 부재, 유휴 자원 방치, 너무 이른 약정 같은 반복 가능한 실수에서 시작됩니다. 그래서 FinOps는 재무팀의 뒷정리가 아니라 엔지니어링 팀의 설계 습관에 가깝습니다.

비용은 성능이나 가용성과 다르게 보이지 않는 경우가 많습니다. 시스템은 멀쩡히 동작하는데 청구서만 커질 수 있기 때문입니다. 그래서 더 의도적으로 설계하고 점검해야 합니다.

## 한눈에 보는 개념

비용 관리의 첫 단계는 보이게 만드는 것입니다. 그다음 알림을 걸고, 안정적인 부하에는 약정을 적용하고, 마지막으로 실제 사용량에 맞춰 자원 크기를 줄입니다.

## 핵심 용어

- **Tag**: 리소스에 붙이는 키-값 레이블입니다.
- **Budget**: 월별 한도와 알림 규칙입니다.
- **Savings Plans**: 일정 사용량을 약정하고 할인을 받는 방식입니다.
- **Reserved Instance**: 특정 인스턴스 계열에 더 강하게 묶이는 할인 방식입니다.
- **Rightsizing**: 실제 사용량에 맞춰 자원을 줄이거나 바꾸는 작업입니다.
- **Cost Allocation Report**: 태그 기준으로 비용을 분류한 월별 리포트입니다.
- **Unit Economics**: 요청 한 건, 사용자 한 명당 비용을 계산하는 방식입니다.

## 적용 전후 비교
**Before**에서는 모든 인스턴스를 `m5.xlarge`로 맞춰 두고 밤에도 그대로 켜 둡니다.

**After**에서는 비프로덕션은 야간에 자동으로 멈추고, 안정적인 프로덕션 부하는 Savings Plans로 할인받습니다.

이 차이는 큰 혁신보다 작은 운영 습관이 비용에 얼마나 큰 영향을 주는지 보여 줍니다.

## 태그 전략

태그가 없으면 비용 리포트는 "총합"만 보여 줍니다. 어떤 팀이, 어떤 서비스에, 어떤 환경에서 비용을 만들었는지 분류할 수 없습니다. 태그는 비용 배분의 출발점입니다.

### 필수 태그 표준

| 태그 키 | 용도 | 예시 값 |
| --- | --- | --- |
| `team` | 비용 책임 팀 식별 | `platform`, `data`, `ml` |
| `env` | 환경 구분 | `prod`, `staging`, `dev` |
| `service` | 서비스 단위 비용 추적 | `auth-api`, `payment`, `batch` |
| `cost-center` | 재무 부서 코드 매핑 | `CC-1001`, `CC-2003` |

선택 태그로 `owner`(담당자 이메일), `ttl`(만료 예정일), `ticket`(생성 근거 이슈 번호)을 추가하면 유휴 자원 정리가 수월해집니다.

### 태그 강제 정책

태그를 권장만 하면 누락률이 빠르게 올라갑니다. SCP(Service Control Policy)나 IAM 조건으로 강제해야 합니다.

```python
# IAM: 팀 태그 없이 EC2를 생성합니다.
require_tags_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "DenyUntaggedEC2",
        "Effect": "Deny",
        "Action": "ec2:RunInstances",
        "Resource": "arn:aws:ec2:*:*:instance/*",
        "Condition": {
            "Null": {
                "aws:RequestTag/team": "true",
                "aws:RequestTag/env": "true",
                "aws:RequestTag/service": "true",
            }
        },
    }],
}
```

## 실습: 예산 만들기

### 1단계 — 클라이언트

```python
import boto3
budgets = boto3.client("budgets")
account_id = boto3.client("sts").get_caller_identity()["Account"]
```

### 2단계 — 예산 정의

```python
budget = {
    "BudgetName": "monthly-cap",
    "BudgetLimit": {"Amount": "500", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
}
```

### 3단계 — 알림 정의

```python
notif = [{
    "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80.0,
        "ThresholdType": "PERCENTAGE",
    },
    "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "ops@example.com"}],
}]
```

### 4단계 — 생성

```python
def create_budget():
    budgets.create_budget(
        AccountId=account_id,
        Budget=budget,
        NotificationsWithSubscribers=notif,
    )
```

### 5단계 — CLI로 예산 확인

```bash
# 예산 생성 확인
aws budgets describe-budget \
    --account-id "$ACCOUNT_ID" \
    --budget-name monthly-cap

# 모든 예산 목록
aws budgets describe-budgets --account-id "$ACCOUNT_ID"
```

**Expected output:**

- 월 예산 한도가 `500 USD`로 보이고, 시간 단위가 `MONTHLY`로 표시되어야 합니다.
- 80% 임계값 알림 설정이 함께 보여야 합니다.

## AWS Cost Explorer CLI 쿼리

Cost Explorer API를 CLI로 호출하면 대시보드에 로그인하지 않고도 비용 추이를 확인할 수 있습니다.

### 일별 비용 조회

```bash
aws ce get-cost-and-usage \
    --time-period Start=2026-05-01,End=2026-05-15 \
    --granularity DAILY \
    --metrics "UnblendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE
```

### 월별 서비스별 비용 요약

```bash
aws ce get-cost-and-usage \
    --time-period Start=2026-01-01,End=2026-06-01 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" "UsageQuantity" \
    --group-by Type=DIMENSION,Key=SERVICE \
    --filter '{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}'
```

### 태그별 비용 분류

```bash
aws ce get-cost-and-usage \
    --time-period Start=2026-05-01,End=2026-06-01 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=TAG,Key=team
```

이 쿼리 결과를 주간 Slack 알림이나 정기 리포트에 연결하면 비용 리뷰가 자동화됩니다.

## 유휴 자원 탐지 스크립트

사용하지 않는 리소스는 비용 낭비의 가장 흔한 원인입니다. 아래 스크립트는 연결되지 않은 EBS 볼륨, 유휴 EC2 인스턴스, 미사용 Elastic IP를 찾습니다.

```python
import boto3
from datetime import datetime, timedelta, timezone

ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")


def find_unattached_ebs() -> list[dict]:
    """연결되지 않은 EBS 볼륨 목록을 반환합니다."""
    volumes = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )["Volumes"]
    results = []
    for vol in volumes:
        results.append({
            "VolumeId": vol["VolumeId"],
            "Size_GB": vol["Size"],
            "CreateTime": vol["CreateTime"].isoformat(),
        })
    return results


def find_idle_ec2(cpu_threshold: float = 5.0, days: int = 7) -> list[dict]:
    """평균 CPU 사용률이 임계값 이하인 인스턴스를 반환합니다."""
    instances = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    idle = []
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    for reservation in instances["Reservations"]:
        for inst in reservation["Instances"]:
            instance_id = inst["InstanceId"]
            stats = cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start,
                EndTime=end,
                Period=86400,
                Statistics=["Average"],
            )
            if stats["Datapoints"]:
                avg_cpu = sum(d["Average"] for d in stats["Datapoints"]) / len(
                    stats["Datapoints"]
                )
                if avg_cpu < cpu_threshold:
                    idle.append({
                        "InstanceId": instance_id,
                        "InstanceType": inst["InstanceType"],
                        "AvgCPU": round(avg_cpu, 2),
                    })
    return idle


def find_unused_eips() -> list[dict]:
    """연결되지 않은 Elastic IP를 반환합니다."""
    addresses = ec2.describe_addresses()["Addresses"]
    return [
        {"PublicIp": addr["PublicIp"], "AllocationId": addr["AllocationId"]}
        for addr in addresses
        if "AssociationId" not in addr
    ]


if __name__ == "__main__":
    print("=== Unattached EBS Volumes ===")
    for vol in find_unattached_ebs():
        print(f"  {vol['VolumeId']}  {vol['Size_GB']} GB")

    print("\n=== Idle EC2 Instances (CPU < 5%) ===")
    for inst in find_idle_ec2():
        print(f"  {inst['InstanceId']}  {inst['InstanceType']}  avg {inst['AvgCPU']}%")

    print("\n=== Unused Elastic IPs ===")
    for eip in find_unused_eips():
        print(f"  {eip['PublicIp']}  {eip['AllocationId']}")
```

이 스크립트를 주 1회 CI 파이프라인이나 cron으로 실행하고, 결과를 Slack 채널에 보내면 유휴 자원이 쌓이는 것을 방지할 수 있습니다.

## 예산 알림 CLI 설정

콘솔 대신 CLI로 예산과 알림을 일괄 생성하면 여러 계정에 동일한 기준을 적용할 수 있습니다.

```bash
# 팀별 예산 생성 (JSON 파일 기반)
aws budgets create-budget \
    --account-id "$ACCOUNT_ID" \
    --budget file://budget-definition.json \
    --notifications-with-subscribers file://budget-notifications.json
```

`budget-definition.json` 예시:

```json
{
  "BudgetName": "team-platform-monthly",
  "BudgetLimit": {"Amount": "2000", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["user:team$platform"]
  }
}
```

`budget-notifications.json` 예시:

```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 50.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {"SubscriptionType": "EMAIL", "Address": "platform-leads@example.com"}
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {"SubscriptionType": "SNS", "Address": "arn:aws:sns:ap-northeast-2:123456789012:cost-alerts"}
    ]
  }
]
```

50% 실제 지출과 100% 예측 초과를 분리하면 대응 시간을 단계적으로 확보할 수 있습니다.

## Reserved Instance vs Savings Plans 비교

| 항목 | Reserved Instance (RI) | Savings Plans (SP) |
| --- | --- | --- |
| 할인 범위 | 특정 인스턴스 패밀리/리전 | Compute SP는 패밀리/리전/OS 무관 |
| 유연성 | 낮음 (변경 시 교환 필요) | 높음 (사용량 기반 자동 적용) |
| 약정 기간 | 1년 또는 3년 | 1년 또는 3년 |
| 할인율 | 최대 72% (3년 전액 선결제) | 최대 66% (Compute SP 3년) |
| 적합한 경우 | 인스턴스 유형이 확정된 안정 워크로드 | 패밀리 변경 가능성이 있는 워크로드 |
| 결제 옵션 | 전액/부분/무선결제 | 전액/부분/무선결제 |
| 적용 순서 | RI 먼저, 남은 부분에 SP 적용 | RI 이후 잔여 사용량에 적용 |

실무에서는 Compute Savings Plans로 시작하고, 인스턴스 유형이 6개월 이상 변하지 않는 워크로드에만 RI를 추가하는 순서가 안전합니다.

## FinOps 성숙도 모델

FinOps Foundation이 정의한 성숙도 모델은 Crawl, Walk, Run 세 단계로 나뉩니다. 팀이 어느 단계에 있는지 파악하면 다음에 해야 할 일이 명확해집니다.

| 단계 | 가시성 | 최적화 | 운영 |
| --- | --- | --- | --- |
| **Crawl** | 태그 표준 정의, Cost Explorer 접근 권한 부여 | 유휴 자원 수동 정리 | 월 1회 비용 리뷰 |
| **Walk** | 태그 강제 정책, 팀별 대시보드 | Rightsizing 권고 적용, SP 도입 | 주간 비용 리뷰, 이상 탐지 알림 |
| **Run** | 실시간 비용 피드백, Unit Economics 추적 | 자동 스케줄링, 예약 커버리지 최적화 | 비용을 설계 리뷰 항목에 포함, 분기 FinOps 회고 |

대부분의 팀은 Crawl 단계에서 시작합니다. Crawl에서 가장 중요한 것은 태그 표준을 정하고 실제로 강제하는 것입니다. 태그 없이 Walk로 넘어가면 대시보드가 있어도 의미 있는 분류를 할 수 없습니다.

## Cost Allocation Report 해석

AWS Cost and Usage Report(CUR)는 가장 상세한 비용 데이터를 제공합니다. S3에 CSV 또는 Parquet 형식으로 적재되며, Athena로 쿼리할 수 있습니다.

### 주요 컬럼과 해석

| 컬럼 | 의미 | 활용 |
| --- | --- | --- |
| `lineItem/UsageType` | 과금 단위 (예: `BoxUsage:m5.xlarge`) | 인스턴스 유형별 비용 분류 |
| `lineItem/UnblendedCost` | 개별 계정 기준 실제 비용 | 팀별 비용 추적 |
| `resourceTags/user:team` | 사용자 정의 태그 | 책임 조직 매핑 |
| `reservation/EffectiveCost` | RI/SP 적용 후 비용 | 약정 효과 측정 |
| `savingsPlan/SavingsPlanRate` | SP 적용 단가 | On-Demand 대비 절감률 계산 |

### Athena 쿼리 예시

```sql
SELECT
    "resourceTags/user:team" AS team,
    "product/servicename" AS service,
    SUM("lineItem/UnblendedCost") AS total_cost
FROM cur_report
WHERE month = '5' AND year = '2026'
GROUP BY 1, 2
ORDER BY total_cost DESC
LIMIT 20;
```

이 쿼리를 정기적으로 실행하면 어떤 팀의 어떤 서비스가 비용을 주도하는지 한눈에 파악할 수 있습니다.

## Rightsizing 워크플로

Rightsizing은 한 번의 이벤트가 아니라 반복 주기를 가진 운영 활동입니다.

### 단계별 진행

1. **데이터 수집** — CloudWatch에서 최소 14일간의 CPU, 메모리, 네트워크 메트릭을 수집합니다.
2. **권고 생성** — AWS Compute Optimizer 또는 Cost Explorer Rightsizing 권고를 확인합니다.
3. **영향 분석** — 권고 대상 인스턴스의 피크 사용량이 새 크기의 80%를 넘지 않는지 확인합니다.
4. **변경 적용** — 비프로덕션에서 먼저 적용하고, 1주일 관찰 후 프로덕션에 적용합니다.
5. **결과 검증** — 변경 전후 비용과 성능 메트릭을 비교합니다.

### CLI로 권고 확인

```bash
aws ce get-rightsizing-recommendation \
    --service AmazonEC2 \
    --configuration '{
        "RecommendationTarget": "SAME_INSTANCE_FAMILY",
        "BenefitsConsidered": true
    }'
```

권고를 무조건 따르지 말고, 피크 트래픽 시간대의 메트릭과 함께 판단해야 합니다. 평균은 낮아도 피크가 높은 워크로드를 축소하면 성능 문제가 발생합니다.

## 비용 이상 탐지

예산 알림은 임계값 기반이므로 점진적 증가는 잡지 못합니다. 이상 탐지(anomaly detection)를 추가하면 평소 패턴과 다른 지출을 자동으로 감지할 수 있습니다.

### AWS Cost Anomaly Detection 설정

```bash
# 서비스 단위 모니터
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "MonitorName": "service-level-monitor",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }'

# 알림 구독 생성
aws ce create-anomaly-subscription \
    --anomaly-subscription '{
        "SubscriptionName": "cost-anomaly-alert",
        "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/monitor-id"],
        "Subscribers": [
            {"Type": "EMAIL", "Address": "finops@example.com"}
        ],
        "Threshold": 50.0,
        "Frequency": "DAILY"
    }'
```

임계값 50 USD는 팀 규모에 맞게 조정합니다. 작은 팀은 10 USD도 의미 있는 이상일 수 있고, 대규모 서비스는 500 USD 이상으로 설정해야 노이즈가 줄어듭니다.

## Unit Economics 계산

총비용만 보면 서비스가 성장하는 건지 비효율이 커지는 건지 구분할 수 없습니다. Unit Economics는 비용을 비즈니스 단위로 나눠서 효율을 추적합니다.

### 주요 지표

| 지표 | 계산 | 의미 |
| --- | --- | --- |
| Cost per Request | 월 총비용 / 월 총 요청 수 | API 효율 |
| Cost per Active User | 월 총비용 / MAU | 사용자당 서비스 비용 |
| Cost per Transaction | 결제 인프라 비용 / 결제 건수 | 거래 효율 |
| Cost per GB Processed | 데이터 파이프라인 비용 / 처리량 | 데이터 처리 효율 |

### 계산 스크립트

```python
from dataclasses import dataclass


@dataclass
class UnitEconomics:
    total_cost_usd: float
    total_requests: int
    active_users: int
    transactions: int

    @property
    def cost_per_request(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_cost_usd / self.total_requests

    @property
    def cost_per_user(self) -> float:
        if self.active_users == 0:
            return 0.0
        return self.total_cost_usd / self.active_users

    @property
    def cost_per_transaction(self) -> float:
        if self.transactions == 0:
            return 0.0
        return self.total_cost_usd / self.transactions

    def report(self) -> str:
        return (
            f"Cost/Request:     ${self.cost_per_request:.6f}\n"
            f"Cost/User:        ${self.cost_per_user:.4f}\n"
            f"Cost/Transaction: ${self.cost_per_transaction:.4f}"
        )


# 사용 예시
may = UnitEconomics(
    total_cost_usd=3200.0,
    total_requests=12_000_000,
    active_users=45_000,
    transactions=180_000,
)
print(may.report())
```

Unit Economics를 월별로 추적하면 비용이 올라도 효율이 유지되는 건강한 성장과, 효율이 떨어지는 비용 누수를 구분할 수 있습니다.

## 비용 최적화 전략 매트릭스

| 전략 | 적용 시점 | 기대 효과 | 주의점 |
| --- | --- | --- | --- |
| 태그 표준화 | 즉시 | 비용 책임 추적 가능 | 강제 정책 없으면 누락 |
| 예산 알림 | 즉시 | 이상 지출 조기 탐지 | 차단 기능 아님 |
| 유휴 자원 정리 | 주간 | 즉시 비용 절감 | 자동화 없으면 재발 |
| Rightsizing | 월간 | 지속 비용 절감 | 성능 영향 검증 필요 |
| Savings Plans | 패턴 안정 후 | 안정 부하 할인 | 과약정 리스크 |
| Spot 활용 | 배치/재시도 가능 작업 | 큰 단가 절감 | 중단 대비 필수 |
| 스케줄링 | 비프로덕션 즉시 | 야간/주말 비용 제거 | 긴급 작업 시 수동 시작 필요 |

## 이 코드에서 먼저 봐야 할 점

- 80% 예산 알림은 대응할 시간을 벌어 줍니다.
- 태그 강제 정책은 비용 추적의 출발점입니다.
- 예산은 계정 전체뿐 아니라 팀 단위로도 나눌 수 있습니다.
- 유휴 자원 탐지는 주기적으로 실행해야 효과가 있습니다.
- Unit Economics는 총비용보다 효율 변화를 보여 줍니다.

## 자주 막히는 지점

- 예산은 경고 장치이지 차단 장치가 아닙니다. 초과를 자동으로 막아 준다고 생각하면 대응이 늦어집니다.
- Savings Plans는 사용 패턴이 안정화된 뒤에 적용해야 합니다. 너무 이른 약정은 비용을 고정 리스크로 바꿉니다.
- NAT와 데이터 전송 비용은 애플리케이션 코드 바깥에서 커지므로, 아키텍처 리뷰에서 따로 점검해야 합니다.
- Cost Allocation Report를 활성화하지 않으면 태그를 붙여도 비용 리포트에 반영되지 않습니다. Billing 콘솔에서 "Cost allocation tags"를 활성화해야 합니다.

## Savings Plans와 라이트사이징은 어떻게 함께 쓰나

약정 할인은 변동성이 낮은 기준 부하에 적용할 때 가장 효과적입니다. 아직 사용 패턴을 잘 모르는 단계에서 과하게 약정하면 할인보다 제약이 더 커질 수 있습니다. 그래서 보통은 먼저 사용량을 관찰하고, 그다음 안정적인 부분에만 약정을 얹습니다.

라이트사이징은 이와 별개로 계속 반복해야 하는 작업입니다. 한때 적절했던 인스턴스 크기가 지금도 적절하다는 보장은 없습니다. 비용 최적화는 한 번의 큰 결정보다 정기적인 작은 조정의 합에 가깝습니다.

약정 적용 순서는 이렇습니다:

1. 최소 30일간 사용 패턴을 관찰합니다.
2. 기준 부하(baseline)와 변동 부하(burst)를 분리합니다.
3. 기준 부하의 70-80%에 해당하는 금액만 Compute SP로 약정합니다.
4. 3개월 후 커버리지를 다시 평가하고 필요하면 추가합니다.

## 자주 하는 실수 5가지

1. 태그 없는 리소스를 그대로 둡니다.
2. 예산 알림을 만들지 않습니다.
3. Savings Plans를 과하게 약정합니다.
4. 비싼 인스턴스를 유휴 상태로 방치합니다.
5. NAT와 데이터 전송 비용을 과소평가합니다.

## 실무에서는 이렇게 생각합니다

- 비용은 설계 지표입니다.
- 태그는 FinOps의 입구입니다.
- 실제 변동성을 본 뒤에만 약정을 걸어야 합니다.
- 데이터 전송 비용은 보이지 않는 곳에서 커지기 쉽습니다.
- 비용 리뷰는 정기 리듬으로 운영해야 합니다.
- Unit Economics가 악화되면 총비용이 줄어도 문제입니다.

## 체크리스트

- [ ] 모든 리소스에 `team`, `env`, `service` 태그가 있는가.
- [ ] 월 예산 알림이 활성화되어 있는가.
- [ ] 유휴 자원을 정기적으로 점검하는가.
- [ ] SP와 RI를 분기마다 한 번 이상 검토하는가.
- [ ] Cost Allocation Tags가 Billing에서 활성화되어 있는가.
- [ ] Unit Economics를 월별로 추적하고 있는가.

## 연습 문제

1. On-Demand와 Savings Plans의 차이를 한 줄로 설명해 보세요.
2. 비용 추적에 필요한 최소 태그 세 가지를 적어 보세요.
3. NAT Gateway 비용을 줄이는 전략 하나를 제안해 보세요.
4. Cost per Request가 지난달 대비 2배 올랐을 때 점검해야 할 항목 세 가지를 나열해 보세요.

## 처음 질문으로 돌아가기

- **클라우드 비용은 왜 예상보다 자주 높게 나올까요?** — 가시성이 없기 때문입니다. 태그가 없으면 누가 무엇에 쓰는지 모르고, 예산 알림이 없으면 이상 지출을 사후에 발견합니다. 유휴 자원은 경고 없이 비용을 누적시킵니다.
- **태그는 비용 배분에서 어떤 역할을 할까요?** — 태그는 비용을 팀, 서비스, 환경 단위로 분류하는 유일한 수단입니다. Cost Allocation Report와 결합하면 누가 얼마를 쓰는지 추적할 수 있고, 책임 소재를 명확히 할 수 있습니다.
- **예산 알림은 언제 만들어야 할까요?** — 첫 리소스를 만드는 시점에 함께 만들어야 합니다. 비용이 작을 때 만들어 두면 습관이 되고, 비용이 커졌을 때 이미 감지 체계가 동작합니다.

## 정리 및 다음 단계

운영, 보안, 비용을 각각 이해했다면 이제는 이 조각들을 하나의 설계 그림으로 묶어야 합니다. 다음 글에서는 시리즈 마지막으로 Cloud Architecture 기초를 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- [Cloud Computing 101 (7/10): Identity와 Security](./07-identity-and-security.md)
- [Cloud Computing 101 (8/10): Monitoring](./08-monitoring.md)
- **Cost Management (현재 글)**
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [AWS Billing user guide](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-what-is.html)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [Savings Plans](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html)
- [FinOps Foundation](https://www.finops.org/framework/)
- [AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, FinOps, Cost, AWS, Architecture
