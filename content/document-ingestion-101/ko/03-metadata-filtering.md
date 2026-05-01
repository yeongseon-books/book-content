---
title: '메타데이터 설계와 필터링'
series: document-ingestion-101
episode: 3
language: ko
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

# 메타데이터 설계와 필터링

## 이 글에서 답할 질문

- 임베딩 검색만으로 해결되지 않는 조건은 어떤 것들일까요?
- LangChain Document 메타데이터를 어떻게 설계해야 나중에 필터가 쉬울까요?
- FAISS 검색에서 `filter` 파라미터를 어떤 식으로 붙일 수 있을까요?

> 메타데이터는 본문을 설명하는 부가 정보라기보다 검색 후보군을 줄이는 첫 번째 인덱스입니다.

예제 코드: `/root/Github/document-ingestion-101/ko/03-metadata-filtering/main.py`

![이 글에서 답할 질문](../../../assets/document-ingestion-101/03/03-01-questions-this-post-answers.ko.png)
RAG 검색이 생각보다 엉뚱한 결과를 내는 가장 흔한 이유는 “비슷한 내용”과 “찾고 싶은 범위”를 분리하지 않았기 때문입니다. 분기, 문서 종류, 출처 같은 조건은 임베딩만으로 깔끔하게 처리되지 않습니다.

이번 예제는 작은 문서 세 개를 FAISS에 넣고, `filter` 파라미터로 category와 quarter를 바꾸면서 검색 결과가 어떻게 달라지는지 확인합니다.

## 메타데이터 스키마 설계

![검색용 메타데이터 필드가 모이는 스키마](../../../assets/document-ingestion-101/03/03-01-metadata-schema-design.ko.png)
검색 스키마는 필드 수를 늘리는 일이 아니라 실제로 후보군을 줄일 키를 좁혀 가는 일에 가깝습니다.

## 필터가 후보군을 줄이는 흐름

![필터가 후보군을 줄이는 검색 흐름](../../../assets/document-ingestion-101/03/03-02-how-filters-narrow-the-candidate-set.ko.png)
의미상 비슷한 청크가 많아도 필터가 먼저 범위를 좁혀 주면 검색 결과가 훨씬 덜 흔들립니다.

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

    print('
[filter=quarter:2024Q4]')
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

## 이 코드에서 봐야 할 것

### 하이브리드 검색 결합 순서

![유사도와 필터가 결합되는 처리 흐름](../../../assets/document-ingestion-101/03/03-01-how-similarity-and-filters-combine.ko.png)
유사도와 필터는 경쟁 관계가 아니라 순서를 가진 협력 관계로 봐야 결과 해석이 쉬워집니다.

- `ChunkSpec`이 본문과 메타데이터를 함께 정의하므로 검색 스키마를 코드에서 한눈에 볼 수 있습니다.
- `SimpleHashEmbeddings`를 써서 네트워크 없이도 `filter` 동작 자체를 재현할 수 있습니다.
- 같은 질의라도 필터 조건을 바꾸면 결과 집합이 달라진다는 점이 핵심입니다.

## 실무에서 헷갈리는 지점

### 출처 추적과 감사 경로

![출처와 분기를 따라가는 추적 경로](../../../assets/document-ingestion-101/03/03-02-how-source-tracking-supports-audits.ko.png)
운영에서 잘못된 답을 추적할 때는 본문보다 source와 분기 정보가 먼저 단서를 주는 경우가 많습니다.

- 메타데이터는 많이 붙일수록 좋은 것이 아닙니다. 실제 필터에 쓰는 필드만 남겨야 유지비가 낮습니다.
- 벡터 검색 결과가 부정확해 보여도 필터 문제일 수 있습니다. 먼저 후보군이 올바르게 제한됐는지 봐야 합니다.
- FAISS 자체는 관계형 DB가 아니므로 복잡한 다중 조건은 애플리케이션 레이어 설계가 함께 필요합니다.

## 체크리스트

- [ ] chunk 메타데이터에 최소한 category, quarter, source를 넣었다.
- [ ] 같은 질의에 대해 서로 다른 filter 결과를 비교했다.
- [ ] 필터 필드 이름이 문서 생성 코드와 검색 코드에서 일관된다.
- [ ] 운영에서 필요한 필드만 남기도록 스키마를 정리했다.

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- **메타데이터 설계와 필터링 (현재 글)**
- 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

- https://python.langchain.com/docs/integrations/vectorstores/faiss/

Tags: RAG, Document Processing, LangChain, Python
