---
series: incident-response-101
episode: 10
title: "Incident Response 101 (10/10): Incident Runbook 만들기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Incident
  - Runbook
  - OnCall
  - Capstone
  - Operations
seo_description: severity, 온콜, 공지 템플릿, 대응 단계, postmortem 링크를 하나의 incident runbook으로 묶는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (10/10): Incident Runbook 만들기

이 글은 Incident Response 101 시리즈의 마지막 글입니다.

사고 대응 문서가 여기저기 흩어져 있으면 실제 incident 순간에는 거의 도움이 되지 않습니다. severity 표는 위키 한쪽에 있고, 온콜 일정은 다른 도구에 있고, 고객 공지 템플릿은 누군가의 개인 문서에 있고, postmortem 양식은 예전 링크 속에 숨어 있습니다.

낮에는 찾을 수 있어도 새벽 3시에는 시작점조차 헷갈립니다. 좋은 runbook은 흩어진 지식을 한 저장소 안에서 바로 실행 가능한 흐름으로 묶어 둔 운영 인터페이스여야 합니다.

이 글은 Incident Response 101 시리즈의 마지막 글입니다. 여기서는 severity, 온콜, 커뮤니케이션, 대응 단계, postmortem 연결을 하나의 runbook으로 통합하는 방법을 정리합니다.


![Incident Response 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/10/10-01-diagram-at-a-glance.ko.png)
*Incident Response 101 10장 흐름 개요*
> Runbook은 경험을 마지막 사건으로 정리하는 것입니다. Git에 관리하고 정기적으로 검토합니다.

## 먼저 던지는 질문

- incident 대응 지식을 왜 한 runbook으로 묶어야 할까요?
- severity 표와 온콜 일정은 runbook 안에서 어떻게 연결될까요?
- 커뮤니케이션 템플릿과 대응 단계는 어떤 식으로 함께 관리해야 할까요?

## 왜 이 주제가 중요한가

incident 대응에서 가장 비싼 시간은 초반 몇 분입니다. 이때 문서를 찾느라 헤매면 복구보다 탐색에 더 많은 시간을 씁니다. 누가 총괄 대응자인지, 어떤 채널을 열어야 하는지, 고객 공지는 어디에 있는지, 사후 분석 템플릿은 무엇인지 한 번에 보이지 않으면 대응은 느려집니다.

runbook은 이 탐색 비용을 줄이는 장치입니다. 더 나아가 운영 지식이 개인 메모에 머무르지 않게 만드는 저장소이기도 합니다. 좋은 팀은 runbook을 사람 머릿속에 두지 않고, 저장소 안에 두고, PR로 바꾸고, 모의 훈련으로 검증합니다.

## 한눈에 보는 구조

이 그림은 runbook이 한 문서가 아니라 연결 구조라는 점을 보여 줍니다. severity에서 시작해 호출, 공지, 대응 순서, 사후 기록까지 한 흐름으로 이어져야 현장에서 바로 쓸 수 있습니다.

## 핵심 용어

- **runbook**: incident 대응 절차를 모아 둔 실행형 문서 모음입니다.
- **on-call**: 현재 호출 책임을 맡는 순번 체계입니다.
- **sev map**: severity 등급과 대응 행동을 연결한 표입니다.
- **template**: 반복해서 쓰는 공지나 기록 양식입니다.
- **drill**: 실제 incident를 가정해 절차를 연습하는 훈련입니다.

이 다섯 요소가 분리돼 있으면 runbook은 형식만 남은 문서가 됩니다. 반대로 하나로 묶이면 사건 시작부터 사후 분석 링크 생성까지 같은 맥락에서 움직일 수 있습니다.

## 전후 비교

이전: 위키, 채팅 핀, 개인 메모, 외부 도구에 정보가 흩어져 있습니다.

이후: Git 저장소 안에서 코드와 문서 형태로 일관되게 관리합니다.

이후 상태의 핵심은 최신성을 검증할 수 있다는 점입니다. PR 리뷰를 걸 수 있고, 변경 이력을 볼 수 있고, 모의 훈련에서 실제로 써 본 뒤 부족한 부분을 바로 수정할 수 있습니다.

## 단계별 실습: runbook 캡스톤 만들기

### 1단계 — severity 매핑 넣기

