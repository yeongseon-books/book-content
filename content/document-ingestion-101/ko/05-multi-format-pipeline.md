---
title: "Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인"
series: document-ingestion-101
episode: 5
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
seo_description: 다중 포맷 파이프라인의 본질은 서로 다른 입력을 하나의 공통 Document 계약으로 수렴시키는 일입니다.
---

# Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인

실제 문서 수집 작업은 한 파일 형식 안에 머무르지 않습니다. 팀은 보통 PDF, 일반 텍스트 메모, Markdown 문서를 섞어 다루면서도 뒤 단계가 그 차이를 계속 신경 쓰지 않게 만들고 싶어 합니다.

이 글은 Document Ingestion 101 시리즈의 다섯 번째 글입니다.

여기서는 여러 형식을 각자 다른 로더로 읽고, 최종적으로는 하나의 공통 `Document` 계약으로 정규화합니다.

![Loader routing by file format](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-01-loader-routing-by-file-format.ko.png)
*Loader routing by file format*
> 다중 포맷 파이프라인의 본질은 서로 다른 입력을 하나의 공통 `Document` 계약으로 밀어 넣는 데 있습니다.

## 먼저 던지는 질문

- PDF, Markdown, HTML을 한 파이프라인에 넣으려면 무엇을 먼저 공통 계약으로 맞춰야 할까요?
- 파일 형식별 loader routing은 어디까지 분기하고 어디서 다시 합쳐져야 할까요?
- 정규화 계층이 없으면 후속 청킹과 메타데이터 필터링에서 어떤 문제가 생길까요?

## 파일 형식별 로더 라우팅

다중 포맷 파이프라인의 첫 단계는 뒤 단계가 파일 형식을 다시 추론하지 않도록 라우팅 책임을 한곳에 모으는 일입니다.

## 형식별 전처리

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

이 출력의 핵심은 세 줄이 모두 비슷한 형식으로 떨어진다는 점입니다. 뒤 단계가 파일 형식을 몰라도 되는 이유는 바로 이 **정규화된 출력 계약** 덕분입니다.

## 공통 계약을 먼저 고정하는 이유

다중 포맷 파이프라인에서는 로더를 더 붙이는 일보다 **뒤 단계를 얼마나 오래 안정적으로 유지할 수 있는지**가 더 중요합니다. 그래서 먼저 `page_content`, `source`, `format`, `loader_name`처럼 뒤 단계가 기대할 최소 키를 고정하고, 그다음에 형식을 늘리는 편이 안전합니다.

| 필드 | 왜 필요한가 | 뒤 단계에서 쓰는 곳 |
| --- | --- | --- |
| `page_content` | 청킹과 임베딩의 입력 본문 | 청킹, 임베딩 |
| `source` | 원본 파일 추적 | 디버깅, 검색 결과 표시 |
| `format` | 파일 유형 정책 분기 | 청킹 프리셋, 오류 처리 |
| `loader_name` | 어떤 경로로 읽었는지 추적 | 운영 로그, 실패 분석 |

이렇게 계약을 먼저 정해 두면, 나중에 HTML이나 DOCX를 추가해도 뒤 단계는 크게 바뀌지 않습니다. 반대로 로더마다 반환 메타데이터가 제각각이면, 청킹과 인덱싱 코드가 형식별 `if` 문으로 금방 오염됩니다.

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

이 정규화 함수는 작지만 역할이 분명합니다. 로더마다 제각각인 출력 차이를 바로 뒤 단계에 넘기지 않고, **중간 handoff 층**에서 한 번 평평하게 만드는 것입니다. 형식이 늘어날수록 이런 얇은 정규화 계층이 유지보수 비용을 줄여 줍니다.

## 실패를 형식별로 분리해서 기록하기

지원 포맷이 늘어나면 실패 원인도 달라집니다. PDF는 텍스트 레이어 문제를 만나고, Markdown은 인코딩보다 구조 보존이 더 중요하며, TXT는 인코딩과 줄바꿈 정규화가 더 자주 문제를 일으킵니다. 그래서 실패도 하나의 예외 메시지로 뭉개지 말고 형식별로 기록하는 편이 좋습니다.

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

## 운영 점검용 출력 예시

