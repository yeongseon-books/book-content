# Template: English article (`content/<series>/en/<NN>-<slug>.md`)
#
# Remove this comment block before saving. Keep only front matter and body.
---
title: "Article Title"
seo_title: "SEO title that ranks (<=60 chars)"
medium_title: "Optional Medium-only title"
series: "series-id"               # e.g. azure-functions-101
episode: 1
language: "en"
status: "draft"                   # draft | ready | published | needs-update
targets:
  tistory: false
  medium: true
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

# Article Title (H1, first content line)

## Intro

Why this matters and who it's for.

## Mental Model

A picture worth keeping in your head.

## Main Explanation

The body.

## Practical Example

```python
# Prefer FastAPI or Flask in user-facing code.
```

## Common Mistakes / Checklist

- Pitfall 1
- Pitfall 2

## Summary

Three-line takeaway.

<!-- toc:begin -->
## In this series

- Series TOC is auto-managed by finalize-posts.py.
<!-- toc:end -->

---

## References

### Official Docs

- [Link title](https://...)

### Source Code

- [Link title](https://...)

Tags: Azure, Cloud
