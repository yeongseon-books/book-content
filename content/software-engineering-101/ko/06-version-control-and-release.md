---
series: software-engineering-101
episode: 6
title: 버전 관리와 릴리스
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareEngineering
  - Git
  - VersionControl
  - Release
  - SemVer
seo_description: git 브랜치 전략, 시맨틱 버저닝, 체인지로그, 안전한 릴리스 절차를 정리합니다.
last_reviewed: '2026-05-15'
---

# 버전 관리와 릴리스

코드를 잘 작성하고 테스트도 통과했는데, 릴리스 단계에서 사고가 나면 사용자는 그 앞의 노력을 알지 못합니다. 서비스는 결국 배포된 버전으로 평가받습니다. 그래서 버전 관리와 릴리스는 개발의 마지막 절차가 아니라, 사용자 신뢰가 실제로 형성되는 접점입니다.

많은 팀이 릴리스를 한 번의 이벤트로만 봅니다. 버전 번호를 올리고, 체인지로그를 쓰고, 프로덕션에 올리면 끝이라고 생각합니다. 하지만 안정적인 팀은 릴리스를 회복 가능한 과정으로 봅니다. 작은 변경을 자주 보내고, 카나리로 먼저 노출하고, 신호가 나쁘면 즉시 되돌릴 수 있어야 합니다.

이 글은 Software Engineering 101 시리즈의 여섯 번째 글입니다. 여기서는 브랜치 전략, 시맨틱 버저닝, 자동 체인지로그, 카나리 배포, 롤백까지 포함한 안전한 릴리스 흐름을 정리합니다.

## 이 글에서 다룰 문제

- 브랜치 전략은 언제 trunk-based가 맞고, 언제 Git Flow가 맞을까요?
- 버전 1.4.2 같은 숫자는 사용자에게 무엇을 약속할까요?
- 체인지로그는 어떻게 자동화할 수 있을까요?
- 카나리와 롤백은 릴리스 안전성에 어떤 차이를 만들까요?
- 릴리스 노트는 개발자 언어가 아니라 사용자 언어로 왜 써야 할까요?

> 시맨틱 버저닝은 버전 표기가 아니라 약속의 표기법입니다. 그 약속이 깨지면 신뢰가 먼저 무너집니다.

## 왜 중요한가

릴리스는 코드와 사용자가 만나는 유일한 순간입니다. 이 단계에서 장애가 나면 그 전의 설계, 구현, 테스트는 모두 뒤로 밀립니다. 반대로 릴리스가 작고 자주, 그리고 회복 가능하게 설계되어 있으면 팀은 더 빠르게 배우고 더 적게 다칩니다.

안정적인 릴리스 문화는 기술 스택보다 운영 습관에서 나옵니다. 버전 결정이 자동화되어 있는지, 체인지로그가 사용자 관점으로 정리되는지, 롤백이 분 단위로 가능한지, 사람 손이 많이 타는 수동 단계가 줄어드는지가 더 중요합니다.

## 한눈에 보는 흐름

![한눈에 보는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/06/06-01-concept-at-a-glance.ko.png)
*기능 브랜치부터 카나리와 프로덕션까지 이어지는 릴리스 흐름*

단계를 잘게 나누면 이상 신호가 생겼을 때 회수 비용도 같이 줄어듭니다.

## 핵심 용어

- **Trunk-Based Development**: 짧은 브랜치를 자주 main에 합치는 방식입니다.
- **Git Flow**: develop, release, hotfix 브랜치를 두는 전통적 모델입니다.
- **SemVer**: MAJOR, MINOR, PATCH로 호환성 약속을 표현하는 방식입니다.
- **Changelog**: 사용자가 읽는 변경 기록입니다.
- **Canary**: 일부 트래픽에 먼저 새 버전을 노출하는 방식입니다.

## 전후 비교

**이전 — 거대한 릴리스**

```text
200 PRs every two weeks -> impossible to localize a bug
```

**이후 — 점진 릴리스**

```text
multiple merges per day -> 5% canary -> monitor -> 100%
```

작고 자주 보내는 릴리스가 더 안전한 이유는, 문제가 생겨도 범위를 빨리 좁힐 수 있기 때문입니다.

## 단계별로 작은 릴리스 파이프라인 만들기

### 1단계 — Conventional Commits 쓰기

```text
# 1_commits.txt
feat(auth): add refresh token rotation
fix(billing): handle zero amount invoices
chore(deps): bump fastapi to 0.110
```

커밋 메시지가 기계가 읽을 수 있는 형태여야 버전과 체인지로그 자동화가 붙습니다.

### 2단계 — SemVer 규칙 정하기

```text
# 2_semver.md
feat -> MINOR
fix  -> PATCH
BREAKING CHANGE -> MAJOR
```

버전은 감으로 정하지 않는 편이 좋습니다. 변경 유형이 버전을 결정하도록 만들어야 일관성이 생깁니다.

### 3단계 — 체인지로그 자동 생성하기

```yaml
# 3_release.yml
- uses: googleapis/release-please-action@v4
  with:
    release-type: python
```

PR가 머지되면 릴리스 PR과 체인지로그가 자동으로 만들어지게 두는 편이 안전합니다.

### 4단계 — 카나리 단계 두기

```yaml
# 4_canary.yml
strategy:
  canary:
    weight: 5
    after: { metrics: error_rate < 0.5%, duration: 10m }
```

