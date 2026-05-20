---
series: devops-101
episode: 10
title: "DevOps 101 (10/10): 운영 가능한 DevOps 흐름"
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
  - DORA
  - Strategy
  - Capstone
  - Engineering
seo_description: 코드부터 포스트모템까지를 하나의 흐름으로 묶는 DevOps 운영 모델을 설명합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (10/10): 운영 가능한 DevOps 흐름

이 글은 DevOps 101 시리즈의 마지막 글입니다.

## 먼저 던지는 질문

- CI, CD, 모니터링, 장애 대응이 각각 있는데도 팀 전체 속도가 느린 이유는 무엇일까요?
- DevOps를 도구 목록이 아니라 하나의 운영 흐름으로 보려면 어떤 그림이 필요할까요?
- DORA 4지표는 무엇을 측정하며 왜 함께 봐야 할까요?

## 큰 그림

![DevOps 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/10/10-01-diagram.ko.png)

*DevOps 101 10장 흐름 개요*

이 그림에서는 운영 가능한 DevOps 흐름를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 운영 가능한 DevOps 흐름의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

도구를 하나씩 붙이는 것만으로는 DevOps가 완성되지 않습니다. CI는 성공하는데 배포는 느리고, 배포는 자주 하는데 장애에서 배우지 못한다면 도구는 있어도 흐름은 없는 상태입니다.

운영 가능한 DevOps는 개별 최적화보다 연결을 봅니다. build, deploy, monitor, incident, postmortem이 서로의 입력이 될 때 속도와 안정성을 함께 끌어올릴 수 있습니다.

> 측정되지 않는 것은 개선되지 않습니다.

## 한눈에 보는 개념

이 그림의 핵심은 마지막 화살표입니다. 포스트모템이 코드와 절차로 돌아오지 않으면, 앞선 모든 자동화는 선형 파이프라인일 뿐 학습 루프가 되지 못합니다.

## 핵심 용어

- **DORA metrics**: Google 연구에서 널리 알려진 네 가지 DevOps 지표입니다.
- **Deploy frequency**: 얼마나 자주 배포하는지를 나타내는 지표입니다.
- **Lead time for changes**: 변경이 merge에서 production까지 가는 데 걸린 시간입니다.
- **Change failure rate**: 장애를 만든 배포의 비율입니다.
- **MTTR**: 장애에서 복구하는 데 걸린 평균 시간입니다.
- **Ritual**: 분명한 목적을 가진 반복 팀 미팅입니다.

DevOps가 추상적으로 느껴질 때는 이 용어들을 흐름 위에 올려 보면 좋습니다. 팀이 어디서 느리고 어디서 불안정한지 숫자와 리듬으로 읽을 수 있기 때문입니다.

## Before/After

**Before**: build, deploy, and monitoring run *separately* and no one looks at the *whole picture*.

도구는 각각 존재하지만 연결이 없습니다. 그래서 같은 문제가 매번 다른 모습으로 다시 나타나고, 팀은 부분 최적화만 반복하게 됩니다.

**After**: a *single dashboard* shows the *four DORA metrics* and the team reviews it weekly.

흐름이 잡힌 팀은 전체 그림을 함께 봅니다. 배포 수, 리드 타임, 실패율, 복구 시간이 같은 대화 안에서 다뤄지기 때문에 속도와 안정성을 동시에 조정할 수 있습니다.

## 흐름을 만드는 5단계

### 1단계 — 한 페이지에 흐름 그리기

많은 팀이 자기 단계만 잘 압니다. 그래서 먼저 해야 할 일은 자동화 추가보다, 전체 흐름을 같은 종이에 올려 모두가 보는 것입니다.

```text
On a single sheet of paper:
PR -> CI -> staging -> prod -> alert -> on-call -> postmortem
For each step, write the *owner* and the *tool*.
```

### 2단계 — DORA 측정 시작