```text
source=incident.pdf format=pdf loader=pypdf status=loaded
source=notes.txt format=txt loader=text status=loaded
source=runbook.md format=md loader=text status=loaded
source=diagram.docx format=docx status=unsupported reason=unsupported format: .docx
```

이런 로그 한 묶음만 있어도 현재 파이프라인이 무엇을 읽었고 무엇을 건너뛰었는지 빠르게 설명할 수 있습니다. 다중 포맷 수집의 운영 가치는 바로 이런 설명 가능성에서 나옵니다.

## 이 코드에서 먼저 봐야 할 점

### 공통 Document 계약 스키마

![Shared Document contract schema](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-01-shared-document-contract-schema.ko.png)

*Shared Document contract schema*

`page_content`, `source`, `format`이 정규화되면 뒤 단계는 훨씬 오래 형식 비종속적으로 유지될 수 있습니다.

- `load_document()`는 확장자 라우팅을 한곳에 모읍니다.
- 모든 로더가 `source`와 `format`을 공통 키로 맞추기 때문에 뒤 코드가 다시 분기하지 않습니다.
- PDF는 `pypdf`, TXT와 MD는 일반 파일 읽기를 쓰지만, 출력 계약은 같습니다.

## 실무에서 자주 헷갈리는 지점

### 파일 형식별 오류 처리

![Format error handling fallback flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/05/05-02-error-handling-across-file-formats.ko.png)

*Format error handling fallback flow*

지원 형식이 늘어날수록, 모든 로더가 똑같이 실패한다고 가정하는 것보다 명시적인 우회 경로를 두는 편이 중요합니다.

- 여러 형식을 지원하는 일의 핵심은 로더 추가보다 메타데이터 키 표준화에 있습니다.
- Markdown은 일반 텍스트처럼 읽을 수 있지만, 헤더를 살린 청킹은 나중에 별도 정책이 필요할 수 있습니다.
- PDF 로더와 텍스트 로더는 반환 단위가 다를 수 있으므로, 계약을 페이지 기준으로 할지 파일 기준으로 할지 먼저 정해야 합니다.

## 체크리스트

- [ ] PDF, TXT, MD를 한 번의 실행에서 처리했습니다.
- [ ] 모든 출력 문서에 `source`와 `format` 메타데이터가 있습니다.
- [ ] 확장자 라우팅이 한 함수에 모여 있습니다.
- [ ] 뒤 단계가 형식별 분기 없이도 동작하는지 확인했습니다.

## 실무에서는 이렇게 생각합니다

초기에는 지원 포맷 수를 늘리는 일보다, **지원하는 포맷이 어떤 계약으로 뒤 단계에 전달되는지**를 더 엄격하게 보는 편이 낫습니다. 파일 형식이 다르더라도 `Document` 계약이 흔들리지 않으면 청킹과 인덱싱은 오래 버팁니다. 반대로 계약이 흐리면 형식이 하나 늘어날 때마다 뒤 코드가 같이 복잡해집니다.

또한 모든 형식을 한 번에 같은 완성도로 처리하려는 욕심도 경계해야 합니다. PDF는 텍스트 레이어 검증이 먼저고, Markdown은 헤더 구조 보존이 먼저며, TXT는 인코딩과 줄바꿈 정규화가 먼저입니다. 파이프라인을 함께 쓰더라도 **좋은 실패 기준**은 형식마다 다릅니다.

## 정리

다중 포맷 파이프라인의 핵심은 로더를 많이 붙이는 데 있지 않습니다. 서로 다른 입력을 공통 `Document` 계약으로 수렴시켜서, 뒤 단계가 파일 형식 차이를 잊게 만드는 데 있습니다.

형식별 전처리는 얼마든지 달라질 수 있습니다. 다만 `page_content`, `source`, `format` 같은 공통 계약이 안정적이어야 청킹, 메타데이터 처리, 인덱싱이 단순해집니다. 다음 글에서는 이 계약을 끝까지 이어 붙여 엔드투엔드 파이프라인을 완성해 보겠습니다.

## 실무 확장: 포맷별 파서 어댑터와 공통 메타데이터 계약

다중 포맷 수집은 "파일을 읽는다"보다 "파일마다 다른 실패를 동일한 계약으로 다룬다"에 가깝습니다. 특히 PDF, Markdown, HTML을 함께 다루면 본문 추출 품질, 구조 보존, 인코딩 이슈가 동시에 발생합니다.

