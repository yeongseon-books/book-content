# Style Guide

이 문서는 기술 글의 문체, 구조, 이미지, 태그, 참고자료 규칙을 정의한다. ko 글의 추가 규칙은 [`.sisyphus/skills/humanize-korean/quick-rules.md`](./.sisyphus/skills/humanize-korean/quick-rules.md) (S1 패턴) 을 함께 따른다.

## Scope

이 문서는 모든 산출물(Tistory / English Blog / Medium / eBook)에 공통으로 적용되는 문체, 코드, 이미지, 참고자료 규칙을 정의한다.

채널별 작성 규칙은 다음 문서를 따른다.

- [`BLOG_WRITING_GUIDE.md`](./BLOG_WRITING_GUIDE.md) — Tistory / English Blog / Medium 블로그 글 작성 규칙
- [`EBOOK_WRITING_GUIDE.md`](./EBOOK_WRITING_GUIDE.md) — eBook 원고 구성 규칙

변환·빌드 규칙은 [`PUBLISHING.md`](./PUBLISHING.md)와 [`EBOOK.md`](./EBOOK.md)를 따른다.

---

## 1. 글 구조 (mandatory order)

모든 글은 다음 순서를 지킨다 ([`AGENTS.md`](./AGENTS.md) "Post structure" 와 동일).

1. **H1 title** (`# Title`) — 첫 본문 라인
2. **Series intro line** — 도입 단락 안에 한 문장 (§1.1 참고)
3. **Body** (sections, code, images, ...)
4. **Series TOC block** — `<!-- toc:begin --> ... <!-- toc:end -->`
5. **References section** — `## 참고 자료` (ko) 또는 `## References` (en/medium)
6. **Tag line** — 마지막 라인: `Tags: A, B, C, D`

권장 본문 구조 (위 mandatory order 와 일치):

```text
1. Title (H1)
2. Intro (왜 이 글이 필요한가) — 시리즈 인트로 한 문장 포함
3. Mental Model (개념 모델 / 그림)
4. Main Explanation
5. Practical Example (코드)
6. Common Mistakes / Checklist
7. Summary
8. Series TOC block (`<!-- toc:begin --> ... <!-- toc:end -->`)
9. References (`## 참고 자료` / `## References`)
10. Tag line (`Tags: A, B, C, D`) — 마지막 줄
```

### 1.1 Series intro line (mandatory)

모든 시리즈 글은 H1 직후 도입 단락 안에 시리즈 안내 한 문장을 포함한다. blog-only 블록으로 감싸지 않고 raw prose로 작성한다 (eBook export 시에도 자연스럽게 읽혀야 한다).

**표준 템플릿 (ko)** — `azure-aks-101` 스타일을 baseline으로 한다.

| 위치 | 권장 문장 |
| --- | --- |
| 첫 글 (1편) | `이 글은 {시리즈 표시명} 시리즈의 첫 번째 글입니다.` |
| 중간 글 (2 ~ N-1편) | `이 글은 {시리즈 표시명} 시리즈의 {N}번째 글입니다.` |
| 마지막 글 (N편) | `이 글은 {시리즈 표시명} 시리즈의 마지막 글입니다.` |

**표준 템플릿 (en)**

| 위치 | 권장 문장 |
| --- | --- |
| 첫 글 | `This is the first post in the {Series Display Name} series.` |
| 중간 글 | `This is post {N} in the {Series Display Name} series.` |
| 마지막 글 | `This is the final post in the {Series Display Name} series.` |

**작성 원칙**

- `{시리즈 표시명}`은 `series.yaml` 의 `title` 필드를 그대로 사용한다 (예: `Azure App Service 101`, `Cloud Computing 101`).
- **배치 (mandatory)**: 인트로 문장은 **자체 단락(standalone paragraph, 앞뒤 빈 줄)** 으로 배치하며, 위치는 **H1 직후 hook 단락 1~2개 다음, 그리고 첫 `---` 구분선이나 첫 `## ` 헤딩보다 앞**이어야 한다.
  - hook 단락이 없으면 짧은 hook 문단(이 글이 다룰 문제·맥락 1~3문장)을 먼저 작성한 뒤 인트로 단락을 둔다. H1 바로 다음에 인트로만 떠 있거나, blockquote 직후·`---` 직전에 인트로 한 줄만 끼워 넣는 형태는 금지한다.
  - 본문 단락 끝에 인트로 문장을 덧붙여 navigation cue가 묻히는 형태도 금지한다.
  - 골든 레퍼런스 예시: `content/azure-app-service-101/ko/01-what-is-app-service.md` (H1 → hook 단락 → 인트로 자체 단락 → 본문).
