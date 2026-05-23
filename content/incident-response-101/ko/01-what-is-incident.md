---
series: incident-response-101
episode: 1
title: "Incident Response 101 (1/10): Incident란 무엇인가?"
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
  - Response
  - SRE
  - Operations
  - OnCall
seo_description: incident와 일반 버그를 구분하는 기준, 고객 영향 임계값, 온콜 첫 판단 원칙을 운영 관점에서 설명합니다.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (1/10): Incident란 무엇인가?

온콜에 처음 들어가면 가장 먼저 흔들리는 질문이 있습니다. 알림이 울렸을 때 이것을 정말 incident로 봐야 하는지, 아니면 일반 버그나 경고로 남겨도 되는지 빠르게 판단하기 어렵기 때문입니다.

기준이 없으면 어떤 팀은 과하게 반응하고, 어떤 팀은 너무 늦게 움직입니다. incident 대응의 출발점은 기술 스택보다 먼저, 고객 영향과 대응 임계값을 같은 언어로 합의하는 일입니다.

이 글은 Incident Response 101 시리즈의 첫 번째 글입니다. 여기서는 장애와 일반 버그를 가르는 기준, 고객 영향 중심의 정의, 그리고 초보 온콜 담당자가 처음부터 붙잡아야 할 판단 축을 정리합니다.

![Incident Response 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/01/01-01-diagram-at-a-glance.ko.png)
*Incident Response 101 1장 흐름 개요*
> Incident 판정의 핵심은 사람의 감각이 아니라 합의한 임계값입니다. 팀이 정한 기준이 있을 때 반복 가능하고 일관된 대응이 가능합니다.

## 먼저 던지는 질문

- 어떤 문제를 incident라고 불러야 할까요?
- alert와 incident는 무엇이 다를까요?
- 고객 영향은 어떤 식으로 수치화해야 할까요?

## 왜 이 주제가 중요한가

incident 정의가 없으면 대응은 두 방향으로 무너집니다. 하나는 과잉 대응입니다. 작은 경고에도 사람을 모두 깨우고, 결국 팀은 알림 자체를 덜 믿게 됩니다. 다른 하나는 과소 대응입니다. 실제로는 고객 영향이 커지고 있는데도 “조금 더 보자”는 말만 반복하다가 대응 타이밍을 놓칩니다.

실무에서 incident 정의는 단어 선택이 아니라 비용 통제 장치입니다. 누가 호출되는지, 어떤 채널을 여는지, 얼마나 자주 업데이트하는지, 언제 경영진에게 올리는지가 모두 여기서 갈립니다. 첫 기준이 흔들리면 뒤에 붙는 severity, 초기 대응, 커뮤니케이션도 함께 흔들립니다.

## 한눈에 보는 구조

이 그림의 핵심은 모든 이벤트가 incident는 아니라는 점입니다. 먼저 고객 영향이 있는지 묻고, 그 영향이 팀이 정한 기준을 넘는지 본 뒤에야 incident라는 이름을 붙입니다. 이름이 바뀌면 대응 경로도 함께 바뀝니다.

## 핵심 용어

- **incident**: 고객 영향이 발생한 비정상 이벤트입니다.
- **alert**: 사람이 조치해야 할 가능성을 알리는 신호입니다.
- **outage**: 서비스 중단 상태입니다.
- **degradation**: 성능이나 품질이 눈에 띄게 떨어진 상태입니다.
- **on-call**: 장애 대응 대기 순번 체계입니다.

이 다섯 용어를 분리해 두면 대화가 훨씬 정확해집니다. alert는 입력 신호이고, incident는 분류 결과입니다. outage와 degradation은 영향의 형태를 설명하는 말이고, on-call은 그 사건을 누가 먼저 받을지를 정하는 운영 체계입니다.

## 전후 비교

이전: 모든 alert를 incident처럼 취급합니다.

이후: 고객 영향을 먼저 보고 incident인지 bug인지 분류한 뒤 대응합니다.

이 차이는 생각보다 큽니다. 이전 상태에서는 사람의 경험과 긴장감이 판단을 좌우합니다. 이후 상태에서는 합의한 기준이 먼저 말합니다. 좋은 온콜 운영은 감각보다 기준이 앞서는 상태를 만드는 일입니다.

## 단계별 실습: incident 판정 로직 만들기

### 1단계 — 영향 정보 모으기

먼저 사건을 판단하는 데 필요한 최소 정보를 한 구조로 묶습니다. 여기서는 영향을 받은 사용자 수와 지속 시간을 넣습니다.

