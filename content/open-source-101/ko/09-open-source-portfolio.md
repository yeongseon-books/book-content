---
series: open-source-101
episode: 9
title: 오픈소스 포트폴리오
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - Portfolio
  - Career
  - GitHub
  - Beginner
seo_description: 채용 담당자가 신뢰하는 오픈소스 포트폴리오 구성 원칙을 정리한 글
last_reviewed: '2026-05-04'
---

# 오픈소스 포트폴리오

> 오픈소스 101 시리즈 (9/10)


## 이 글에서 다룰 문제

*포트폴리오* 는 *경력* 의 *증거* 입니다.

## 전체 흐름
```mermaid
flowchart LR
    P[Profile] --> R[Pinned]
    R --> C[Contribs]
    C --> N[Narrative]
```

## Before/After

**Before**: "*GitHub* 에 *fork* 만 *가득* 하다."

**After**: "*세 개* 의 *대표 PR* 과 *하나* 의 *자작 프로젝트* 가 *고정* 되어 있다."

## 포트폴리오 정비

### 1단계 — Profile README

```bash
gh repo create <username> --public
echo "# Hi, I am ..." > README.md
```

### 2단계 — Pinned 6개 선정

```text
- 자작 프로젝트 1
- 의미 있는 PR 3
- 학습 노트 1
- 기여한 OSS 1
```

### 3단계 — PR 인덱스

```markdown
## Notable PRs
- pandas#123 — Fix x
- requests#456 — Add y
```

### 4단계 — 기여 서사

```markdown
## Story
Started with docs, moved to bugs, now feature work.
```

### 5단계 — 지속 증거

```text
주 2 commits 이상, 3개월 연속
```

## 이 코드에서 주목할 점

- *서사* 가 *맥락*.
- *Pinned* 가 *얼굴*.
- *지속* 이 *신뢰*.

## 자주 하는 실수 5가지

1. ***fork* 만 *쌓는다*.**
2. ***README* 가 *비어 있다*.**
3. ***PR* 링크가 *깨져 있다*.**
4. ***활동* 이 *간헐적*.**
5. ***설명* 이 *없다*.**

## 실무에서는 이렇게 쓰입니다

기업 *채용* 시에도 *GitHub* 활동을 *기술 인터뷰* *전* *참고* 자료로 *활용* 합니다.

## 체크리스트

- [ ] *Profile README* 작성.
- [ ] *Pinned 6개* 선정.
- [ ] *Notable PRs* 인덱스.
- [ ] *3개월* 활동.

## 정리 및 다음 단계

다음 글은 *내 첫 오픈소스 프로젝트* 입니다.

<!-- toc:begin -->
- [오픈소스란 무엇인가](./01-what-is-open-source.md)
- [라이선스 이해하기](./02-understanding-licenses.md)
- [Issue 읽기](./03-reading-issues.md)
- [PR 만들기](./04-creating-pull-requests.md)
- [좋은 README](./05-good-readme.md)
- [Release 와 Versioning](./06-release-and-versioning.md)
- [Community 관리](./07-community-management.md)
- [Maintainer 의 역할](./08-maintainer-role.md)
- **오픈소스 포트폴리오 (현재 글)**
- 내 첫 오픈소스 프로젝트 (예정)
<!-- toc:end -->

## 참고 자료

- [GitHub Profile README](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile)
- [Pinning items](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/pinning-items-to-your-profile)
- [Open Source Guides — Finding Users](https://opensource.guide/finding-users/)
- [Hiring with GitHub](https://github.com/readme)

Tags: OpenSource, Portfolio, Career, GitHub, Beginner
