---
series: devops-101
episode: 8
title: "DevOps 101 (8/10): 로그 수집과 분석"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - Logging
  - Observability
  - ELK
  - Loki
seo_description: 구조화 로그와 중앙 수집으로 디버깅 속도를 높이는 로깅 전략을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (8/10): 로그 수집과 분석

이 글은 DevOps 101 시리즈의 여덟 번째 글입니다.


![DevOps 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/08/08-01-diagram.ko.png)
*DevOps 101 8장 흐름 개요*
> 로그 수집과 분석의 핵심은 양이 아니라, 문제가 발생했을 때 빠르게 원인을 찾을 수 있도록 구조화하는 것입니다.

## 먼저 던지는 질문

- 구조화 로그와 비구조화 로그는 실무에서 무엇이 다를까요?
- 여러 서버의 로그를 한곳에 모아야 하는 이유는 무엇일까요?
- Loki와 ELK는 어떤 관점에서 비교하면 좋을까요?

## 왜 중요한가

서버 한 대에 SSH로 들어가 grep 하던 시대는 끝났습니다. 분산 시스템에서는 동시에 여러 인스턴스에서 같은 요청이 흐르고, 문제는 그 사이에서 발생합니다. 그래서 로그는 중앙에서 수집되고 검색 가능해야 합니다.

실제 운영에서는 로그를 지금 보는 시간보다 며칠 뒤, 혹은 몇 주 뒤에 다시 보는 시간이 더 많습니다. 검색성과 보존 정책이 중요한 이유도 여기에 있습니다.

> 로그는 지금보다 몇 주 뒤에 더 자주 읽히는 운영 기록입니다.

## 한눈에 보는 개념

애플리케이션은 stdout으로 로그를 내보내고, 수집 에이전트가 이를 중앙 저장소로 보내며, 운영자는 Grafana나 Kibana에서 검색합니다. 이 구조가 갖춰져야 "어디서 어떤 에러가 났는가"를 한 번에 찾을 수 있습니다.

## 핵심 용어

- **Structured log**: 보통 JSON 형태의 key-value 로그입니다.
- **Log level**: DEBUG, INFO, WARN, ERROR, CRITICAL 같은 심각도 구분입니다.
- **Correlation ID**: 하나의 요청을 끝까지 따라가기 위한 고유 ID입니다.
- **Log aggregator**: 여러 인스턴스 로그를 한곳에 모으는 시스템입니다.
- **Retention**: 로그를 얼마나 오래 보관할지 정한 정책입니다.

로깅은 저장보다 설계가 중요합니다. 어떤 필드를 남길지, 어떤 데이터는 마스킹할지, 몇 일 동안 보관할지가 모두 비용과 디버깅 품질을 함께 결정합니다.

## 전환 전후

**Before (print 스타일 로그)**

```python
print("user logged in", user_id)
# ssh server-01 && grep "logged in" /var/log/app.log
```

이 방식은 서버가 하나일 때만 겨우 버팁니다. 서비스가 분산되면 어떤 요청이 어느 서버를 지났는지 금방 놓치게 됩니다.

**After (구조화 + 중앙 수집)**

```python
import structlog
log = structlog.get_logger()
log.info("user.login", user_id=user_id, request_id=req_id)
# In Grafana, search with {service="api"} |= "user.login"
```

구조화 로그와 중앙 수집을 붙이면, 특정 서비스와 특정 요청을 조건으로 빠르게 좁힐 수 있습니다. 이 차이가 곧 디버깅 속도 차이입니다.

## 로깅을 위한 5단계

### 1단계 — JSON 로그로 전환

로그가 기계가 읽기 좋은 구조를 가져야 쿼리와 집계가 쉬워집니다. 사람에게 보이기만 하는 문자열 로그는 운영 규모가 커질수록 금방 한계에 닿습니다.

```python
import structlog
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
)
log = structlog.get_logger()
```

### 2단계 — correlation ID 주입

요청이 프론트엔드, API, 데이터베이스를 거칠 때 같은 ID를 따라갈 수 있어야 원인을 좁히기 쉽습니다. correlation ID는 분산 시스템의 최소 추적 장치입니다.

```python
import uuid
@app.middleware("http")
async def add_request_id(request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=rid)
    return await call_next(request)
```

### 3단계 — stdout으로 출력

컨테이너 시대에는 애플리케이션이 파일을 직접 돌보기보다 stdout으로 내보내고, 수집은 런타임과 인프라에 맡기는 편이 훨씬 단순합니다.

```text
The container-era principle is *stdout, not files*.
The runtime collects them for you.
```

### 4단계 — Promtail로 Loki에 전송

로그를 중앙 저장소로 모으는 단계입니다. 수집 에이전트가 붙어야 여러 컨테이너와 여러 호스트의 로그를 하나의 인터페이스에서 볼 수 있습니다.

