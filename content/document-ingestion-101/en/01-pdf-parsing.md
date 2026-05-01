---
title: 'PDF parsing and text extraction'
series: document-ingestion-101
episode: 1
language: en
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

# PDF parsing and text extraction

## Questions this post answers

- How do you make a PDF extraction demo reproducible when no sample file exists?
- How do you inspect page-level text and character counts with pypdf?
- Which metadata is worth keeping at the very first ingestion step?

> The first goal of PDF parsing is to turn a visual document into a verifiable list of strings.

Example code: `/root/Github/document-ingestion-101/en/01-pdf-parsing/main.py`

![Questions this post answers](../../../assets/document-ingestion-101/01/01-01-questions-this-post-answers.en.png)
The first practical problem in a PDF parsing tutorial is usually the sample file. If readers cannot reproduce the example from scratch, the pipeline story starts with friction.

This example generates its own PDF with `reportlab`, then reads it back with `pypdf` and prints page-level text summaries. That is exactly the shape you want for the first ingestion step.

## Runnable example

```python
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)
PDF_PATH = DATA_DIR / 'sample.pdf'

def create_sample_pdf(pdf_path: Path) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    _, height = A4
    pages = [
        [
            'Document ingestion notes',
            '',
            '1. PDF text extraction is the first pipeline step.',
            '2. pypdf is reliable when the layout is simple.',
            '3. Keeping page numbers in metadata makes debugging easier.',
        ],
        [
            'Operational checks',
            '',
            '1. The script creates its own sample PDF.',
            '2. Re-reading the file should stay reproducible.',
            '3. Verify both page count and extracted character count.',
        ],
    ]
    for page_index, lines in enumerate(pages, start=1):
        y = height - 72
        c.setFont('Helvetica-Bold', 16)
        c.drawString(72, y, f'Page {page_index}')
        y -= 36
        c.setFont('Helvetica', 12)
        for line in lines:
            c.drawString(72, y, line)
            y -= 20
        c.showPage()
    c.save()

class PageSummary(TypedDict):
    page: int
    chars: int
    preview: str

def extract_pages(pdf_path: Path) -> list[PageSummary]:
    reader = PdfReader(str(pdf_path))
    pages: list[PageSummary] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or '').strip()
        pages.append(
            {
                'page': index,
                'chars': len(text),
                'preview': text.replace('
', ' ')[:100],
            }
        )
    return pages

def main() -> None:
    create_sample_pdf(PDF_PATH)
    pages = extract_pages(PDF_PATH)
    print(f'created: {PDF_PATH.name}')
    print(f'page_count: {len(pages)}')
    total_chars = sum(int(page['chars']) for page in pages)
    print(f'total_chars: {total_chars}')
    for page in pages:
        print(f"page={page['page']} chars={page['chars']} preview={page['preview']}")

if __name__ == '__main__':
    main()
```

## How to run it

```bash
python main.py
```

## Verified run output

```text
created: sample.pdf
page_count: 2
total_chars: 363
page=1 chars=190 preview=Page 1 Document ingestion notes ...
page=2 chars=173 preview=Page 2 Operational checks ...
```

## What to notice in this code

- `create_sample_pdf()` creates the input data, so the example has no hidden file dependency.
- `extract_pages()` returns page number, character count, and preview together, which maps cleanly to later metadata work.
- The output stays human-readable, so layout failures are easy to catch by inspection.

## Where engineers get confused

- PDF parsing is not the same as OCR. If the PDF already has a text layer, verify plain extraction first.
- A high character count does not automatically mean high quality. Reading order and repeated headers still matter.
- Complex layouts do require library comparison, but the first tutorial should start with a reproducible simple sample.

## Checklist

- [ ] The script creates its own PDF.
- [ ] It prints both page count and character count.
- [ ] The page preview is enough to verify extraction order by eye.
- [ ] You identified which metadata should flow into the next stage.

<!-- toc:begin -->
## In this series

- **PDF parsing and text extraction (current)**
- Chunking strategies — optimizing by document type (upcoming)
- Metadata design and filtering (upcoming)
- Incremental indexing — updating only changed documents (upcoming)
- Multi-format document pipeline (upcoming)
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

## References

- https://pypdf.readthedocs.io/
- https://docs.reportlab.com/reportlab/userguide/ch1_intro/

Tags: RAG, Document Processing, LangChain, Python
