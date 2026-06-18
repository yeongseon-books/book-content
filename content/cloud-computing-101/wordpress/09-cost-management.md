---
title: "바이브코딩을 위한 Cloud Computing 기초 (9/10): Cost Management"
series: cloud-computing-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Cloud
  - FinOps
  - Cost
  - AWS
---

# 바이브코딩을 위한 Cloud Computing 기초 (9/10): Cost Management

이 글은 "바이브코딩을 위한 Cloud Computing 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 예산 알림과 태그 정책을 빠르게 만들어 줍니다. 하지만 첫 청구서를 보고 놀라는 일은 너무 흔해서 거의 통과 의례처럼 취급되기도 합니다. 비용을 뒤늦게 확인하는 회계 숫자로만 보면 이미 대응이 늦습니다. 비용은 설계와 운영이 남긴 결과로 읽어야 합니다.

보이지 않는 비용은 줄일 수 없고, 책임이 배정되지 않은 비용은 계속 커집니다. 비용 관리의 첫 단계는 보이게 만드는 것입니다. 그다음 알림을 걸고, 안정적인 부하에는 약정을 적용하고, 마지막으로 실제 사용량에 맞춰 자원 크기를 줄입니다. 이 순서를 지키지 않으면 비용 최적화는 언제나 사후 대응이 됩니다.

FinOps는 재무팀의 뒷정리가 아니라 엔지니어링 팀의 설계 습관에 가깝습니다. 비용 놀람은 기술 팀이 피할 수 없는 운명이 아닙니다. 대부분은 가시성 부족, 태그 부재, 유휴 자원 방치, 너무 이른 약정 같은 반복 가능한 실수에서 시작됩니다.

태그, 예산, Savings Plans, 라이트사이징을 중심으로 비용 관리를 엔지니어링의 일부로 보는 관점을 정리합니다.

> **핵심 인사이트:** 비용 관리는 기술 선택이 아니라 가시성과 통제권을 확보하는 운영 결정입니다. 태그가 비용 배분의 출발점이고, SCP로 태그를 강제해야 실제로 작동합니다.

## 이 글에서 다룰 문제

- 클라우드 비용은 왜 예상보다 자주 높게 나올까요?
- 태그는 비용 배분에서 어떤 역할을 할까요?
- Savings Plans와 Reserved Instance는 어떻게 다를까요?
- 알람 피로 없이 유휴 자원을 어떻게 탐지할까요?
- AI가 만든 비용 설정에서 확인해야 할 것은 무엇인가요?

## 비용 관리 핵심 패턴

```python
import boto3
budgets = boto3.client("budgets")
account_id = boto3.client("sts").get_caller_identity()["Account"]

# 월 예산 + 80% 알림
budgets.create_budget(
    AccountId=account_id,
    Budget={
        "BudgetName": "monthly-cap",
        "BudgetLimit": {"Amount": "500", "Unit": "USD"},
        "TimeUnit": "MONTHLY",
        "BudgetType": "COST",
    },
    NotificationsWithSubscribers=[{
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 80.0,
            "ThresholdType": "PERCENTAGE",
        },
        "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "ops@example.com"}],
    }],
)
```

```bash
# 태그별 비용 조회 (Cost Explorer CLI)
aws ce get-cost-and-usage \
    --time-period Start=2026-05-01,End=2026-06-01 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=TAG,Key=team
```

## 변경 전후 비교

**Before: 비용이 보이지 않는 구조**
```text
- 태그 없는 리소스가 섞여 있음
- 예산 알림 없음
- 유휴 인스턴스를 모른 채 방치
- 첫 청구서에서 비용 확인
```