- 표현은 위 표를 baseline으로 하되 글의 톤에 맞춰 자연스럽게 변형해도 된다 (`출발점입니다`, `마무리 글입니다`, `1화입니다` 등 기존 패턴 허용). 핵심은 독자가 "이 글이 어떤 시리즈의 어떤 위치인지"를 H1 직후 도입부에서 즉시 알 수 있어야 한다는 것이다.
- 인트로 단락 뒤에 한 문장으로 이 글이 다룰 범위를 덧붙여도 좋다 (`여기서는 ... 를 다룹니다.`). 단 이 보조 문장은 인트로와 같은 단락 안에 두며, 별도 hook 단락을 대체하지 않는다.
- AI slop 표현 금지 (`이 글에서는 다음을 배웁니다:`, `By the end of this post, you will...`).

**검증**

`scripts/check_article_structure.py` 가 advisory(warning) 단계로 검사한다. 일괄 백필 완료 후 blocking 으로 승격할 예정이다.

---

## 2. 한국어 글 스타일 (`ko/`)

### 기본 톤

- 자연스러운 `~입니다` 체. 시니어 엔지니어 voice.
- 번역체(translation smell) 회피. `.sisyphus/style/check-ko.sh` 가 `translation-smells.txt` 와 humanize-korean S1 패턴을 grep으로 자동 검증한다.
- 기술 용어는 필요 시 영어 병기 (`이벤트 기반(event-driven) 실행 모델`).
- 비유는 핵심 기술 설명을 흐리지 않는 선에서만.

### im-not-ai S1 패턴 (자동 검증 대상)

`.sisyphus/skills/humanize-korean/quick-rules.md` 의 S1 패턴은 첫 줄부터 회피한다. 자주 적발되는 것:

- `~에 대해(서)` → 목적격 조사 직결
- `~에 있어서` → `~에서`, `~을 볼 때`
- `~을 가지고 있다` → 형용사형
- 이중 피동 `되어진다` → 능동/단일 피동
- 종결 공식 `요약하면`, `정리하자면`, `종합하면`
- hype 어휘 `획기적인`, `압도적인`, `폭발적인`
- 결말 공식 `~할 때입니다`, `~할 시점입니다`
- `~한 것이다`, `~다는 뜻이다` 결말
- 문두 접속사 `나아가,`, `아울러,`, `게다가,`, `더욱이,`

### 좋은 예 / 나쁜 예

```text
좋음:
Azure Functions는 이벤트가 들어올 때 함수를 깨우는 실행 모델입니다.

피함:
Azure Functions는 혁신적인 클라우드 네이티브 서버리스 컴퓨팅 패러다임입니다.
```

---

## 3. 영어 글 스타일 (`en/`, `medium/`)

- Medium 독자를 고려해 짧은 문단.
- 공식 문서 톤(`It is recommended that one should consider...`) 회피. 시니어 엔지니어 voice.
- 실무 문제 중심 제목 (`How to fix cold start in Azure Functions Premium plan` ≫ `An overview of cold start`).
- 복잡한 문장은 분해.
- AI slop 회피: `In today's rapidly evolving landscape...`, `It's worth noting that...`, `Let's dive in!`, `In conclusion,...` 등 금지.

---

## 4. Deep Dive 글 추가 규칙

`*-deep-dive` 시리즈는 신뢰성이 핵심이므로 다음 두 섹션을 반드시 포함한다.

### Source Version

```markdown
## Source Version

- Repository: Azure/azure-functions-host
- Commit: 5e59423
- Runtime family: Azure Functions Host v4
- Last reviewed: 2026-04-28
```

### Call Path Summary (가능 시)

```markdown
## Call Path Summary

Program.cs
  → WebJobsScriptHostService.StartAsync()
    → ScriptHost.InitializeAsync()
      → Read host.json
      → Index function metadata
      → Prepare worker channels
    → JobHost.StartAsync()
      → Start trigger listeners
```

---

## 5. 101 글 추가 규칙 — Article Depth Standard

`*-101` 및 입문 시리즈는 "학습형 챕터" 깊이를 갖춰야 한다. 블로그 요약이 아니라, 초보자가 읽고 따라 하며 작은 결과물을 만들 수 있는 단원을 목표로 한다.

### 분량 기준

