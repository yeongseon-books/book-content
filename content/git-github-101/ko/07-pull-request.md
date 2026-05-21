---
episode: 7
language: ko
last_reviewed: '2026-05-12'
series: git-github-101
status: publish-ready
tags:
- github-pull-request
- code-review
- feature-branch
- merge-commit
- github-collaboration
- pr-workflow
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Git & GitHub 101 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지"
seo_description: Pull Request를 branch, review, merge 흐름으로 설명하는 글입니다.
---

# Git & GitHub 101 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지

branch가 개인 작업 공간이라면 Pull Request는 그 작업을 팀에 설명하는 자리입니다. 변경을 곧바로 합치는 대신, 왜 필요한지 말하고 검토를 받고 합의한 뒤 `main`에 반영하는 절차가 여기서 시작됩니다.

이 글은 Git/GitHub 101 시리즈의 일곱 번째 글입니다. 여기서는 feature branch에서 시작해 review를 거쳐 `main`으로 돌아오는 PR 한 사이클을 따라갑니다.


![Git & GitHub 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/git-github-101/07/07-01-mental-model.ko.png)
*Git & GitHub 101 7장 흐름 개요*

## 먼저 던지는 질문

- Pull Request는 plain `git merge`와 무엇이 다를까요?
- branch를 만들고 commit한 뒤 PR을 열기까지의 순서는 어떻게 될까요?
- review comment에는 왜 같은 branch에 commit을 더하는 방식으로 답할까요?

## 왜 중요한가

혼자 작업할 때는 `git merge feature/x`로 끝낼 수 있습니다. 하지만 두 번째 사람이 들어오는 순간부터는 그 방식이 금방 한계를 드러냅니다. 무엇이 바뀌었는지, 왜 바뀌었는지, 어떤 기준으로 통과시켰는지, 누가 동의했는지를 남길 자리가 없기 때문입니다.

PR은 이 빈자리를 메우는 협업 경계입니다. 변경 설명, 파일 diff, 리뷰 댓글, 승인 기록, CI 결과가 모두 한 화면에 남고, 몇 주 뒤 문제가 생겨도 PR 번호를 기준으로 의사결정 맥락을 복원할 수 있습니다. 특히 팀 규모가 커질수록 PR은 단순 merge 버튼이 아니라 변경 위험을 낮추는 운영 장치가 됩니다.

실무에서 PR이 중요한 이유는 세 가지로 요약할 수 있습니다.

- 변경 품질: 리뷰어가 로직, 경계 조건, 네이밍, 테스트 누락을 조기에 잡습니다.
- 운영 안정성: CI가 PR 단위로 자동 검증을 수행해 `main` 유입 전에 실패를 차단합니다.
- 지식 공유: 한 사람의 로컬 맥락이 팀의 문서화된 맥락으로 전환됩니다.

## 핵심 그림

흐름은 단순해 보이지만 각 단계의 목적이 다릅니다.

1. 로컬에서 `feature/...` branch를 만들고 commit을 쌓습니다. (변경 생성)
2. GitHub에 push하면 같은 이름의 remote branch가 생깁니다. (변경 공유)
3. 그 branch를 `main`에 합쳐 달라고 PR을 엽니다. (검토 요청)
4. review와 추가 commit이 PR 안에서 이어집니다. (품질 보정)
5. CI와 리뷰가 통과되면 merge합니다. (통합 승인)
6. merge 후 `git pull`로 로컬 `main`을 따라잡고 작업 branch를 정리합니다. (상태 동기화)

PR은 merge 자체보다, merge를 둘러싼 대화와 검증의 구조에 가깝습니다.

## 핵심 개념

| 용어 | 뜻 |
| --- | --- |
| base branch | PR이 합쳐질 대상 branch, 보통 `main` |
| compare branch | 변경이 들어 있는 branch |
| draft PR | 아직 리뷰 준비는 안 됐지만 진행 상황을 공유하는 PR |
| review | Approve, Request changes, Comment 중 하나를 남기는 검토 |
| merge commit | PR merge 시 GitHub가 만드는 두 부모 commit |
| squash merge | PR의 여러 commit을 하나로 합쳐 base에 올리는 방식 |
| rebase merge | PR commit을 base 위에 다시 쌓는 방식 |

여기서 중요한 점은 `base branch`와 `compare branch`를 분리해서 생각하는 습관입니다. `base`는 팀의 기준선이며, 보호 정책과 CI 필수 규칙이 걸리는 지점입니다. 반대로 `compare`는 실험과 수정이 반복되는 작업선입니다. PR은 이 둘 사이의 차이를 안전하게 줄여 가는 절차입니다.

