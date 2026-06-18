---
title: "바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림"
series: devops-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 배포한 서비스가 정상 동작하는지 어떻게 알 수 있을까요? AI가 만든 앱에 모니터링을 붙이는 방법과 의미 있는 알림 설계 원칙을 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 7번째 글입니다.

AI 코딩 도구로 앱을 만들고 배포했습니다. 그러면 이제 끝일까요? 서비스가 실제로 잘 동작하는지는 어떻게 알 수 있을까요? 응답이 느려지는지, 에러가 늘어나는지, 서버가 메모리를 다 쓰고 있는지 - 이런 문제는 모니터링이 없으면 사용자가 먼저 알게 됩니다.

모니터링은 서비스 상태를 수치로 관찰하는 것입니다. 요청이 얼마나 들어오는지(Rate), 에러가 얼마나 나는지(Errors), 응답이 얼마나 걸리는지(Duration) - 이 세 가지만 보여도 서비스 상태의 80%를 파악할 수 있습니다.

AI에게 "Prometheus 메트릭 추가해줘"라고 요청할 수 있습니다. 하지만 어떤 지표를 왜 봐야 하는지, 알림은 어떻게 설계해야 의미 있는지 모르면 지표 잔뜩에 알림 폭탄만 생깁니다. 새벽 2시에 울리는 알림이 "지금 당장 봐야 하는 것"인지 "아침에 봐도 되는 것"인지 구분이 안 되면 알림은 오히려 피로만 줍니다.

> 모니터링 없이 운영하는 것은 눈을 감고 운전하는 것과 같습니다.

---

## 이 글에서 다룰 문제
- 모니터링의 세 신호인 로그, 메트릭, 트레이스는 어떻게 역할이 다를까요?
- RED 지표(Rate, Errors, Duration)는 왜 서비스 상태 파악의 출발점일까요?
- Prometheus와 Grafana는 어떤 흐름으로 함께 동작할까요?
- AI가 만든 앱에 모니터링을 추가할 때 무엇부터 시작해야 할까요?
- 의미 없는 알림이 왜 의미 있는 알림보다 더 위험할까요?

## 모니터링 세 신호 비교

| 신호 | 역할 | "왜 느리지?" 상황에서 |
|---|---|---|
| 메트릭 | 수치로 상태를 보여줌 (CPU, 에러율, 지연시간) | 에러율이 언제부터 올랐는지 확인 |
| 로그 | 무슨 일이 일어났는지 기록 | 어떤 요청이 에러를 냈는지 확인 |
| 트레이스 | 요청이 시스템을 어떻게 지나갔는지 추적 | 어느 단계에서 지연이 발생했는지 확인 |

바이브코딩으로 만든 앱에 처음 모니터링을 붙인다면 메트릭부터 시작하세요. 특히 RED 지표(Rate, Errors, Duration)만 있어도 큰 문제를 빠르게 발견할 수 있습니다.

## FastAPI에 Prometheus 메트릭 추가하기

```python
from prometheus_client import Counter, Histogram, make_asgi_app
from fastapi import FastAPI, Request
import time

app = FastAPI()

# RED 지표 정의
requests_total = Counter(
    "http_requests_total",
    "총 HTTP 요청 수",
    ["method", "path", "status"]
)
request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP 요청 응답 시간",
    ["method", "path"]
)

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    requests_total.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()
    request_duration.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

# Prometheus가 수집할 엔드포인트
app.mount("/metrics", make_asgi_app())
```

이 코드를 추가하면 `/metrics` 엔드포인트에서 Prometheus가 메트릭을 수집할 수 있습니다. 요청 수, 에러 수, 응답 시간이 자동으로 기록됩니다.

## Before / After

**Before**: "서비스가 느리다는 사용자 신고를 받고 나서야 문제를 알았다. 언제부터 느려졌는지, 어떤 API가 문제인지 찾는 데 1시간이 걸렸다."

**After**: "p95 응답 시간이 200ms를 5분 이상 넘으면 알림이 옵니다. 알림에는 Grafana 대시보드 링크와 런북 링크가 있습니다. 무엇을 확인해야 할지 즉시 알 수 있습니다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 알림을 너무 많이 만드는 실수 | 알림 피로가 쌓이면 중요한 알림도 무시하게 됨 | 새벽에 울려도 즉시 행동해야 하는 것만 알림으로 |
| 평균 응답 시간만 보는 실수 | 평균은 일부 사용자의 느린 경험을 숨김 | p95, p99 지표를 함께 봄 |
| AI가 만든 메트릭 코드에서 카디널리티 폭발 | user_id 같은 고유값을 라벨로 쓰면 메트릭 수백만 개 생성 | 라벨 값은 적은 종류만 (method, status_code 등) |
| 알림에 런북 링크가 없는 실수 | 새벽에 알림 받고 무엇을 해야 할지 검색부터 시작 | 모든 알림에 런북 URL 포함 |
| 모니터링 시스템 자체를 감시 안 하는 실수 | Prometheus가 죽으면 나머지 알림도 모두 사라짐 | 모니터링 시스템 헬스체크 알림 추가 |

## AI에게 모니터링 관련 질문하는 팁

모니터링 코드를 AI에게 요청할 때 이 정보를 포함하면 실용적인 결과를 받습니다:

```
프레임워크: [FastAPI, Django, Express 등]
원하는 지표: [RED 지표 / USE 지표 / 비즈니스 지표]
알림 조건: [에러율 1% 초과, 응답시간 200ms 초과 등]
알림 대상: [Slack, PagerDuty, 이메일]
대시보드 도구: [Grafana]
```

AI가 만든 알림 규칙을 받았다면 반드시 확인할 것: `for` 조건으로 순간 스파이크를 걸러내는지, 런북 URL이 포함되어 있는지, 라벨이 카디널리티를 폭발시키지 않는지.

## 운영 체크리스트

- [ ] 모든 API 엔드포인트의 요청 수, 에러율, 응답 시간을 측정합니다
- [ ] p95 지연시간이 대시보드에 표시됩니다
- [ ] 알림에 런북 링크가 포함됩니다
- [ ] 알림 조건에 `for: 5m` 같은 지속 시간이 설정되어 순간 스파이크를 걸러냅니다
- [ ] 헬스체크 엔드포인트가 있고 모니터링됩니다

## 처음 질문으로 돌아가기

"AI가 만들어준 앱이 잘 동작하는지 어떻게 알 수 있나요?"

모니터링 없이는 알 수 없습니다. 사용자가 먼저 신고하거나, 매출이 떨어지거나, 서버가 다운되고 나서야 문제를 알게 됩니다. RED 지표 세 가지(요청 수, 에러율, 응답 시간)만 있어도 서비스 상태를 실시간으로 파악할 수 있습니다. AI가 코드를 만들어줘도 서비스 품질을 보장하는 것은 모니터링의 역할입니다.

## 정리

모니터링은 서비스 상태를 수치로 보는 눈입니다. RED 지표부터 시작해서 의미 있는 알림만 남기는 것이 핵심입니다. 다음 글에서는 메트릭이 "무엇이 문제인지"를 보여준다면, 로그가 "왜 문제인지"를 설명하는 로그 수집과 분석을 다룹니다.

## 참고 자료
### 공식 문서
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Google SRE — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- **바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림 (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, Monitoring, Prometheus
