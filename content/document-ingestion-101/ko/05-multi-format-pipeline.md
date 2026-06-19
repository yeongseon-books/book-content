---
title: "Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인"
series: document-ingestion-101
episode: 5
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/63"
    published_at: '2026-05-05'
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
seo_description: 다중 포맷 파이프라인의 본질은 서로 다른 입력을 하나의 공통 Document 계약으로 수렴시키는 일입니다.
---

# Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인

실제 문서 수집 작업은 한 파일 형식 안에 머무르지 않습니다. 팀은 보통 PDF, 일반 텍스트 메모, Markdown 문서를 섞어 다루면서도 뒤 단계가 그 차이를 계속 신경 쓰지 않게 만들고 싶어 합니다.

이 글은 문서 수집과 인덱싱 101 시리즈의 5번째 글입니다.

여기서는 여러 형식을 각자 다른 로더로 읽고, 최종적으로는 하나의 공통 `Document` 계약으로 정규화합니다.

![Loader routing by file format](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-01-loader-routing-by-file-format.ko.png)
*Loader routing by file format*
> 다중 포맷 파이프라인의 본질은 서로 다른 입력을 하나의 공통 `Document` 계약으로 밀어 넣는 데 있습니다.

## 이 글에서 다룰 문제

- PDF, Markdown, HTML을 한 파이프라인에 넣으려면 무엇을 먼저 공통 계약으로 맞춰야 할까요?
- 파일 형식별 loader routing은 어디까지 분기하고 어디서 다시 합쳐져야 할까요?
- 정규화 계층이 없으면 후속 청킹과 메타데이터 필터링에서 어떤 문제가 생길까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 파일 형식별 로더 라우팅

다중 포맷 파이프라인의 첫 단계는 뒤 단계가 파일 형식을 다시 추론하지 않도록 라우팅 책임을 한곳에 모으는 일입니다.

![Format-specific preprocessing branches](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-02-format-specific-preprocessing.ko.png)

*Format-specific preprocessing branches*

전처리 방식은 형식마다 달라도 괜찮습니다. 다만 최종 출력은 하나의 본문 텍스트 계약으로 수렴해야 합니다.

## 실행 예제

```python
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

def create_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont('Helvetica', 12)
    c.drawString(72, 780, 'PDF source: incident review and remediation steps.')
    c.drawString(72, 760, 'Store the source format in metadata so later stages stay uniform.')
    c.save()

def seed_files() -> list[Path]:
    pdf_path = DATA_DIR / 'incident.pdf'
    txt_path = DATA_DIR / 'notes.txt'
    md_path = DATA_DIR / 'runbook.md'
    create_pdf(pdf_path)
    txt_path.write_text('TXT source: queue backlog grew overnight. Scale-out reduced latency.\n', encoding='utf-8')
    md_path.write_text('# Runbook\n\nMD source: restart the worker only after checking the dead-letter queue.\n', encoding='utf-8')
    return [pdf_path, txt_path, md_path]

def load_pdf(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    text = '\n'.join((page.extract_text() or '').strip() for page in reader.pages)
    return [Document(page_content=text, metadata={'source': path.name, 'format': 'pdf'})]

def load_text_like(path: Path, fmt: str) -> list[Document]:
    return [Document(page_content=path.read_text(encoding='utf-8'), metadata={'source': path.name, 'format': fmt})]

def load_document(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        return load_pdf(path)
    if suffix == '.txt':
        return load_text_like(path, 'txt')
    if suffix in {'.md', '.markdown'}:
        return load_text_like(path, 'md')
    raise ValueError(f'unsupported format: {suffix}')

def main() -> None:
    for path in seed_files():
        docs = load_document(path)
        for doc in docs:
            preview = doc.page_content.replace('\n', ' ')[:90]
            print(f"source={doc.metadata['source']} format={doc.metadata['format']} preview={preview}")

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
source=incident.pdf format=pdf preview=PDF source: incident review and remediation steps. ...
source=notes.txt format=txt preview=TXT source: queue backlog grew overnight. ...
source=runbook.md format=md preview=# Runbook MD source: restart the worker ...
```

