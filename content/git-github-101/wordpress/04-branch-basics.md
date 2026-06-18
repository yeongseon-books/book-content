---
title: "바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기"
series: git-github-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI에게 실험적 코드를 맡길 때 branch로 안전하게 분리하는 방법을 배웁니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 4번째 글입니다.

AI에게 "이 기능을 완전히 새로운 방식으로 바꿔 봐"라고 할 때, 기존 코드가 망가질까 봐 망설인 적 있나요? 바이브코딩에서 branch는 이 두려움을 해소하는 도구입니다. AI에게 실험적인 구현을 맡기고 싶다면, 새 branch를 만들어서 그 안에서 마음껏 시도하면 됩니다. 마음에 들면 합치고, 아니면 그냥 버리면 됩니다. `main`은 항상 안전합니다.

branch를 이해하는 순간 AI와의 협업 방식이 달라집니다. "A 방식으로 구현해 봐"와 "B 방식으로 구현해 봐"를 각각 다른 branch에서 AI에게 시키고, 결과를 비교한 다음 더 나은 것을 선택할 수 있습니다. 이것이 바이브코딩에서 branch가 단순한 버전 관리 이상의 의미를 갖는 이유입니다.

branch는 새로운 폴더 복사가 아닙니다. 특정 commit을 가리키는 가벼운 포인터입니다. 만들어도 디스크가 거의 늘지 않고, 전환해도 빠릅니다.

> branch는 AI 실험의 격리 공간입니다. `main`을 건드리지 않고 AI가 마음껏 바꿔볼 수 있는 안전한 작업 줄기를 만드는 것이 핵심입니다.

---

## 이 글에서 다룰 문제
- AI 실험용 branch를 어떻게 만들고 전환하나요?
- branch는 왜 파일 복사가 아니라 포인터인가요?
- 두 AI 구현 결과를 branch로 비교하는 방법은 무엇인가요?
- `HEAD`와 branch의 관계는 무엇인가요?
- 실험이 실패했을 때 branch를 어떻게 버리나요?

바이브코딩에서 "AI에게 다른 접근을 시도해 봐"라고 할 때마다 새 branch를 만드는 습관이 있다면, `main`은 항상 안정적인 상태로 유지됩니다. AI가 실험에서 실패해도, main branch로 돌아오면 원래대로입니다.

## branch가 만들어 내는 AI 협업 패턴

AI와 바이브코딩을 할 때 branch는 세 가지 방식으로 활용됩니다.

```bash
# 패턴 1: AI 기능 구현 실험
$ git switch -c feature/ai-login-v1
# AI에게: "소셜 로그인 기능을 OAuth로 구현해 줘"

# 패턴 2: AI 리팩터링 실험 (기존 코드 보존)
$ git switch -c refactor/ai-auth-cleanup
# AI에게: "auth 모듈을 더 깔끔하게 리팩터링해 줘"

# 패턴 3: AI A/B 구현 비교
$ git switch -c experiment/approach-a
# AI에게: "패턴 A로 구현"
$ git switch main
$ git switch -c experiment/approach-b
# AI에게: "패턴 B로 구현"
$ git diff experiment/approach-a experiment/approach-b
```

## Before / After

**Branch 없이 AI 실험할 때**

```text
$ # AI에게 리팩터링 요청
$ # 마음에 안 들어서 되돌리려 함
$ git log  # 어디로 되돌아가야 할지 모름
$ # 결국 수동으로 이전 버전 복원
```

**Branch로 AI 실험 격리할 때**

```bash
$ git switch main
$ git switch -c experiment/ai-refactor
$ # AI 리팩터링 진행
$ # 마음에 안 들면
$ git switch main  # 즉시 원래 상태로
$ git branch -D experiment/ai-refactor  # 실험 폐기
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| main에서 바로 AI 실험 코드 작성 | main이 불안정해져 되돌리기 어려움 | AI 실험은 항상 새 branch에서 시작 |
| branch 만들고 이동 안 함 | main에 commit이 쌓임 | `git switch -c <name>`으로 만들기와 이동 동시에 |
| 실험 branch를 너무 오래 방치 | main과 멀어져 나중에 합치기 어려움 | 실험 결론 나면 즉시 merge하거나 삭제 |
| 수정 중에 branch 전환 | 변경이 새 branch로 따라감 | 전환 전 commit 또는 stash |
| `-D`로 merge 안 된 branch 삭제 | AI가 만든 실험 코드가 사라짐 | `-d`로 시도 먼저, 경고 읽고 판단 |

## AI에게 Git 관련 질문하는 팁

AI와 branch 전략을 세울 때 효과적인 프롬프트입니다.

- "이 기능을 두 가지 방식으로 구현하려고 해. 각각 어떤 branch 이름이 적절할까?"
- "AI가 리팩터링한 코드를 main에 합치기 전에 어떤 검증이 필요할까?"
- "`git diff main experiment/ai-refactor` 결과야. 이 변경이 안전하게 합칠 수 있는지 설명해 줘."
- "현재 branch 목록을 보여줄게. 어떤 branch를 먼저 처리해야 할까?"

## 운영 체크리스트

- [ ] AI 실험 코드는 항상 새 branch에서 시작합니다.
- [ ] `git switch -c`로 branch 만들기와 이동을 한 번에 합니다.
- [ ] `git log --oneline --graph --decorate --all`로 branch 구조를 확인합니다.
- [ ] `git diff main <branch>`로 AI 구현 결과를 비교합니다.
- [ ] 실험이 끝나면 branch를 합치거나 삭제해 정리합니다.
- [ ] branch 전환 전에 `git status`로 현재 상태를 확인합니다.

## 처음 질문으로 돌아가기

AI 실험을 안전하게 하려면? branch를 만들어 격리합니다. AI가 실험적인 코드를 마음껏 작성해도 `main`은 건드리지 않습니다. 결과가 마음에 들면 merge하고, 아니면 branch를 버립니다. 이것이 바이브코딩에서 두려움 없이 AI 실험을 반복하는 방법입니다.

## 정리

branch는 commit을 가리키는 가벼운 포인터이고, `HEAD`는 현재 작업 branch를 가리키는 또 다른 포인터입니다. `git switch -c`로 만들기와 전환을 한 번에 처리하고, `git diff A B`로 두 branch의 AI 구현을 비교합니다. 바이브코딩에서는 AI 실험마다 새 branch를 만드는 것이 `main`을 안정적으로 유지하는 핵심 습관입니다.

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
- 바이브코딩을 위한 Git & GitHub 기초 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기
- **바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기
- 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기
- 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
