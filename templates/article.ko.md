# Template: Korean article (`content/<series>/ko/<NN>-<slug>.md`)
#
# 사용 후 본 안내(`#` 주석) 를 모두 제거하고, front matter 와 본문만 남긴다.
# front matter 는 Phase 7 에서 자동 검증된다 (scripts/check_frontmatter.py).
---
title: "글 제목 (한국어)"
seo_title: "\uac80\uc0c9\uc5d0 \ub178\ucd9c\ub420 SEO \uc81c\ubaa9 (\uc120\ud0dd\uc0ac\ud56d, ko 36\uc790 \ub0b4. \uc0dd\ub7b5\ud558\uba74 title \uc0ac\uc6a9)"
seo_description: "\uac80\uc0c9 \uacb0\uacfc\uc5d0 \ub178\ucd9c\ub420 \ud55c \ubb38\uc7a5 \uc124\uba85 (ko 80\uc790 \ub0b4, 75\uc790 \uad8c\uc7a5). seed_seo_metadata.py\ub85c \ucd08\uae30\uac12\uc744 \ucc44\uc6b8 \uc218 \uc788\ub2e4."
series: "series-id"               # 예: azure-functions-101
episode: 1
language: "ko"
status: "draft"                   # draft | ready | published | needs-update
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
published:
  tistory_url: ""
  medium_url: ""
  mkdocs_url: ""
tags:
  - Azure
  - Cloud
last_reviewed: "2026-04-29"
---

# 글 제목 (H1, 첫 본문 라인)

## Intro

왜 이 글이 필요한가, 누구를 위한 글인가.

## Mental Model

개념 모델 / 그림.

## Main Explanation

본론.

## Practical Example

```python
# 가능하면 FastAPI 또는 Flask 기반.
```

## Common Mistakes / Checklist

- 자주 빠지는 함정 1
- 자주 빠지는 함정 2

## Summary

핵심 3줄 요약.

<!-- toc:begin -->
## 시리즈 목차

- 시리즈 TOC 는 finalize-posts.py 가 자동 생성/갱신한다.
<!-- toc:end -->

---

## 참고 자료

### Official Docs

- [링크 제목](https://...)

### Source Code

- [링크 제목](https://...)

Tags: Azure, Cloud