이 출력의 핵심은 세 줄이 모두 비슷한 형식으로 떨어진다는 사실입니다. 뒤 단계가 파일 형식을 몰라도 되는 이유는 바로 이 정규화된 출력 계약 덕분입니다.

## 공통 계약을 먼저 고정하는 이유

다중 포맷 파이프라인에서는 로더를 더 붙이는 일보다 뒤 단계를 얼마나 오래 안정적으로 유지할 수 있는지가 더 중요합니다. 그래서 먼저 `page_content`, `source`, `format`, `loader_name`처럼 뒤 단계가 기대할 최소 키를 고정하고, 그다음에 형식을 늘리는 편이 안전합니다.

| 필드 | 왜 필요한가 | 뒤 단계에서 쓰는 곳 |
| --- | --- | --- |
| `page_content` | 청킹과 임베딩의 입력 본문 | 청킹, 임베딩 |
| `source` | 원본 파일 추적 | 디버깅, 검색 결과 표시 |
| `format` | 파일 유형 정책 분기 | 청킹 프리셋, 오류 처리 |
| `loader_name` | 어떤 경로로 읽었는지 추적 | 운영 로그, 실패 분석 |

이렇게 계약을 먼저 정해 두면, 나중에 HTML이나 DOCX를 추가해도 뒤 단계는 크게 바뀌지 않습니다. 반대로 로더마다 반환 메타데이터가 제각각이면, 청킹과 인덱싱 코드가 형식별 `if` 문으로 금방 오염됩니다.

## 자주 하는 실수

| 실수 | 왜 생기는가 | 올바른 접근 |
| --- | --- | --- |
| 포맷별 메타데이터 키가 제각각 | 로더를 독립적으로 붙이면서 정규화를 잊음 | 정규화 계층을 두고 `source`, `format`, `loader_name`을 항상 통일 |
| 모든 포맷을 같은 완성도로 한번에 구현 | 빠르게 지원 포맷을 늘리려는 욕심 | PDF → TXT → MD 순서로 한 포맷씩 검증 후 추가 |
| 지원 포맷과 실패 포맷을 같은 예외로 처리 | 예외 처리를 단순화하려는 경향 | `unsupported`와 `failed`를 명시적으로 분리해 로그 기록 |
| 로더 직후 임베딩 전처리 적용 | 정규화 타이밍을 혼동 | 구조 보존은 로더 직후, 텍스트 정규화는 임베딩 직전에 분리 적용 |
| Markdown 헤더를 텍스트 추출 시 제거 | 태그 제거와 동일하게 취급 | 헤더는 청킹용 구조 정보로 보존하고, 임베딩 전에만 정규화 |

## 정규화 계층을 별도로 두는 예제

```python
from __future__ import annotations

from langchain_core.documents import Document

def normalize_document(doc: Document, *, source: str, fmt: str, loader_name: str) -> Document:
    metadata = dict(doc.metadata)
    metadata.update(
        {
            'source': source,
            'format': fmt,
            'loader_name': loader_name,
        }
    )
    return Document(page_content=doc.page_content.strip(), metadata=metadata)

def normalize_batch(docs: list[Document], *, source: str, fmt: str, loader_name: str) -> list[Document]:
    return [normalize_document(doc, source=source, fmt=fmt, loader_name=loader_name) for doc in docs]
```

이 정규화 함수는 작지만 역할이 분명합니다. 로더마다 제각각인 출력 차이를 바로 뒤 단계에 넘기지 않고, 중간 handoff 층에서 한 번 평평하게 만드는 것입니다. 형식이 늘어날수록 이런 얇은 정규화 계층이 유지보수 비용을 줄여 줍니다.

