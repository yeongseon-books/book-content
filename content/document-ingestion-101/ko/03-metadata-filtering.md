---
title: "Document Ingestion 101 (3/6): 메타데이터 설계와 필터링"
series: document-ingestion-101
episode: 3
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
seo_description: 메타데이터는 장식이 아니라 검색 후보군을 먼저 줄이는 첫 번째 인덱스입니다.
---

# Document Ingestion 101 (3/6): 메타데이터 설계와 필터링

좋은 검색은 의미 유사도만으로 완성되지 않습니다. 운영 환경에서는 범위, 출처, 시간 구간처럼 랭킹 전에 먼저 좁혀야 하는 조건이 분명히 생깁니다.

이 글은 Document Ingestion 101 시리즈의 3번째 글입니다. 여기서는 실무에서 바로 쓸 수 있는 메타데이터 형태를 설계하고, 필터가 검색 동작을 어떻게 바꾸는지 눈에 보이게 확인합니다.

## 먼저 던지는 질문

- 메타데이터 스키마는 왜 임베딩 후가 아니라 수집 단계에서 먼저 설계해야 할까요?
- 필터는 벡터 유사도 검색 전에 후보군을 어떻게 바꿀까요?
- 필수 메타데이터가 빠지면 검색과 출처 표시에 어떤 문제가 생길까요?

## 큰 그림

![Retrieval metadata schema flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-01-metadata-schema-design.ko.png)

*Retrieval metadata schema flow*

이 그림에서는 문서가 공통 메타데이터 스키마를 얻고, 필터가 벡터 검색 전에 후보군을 좁히는 흐름을 봅니다. 메타데이터는 부가 정보가 아니라 검색 범위와 출처 설명을 결정하는 계약입니다.

> 메타데이터는 본문 옆의 장식이 아니라 검색 후보군을 줄이는 첫 번째 인덱스입니다.

## 메타데이터 스키마 설계

좋은 스키마는 필드를 많이 모으는 데 있지 않습니다. 실제로 후보군을 줄이는 몇 개의 키를 남기는 데 있습니다.

## 필터가 후보군을 좁히는 방식

![Filtered retrieval candidate flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-02-how-filters-narrow-the-candidate-set.ko.png)

*Filtered retrieval candidate flow*

여러 청크가 의미상 비슷해도, 필터는 랭킹 전에 범위를 먼저 줄여서 검색 결과를 안정시킵니다.

## 실행 예제

```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

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

@dataclass
class ChunkSpec:
    title: str
    text: str
    category: str
    quarter: str
    source: str

    def to_document(self) -> Document:
        metadata = {
            'title': self.title,
            'category': self.category,
            'quarter': self.quarter,
            'source': self.source,
        }
        return Document(page_content=self.text, metadata=metadata)

def build_vectorstore() -> FAISS:
    docs = [
        ChunkSpec(
            title='Q4 marketing budget',
            text='The 2024 Q4 marketing budget focuses on campaign spend and partner events.',
            category='marketing',
            quarter='2024Q4',
            source='q4-report.pdf',
        ).to_document(),
        ChunkSpec(
            title='Q4 infrastructure cost',
            text='The 2024 Q4 infrastructure budget focuses on storage migration and backup cost.',
            category='engineering',
            quarter='2024Q4',
            source='q4-report.pdf',
        ).to_document(),
        ChunkSpec(
            title='Q3 marketing review',
            text='The 2024 Q3 marketing review summarizes webinar leads and conversion rate.',
            category='marketing',
            quarter='2024Q3',
            source='q3-review.md',
        ).to_document(),
    ]
    return FAISS.from_documents(docs, SimpleHashEmbeddings())

def main() -> None:
    vectorstore = build_vectorstore()
    query = 'marketing budget'

    print('[filter=category:marketing]')
    for doc in vectorstore.similarity_search(query, k=3, filter={'category': 'marketing'}):
        print(doc.metadata['title'], doc.metadata['quarter'], '-', doc.page_content)

    print('\n[filter=quarter:2024Q4]')
    for doc in vectorstore.similarity_search(query, k=3, filter={'quarter': '2024Q4'}):
        print(doc.metadata['title'], doc.metadata['category'], '-', doc.page_content)

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
[filter=category:marketing]
Q3 marketing review 2024Q3 - ...
Q4 marketing budget 2024Q4 - ...

[filter=quarter:2024Q4]
Q4 marketing budget marketing - ...
Q4 infrastructure cost engineering - ...
```

## 이 코드에서 먼저 봐야 할 점

### 유사도와 필터가 결합되는 순서

![Similarity and filter processing flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-01-how-similarity-and-filters-combine.ko.png)

*Similarity and filter processing flow*

유사도와 필터는 하나의 불투명한 검색 단계가 아니라, 순서가 보이는 별도 단계로 다룰 때 해석이 쉬워집니다.

