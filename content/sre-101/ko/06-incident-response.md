---
episode: 6
language: ko
last_reviewed: '2026-05-14'
seo_description: 장애 대응을 팀 시스템으로 만드는 심각도 분류와 Incident Commander의 역할, 실시간 소통 규칙을 정리합니다.
series: sre-101
status: content-ready
tags:
- SRE
- Incident
- Response
- OnCall
- Operations
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "SRE 101 (6/10): Incident Response"
---

# SRE 101 (6/10): Incident Response

장애가 시작되는 순간 기술 문제만 커지는 것은 아닙니다. 사람도 동시에 흔들립니다. 누가 먼저 판단할지, 누가 복구를 맡을지, 누가 고객과 내부 조직에 상태를 알릴지 정해져 있지 않으면 같은 수준의 장애도 훨씬 크게 번집니다.

강한 팀은 장애가 없을 때 절차를 준비합니다. 장애가 난 다음에 역할을 정하는 조직보다, 미리 역할과 채널과 종료 기준을 정해 둔 조직이 훨씬 빠르게 회복합니다.

이 글은 SRE 101 시리즈의 6번째 글입니다. 여기서는 incident response를 정해진 순서와 역할을 가진 팀 활동으로 설명하고, 심각도 분류, Incident Commander, 커뮤니케이션 규칙, 종료 기준을 함께 정리합니다.

## 먼저 던지는 질문

- 장애 대응은 왜 개인 역량보다 팀 구조에 더 크게 좌우될까요?
- 심각도는 왜 느낌이 아니라 영향 기준으로 정의해야 할까요?
- Incident Commander는 무엇을 직접 하고 무엇을 하지 말아야 할까요?

## 큰 그림

![SRE 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/06/06-01-concept-at-a-glance.ko.png)

*SRE 101 6장 흐름 개요*

Incident Response로 나닜 단계 나눰까지 나눰는 간 갑신 나대다 분대 나나 보까 메 낤낰니다. 근단 연부 첫대로 나눰나 첫대 결닝 나나 낤낰 드돐 물어그 처리 낤내 메 보 메나 낤낰 듀 난당니다.

> 늄 동진 동려 먼8 메 벼 반북 동진동요리꨼ 는 남대다 메 분 나나 볰그 남 메 메 분 메 보 메나 낤낰니다.

## 왜 이 주제가 중요한가

혼란은 장애 영향을 키웁니다. 기술적으로는 빨리 복구할 수 있는 문제였는데도, 역할 충돌과 커뮤니케이션 지연 때문에 대응 시간이 늘어나는 경우가 많습니다. 장애 대응 체계는 기술 수준만큼이나 운영 성숙도를 보여 주는 지표입니다.

또한 좋은 대응 절차는 복구 속도만 높이는 것이 아닙니다. 고객 신뢰를 덜 잃게 하고, 기록을 남기며, 다음 포스트모템으로 자연스럽게 이어지게 만듭니다. 장애 대응은 단발성 행동이 아니라 학습 체계의 입구이기도 합니다.

## 한 문장으로 잡는 멘탈 모델

> 장애 대응은 모두가 동시에 뛰어드는 일이 아니라, 역할이 분리된 팀이 정해진 순서로 움직이는 작업입니다.

## 한눈에 보는 구조

탐지, 분류, 완화, 해결, 포스트모템이라는 흐름을 기준으로 보면 장애 대응이 훨씬 읽기 쉬워집니다. 복구만 끝내면 되는 일이 아니라, 기록과 후속 학습까지 이어지는 전 과정으로 봐야 합니다.

## 핵심 용어 먼저 정리

| 용어 | 뜻 | 실무에서 하는 역할 |
| --- | --- | --- |
| incident | 실제 영향을 가진 비정상 상태 | 대응이 필요한 사건을 구분합니다 |
| severity | 장애 영향의 크기 | 대응 강도와 참여 범위를 정합니다 |
| IC | Incident Commander | 우선순위와 의사결정을 조율합니다 |
| ops lead | 복구 작업을 이끄는 역할 | 기술 조치를 정리하고 실행합니다 |
| comms lead | 내부와 외부 공지를 맡는 역할 | 고객과 조직의 신뢰 축을 지킵니다 |

## 장애 대응은 왜 역할 분리가 먼저일까

장애가 나면 가장 잘 아는 사람이 가장 많이 말하게 되기 쉽습니다. 하지만 기술적으로 가장 많은 지식을 가진 사람이 반드시 조율까지 잘하는 것은 아닙니다. 그래서 대응 체계에서는 역할 분리가 중요합니다.

