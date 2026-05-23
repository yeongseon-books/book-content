---
episode: 8
language: ko
last_reviewed: '2026-05-15'
seo_description: blameless postmortem 구조, 영향 수치화, owner와 due date가 있는 후속 조치 추적 원칙을 정리합니다.
series: incident-response-101
status: publish-ready
tags:
- Incident
- Postmortem
- Blameless
- Learning
- Operations
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Incident Response 101 (8/10): Postmortem"
---

# Incident Response 101 (8/10): Postmortem

incident가 끝나면 팀은 잠깐 안도합니다. 서비스가 복구됐고, 호출도 멈췄고, 채널도 조용해졌기 때문입니다. 그런데 바로 그 시점에 가장 중요한 작업 하나가 남습니다.

이번 사건에서 배운 내용을 조직 자산으로 바꾸는 일입니다. 이 단계를 건너뛰면 같은 문제를 다른 날짜에 다시 맞게 됩니다.

이 글은 Incident Response 101 시리즈의 8번째 글입니다. 여기서는 비난 없는 postmortem 구조, 영향과 원인을 수치와 사실로 남기는 법, owner와 due date가 있는 후속 조치 추적을 다룹니다.

![Incident Response 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/08/08-01-diagram-at-a-glance.ko.png)
*Incident Response 101 8장 흐름 개요*
> Postmortem의 가치는 대응 중 배운 것을 팀이 함께 공유하고, 재발 방지 항목으로 구체화하는 데 있습니다.

## 먼저 던지는 질문

- postmortem은 왜 incident 종료 뒤에 꼭 필요할까요?
- 비난 없는 원칙은 책임 없음과 어떻게 다를까요?
- 매번 새 양식을 만드는 대신 템플릿을 고정해야 하는 이유는 무엇일까요?

## 왜 이 주제가 중요한가

같은 incident가 반복된다는 말은 대개 시스템보다 학습 루프가 끊겼다는 신호입니다. 사건은 끝났는데 원인이 구조로 정리되지 않았고, 후속 조치가 추적되지 않았으며, 다음 사람에게 전달되지 않았기 때문입니다. postmortem은 회고 문서이면서 동시에 예방 장치입니다.

또 하나 중요한 이유는 기억의 왜곡입니다. 사건이 끝난 직후에는 모두가 생생하게 기억한다고 생각하지만, 며칠만 지나도 순서와 판단 근거가 흐려집니다. 사실을 남기지 않으면 조직은 가장 큰 목소리나 마지막 기억에 의존하게 됩니다.

## 한눈에 보는 구조

postmortem은 publish로 끝나면 안 됩니다. 공유 뒤에 action item 등록과 추적이 이어져야 학습이 행동으로 바뀝니다.

## 핵심 용어

- **blameless**: 개인 비난 없이 시스템과 맥락을 중심으로 원인을 보는 원칙입니다.
- **summary**: 사건을 짧게 이해할 수 있도록 정리한 요약입니다.
- **impact**: 고객이 실제로 겪은 영향입니다.
- **action item**: 검증 가능한 후속 작업입니다.
- **owner**: 후속 작업의 책임자입니다.

여기서 비난 없는 원칙은 책임을 지우지 않는다는 말이 아닙니다. 개인을 원인으로 끝내지 않는다는 말입니다. 어떤 경보가 없었는지, 어떤 리뷰가 부족했는지, 어떤 기본값이 위험했는지를 함께 봐야 같은 사고를 줄일 수 있습니다.

## 전후 비교

이전: 내부에서만 돌고 비난과 방어가 섞인 문서를 남깁니다.

이후: 조직 전체가 참고할 수 있는 비난 없는 문서와 후속 조치 목록을 남깁니다.

이후 상태에서는 문서의 용도가 바뀝니다. 읽는 사람은 누구를 탓해야 하는지가 아니라, 다음에 무엇을 바꿔야 하는지를 찾습니다. 그래서 좋은 postmortem은 감정보다 구조가 앞에 옵니다.

## 단계별 실습: 작은 postmortem 빌더 만들기

