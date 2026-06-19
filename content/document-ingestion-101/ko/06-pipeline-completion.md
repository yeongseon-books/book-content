---
title: "Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성"
series: document-ingestion-101
episode: 6
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/64"
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
seo_description: 완성된 수집 파이프라인은 단계 수보다 단계 간 handoff가 깨지지 않는지로 판단해야 합니다.
---

# Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성

수집 파이프라인의 가치는 각 단계를 따로 아는 데서 나오지 않습니다. 로딩, 청킹, 인덱싱을 각각 이해해도, 그것들이 엔드투엔드 실행에서 함께 버티지 못하면 실제 파이프라인이라고 부르기 어렵습니다.

이 글은 문서 수집과 인덱싱 101 시리즈의 마지막 글입니다.

여기서는 앞선 조각들을 하나의 재현 가능한 흐름으로 연결하고, 인덱스를 저장한 뒤 다시 불러와 검색까지 되는지 확인합니다.

![End-to-end ingestion pipeline flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/06/06-01-end-to-end-ingestion-pipeline.ko.png)
*End-to-end ingestion pipeline flow*
> 완성된 수집 파이프라인은 단계 수가 아니라, 각 단계가 다음 단계로 깨지지 않고 넘겨지는지로 판단해야 합니다.

## 이 글에서 다룰 문제

- 완성된 문서 수집 파이프라인은 어떤 단계별 검증 체크포인트를 가져야 할까요?
- 파싱, 정규화, 청킹, 인덱싱 중 어디서 실패했는지 어떻게 빠르게 알 수 있을까요?
- 운영에서 재실행 가능한 파이프라인으로 만들려면 어떤 산출물을 남겨야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 엔드투엔드 수집 파이프라인

마지막 글의 핵심은 개별 함수의 깊은 로직보다 단계 사이 handoff가 깨지지 않는지 확인하는 데 있습니다.

![Stage verification checkpoint flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/06/06-02-stage-verification-checkpoints.ko.png)

*Stage verification checkpoint flow*

단계별 체크포인트 몇 개만 잘 두어도 파이프라인이 어디서 깨졌는지 빠르게 좁힐 수 있습니다.

## 실행 예제

```python
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
INDEX_DIR = BASE_DIR / 'faiss_store'
DATA_DIR.mkdir(exist_ok=True)

class SimpleHashEmbeddings(Embeddings):
    def __init__(self, size: int = 32):
        self.size = size

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.size
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode('utf-8')).digest()
            for index in range(self.size):
                vector[index] += digest[index] / 255.0
        return vector

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

def create_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont('Helvetica', 12)
    c.drawString(72, 780, 'PDF source: access policy and retention rules.')
    c.drawString(72, 760, 'Chunk metadata should preserve the original file name and format.')
    c.save()

def seed_files() -> list[Path]:
    pdf_path = DATA_DIR / 'policy.pdf'
    txt_path = DATA_DIR / 'ops.txt'
    md_path = DATA_DIR / 'faq.md'
    create_pdf(pdf_path)
    txt_path.write_text('TXT source: nightly ingestion runs at 02:00 and retries failed files first.\n', encoding='utf-8')
    md_path.write_text('# FAQ\n\nMD source: metadata filters reduce the candidate set before answer generation.\n', encoding='utf-8')
    return [pdf_path, txt_path, md_path]

def load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        reader = PdfReader(str(path))
        text = '\n'.join((page.extract_text() or '').strip() for page in reader.pages)
        return [Document(page_content=text, metadata={'source': path.name, 'format': 'pdf'})]
    if suffix == '.txt':
        return [Document(page_content=path.read_text(encoding='utf-8'), metadata={'source': path.name, 'format': 'txt'})]
    if suffix in {'.md', '.markdown'}:
        return [Document(page_content=path.read_text(encoding='utf-8'), metadata={'source': path.name, 'format': 'md'})]
    raise ValueError(f'unsupported format: {suffix}')

def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=90,
        chunk_overlap=20,
        separators=['\n\n', '\n', '. ', ' '],
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata['chunk_id'] = f'chunk-{index:02d}'
    return chunks

def main() -> None:
    files = seed_files()
    loaded = [doc for path in files for doc in load_file(path)]
    chunks = chunk_documents(loaded)
    if INDEX_DIR.exists():
        shutil.rmtree(INDEX_DIR)
    vectorstore = FAISS.from_documents(chunks, SimpleHashEmbeddings())
    vectorstore.save_local(str(INDEX_DIR))
    reloaded = FAISS.load_local(
        str(INDEX_DIR),
        SimpleHashEmbeddings(),
        allow_dangerous_deserialization=True,
    )
    results = reloaded.similarity_search('metadata filters and retention', k=2)

    print(f'loaded_documents: {len(loaded)}')
    print(f'chunks: {len(chunks)}')
    print(f'faiss_saved: {INDEX_DIR}')
    for doc in results:
        preview = doc.page_content.replace('\n', ' ')[:90]
        print(f"result={doc.metadata['source']} chunk_id={doc.metadata['chunk_id']} preview={preview}")

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
loaded_documents: 3
chunks: 4
faiss_saved: en/06-pipeline-completion/faiss_store
result=policy.pdf chunk_id=chunk-00 preview=PDF source: access policy and retention rules.
result=policy.pdf chunk_id=chunk-01 preview=Chunk metadata should preserve the original file name and format.
```

