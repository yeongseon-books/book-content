---
series: incident-response-101
episode: 2
title: "Incident Response 101 (2/10): Severity 분류"
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
  - Severity
  - Triage
  - Response
  - Operations
seo_description: SEV1, SEV2, SEV3를 영향 축과 호출 정책, 업데이트 cadence에 연결하는 severity 설계 원칙을 정리합니다.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (2/10): Severity 분류

incident라고 부를 기준이 생겨도 아직 한 단계가 더 남습니다. 같은 incident라도 모두 같은 방식으로 대응하면 안 되기 때문입니다.

전사 장애와 일부 사용자 불편은 호출 범위도, 보고 주기도, 의사결정 속도도 달라야 합니다. 그래서 팀은 severity라는 공통 언어로 영향의 크기를 행동 규칙에 연결합니다.

이 글은 Incident Response 101 시리즈의 2번째 글입니다. 여기서는 SEV1·SEV2·SEV3를 나누는 영향 축, 등급과 호출 정책을 연결하는 방법, 그리고 경계 사례를 문서화하는 실무 원칙을 다룹니다.

## 먼저 던지는 질문

- severity는 무엇을 위한 언어일까요?
- SEV1, SEV2, SEV3는 어떤 기준으로 갈라야 할까요?
- 사용자 수, 범위, 금전 손실 같은 영향 축은 왜 필요할까요?

## 큰 그림

![Incident Response 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/02/02-01-diagram-at-a-glance.ko.png)

*Incident Response 101 2장 흐름 개요*

Severity 등급은 SEV1, SEV2, SEV3로 나누면 호출 대상과 업데이트 비도가 함께 결정되는 중요한 의사결정 축입니다.

> Severity는 단순 라벨이 아니라, 행동 규칙과 함께 이해되는 운영 언어입니다. 같은 단어를 다르게 쓰면 대응은 엇나갑니다.

## 왜 이 주제가 중요한가

severity 체계가 없으면 incident 대응은 매번 즉석 토론으로 시작합니다. 어떤 사건은 실제로는 작지 않은데도 낮게 평가되고, 어떤 사건은 내부 긴장감 때문에 과하게 올라갑니다. 같은 단어를 다른 의미로 쓰면 대응은 엇나갈 수밖에 없습니다.

잘 만든 severity 체계는 설명을 줄이고 행동을 맞춥니다. SEV2라는 말이 나오면 누가 호출되고, 몇 분마다 상황을 공유하며, 어느 정도까지 escalation하는지가 함께 떠올라야 합니다. 이때 severity는 단순한 라벨이 아니라 행동의 축약어가 됩니다.

## 한눈에 보는 구조

여기서 핵심은 매핑입니다. 영향이 먼저 있고, severity는 그 영향을 운영 언어로 번역한 결과입니다. 그리고 각 등급은 누가 움직이고 얼마나 자주 공유할지를 결정합니다.

## 핵심 용어

- **SEV1**: 전사 차원의 영향이 있는 수준입니다.
- **SEV2**: 주요 기능이 크게 흔들리는 수준입니다.
- **SEV3**: 부분적인 영향이 있는 수준입니다.
- **scope**: 영향 범위입니다.
- **duration**: 영향 지속 시간입니다.

이 용어를 정할 때는 추상 표현보다 예시가 더 중요합니다. “심각하다” 같은 말만 두면 해석이 갈립니다. 결제 실패는 SEV1, 검색 정렬 오류는 SEV3처럼 사례를 함께 두면 경계가 훨씬 선명해집니다.

## 전후 비교

이전: “꽤 심각하다” 같은 모호한 표현으로 상황을 설명합니다.

이후: “SEV2입니다”처럼 합의된 등급과 그에 따른 행동을 함께 공유합니다.

이 차이는 단순한 말투 차이가 아닙니다. 이전 상태에서는 호출 범위와 우선순위가 사람마다 달라집니다. 이후 상태에서는 등급 한 단어만 들어도 다음 행동이 자연스럽게 이어집니다.

## 단계별 실습: severity 매핑 만들기

### 1단계 — 영향 축 정의하기

영향을 한 숫자로만 보면 놓치는 부분이 많습니다. 사용자 수, 지역 범위, 금전 손실처럼 사건을 여러 축으로 나눠 봐야 경계가 분명해집니다.

```python
def axes(users, region, money_loss):
    return {"users": users, "region": region, "money": money_loss}
```

