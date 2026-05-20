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

븴박 비 나뎲닉니다.

> 븴박 비 나뎲닉니다.

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

## 체크리스트 표

| 항목 | 확인 방법 | 자동화 가능 여부 |
| --- | --- | --- |
| **제목 검토** | 55자 이하, 동사 포함, 독자 언어 사용 | 부분 자동화 (length check) |
| **링크 검증** | 모든 내부/외부 링크 404 여부 | 완전 자동화 (`check_links.py`) |
| **코드 실행** | 모든 코드 블록이 복사-붙여넣기로 동작 | 수동 + 단위 테스트 |
| **이미지 점검** | 캡션 존재, alt 텍스트, 2x 해상도 | 완전 자동화 (`lint_captions.py`) |
| **프론트매터 검증** | status, targets, tags 유효성 | 완전 자동화 (`check_frontmatter.py`) |
| **구조 검사** | TOC, 참고 자료, tags 위치 | 완전 자동화 (`check_article_structure.py`) |
| **문체 검사** | AI slop, S1 규칙 위반 | 부분 자동화 (`check-ko.sh`) |
| **동료 리뷰** | 논리 흐름, 기술 정확성 | 수동 |
| **발행 후 모니터링** | 24시간 내 오탈자 수정, 독자 피드백 | 수동 |

자동화 가능한 항목은 CI로 돌리고, 수동 항목은 팀 루틴으로 고정합니다.

## 자동 검증 도구

발행 전 품질을 보장하려면 자동화 도구를 적극 활용해야 합니다.

### 1. markdownlint

Markdown 문법을 검사합니다.

```bash
npm install -g markdownlint-cli
markdownlint content/**/*.md
```

**주요 규칙**:

- 제목 계층 구조 (H1 → H2 → H3)
- 코드 블록 언어 명시
- 트레일링 공백

### 2. vale

문체와 용어 일관성을 검사합니다.

```bash
brew install vale
vale content/technical-writing-101/ko/
```

**주요 규칙**:

- 수동태 금지
- 중복 단어 경고
- 용어집 일관성

### 3. link checker

링크 깨진 것을 감지합니다.

```bash
python3 scripts/check_links.py
```

**검사 항목**:

- 내부 링크 파일 존재 여부
- 외부 링크 HTTP 상태 코드
- 앞커 링크 유효성

### 4. 커스텀 스크립트

이 저장소는 여러 커스텀 검증 스크립트를 사용합니다.

```bash
# 전체 검증
make check

# 품질 경고 (warning-only)
make check-quality
```

**포함 내용**:

- `finalize-posts.py`: TOC, tags, 참고 자료 위치
- `check-ko.sh`: 한국어 S1 규칙
- `check_frontmatter.py`: front matter 유효성
- `check_article_structure.py`: A-grade 구조

## 동료 리뷰 요청 템플릿

자동화 도구가 통과한 뒤에도 동료 리뷰는 필수입니다. 다음 템플릿을 사용하면 리뷰어가 무엇을 확인해야 하는지 명확해집니다.

```markdown
## 리뷰 요청

### 목적

이 글은 [Technical Writing 101 시리즈 6번째 글]로, 그림과 표 사용법을 다룹니다.

### 확인 요청 사항

- [ ] **논리 흐름**: 독자가 따라가기 쉽운가?
- [ ] **기술 정확성**: 코드와 설명이 일치하는가?
- [ ] **예시 품질**: 코드가 실제로 동작하는가?
- [ ] **캐프션**: 모든 이미지에 캐프션이 있는가?
- [ ] **톤**: ~입니다 register가 일관되는가?

### 자동 검증 통과

```bash
make check  # Pass
```

### 타임라인

리뷰 요청: 2026-05-21
희망 피드백: 2026-05-22 이전
```

이 템플릿은 리뷰어가 무엇을 보아야 하는지 체크리스트로 제공합니다.

## 발행 전 최종 체크 3단계

발행 버튼을 누르기 직전, 마지막으로 세 가지를 확인합니다.

### 1단계: 제목과 도입부 다시 읽기

독자는 제목과 첨 세 단락만 보고도 글의 방향을 판단합니다.

```markdown
# Technical Writing 101 (6/10): 그림과 표 사용하기

문단으로 충분히 설명할 수 있는 내용을 그림으로 바꾸면 오히려 독자를 헷갈리게 만들 수 있습니다. 반대로 흐름이나 비교를 문단으로만 밀어붙이면 독자는 핵심 구조를 파악하기도 전에 스크롤부터 내리게 됩니다.
```

제목은 55자 이하, 동사 포함, 독자 언어를 사용해야 합니다.

### 2단계: 코드와 명령 실행

모든 코드 블록을 새 터미널에서 복사-붙여넣기로 실행해 봅니다.

```bash
# 새 세션에서 테스트
python3 -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
python3 main.py
```

하나라도 실패하면 발행 전에 수정합니다.

### 3단계: 모바일 화면 확인

모바일 트래픽이 전체의 60% 이상이므로, 모바일에서 그림과 표가 깨지지 않는지 확인합니다.

- [ ] 그림이 화면 너비를 넘지 않는가
- [ ] 표가 가로 스크롤로 보이는가
- [ ] 코드 블록이 내용을 잠식하지 않는가

## 발행 후 모니터링

글을 발행한 뒤에도 첫 24시간은 중요합니다.

### 1. 오탈자 모니터링

독자가 제보하는 오탈자는 24시간 내에 수정합니다.

```markdown
> 수정: 2026-05-21 오탄 10시 - 코드 블록 3번째 줄 오타 수정
```

### 2. 독자 피드백 응답

댓글이나 이메일로 들어온 피드백은 48시간 내에 응답합니다.

### 3. 조회 수 모니터링

발행 후 일주일 동안 조회 수를 추적하면 어떤 글이 독자에게 더 유용한지 파악할 수 있습니다.

### 4. 검색 유입 키워드

Google Search Console로 어떤 검색어로 유입되는지 확인하고, 다음 글의 키워드 선정에 반영합니다.

### 5. 회고와 개선

발행 후 1주일이 지나면 간단한 회고를 남깁니다.

```markdown
## 회고 (2026-05-28)

- **잘된 점**: 코드 예시가 명확했다는 피드백 3건
- **개선 필요**: 다이어그램 설명이 부족하다는 지적 1건
- **다음 글 반영**: 다이어그램 설명 분량 늘리기
```

회고는 다음 글의 품질을 높이는 입력이 됩니다.

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
  단띄닉니다.
- **제목, 링크, 코드, 이미지, 발행 후 대응은 왜 한 루틴으로 봐야 할까요?**
  단렷닉니다.
- **발행 후 수정 비용은 왜 발행 전 점검 비용보다 훨씬 클까요?**
  늨륹 낸말니다.

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
