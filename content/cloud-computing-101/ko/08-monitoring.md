---
series: cloud-computing-101
episode: 8
title: Monitoring
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Cloud
  - Monitoring
  - CloudWatch
  - AWS
  - Observability
seo_description: CloudWatch 메트릭, 로그, 알람으로 시작하는 클라우드 모니터링의 기초를 boto3 예제와 함께 정리한 입문 글
last_reviewed: '2026-05-04'
---

# Monitoring

> Cloud Computing 101 시리즈 (8/10)


## 이 글에서 다룰 문제

*모니터링 없이* 운영하면 *고객* 이 *장애* 를 먼저 알게 됩니다. *알람* 한 줄이 *밤잠* 을 지킵니다.

## 전체 흐름
```mermaid
flowchart LR
    App["app"] --> Logs["log"]
    App --> Metric["metric"]
    Metric --> Alarm["alarm"]
    Alarm --> SNS["sns/email"]
    Logs --> Insight["query"]
```

## Before/After

**Before**: *오류* 는 *고객 문의* 로 발견.

**After**: *5xx* 비율 *임계값* 초과 시 *Slack 알림*.

## CloudWatch 알람

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

### 3단계 — 구독 (이메일)

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

## 이 코드에서 주목할 점

- *Period* 와 *EvaluationPeriods* 가 *민감도* 결정.
- *사용자 정의 메트릭* 은 *비즈니스 지표* 에 활용.
- *Topic* 으로 *수신자* 분리.

## 자주 하는 실수 5가지

1. ***모든 것* 에 알람 → *알람 피로*.**
2. ***로그* 만 있고 *메트릭* 없음.**
3. ***임계값* 이 *너무 민감* / *둔감*.**
4. ***로그 보존 기간* 무한 → 비용.**
5. ***대시보드* 가 *너무 복잡* 해 *읽히지 않음*.**

## 실무에서는 이렇게 쓰입니다

*ALB* 5xx 비율, *RDS* 연결 수, *Lambda* 에러율, *주문 생성* 분당 카운트 → *대시보드* + *알람* + *Slack/PagerDuty*.

## 체크리스트

- [ ] *핵심 메트릭* 알람 존재.
- [ ] *로그 보존* 정책 설정.
- [ ] *대시보드* 1개 이상 운영.
- [ ] *온콜* 통보 경로 점검.

## 정리 및 다음 단계

관측이 잡혔으면 *비용* 도 봐야 합니다. 다음 글은 *Cost Management*.

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

- [AWS CloudWatch 사용자 가이드](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)
- [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)

Tags: Cloud, Monitoring, CloudWatch, AWS, Observability
