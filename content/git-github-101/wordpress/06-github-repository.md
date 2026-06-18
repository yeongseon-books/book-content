---
title: "바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기"
series: git-github-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 만든 코드를 GitHub에 올려 백업하고 공유하는 remote, push, pull 흐름을 익힙니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 6번째 글입니다.

바이브코딩으로 만든 프로젝트가 노트북에만 있다면, 노트북이 고장나면 모든 이력이 사라집니다. AI와 함께 쌓아온 commit 역사도, 각 기능을 만든 맥락도 전부 없어집니다. GitHub에 올리는 순간 그 걱정이 사라집니다.

GitHub는 단순한 백업 도구가 아닙니다. AI 도구들이 GitHub repository와 직접 연동할 수 있어서, "이 저장소의 코드를 리뷰해 줘"나 "최근 commit을 보고 문제를 찾아줘" 같은 요청이 가능해집니다. 바이브코딩과 GitHub의 결합이 개발 생산성을 크게 높이는 이유가 여기에 있습니다.

`push`, `fetch`, `pull`은 별개 기능이 아닙니다. 로컬과 원격의 history를 어느 방향으로 동기화할 것인가라는 한 가지 질문의 세 가지 답입니다.

> remote가 생기는 순간 Git은 혼자만의 도구에서 AI와 팀이 함께 쓰는 협업 플랫폼으로 바뀝니다. push하지 않으면 GitHub는 모르고, pull하지 않으면 로컬은 모릅니다.

---

## 이 글에서 다룰 문제
- GitHub에 AI 프로젝트를 처음 올리는 순서는 어떻게 되나요?
- remote, origin이란 무엇이고 왜 그렇게 부르나요?
- `git push -u origin main`이 한 번에 설정하는 두 가지는 무엇인가요?
- `git fetch`와 `git pull`의 차이는 무엇인가요?
- GitHub에 올리면 안 되는 파일은 무엇인가요?

바이브코딩 프로젝트를 GitHub에 올리는 것은 세 가지 이점이 있습니다. AI가 만든 코드를 안전하게 보관할 수 있고, 다른 기기에서 계속 작업할 수 있으며, 협업자나 AI 도구가 코드에 접근할 수 있습니다.

## Remote 연결 흐름

```bash
# 1. GitHub에서 새 빈 저장소 생성 (README 생성 체크 해제)

# 2. 로컬 저장소에 remote 등록
$ git remote add origin https://github.com/<your-id>/my-ai-project.git

# 3. 확인
$ git remote -v
origin  https://github.com/<your-id>/my-ai-project.git (fetch)
origin  https://github.com/<your-id>/my-ai-project.git (push)

# 4. 첫 push (upstream 설정 포함)
$ git push -u origin main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

`-u` 옵션이 두 가지를 동시에 설정합니다. 로컬 `main`이 `origin/main`을 추적하게 만들고, 이후 `git push`만 쳐도 같은 대상으로 보내게 합니다.

## Before / After

**GitHub 없이 AI 프로젝트 관리할 때**

```text
- 로컬 컴퓨터에만 코드 존재
- AI 도구가 코드를 "볼" 수 없음
- 협업자에게 파일을 직접 전달해야 함
- 노트북 분실 시 모든 이력 소멸
```

**GitHub로 AI 프로젝트 관리할 때**

```bash
$ git push  # AI가 만든 코드를 GitHub에 저장
$ # 다른 기기에서
$ git clone https://github.com/<your-id>/my-ai-project.git
$ # AI 도구에게: "이 GitHub 저장소를 분석해 줘"
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| GitHub 저장소 생성 시 README 체크 | 로컬 이력과 충돌해 첫 push 복잡해짐 | 저장소를 비워 두고 로컬에서 push |
| `.env` 파일이 있는데 push | API 키, 시크릿이 공개 저장소에 노출 | `.gitignore`에 `.env` 추가 후 push |
| `git fetch`만 하고 로컬이 바뀐다고 착각 | fetch는 다운로드만, 로컬 branch는 그대로 | fetch 후 `git pull` 또는 `git merge origin/main` |
| HTTPS에 비밀번호로 인증 시도 | GitHub는 비밀번호 인증 지원 안 함 | PAT(Personal Access Token) 또는 SSH 사용 |
| `git remote -v` 확인 없이 push | 엉뚱한 저장소에 올라갈 수 있음 | push 전 remote URL 항상 확인 |

## AI에게 Git 관련 질문하는 팁

GitHub 연동과 관련해 AI에게 물어볼 수 있는 효과적인 프롬프트입니다.

- "이 프로젝트를 GitHub에 올리려고 해. `.gitignore`에 뭘 추가해야 할까?"
- "GitHub PAT를 생성하는 방법과 Git credential에 등록하는 방법을 알려줘."
- "이 저장소에서 `git log --oneline -20` 결과야. 어떤 기능이 최근에 추가됐는지 요약해 줘."
- "GitHub Actions를 써서 push할 때마다 자동으로 테스트가 돌게 하려면 어떻게 해?"

## 운영 체크리스트

- [ ] GitHub 저장소를 빈 상태로 만들었습니다 (README 없음).
- [ ] `git remote add origin <URL>`로 remote를 등록했습니다.
- [ ] `.env`, API 키 파일을 `.gitignore`에 추가했습니다.
- [ ] `git push -u origin main`으로 첫 push를 완료했습니다.
- [ ] `git fetch`와 `git pull`의 차이를 설명할 수 있습니다.
- [ ] `git remote -v`로 연결된 remote를 확인할 수 있습니다.

## 처음 질문으로 돌아가기

AI가 만든 코드를 GitHub에 올리면 무엇이 좋아지나? 코드가 안전하게 백업되고, 다른 기기에서 접근할 수 있으며, AI 도구가 코드를 분석하는 데 활용할 수 있습니다. push는 로컬 commit을 올리고, fetch는 가져오기만 하며, pull은 가져온 후 합칩니다. `git push -u`로 한 번 설정하면 이후 `git push`만으로 충분합니다.

## 정리

remote는 다른 위치의 저장소를 가리키는 별칭이고, 첫 이름은 보통 `origin`입니다. `git push`는 로컬 commit을 올리고, `git fetch`는 가져오기만 하며, `git pull`은 가져온 뒤 합칩니다. 바이브코딩 환경에서는 AI 프로젝트를 시작할 때 GitHub 저장소를 함께 만들어 두는 것이 가장 안전한 습관입니다.

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
- 바이브코딩을 위한 Git & GitHub 기초 (4/10): branch 기초 - 만들고 옮기고 비교하기
- 바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기
- **바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
