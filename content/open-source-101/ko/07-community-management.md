---
series: open-source-101
episode: 7
title: "Open Source 101 (7/10): 커뮤니티 운영"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - Community
  - CodeOfConduct
  - Governance
  - Beginner
seo_description: 건강한 오픈소스 커뮤니티 유지를 위한 행동 강령, 기여 안내, 토론 공간 분리와 첫 기여자를 환영하는 운영 원칙을 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (7/10): 커뮤니티 운영

오픈소스 프로젝트는 코드만으로 유지되지 않습니다. 처음 저장소를 공개할 때는 기능과 문서가 가장 중요해 보이지만, 사용자가 늘고 기여자가 생기기 시작하면 커뮤니티 운영 방식이 프로젝트의 분위기와 지속 가능성을 결정합니다. 응답이 느리거나, 경계가 모호하거나, 신규 기여자를 방치하면 코드가 좋아도 사람은 떠납니다.

이 글은 오픈소스 101 시리즈의 7번째 글입니다.

여기서는 행동 강령, 기여 안내, 토론 공간, 응답 속도, 환영 메시지를 중심으로 건강한 오픈소스 커뮤니티를 유지하는 기본기를 정리하겠습니다.

![Open Source 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/07/07-01-the-smallest-structure-that-still-works.ko.png)
*Open Source 101 7장 흐름 개요*
> 커뮤니티 운영은 "좋은 사람만 모이면 자동으로 잘 된다"는 식이 아닙니다. **명확한 기준, 일관된 응답, 보이는 규칙**이 있어야 신뢰가 쌓입니다.

## 이 글에서 다룰 문제

- 프로젝트에 행동 강령이 왜 필요할까요?
- 기여 안내 문서는 단순 절차 문서가 아니라 어떤 역할을 할까요?
- 이슈와 토론 공간을 분리하면 무엇이 좋아질까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

프로젝트는 커뮤니티가 살아 있는 동안만 살아남습니다. 메인테이너가 아무리 뛰어나도 질문과 기여가 반복 가능하게 정리되지 않으면 병목이 생깁니다. 결국 커뮤니티 운영은 친절의 문제가 아니라 프로젝트 수명의 문제입니다.

실무에서도 비슷합니다. 내부 개발자 플랫폼이나 공용 라이브러리도 문서, 채널, 응답 규칙이 명확할수록 확산이 쉬워집니다. 오픈소스 커뮤니티 운영은 코드 밖의 일처럼 보일 수 있지만, 실제로는 유지보수 비용을 가장 크게 바꾸는 영역 가운데 하나입니다.

## 핵심 관점

커뮤니티가 굴러가는 최소 구조는 네 가지입니다:

```text
1. 경계 (행동 강령)        ← 허용되는/허용되지 않는 행동 명시
2. 안내 (CONTRIBUTING.md)  ← 어떻게 참여하는지 설명
3. 공간 (이슈 + Discussions) ← 대화 성격에 맞는 채널 분리
4. 환영 (첫 응답 + 자동화)  ← 신규 기여자 경험 보장
```

> 문서는 입구를 만들고, 응답은 그 입구가 실제로 열려 있음을 증명합니다. 둘 중 하나라도 빠지면 프로젝트는 닫힌 공간처럼 보이기 쉽습니다.

## 핵심 개념

### 거버넌스 모델 비교

커뮤니티 운영은 사람과 규칙의 문제이면서 동시에 의사결정 구조의 문제이기도 합니다.

| 모델 | 예시 | 장점 | 단점 | 적합한 규모 |
|---|---|---|---|---|
| BDFL (Benevolent Dictator) | Python (Guido), Linux (Linus) | 빠른 결정, 일관된 방향 | 한 명 의존, 승계 문제 | 초기~중형 |
| 메리토크라시 | Rust, Kubernetes | 기여도로 권한 획득, 투명 | 초기 혼란, 의견 충돌 | 중형~대형 |
| 위원회 (TSC) | Node.js | 분산 책임, 규모 대응 | 결정 느림, 절차 부담 | 대형 |
| 재단 | Apache, Eclipse | 법적 보호, 장기 안정성 | 행정 부담, 의사결정 느림 | 매우 대형 |

소규모 프로젝트는 BDFL이나 메리토크라시로 시작하는 편이 부담 없이 좋습니다. 프로젝트가 사용자 1만 명을 넘기기 시작하면 위원회 구조를 고려할 때입니다.

### 커뮤니티 건강 지표

