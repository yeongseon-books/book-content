---
series: technical-writing-101
episode: 10
title: "Technical Writing 101 (10/10): 발행 전 체크리스트"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - TechnicalWriting
  - Checklist
  - Publishing
  - Quality
  - Beginner
seo_description: 발행 전 제목 검토, 링크 검증, 코드 실행 등 품질을 보장하는 최종 체크리스트를 살펴봅니다. 수정 비용을 줄이는 실전 점검 루틴을 다룹니다.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (10/10): 발행 전 체크리스트

글을 다 썼을 때 가장 위험한 순간은 거의 끝났다고 느끼는 순간입니다. 이때는 제목 오탈자, 끊어진 링크, 실행되지 않는 명령, 빠진 캡션 같은 작은 흠을 대충 넘기기 쉽습니다. 하지만 독자는 바로 그 작은 흠에서 글 전체의 신뢰도를 판단합니다.

이 글은 기술 글쓰기 101 시리즈의 마지막 글입니다.

발행 전 점검은 글을 완벽하게 꾸미는 과정이 아니라 수정 비용을 앞당겨 줄이는 운영 루틴입니다. 한 번의 자동 검증과 한 번의 사람 눈 검토가 있으면, 발행 뒤 급하게 고칠 일을 상당수 줄일 수 있습니다.

여기서는 제목, 링크, 코드, 이미지, 발행 후 대응까지 한 번에 점검하는 마지막 루틴을 정리합니다.

![Technical Writing 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/10/10-01-concept-at-a-glance.ko.png)
*Technical Writing 101 10장 흐름 개요*
> 발행 전 체크리스트는 완벽주의가 아니라 운영 습관입니다. 작은 루틴이 큰 수정 비용을 막습니다.

## 이 글에서 다룰 문제

- 발행 버튼을 누르기 전에 마지막으로 무엇을 봐야 할까요?
- 제목, 링크, 코드, 이미지, 발행 후 대응은 왜 한 루틴으로 봐야 할까요?
- 발행 후 수정 비용은 왜 발행 전 점검 비용보다 훨씬 클까요?
- 자동화 도구와 수동 검토를 어떻게 나눠야 효율적일까요?
- 발행 후 첫 24시간을 어떻게 관리해야 할까요?

## 이 글에서 배울 것

- 발행 전 10분 점검 루틴 (5단계)
- 자동화 가능한 품질 검증 도구
- 동료 리뷰 요청 템플릿
- 심각도별 발행 후 수정 대응 가이드
- 발행 후 24시간 모니터링 루틴

발행 후 수정은 발행 전 점검보다 훨씬 비쌉니다. 독자는 이미 잘못된 링크를 눌렀을 수 있고, 깨진 명령을 복사했을 수 있고, 첫인상도 이미 남았을 수 있기 때문입니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 발행 전 체크리스트는 완벽주의가 아니라 운영 습관입니다. 제목에서 시작해 링크와 코드와 이미지를 확인하고, 발행 뒤까지 이어지는 작은 루틴이 큰 수정 비용을 막습니다.

- **link rot**: 시간이 지나며 생기는 깨진 링크입니다.
- **smoke test**: 기본 동작 점검입니다.
- **canary read**: 동료의 사전 읽기입니다.
- **post-mortem**: 발행 뒤 회고입니다.
- **errata**: 오탈자 수정 목록입니다.

## 발행 전 점검 흐름

```
글 초안 완성
      │
      ▼
[자동 검증]  make check
  ─ 링크 깨짐 여부
  ─ frontmatter 유효성
  ─ 구조 검사 (TOC, 참고 자료)
  ─ 한국어 스타일 규칙
      │
      ▼
[수동 검토]  사람 눈
  ─ 제목과 도입부 재독
  ─ 코드 블록 실행 확인
  ─ 이미지 캡션/alt 텍스트 확인
  ─ 모바일 화면 점검
      │
      ▼
[동료 리뷰]  (선택)
  ─ 논리 흐름 확인
  ─ 기술 정확성 검증
      │
      ▼
[발행]
      │
      ▼
[발행 후 24시간]
  ─ 오탈자 수정
  ─ 독자 피드백 응답
  ─ 검색 유입 키워드 확인
```