runbook의 시작점은 severity별 대응 규칙입니다. 누가 호출되는지와 공지 간격이 먼저 보여야 incident 초반 판단이 빨라집니다.

```python
SEV = {
    "SEV1": {"page": True, "comms": 15},
    "SEV2": {"page": True, "comms": 30},
    "SEV3": {"page": False, "comms": 60},
}
```

### 2단계 — 온콜 조회 붙이기

규칙이 있어도 현재 누가 받는지 모르면 실행할 수 없습니다. 온콜 정보는 runbook에서 바로 이어져야 합니다.

```python
def on_call(schedule, now):
    return next(p for p in schedule if p["from"] <= now <= p["to"])
```

### 3단계 — 커뮤니케이션 템플릿 연결하기

incident 중에는 말보다 템플릿이 빠릅니다. 청중별 공지 틀을 runbook 안에 두면 초기 공지를 훨씬 안정적으로 보낼 수 있습니다.

```python
def comms(audience, sev, summary):
    return {"to": audience, "sev": sev, "text": summary}
```

### 4단계 — 대응 단계 정의하기

runbook은 단계 진행표 역할도 해야 합니다. 지금 확인 단계인지, 안정화 단계인지, 조사 단계인지가 보여야 대응 흐름이 흔들리지 않습니다.

```python
STEPS = ("ack", "stabilize", "communicate", "investigate", "resolve")

def next_step(current):
    i = STEPS.index(current)
    return STEPS[i + 1] if i + 1 < len(STEPS) else "done"
```

### 5단계 — postmortem 템플릿 연결하기

incident는 복구에서 끝나지 않습니다. 사후 기록으로 자연스럽게 이어지도록 runbook 안에서 postmortem 경로도 바로 연결해 두는 편이 좋습니다.

```python
def link_postmortem(incident_id):
    return f"runbook/postmortems/{incident_id}.md"
```

### 6단계 — 전체 흐름 묶기

마지막으로 지금까지의 요소를 한 함수로 묶어 보면 runbook이 왜 코드형 문서인지 분명해집니다. 데이터와 절차가 같은 구조 안에 들어가기 때문입니다.

```python
def run_incident(sev, schedule, now, summary):
    person = on_call(schedule, now)
    msg = comms("internal", sev, summary)
    return {
        "sev": SEV[sev],
        "ic": person["name"],
        "first_msg": msg,
        "step": "ack",
        "postmortem": link_postmortem("INC-001"),
    }
```

## 이 코드에서 먼저 볼 점

- 대응의 각 단계가 데이터 구조로 표현됩니다.
- 상태 전환은 단계 목록으로 단순하게 관리합니다.
- postmortem도 별도 세상이 아니라 runbook 흐름 안에 있습니다.

runbook은 정적인 참고 문서보다 실행 흐름을 더 닮아야 합니다. 읽는 순간 바로 행동으로 옮길 수 있어야 하고, 새 팀원도 같은 출발점에서 시작할 수 있어야 합니다.

## 자주 하는 실수 5가지

1. runbook을 위키에만 두고 실제 저장소와 분리합니다.
2. 모든 severity에 같은 절차를 적용합니다.
3. 온콜 정보가 외부 도구에만 있어 대응 시작점이 끊깁니다.
4. 템플릿이 낡았는데도 모의 훈련 없이 그대로 둡니다.
5. 실제 연습 없이 운영에 바로 투입합니다.

특히 마지막 실수는 치명적입니다. 읽어 본 문서와 실제로 써 본 문서는 다릅니다. 모의 훈련을 돌려 보면 링크가 끊긴 곳, 템플릿이 어색한 곳, 단계가 빠진 곳이 금방 드러납니다.

## 실무에서는 이렇게 봅니다

실무에서는 `runbook/` 디렉터리에 Markdown 문서와 간단한 스크립트를 함께 두고, 변경은 PR 리뷰로 관리하는 경우가 많습니다. 분기마다 모의 훈련이나 game day를 돌려 최신성을 확인하고, incident 뒤에는 사후 분석 결과를 다시 runbook에 반영합니다. 이렇게 해야 문서와 운영이 같이 진화합니다.

시니어 엔지니어는 runbook을 문화의 일부로 봅니다. 연습 없는 runbook은 거의 쓸모가 없고, 모든 severity에 같은 절차를 쓰는 runbook은 오히려 위험하다는 점을 잘 압니다.