Incident Commander는 직접 모든 문제를 해결하는 사람이 아닙니다. 현재 상황에서 무엇이 가장 중요한지 정하고, 누구에게 어떤 작업을 맡길지 결정하는 사람입니다. 반대로 ops lead와 개별 전문가들은 복구 작업에 집중해야 합니다. 이 구분이 있어야 의사결정과 실행이 서로 방해하지 않습니다.

## 심각도는 왜 숫자와 영향으로 정의해야 할까

심각도를 주관적으로 정하면 조직마다 같은 장애를 다르게 해석합니다. 어떤 사람은 사용자 1,000명 영향도 큰 사고로 보고, 어떤 사람은 1시간 이상 지속되지 않으면 낮게 볼 수 있습니다. 이 차이를 줄이려면 기준을 문서화해야 합니다.

심각도는 보통 영향 사용자 수, 지속 시간, 핵심 기능 마비 여부 같은 축으로 정의합니다. 중요한 점은 누가 봐도 비슷한 판정을 내릴 수 있어야 한다는 것입니다. 그래야 온콜 호출 범위와 공지 수준도 일관되게 맞출 수 있습니다.

## 인시던트 심각도 분류 기준

심각도 분류는 대응 강도와 조직 동원 범위를 정하는 핵심 기준입니다. 다음 표는 일반적인 4단계 심각도 분류 체계를 보여 줍니다.

| 심각도 | 영향 기준 | 대응 시간 | 에스컬레이션 | 예시 |
| --- | --- | --- | --- | --- |
| SEV1 | 전체 서비스 다운 또는 핵심 기능 완전 마비 | 즉시 (5분 이내) | 전체 온콜 + 경영진 | 결제 API 전면 중단, DB 클러스터 다운 |
| SEV2 | 주요 기능 심각한 저하, 다수 사용자 영향 | 15분 이내 | 관련 팀 온콜 | 홈 피드 latency 5초 초과, 로그인 실패율 20% |
| SEV3 | 비핵심 기능 이슈, 일부 사용자 영향 | 1시간 이내 | 담당 팀만 | 프로필 이미지 업로드 느림, 알림 지연 |
| SEV4 | 기능 영향 없음, 내부 모니터링 이슈 | 다음 업무일 | 담당자 확인 | 대시보드 표시 오류, 로그 수집 지연 |

각 심각도마다 대응 시간 기준을 명확히 하면, 장애 발생 시 누구를 호출하고 얼마나 빠르게 움직여야 하는지 즉시 정해집니다. 이 기준이 없으면 매번 판단이 흔들리고, 과대 대응이나 과소 대응이 반복됩니다.

## 인시던트 타임라인 작성법

타임라인은 장애 대응 중 가장 중요한 기록입니다. 누가 언제 무엇을 보고 어떤 조치를 했는지 시간 순서로 적으면, 나중에 포스트모템을 쓸 때 기억에 의존하지 않아도 됩니다.

### 타임라인에 반드시 포함해야 할 항목

| 항목 | 설명 | 예시 |
| --- | --- | --- |
| 시각 | 분 단위 타임스탬프 (HH:MM) | 14:32 |
| 이벤트 | 무엇이 일어났는가 | Redis 클러스터 primary OOM kill |
| 행동 | 누가 무엇을 했는가 | @alice가 failover 명령 실행 |
| 결과 | 조치 후 무엇이 바뀌었는가 | replica 승격, latency 정상화 |
| 링크 | 관련 로그/메트릭/스크린샷 | [Grafana 링크] |

타임라인은 Slack 채널 메시지를 그대로 복사하는 것만으로도 시작할 수 있습니다. 중요한 것은 사건이 일어나는 동안 실시간으로 기록하는 습관입니다. 장애가 끝난 뒤 기억을 되살려 쓰려고 하면 디테일이 사라집니다.

### 타임라인 작성 예시

```
14:12 - Redis 클러스터 primary 노드 OOM kill 발생
14:13 - 홈 피드 latency 경보 (p99 5초 초과)
14:15 - @bob이 IC로 지정됨, #inc-0519-redis 채널 생성
14:18 - @alice가 Redis 메모리 사용률 확인: 99% 도달
14:20 - @bob이 failover 명령 승인
14:22 - replica 승격 완료, 클러스터 정상화
14:25 - DB fallback 경로로 일부 요청 서빙 확인
14:30 - 홈 피드 p99 latency 800ms 이하 복구
14:37 - @bob이 incident 종료 선언
```