### 2단계 — 등급으로 변환하기

축을 정했으면 이제 기준선을 둡니다. 여기서는 단순하게 사용자 수와 금전 손실로 SEV1을 판정하고, 그보다 작은 사건을 SEV2와 SEV3로 나눕니다.

```python
def severity(a):
    if a["users"] > 100000 or a["money"] > 100000:
        return "SEV1"
    if a["users"] > 1000:
        return "SEV2"
    return "SEV3"
```

### 3단계 — 호출 정책 연결하기

severity는 이름표로 끝나면 안 됩니다. 각 등급이 누구를 언제 깨울지로 이어져야 실제 운영 체계가 됩니다.

```python
def page_policy(sev):
    return {"SEV1": "all", "SEV2": "primary", "SEV3": "next-day"}[sev]
```

### 4단계 — 보고 주기 정하기

상황 공유 간격도 severity와 함께 바뀌어야 합니다. 높은 severity는 더 자주, 낮은 severity는 더 길게 가져가는 식입니다.

```python
def report_every_min(sev):
    return {"SEV1": 15, "SEV2": 30, "SEV3": 60}[sev]
```

### 5단계 — 자동 분기 완성하기

마지막으로 severity, 호출 정책, 보고 주기를 한 번에 묶으면 운영 판단을 자동화할 수 있습니다.

```python
def route(a):
    sev = severity(a)
    return {"sev": sev, "page": page_policy(sev), "every": report_every_min(sev)}
```

## 이 코드에서 먼저 볼 점

- 영향은 축으로 나눠야 경계가 선명해집니다.
- 등급은 반드시 행동과 연결돼야 의미가 있습니다.
- 자동 분기는 사람마다 다른 판단을 줄여 줍니다.

여기서 중요한 사실은 severity가 기술 규칙이면서 동시에 조직 규칙이라는 점입니다. 숫자는 코드에 있지만, 그 숫자를 정하는 기준은 서비스 특성과 비즈니스 맥락에서 나옵니다. 결제 서비스의 SEV1과 내부 도구의 SEV1이 같을 필요는 없습니다.

## 자주 하는 실수 5가지

1. 등급 정의를 너무 추상적으로 써서 누구나 다르게 해석합니다.
2. 금전 손실이나 법적 영향을 빼먹고 사용자 수만 봅니다.
3. SEV2와 SEV3 경계를 예시 없이 남겨 둡니다.
4. 판정을 매번 수동으로 하면서 자동화 규칙을 만들지 않습니다.
5. 고객 영향보다 내부 불편을 더 크게 보고 등급을 올립니다.

실무에서 가장 자주 부딪히는 문제는 경계 사례입니다. 그래서 경계선에 걸리는 대표 사례를 문서에 함께 두는 편이 좋습니다. 추상 정의보다 사례가 훨씬 오래 남습니다.

## 실무에서는 이렇게 봅니다

실서비스에서는 결제 실패가 기본적으로 SEV1로 올라가고, 검색 결과 정렬 오류는 기본적으로 SEV3로 내려가는 식의 기본 규칙을 둡니다. 중요한 점은 사건이 발생한 뒤 감으로 토론하는 것이 아니라, 발생하기 전에 이미 표와 예시를 만들어 둔다는 점입니다.

시니어 엔지니어는 severity를 “중요도 설명”이 아니라 “행동의 축약어”로 봅니다. SEV2라고 말하는 순간 누가 호출되고, 몇 분마다 업데이트가 나가며, 어떤 채널이 열리는지가 함께 떠올라야 합니다.

## severity 표를 실제 행동으로 연결하는 예시

등급 정의가 문서로만 남아 있으면 실전에서 오래 걸립니다. 아래처럼 등급, 호출 범위, 업데이트 cadence를 한 표에 묶어 두면 incident 방에서 논의해야 할 항목이 크게 줄어듭니다.

| Severity | 대표 영향 | 호출 범위 | 내부 업데이트 | 고객 공지 |
| --- | --- | --- | --- | --- |
| SEV1 | 핵심 기능 광범위 중단 | 전체 incident 코어 팀 + 리더 | 15분 | 즉시 |
| SEV2 | 주요 기능 심각한 저하 | primary on-call + 담당 팀 | 30분 | 필요 시 즉시 |
| SEV3 | 제한적 영향 | primary on-call 중심 | 60분 | 보통 생략 |

