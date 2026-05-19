# Asset Policy

이 문서는 `book-content`(private)와 `book-public-assets`(public) 간의 이미지 자산 관리 정책을 정의한다.

## Dual-Repository 구조

| Repository | Visibility | Purpose |
| --- | --- | --- |
| `yeongseon-books/book-content` | private | Canonical source, scripts, exports, 이미지 원본 |
| `yeongseon-books/book-public-assets` | **public** | GitHub Pages로 호스팅하는 이미지 CDN |

## 원칙

1. 이미지 원본은 `book-content/assets/<series>/<NN>/`에 저장한다.
2. 외부 발행용 이미지는 `book-public-assets`를 경유한다.
3. **Canonical source(`ko/*.md`, `en/*.md`)는 `book-public-assets`의 public URL을 직접 참조한다.** Tistory/Hashnode/Medium/MkDocs 모두 동일한 URL을 사용하므로, 발행 시점의 경로 재작성이 필요 없다.
4. Public URL을 사용하는 글은 `book-public-assets`가 동기화된 뒤에만 안전하게 발행할 수 있다. 새 이미지를 추가한 글은 `make assets-sync` → public-assets commit/push → GitHub Pages 배포 확인 순서를 지킨다.
5. `series.yaml`의 `meta.asset_base_url`은 정책 참조용 단일 출처(`https://yeongseon-books.github.io/book-public-assets`)로 유지한다. 경로 문자열에 trailing slash를 넣지 않는다.

## URL 구조

```text
Base URL:  https://yeongseon-books.github.io/book-public-assets
Image URL: {asset_base_url}/assets/{series}/{NN}/{file}.png
```

## 동기화

`scripts/sync_assets.py`로 `book-content/assets/` → `book-public-assets/assets/`를 미러링한다.

```bash
# Dry-run (변경 사항 미리보기)
make assets-sync-dry

# 실제 동기화
make assets-sync

# 삭제된 파일까지 정리
make assets-sync-prune
```

### 안전 장치

- `sync_assets.py`는 대상 디렉터리가 `book-public-assets` git 저장소인지 확인한다.
- `--dry-run` 기본값이므로 `--apply`를 명시해야 실제 파일이 복사된다.
- `--prune` 플래그 없이는 대상에서 파일을 삭제하지 않는다.
- 자동 push는 하지 않는다. 동기화 후 수동으로 commit/push한다.

## 파이프라인별 이미지 처리

| Pipeline | 이미지 경로 처리 |
| --- | --- |
| Canonical source | `book-public-assets` public URL 직접 참조 |
| Tistory | 그대로 통과 (canonical과 동일한 public URL) |
| Hashnode | 그대로 통과 |
| Medium | 기본: 그대로 통과. `--asset-mode inline`은 base64 내장. `--asset-mode local`은 상대 경로로 강제 변환 |
| MkDocs | 그대로 통과 |
| eBook | `assets/...` (bundle 내부 상대 경로). Public URL을 로컬 이미지로 다운로드해 self-contained로 만든다. |

## check_links.py 정책

- 로컬 파일 존재 여부만 검증한다.
- 외부 public asset URL은 검증하지 않는다.

## eBook 예외

eBook source bundle은 self-contained이다. `book-public-assets`의 public URL을 사용하지 않고, 이미지를 bundle 내부(`docs/assets/`)에 복사한다.

## 저작권

이미지 원본의 저작권과 라이선스는 `series.yaml`의 `meta.copyright_holder`, `meta.copyright_year`, `meta.license` 필드를 따른다.

## Sync Workflow

1. Dry run:

```bash
make assets-sync-dry
```

2. Apply sync:

```bash
make assets-sync
```

3. Validate references:

```bash
make assets-check
```

4. Commit public assets:

```bash
cd ../book-public-assets
git status
git add assets
git commit -m "assets: sync book-content images"
git push
```

## Publishing Asset Workflow

Before publishing to external platforms (Tistory, Hashnode, Medium), ensure public assets are synced and validated:

1. Dry-run asset sync:

```bash
make assets-sync-dry
```

2. Apply asset sync:

```bash
make assets-sync
```

3. Commit and push public assets:

```bash
cd ../book-public-assets
git status
git add assets
git commit -m "assets: sync book-content images"
git push
```

4. Return to `book-content` and run publish checks:

```bash
cd ../book-content
make publish-check
```

`assets-check` validates the local `book-public-assets` checkout. GitHub Pages deployment may take a short time after pushing, so public URL availability can be verified separately if needed.

## Publish Check

`make publish-check` runs:

- repository quality checks (`make check`)
- MkDocs strict build (`make docs-build`)
- public asset reference validation (`make assets-check`)

It does not generate publishing outputs.

Before running `make publish-check`, regenerate the required outputs and sync public assets if content has changed:

```bash
# Regenerate exports if content changed
make tistory SERIES=<series-id>
make hashnode SERIES=<series-id>
make medium SERIES=<series-id>

# Then validate
make publish-check
```

## Publishing Smoke Test

**Status: Pass** (Last verified: 2026-05-02)

Recommended test target: `rag-deep-dive` episode 1

```bash
# 1. Sync public assets (if images changed)
make assets-sync-dry
make assets-sync

cd ../book-public-assets
git status
git add assets
git commit -m "assets: sync book-content images"
git push

# 2. Generate exports
cd ../book-content
python3 scripts/export_tistory.py rag-deep-dive --episode 1
python3 scripts/export_hashnode.py rag-deep-dive --episode 1
python3 scripts/export_medium.py rag-deep-dive --episode 1

# 3. Validate (against synced public assets)
cd ../book-public-assets
git pull  # Ensure up-to-date
cd ../book-content
python3 scripts/check_public_assets.py --target ../book-public-assets
```

Expected results:

- Pass `exports/tistory/rag-deep-dive/01-document-loading-and-chunking.md` image URLs use `book-public-assets`
- Pass `exports/hashnode/rag-deep-dive/01-document-loading-and-chunking.md` image URLs use `book-public-assets`
- Pass `exports/medium/rag-deep-dive/01.html` image URLs use `book-public-assets`
- Pass `check_public_assets.py` reports 620+ references verified
- Pass No `../../../assets/` paths remain in external publishing outputs
