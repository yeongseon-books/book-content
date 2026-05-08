
# 내 첫 오픈소스 프로젝트

> 오픈소스 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *작은* *도구* *하나* 를 *오픈소스* 로 *공개* 하려면 *무엇* 이 *필요* 할까요?

> *코드*, *문서*, *라이선스*, *릴리스*, *커뮤니티*.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *아이디어* *선정*
- *최소* *기능*
- *공개 준비*
- *첫 릴리스*
- *공지* 와 *피드백*

## 왜 중요한가

*공개* 가 *학습* 을 *완성* 합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    I[Idea] --> M[MVP]
    M --> D[Docs]
    D --> R[Release]
    R --> A[Announce]
```

## 핵심 용어 정리

- **MVP**: *최소* *기능* *제품*.
- **scope**: *범위*.
- **roadmap**: *계획*.
- **announcement**: *공지*.
- **feedback loop**: *피드백 순환*.

## Before/After

**Before**: "*아이디어* 만 *있고* *코드* 가 *없다*."

**After**: "*v0.1.0* 을 *공개* 하고 *피드백* 을 *받는다*."

## 실습: 첫 프로젝트 공개

### 1단계 — 아이디어와 범위

```markdown
- 이름: tinytool
- 목적: 한 줄 명령으로 X
- 비목적: GUI, 다국어
```

### 2단계 — MVP 코드

```bash
mkdir tinytool && cd tinytool
git init
python -m venv .venv
```

### 3단계 — 문서 5종

```text
README.md
LICENSE
CONTRIBUTING.md
CODE_OF_CONDUCT.md
CHANGELOG.md
```

### 4단계 — v0.1.0 릴리스

```bash
git tag v0.1.0
gh release create v0.1.0 --generate-notes
```

### 5단계 — 공지

```markdown
> Released tinytool v0.1.0. Feedback welcome!
```

## 이 코드에서 주목할 점

- *범위* 가 *작다*.
- *문서* 가 *완비*.
- *공지* 가 *유입*.

## 자주 하는 실수 5가지

1. ***완벽주의* 로 *공개* 가 *늦다*.**
2. ***라이선스* 가 *없다*.**
3. ***README* 가 *모호* 하다.**
4. ***피드백* 채널이 *없다*.**
5. ***로드맵* 이 *없다*.**

## 실무에서는 이렇게 쓰입니다

기업의 *내부 도구* 도 *오픈소스 절차* 를 *그대로* *사용* 하면 *온보딩* 이 *빨라집니다*.

## 시니어 엔지니어는 이렇게 생각합니다

- *MVP* 가 *시작*.
- *문서* 가 *제품* 의 *절반*.
- *공지* 가 *마케팅*.
- *피드백* 이 *방향*.
- *지속* 이 *완성*.

## 체크리스트

- [ ] *MVP* 동작.
- [ ] *문서 5종* 완비.
- [ ] *v0.1.0* 릴리스.
- [ ] *공지* 게시.

## 연습 문제

1. *MVP* 한 줄 정의.
2. *비목적(non-goal)* 명시의 *효과* 한 줄.
3. *피드백 루프* *예* 한 줄.

## 정리 및 다음 단계

시리즈를 마칩니다. *첫 PR* 또는 *첫 릴리스* 로 *시작* 하세요.

- [오픈소스란 무엇인가](./01-what-is-open-source.md)
- [라이선스 이해하기](./02-understanding-licenses.md)
- [Issue 읽기](./03-reading-issues.md)
- [PR 만들기](./04-creating-pull-requests.md)
- [좋은 README](./05-good-readme.md)
- [Release 와 Versioning](./06-release-and-versioning.md)
- [Community 관리](./07-community-management.md)
- [Maintainer 의 역할](./08-maintainer-role.md)
- [오픈소스 포트폴리오](./09-open-source-portfolio.md)
- **내 첫 오픈소스 프로젝트 (현재 글)**
## 참고 자료

- [Open Source Guides — Starting a Project](https://opensource.guide/starting-a-project/)
- [Choose a License](https://choosealicense.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Show HN](https://news.ycombinator.com/showhn.html)

Tags: OpenSource, Project, Capstone, GitHub, Beginner

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
