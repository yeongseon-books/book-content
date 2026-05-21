---
series: incident-response-101
episode: 5
title: "Incident Response 101 (5/10): Timeline 작성"
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
  - Timeline
  - Postmortem
  - Logging
  - Operations
seo_description: incident timeline을 실시간으로 기록하고 사실과 해석을 분리하는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (5/10): Timeline 작성

이 글은 Incident Response 101 시리즈의 다섯 번째 글입니다.

incident가 끝난 뒤 가장 자주 벌어지는 일 중 하나는 기억이 서로 다르게 남는 일입니다. 모두가 같은 채널에 있었고 같은 로그를 봤다고 생각하지만, 며칠만 지나도 순서와 판단 근거가 흐려집니다.

그래서 timeline은 사건이 끝난 뒤 쓰는 장식이 아니라, 대응 중에 함께 만들어 두는 기록 장치여야 합니다. 짧고 정확한 한 줄이 나중의 RCA와 postmortem 품질을 결정합니다.

이 글은 Incident Response 101 시리즈의 5번째 글입니다. 여기서는 사실과 해석을 분리하는 기록법, 여러 채널을 스크랩하는 방법, anchor 시점을 고정하는 원칙을 정리합니다.

## 먼저 던지는 질문

- incident가 끝난 뒤 무엇이 언제 일어났는지 어떻게 복원할까요?
- 왜 사건 중간에 바로 기록해야 할까요?
- 한 채널이 아니라 여러 채널을 함께 스크랩해야 하는 이유는 무엇일까요?

## 큰 그림

![Incident Response 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/05/05-01-diagram-at-a-glance.ko.png)

*Incident Response 101 5장 흐름 개요*

타임라인 작성은 대응 중 계속 업데이트하는 살아있는 기록입니다. 각 단계마다 시간과 행동을 명확히 기록해야 나중 분석이 정확합니다.

> 타임라인은 나중 postmortem 분석을 위한 것입니다. 감정보다 사실과 시간을 정확히 남기는 게 핵심입니다.

## 왜 이 주제가 중요한가

기억은 생각보다 빨리 왜곡됩니다. incident 직후에는 모두가 선명하게 기억한다고 믿지만, 며칠만 지나도 순서가 바뀌고, 나중에 알게 된 사실을 마치 당시에도 알고 있었던 것처럼 덧붙이기 쉽습니다. 이렇게 되면 사후 분석은 점점 이야기 중심이 되고, 근거 중심에서 멀어집니다.

timeline은 RCA와 postmortem의 기초 재료입니다. 감정이나 해석보다 “언제, 어디서, 무엇을 관찰했고, 어떤 조치를 실행했는가”를 남겨야 다음 분석이 튼튼해집니다. 그래서 좋은 팀은 timeline 작성을 별도 업무로 보지 않고 incident 대응의 일부로 포함합니다.

## 한눈에 보는 구조

기록원은 하나가 아니어야 합니다. 채팅 채널, 호출 시스템, 배포 로그를 함께 모아 시간순으로 정리해야 사건의 실제 흐름이 드러납니다.

## 핵심 용어

- **timestamp**: UTC 기준 시각입니다.
- **scrape**: 여러 채널에서 이벤트를 모으는 일입니다.
- **fact**: 기록된 관찰 사실입니다.
- **interpretation**: 추정과 의견입니다.
- **anchor**: detected, mitigated 같은 기준 시점입니다.

이 용어를 분리해야 timeline이 흔들리지 않습니다. fact는 그때 실제로 관찰한 내용이고, interpretation은 그 사실에 대한 가설입니다. anchor는 incident 전체 흐름을 정렬하는 기준점 역할을 합니다.

## 전후 비교

이전: 사건이 끝난 뒤 기억에만 의존해 재구성합니다.

이후: 대응 중 남긴 기록과 채널 스크랩을 바탕으로 재구성합니다.

이후 상태의 장점은 분명합니다. 나중에 더 많은 정보를 알게 되더라도 당시 판단과 나중 판단을 구분할 수 있습니다. 기록이 남아 있으면 “그때 왜 그렇게 판단했는가”를 훨씬 공정하게 볼 수 있습니다.