이 표는 정답이 아니라 출발점입니다. 중요한 점은 “SEV2입니다”라는 한마디가 곧 호출 범위와 보고 주기를 함께 떠올리게 해야 한다는 사실입니다.

## 체크리스트

- [ ] SEV1/2/3 정의가 문서로 정리되어 있다.
- [ ] 사용자 수, 범위, 금전 손실 같은 영향 축이 합의되어 있다.
- [ ] 등급별 호출 정책과 보고 주기가 정리되어 있다.
- [ ] 경계 사례 예시가 문서에 포함되어 있다.

## 연습 문제

1. 여러분 팀에서 SEV1을 한 문장으로 정의해 보세요.
2. scope와 duration을 각각 어떤 수치로 표현할지 적어 보세요.
3. 내부 도구와 고객 서비스의 severity 기준이 왜 달라질 수 있는지 설명해 보세요.

## 정리와 다음 글

severity는 단순한 라벨이 아니라 영향과 행동을 연결하는 공통 언어입니다. 같은 단어를 같은 뜻으로 써야 온콜, 보고, 우선순위가 함께 맞춰집니다. 좋은 severity 체계는 영향 축이 분명하고, 경계 사례가 있으며, 각 등급이 실제 행동으로 이어집니다.

다음 글에서는 incident가 발생했을 때 처음 몇 분 안에 무엇을 해야 하는지, 즉 초기 대응을 다루겠습니다.


## 심각도 체계 확장: SEV 등급표를 행동 규칙으로 고정하기

severity 정의가 있어도 실제 현장에서 흔들리는 이유는 "라벨"만 있고 "행동"이 빠져 있기 때문입니다. SEV2라고 말했을 때 누가 들어오고, 얼마나 자주 공유하고, 어떤 승인 경로로 조치하는지 즉시 떠올라야 합니다. 이를 위해 등급표는 영향 설명과 운영 규칙을 한 표로 묶어야 합니다.

| 등급 | 서비스 상태 | 고객 영향 | 호출 정책 | 내부 업데이트 | 외부 공지 |
| --- | --- | --- | --- | --- | --- |
| SEV1 | 핵심 기능 중단 | 광범위/매출 직접 영향 | IC 포함 코어팀 즉시 호출 | 15분 | 즉시 개시 |
| SEV2 | 핵심 기능 심각 저하 | 다수 고객 실패/지연 | primary + 담당팀 | 30분 | 필요 시 즉시 |
| SEV3 | 부분 기능 이상 | 제한적 고객 영향 | primary 중심 | 60분 | 보통 생략 |

표를 만들 때 핵심은 "이벤트"가 아니라 "고객 여정" 중심으로 정의하는 것입니다. 예를 들어 API 오류율이 동일해도 결제 단계 실패와 추천 위젯 실패는 사업 영향이 전혀 다릅니다. 그래서 등급 기준에는 반드시 핵심 여정 태그를 포함해야 합니다.

## 경계 사례 처리 규칙

실무에서 가장 많이 시간을 쓰는 구간은 SEV1/SEV2 경계입니다. 아래 규칙을 두면 논쟁 시간을 줄일 수 있습니다.

1. 결제/로그인/인증 실패는 고객 수가 작아도 상향 검토합니다.
2. 장애 파급 범위가 늘어나는 추세면 1단계 상향합니다.
3. 외부 규제/법적 위험이 있으면 보수적으로 상향합니다.
4. 데이터 무결성 의심이 있으면 즉시 고심각 체계로 전환합니다.

이 규칙은 "정답"이 아니라 "일관성"을 위한 장치입니다. 같은 상황에서 매번 다른 결론이 나오는 비용이 가장 큽니다.

## severity 기반 보고 주기 설계

보고 주기는 팀 집중력과 고객 신뢰를 동시에 다룹니다. 지나치게 잦으면 대응자가 소모되고, 너무 드물면 신뢰가 떨어집니다. 아래는 실무에서 자주 쓰는 기본안입니다.

```yaml
severity_cadence:
  SEV1:
    internal_minutes: 15
    exec_minutes: 30
    external_minutes: 30
  SEV2:
    internal_minutes: 30
    exec_minutes: 60
    external_minutes: 60
  SEV3:
    internal_minutes: 60
    exec_minutes: 180
    external_minutes: null
```

여기서 중요한 점은 "외부 공지 없음"도 정책으로 명시해야 한다는 점입니다. 명시되지 않으면 incident마다 임의 해석이 생깁니다.