또한 draft PR은 "미완성 PR"이 아니라 "조기 피드백 채널"입니다. 구현 중이라도 방향성이나 설계 선택이 맞는지 빠르게 확인할 수 있어, 뒤늦은 대규모 수정 비용을 줄여 줍니다.

## 전후 비교

PR 없이 branch만 만들어 두면 이런 상태가 됩니다.

```text
$ git switch -c feature/release-notes
$ git commit -am "Draft release notes"
$ # a few days pass
$ git log --oneline main..feature/release-notes
3c4d5e6 Draft release notes
$ # nobody else has seen the change yet
```

PR을 열면 같은 branch라도 설명과 리뷰가 붙습니다.

```text
$ git push -u origin feature/release-notes
$ # open a PR on GitHub, a teammate leaves a one-line review
$ git commit -am "Tweak release checklist heading"
$ git push
$ # click "Merge pull request" on GitHub
$ git switch main
$ git pull
```

## 단계별 실습

### 1. `main`을 먼저 동기화하기

```text
$ git switch main
Already on 'main'
Your branch is up to date with 'origin/main'.
$ git pull
Already up to date.
```

### 2. feature branch 만들기

```text
$ git switch -c feature/release-notes
Switched to a new branch 'feature/release-notes'
$ git status
On branch feature/release-notes
nothing to commit, working tree clean
```

### 3. 첫 commit 만들기

```text
$ printf '\n## Release checklist\n\n- [ ] Tag version\n- [ ] Update CHANGELOG\n' >> notes.md
$ git add notes.md
$ git commit -m "Add release checklist"
[feature/release-notes 3c4d5e6] Add release checklist
 1 file changed, 5 insertions(+)
```

### 4. branch를 GitHub에 push하기

```text
$ git push -u origin feature/release-notes
Enumerating objects: 5, done.
...
remote: Create a pull request for 'feature/release-notes' on GitHub by visiting:
remote:      https://github.com/<your-id>/vacation-notes/pull/new/feature/release-notes
To https://github.com/<your-id>/vacation-notes.git
 * [new branch]      feature/release-notes -> feature/release-notes
Branch 'feature/release-notes' set up to track remote branch 'feature/release-notes' from 'origin'.
```

### 5. GitHub에서 PR 열기

- Title: `Add release checklist to notes`
- Description: 변경 동기, 검증 방법, 영향 범위를 짧게 적습니다.
- Reviewers: 동료 한 명을 지정합니다.

여기서 본문을 비워 두지 않는 것이 중요합니다. 리뷰어는 diff를 보기 전에 "왜 이 변경이 필요한가"를 먼저 이해해야 하고, 운영자 관점에서는 "어떻게 검증했는가"가 핵심입니다. 최소한 다음 네 줄은 포함하는 편이 좋습니다.

```text
## 배경
로그인 세션 갱신 누락으로 401 재로그인이 자주 발생했습니다.

## 변경 내용
- 세션 만료 5분 전 refresh 호출 로직 추가
- 실패 시 재시도 1회 추가

## 검증
- pytest tests/test_auth.py -q
- staging에서 30분 세션 유지 수동 확인

## 영향 범위
- app/auth.py, tests/test_auth.py
```

PR 번호가 생기면 그 번호가 이후 이 변경의 대표 식별자가 됩니다.

### 6. review comment에 추가 commit으로 답하기

```text
$ git switch feature/release-notes
$ sed -i 's/## Release checklist/## Release checklist (per version)/' notes.md
$ git add notes.md
$ git commit -m "Tweak release checklist heading"
[feature/release-notes 4d5e6f7] Tweak release checklist heading
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git push
Enumerating objects: 5, done.
...
To https://github.com/<your-id>/vacation-notes.git
   3c4d5e6..4d5e6f7  feature/release-notes -> feature/release-notes
```

같은 branch에 commit을 더하면 PR이 자동으로 갱신됩니다.

### 7. PR merge하기

```text
Merge pull request #1 from <your-id>/feature/release-notes

Add release checklist to notes
```

GitHub의 기본 merge commit 형식입니다. merge 후 remote branch 삭제 버튼도 함께 뜹니다.

merge 버튼을 누르기 전에 확인할 기준도 고정해 두는 편이 좋습니다.