### 모니터링과 복구 경로

![Monitoring and recovery flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/06/06-01-monitoring-and-recovery-path.ko.png)

*Monitoring and recovery flow*

운영용 수집 파이프라인에는 성공 경로만이 아니라, 실패 후 어디서 다시 시작할지 보이는 복구 경로도 필요합니다.

- `load_file()`는 파일 형식 차이를 흡수하고, `chunk_documents()`는 공통 청크 계약을 만듭니다.
- `SimpleHashEmbeddings`는 외부 모델 다운로드 없이도 FAISS 저장·재로드 동작을 검증하게 해 줍니다.
- 로그는 `loaded_documents`, `chunks`, `faiss_saved`, `result`라는 네 개의 짧은 체크포인트를 남깁니다.

## 자주 하는 실수

| 실수 | 왜 생기는가 | 올바른 접근 |
| --- | --- | --- |
| 인덱스 저장만 하고 재로드 검증 생략 | "저장됐으면 됐다"는 가정 | 저장 직후 `load_local` 후 샘플 질의로 검색까지 검증 |
| 파이프라인 성공 로그만 보고 완료 판단 | 배치 실행 코드가 예외를 삼킴 | `chunks_total`, `failures_total`, 샘플 검색 통과 여부를 함께 확인 |
| 단계 실패를 모두 즉시 중단으로 처리 | 안전하다는 생각에 예외를 즉시 raise | 파일 단위 실패는 누적하고, 계약 위반만 즉시 중단 |
| 엔드투엔드 데모에 LLM 호출 먼저 추가 | 완성도를 빨리 높이려는 욕심 | 인덱스 저장·재로드 검증이 먼저, LLM은 그 다음 |
| 완료 기준을 팀마다 다르게 정의 | 구두 합의로만 기준 관리 | 입력 수, 청크 수, 실패율, 샘플 검색 통과를 코드로 강제 |

## 재시도와 재실행 제어

![Retry and replay control flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/06/06-02-retry-and-replay-control.ko.png)

*Retry and replay control flow*

재시도와 재실행은 다른 제어 경로입니다. 둘을 하나의 동작으로 뭉개면 시간과 계산 비용을 쉽게 낭비합니다.

