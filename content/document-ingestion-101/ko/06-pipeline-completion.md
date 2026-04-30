# 문서 수집 파이프라인 완성

> 문서 수집과 인덱싱 101 시리즈 (6/6)

이 시리즈에서 다룬 모든 요소를 하나의 완전한 파이프라인으로 조합합니다. PDF/Word/HTML/Markdown 파싱, 문서 유형별 청킹, 메타데이터 부착, 증분 인덱싱, FAISS 검색, LangChain RAG 체인까지 모두 포함합니다.

---

## 완전한 문서 수집 파이프라인

```python
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from langchain.schema import Document
from langchain_community.document_loaders import (
    BSHTMLLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── 청킹 설정 ──────────────────────────────────────────────────────────────
CHUNKING_CONFIG = {
    "pdf": {"chunk_size": 500, "chunk_overlap": 100},
    "docx": {"chunk_size": 500, "chunk_overlap": 100},
    "html": {"chunk_size": 300, "chunk_overlap": 50},
    "txt": {"chunk_size": 400, "chunk_overlap": 80},
    "md": {"chunk_size": 400, "chunk_overlap": 80},
}

SEPARATORS = ["\n\n", "\n", ". ", " "]

# ── 포맷별 로더 ────────────────────────────────────────────────────────────
def _add_base_metadata(docs: list[Document], file_path: str, fmt: str) -> list[Document]:
    path = Path(file_path)
    stat = path.stat()
    for doc in docs:
        doc.metadata.update({
            "format": fmt,
            "source": path.name,
            "source_path": str(path),
            "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
            "file_size_kb": stat.st_size // 1024,
        })
    return docs

LOADERS = {
    ".pdf": lambda p: _add_base_metadata(PyMuPDFLoader(p).load(), p, "pdf"),
    ".docx": lambda p: _add_base_metadata(Docx2txtLoader(p).load(), p, "docx"),
    ".doc": lambda p: _add_base_metadata(Docx2txtLoader(p).load(), p, "docx"),
    ".html": lambda p: _add_base_metadata(BSHTMLLoader(p, bs_kwargs={"features": "html.parser"}).load(), p, "html"),
    ".htm": lambda p: _add_base_metadata(BSHTMLLoader(p, bs_kwargs={"features": "html.parser"}).load(), p, "html"),
    ".txt": lambda p: _add_base_metadata(TextLoader(p, encoding="utf-8").load(), p, "txt"),
    ".md": lambda p: _add_base_metadata(TextLoader(p, encoding="utf-8").load(), p, "md"),
    ".markdown": lambda p: _add_base_metadata(TextLoader(p, encoding="utf-8").load(), p, "md"),
}

def load_file(file_path: str) -> list[Document]:
    suffix = Path(file_path).suffix.lower()
    loader = LOADERS.get(suffix)
    if not loader:
        raise ValueError(f"지원하지 않는 포맷: {suffix}")
    return loader(file_path)

# ── 상태 저장소 ─────────────────────────────────────────────────────────────
class StateStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def save(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2))

    def hash_file(self, fp: str) -> str:
        h = hashlib.md5()
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def needs_update(self, fp: str) -> bool:
        stored = self.data.get(fp, {})
        mtime = Path(fp).stat().st_mtime
        if stored.get("mtime") == mtime:
            return False
        return stored.get("hash") != self.hash_file(fp)

    def mark(self, fp: str, chunk_ids: list[str]):
        self.data[fp] = {
            "hash": self.hash_file(fp),
            "mtime": Path(fp).stat().st_mtime,
            "indexed_at": datetime.now().isoformat(),
            "chunk_ids": chunk_ids,
        }

# ── 청킹 ───────────────────────────────────────────────────────────────────
def chunk_documents(docs: list[Document]) -> list[Document]:
    all_chunks = []
    for doc in docs:
        fmt = doc.metadata.get("format", "txt")
        cfg = CHUNKING_CONFIG.get(fmt, CHUNKING_CONFIG["txt"])
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
            separators=SEPARATORS,
        )
        chunks = splitter.split_documents([doc])
        for idx, chunk in enumerate(chunks):
            cid = hashlib.md5(chunk.page_content.encode()).hexdigest()[:8]
            chunk.metadata["chunk_id"] = f"{Path(doc.metadata['source']).stem}_c{idx}_{cid}"
            chunk.metadata["chunk_idx"] = idx
        all_chunks.extend(chunks)
    return all_chunks

# ── 메인 파이프라인 ─────────────────────────────────────────────────────────
class DocumentIngestionPipeline:
    def __init__(self, index_dir: str):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.state = StateStore(str(self.index_dir / "state.json"))
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        faiss_path = self.index_dir / "faiss"
        if faiss_path.exists():
            self.vectorstore = FAISS.load_local(
                str(faiss_path), self.embedding, allow_dangerous_deserialization=True
            )
        else:
            dummy = Document(page_content="__init__", metadata={"_dummy": True})
            self.vectorstore = FAISS.from_documents([dummy], self.embedding)

    def ingest(self, file_paths: list[str]) -> dict:
        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

        for fp in file_paths:
            try:
                if not self.state.needs_update(fp) and fp in self.state.data:
                    stats["skipped"] += 1
                    continue

                is_update = fp in self.state.data
                docs = load_file(fp)
                chunks = chunk_documents(docs)

                if chunks:
                    self.vectorstore.add_documents(chunks)
                    chunk_ids = [c.metadata["chunk_id"] for c in chunks]
                    self.state.mark(fp, chunk_ids)
                    stats["updated" if is_update else "added"] += 1
                    print(f"  [{'updated' if is_update else 'added'}] {Path(fp).name}: {len(chunks)}개 청크")

            except Exception as e:
                stats["errors"] += 1
                print(f"  [오류] {fp}: {e}")

        self.state.save()
        self.vectorstore.save_local(str(self.index_dir / "faiss"))
        return stats

    def build_rag_chain(self, llm):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "다음 문서를 참고해서 질문에 답하세요.\n"
                "문서에 없는 내용은 '문서에서 찾을 수 없습니다'라고 하세요.\n\n"
                "문서:\n{context}",
            ),
            ("human", "{question}"),
        ])

        def format_docs(docs: list) -> str:
            parts = []
            for doc in docs:
                src = doc.metadata.get("source", "알 수 없음")
                parts.append(f"[출처: {src}]\n{doc.page_content}")
            return "\n\n".join(parts)

        return (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
```

