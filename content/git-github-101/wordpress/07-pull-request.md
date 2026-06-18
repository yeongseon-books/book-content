---
title: "바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지"
series: git-github-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 만든 코드를 팀에 공유하고 리뷰받는 Pull Request 흐름을 익힙니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 7번째 글입니다.

바이브코딩으로 기능을 구현했을 때 "AI가 만든 코드를 그냥 main에 올려도 될까?"라는 걱정이 드는 것은 자연스럽습니다. Pull Request는 이 걱정을 해소하는 구조입니다. AI가 만든 코드가 `main`에 들어가기 전에, 팀원이 검토하고 CI가 자동 검증하는 절차를 강제합니다.

바이브코딩 환경에서 PR이 특히 중요한 이유가 있습니다. AI는 빠르게 많은 코드를 생성하지만, 그 코드가 팀의 코딩 스타일, 보안 정책, 아키텍처 원칙과 맞는지는 사람이 판단해야 합니다. PR은 그 판단의 공간입니다.

더 나아가 PR에 "AI가 생성한 코드입니다. 다음 부분을 특히 검토해 주세요"라고 명시하면, 리뷰어가 AI 코드 특유의 패턴(과도한 추상화, 불필요한 복잡성)을 집중적으로 볼 수 있습니다.

> Pull Request는 AI가 만든 코드의 품질 게이트입니다. branch가 AI의 작업 공간이라면, PR은 그 결과를 팀에 설명하고 검증받는 공간입니다.

---

## 이 글에서 다룰 문제
- Pull Request는 `git merge`와 무엇이 다른가요?
- AI가 만든 코드의 PR을 어떻게 잘 설명할 수 있나요?
- PR 리뷰 comment에 어떻게 응답해야 하나요?
- AI 코드 리뷰에서 특별히 주의할 점은 무엇인가요?
- merge 방식(squash, merge commit)을 어떻게 선택할까요?

바이브코딩에서 PR을 잘 쓰면 두 가지 이점이 생깁니다. 첫째, AI가 만든 코드의 품질을 팀이 함께 검토합니다. 둘째, "이 기능은 AI가 어떻게 구현했는지"를 PR 기록으로 남겨 나중에 참고할 수 있습니다.

## PR 한 사이클 흐름

```bash
# 1. main 최신화
$ git switch main
$ git pull

# 2. AI 작업용 branch 생성
$ git switch -c feature/ai-social-login

# 3. AI와 함께 코드 작성 후 commit
$ git add .
$ git commit -m "feat(auth): AI가 구현한 소셜 로그인 OAuth 플로우"

# 4. GitHub에 push
$ git push -u origin feature/ai-social-login

# 5. GitHub에서 PR 생성
# Title: feat(auth): 소셜 로그인 OAuth 구현
# Body: Closes #42 + AI 생성 코드 검토 요청 포함
```

## AI 코드 PR 본문 예시

```markdown
## 배경
소셜 로그인 기능 추가 요청 (#42)

## AI 생성 코드 안내
- 이 PR의 핵심 로직(OAuth 플로우)은 Claude AI가 생성했습니다.
- 특히 token_refresh.py의 만료 처리 로직을 집중 검토해 주세요.
- 보안 관점에서 token 저장 방식이 적절한지 확인이 필요합니다.

## 변경 내용
- app/auth/oauth.py: OAuth 인증 플로우 구현
- app/auth/token_refresh.py: 토큰 갱신 로직
- tests/test_oauth.py: AI가 생성한 테스트 케이스

## 검증
- [ ] pytest tests/test_oauth.py 통과
- [ ] 실제 Google OAuth로 수동 테스트

## 영향 범위
- app/auth/ 디렉터리
- 기존 로그인 플로우 변경 없음
```

## Before / After

**AI 코드를 main에 직접 push할 때**

```bash
$ git switch main
$ git merge feature/ai-social-login
$ git push  # 검토 없이 배포
# 나중에 보안 문제, 코드 스타일 문제 발견
```

**PR로 AI 코드를 검토받을 때**

```bash
$ git push -u origin feature/ai-social-login
# PR 생성 → 리뷰어 지정 → CI 자동 검증
# 팀원: "AI가 생성한 token 저장 방식이 안전하지 않아요"
# 수정 후 merge → 품질 보장
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| AI 코드 PR 본문 비워두기 | 리뷰어가 무엇을 검토해야 할지 모름 | AI가 만든 부분과 검토 포인트 명시 |
| 너무 큰 PR (AI가 많이 만들었으니까) | 리뷰어가 전체를 제대로 못 봄 | AI 작업도 기능 단위로 PR 나누기 |
| CI 실패를 무시하고 merge | AI 코드에 버그/오류 있음 | 반드시 CI 통과 후 merge |
| 리뷰 comment에 새 branch 만들어 응답 | 대화 맥락이 끊김 | 같은 branch에 commit 추가로 응답 |
| AI 코드임을 PR에 명시 안 함 | 리뷰어가 AI 특유 패턴을 모르고 넘어감 | PR 본문에 AI 생성 코드임을 표시 |

## AI에게 Git 관련 질문하는 팁

AI와 PR 과정에서 효과적인 프롬프트입니다.

- "이 PR의 diff를 붙여넣을게. 코드 리뷰어 입장에서 주의할 점을 알려줘."
- "방금 AI가 만든 코드야. PR 본문에 어떤 검토 포인트를 강조해야 할까?"
- "리뷰어가 이런 comment를 남겼어. 이 코드를 어떻게 개선할까?"
- "이 PR에 포함된 AI 코드에서 보안 취약점이 있는지 점검해 줘."

## 운영 체크리스트

- [ ] AI 코드 PR에 AI 생성임을 명시하고 검토 포인트를 안내합니다.
- [ ] PR 크기를 기능 단위로 유지합니다 (300줄 이하 권장).
- [ ] CI 결과가 통과된 후에만 merge합니다.
- [ ] 리뷰 comment에 같은 branch에 commit을 추가해 응답합니다.
- [ ] merge 후 로컬 main을 pull하고 작업 branch를 삭제합니다.
- [ ] PR 본문에 `Closes #N`으로 관련 issue를 연결합니다.

## 처음 질문으로 돌아가기

AI가 만든 코드를 팀이 안전하게 도입하려면? PR을 통해 검토받습니다. AI 생성 코드임을 명시하고, 특별히 검토가 필요한 부분을 안내하며, CI를 통과한 후에 merge합니다. PR은 AI 코드의 품질 게이트이자 팀의 지식 공유 채널입니다.

## 정리

PR은 branch를 합치자는 요청이며, AI가 만든 코드를 팀에 설명하고 검증받는 공간입니다. AI 코딩 환경에서는 PR 본문에 AI 생성 코드임을 명시하고, 검토 포인트를 구체적으로 안내하는 것이 리뷰 품질을 높입니다. branch → push → PR → review → CI → merge → 로컬 정리까지가 한 사이클입니다.

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
- 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기
- **바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