- 엔드투엔드 데모라고 해서 첫날부터 LLM 호출까지 넣을 필요는 없습니다. 우선 인덱스 저장과 재로드를 검증하는 편이 더 중요합니다.
- 임베딩 품질과 파이프라인의 정합성은 다른 문제입니다. 데모 단계에서는 재현성이 우선입니다.
- 재로드 단계를 건너뛰면 배포 시점의 경로 문제와 직렬화 문제가 나중까지 숨어 버립니다.

## 단계 오케스트레이션에 입력과 출력을 명시하기

각 단계가 어떤 키를 읽고 어떤 키를 쓰는지 명시하면 계약 위반을 초기에 찾을 수 있습니다.

```python
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class StageSpec:
    name: str
    requires: set[str]
    provides: set[str]

def validate_stage_contract(context: dict[str, object], spec: StageSpec) -> None:
    missing = sorted(spec.requires - set(context.keys()))
    if missing:
        raise RuntimeError(f'stage={spec.name} missing_inputs={missing}')
```

이 검증을 실행 전에 걸어 두면, 예를 들어 청킹 단계가 `normalized_docs`를 받지 못한 상태에서 진행되는 문제를 즉시 발견할 수 있습니다.

### 단계 실행기와 지연 시간 측정

엔드투엔드 스크립트가 커질수록 각 단계가 암묵적으로 호출되기 쉽습니다. 오케스트레이터에서 단계 정의와 실행 순서를 별도 구조로 분리하면 운영성이 좋아집니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable

StageFn = Callable[[dict[str, Any]], dict[str, Any]]

@dataclass(frozen=True)
class Stage:
    name: str
    fn: StageFn

def run_pipeline(stages: list[Stage], initial_context: dict[str, Any]) -> dict[str, Any]:
    context = initial_context.copy()
    for stage in stages:
        started = perf_counter()
        context = stage.fn(context)
        elapsed_ms = (perf_counter() - started) * 1000
        print(f"stage={stage.name} status=ok elapsed_ms={elapsed_ms:.1f}")
    return context
```

이 구조의 핵심은 단계 함수가 `context`를 입력과 출력으로 공유한다는 사실입니다. 입력 파일 목록, 추출된 문서, 청크 목록, 인덱스 경로 같은 중간 산출물을 한 객체에 모으면 디버깅 경로가 짧아집니다.

### 오류 처리 패턴: 치명적 실패와 부분 실패를 분리하기

모든 실패를 즉시 중단으로 처리하면 파이프라인 안정성이 떨어질 수 있습니다. 반대로 모든 실패를 무시하면 품질이 조용히 붕괴합니다. 파일 단위 실패는 누적하고, 계약 위반은 즉시 중단하는 이중 정책이 실무에서 자주 쓰입니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class StageFailure:
    stage: str
    source: str
    error: str

class PipelineContractError(RuntimeError):
    pass

def load_stage(context: dict[str, Any]) -> dict[str, Any]:
    loaded = []
    failures: list[StageFailure] = context.setdefault('failures', [])
    for source in context['sources']:
        try:
            loaded.extend(load_file(source))
        except Exception as exc:  # noqa: BLE001
            failures.append(StageFailure(stage='load', source=str(source), error=str(exc)))
    context['loaded'] = loaded
    return context

def validate_stage(context: dict[str, Any]) -> dict[str, Any]:
    chunks = context.get('chunks', [])
    if not chunks:
        raise PipelineContractError('chunk stage produced zero chunks')
    if any('source' not in chunk.metadata for chunk in chunks):
        raise PipelineContractError('chunk metadata missing source')
    return context
```

위 패턴은 재시도 대상과 즉시 수정 대상을 구분해 줍니다. 로더에서 개별 파일 실패가 일부 발생해도 전체 배치를 끝까지 실행해 리포트를 만들 수 있고, 계약 위반은 빠르게 멈춰 잘못된 인덱스를 남기지 않습니다.

### 벡터 DB 저장 후 샘플 질의를 품질 게이트로 두기

