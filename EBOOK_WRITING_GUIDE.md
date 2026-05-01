# eBook Writing Guide

이 문서는 블로그 시리즈를 eBook(PDF/EPUB/MkDocs book)으로 묶을 때의 원고 구성 규칙을 정의한다.

eBook export·build 정책은 [`EBOOK.md`](./EBOOK.md), 변환 규칙은 [`PUBLISHING.md`](./PUBLISHING.md), 공통 문체·이미지 규칙은 [`STYLE_GUIDE.md`](./STYLE_GUIDE.md)를 따른다.

---

## Blog Series to eBook Workflow

`tech-writing`의 기본 출판 흐름은 다음과 같다.

```text
1. 블로그 시리즈로 먼저 발행한다.
2. 독자 반응과 원고 품질을 확인한다.
3. 같은 canonical source를 기반으로 eBook source bundle을 만든다.
4. eBook 단계에서 Preface, Prerequisites, Book Map, Part intro, Appendix를 추가한다.
```

따라서 eBook은 블로그를 단순히 합친 결과물이 아니다. 블로그에서 검증된 글을 책의 흐름에 맞게 재구성한 두 번째 산출물이다.

---

## 1. eBook의 목적

eBook은 블로그 글 모음이 아니라 **학습 경로**다.

- 독자는 1장부터 순서대로 읽는다.
- 앞 장을 전제하고 쌓아올릴 수 있다. 반복 설명은 줄이고 앞 장을 참조한다.
- 각 장은 책 전체 흐름 안에서 자기 위치를 알아야 한다.

블로그와 eBook의 차이:

| 항목 | 블로그 | eBook |
| --- | --- | --- |
| 독자 진입 | 검색/링크로 한 편만 들어옴 | 1장부터 순서대로 읽음 |
| 제목 | 검색 키워드와 클릭 유도 중요 | 책 전체 흐름 안에서 일관성 중요 |
| 도입부 | 이 글 하나만 읽어도 맥락을 줘야 함 | 앞 장에서 이어받는 흐름이 중요 |
| 반복 설명 | 어느 정도 필요 | 반복 줄이고 앞 장 참조 |
| 코드 | 독립 실행 가능해야 함 | 점진적으로 누적 가능 |
| 요약 | 빠른 정리 + 다음 글 링크 | 장 요약 + 다음 장으로 자연 연결 |
| 링크 | 외부/관련 글 링크 적극 활용 | 참고자료 중심, 내부 흐름 우선 |
| 산출물 | Tistory / Blogger / Medium | PDF / EPUB / MkDocs book |

---

## 2. eBook 구성

한 권의 eBook은 다음 구성 요소를 갖는다.

```text
Cover          (private builder가 처리)
Preface        (이 책을 읽는 방법, 독자 수준, 실습 환경)
Prerequisites  (필요한 사전 지식)
Book Map       (책 전체 지도)

Part I. ...
  Chapter 1. ...
  Chapter 2. ...

Part II. ...
  Chapter 3. ...
  ...

Appendix       (선택)
References
```

### 예: Azure Functions 101 eBook

```text
Preface
Prerequisites
Book Map

Part I. Mental Model
  1. Azure Functions란?
  2. Trigger와 Binding
  3. Host와 Worker

Part II. First Hands-On
  4. 함수 하나 배포하기

Part III. Production-Aware Basics
  5. 플랜 선택
  6. 스케일링과 콜드 스타트
  7. 모니터링과 운영
```

---

## 3. 장(Chapter) 구성 템플릿

각 장은 아래 순서를 따른다.

```text
# 장 제목

<!-- ebook-only:start -->
## 이 장의 위치

앞 장에서 무엇을 봤고, 이 장에서 무엇을 이어서 보는지 설명한다.
<!-- ebook-only:end -->

## 이 장에서 답할 질문

- 질문 1
- 질문 2
- 질문 3

## 한 문장 멘탈 모델

이 장의 핵심을 한 문장으로 압축한다.

## 핵심 그림

장 전체를 관통하는 도식.

## 본문 설명

개념 → 예제 → 해석 → 실무 포인트.

## 이 장에서 가져갈 것

핵심 요약.

<!-- ebook-only:start -->
## 다음 장으로

다음 장이 왜 필요한지 자연스럽게 연결한다.
<!-- ebook-only:end -->

## 참고 자료
```

