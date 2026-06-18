---
title: "바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기"
series: git-github-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Git
- GitHub
- AI코딩
seo_description: "바이브코딩 시대, AI가 만든 두 branch를 합칠 때 conflict를 두려워하지 않고 해결하는 방법을 배웁니다."
---

# 바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기

이 글은 바이브코딩을 위한 Git & GitHub 기초 시리즈의 5번째 글입니다.

AI에게 "로그인 기능을 구현해 줘"라고 한 branch와 "인증 모듈을 리팩터링해 줘"라고 한 branch가 동시에 같은 파일을 건드렸다면 어떻게 될까요? Git은 자동으로 합칠 수 있는 부분은 처리하고, 사람이 판단해야 하는 부분에서 멈춥니다. 이것이 conflict입니다.

바이브코딩에서 conflict는 AI의 실수가 아니라 "두 작업이 같은 곳을 동시에 바꾸려 했다"는 자연스러운 신호입니다. AI가 만든 두 버전 중 어느 것이 올바른지는 결국 사람이 판단해야 합니다. Git은 그 판단을 요구하는 지점을 정확히 표시해 줄 뿐입니다.

merge를 두려워하면 branch를 만들기 두려워지고, branch를 만들지 않으면 AI 실험의 안전망이 사라집니다. conflict 해결 흐름을 한 번 따라가 보면 그 두려움이 크게 줄어듭니다.

> merge는 AI가 만든 두 history를 어디서 만나게 할지 결정하는 일입니다. conflict는 도구의 실패가 아니라 사람의 결정이 필요한 정상 상태 표시입니다.

---

## 이 글에서 다룰 문제
- fast-forward merge는 어떤 상황에서 일어날까요?
- AI가 같은 파일을 두 branch에서 다르게 바꿨을 때 어떻게 처리할까요?
- conflict marker `<<<`, `===`, `>>>` 세 줄을 어떻게 읽을까요?
- AI에게 conflict 해결을 도움받으려면 어떻게 해야 할까요?
- merge를 중간에 포기하고 원래대로 돌아가는 방법은 무엇인가요?

바이브코딩에서 conflict가 무서운 이유는 대개 어떻게 읽어야 하는지 몰라서입니다. 한 번 구조를 이해하고 나면, AI와 함께 해결하는 것도 어렵지 않습니다.

## merge의 두 가지 패턴

**Fast-forward**: AI가 작업한 branch가 main의 연장선에 있을 때 포인터만 이동합니다.

```bash
$ git switch main
$ git merge feature/ai-login
Updating e7d2c1a..a2b3c4d
Fast-forward
 login.py | 28 ++++++++++
```

**Three-way merge**: main과 feature branch가 각각 독립적으로 진행됐을 때 merge commit이 생깁니다.

```bash
$ git merge feature/ai-auth
Merge made by the 'ort' strategy.
 auth.py | 15 +++++
```

## Conflict 해결 흐름

```bash
$ git merge feature/ai-refactor
CONFLICT (content): Merge conflict in auth.py
Automatic merge failed; fix conflicts and then commit the result.
```

파일을 열면 이런 마커가 보입니다.

```text
<<<<<<< HEAD
def login(user, password):
    return check_credentials(user, password)
=======
def login(user: str, password: str) -> bool:
    result = authenticate(user, password)
    logger.info(f"Login attempt: {user}")
    return result
>>>>>>> feature/ai-refactor
```

- `<<<<<<< HEAD`와 `=======` 사이: 현재 branch(main)의 코드
- `=======`와 `>>>>>>>` 사이: AI가 작업한 branch의 코드

마커를 지우고 최종 코드를 남깁니다. AI에게 "이 두 버전을 합쳐 줘"라고 요청할 수도 있습니다.

```bash
# conflict 해결 후
$ git add auth.py
$ git commit  # merge commit 완성
```

## Before / After

**Conflict를 무서워해서 branch 안 만들 때**