## 실패를 형식별로 분리해서 기록하기

지원 포맷이 늘어나면 실패 원인도 달라집니다. PDF는 텍스트 레이어 문제를 만나고, Markdown은 인코딩보다 구조 보존이 더 중요하며, TXT는 인코딩과 줄바꿈 정규화가 더 자주 문제를 일으킵니다. 실패도 하나의 예외 메시지로 뭉개지 말고 형식별로 기록하는 편이 좋습니다.

```python
from __future__ import annotations

from pathlib import Path

def safe_load_document(path: Path) -> tuple[list[Document], dict[str, str] | None]:
    try:
        docs = load_document(path)
    except ValueError as exc:
        return [], {'source': path.name, 'status': 'unsupported', 'reason': str(exc)}
    except Exception as exc:  # tutorial logging path
        return [], {'source': path.name, 'status': 'failed', 'reason': str(exc)}
    return docs, None
```

이렇게 해 두면 운영 로그에서 `unsupported`와 `failed`를 분리해 볼 수 있습니다. 새 포맷을 아직 지원하지 않는 상황과, 지원하는 포맷인데 추출이 깨진 상황은 대응 방식이 완전히 다르기 때문입니다.

## 어댑터 패턴으로 로더를 교체 가능하게 만들기

형식별 로더를 함수로 흩어 두면 테스트와 교체가 어렵습니다. 아래처럼 어댑터 인터페이스를 두면 파서를 바꿀 때 영향 범위를 줄일 수 있습니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from langchain_core.documents import Document

class LoaderAdapter(Protocol):
    def supports(self, path: Path) -> bool: ...
    def load(self, path: Path) -> list[Document]: ...

@dataclass
class LoaderRegistry:
    adapters: list[LoaderAdapter]

    def load(self, path: Path) -> list[Document]:
        for adapter in self.adapters:
            if adapter.supports(path):
                return adapter.load(path)
        raise ValueError(f'unsupported format: {path.suffix.lower()}')
```

이 구조는 DOCX 추가나 HTML 파서 교체처럼 포맷 확장이 필요할 때 특히 유리합니다. 라우팅 로직과 로딩 로직을 분리하면 테스트 케이스도 포맷별로 깔끔하게 나눌 수 있습니다.

### 포맷별 임베딩 전처리 정규화

PDF에서 추출한 텍스트는 줄바꿈이 많고, Markdown은 헤더 기호가 포함되며, HTML은 태그 잔여물이 남을 수 있습니다. 이런 차이를 임베딩 직전에 정규화하지 않으면 같은 의미의 문장이 포맷에 따라 서로 다른 벡터 공간에 놓일 수 있습니다.

```python
from __future__ import annotations

import re

def clean_for_embedding(text: str, fmt: str) -> str:
    if fmt == 'md':
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    if fmt == 'html':
        text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()
```

이 정규화 함수는 로더 직후가 아니라 임베딩 직전에 적용합니다. 로더 출력에는 구조 정보가 남아 있어야 청킹에서 경계를 잡을 수 있기 때문입니다. 즉, 구조 보존(청킹용)과 텍스트 정규화(임베딩용)는 서로 다른 시점에 적용해야 합니다.

### 포맷별 실패를 재처리 큐와 연결하기

```python
def classify_failure(fmt: str, reason: str) -> str:
    if fmt == 'pdf' and 'encrypted' in reason.lower():
        return 'manual-review'
    if fmt in {'md', 'html'} and 'encoding' in reason.lower():
        return 'retry-with-utf8'
    return 'generic-retry'