### 1단계 — 템플릿 고정하기

사건마다 양식이 달라지면 비교와 검색이 어려워집니다. summary, impact, timeline, rca, actions 정도는 고정하는 편이 좋습니다.

```python
TEMPLATE = ("summary", "impact", "timeline", "rca", "actions")

def new_doc():
    return {k: "" for k in TEMPLATE}
```

### 2단계 — 요약 길이 제한하기

요약이 길어지면 읽는 사람이 핵심을 놓칩니다. 첫머리에는 짧은 사고 개요가 있어야 합니다.

```python
def is_short(text):
    return text.count(".") <= 3
```

### 3단계 — 영향 수치화하기

영향을 “컸다”라고만 쓰면 다음 비교가 어렵습니다. 사용자 수와 지속 시간처럼 비교 가능한 단위를 남기는 편이 좋습니다.

```python
def impact(users, minutes):
    return {"users": users, "minutes": minutes}
```

### 4단계 — 후속 조치 등록하기

후속 조치에는 내용만 있으면 안 됩니다. 누가 맡는지와 언제까지 끝낼지가 함께 있어야 추적할 수 있습니다.

```python
def action(text, owner, due):
    return {"text": text, "owner": owner, "due": due}
```

### 5단계 — 기한 지난 작업 찾기

추적은 복잡할 필요가 없습니다. 오늘 날짜와 due date를 비교하는 것만으로도 방치된 작업을 찾을 수 있습니다.

```python
def overdue(actions, today):
    return [a for a in actions if a["due"] < today]
```

## 이 코드에서 먼저 볼 점

- 템플릿이 고정돼 있어 문서 구조가 흔들리지 않습니다.
- impact는 숫자로 남겨 비교 가능하게 합니다.
- 추적은 결국 owner와 deadline을 확인하는 일입니다.

좋은 postmortem은 글을 잘 쓰는 재능보다 구조를 잘 고정하는 습관에서 나옵니다. 양식이 일정해야 읽는 사람도 빨리 훑을 수 있고, 사건 사이 비교도 쉬워집니다.

## 자주 하는 실수 5가지

1. 개인 이름을 그대로 원인으로 적고 시스템 원인을 더 보지 않습니다.
2. 후속 조치에 담당자를 붙이지 않습니다.
3. due date가 없어 추적이 끊깁니다.
4. 문서를 대응팀 내부에서만 보고 조직에 공유하지 않습니다.
5. 사건마다 템플릿을 새로 만들어 비교 가능성을 잃습니다.

가장 위험한 실수는 후속 조치 없는 postmortem입니다. 문서는 근사하지만 무엇도 바뀌지 않습니다. 그 문서는 기록일 수는 있어도 학습 장치는 아닙니다.

## 실무에서는 이렇게 봅니다

실무에서는 Notion이나 Confluence에 postmortem 템플릿을 고정해 두고, 후속 조치는 Jira 같은 추적 도구와 연결하는 경우가 많습니다. 그리고 분기 리뷰에서 기한을 넘긴 항목을 다시 확인합니다. 이 분기 리뷰가 있어야 문서와 운영이 다시 연결됩니다.

시니어 엔지니어는 blameless를 문화라고 봅니다. 사고의 원인을 개인에게만 묶지 않고, 시스템과 프로세스의 빈틈으로 확장해서 봅니다. 동시에 문서만 남겨서는 아무 의미가 없다는 점도 잘 압니다.

## postmortem action item 좋은 예와 나쁜 예

후속 조치는 문장 차이 하나로도 실행 가능성이 크게 달라집니다.

- 나쁜 예: `모니터링을 강화한다.`
- 좋은 예: `checkout API 5xx 비율이 3분 연속 2%를 넘으면 PagerDuty SEV2 규칙이 열리도록 Alertmanager 규칙을 추가한다. Owner: platform-oncall, Due: 2026-06-01`

좋은 action item은 동사로 시작하고, 누가 맡는지와 언제 검증할지를 함께 적습니다. 그래야 문서가 실제 운영 변경으로 이어집니다.