| 지표 | 측정 방법 | 건강 기준 | 개선 방법 |
|---|---|---|---|
| 평균 첫 응답 시간 | 이슈 생성 → 첫 댓글까지 | 48시간 이내 | 자동 응답 봇, triage 루틴 |
| 활성 기여자 수 | 최근 90일 커밋 작성자 | 3명 이상 | good first issue 확대 |
| 이슈 해결률 | 닫힌 이슈 / 전체 이슈 | 70% 이상 | 정기 triage, stale bot |
| PR 머지율 | 머지된 PR / 전체 PR | 60% 이상 | 명확한 기여 가이드 |
| 문서 커버리지 | README, CHANGELOG, API docs | 모두 있음 | 문서 기여 이슈 라벨 |

## 행동 강령 설정

행동 강령은 문제가 생긴 뒤에 쓰는 문서가 아니라, 문제를 줄이기 위해 미리 두는 기준입니다.

### Contributor Covenant 2.1 핵심 조항

```markdown
# Code of Conduct

## 우리의 약속

나이, 신체 크기, 장애, 민족성, 성별 정체성과 표현, 경험 수준,
교육, 사회경제적 지위, 국적, 외모, 인종, 종교, 성적 정체성에
관계없이 모든 사람에게 괴롭힘 없는 경험을 제공합니다.

## 긍정적 환경을 만드는 행동

- 환영하고 포용적인 언어 사용
- 다른 관점과 경험 존중
- 건설적 비판을 우아하게 받아들임
- 커뮤니티에 가장 좋은 것에 집중
- 다른 커뮤니티 구성원에게 공감 표현

## 허용되지 않는 행동

- 성적 언어나 이미지 사용
- 트롤링, 모욕적/경멸적 댓글
- 개인적 또는 정치적 공격
- 공개적 또는 사적 괴롭힘
- 명시적 허가 없이 개인 정보 게시

## 신고 방법

위반 사항은 conduct@example.com으로 신고해 주세요.
모든 신고는 48시간 이내에 처리됩니다.
```

```bash
# Contributor Covenant 다운로드
curl -O https://www.contributor-covenant.org/version/2/1/code_of_conduct.md
mv code_of_conduct.md CODE_OF_CONDUCT.md
```

## CONTRIBUTING.md 작성 가이드

기여자가 어디서 시작해야 하는지 모르면 메인테이너에게 바로 질문이 몰립니다. 최소한 다음 네 섹션이 필요합니다.

```markdown
# Contributing to [Project Name]

## 시작하기 전에

[good first issue](링크) 라벨이 붙은 이슈부터 시작하는 것을 권장합니다.

## 개발 환경 설정

```bash
# 1. 포크 및 클론
gh repo fork owner/repo --clone
cd repo

# 2. 의존성 설치
pip install -e ".[dev]"

# 3. pre-commit 훅 설치 (코드 스타일 자동 검사)
pre-commit install