자동 수집이 완벽히 준비되기 전이라도 측정은 시작할 수 있습니다. 처음에는 손으로 적어도 됩니다. 중요한 것은 숫자를 보기 시작하는 습관입니다.

```python
# Simplest start: create a GitHub Release on every deploy.
# Even hand-tracking these four numbers weekly is enough.
metrics = {
    "deploy_frequency": "5 per week",
    "lead_time": "6 hours average",
    "change_failure_rate": "8%",
    "mttr": "22 minutes",
}
```

### 3단계 — 주간 의식: 배포 리뷰 (30분)

지표는 읽지 않으면 쌓이기만 합니다. 짧고 반복적인 주간 리뷰는 흐름을 살아 있게 만드는 최소한의 팀 리듬입니다.

```text
- Last week's deploy count
- One incident summary from last week
- This week's risky deploys
```

### 4단계 — 월간 의식: 포스트모템 읽기 (60분)

개별 장애보다 중요한 것은 반복 패턴입니다. 포스트모템을 함께 읽어야 시스템 결함이 팀의 다음 변경으로 이어집니다.

```text
- Read the month's postmortems together
- Track the action-item completion rate
- When patterns appear, change the *system*
```

### 5단계 — 분기마다 다음 단계 고르기

DevOps 흐름은 한 번 설계하고 끝나는 체계가 아닙니다. 팀 규모와 병목이 바뀌면 다음 학습 주제와 도구 구성도 함께 바뀌어야 합니다.

```text
- Pick the next learning track
- Add or remove tools
- Propose org-structure changes
```

## DORA 지표를 실제 운영 대화로 바꾸는 법

DORA 4지표는 숫자를 모으는 것으로 끝나면 금방 형식이 됩니다. 핵심은 각 숫자가 어떤 운영 질문으로 이어지는지 팀이 함께 알고 있는가입니다. 예를 들어 배포 빈도는 "우리가 자주 배포하느냐"보다 "작게 나눠 배포할 수 있을 만큼 변경 단위를 관리하고 있느냐"라는 질문으로 읽는 편이 더 유용합니다.

```text
Deploy frequency      -> 변경을 충분히 작게 나누고 있는가
Lead time             -> 리뷰/빌드/승인 중 어디가 병목인가
Change failure rate   -> 어떤 종류의 변경이 자주 사고를 내는가
MTTR                  -> 탐지, 판단, 복구 중 어디가 가장 느린가
```

이렇게 해석해야 숫자가 회고 자료가 아니라 다음 액션의 입력으로 바뀝니다.

## 90일 운영 개선 계획 예시

마지막 장에서 가장 필요한 것은 거대한 비전보다 실행 가능한 다음 90일 계획입니다. 예를 들면 작은 팀은 아래처럼 잡을 수 있습니다.

```text
1-30일   PR 필수 체크 정리, staging 스모크 테스트 추가, runbook 3개 작성
31-60일  RED 대시보드 구축, alert -> runbook 링크 연결, DORA 수기 집계 시작
61-90일  배포 리뷰/포스트모템 리듬 고정, 가장 잦은 실패 유형 1개 자동화
```

이 계획이 좋은 이유는 도구 도입보다 루프 단축에 직접 연결되기 때문입니다. 팀이 이미 가진 시스템을 더 자주 보고, 더 빨리 복구하고, 더 작은 변경으로 움직이게 만드는 항목만 남겨 두는 것이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- 지표는 처음부터 자동 수집하지 않아도 됩니다. 중요한 것은 측정을 시작하는 일입니다.
- 팀 리듬은 길고 무거운 행사보다 짧고 반복적인 의식이 더 잘 유지됩니다.
- 피드백 루프가 닫힐 때 팀은 비로소 장애에서 학습하기 시작합니다.

좋은 DevOps 흐름은 자동화 수가 아니라, 팀이 같은 데이터를 같은 주기로 읽고 실제 변경으로 연결하는 힘에서 만들어집니다.

## 자주 하는 실수 5가지