인덱스를 저장했다는 사실만으로는 충분하지 않습니다. 저장 직후 샘플 질의가 기대 출처를 회수하는지 확인해야 합니다.

```python
def verify_post_index(vectorstore, checks: list[tuple[str, str]], k: int = 5) -> None:
    for query, expected_source in checks:
        docs = vectorstore.similarity_search(query, k=k)
        if not any(doc.metadata.get('source') == expected_source for doc in docs):
            raise RuntimeError(
                f'post-index check failed query={query!r} expected_source={expected_source!r}'
            )
```

이 게이트는 파이프라인은 성공했지만 검색 품질이 이미 무너진 상태를 조기에 막아 줍니다.

### 모니터링 지표를 로그에 구조화해 남기는 방법

운영에서는 "성공했다"라는 한 줄보다 단계별 수치가 중요합니다.

```python
from __future__ import annotations

import json
from datetime import datetime

def emit_metric(name: str, value: int | float, **labels: str) -> None:
    payload = {
        'ts': datetime.now().isoformat(timespec='seconds'),
        'metric': name,
        'value': value,
        'labels': labels,
    }
    print(json.dumps(payload, ensure_ascii=False))

def report_run_summary(context: dict[str, object]) -> None:
    emit_metric('ingestion.files_total', int(context.get('files_total', 0)), env='prod')
    emit_metric('ingestion.chunks_total', int(context.get('chunks_total', 0)), env='prod')
    emit_metric('ingestion.failures_total', int(context.get('failures_total', 0)), env='prod')
    emit_metric('ingestion.duration_ms', float(context.get('duration_ms', 0.0)), env='prod')
```

JSON 로그를 쓰면 이후 로그 수집기나 메트릭 변환기에서 파싱하기 쉽습니다.

## 운영 노트: 파이프라인 완료 후 검증 리허설

엔드투엔드 배치는 성공 로그만 보고 끝내지 말고, 완료 직후 짧은 리허설을 수행하는 편이 좋습니다.

```python
smoke_queries = [
    ('보존기간 정책', 'policy.pdf'),
    ('메타데이터 필터', 'faq.md'),
    ('야간 배치 재시도', 'ops.txt'),
]

verify_post_index(vectorstore, smoke_queries, k=5)
```

이 리허설을 통과해야 배치 상태를 "완료"로 승격합니다. 실패하면 인덱스 버전을 이전 배치로 되돌리고 원인 분석을 시작합니다.

### 파이프라인 완료 기준을 코드로 정의하기

완료 기준이 문서로만 남아 있으면 실제 실행에서 누락되기 쉽습니다. 아래처럼 품질 게이트를 함수로 두면, 완료 조건을 실행 가능한 규칙으로 관리할 수 있습니다.

```python
from __future__ import annotations

def assert_completion(context: dict[str, object]) -> None:
    if int(context.get('files_total', 0)) == 0:
        raise RuntimeError('no input files discovered')
    if int(context.get('chunks_total', 0)) == 0:
        raise RuntimeError('no chunks generated')
    if int(context.get('index_rows_total', 0)) < int(context.get('chunks_total', 0)):
        raise RuntimeError('index row count is smaller than chunk count')
    if int(context.get('sample_results_total', 0)) == 0:
        raise RuntimeError('post-index validation query returned zero results')
```

이 기준은 작은 데모에서도 유효하고, 실제 운영 파이프라인으로 확장할 때도 그대로 재사용할 수 있습니다.

## 실전 점검 체크리스트

아래 체크리스트는 배포 직전 10분 점검용으로 자주 사용합니다.

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

이 정도 점검만 자동화해도 "돌아갔다"와 "운영 가능한 상태로 끝났다"를 구분할 수 있습니다.

## 마무리: 장기 운영 기준

문서 수집 파이프라인은 새 기능보다 기준 유지가 더 중요합니다. 팀 단위 운영에서는 아래 네 가지를 주간 기준으로 고정해 두는 편이 좋습니다.