## Before / After 비교: 점검 방식

### Before / After 예시 1: 점검 없이 발행 vs 체크리스트 통과 후 발행

**Before — 발행 직전 확인 없이 배포**

발행 후 독자로부터 "링크가 깨져 있습니다", "코드가 실행되지 않습니다" 피드백이 쏟아집니다. 급하게 수정하느라 시간을 씁니다.

**After — 자동 검증 스크립트 실행 후 발행**

```bash
python3 .sisyphus/medium/finalize-posts.py
bash .sisyphus/style/check-ko.sh content/technical-writing-101/ko
python3 scripts/check_frontmatter.py
python3 scripts/check_links.py
python3 scripts/check_article_structure.py
make check
```

```text
hard failures: 0
warnings: 0
```

자동 검증 통과 후 발행하면 링크 깨짐, frontmatter 오류, 구조 누락을 사전에 잡을 수 있습니다.

---

### Before / After 예시 2: 모호한 제목 vs 독자 중심 제목

**Before — 검색어와 독자 의도를 고려하지 않은 제목**

```
FastAPI 정리
```

**After — 독자의 질문을 반영한 제목**

```
FastAPI로 REST API 만들기: 5분 Quick Start
```

제목 교정 기준: 55자 이하, 동사 포함, 독자 언어 사용.

---

### Before / After 예시 3: 수정 안내 없음 vs 수정 공지 포함

**Before — 오류 수정 후 조용히 내용만 변경**

독자는 이전에 읽은 내용과 달라진 것을 알 방법이 없습니다.

**After — 수정 공지를 글 상단에 추가**

```markdown
> 수정: 2026-05-21 오후 2시 — 3번 코드 블록 오류 수정 (Thanks @username)
```

독자가 이전에 읽었다면 어느 부분이 바뀌었는지 알 수 있습니다.

## 문서 템플릿: 동료 리뷰 요청 카드

```markdown
## 리뷰 요청

### 목적

이 글은 [시리즈명 N번째 글]로, [주제]를 다룹니다.

### 확인 요청 사항

- [ ] **논리 흐름**: 독자가 따라가기 쉬운가?
- [ ] **기술 정확성**: 코드와 설명이 일치하는가?
- [ ] **예시 품질**: 코드가 실제로 동작하는가?
- [ ] **캡션**: 모든 이미지에 캡션이 있는가?
- [ ] **톤**: ~입니다 체가 일관되는가?

### 자동 검증 통과

```bash
make check  # 통과
```

### 타임라인

- 리뷰 요청: [날짜]
- 희망 피드백: [날짜] 이전
```

## 발행 전 10분 루틴

| 시간 | 작업 | 통과 기준 |
| --- | --- | --- |
| 2분 | 제목/도입부 재검토 | 독자, 목표, 범위가 첫 단락에 보임 |
| 3분 | 링크/구조 자동 검사 | 스크립트 오류 0 |
| 3분 | 코드 블록 스모크 테스트 | 핵심 명령 실행 성공 |
| 2분 | 이미지/캡션 점검 | 캡션, alt, 해상도 기준 통과 |

## 자동 검증 도구

| 도구 | 역할 | 명령 |
| --- | --- | --- |
| markdownlint | Markdown 문법 검사 | `markdownlint content/**/*.md` |
| vale | 문체와 용어 일관성 | `vale content/` |
| check_links.py | 링크 깨짐 감지 | `python3 scripts/check_links.py` |
| check_frontmatter.py | frontmatter 유효성 | `python3 scripts/check_frontmatter.py` |
| check_article_structure.py | TOC, 구조 검사 | `python3 scripts/check_article_structure.py` |

자동화 가능한 항목은 CI로 돌리고, 수동 항목은 팀 루틴으로 고정합니다.

## 발행 후 심각도별 대응

