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

이 글은 Document Ingestion 101 시리즈의 세 번째 글입니다.

여기서는 실무에서 바로 쓸 수 있는 메타데이터 형태를 설계하고, 필터가 검색 동작을 어떻게 바꾸는지 눈에 보이게 확인합니다.

![Retrieval metadata schema flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-01-metadata-schema-design.ko.png)
*Retrieval metadata schema flow*
> 메타데이터는 본문 옆의 장식이 아니라 검색 후보군을 줄이는 첫 번째 인덱스입니다.

## 먼저 던지는 질문

- 메타데이터 스키마는 왜 임베딩 후가 아니라 수집 단계에서 먼저 설계해야 할까요?
- 필터는 벡터 유사도 검색 전에 후보군을 어떻게 바꿀까요?
- 필수 메타데이터가 빠지면 검색과 출처 표시에 어떤 문제가 생길까요?

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

## 실무 확장: 벡터 DB 필터 설계와 감사 가능한 스키마

메타데이터 필터는 단순한 검색 옵션이 아니라 접근 범위 제어 장치입니다. 특히 다중 테넌트 환경에서는 필터가 빠지는 순간 다른 조직 문서가 검색 후보에 섞일 수 있으므로, 스키마와 쿼리 빌더를 함께 관리해야 합니다.

### 필터 가능 필드와 표시 전용 필드를 분리하기

모든 메타데이터를 필터 대상에 넣으면 인덱싱 비용과 쿼리 복잡도만 커집니다. 운영에서는 보통 다음처럼 역할을 나눕니다.

- 필터 가능: `tenant`, `doc_type`, `category`, `quarter`, `language`, `version`
- 표시 전용: `title`, `author`, `uploaded_by`, `summary`

필터 가능 필드는 값 정규화가 필수이고, 표시 전용 필드는 사용자 경험 중심으로 확장합니다. 이 분리가 없으면 필터 조건식이 불필요하게 복잡해지고, 질의 성능도 예측하기 어려워집니다.

### 벡터 DB 조건식을 어플리케이션 계층에서 강제하기

아래 예시는 테넌트 조건을 무조건 포함시키는 필터 컴파일러입니다. 클라이언트가 테넌트를 누락해도 서버에서 강제할 수 있습니다.

```python
from __future__ import annotations

from typing import Any

def compile_filter(*, tenant: str, category: str | None, quarter: str | None) -> dict[str, Any]:
    clauses: list[dict[str, str]] = [{'tenant': tenant.lower()}]
    if category:
        clauses.append({'category': category.lower()})
    if quarter:
        clauses.append({'quarter': quarter.upper().replace('-', '')})
    return {'$and': clauses}

def search_with_guard(vectorstore: Any, query: str, tenant: str) -> list[Any]:
    filter_query = compile_filter(tenant=tenant, category='marketing', quarter='2024Q4')
    return vectorstore.similarity_search(query, k=8, filter=filter_query)
```

중요한 포인트는 필터를 UI에서만 만들지 않는 것입니다. 백엔드에서 최소 보안/범위 조건을 강제해야 예외 경로에서도 검색 범위가 흔들리지 않습니다.

### 메타데이터 스키마 버전을 도입하는 이유

필드 구조는 시간이 지나며 바뀝니다. `department`를 `category`로 통합하거나 `region`을 추가하는 순간, 기존 인덱스와 신규 인덱스가 섞일 수 있습니다. 아래처럼 스키마 버전을 명시하면 마이그레이션 경로를 분리할 수 있습니다.

```json
{
  "source": "q4-report.pdf",
  "tenant": "acme",
  "category": "marketing",
  "quarter": "2024Q4",
  "language": "ko",
  "version": "v3",
  "schema_version": "metadata-v2"
}
```

검색 서비스는 `schema_version`을 기준으로 호환 필터를 선택하거나, 구버전 문서를 재색인 대상으로 분류할 수 있습니다. 이 장치가 없으면 필드명 변경이 즉시 검색 장애로 이어질 수 있습니다.