---

## 사용 예시

```python
import tempfile

# 임시 파일 생성
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    (tmpdir / "python_guide.txt").write_text(
        "파이썬 기초 가이드\n\n"
        "파이썬은 1991년에 만들어진 고수준 프로그래밍 언어입니다.\n"
        "가독성을 최우선으로 설계되었습니다.\n\n"
        "설치 방법:\npython.org에서 최신 버전을 다운로드합니다.\n"
        "pip install 명령으로 패키지를 설치합니다.",
        encoding="utf-8",
    )
    (tmpdir / "faq.md").write_text(
        "# 자주 묻는 질문\n\n"
        "## 파이썬과 자바의 차이는?\n\n"
        "파이썬은 인터프리터 언어, 자바는 컴파일 언어입니다.\n"
        "파이썬은 코드가 짧고 가독성이 높습니다.\n\n"
        "## 파이썬으로 웹 개발이 가능한가요?\n\n"
        "네, Django와 FastAPI가 대표적인 웹 프레임워크입니다.",
        encoding="utf-8",
    )

    # 파이프라인 초기화
    pipeline = DocumentIngestionPipeline(str(tmpdir / ".index"))

    # 문서 수집
    files = [str(tmpdir / "python_guide.txt"), str(tmpdir / "faq.md")]
    stats = pipeline.ingest(files)
    print(f"수집 결과: {stats}")

    # RAG 체인 구성
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
    )
    chain = pipeline.build_rag_chain(llm)

    # 질문
    questions = [
        "파이썬은 언제 만들어졌나요?",
        "파이썬으로 웹 개발을 할 수 있나요?",
    ]
    for question in questions:
        answer = chain.invoke(question)
        print(f"\n질문: {question}")
        print(f"답변: {answer}")
```

---

## 마무리

이 시리즈에서는 PDF 파싱부터 완전한 RAG 파이프라인까지 문서 수집의 전 과정을 다뤘습니다. 각 단계는 독립적으로 교체 가능합니다. 파서만 바꿔도 새 포맷을 지원하고, 청킹 설정만 조정해도 검색 품질이 달라집니다. 상태 저장소를 JSON에서 SQLite나 Redis로 교체하면 더 대규모 시스템으로 확장할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [메타데이터 설계와 필터링](./03-metadata-filtering.md)
- [증분 인덱싱 — 변경된 문서만 업데이트](./04-incremental-indexing.md)
- [다중 포맷 문서 파이프라인](./05-multi-format-pipeline.md)
- **문서 수집 파이프라인 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [LangChain 인덱싱 API](https://python.langchain.com/docs/modules/data_connection/indexing/)
- [FAISS 공식 문서](https://faiss.ai/)
- [pymupdf 공식 문서](https://pymupdf.readthedocs.io/)

Tags: RAG, Document Processing, LangChain, Python