## 단계별 실습: 작은 timeline 빌더 만들기

### 1단계 — 이벤트 모델 정의하기

모든 이벤트를 같은 형태로 모으려면 공통 필드가 필요합니다. 여기서는 시각, 출처, 텍스트 세 가지를 둡니다.

```python
def event(ts, source, text):
    return {"ts": ts, "src": source, "text": text}
```

### 2단계 — 채널 스크랩하기

한 채널만 보면 사건이 반쪽만 보입니다. incident 채널의 메시지를 같은 이벤트 구조로 바꿔 모읍니다.

```python
def scrape(channel):
    return [event(m["ts"], channel, m["text"]) for m in channel.get("messages", [])]
```

### 3단계 — 시간순 정렬하기

모은 이벤트는 반드시 시간순으로 다시 정렬해야 합니다. 순서가 맞아야 원인과 결과를 섞지 않습니다.

```python
def order(events):
    return sorted(events, key=lambda e: e["ts"])
```

### 4단계 — 사실과 해석 분리하기

timeline에는 사실이 먼저 와야 합니다. 추정 메모는 별도 표시로 분리해 두는 편이 좋습니다.

```python
def split(events):
    facts = [e for e in events if not e["text"].startswith("?")]
    notes = [e for e in events if e["text"].startswith("?")]
    return facts, notes
```

### 5단계 — 기준 시점 표시하기

detected, acknowledged, mitigated, resolved 같은 시점을 표시하면 incident 대시보드와 문서를 함께 맞추기 쉬워집니다.

```python
ANCHORS = ("detected", "acknowledged", "mitigated", "resolved")

def mark(event):
    return event["text"].lower() in ANCHORS
```

## 이 코드에서 먼저 볼 점

- 모든 이벤트는 세 필드만으로도 충분히 정리할 수 있습니다.
- 해석은 접두사로 구분해 사실과 섞이지 않게 해야 합니다.
- 기준 시점은 문서와 대시보드를 맞추는 기준점입니다.

timeline에서 가장 중요한 감각은 짧고 자주 기록하는 습관입니다. 길고 잘 쓴 문장보다, 그 순간 남긴 짧은 한 줄이 나중 분석에 더 큰 가치를 줍니다.

## 자주 하는 실수 5가지

1. 사건이 끝난 뒤 한꺼번에 쓰려고 합니다.
2. 해석을 사실처럼 적어 둡니다.
3. 시간대를 KST와 UTC로 섞어 씁니다.
4. 단일 채널만 스크랩합니다.
5. 민감 정보를 그대로 붙여 넣습니다.

특히 첫 번째 실수는 timeline의 가치를 거의 없애 버립니다. 대응 중에 남기지 않은 사실은 나중에 정확히 복원하기 어렵습니다. 그래서 기록 담당자를 따로 두는 편이 도움이 됩니다.

## 실무에서는 이렇게 봅니다

실무에서는 Slack bot이 `!ts <text>` 명령으로 이벤트를 수집하고 postmortem 문서로 내보내도록 구성하기도 합니다. 핵심은 기록을 사람의 기억이 아니라 흐름 안에 끼워 넣는 것입니다.

시니어 엔지니어는 timeline에서 문장력보다 기준 시점의 정확성을 먼저 봅니다. detected, acknowledged, mitigated, resolved가 맞게 잡혀 있으면 나머지 세부 사건도 더 쉽게 복원할 수 있기 때문입니다.

## timeline 입력 예시

좋은 timeline은 긴 문장이 아니라 짧은 사실의 연속입니다. 아래처럼 사실과 해석을 구분해 두면 나중에 RCA에서 기억 왜곡을 줄일 수 있습니다.

```text
2026-05-15T00:03Z fact: error rate exceeded 12%
2026-05-15T00:05Z fact: primary on-call acknowledged page
2026-05-15T00:08Z note: ?possible DB connection pool exhaustion
2026-05-15T00:11Z fact: rollback initiated
2026-05-15T00:19Z fact: error rate returned below 1%
```

