---
title: 'Multi-format document pipeline'
series: document-ingestion-101
episode: 5
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

# Multi-format document pipeline

> Document Ingestion 101 (5/6)

Real services do not process only PDFs. Word documents, HTML pages, Markdown files, and plain text files arrive together. The pipeline needs to select the right parser for each format and convert every source into a common representation.

Topics:

- LangChain DocumentLoaders by format
- automatic format detection
- unified document processing pipeline
- stripping noise from HTML

---

## LangChain DocumentLoader catalog

```python
from langchain_community.document_loaders import (
    PyMuPDFLoader,               # PDF — most accurate
    Docx2txtLoader,              # Word (.docx)
    UnstructuredHTMLLoader,      # HTML (requires unstructured package)
    BSHTMLLoader,                # HTML (BeautifulSoup4)
    TextLoader,                  # plain text
    UnstructuredMarkdownLoader,  # Markdown
    CSVLoader,                   # CSV
    JSONLoader,                  # JSON
)
```

---

## Per-format loader functions

```python
from pathlib import Path

from langchain.schema import Document
from langchain_community.document_loaders import (
    BSHTMLLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)

def load_pdf(file_path: str) -> list[Document]:
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "pdf"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_word(file_path: str) -> list[Document]:
    loader = Docx2txtLoader(file_path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "docx"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_html(file_path: str) -> list[Document]:
    loader = BSHTMLLoader(file_path, bs_kwargs={"features": "html.parser"})
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "html"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_text(file_path: str, encoding: str = "utf-8") -> list[Document]:
    loader = TextLoader(file_path, encoding=encoding)
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "txt"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_markdown(file_path: str) -> list[Document]:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "md"
        doc.metadata["source"] = Path(file_path).name
    return docs
```

---

## Format-detection router

```python
LOADER_MAP = {
    ".pdf": load_pdf,
    ".docx": load_word,
    ".doc": load_word,
    ".html": load_html,
    ".htm": load_html,
    ".txt": load_text,
    ".md": load_markdown,
    ".markdown": load_markdown,
}

def load_document(file_path: str) -> list[Document]:
    """Select the appropriate loader based on file extension."""
    suffix = Path(file_path).suffix.lower()
    loader_fn = LOADER_MAP.get(suffix)

    if loader_fn is None:
        raise ValueError(
            f"unsupported format: {suffix}\nsupported: {list(LOADER_MAP.keys())}"
        )

    docs = loader_fn(file_path)
    print(f"  [{suffix[1:].upper()}] {Path(file_path).name}: {len(docs)} page(s)/section(s)")
    return docs
```

---

## Unified pipeline

```python
import tempfile
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_directory(
    directory: str,
    patterns: list[str] = None,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> FAISS:
    """Load, chunk, and index all supported documents in a directory."""
    if patterns is None:
        patterns = ["*.pdf", "*.docx", "*.html", "*.txt", "*.md"]

    directory = Path(directory)
    all_files = []
    for pattern in patterns:
        all_files.extend(directory.glob(pattern))

    print(f"files found: {len(all_files)}")

    all_docs = []
    for file_path in all_files:
        try:
            docs = load_document(str(file_path))
            all_docs.extend(docs)
        except Exception as e:
            print(f"  [error] {file_path.name}: {e}")

    if not all_docs:
        raise ValueError("no documents to process")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(all_docs)
    print(f"total chunks: {len(chunks)}")

    format_counts: dict[str, int] = {}
    for chunk in chunks:
        fmt = chunk.metadata.get("format", "unknown")
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    print(f"chunks by format: {format_counts}")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    print(f"index ready: {vectorstore.index.ntotal} vectors")
    return vectorstore

# Test with temporary files
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    (tmpdir / "guide.txt").write_text(
        "Python Installation Guide\n\nDownload Python 3.10 or later from python.org.\nInstall packages with: pip install <name>.",
        encoding="utf-8",
    )
    (tmpdir / "readme.md").write_text(
        "# Project overview\n\nThis project implements a RAG pipeline.\n\n## Features\n\n- Document indexing\n- Question answering",
        encoding="utf-8",
    )
    (tmpdir / "index.html").write_text(
        "<html><body><h1>Product introduction</h1><p>AI-powered document search system.</p></body></html>",
        encoding="utf-8",
    )

    vectorstore = process_directory(str(tmpdir))

    results = vectorstore.similarity_search("Python installation", k=2)
    print("\nsearch results:")
    for r in results:
        print(f"  [{r.metadata.get('format')}] {r.page_content[:80]}")
```

---

## Conclusion

The key to multi-format pipelines is the common interface: every format converter returns `list[Document]`. The router maps file extensions to converter functions. Adding a new format means writing one loader function and one LOADER_MAP entry — the chunking and indexing stages remain unchanged.

The final post assembles all components into a complete production document ingestion pipeline.

<!-- toc:begin -->
## In this series

- [PDF parsing and text extraction](./01-pdf-parsing.md)
- [Chunking strategies — optimizing by document type](./02-chunking-strategies.md)
- [Metadata design and filtering](./03-metadata-filtering.md)
- [Incremental indexing — updating only changed documents](./04-incremental-indexing.md)
- **Multi-format document pipeline (current)**
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

---

## References

- [LangChain DocumentLoaders](https://python.langchain.com/docs/integrations/document_loaders/)
- [Unstructured.io library](https://unstructured.io/)
- [python-docx](https://python-docx.readthedocs.io/)

Tags: RAG, Document Processing, LangChain, Python
