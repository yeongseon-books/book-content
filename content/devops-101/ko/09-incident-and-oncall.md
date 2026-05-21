---
series: devops-101
episode: 9
title: "DevOps 101 (9/10): 장애 대응과 on-call"
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
  - Incident
  - OnCall
  - SRE
  - Postmortem
seo_description: SEV, on-call, 런북, 포스트모템으로 장애 대응 체계를 설계하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (9/10): 장애 대응과 on-call

이 글은 DevOps 101 시리즈의 아홉 번째 글입니다.


![DevOps 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/09/09-01-diagram.ko.png)
*DevOps 101 9장 흐름 개요*
> 장애 대응과 on-call의 핵심은 누가 빠르게 행동하는지가 아니라, 팀이 함께 배우고 같은 실수를 반복하지 않는 것입니다.

## 먼저 던지는 질문

- 새벽 3시에 알림이 울리면 누가 무엇을 해야 할까요?
- 장애 심각도(SEV)는 어떤 기준으로 나눠야 팀이 같은 언어로 움직일까요?
- on-call 로테이션은 왜 일정표가 아니라 운영 설계일까요?

## 왜 중요한가

장애는 항상 발생할 수 있습니다. 중요한 차이는 장애가 오느냐가 아니라, 팀이 얼마나 빠르고 침착하게 복구하느냐입니다. 역할과 절차가 없는 팀은 같은 기술력을 갖고 있어도 장애 순간에 훨씬 더 큰 혼선을 겪습니다.

특히 작은 팀일수록 이 주제가 중요합니다. 사람이 적을수록 한 사람이 진단, 복구, 커뮤니케이션을 동시에 떠안기 쉬워지고, 그럴수록 판단 품질이 급격히 떨어집니다.

> 프로세스는 기억력을 대신합니다.

## 한눈에 보는 개념

좋은 장애 대응은 영웅적인 개인에게 기대지 않습니다. 알림을 받은 사람이 런북을 열고, 완화 조치를 하고, 필요하면 조율 역할이 붙고, 마지막에 포스트모템으로 학습이 남는 흐름이 있어야 합니다.

## 핵심 용어

- **SEV1~SEV4**: 회사 전체 장애부터 경미한 버그까지 나누는 심각도 체계입니다.
- **On-call**: 특정 시간대에 알림을 직접 받는 담당자입니다.
- **Runbook**: 증상, 진단, 조치 순서를 적은 대응 문서입니다.
- **Incident commander (IC)**: 장애 중 역할과 의사결정을 조율하는 사람입니다.
- **Postmortem**: 장애 이후 원인과 재발 방지책을 정리하는 문서입니다.
- **MTTD/MTTR**: 탐지와 복구까지 걸린 평균 시간입니다.

이 용어를 미리 정리해 두면 장애 순간의 대화가 훨씬 짧아집니다. 무엇을 보고, 누가 받고, 누가 결정하는지 언어가 합의되어 있기 때문입니다.

## 전환 전후

**Before**: 알림이 울리면 Slack에서 "이거 누가 보고 있나요?"가 먼저 나오고, 여러 사람이 동시에 손을 대다가 오히려 문제를 더 키우기 쉽습니다.

이 상태에서는 기술적으로 정답을 알고 있는 사람도 팀 전체를 안정시키기 어렵습니다. 기록과 커뮤니케이션, 복구가 뒤섞여 버리기 때문입니다.

**After**: *one on-call* applies a *runbook* to *mitigate*, then an *IC* coordinates and the team holds a *postmortem*.

역할이 분리된 팀은 첫 대응부터 다릅니다. on-call이 초기 조치를 하고, 필요하면 IC가 의사결정과 커뮤니케이션을 정리하며, 복구 후에는 학습까지 남깁니다.

## 장애 대응을 구성하는 5단계

### 1단계 — 심각도(SEV) 정의