### 어댑터 패턴으로 로더를 교체 가능하게 만들기

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

### HTML과 Markdown을 같은 청킹 정책으로 다루기 위한 정규화

HTML은 태그를 제거하면서 의미 경계를 잃기 쉽고, Markdown은 헤더를 유지해야 검색 설명력이 올라갑니다. 그래서 정규화 단계에서 최소 구조 정보를 메타데이터로 옮겨 두는 편이 좋습니다.

```python
def normalize_text_document(doc: Document, *, source: str, fmt: str, section: str | None = None) -> Document:
    cleaned = ' '.join(doc.page_content.split())
    metadata = dict(doc.metadata)
    metadata.update(
        {
            'source': source,
            'format': fmt,
            'section': section or 'body',
            'content_kind': 'text',
        }
    )
    return Document(page_content=cleaned, metadata=metadata)
```

핵심은 포맷별 세부 정보는 유지하되, 후속 단계가 기대하는 공통 키는 반드시 맞추는 것입니다.

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

정규화된 문서는 결국 벡터 DB로 들어갑니다. 따라서 인덱싱 전에 아래 필드가 항상 채워지는지 검증하는 게 좋습니다.

- `source`: 원본 파일 이름 또는 URI
- `format`: pdf, md, html, txt
- `doc_type`: manual, policy, faq
- `section`: heading 또는 body 구간
- `version`: 문서 버전

이 계약이 안정되면 메타데이터 필터와 증분 인덱싱이 같은 키 집합을 공유할 수 있습니다. 즉, 다중 포맷 설계가 후속 단계 전체의 결합 비용을 낮추는 기반이 됩니다.

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

## 실전 점검 체크리스트 확장

아래 체크리스트는 배포 직전 10분 점검용으로 자주 사용합니다. 문서 수집 파이프라인은 기능이 아니라 경계 검증으로 안정성이 결정되므로, 매 실행에서 같은 항목을 반복 확인하는 습관이 중요합니다.

- 입력 파일 수가 평소 범위에서 크게 벗어나지 않는지 확인합니다.
- 실패 문서 비율이 임계치(예: 3%)를 넘지 않는지 확인합니다.
- 샘플 문서 3건 이상에 대해 source, page, chunk_id 추적이 가능한지 확인합니다.
- 메타데이터 필드 누락(`source`, `format`, `doc_type`)이 0건인지 확인합니다.
- 벡터 검색 샘플 질의에서 기대 출처가 상위 결과에 포함되는지 확인합니다.

```python
def quick_health_report(stats: dict[str, int | float]) -> None:
    print(f"files_total={stats['files_total']}")
    print(f"failed_total={stats['failed_total']}")
    print(f"chunks_total={stats['chunks_total']}")
    print(f"metadata_missing={stats['metadata_missing']}")
    print(f"smoke_passed={stats['smoke_passed']}")
```

이 정도 점검만 자동화해도 "돌아갔다"와 "운영 가능한 상태로 끝났다"를 구분할 수 있습니다. 장기적으로는 이 리포트를 누적해 주간 추세를 보고, 특정 단계에서 실패율이 증가하는 패턴을 조기에 잡는 것이 좋습니다.

## 장애 대응 메모: 단계별 원인 축소 순서

문서 수집 장애가 나면 모든 단계를 동시에 의심하기 쉽습니다. 그러나 실제로는 아래 순서로 좁히면 훨씬 빠르게 원인을 찾을 수 있습니다.

1. **입력 경계 확인**: 이번 배치의 입력 파일 목록과 직전 배치 목록을 비교해 비정상 증가/감소를 찾습니다.
2. **파싱 경계 확인**: 빈 본문, 비정상 길이, OCR 비율 급증 문서를 먼저 분리합니다.
3. **청킹 경계 확인**: 너무 짧거나 긴 청크 비율, chunk_id 누락, section 누락을 점검합니다.
4. **인덱싱 경계 확인**: upsert/delete 건수와 상태 저장소 run_id 일치 여부를 확인합니다.
5. **검색 경계 확인**: 샘플 질의로 expected source가 회수되는지 검증합니다.