## 나쁨 vs 좋은 조치 항목 예시

후속 조치는 문장 하나 차이로도 실행 가능성이 크게 달라집니다. 구체성과 검증 가능성을 함께 비교해 보겠습니다.

**나쁨 예: 추상적이고 검증할 수 없음**

- 모니터링을 강화한다
- 커뮤니케이션을 개선한다
- 더 주의하기로 한다
- 로그를 더 자세히 남긴다

**좋은 예: 구체적이고 검증 가능**

- checkout API 5xx 비율이 3분 연속 2%를 넘으면 PagerDuty SEV2 규칙이 열리도록 Alertmanager 규칙을 추가한다. Owner: @platform-oncall, Due: 2026-06-01, Verify: Alertmanager config PR 머지 + 테스트 실행
- incident channel에 자동 timeline bot을 추가해 모든 메시지에 UTC 타임스탬프를 붙인다. Owner: @incident-lead, Due: 2026-05-25, Verify: 봇 배포 후 테스트 incident 채널에서 확인
- 로그에 request_id를 포함하도록 structured logging 형식을 모든 서비스에 적용한다. Owner: @backend-team, Due: 2026-06-15, Verify: 각 서비스별 PR + production 로그 샘플 검사
- staging 환경에 production 수준 부하 테스트를 매주 화요일 오전 자동 실행하도록 CI에 추가한다. Owner: @qa-platform, Due: 2026-06-10, Verify: CI config PR + 첫 실행 결과 확인

좋은 예에서는 모든 action item이 동사로 시작하고, 누가 맡는지, 언제까지, 어떻게 검증할지가 모두 명시돼 있습니다. 이렇게 써야 분기 리뷰에서 진행 상황을 추적할 수 있고, 완료 여부를 명확히 판단할 수 있습니다.

## 비난 없는 포스트모템 문화

blameless postmortem의 핵심은 개인의 실수를 원인으로 끝내지 않는 것입니다. "누가 잘못했는가"로 끝나면 다음 사건에서도 같은 구조가 반복됩니다. 대신 "어떤 시스템 조건이 그 실수를 가능하게 만들었는가"를 물어야 합니다.

예를 들어 프로덕션 DB에서 잘못된 쿼리를 실행해 장애가 발생했다고 가정해 보겠습니다.

나쁨 예:

- 원인: 엔지니어 A가 프로덕션 DB를 직접 수정함
- 후속 조치: 엔지니어 A에게 경고

좋은 예:

- 원인: 프로덕션 DB 접근 권한이 개발자 계정에 부여돼 있음 + 위험한 명령어 실행 전 리뷰 절차 없음 + staging와 production 연결 문자열 구분이 불분명함
- 후속 조치: 프로덕션 DB 접근을 별도 bastion을 통한 승인 절차로 변경 + SQL 쿼리 리뷰 체크리스트 추가 + 연결 문자열에 환경 태그 포함

좋은 예에서는 개인을 비난하는 대신, 그 실수가 가능했던 조건을 여럿 찾아냅니다. 그리고 후속 조치도 그 조건을 모두 개선하는 방향으로 적습니다.

실무에서는 포스트모템 문서 상단에 "blameless" 태그를 붙여 두고, 문서 리뷰에서 개인 비난 부분이 들어가면 수정을 요청하는 경우가 많습니다. 이 문화는 시간이 걸리지만, 정착되면 팀원들이 incident 후에도 솔직하게 사실을 공유하게 됩니다.

## 포스트모템 템플릿 구성요소

포스트모템 템플릿은 간결해야 하지만, 필수 요소는 빠지면 안 됩니다. 각 섹션의 역할과 작성 팁을 미리 정리해 두면 incident 마다 일관된 품질의 문서를 남길 수 있습니다.