- `ChunkSpec`은 본문과 메타데이터를 함께 두어 검색 스키마를 한곳에서 보이게 합니다.
- `SimpleHashEmbeddings`는 네트워크 없이도 실제 `filter` 경로를 그대로 재현하게 해 줍니다.
- 핵심은 같은 질의라도 필터가 바뀌면 결과 집합이 달라진다는 점입니다.

## 실무에서 자주 헷갈리는 지점

### 출처 추적이 감사를 돕는 방식

![Source tracking and audit path](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-02-how-source-tracking-supports-audits.ko.png)

*Source tracking and audit path*

응답이 이상해 보일 때는 청크 본문만 들여다보는 것보다, source와 scope 메타데이터가 실패 원인을 더 빨리 설명하는 경우가 많습니다.

- 메타데이터가 많다고 항상 좋은 것은 아닙니다. 실제로 필터링할 필드만 남겨야 합니다.
- 검색 결과가 이상하면 임베딩 모델보다 후보군 설계가 먼저 문제일 수 있습니다.
- FAISS는 관계형 데이터베이스가 아니므로, 더 복잡한 조건은 애플리케이션 레벨 설계가 함께 필요합니다.

## 체크리스트

- [ ] 청크 메타데이터에 최소한 `category`, `quarter`, `source`가 들어 있습니다.
- [ ] 같은 질의에 대해 서로 다른 필터 결과를 비교했습니다.
- [ ] 필드 이름이 문서 생성과 검색 단계에서 일관됩니다.
- [ ] 운영상 유용한 필드만 남기도록 스키마를 다듬었습니다.

## 정리

메타데이터는 본문을 설명하는 부가 정보가 아니라, 검색 전에 후보군을 줄이는 첫 번째 인덱스입니다. 그래서 어떤 필드를 저장할지보다, 어떤 필드가 실제로 검색 범위를 줄이는지부터 따져야 합니다.

이 글에서 본 `category`, `quarter`, `source` 같은 키는 단순하지만 강력합니다. 다음 글에서는 이런 메타데이터 계약을 유지한 채, 변경된 문서만 다시 처리하는 증분 인덱싱 흐름으로 넘어가겠습니다.

### 필수 메타데이터 스키마를 계약으로 고정하기

필드가 느슨하면 검색 기능은 돌아가도 운영 중에 결과 해석이 어려워집니다. 특히 `source`나 `version`이 빠진 문서는 나중에 재색인 대상 판별과 감사 로그 연결이 힘들어집니다. 그래서 수집 단계에서 최소 계약을 코드로 강제하는 편이 안전합니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class MetadataSchema:
    source: str
    doc_type: str
    category: str
    quarter: str
    language: str
    tenant: str
    version: str
    ingested_at: str

def build_metadata(
    *,
    source: str,
    doc_type: str,
    category: str,
    quarter: str,
    language: str,
    tenant: str,
    version: str,
) -> dict[str, str]:
    schema = MetadataSchema(
        source=source,
        doc_type=doc_type,
        category=category,
        quarter=quarter,
        language=language,
        tenant=tenant,
        version=version,
        ingested_at=datetime.now().isoformat(timespec='seconds'),
    )
    return schema.__dict__.copy()
```

이처럼 필수 키를 명시해 두면, 검색 단계에서 조건식을 작성할 때 누락 필드 때문에 런타임에서 뒤늦게 실패하는 일을 줄일 수 있습니다. 또한 테넌트 분리나 버전 롤백 같은 운영 작업에서 같은 키 집합을 재사용할 수 있습니다.

### 다중 조건 필터 쿼리를 조합하는 패턴

실무 질의는 단일 조건보다 복합 조건이 많습니다. 예를 들어 마케팅 문서만 보되, 특정 분기와 특정 테넌트로 범위를 더 줄이는 식입니다. 조건을 코드로 조합해 두면 프론트엔드 필터 UI와 백엔드 검색 로직 사이 계약도 안정적으로 맞출 수 있습니다.

```python
from __future__ import annotations

from typing import Any