---

## 4. ebook-only 블록 사용법

앞뒤 장 연결 문장, 책 내 위치 설명처럼 eBook에서만 의미 있는 내용은 `ebook-only` 블록으로 감싼다.

```markdown
<!-- ebook-only:start -->
## 이 장의 위치

이 장은 Part I의 첫 번째 장입니다. 앞 장에서 Functions의 전체 실행 흐름을 봤고,
이 장에서는 그 흐름을 깨우는 입구인 Trigger와 외부 리소스 연결을 담당하는 Binding을 다룹니다.
<!-- ebook-only:end -->
```

블로그 발행 시에는 이 블록이 제거된다. [`PUBLISHING.md`](./PUBLISHING.md) §6 비교 표 참조.

---

## 5. 반복 제거 규칙

블로그에서는 앞 글을 읽지 않은 독자를 위해 배경을 반복한다. eBook에서는 줄인다.

| 상황 | 블로그 | eBook |
| --- | --- | --- |
| 앞서 설명한 개념 재등장 | 간략 재설명 | "앞 장에서 본 것처럼" + 장 번호 참조 |
| 시리즈 TOC | 글마다 포함 | 제거 (책 자체 TOC 대체) |
| 다음 글 링크 CTA | blog-only 블록으로 포함 | ebook-only 블록의 "다음 장으로"로 대체 |
| 배경 맥락 단락 | 글 초반에 포함 | 첫 장에서 한 번, 이후 생략 |

---

## 6. Part 구조 작성 규칙

각 Part는 `part-N-intro.md` 파일로 시작한다.

```markdown
# Part I. Mental Model

이 Part에서는 Azure Functions의 전체 그림을 잡는다.
Trigger가 함수를 어떻게 깨우는지, Binding이 외부 리소스를 어떻게 연결하는지,
Host와 Worker가 어떻게 협력하는지를 순서대로 다룬다.

이 Part를 마치면 함수 하나가 이벤트를 받아 처리하는 전 과정을 그릴 수 있게 된다.
```

---

## 7. 블로그 → eBook 변환 시 제거·추가 대상

### 제거

- "이 글은 시리즈의 N번째 글입니다" 같은 블로그형 브리지 문장 (`blog-only` 블록)
- 시리즈 TOC `<!-- toc:begin --> ... <!-- toc:end -->` 전체
- 하단 `Tags:` 라인
- 검색 SEO용 반복 키워드
- `blog-only` 블록 전체

### 추가 (eBook 전용 파일)

- `preface.md` — 이 책을 읽는 방법, 독자 수준, 실습 환경, 책 전체 지도
- `prerequisites.md` — 필요한 사전 지식, 권장 개발 환경
- `book-map.md` — 시각적 챕터 맵 (어떤 순서로 읽어야 하는지)
- `part-N-intro.md` — 각 Part 시작 페이지
- `appendix.md` — 핵심 용어 정리, 자주 쓰는 CLI 명령 등 (선택)

---

## 8. eBook 전용 front matter 필드

블로그 원고의 front matter에 eBook 빌드 시 사용할 필드를 추가할 수 있다.

```yaml
---
title: "Azure Functions란?"
series: azure-functions-101
episode: 1
language: ko
targets:
  tistory: true
  blogger: true
  medium: true
  mkdocs: true
  ebook: true
ebook_part: 1
ebook_chapter: 1
---
```

`targets.ebook: true`이어야 `export_ebook_source.py`가 해당 글을 번들에 포함한다.
`ebook_part`, `ebook_chapter`는 Part 구조 자동 생성 시 사용된다 (옵션).

---

## 9. eBook 출판 체크리스트

eBook bundle 생성 전 아래를 확인한다.

- [ ] `preface.md`, `prerequisites.md`, `book-map.md`가 작성되어 있다.
- [ ] 각 장에 `ebook-only` 블록으로 "이 장의 위치"와 "다음 장으로"가 있다.
- [ ] 앞 장을 전제하는 반복 설명이 줄어 있다.
- [ ] 시리즈 TOC, `Tags:` 라인, `blog-only` 블록이 제거 대상으로 마킹되어 있다.
- [ ] `series.yaml`에 `targets.ebook: true`가 설정되어 있다.
- [ ] `export_ebook_source.py` 실행 후 `mkdocs build --strict` 통과.
