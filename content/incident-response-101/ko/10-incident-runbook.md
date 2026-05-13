---
series: incident-response-101
episode: 10
title: Incident Runbook 만들기
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Incident
  - Runbook
  - OnCall
  - Capstone
  - Operations
seo_description: incident runbook을 코드형 운영 문서로 묶는 법을 정리합니다
last_reviewed: '2026-05-12'
---

# Incident Runbook 만들기

이 글은 Incident Response 101 시리즈의 마지막 글입니다.

사고 대응 문서가 여기저기 흩어져 있으면 실제 incident 순간에는 거의 도움이 되지 않습니다. severity 표는 위키 한쪽에 있고, 온콜 일정은 다른 도구에 있고, 고객 공지 템플릿은 누군가의 개인 문서에 있고, postmortem 양식은 예전 링크 속에 숨어 있습니다. 낮에는 찾을 수 있어도 새벽 3시에는 시작점조차 헷갈립니다.

## 이 글에서 다룰 문제

좋은 runbook은 단순한 문서 모음이 아닙니다. 사건이 터졌을 때 사람이 가장 먼저 펼쳐 보는 운영 인터페이스에 가깝습니다. severity 판단, 호출, 커뮤니케이션, 대응 단계, postmortem 연결까지 한 흐름으로 이어져 있어야 바로 실행할 수 있습니다.

> runbook은 흩어진 운영 지식을 한 저장소로 묶은 코드형 운영 문서이며, 새벽에도 바로 실행할 수 있어야 합니다.

- incident 대응 지식을 왜 한 runbook으로 묶어야 할까요?
- severity 표와 온콜 일정은 runbook 안에서 어떻게 연결될까요?
- 커뮤니케이션 템플릿과 대응 단계는 어떤 식으로 함께 관리해야 할까요?
- runbook을 위키 문서가 아니라 코드처럼 관리하면 무엇이 좋아질까요?
- 실전 투입 전에 모의 훈련은 왜 꼭 필요할까요?

## 왜 이 주제가 중요한가

incident 대응에서 가장 비싼 시간은 초반 몇 분입니다. 이때 문서를 찾느라 헤매면 복구보다 탐색에 더 많은 시간을 씁니다. 누가 총괄 대응자인지, 어떤 채널을 열어야 하는지, 고객 공지는 어디에 있는지, 사후 분석 템플릿은 무엇인지 한 번에 보이지 않으면 대응은 느려집니다.

runbook은 이 탐색 비용을 줄이는 장치입니다. 더 나아가 운영 지식이 개인 메모에 머무르지 않게 만드는 저장소이기도 합니다. 좋은 팀은 runbook을 사람 머릿속에 두지 않고, 저장소 안에 두고, PR로 바꾸고, 모의 훈련으로 검증합니다.

## 한눈에 보는 구조

```mermaid
flowchart LR
    Sev["SEV 맵"] --> OnCall["온콜"]
    OnCall --> Comms["공지 템플릿"]
    Comms --> Steps["대응 단계"]
    Steps --> PM["사후 분석 템플릿"]
    PM --> Repo["런북 저장소"]
```

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

<!-- toc:begin -->
- [Incident란 무엇인가?](./01-what-is-incident.md)
- [Severity 분류](./02-severity.md)
- [초기 대응](./03-initial-response.md)
- [Communication](./04-communication.md)
- [Timeline 작성](./05-timeline.md)
- [Root Cause Analysis](./06-root-cause-analysis.md)
- [Mitigation과 Resolution](./07-mitigation-and-resolution.md)
- [Postmortem](./08-postmortem.md)
- [재발 방지](./09-prevention.md)
- **Incident Runbook 만들기 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Runbook Template - PagerDuty](https://response.pagerduty.com/oncall/runbooks/)
- [Runbooks as Code - Google SRE Workbook](https://sre.google/workbook/managing-load/)
- [On-Call Rotations - Atlassian](https://www.atlassian.com/incident-management/on-call)
- [Chaos Drills and Game Days - Increment](https://increment.com/reliability/game-days/)

Tags: Incident, Runbook, OnCall, Capstone, Operations
