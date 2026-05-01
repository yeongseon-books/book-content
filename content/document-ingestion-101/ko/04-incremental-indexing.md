---
title: '증분 인덱싱 — 변경된 문서만 업데이트'
series: document-ingestion-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-01'
---

# 증분 인덱싱 — 변경된 문서만 업데이트

## 이 글에서 답할 질문

- 문서 전체를 다시 인덱싱하지 않고 변경분만 처리하려면 무엇이 필요할까요?
- 파일 해시와 상태 저장소를 가장 단순하게 어떻게 구현할 수 있을까요?
- 동일 파일, 변경 파일, 신규 파일을 실행 로그에서 어떻게 구분할까요?

> 증분 인덱싱은 벡터 DB 기술이라기보다 파일 상태를 기억하는 운영 자동화 문제입니다.

예제 코드: `/root/Github/document-ingestion-101/ko/04-incremental-indexing/main.py`

![이 글에서 답할 질문](../../../assets/document-ingestion-101/04/04-01-questions-this-post-answers.ko.png)
문서가 수십 개일 때는 전체 재처리도 견딜 수 있지만, 수천 개가 되면 매 실행마다 같은 비용을 내는 구조가 병목이 됩니다.

이번 예제는 해시와 JSON 상태 파일만으로 `added`, `unchanged`, `updated`를 구분합니다. 먼저 이 단순한 기준을 확실히 이해해야 이후에 벡터 저장소 업데이트도 깔끔해집니다.

## 실행 예제

```python
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WORK_DIR = BASE_DIR / 'workspace'
WORK_DIR.mkdir(exist_ok=True)
STATE_FILE = BASE_DIR / 'index_state.json'

class IndexStateStore:
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}

    def save(self) -> None:
        self.state_file.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding='utf-8')

    def file_hash(self, file_path: Path) -> str:
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def classify(self, file_path: Path) -> str:
        record = self.state.get(str(file_path))
        if record is None:
            return 'added'
        current_hash = self.file_hash(file_path)
        if record['hash'] != current_hash:
            return 'updated'
        return 'unchanged'

    def mark_indexed(self, file_path: Path) -> None:
        self.state[str(file_path)] = {
            'hash': self.file_hash(file_path),
            'mtime': file_path.stat().st_mtime,
            'indexed_at': datetime.now().isoformat(timespec='seconds'),
        }

def reset_demo_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    for file_path in WORK_DIR.glob('*'):
        if file_path.is_file():
            file_path.unlink()

def seed_files() -> list[Path]:
    files = {
        'alpha.txt': 'This is the first document. It acts as the baseline for incremental indexing.
',
        'beta.txt': 'This is the second document. We will revise it later.
',
    }
    paths = []
    for name, content in files.items():
        path = WORK_DIR / name
        if not path.exists():
            path.write_text(content, encoding='utf-8')
        paths.append(path)
    return paths

def scan(store: IndexStateStore, files: list[Path], label: str) -> None:
    print(f'[{label}]')
    for file_path in files:
        state = store.classify(file_path)
        print(f'  {file_path.name}: {state}')
        if state in {'added', 'updated'}:
            store.mark_indexed(file_path)
    store.save()

def main() -> None:
    reset_demo_state()
    files = seed_files()
    store = IndexStateStore(STATE_FILE)
    scan(store, files, 'first run')
    scan(store, files, 'second run without changes')
    files[1].write_text('This is the second document. Its contents changed, so it must be reprocessed.
', encoding='utf-8')
    scan(store, files, 'third run after beta update')

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
[first run]
  alpha.txt: added
  beta.txt: added
[second run without changes]
  alpha.txt: unchanged
  beta.txt: unchanged
[third run after beta update]
  alpha.txt: unchanged
  beta.txt: updated
```

## 이 코드에서 봐야 할 것

- `IndexStateStore`가 해시, mtime, indexed_at을 함께 저장해 디버깅 포인트를 남깁니다.
- 동일한 스크립트를 세 번 연속 실행하면서 added → unchanged → updated 흐름을 재현합니다.
- 상태 저장소가 JSON이어서 로직을 먼저 이해하고 나중에 DB로 옮기기 쉽습니다.

## 실무에서 헷갈리는 지점

- mtime만 비교하면 빠르지만 오탐이 생길 수 있습니다. 내용 해시를 같이 보는 이유가 여기에 있습니다.
- 증분 인덱싱은 “변경 감지”와 “변경 반영” 두 단계입니다. 둘을 섞어 생각하면 구현이 꼬입니다.
- 삭제 처리까지 넣으려면 현재 파일 목록과 이전 상태 목록을 비교하는 루프가 추가로 필요합니다.

## 체크리스트

- [ ] 상태 저장소에 해시와 시각을 함께 기록한다.
- [ ] 변경 없는 두 번째 실행이 unchanged로 떨어진다.
- [ ] 파일 수정 후 세 번째 실행이 updated로 바뀐다.
- [ ] 삭제 처리 확장 포인트를 설계했다.

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [메타데이터 설계와 필터링](./03-metadata-filtering.md)
- **증분 인덱싱 — 변경된 문서만 업데이트 (현재 글)**
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

- https://docs.python.org/3/library/hashlib.html

Tags: RAG, Document Processing, LangChain, Python