```python
def impact(users, minutes):
    return {"users": users, "minutes": minutes}
```

### 2단계 — 임계값 정하기

다음은 어디까지를 incident로 볼지 코드에 고정하는 단계입니다. 이 숫자는 기술 법칙이 아니라 팀의 운영 합의입니다.

```python
def is_incident(i, user_th=100, min_th=5):
    return i["users"] >= user_th or i["minutes"] >= min_th
```

### 3단계 — 사건 분류하기

이제 앞에서 정한 기준으로 사건 이름을 붙입니다. 분류가 있어야 이후 채널과 우선순위도 분리할 수 있습니다.

```python
def classify(i):
    return "incident" if is_incident(i) else "bug"
```

### 4단계 — 호출 여부 정하기

incident라면 사람을 깨우고, 아니면 일반 이슈 흐름으로 보낼 수 있습니다. 온콜 피로도는 이런 분기에서 크게 갈립니다.

```python
def page(i):
    return classify(i) == "incident"
```

### 5단계 — 채널 연결하기

마지막으로 분류 결과를 대응 채널과 연결합니다. 사건 이름이 곧 협업 경로를 정합니다.

```python
def channel(kind):
    return "#inc" if kind == "incident" else "#bugs"
```

## 이 코드에서 먼저 볼 점

- 임계값은 취향이 아니라 합의입니다.
- 분류는 기술 구현이면서 동시에 운영 정책입니다.
- 코드로 기준을 남기면 주관적 판단을 줄일 수 있습니다.

특히 중요한 점은 incident 판정이 사람 감각에만 머물지 않는다는 사실입니다. 코드는 모든 예외를 없애 주지는 못하지만, 최소한 팀이 같은 출발선에서 판단하게 해 줍니다. 온콜이 성숙한 팀일수록 이런 기준이 문서와 코드 양쪽에 남아 있습니다.

## 자주 하는 실수 5가지

1. alert와 incident를 같은 말처럼 씁니다.
2. 합의된 임계값이 없어 사람마다 다르게 판단합니다.
3. 고객 영향 대신 내부 불편만 보고 incident를 선언합니다.
4. 신규 온콜 담당자를 위한 예시와 교육 자료가 없습니다.
5. 사건이 끝난 뒤 기록을 남기지 않아 다음 대응이 다시 처음부터 시작됩니다.

이 실수들은 대부분 기술 부족보다 기준 부재에서 나옵니다. 정의를 세우고, 예시를 붙이고, 기록을 남기면 대응 품질이 빠르게 안정됩니다.

## 실무에서는 이렇게 봅니다

실서비스에서는 PagerDuty 같은 도구가 severity 규칙과 함께 incident 분류를 자동화하기도 합니다. 다만 도구가 incident를 대신 이해해 주지는 않습니다. 팀이 먼저 무엇을 incident로 볼지 합의해야 도구도 제대로 동작합니다.

시니어 엔지니어는 대개 고객 영향을 가장 먼저 봅니다. 로그의 화려함보다 실제로 몇 명이 얼마나 오래 영향을 받았는지가 기준이기 때문입니다. 과잉 대응도 비용이고, 늦은 대응도 비용입니다. 그래서 좋은 팀은 기록을 남기고, 그 기록으로 다음 임계값을 다듬습니다.

## 첫 판단에서 바로 확인할 질문

incident 여부를 선언하기 전에 다음 다섯 질문을 빠르게 훑어보면 감각보다 기준이 앞서기 시작합니다. 이 질문은 온콜 초보자에게 특히 유용합니다.

- 지금 영향을 받는 사용자는 누구이며, 몇 명 정도로 보이나요?
- 에러율, 지연 시간, 결제 실패율처럼 바로 확인할 수 있는 숫자가 있나요?
- 최근 30분 안에 배포, 설정 변경, 외부 의존성 장애가 있었나요?
- 우회 경로가 있나요, 아니면 고객이 바로 막히는 상태인가요?
- 지금 이 상태가 5분 더 지속되면 누구를 깨워야 하나요?

```bash
# 예시: 선언 전에 바로 보는 첫 확인 목록
checklist=(error-rate latency saturation deploy-feed statuspage)
for item in "${checklist[@]}"; do
  printf 'check: %s\n' "$item"
done
```

여기서 중요한 일은 완벽한 진단보다 선언 근거를 먼저 모으는 것입니다. 다섯 질문에 답하면 지금 대응 채널을 열지, 일반 이슈로 돌릴지 더 차분하게 고를 수 있습니다.