- Required checks가 모두 Pass인지 확인합니다.
- Request changes 상태가 남아 있지 않은지 확인합니다.
- 최신 `main`과 충돌이 없는지 확인합니다.
- 배포 영향이 있는 경우 롤백 경로를 PR 본문에 남깁니다.

### 8. 로컬 정리하기

```text
$ git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
$ git pull
remote: Enumerating objects: 1, done.
...
Updating 7e8f9a0..5e6f7a8
Fast-forward
 notes.md | 5 +++++
 1 file changed, 5 insertions(+)
$ git branch -d feature/release-notes
Deleted branch feature/release-notes (was 4d5e6f7).
```

## 자주 하는 실수

- `main`에 직접 commit하고 branch protection에 막히는 경우가 많습니다.
- PR이 너무 크면 리뷰어가 세부 diff를 읽지 못합니다.
- review comment를 받고 새 branch를 만드는 것은 흐름을 불필요하게 복잡하게 만듭니다.
- merge 후 로컬 `main`을 pull하지 않은 채 다음 작업을 시작하면 충돌 가능성이 커집니다.
- merge commit 메시지를 임의로 크게 바꾸면 검색성과 일관성이 떨어질 수 있습니다.

추가로 자주 보이는 실패 패턴은 다음과 같습니다.

- "한 번에 끝내겠다"는 생각으로 수백 줄 PR을 올려 리뷰가 형식화됩니다.
- 리뷰어 없이 self-merge를 반복해 팀 코드 스타일이 분기됩니다.
- CI 실패를 "나중에 고치자"고 넘겨 flaky가 누적됩니다.
- 관련 Issue 링크를 남기지 않아 변경 목적 추적이 어려워집니다.

이 네 가지는 기술 문제가 아니라 운영 습관 문제라서, 팀 규칙으로 미리 막는 것이 가장 효과적입니다.

## PR 워크플로우를 운영 절차로 고정하기

branch → push → PR → review → merge를 매번 비슷한 방식으로 수행하면 협업 비용이 급격히 줄어듭니다. 아래는 가장 많이 쓰는 표준 절차입니다.

1. `main` 동기화 후 feature branch 생성
2. 작은 commit 단위로 구현
3. remote push + PR 생성
4. 리뷰 반영 commit 추가
5. CI 통과 + 승인 후 merge
6. 로컬/원격 branch 정리

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/pr-template

# 작업 후
git add .
git commit -m "docs(pr): add pull request template"
git push -u origin feature/pr-template

# PR 생성 후 리뷰 반영
git add .
git commit -m "docs(pr): clarify validation checklist"
git push

# merge 후 로컬 정리
git switch main
git pull --ff-only origin main
git branch -d feature/pr-template
```

이 흐름의 핵심은 "리뷰 반영도 같은 branch에서 이어 간다"는 점입니다. 그래야 PR 대화와 commit 이력이 하나의 맥락으로 유지됩니다.

## 코드 리뷰 품질을 높이는 기준

리뷰는 "맞다/틀리다" 판정이 아니라 변경 위험을 줄이는 공동 점검입니다. 리뷰 품질을 안정적으로 유지하려면 체크 기준을 명시적으로 분리하는 편이 좋습니다.

### 작성자 기준

- PR 크기를 줄입니다. 한 PR에 한 가지 목적만 담습니다.
- 제목은 "무엇"보다 "왜"가 드러나게 씁니다.
- 본문에 재현 방법과 검증 명령을 포함합니다.
- 스크린샷, 로그, before/after를 필요 시 첨부합니다.

### 리뷰어 기준

- 설계 의도와 실제 구현이 일치하는지 먼저 확인합니다.
- 경계 조건(빈 값, 실패 경로, 타임아웃)을 집중 점검합니다.
- 테스트가 변경을 충분히 덮는지 확인합니다.
- 모호한 코멘트 대신 제안 가능한 대안을 함께 남깁니다.

### 대화 기준

- 사실과 의견을 구분해 코멘트합니다.
- "필수 수정"과 "선택 제안"을 라벨로 나눕니다.
- 합의된 결정은 PR 대화에 문장으로 남깁니다.

이 기준을 적용하면 리뷰 속도는 약간 느려질 수 있지만, 배포 후 되돌림 비용은 크게 줄어듭니다.

## PR 템플릿으로 품질 하한선 만들기

팀마다 글쓰기 습관이 다르면 PR 품질 편차가 커집니다. 이때 `.github/pull_request_template.md`를 두면 모든 PR에 최소 공통 문맥을 강제할 수 있습니다.

예시 템플릿은 다음과 같습니다.

```md
## 배경
- 어떤 문제를 해결하나요?

