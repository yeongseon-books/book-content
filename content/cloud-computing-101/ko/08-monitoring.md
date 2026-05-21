---
series: cloud-computing-101
episode: 8
title: "Cloud Computing 101 (8/10): Monitoring"
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

# Cloud Computing 101 (8/10): Monitoring

운영 중인 시스템을 보지 못하면 문제가 생겼을 때 가장 먼저 알려 주는 사람은 늘 고객이 됩니다. 반대로 잘 설계된 알람 하나는 장애 대응 시간을 크게 줄여 주고, 주말 한 번을 통째로 지켜 주기도 합니다.

좋은 모니터링은 데이터를 많이 모으는 일이 아닙니다. 지금 무슨 일이 일어나는지, 왜 일어나는지, 누구에게 알려야 하는지를 빠르게 연결하는 일입니다.

이 글은 Cloud Computing 101 시리즈의 8번째 글입니다.

여기서는 메트릭, 로그, 트레이스가 각각 어떤 질문에 답하는지부터 시작해 CloudWatch 알람까지 정리해 보겠습니다.

## 먼저 던지는 질문

- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- CloudWatch는 어떤 기본 기능을 제공할까요?
- 알람과 SNS 알림은 어떻게 연결될까요?

## 큰 그림

![Cloud Computing 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/08/08-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 8장 흐름 개요*

메트릭(Metric)은 CPU, 메모리, 네트워크 같은 수치적 신호입니다. 로그(Log)는 애플리케이션이 기록한 이벤트 텍스트입니다. 트레이스(Trace)는 요청 하나가 여러 서비스를 거쳐 가면서 남긴 기록입니다. 대시보드는 이들을 시각화하고, 알람은 임계값을 넘으면 자동으로 알려줍니다.

> 모니터링의 핵심은 문제를 빨리 감지하고, 원인을 빨리 찾는 운영 신호 체계를 만드는 것입니다.

## 왜 중요한가

모니터링 없이 운영하면 장애를 발견하는 순서가 늘 나쁩니다. 고객이 먼저 신고하고, 팀은 뒤늦게 원인을 추적하며, 대응은 이미 늦어진 상태에서 시작됩니다. 반대로 핵심 메트릭과 적절한 알람이 있으면 문제가 커지기 전에 먼저 움직일 수 있습니다.

또한 모니터링은 단순한 시각화가 아니라 운영 계약입니다. 무엇을 경고해야 하는지, 어디까지가 정상 범위인지, 누가 알림을 받아야 하는지를 합의하는 작업이기도 합니다.

## 한눈에 보는 개념

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

CPU와 메모리만 모니터링하면 애플리케이션 수준의 문제를 놓칩니다. 에러율, 응답 시간, 데이터베이스 커넥션 수 같은 비즈니스 메트릭을 함께 봐야 합니다.

로그 없이는 문제가 났을 때 무엇이 잘못되었는지 알 수 없습니다. 중요한 결정 지점(예: 사용자 로그인 시도, 결제 실패)을 반드시 로그로 남겨야 합니다.
  - 본문의 기준은 Monitoring를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
알람은 너무 많으면 무시하게 되고(알람 피로), 너무 적으면 문제를 놓칩니다. 실제 문제만 알리는 알람을 설정하고 정기적으로 검토하는 것이 중요합니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **알람과 SNS 알림은 어떻게 연결될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

## 모니터링 신호 체계 확장

| 신호 | 핵심 질문 | 대표 지표/데이터 | 한계 |
| --- | --- | --- | --- |
| Metric | 지금 이상한가 | CPU, 에러율, p95 지연 | 원인 맥락 부족 |
| Log | 정확히 무엇이 일어났나 | 요청/에러 이벤트 | 양이 많으면 탐색 난이도 증가 |
| Trace | 어디서 느려졌나 | 서비스 간 호출 구간 | 샘플링 전략 필요 |

```yaml
observability_baseline:
  metrics:
    - name: HTTP5xxRate
      threshold: 1.0
    - name: P95LatencyMs
      threshold: 500
  logs:
    retention_days: 30
    structured_json: true
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



짧은 결론으로 정리하면, 운영 품질은 도구 선택 자체보다 기준의 일관성과 검증 습관에서 결정됩니다. 기준이 문서와 자동화로 남아 있어야 다음 변경에서도 같은 품질을 반복할 수 있습니다.

추가 점검 문장입니다.

## 운영 알람 설계 확장 예시

알람은 개수보다 설계 품질이 중요합니다. 아래 예시는 인프라 신호와 서비스 신호를 함께 묶어 운영자가 실제로 행동 가능한 경보 체계를 만드는 방식입니다.

```bash
# AWS: 알람/대시보드 상태 점검
aws cloudwatch describe-alarms --state-value ALARM
aws cloudwatch get-dashboard --dashboard-name core-service-dashboard

# Azure Monitor: 메트릭 알림 규칙 조회
az monitor metrics alert list --resource-group rg-core-prod

# Google Cloud Monitoring: 정책 목록 조회
gcloud alpha monitoring policies list --format="table(displayName,enabled)"
```

```hcl
resource "aws_cloudwatch_metric_alarm" "http_5xx_rate" {
  alarm_name          = "prod-http-5xx-rate-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 20
  alarm_description   = "5xx burst detection"
  treat_missing_data  = "notBreaching"
}
```

| 알람 대상 | 지표 예시 | 권장 임계값 접근 |
| --- | --- | --- |
| 가용성 | 5xx 비율 | 트래픽 구간별 동적 기준 |
| 성능 | p95 지연 | SLO 기반 임계값 |
| 용량 | CPU/메모리 | 증설 리드타임 고려 |
| 비즈니스 | 주문 실패율 | 인프라 지표와 동시 확인 |

텍스트 아키텍처 다이어그램:
`App Metric/Log/Trace -> CloudWatch/Azure Monitor/Cloud Monitoring -> Alert Policy -> SNS/Email/ChatOps -> On-call Runbook`

이 구조를 운영 루틴에 붙이면 "문제가 발생한 뒤 조사"가 아니라 "징후 단계에서 대응"으로 전환할 수 있습니다. 알람 규칙, 수신 경로, 런북 링크를 한 세트로 유지하는 것이 핵심입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- [Cloud Computing 101 (7/10): Identity와 Security](./07-identity-and-security.md)
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