| 섹션 | 역할 | 작성 팁 |
| --- | --- | --- |
| Summary | 사건 요약 | 3문장 이내, severity·서비스·기간 포함 |
| Impact | 고객 영향 | 사용자 수, 지속시간, 매출 영향 수치화 |
| Timeline | 시간순 기록 | UTC 타임스탬프, 타임존 표기, 비난 없는 사실 나열 |
| Root Cause | 원인 분석 | trigger와 root cause 구분, 5 Whys 체인 |
| Action Items | 후속 조치 | 동사 시작, owner·due date 필수, 검증 기준 포함 |
| Lessons Learned | 학습 요약 | 무엇을 배웠고, 다음에 어떻게 달라질지 명시 |

템플릿을 고정하면 문서의 일관성이 높아집니다. 신규 팀원도 과거 postmortem을 빠르게 훈을 수 있고, 분기 리뷰에서 비슷한 유형의 incident를 쉽게 찾을 수 있습니다. 실무에서는 이 템플릿을 Markdown이나 Notion 페이지로 만들어 두고, 각 incident마다 복사해 채워 넣는 방식을 씁니다.

## 체크리스트

- [ ] 고정된 postmortem 템플릿이 있다.
- [ ] action item마다 owner와 due date가 있다.
- [ ] 문서를 저장하고 검색할 공용 공간이 있다.
- [ ] 분기 리뷰 등 추적 루프가 운영되고 있다.

## 연습 문제

1. blameless를 한 문장으로 정의해 보세요.
2. action item에 owner가 빠지면 왜 문제가 되는지 설명해 보세요.
3. 여러분 팀의 postmortem 템플릿에 반드시 들어가야 할 항목 다섯 개를 적어 보세요.

## 정리와 다음 글

postmortem은 incident 뒤에 남기는 회고 메모가 아니라, 조직 학습을 실제 행동으로 바꾸는 문서입니다. 비난 없는 원칙으로 사실과 맥락을 정리하고, 영향을 수치로 남기고, 후속 조치에 담당자와 기한을 붙여야 같은 문제가 반복되는 일을 줄일 수 있습니다.

다음 글에서는 이렇게 남긴 학습을 실제 재발 방지 체계로 바꾸는 방법을 다루겠습니다.

## 포스트모템 심화: 템플릿 전문과 작성 가이드

postmortem은 사건 기록이 아니라 조직 운영 설계 문서입니다. 그래서 템플릿은 읽기 쉬워야 하고, 항목은 실행 가능해야 합니다. 아래는 실무에서 그대로 사용할 수 있는 기본 템플릿입니다.

### Postmortem 템플릿

```markdown
# Postmortem: INC-YYYYMMDD-XXX

## 1) Incident Summary
- Date/Time (UTC):
- Severity:
- Affected Service:
- Incident Commander:
- Current Status: Resolved

## 2) Customer Impact
- Impacted users (estimate):
- Impact duration (minutes):
- Affected journey (checkout/login/search/...):
- Financial/contractual impact (if known):

## 3) Timeline (Fact Only)
- 00:01 detected ...
- 00:03 acknowledged ...
- 00:07 mitigation started ...
- 00:19 impact reduced ...
- 00:41 resolved ...

## 4) Root Cause Analysis
- Trigger:
- Root cause:
- Contributing factors:
  - People:
  - Process:
  - Tooling:
  - System:

## 5) 잘된 점
- 

## 6) 아쉬운 점
- 

## 7) Action Items
| Action | Owner | Due | Priority | Verification |
| --- | --- | --- | --- | --- |

## 8) Follow-up Review Date
- YYYY-MM-DD
```

### 작성 가이드

1. 요약은 5문장 이내로 유지합니다.
2. impact는 반드시 숫자로 씁니다.
3. timeline은 fact와 note를 분리합니다.
4. 원인은 개인이 아니라 시스템 경계로 기술합니다.
5. action item은 검증 방법까지 포함합니다.

이 다섯 규칙만 지켜도 postmortem 품질 편차를 크게 줄일 수 있습니다.

## 좋은 action item 판별 기준

- 동사로 시작하는가?
- 담당자(owner)가 지정됐는가?
- 기한(due)이 명시됐는가?
- 검증 방법이 있는가?
- 우선순위가 분명한가?

