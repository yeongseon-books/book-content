---
series: cloud-computing-101
episode: 8
title: Monitoring
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
  - Monitoring
  - CloudWatch
  - AWS
  - Observability
seo_description: 메트릭, 로그, 트레이스와 CloudWatch 알람의 기본을 정리합니다.
last_reviewed: '2026-05-14'
---

# Monitoring

운영 중인 시스템을 보지 못하면 문제가 생겼을 때 가장 먼저 알려 주는 사람은 늘 고객이 됩니다. 반대로 잘 설계된 알람 하나는 장애 대응 시간을 크게 줄여 주고, 주말 한 번을 통째로 지켜 주기도 합니다.

좋은 모니터링은 데이터를 많이 모으는 일이 아닙니다. 지금 무슨 일이 일어나는지, 왜 일어나는지, 누구에게 알려야 하는지를 빠르게 연결하는 일입니다.

이 글은 Cloud Computing 101 시리즈의 8번째 글입니다.

여기서는 메트릭, 로그, 트레이스가 각각 어떤 질문에 답하는지부터 시작해 CloudWatch 알람까지 정리해 보겠습니다.

## 이 글에서 다룰 문제

- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- CloudWatch는 어떤 기본 기능을 제공할까요?
- 알람과 SNS 알림은 어떻게 연결될까요?
- 운영 대시보드는 얼마나 단순해야 할까요?
- 모니터링 설계에서 가장 자주 하는 실수는 무엇일까요?

> 모니터링은 숫자(메트릭), 텍스트(로그), 흐름(트레이스)이라는 세 축으로 시스템을 관찰 가능하게 만드는 일입니다.

## 왜 중요한가

모니터링 없이 운영하면 장애를 발견하는 순서가 늘 나쁩니다. 고객이 먼저 신고하고, 팀은 뒤늦게 원인을 추적하며, 대응은 이미 늦어진 상태에서 시작됩니다. 반대로 핵심 메트릭과 적절한 알람이 있으면 문제가 커지기 전에 먼저 움직일 수 있습니다.

또한 모니터링은 단순한 시각화가 아니라 운영 계약입니다. 무엇을 경고해야 하는지, 어디까지가 정상 범위인지, 누가 알림을 받아야 하는지를 합의하는 작업이기도 합니다.

## 한눈에 보는 개념

![메트릭이 알람으로 이어지고 로그가 분석 쿼리로 이어지는 관측 흐름](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/08/08-01-concept-at-a-glance.ko.png)

*메트릭이 알람으로 이어지고 로그가 분석 쿼리로 이어지는 관측 흐름*
메트릭은 추세와 임계값에 강하고, 로그는 사건의 세부 맥락에 강하며, 트레이스는 분산 호출의 흐름을 보여 줍니다. 이 셋을 구분해야 “지금 상태가 이상한가”와 “왜 이상한가”를 함께 풀 수 있습니다.

## 핵심 용어

- **Metric**: CPU, 지연 시간 같은 숫자 시계열입니다.
- **Log**: 요청, 오류 같은 텍스트 이벤트입니다.
- **Trace**: 분산 호출 경로를 보여 주는 흐름 데이터입니다.
- **Alarm**: 임계값을 넘을 때 알림을 보내는 규칙입니다.
- **SLO**: 예를 들어 99.9% 같은 운영 목표입니다.

## Before / After

**Before**에서는 고객 문의를 통해 오류를 처음 알게 됩니다.

**After**에서는 5xx 비율이 임계값을 넘으면 몇 분 안에 Slack이나 메일로 알림이 갑니다.

이 차이는 단순한 편의성이 아니라 대응 속도와 장애 범위를 바꾸는 운영 능력의 차이입니다.

## 실습: CloudWatch 알람 만들기

### 1단계 — 클라이언트

```python
import boto3
cw = boto3.client("cloudwatch")
sns = boto3.client("sns")
```

### 2단계 — 토픽 만들기

```python
def create_topic(name):
    res = sns.create_topic(Name=name)
    return res["TopicArn"]
```

### 3단계 — 이메일 구독

```python
def subscribe(topic_arn, email):
    sns.subscribe(
        TopicArn=topic_arn, Protocol="email", Endpoint=email,
    )
```

### 4단계 — CPU 알람

```python
def cpu_alarm(name, instance_id, topic_arn):
    cw.put_metric_alarm(
        AlarmName=name,
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        Statistic="Average",
        Period=60, EvaluationPeriods=5,
        Threshold=80.0, ComparisonOperator="GreaterThanThreshold",
        AlarmActions=[topic_arn],
    )
```

### 5단계 — 사용자 정의 메트릭

```python
def emit(value):
    cw.put_metric_data(
        Namespace="MyApp",
        MetricData=[{"MetricName": "OrdersPerMin", "Value": value}],
    )
```