## runbook 저장소 예시 구조

runbook을 코드처럼 관리하려면 디렉터리 구조도 단순해야 합니다. 아래 정도만 있어도 실제 incident에서 시작점을 찾기 쉬워집니다.

```text
runbook/
  sev-matrix.md
  oncall.md
  comms/
    internal.md
    external.md
    exec.md
  procedures/
    rollback.md
    scale-out.md
    statuspage.md
  postmortems/
    template.md
```

중요한 점은 모든 정보를 한 파일에 몰아넣는 것이 아니라, 시작 링크가 한곳에서 보이게 만드는 것입니다. 그래야 PR 리뷰와 모의 훈련으로도 유지하기 쉽습니다.

## Jinja2 런북 템플릿 생성 예제

서비스가 많아지면 수동으로 runbook을 관리하기 어려워집니다. 이때 Jinja2 같은 템플릿 엔진을 쓰면 일관된 형식의 runbook을 자동으로 생성할 수 있습니다.

```python
from jinja2 import Template


RUNBOOK_TEMPLATE = """
# 런북: {{ service_name }}

**Last reviewed**: {{ last_reviewed }}
**Owner**: {{ owner }}

## Trigger

{{ trigger }}

## Diagnosis

1. Check error rate:
   ```
   {{ diagnosis_command }}
   ```
2. Expected: {{ expected_state }}

## Action

{% for step in action_steps %}
{{ loop.index }}. {{ step.description }}
   ```
   {{ step.command }}
   ```
   Expected time: {{ step.time }}
{% endfor %}

## Verification

{{ verification }}

## Escalation

{{ escalation }}
"""


def generate_runbook(config):
    template = Template(RUNBOOK_TEMPLATE)
    return template.render(**config)


# 사용 예시
payment_runbook_config = {
    "service_name": "Payment API High Error Rate",
    "last_reviewed": "2026-05-15",
    "owner": "@payment-team",
    "trigger": "Payment API 5xx rate > 5% for 3 minutes",
    "diagnosis_command": "kubectl logs -n prod payment-api --tail=100 | grep ERROR",
    "expected_state": "No timeout errors, circuit breaker not open",
    "action_steps": [
        {
            "description": "Check current deployment version",
            "command": "kubectl get deploy payment-api -n prod -o jsonpath='{.spec.template.spec.containers[0].image}'",
            "time": "30s",
        },
        {
            "description": "Rollback to previous version if needed",
            "command": "kubectl rollout undo deployment/payment-api -n prod",
            "time": "2min",
        },
        {
            "description": "Verify error rate decreased",
            "command": "# Check Grafana dashboard",
            "time": "1min",
        },
    ],
    "verification": "Error rate < 1% maintained for 5 minutes",
    "escalation": "If not resolved in 30 minutes, page @platform-lead",
}

# Runbook 생성
runbook_md = generate_runbook(payment_runbook_config)
print(runbook_md)

# 파일로 저장
with open("runbook/payment-api-high-error.md", "w", encoding="utf-8") as f:
    f.write(runbook_md)
```

이 방식의 장점은 runbook 형식이 일관되고, 서비스가 추가될 때마다 config만 바꿔 빠르게 생성할 수 있다는 점입니다. 템플릿을 수정하면 모든 runbook을 한 번에 업데이트할 수도 있습니다.

실무에서는 이런 자동 생성 스크립트를 CI에 포함시켜, 서비스 메타데이터가 변경될 때마다 runbook도 함께 업데이트되도록 합니다.

## 런북 작성 원칙

좋은 runbook은 글의 양이 아니라 구조의 질로 결정됩니다. 다음 다섯 가지 원칙을 따르면 현장에서 바로 쓸 수 있는 runbook을 만들 수 있습니다.

**1. 실행 가능하게 (명령어 그대로)**

"로그를 확인한다" 대신 "kubectl logs -n production payment-api --tail=100"처럼 복사해 실행할 수 있는 명령어를 적습니다.

**2. 검증 가능하게 (수치 기준)**

"괜찮아 보인다" 대신 "오류율 < 1% 유지 5분"처럼 명확한 기준을 적습니다.

**3. 순서대로 (시간순 단계)**

1번 단계, 2번 단계처럼 순서를 명시하고, 각 단계의 예상 소요 시간도 함께 적습니다.

**4. 결정 분기 표시 (조건분기)**