1. **도구부터 도입하는 실수**입니다. 흐름이 없으면 도구는 연결되지 않은 섬이 됩니다.
2. **DORA 네 지표 중 하나만 보는 실수**입니다. 네 개를 함께 봐야 속도와 안정성의 균형이 보입니다.
3. **포스트모템을 읽지 않는 실수**입니다. 문서는 남아도 학습은 남지 않습니다.
4. **의식을 길고 형식적으로 만드는 실수**입니다. 짧고 데이터 중심이어야 지속됩니다.
5. **개선 책임자를 두지 않는 실수**입니다. 흐름에도 owner가 필요합니다.

## 실무에서는 이렇게 이어집니다

성숙한 조직은 플랫폼 팀을 두고, 내부 개발자 플랫폼을 통해 이 흐름 자체를 셀프서비스로 제공합니다. 새 서비스가 기본 CI, 배포, 관측성, 문서 템플릿을 자동으로 상속받게 만드는 식입니다.

하지만 작은 팀이라면 한 장짜리 흐름, 손으로 적는 DORA 지표, 짧은 주간·월간 리뷰만으로도 충분히 큰 변화를 만들 수 있습니다. DevOps의 핵심은 거대한 시스템보다 학습 리듬에 있습니다.

## 시니어 엔지니어는 이렇게 봅니다

- 흐름 자체가 아키텍처입니다.
- 지표가 없으면 토론은 쉽게 의견 싸움이 됩니다.
- 작은 의식이 큰 변화를 더 오래 끌고 갑니다.
- 플랫폼화는 규모가 커질수록 중요해집니다.
- 학습은 끝나지 않으므로 다음 학습 트랙을 의도적으로 골라야 합니다.

## 체크리스트

- [ ] 코드부터 포스트모템까지의 전체 흐름이 한 그림에 있습니다.
- [ ] 팀이 DORA 4지표를 매주 확인합니다.
- [ ] 주간과 월간 운영 의식이 일정에 잡혀 있습니다.
- [ ] 흐름의 개선을 책임지는 owner가 분명합니다.

## 연습 문제

1. 팀의 Code -> Postmortem 흐름을 한 장으로 그려 보세요.
2. 한 주 동안 DORA 4지표를 손으로 측정해 보세요.
3. 30분짜리 주간 배포 리뷰를 한 번 직접 운영해 보세요.

## 정리 및 다음 단계

DevOps 101 시리즈는 여기서 마무리입니다. 핵심은 하나입니다. DevOps는 도구의 집합이 아니라, 팀이 빠르게 배포하고 장애에서 배우고 다시 시스템을 고치는 학습 루프입니다.

다음 학습 경로는 현재 팀의 병목에 따라 고르면 됩니다.

- **Observability 101** — 메트릭, 로그, trace를 함께 읽는 방법
- **SRE 101** — SLO, SLI, error budget으로 신뢰성을 운영하는 방법
- **Kubernetes 101** — 컨테이너 오케스트레이션을 본격적으로 다루는 방법

DevOps는 결국 팀이 배우는 방식입니다. 이 감각을 잡았다면 이제 다음 도구보다 다음 학습 루프를 설계할 차례입니다.

## 처음 질문으로 돌아가기

- **CI, CD, 모니터링, 장애 대응이 각각 있는데도 팀 전체 속도가 느린 이유는 무엇일까요?**
  - 본문의 기준은 운영 가능한 DevOps 흐름를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DevOps를 도구 목록이 아니라 하나의 운영 흐름으로 보려면 어떤 그림이 필요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **DORA 4지표는 무엇을 측정하며 왜 함께 봐야 할까요?**
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
- [DevOps 101 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- **운영 가능한 DevOps 흐름 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [DORA Research Program](https://dora.dev/)
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)
- [Accelerate (book)](https://itrevolution.com/product/accelerate/)
- [Team Topologies](https://teamtopologies.com/)

Tags: DevOps, DORA, Strategy, Capstone, Engineering
