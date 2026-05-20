<!--
  ARTICLE_TEMPLATE.md
  101 시리즈 글의 Question Loop 표준 템플릿.
  - 본문 4,000자 이상 권장 (목표 6,000자 전후)
  - 신규 글과 대규모 리라이트 글은 이 구조를 우선 적용
  - 처음 질문으로 독자의 호기심을 만들고, 본문 마지막에서 질문별 답을 회수
  - Front matter는 templates/article.ko.md / article.en.md 참조
  - 자세한 기준은 STYLE_GUIDE.md "Question Loop 구조"와 "Article Depth Standard" 섹션 참조

  사용법:
  1. 새 글 작성 시 이 파일을 복사하여 시작
  2. 모든 HTML 주석을 제거
  3. 섹션을 채운 뒤 `python3 scripts/check_article_structure.py` 통과 확인
-->

---
title: "Series Short Title (N/M): 글 제목"
seo_title: "글 제목"
series: "series-id"
episode: 1
language: "ko"
status: "draft"
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Tag1
  - Tag2
  - Tag3
  - Tag4
  - Tag5
last_reviewed: "YYYY-MM-DD"
---

# Series Short Title (N/M): 글 제목

독자가 실제로 겪는 문제 상황에서 시작합니다. 정의부터 말하지 말고, 이 개념을 모르면 어디서 헷갈리는지 1-2문단으로 보여줍니다.

이 글은 {시리즈 표시명} 시리즈의 {N}번째 글입니다. 여기서는 {이번 글의 범위}를 다룹니다.

## 먼저 던지는 질문

- 독자가 이 글을 읽으며 답을 찾을 질문 1
- 독자가 실제로 겪는 판단/장애/혼란 상황 2
- 글 끝에서 반드시 회수할 질문 3

## 큰 그림

![큰 그림 설명](https://yeongseon-books.github.io/book-public-assets/assets/<series>/<NN>/<NN>-01-big-picture.ko.png)

_이 그림이 보여주는 구조, 흐름, 경계, 책임 분리 중 하나를 한 줄로 설명_

이 그림에서는 {가장 먼저 봐야 할 구조/흐름/경계}만 봅니다. 세부 개념은 아래 섹션에서 하나씩 나눠 설명합니다.

## 핵심 개념 1

개념을 설명합니다. 설명만으로 끝내지 말고, 독자가 손으로 실행하거나 눈으로 비교할 수 있는 concrete anchor를 둡니다.

```python
# 실행 가능한 작은 예시
from flask import Flask

app = Flask(__name__)

@app.get("/")
def index() -> dict[str, str]:
    return {"message": "hello"}
```

이 예시에서 봐야 할 점을 2-4문장으로 설명합니다.

## 핵심 개념 2

개념의 성격에 맞는 anchor를 고릅니다. 코드가 가장 좋지 않다면 표, before/after, 로그, 요청/응답, CLI 출력, 설정 예시를 사용합니다.

| 구분 | 선택지 A | 선택지 B |
| --- | --- | --- |
| 책임 | A가 맡는 일 | B가 맡는 일 |
| 확인 방법 | 어떤 값을 보는가 | 어떤 로그를 보는가 |

표나 그림을 사용했다면 바로 아래에서 독자가 무엇을 비교해야 하는지 짧게 설명합니다.

## 실무에서 헷갈리는 지점

### 헷갈리는 지점 1

왜 헷갈리는지, 어떤 기준으로 나누면 되는지 설명합니다.

### 헷갈리는 지점 2

실제 장애, 운영, 협업 상황에서 어떻게 판단하는지 설명합니다.

### 헷갈리는 지점 3

피해야 할 오해와 안전한 판단 순서를 설명합니다.

## 체크리스트

- [ ] 처음 질문 1에 답할 수 있는가?
- [ ] 핵심 개념의 경계나 흐름을 그림 없이 말로 설명할 수 있는가?
- [ ] 예시 코드, 표, 로그, 설정 중 하나로 개념을 확인할 수 있는가?

## 정리

- 핵심 요약 1
- 핵심 요약 2
- 핵심 요약 3

## 처음 질문으로 돌아가기

- 독자가 이 글을 읽으며 답을 찾을 질문 1
  - 본문에서 이미 설명한 기준으로 짧게 답합니다. 새 개념을 추가하지 않습니다.

- 독자가 실제로 겪는 판단/장애/혼란 상황 2
  - 본문에서 만든 흐름, 표, 코드, 로그 해석을 압축해 답합니다.

- 글 끝에서 반드시 회수할 질문 3
  - 독자가 이 글을 닫을 때 가져가야 할 판단 문장으로 답합니다.

다음 글에서는 {다음 글의 주제}를 다룹니다. 실제 이동 링크는 아래 시리즈 목차에서 확인합니다.

---

<!-- toc:begin -->
## series-name 시리즈

- 시리즈 TOC는 finalize-posts.py가 자동 생성/갱신합니다.
<!-- toc:end -->

## 참고 자료

- [공식 문서 제목](https://...)
- [관련 글 또는 spec](https://...)
- [추가 reading](https://...)

Tags: Tag1, Tag2, Tag3, Tag4, Tag5