```bash
$ # main에서 바로 AI 작업
$ # 나중에 충돌 가능성 없는 대신 실험 안전망도 없음
$ # 잘못된 AI 코드를 되돌리기 어려움
```

**Branch + merge로 AI 작업 관리할 때**

```bash
$ git switch -c feature/ai-v2
$ # AI 작업 진행
$ git switch main
$ git merge feature/ai-v2  # conflict가 나도 해결 가능
$ # 또는
$ git merge --abort  # 마음 바뀌면 언제든 취소
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Conflict 보고 당황해서 폴더 복사 | 이력이 사라지고 더 복잡해짐 | `git merge --abort`로 중단하고 차분히 재시도 |
| Conflict marker를 남긴 채 commit | 코드가 실행 오류를 일으킴 | `<<<`, `===`, `>>>` 마커를 모두 제거했는지 확인 |
| `git add` 없이 commit 시도 | 해결 완료로 표시 안 됨 | 해결 후 반드시 `git add <file>` 실행 |
| fast-forward와 three-way를 혼동 | history가 예상과 다르게 생김 | `git log --graph`로 결과 확인 |
| conflict 해결 후 테스트 생략 | "합쳐졌지만 동작 안 함" 상태 발생 | merge 후 반드시 테스트 실행 |

## AI에게 Git 관련 질문하는 팁

AI와 conflict를 해결할 때 효과적인 프롬프트입니다.

- "이 Git conflict를 붙여넣을게. 두 버전을 합쳐서 올바른 코드를 만들어 줘."
- "conflict 해결 후 어떤 테스트를 실행해야 할지 알려줘."
- "이 merge conflict에서 보안 관점에서 주의해야 할 부분이 있어?"
- "현재 conflict 상태야. `git status` 결과를 붙여넣을게. 어떻게 해결해야 할까?"

## 운영 체크리스트

- [ ] fast-forward merge와 three-way merge의 차이를 설명할 수 있습니다.
- [ ] conflict marker 세 줄이 각각 어느 쪽 코드인지 읽을 수 있습니다.
- [ ] conflict 해결 순서(edit → `git add` → `git commit`)를 압니다.
- [ ] `git merge --abort`로 merge를 중단하고 돌아갈 수 있습니다.
- [ ] merge 후 반드시 동작 테스트를 합니다.
- [ ] `git log --oneline --graph`로 merge 결과를 확인합니다.

## 처음 질문으로 돌아가기

AI가 만든 두 branch를 합칠 때 conflict가 나면? 당황하지 말고 마커를 읽습니다. 어느 버전이 올바른지 판단하고(또는 AI에게 물어보고), 마커를 지우고 최종 코드를 남긴 뒤 `git add`와 `git commit`으로 마무리합니다. 어렵다면 `git merge --abort`로 언제든 되돌아갈 수 있습니다.

## 정리

merge에는 크게 두 가지가 있습니다. 직선 이력이면 fast-forward로 포인터만 이동하고, 갈라진 이력이면 three-way merge로 새 commit을 만듭니다. conflict가 나면 Git은 멈추고 마커를 남기며, 사람이 최종 코드를 결정한 뒤 `git add`, `git commit`으로 마무리합니다. 바이브코딩에서는 AI에게 conflict 해결을 도움받을 수 있다는 것도 기억하세요.

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
- **바이브코딩을 위한 Git & GitHub 기초 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기 (현재 글)**
- 바이브코딩을 위한 Git & GitHub 기초 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기
- 바이브코딩을 위한 Git & GitHub 기초 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지
- 바이브코딩을 위한 Git & GitHub 기초 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법
- 바이브코딩을 위한 Git & GitHub 기초 (9/10): 좋은 commit message 쓰기 - Conventional Commits와 좋은 본문
- 바이브코딩을 위한 Git & GitHub 기초 (10/10): 실전 Git workflow 만들기 - issue부터 release까지 한 흐름으로
<!-- toc:end -->

Tags: 바이브코딩, Git, GitHub, AI코딩