```yaml
scrape_configs:
  - job_name: containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
```

### 5단계 — 의미 있는 쿼리 작성

좋은 로그 설계는 좋은 쿼리까지 포함합니다. 어떤 조건으로 원하는 사건을 좁혀 볼지 팀이 알고 있어야 실제 장애 순간에 바로 쓸 수 있습니다.

```text
{service="api", level="error"} | json | line_format "{{.user_id}} {{.msg}}"
```

## 이 코드에서 먼저 봐야 할 점

- request ID 하나만 있어도 프론트엔드부터 API, DB까지 요청 흐름을 한 줄로 좁힐 수 있습니다.
- 애플리케이션은 stdout에 집중하고 수집은 인프라가 맡는 편이 더 단순합니다.
- PII는 처음부터 코드 수준에서 마스킹해야 합니다.

로그는 많이 남기는 것보다 다시 읽을 수 있게 남기는 것이 중요합니다. 구조와 필드, 쿼리 가능성이 그 핵심입니다.

## 로그 레벨 기준

로그 레벨은 심각도와 용도를 결정합니다. 아래 표는 각 레벨을 언제 사용하고, 프로덕션 환경에서 활성화할지 정리한 것입니다.

| 레벨 | 용도 | 프로덕션 활성화 |
| --- | --- | --- |
| DEBUG | 상세한 디버깅 정보, 변수 값 | 기본 OFF (일시적 ON 가능) |
| INFO | 정상적인 흐름, 사용자 행동 | ON |
| WARNING | 문제는 아니지만 주의 필요 | ON |
| ERROR | 기능 실패, 예외 발생 | ON |
| CRITICAL | 시스템 전체 중단 가능한 상황 | 항상 ON |

DEBUG 레벨은 개발 환경에서는 유용하지만, 프로덕션에서 계속 켜 두면 비용과 노이즈가 폭증합니다. INFO 이상만 활성화하고, 필요할 때만 일시적으로 DEBUG를 켜는 구조가 바람직합니다.

## 파이썬 스트럭트로그 예시

구조화 로그를 바로 적용할 수 있는 Python structlog 설정 예제입니다.

```python
import structlog
from structlog.processors import JSONRenderer
from structlog.contextvars import merge_contextvars

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# Usage example
@app.post("/orders")
async def create_order(order: Order, request: Request):
    request_id = request.headers.get("X-Request-ID")
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        user_id=order.user_id
    )
    
    log.info("order.create.start", order_id=order.id, amount=order.amount)
    
    try:
        result = await process_order(order)
        log.info("order.create.success", order_id=order.id)
        return result
    except Exception as e:
        log.error("order.create.failed", order_id=order.id, error=str(e))
        raise
```

이 코드는 모든 로그를 JSON 형식으로 출력하고, request ID와 user ID를 각 로그 항목에 자동으로 포함시킵니다. 나중에 특정 요청이나 사용자의 행동을 추적할 때 매우 유용합니다.

## 로그 파이프라인

로그는 수집부터 검색까지 여러 단계를 거칩니다. 전체 흐름을 이해해야 병목 지점을 찾을 수 있습니다.

### 수집 (Collection)

애플리케이션은 stdout으로 로그를 내보냅니다. 컨테이너 런타임이 이를 수집하고, Promtail 같은 에이전트가 가져갑니다.

```yaml
# Promtail config
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container'
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'stream'
```

### 전송 (Shipping)

수집된 로그는 중앙 저장소로 전송됩니다. 네트워크 지연이나 장애에 대비해 버퍼와 재시도 로직이 필요합니다.

### 저장 (Storage)

Loki나 Elasticsearch가 로그를 저장하고 인덱싱합니다. 보존 기간을 정해야 저장 비용을 관리할 수 있습니다.

```yaml
# Loki retention
limits_config:
  retention_period: 30d
```

### 검색 (Search)

운영자는 Grafana나 Kibana를 통해 로그를 검색합니다. 구조화된 필드가 있어야 빠른 필터링이 가능합니다.

```text
{service="api", level="error", user_id="12345"} | json | line_format "{{.timestamp}} {{.msg}}"
```

이 네 단계가 모두 원활하게 작동해야 장애 시점에 빠른 분석이 가능합니다. 어느 한 단계라도 병목이 생기면 전체 파이프라인이 느려집니다.

## 자주 하는 실수 5가지

