# Content Model

## Root Catalog (`series.yaml`)

Root `series.yaml`은 저장소 전체의 시리즈 카탈로그이며 단일 출처(single source of truth)이다.

정의하는 필드:

- `id`: 시리즈 식별자
- `category`: 주제 분류 (azure, ai 등)
- `title`: 시리즈 제목 (ko/en)
- `description`: 시리즈 설명 (ko/en)
- `languages`: 지원 언어 목록
- `targets`: 발행 대상 (tistory, hashnode, medium, mkdocs, ebook)
- `level`: 난이도 (101, deep-dive 등)
- `status`: 시리즈 상태 (planned, draft, active, complete)
- `path`: 시리즈 디렉토리 경로

## Per-Series Catalog (`content/<series>/series.yaml`)

각 시리즈 디렉토리에 위치하며, 해당 시리즈의 에피소드 목록과 메타데이터를 관리한다.

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
| `last_reviewed` | string | 마지막 리뷰 날짜 (`YYYY-MM-DD`) |

### Optional Fields

| Field | Type | Description |
| --- | --- | --- |
| `seo_title` | string | Tistory SEO 제목 |
| `hashnode_title` | string | Hashnode 발행 제목 |
| `medium_title` | string | Medium 발행 제목 |
| `ebook_title` | string | eBook 장 제목 |
| `published` | mapping | 발행된 URL (`tistory_url`, `hashnode_url`, `medium_url`) |
| `code_required` | boolean | `false`이면 code block 검사 생략 (default: `true`) |

## Article Status Lifecycle

| Status | Meaning |
| --- | --- |
| `draft` | 초안 또는 skeleton |
| `content-ready` | 본문 작성 완료, 코드 검증 전 |
| `code-checked` | 예제 코드 검증 완료 |
| `publish-ready` | 발행 직전 상태 |
| `published` | 하나 이상의 채널에 발행 완료 |
| `needs-update` | 내용 갱신 필요 |

`ready`는 `publish-ready`의 legacy alias이다. 신규 글에서는 사용하지 않는다.

### Status 전이 규칙

- `publish-ready` 이상: `last_reviewed` 필드 필수
- `published`: `published` URL mapping 필드 필수
- `ready` → `publish-ready` 또는 `code-checked`로 순차 변경 예정

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