## 체크리스트

- [ ] incident 판정 임계값이 팀 문서에 정리되어 있다.
- [ ] 분류 기준이 코드나 자동화 규칙에 반영되어 있다.
- [ ] incident와 bug의 라우팅 채널이 분리되어 있다.
- [ ] 신규 온콜 담당자를 위한 예시와 교육 자료가 있다.

## 연습 문제

1. incident를 한 문장으로 정의해 보세요.
2. outage와 degradation의 차이를 한 문장씩 적어 보세요.
3. 여러분 팀에서는 사용자 수와 지속 시간 중 어느 축을 더 중요하게 볼지 정해 보세요.

## 정리와 다음 글

incident는 “이상한 일”이 아니라, 고객 영향이 합의한 선을 넘은 사건입니다. 이 기준이 있어야 alert, bug, outage, degradation을 구분할 수 있고, 누구를 호출할지와 어느 채널로 모을지도 일관되게 정할 수 있습니다. 온콜 운영은 결국 판단 기준을 공유하는 일에서 시작합니다.

다음 글에서는 incident의 심각도를 공통 언어로 표현하는 방법, 즉 severity 분류를 다루겠습니다.

## 운영 기준 심화: Incident 판정 매트릭스

초기 판정에서 가장 어려운 지점은 "불편"과 "장애"의 경계입니다. 이 경계를 사람의 감각에만 맡기면 같은 상황에서 다른 결론이 반복됩니다. 그래서 팀은 최소한 세 축을 고정해야 합니다. 첫째는 고객 수, 둘째는 핵심 경로 영향 여부, 셋째는 지속 시간입니다. 이 세 축은 복잡한 모델이 아니라, 누구나 같은 값을 보고 같은 질문을 던지게 만드는 공통 프레임입니다.

| 구분 | 고객 수(추정) | 핵심 경로 영향 | 지속 시간 | 기본 판정 |
| --- | --- | --- | --- | --- |
| A | 1~99 | 없음 | 5분 미만 | bug/alert |
| B | 100~999 | 부분 영향 | 5~15분 | incident 후보 |
| C | 1,000~9,999 | 핵심 기능 저하 | 15~30분 | incident |
| D | 10,000+ | 결제/로그인/주요 API 중단 | 30분+ | 고심각 incident |

표의 목적은 완벽한 분류가 아니라, 논의를 빠르게 수렴시키는 것입니다. 실무에서는 항상 경계 사례가 나옵니다. 예를 들어 고객 수는 작지만 결제 실패율이 급증하는 경우가 있습니다. 이때는 "핵심 경로 영향" 축에 더 높은 가중치를 두는 규칙을 미리 문서화해 두면 판단 편차가 줄어듭니다.

## 대응 프로세스 흐름도 해설

incident 판정 이후에도 혼선이 잦은 이유는 "무엇을 먼저 할지"가 고정되어 있지 않기 때문입니다. 아래 순서는 많은 팀에서 재현 가능하게 동작하는 기본 흐름입니다.

1. 탐지 신호 확인: 알림이 실제 서비스 상태와 일치하는지 1차 검증합니다.
2. 임시 판정: incident 후보인지, 일반 이슈인지 빠르게 분리합니다.
3. 소유권 확정: primary on-call이 ack를 남기고 채널을 엽니다.
4. 영향 측정: 고객 수, 오류율, 실패 경로를 숫자로 기록합니다.
5. 대응 경로 선택: incident면 전용 워크플로, 아니면 backlog/bug 경로로 라우팅합니다.

이 순서는 기술적으로 단순하지만 조직적으로 강력합니다. 특히 3단계와 4단계를 건너뛰면, 실제 대응은 시작된 것처럼 보여도 소유권과 근거가 없어져서 재현성과 회고 품질이 급격히 떨어집니다.

## 판정 회의에서 쓰는 질문 카드

온콜 초반 3분은 정보가 불완전합니다. 이때 아래 질문 카드를 그대로 읽는 습관이 유용합니다.

- 지금 실패하는 기능이 핵심 사용자 여정에 포함되는가?
- 실패 비율이 절대 수치와 추세 둘 다에서 상승 중인가?
- 최근 배포/설정 변경/외부 의존성 변동이 있었는가?
- 고객이 즉시 우회 가능한가, 아니면 업무가 중단되는가?
- 10분 뒤 동일 상태라면 누가 추가로 호출되어야 하는가?

