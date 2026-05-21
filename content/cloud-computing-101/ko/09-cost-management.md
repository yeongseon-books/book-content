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

## 먼저 던지는 질문

- 클라우드 비용은 왜 예상보다 자주 높게 나올까요?
- 태그는 비용 배분에서 어떤 역할을 할까요?
- 예산 알림은 언제 만들어야 할까요?

## 큰 그림

![Cloud Computing 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/09/09-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 9장 흐름 개요*

예약 인스턴스(Reserved Instance)는 1년 또는 3년 약정으로 할인을 받는 방식입니다. 스팟 인스턴스(Spot)는 남는 용량을 대폭 할인된 가격에 사용하되, 언제든 중단될 수 있습니다. 저장소(Storage)와 데이터 전송(Data Transfer) 비용도 누적되면 큽니다. 리소스 태그와 비용 배분이 없으면 누가 어디에 돈을 쓰는지 알 수 없습니다.

> 비용 관리는 기술 선택이 아니라 가시성과 통제권을 확보하는 운영 결정입니다.

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

## Before / After

**Before**에서는 모든 인스턴스를 `m5.xlarge`로 맞춰 두고 밤에도 그대로 켜 둡니다.

**After**에서는 비프로덕션은 야간에 자동으로 멈추고, 안정적인 프로덕션 부하는 Savings Plans로 할인받습니다.

이 차이는 큰 혁신보다 작은 운영 습관이 비용에 얼마나 큰 영향을 주는지 보여 줍니다.

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

### 5단계 — 태그 강제 정책

```python
require_tags = {
    "Effect": "Deny",
    "Action": "ec2:RunInstances",
    "Resource": "*",
    "Condition": {"Null": {"aws:RequestTag/Project": "true"}},
}
```

이 예제는 비용 관리가 보고서 읽기로 끝나지 않는다는 점을 보여 줍니다. 태그가 없으면 누가 비용을 만들었는지 추적할 수 없고, 예산 알림이 없으면 이상 징후를 너무 늦게 발견하게 됩니다. 비용 관리도 결국 정책과 자동화 문제입니다.

## 이 코드에서 먼저 봐야 할 점

- 80% 예산 알림은 대응할 시간을 벌어 줍니다.
- 태그 강제 정책은 비용 추적의 출발점입니다.
- 예산은 계정 전체뿐 아니라 팀 단위로도 나눌 수 있습니다.

## 이 예제를 실제로 검증하는 순서

예산과 태그 정책은 만들어 놓고 잊기 쉬운 영역입니다. 그래서 실제 계정에 어떤 이름의 예산이 생성되었는지, 어떤 임계값에서 알림이 나가도록 설정되었는지 바로 확인하는 루틴이 중요합니다.

```bash
aws budgets describe-budget --account-id "$ACCOUNT_ID" --budget-name monthly-cap
```

**Expected output:**

- 월 예산 한도가 `500 USD`로 보이고, 시간 단위가 `MONTHLY`로 표시되어야 합니다.
- 80% 임계값 알림 설정이 함께 보여야 합니다.
- 태그 강제 정책을 별도로 적용하지 않으면 비용 리포트는 여전히 "누가 만든 비용인가"에 답하지 못합니다.

### 자주 막히는 지점

- 예산은 경고 장치이지 차단 장치가 아닙니다. 초과를 자동으로 막아 준다고 생각하면 대응이 늦어집니다.
- Savings Plans는 사용 패턴이 안정화된 뒤에 적용해야 합니다. 너무 이른 약정은 비용을 고정 리스크로 바꿉니다.
- NAT와 데이터 전송 비용은 애플리케이션 코드 바깥에서 커지므로, 아키텍처 리뷰에서 따로 점검해야 합니다.

## Savings Plans와 라이트사이징은 어떻게 함께 쓰나

약정 할인은 변동성이 낮은 기준 부하에 적용할 때 가장 효과적입니다. 아직 사용 패턴을 잘 모르는 단계에서 과하게 약정하면 할인보다 제약이 더 커질 수 있습니다. 그래서 보통은 먼저 사용량을 관찰하고, 그다음 안정적인 부분에만 약정을 얹습니다.

라이트사이징은 이와 별개로 계속 반복해야 하는 작업입니다. 한때 적절했던 인스턴스 크기가 지금도 적절하다는 보장은 없습니다. 비용 최적화는 한 번의 큰 결정보다 정기적인 작은 조정의 합에 가깝습니다.

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

## 체크리스트

- [ ] 모든 리소스에 `Project` 태그가 있는가.
- [ ] 월 예산 알림이 활성화되어 있는가.
- [ ] 유휴 자원을 정기적으로 점검하는가.
- [ ] SP와 RI를 분기마다 한 번 이상 검토하는가.

## 연습 문제

1. On-Demand와 Savings Plans의 차이를 한 줄로 설명해 보세요.
2. 비용 추적에 필요한 최소 태그 세 가지를 적어 보세요.
3. NAT Gateway 비용을 줄이는 전략 하나를 제안해 보세요.

## 정리 및 다음 단계

운영, 보안, 비용을 각각 이해했다면 이제는 이 조각들을 하나의 설계 그림으로 묶어야 합니다. 다음 글에서는 시리즈 마지막으로 Cloud Architecture 기초를 정리하겠습니다.

사용하지 않는 리소스는 비용 낭비입니다. 정기적으로 사용하지 않는 인스턴스, 디스크, IP 주소를 정리하는 자동화된 정책이 필요합니다.

비용 알람(Budget Alert)을 설정하면 예상 외 지출을 조기에 감지할 수 있습니다. 팀별, 프로젝트별로 비용을 분류하는 태그도 필수입니다.
  - 본문의 기준은 Cost Management를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
기술 선택이 직결 비용에 미치는 영향을 이해해야 합니다. 예를 들어 서버리스는 사용량 기반이므로 예측 불가능한 트래픽에는 좋지만, 높은 기준 트래픽은 예약 인스턴스가 더 쌉니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **예산 알림은 언제 만들어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

## 비용 최적화 전략 매트릭스

| 전략 | 적용 시점 | 기대 효과 | 주의점 |
| --- | --- | --- | --- |
| 태그 표준화 | 즉시 | 비용 책임 추적 가능 | 강제 정책 없으면 누락 |
| 예산 알림 | 즉시 | 이상 지출 조기 탐지 | 차단 기능 아님 |
| Rightsizing | 월간 | 지속 비용 절감 | 성능 영향 검증 필요 |
| Savings Plans | 패턴 안정 후 | 안정 부하 할인 | 과약정 리스크 |
| Spot 활용 | 배치/재시도 가능 작업 | 큰 단가 절감 | 중단 대비 필수 |

```python
def monthly_compute_cost(hourly_price: float, instance_count: int) -> float:
    return hourly_price * 24 * 30 * instance_count

def commitment_saving(on_demand: float, discounted: float) -> float:
    return max(on_demand - discounted, 0.0)
```



### 운영 리뷰 질문 세트

아래 질문은 설계 문서 리뷰와 장애 회고에서 반복적으로 사용할 수 있는 체크 질문입니다.

| 질문 | 확인 포인트 | 흔한 실패 |
| --- | --- | --- |
| 책임 경계가 명확한가 | 공급자/사용자 책임 문서화 | "누가 고칠지" 미정 상태 |
| 변경 영향이 예측 가능한가 | 롤백/격리 경로 존재 | 단일 경로 의존 |
| 비용 신호가 보이는가 | 태그/예산/알림 연동 | 비용 급증 사후 인지 |
| 보안 기준이 자동화되었는가 | 정책 코드화, 주기 점검 | 수동 예외 누적 |
| 복구 가능성이 검증되었는가 | 정기 복원 리허설 | 백업만 있고 복원 실패 |

이 질문 세트는 기술 스택과 무관하게 적용할 수 있습니다. 중요한 것은 문장으로 "대답할 수 있는가"가 아니라, 로그/정책/테스트로 "증명할 수 있는가"입니다.

### 팀 운영 계약 예시

```yaml
team_operating_contract:
  deploy:
    requires_review: true
    rollback_plan_required: true
  security:
    least_privilege_default: true
    mfa_for_privileged_actions: true
  reliability:
    monthly_recovery_drill: true
    incident_postmortem_required: true
  cost:
    budget_alert_thresholds: [50, 80, 100]
    untagged_resource_policy: deny
```

운영 계약을 명시하면 담당자가 바뀌어도 품질 기준이 유지됩니다. 클라우드의 핵심은 리소스를 빨리 만드는 능력이 아니라, 같은 품질을 반복해서 만드는 능력입니다. 따라서 이 문서와 같은 계약은 초기에 작게 시작해도 반드시 있어야 하며, 분기 단위로 업데이트하는 루틴을 두는 편이 안정적입니다.

### 장애/비용/보안을 함께 보는 회고 포맷

1. 무엇이 실패했는가를 한 문장으로 기록합니다.
2. 탐지 시점과 첫 대응 시점을 분 단위로 기록합니다.
3. 영향 범위(사용자 수, 금액, 데이터 범위)를 숫자로 기록합니다.
4. 재발 방지 항목을 자동화/문서/훈련으로 분류합니다.
5. 다음 점검 날짜를 지정하고 담당자를 명시합니다.

위 다섯 단계는 단순하지만 반복 효과가 큽니다. 특히 비용 이슈도 장애와 같은 수준으로 회고에 포함하면, 기술 선택과 운영 비용을 분리해서 보는 습관을 줄일 수 있습니다.



### 실무 적용 시나리오

다음 시나리오는 교육용 예시이지만, 실제 프로젝트에서 의사결정을 정리할 때 그대로 활용할 수 있습니다.

| 상황 | 선택 | 이유 | 검증 방법 |
| --- | --- | --- | --- |
| 신규 서비스 초기 론칭 | 단순한 기본 아키텍처 + 필수 가드레일 | 속도와 안정성의 균형 | 체크리스트 기반 사전 점검 |
| 트래픽 급증 이벤트 | 자동 확장 + 임계값 알림 강화 | 수동 대응 지연 방지 | 부하 테스트 + 알람 리허설 |
| 보안 감사 대응 | 권한 축소 + 로그 보존 정책 정리 | 증빙 가능성 확보 | 감사 항목 매핑 문서 |
| 비용 급증 발생 | 태그 누락/유휴 자원 우선 정리 | 즉시 효과가 큼 | 주간 비용 리포트 비교 |

시나리오 기반으로 운영하면 기술 논의가 추상적 취향 싸움으로 흐르지 않습니다. 각 선택에 대해 "왜 이 결정을 했는가"와 "어떻게 검증할 것인가"를 짝지어 기록하면, 팀이 커져도 의사결정 품질을 유지할 수 있습니다. 또한 운영 회고에서 같은 포맷을 재사용하면 변경 누락과 책임 공백을 줄일 수 있습니다.



### 빠른 점검 메모

운영 단계에서는 정답 하나보다 반복 가능한 점검 리듬이 더 중요합니다. 배포 전 점검, 주간 운영 점검, 월간 개선 회고를 분리해 기록하면 누락이 줄어듭니다. 특히 신규 팀원이 합류할 때는 문서의 완성도보다 문서의 최신성이 더 큰 가치를 만듭니다. 따라서 작은 변경이라도 근거와 검증 결과를 함께 남기는 습관이 필요합니다.

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

Tags: Cloud, FinOps, Cost, AWS, Architecture
