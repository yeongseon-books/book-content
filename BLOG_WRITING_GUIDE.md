# Blog Writing Guide

이 문서는 Tistory(한국어)와 Medium(영어) 블로그 발행을 위한 원고 작성 규칙을 정의한다.

문체·이미지·코드·태그 공통 규칙은 [`STYLE_GUIDE.md`](./STYLE_GUIDE.md), 변환·산출물 규칙은 [`PUBLISHING.md`](./PUBLISHING.md)를 따른다.

---

## 1. 블로그 글의 목적

블로그 글은 **검색 또는 공유 링크를 통해 한 편만 들어온 독자**가 읽는다.

- 앞 글을 읽지 않아도 맥락을 이해할 수 있어야 한다.
- 이 글 하나만 읽어도 핵심 결론을 가져갈 수 있어야 한다.
- 시리즈 흐름은 도움이 되지만 전제가 되어선 안 된다.

---

## 2. 블로그 글 구조

모든 블로그 글은 아래 순서를 따른다. ([`STYLE_GUIDE.md`](./STYLE_GUIDE.md) §1의 mandatory order와 일치)

```text
1. H1 제목 (SEO 키워드 포함)
2. 이 글에서 다룰 문제
3. 한 문장 결론 / 멘탈 모델
4. 배경 설명 (이 글 하나로 충분한 최소 맥락)
5. 핵심 그림 (다이어그램)
6. 본문 설명 (개념 → 예제 → 해석)
7. 실무에서 헷갈리는 지점 / 체크리스트
8. 시리즈 TOC block (<!-- toc:begin --> ... <!-- toc:end -->)
9. 참고 자료 (## 참고 자료 / ## References)
10. Tags: A, B, C, D (마지막 줄)
```

### blog-only 블록 사용

앞 글 안 읽은 독자를 위한 브리지, 다음 글 링크처럼 블로그에서만 의미 있는 내용은 `blog-only` 블록으로 감싼다.

```markdown
<!-- blog-only:start -->
이 글은 Azure Functions 101 시리즈의 두 번째 글입니다.
앞 글에서 Functions의 실행 모델을 다뤘고, 이 글에서는 Trigger와 Binding을 다룹니다.

다음 글: [Host와 Worker 구조](./03-host-and-worker.md)
<!-- blog-only:end -->
```

---

## 3. SEO 제목 규칙

### ko (Tistory)

- 핵심 키워드를 제목 앞부분에 배치한다.
- 독자의 질문 형태 또는 "한 번에 이해하기" 형태가 잘 작동한다.
- 예:
  - `Azure Functions란? Trigger, Binding, Host 구조 한 번에 이해하기`
  - `Azure App Service Kudu란? SCM 사이트와 앱 런타임의 차이`
  - `Azure Functions Flex Consumption 플랜 선택 기준 정리`

### en (Medium)

- Hook과 첫 문단이 독자를 붙잡는다. 제목은 실무 문제 중심으로.
- 예:
  - `How to fix cold start in Azure Functions Premium plan`
  - `Azure App Service vs Azure Functions: when to use which`
- "An overview of", "Introduction to" 같은 generic prefix는 피한다.

---

## 4. Tistory 발행 규칙

- 발행 대상: `content/<series>/ko/*.md`
- 산출물: `exports/tistory/<series>/<NN>-<slug>.md`
- `ebook-only` 블록을 제거하고 `blog-only` 블록을 유지한다.
- 하단 `Tags:` 라인을 Tistory 태그 칸에 그대로 복사한다.
- 이미지는 Tistory 에디터에 PNG를 직접 업로드한다.
- 발행 후 글 URL을 시리즈 TOC에 반영한다.

---

## 5. Medium 발행 규칙

- 발행 대상: `content/<series>/en/*.md`
- 산출물: `content/<series>/medium/<NN>.html` (브라우저 붙여넣기용)
- Chrome에서 .html 파일을 열고 전체 선택(Ctrl+A) → 복사 → 빈 Medium 초안에 붙여넣기.
- 첫 `<h1>`이 Medium 제목 슬롯에 매핑된다.
- 이미지는 이미 base64 data URI로 인라인 처리되어 있다.
- 하단 `Tags:` 라인의 내용을 Medium의 태그 입력칸에 수동으로 복사한다.
- 발행 후 canonical URL을 `ko/` 원본의 참고자료 또는 blog-only 링크에 추가할 수 있다.

---

## 6. 원고 작성 체크리스트

발행 전 아래를 확인한다.

- [ ] H1 제목에 핵심 검색 키워드가 포함되어 있다.
- [ ] 이 글 하나만 읽어도 배경 맥락을 이해할 수 있다.
- [ ] 핵심 결론이 글 초반에 나온다.
- [ ] 코드 예제는 독립 실행 가능하다 (이전 글 결과물에 의존하지 않는다).
- [ ] 다음 글 링크가 `blog-only` 블록 안에 있다.
- [ ] `ebook-only` 블록이 없거나, 있다면 `blog-only` 블록과 겹치지 않는다.
- [ ] `make check` 통과 (`hard failures: 0, warnings: 0`).
