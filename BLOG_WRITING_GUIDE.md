# Blog Writing Guide

이 문서는 Tistory(한국어), Hashnode(영어 Markdown-first 블로그), Medium(영어권 발행 변형) 블로그 발행을 위한 원고 작성 규칙을 정의한다.

문체·이미지·코드·태그 공통 규칙은 [`STYLE_GUIDE.md`](./STYLE_GUIDE.md), 변환·산출물 규칙은 [`PUBLISHING.md`](./PUBLISHING.md)를 따른다.

---

## 1. 발행처

| Pipeline | Platform | URL | Source |
| --- | --- | --- | --- |
| Korean Blog | Tistory | `https://yeongseonchoe.tistory.com/` | `content/<series>/ko/*.md` |
| English Blog | Hashnode | `https://hashnode.com/@yeongseon` | `content/<series>/en/*.md` |
| Medium | Medium | `https://medium.com/@yeongseonchoe` | `content/<series>/medium/*.html` |

---

## 2. 블로그 글의 목적

블로그 글은 **검색 또는 공유 링크를 통해 한 편만 들어온 독자**가 읽는다.

- 앞 글을 읽지 않아도 맥락을 이해할 수 있어야 한다.
- 이 글 하나만 읽어도 핵심 결론을 가져갈 수 있어야 한다.
- 시리즈 흐름은 도움이 되지만 전제가 되어선 안 된다.

---

## 3. 블로그 글 구조

모든 블로그 글은 아래 순서를 따른다. ([`STYLE_GUIDE.md`](./STYLE_GUIDE.md) §1의 mandatory order와 일치)

```text
1. H1 제목 (SEO 키워드 포함)
2. Series intro line (H1 직후 도입 단락 안에 한 문장 — 표준 템플릿 STYLE_GUIDE §1.1)
3. 먼저 던지는 질문 / Questions to Keep in Mind
4. 큰 그림 / Big Picture (다이어그램 1개 + caption + 짧은 해설)
5. 배경 설명 (이 글 하나로 충분한 최소 맥락)
6. 본문 설명 (개념 → concrete anchor → 해석)
7. 실무에서 헷갈리는 지점 / 체크리스트
8. 정리
9. 처음 질문으로 돌아가기 / Answering the Opening Questions
10. 시리즈 TOC block (<!-- toc:begin --> ... <!-- toc:end -->)
11. 참고 자료 (## 참고 자료 / ## References)
12. Tags: A, B, C, D (마지막 줄)
```

### Question Loop opening / closing

블로그 글은 검색 또는 공유 링크로 한 편만 들어온 독자가 읽는다. 따라서 초반 질문과 마지막 답이 같은 글 안에서 닫혀야 한다.

**초반 질문**

- ko 섹션명: `## 먼저 던지는 질문`
- en 섹션명: `## Questions to Keep in Mind`
- 질문은 2-3개를 권장한다.
- 질문은 독자의 실제 혼란, 판단, 장애 상황에서 나온다.
- ko 질문은 번역투 의문문을 피하고 자연스러운 상황형으로 쓴다.

```markdown
## 먼저 던지는 질문

- 함수 코드는 하나인데, 실제 실행은 어디서 시작될까요?
- Trigger는 단순한 함수 호출과 무엇이 다를까요?
- 장애가 났을 때 코드, 설정, 플랫폼 중 어디부터 봐야 할까요?
```

**마지막 답 회수**

- ko 섹션명: `## 처음 질문으로 돌아가기`
- en 섹션명: `## Answering the Opening Questions`
- 처음 질문과 답은 1:1로 대응한다.
- 새 개념을 추가하지 말고 본문에서 만든 판단 기준을 압축해 답한다.

```markdown
## 처음 질문으로 돌아가기

- 함수 코드는 하나인데, 실제 실행은 어디서 시작될까요?
  - 실행은 함수 코드 안에서 시작되지 않습니다. 런타임이 이벤트를 감지하고 Trigger 계약에 따라 함수를 호출합니다.
```

### Big Picture and concrete anchors

`## 큰 그림` / `## Big Picture` 섹션은 본문에 들어가기 전 지도를 주는 곳이다.

- 다이어그램은 1개를 우선 둔다.
- 다이어그램 내부 제목, alt text, visible italic caption은 섹션명을 반복하지 않는다. `큰 그림`, `Big Picture` 대신 `요청 흐름`, `책임 경계`, `실행 순서`, `데이터 이동 경로`처럼 그림이 실제로 보여주는 대상을 쓴다.
- visible italic caption은 한 줄로 쓴다.
- 그림 해설은 2-4문장으로 제한한다.
- 그림은 구조, 흐름, 경계, 책임 분리 중 하나를 보여준다.

핵심 개념은 설명만으로 끝내지 않는다. 각 개념에는 코드, 다이어그램, 표, before/after, 로그, 요청/응답, CLI 출력, 설정 예시, 작은 숫자 예제 중 글의 성격에 맞는 concrete anchor를 하나 이상 둔다. 그림과 코드를 모든 개념에 억지로 넣지 않는다.