장애 대응의 첫 번째 준비물은 기술 지식이 아니라 같은 상황을 같은 기준으로 부를 수 있는 언어입니다. 심각도 정의가 없으면 누구는 큰일이라고 하고 누구는 경미하다고 판단해 대응이 흔들립니다.

```text
SEV1: company-wide outage     | respond immediately
SEV2: core feature degraded   | within 30 min
SEV3: partial degradation     | within business day
SEV4: low-impact bug          | backlog
```

### 2단계 — on-call 로테이션

누가 언제 알림을 받을지 명확하지 않으면 결국 모두가 책임지는 척하지만 실제로는 아무도 선명하게 책임지지 않게 됩니다. primary와 secondary, handoff를 포함한 로테이션이 필요합니다.

```yaml
rotation:
  schedule: weekly
  primary: [alice, bob, carol]
  secondary: [dave, erin]
  handoff: "Mondays 10:00, hand off open incidents"
```

### 3단계 — runbook 템플릿

런북은 기억 의존을 줄이는 핵심 문서입니다. 좋은 런북은 배경 설명보다, 지금 무엇을 열고 어떤 명령을 실행해야 하는지가 먼저 보입니다.

```markdown
# Runbook: API 500 spike

## 증상
- /api/* 5xx ratio above 5%

## 진단
1. Open the Grafana "API Errors" dashboard
2. Check recent logs: {service="api", level="error"}

## 완화 조치
- If a recent deploy is suspect: `kubectl rollout undo deploy/api`

## 에스컬레이션
- If unresolved in 30 min, page IC in #incident channel
```

### 4단계 — incident commander 역할

장애 때 가장 흔한 실수는 가장 잘 아는 사람이 모든 일을 동시에 하게 두는 것입니다. IC는 직접 복구하기보다, 역할을 나누고 판단과 소통을 정리하는 역할이어야 합니다.

```text
IC = decision maker. Does NOT fix things directly.
- Single source of communication
- Assigns roles (investigator/comms/scribe)
- Decides on external announcements
```

### 5단계 — blameless postmortem

복구가 끝났다고 장애 대응이 끝난 것은 아닙니다. 시스템과 절차를 고쳐야 같은 종류의 장애를 반복하지 않습니다.

```markdown
# Postmortem: 2026-05-04 API outage

- Impact: 12 minutes at 30% 5xx
- Timeline: 03:11 alert -> 03:18 rollback -> 03:23 recovery
- Root cause: typo in feature flag default
- Prevention: add flag-validation checklist to PR template
```

## 알림 후 첫 15분 대응 순서

장애 대응은 무엇을 아느냐보다, 처음 15분 동안 무엇부터 하느냐가 더 크게 좌우합니다. 알림 직후에 순서가 없으면 팀은 기술적으로 맞는 조치를 해도 전체 복구 시간은 오히려 늘어납니다.

```text
0-3분   알림 확인, SEV 판정, incident channel 개설
3-5분   on-call이 런북 시작, 최근 배포/변경 여부 확인
5-8분   고객 영향 범위와 우회 가능성 판단
8-12분  IC 지정, 역할 분리, 외부 공지 필요 여부 결정
12-15분 완화 조치 실행 또는 상위 에스컬레이션
```

이 순서가 좋은 이유는 기술 조사와 커뮤니케이션을 동시에 분리하기 때문입니다. 복구를 하는 사람과 상태를 정리하는 사람이 같아지면 정보는 많아도 결정은 느려집니다.

## 좋은 포스트모템이 남기는 산출물

포스트모템의 품질은 문장 톤보다 후속 산출물에서 드러납니다. 좋은 포스트모템은 최소한 세 가지를 남깁니다. 첫째, 재현 가능한 타임라인입니다. 둘째, 다시는 같은 방식으로 놓치지 않게 만드는 감지 또는 예방 조치입니다. 셋째, owner와 due date가 있는 액션 아이템입니다.