소수 트래픽으로 먼저 건강 상태를 확인하고, 신호가 좋을 때만 전체로 넓혀 가는 흐름입니다.

### 5단계 — 즉시 롤백 가능하게 만들기

```bash
# 5_rollback.sh
kubectl rollout undo deployment/api
```

롤백은 문서에만 있는 절차가 아니라, 실제로 1분 안팎에 끝날 수 있어야 합니다.

## 릴리스 절차를 점검하는 방법

릴리스 안전성은 배포 도구보다 되돌릴 수 있는지에서 더 분명하게 드러납니다. 최근 배포 하나를 골라 버전 결정부터 롤백까지의 시간을 따라가 보세요.

### 확인 절차

1. 최근 릴리스 노트와 관련 커밋 세 개를 엽니다.
2. SemVer가 실제 변경 성격과 맞는지 확인합니다.
3. 카나리 확장 조건과 롤백 명령이 문서로 남아 있는지 점검합니다.

**예상 결과:**

- 커밋 규칙이 일정하면 체인지로그 자동화가 훨씬 매끄럽게 붙습니다.
- 릴리스 노트가 사용자 관점으로 바뀌면 영향 범위를 설명하기 쉬워집니다.
- 롤백 경로가 문서와 실습으로 검증된 팀일수록 배포 빈도를 높이기 쉽습니다.

### 실패 신호

- 버전 번호가 변경 크기와 무관하게 감으로 정해집니다.
- 카나리 단계 없이 바로 전체 트래픽에 노출합니다.
- 롤백 명령은 있지만 마지막으로 연습한 시점을 아무도 모릅니다.

## 이 코드에서 먼저 봐야 할 점

- 커밋 규칙이 자동화의 입력이 됩니다.
- 카나리는 되돌릴 수 있는 배포 결정을 가능하게 합니다.
- 롤백 속도는 릴리스 안전성의 지표입니다.
- 체인지로그는 개발자 내부 메모가 아니라 사용자용 기록이어야 합니다.

## 어디서 자주 헷갈릴까요?

첫 번째 오해는 버전 번호를 단순한 숫자로 보는 것입니다. 사용자는 MAJOR가 올랐을 때 호환성 변화가 있다고 기대하고, PATCH가 올라갔을 때 큰 동작 변화가 없다고 기대합니다. 이 약속이 흔들리면 버전에 대한 신뢰가 사라집니다.

두 번째 오해는 릴리스 노트를 팀 내부 용어로 쓰는 것입니다. 사용자는 어떤 버그가 줄었는지, 어떤 기능이 추가되었는지, 자신에게 영향이 무엇인지 알고 싶습니다. 구현 세부사항만 나열한 노트는 신뢰를 쌓지 못합니다.

세 번째 오해는 롤백 절차를 한 번도 연습하지 않은 채 “문서가 있으니 괜찮다”고 생각하는 것입니다. 실제 장애에서 처음 시도하는 롤백은 대개 늦고 어설픕니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 trunk-based 개발, 기능 플래그, 자동 버전 결정, 자동 체인지로그, 카나리 배포, 즉시 롤백을 하나의 세트로 봅니다. 이 흐름이 자리 잡으면 릴리스는 큰 행사보다 일상 작업에 가까워집니다.

시니어 엔지니어는 릴리스 속도만큼 회복 속도를 봅니다. 배포 빈도가 높아도 되돌리는 데 오래 걸리면 안전하다고 말하기 어렵습니다. 반대로 릴리스가 매우 잦아도 회복이 빠르면 전체 위험은 오히려 줄어듭니다.

## 체크리스트

- [ ] 브랜치 전략이 문서로 정리되어 있나요?
- [ ] 버전 선택이 자동화되어 있나요?
- [ ] 체인지로그가 사용자 언어로 작성되나요?
- [ ] 카나리 단계가 있나요?
- [ ] 1분 안팎에 롤백할 수 있나요?

## 연습 문제

1. 최근 커밋 열 개를 Conventional Commits 형식으로 다시 써 보세요.
2. 최근 릴리스 노트 하나를 사용자 관점 문장으로 다시 적어 보세요.
3. 한 장짜리 롤백 런북을 작성해 보세요.

## 정리

버전 관리와 릴리스는 개발의 끝이 아니라 신뢰의 인터페이스입니다. 커밋 규칙, SemVer, 자동 체인지로그, 카나리, 빠른 롤백이 함께 있을 때 릴리스는 두려운 이벤트가 아니라 반복 가능한 운영 절차가 됩니다.

다음 글에서는 이 신뢰를 글로 남기는 방법, 곧 문서화를 다룹니다. 코드가 설명하지 못하는 왜와 언제를 어떻게 기록해야 하는지 이어서 살펴보겠습니다.

<!-- toc:begin -->
- [소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [요구사항 이해하기](./02-understanding-requirements.md)
- [설계와 구현의 차이](./03-design-vs-implementation.md)
- [코드 리뷰](./04-code-review.md)
- [테스트 전략](./05-testing-strategy.md)
- **버전 관리와 릴리스 (현재 글)**
- 문서화 (예정)
- 협업 프로세스 (예정)
- 유지보수와 기술부채 (예정)
- 좋은 소프트웨어의 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [Google SRE Book — Release Engineering](https://sre.google/sre-book/release-engineering/)

Tags: Computer Science, SoftwareEngineering, Git, VersionControl, Release, SemVer
