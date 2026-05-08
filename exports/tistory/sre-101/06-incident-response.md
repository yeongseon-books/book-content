
# Incident Response

> SRE 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *장애* 가 *터졌을 때* *팀* 은 *어떻게* *움직여야* 할까요?

> *인시던트 대응* 은 *역할* 과 *순서* 가 *정해진* *공동 작업* 입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *인시던트* 의 *정의*
- *심각도* 분류
- *역할* 과 *책임*
- *의사소통* 채널
- *종료* 와 *전환*

## 왜 중요한가

*혼란* 은 *영향* 을 *키웁니다*.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Detect["detect"] --> Triage["triage"]
    Triage --> Mitigate["mitigate"]
    Mitigate --> Resolve["resolve"]
    Resolve --> PM["postmortem"]
```

## 핵심 용어 정리

- **incident**: *영향* 이 있는 *비정상*.
- **severity**: *심각도*.
- **IC**: *Incident Commander*.
- **OPS lead**: *운영 책임자*.
- **comms lead**: *소통 책임자*.

## Before/After

**Before**: *발생* 즉시 *모두* 가 *동시* 에 *대응*.

**After**: *역할* 과 *채널* 을 *고정*.

## 실습: 절차 정의

### 1단계 — 심각도 매핑

```python
def severity(impact_users, duration_min):
    if impact_users > 10000 or duration_min > 60:
        return "SEV1"
    if impact_users > 1000:
        return "SEV2"
    return "SEV3"
```

### 2단계 — IC 지정

```python
def assign_ic(on_call):
    return on_call[0]
```

### 3단계 — 채널 생성

```python
def channel(name):
    return f"#inc-{name}"
```

### 4단계 — 상태 업데이트

```python
def update(channel, msg, every_min=15):
    return {"channel": channel, "msg": msg, "every": every_min}
```

### 5단계 — 종료 조건

```python
def can_close(mitigated, customer_impact_zero):
    return mitigated and customer_impact_zero
```

## 이 코드에서 주목할 점

- *심각도* 는 *영향* 으로 정의.
- *IC* 가 *단일* 의사결정자.
- *채널* 분리로 *기록* 보존.

## 자주 하는 실수 5가지

1. ***IC* 없이 *합의* 로 *지연*.**
2. ***영향* 을 *주관* 적으로 평가.**
3. ***고객 공지* 누락.**
4. ***종료* 기준 *모호*.**
5. ***기록* 없이 *복귀*.**

## 실무에서는 이렇게 쓰입니다

*PagerDuty* / *Statuspage* / *Slack* 의 *연동* 으로 *역할* 과 *공지* 가 *자동* 화 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *대응* 은 *훈련* 으로 *빨라짐*.
- *IC* 는 *결정* 만, *손* 은 *전문가*.
- *공지* 는 *신뢰* 의 *축*.
- *종료* 는 *조심스럽게*.
- *훈련* 은 *평소* 에.

## 체크리스트

- [ ] *심각도* 정의.
- [ ] *IC* 로테이션.
- [ ] *공지* 템플릿.
- [ ] *종료* 기준.

## 연습 문제

1. *IC* 의 역할 한 줄로.
2. *severity* 의 의미 한 줄로.
3. *Statuspage* 의 역할 한 줄로.

## 정리 및 다음 단계

다음 글은 *Postmortem* 입니다.

- [SRE란 무엇인가?](./01-what-is-sre.md)
- [Reliability](./02-reliability.md)
- [SLI, SLO, SLA](./03-sli-slo-sla.md)
- [Error Budget](./04-error-budget.md)
- [Monitoring](./05-monitoring.md)
- **Incident Response (현재 글)**
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)
## 참고 자료

- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident Response - PagerDuty](https://response.pagerduty.com/)
- [Incident Command System](https://en.wikipedia.org/wiki/Incident_Command_System)
- [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook)

Tags: SRE, Incident, Response, OnCall, Operations

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