```text
incident_id=ingestion-2026-05-21-01
step=input files_total=412 delta=+187
step=parse ocr_ratio=0.62 alert=true
step=chunk tiny_ratio=0.41 alert=true
step=index upsert=9342 delete=0 state_commit=true
step=search smoke_passed=false
```

위 예시처럼 단계별 신호를 한 줄씩 남기면, 장애 원인이 파서 변경인지 청킹 정책 회귀인지 빠르게 구분할 수 있습니다. 특히 `state_commit=true`인데 `smoke_passed=false`인 경우는 인덱스 내용 품질 문제일 가능성이 높으므로, 상태를 되돌리기 전에 품질 게이트 로그를 먼저 확인해야 합니다.

장애 대응의 목표는 완벽한 분석이 아니라 재현 가능한 축소입니다. 같은 형식의 로그를 남기고 같은 순서로 확인하는 운영 습관이 결국 파이프라인의 평균 복구 시간을 줄입니다.

## 마무리 운영 기준

문서 수집 파이프라인은 새 기능보다 기준 유지가 더 중요합니다. 그래서 팀 단위 운영에서는 아래 네 가지를 주간 기준으로 고정해 두는 편이 좋습니다.

- 파싱 품질 지표(평균 문자 수, OCR 비율, 재처리 비율)
- 청킹 품질 지표(평균 길이, 극단 길이 비율, 정책 버전 분포)
- 메타데이터 품질 지표(필수 필드 누락률, 정규화 실패 건수)
- 검색 검증 지표(샘플 질의 recall@k, 출처 회수율)

이 네 축을 함께 보면 어느 경계에서 품질이 떨어지는지 빠르게 확인할 수 있습니다. 결국 안정적인 ingestion은 화려한 모델 선택보다, 입력 품질과 단계 계약을 지속적으로 측정하는 운영 루틴에서 만들어집니다.

## 포맷별 임베딩 전처리 차이와 통합 전략

PDF에서 추출한 텍스트는 줄바꿈이 많고, Markdown은 헤더 기호가 포함되며, HTML은 태그 잔여물이 남을 수 있습니다. 이런 차이를 임베딩 직전에 정규화하지 않으면 같은 의미의 문장이 포맷에 따라 서로 다른 벡터 공간에 놓일 수 있습니다.

```python
from __future__ import annotations

import re

def clean_for_embedding(text: str, fmt: str) -> str:
    if fmt == 'md':
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    if fmt == 'html':
        text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'
{2,}', '
', text)
    text = re.sub(r'[ 	]+', ' ', text)
    return text.strip()
```

이 정규화 함수는 로더 직후가 아니라 임베딩 직전에 적용합니다. 로더 출력에는 구조 정보가 남아 있어야 청킹에서 경계를 잡을 수 있기 때문입니다. 즉, 구조 보존(청킹용)과 텍스트 정규화(임베딩용)는 서로 다른 시점에 적용해야 합니다.

포맷별 정규화 차이를 무시하고 원문을 그대로 임베딩하면, 검색 시 "같은 내용인데 포맷이 달라서 유사도가 낮은" 현상이 나타납니다. 이 문제는 모델을 바꿔도 해결되지 않고, 전처리 계층에서만 잡을 수 있습니다.

## 처음 질문으로 돌아가기

- **PDF, Markdown, HTML을 한 파이프라인에 넣으려면 무엇을 먼저 공통 계약으로 맞춰야 할까요?**
  텍스트 본문, source, doc_type, title, page_or_section, version 같은 공통 필드를 먼저 정해야 합니다.

- **파일 형식별 loader routing은 어디까지 분기하고 어디서 다시 합쳐져야 할까요?**
  로딩과 전처리는 형식별로 분기하되, 정규화된 Document 목록을 만드는 지점에서 다시 합쳐져야 합니다.

- **정규화 계층이 없으면 후속 청킹과 메타데이터 필터링에서 어떤 문제가 생길까요?**
  정규화가 없으면 어떤 형식은 제목이 빠지고 어떤 형식은 source가 달라져 청킹 기준과 필터 조건이 흔들립니다.

<!-- toc:begin -->
## 시리즈 목차

- [Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [Document Ingestion 101 (3/6): 메타데이터 설계와 필터링](./03-metadata-filtering.md)
- [Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트](./04-incremental-indexing.md)
- **Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 (현재 글)**
- Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 (예정)

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
