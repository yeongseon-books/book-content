---
title: 'Completing the document ingestion pipeline'
series: document-ingestion-101
episode: 6
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

# Completing the document ingestion pipeline

> Document Ingestion 101 (6/6)

Example code: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/en/06-pipeline-completion)

This post assembles all components from the series into one complete pipeline: PDF/Word/HTML/Markdown parsing, format-aware chunking, metadata attachment, incremental indexing, FAISS retrieval, and a LangChain RAG chain.

---

## Complete document ingestion pipeline

```python
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

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

# ── chunking config ─────────────────────────────────────────────────────────
CHUNKING_CONFIG = {
    "pdf":  {"chunk_size": 500, "chunk_overlap": 100},
    "docx": {"chunk_size": 500, "chunk_overlap": 100},
    "html": {"chunk_size": 300, "chunk_overlap": 50},
    "txt":  {"chunk_size": 400, "chunk_overlap": 80},
    "md":   {"chunk_size": 400, "chunk_overlap": 80},
}

SEPARATORS = ["\n\n", "\n", ". ", " "]

# ── format loaders ──────────────────────────────────────────────────────────
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
    ".pdf":      lambda p: _add_base_metadata(PyMuPDFLoader(p).load(), p, "pdf"),
    ".docx":     lambda p: _add_base_metadata(Docx2txtLoader(p).load(), p, "docx"),
    ".doc":      lambda p: _add_base_metadata(Docx2txtLoader(p).load(), p, "docx"),
    ".html":     lambda p: _add_base_metadata(BSHTMLLoader(p, bs_kwargs={"features": "html.parser"}).load(), p, "html"),
    ".htm":      lambda p: _add_base_metadata(BSHTMLLoader(p, bs_kwargs={"features": "html.parser"}).load(), p, "html"),
    ".txt":      lambda p: _add_base_metadata(TextLoader(p, encoding="utf-8").load(), p, "txt"),
    ".md":       lambda p: _add_base_metadata(TextLoader(p, encoding="utf-8").load(), p, "md"),
    ".markdown": lambda p: _add_base_metadata(TextLoader(p, encoding="utf-8").load(), p, "md"),
}

def load_file(file_path: str) -> list[Document]:
    suffix = Path(file_path).suffix.lower()
    loader = LOADERS.get(suffix)
    if not loader:
        raise ValueError(f"unsupported format: {suffix}")
    return loader(file_path)

# ── state store ─────────────────────────────────────────────────────────────
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

# ── chunking ────────────────────────────────────────────────────────────────
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

# ── main pipeline ───────────────────────────────────────────────────────────
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
                    self.state.mark(fp, [c.metadata["chunk_id"] for c in chunks])
                    stats["updated" if is_update else "added"] += 1
                    label = "updated" if is_update else "added"
                    print(f"  [{label}] {Path(fp).name}: {len(chunks)} chunks")

            except Exception as e:
                stats["errors"] += 1
                print(f"  [error] {fp}: {e}")

        self.state.save()
        self.vectorstore.save_local(str(self.index_dir / "faiss"))
        return stats

    def build_rag_chain(self, llm):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Answer the question using the documents below.\n"
                "If the answer is not in the documents, say so.\n\n"
                "Documents:\n{context}",
            ),
            ("human", "{question}"),
        ])

        def format_docs(docs: list) -> str:
            parts = []
            for doc in docs:
                src = doc.metadata.get("source", "unknown")
                parts.append(f"[source: {src}]\n{doc.page_content}")
            return "\n\n".join(parts)

        return (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
```

---

## Usage

```python
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    (tmpdir / "python_guide.txt").write_text(
        "Python Basics Guide\n\n"
        "Python is a high-level programming language created in 1991.\n"
        "It prioritizes readability above all else.\n\n"
        "Installation:\nDownload the latest version from python.org.\n"
        "Install packages with: pip install <name>.",
        encoding="utf-8",
    )
    (tmpdir / "faq.md").write_text(
        "# Frequently asked questions\n\n"
        "## What is the difference between Python and Java?\n\n"
        "Python is interpreted, Java is compiled.\n"
        "Python code is shorter and more readable.\n\n"
        "## Can I build web apps with Python?\n\n"
        "Yes. Django and FastAPI are the leading web frameworks.",
        encoding="utf-8",
    )

    pipeline = DocumentIngestionPipeline(str(tmpdir / ".index"))
    files = [str(tmpdir / "python_guide.txt"), str(tmpdir / "faq.md")]
    stats = pipeline.ingest(files)
    print(f"ingestion result: {stats}")

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
    )
    chain = pipeline.build_rag_chain(llm)

    questions = [
        "When was Python created?",
        "Can Python be used for web development?",
    ]
    for question in questions:
        answer = chain.invoke(question)
        print(f"\nquestion: {question}")
        print(f"answer: {answer}")
```

---

## Conclusion

This series covered the full document ingestion lifecycle: parsing, chunking, metadata, incremental indexing, multi-format support, and RAG chain assembly. Each stage is independently replaceable — swap the parser to support a new format, tune the chunking config to improve retrieval quality, replace the JSON state store with SQLite or Redis to scale further.

<!-- toc:begin -->
## In this series

- [PDF parsing and text extraction](./01-pdf-parsing.md)
- [Chunking strategies — optimizing by document type](./02-chunking-strategies.md)
- [Metadata design and filtering](./03-metadata-filtering.md)
- [Incremental indexing — updating only changed documents](./04-incremental-indexing.md)
- [Multi-format document pipeline](./05-multi-format-pipeline.md)
- **Completing the document ingestion pipeline (current)**

<!-- toc:end -->

---

## References

- [LangChain indexing API](https://python.langchain.com/docs/modules/data_connection/indexing/)
- [FAISS documentation](https://faiss.ai/)
- [pymupdf documentation](https://pymupdf.readthedocs.io/)

Tags: RAG, Document Processing, LangChain, Python