**After: 가시성과 통제권 확보**
```text
- team/env/service 태그 강제 정책 (SCP)
- 80% 실제 + 100% 예측 예산 알림
- 주간 유휴 자원 탐지 스크립트 실행
- Unit Economics로 효율 추적
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 태그 없는 리소스 방치 | 비용 리포트에서 책임 주체 불명 | SCP로 team/env/service 태그 강제 |
| 예산 알림만 믿음 | 점진적 증가는 잡지 못함 | Cost Anomaly Detection 병행 |
| 너무 이른 Savings Plans 약정 | 패턴 미파악 상태에서 과약정 | 30일 패턴 관찰 후 적용 |
| 유휴 자원 수동 확인 | 재발 반복, 비용 낭비 | 주간 자동화 스크립트 + Slack 알림 |
| NAT/데이터 전송 비용 간과 | 코드 바깥에서 조용히 증가 | 아키텍처 리뷰에서 별도 점검 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"AWS 월 예산을 만들어줘.
team/env/service 태그가 없으면 EC2 생성을 차단하는 SCP도 포함해야 해.
80% 실제 지출과 100% 예측 초과 알림을 분리해서 설정해줘"

# 비용 최적화 우선순위:
# 1. 태그 표준화 → 가시성 확보
# 2. 예산 알림 → 조기 탐지
# 3. 유휴 자원 정리 → 즉시 절감
# 4. Rightsizing → 지속 절감
# 5. Savings Plans → 안정 부하 할인 (패턴 확인 후)
```

## 운영 체크리스트

- [ ] 모든 리소스에 team, env, service 태그가 있다
- [ ] 월 예산 알림(80% 실제 + 100% 예측)이 활성화되어 있다
- [ ] Cost Allocation Tags가 Billing에서 활성화되어 있다
- [ ] 유휴 자원 탐지를 주기적으로 실행한다
- [ ] Savings Plans 적용 전 30일 이상 패턴을 관찰했다
- [ ] Unit Economics(요청당/사용자당 비용)를 월별로 추적한다

## 처음 질문으로 돌아가기

- **클라우드 비용은 왜 예상보다 자주 높게 나올까요?** 태그 없는 리소스, 유휴 자원 방치, NAT/데이터 전송 비용 간과가 반복 원인입니다. 가시성 확보가 가장 먼저입니다.
- **태그는 비용 배분에서 어떤 역할을 할까요?** 태그가 없으면 비용 리포트는 총합만 보여줍니다. team/env/service 태그와 SCP 강제 정책이 출발점입니다.
- **Savings Plans와 Reserved Instance 차이는?** Savings Plans는 인스턴스 패밀리/리전 변경이 가능한 유연한 약정, RI는 특정 인스턴스 계열에 더 강하게 묶이지만 할인율이 높습니다. Compute SP로 시작이 안전합니다.

## 정리

바이브코딩에서 AI가 만들어 준 예산 알림과 태그 정책에서 Cost Allocation Tags 활성화 여부, SCP 강제 정책 포함 여부, Savings Plans 약정 시점을 반드시 확인하세요. 비용 최적화는 한 번의 큰 결정보다 정기적인 작은 조정의 합에 가깝습니다. 다음 글에서는 시리즈 마지막으로 Cloud Architecture 기초를 정리합니다.

## 참고 자료

- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [Savings Plans](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html)
- [FinOps Foundation](https://www.finops.org/framework/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Cloud Computing 기초 (1/10): Cloud Computing이란 무엇인가?
- 바이브코딩을 위한 Cloud Computing 기초 (2/10): IaaS, PaaS, SaaS
- 바이브코딩을 위한 Cloud Computing 기초 (3/10): Region과 Availability Zone
- 바이브코딩을 위한 Cloud Computing 기초 (4/10): Compute
- 바이브코딩을 위한 Cloud Computing 기초 (5/10): Storage
- 바이브코딩을 위한 Cloud Computing 기초 (6/10): Network
- 바이브코딩을 위한 Cloud Computing 기초 (7/10): Identity와 Security
- 바이브코딩을 위한 Cloud Computing 기초 (8/10): Monitoring
- **바이브코딩을 위한 Cloud Computing 기초 (9/10): Cost Management (현재 글)**
- 바이브코딩을 위한 Cloud Computing 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, Cloud, FinOps, Cost, AWS
