---
title: "Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트"
series: document-ingestion-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-15'
seo_description: 증분 인덱싱은 벡터 저장소 기법이라기보다 무엇이 바뀌었는지 기억하는 운영 문제입니다.
---

# Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트

전체 인덱스를 다시 만드는 방식은 단순합니다. 하지만 코퍼스가 커지면 생각보다 빨리 한계가 옵니다. 그 시점부터 중요한 질문은 무엇이 바뀌었는지 기억하고, 나머지는 안전하게 건너뛰는 방법입니다.

이 글은 Document Ingestion 101 시리즈의 4번째 글입니다. 여기서는 파일 해시와 작은 상태 저장소를 이용해 추가된 문서, 변경 없는 문서, 수정된 문서를 구분합니다.

## 먼저 던지는 질문

- 문서가 조금 바뀔 때마다 전체 인덱스를 다시 만들면 어떤 비용이 생길까요?
- 변경 감지는 파일 시간보다 왜 content hash와 상태 저장소가 더 안전할까요?
- 삭제된 문서와 수정된 청크를 인덱스에서 어떻게 구분해야 할까요?

## 큰 그림

![Incremental scan and change detection flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-01-incremental-scan-and-change-detection.ko.png)

*Incremental scan and change detection flow*

이 그림에서는 현재 문서 상태와 이전 인덱싱 상태를 비교해 추가, 수정, 삭제만 처리하는 흐름을 봅니다. 증분 인덱싱은 속도 최적화가 아니라 인덱스와 원문 상태를 일치시키는 운영 계약입니다.

> 증분 인덱싱은 벡터 저장소 트릭이라기보다 무엇을 기억할지 정하는 운영 문제에 더 가깝습니다.

## 증분 스캔과 변경 감지

증분 인덱싱의 첫 이득은 비싼 후속 처리를 시작하기 전에 작업 집합을 먼저 줄이는 데 있습니다.

## 상태 저장소와 해시 비교

![State store and hash comparison flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-02-state-store-and-hash-comparison.ko.png)

*State store and hash comparison flow*

타임스탬프 옆에 내용 해시까지 두면, 변경 감지기는 mtime만 보는 방식보다 훨씬 믿을 만해집니다.

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
        'alpha.txt': 'This is the first document. It acts as the baseline for incremental indexing.\n',
        'beta.txt': 'This is the second document. We will revise it later.\n',
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
    files[1].write_text('This is the second document. Its contents changed, so it must be reprocessed.\n', encoding='utf-8')
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

## 이 코드에서 먼저 봐야 할 점

### 추가 수정 삭제 경로

![Added updated and deleted decision flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-01-added-updated-and-deleted-paths.ko.png)

*Added updated and deleted decision flow*

삭제를 별도 경로로 모델링해 두면, 인덱스 정리 역시 같은 상태 기계의 확장으로 다룰 수 있습니다.

- `IndexStateStore`는 해시, mtime, indexed_at을 함께 저장해 디버깅을 쉽게 만듭니다.
- 스크립트는 의도적으로 세 번 실행되어 `added → unchanged → updated` 수명 주기를 다시 보여 줍니다.
- 처음에는 JSON을 써서 로직을 투명하게 만들고, 같은 패턴을 나중에 데이터베이스로 옮기면 됩니다.

## 실무에서 자주 헷갈리는 지점

### 인덱스 버전과 실행 이력

![Index version and run history flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-02-index-version-and-run-history-flow.ko.png)

*Index version and run history flow*

규모가 커지면 무엇이 바뀌었는지 아는 것만큼, 어떤 실행이 어떤 인덱스 버전을 만들었는지 아는 일도 중요해집니다.

- mtime만 보는 체크는 빠르지만 변경을 과하게 잡을 수 있습니다. 그래서 내용 해시가 여전히 중요합니다.
- 증분 인덱싱에는 변경을 감지하는 단계와 변경을 반영하는 단계, 두 가지 관심사가 있습니다.
- 삭제 처리는 현재 파일 목록과 저장된 상태를 비교하는 추가 패스를 필요로 합니다.

## 체크리스트

- [ ] 상태 저장소에 해시와 타임스탬프를 함께 기록합니다.
- [ ] 수정 없는 두 번째 실행이 `unchanged`로 떨어집니다.
- [ ] 나중의 파일 수정이 `updated`로 분류됩니다.
- [ ] 삭제 처리를 어디에 끼워 넣을지 정했습니다.

## 정리

증분 인덱싱의 본질은 벡터 저장소보다 먼저 상태 기억에 있습니다. 무엇이 새 파일인지, 무엇이 바뀌지 않았는지, 무엇이 다시 처리되어야 하는지를 안정적으로 구분해야 뒤의 임베딩 비용을 아낄 수 있습니다.

해시와 작은 상태 저장소만으로도 그 출발점은 충분히 만들 수 있습니다. 다음 글에서는 이렇게 구분된 문서를 여러 파일 형식에서 공통 `Document` 계약으로 모으는 다중 포맷 파이프라인을 보겠습니다.

### 해시 기반 변경 감지를 파일 단위에서 청크 단위로 확장하기

파일 해시만 비교하면 문서가 바뀌었다는 사실은 알 수 있지만, 어느 청크가 바뀌었는지는 알기 어렵습니다. 대형 문서에서는 이 차이가 곧 비용 차이로 이어집니다. 그래서 파일 상태와 별개로 청크 해시 매니페스트를 함께 저장하면 부분 업데이트 경로를 열 수 있습니다.