### Series navigation

시리즈 글의 H1/front matter `title`은 가능하면 `{Series Short Title} ({N}/{Total}): {Article Title}` 형식을 사용한다. SEO 길이 제한이 걸리면 `seo_title`에서 시리즈 prefix를 생략할 수 있다.

도입부에는 현재 글이 몇 번째인지 밝히되, 다음 글 링크는 넣지 않는다. 다음 글 예고 문장은 본문 끝에 둘 수 있으며, 실제 이동 링크는 Series TOC block에 맡긴다.

### Series intro line (mandatory)

H1 직후 도입 단락 안에 시리즈 안내를 한 문장으로 포함한다. raw prose 로 작성하며 `<!-- blog-only -->` 블록으로 감싸지 않는다 (eBook 빌드에서도 자연스럽게 읽혀야 한다). 표준 템플릿과 작성 원칙은 [`STYLE_GUIDE.md`](./STYLE_GUIDE.md) §1.1 참조.

```markdown
# Azure Functions란? — 이벤트가 코드를 부르는 세계

처음 Azure Functions 를 접하면 ... (도입 hook)

이 글은 Azure Functions 101 시리즈의 두 번째 글입니다. 여기서는 Trigger 와 Binding 의 동작 모델을 정리합니다.
```

### blog-only 블록 사용

다음 글 링크처럼 블로그에서만 의미 있는 보조 정보는 `blog-only` 블록으로 감싼다. 시리즈 인트로 한 문장은 blog-only 가 아니라 본문 도입의 일부로 둔다.

```markdown
<!-- blog-only:start -->
다음 글: [Host와 Worker 구조](./03-host-and-worker.md)
<!-- blog-only:end -->
```

---

## 4. SEO 제목 규칙

### ko (Tistory)

- 핵심 키워드를 제목 앞부분에 배치한다.
- 독자의 질문 형태 또는 "한 번에 이해하기" 형태가 잘 작동한다.
- 예:
  - `Azure Functions란? Trigger, Binding, Host 구조 한 번에 이해하기`
  - `Azure App Service Kudu란? SCM 사이트와 앱 런타임의 차이`
  - `Azure Functions Flex Consumption 플랜 선택 기준 정리`

### en (Hashnode English Blog)

- `ko/` 원문의 구조와 의미를 보존한다. 기술적 정확성과 bilingual archive 역할을 우선한다.
- 제목은 원문 제목의 자연스러운 영어 대응본으로 작성한다.
- 예:
  - `What Is Azure Functions? — A World Where Events Call Your Code`
  - `Request Lifecycle: Where Should You Start When a 502 Happens at 3 AM?`
  - `LangChain introduction — LCEL and the Runnable interface`

### medium

- strict translation이 아니라 publication adaptation이다. 영어권 독자의 문제의식과 hook을 우선한다.
- 도입부는 reader pain point를 강하게 제시한다.
- 예:
  - `Azure Functions Is Not Just "Serverless"`
  - `Most Azure App Service 502s Make More Sense Once You Understand the Request Path`
  - `Kudu Is Not Your App: Understanding the SCM Plane in Azure App Service`

### 4.5 SEO front matter (`seo_title`, `seo_description`)

모든 글의 front matter에는 `seo_description`이 포함되어야 한다. `seo_title`은 선택사항이며, 생략하면 canonical `title`이 사용된다.

**Hard / recommended limits (NFC code-points)**

| Field | ko hard | ko rec | en hard | en rec |
| --- | --- | --- | --- | --- |
| `seo_title` | 36 | 32 | 60 | 55 |
| `seo_description` | 80 | 75 | 150 | 145 |

Hard limit를 넘으면 `scripts/check_frontmatter.py`가 실패한다. 이모지와 ZWJ는 금지된다.

**작성 원칙**

- `seo_title`은 검색 결과 목록에서 독자가 클릭할 이유를 주는 단괴적인 제목이다. canonical title이 hard limit을 넘을 때만 추가한다.
- `seo_description`은 검색 결과 스니펫에 노출되는 한 문장 설명이다. 조사 제목, 번호 매김, 매키업은 피한다.
- ko/en은 독립적으로 작성한다. 자동 번역 금지.
- AI slop 금지: "이 글을 마치면...", "By the end of this chapter..." 같은 meta-intro는 쓰지 않는다.

**초기값 채우기**

```bash
# 단일 시리즈 dry-run
python3 scripts/seed_seo_metadata.py --dry-run <series-id>

# 실제 적용
python3 scripts/seed_seo_metadata.py <series-id>

# 전체 시리즈
python3 scripts/seed_seo_metadata.py --all
```

Extractor 우선순위: `## Mental Model` 블록인용 → `## 왜 중요한가` / `## Why It Matters` 단락 → 메타-인트로가 아닌 첫 단락. 시드 값은 초안이며, 필요시 손으로 다듬는다.
---

## 5. Tistory 발행 규칙