이 예제는 좋은 모니터링이 인프라 메트릭에서 끝나지 않는다는 점을 보여 줍니다. CPU 같은 시스템 신호도 중요하지만, 분당 주문 수처럼 비즈니스 메트릭을 함께 봐야 실제 서비스 상태를 더 정확히 이해할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `Period`와 `EvaluationPeriods` 조합이 알람 민감도를 결정합니다.
- 사용자 정의 메트릭은 비즈니스 신호를 감시할 때 유용합니다.
- SNS Topic은 알람과 수신 대상을 분리해 줍니다.

## 이 예제를 실제로 검증하는 순서

모니터링 예제는 알람이 만들어졌다는 사실보다 "언제 울리는가"를 명확히 이해하는 것이 중요합니다. `Period`, `EvaluationPeriods`, `Threshold` 조합을 읽을 수 있어야 과민한 알람과 둔감한 알람을 구분할 수 있습니다.

```bash
aws cloudwatch describe-alarms --alarm-names high-cpu-demo
```

**Expected output:**

- `MetricName`이 `CPUUtilization`으로 설정되어 있어야 합니다.
- `Period=60`, `EvaluationPeriods=5`, `Threshold=80` 조합이 그대로 보여야 합니다.
- SNS 구독 메일을 열어 승인하지 않았다면 알람은 만들어져도 실제 통보는 가지 않을 수 있습니다.

### 자주 막히는 지점

- 알람이 많다고 관측성이 좋아지는 것은 아닙니다. 팀이 행동할 수 없는 알람은 오히려 신뢰를 떨어뜨립니다.
- 로그 보존 기간을 정하지 않으면 CloudWatch 비용이 조용히 커질 수 있습니다.
- 비즈니스 메트릭이 없으면 인프라 상태는 좋아 보여도 서비스 품질 저하를 놓치기 쉽습니다.

## 메트릭, 로그, 트레이스는 언제 각각 쓸까

메트릭은 “지금 상태가 평소와 다른가”를 빠르게 보는 데 적합합니다. 로그는 “정확히 어떤 요청과 오류가 있었는가”를 파고들 때 유용합니다. 트레이스는 “어느 서비스 구간에서 지연이 생겼는가”를 따라갈 때 강합니다.

세 가지를 한 도구로만 해결하려고 하면 금방 한계가 보입니다. 숫자는 빠르지만 맥락이 부족하고, 로그는 자세하지만 추세 파악이 느리며, 트레이스는 흐름을 보여 주지만 모든 비즈니스 사건을 대신 설명하지는 못합니다.

## 자주 하는 실수 5가지

1. 모든 항목에 알람을 걸어 알람 피로를 만듭니다.
2. 로그만 있고 메트릭이 없습니다.
3. 임계값이 너무 민감하거나 너무 둔감합니다.
4. 로그 보존 기간을 무기한으로 둡니다.
5. 대시보드를 너무 복잡하게 만듭니다.

## 실무에서는 이렇게 생각합니다

- 모든 알람은 실제 행동으로 이어질 수 있어야 합니다.
- SLO가 알람 임계값을 결정합니다.
- 로그는 백업이 아니라 질문에 답하는 도구입니다.
- 대시보드는 적을수록 읽기 쉽습니다.
- 게임데이나 훈련으로 알람이 실제로 동작하는지 검증해야 합니다.

## 체크리스트

- [ ] 핵심 메트릭에 대한 알람이 존재하는가.
- [ ] 로그 보존 정책이 설정되어 있는가.
- [ ] 운영용 대시보드가 최소 1개 이상 있는가.
- [ ] 온콜 통보 경로를 실제로 점검했는가.

## 연습 문제

1. 메트릭과 로그의 차이를 한 줄로 설명해 보세요.
2. “CPU 80%가 5분 지속” 알람의 `Period`와 `EvaluationPeriods`를 적어 보세요.
3. 알람 피로를 줄이는 전략 하나를 제안해 보세요.

## 정리 및 다음 단계

관측 체계를 갖췄다면 이제는 그 시스템을 얼마에 운영하는지도 함께 통제해야 합니다. 다음 글에서는 FinOps의 출발점인 Cost Management로 넘어가겠습니다.

<!-- toc:begin -->
- [Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Compute](./04-compute.md)
- [Storage](./05-storage.md)
- [Network](./06-network.md)
- [Identity와 Security](./07-identity-and-security.md)
- **Monitoring (현재 글)**
- Cost Management (예정)
- Cloud Architecture 기초 (예정)
<!-- toc:end -->

## 참고 자료

- [AWS CloudWatch user guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)
- [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)

Tags: Cloud, Monitoring, CloudWatch, AWS, Observability