이런 타임라인이 있으면 포스트모템에서 "복구가 왜 늦었는가"나 "어떤 조치가 효과가 있었는가" 같은 질문에 사실 기반으로 답할 수 있습니다.

## PagerDuty Webhook 핸들러 예제

장애 알림을 받으면 자동으로 Slack 채널을 만들고, IC를 지정하고, 초기 공지를 보내는 자동화가 있으면 대응 속도가 빨라집니다. 다음은 PagerDuty webhook을 받아 초기 대응을 자동화하는 Python 예제입니다.

```python
from fastapi import FastAPI, Request
import requests
import json
from datetime import datetime

app = FastAPI()

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
SLACK_TOKEN = "xoxb-your-slack-bot-token"
ON_CALL_SCHEDULE = ["alice", "bob", "charlie"]  # 순환 온콜 명단

def create_incident_channel(incident_id: str) -> str:
    """Slack에 인시던트 전용 채널 생성"""
    channel_name = f"inc-{datetime.now().strftime('%m%d')}-{incident_id}"
    
    response = requests.post(
        "https://slack.com/api/conversations.create",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"name": channel_name, "is_private": False}
    )
    
    if response.json().get("ok"):
        return channel_name
    return None

def assign_ic() -> str:
    """현재 온콜 담당자를 IC로 지정"""
    # 현재 시간 기준으로 온콜 순번 계산 (단순화)
    hour = datetime.now().hour
    index = (hour // 8) % len(ON_CALL_SCHEDULE)
    return ON_CALL_SCHEDULE[index]

def post_initial_update(channel: str, incident_id: str, summary: str, severity: str):
    """초기 공지 메시지 전송"""
    message = f"""
:rotating_light: **Incident {incident_id} - {severity}**

**요약:** {summary}
**발생 시각:** {datetime.now().strftime('%H:%M')}
**IC:** @{assign_ic()}
**채널:** #{channel}

**다음 단계:**
1. 현재 영향 범위 확인
2. 임시 우회책 검토
3. 15분 후 상태 업데이트
"""
    
    requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message, "channel": f"#{channel}"}
    )

@app.post("/webhook/pagerduty")
async def pagerduty_webhook(request: Request):
    """
    PagerDuty webhook을 받아 자동 대응 시작
    
    PagerDuty에서 incident.triggered 이벤트가 오면:
    1. Slack 전용 채널 생성
    2. IC 자동 지정
    3. 초기 공지 전송
    """
    payload = await request.json()
    
    # PagerDuty 이벤트 파싱
    for message in payload.get("messages", []):
        event = message.get("event")
        
        if event == "incident.triggered":
            incident = message.get("incident", {})
            incident_id = incident.get("id")
            summary = incident.get("summary")
            urgency = incident.get("urgency", "high")
            
            # 심각도 매핑
            severity = "SEV1" if urgency == "high" else "SEV2"
            
            # 1. 채널 생성
            channel = create_incident_channel(incident_id)
            
            if channel:
                # 2. IC 지정 및 초기 공지
                post_initial_update(channel, incident_id, summary, severity)
                
                return {
                    "status": "success",
                    "channel": channel,
                    "ic": assign_ic(),
                    "severity": severity
                }
    
    return {"status": "ignored"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

이 코드는 PagerDuty에서 장애 알림이 오면 자동으로 Slack 채널을 만들고, 현재 온콜 담당자를 IC로 지정하고, 초기 공지를 보냅니다. 사람이 수동으로 채널을 만들고 역할을 정하는 시간을 절약할 수 있습니다.

## 단계별로 대응 절차 정의하기

### 1단계 — 심각도 기준 만들기

```python
def severity(impact_users, duration_min):
    if impact_users > 10000 or duration_min > 60:
        return "SEV1"
    if impact_users > 1000:
        return "SEV2"
    return "SEV3"