def build_filter(
    *,
    category: str | None = None,
    quarter: str | None = None,
    tenant: str | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    clauses: list[dict[str, str]] = []
    if category:
        clauses.append({'category': category})
    if quarter:
        clauses.append({'quarter': quarter})
    if tenant:
        clauses.append({'tenant': tenant})
    if language:
        clauses.append({'language': language})
    if not clauses:
        return {}
    if len(clauses) == 1:
        return clauses[0]
    return {'$and': clauses}

def run_filtered_search(vectorstore: Any, query: str) -> None:
    filter_query = build_filter(
        category='marketing',
        quarter='2024Q4',
        tenant='acme',
        language='ko',
    )
    docs = vectorstore.similarity_search(query, k=5, filter=filter_query)
    for rank, doc in enumerate(docs, start=1):
        print(
            f"rank={rank} source={doc.metadata['source']} "
            f"category={doc.metadata['category']} quarter={doc.metadata['quarter']}"
        )
```

벡터 유사도만으로는 근접하지만 범위가 틀린 문서가 끼어들 수 있습니다. 위 패턴처럼 조건을 먼저 조합하면 검색 후보군이 줄어들고, 랭킹이 해야 할 일이 더 명확해집니다. 결과적으로 응답 품질뿐 아니라 지연 시간과 비용도 함께 안정되는 경우가 많습니다.

### 인덱싱 시점에 필터 성능을 고려한 설정

필터가 많은 시스템에서는 인덱싱 단계에서 메타데이터 정규화를 함께 처리해야 합니다. 같은 의미를 가진 값이 `Q4`, `2024-Q4`, `2024Q4`로 섞여 있으면 필터 정확도가 떨어지고 캐시 적중률도 나빠집니다. 아래처럼 인덱싱 전에 정규화 함수를 강제하면 운영 품질이 좋아집니다.

```python
from __future__ import annotations

from langchain_core.documents import Document

def normalize_quarter(value: str) -> str:
    compact = value.replace('-', '').replace(' ', '').upper()
    if compact.startswith('Q') and len(compact) == 2:
        raise ValueError('quarter must include year, for example 2024Q4')
    return compact

def normalize_metadata(metadata: dict[str, str]) -> dict[str, str]:
    normalized = metadata.copy()
    normalized['category'] = normalized['category'].strip().lower()
    normalized['doc_type'] = normalized['doc_type'].strip().lower()
    normalized['language'] = normalized['language'].strip().lower()
    normalized['tenant'] = normalized['tenant'].strip().lower()
    normalized['quarter'] = normalize_quarter(normalized['quarter'])
    return normalized

def prepare_document(text: str, metadata: dict[str, str]) -> Document:
    normalized = normalize_metadata(metadata)
    return Document(page_content=text, metadata=normalized)
```

정규화는 눈에 덜 띄지만, 메타데이터 기반 검색의 핵심 안정장치입니다. 인덱싱할 때 한 번 강제해 두면 이후 필터 조건이 단순해지고, 분석 대시보드에서 지표를 집계할 때도 값이 깨끗하게 모입니다.

### 운영에서 자주 쓰는 메타데이터 인덱싱 구성 예시

문서 저장소를 분리하지 않더라도, 최소한 어떤 필드를 필터 대상으로 삼을지 사전에 정해 두어야 합니다. 아래 예시는 애플리케이션 설정 파일에 필터 가능 필드를 선언하고, 수집 파이프라인이 이를 검증하는 흐름입니다.

```yaml
metadata_index:
  required_fields:
    - source
    - doc_type
    - category
    - quarter
    - tenant
    - language
    - version
  filterable_fields:
    - category
    - quarter
    - tenant
    - language
  strict_mode: true
```

`strict_mode`를 켜면 필수 필드 누락 문서를 인덱싱 단계에서 즉시 실패로 처리할 수 있습니다. 처음에는 엄격해 보이지만, 이 장치가 있어야 나중에 검색 장애를 인덱스 정비 작업으로 되돌리지 않고 수집 경계에서 바로 잡을 수 있습니다.

요약하면 메타데이터 설계는 검색 직전의 옵션이 아니라 수집 파이프라인의 핵심 계약입니다. 스키마 정의, 값 정규화, 복합 필터 조합, 인덱싱 검증이 한 세트로 맞물려야 실제 서비스에서 예측 가능한 검색 동작을 얻을 수 있습니다.

## 처음 질문으로 돌아가기

- **메타데이터 스키마는 왜 임베딩 후가 아니라 수집 단계에서 먼저 설계해야 할까요?**
  수집 단계에서 source, doc_type, date, owner 같은 필드를 정해야 모든 청크와 인덱스가 같은 필터 계약을 공유합니다.

- **필터는 벡터 유사도 검색 전에 후보군을 어떻게 바꿀까요?**
  필터는 유사도 계산 전에 검색 대상 문서 집합을 줄여 관련 없는 후보가 상위 결과에 들어오는 것을 줄입니다.

- **필수 메타데이터가 빠지면 검색과 출처 표시에 어떤 문제가 생길까요?**
  필수 메타데이터가 빠지면 특정 문서군만 검색하거나, 답변에 정확한 출처·페이지·버전을 붙이는 일이 어려워집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- **Document Ingestion 101 (3/6): 메타데이터 설계와 필터링 (현재 글)**
- Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 (예정)
- Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangChain FAISS integration guide](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [LangChain Document object concepts](https://python.langchain.com/docs/concepts/documents/)

### 검증에 도움 되는 자료

- [FAISS GitHub repository](https://github.com/facebookresearch/faiss)
- [FAISS documentation](https://faiss.ai/)

Tags: RAG, Document Processing, LangChain, Python