## 변경 내용
- 핵심 변경 1
- 핵심 변경 2

## 검증 방법
- [ ] 단위 테스트 통과
- [ ] 수동 시나리오 확인

## 영향 범위
- 사용자 영향: 없음/있음 (설명)
- 운영 영향: 마이그레이션 필요/불필요

## 관련 이슈
- Closes #123
```

템플릿의 목적은 문장을 길게 쓰게 만드는 것이 아니라, 리뷰에 필요한 정보를 빠뜨리지 않게 만드는 것입니다. 특히 "검증 방법"과 "영향 범위" 항목은 CI 결과 해석과 배포 판단에 직접 연결됩니다.

## Draft PR을 언제 쓰는가

Draft PR은 구현 중간 상태를 공유하는 도구입니다. 다음 조건 중 하나에 해당하면 초반부터 draft로 열어 두는 편이 좋습니다.

- 설계 선택지(A/B) 중 팀 합의가 필요한 경우
- 파일 변경 범위가 넓어 조기 피드백이 필요한 경우
- 외부 API 변경처럼 리스크가 큰 경우

Draft 단계에서는 "완성도"보다 "방향성"을 검토합니다. 기능이 안정되면 `Ready for review`로 전환해 정식 승인 절차로 들어갑니다. 이 전환 시점에 체크할 항목은 아래와 같습니다.

- TODO 주석과 임시 코드 제거
- 테스트/린트 통과
- PR 본문의 검증 절차 최신화
- 리뷰어가 재현 가능한 상태인지 확인

즉 draft는 느슨한 상태가 아니라, 리뷰 단계별 기대치를 분리하는 장치입니다.

## Squash merge vs Merge commit

두 방식 중 정답은 없고 팀의 추적 방식에 따라 선택이 달라집니다. 핵심 차이는 "히스토리를 어디서 읽을 것인가"입니다.

| 항목 | Merge commit | Squash merge |
| --- | --- | --- |
| 히스토리 형태 | PR의 개별 commit 유지 | PR당 1 commit으로 압축 |
| 장점 | 작업 과정 추적이 쉽습니다 | `main` 히스토리가 짧고 깔끔합니다 |
| 단점 | `main` 로그가 길어질 수 있습니다 | 중간 의사결정 commit이 사라집니다 |
| 적합한 팀 | commit 단위 분석을 자주 하는 팀 | 릴리스 노트/체인지로그 중심 팀 |

운영 팁은 단순합니다.

- PR이 충분히 작고 commit 메시지 품질이 좋다면 merge commit도 읽기 쉽습니다.
- PR 내부 commit이 "fix typo"처럼 산만하다면 squash merge가 더 유리합니다.
- 어떤 방식을 쓰든 CI 통과와 승인 조건이 우선이며, merge 방식은 그 다음 결정입니다.

## CI를 PR에 통합하는 방법

PR 협업에서 CI는 "자동 리뷰어" 역할을 합니다. 사람이 보기 전에 기계가 실패를 먼저 걸러 주면 리뷰 집중도가 크게 올라갑니다.

보통 PR CI는 다음 순서로 구성합니다.

1. 정적 검사(lint, format check)
2. 단위 테스트
3. 빌드/패키징
4. 필요 시 보안 스캔 또는 스모크 테스트

GitHub Actions 예시는 다음과 같습니다.

```yaml
name: pr-check

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q
```

이 워크플로우를 branch protection과 연결하면 "체크가 Pass일 때만 merge 가능"한 상태를 만들 수 있습니다. 결국 PR 품질은 개인의 성실함보다 자동화된 안전장치 유무에 더 크게 좌우됩니다.

## 실무에서는 이렇게 본다

PR은 merge 도구라기보다 의사결정 기록 도구입니다. 왜 바꿨는지 긴 설명은 PR 본문에 남기고, CI 결과는 PR 화면에서 확인하며, draft PR로 진행 중 방향을 미리 공유합니다. 관련 issue를 `Closes #42`처럼 연결해 두면 merge 시 자동으로 닫히는 흐름도 만들 수 있습니다.