```

심각도는 감정보다 영향 기준으로 정해야 합니다. 사용자 수와 지속 시간이 대표적인 기준입니다. 여기에 핵심 결제 기능 마비 같은 조건이 더해질 수도 있습니다.

### 포스트모템 준비 항목

장애 대응이 끝나면 즉시 포스트모템으로 이어질 수 있게 준비해야 합니다. 채널에 남은 메시지, 타임라인, 조치 기록을 정리하는 것이 출발점입니다.

| 항목 | 어디서 가져오는가 | 포스트모템에서 쓰이는 방식 |
| --- | --- | --- |
| 타임라인 | Slack 채널 메시지 타임스탬프 | 사건 순서 재구성에 사용됩니다 |
| 영향 범위 | 모니터링 대시보드 수치 | 장애 심각도와 비즈니스 영향을 정량화합니다 |
| 조치 기록 | 실행 명령어, 배포 로그 | 복구 절차와 우회책을 문서화합니다 |
| 커뮤니케이션 | 공지 문구, 업데이트 시각 | 고객 소통 품질을 점검합니다 |

장애 중에 기록을 미루면 기억에 의존하게 됩니다. 전용 채널에 남긴 대화는 그 자체로 포스트모템의 초안이 됩니다.

### 2단계 — IC 지정

```python
def assign_ic(on_call):
    return on_call[0]
```

IC는 대응 중 단일한 조율 축을 만드는 역할입니다. 모두의 의견을 듣되, 다음 결정을 미루지 않는 사람이 필요합니다. 합의만 기다리면 장애는 길어집니다.

### 3단계 — 채널 생성

```python
def channel(name):
    return f"#inc-{name}"
```

전용 채널은 기록을 남기고, 대응 대화를 한곳에 모읍니다. 나중에 타임라인을 재구성할 때도 큰 도움이 됩니다. 장애 대응이 구두로만 흩어지면 복구는 끝나도 학습은 남기기 어렵습니다.

### 4단계 — 상태 업데이트 규칙

```python
def update(channel, msg, every_min=15):
    return {"channel": channel, "msg": msg, "every": every_min}
```

장애 중에는 원인을 아직 몰라도 정기 업데이트가 필요합니다. 현재 영향, 우회책, 다음 공지 시각만 반복해서 알려도 신뢰를 지키는 데 도움이 됩니다. 침묵은 상황을 더 나쁘게 만듭니다.

### 5단계 — 종료 조건 확인

```python
def can_close(mitigated, customer_impact_zero):
    return mitigated and customer_impact_zero