```

이 분류가 있으면 실패를 일괄 재시도하지 않고 원인별 큐로 보낼 수 있습니다. 다중 포맷 파이프라인의 안정성은 성공 경로보다 실패 분류 정확도에서 더 크게 갈립니다.

### 공통 계약을 벡터 DB 스키마와 맞추기

정규화된 문서는 결국 벡터 DB로 들어갑니다. 따라서 인덱싱 전에 아래 필드가 항상 채워지는지 검증하는 것이 좋습니다.

- `source`: 원본 파일 이름 또는 URI
- `format`: pdf, md, html, txt
- `doc_type`: manual, policy, faq
- `section`: heading 또는 body 구간
- `version`: 문서 버전

이 계약이 안정되면 메타데이터 필터와 증분 인덱싱이 같은 키 집합을 공유할 수 있습니다. 즉, 다중 포맷 설계가 후속 단계 전체의 결합 비용을 낮추는 기반이 됩니다.

### 배치 로딩과 포맷별 통계 수집

실운영에서는 단일 파일 로딩보다 디렉터리 단위 배치 로딩을 더 자주 씁니다. 포맷별 성공·실패 수를 함께 집계하면 어느 형식이 파이프라인 병목인지 빠르게 파악할 수 있습니다.

```python
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from langchain_core.documents import Document

def load_directory(root: Path, extensions: set[str]) -> tuple[list[Document], dict[str, int]]:
    all_docs: list[Document] = []
    stats: dict[str, int] = defaultdict(int)
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in extensions:
            continue
        docs, error = safe_load_document(path)
        if error:
            stats[f'failed_{suffix}'] += 1
        else:
            all_docs.extend(docs)
            stats[f'loaded_{suffix}'] += 1
    return all_docs, dict(stats)
```

이 함수는 성공 문서와 통계를 함께 반환합니다. 통계를 로그로 남기면 `failed_pdf=3`처럼 포맷별 실패 신호를 배치 단위로 한눈에 볼 수 있습니다. 또한 `extensions` 파라미터로 지원 포맷을 명시하면 새 확장자가 실수로 들어오는 경우도 차단됩니다.

## 공통 Document 계약 스키마

![Shared Document contract schema](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-01-shared-document-contract-schema.ko.png)

*Shared Document contract schema*

`page_content`, `source`, `format`이 정규화되면 뒤 단계는 훨씬 오래 형식 비종속적으로 유지될 수 있습니다.

- `load_document()`는 확장자 라우팅을 한곳에 모읍니다.
- 모든 로더가 `source`와 `format`을 공통 키로 맞추기 때문에 뒤 코드가 다시 분기하지 않습니다.
- PDF는 `pypdf`, TXT와 MD는 일반 파일 읽기를 쓰지만, 출력 계약은 같습니다.

## 파일 형식별 오류 처리

![Format error handling fallback flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-02-error-handling-across-file-formats.ko.png)

*Format error handling fallback flow*

지원 형식이 늘어날수록, 모든 로더가 똑같이 실패한다고 가정하는 것보다 명시적인 우회 경로를 두는 편이 중요합니다.

- 여러 형식을 지원하는 일의 핵심은 로더 추가보다 메타데이터 키 표준화에 있습니다.
- Markdown은 일반 텍스트처럼 읽을 수 있지만, 헤더를 살린 청킹은 나중에 별도 정책이 필요할 수 있습니다.
- PDF 로더와 텍스트 로더는 반환 단위가 다를 수 있으므로, 계약을 페이지 기준으로 할지 파일 기준으로 할지 먼저 정해야 합니다.

## 운영 노트: 포맷별 품질 임계치와 재처리 정책

다중 포맷 수집에서는 포맷별 품질 임계치를 다르게 잡아야 합니다. PDF는 텍스트 추출률, Markdown은 헤더 보존률, HTML은 본문 추출 정확도를 핵심 지표로 두는 방식이 일반적입니다.

```yaml
quality_gate:
  pdf:
    min_chars_per_page: 80
    max_ocr_ratio: 0.35
  markdown:
    min_heading_retention: 0.90
  html:
    min_main_content_ratio: 0.70