- 발행 대상: `content/<series>/ko/*.md`
- 산출물: `exports/tistory/<series>/<NN>-<slug>.md`
- `ebook-only` 블록을 제거하고 `blog-only` 블록을 유지한다.
- 하단 `Tags:` 라인을 Tistory 태그 칸에 그대로 복사한다.
- 이미지는 Tistory 에디터에 PNG를 직접 업로드한다.
- 발행 후 글 URL을 시리즈 TOC에 반영한다.

---

## 6. Hashnode English Blog 발행 규칙

- 플랫폼: `https://hashnode.com/@yeongseon`
- 발행 대상: `content/<series>/en/*.md`
- 목적: 한국어 원문의 충실한 영어 대응본을 제공한다. 영어 개발자 브랜딩 및 eBook 유입 채널.
- Markdown 원본 구조를 최대한 유지한다. Medium처럼 hook 중심으로 재작성하지 않는다.
- `ko/` 원문과 구조, 기술적 주장, 코드, 그림, 참고자료를 최대한 일치시킨다.
- `ebook-only` 블록을 제거하고 `blog-only` 블록을 유지한다.
- 하단 `Tags:` 라인은 Hashnode tags에 활용한다.
- 이미지는 Hashnode 에디터에 PNG를 직접 업로드한다.
- 발행 후 글 URL을 시리즈 TOC에 반영한다.

---

## 7. Hashnode vs Medium

`en/`과 `medium/`은 모두 영어 콘텐츠이지만 목적이 다르다.

| 항목 | Hashnode English Blog (`en/`) | Medium (`medium/`) |
| --- | --- | --- |
| 플랫폼 | Hashnode | Medium |
| 역할 | 한국어 원문의 충실한 영어 대응본 | 영어권 독자용 발행 변형 |
| 포맷 | Markdown 중심 | HTML 붙여넣기 / 에디터 중심 |
| 구조 | `ko/` 원문 구조를 최대한 유지 | 제목, 도입부, 전환, 결론 재작성 가능 |
| 목적 | bilingual archive, 검색, 개발자 브랜딩, eBook 유입 | reach, branding, 공유 |
| 제목 | 원문 제목의 자연스러운 영어화 | hook 중심 제목 |
| 도입부 | 원문 흐름 유지 | 문제 제기와 reader pain point 강화 |
| 코드/기술 주장 | 원문과 동일하게 유지 | 원문과 동일하게 유지 |
| 참고자료 | 충실히 유지 | 핵심 링크 중심으로 압축 가능 |

Medium은 strict translation이 아니다. `en/`을 기반으로 하되, 영어권 독자에게 더 잘 읽히도록 제목, opening, transition, ending을 조정한 publication adaptation이다.

---

## 8. Medium 발행 규칙

- 플랫폼: `https://medium.com/@yeongseonchoe`
- 발행 대상: `content/<series>/medium/<NN>.html`
- 기반 원고: `content/<series>/en/*.md`
- 목적: 영어권 독자용 발행 변형을 제공한다.
- Medium은 `en/`의 strict translation output이 아니다. 기술적 주장, 코드, 그림, 참고자료는 유지하되 제목, opening, transition, ending은 Medium 독자에게 맞게 조정할 수 있다.
- Chrome에서 `.html` 파일을 열고 전체 선택(Ctrl+A) → 복사 → 빈 Medium 초안에 붙여넣는다.
- 첫 `<h1>`이 Medium 제목 슬롯에 매핑된다.
- 이미지는 기본적으로 public GitHub Pages URL로 재작성되어 있다.
- 하단 `Tags:` 라인의 내용을 Medium 태그 입력칸에 수동으로 복사한다.
- 발행 후 canonical URL을 `ko/` 원본의 참고자료 또는 blog-only 링크에 추가할 수 있다.

---

## 9. 원고 작성 체크리스트

발행 전 아래를 확인한다.

**공통**
- [ ] H1 제목에 핵심 검색 키워드가 포함되어 있다.
- [ ] 이 글 하나만 읽어도 배경 맥락을 이해할 수 있다.
- [ ] 핵심 결론이 글 초반에 나온다.
- [ ] 코드 예제는 독립 실행 가능하다 (이전 글 결과물에 의존하지 않는다).
- [ ] 다음 글 링크가 `blog-only` 블록 안에 있다.
- [ ] `ebook-only` 블록이 없거나, 있다면 `blog-only` 블록과 겹치지 않는다.
- [ ] `make check` 통과 (`hard failures: 0, warnings: 0`).

**Hashnode (`en/`) 발행 시**
- [ ] `ko/` 원문의 구조와 기술적 주장을 그대로 유지한다.
- [ ] 코드, 버전 조건, 경고/제약 사항이 원문과 일치한다.
- [ ] 번역투가 없다 (senior-engineer voice).

**Medium (`medium/`) 발행 시**
- [ ] 제목·opening·section transition·결론이 Medium 독자에게 맞게 조정되어 있다.
- [ ] 기술적 주장, 코드 의미, 버전 조건, 참고자료가 `en/` 원본과 일치한다.
- [ ] `to-medium.py`로 생성한 `.html`을 브라우저에서 열어 렌더링이 정상임을 확인했다.
