---
episode: 3
language: ko
last_reviewed: '2026-05-15'
seo_description: SEO 제목과 헤딩 계층, 도입과 본문, 정리로 이어지는 기술 글의 표준 구조와 개요 설계 원칙을 정리합니다.
series: technical-writing-101
status: publish-ready
tags:
- TechnicalWriting
- Title
- Structure
- Outline
- Beginner
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: 제목과 구조 잡기
---

# 제목과 구조 잡기

제목은 그럴듯한데 막상 읽어 보면 어디서 핵심이 나오는지 알 수 없는 글이 있습니다. 반대로 내용은 괜찮은데 제목이 흐려서 검색 결과에서 지나쳐 버리는 글도 많습니다. 두 문제는 따로 생기는 것처럼 보여도 뿌리는 같습니다. 제목이 약속한 독자 행동과 본문 구조가 맞물리지 않았기 때문입니다.

좋은 제목은 클릭을 유도하는 문구가 아니라 글의 목적을 압축한 설계 문장입니다. 구조는 그 약속을 독자가 가장 짧게 따라가도록 만든 경로입니다. 그래서 제목과 구조는 초안 단계부터 같이 다루는 편이 훨씬 안전합니다.

이 글은 Technical Writing 101 시리즈의 3번째 글입니다. 여기서는 제목, 개요, 헤딩, 정리를 한 세트로 설계하는 기준을 정리합니다.

## 이 글에서 다룰 문제

- 좋은 제목과 좋은 구조는 왜 항상 같이 움직여야 할까요?
- 제목은 어떻게 약속이 되고, 구조는 어떻게 그 약속을 전달할까요?
- 제목, 개요, 본문, 정리는 어떤 순서로 맞물려야 할까요?
- 짧은 글도 왜 먼저 뼈대를 세우는 편이 좋을까요?

## 이 글에서 배울 것

- SEO 제목
- 헤딩 계층
- 도입, 본문, 정리 구조
- 개요 만들기
- 문단 다루기

## 왜 중요한가

제목은 클릭을 얻고, 구조는 독자의 시간을 얻습니다. 둘 중 하나만 좋으면 글은 발견되기만 하거나 읽히기만 하고, 끝까지 제대로 전달되지는 않습니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 제목은 약속이고, 개요는 지도이고, 본문은 전달이며, 정리는 독자를 다음 행동으로 밀어 주는 마무리입니다.

![한눈에 보는 멘탈 모델](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/03/03-01-concept-at-a-glance.ko.png)

*한눈에 보는 멘탈 모델*
## 핵심 용어

- **SEO title**: 검색 친화적인 제목입니다.
- **outline**: 초안 단계의 목차입니다.
- **heading**: 제목 레벨입니다.
- **lede**: 첫 단락입니다.
- **TL;DR**: 너무 길어서 다 읽지 못한 독자를 위한 요약입니다.

## Before / After

**Before**: "FastAPI notes"

**After**: "Ship your first FastAPI endpoint in five minutes"

## 초안에서 바로 해 보는 스캔 테스트

다음 개요를 한 번 비교해 보겠습니다.

```markdown
# FastAPI 메모

## 개요
## 내용 1
## 내용 2
## 정리
```

```markdown
# 5분 안에 첫 FastAPI 엔드포인트 실행하기

## 왜 이 글이 필요한가
## 설치
## 코드 작성
## 실행과 검증
## 자주 막히는 지점
```

두 번째 개요가 더 강한 이유는 독자가 헤딩만 읽어도 이동 경로를 알 수 있기 때문입니다. 제목이 약속한 행동이 헤딩에도 이어지고, 중간 검증 지점이 드러나며, 막히는 지점까지 예고됩니다. 스캔 테스트는 간단합니다. 제목과 H2만 읽고도 독자가 해야 할 다음 행동이 보이면 구조가 살아 있는 것입니다.

## 실습: 글 한 편의 뼈대 만들기

### 1단계 — 제목

```python
title = "Ship your first FastAPI endpoint in five minutes"
```

### 2단계 — 개요

```python
outline = ["Install", "Code", "Run", "Verify", "Next step"]
```

### 3단계 — 첫 단락

```python
lede = "Hello World in five minutes"
```

### 4단계 — 본문 헤딩

```markdown
## Install
## Code
## Run
```

### 5단계 — 정리

```python
summary = "Now you can ship your own endpoint"
```

## 이 코드에서 먼저 볼 점

- 제목에 동사가 있습니다.
- 개요는 다섯 항목 이하입니다.
- 정리는 행동으로 닫힙니다.

## 자주 하는 실수 5가지

1. **명사만 있는 제목입니다.**
2. **개요가 너무 깊습니다.**
3. **첫 단락이 너무 깁니다.**
4. **정리가 없습니다.**
5. **H1이 여러 개입니다.**

## 실무에서는 이렇게 드러납니다

뉴스 기사는 역피라미드 구조를 쓰고, 기술 블로그는 결론을 먼저 두는 글쓰기를 자주 씁니다. 둘 다 독자가 처음부터 끝까지 천천히 읽지 않는다는 사실을 전제로 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 제목은 약속입니다.
- 개요는 지도입니다.
- 정리는 행동을 가리켜야 합니다.
- 문단은 짧아야 합니다.
- H1은 하나입니다.

## 체크리스트

- [ ] 제목에 동사가 있는가
- [ ] 개요가 다섯 항목 이하인가
- [ ] 첫 단락이 세 줄 이하인가
- [ ] 한 줄 정리가 있는가

## 연습 문제

1. SEO title의 뜻을 한 줄로 적어 보세요.
2. outline의 뜻을 한 줄로 적어 보세요.
3. TL;DR의 뜻을 한 줄로 적어 보세요.

## 정리

좋은 제목은 독자에게 무엇을 얻는지 약속하고, 좋은 구조는 그 약속을 가장 짧은 경로로 전달합니다. 그래서 제목과 구조는 따로 고치는 요소가 아니라 처음부터 함께 설계해야 하는 한 세트입니다. 다음 글에서는 독자가 처음 보는 개념을 어떻게 설명해야 하는지 살펴보겠습니다.

<!-- toc:begin -->
- [기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [독자 정의하기](./02-defining-the-reader.md)
- **제목과 구조 잡기 (현재 글)**
- 개념 설명하기 (예정)
- 예제 코드 설명하기 (예정)
- 그림과 표 사용하기 (예정)
- README 작성하기 (예정)
- 튜토리얼 작성하기 (예정)
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)
<!-- toc:end -->

## 참고 자료

- [On Writing Well - Zinsser](https://www.harpercollins.com/products/on-writing-well-william-zinsser)
- [The Elements of Style - Strunk & White](https://www.bartleby.com/141/)
- [Inverted Pyramid - Nielsen Norman Group](https://www.nngroup.com/articles/inverted-pyramid/)
- [Google Search Central Title Best Practices](https://developers.google.com/search/docs/appearance/title-link)

Tags: TechnicalWriting, Title, Structure, Outline, Beginner