"만약 A라면 B", "그렇지 않으면 C"처럼 분기가 명확해야 현장에서 헤매지 않습니다.

**5. 업데이트 주기 목록화 (마지막 검토일)**

Runbook 상단에 "Last reviewed: 2026-05-15" 같은 표시를 남겨 폐기한 문서를 방지합니다.

실무에서는 runbook PR에 이 다섯 원칙을 체크리스트로 추가해 리뷰어가 확인하도록 합니다. 모의 훈련에서도 이 원칙을 기준으로 runbook의 완성도를 평가합니다.

## 런북 구성요소

runbook이 현장에서 도움이 되려면 필수 요소들을 모두 포함해야 합니다. 각 요소가 무엇을 담아야 하는지 명확히 하면 모든 incident가 같은 형식으로 시작할 수 있습니다.

| 구성요소 | 역할 | 예시 |
| --- | --- | --- |
| Trigger | 언제 runbook을 열어야 하는가 | "결제 API 5xx 비율 > 5%", "DB 연결 풀 고갈" |
| Diagnosis | 문제를 어떻게 확인하는가 | 로그 패턴, 메트릭 판단 기준, 대시보드 URL |
| Action | 무엇을 실행해야 하는가 | 롤백 명령어, 스케일 아웃 절차, feature flag off |
| Verification | 복구를 어떻게 확인하는가 | "오류율 < 1% 유지 5분", "p99 레이턴시 < 200ms" |
| Escalation | 언제 상위로 보고하는가 | "30분 내 미해결", "SEV1로 상향", "CTO 호출" |

좋은 runbook은 이 다섯 요소가 모두 명확하게 적혀 있습니다. trigger가 애매하면 runbook을 열어야 할지 말아야 할지 판단이 어려워지고, action이 구체적이지 않으면 대응자가 매번 다른 방법을 시도할 수 있습니다.

실무에서는 각 주요 서비스나 장애 유형별로 별도 runbook 페이지를 만들고, 이 다섯 요소를 템플릿으로 고정합니다. 그러면 새 팀원도 바로 runbook을 작성할 수 있고, 모의 훈련에서도 일관된 형식으로 확인할 수 있습니다.

## 체크리스트

- [ ] severity 매핑 표가 runbook 안에 있다.
- [ ] 현재 온콜 일정과 조회 경로가 연결되어 있다.
- [ ] 청중별 커뮤니케이션 템플릿이 포함되어 있다.
- [ ] postmortem 템플릿과 링크 구조가 정리되어 있다.
- [ ] 분기 모의 훈련 또는 game day 일정이 있다.

## 연습 문제

1. runbook을 한 문장으로 정의해 보세요.
2. 모의 훈련이 없는 runbook이 왜 위험한지 설명해 보세요.
3. 여러분 팀 runbook에 가장 먼저 추가해야 할 정보 세 가지를 적어 보세요.

## 정리와 다음 글

runbook은 흩어진 운영 지식을 한곳에 모아 incident 순간 바로 실행할 수 있게 만든 코드형 문서입니다. severity, 온콜, 커뮤니케이션, 대응 단계, postmortem 템플릿이 한 흐름으로 연결돼 있어야 하고, 저장소 안에서 PR과 모의 훈련으로 계속 다듬어야 합니다.

이 시리즈는 여기서 마무리합니다. 다음에는 SRE 101, Information Security 101 같은 시리즈로 범위를 넓혀 신뢰성과 보안을 함께 키워 가면 좋습니다.


## 캡스톤 확장: 사고 대응 성숙도 모델과 훈련 시나리오 설계

runbook을 만든 뒤 진짜 차이는 "문서가 있는가"가 아니라 "문서가 현장에서 작동하는가"에서 생깁니다. 이를 점검하려면 성숙도 모델과 정기 훈련 시나리오가 필요합니다.

### 사고 대응 성숙도 모델

| 단계 | 특징 | 리스크 | 다음 목표 |
| --- | --- | --- | --- |
| Level 1: Ad-hoc | 개인 경험 중심 대응 | 사람 의존/편차 큼 | 기본 runbook 작성 |
| Level 2: Repeatable | 공통 절차 존재 | 업데이트 지연 | 템플릿/체크리스트 표준화 |
| Level 3: Defined | 역할/주기/지표 고정 | 훈련 부족 | game day 정례화 |
| Level 4: Managed | 메트릭 기반 개선 | 복잡도 증가 | 자동화 확장 |
| Level 5: Optimized | 학습 루프 자동 반영 | 과최적화 위험 | 단순성 유지 |

