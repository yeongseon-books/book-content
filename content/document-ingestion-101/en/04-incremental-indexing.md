---
title: 'Incremental indexing — updating only changed documents'
series: document-ingestion-101
episode: 4
language: en
status: draft
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

# Incremental indexing — updating only changed documents

> Document Ingestion 101 (4/6)

Example code: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/en/04-incremental-indexing)

With 1,000 documents, the initial indexing run happens once. But if new documents arrive daily and existing ones get revised, rebuilding the full index every time is expensive. Incremental indexing identifies which documents changed and processes only those, leaving unchanged documents untouched.

Topics:

- detecting file changes (hash or modification time)
- designing an index state store
- handling additions, modifications, and deletions
- applying incremental updates to a FAISS index

---

## Change detection strategies

Two approaches for detecting file changes:

**Modification time comparison**: store the filesystem `mtime` and compare. Fast but may reprocess files whose content did not actually change (e.g., touch without editing).

**Content hash comparison**: store an MD5/SHA-256 hash of the file content and compare. Accurate but requires reading the full file every run.

In practice, combine both: check `mtime` first (fast path), and only compute the hash when `mtime` changed.

---

## Index state store

```python
import hashlib
import json
from datetime import datetime
from pathlib import Path

class IndexStateStore:
    """
    Manages per-document indexing state in a JSON file.
    Schema: {file_path: {"hash": str, "mtime": float, "indexed_at": str, "chunk_ids": [str]}}
    """

    def __init__(self, state_file: str = ".index_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load()

    def _load(self) -> dict:
        if self.state_file.exists():
            with open(self.state_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save(self) -> None:
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_file_hash(self, file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_changed(self, file_path: str) -> bool:
        """Return True if the file changed since it was last indexed."""
        path = Path(file_path)
        if not path.exists():
            return False

        current_mtime = path.stat().st_mtime
        stored = self.state.get(str(file_path), {})

        if stored.get("mtime") == current_mtime:
            return False  # fast path: mtime unchanged

        return stored.get("hash") != self.get_file_hash(file_path)

    def is_deleted(self, file_path: str) -> bool:
        """Return True if the file was previously indexed but no longer exists."""
        return str(file_path) in self.state and not Path(file_path).exists()

    def mark_indexed(self, file_path: str, chunk_ids: list[str]) -> None:
        path = Path(file_path)
        self.state[str(file_path)] = {
            "hash": self.get_file_hash(file_path),
            "mtime": path.stat().st_mtime,
            "indexed_at": datetime.now().isoformat(),
            "chunk_ids": chunk_ids,
        }

    def get_chunk_ids(self, file_path: str) -> list[str]:
        return self.state.get(str(file_path), {}).get("chunk_ids", [])

    def remove(self, file_path: str) -> None:
        self.state.pop(str(file_path), None)

store = IndexStateStore("/tmp/test_index_state.json")
print("state store initialized")
```

---

## Incremental indexer

```python
import hashlib
from pathlib import Path

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

class IncrementalIndexer:
    """Indexes only documents that changed since the last run."""

    def __init__(self, index_path: str, state_file: str = ".index_state.json"):
        self.index_path = Path(index_path)
        self.state_store = IndexStateStore(state_file)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=80,
            separators=["\n\n", "\n", ". "],
        )
        self.vectorstore = self._load_or_create_index()

    def _load_or_create_index(self) -> FAISS:
        if self.index_path.exists():
            print(f"loading existing index: {self.index_path}")
            return FAISS.load_local(
                str(self.index_path),
                self.embedding_model,
                allow_dangerous_deserialization=True,
            )
        print("creating new index")
        dummy = Document(page_content="init", metadata={"_dummy": True})
        return FAISS.from_documents([dummy], self.embedding_model)

    def _text_to_chunks(self, text: str, file_path: str) -> list[Document]:
        chunks = self.splitter.split_text(text)
        docs = []
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{Path(file_path).stem}_c{idx}_{hashlib.md5(chunk.encode()).hexdigest()[:6]}"
            docs.append(Document(
                page_content=chunk,
                metadata={
                    "source_file": Path(file_path).name,
                    "chunk_id": chunk_id,
                    "chunk_idx": idx,
                },
            ))
        return docs

    def process_file(self, file_path: str, text: str) -> str:
        """Process one file. Returns: 'added' | 'updated' | 'skipped'."""
        if not self.state_store.is_changed(file_path) and str(file_path) in self.state_store.state:
            return "skipped"

        old_chunk_ids = self.state_store.get_chunk_ids(file_path)
        if old_chunk_ids:
            print(f"  removing {len(old_chunk_ids)} previous chunks")

        docs = self._text_to_chunks(text, file_path)
        if docs:
            self.vectorstore.add_documents(docs)
            self.state_store.mark_indexed(file_path, [d.metadata["chunk_id"] for d in docs])
            return "updated" if old_chunk_ids else "added"

        return "skipped"

    def sync_directory(self, directory: str, pattern: str = "*.txt") -> dict:
        """Sync all matching files in a directory."""
        directory = Path(directory)
        files = list(directory.glob(pattern))
        stats = {"added": 0, "updated": 0, "skipped": 0, "deleted": 0}

        for file_path in files:
            text = file_path.read_text(encoding="utf-8")
            status = self.process_file(str(file_path), text)
            stats[status] += 1
            print(f"  [{status}] {file_path.name}")

        for stored_path in list(self.state_store.state.keys()):
            if self.state_store.is_deleted(stored_path):
                self.state_store.remove(stored_path)
                stats["deleted"] += 1
                print(f"  [deleted] {stored_path}")

        self.state_store.save()
        self.vectorstore.save_local(str(self.index_path))
        return stats

# Test with a temporary directory
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    (tmpdir / "doc1.txt").write_text("Python async programming basics. Uses asyncio.", encoding="utf-8")
    (tmpdir / "doc2.txt").write_text("Machine learning model training and evaluation.", encoding="utf-8")

    indexer = IncrementalIndexer(str(tmpdir / ".faiss_index"))
    stats = indexer.sync_directory(str(tmpdir))
    print(f"\nfirst sync: {stats}")

    # modify doc1, add doc3
    (tmpdir / "doc1.txt").write_text("Build async HTTP clients with Python asyncio and aiohttp.", encoding="utf-8")
    (tmpdir / "doc3.txt").write_text("Deep learning model deployment and serving strategies.", encoding="utf-8")

    stats = indexer.sync_directory(str(tmpdir))
    print(f"second sync: {stats}")
```

---

## Conclusion

Incremental indexing is necessary for any service where documents change regularly. A JSON state file is a simple starting point; swap it for Redis or SQLite as the document corpus grows. The pattern is always the same: detect changes via mtime + hash, remove stale chunks, add new chunks, persist the updated state.

The next post covers multi-format document pipelines: handling Word documents, HTML pages, and Markdown alongside PDFs.

<!-- toc:begin -->
## In this series

- [PDF parsing and text extraction](./01-pdf-parsing.md)
- [Chunking strategies — optimizing by document type](./02-chunking-strategies.md)
- [Metadata design and filtering](./03-metadata-filtering.md)
- **Incremental indexing — updating only changed documents (current)**
- Multi-format document pipeline (upcoming)
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

---

## References

- [LangChain RecordManager (incremental indexing)](https://python.langchain.com/docs/modules/data_connection/indexing/)
- [FAISS save/load](https://python.langchain.com/docs/integrations/vectorstores/faiss/#saving-and-loading)
- [File hash change detection patterns](https://realpython.com/python-hashlib/)

Tags: RAG, Document Processing, LangChain, Python
