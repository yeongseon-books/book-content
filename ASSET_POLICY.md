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
3. Canonical source(`ko/*.md`, `en/*.md`)에 public asset URL을 hardcode하지 않는다.
4. Exporter가 발행 시점에 `series.yaml`의 `meta.asset_base_url`을 읽어 경로를 재작성한다.
5. `asset_base_url`에는 trailing slash를 넣지 않는다.

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
| Canonical source | 상대 경로 유지 (`../../../assets/...`) |
| Tistory | 기본: public URL 재작성. `--local-assets`로 상대 경로 유지 가능 |
| Hashnode | 기본: public URL 재작성. `--local-assets`로 상대 경로 유지 가능 |
| Medium | `--asset-mode public` (기본): public URL. `inline`: base64. `local`: 상대 경로 |
| MkDocs | `../../assets/...` (docs 기준 상대 경로) |
| eBook | `assets/...` (bundle 내부 상대 경로). Public URL 미사용 (self-contained) |

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