예를 들어 `feature flag 기본값 오타`가 원인이었다면, "조심하자"로 끝내는 대신 아래처럼 바뀌어야 합니다.

- PR 템플릿에 flag validation 체크박스 추가
- 배포 전 smoke test에 기본 플래그 상태 검증 포함
- 2주 내 기존 플래그 기본값 일괄 점검

이렇게 남겨야 장애가 문서가 아니라 시스템 변경으로 이어집니다.

## 인시던트 심각도

장애 심각도를 명확히 정의해야 팀이 같은 기준으로 대응할 수 있습니다. 아래 표는 네 단계 심각도와 기대 응답 시간을 정리한 것입니다.

| 심각도 | 기준 | 응답 시간 |
| --- | --- | --- |
| SEV1 | 전체 서비스 중단, 데이터 손실 가능 | 즉시 (5분 이내) |
| SEV2 | 핵심 기능 저하, 일부 사용자 영향 | 30분 이내 |
| SEV3 | 비핵심 기능 문제, 우회 가능 | 영업 시간 내 |
| SEV4 | 경미한 버그, 사용자 영향 없음 | 백로그로 처리 |

이 기준은 팀마다 달라야 합니다. 중요한 것은 숫자가 아니라, 팀이 같은 상황을 같은 이름으로 부를 수 있는가입니다. 심각도가 합의되면 알림 설정, on-call 로테이션, 에스케일레이션 규칙도 함께 명확해집니다.

## 온콜 로테이션 설계

on-call은 단순한 대기가 아니라, 팀의 피로도와 대응 품질을 함께 결정하는 운영 설계입니다. 좋은 로테이션은 피로를 분산시키고 항상 백업 경로를 남깁니다.

### Primary 와 Secondary

Primary가 먼저 알림을 받고, 응답하지 못하면 secondary가 자동으로 호출됩니다. 이 구조는 한 사람에게 만 의존하지 않고, 항상 백업 경로를 유지합니다.

```yaml
rotation:
  schedule: weekly
  primary:
    - alice  # Week 1
    - bob    # Week 2
    - carol  # Week 3
  secondary:
    - dave
    - erin
  escalation_timeout: 15m
```

### Handoff 의식

로테이션 교대 시점에 짧은 handoff 미팅을 하면, 진행 중인 인시던트와 주의 사항을 전달할 수 있습니다.

```text
Every Monday 10:00 AM:
- Previous on-call summarizes the week
- Hands off open incidents
- Next on-call confirms receipt
```

### 피로 관리

on-call 주기를 너무 길게 하면 피로가 쌓이고, 너무 짧게 하면 맥락 전환 비용이 커집니다. 1주일 단위가 가장 흔하지만, 팀 규모에 따라 조정해야 합니다.

## 파이썬 페이저듀티 웹훅 예시

실제 on-call 시스템과 연동하는 webhook 처리 예제입니다. PagerDuty나 Opsgenie 같은 서비스에서 인시던트를 생성할 때 사용합니다.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

PAGERDUTY_URL = "https://events.pagerduty.com/v2/enqueue"
PAGERDUTY_KEY = os.getenv("PAGERDUTY_INTEGRATION_KEY")

class Alert(BaseModel):
    severity: str  # SEV1, SEV2, SEV3, SEV4
    title: str
    description: str
    service: str

