---
title: '증분 인덱싱 — 변경된 문서만 업데이트'
series: document-ingestion-101
episode: 4
language: ko
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

# 증분 인덱싱 — 변경된 문서만 업데이트

> 문서 수집과 인덱싱 101 시리즈 (4/6)

예제 코드: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/ko/04-incremental-indexing)

문서가 1,000개라면 처음 인덱싱은 한 번만 하면 됩니다. 하지만 매일 새 문서가 추가되고 기존 문서가 수정된다면 어떻게 할까요? 매번 전체를 다시 인덱싱하면 시간과 비용이 큽니다. 증분 인덱싱은 변경된 문서만 찾아서 처리하고, 변경되지 않은 문서는 그대로 두는 방법입니다.

다룰 내용은 다음과 같습니다.

- 파일 변경 감지 (해시 또는 수정 날짜)
- 인덱스 상태 저장소 설계
- 추가/수정/삭제 처리
- FAISS 인덱스에 증분 업데이트 적용

---

<!-- ebook-only:start -->

이 장의 핵심: **증분 인덱싱은 바뀐 문서만 재처리한다.** 해시 또는 수정 시각으로 변경을 감지하고 해당 청크만 업데이트한다.

## 이 장의 위치

이 글은 시리즈 6편 중 4번째 장입니다.
앞 장에서는 **메타데이터 설계와 필터링**을 다뤘습니다.
이 장을 마치면 다음 장에서 **다중 포맷 문서 파이프라인**으로 이어집니다.
<!-- ebook-only:end -->

## 변경 감지 전략

파일이 변경됐는지 감지하는 방법은 두 가지입니다.

**수정 날짜 비교**: 파일 시스템의 `mtime`을 저장해두고 비교합니다. 빠르지만 파일 내용이 같아도 수정 날짜가 바뀌면 재처리합니다.

**내용 해시 비교**: 파일 내용의 MD5/SHA-256 해시를 저장해두고 비교합니다. 느리지만 내용이 정말 바뀐 경우만 감지합니다.

실무에서는 두 방법을 조합합니다. 수정 날짜가 바뀐 파일만 해시를 계산해서 실제 변경 여부를 확인합니다.

---

## 인덱스 상태 저장소

```python
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

class IndexStateStore:
    """
    각 문서의 인덱싱 상태를 JSON 파일로 관리합니다.
    저장 형식: {file_path: {"hash": str, "mtime": float, "indexed_at": str, "chunk_ids": [str]}}
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
        """파일 내용의 MD5 해시를 반환합니다."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_changed(self, file_path: str) -> bool:
        """파일이 마지막 인덱싱 이후 변경됐는지 확인합니다."""
        path = Path(file_path)
        if not path.exists():
            return False

        current_mtime = path.stat().st_mtime
        stored = self.state.get(str(file_path), {})

        # 수정 날짜가 같으면 변경 없음 (빠른 경로)
        if stored.get("mtime") == current_mtime:
            return False

        # 수정 날짜가 다르면 해시로 실제 변경 여부 확인
        current_hash = self.get_file_hash(file_path)
        return stored.get("hash") != current_hash

    def is_deleted(self, file_path: str) -> bool:
        """이전에 인덱싱했지만 현재 파일이 없는지 확인합니다."""
        return str(file_path) in self.state and not Path(file_path).exists()

    def mark_indexed(self, file_path: str, chunk_ids: list[str]) -> None:
        """파일의 인덱싱 상태를 기록합니다."""
        path = Path(file_path)
        self.state[str(file_path)] = {
            "hash": self.get_file_hash(file_path),
            "mtime": path.stat().st_mtime,
            "indexed_at": datetime.now().isoformat(),
            "chunk_ids": chunk_ids,
        }

    def get_chunk_ids(self, file_path: str) -> list[str]:
        """파일의 이전 청크 ID 목록을 반환합니다."""
        return self.state.get(str(file_path), {}).get("chunk_ids", [])

    def remove(self, file_path: str) -> None:
        """파일 상태를 삭제합니다."""
        self.state.pop(str(file_path), None)

# 사용 예시
store = IndexStateStore("/tmp/test_index_state.json")
print("상태 저장소 초기화 완료")
```

---

## 증분 인덱싱 구현