- **최소**: 본문 4,000자 이상
- **권장**: 6,000자 전후
- Deep Dive 챕터: 8,000-15,000자 ([§4](#4-deep-dive-글-추가-규칙) 참조)

### 권장 섹션 구조 (11개)

다음 11개 섹션을 순서대로 포함하는 것을 표준으로 한다. 글의 성격에 따라 일부 섹션은 합치거나 생략할 수 있지만, **"이 글에서 배울 것", "왜 중요한가", "자주 하는 실수", "정리", "다음 글"** 다섯은 반드시 포함한다.

1. **이 글에서 배울 것** — 글을 읽고 나면 이해하게 될 것을 bullet 3개로
2. **왜 중요한가** — 정의가 아니라 독자가 겪을 문제 상황에서 시작
3. **Mental Model** — 머릿속에 남길 비유나 모델 (1-2 문단)
4. **핵심 개념** — 1-2개의 핵심 개념 설명 + self-contained 코드
5. **Before / After** 또는 구체적 예시 — 변경 전후 비교로 효과를 가시화
6. **단계별 실습** — Step 1, 2, 3 형식으로 따라할 수 있는 실습
7. **자주 하는 실수** — 3-5개의 흔한 함정과 회피법
8. **실무에서는 이렇게 생각한다** — 트레이드오프, 팀 협업 시 고려사항
9. **체크리스트** — 독자가 스스로 점검할 수 있는 checkbox 리스트
10. **연습 문제** — 1-3개의 작은 문제 (선택)
11. **정리 + 다음 글** — 5줄 요약 + 다음 글로의 bridge

### 코드 요건

- 모든 code snippet은 self-contained여야 한다 (import 포함, copy-paste만으로 실행 가능)
- 사용자 코드는 Python (FastAPI / Flask) 기준
- DB 시리즈는 SQLite 기준

### 템플릿

표준 템플릿은 [`ARTICLE_TEMPLATE.md`](./ARTICLE_TEMPLATE.md) 참조.

## 6. 이미지 규칙

### 위치

```text
assets/<series>/<NN>/<NN>-<idx>-<slug>.{ko|en}.png
```

- ko slug = en counterpart heading slug (ko/en 파일명 대칭 유지)
- 공통 이미지는 `assets/shared/`

### 출처

- 모든 다이어그램의 source는 본문 내 mermaid 코드 블록.
- `flowchart LR` 권장 (이벤트 소스가 왼쪽).
- `()`, `/`, `;`, `(.NET)` 같은 특수문자가 든 라벨은 따옴표로 감싼다: `["Label (with parens)"]`.
- en 다이어그램은 영어 라벨만, ko 다이어그램은 한국어 라벨만.

### 변환

```bash
python3 .sisyphus/medium/mermaid-to-png.py <ko-file> <en-file>
```

ko/en 본문은 로컬 상대 경로를, 외부 발행 변형(medium, tistory, hashnode)은 `series.yaml`의 `meta.asset_base_url` 기준 공개 URL로 재작성된다.

---

## 7. 태그 규칙

태그의 단일 출처는 `.sisyphus/medium/finalize-posts.py` 의 `SERIES_TAGS` dict이다.

- 하단 `Tags: A, B, C, D` visible 라인은 **반드시 유지** (Tistory/Medium 입력 칸에 직접 복사).
- YAML front matter `tags:` 가 도입되면 `finalize-posts.py` 가 두 위치를 동기화한다.
- visible 라인을 직접 손으로 편집하지 않는다 — `SERIES_TAGS` 만 수정한 뒤 finalizer 재실행.

---

## 8. 참고자료 규칙

```markdown
## References

### Official Docs

- [Azure Functions overview](https://learn.microsoft.com/...)

### Source Code

- [Azure/azure-functions-host @ 5e59423](https://github.com/Azure/azure-functions-host/tree/5e59423)
```

- ko 글: 헤딩은 `## 참고 자료` (`## References`, `## 참고문헌`, `## 참고` 사용 금지). `finalize-posts.py` 가 자동 정규화.
- Deep Dive: 가능한 한 commit-pinned 링크 사용.

---

## 9. blog-only / ebook-only 블록

플랫폼별 분기를 위한 마커.

```markdown
<!-- blog-only:start -->
다음 글에서는 ...
<!-- blog-only:end -->

<!-- ebook-only:start -->
이 장은 책 전체 흐름에서 ...
<!-- ebook-only:end -->
```

플랫폼별 처리는 [`PUBLISHING.md`](./PUBLISHING.md) §6 비교 표 참조.

---

## 10. 금지 사항

- 이모지 (`✅`, `❌` 대신 `Pass` / `Fail` 텍스트).
- 모든 사용자 코드는 Python 기반 (FastAPI 또는 Flask).
- AI slop 표현 (한/영 모두).
- visible Tags 라인을 손으로 편집.
- mermaid를 PNG로 대체하지 않은 채 Tistory 업로드.
- medium 변형에서 `master`/`HEAD`/`main` URL 사용 (반드시 commit-pinned `TAG`).
- 타입/린트 에러 suppression (`as any`, `# type: ignore` 등) 코드 예제에서 사용.

---

## 11. Asset Policy

### Location

Generated PNG assets are stored under `assets/<series>/<NN>/`.

### Rules

- Generated PNG files should not be regenerated unless the source diagram changed.
- Do not commit duplicate images with only minor filename differences.
- Medium publishing must not depend on private raw GitHub image URLs.
- If repository size exceeds the agreed threshold, migrate assets to Git LFS or external hosting.
- 외부 발행용 이미지는 `book-public-assets` 저장소(public)를 경유한다.
- Canonical source에 public asset URL을 hardcode하지 않는다.

### Public Asset Workflow

- 동기화: `scripts/sync_assets.py`로 `book-content/assets/` → `book-public-assets/assets/`를 미러링한다.
- Exporter가 발행 시점에 `series.yaml`의 `meta.asset_base_url`을 읽어 경로를 재작성한다.
- 상세 정책은 [`ASSET_POLICY.md`](./ASSET_POLICY.md) 참조.

### Future Options

- Git LFS
- Cloudflare R2 public bucket
- Azure Blob Storage static website