## 자동 라우팅 예시

```python
def route_by_severity(sev: str) -> dict:
    policies = {
        "SEV1": {"page": "all", "war_room": True, "cadence": 15},
        "SEV2": {"page": "primary", "war_room": True, "cadence": 30},
        "SEV3": {"page": "primary", "war_room": False, "cadence": 60},
    }
    return policies[sev]
```

자동 라우팅은 대응 속도를 높이지만, 기준이 부정확하면 잘못된 자신감을 만듭니다. 그래서 분기마다 실제 incident 사례를 기준으로 임계값을 재검토해야 합니다.

## 운영 점검 항목

- SEV 판정 근거가 timeline에 남는가?
- 상향/하향 조정 시점이 기록되는가?
- 등급별 호출/공지 템플릿이 준비돼 있는가?
- 분기 리뷰에서 오분류 사례를 다시 학습하는가?

severity 체계의 품질은 문서 길이가 아니라 "분류 이후 행동 일관성"으로 평가해야 합니다.

## severity 운영 리뷰 방법

분기 리뷰에서는 SEV 상향/하향 사례를 따로 모아 "왜 그 판단을 했는지"를 재검토하는 절차가 필요합니다. 상향이 잦다면 임계값이 보수적으로 설정됐을 수 있고, 하향이 잦다면 초기 판단 정보가 부족했을 가능성이 큽니다. 또한 야간과 주간, 평일과 이벤트 기간의 분류 패턴을 나눠 보면 맥락별 편차를 줄일 수 있습니다.

리뷰 결과는 다음 분기 실험 항목으로 연결해야 의미가 있습니다. 예를 들어 SEV2 경계 사례가 반복된다면 탐지 지표를 추가하거나 공통 확인 질문을 늘려 분류 입력 품질을 높일 수 있습니다. severity 체계는 정답표가 아니라 학습 루프입니다.

## 운영 보강 메모

현장에서는 문서 규칙만으로 품질이 자동으로 올라가지 않습니다. 그래서 각 팀은 월 1회 이상 실제 incident 사례를 골라 기준 적용 여부를 점검해야 합니다. 점검 항목은 단순할수록 좋습니다. 선언 근거가 수치로 남았는지, 역할 분리가 지켜졌는지, 커뮤니케이션 주기가 유지됐는지, 후속 조치가 티켓으로 연결됐는지 네 가지를 반복 확인하면 됩니다.

이 보강 메모를 남기는 목적은 분량을 늘리는 데 있지 않습니다. 기준을 사건 데이터와 연결해 "다음 대응의 입력"으로 쓰는 데 있습니다. 문서가 저장소 안에서 살아 있으려면 변경 이력, 검증 절차, 교육 루프가 함께 있어야 합니다. 결국 incident 대응 역량은 한 번의 완벽한 대응이 아니라, 같은 실수를 덜 반복하는 조직 습관에서 만들어집니다.

## 처음 질문으로 돌아가기

- **severity는 무엇을 위한 언어일까요?**
  - SEV1은 전사 차원 중단, SEV2는 주요 기능 불가, SEV3는 부분적 영향으로 나뉘며, 각 등급이 호출과 보고 규칙을 결정합니다.
- **SEV1, SEV2, SEV3는 어떤 기준으로 갈라야 할까요?**
  - 영향받은 사용자 수, 영향 범위(전체/일부), 추정 복구 시간으로 동적 분류하고, 경계 사례마다 선배와 의논해 임계값을 다듭니다.
- **사용자 수, 범위, 금전 손실 같은 영향 축은 왜 필요할까요?**
  - 이 수치들이 필요한 이유는 '심각하다'는 주관적 표현 대신 '15분 이상 5000명 영향'처럼 객관적 판단 기준을 제공하기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- **Severity 분류 (현재 글)**
- 초기 대응 (예정)
- Communication (예정)
- Timeline 작성 (예정)
- Root Cause Analysis (예정)
- Mitigation과 Resolution (예정)
- Postmortem (예정)
- 재발 방지 (예정)
- Incident Runbook 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Severity Levels - PagerDuty](https://response.pagerduty.com/before/severity_levels/)
- [Severity level examples - Atlassian](https://www.atlassian.com/incident-management/kpis/severity-levels)
- [Incident Response - Google SRE Workbook](https://sre.google/workbook/incident-response/)
- [NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)

### 예제 소스
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Severity, Triage, Response, Operations
