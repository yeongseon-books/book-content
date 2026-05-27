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

이 글은 Cloud Computing 101 시리즈의 8번째 글입니다.

좋은 모니터링은 데이터를 많이 모으는 일이 아닙니다. 지금 무슨 일이 일어나는지, 왜 일어나는지, 누구에게 알려야 하는지를 빠르게 연결하는 일입니다.

여기서는 메트릭, 로그, 트레이스가 각각 어떤 질문에 답하는지부터 시작해 CloudWatch 알람까지 정리해 보겠습니다.

![Cloud Computing 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/08/08-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 8장 흐름 개요*
> 모니터링의 핵심은 문제를 빨리 감지하고, 원인을 빨리 찾는 운영 신호 체계를 만드는 것입니다.

## 먼저 던지는 질문

- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- CloudWatch는 어떤 기본 기능을 제공할까요?
- 알람과 SNS 알림은 어떻게 연결될까요?

## 왜 중요한가

모니터링 없이 운영하면 장애를 발견하는 순서가 늘 나쁩니다. 고객이 먼저 신고하고, 팀은 뒤늦게 원인을 추적하며, 대응은 이미 늦어진 상태에서 시작됩니다. 반대로 핵심 메트릭과 적절한 알람이 있으면 문제가 커지기 전에 먼저 움직일 수 있습니다.

또한 모니터링은 단순한 시각화가 아니라 운영 계약입니다. 무엇을 경고해야 하는지, 어디까지가 정상 범위인지, 누가 알림을 받아야 하는지를 합의하는 작업이기도 합니다.

## 관측 가능성의 세 기둥 비교

메트릭, 로그, 트레이스는 관측 가능성(Observability)의 세 기둥으로 불립니다. 각각이 답하는 질문, 강점, 한계가 다르기 때문에 셋을 조합해야 운영 상황을 입체적으로 파악할 수 있습니다.

| 구분 | Metric | Log | Trace |
| --- | --- | --- | --- |
| 핵심 질문 | 지금 상태가 평소와 다른가 | 정확히 어떤 이벤트가 발생했는가 | 어느 서비스 구간에서 지연이 생겼는가 |
| 데이터 형태 | 숫자 시계열 (타임스탬프 + 값) | 텍스트 이벤트 (구조화/비구조화) | 스팬(span) 트리 (parent-child 관계) |
| 저장 비용 | 낮음 (집계된 숫자) | 높음 (원본 텍스트 전체 보관) | 중간 (샘플링 비율에 따라 가변) |
| 탐색 속도 | 빠름 (인덱스된 시계열 쿼리) | 느림 (전문 검색 필요) | 중간 (trace ID 기반 조회) |
| 대표 도구 | CloudWatch Metrics, Prometheus | CloudWatch Logs, Elasticsearch | AWS X-Ray, Jaeger, Zipkin |
| 최적 사용 시점 | 대시보드, 알람, 용량 계획 | 디버깅, 감사, 포렌식 | 분산 시스템 병목 분석 |
| 한계 | 원인 맥락 부족 | 양이 많으면 탐색 비용 증가 | 모든 요청을 추적하면 오버헤드 발생 |

이 셋을 하나의 도구로만 해결하려 하면 금방 한계가 보입니다. 숫자는 빠르지만 맥락이 부족하고, 로그는 자세하지만 추세 파악이 느리며, 트레이스는 흐름을 보여 주지만 모든 비즈니스 사건을 대신 설명하지는 못합니다.

## 핵심 용어

- **Metric**: CPU, 지연 시간 같은 숫자 시계열입니다.
- **Log**: 요청, 오류 같은 텍스트 이벤트입니다.
- **Trace**: 분산 호출 경로를 보여 주는 흐름 데이터입니다.
- **Alarm**: 임계값을 넘을 때 알림을 보내는 규칙입니다.
- **SLI (Service Level Indicator)**: 서비스 품질을 측정하는 구체적 지표입니다. 예를 들어 "전체 요청 중 200ms 이내 응답 비율"입니다.
- **SLO (Service Level Objective)**: SLI에 대한 목표 수치입니다. 예를 들어 "월간 가용성 99.9%"입니다.
- **SLA (Service Level Agreement)**: SLO를 위반했을 때의 계약 조건(보상, 크레딧 등)입니다.
- **Golden Signals**: Google SRE가 제안한 네 가지 핵심 신호 — 지연(Latency), 트래픽(Traffic), 오류(Errors), 포화도(Saturation)입니다.

## SLI, SLO, SLA 실전 예시

운영 목표를 숫자로 정의하지 않으면 "충분히 안정적인가"라는 질문에 답할 수 없습니다. 아래 표는 가용성 목표에 따른 허용 다운타임을 보여 줍니다.

| 가용성 목표 | 연간 허용 다운타임 | 월간 허용 다운타임 | 현실적 난이도 |
| --- | --- | --- | --- |
| 99% (two nines) | 3일 15시간 36분 | 7시간 18분 | 단일 인스턴스로 달성 가능 |
| 99.9% (three nines) | 8시간 46분 | 43분 33초 | 자동 복구 + 이중화 필요 |
| 99.95% | 4시간 23분 | 21분 46초 | 멀티 AZ + 헬스체크 필수 |
| 99.99% (four nines) | 52분 34초 | 4분 21초 | 멀티 리전 + 자동 페일오버 |

SLO는 알람 임계값의 근거가 됩니다. "왜 이 수치에서 알람이 울리는가"라는 질문에 "SLO를 위반할 위험이 있기 때문"이라고 답할 수 있어야 합니다. SLO 없이 설정한 임계값은 근거 없는 추측이고, 팀원이 바뀌면 의미를 잃습니다.

에러 버짓(Error Budget)은 SLO의 역수입니다. 99.9% SLO라면 월간 43분의 에러 버짓이 있고, 이 범위 안에서 배포와 실험을 허용합니다. 에러 버짓이 소진되면 새 기능 배포를 멈추고 안정성 작업에 집중하는 것이 SRE 방식입니다.

## 적용 전후 비교
**Before**에서는 고객 문의를 통해 오류를 처음 알게 됩니다.

**After**에서는 5xx 비율이 임계값을 넘으면 몇 분 안에 Slack이나 메일로 알림이 갑니다.

이 차이는 단순한 편의성이 아니라 대응 속도와 장애 범위를 바꾸는 운영 능력의 차이입니다.

## 로그 수집 아키텍처

로그는 발생 지점에서 끝나는 것이 아니라 중앙 저장소로 모여야 검색과 분석이 가능합니다. 아래는 전형적인 로그 수집 흐름입니다.

```text
[Application]
     |
     | stdout / file
     v
[Log Agent]  (CloudWatch Agent, Fluentd, Filebeat)
     |
     | 버퍼링 + 전송
     v
[Central Log Store]  (CloudWatch Logs, Elasticsearch, Loki)
     |
     | 쿼리 + 필터
     v
[Dashboard / Alert]  (CloudWatch Insights, Kibana, Grafana)
     |
     | 조건 매칭
     v
[Notification]  (SNS, Slack, PagerDuty)
```

각 단계에서 고려할 점이 있습니다.

- **Agent 선택**: CloudWatch Agent는 AWS 환경에서 설정이 간단합니다. 멀티 클라우드라면 Fluentd나 OpenTelemetry Collector가 범용적입니다.
- **버퍼링**: Agent는 네트워크 장애 시 로그를 로컬에 버퍼링합니다. 버퍼 크기와 재전송 정책을 설정해야 유실을 줄입니다.
- **보존 기간**: 로그를 무기한 보관하면 비용이 조용히 커집니다. 용도별로 보존 기간을 분리하는 것이 좋습니다 (운영 로그 30일, 감사 로그 1년 등).

## 구조화된 로그 (Structured Logging)

비구조화 로그는 사람이 읽기엔 괜찮지만 기계가 파싱하기 어렵습니다. JSON 형식의 구조화된 로그를 사용하면 필드 단위 검색과 집계가 가능해집니다.

```json
{
  "timestamp": "2026-05-21T09:15:32.456Z",
  "level": "ERROR",
  "service": "order-api",
  "correlation_id": "req-abc-12345",
  "user_id": "u-98765",
  "message": "Payment gateway timeout",
  "duration_ms": 30012,
  "error_code": "PAYMENT_TIMEOUT",
  "upstream": "payment-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

핵심 필드 설명:

- **correlation_id**: 하나의 요청이 여러 서비스를 거칠 때 동일한 ID를 전파합니다. 이 ID로 검색하면 요청의 전체 여정을 추적할 수 있습니다.
- **trace_id**: 분산 트레이싱 시스템과 연결하는 키입니다. 로그에서 trace_id를 찾으면 X-Ray나 Jaeger에서 해당 트레이스를 바로 열 수 있습니다.
- **duration_ms**: 처리 시간을 숫자로 기록하면 나중에 p50, p95, p99 백분위 집계가 가능합니다.
- **error_code**: 자유 텍스트 메시지 대신 코드화된 오류 유형을 함께 남기면 집계와 알람 조건에 활용할 수 있습니다.

비구조화 로그와 비교하면 차이가 명확합니다.

```text
2026-05-21 09:15:32 ERROR Payment gateway timeout for user u-98765 (took 30012ms)
```

위 로그에서 `duration_ms > 5000`인 이벤트만 추출하려면 정규식 파싱이 필요합니다. JSON 로그라면 필드 쿼리 한 줄로 끝납니다.

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

### CLI로 알람 설정하기

Python SDK 외에 AWS CLI로도 동일한 알람을 만들 수 있습니다. 인프라를 코드로 관리하기 전 빠른 검증에 유용합니다.

```bash
# SNS 토픽 생성
aws sns create-topic --name high-cpu-alert

# 이메일 구독 (승인 메일 확인 필요)
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789012:high-cpu-alert \
  --protocol email \
  --notification-endpoint ops-team@example.com

# CPU 알람 생성
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-demo \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --statistic Average \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:high-cpu-alert
```

## 메트릭 조회와 임계값 점검 스크립트

알람을 설정한 뒤에는 실제 메트릭 값이 임계값에 얼마나 가까운지 주기적으로 확인하는 습관이 필요합니다. 아래 스크립트는 최근 1시간의 CPU 사용률을 조회하고, 경고 수준에 도달했는지 판단합니다.

```python
from datetime import datetime, timedelta, timezone
import boto3

cw = boto3.client("cloudwatch")

def get_cpu_stats(instance_id, hours=1):
    """최근 N시간의 CPU 평균/최대값을 5분 간격으로 조회합니다."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    response = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average", "Maximum"],
    )
    return sorted(response["Datapoints"], key=lambda d: d["Timestamp"])

def check_threshold(datapoints, warn=60.0, critical=80.0):
    """각 데이터포인트의 평균값을 임계값과 비교합니다."""
    results = []
    for dp in datapoints:
        avg = dp["Average"]
        if avg >= critical:
            level = "CRITICAL"
        elif avg >= warn:
            level = "WARNING"
        else:
            level = "OK"
        results.append({
            "time": dp["Timestamp"].isoformat(),
            "avg": round(avg, 2),
            "max": round(dp["Maximum"], 2),
            "level": level,
        })
    return results

if __name__ == "__main__":
    instance_id = "i-0abc123def456"
    stats = get_cpu_stats(instance_id)
    for r in check_threshold(stats):
        print(f"[{r['level']:>8}] {r['time']}  avg={r['avg']}%  max={r['max']}%")
```

이 스크립트의 핵심은 `Period=300`(5분 집계)과 임계값 분리(warn/critical)입니다. 운영 환경에서는 이 로직을 Lambda로 옮기고 결과를 Slack으로 전송하는 패턴이 흔합니다.

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

## 알람 피로 방지 전략

알람이 너무 많이 울리면 팀은 알림을 무시하기 시작합니다. 이것이 알람 피로(Alert Fatigue)입니다. 실제 장애 알람까지 묻히는 상황을 만들지 않으려면 심각도 분류와 라우팅 규칙이 필요합니다.

### 심각도 분류 체계

| 심각도 | 정의 | 대응 시간 | 통보 채널 | 예시 |
| --- | --- | --- | --- | --- |
| P1 (Critical) | 서비스 전체 중단 또는 데이터 유실 위험 | 5분 이내 | 전화 + Slack + PagerDuty | 전체 5xx 비율 50% 초과 |
| P2 (High) | 일부 기능 장애, 사용자 영향 있음 | 15분 이내 | Slack + 이메일 | 결제 실패율 5% 초과 |
| P3 (Medium) | 성능 저하, 즉각 장애는 아님 | 업무 시간 내 | Slack 채널 | p95 지연 2초 초과 |
| P4 (Low) | 정보성, 추세 확인용 | 다음 업무일 | 대시보드 기록 | 디스크 사용률 70% 도달 |

### 라우팅 규칙 설계

```yaml
alert_routing:
  p1_critical:
    channels: [pagerduty, slack-oncall, phone]
    escalation_after_min: 5
    auto_create_incident: true
  p2_high:
    channels: [slack-oncall, email]
    escalation_after_min: 15
    auto_create_incident: true
  p3_medium:
    channels: [slack-alerts]
    escalation_after_min: null
    auto_create_incident: false
  p4_low:
    channels: [dashboard-only]
    escalation_after_min: null
    auto_create_incident: false
```

### 알람 피로를 줄이는 실천 원칙

1. **행동 가능한 알람만 남깁니다.** 알람을 받았을 때 취할 행동이 명확하지 않다면 그 알람은 대시보드로 내립니다.
2. **주간 알람 리뷰를 합니다.** 지난 7일간 울린 알람 중 실제 행동으로 이어진 비율을 측정합니다. 50% 미만이면 임계값을 조정하거나 알람을 제거합니다.
3. **그룹핑과 중복 제거를 적용합니다.** 동일 원인으로 10개 알람이 동시에 울리면 1개의 요약 알림만 전달합니다.
4. **업무 시간 외 알람을 P1/P2로 제한합니다.** 새벽에 P4 알람이 울리면 on-call 엔지니어의 수면만 방해합니다.

## 대시보드 설계 원칙

대시보드는 한 화면에서 서비스 상태를 30초 안에 파악할 수 있어야 합니다. Google SRE의 Golden Signals를 기준으로 구성하면 핵심을 놓치지 않습니다.

| Golden Signal | 측정 대상 | 대시보드 위젯 예시 | 왜 중요한가 |
| --- | --- | --- | --- |
| Latency (지연) | 요청 처리 시간 | p50 / p95 / p99 시계열 그래프 | 사용자 체감 품질의 직접 지표 |
| Traffic (트래픽) | 초당 요청 수 (RPS) | 실시간 RPS 카운터 | 부하 수준과 용량 여유 확인 |
| Errors (오류) | 실패 요청 비율 | 5xx 비율 게이지 + 추세선 | 서비스 정상 여부의 첫 번째 신호 |
| Saturation (포화도) | 자원 사용률 | CPU/메모리/디스크/커넥션 풀 | 한계에 도달하기 전 증설 판단 |

대시보드 구성 시 흔한 실수:

- 위젯을 20개 이상 넣어 한눈에 파악이 불가능한 대시보드를 만듭니다. 핵심 6-8개 위젯이면 충분합니다.
- 절대값만 보여 주고 추세를 보여 주지 않습니다. "지금 CPU 45%"보다 "지난 1시간 동안 30%에서 45%로 상승 중"이 더 유용합니다.
- 비즈니스 메트릭과 인프라 메트릭을 한 대시보드에 섞습니다. 역할별로 분리하는 것이 읽기 쉽습니다 (운영 대시보드 / 비즈니스 대시보드 / 용량 대시보드).

## 모니터링 비용 관리

모니터링은 공짜가 아닙니다. 수집하는 메트릭과 로그가 늘어날수록 비용도 함께 커집니다. "무엇을 수집할 것인가"만큼 "무엇을 수집하지 않을 것인가"가 중요합니다.

| 항목 | 수집 권장 | 수집 주의 / 생략 가능 |
| --- | --- | --- |
| 애플리케이션 에러 로그 | 항상 수집 | - |
| 비즈니스 핵심 메트릭 (주문, 결제) | 항상 수집 | - |
| 인프라 기본 메트릭 (CPU, 메모리, 네트워크) | 항상 수집 | - |
| DEBUG 레벨 로그 | 개발/스테이징만 | 프로덕션에서는 비용 폭증 위험 |
| 모든 HTTP 요청 본문 | 특수 감사 요건 시만 | 저장 비용 + 개인정보 위험 |
| 1초 미만 해상도 메트릭 | 실시간 트레이딩 등 극소수 | 대부분 60초 해상도면 충분 |
| 헬스체크 성공 로그 | 불필요 | 양만 많고 정보 가치 없음 |

CloudWatch 비용 최적화 팁:

- 로그 그룹별 보존 기간을 명시적으로 설정합니다. 기본값은 "만료 없음"이므로 비용이 계속 누적됩니다.
- 사용자 정의 메트릭은 `put_metric_data` 호출 건수로 과금됩니다. 배치로 묶어 전송하면 비용을 줄일 수 있습니다.
- 로그 필터 메트릭을 사용하면 로그 전체를 저장하지 않고도 특정 패턴의 발생 횟수를 메트릭으로 추출할 수 있습니다.

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
- [ ] 알람 심각도 분류 체계가 정의되어 있는가.
- [ ] 구조화된 로그에 correlation_id가 포함되어 있는가.

## 연습 문제

1. 메트릭과 로그의 차이를 한 줄로 설명해 보세요.
2. "CPU 80%가 5분 지속" 알람의 `Period`와 `EvaluationPeriods`를 적어 보세요.
3. 알람 피로를 줄이는 전략 하나를 제안해 보세요.
4. 99.9% 가용성 SLO의 월간 허용 다운타임을 계산해 보세요.
5. 아래 비구조화 로그를 JSON 구조화 로그로 변환해 보세요: `ERROR: user 123 payment failed after 5000ms`

## 처음 질문으로 돌아가기

- **메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?**
  - 메트릭은 "지금 상태가 이상한가"에, 로그는 "정확히 무엇이 일어났는가"에, 트레이스는 "어디서 느려졌는가"에 답합니다. 세 가지를 조합해야 감지와 원인 분석을 모두 커버할 수 있습니다.
- **CloudWatch는 어떤 기본 기능을 제공할까요?**
  - 메트릭 수집과 시계열 저장, 로그 그룹과 Insights 쿼리, 알람과 SNS 연동, 대시보드 시각화를 제공합니다. 사용자 정의 메트릭으로 비즈니스 지표까지 확장할 수 있습니다.
- **알람과 SNS 알림은 어떻게 연결될까요?**
  - 알람의 `AlarmActions`에 SNS Topic ARN을 지정하면, 임계값 위반 시 Topic에 메시지가 발행되고, 구독된 이메일/Lambda/Slack 등으로 알림이 전달됩니다.

## 정리 및 다음 단계

관측 체계를 갖췄다면 이제는 그 시스템을 얼마에 운영하는지도 함께 통제해야 합니다. 다음 글에서는 FinOps의 출발점인 Cost Management로 넘어가겠습니다.

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
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, Monitoring, CloudWatch, AWS, Observability