- 파싱 품질 지표(평균 문자 수, OCR 비율, 재처리 비율)
- 청킹 품질 지표(평균 길이, 극단 길이 비율, 정책 버전 분포)
- 메타데이터 품질 지표(필수 필드 누락률, 정규화 실패 건수)
- 검색 검증 지표(샘플 질의 recall@k, 출처 회수율)

이 네 축을 함께 보면 어느 경계에서 품질이 떨어지는지 빠르게 확인할 수 있습니다. 결국 안정적인 ingestion은 화려한 모델 선택보다, 입력 품질과 단계 계약을 지속적으로 측정하는 운영 루틴에서 만들어집니다.

## 운영 체크리스트

- [ ] 세 가지 형식을 모두 로드했습니다.
- [ ] 청크 수가 납득 가능한지 확인했습니다.
- [ ] FAISS 인덱스를 저장하고 다시 불러왔습니다.
- [ ] 재로드한 인덱스로 검색까지 검증했습니다.

## 정리

완성된 파이프라인은 기능 목록이 많아서가 아니라, 각 단계의 출력이 다음 단계의 입력으로 자연스럽게 이어질 때 비로소 완성됩니다. 마지막 검증은 개별 기술보다 handoff가 끊기지 않는지를 보는 데 초점이 있어야 합니다.

이 시리즈에서 다룬 PDF 추출, 청킹, 메타데이터, 증분 인덱싱, 다중 포맷 수집은 따로 존재하는 팁이 아닙니다. 하나의 흐름으로 묶였을 때 비로소 문서 수집 시스템의 최소 형태가 됩니다. 여기에 LLM 기반 답변 생성, 사용자 피드백 루프, A/B 검색 실험을 붙이면 RAG 시스템의 전체 윤곽이 됩니다.

## 처음 질문으로 돌아가기

- **완성된 문서 수집 파이프라인은 어떤 단계별 검증 체크포인트를 가져야 할까요?**
  - 최소 네 개의 체크포인트가 필요합니다. 로드된 문서 수, 생성된 청크 수, 인덱스 저장 경로, 샘플 검색 결과 출처입니다. 이 네 개가 로그에 찍히면 파이프라인의 어느 단계가 실패했는지 즉시 좁힐 수 있습니다.
- **파싱, 정규화, 청킹, 인덱싱 중 어디서 실패했는지 어떻게 빠르게 알 수 있을까요?**
  - 각 단계의 출력 크기를 로그로 남기고, `StageSpec`으로 입출력 계약을 검증합니다. 청크 수가 0이면 청킹 단계, 인덱스 행 수가 청크 수보다 작으면 인덱싱 단계, 샘플 검색이 빈 결과면 저장 또는 임베딩 단계가 원인입니다.
- **운영에서 재실행 가능한 파이프라인으로 만들려면 어떤 산출물을 남겨야 할까요?**
  - run_id, 처리된 파일 목록과 해시, 청크 수, 실패 목록, 샘플 검색 통과 여부를 포함한 JSON 실행 리포트를 남겨야 합니다. 이 산출물이 있으면 같은 manifest로 파이프라인을 다시 돌려 동일한 결과를 재현할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [Document Ingestion 101 (3/6): 메타데이터 설계와 필터링](./03-metadata-filtering.md)
- [Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트](./04-incremental-indexing.md)
- [Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인](./05-multi-format-pipeline.md)
- **Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangChain FAISS integration guide](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [FAISS documentation](https://faiss.ai/)

### 검증에 도움 되는 자료

- [FAISS GitHub repository](https://github.com/facebookresearch/faiss)
- [LangChain text splitters integration package](https://docs.langchain.com/oss/python/integrations/splitters/index)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/document-ingestion-101/ko)

Tags: RAG, Document Processing, LangChain, Python