```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

@dataclass(frozen=True)
class ChunkDigest:
    chunk_id: str
    content_hash: str

def build_chunk_manifest(chunks: list[str], source: str) -> list[ChunkDigest]:
    manifest: list[ChunkDigest] = []
    for index, chunk in enumerate(chunks):
        chunk_id = f'{source}#chunk-{index:04d}'
        manifest.append(ChunkDigest(chunk_id=chunk_id, content_hash=sha256_text(chunk)))
    return manifest

def diff_chunk_manifest(
    previous: list[ChunkDigest],
    current: list[ChunkDigest],
) -> tuple[list[str], list[str], list[str]]:
    prev_map = {item.chunk_id: item.content_hash for item in previous}
    cur_map = {item.chunk_id: item.content_hash for item in current}

    added = [chunk_id for chunk_id in cur_map if chunk_id not in prev_map]
    removed = [chunk_id for chunk_id in prev_map if chunk_id not in cur_map]
    updated = [
        chunk_id
        for chunk_id in cur_map
        if chunk_id in prev_map and cur_map[chunk_id] != prev_map[chunk_id]
    ]
    return added, updated, removed
```

이 방식은 문서 전체를 다시 임베딩하지 않고도 변경된 청크만 교체할 근거를 제공합니다. 특히 정책 문서처럼 일부 문단만 자주 바뀌는 코퍼스에서 효과가 큽니다.

### delta sync 실행 순서를 명시하는 패턴

증분 인덱싱에서 자주 생기는 실수는 삭제와 추가 순서를 섞는 것입니다. 같은 `chunk_id`를 다시 쓰는 시스템이라면 순서가 바뀔 때 오래된 벡터가 남을 수 있습니다. 그래서 delta sync는 단계별로 고정된 실행 순서를 갖는 편이 안전합니다.

```python
from __future__ import annotations

from collections.abc import Callable

def apply_delta_sync(
    *,
    added: list[str],
    updated: list[str],
    removed: list[str],
    delete_chunks: Callable[[list[str]], None],
    upsert_chunks: Callable[[list[str]], None],
) -> None:
    # 1) 삭제를 먼저 반영합니다.
    if removed:
        delete_chunks(removed)

    # 2) 업데이트 대상은 기존 벡터를 먼저 지우고 다시 올립니다.
    if updated:
        delete_chunks(updated)
        upsert_chunks(updated)

    # 3) 신규 청크를 마지막에 추가합니다.
    if added:
        upsert_chunks(added)
```

이 순서를 지키면 인덱스가 중간 상태에 머무는 시간을 줄일 수 있습니다. 또한 실행 로그를 `removed -> updated -> added` 순서로 읽을 수 있어 장애 분석도 빨라집니다.

### 파일 삭제를 탐지하는 역방향 스캔

추가와 수정은 현재 파일 목록에서 찾을 수 있지만, 삭제는 현재 목록에 나타나지 않습니다. 따라서 상태 저장소에 남아 있는 경로를 기준으로 역방향 스캔을 해야 합니다.

```python
from __future__ import annotations

from pathlib import Path

def detect_deleted_files(state_paths: set[str], live_paths: set[str]) -> list[str]:
    return sorted(state_paths - live_paths)

def collect_live_paths(root: Path) -> set[str]:
    return {
        str(path)
        for path in root.rglob('*')
        if path.is_file() and path.suffix.lower() in {'.txt', '.md', '.pdf'}
    }
```

삭제 탐지를 별도 함수로 분리하면, 문서 삭제 정책이 바뀔 때도 파이프라인 전체를 뜯어고치지 않고 해당 경계만 수정할 수 있습니다.

### 배치 단위 상태 갱신에서 지켜야 할 원칙

증분 작업은 중간 실패가 전제인 작업입니다. 그래서 변경 반영이 끝나기 전에 상태 파일을 먼저 저장하면 재시작 시점에 불일치가 생길 수 있습니다. 안전한 기본 원칙은 다음과 같습니다.

- 벡터 저장소 반영이 끝난 뒤에만 상태 저장소를 커밋합니다.
- 배치 실행 ID를 상태에 기록해 어떤 실행이 어떤 해시 집합을 만들었는지 남깁니다.
- 실패 시에는 상태 파일을 롤백하거나, 다음 실행이 이전 상태에서 다시 시작하게 합니다.

이 원칙을 지키면 증분 인덱싱은 단순한 성능 최적화가 아니라 신뢰 가능한 동기화 메커니즘이 됩니다. 즉, 파일 시스템 상태와 벡터 인덱스 상태를 같은 기준으로 비교하고, 같은 순서로 반영하는 운영 시스템으로 확장됩니다.

## 처음 질문으로 돌아가기

- **문서가 조금 바뀔 때마다 전체 인덱스를 다시 만들면 어떤 비용이 생길까요?**
  전체 재빌드는 시간이 오래 걸리고 비용이 커지며, 큰 corpus에서는 배포 중 검색 품질이 흔들릴 수 있습니다.

- **변경 감지는 파일 시간보다 왜 content hash와 상태 저장소가 더 안전할까요?**
  mtime은 복사·배포 과정에서 바뀌거나 보존될 수 있지만 content hash는 실제 내용 변경을 더 직접적으로 나타냅니다. 상태 저장소는 이전 hash와 chunk ID를 비교하게 해 줍니다.

- **삭제된 문서와 수정된 청크를 인덱스에서 어떻게 구분해야 할까요?**
  삭제는 해당 문서의 기존 벡터와 메타데이터를 제거해야 하고, 수정은 이전 chunk 세트를 새 chunk 세트로 교체해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [Document Ingestion 101 (3/6): 메타데이터 설계와 필터링](./03-metadata-filtering.md)
- **Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트 (현재 글)**
- Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 (예정)
- Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)
- [Python json documentation](https://docs.python.org/3/library/json.html)

### 검증에 도움 되는 자료

- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html)

Tags: RAG, Document Processing, LangChain, Python