`fact`와 `note`를 따로 남기면, 당시 관찰한 내용과 나중에 붙인 해석이 섞이지 않습니다.

## 체크리스트

- [ ] 기록 책임자가 정해져 있다.
- [ ] bot 명령이나 기록 형식이 팀에 공유되어 있다.
- [ ] UTC 사용 규칙이 정리되어 있다.
- [ ] 기준 시점 정의가 문서에 적혀 있다.

## 연습 문제

1. anchor를 한 문장으로 정의해 보세요.
2. 사실과 해석의 차이를 한 문장으로 적어 보세요.
3. 왜 UTC를 기준으로 써야 하는지 설명해 보세요.

## 정리와 다음 글

timeline은 incident가 끝난 뒤 기억으로 쓰는 이야기가 아니라, 대응 중 남긴 사실을 시간순으로 정리한 기록입니다. 여러 채널을 함께 모으고, 사실과 해석을 분리하고, 기준 시점을 정확히 남겨야 이후 RCA와 postmortem이 단단해집니다.

다음 글에서는 trigger와 root cause를 구분해 근본 원인을 찾는 방법을 다루겠습니다.


## 타임라인 심화: 작성 예시와 이벤트 로깅 구현

timeline은 사건이 끝난 뒤 쓰는 회고 문장이 아니라, 대응 중 생성되는 운영 데이터입니다. 기록이 늦어질수록 사실과 해석이 섞이고, RCA 품질이 급격히 떨어집니다. 좋은 timeline은 짧고 빈번한 기록으로 구성됩니다.

### 타임라인 작성 원칙

1. 한 줄에 하나의 사실만 기록합니다.
2. 시각은 UTC로 통일합니다.
3. 사실(fact)과 추정(note)을 접두사로 분리합니다.
4. 핵심 기준 시점(deteced/ack/mitigated/resolved)을 명확히 표기합니다.
5. 수정 이력은 삭제 대신 정정으로 남깁니다.

이 다섯 원칙은 단순하지만, incident 이후 "왜 그렇게 판단했는가"를 되짚는 데 결정적입니다.

### 타임라인 예시

```text
2026-05-21T00:01:20Z fact: alert fired - checkout 5xx ratio 7.2%
2026-05-21T00:02:05Z fact: page acknowledged by primary on-call
2026-05-21T00:03:10Z fact: #inc-checkout channel opened
2026-05-21T00:04:40Z note: ?suspect regression after 23:55 deploy
2026-05-21T00:06:00Z fact: rollback initiated
2026-05-21T00:11:25Z fact: error ratio decreased below 1%
2026-05-21T00:18:00Z fact: customer update published
```

예시를 보면 note가 fact 사이에 섞이더라도 접두사로 구분되어 해석 오염을 줄입니다. 나중에 note가 틀렸어도 당시 판단 맥락은 보존됩니다.

## 이벤트 로깅 코드 예시

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class TimelineEvent:
    ts: str
    kind: str  # fact | note
    source: str
    text: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_event(kind: str, source: str, text: str) -> TimelineEvent:
    return TimelineEvent(ts=utc_now(), kind=kind, source=source, text=text)


def to_line(event: TimelineEvent) -> str:
    return f"{event.ts} {event.kind}: [{event.source}] {event.text}"
```

이 정도 모델만 있어도 Slack bot, incident command tool, postmortem exporter와 연동하기 쉬워집니다.

### 기준 시점(anchor) 계산

```python
ANCHORS = ("detected", "acknowledged", "mitigated", "resolved")


def extract_anchor(line: str) -> str | None:
    lower = line.lower()
    for a in ANCHORS:
        if a in lower:
            return a
    return None
