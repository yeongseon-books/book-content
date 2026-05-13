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
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
seo_description: Pull Request를 branch, review, merge 흐름으로 설명하는 글입니다.
---

# Pull Request로 협업하기 - branch에서 review를 거쳐 main까지

branch가 개인 작업 공간이라면 Pull Request는 그 작업을 팀에 설명하는 자리입니다. 변경을 곧바로 합치는 대신, 왜 필요한지 말하고 검토를 받고 합의한 뒤 `main`에 반영하는 절차가 여기서 시작됩니다.

이 글은 Git/GitHub 101 시리즈의 일곱 번째 글입니다. 여기서는 feature branch에서 시작해 review를 거쳐 `main`으로 돌아오는 PR 한 사이클을 따라갑니다.

## 이 글에서 다룰 문제

> Pull Request는 단순한 merge 명령이 아니라, 내 branch를 `main`에 합치자고 제안하고 그 제안을 둘러싼 설명, 검토, 합의를 남기는 작업 공간입니다.

- Pull Request는 plain `git merge`와 무엇이 다를까요?
- branch를 만들고 commit한 뒤 PR을 열기까지의 순서는 어떻게 될까요?
- review comment에는 왜 같은 branch에 commit을 더하는 방식으로 답할까요?
- PR을 merge한 뒤 로컬 `main`은 어떻게 정리해야 할까요?
- PR이 너무 크면 왜 리뷰 품질이 급격히 떨어질까요?

## 왜 중요한가

혼자 작업할 때는 `git merge feature/x`로 끝낼 수 있습니다. 하지만 두 번째 사람이 들어오는 순간부터는 그 방식이 거칠어집니다. 무엇이 바뀌었는지, 왜 필요한지, 누가 동의했는지를 남길 자리가 없기 때문입니다.

PR은 이 빈자리를 메웁니다. 변경 설명, 파일 diff, 리뷰 댓글, 승인 기록이 모두 한 화면에 남고, 한 달 뒤 문제가 생겨도 PR 번호를 통해 맥락을 다시 복원할 수 있습니다. 또한 PR을 자주 열수록 큰 변경을 작은 단위로 자르는 습관도 자연스럽게 생깁니다.

## 핵심 그림

![Mental Model](../../../assets/git-github-101/07/07-01-mental-model.ko.png)

*Mental Model*

흐름은 단순합니다.

1. 로컬에서 `feature/...` branch를 만들고 commit을 쌓습니다.
2. GitHub에 push하면 같은 이름의 remote branch가 생깁니다.
3. 그 branch를 `main`에 합쳐 달라고 PR을 엽니다.
4. review와 추가 commit이 PR 안에서 이어집니다.
5. merge 후 `git pull`로 로컬 `main`을 따라잡습니다.

PR은 merge 자체보다, merge를 둘러싼 대화와 기록에 더 가깝습니다.

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

## 실무에서는 이렇게 본다

PR은 merge 도구라기보다 의사결정 기록 도구입니다. 왜 바꿨는지 긴 설명은 PR 본문에 남기고, CI 결과는 PR 화면에서 확인하며, draft PR로 진행 중 방향을 미리 공유하기도 합니다. 관련 issue를 `Closes #42`처럼 연결해 두면 merge 시 자동으로 닫히는 흐름도 만들 수 있습니다.

## 체크리스트

- [ ] 새 작업 전 `main`을 최신으로 맞췄습니다.
- [ ] `feature/`, `fix/`, `chore/` 같은 접두사로 branch 이름을 만들었습니다.
- [ ] 첫 push에 `-u origin <branch>`로 upstream을 설정했습니다.
- [ ] PR 본문에 변경 동기와 검증 방법을 적었습니다.
- [ ] review 의견에는 같은 branch에 commit을 더해 답했습니다.
- [ ] merge 후 `main`을 pull하고 사용한 branch를 삭제했습니다.

## 연습 문제

1. `feature/contact-section` branch를 만들고 작은 변경을 commit한 뒤 PR을 열어 보세요.
2. 설명이 비어 있는 PR과 설명이 있는 PR을 비교해 보고, 몇 달 뒤 자신이 다시 읽기 쉬운 쪽을 골라 보세요.

## 정리와 다음 글

PR은 branch를 합치자는 요청이며, 실제 merge는 그 요청의 마지막 단계입니다. branch에서 commit을 쌓고, GitHub에 push한 뒤, PR에서 review와 토론을 거쳐 `main`에 반영합니다. merge 후에는 로컬 `main`을 pull하고 작업 branch를 정리하는 것까지가 한 사이클입니다.

다음 글에서는 PR 본문에서 자주 보게 되는 `Closes #42`의 정체, 즉 GitHub Issue와 Project를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Git이란 무엇인가? 버전 관리의 시작](./01-what-is-git.md)
- [첫 commit 만들기 - init, status, add, commit](./02-first-commit.md)
- [변경 사항 확인하기 - status, diff, log로 읽기](./03-status-diff-log.md)
- [branch 기초 - 만들고 옮기고 비교하기](./04-branch-basics.md)
- [merge와 conflict 해결하기 - 두 줄기를 다시 합치기](./05-merge-and-conflict.md)
- [GitHub repository 만들기 - remote, push, pull 한 번에 익히기](./06-github-repository.md)
- **Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (현재 글)**
- Issue와 Project로 일감 관리하기 (예정)
- 좋은 commit message 쓰기 (예정)
- 실전 Git workflow 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- GitHub Docs, "About pull requests": <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests>
- GitHub Docs, "Creating a pull request": <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>
- GitHub Docs, "Reviewing changes in pull requests": <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests>
- GitHub Docs, "About protected branches": <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>
- Git docs, `git switch`: <https://git-scm.com/docs/git-switch>

Tags: github-pull-request, code-review, feature-branch, merge-commit, github-collaboration, pr-workflow
