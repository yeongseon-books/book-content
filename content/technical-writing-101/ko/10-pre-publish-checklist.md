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

발행 전 점검은 글을 완벽하게 꾸미는 과정이 아니라 수정 비용을 앞당겨 줄이는 운영 루틴입니다. 한 번의 자동 검증과 한 번의 사람 눈 검토가 있으면, 발행 뒤 급하게 고칠 일을 상당수 줄일 수 있습니다.

이 글은 Technical Writing 101 시리즈의 마지막 글입니다. 여기서는 제목, 링크, 코드, 이미지, 발행 후 대응까지 한 번에 점검하는 마지막 루틴을 정리합니다.

## 먼저 던지는 질문

- 발행 버튼을 누르기 전에 마지막으로 무엇을 봐야 할까요?
- 제목, 링크, 코드, 이미지, 발행 후 대응은 왜 한 루틴으로 봐야 할까요?
- 발행 후 수정 비용은 왜 발행 전 점검 비용보다 훨씬 클까요?

## 큰 그림

![Technical Writing 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/10/10-01-concept-at-a-glance.ko.png)

*Technical Writing 101 10장 흐름 개요*

이 그림에서는 발행 전 체크리스트를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 발행 전 체크리스트의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- 제목 검토
- 링크 검증
- 코드 실행
- 이미지 점검
- 발행 후 검토

## 왜 중요한가

발행 후 수정은 발행 전 점검보다 훨씬 비쌉니다. 독자는 이미 잘못된 링크를 눌렀을 수 있고, 깨진 명령을 복사했을 수 있고, 첫인상도 이미 남았을 수 있기 때문입니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 발행 전 체크리스트는 완벽주의가 아니라 운영 습관입니다. 제목에서 시작해 링크와 코드와 이미지를 확인하고, 발행 뒤까지 이어지는 작은 루틴이 큰 수정 비용을 막습니다.

## 핵심 용어

- **link rot**: 시간이 지나며 생기는 깨진 링크입니다.
- **smoke test**: 기본 동작 점검입니다.
- **canary read**: 동료의 사전 읽기입니다.
- **post-mortem**: 발행 뒤 회고입니다.
- **errata**: 오탈자 수정 목록입니다.

## Before / After

**Before**: A broken link found right after publish.

**After**: The checklist passes before publish.

## 체크리스트를 릴리스 루틴으로 고정합니다

이 저장소처럼 글을 시리즈 단위로 관리한다면 발행 직전 점검도 명령으로 굳혀 두는 편이 좋습니다. 예를 들어 아래 순서는 사람이 빠뜨리기 쉬운 항목을 꽤 잘 잡아 줍니다.

```bash
python3 .sisyphus/medium/finalize-posts.py
bash .sisyphus/style/check-ko.sh content/technical-writing-101/ko
python3 scripts/check_frontmatter.py
python3 scripts/check_links.py
python3 scripts/check_article_structure.py
make check
```

**Expected output:**

```text
hard failures: 0
warnings: 0
```

사람 검토도 여기서 끝나지 않습니다. 자동 검증이 통과한 뒤에는 제목과 첫 세 단락만 따로 다시 읽어 보는 편이 좋습니다. 독자는 그 부분만 읽고도 글의 신뢰도를 판단하는 경우가 많기 때문입니다.

## 실습: 다섯 단계로 점검하기

### 1단계 — 제목 다시 보기

```python
title_ok = ["has a verb", "fits 55 chars", "uses reader words"]
```

### 2단계 — 링크 검증

```bash
python3 scripts/check_links.py
```

### 3단계 — 코드 실행

```bash
python3 -c "from m import add; assert add(2,3) == 5"
```

### 4단계 — 이미지 점검

```python
images = {"caption": True, "alt_text": True, "resolution": "2x"}
```

### 5단계 — 발행 후 검토

```python
post = ["fix typos within 24h", "reply to reader comments"]
```

## 이 코드에서 먼저 볼 점

- 제목은 55자 안에 들어갑니다.
- 링크는 자동으로 검증합니다.
- 코드는 실제로 실행합니다.

## 자주 하는 실수 5가지

1. **link rot를 방치합니다.**
2. **코드가 실행되지 않습니다.**
3. **이미지에 대체 텍스트가 없습니다.**
4. **오탈자를 그대로 둡니다.**
5. **post-mortem이 없습니다.**

## 실무에서는 이렇게 드러납니다

엔지니어링 블로그 팀은 동료 검토, 자동 점검, 발행 후 회고를 함께 굴립니다. 이 세 가지가 있어야 한 번의 발행이 다음 글의 품질까지 끌어올립니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 체크리스트는 루틴입니다.
- 링크는 자동으로 검증합니다.
- 코드는 복사해 붙여 넣어도 돌아가야 합니다.
- 오탈자는 24시간 안에 고칩니다.
- 회고는 다음 글의 입력입니다.

## 체크리스트

- [ ] 제목 점검이 끝났는가
- [ ] 링크 검증이 통과하는가
- [ ] 코드 실행이 통과하는가
- [ ] 이미지 점검이 끝났는가

## 연습 문제

1. link rot의 뜻을 한 줄로 적어 보세요.
2. canary read의 뜻을 한 줄로 적어 보세요.
3. errata의 예시를 한 줄로 적어 보세요.

## 정리

발행 전 체크리스트는 글의 마지막 장식이 아니라 품질을 지키는 운영 절차입니다. 제목, 링크, 코드, 이미지, 발행 후 대응까지 한 흐름으로 점검해야 독자 경험이 안정됩니다. 이 글로 Technical Writing 101 시리즈를 마치며, 다음 시리즈에서는 오픈소스 기여로 이어지는 글쓰기와 협업 흐름을 다루게 됩니다.

## 처음 질문으로 돌아가기

- **발행 버튼을 누르기 전에 마지막으로 무엇을 봐야 할까요?**
  - 본문의 기준은 발행 전 체크리스트를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **제목, 링크, 코드, 이미지, 발행 후 대응은 왜 한 루틴으로 봐야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **발행 후 수정 비용은 왜 발행 전 점검 비용보다 훨씬 클까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: TechnicalWriting, Checklist, Publishing, Quality, Beginner