```

임계치가 있으면 실패를 "다시 시도할지"와 "사람 검토로 보낼지"를 자동 분기할 수 있습니다. 예를 들어 OCR 비율이 60%를 넘는 PDF는 재시도보다 수동 검토 큐로 보내는 편이 비용을 줄입니다.

또한 포맷별 처리량과 실패율을 같은 대시보드에서 보되, 경보 기준은 포맷별로 따로 두는 것이 좋습니다. 하나의 임계치로 모든 포맷을 감시하면 과다 경보가 발생하거나 중요한 신호를 놓치기 쉽습니다.

## 운영 점검용 출력 예시

```text
source=incident.pdf format=pdf loader=pypdf status=loaded
source=notes.txt format=txt loader=text status=loaded
source=runbook.md format=md loader=text status=loaded
source=diagram.docx format=docx status=unsupported reason=unsupported format: .docx
```

이런 로그 한 묶음만 있어도 현재 파이프라인이 무엇을 읽었고 무엇을 건너뛰었는지 빠르게 설명할 수 있습니다. 다중 포맷 수집의 운영 가치는 바로 이런 설명 가능성에서 나옵니다.

## 운영 체크리스트

- [ ] PDF, TXT, MD를 한 번의 실행에서 처리했습니다.
- [ ] 모든 출력 문서에 `source`와 `format` 메타데이터가 있습니다.
- [ ] 확장자 라우팅이 한 함수에 모여 있습니다.
- [ ] 뒤 단계가 형식별 분기 없이도 동작하는지 확인했습니다.

## 정리

다중 포맷 파이프라인의 핵심은 로더를 많이 붙이는 데 있지 않습니다. 서로 다른 입력을 공통 `Document` 계약으로 수렴시켜서, 뒤 단계가 파일 형식 차이를 잊게 만드는 데 있습니다.

형식별 전처리는 얼마든지 달라질 수 있습니다. 다만 `page_content`, `source`, `format` 같은 공통 계약이 안정적이어야 청킹, 메타데이터 처리, 인덱싱이 단순해집니다. 다음 글에서는 이 계약을 끝까지 이어 붙여 엔드투엔드 파이프라인을 완성해 보겠습니다.

## 처음 질문으로 돌아가기

- **PDF, Markdown, HTML을 한 파이프라인에 넣으려면 무엇을 먼저 공통 계약으로 맞춰야 할까요?**
  - `page_content`, `source`, `format`, `loader_name` 네 개의 키를 먼저 고정해야 합니다. 이 계약이 안정되면 로더가 달라져도 청킹과 인덱싱 단계는 바뀌지 않습니다.
- **파일 형식별 loader routing은 어디까지 분기하고 어디서 다시 합쳐져야 할까요?**
  - 분기는 `load_document()` 같은 라우팅 함수 한 곳에서 처리합니다. 정규화 함수를 거친 뒤에는 모든 포맷이 동일한 `Document` 계약으로 합쳐져 뒤 단계에 넘어갑니다.
- **정규화 계층이 없으면 후속 청킹과 메타데이터 필터링에서 어떤 문제가 생길까요?**
  - 로더마다 반환 키가 달라지면 청킹 코드에 포맷별 `if` 문이 누적됩니다. 메타데이터 필터에서도 필드 이름 불일치로 결과가 빠지거나 잘못 걸립니다. 형식이 늘어날수록 이 오염은 빠르게 확산됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [Document Ingestion 101 (3/6): 메타데이터 설계와 필터링](./03-metadata-filtering.md)
- [Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트](./04-incremental-indexing.md)
- **Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 (현재 글)**
- [Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성](./06-pipeline-completion.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangChain document loaders concepts](https://python.langchain.com/docs/concepts/document_loaders/)
- [pypdf user guide](https://pypdf.readthedocs.io/)

### 검증에 도움 되는 자료

- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Markdown Guide - Basic Syntax](https://www.markdownguide.org/basic-syntax/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/document-ingestion-101/ko)

Tags: RAG, Document Processing, LangChain, Python