성숙도 모델은 평가표가 아니라 투자 우선순위 도구입니다. 현재 단계와 다음 단계 사이 격차를 명확히 하면 개선 계획이 구체화됩니다.

## 워룸 운영 원칙

- 워룸 채널은 단일 진실 원천으로 유지합니다.
- 의사결정 로그는 Scribe가 구조화해 남깁니다.
- 15~30분 주기 상태 브리핑을 고정합니다.
- 복구 후 워룸 종료 조건을 명시합니다.

워룸이 없거나 느슨하면 대응팀이 여러 채널로 분산되어 동일 사실을 반복 검증하는 낭비가 커집니다.

## 훈련 시나리오 설계 예시

```yaml
drill:
  name: checkout-timeout-surge
  objective:
    - 10분 내 incident 선언
    - 20분 내 첫 mitigation 실행
    - 30분 내 외부 공지 발행
  injects:
    - t+00m: error_rate 7%
    - t+05m: db latency spike
    - t+10m: payment provider partial outage
  success_criteria:
    - role_assignment_completed: true
    - timeline_entries_min: 12
    - first_customer_update_minutes: 30
```

시나리오는 "무엇이 터지는가"뿐 아니라 "성공 기준"을 함께 정의해야 학습이 남습니다.

## 훈련 후 리뷰 질문

1. 선언/역할 배정/공지 시작이 목표 시간 내 이루어졌는가?
2. runbook 링크, 템플릿, 연락 체계에 끊김이 있었는가?
3. 자동화가 부족해 수작업 병목이 발생한 지점은 어디인가?
4. 다음 훈련 전까지 반드시 개선할 항목 세 가지는 무엇인가?

질문을 고정하면 훈련 품질이 회차마다 누적됩니다.

## runbook 운영 자동 점검 예시

```python

def runbook_health(has_sev_map: bool, has_oncall: bool, has_comms: bool, has_drill: bool) -> str:
    score = sum([has_sev_map, has_oncall, has_comms, has_drill])
    if score == 4:
        return "healthy"
    if score >= 2:
        return "needs_improvement"
    return "critical"
```

이 점검은 단순하지만, 분기 리뷰에서 runbook 유지 상태를 빠르게 확인하는 데 유용합니다.

## 운영 결론

incident 대응 역량은 큰 시스템 교체보다 작은 반복 개선에서 올라갑니다. runbook, 메트릭, 훈련 시나리오, postmortem 루프를 연결해 "경험"을 "체계"로 바꾸면, 야간 incident에서도 대응 품질을 안정적으로 유지할 수 있습니다.

## 런북 통합 템플릿(캡스톤)

시리즈 마지막 단계에서는 앞에서 다룬 내용을 하나의 실행 템플릿으로 묶는 것이 중요합니다. 아래 템플릿은 incident 선언부터 종료까지 필요한 링크와 결정을 한 화면에서 보게 만드는 최소 형태입니다.

```markdown
# Incident Runbook: <service-name>

## 1) Severity Matrix Link
- ./sev-matrix.md

## 2) On-call Contacts
- primary:
- secondary:
- escalation:

## 3) First 10 Minutes Checklist
- [ ] page ack
- [ ] incident channel open
- [ ] role assignment (IC/Ops/Comms/Scribe)
- [ ] first mitigation started
- [ ] first customer update sent

## 4) Communication Templates
- ./comms/internal.md
- ./comms/external.md
- ./comms/exec.md

## 5) Resolution Gates
- error_ratio < 1% for 15 minutes
- p95 latency recovered
- no new critical alerts

## 6) Postmortem Link
- ./postmortems/template.md
```

핵심은 정보량이 아니라 연결성입니다. incident 중 필요한 문서가 runbook에서 한 번에 열려야 탐색 시간이 줄어듭니다.

## 게임데이 운영 시나리오 템플릿

| 항목 | 내용 |
| --- | --- |
| 목표 | 선언/완화/공지/기록 루프 검증 |
| 시나리오 | 결제 API 오류율 급증 + 외부 의존성 지연 |
| 성공 기준 | 10분 내 역할 배정, 30분 내 첫 고객 공지, timeline 12줄 이상 |
| 회고 질문 | 어떤 링크가 끊겼는가, 어떤 단계가 느렸는가 |