여기에 한 가지를 더하면 실무 품질이 크게 올라갑니다. "리뷰 가능 상태"를 명시적으로 정의하는 것입니다. 예를 들어 "테스트 통과 + 템플릿 작성 + 변경 범위 400줄 이하"를 팀 규칙으로 두면 리뷰어의 피로도가 줄고 승인 속도가 빨라집니다.

## 실무에서는 이렇게 본다

PR은 merge 도구라기보다 의사결정 기록 도구입니다. 왜 바꿨는지 긴 설명은 PR 본문에 남기고, CI 결과는 PR 화면에서 확인하며, draft PR로 진행 중 방향을 미리 공유하기도 합니다. 관련 issue를 `Closes #42`처럼 연결해 두면 merge 시 자동으로 닫히는 흐름도 만들 수 있습니다.

## 체크리스트

- [ ] 새 작업 전 `main`을 최신으로 맞췄습니다.
- [ ] `feature/`, `fix/`, `chore/` 같은 접두사로 branch 이름을 만들었습니다.
- [ ] 첫 push에 `-u origin <branch>`로 upstream을 설정했습니다.
- [ ] PR 본문에 변경 동기와 검증 방법을 적었습니다.
- [ ] 필요하면 draft PR로 먼저 열고, 준비되면 ready for review로 전환했습니다.
- [ ] review 의견에는 같은 branch에 commit을 더해 답했습니다.
- [ ] merge 방식(merge commit/squash)을 팀 기준에 맞게 선택했습니다.
- [ ] Required checks가 모두 Pass된 뒤 merge했습니다.
- [ ] merge 후 `main`을 pull하고 사용한 branch를 삭제했습니다.

## 연습 문제

1. `feature/contact-section` branch를 만들고 작은 변경을 commit한 뒤 PR을 열어 보세요.
2. 설명이 비어 있는 PR과 설명이 있는 PR을 비교해 보고, 몇 달 뒤 자신이 다시 읽기 쉬운 쪽을 골라 보세요.

## 정리와 다음 글

PR은 branch를 합치자는 요청이며, 실제 merge는 그 요청의 마지막 단계입니다. branch에서 commit을 쌓고, GitHub에 push한 뒤, PR에서 review와 토론, CI 검증을 거쳐 `main`에 반영합니다. 이때 PR 템플릿, draft 전환, merge 방식 선택, branch protection을 함께 운용하면 협업 품질이 안정적으로 올라갑니다. merge 후에는 로컬 `main`을 pull하고 작업 branch를 정리하는 것까지가 한 사이클입니다.

다음 글에서는 PR 본문에서 자주 보게 되는 `Closes #42`의 정체, 즉 GitHub Issue와 Project를 다룹니다.


## 실전 CLI 시나리오

