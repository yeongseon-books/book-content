# Content Model

## Root Catalog (`series.yaml`)

Root `series.yaml`은 저장소 전체의 시리즈 카탈로그이며 단일 출처(single source of truth)이다.

시리즈 카탈로그 외에 `meta` 블록이 저장소 전역 메타데이터를 정의한다.

### Root `meta` Fields

| Field | Type | Description |
| --- | --- | --- |
| `repo` | string | GitHub 저장소 경로 (`owner/repo`) |
| `published_ref` | string | 외부 발행물에 사용된 검증된 commit SHA |
| `validated_ref` | string | 산출물 검증 시점의 commit SHA |
| `asset_repo` | string | Public 이미지 저장소 경로 (e.g. `yeongseon-books/book-public-assets`) |
| `asset_base_url` | string | Public 이미지 base URL (trailing slash 없음) |
| `copyright_holder` | string | 저작권 보유자 |
| `copyright_year` | string | 저작권 연도 |
| `license` | string | 콘텐츠 라이선스 (e.g. `CC BY-NC-ND 4.0`) |

정의하는 필드:

- `id`: 시리즈 식별자
- `category`: 주제 분류 (azure, ai 등)
- `title`: 시리즈 제목 (ko/en)
- `description`: 시리즈 설명 (ko/en)
- `languages`: 지원 언어 목록
- `targets`: 발행 대상 (tistory, hashnode, medium, mkdocs, ebook)
- `level`: 난이도 (101, deep-dive 등)
- `lifecycle`: 시리즈 생명주기 (active, archived, superseded)
- `tier`: 포트폴리오 티어 (core, supported, archive)

### Series Lifecycle

| Lifecycle | Meaning |
| --- | --- |
| `active` | 시리즈가 활발히 작성/발행 중이거나 완료된 후에도 유효한 콘텐츠 |
| `archived` | 내용이 오래되어 갱신 필요, 검색 노출 유지하지만 신규 독자에게 추천하지 않음 |
| `superseded` | 후속 시리즈로 대체됨 (예: ai-web-dev-101 → llm-app-foundations-101) |

- `path`: 시리즈 디렉토리 경로

### Portfolio Tier

| Tier | 의미 | 채널 | 업데이트 주기 |
| --- | --- | --- | --- |
| `core` | 핵심 시리즈, 적극 관리 | 5채널 전체 | 분기 1회 이상 |
| `supported` | 유지보수, 필요시 업데이트 | mkdocs + 블로그 1개 | 반기 1회 |
| `archive` | 보존만, 신규 발행 안 함 | mkdocs only | 업데이트 없음 |

## Per-Series Catalog (`content/<series>/series.yaml`)

각 시리즈 디렉토리에 위치하며, 해당 시리즈의 에피소드 목록과 메타데이터를 관리한다.

## Metadata Ownership

메타데이터 필드별 단일 소유자 원칙:

| 필드 | 소유자 | 비고 |
| --- | --- | --- |
| `id`, `category`, `title`, `description`, `targets`, `lifecycle`, `level` | Root `series.yaml` | 포트폴리오 수준 메타데이터 |
| `related`, `track`, `stage` | Root `series.yaml` | 시리즈 간 관계 |
| 에피소드 순서 (`articles`), 시리즈별 `status` | `content/<series>/series.yaml` | 에피소드 카탈로그 |
| `title`, `tags`, `seo_title`, `seo_description` | Article front matter | 글 로컬 필드 |
| `series`, `episode`, `status` | Article front matter | 글이 속한 시리즈/에피소드 식별 |

Root `series.yaml`의 `per:` 블록은 레거시 호환용이며, 신규 시리즈에서는 `content/<series>/series.yaml`의 `articles` 필드를 사용한다.

## Article Front Matter

모든 canonical article(`ko/*.md`, `en/*.md`)은 YAML front matter를 가진다.

### Required Fields

| Field | Type | Description |
| --- | --- | --- |
| `title` | string | Canonical 제목. H1과 반드시 일치해야 한다. |
| `series` | string | Root `series.yaml`의 시리즈 id |
| `episode` | integer | 에피소드 번호 (파일 numeric prefix와 일치) |
| `language` | string | `ko` 또는 `en` |
| `status` | string | Article lifecycle status |
| `targets` | mapping | 발행 대상 플래그 |
| `tags` | list | 태그 목록 |

### Optional Fields