```

anchor 추출을 붙이면 incident 메트릭 계산(MTTA, MTTM, MTTR)의 입력 품질이 올라갑니다.

## 기록 담당 운영 방식

- Scribe를 별도 지정하고, 5분 간격으로 누락 이벤트를 확인합니다.
- 명령 실행자는 결과를 말로 보고, Scribe가 표준 형식으로 기록합니다.
- 커뮤니케이션 발행 시점도 동일 타임라인에 기록합니다.
- incident 종료 후 24시간 내에 기록 정합성 리뷰를 진행합니다.

기록 담당을 분리하면 IC/Ops가 복구에 집중하면서도 사후 학습 품질을 지킬 수 있습니다.

## 품질 점검 질문

- 사실과 해석이 분리되어 있는가?
- UTC 표기가 일관적인가?
- 기준 시점 네 가지가 모두 존재하는가?
- 외부 공지 시점이 누락되지 않았는가?

이 질문에 모두 yes라면 timeline은 postmortem과 RCA의 신뢰 가능한 근거로 사용할 수 있습니다.

## 타임라인 품질 감사 기준

timeline은 작성 후 품질 감사를 거쳐야 합니다. 기준은 간단합니다. 시각 누락이 없는지, 사실과 추정이 분리됐는지, 주요 의사결정이 누락되지 않았는지 확인합니다. 특히 고객 공지 발행 시점과 내부 완화 시점이 모두 포함되어야 커뮤니케이션 품질과 복구 품질을 함께 분석할 수 있습니다.

품질 감사는 문서 팀의 일이 아니라 incident 대응팀의 일부 업무입니다. 대응 당사자가 리뷰에 참여해야 당시 맥락을 정확히 보정할 수 있습니다.

## 운영 보강 메모

현장에서는 문서 규칙만으로 품질이 자동으로 올라가지 않습니다. 그래서 각 팀은 월 1회 이상 실제 incident 사례를 골라 기준 적용 여부를 점검해야 합니다. 점검 항목은 단순할수록 좋습니다. 선언 근거가 수치로 남았는지, 역할 분리가 지켜졌는지, 커뮤니케이션 주기가 유지됐는지, 후속 조치가 티켓으로 연결됐는지 네 가지를 반복 확인하면 됩니다.

이 보강 메모를 남기는 목적은 분량을 늘리는 데 있지 않습니다. 기준을 사건 데이터와 연결해 "다음 대응의 입력"으로 쓰는 데 있습니다. 문서가 저장소 안에서 살아 있으려면 변경 이력, 검증 절차, 교육 루프가 함께 있어야 합니다. 결국 incident 대응 역량은 한 번의 완벽한 대응이 아니라, 같은 실수를 덜 반복하는 조직 습관에서 만들어집니다.

## 타임라인 작성 템플릿과 품질 규칙

timeline은 대응 품질의 원본 데이터입니다. 글로 잘 쓰는 것보다 누락 없이 남기는 것이 더 중요합니다. 아래 템플릿은 현장에서 그대로 복사해 쓰기 위한 최소 형식입니다.

```text
[timeline-entry]
- ts_utc:
- kind: fact | note | decision
- source: pagerduty | slack | deploy | dashboard
- message:
- actor:
```

이 형식의 장점은 단순함입니다. 형식이 짧아야 대응 중에도 계속 입력할 수 있습니다. 긴 양식은 평시에는 좋아 보여도 incident 중에는 잘 지켜지지 않습니다.

## 기준 시점(anchor) 표준

| anchor | 정의 | 예시 |
| --- | --- | --- |
| detected | 이상 탐지 시점 | alert fired |
| acknowledged | 온콜 확인 시점 | page ack |
| mitigated | 고객 영향 감소 확인 시점 | error ratio < 1% |
| resolved | 원인 제거 확인 시점 | permanent fix deployed |
| closed | 후속 기록 연결 시점 | postmortem ticket linked |

anchor를 고정하면 MTTA, MTTM, MTTR 계산이 쉬워집니다. 무엇보다 사건 간 비교가 가능해져 예방 투자 우선순위를 정하기 좋아집니다.

## 기록 누락 방지 운영법

1. Scribe를 별도 지정하고 5분마다 누락 항목을 점검합니다.
2. 명령 실행자는 결과를 구두로 보고하고 Scribe가 표준 형식으로 기록합니다.
3. 공지 발행 시점과 내용 요약도 반드시 동일 타임라인에 남깁니다.
4. incident 종료 24시간 내 정합성 점검을 한 번 더 수행합니다.

이 네 가지를 지키면 timeline이 postmortem의 부록이 아니라, 분석의 중심 데이터로 작동합니다.

## 운영 부록: 타임라인 CSV 예시

```text
ts_utc,kind,source,actor,message
2026-05-21T01:00:03Z,fact,pagerduty,system,alert fired checkout 5xx 7.1%
2026-05-21T01:01:10Z,fact,pagerduty,primary,acknowledged page
2026-05-21T01:03:02Z,fact,slack,IC,incident channel created
2026-05-21T01:05:40Z,note,slack,ops,?suspect timeout regression
2026-05-21T01:08:11Z,fact,deploy,ops,rollback started
2026-05-21T01:14:45Z,fact,dashboard,system,error ratio below 1%
```

CSV 형태로 남기면 검색, 통계, 시각화가 쉬워집니다.

## 운영 부록: 타임라인 품질 검사 규칙

1. 모든 레코드는 UTC 표기를 사용합니다.
2. kind가 fact/note/decision 중 하나인지 확인합니다.
3. note는 물음표 접두사 또는 별도 kind로 표기합니다.
4. anchor 시점(detected/acknowledged/mitigated/resolved)을 누락 없이 포함합니다.
5. 고객 공지 이벤트를 별도 source로 남깁니다.

## 운영 부록: 간단 검증 코드

```python
def validate_timeline(rows: list[dict]) -> list[str]:
    errors = []
    required = {"ts_utc", "kind", "source", "actor", "message"}
    for i, row in enumerate(rows, start=1):
        if not required.issubset(row):
            errors.append(f"row {i}: missing required columns")
        if row.get("kind") not in {"fact", "note", "decision"}:
            errors.append(f"row {i}: invalid kind")
        if "Z" not in row.get("ts_utc", ""):
            errors.append(f"row {i}: timestamp must be UTC")
    return errors