@app.post("/alert")
async def create_alert(alert: Alert):
    # Map severity to PagerDuty severity
    pd_severity_map = {
        "SEV1": "critical",
        "SEV2": "error",
        "SEV3": "warning",
        "SEV4": "info"
    }
    
    payload = {
        "routing_key": PAGERDUTY_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": alert.title,
            "severity": pd_severity_map.get(alert.severity, "error"),
            "source": alert.service,
            "custom_details": {
                "description": alert.description,
                "severity": alert.severity
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(PAGERDUTY_URL, json=payload)
        
    if response.status_code != 202:
        raise HTTPException(status_code=500, detail="Failed to create PagerDuty incident")
    
    return {"status": "triggered", "dedup_key": response.json().get("dedup_key")}
```

이 코드는 내부 알림 시스템에서 PagerDuty로 인시던트를 전송합니다. 심각도를 PagerDuty 형식으로 매핑하고, on-call 엔지니어에게 자동으로 통지됩니다.

## 이 코드에서 먼저 봐야 할 점

- 사람이 아니라 시스템과 절차를 고치는 관점이 일관되게 들어 있습니다.
- 런북은 코드 가까이에 있어야 실제 장애 때 찾을 수 있습니다.
- 후속 조치는 반드시 담당자와 기한이 있어야 합니다.

장애 대응 체계의 품질은 문서 양이 아니라, 알림이 울렸을 때 팀이 실제로 따라갈 수 있는가로 판단해야 합니다.

## 자주 하는 실수 5가지

1. **포스트모템에 사람 이름과 잘못을 적는 실수**입니다. 신뢰가 무너지면 학습도 멈춥니다.
2. **런북을 깊은 위키에 묻어 두는 실수**입니다. 새벽 3시에 못 찾으면 없는 문서와 다르지 않습니다.
3. **알림을 너무 많이 두는 실수**입니다. 결국 진짜 중요한 알림을 놓치게 됩니다.
4. **주니어를 혼자 on-call에 세우는 실수**입니다. 항상 백업 경로가 있어야 합니다.
5. **장애 뒤에 액션 아이템을 남기지 않는 실수**입니다. 같은 사고가 다른 이름으로 반복됩니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 모든 알림에 runbook URL을 붙입니다. on-call 엔지니어가 검색부터 시작하지 않도록 하기 위해서입니다. PagerDuty나 Opsgenie가 runbook URL 필드를 제공하는 이유도 여기에 있습니다.

또한 MTTD와 MTTR을 숫자로 남깁니다. 장애 대응은 감정이 강하게 남는 영역이라 체감으로 판단하기 쉬운데, 실제 개선은 측정에서 시작합니다.

## 시니어 엔지니어는 이렇게 봅니다

- 알림 품질이 팀의 수면 품질을 결정합니다.
- 모든 SEV1은 포스트모템까지 이어져야 합니다.
- blameless 원칙은 선택 사항이 아닙니다.
- 액션 아이템은 티켓으로 추적해야 합니다.
- MTTR은 측정하기 전에는 줄어들지 않습니다.

## 체크리스트

- [ ] SEV 정의가 문서화되어 있습니다.
- [ ] on-call 로테이션이 자동화되어 있습니다.
- [ ] 알림에서 런북으로 바로 이동할 수 있습니다.
- [ ] 포스트모템 템플릿이 존재합니다.

## 연습 문제

1. 팀에서 가장 자주 겪는 장애에 대한 런북을 작성해 보세요.
2. SEV 정의를 팀과 합의하고 문서화해 보세요.
3. 최근 장애 하나를 blameless postmortem 형식으로 다시 정리해 보세요.

## 정리 및 다음 단계

장애 대응은 기술과 조직이 만나는 운영 역량입니다. 다음 글에서는 지금까지 살펴본 모든 요소를 하나의 DevOps 흐름으로 연결해 정리합니다.

## 장애 대응 조직 설계를 팀 운영 모델로 정착시키기

on-call은 개인 헌신이 아니라 시스템 설계입니다. 누가 알림을 받는지뿐 아니라, 누가 의사결정하고 누가 기록하며 누가 외부 커뮤니케이션을 담당하는지까지 미리 정의해야 합니다.

### 팀 구조 비교표

| 구조 | 특징 | 장점 | 리스크 |
| --- | --- | --- | --- |
| 중앙 운영팀 단독 | 운영팀이 대부분 장애 처리 | 역할 집중 | 도메인 지식 단절 |
| 서비스 팀 on-call | 개발팀이 서비스 직접 대응 | 복구 속도 향상 | 피로도 관리 필요 |
| 하이브리드 | 서비스 팀 + 플랫폼 지원 | 균형 잡힌 대응 | 역할 경계 모호 가능 |

### SEV 정의 예시

| SEV | 영향 범위 | 목표 응답 시간 |
| --- | --- | --- |
| SEV1 | 전사 핵심 기능 중단 | 즉시 대응 |
| SEV2 | 주요 기능 성능 저하 | 30분 이내 |
| SEV3 | 부분 기능 저하 | 영업시간 내 |
| SEV4 | 경미한 결함 | 백로그 처리 |

### DORA 지표와 incident 연결

| 지표 | incident 관점 해석 |
| --- | --- |
| Deploy Frequency | 작은 변경 단위 유지 여부 |
| Lead Time | 복구성 있는 배포 흐름 여부 |
| Change Failure Rate | 배포 품질 게이트 효과 |
| MTTR | 감지/판단/복구 체계 성숙도 |

### on-call 운영 YAML 예시

```yaml
oncall:
  rotation: weekly
  primary: [alice, bob, carol]
  secondary: [dave, erin]
  escalation:
    - after: 10m
      to: secondary
    - after: 20m
      to: incident-commander
  handoff:
    day: monday
    time: "10:00"
```

### 사고 대응 템플릿

```markdown
# Incident Record
- started_at:
- detected_by:
- sev:
- impacted_scope:
- mitigation:
- status_page_update:
- follow_up_owner:
```

### 운영 규칙

1. 모든 페이지 알림에 runbook 링크를 포함합니다.
2. IC는 복구 실무보다 조율과 의사결정에 집중합니다.
3. 포스트모템 액션은 반드시 이슈 트래커로 추적합니다.
4. 월 단위로 알림 노이즈와 on-call 부하를 점검합니다.

장애 대응 체계의 목표는 완벽한 무장애가 아니라 빠른 복구와 반복 방지입니다. 이 구조가 있을 때 팀은 안정성과 개발 속도를 동시에 유지할 수 있습니다.

### on-call 피로도 관리 지표

장애 대응 체계는 복구 속도뿐 아니라 지속 가능성도 관리해야 합니다. on-call이 소수에게 과도하게 집중되면 대응 품질이 장기적으로 떨어집니다.

| 지표 | 권장 관찰 |
| --- | --- |
| 주간 페이지 수 | 개인별 편차 확인 |
| 야간 호출 비율 | 특정 서비스 노이즈 점검 |
| 30분 내 완화율 | 런북 실효성 확인 |
| 반복 알림 비율 | 알림 조건 튜닝 필요성 판단 |

월간으로 이 지표를 점검하면 "장애는 줄었는데 팀 피로는 증가"하는 역전 현상을 조기에 발견할 수 있습니다.


또한 인수인계 품질을 위해 주간 handoff 노트에 열린 incident, 미완료 액션, 취약 시간대를 반드시 기록해야 합니다. 이 문서가 누락되면 로테이션이 바뀔 때마다 같은 조사 과정이 반복되어 MTTR이 불필요하게 증가합니다.


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

## 처음 질문으로 돌아가기

- **새벽 3시에 알림이 울리면 누가 무엇을 해야 할까요?**
  - 본문의 기준은 장애 대응과 on-call를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **장애 심각도(SEV)는 어떤 기준으로 나눠야 팀이 같은 언어로 움직일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **on-call 로테이션은 왜 일정표가 아니라 운영 설계일까요?**
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
- [DevOps 101 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- **장애 대응과 on-call (현재 글)**
- 운영 가능한 DevOps 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [Google SRE Book — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [PagerDuty Incident Response](https://response.pagerduty.com/)
- [Atlassian Postmortem Template](https://www.atlassian.com/incident-management/postmortem/templates)
- [Blameless Postmortems (Etsy)](https://www.etsy.com/codeascraft/blameless-postmortems/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, Incident, OnCall, SRE, Postmortem