한 항목이라도 빠지면 실행률이 급락합니다. 특히 검증 방법이 없으면 완료 보고가 형식화되기 쉽습니다.

## 추적 자동화 예시

```python
from dataclasses import dataclass

@dataclass
class ActionItem:
    text: str
    owner: str
    due: str
    priority: str
    verify: str
    status: str = "open"

def is_complete(item: ActionItem) -> bool:
    return item.status == "done" and bool(item.verify)
```

코드는 단순하지만, 상태를 구조화하면 분기 리뷰에서 미완료 항목을 빠르게 식별할 수 있습니다.

## 운영 루프

- incident 종료 48시간 내 postmortem 초안 작성
- 5영업일 내 리뷰 완료
- action item 티켓 발행 및 owner 지정
- 30일 내 후속 점검

이 루프가 고정되면 postmortem은 "좋은 문서"가 아니라 "실제 변경을 만드는 장치"가 됩니다.

## 리뷰 미팅 운영 방식

postmortem 리뷰 미팅은 사실 확인 회의와 개선 설계 회의를 분리하면 효과가 높습니다. 1차 회의에서는 타임라인과 원인 분류의 정확성만 검토하고, 2차 회의에서 action item 우선순위를 정합니다. 한 회의에서 모든 것을 끝내려 하면 감정 소모가 커지고 결론이 흐려질 수 있습니다.

회의 결과는 반드시 티켓 시스템에 연결해야 합니다. 문서 코멘트로만 남기면 실행 추적이 약해집니다. owner 지정과 due date 확정은 회의 종료 조건으로 두는 편이 좋습니다.

## 운영 보강 메모

현장에서는 문서 규칙만으로 품질이 자동으로 올라가지 않습니다. 그래서 각 팀은 월 1회 이상 실제 incident 사례를 골라 기준 적용 여부를 점검해야 합니다. 점검 항목은 단순할수록 좋습니다. 선언 근거가 수치로 남았는지, 역할 분리가 지켜졌는지, 커뮤니케이션 주기가 유지됐는지, 후속 조치가 티켓으로 연결됐는지 네 가지를 반복 확인하면 됩니다.

이 보강 메모를 남기는 목적은 분량을 늘리는 데 있지 않습니다. 기준을 사건 데이터와 연결해 "다음 대응의 입력"으로 쓰는 데 있습니다. 문서가 저장소 안에서 살아 있으려면 변경 이력, 검증 절차, 교육 루프가 함께 있어야 합니다. 결국 incident 대응 역량은 한 번의 완벽한 대응이 아니라, 같은 실수를 덜 반복하는 조직 습관에서 만들어집니다.

## 운영 리허설 권장안

문서 개정 후에는 반드시 짧은 리허설을 수행해야 합니다. 20분짜리 tabletop만으로도 기준 누락을 빠르게 발견할 수 있습니다. 진행 순서는 간단합니다. 가상 알림을 열고, 역할을 배정하고, 첫 공지를 작성하고, 종료 조건을 선언해 봅니다. 그 과정에서 헷갈리는 문장이나 끊긴 링크가 나오면 즉시 수정 항목으로 기록합니다.

리허설의 목적은 사람 평가가 아니라 문서 검증입니다. 실제 incident는 긴장 상태에서 진행되므로, 평시에는 분명해 보이던 절차도 현장에서는 모호해질 수 있습니다. 정기 리허설을 운영 루틴에 넣으면 문서와 실행 사이의 간극을 줄일 수 있습니다.

## 포스트모템 회의 운영안

postmortem 품질은 문서 작성보다 회의 운영에서 크게 갈립니다. 사실 확인과 개선 설계를 한 번에 끝내려 하면 감정 소모가 커지고 결론이 흐려집니다. 아래처럼 2단계 회의로 분리하면 품질이 안정됩니다.

| 회차 | 목표 | 입력 | 출력 |
| --- | --- | --- | --- |
| 1차(사실 검증) | timeline/impact/rca 정확성 확인 | 기록 로그, 대시보드 | 수정된 사실 기반 문서 |
| 2차(개선 설계) | action item 우선순위 결정 | 확정된 1차 문서 | owner/due/verify 포함 실행 목록 |