```

타임라인 검증 코드는 단순해도 충분합니다. 핵심은 기록 품질을 사람이 아닌 규칙으로 반복 점검하는 데 있습니다.

## 타임라인 운영 추가 점검 항목

아래 항목은 실무에서 바로 점검할 수 있는 추가 체크포인트입니다.

- 체크포인트 1: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 2: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 3: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 4: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 5: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 6: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 7: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 8: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.

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

운영팀은 이 점검 결과를 다음 주 온콜 브리핑에서 공유하고, 기준 변경이 있으면 같은 날 runbook과 템플릿을 함께 갱신해 문서-실행 간 시차를 줄여야 합니다.

또한 월 1회 교차 리뷰를 통해 템플릿 문장, 보고 주기, 연락 체계가 실제 조직 변경을 반영하는지 확인하고, 변경 사항은 즉시 버전 이력으로 남겨야 합니다.

## 처음 질문으로 돌아가기

- **incident가 끝난 뒤 무엇이 언제 일어났는지 어떻게 복원할까요?**
  - 본문의 기준은 Timeline 작성를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
  - 타임라인은 결과물이 아니라, 대응 중 계속 업데이트하는 살아있는 기록입니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
  - 각 단계마다 '누가 어떤 행동을 했고 그 결과가 무엇인가'를 UTC나 로컬 시간으로 기록합니다.
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.
  - 후속 분석에 쓸 정보이므로, 감정보다 사실과 시간을 정확히 남기는 게 핵심입니다.
<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity 분류](./02-severity.md)
- [Incident Response 101 (3/10): 초기 대응](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- **Timeline 작성 (현재 글)**
- Root Cause Analysis (예정)
- Mitigation과 Resolution (예정)
- Postmortem (예정)
- 재발 방지 (예정)
- Incident Runbook 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem Process - PagerDuty](https://response.pagerduty.com/after/post_mortem_process/)
- [Postmortem guide - Atlassian](https://www.atlassian.com/incident-management/postmortem)
- [OpenTelemetry Semantic Conventions](https://github.com/open-telemetry/semantic-conventions)

### 예제 소스
- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Timeline, Postmortem, Logging, Operations