```python
import hashlib
from pathlib import Path

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

class IncrementalIndexer:
    """
    변경된 문서만 인덱싱하는 증분 인덱서입니다.
    """

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
        """저장된 인덱스를 로드하거나 새로 만듭니다."""
        if self.index_path.exists():
            print(f"기존 인덱스 로드: {self.index_path}")
            return FAISS.load_local(
                str(self.index_path),
                self.embedding_model,
                allow_dangerous_deserialization=True,
            )
        else:
            print("새 인덱스 생성")
            # 더미 문서로 빈 인덱스 초기화
            dummy_doc = Document(page_content="init", metadata={"_dummy": True})
            vs = FAISS.from_documents([dummy_doc], self.embedding_model)
            return vs

    def _text_to_chunks(self, text: str, file_path: str) -> list[Document]:
        """텍스트를 청크 Document 목록으로 변환합니다."""
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
        """
        단일 파일을 처리합니다. 반환값: "added" | "updated" | "skipped"
        """
        if not self.state_store.is_changed(file_path) and str(file_path) in self.state_store.state:
            return "skipped"

        # 이전 청크 삭제 (수정된 경우)
        old_chunk_ids = self.state_store.get_chunk_ids(file_path)
        if old_chunk_ids:
            # FAISS는 직접 삭제가 제한적 — 재구성이 필요한 경우 별도 처리
            print(f"  이전 청크 {len(old_chunk_ids)}개 제거 예정")

        # 새 청크 추가
        docs = self._text_to_chunks(text, file_path)
        if docs:
            self.vectorstore.add_documents(docs)
            chunk_ids = [d.metadata["chunk_id"] for d in docs]
            self.state_store.mark_indexed(file_path, chunk_ids)
            return "updated" if old_chunk_ids else "added"

        return "skipped"

    def sync_directory(self, directory: str, pattern: str = "*.txt") -> dict:
        """
        디렉터리의 모든 파일을 동기화합니다.
        """
        directory = Path(directory)
        files = list(directory.glob(pattern))

        stats = {"added": 0, "updated": 0, "skipped": 0, "deleted": 0}

        for file_path in files:
            text = file_path.read_text(encoding="utf-8")
            status = self.process_file(str(file_path), text)
            stats[status] += 1
            print(f"  [{status}] {file_path.name}")

        # 삭제된 파일 처리
        for stored_path in list(self.state_store.state.keys()):
            if self.state_store.is_deleted(stored_path):
                self.state_store.remove(stored_path)
                stats["deleted"] += 1
                print(f"  [deleted] {stored_path}")

        self.state_store.save()
        self.vectorstore.save_local(str(self.index_path))
        return stats

# 테스트: 임시 디렉터리에 텍스트 파일 생성
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    # 초기 파일 생성
    (tmpdir / "doc1.txt").write_text("파이썬 비동기 프로그래밍의 기초. asyncio를 사용합니다.", encoding="utf-8")
    (tmpdir / "doc2.txt").write_text("머신러닝 모델 훈련과 평가 방법.", encoding="utf-8")

    indexer = IncrementalIndexer(str(tmpdir / ".faiss_index"))
    stats = indexer.sync_directory(str(tmpdir))
    print(f"\n1차 동기화: {stats}")

    # doc1 수정, doc3 추가
    (tmpdir / "doc1.txt").write_text("파이썬 asyncio와 aiohttp로 비동기 HTTP 클라이언트를 만듭니다.", encoding="utf-8")
    (tmpdir / "doc3.txt").write_text("딥러닝 모델 배포와 서빙 방법.", encoding="utf-8")

    stats = indexer.sync_directory(str(tmpdir))
    print(f"2차 동기화: {stats}")
```

---

## 마무리

증분 인덱싱은 문서가 자주 변경되는 실제 서비스에서 필수입니다. 상태 저장소를 JSON 파일로 관리하면 간단하게 시작할 수 있고, 나중에 Redis나 SQLite로 교체해서 더 견고하게 만들 수 있습니다.

다음 글에서는 PDF 외에 Word, HTML, Markdown 등 다양한 포맷을 처리하는 다중 포맷 파이프라인을 다룹니다.

<!-- blog-only:start -->
다음 글: [다중 포맷 문서 파이프라인](./05-multi-format-pipeline.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [메타데이터 설계와 필터링](./03-metadata-filtering.md)
- **증분 인덱싱 — 변경된 문서만 업데이트 (현재 글)**
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain RecordManager (증분 인덱싱)](https://python.langchain.com/docs/modules/data_connection/indexing/)
- [FAISS save/load](https://python.langchain.com/docs/integrations/vectorstores/faiss/#saving-and-loading)
- [파일 해시 변경 감지 패턴](https://realpython.com/python-hashlib/)

Tags: RAG, Document Processing, LangChain, Python