질문 카드는 기술 수준과 무관하게 팀 전체 의사결정을 평준화합니다. 주니어 온콜도 같은 질문을 던질 수 있고, 시니어는 답의 질을 빠르게 평가할 수 있습니다.

## 간단한 판정 자동화 예시

```python
from dataclasses import dataclass

@dataclass
class IncidentSignal:
    users: int
    minutes: int
    core_path_impacted: bool
    error_ratio: float

def decide(signal: IncidentSignal) -> str:
    if signal.core_path_impacted and signal.error_ratio >= 0.05:
        return "incident"
    if signal.users >= 1000 or signal.minutes >= 15:
        return "incident"
    return "bug"
```

코드의 목적은 모든 상황을 기계적으로 판단하는 것이 아닙니다. 팀이 합의한 기준을 명시적으로 남겨 "왜 incident로 분류했는지"를 설명 가능하게 만드는 데 있습니다.

## 운영 체크포인트

- 임계값 변경 이력이 Git 기록으로 남는가?
- 분류 결과가 채널/호출 정책과 자동 연동되는가?
- 경계 사례가 새로 나올 때 문서가 즉시 갱신되는가?
- 신규 온콜 교육에서 실제 사례 기반 분류 연습을 하는가?

이 네 가지가 갖춰지면 incident 정의는 문서가 아니라 운영 시스템으로 작동합니다.

## 판정 기준 운영 노트

incident 기준은 한 번 정하고 끝나는 문서가 아닙니다. 월별로 실제 사례를 표본 추출해 오분류를 점검해야 합니다. 특히 "incident였지만 bug로 처리된 사례"와 "bug였지만 incident로 과대 처리된 사례"를 따로 모으면 임계값 조정 방향이 분명해집니다. 운영팀은 숫자만 보는 대신 사건 본문을 함께 읽어 왜 오분류가 발생했는지 확인해야 합니다.

또한 기준 개정은 문서 수정으로 끝내지 말고, 온콜 교육과 자동화 규칙에 동시에 반영해야 합니다. 문서와 자동화가 분리되면 실전에서 구버전 기준이 계속 작동합니다. 그래서 개정 PR에는 최소한 세 항목을 포함하는 편이 좋습니다. 기준 변경 사유, 적용 시점, 영향받는 대응 규칙입니다.

## 운영 보강 메모

현장에서는 문서 규칙만으로 품질이 자동으로 올라가지 않습니다. 그래서 각 팀은 월 1회 이상 실제 incident 사례를 골라 기준 적용 여부를 점검해야 합니다. 점검 항목은 단순할수록 좋습니다. 선언 근거가 수치로 남았는지, 역할 분리가 지켜졌는지, 커뮤니케이션 주기가 유지됐는지, 후속 조치가 티켓으로 연결됐는지 네 가지를 반복 확인하면 됩니다.

이 보강 메모를 남기는 목적은 분량을 늘리는 데 있지 않습니다. 기준을 사건 데이터와 연결해 "다음 대응의 입력"으로 쓰는 데 있습니다. 문서가 저장소 안에서 살아 있으려면 변경 이력, 검증 절차, 교육 루프가 함께 있어야 합니다. 결국 incident 대응 역량은 한 번의 완벽한 대응이 아니라, 같은 실수를 덜 반복하는 조직 습관에서 만들어집니다.

## 현장에서 바로 쓰는 Incident 판정 템플릿

incident를 선언할지 말지 망설이는 시간은 생각보다 비쌉니다. 그래서 팀은 선언 기준을 문장으로 외우기보다 표와 템플릿으로 고정하는 편이 좋습니다. 아래 템플릿은 초보 온콜이 첫 3분 안에 incident 후보를 정리할 때 그대로 붙여 넣어 사용할 수 있는 최소 양식입니다.

```text
[incident-triage-template]
- detected_at_utc:
- affected_journey: (로그인/결제/검색/주문/...)
- estimated_impacted_users:
- impact_duration_minutes:
- current_error_rate:
- current_latency_p95_ms:
- current_severity_candidate: (SEV1/SEV2/SEV3/bug)
- immediate_action: (declare incident / monitor as bug)
- owner_oncall:
```

템플릿을 쓰면 개인 감각이 아니라 팀 기준으로 판단하게 됩니다. 더 중요한 점은 이 양식이 뒤의 severity 분류, 커뮤니케이션, timeline 작성으로 자연스럽게 이어진다는 사실입니다. incident 대응 품질은 정답을 빨리 찾는 능력보다, 같은 입력을 같은 구조로 받는 능력에서 먼저 올라갑니다.

## 온콜 교대 기준과 최소 운영 규칙

