<!--
  ARTICLE_TEMPLATE.md
  101 시리즈 글의 학습형 챕터 표준 템플릿.
  - 본문 4,000자 이상 권장 (목표 6,000자 전후)
  - 11개 섹션 모두 포함 권장
  - Front matter는 templates/article.ko.md / article.en.md 참조
  - 자세한 기준은 STYLE_GUIDE.md "Article Depth Standard" 섹션 참조

  사용법:
  1. 새 글 작성 시 이 파일을 복사하여 시작
  2. 모든 주석(<!-- -->)을 제거
  3. 섹션을 채운 뒤 `python3 scripts/check_article_structure.py <file>` 통과 확인
-->

---
title: "글 제목"
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

# 글 제목

> series-name 시리즈 (N/M)

---

## 이 글에서 배울 것

이 글을 읽고 나면 다음을 이해할 수 있습니다.

- 핵심 개념 1
- 핵심 개념 2
- 실습으로 만들 결과물

## 왜 중요한가

독자가 실제로 겪을 문제 상황에서 시작합니다. 단순 정의가 아니라 "이걸 모르면 무엇이 막히는가"를 보여줍니다.

> 예: Python 파일 하나로 시작한 코드는 금방 커집니다. 처음에는 main.py 하나면 충분하지만, 기능이 늘어나면 import가 꼬이고 테스트가 어려워집니다.

## Mental Model

독자가 머릿속에 남길 비유나 모델을 한두 문단으로 설명합니다.

> 예: Python package는 "코드 박스"입니다. 스크립트는 책상 위에 놓인 종이 한 장이라면, 패키지는 라벨이 붙은 정리함입니다.

## 핵심 개념

### 개념 1

설명 + 코드 또는 예시.

```python
# 짧고 self-contained한 예시
```

### 개념 2

다른 개념과의 비교, 또는 보조 개념.

## Before / After

변경 전후를 비교하여 효과를 가시화합니다.

**Before**

```text
project/
└── main.py
```

**After**

```text
project/
├── pyproject.toml
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── main.py
└── tests/
    └── test_main.py
```

## 단계별 실습

### Step 1. 환경 준비

```bash
# 명령
```

### Step 2. 코드 작성

```python
# 코드
```

### Step 3. 실행 및 확인

```bash
# 결과 확인
```

## 자주 하는 실수

### 실수 1. ...

설명. 왜 발생하고 어떻게 피하는지.

### 실수 2. ...

설명.

### 실수 3. ...

설명.

(권장: 3-5개)

## 실무에서는 이렇게 생각한다

101 독자에게 실무 감각을 줍니다. 트레이드오프, 언제 이 방법을 쓰지 않는지, 팀 협업 시 고려사항.

## 체크리스트

- [ ] 항목 1
- [ ] 항목 2
- [ ] 항목 3

## 연습 문제

1. 직접 따라할 수 있는 작은 문제
2. 개념을 적용해보는 문제
3. (선택) 확장 응용

## 정리

오늘 배운 내용을 5줄 이내로 정리합니다.

- 핵심 1
- 핵심 2
- 핵심 3

## 다음 글

다음 글에서는 ...를 다룹니다.

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