### 감사 로그와 검색 로그를 연결하는 운영 패턴

메타데이터 필터를 실제로 어떻게 썼는지 남겨 두면 사고 대응이 빨라집니다.

```python
def emit_search_audit(*, query: str, filter_query: dict[str, object], user_id: str, request_id: str) -> None:
    print(
        {
            'event': 'vector_search',
            'request_id': request_id,
            'user_id': user_id,
            'query': query,
            'filter': filter_query,
        }
    )
```

이 로그는 "왜 이 결과가 나왔는가"를 재현할 수 있는 최소 재료입니다. 필터를 설계할 때는 검색 정확도뿐 아니라 감사 가능성까지 함께 고려해야 합니다.

## 운영 노트: 메타데이터 필터와 권한 경계

메타데이터 필터는 검색 정확도뿐 아니라 권한 경계를 지키는 역할도 합니다. 특히 B2B 환경에서는 `tenant`, `workspace`, `visibility` 같은 필드를 누락하면 다른 고객 문서가 후보군에 섞일 위험이 생깁니다.

```python
def build_access_filter(*, tenant: str, workspace: str, visibility: str = 'internal') -> dict[str, object]:
    return {
        '$and': [
            {'tenant': tenant.lower()},
            {'workspace': workspace.lower()},
            {'visibility': visibility.lower()},
        ]
    }
```

이 필터는 "검색 옵션"이 아니라 "최소 접근 제어"입니다. 따라서 애플리케이션 계층에서 무조건 결합하고, 감사 로그에 항상 남겨야 합니다.

또한 운영 초기에 필터 값 카디널리티를 점검하는 것이 좋습니다. 예를 들어 `quarter` 값이 5종이어야 하는데 27종으로 늘어났다면 정규화가 깨진 신호입니다. 메타데이터 품질은 인덱싱 시점에 한 번만 엄격하게 잡아도 이후 검색 안정성이 크게 올라갑니다.

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

## 마무리 운영 기준

문서 수집 파이프라인은 새 기능보다 기준 유지가 더 중요합니다. 그래서 팀 단위 운영에서는 아래 네 가지를 주간 기준으로 고정해 두는 편이 좋습니다.

- 파싱 품질 지표(평균 문자 수, OCR 비율, 재처리 비율)
- 청킹 품질 지표(평균 길이, 극단 길이 비율, 정책 버전 분포)
- 메타데이터 품질 지표(필수 필드 누락률, 정규화 실패 건수)
- 검색 검증 지표(샘플 질의 recall@k, 출처 회수율)

이 네 축을 함께 보면 어느 경계에서 품질이 떨어지는지 빠르게 확인할 수 있습니다. 결국 안정적인 ingestion은 화려한 모델 선택보다, 입력 품질과 단계 계약을 지속적으로 측정하는 운영 루틴에서 만들어집니다.

## 벡터 DB 쿼리에서 필터와 유사도 점수를 함께 활용하기

필터만으로 후보군을 줄인 뒤에도 유사도 점수 임계치를 추가로 걸면 노이즈를 한 번 더 줄일 수 있습니다. 실무에서는 `score_threshold`를 고정값으로 두기보다, 질의 유형별로 다르게 설정하는 패턴이 더 안정적입니다.

```python
from __future__ import annotations

from typing import Any

def search_with_threshold(
    vectorstore: Any,
    query: str,
    filter_query: dict[str, Any],
    score_threshold: float = 0.72,
    k: int = 8,
) -> list[Any]:
    docs_and_scores = vectorstore.similarity_search_with_score(query, k=k, filter=filter_query)
    return [(doc, score) for doc, score in docs_and_scores if score >= score_threshold]
```

이렇게 하면 필터를 통과했지만 의미적으로 동떨어진 청크가 최종 답변에 섞이는 것을 줄일 수 있습니다. 점수 임계치를 너무 높게 잡으면 recall이 떨어지므로, 샘플 질의 세트로 적정값을 먼저 확인하는 편이 좋습니다.

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/document-ingestion-101/ko)

Tags: RAG, Document Processing, LangChain, Python
