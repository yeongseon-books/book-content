---
title: "바이브코딩을 위한 Cloud Computing 기초 (8/10): Monitoring"
series: cloud-computing-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Cloud
  - Monitoring
  - CloudWatch
  - AWS
  - Observability
---

# 바이브코딩을 위한 Cloud Computing 기초 (8/10): Monitoring

이 글은 "바이브코딩을 위한 Cloud Computing 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 CloudWatch 알람을 빠르게 만들어 줍니다. 하지만 모니터링 없이 운영하면 장애를 발견하는 순서가 늘 나쁩니다. 고객이 먼저 신고하고, 팀은 뒤늦게 원인을 추적하며, 대응은 이미 늦어진 상태에서 시작됩니다. 좋은 모니터링은 데이터를 많이 모으는 일이 아니라, 무슨 일이 일어나는지 빠르게 연결하는 일입니다.

메트릭, 로그, 트레이스가 각각 어떤 질문에 답하는지부터 시작해 CloudWatch 알람까지 정리합니다.

> **핵심 인사이트:** 모니터링의 핵심은 문제를 빨리 감지하고 원인을 빨리 찾는 운영 신호 체계를 만드는 것입니다. SLO가 알람 임계값의 근거가 됩니다.

## 이 글에서 다룰 문제

- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- CloudWatch는 어떤 기본 기능을 제공할까요?
- 알람과 SNS 알림은 어떻게 연결될까요?
- 알람 피로(Alert Fatigue)를 어떻게 줄일까요?
- AI가 만든 모니터링 설정에서 확인해야 할 것은 무엇인가요?

## 관측 가능성의 세 기둥과 CloudWatch 알람

| 구분 | 핵심 질문 | 대표 도구 |
|------|-----------|-----------|
| Metric | 지금 상태가 평소와 다른가 | CloudWatch Metrics |
| Log | 정확히 어떤 이벤트가 발생했는가 | CloudWatch Logs |
| Trace | 어느 서비스 구간에서 지연이 생겼는가 | AWS X-Ray |

```python
import boto3
cw = boto3.client("cloudwatch")
sns = boto3.client("sns")

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

## 변경 전후 비교

**Before: 고객이 먼저 알리는 구조**
```text
- 장애 발생
- 고객 문의 접수
- 팀이 뒤늦게 원인 추적 시작
- 이미 늦어진 대응
```

**After: 알람이 먼저 알리는 구조**
```text
- CPU/5xx 비율이 임계값 초과
- SNS → Slack/이메일 알림 (수분 내)
- 팀이 선제적으로 대응
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 모든 항목에 알람 설정 | 알람 피로로 실제 장애 알람 무시 | 행동 가능한 알람만 유지 |
| 로그만 있고 메트릭 없음 | 추세 파악 불가 | 메트릭 + 로그 함께 수집 |
| 임계값이 너무 민감하거나 둔감 | 오탐 또는 탐지 지연 | SLO 기반 임계값 설정 |
| 로그 보존 기간 무기한 | CloudWatch 비용 폭증 | 용도별 보존 기간 설정 |
| 비즈니스 메트릭 없음 | 인프라 정상인데 서비스 장애 못 감지 | 주문 수 등 비즈니스 신호 추가 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"CloudWatch CPU 알람을 만들어줘.
80% 초과 시 SNS로 이메일 알림,
5분 평균으로 5회 연속 초과할 때만 울려야 해"

# 알람 설계 기준 (Google Golden Signals):
# - Latency: p95/p99 응답 시간
# - Traffic: 초당 요청 수 (RPS)
# - Errors: 5xx 비율
# - Saturation: CPU/메모리/디스크
```

## 운영 체크리스트

- [ ] 핵심 메트릭(CPU, 5xx, 지연)에 알람이 있다
- [ ] 로그 보존 정책이 설정되어 있다
- [ ] 운영용 대시보드가 최소 1개 있다
- [ ] 온콜 알림 경로를 실제로 점검했다
- [ ] 알람 심각도 분류 체계가 정의되어 있다
- [ ] 구조화 로그에 correlation_id가 포함되어 있다

## 처음 질문으로 돌아가기

- **메트릭, 로그, 트레이스의 차이는?** 메트릭은 숫자 추세, 로그는 이벤트 상세, 트레이스는 분산 호출 경로를 보여줍니다. 셋을 함께 봐야 장애 원인을 구조적으로 좁힐 수 있습니다.
- **알람 임계값은 어떻게 정하나요?** SLO가 임계값의 근거가 됩니다. "왜 이 수치에서 알람이 울리는가"에 SLO로 답할 수 있어야 합니다.
- **알람 피로를 줄이려면?** 행동 가능한 알람만 남기고, 주간 알람 리뷰로 임계값을 조정합니다.

## 정리

바이브코딩에서 AI가 만들어 준 CloudWatch 알람에서 `Period`, `EvaluationPeriods`, `Threshold` 조합을 반드시 확인하고, 비즈니스 메트릭과 알람 심각도 분류까지 추가하세요. 다음 글에서는 FinOps의 출발점인 Cost Management를 다룹니다.

## 참고 자료

- [AWS CloudWatch user guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
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
- **바이브코딩을 위한 Cloud Computing 기초 (8/10): Monitoring (현재 글)**
- 바이브코딩을 위한 Cloud Computing 기초 (9/10): Cost Management
- 바이브코딩을 위한 Cloud Computing 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, Cloud, Monitoring, CloudWatch, AWS, Observability