incident는 근무시간에만 발생하지 않습니다. 교대 품질이 낮으면 같은 사건을 두 번 대응하는 상황이 생깁니다. 아래는 작은 팀에서도 바로 적용 가능한 교대 규칙입니다.

| 항목 | 최소 기준 | 실패 신호 |
| --- | --- | --- |
| 인계 메시지 | 4줄 요약(영향/완화/미해결/다음 행동) | "지금 어디까지 했죠?" 반복 질문 |
| 인계 시점 | 교대 10분 전 초안, 교대 시 확정 | 교대 직후 15분 공백 |
| 지표 확인 | 인수자가 핵심 지표 2회 재확인 | 구두만 듣고 즉시 판단 |
| 문서 링크 | incident 채널, 대시보드, runbook 링크 포함 | 링크 누락으로 탐색 시간 증가 |

운영 규칙의 목적은 문서를 늘리는 데 있지 않습니다. 누가 들어와도 같은 속도로 판단하도록 만드는 데 있습니다. incident 대응은 개인의 영웅 플레이가 아니라 교대 가능한 팀 스포츠여야 합니다.

## 운영 부록: Incident 선언 기록 예시

아래 예시는 실제 incident 선언 직후 남기는 기록 형식입니다. 핵심은 긴 설명이 아니라 판단 근거를 빠르게 남기는 것입니다.

```text
[declare-incident]
incident_id: INC-2026-05-21-001
detected_at_utc: 2026-05-21T01:03:11Z
detected_by: alert.checkout.error_ratio
candidate_severity: SEV2
affected_journey: checkout
estimated_impacted_users: 4300
error_ratio: 0.087
latency_p95_ms: 1840
decision: declare_incident
owner: primary-oncall
next_update_utc: 2026-05-21T01:30:00Z
```

## 운영 부록: 팀 합의 규칙 카드

1. incident 선언은 늦게 맞추는 정답보다 빠른 가설이 더 낫습니다.
2. 선언 후 하향 조정은 가능하지만, 선언 자체를 늦추면 잃는 시간이 큽니다.
3. 영향 수치가 불완전해도 "추정" 표기를 붙여 즉시 공유합니다.
4. 원인 추정은 분리하고, 사실 데이터는 timeline에 우선 기록합니다.
5. 사건 종료 후에는 반드시 선언 시점 판단이 적절했는지 리뷰합니다.

## 운영 부록: 판정 회고 질문

- 선언이 늦어진 원인은 무엇이었는가?
- 선언 직후 역할 배정이 5분 안에 끝났는가?
- 영향 수치가 첫 공지에 반영됐는가?
- 선언 기준 문서와 실제 판단이 어긋난 지점은 어디였는가?
- 다음 incident에서 바로 줄일 수 있는 마찰은 무엇인가?

## 운영 추가 점검 항목

아래 항목은 실무에서 바로 점검할 수 있는 추가 체크포인트입니다.

- 체크포인트 1: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 2: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 3: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 4: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 5: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.

```text
[quick-audit]
- declaration_latency_minutes:
- first_update_latency_minutes:
- mitigation_started_minutes:
- recovery_verification_metrics:
- postmortem_linked: true/false
```

## 운영 메모: 점검 루프

운영 문서는 작성으로 끝나지 않습니다. 월간 점검 루프를 통해 선언 기준, 역할 분리, 공지 주기, 후속 조치 추적이 실제 incident에서 유지되는지 확인해야 합니다. 점검 결과는 다음 리허설 시나리오와 runbook 개정 항목으로 바로 연결하는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **어떤 문제를 incident라고 불러야 할까요?**
  - 고객 영향을 먼저 봅니다. 호출할 사람, 열 채널, 공지 빈도가 모두 여기서 결정됩니다.
- **alert와 incident는 무엇이 다를까요?**
  - Alert는 '무언가 일어났다'는 입력 신호이고, Incident는 '대응이 필요하다'는 분류 결과입니다.
- **고객 영향은 어떤 식으로 수치화해야 할까요?**
  - 사용자 수와 장애 지속 시간으로 임계값을 정합니다. 기술 법칙이 아니라 팀의 운영 합의이므로 기록으로 남겨야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Incident란 무엇인가? (현재 글)**
- Severity 분류 (예정)
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
- [PagerDuty Incident Response Documentation](https://response.pagerduty.com/)
- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident management overview - Atlassian](https://www.atlassian.com/incident-management)
- [NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)

### 예제 소스
- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Response, SRE, Operations, OnCall
