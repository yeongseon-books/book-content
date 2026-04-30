# PDF parsing and text extraction

> Document Ingestion 101 (1/6)

The first step in a RAG pipeline is pulling text out of documents. Plain text files are trivial to read, but most real-world documents arrive as PDFs. PDF is a complex format where text, images, tables, and layout information are interleaved — a naive read rarely gives you the right content in the right order. This post covers PDF text extraction step by step.

Topics:

- extracting text with PyMuPDF
- comparing with pypdf
- preserving per-page metadata
- handling tables and multi-column layouts

---

## Choosing a PDF parsing library

Python has three main PDF libraries.

**pymupdf** (`fitz`): fastest and most accurate. Extracts text block positions, font sizes, and image data. Preserves reading order reliably in complex layouts.

**pypdf**: pure Python with minimal dependencies. Sufficient for simple PDFs but reading order breaks on complex layouts.

**pdfplumber**: strong table extraction. Slower than pymupdf but the right choice for heavily tabular documents.

For a general RAG pipeline, use pymupdf by default and add pdfplumber for table-heavy documents.

---

## Basic pymupdf usage

```bash
pip install pymupdf pypdf pdfplumber langchain-community
```

```python
from pathlib import Path

import fitz  # pymupdf

def extract_text_pymupdf(pdf_path: str) -> list[dict]:
    """
    Extract text page by page from a PDF.
    Returns: [{"page_num": int, "text": str, "char_count": int}]
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages.append({
            "page_num": page_num + 1,
            "text": text.strip(),
            "char_count": len(text.strip()),
        })

    doc.close()
    return pages

def extract_blocks_pymupdf(pdf_path: str) -> list[dict]:
    """
    Extract text at the block level.
    block_type: 0=text, 1=image
    """
    doc = fitz.open(pdf_path)
    all_blocks = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")

        for block_idx, block in enumerate(blocks):
            x0, y0, x1, y1, text, block_no, block_type = block
            if block_type == 0 and text.strip():
                all_blocks.append({
                    "page_num": page_num + 1,
                    "block_num": block_idx,
                    "text": text.strip(),
                    "bbox": (x0, y0, x1, y1),
                    "block_type": block_type,
                })

    doc.close()
    return all_blocks

def create_sample_pdf(output_path: str) -> None:
    """Create a sample PDF for testing."""
    doc = fitz.open()

    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Python Programming Guide\n\n"
        "Chapter 1: Introduction\n"
        "Python is a programming language created by Guido van Rossum in 1991.\n"
        "It was designed for readability and uses indentation to delimit code blocks.\n\n"
        "Chapter 2: Features\n"
        "Dynamic typing, automatic memory management, and a rich library ecosystem are its hallmarks.\n"
        "It is widely used in web development, data science, and AI.",
        fontsize=12,
        fontname="helv",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (50, 50),
        "Chapter 3: Installation\n"
        "Download the latest version from python.org.\n"
        "Python 3.10 or later is recommended for new projects.\n\n"
        "Chapter 4: Package management\n"
        "Install packages with: pip install <package-name>\n"
        "Use virtual environments (venv) to isolate per-project dependencies.",
        fontsize=12,
        fontname="helv",
    )

    doc.save(output_path)
    doc.close()
    print(f"sample PDF created: {output_path}")

create_sample_pdf("/tmp/sample_en.pdf")
pages = extract_text_pymupdf("/tmp/sample_en.pdf")
for page in pages:
    print(f"\n=== page {page['page_num']} ({page['char_count']} chars) ===")
    print(page["text"][:200])
```

---

## Comparing with pypdf

```python
from pypdf import PdfReader

def extract_text_pypdf(pdf_path: str) -> list[dict]:
    """Extract text page by page using pypdf."""
    reader = PdfReader(pdf_path)
    pages = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({
            "page_num": page_num + 1,
            "text": text.strip(),
            "char_count": len(text.strip()),
        })

    return pages

pymupdf_pages = extract_text_pymupdf("/tmp/sample_en.pdf")
pypdf_pages = extract_text_pypdf("/tmp/sample_en.pdf")

print("pymupdf total chars:", sum(p["char_count"] for p in pymupdf_pages))
print("pypdf total chars:", sum(p["char_count"] for p in pypdf_pages))
```

---

## Extracting PDF metadata

```python
def extract_metadata(pdf_path: str) -> dict:
    """Extract file-level metadata from a PDF."""
    doc = fitz.open(pdf_path)

    metadata = {
        "file_path": str(pdf_path),
        "file_name": Path(pdf_path).name,
        "page_count": len(doc),
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "creator": doc.metadata.get("creator", ""),
        "creation_date": doc.metadata.get("creationDate", ""),
        "modification_date": doc.metadata.get("modDate", ""),
        "file_size_kb": Path(pdf_path).stat().st_size // 1024,
    }

    doc.close()
    return metadata

meta = extract_metadata("/tmp/sample_en.pdf")
for key, value in meta.items():
    if value:
        print(f"  {key}: {value}")
```

---

## LangChain DocumentLoader integration

```python
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyMuPDFLoader("/tmp/sample_en.pdf")
documents = loader.load()

print(f"pages loaded: {len(documents)}")
for doc in documents:
    print(f"\npage {doc.metadata.get('page', 0) + 1}:")
    print(f"  metadata: {doc.metadata}")
    print(f"  first 100 chars: {doc.page_content[:100]}")

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"\nchunk count: {len(chunks)}")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = FAISS.from_documents(chunks, embedding_model)
print(f"index ready: {vectorstore.index.ntotal} vectors")
```

---

## Conclusion

For most RAG pipelines, pymupdf is the right choice: it is fast, preserves reading order in complex layouts, and exposes page-level metadata that chunking strategies and retrieval filters depend on. LangChain's `PyMuPDFLoader` wraps it with automatic metadata attachment so documents flow directly into splitters and vector stores.

The next post covers chunking strategies: finding the optimal chunk size and overlap for different document types.

<!-- toc:begin -->
## In this series

- **PDF parsing and text extraction (current)**
- Chunking strategies — optimizing by document type (upcoming)
- Metadata design and filtering (upcoming)
- Incremental indexing — updating only changed documents (upcoming)
- Multi-format document pipeline (upcoming)
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

---

## References

- [pymupdf documentation](https://pymupdf.readthedocs.io/)
- [pypdf documentation](https://pypdf.readthedocs.io/)
- [LangChain PyMuPDFLoader](https://python.langchain.com/docs/integrations/document_loaders/pymupdf/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)

Tags: RAG, Document Processing, LangChain, Python
