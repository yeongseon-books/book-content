
# Cost Management

> Cloud Computing 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *클라우드 청구서* 가 *왜* *예측보다 항상 더 많이* 나올까요?

> *클라우드 비용 은 *가시성(태그)*, *예산(알림)*, *약정(Savings)*, *최적화(라이트사이징)* 의 *4단계* 로 다스립니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *비용 모델* 의 *기본*
- *태그* 로 *비용 분배*
- *예산 알림*
- *Savings Plans / RI*
- 흔한 함정 5가지

## 왜 중요한가

*첫 청구서* 의 *놀람* 은 *전형적* 입니다. *FinOps* 는 *엔지니어링* 의 일부입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Tag["tag"] --> Visibility["visibility"]
    Budget["budget"] --> Alert["alert"]
    Savings["savings plan"] --> Discount["discount"]
    Right["right-size"] --> Saving["saving"]
```

## 핵심 용어 정리

- **Tag**: *리소스* 에 붙는 *키-값* 라벨.
- **Budget**: *월 한도* 와 *알림*.
- **Savings Plans**: *기간 약정* 으로 *할인*.
- **Reserved Instance**: *특정 인스턴스 약정*.
- **Rightsizing**: *실사용* 에 맞춰 *축소*.

## Before/After

**Before**: *모든 인스턴스* 가 *m5.xlarge*, *야간* 에도 *풀타임 가동*.

**After**: *비프로덕션* 은 *야간 정지*, *프로덕션* 은 *Savings Plans*.

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

### 5단계 — 태그 강제 (의사 정책)

```python
require_tags = {
    "Effect": "Deny",
    "Action": "ec2:RunInstances",
    "Resource": "*",
    "Condition": {"Null": {"aws:RequestTag/Project": "true"}},
}
```

## 이 코드에서 주목할 점

- *80%* 알림은 *행동 시간* 을 줍니다.
- *Tag* 정책은 *비용 추적* 의 *전제 조건*.
- *예산* 은 *팀 단위* 로도 가능.

## 자주 하는 실수 5가지

1. ***태그* 없는 *리소스* 방치.**
2. ***예산 알림* 없음.**
3. ***SP* 를 *과다 약정*.**
4. ***고가 인스턴스* 를 *유휴 상태* 로 방치.**
5. ***NAT/데이터 전송 비용* 간과.**

## 실무에서는 이렇게 쓰입니다

*Project=acme* 태그로 *팀 비용 분리*, *야간 자동 정지* Lambda, *SP 1년 약정*, *분기별* *라이트사이징* 회의.

## 시니어 엔지니어는 이렇게 생각합니다

- *비용* 은 *아키텍처 지표*.
- *태그* 가 *FinOps 의 출발*.
- *Savings* 는 *변동성* 을 본 뒤.
- *전송 비용* 은 *드러나지 않는다*.
- *비용 회의* 는 *주기적* 으로.

## 체크리스트

- [ ] *모든 리소스* 에 *Project 태그*.
- [ ] *월 예산* 알림 활성.
- [ ] *유휴 자원* 정기 점검.
- [ ] *SP/RI* 검토 분기 1회.

## 연습 문제

1. *On-demand* 와 *Savings Plans* 의 *차이* 를 한 줄로.
2. *비용 추적* 을 위한 *최소 3가지 태그* 를 적으세요.
3. *NAT 비용* 을 줄이는 *전략* 한 가지를 들어 보세요.

## 정리 및 다음 단계

운영, 보안, 비용까지 다 봤으면 *전체 그림* 을 묶어 봅니다. 다음 글은 *Cloud Architecture 기초*.

- [Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Compute](./04-compute.md)
- [Storage](./05-storage.md)
- [Network](./06-network.md)
- [Identity와 Security](./07-identity-and-security.md)
- [Monitoring](./08-monitoring.md)
- **Cost Management (현재 글)**
- Cloud Architecture 기초 (예정)
## 참고 자료

- [AWS Billing 사용자 가이드](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-what-is.html)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [Savings Plans](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html)
- [FinOps Foundation](https://www.finops.org/framework/)

Tags: Cloud, FinOps, Cost, AWS, Architecture

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
