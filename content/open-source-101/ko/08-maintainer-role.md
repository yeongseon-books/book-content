---
series: open-source-101
episode: 8
title: Maintainer 의 역할
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - Maintainer
  - Triage
  - Burnout
  - Beginner
seo_description: Maintainer 가 하는 일과 번아웃 없이 지속하는 방법을 정리한 글
last_reviewed: '2026-05-11'
---

# Maintainer 의 역할

오픈소스를 처음 볼 때는 메인테이너를 코드를 가장 잘 아는 사람 정도로 생각하기 쉽습니다. 물론 기술적인 판단도 중요합니다. 하지만 실제로 메인테이너가 하는 일은 훨씬 넓습니다. 이슈를 정리하고, 리뷰 우선순위를 잡고, 릴리스를 내고, 사람 사이의 경계를 조율하고, 후계자를 키우는 일까지 포함됩니다.

그래서 메인테이너 역할은 실력만으로 버티기 어렵습니다. 모든 일을 혼자 처리하면 금방 번아웃이 오고, 프로젝트는 한 사람의 체력에 묶여 버립니다. 이 글에서는 메인테이너를 기술 리더이자 운영자라는 관점에서 정리해 보겠습니다.

## 이 글에서 다룰 문제

- 메인테이너는 실제로 어떤 책임을 집고 있을까요?
- triage, review, release는 왜 하나의 루틴으로 묶어 봐야 할까요?
- 권한 위임과 후계자 육성은 왜 선택이 아니라 지속성 문제일까요?
- 번아웃을 막기 위해 메인테이너가 먼저 세워야 할 경계는 무엇일까요?
- bus factor가 낮은 프로젝트는 어떤 위험을 안고 있을까요?

## 왜 중요한가

메인테이너의 건강 상태가 곧 프로젝트의 수명과 연결되는 경우가 많습니다. 한 사람에게 리뷰, 릴리스, 커뮤니티 응답이 모두 몰리면 코드 품질보다 지속 가능성이 먼저 무너집니다.

또 메인테이너는 프로젝트 문화의 기준점 역할을 합니다. 응답 속도, 리뷰 톤, 문서 수준, 릴리스 규칙이 대부분 여기서 시작됩니다. 그래서 메인테이너 역할을 이해하는 것은 오픈소스 운영의 본체를 이해하는 일과 비슷합니다.

## 먼저 잡아둘 멘탈 모델

> 메인테이너는 모든 일을 직접 처리하는 개발자가 아니라, 프로젝트가 계속 굴러가도록 흐름과 책임을 조정하는 지휘자에 가깝습니다.

```mermaid
flowchart LR
    T[트리아지] --> R[리뷰]
    R --> Re[릴리스]
    Re --> D[위임]
```

이 순서가 중요한 이유는 일이 쌓이는 방식이 이 흐름을 따르기 때문입니다. triage가 흔들리면 리뷰가 밀리고, 리뷰가 밀리면 릴리스가 늦어지고, 릴리스가 늦어지면 메인테이너에게 더 많은 요청이 몰립니다. 결국 위임이 없으면 루프 전체가 막힙니다.

## 핵심 개념

- maintainer는 저장소 방향과 품질 기준을 지키는 책임자입니다.
- triage는 들어오는 일을 분류하고 우선순위를 정하는 과정입니다.
- review는 코드 품질뿐 아니라 프로젝트 방향과의 정합성을 확인하는 일입니다.
- delegate는 권한과 책임을 신뢰할 수 있는 사람에게 넘기는 행위입니다.
- bus factor는 특정 인물이 빠졌을 때 프로젝트가 얼마나 위험해지는지 보여 주는 지표입니다.

이 다섯 가지가 모두 메인테이너의 하루 안에 들어 있습니다. 그래서 메인테이너 역할은 개발 업무의 확장판이 아니라 운영 역할이 더해진 별도 책임으로 보는 편이 맞습니다.

## 생각이 어떻게 바뀌는가

Before: 혼자 모든 이슈와 PR을 처리해야 메인테이너답다.

After: 권한을 나누고 루틴을 만들수록 프로젝트는 더 오래 간다.

## 직접 따라해 보기: 메인테이너 루틴 설계

### 1단계 — 주간 triage 시간 정하기

일이 들어올 때마다 반응하면 항상 밀립니다. 짧더라도 정해진 시간에 분류와 우선순위 조정을 하는 편이 효과적입니다.

```text
Monday, 30 minutes: label and prioritize
```

