# Template: eBook preface (`exports/ebook-source/<series>-<lang>/docs/preface.md`)
#
# scripts/export_ebook_source.py 가 시리즈별로 채워 넣는다.
# 사람이 직접 손볼 자리는 "{{ ... }}" 자리표시자로 표기.

# Preface

## 이 책을 읽는 방법

이 책은 {{ series_title }} 시리즈를 한 권으로 묶은 것입니다.
각 장은 블로그 글 한 편에 대응하지만, eBook 흐름에 맞춰 다음과 같이 다듬어졌습니다.

- 다음 글로 넘어가는 안내 문장(`다음 글에서는 ...`) 은 제거되었습니다.
- 책 흐름에서만 의미가 있는 보충 설명(`<!-- ebook-only -->` 블록)이 추가되었습니다.
- 시리즈 TOC 와 블로그 태그 라인은 책 자체 목차로 대체되었습니다.

## 시리즈 전체 구조

{{ series_overview }}

## 챕터 간 연결

{{ chapter_connections }}

## 참고

- 원본 블로그 글: {{ canonical_links }}
- 마지막 업데이트: {{ last_updated }}