이 구조는 비난 없는 문화에도 도움이 됩니다. 1차에서는 사실만 다루고, 2차에서 개선을 설계하므로 개인 평가처럼 흐르는 것을 줄일 수 있습니다.

## action item 등록 템플릿

```text
[action-item-template]
- description:
- owner:
- due_date:
- priority: (high/medium/low)
- verification:
- linked_ticket:
```

포스트모템이 조직 자산이 되려면 action item이 티켓 시스템과 연결되어야 합니다. 문서 코멘트만으로는 실행 추적이 어렵습니다.

## 운영 부록: Postmortem 검토 체크시트

| 항목 | 확인 질문 |
| --- | --- |
| Summary | 세 문장 안에 사건 핵심이 담겼는가? |
| Impact | 사용자/시간/사업 영향이 수치화됐는가? |
| Timeline | fact와 note가 분리됐는가? |
| RCA | trigger와 root cause가 분리됐는가? |
| Actions | owner/due/verify가 모두 있는가? |

## 운영 부록: 리뷰 회의 종료 조건

1. 사실 오류가 모두 수정되었다.
2. action item 우선순위가 합의되었다.
3. 각 action item owner가 확정되었다.
4. due date가 입력되었다.
5. 다음 점검 일정이 캘린더에 등록되었다.

종료 조건이 있어야 postmortem이 문서 단계에서 멈추지 않고 실행 단계로 넘어갑니다.

## 포스트모템 운영 추가 점검 항목

아래 항목은 실무에서 바로 점검할 수 있는 추가 체크포인트입니다.

- 체크포인트 1: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 2: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 3: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.

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

- **postmortem은 왜 incident 종료 뒤에 꼭 필요할까요?**
  - 본문에서 강조했듯이 incident 한 번에 큰 비용을 이미 치렀기 때문에, 그 경험에서 배우지 않으면 같은 비용이 그대로 반복됩니다. postmortem은 발생-감지-완화-회복으로 흩어진 정보를 한 문서에 모아 timeline, root cause, action item을 명시화해 조직 자산으로 바꾸는 유일한 단계입니다.
- **비난 없는 원칙은 책임 없음과 어떻게 다를까요?**
  - 본문에서 본 것처럼 blameless는 "사람을 탓하지 않는다"는 뜻이지 "책임이 없다"는 뜻이 아닙니다. 개인을 처벌 대상으로 만들면 다음 incident 때 정보가 숨겨져 같은 사고가 더 자주 일어나기 때문에, 원인은 시스템·프로세스 수준에서 찾되 후속 조치와 책임자는 명확히 남기는 것이 두 원칙을 동시에 지키는 방법입니다.
- **매번 새 양식을 만드는 대신 템플릿을 고정해야 하는 이유는 무엇일까요?**
  - 본문 예시처럼 incident마다 양식이 달라지면 timeline·impact·root cause·action item 같은 필수 칸이 누락되기 쉽고, 사후에 incident 간 비교도 어려워집니다. 고정 템플릿은 작성자의 인지 부담을 줄여 사실 수집과 분석에 더 많은 시간을 쓰게 해 주고, 누적된 postmortem을 패턴 분석 가능한 데이터셋으로 만들어 줍니다.
  - 대응이 끝나고 며칠 안에 열어야 기억이 생생합니다.
<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity 분류](./02-severity.md)
- [Incident Response 101 (3/10): 초기 대응](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Timeline 작성](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- [Incident Response 101 (7/10): Mitigation과 Resolution](./07-mitigation-and-resolution.md)
- **Postmortem (현재 글)**
- 재발 방지 (예정)
- Incident Runbook 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)

### 공식 문서
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem Process - PagerDuty](https://response.pagerduty.com/after/post_mortem_process/)
- [Postmortem templates - Atlassian](https://www.atlassian.com/incident-management/postmortem/templates)
- [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/)

Tags: Incident, Postmortem, Blameless, Learning, Operations