아래 예시는 feature branch에서 작업하고 main으로 합치는 가장 보편적인 흐름입니다. 핵심은 "작업 단위를 작게 자르고, 상태를 자주 확인하며, 충돌은 빠르게 해결한다"는 운영 원칙입니다.

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/auth-session
git status
git add app/auth.py tests/test_auth.py
git commit -m "feat(auth): add session refresh flow"
git push -u origin feature/auth-session
```

`git pull --ff-only`를 앞단에 두면 로컬 main이 원격과 어긋난 상태에서 오래된 기반으로 branch를 파는 실수를 줄일 수 있습니다. 또한 `git status`를 commit 직전에 반복하면 불필요한 파일이 함께 올라가는 문제를 예방할 수 있습니다.

## 브랜치 전략을 선택하는 기준

실무에서는 전략 자체보다 "팀이 어떤 리듬으로 릴리스를 내는가"가 더 중요합니다. 아래 표는 초급 팀이 자주 비교하는 세 가지 전략입니다.

| 전략 | 특징 | 적합한 상황 | 주의할 점 |
| --- | --- | --- | --- |
| Trunk-based | 짧은 branch 수명, 빠른 머지 | 배포 빈도가 높고 테스트 자동화가 있는 팀 | 작은 PR 규율이 없으면 main이 불안정해집니다 |
| GitHub Flow | main + feature branch + PR | SaaS, 웹 서비스처럼 연속 배포 중심 | 환경별 배포 정책을 별도로 정의해야 합니다 |
| Git Flow | develop/release/hotfix 등 다중 branch | 릴리스 윈도우가 고정된 제품형 조직 | 브랜치가 많아 운영 복잡도가 커집니다 |

입문 단계에서는 GitHub Flow로 시작하는 편이 안전합니다. 규칙이 단순하고 Pull Request 중심의 협업 도구와 잘 맞기 때문입니다. 이후 릴리스 요구가 복잡해지면 release branch를 추가하는 방식으로 확장하면 됩니다. 중요한 것은 전략 이름보다 "PR 단위 검증이 자동화되어 있는가"입니다.

## 충돌 해결 절차를 표준화하기

충돌은 실패가 아니라 동시 작업의 자연스러운 신호입니다. 중요한 것은 해결 순서와 검증 절차를 팀 공통 규칙으로 맞추는 일입니다.

1. 충돌 파일을 확인하고, 어느 변경이 도메인 규칙에 맞는지 먼저 결정합니다.
2. 마커(`<<<<<<<`, `=======`, `>>>>>>>`)를 제거하면서 의도한 최종 코드를 남깁니다.
3. 단위 테스트와 정적 검사를 실행해 문법/동작 회귀를 확인합니다.
4. 충돌 해결 commit을 별도로 남겨 리뷰어가 판단 근거를 읽을 수 있게 합니다.

```bash
git fetch origin
git switch feature/auth-session
git merge origin/main
# 충돌 해결 후
git add app/auth.py tests/test_auth.py
git commit -m "merge: resolve auth-session conflicts with main"
pytest -q
git push
```

`merge` 대신 `rebase`를 쓰는 팀이라면 마지막 히스토리 모양이 달라질 뿐, 충돌을 해결하고 검증해야 한다는 원칙은 같습니다. 충돌 직후 테스트를 생략하면 "머지는 됐지만 동작은 깨진" 상태가 만들어지므로 반드시 자동 검증을 붙여야 합니다.

## 리뷰 품질을 올리는 운영 팁

- PR 설명에는 "무엇을 바꿨는가"보다 "왜 이 선택을 했는가"를 먼저 적는 편이 좋습니다.
- 파일 수가 많다면 기능 단위로 commit을 분리해 reviewer가 논리 흐름을 추적하기 쉽게 만듭니다.
- `git range-diff`를 사용하면 리뷰 피드백 반영 전후의 commit 변경을 선명하게 비교할 수 있습니다.
- 긴급 수정(hotfix)은 main으로 직접 넣는 대신 작은 PR로 남겨 이력과 승인 기록을 보존합니다.
- 리뷰어가 반복 질문하는 항목은 PR 템플릿과 CI 체크로 올려 사람 의존도를 낮춥니다.

이 네 가지를 지키면 Git 명령을 많이 아는 것보다 훨씬 빠르게 협업 안정성이 올라갑니다.

## 처음 질문으로 돌아가기

- **Pull Request는 plain `git merge`와 무엇이 다를까요?**
  - `git merge`는 통합 동작 자체이고, PR은 그 전에 필요한 설명, 리뷰, 승인, CI 검증까지 포함한 협업 절차입니다.
- **branch를 만들고 commit한 뒤 PR을 열기까지의 순서는 어떻게 될까요?**
  - `main` 동기화 → feature branch 생성 → commit → push → PR 생성 순서로 진행하고, PR 본문에 배경/검증/영향을 명시합니다.
- **review comment에는 왜 같은 branch에 commit을 더하는 방식으로 답할까요?**
  - 그래야 PR 대화와 코드 변경 이력이 한 곳에 남아, 리뷰 맥락과 최종 결과를 함께 추적할 수 있기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- [Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기](./06-github-repository.md)
- **Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (현재 글)**
- Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 (예정)
- 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 (예정)
- 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 (예정)

<!-- toc:end -->

## 참고 자료

- [GitHub Docs — About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) — PR이 단순 merge가 아니라 설명·검토·합의의 공간이라는 개념을 공식적으로 정리합니다.
- [GitHub Docs — Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) — branch push 뒤 PR을 열고 제목·본문을 채우는 실제 절차와 직접 연결됩니다.
- [GitHub Docs — Reviewing changes in pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests) — review comment, approve, request changes 흐름을 보강합니다.
- [GitHub Docs — About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#draft-pull-requests) — draft PR이 언제 쓰이고 ready for review로 언제 넘기는지 확인할 수 있습니다.
- [GitHub Docs — About merge methods on GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github) — merge commit, squash merge, rebase merge 차이를 PR 기준으로 설명합니다.
- [GitHub Docs — About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) — `main` 직접 commit이 막히는 이유와 branch protection 맥락을 보완합니다.
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/git-github-101/ko/07-pull-request)

Tags: github-pull-request, code-review, feature-branch, merge-commit, github-collaboration, pr-workflow