# 4. 테스트 실행 (초기 환경 확인)
pytest
```

## 기여 흐름

1. `good first issue` 라벨 이슈 선택
2. 이슈 댓글에 작업 의사 표시: "이 이슈를 작업해도 될까요?"
3. 포크 후 브랜치 생성: `fix/이슈번호-짧은-설명`
4. 변경 구현 + 테스트 추가
5. `pytest` 통과 확인
6. PR 제출 (템플릿 모든 항목 채우기)
7. 리뷰 피드백 대응

## 코드 스타일

- Formatter: `black .`
- Linter: `flake8 .`
- Type checker: `mypy src/`
- pre-commit으로 커밋 전 자동 검사

커밋 메시지: [Conventional Commits](https://www.conventionalcommits.org/) 형식
```
feat: 새 기능
fix: 버그 수정
docs: 문서 수정
test: 테스트 추가/수정
```

## 이슈 라벨 안내

| 라벨 | 의미 | 추천 대상 |
|---|---|---|
| `good first issue` | 첫 기여에 적합 | 처음 기여하는 분 |
| `help wanted` | 도움 필요 | 경험 있는 기여자 |
| `bug` | 버그 수정 | 모든 기여자 |
| `documentation` | 문서 개선 | 글쓰기 좋아하는 분 |

## PR 체크리스트

- [ ] `pytest` 통과
- [ ] 새 코드에 테스트 추가
- [ ] 문서 업데이트 (해당 시)
- [ ] 관련 이슈 연결 (`Closes #N`)
- [ ] Conventional Commits 형식 커밋 메시지
```

## 토론 공간 분리

모든 대화를 이슈에 몰아넣으면 버그와 아이디어와 질문이 섞입니다.

```text
이슈(Issues)        ← 버그 리포트, 기능 요청
GitHub Discussions  ← 질문, 아이디어, 사용 사례 공유
PR Comments         ← 코드 리뷰
Discord/Slack       ← 실시간 대화 (규모 클 때)
```

### GitHub Discussions 카테고리 설정

```text
Q&A          ← 사용 방법 질문 (답변 표시 기능 활용)
Ideas        ← 기능 아이디어 제안
Show & Tell  ← 프로젝트 활용 사례 공유
General      ← 일반 대화
Announcements ← 릴리스, 이벤트 공지 (메인테이너 전용)
```

## 신규 기여자 환영 자동화

```yaml
# .github/workflows/welcome.yml
name: Welcome

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  welcome:
    runs-on: ubuntu-latest
    steps:
    # 첫 이슈 환영
    - uses: actions/first-interaction@v1
      with:
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        issue-message: |
          안녕하세요 @${{ github.event.sender.login }}님!
          첫 이슈를 열어 주셔서 감사합니다.

          프로젝트에 기여하고 싶으시다면 [CONTRIBUTING.md](CONTRIBUTING.md)를 먼저 읽어 보세요.
          `good first issue` 라벨 이슈도 확인해 보세요: [링크](https://github.com/${{ github.repository }}/issues?q=label%3A%22good+first+issue%22)

        pr-message: |
          안녕하세요 @${{ github.event.sender.login }}님!
          첫 PR을 제출해 주셔서 감사합니다.

          리뷰는 보통 48시간 이내에 시작됩니다.
          기다리시는 동안 다른 PR에 리뷰 코멘트를 달아 보시는 것도 좋습니다!
```

## 기여자 활동 가시화

```yaml
# .github/workflows/contributors.yml
name: Update Contributors

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # 매주 일요일

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: minicli/action-contributors@v3
      with:
        repo: '${{ github.repository }}'
        output: CONTRIBUTORS.md
        template: 'table'
    - run: |
        git config user.name github-actions
        git config user.email github-actions@github.com
        git add CONTRIBUTORS.md
        git diff --quiet || git commit -m "docs: update contributors list"
        git push
```

## 독성 참여자 대응

커뮤니티가 커지면 공격적이거나 반복적으로 규칙을 어기는 참여자가 나타납니다.

### 단계별 대응 절차

**1단계: 행동 강령 조항 인용 경고**

```markdown
@username, 이 댓글은 Code of Conduct 2.1절 "건설적 비판" 기준에
어긋납니다. 구체적 기술 근거를 들어 다시 작성해 주시기 바랍니다.

관련 조항: https://github.com/owner/repo/blob/main/CODE_OF_CONDUCT.md#standards
```

**2단계: 임시 참여 제한**

```bash
# GitHub Org 설정
# Settings → Moderation → Interaction limits
# 옵션: 7 days / 30 days / indefinite
```

**3단계: 영구 차단 및 공개 기록**

```markdown
## Moderation Log

이 파일은 커뮤니티 투명성을 위해 모더레이션 결정을 기록합니다.

| 날짜 | 조치 | 사유 | 관련 이슈 |
|---|---|---|---|
| 2026-05-20 | 영구 차단 | 2차 경고 후 반복 괴롭힘 | #123, #456 |
```

독성 참여자를 방치하면 건강한 기여자가 떠납니다. 커뮤니티 안전은 코드 품질만큼 메인테이너의 책임입니다.

## 직접 따라해 보기: 커뮤니티 기본 문서 만들기

### 1단계 — 행동 강령 두기

```bash
curl -sL https://www.contributor-covenant.org/version/2/1/code_of_conduct.md \
  > CODE_OF_CONDUCT.md
```

### 2단계 — 기여 안내 문서 쓰기

```bash
# 최소 구조 생성
cat > CONTRIBUTING.md << 'EOF'
# Contributing

## 시작하기

1. `good first issue` 라벨 이슈 선택
2. 이슈 댓글에 "이 이슈를 작업해도 될까요?" 작성
3. Fork → Branch → Implement → Test → PR

## 개발 환경

```bash
pip install -e ".[dev]"
pre-commit install
pytest
```

## 커밋 형식

Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`
EOF
```

### 3단계 — 이슈 템플릿 준비하기

```bash
mkdir -p .github/ISSUE_TEMPLATE
```

### 4단계 — Discussions 활성화

GitHub 저장소 Settings → Features → Discussions 체크

### 5단계 — 첫 기여자 환영 자동화

```bash
mkdir -p .github/workflows
# welcome.yml 생성 (위 예시 참조)
```

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 행동 강령 없음 | 갈등 발생 시 판단 기준 없음 | Contributor Covenant 채택, 신고 채널 명시 |
| 이슈에 모든 대화 혼재 | 사용 방법 질문과 버그 리포트가 섞임 | Discussions로 질문 유도, 이슈는 버그/기능 전용 |
| 신규 기여자 응답 지연 | 첫 PR에 2주 이상 무응답 | 48시간 첫 응답 목표, 자동화 환영 메시지 |
| 기여 감사 생략 | 머지 후 "LGTM" 한 줄만 | "훌륭한 기여입니다! 덕분에 X 문제가 해결됩니다" |
| 암묵지 의존 | 규칙이 메인테이너 머릿속에만 있음 | CONTRIBUTING.md에 모든 규칙 문서화 |

## 실무에서는 이렇게 생각한다

개발자 관계 팀이나 플랫폼 팀이 내부 커뮤니티를 운영할 때도 비슷한 원칙을 씁니다. 어디에 질문할지, 어떤 정보가 있어야 답할 수 있는지, 어떤 행동은 허용되지 않는지 미리 보이면 채널 품질이 안정됩니다.

시니어 엔지니어는 커뮤니티를 감정 노동으로만 보지 않습니다. 응답 속도는 신뢰를 만들고, 명시적 규칙은 안전을 만들며, 인정은 참여 지속성을 만듭니다.

**커뮤니티 건강 지표 모니터링**:

```bash
# 이슈 응답 통계
gh issue list --state all --json state,createdAt,comments \
  | jq '[group_by(.state) | .[] | {state: .[0].state, count: length}]'

# 최근 30일 활동
gh api repos/:owner/:repo/stats/commit_activity \
  | jq '.[-4:] | .[] | {week: .week, commits: .total}'

# 활성 기여자 (최근 90일)
gh api repos/:owner/:repo/contributors \
  | jq '[.[] | select(.contributions > 1)] | length'
```

## 운영 체크리스트

- [ ] 행동 강령을 두었습니다.
- [ ] 기여 안내 문서를 작성했습니다.
- [ ] 이슈 템플릿을 준비했습니다.
- [ ] 토론 공간 또는 질문 채널 분리 방식을 정했습니다.
- [ ] 신규 기여자 환영 자동화가 있습니다.

## 연습 문제

1. Contributor Covenant가 무엇인지 한 문장으로 적어 보세요.
2. `good first issue`와 `help wanted`의 차이를 한 문장으로 적어 보세요.
3. 환영 메시지가 왜 중요한지 한 문장으로 적어 보세요.

## 정리

이번 글에서는 커뮤니티 운영을 친절의 문제가 아니라 프로젝트 지속성의 문제로 정리했습니다. 규칙, 가이드, 응답, 환영이 함께 있어야 신규 기여자가 실제 구성원으로 들어올 수 있습니다.

다음 글에서는 메인테이너의 역할을 다룹니다. 커뮤니티가 생기면 결국 누군가는 우선순위를 정하고, 리뷰하고, 경계를 지켜야 하기 때문입니다.

## 처음 질문으로 돌아가기

- **프로젝트에 행동 강령이 왜 필요할까요?**
  - 행동 강령은 허용되는 행동과 허용되지 않는 행동의 경계를 문서로 명시합니다. 문제가 생겼을 때 "이 행동은 규칙 X에 위배됩니다"라고 말할 수 있어야 메인테이너가 감정 소모 없이 조치를 취할 수 있습니다. 경계가 없으면 갈등이 생겼을 때 모든 판단이 메인테이너의 개인 감정으로 귀결됩니다.
- **기여 안내 문서는 단순 절차 문서가 아니라 어떤 역할을 할까요?**
  - CONTRIBUTING.md는 신규 기여자가 스스로 준비 상태를 확인할 수 있는 체크리스트입니다. 메인테이너는 같은 질문에 반복 답변하는 시간을 줄이고, 기여자는 불확실성 없이 첫 PR을 시작할 수 있습니다. 좋은 문서는 메인테이너 없이도 기여자가 다음 단계를 알 수 있게 해 줍니다.
- **이슈와 토론 공간을 분리하면 무엇이 좋아질까요?**
  - 이슈는 버그/기능의 추적 가능한 단위로 유지되고, 사용 방법 질문은 Discussions에서 자유롭게 논의됩니다. 메인테이너는 이슈 탭을 보면 현재 해결해야 할 실제 문제만 볼 수 있고, 기여자는 적합한 채널에서 더 빠른 응답을 받습니다.

<!-- toc:end -->

## 참고 자료

- [Contributor Covenant](https://www.contributor-covenant.org/)
- [Open Source Guides — Building Communities](https://opensource.guide/building-community/)
- [GitHub Discussions](https://docs.github.com/en/discussions)
- [first-interaction action](https://github.com/actions/first-interaction)
- [contributor-covenant 저장소](https://github.com/contributor-covenant/contributor_covenant)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, Community, CodeOfConduct, Governance, Beginner