| 심각도 | 문제 예시 | 대응 시간 | 조치 |
| --- | --- | --- | --- |
| **치명적** | 코드가 전혀 동작하지 않음 | 즉시 | 글 비공개 + 수정 후 재발행 |
| **주요** | 링크가 깨짐, 오타로 의미 왜곡 | 1시간 내 | 수정 + 상단 수정 안내 추가 |
| **경미** | 여백 오류, 표현 개선 | 24시간 내 | 수정 |

## 자주 하는 실수

| 실수 | 왜 문제인가 | 바로 고치는 방법 |
| --- | --- | --- |
| link rot를 방치합니다 | 독자가 깨진 링크를 눌러 신뢰를 잃습니다 | 주기적으로 `check_links.py`를 실행합니다 |
| 코드가 실행되지 않습니다 | 독자가 첫 단계에서 실패하고 이탈합니다 | 발행 전 새 환경에서 모든 코드 블록을 직접 실행합니다 |
| 이미지에 대체 텍스트가 없습니다 | 스크린 리더 사용자가 이미지 정보를 얻지 못합니다 | 모든 이미지에 핵심 내용을 설명하는 alt 텍스트를 추가합니다 |
| 오탈자를 그대로 둡니다 | 독자가 글 전체의 신뢰도를 낮게 평가합니다 | 발행 후 24시간 내 수정하고 수정 공지를 추가합니다 |
| 발행 후 회고가 없습니다 | 다음 글에서 같은 실수를 반복합니다 | 발행 1주일 후 잘된 점과 개선점을 간단히 기록합니다 |
| 동료 리뷰 없이 발행합니다 | 논리 오류나 기술 부정확성을 놓칩니다 | 자동 검증 통과 후 동료에게 리뷰 요청합니다 |

## 운영 체크리스트

- [ ] 자동 검증(`make check`)이 오류 0으로 통과했는가
- [ ] 제목이 55자 이하이고 동사를 포함하는가
- [ ] 모든 코드 블록이 새 환경에서 실행되는가
- [ ] 모든 이미지에 캡션과 alt 텍스트가 있는가
- [ ] 모든 링크가 동작하는가
- [ ] 발행 후 24시간 모니터링 계획이 있는가

## 연습 문제

1. link rot와 smoke test를 각각 한 문장으로 설명하세요.
2. 발행 전 10분 루틴의 4단계를 순서대로 나열하세요.
3. 발행 후 "코드가 동작하지 않는다"는 제보를 받았을 때 심각도를 분류하고 대응 시간을 결정하세요.

## 정리

발행 전 체크리스트는 글의 마지막 장식이 아니라 품질을 지키는 운영 절차입니다. 제목, 링크, 코드, 이미지, 발행 후 대응까지 한 흐름으로 점검해야 독자 경험이 안정됩니다. 자동화 도구로 반복 가능한 항목을 먼저 처리하고, 사람 눈 검토를 마지막 단계로 두면 10분 안에 발행 품질을 확보할 수 있습니다. 이 글로 Technical Writing 101 시리즈를 마치며, 다음 시리즈에서는 오픈소스 기여로 이어지는 글쓰기와 협업 흐름을 다루게 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): 예제 코드 설명하기](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): 그림과 표 사용하기](./06-using-figures-and-tables.md)
- [Technical Writing 101 (7/10): README 작성하기](./07-writing-the-readme.md)
- [Technical Writing 101 (8/10): 튜토리얼 작성하기](./08-writing-tutorials.md)
- [Technical Writing 101 (9/10): 블로그와 문서 차이](./09-blog-vs-docs.md)
- **발행 전 체크리스트 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Editorial Calendars - Trello Guide](https://blog.trello.com/editorial-calendar)
- [Hemingway Editor](https://hemingwayapp.com/)
- [Vale - Prose Linter](https://vale.sh/)
- [Plain Language Guidelines](https://www.plainlanguage.gov/guidelines/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/technical-writing-101/ko)

Tags: TechnicalWriting, Checklist, Publishing, Quality, Beginner