### 2단계 — PR 첫 응답 기준 정하기

완벽한 리뷰보다 예측 가능한 응답이 더 중요할 때가 많습니다. 첫 응답 시간이 보이면 기여자는 기다릴 수 있습니다.

```text
Aim for first response within two days
```

### 3단계 — 릴리스 리듬 만들기

패치와 마이너 릴리스 주기를 어느 정도 고정하면 사용자 기대치도 함께 안정됩니다.

```text
Patch weekly, minor monthly
```

### 4단계 — 권한 위임하기

위임은 부담을 덜기 위한 편법이 아니라 프로젝트 리스크를 줄이는 핵심 수단입니다. 리뷰, 라벨링, 문서 수정 권한부터 나누기 시작할 수 있습니다.

```text
GitHub Org → Teams → write permission
```

### 5단계 — 휴식 공지하기

비어 있는 시간을 숨기면 기여자는 침묵을 거절로 오해합니다. 경계를 분명히 알리는 편이 오히려 신뢰를 줍니다.

```markdown
> Maintainer is on vacation Aug 1-14.
```

## 이 예시에서 읽어야 할 포인트

- 루틴은 피로를 줄입니다.
- 위임은 규모 확장의 출발점입니다.
- 공지는 경계를 세우는 문장입니다.
- bus factor를 낮추는 일은 기술보다 사람 구조의 문제입니다.

## 자주 하는 실수 5가지

1. 모든 PR 리뷰를 혼자 맡습니다.
2. 부재 기간을 알리지 않습니다.
3. bus factor가 1인 상태를 오래 방치합니다.
4. 라벨과 우선순위 체계를 만들지 않습니다.
5. 후계자를 키우지 않습니다.

## 실무에서는 이렇게 봅니다

회사 안에서 Tech Lead나 플랫폼 오너가 맡는 역할과 매우 비슷합니다. 들어오는 요청을 정리하고, 코드 기준을 맞추고, 릴리스 일정을 잡고, 사람을 성장시키는 일이 함께 묶여 있습니다. 그래서 오픈소스 메인테이너 경험은 기술 리더십 훈련으로도 가치가 큽니다.

시니어 엔지니어는 메인테이너십을 영웅 역할로 보지 않습니다. 혼자 버티는 구조는 오래 못 갑니다. 반복 가능한 루틴, 명확한 권한 위임, 공개된 일정과 경계, 그리고 후계자 육성이 있어야 프로젝트가 사람 한 명을 넘어섭니다.

## 체크리스트

- [ ] 주간 triage 루틴이 있습니다.
- [ ] 리뷰 응답 기준을 정했습니다.
- [ ] 위임 가능한 권한을 식별했습니다.
- [ ] bus factor를 2 이상으로 올릴 계획이 있습니다.

## 연습 문제

1. bus factor를 한 문장으로 정의해 보세요.
2. triage와 review의 차이를 한 문장으로 적어 보세요.
3. 후계자를 키우는 방법 하나를 적어 보세요.

## 마무리

이번 글에서는 메인테이너를 뛰어난 개발자가 아니라 프로젝트의 흐름을 지키는 운영 책임자로 정리했습니다. 오픈소스가 오래 가려면 코드를 잘 쓰는 사람보다, 일을 나누고 경계를 세울 수 있는 사람이 필요할 때가 많습니다.

다음 글에서는 이런 경험이 개인 경력에 어떻게 쌓이는지 보겠습니다. 오픈소스 활동을 포트폴리오로 정리하는 방법이 이어집니다.

<!-- toc:begin -->
- [오픈소스란 무엇인가](./01-what-is-open-source.md)
- [라이선스 이해하기](./02-understanding-licenses.md)
- [Issue 읽기](./03-reading-issues.md)
- [PR 만들기](./04-creating-pull-requests.md)
- [좋은 README](./05-good-readme.md)
- [Release 와 Versioning](./06-release-and-versioning.md)
- [Community 관리](./07-community-management.md)
- **Maintainer 의 역할 (현재 글)**
- 오픈소스 포트폴리오 (예정)
- 내 첫 오픈소스 프로젝트 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Source Guides — Maintainer](https://opensource.guide/best-practices/)
- [Bus factor](https://en.wikipedia.org/wiki/Bus_factor)
- [Maintainer Burnout](https://opensource.guide/maintainer-mental-health/)
- [GitHub Teams](https://docs.github.com/en/organizations/organizing-members-into-teams)

Tags: OpenSource, Maintainer, Triage, Burnout, Beginner