1. **프로덕션에서 DEBUG 로그를 계속 켜 두는 실수**입니다. 비용과 노이즈가 함께 폭증합니다.
2. **PII를 그대로 남기는 실수**입니다. 이는 운영 편의 문제가 아니라 컴플라이언스 문제입니다.
3. **보존 정책 없이 계속 쌓는 실수**입니다. 로그 비용이 뒤늦게 크게 터집니다.
4. **correlation ID 없이 운영하는 실수**입니다. 요청 단위 추적이 거의 불가능해집니다.
5. **에러 로그에 스택트레이스를 남기지 않는 실수**입니다. 원인 분석이 반쯤 막힙니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 `trace_id`를 로그, 메트릭, 트레이스의 공통 키로 사용합니다. 하나의 ID로 세 신호를 교차 분석할 수 있어야 장애 원인 파악 속도가 크게 빨라집니다.

작은 팀이라면 먼저 JSON 로그, Request ID, 중앙 수집 세 가지부터 갖추는 것이 좋습니다. 이 세 가지가 로깅 품질을 가장 크게 끌어올립니다.

## 시니어 엔지니어는 이렇게 봅니다

- 로그는 비용입니다. 레벨과 보존 기간을 의식해야 합니다.
- 구조화 로그는 검색의 전제 조건입니다.
- 민감 정보는 나중이 아니라 코드에서 바로 마스킹해야 합니다.
- trace_id가 세 관측 신호를 이어 줍니다.
- INFO 이하 로그는 샘플링도 적극적으로 고려합니다.

## 체크리스트

- [ ] 로그가 JSON 형태로 출력됩니다.
- [ ] 모든 로그에 Request ID가 포함됩니다.
- [ ] PII 마스킹이 적용됩니다.
- [ ] 보존 정책이 정해져 있습니다.

## 연습 문제

1. 현재 애플리케이션을 structlog 기반으로 바꿔 보세요.
2. Request ID 미들웨어를 추가해 보세요.
3. Loki 또는 Elasticsearch로 중앙 수집을 구성해 보세요.

## 정리 및 다음 단계

로그는 시스템을 시간을 거슬러 읽게 해 주는 기록입니다. 다음 글에서는 로그와 메트릭, 절차를 묶어 실제 장애에 대응하는 방법을 다룹니다.

## 로그 분석을 장애 복구 속도로 연결하는 설계

로그는 관측성의 마지막 근거입니다. 메트릭이 "어디가 나쁘다"를 보여 준다면 로그는 "왜 나쁜가"를 설명합니다. 따라서 로그 설계는 출력 형식보다 검색 전략, 필드 표준, 보존 정책이 먼저 합의되어야 합니다.

### 로깅 스택 비교표

| 항목 | ELK | Loki |
| --- | --- | --- |
| 저장 모델 | 전문 텍스트 인덱싱 | 라벨 기반 인덱싱 |
| 장점 | 강력한 검색/집계 | 비용 효율, Grafana 통합 |
| 주의점 | 운영 복잡도와 비용 증가 | 라벨 설계 실패 시 검색 한계 |
| 적합 상황 | 복잡한 로그 분석 요구 | 메트릭+로그 통합 관측 |

### 구조화 로그 필드 표준 예시

| 필드 | 설명 |
| --- | --- |
| timestamp | RFC3339 시각 |
| level | info/warn/error |
| service | 서비스 이름 |
| env | 실행 환경 |
| request_id | 요청 추적 키 |
| trace_id | 분산 추적 연계 키 |
| message | 이벤트 설명 |

### Python 구조화 로깅 예시

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()
log.info("payment.authorized", service="api", env="prod", request_id="req-123")
```

### Trivy 로그 기반 보안 이벤트 연계 예시

```yaml
security_pipeline:
  sast:
    tool: semgrep
  dast:
    tool: zap
  image_scan:
    tool: trivy
    fail_on: [HIGH, CRITICAL]
```

로그 파이프라인과 보안 파이프라인을 연결하면 취약점 탐지 이벤트를 운영 로그와 같은 채널에서 추적할 수 있습니다.

### Loki 수집 설정 예시

```yaml
scrape_configs:
  - job_name: containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        target_label: container
```

### 운영 규칙

1. PII는 애플리케이션 계층에서 마스킹합니다.
2. 로그 레벨 정책을 서비스 공통 규칙으로 둡니다.
3. 장애 빈도가 높은 이벤트에 대해 저장 기간을 길게 유지합니다.
4. 주간으로 "자주 사용하는 쿼리"를 팀 위키에 축적합니다.

결국 로그 품질은 장애 대응 품질과 같습니다. 같은 사건을 더 빠르게 재구성할 수 있을수록 MTTR이 줄어듭니다.


## 운영 앵커: 배포, 인프라, 관측성, 대응을 한 장으로 연결하기

앞선 섹션에서 각 주제를 따로 설명했다면, 이 섹션은 실무에서 한 번에 연결해 쓰는 최소 구성 예시를 제공합니다. 핵심은 화려한 도구 조합이 아니라, 같은 기준으로 변경을 통과시키고 문제를 되돌릴 수 있는가입니다.

### CI/CD 파이프라인 공통 YAML

```yaml
name: delivery-flow
on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q

  deploy-stage:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_stage.sh
      - run: ./scripts/smoke_test.sh https://stage.example.com

  deploy-prod-canary:
    needs: deploy-stage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_prod.sh --strategy canary --percent 10
      - run: ./scripts/check_slo.sh --window 5m
      - run: ./scripts/promote_or_rollback.sh
