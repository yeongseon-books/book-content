---
title: "바이브코딩을 위한 Git & GitHub 기초 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기"
series: git-github-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 바꾼 코드를 정확히 파악하려면 status, diff, log 세 명령을 함께 읽어야 합니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 3번째 글입니다.

AI에게 "이 함수를 리팩터링해 줘"라고 했을 때, AI는 어떤 줄을 바꿨을까요? 눈으로 전체 파일을 다시 읽기는 번거롭습니다. 그렇다고 AI가 설명하는 내용만 믿기도 불안합니다. 바이브코딩에서 진짜 안전은 AI의 말이 아니라 Git의 diff에서 옵니다.

`git diff`를 보면 AI가 어떤 줄을 추가하고 어떤 줄을 삭제했는지 정확하게 알 수 있습니다. `git log`를 보면 어느 시점에 어떤 변경이 들어왔는지 흐름이 보입니다. `git status`는 지금 내 작업 트리가 어떤 상태인지 실시간으로 알려 줍니다.

이 세 명령을 commit 전마다 습관적으로 보는 것, 이것이 바이브코딩에서 실수를 줄이는 가장 효과적인 방법입니다.

> AI가 만든 코드를 치기 전에 먼저 읽으세요. `status`는 지금 어디에 있는지, `diff`는 AI가 무엇을 바꿨는지, `log`는 어떤 변경이 저장됐는지를 보여 줍니다.

---

## 이 글에서 다룰 문제
- `git diff`로 AI가 바꾼 내용을 어떻게 줄 단위로 확인할까요?
- `git diff`, `git diff --cached`, `git diff HEAD`는 각각 무엇이 다를까요?
- `git log`로 AI와의 협업 이력을 어떻게 읽을까요?
- AI가 예상보다 많은 파일을 수정했을 때 어떻게 확인할까요?
- commit 전 자기 검토를 어떤 순서로 해야 할까요?

AI는 프롬프트 하나로 여러 파일을 동시에 바꿉니다. 사람이 코드를 타이핑할 때는 변경 내용을 자연스럽게 인지하지만, AI 생성 코드는 한 번에 많은 양이 나오기 때문에 실제로 무엇이 바뀌었는지 놓치기 쉽습니다. `status`, `diff`, `log` 세 명령이 이 갭을 메워 줍니다.

## 세 명령의 역할 구분

기억할 규칙은 세 줄이면 충분합니다.

- `git diff`는 기본적으로 **Working Directory vs Staging** 비교입니다.
- `git diff --cached`는 **Staging vs HEAD** 비교입니다. commit에 들어갈 내용을 미리 봅니다.
- `git diff HEAD`는 **전체 변경 vs 마지막 commit** 비교입니다.

바이브코딩 흐름에서는 AI가 코드를 수정한 직후 `git diff`로 변경 내용을 먼저 읽고, `git add` 후 `git diff --cached`로 commit에 들어갈 내용을 한 번 더 확인하는 습관이 사고를 줄여 줍니다.

## Before / After

**AI가 코드를 바꾼 후 확인 없이 commit할 때**

```bash
$ git add .
$ git commit -m "AI 리팩터링 적용"
# 나중에 버그 발생 - AI가 뭘 바꿨는지 알 수 없음
```

**`diff`로 AI 변경을 검증하고 commit할 때**

```bash
$ git diff  # AI가 바꾼 줄 확인
$ git add app.py
$ git diff --cached  # commit에 들어갈 내용 최종 확인
$ git commit -m "refactor(auth): AI 세션 갱신 로직 분리"
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| AI 수정 후 diff 확인 없이 commit | AI가 의도치 않은 파일까지 바꿨을 수 있음 | 반드시 `git diff`로 변경 확인 후 commit |
| `git diff`가 비어 있어서 변경 없다고 착각 | 이미 staging된 상태일 수 있음 | `git diff --cached`도 함께 확인 |
| `git log`를 안 봐서 이력 파악 못 함 | AI와의 작업 흐름을 놓침 | PR 전에 `git log --oneline -10`으로 이력 검토 |
| untracked 파일을 `diff`에서 못 봐서 놓침 | `git diff`는 추적 파일만 보여줌 | `git status`로 untracked도 별도 확인 |
| `git log` 페이지 출력에서 나오지 못함 | `q` 키를 모름 | `q`로 빠져나오기 |

## AI에게 Git 관련 질문하는 팁

AI와 함께 diff를 분석할 때 효과적인 프롬프트입니다.

- "`git diff` 출력 결과를 붙여넣을게. 이 변경이 안전한지 설명해 줘."
- "방금 리팩터링한 코드에서 `git diff --cached` 결과야. commit message를 추천해 줘."
- "`git log --oneline -20` 결과를 보여줄게. 어떤 commit이 문제를 일으켰을지 추측해 줘."
- "이 `git diff` 출력에서 보안 위험이 있는 변경을 찾아 줘."

## 운영 체크리스트

- [ ] AI가 코드를 수정한 후 반드시 `git diff`로 변경 내용을 확인합니다.
- [ ] `git add` 후 `git diff --cached`로 commit 내용을 검증합니다.
- [ ] `git status -s`의 두 자리 코드를 읽을 수 있습니다.
- [ ] `git log --oneline --graph`로 AI 작업 이력을 주기적으로 검토합니다.
- [ ] `git diff <old> <new>`로 두 시점 사이 변경을 비교할 수 있습니다.
- [ ] `git log`에서 `q`로 빠져나올 수 있습니다.

## 처음 질문으로 돌아가기

AI가 바꾼 코드를 어떻게 검증하나? `git diff`로 줄 단위 변경을 읽고, `git diff --cached`로 commit 내용을 미리 확인하고, `git log`로 이력 흐름을 파악합니다. 이 세 명령을 commit 전마다 보는 습관이 바이브코딩의 품질을 지킵니다.

## 정리

`git status`는 변경의 위치를, `git diff`는 변경의 내용을, `git log`는 이미 저장된 이력의 흐름을 보여 줍니다. 바이브코딩 환경에서는 AI가 코드를 수정할 때마다 이 세 명령으로 검증하는 습관이 의도치 않은 변경이 commit되는 사고를 막아 줍니다.

## 참고 자료

### 공식 문서
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)

### 관련 시리즈
- [GitHub Actions 101](../../github-actions-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Git & GitHub 기초 (1/10): Git이란 무엇인가? 버전 관리의 시작
- 바이브코딩을 위한 Git & GitHub 기초 (2/10): 첫 commit 만들기 - init, status, add, commit
- **바이브코딩을 위한 Git & GitHub 기초 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기
- 바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기
- 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기
- 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