| Field | Type | Description |
| --- | --- | --- |
| `seo_title` | string | SEO/`<title>` 슬롯 override. 비어 있으면 `title`을 그대로 사용한다. 자동 truncate 금지. NFC code-point 기준 길이 제한: ko ≤36, en ≤60. |
| `seo_description` | string | SEO meta description (`<meta name="description">`, `og:description`). NFC code-point 기준 길이 제한: ko ≤80, en ≤150. 권장: ko 75 / en 145. 이모지·ZWJ 금지. 한 글에서 하나의 SEO description 출처로 사용한다. |
| `hashnode_title` | string | Hashnode 발행 제목 override (display only) |
| `medium_title` | string | Medium 발행 제목 override (display only) |
| `ebook_title` | string | eBook 장 제목 override (display only) |
| `published` | mapping | (legacy) 발행된 URL (`tistory_url`, `hashnode_url`, `medium_url`, `mkdocs_url`) |
| `published_to` | mapping | 채널별 발행 정보. `tistory`/`hashnode`/`medium`/`mkdocs` 키 아래 `{url, published_at: YYYY-MM-DD}`. `published`보다 풍부한 추적용 필드. |
| `code_required` | boolean | `publish-ready` 이상 글에서 code block을 요구할지 여부. 기본값은 `true`. 개념 설명, 운영 전략, 아키텍처 해설처럼 코드가 필수가 아닌 글은 `false`로 둘 수 있다. |
| `last_reviewed` | string | 마지막 리뷰 날짜 (`YYYY-MM-DD`). `publish-ready` 이상 status에서 필수. |

### `title` vs `seo_title` 의미

- `title`: canonical. H1과 반드시 일치. 사람이 읽는 제목.
- `seo_title`: 검색 엔진/`<title>` 태그/`og:title` 슬롯 전용 override. 비어 있으면 `title`을 사용한다.
- `seo_title`은 모든 외부 채널 (Tistory, Hashnode, Medium HTML `<title>`, MkDocs `<title>`) 에서 공유한다.
- `hashnode_title`/`medium_title`/`ebook_title`은 본문 상단에 노출되는 display title의 채널별 override일 뿐, SEO `<title>` 슬롯에는 영향을 주지 않는다.
- `seo_title`을 `title`에서 자동 잘라내지 않는다. `len(title) > 60`일 때 검사 도구가 경고만 발생시키며, 저자가 수동으로 `seo_title`을 채워야 한다.

### SEO 길이 제한 (NFC code-point 기준)

| 언어 | 필드 | 권장 | hard limit |
| --- | --- | --- | --- |
| ko | `seo_title` | 32 | 36 |
| ko | `seo_description` | 75 | 80 |
| en | `seo_title` | 55 | 60 |
| en | `seo_description` | 145 | 150 |

검사 도구(`scripts/check_frontmatter.py`)는 NFC 정규화 후 code-point 단위로 길이를 측정한다. 이모지 및 ZWJ는 사용 금지.
## Article Status Lifecycle

| Status | Meaning |
| --- | --- |
| `draft` | 초안 또는 skeleton |
| `content-ready` | 본문 작성 완료 |
| `publish-ready` | 발행 직전 상태 (코드 검증 포함) |
| `published` | 하나 이상의 채널에 발행 완료 |
| `needs-update` | 내용 갱신 필요 |

`ready`는 `publish-ready`의 legacy alias이다. 신규 글에서는 사용하지 않는다.

### Status 전이 규칙

- `publish-ready` 이상: `last_reviewed` 필드 필수
- `published`: `published` URL mapping 필드 필수
- `ready` → `publish-ready`로 순차 변경 예정
- `publish-ready` 이상 글은 기본적으로 code block이 권장된다. 다만 글 성격상 코드가 필요 없는 경우 `code_required: false`를 front matter에 명시한다.
- `published` 상태 글은 advisory check(questions, mental model, code, checklist)가 blocking error로 승격된다.
- `<!-- a-grade-intro:begin -->` 마커가 있는 글은 A-grade 구조 검사를 자동으로 통과한다. 이 마커는 표준 구조와 다른 형식(예: 시리즈 도입 글)에 사용한다.

## Targets

`targets` 필드는 해당 글의 발행 대상을 boolean으로 지정한다.

Required keys: `tistory`, `medium`, `mkdocs`, `ebook`
Optional key: `hashnode`

## Visible Tags Line

모든 source post(`ko/*.md`, `en/*.md`)의 맨 마지막 줄에 `Tags: A, B, C, D` 형식의 visible tag line이 있다. 이 태그의 단일 출처는 `finalize-posts.py`의 `SERIES_TAGS`이다.

## `published_ref` Policy

`series.yaml`의 `meta.published_ref`는 최신 커밋이 아니라, 외부 발행물(Medium HTML 등)에 사용된 검증된 immutable snapshot이다.
- 조직 이전이나 문서 수정만으로 자동 변경하지 않는다.
- Medium HTML을 재생성하고 모든 산출물을 검증한 뒤에만 갱신한다.

## `validated_ref` Policy

`series.yaml`의 `meta.validated_ref`는 `published_ref`와 동일한 정책을 따르되, 산출물 검증 시점의 커밋을 기록한다.
- `published_ref`와 `validated_ref`는 동시에 갱신하는 것이 원칙이다.
- 검증 없이 커밋 해시만 올리지 않는다.

## Disclosure Policy

본 저장소의 콘텐츠는 AI 도구를 활용하여 작성한다. 최종 검토와 기술적 확인은 저자가 직접 수행한다.

블로그 및 eBook 발행물에 이 사실을 명시할 수 있도록 `templates/copyright-page.md`에 표준 disclosure 문구를 둔다.