```

이 흐름의 실전 포인트는 세 가지입니다. 첫째, CI 통과 전에는 어떤 배포도 시작하지 않습니다. 둘째, stage 통과 후에만 production으로 승격합니다. 셋째, production 승격은 canary 관찰 통과를 조건으로 강제합니다.

### Terraform과 Ansible 역할 분리 예시

```hcl
# infra/main.tf
resource "aws_security_group" "api" {
  name        = "api-sg"
  description = "api security group"
}

resource "aws_instance" "api" {
  ami           = var.ami
  instance_type = "t3.small"
  tags = {
    service = "api"
    env     = var.env
  }
}
```

```yaml
# ops/playbooks/hardening.yml
- hosts: api
  become: true
  tasks:
    - name: Install security updates
      apt:
        update_cache: true
        upgrade: dist

    - name: Ensure auditd is installed
      apt:
        name: auditd
        state: present

    - name: Ensure ssh root login is disabled
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin'
        line: 'PermitRootLogin no'
```

Terraform은 "무엇을 만들 것인가"를 선언하고, Ansible은 "만들어진 시스템을 어떤 상태로 유지할 것인가"를 담당합니다. 두 도구를 구분하면 변경 리뷰 범위가 명확해지고, 장애 시 원인 추적도 빨라집니다.

### 모니터링/알림 설정 예시

```yaml
# monitoring/alerts.yml
groups:
  - name: api-slo
    rules:
      - alert: ApiHighErrorRate
        expr: rate(http_requests_total{service="api",status=~"5.."}[5m]) / rate(http_requests_total{service="api"}[5m]) > 0.01
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "API 5xx 비율 1% 초과"
          runbook: "https://internal/wiki/runbooks/api-high-error-rate"

      - alert: ApiHighLatencyP95
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="api"}[5m])) by (le)) > 0.35
        for: 10m
        labels:
          severity: warning
```

알림은 많이 울리는 것이 목표가 아닙니다. 운영자가 실제로 행동할 수 있는 신호만 남기고, 모든 page 알림에 runbook 링크를 붙여 대응 시작 시간을 줄여야 합니다.

### 블루그린/카나리 승격 절차 예시

```bash
# blue-green switch
./scripts/deploy_blue.sh
./scripts/smoke_test.sh https://blue.example.com
./scripts/switch_traffic.sh --from green --to blue

# canary rollout
./scripts/deploy_canary.sh --percent 10
./scripts/check_metrics.sh --window 5m
./scripts/promote_canary.sh --to 50
./scripts/promote_canary.sh --to 100
```

블루그린은 즉시 전환과 즉시 롤백에 유리하고, 카나리는 위험을 작게 나눠 검증하는 데 유리합니다. 서비스 특성과 팀 역량에 따라 전략을 고르되, 승격/철수 명령을 반드시 런북과 자동화 스크립트로 함께 유지해야 합니다.

### 인시던트 대응 런북 예시

```markdown
# Runbook: API 5xx 급증

## 0-5분
1. SEV 판정 (SEV1/SEV2)
2. incident 채널 개설
3. 최근 배포 커밋 확인

## 5-10분
1. canary/최근 릴리스 롤백 시도
2. 에러율, p95, DB 연결수 확인
3. 고객 영향 범위 요약 공지

## 10-20분
1. 임시 완화 조치 적용
2. 영구 수정 owner 지정
3. postmortem 일정 예약
```

운영에서는 "잘 아는 사람"보다 "같은 순서를 따르는 팀"이 더 빠르게 복구합니다. 그래서 runbook은 설명 문서가 아니라 실행 문서여야 하며, 경보에서 한 번에 열 수 있어야 합니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

## 처음 질문으로 돌아가기

- **구조화 로그와 비구조화 로그는 실무에서 무엇이 다를까요?**
  - 본문의 기준은 로그 수집과 분석를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **여러 서버의 로그를 한곳에 모아야 하는 이유는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Loki와 ELK는 어떤 관점에서 비교하면 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [DevOps 101 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [DevOps 101 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- **로그 수집과 분석 (현재 글)**
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [structlog](https://www.structlog.org/)
- [Grafana Loki](https://grafana.com/docs/loki/latest/)
- [Elastic Stack](https://www.elastic.co/elastic-stack)
- [OpenTelemetry Logs](https://opentelemetry.io/docs/specs/otel/logs/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, Logging, Observability, ELK, Loki