```

복구가 끝났다는 말과 장애를 닫아도 된다는 말은 다를 수 있습니다. 임시 우회만 된 상태인지, 실제 고객 영향이 사라졌는지, 후속 인수인계가 필요한지까지 확인해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- 심각도는 영향 기준으로 정의됩니다.
- IC는 단일한 의사결정 축을 만듭니다.
- 전용 채널은 기록과 협업을 동시에 지원합니다.
- 종료 기준이 있어야 장애가 애매하게 열린 채로 남지 않습니다.

## 여기서 자주 헷갈립니다

첫 번째 실수는 IC가 직접 모든 기술 문제를 해결해야 한다고 생각하는 것입니다. IC의 역할은 조율과 우선순위 결정입니다. 전문가들이 복구 작업에 집중할 수 있게 만드는 사람이기도 합니다.

두 번째 실수는 고객 공지를 기술 복구 뒤로 미루는 것입니다. 원인을 아직 몰라도 현재 영향과 다음 업데이트 시각을 알리는 편이 훨씬 낫습니다.

세 번째 실수는 종료 선언을 너무 빨리 하는 것입니다. 대시보드 수치가 잠깐 안정됐다고 끝난 것이 아닙니다. 사용자 영향이 실제로 사라졌는지까지 봐야 합니다.

## 심각도 분류 표 예시

심각도 분류는 팀마다 다를 수 있지만, 기본 틀은 다음과 같습니다.

| 심각도 | 영향 범위 | 대응 수준 | 예시 |
| --- | --- | --- | --- |
| SEV1 | 전체 서비스 다운 또는 핵심 기능 마비 | 즉시 전체 on-call 호출, 15분마다 업데이트 | 결제 API 전면 중단 |
| SEV2 | 주요 기능 저하 또는 일부 사용자 영향 | 1시간 내 대응, 30분마다 업데이트 | 홀 피드 latency 증가 |
| SEV3 | 비핵심 기능 이슈, 소수 사용자 영향 | 다음 업무 시간 대응, 필요시 업데이트 | 대시보드 표시 오류 |

이 표를 문서화해 두면 장애가 발생했을 때 누구나 비슷한 판단을 내릴 수 있습니다.

## IC 역할의 세부 책임

Incident Commander는 장애 대응의 중심이지만, 모든 기술 문제를 직접 해결하는 사람은 아닙니다. IC의 주요 책임은 다음과 같습니다.

**해야 할 일:**

- 현재 상황 파악 및 우선순위 결정
- 역할 분배 (ops lead, comms lead, 전문가)
- 타임라인 기록 및 체크포인트 확인
- 확대 결정 (더 많은 사람 호출, 고위층 에스케일레이션)
- 종료 조건 확인 및 선언

**하지 말아야 할 일:**

- 직접 코드 디버깅
- 서버 접속하여 명령 실행
- 로그 파일 수동 분석
- 여러 작업을 동시에 직접 수행

IC는 조율자이지 실행자가 아닙니다. 기술적 결정은 ops lead와 전문가가 내리고, IC는 그 결정이 대응 전체 흐름에서 어떻게 맞물리는지 판단합니다.
## 운영 체크리스트

- [ ] 심각도 기준이 숫자와 영향으로 정의되어 있다.
- [ ] IC, 복구 담당, 커뮤니케이션 담당 역할을 구분했다.
- [ ] 전용 채널과 정기 업데이트 규칙이 있다.
- [ ] 종료 조건과 인수인계 기준이 문서화되어 있다.
- [ ] 장애 기록이 포스트모템으로 이어질 준비가 되어 있다.

## 포스트모템 예시 — DB 커넥션 풀 고갈

```python
postmortem = {
    "title": "2026-05-21 DB 커넥션 풀 고갈로 인한 API 지연",
    "summary": "18:45~19:20 사이 API latency가 3초 → 15초로 증가, 전체 사용자 영향",
    "impact": {
        "users": 12000,
        "duration_min": 35,
        "severity": "SEV1"
    },
    "timeline": [
        "18:45 - latency 급증 알림 발화",
        "18:47 - IC 지정, #inc-0521-db-pool 채널 생성",
        "18:52 - DB 커넥션 수 max(100) 도달 확인",
        "18:58 - 임시 조치: pool size 100 → 200 증설",
        "19:10 - latency 3초 이하 복구 확인",
        "19:20 - incident 종료"
    ],
    "root_cause": "배치 작업이 커넥션을 반환하지 않고 계속 점유",
    "actions": [
        {"desc": "배치 작업에 커넥션 타임아웃 추가", "owner": "backend-team", "due": "2026-05-25"},
        {"desc": "커넥션 풀 사용률 알림 추가 (80% threshold)", "owner": "sre-team", "due": "2026-05-23"}
    ]
}
```

이 예시는 타임라인, 영향, 원인, 후속 조치를 실제 데이터로 보여 줍니다. 포스트모템 작성은 장애 대응의 마지막 단계가 아니라, 같은 장애를 예방하는 첫 단계입니다.

## 비난 없는 문화가 장애 대응에 미치는 영향

blameless 원칙은 단순히 좋은 팀 문화가 아니라, 장애 대응 품질을 직접 좌우합니다. 개인 비난이 강한 조직에서는 사람들이 중요한 사실을 숨기거나, 자신을 방어하는 방식으로 말하게 됩니다. 그러면 실제 원인이 잘 드러나지 않고, 같은 문제가 반복됩니다.

비난 없는 문화가 있으면:

- 장애 당시 정보가 부족했던 이유를 솔직히 말할 수 있습니다.
- 경고 신호가 있었는데 무시한 배경을 설명할 수 있습니다.
- 절차가 불명확했거나 도구가 부족했던 사실을 드러낼 수 있습니다.
- 판단 실수보다 시스템 설계 빈틈을 먼저 볼 수 있습니다.

이런 정보가 포스트모템에 들어가야 후속 개선 방향도 현실적으로 정해집니다. 비난 문화는 장기적으로 신뢰성을 낮춥니다.

### 비난 없는 질문의 예시

| 비난적 질문 | 비난 없는 질문 |
| --- | --- |
| 왜 백업을 확인하지 않았나요? | 백업 확인 절차가 문서화되어 있었나요? |
| 왜 알림을 놓쳤나요? | 알림이 평소에도 자주 발화했나요? |
| 왜 롤백을 더 빨리 하지 않았나요? | 롤백 버튼이 바로 보이는 위치에 있었나요? |
| 왜 장애를 예측하지 못했나요? | 장애 전에 어떤 신호가 있었는지 찾아볼까요? |

같은 사실을 묻더라도 질문의 방향을 바꾸면 답의 품질이 달라집니다. 시스템과 절차를 개선하는 정보가 더 많이 나옵니다.

## 커뮤니케이션 템플릿

장애 대응 중 커뮤니케이션은 일관된 포맷이 있어야 합니다. 매번 새로 쓰려고 하면 시간이 걸리고, 빠뜨릴 정보가 생깁니다.

**초기 공지 템플릿:**

```
[장애 통지] {서비스명}
- 발생 시각: {HH:MM}
- 영향 범위: {전체 사용자 / 일부 기능}
- 증상: {간단한 설명}
- 현재 조치: {복구 작업 진행 중}
- 다음 업데이트: {15분 후}
```

**진행 중 업데이트 템플릿:**

```
[업데이트] {서비스명}
- 현재 시각: {HH:MM}
- 원인 파악: {진행 중 / 확인됨}
- 복구 상황: {임시 우회 적용 / 근본 해결 진행 중}
- 영향: {여전히 지속 중 / 일부 완화}
- 다음 업데이트: {15분 후}
```

**종료 공지 템플릿:**

```
[복구 완료] {서비스명}
- 복구 시각: {HH:MM}
- 영향 기간: {총 N분}
- 원인: {간단한 요약}
- 후속 조치: {포스트모템 일정}
```

이 템플릿을 미리 준비해 두면 장애 중 커뮤니케이션 부담이 줄어들고, 고객에게 일관된 정보를 전달할 수 있습니다.
## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 장애 대응을 기술 실력만으로 풀리는 문제로 보지 않습니다. 잘 준비된 절차가 없으면 뛰어난 엔지니어도 혼란 속에서 힘을 제대로 쓰기 어렵기 때문입니다.

또한 PagerDuty, Slack, Statuspage 같은 도구는 절차를 강화할 수는 있어도 대신해 주지는 못합니다. 먼저 필요한 것은 역할과 기준입니다. 자동화는 구조가 있을 때 가장 잘 작동합니다.

## 정리

incident response는 정해진 순서와 역할을 갖춘 팀 활동입니다. 심각도를 영향 기준으로 정하고, IC를 중심으로 복구와 커뮤니케이션을 병렬로 움직이며, 종료 기준까지 명확히 할 때 장애 대응은 더 짧고 덜 혼란스러워집니다.

다음 글에서는 postmortem을 다룹니다. 장애가 끝난 뒤 무엇을 남겨야 같은 문제가 반복되지 않는지, 기록과 액션 추적 관점에서 이어서 정리하겠습니다.

## 처음 질문으로 돌아가기

- **장애 대응은 왜 개인 역량보다 팀 구조에 더 크게 좌우될까요?**
  - 역할이 분리되어 있으면 IC는 조율에, ops lead는 복구에, comms lead는 공지에 집중할 수 있습니다. 역할 충돌이 없어야 빠른 대응이 가능합니다.
- **심각도는 왜 느낌이 아니라 영향 기준으로 정의해야 할까요?**
  - 영향 사용자 수, 지속 시간, 핵심 기능 마비 여부를 기준으로 심각도를 정하면 누가 봐도 비슷한 판정을 내릴 수 있고, 대응 강도와 호출 범위도 일관되게 정해집니다.
- **Incident Commander는 무엇을 직접 하고 무엇을 하지 말아야 할까요?**
  - IC는 우선순위 결정, 역할 분배, 타임라인 기록, 에스케일레이션, 종료 선언을 합니다. 코드 디버깅, 서버 접속, 로그 분석 같은 기술 작업은 ops lead와 전문가에게 맡깁니다.
- **심각도는 왜 느낌이 아니라 영향 기준으로 정의해야 할까요?**
  - 일단 동진 동지리가 나몘늾답닝니다. 그낤늹 나몘늾답닝니다. 그린 나몘늾답닝니다. 메 나몘늾답닝니다.
- **Incident Commander는 무엇을 직접 하고 무엇을 하지 말아야 할까요?**
  - Incident Commander는 나눌 메 값서 낕리 나나 보까 메낤 메 분 돑 나나 볰그 낺 먄 동 메 분돍 나나 낤낰니다.

<!-- toc:begin -->
## 시리즈 목차

- [SRE 101 (1/10): SRE란 무엇인가?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- **Incident Response (현재 글)**
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident Response - PagerDuty](https://response.pagerduty.com/)
- [Incident Command System](https://en.wikipedia.org/wiki/Incident_Command_System)
- [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook)
- [SRE 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sre-101/ko)

Tags: SRE, Incident, Response, OnCall, Operations