정기 게임데이를 통해 runbook을 실제 운영 인터페이스로 유지할 수 있습니다. 문서는 작성보다 갱신이 더 중요합니다.

## 운영 부록: 런북 정기 점검 체크리스트

- severity 매트릭스가 최신 incident 기준과 일치하는가?
- 온콜 연락망과 escalation 체인이 현재 조직 구조와 맞는가?
- 커뮤니케이션 템플릿의 링크가 모두 유효한가?
- rollback/scale/throttle 명령이 실제 환경에서 실행 가능한가?
- postmortem 템플릿과 티켓 연결 규칙이 유지되는가?

## 운영 부록: 점검 기록 템플릿

```text
[runbook-review-log]
reviewed_at_utc:
reviewer:
scope:
broken_links:
outdated_steps:
required_updates:
next_review_date:
```

런북은 작성보다 유지가 어렵습니다. 점검 로그를 남기면 "알고 있지만 미뤄진" 변경을 줄일 수 있습니다.

## 런북 운영 추가 점검 항목

아래 항목은 실무에서 바로 점검할 수 있는 추가 체크포인트입니다.

- 체크포인트 1: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.

```text
[quick-audit]
- declaration_latency_minutes:
- first_update_latency_minutes:
- mitigation_started_minutes:
- recovery_verification_metrics:
- postmortem_linked: true/false
```


## 처음 질문으로 돌아가기

- **incident 대응 지식을 왜 한 runbook으로 묶어야 할까요?**
  - 본문에서 강조했듯이 incident 시점에는 사람이 평소처럼 사고할 수 없고, 정보가 채팅·위키·코드·티켓 여러 곳에 흩어져 있으면 첫 30분이 전부 정보 사냥에 소진됩니다. severity 표, 온콜 일정, 커뮤니케이션 템플릿, 단계별 체크리스트를 한 곳에 묶은 runbook이 있어야 인지 부하가 줄고 대응 속도가 결정적으로 빨라집니다.
- **severity 표와 온콜 일정은 runbook 안에서 어떻게 연결될까요?**
  - 본문 예시처럼 severity 표는 "어떤 신호가 보이면 어떤 등급인지"를 정해 누구를 얼마나 빨리 깨울지를 결정하고, 온콜 일정은 "지금 그 등급에서 깨울 사람이 누구인지"를 알려 줍니다. 두 항목이 같은 runbook에 있어야 알람 → 등급 판정 → 호출 대상 결정의 흐름이 한 번도 끊기지 않고 자동으로 이어집니다.
- **커뮤니케이션 템플릿과 대응 단계는 어떤 식으로 함께 관리해야 할까요?**
  - 본문에서 본 것처럼 대응 단계(감지·완화·회복·종료) 각각에 대응되는 사내 공지·status page·고객 공지 템플릿을 같은 runbook에 짝지어 두면, 엔지니어가 mitigation 도중에도 "지금 단계에서 어떤 채널에 무엇을 알려야 하는지"를 매번 새로 고민하지 않아도 됩니다. 단계와 템플릿을 분리해 두면 한쪽은 업데이트되고 다른 쪽은 낡아 결국 사고 중에 어긋난 메시지가 나가는 사고가 반복됩니다.
  - Git에 관리하고, 정기적으로 검토하고 업데이트합니다.
<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity 분류](./02-severity.md)
- [Incident Response 101 (3/10): 초기 대응](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Timeline 작성](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- [Incident Response 101 (7/10): Mitigation과 Resolution](./07-mitigation-and-resolution.md)
- [Incident Response 101 (8/10): Postmortem](./08-postmortem.md)
- [Incident Response 101 (9/10): 재발 방지](./09-prevention.md)
- **Incident Runbook 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Runbooks - PagerDuty](https://response.pagerduty.com/oncall/runbooks/)
- [Managing Load - Google SRE Workbook](https://sre.google/workbook/managing-load/)
- [On-call management - Atlassian](https://www.atlassian.com/incident-management/on-call)
- [Game days - Azure Architecture Center](https://learn.microsoft.com/azure/architecture/framework/resiliency/testing)

### 예제 소스
- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Runbook, OnCall, Capstone, Operations
