---
title: "Document Ingestion 101 (4/6): Incremental indexing — updating only changed documents"
series: document-ingestion-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-15'
seo_description: Incremental indexing is less a vector-store trick and more an operational
  memory problem.
---

# Document Ingestion 101 (4/6): Incremental indexing — updating only changed documents

Rebuilding an entire index is simple, but it stops scaling surprisingly quickly. Once the corpus grows, the real question becomes how to remember what changed and skip the rest safely.

This is the fourth post in the Document Ingestion 101 series. Here, we use file hashes and a small state store to separate added, unchanged, and updated documents.

![Incremental scan and change detection flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-01-incremental-scan-and-change-detection.en.png)
*Incremental scan and change detection flow*
> Incremental indexing is less a vector-store trick and more an operational memory problem.

## Questions to Keep in Mind

- What cost appears when every small document change rebuilds the full index?
- Why are content hashes and a state store safer than file timestamps for change detection?
- How should deleted documents and modified chunks be separated in the index?

## Incremental scan and change detection

The first win in incremental indexing is narrowing the work set before any expensive downstream processing starts.

## State store and hash comparison

![State store and hash comparison flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-02-state-store-and-hash-comparison.en.png)

*State store and hash comparison flow*
A content hash next to timestamps makes the change detector much more trustworthy than mtime alone.

## Runnable example

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

## How to run it

```bash
python main.py
```

## Verified run output

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

## What to notice in this code

### Added updated and deleted paths

![Added updated and deleted decision flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-01-added-updated-and-deleted-paths.en.png)

*Added updated and deleted decision flow*
Once deletion is modeled as its own path, index cleanup becomes an extension of the same state machine.

- `IndexStateStore` keeps hash, mtime, and indexed_at together, which makes debugging easier.
- The script intentionally runs three passes to replay the added → unchanged → updated lifecycle.
- Using JSON first keeps the logic transparent before moving the same pattern into a database.

## Where engineers get confused

### Index version and run history flow

![Index version and run history flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/04/04-02-index-version-and-run-history-flow.en.png)

*Index version and run history flow*
Past a certain scale, knowing which run produced which index version becomes as important as change detection itself.

- mtime-only checks are fast but can over-report changes. That is why content hashes still matter.
- Incremental indexing has two separate concerns: detecting change and applying the change.
- Deletion handling needs an extra pass that compares the current file list with stored state.

## Checklist

- [ ] The state store records both hash and timestamp.
- [ ] A second run without edits resolves to unchanged.
- [ ] A later file edit resolves to updated.
- [ ] You identified where deletion handling would plug in.

## Answering the Opening Questions

- **What cost appears when every small document change rebuilds the full index?**
  Full rebuilds take time and cost more, and at larger corpus sizes they can disrupt search quality during deployment.

- **Why are content hashes and a state store safer than file timestamps for change detection?**
  Timestamps can change or be preserved by copy and deploy workflows, while content hashes represent actual content changes. A state store lets you compare previous hashes and chunk ids.

- **How should deleted documents and modified chunks be separated in the index?**
  Deletes should remove existing vectors and metadata for that document; updates should replace the previous chunk set with the new one.

<!-- toc:begin -->
## In this series

- [Document Ingestion 101 (1/6): PDF parsing and text extraction](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): Chunking strategies — optimizing by document type](./02-chunking-strategies.md)
- [Document Ingestion 101 (3/6): Metadata design and filtering](./03-metadata-filtering.md)
- **Document Ingestion 101 (4/6): Incremental indexing — updating only changed documents (current)**
- Document Ingestion 101 (5/6): Multi-format document pipeline (upcoming)
- Document Ingestion 101 (6/6): Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

## References

### Official docs

- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)
- [Python json documentation](https://docs.python.org/3/library/json.html)

### Verification-friendly sources

- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html)

Tags: RAG, Document Processing, LangChain, Python
